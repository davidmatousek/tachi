---
name: tachi-orchestration
description: "Domain knowledge for the tachi orchestrator agent: input format detection, DFD classification, trust boundary notation, STRIDE-per-Element dispatch rules, coverage requirements per component type, coverage matrix model, SARIF 2.1.0 generation specification, output schema tables for threats.md, baseline correlation, structural validation checklist, and error handling templates. Loaded on-demand by the orchestrator during specific pipeline phases."
---

# Tachi Orchestration Skill

Domain knowledge extracted from the tachi orchestrator agent to support the OWASP four-step threat modeling pipeline. This skill provides reference material that the orchestrator loads on-demand at specific workflow phases, keeping the agent definition focused on orchestration logic.

## Domain Coverage

This skill contains six categories of domain knowledge:

1. **Format Detection** -- Input format recognition patterns for ASCII, Free-text, Mermaid, PlantUML, and C4 architecture descriptions with priority ordering and heuristic matching rules.

2. **DFD Classification** -- DFD element type classification signals for External Entity, Process, Data Store, and Data Flow with ambiguous-classification defaults and format-specific extraction guidance.

3. **Trust Boundaries** -- Format-specific boundary notation for Mermaid subgraph, ASCII dashes, PlantUML boundary, C4 boundaries, and Free-text prose markers.

4. **Dispatch Rules** -- STRIDE-per-Element normalization table mapping DFD element types to applicable threat categories, AI keyword dispatch rules with keyword-to-category mappings and matching semantics, dispatch table format specification, and the five correlation rules with detection algorithm and group assembly instructions.

5. **Coverage Requirements & Matrix** -- Required STRIDE+AI categories per component type (external-entity, process, data-store, data-flow, llm-process, mcp-server), category-to-agent mapping for targeted re-analysis, three-state coverage matrix cell model, deduplication rules, and footnote conventions.

6. **Output & SARIF** -- Output format specification for threats.md (frontmatter fields, all 7 required sections plus Section 4a), SARIF 2.1.0 generation specification with fingerprint preservation and taxonomy passthrough rules, structural validation checklist, and error handling templates.

## Loading Table

| Reference File | Load Condition | Workflow Phase |
|----------------|----------------|----------------|
| `references/format-detection.md` | Entering Phase 1 (Format Identification) | Before determining architecture description format |
| `references/dfd-classification.md` | Entering Phase 1 (DFD Extraction) | Before classifying components into DFD element types |
| `references/trust-boundaries.md` | Entering Phase 1 (Boundary Identification) | Before extracting trust boundary notation |
| `references/dispatch-rules.md` | Entering Phase 2 (Determine Threats) | After Phase 1 component inventory is produced, before agent dispatch |
| `references/coverage-requirements.md` | Entering Phase 3 (Coverage Gate) | Before evaluating coverage completeness per component |
| `references/coverage-matrix-model.md` | Entering Phase 4 (Output Assembly) | Before building the coverage matrix in threats.md |
| `references/output-schemas.md` | Entering Phase 1 (Scope) for output format awareness; Phase 3 for table assembly; Phase 4 for validation | Before assembling Section 1, and before running the structural validation checklist |
| `references/sarif-specification.md` | Entering SARIF generation step in Phase 4 | After threats.md structural validation passes, before writing threats.sarif |
| `references/baseline-correlation.md` | Entering Phase 1a+ (Baseline Handling) | Before parsing baseline file, before carry-forward logic |

## Baseline-Aware Pipeline Domain Knowledge

The orchestrator supports a baseline-aware mode that extends the standard OWASP pipeline with finding stability, delta annotations, and coverage assurance. This domain knowledge is loaded on-demand during Phase 1a+ (Baseline Handling) and subsequent carry-forward phases.

### Baseline File Detection Rules

The orchestrator detects baselines in priority order:

1. **Explicit flag**: `--baseline <path>` — use the specified file directly.
2. **Auto-detection**: Check the output directory for an existing `threats.md`. If found, use it.
3. **No baseline**: If neither method finds a baseline, operate in stateless mode (identical to pre-baseline behavior).

**Graceful degradation**: If a baseline file is found but is corrupted or unparseable, log a warning and fall back to stateless mode. The pipeline must never block on a bad baseline.

### Finding Registry Extraction Format

Parse all finding tables (Sections 3, 4, 4a) from the baseline `threats.md` to build the finding registry:

```yaml
registry_entry:
  id: "S-3"                    # Finding ID (primary correlation key)
  category: "spoofing"          # Threat category from ID prefix
  component: "API Gateway"      # Target component
  threat: "description..."      # Full threat description
  likelihood: "HIGH"            # Assessed likelihood
  impact: "HIGH"                # Assessed impact
  risk_level: "Critical"        # Computed risk level
  mitigation: "countermeasure..." # Recommended mitigation
  fingerprints:
    findingId/v1: "S-3"         # Primary correlation key
    primaryLocationLineHash: "a1b2c3d4e5f6a1b2" # SHA-256(ruleId|component_name) truncated to 16 hex
```

### Fingerprint Correlation Algorithm

Finding correlation across runs uses a two-tier matching strategy:

**Primary key**: `partialFingerprints.findingId/v1` — the stable finding ID (e.g., "S-3"). This is the authoritative correlation mechanism. Two findings with the same `findingId/v1` are the same finding across runs.

**Validation signal**: `partialFingerprints.primaryLocationLineHash` — SHA-256 hash of `ruleId|component_name` truncated to 16 hex characters. This confirms the match is correct but does **not** discriminate between findings. It is a secondary signal, not a primary key.

**Matching rules**:
1. Match findings by `findingId/v1` first (exact string match).
2. If `findingId/v1` matches, check `primaryLocationLineHash`:
   - If both match: high-confidence correlation → `UNCHANGED` or `UPDATED`.
   - If `findingId/v1` matches but `primaryLocationLineHash` differs: flag for review but still correlate (component may have been renamed).
3. Baseline findings with no matching current finding: candidates for `RESOLVED`.
4. Current findings with no matching baseline finding: candidates for `NEW`.

**Tie-breaking**: When multiple current findings could match a single baseline finding (e.g., after component rename), prefer the match with:
1. Exact `primaryLocationLineHash` match (highest confidence).
2. Same component name (next highest).
3. Highest description similarity (lowest confidence — use only as tiebreaker).

### Deterministic Similarity Algorithm

Phase 3a merge/dedup uses normalized Levenshtein distance on preprocessed description tokens to determine whether a Phase 2 discovery duplicates a carry-forward finding. This algorithm is deterministic — identical inputs always produce identical similarity scores.

#### Preprocessing Pipeline

1. **Lowercase**: Convert the entire description string to lowercase.
2. **Remove stopwords**: Remove the following English stopwords: `a`, `an`, `the`, `is`, `are`, `was`, `were`, `be`, `been`, `by`, `for`, `of`, `to`, `in`, `on`, `at`, `with`, `from`, `that`, `this`, `which`, `through`, `via`.
3. **Tokenize**: Split on whitespace and punctuation (`,`, `.`, `;`, `:`, `(`, `)`, `-`, `/`). Discard empty tokens.
4. **Sort tokens**: Sort the token list alphabetically. This ensures word order does not affect similarity (a reworded description with the same vocabulary produces the same token set).

#### Similarity Computation

Given two preprocessed, sorted token lists `A` and `B`:

1. Join each token list into a single space-separated string: `str_A = join(A, " ")`, `str_B = join(B, " ")`.
2. Compute Levenshtein edit distance: `dist = levenshtein(str_A, str_B)`.
3. Compute similarity: `sim = 1.0 - (dist / max(len(str_A), len(str_B)))`.
4. If both strings are empty: `sim = 1.0`.

#### Threshold and Policy

- **Duplicate threshold**: `sim > 0.80` (strictly greater than 80%).
- **Baseline wins**: When a duplicate is detected, the carry-forward (baseline) version is kept. The Phase 2 discovery version is discarded.
- **Rationale**: The 80% threshold accommodates minor wording variations from LLM non-determinism while filtering out genuinely different threats. The baseline-wins policy preserves finding stability per the core design goal.

#### Tie-Breaking

When multiple Phase 2 findings match the same carry-forward finding above the 0.80 threshold:
1. **Highest similarity score wins** (most likely duplicate).
2. If tied: **exact component name match** wins.
3. If still tied: **first in Phase 2 output order** wins (stable ordering).

Each carry-forward finding can be matched at most once. Once matched, it is removed from the candidate pool for subsequent Phase 2 findings.

### Coverage Gate Orchestration Rules

The coverage gate (Phase 3b) verifies that all required threat categories have been evaluated for each component. It uses `schemas/coverage-checklists.yaml` as its configuration source and runs in both baseline and stateless modes.

