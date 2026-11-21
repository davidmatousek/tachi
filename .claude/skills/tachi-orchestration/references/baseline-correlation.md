---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# Baseline Correlation Reference

Reference material for baseline handling and carry-forward logic in the baseline-aware pipeline. Loaded on-demand by the orchestrator when entering Phase 1a+ (Baseline Handling).

## Baseline File Detection

### Priority Order

1. **Explicit `--baseline <path>`**: Use the specified file directly.
2. **Auto-detection**: Scan the output directory's **parent** for the most recent sibling directory containing a `threats.md`. Since each run creates a timestamped subfolder (e.g., `docs/security/2026-04-08T15-16-21/`), list all sibling directories, sort lexicographically (ISO timestamps sort naturally), exclude the current run's directory, and use the `threats.md` from the most recent match.
3. **No baseline found**: Operate in stateless mode (identical to pre-baseline behavior).

### Validation

A valid baseline must:
- Be a markdown file with YAML frontmatter
- Contain at least one finding table (Sections 3 or 4)
- Parse without errors

If validation fails, log a warning and fall back to stateless mode:
```
Warning: Baseline file found but unparseable — falling back to stateless mode.
```

## Finding Registry Extraction

Parse all finding tables from the baseline to build the finding registry.

### Table Parsing Order

1. Section 3: STRIDE tables (3.1 Spoofing through 3.6 Elevation of Privilege)
2. Section 4: AI threat tables (4.1 Agentic, 4.2 LLM)
3. Section 4a: Correlated Findings (extract correlation group membership)

### Per-Finding Fields

For each finding row in a table, extract:

| Field | Source Column | Notes |
|-------|-------------|-------|
| `id` | ID | Finding identifier (e.g., "S-3") |
| `category` | Derived from ID prefix | S→spoofing, T→tampering, etc. |
| `component` | Component | Target component name |
| `threat` | Threat | Full threat description |
| `likelihood` | Likelihood | LOW, MEDIUM, or HIGH |
| `impact` | Impact | LOW, MEDIUM, or HIGH |
| `risk_level` | Risk Level | Critical, High, Medium, Low, or Note |
| `mitigation` | Mitigation | Recommended countermeasure |
| `owasp_ref` | OWASP Reference | AI tables only; null for STRIDE. Carried-forward `LLM<NN>:2025` tokens are re-keyed to 2026 (see Delta Classification) |

### ID Prefix Mapping

| Prefix | Category |
|--------|----------|
| S | spoofing |
| T | tampering |
| R | repudiation |
| I | info-disclosure |
| D | denial-of-service |
| E | privilege-escalation |
| AG | agentic |
| LLM | llm |

## Fingerprint Correlation

### Computing Fingerprints

For each finding in the registry, compute:

1. **`findingId/v1`**: The finding ID itself (e.g., "S-3"). This is the primary correlation key.

2. **`primaryLocationLineHash`**: SHA-256 of `{ruleId}|{component_name}`, truncated to 16 hexadecimal characters. Where:
   - `ruleId` = category prefix + sequential number (matches finding ID)
   - `component_name` = exact component name from the finding

### Matching Algorithm

```
FOR each current_finding IN current_run:
    match = baseline_registry.find_by_id(current_finding.id)
    
    IF match found:
        IF match.primaryLocationLineHash == current_finding.primaryLocationLineHash:
            → High-confidence match (same finding, same location)
        ELSE:
            → Match with location change (component may have been renamed)
            → Flag for review but still correlate
    ELSE:
        → Candidate for NEW finding
        
FOR each baseline_finding IN baseline_registry:
    IF NOT matched by any current_finding:
        → Candidate for RESOLVED
```

### Tie-Breaking Rules

When multiple current findings could match a single baseline finding:

1. **Exact `primaryLocationLineHash` match** — highest confidence, always wins.
2. **Same component name** — next highest confidence.
3. **Highest description similarity** — lowest confidence, use as final tiebreaker only.

Tie-breaking is deterministic: given the same inputs, the same matches are produced.

## Delta Classification

After matching, classify each finding:

| Status | Condition | ID Assignment | Score Treatment |
|--------|-----------|---------------|-----------------|
| `UNCHANGED` | Baseline match found, same assessment | Inherit baseline ID | Inherit all scores |
| `UPDATED` | Baseline match found, changed description or context | Inherit baseline ID | Re-score fresh |
| `RESOLVED` | Baseline finding has no current match (component/threat removed) | Retain baseline ID | Retain last-known score |
| `NEW` | Current finding has no baseline match | Assign new sequential ID | Score fresh with bounds |

**MAESTRO layer handling**: `maestro_layer` is a classification field, not a score. For `UNCHANGED` and `UPDATED` findings, re-derive `maestro_layer` from the current Phase 1 component inventory rather than inheriting from the baseline finding. This prevents stale layer labels from persisting across MAESTRO taxonomy revisions (schema version bumps or keyword table changes). `RESOLVED` findings retain the baseline `maestro_layer` because the component is absent from the current inventory.

**OWASP edition re-keying**: `owasp_ref` is also a classification field. For every carried-forward finding (`UNCHANGED`, `UPDATED` and `RESOLVED`), replace each `LLM<NN>:2025` token in `owasp_ref` with its 2026 token from the table below. This is the OWASP LLM Top 10 2025 → 2026 mapping adopted in ADR-048, which bars re-emitting 2025 tokens. The change between editions is a permutation, not a renumbering, so a token copied verbatim would name a different category than a NEW finding's token with the same number: `LLM07:2025` is System Prompt Leakage, while `LLM07:2026` is Misinformation. Replace only the token and keep the rest of the cell, so `OWASP LLM07:2025` becomes `OWASP LLM08:2026`, and `OWASP LLM01:2025, ASI-01` becomes `OWASP LLM01:2026, ASI-01`. Leave `:2026`, ASI and MCP tokens unchanged. Re-keying is not a change of assessment: it never changes a finding's delta status, so an `UNCHANGED` finding stays `UNCHANGED`.

| 2025 token | 2026 token | Category (2026 name) |
|------------|------------|----------------------|
| `LLM01:2025` | `LLM01:2026` | Prompt Injection |
| `LLM02:2025` | `LLM02:2026` | Sensitive Information Disclosure |
| `LLM03:2025` | `LLM04:2026` | Supply Chain |
| `LLM04:2025` | `LLM05:2026` | Data and Model Poisoning |
| `LLM05:2025` | `LLM10:2026` | Improper Output Handling |
| `LLM06:2025` | `LLM03:2026` | Excessive Agency |
| `LLM07:2025` | `LLM08:2026` | Hidden Context Exposure |
| `LLM08:2025` | `LLM09:2026` | Vector and Embedding Weaknesses |
| `LLM09:2025` | `LLM07:2026` | Misinformation |
| `LLM10:2025` | `LLM06:2026` | Unbounded Consumption |

### Sequential ID Assignment for NEW Findings

New findings receive IDs that continue after the highest existing ID in their category:

```
highest_existing = max(baseline_ids_for_category)
new_id = category_prefix + "-" + (highest_existing_number + 1)
```

Example: If baseline has S-1 through S-5, a new spoofing finding gets S-6.

## Baseline Metadata

Extract from frontmatter or compute from file:

| Field | Primary Source | Fallback |
|-------|---------------|----------|
| `source` | Filename | N/A |
| `date` | frontmatter `date` | File modification date |
| `finding_count` | frontmatter or count parsed findings | Count all finding rows |
| `run_id` | frontmatter `run_id` | Generate from file modification timestamp |
