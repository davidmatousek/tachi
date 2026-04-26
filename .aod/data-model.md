# Data Model: Feature 224 — `human-trust-exploitation` Threat Agent

**Phase**: 1 (post plan.md design)
**Date**: 2026-04-26

## Key Entities

### 1. Agent Metadata YAML (lean-agent shape per ADR-023)

Located in `.claude/agents/tachi/human-trust-exploitation.md` immediately after the YAML frontmatter, before `## Purpose`.

```yaml
category: agentic                     # existing enum value (Q3 binding)
threat_class: ASI                     # OWASP Agentic Top 10 framework
dfd_targets: [Process]                # Process only (Q4 BLOCKING-1 binding); human-user trust boundary at indicator level
owasp_references: [OWASP ASI09:2026]  # primary attribution
output_schema: ../../../schemas/finding.yaml  # relative path to schema
```

**Invariants**:
- `agentic_pattern` is **NOT** declared in agent metadata (assigned downstream by orchestrator Phase 3.6 per ADR-026)
- `dfd_targets` is `[Process]` only — no External Entity declaration per BLOCKING-1
- `owasp_references` is the only required attribution at the metadata level; per-finding `source_attribution` carries the per-finding attribution (FR-007 / SC-010)

### 2. Pattern Category (5 categories per FR-004)

Each pattern category in `.claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md` follows this shape:

```markdown
### Pattern Category {N}: {Name}

**Primary**: OWASP ASI09:2026
**Related**: CWE-{NUMBER} ({Description}) [+ optional additional CWEs per FR-007]

**Indicators** (3-6 bullets):
- {Architectural feature whose presence raises the risk}
- ...

**Anti-Indicators** (per architect Q2 LOW-2 — at minimum the persona anti-indicator on category 4):
- {Architectural feature whose presence suppresses emission}

**Worked Example** (NFR-006 safe-language patterns enforced):
> Hypothetical: a {fictional-domain} {fictional-component-name} (fictional scenario; no real {institution-type})
> [scenario description with non-clinical distress framing where applicable]
> [for context, not legal interpretation: see, e.g., {regulatory framework}]

**Mitigations**:
- {Specific, named mechanism — Implement X / Configure Y / Enable Z}
- {Additional named mechanism}
- ...
```

**Invariants**:
- Each category MUST have ≥1 worked example with all four NFR-006 safe-language patterns applied (Hypothetical: prefix; "for context, not legal interpretation" framing where regulation is cited; non-clinical distress framing on category 5; no real institutional/clinician/lawyer/advisor/product names)
- Each category MUST have ≥1 primary-source citation (OWASP ASI09:2026 minimum)
- Each category MUST have applicable DFD element types declared (Process only with indicator-level filtering)
- Mitigations MUST be specific named mechanisms (NFR-007 — no generic "disclose AI authorship")

### 3. Human-User-Facing Emission Indicator (4 categories per FR-006)

The `## Detection Scope` `### Human-User-Facing Emission Indicators` subsection enumerates the indicator-level filtering criteria. The agent emits a finding when **at least one** of these four indicator categories is structurally present (after AI-agent keyword match per FR-013 two-part emission gate):

```markdown
### Human-User-Facing Emission Indicators

The agent emits a TE-{N} finding only when an AI-agent keyword match (per ### Trigger Keywords) is accompanied by at least one of the following human-user-facing emission indicators structurally present in the architecture:

#### Indicator A: Outgoing Data Flow to Human-Named External Entity
- The Process has at least one outgoing Data Flow targeting an External Entity whose name matches human-user nomenclature: "Customer", "Patient", "User", "Student", "Client", "Member", "Individual", "Subscriber", "Citizen", etc.

#### Indicator B: Process Description with Human-User-Facing Emission Keywords
- The Process description contains keywords like: `customer support`, `user-facing chat`, `consumer-facing advisory`, `direct-to-consumer`, `end-user interaction`, `client communication`, etc.

#### Indicator C: Sustained-Engagement Framing
- The architecture describes the Process as having sustained engagement with human users: `long-running dialogue`, `persistent persona`, `continuous conversation`, `session memory`, `user history`, `multi-turn dialog`, `relationship persistence`, etc.

#### Indicator D: Authority-Claim Emission Framing
- The Process is described as emitting authority-bearing content: `legal advice`, `medical recommendation`, `financial advisory`, `clinical decision support`, `regulatory guidance`, `expert advisory`, `professional consultation`, etc.

**Indicator Combination Rules**:
- Indicator presence is **at least one** for emission to fire
- Multiple indicators amplify finding severity (per OWASP 3×3 matrix application) but do not gate emission
- Indicators C and D, when combined, signal vulnerable-population deployment surface (category 5 vulnerable-population safeguards layer applies)
```

### 4. Trigger Keyword + Anti-Indicator Pair

Each trigger keyword that has a dual-use anti-indicator is paired with a negation condition that suppresses emission:

```markdown
**Anti-indicator subsection (architect Q2 LOW-2 discipline)**:

The following keywords trigger dispatch but require an additional human-user-facing emission indicator (per FR-006) to emit a finding. If these keywords appear ONLY in a prompt-engineering context (no human-user-facing emission), the agent emits zero findings on that component:

- `persona`: when used only in `system prompt: "You are a [persona name]..."` context with no consumer-facing surface
- `personality`: when used only as model-tuning vocabulary with no human user trust-boundary crossing
- `character agent`: when used as terminology for non-consumer-facing AI sub-agents in a multi-agent topology
```

### 5. Finding IR Shape (TE-{N} findings)

See `contracts/finding-contract.md` for the complete shape and invariants. Summary:

```yaml
id: "TE-{N}"
category: "agentic"
title: "{pattern_category}: {short_summary}"
severity: "low" | "medium" | "high" | "critical"
component: "{DFD Process component name}"
description: "{2-4 sentence threat description}"
mitigation: "{specific named mechanism}"
references:
  - "OWASP ASI09:2026"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-{NUMBER}", relationship: "related"}
maestro_layer: "L7"
agentic_pattern: "none" | "<existing enum value>"
delta_status: null
```

**Critical invariants** (R11 mitigation):
- `agentic_pattern` MUST NOT take value `trust_exploitation` (that's the agent-to-agent multi-agent topology pattern from Feature 142, not the agent-to-human communication-axis pattern from F-4)
- The two namespaces (`human-trust-exploitation` agent + `trust_exploitation` agentic_pattern enum value) cover non-overlapping scopes; FR-018 grep test verifies no prose synthesis at threat-report rendering

### 6. Companion Skill README Shape

Located in `.claude/skills/tachi-human-trust-exploitation/README.md`:

```markdown
# Tachi Human-Trust-Exploitation Detection Skill

> **Purpose**: Skill references consumed by `human-trust-exploitation` threat agent for ASI09:2026 communication-axis detection.

## Consumers

- `tachi-human-trust-exploitation` (the agent)

## Layout

- `references/detection-patterns.md` — pattern catalog with 5 categories, trigger keywords, human-user-facing emission indicators, worked examples, mitigations
```

Mirror `.claude/skills/tachi-misinformation/README.md` shape exactly.

## Validation Rules

| Rule | Source | Enforcement |
|------|--------|-------------|
| Agent file ≤150 lines (≤180 hard ceiling) | NFR-003 | `wc -l` at Wave 2 structural validation |
| Exactly 1 `**MANDATORY**: Read` directive | FR-001 / SC-001 | `grep -c '\*\*MANDATORY\*\*: Read'` = 1 |
| Zero MAESTRO references | FR-001 / SC-001 | `grep -i maestro` returns empty |
| Pattern category count ≥5 | FR-004 / SC-002 | Manual review of `## Detection Patterns` numbered headings |
| Each category has worked example with NFR-006 patterns | NFR-006 | Code-reviewer at Wave 6 |
| Each category has primary-source citation | FR-004 | grep for `OWASP ASI09:2026` per category |
| Each category has applicable DFD element types | FR-004 | grep for `Process` per category |
| `source_attribution` array non-empty on every TE-{N} finding | FR-007 / SC-010 | F-A2 `validate_source_attribution()` at orchestrator Phase 4 |
| `source_attribution` minimum: `{taxonomy: owasp, id: ASI09, relationship: primary}` | FR-007 / SC-010 | F-A2 validator |
| CWE entries use IDs present in `cwe.yaml` | FR-007 | F-A2 referential-integrity validator |
| CWE-451 NOT in `source_attribution` | FR-007 | Plan-time + post-regen check |
| MITRE ATLAS NOT in `source_attribution` | FR-007 | Plan-time + post-regen check |
| External regulatory refs NOT in `source_attribution` | FR-007 | Plan-time + post-regen check |
| `agentic_pattern` ≠ `trust_exploitation` on TE-{N} findings | FR-007 / R11 | FR-018 grep test on regenerated `threat-report.md` |
| Two-part emission gate: AI keyword AND human-user-facing indicator | FR-013 / SC-004 | Wave 4 false-positive check on web-app + microservices |
| `consumers:` list edit byte-identical on `## ` headings | FR-010 / SC-003 | structural-diff at Wave 3 |
| Schema 1.8 regex matches `TE-1` | FR-011 | `test_human_trust_exploitation.py::test_regex_matches_te_prefix` |
| 26-file zero-edit invariant including `agent-autonomy.md` | FR-014 / SC-009 | grep audit at PR pre-merge |
| 5 non-consumer-facing baselines byte-identical PDFs | FR-016 / SC-006 | `test_backward_compatibility.py` under SOURCE_DATE_EPOCH=1700000000 |
| Wave 2.0 grep-checklist verifies 6 coordinated edits | FR-009 / SC-015 | PR description artifact |
| FR-018 grep test passes on regenerated `threat-report.md` | FR-018 / SC-012 / R11 | `test_human_trust_exploitation.py::test_no_agp_te_prose_synthesis` |
| PR title `feat(224): ...` Conventional-Commit-formatted | FR-019 / SC-013 / R12 | `gh pr view --json title` at deliver-stage |
| NFR-006 four safe-language patterns on all 5 worked examples | NFR-006 | Code-reviewer at Wave 6 |
| NFR-007 self-disclosure discipline (no persuasive language) | NFR-007 | Code-reviewer at Wave 6 |

## Pattern Category Mapping

| Category | Primary | Related CWE(s) | Vulnerable-Population? |
|----------|---------|----------------|------------------------|
| 1. Undisclosed AI Authorship | OWASP ASI09:2026 | CWE-223 | No (general consumer) |
| 2. Authority-Claim Emission Without Confidence/Source Attestation | OWASP ASI09:2026 | CWE-345 | No (general high-stakes) |
| 3. Persuasive-Tone Manipulation / Missing Uncertainty Disclosure | OWASP ASI09:2026 | CWE-345 + optional CWE-223 | No (general consumer) |
| 4. Persona-Boundary Violations on Long-Running Dialogues | OWASP ASI09:2026 | CWE-287 + CWE-290 | No (general consumer; vulnerable subgroup overlaps with category 5) |
| 5. Synthetic-Relationship Exploitation | OWASP ASI09:2026 | CWE-223 + CWE-290 | **YES** (mental health / eldercare / minors / cognitive-impairment) — vulnerable-population safeguards layer applies |