#### Component Type Detection Rules

Detection is a two-step process: AI subtype check (takes precedence) then DFD type fallback.

**Step 1 — AI subtype detection**: For each component classified as `Process` in Phase 1, check name and description against AI keywords. Matching is **case-insensitive substring** (e.g., "LLM Agent Orchestrator" matches keyword `llm`; "MCP Tool Server" matches keyword `mcp`).

| AI Subtype | Keywords | Resulting Type |
|------------|----------|---------------|
| LLM Process | `llm`, `language model`, `gpt`, `claude`, `ai model`, `inference` | `llm_process` |
| MCP Server | `mcp`, `model context protocol`, `tool server`, `plugin host` | `mcp_server` |

**Step 2 — DFD type fallback**: If no AI keywords matched, map the Phase 1 DFD classification directly:

| DFD Element Type | Coverage Type |
|-----------------|---------------|
| External Entity | `external_entity` |
| Process | `process` |
| Data Store | `data_store` |
| Data Flow | `data_flow` |

**Precedence rule**: AI subtype always wins. A Process matching LLM keywords becomes `llm_process`, not `process`. A component can match at most one AI subtype. If both LLM and MCP keywords match (unlikely but possible), prefer `llm_process` (LLM threats are broader).

#### Checklist Lookup Logic

After determining each component's type, look up required categories from `schemas/coverage-checklists.yaml`. The schema defines `component_types.{type}.required_categories` as a list of category strings.

Category strings map to finding ID prefixes for coverage evaluation:

| Checklist Category | Finding Prefix | Threat Agent(s) |
|-------------------|---------------|-----------------|
| `spoofing` | S | tachi-spoofing |
| `tampering` | T | tachi-tampering |
| `repudiation` | R | tachi-repudiation |
| `info-disclosure` | I | tachi-info-disclosure |
| `denial-of-service` | D | tachi-denial-of-service |
| `privilege-escalation` | E | tachi-privilege-escalation |
| `agentic` | AG | tachi-tool-abuse, tachi-agent-autonomy |
| `llm` | LLM | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft |

#### Gap Flagging Format

A **gap** is a `(component, required_category)` pair where no active finding exists in the current finding set. Active findings exclude `RESOLVED` findings.

The gap list is structured as:

```yaml
gaps:
  - component: "LLM Agent"
    missing_category: "model-theft"
    resolution: null  # set after re-analysis
  - component: "API Gateway"
    missing_category: "repudiation"
    resolution: null
```

#### Targeted Re-Analysis Dispatch Rules

For each gap, dispatch the agent(s) mapped to the missing category (see table above). For compound categories (`agentic`, `llm`), dispatch **all** listed agents — findings from any satisfy the requirement.

**Dispatch constraints**:
- **Single component scope**: Each re-analysis targets exactly one component for one category. The agent receives the full architecture context but is instructed to analyze only the specified component.
- **One attempt per gap**: No retry loops. If the agent returns no findings, the gap is `"analyzed_clean"`. If dispatch fails, the gap is `"dispatch_failure"`.
- **Isolated context in baseline mode**: Re-analysis agents follow the same isolation rules as Phase 2 — no baseline finding descriptions in the payload. Only the coverage summary is provided.
- **ID assignment**: New findings from re-analysis get sequential IDs after the highest existing ID in the category, consistent with Phase 3a rules.

#### Non-Blocking Warning Semantics

The coverage gate is **advisory, not blocking**. It produces warnings, never errors.

- **`pass`**: All required categories evaluated. No gaps, or all gaps resolved (findings produced or analyzed clean).
- **`warn`**: One or more gaps remain unresolved (dispatch failure). The pipeline continues regardless.
- The coverage gate **never** halts the pipeline. Even with unresolved gaps, Phase 3 continues to Risk Level Validation and table assembly.
- Coverage gate results are recorded in the output frontmatter (`coverage_gate.status`, `coverage_gate.gaps`) and rendered in Section 5a of `threats.md` for transparency.

## Loading Mechanism

The orchestrator agent uses the Read tool to load reference files on-demand per ADR-002. Each reference file is self-contained and can be loaded independently at the workflow phase indicated above. Content is evictable from context after the relevant phase completes.

```markdown
# Example loading instruction in orchestrator agent body:
Read `.claude/skills/tachi-orchestration/references/sarif-specification.md`
when entering the SARIF generation step in Phase 4.
```
