# Data Model: `misinformation` Threat Agent (F-2)

**Feature**: 206
**Status**: Phase 1 design artifact
**Scope**: Agent metadata YAML shape + pattern category structure + companion skill README shape

## Entities

### 1. Threat Agent Metadata (in `.claude/agents/tachi/misinformation.md`)

**Shape** (YAML block immediately after Markdown frontmatter):

```yaml
category: llm
threat_class: LLM
dfd_targets: [Process]
owasp_references:
  - "OWASP LLM09:2025"
output_schema: ../../../schemas/finding.yaml
```

**Fields**:

| Field | Type | Value | Rationale |
|-------|------|-------|-----------|
| `category` | enum | `llm` | Existing enum value — reused for `MI-{N}` ID family (no enum inflation) |
| `threat_class` | string | `LLM` | Mirror F-1 and 3 existing LLM-tier agents (prompt-injection, data-poisoning, model-theft) |
| `dfd_targets` | list | `[Process]` | Architect Q3 decision: Process only (mirror F-1); Data Flow extension deferred to F-2.1 |
| `owasp_references` | list | `[OWASP LLM09:2025]` | Single canonical OWASP reference; CWE references emitted per-finding in `source_attribution` |
| `output_schema` | path | `../../../schemas/finding.yaml` | Relative path to schema from agent file location |

**Invariants**:
- **`agentic_pattern` MUST NOT appear** in metadata (FR-016) — assigned by orchestrator Phase 3.6 per ADR-026
- **`dfd_targets` MUST be `[Process]`** per Q3 decision; Data Flow targeting would break precedent across 12 existing AI agents (11 original + F-1)
- **`category` MUST be `llm`** (not a new enum value); ID prefix `MI-{N}` distinguishes the finding-family without category-enum expansion
- **`owasp_references` SHOULD contain exactly one entry**: `OWASP LLM09:2025`. F-1 precedent included ML09:2023 as a doc-only bundling reference; F-2 has no analogous bundling (ML09 is distinct enough that documentation-only reference in ADR-031 rationale suffices, not in agent metadata)

### 2. Pattern Category (in `.claude/skills/tachi-misinformation/references/detection-patterns.md`)

**Shape** (one entry per numbered category under `## Detection Patterns`):

```markdown
### N. {Pattern Category Name}

**Primary Source**: OWASP LLM09:2025
**Related Source**: CWE-{NUMBER} ({CWE Name})
**Trigger Keywords**: {comma-separated subset of the 12 trigger keywords most relevant to this pattern}
**Applicable DFD Element Types**: Process

**Indicators** (3-6 bullets — conditions whose presence suggests this pattern applies):
- {Indicator 1}
- {Indicator 2}
- {Indicator 3}
- ...

**Anti-Indicators** (≥1 bullet — conditions whose presence MUST NOT trigger this pattern; per MEDIUM-5):
- {Anti-indicator describing a declared grounding / verification / HITL / calibration mechanism whose presence closes the gap}

**Worked Example** (clearly-fictional framing per NFR-6):

_Scenario_: {2-4 sentence clearly-fictional scenario — "a hypothetical clinical-decision-support system...", "a generic legal-research tool...", "a synthetic financial-advisory component..."}

_Finding shape_:
- **Severity**: {severity band}
- **Component**: {fictional component name}
- **Mitigation**: {named mitigation mechanism}

**Mitigations** (≥1 named mechanism):
- {Mitigation 1 — specific technology/pattern}
- {Mitigation 2}
```

**Fields**:

| Field | Type | Required | Rationale |
|-------|------|----------|-----------|
| Pattern category name | H3 heading | Yes | Names the sub-class per OWASP LLM09:2025 taxonomy |
| Primary Source | citation | Yes | OWASP LLM09:2025 on every pattern (catalog-resolvable) |
| Related Source | citation | Yes (≥1) | CWE-345 or CWE-223 (catalog-resolvable) |
| Trigger Keywords | list | Yes | Subset of the 12 keyword master list; guides keyword-emission-gate logic |
| Applicable DFD Element Types | list | Yes | `Process` only per Q3 |
| Indicators | bulleted list | Yes (3-6) | Structural conditions architect-reviewed during Wave 2 |
| Anti-Indicators | bulleted list | Yes (≥1) | Per architect MEDIUM-5 — bounds false-positive surface |
| Worked Example | prose block | Yes (≥1) | Clearly-fictional framing per NFR-6 |
| Mitigations | bulleted list | Yes (≥1) | Named grounding/verification/HITL/calibration mechanism |

**Invariants**:
- **Primary source MUST be OWASP LLM09:2025** on every pattern (SC-002, FR-007)
- **Related sources MUST be catalog-resolvable IDs** from `schemas/taxonomy/cwe.yaml` only (SC-010, FR-012)
- **Worked examples MUST use clearly-fictional framing** per NFR-6 — no real institutional names, no real clinician / lawyer / advisor identities, no real regulatory-citation examples
- **Anti-indicators MUST describe a declared mechanism** whose presence closes the gap (e.g., "RAG declared with retrieval-strength metric ≥0.85 declared adjacent to the LLM Process")

### 3. Five Pattern Categories (F-2 Scope)

| # | Category | Primary | Related (CWE in cwe.yaml) |
|---|----------|---------|----------------------------|
| 1 | **Ungrounded Factual Emission** | OWASP LLM09:2025 | CWE-345 |
| 2 | **Citation Fabrication** | OWASP LLM09:2025 | CWE-345 |
| 3 | **Overreliance / Missing HITL on Decision-Critical Output** | OWASP LLM09:2025 | CWE-223 primary; CWE-345 optional |
| 4 | **Retrieval-Grounding Gaps** | OWASP LLM09:2025 | CWE-345 |
| 5 | **Confidence-Calibration Absence** | OWASP LLM09:2025 | CWE-345 |

A 6th category (`Model-Specific Hallucination Patterns` or `Feedback-Loop Overreliance`) is out of scope per Q1 decision; architect may override at Wave 1.2 if a compelling signal-class differentiator surfaces.

### 4. Companion Skill README (`.claude/skills/tachi-misinformation/README.md`)

**Shape** (mirror `tachi-output-integrity/README.md`):

```markdown
# tachi-misinformation

Companion skill for `.claude/agents/tachi/misinformation.md` — provides the pattern catalog for OWASP LLM09:2025 misinformation detection.

## Consumers

- `.claude/agents/tachi/misinformation.md` (primary consumer)

## Layout

- `references/detection-patterns.md` — 5 pattern categories with indicators, worked examples, mitigations, and primary-source citations
```

**Fields**:

| Section | Content |
|---------|---------|
| H1 heading | `tachi-misinformation` |
| Description | One-sentence description of the skill's purpose |
| Consumers | List of agents that load this skill (single entry: `misinformation.md`) |
| Layout | Brief layout overview of the `references/` directory |

### 5. Trigger Keyword Set (12 keywords per Q2 decision)

**Keywords** (architect may refine at Wave 2 pattern authoring):

1. `factual output`
2. `citation generation`
3. `recommendation engine`
4. `decision support`
5. `RAG`
6. `grounding`
7. `hallucination`
8. `advisory`
9. `medical`
10. `legal`
11. `financial`
12. `clinical`

**Rationale**: 8 primary LLM09 vocabulary keywords + 4 high-stakes domain signals. Mirrors F-1's 12-keyword count for pattern-continuity.

**Invariants**:
- Keywords are case-insensitive (per existing dispatch-rules.md convention)
- Trigger keyword match alone is necessary but NOT sufficient for emission (FR-011 two-part gate)
- Factual-output indicator (structural feature in component description or connected Data Flows) is the second required condition

### 6. Two-Part Emission Gate (FR-011)

The agent's detection workflow enforces a gate requiring both:

1. **LLM trigger keyword match** on the dispatched Process component (one of the 12 keywords above)
2. **Factual-output indicator** structurally present in the component's description or connected Data Flows — architectural evidence that the component emits factual, citation-bearing, or decision-critical output

If only condition (1) is met (keyword match but purely stylistic output), the agent MUST emit zero findings for that component. Dispatch still happens, but the agent self-gates emission to prevent false positives on LLM components whose output is purely stylistic (copy generation, summarization, translation).

### 7. ADR-031 Structure (`docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`)

**Shape** (mirror ADR-030 + incorporate F-2-specific decisions):

| Section | Content |
|---------|---------|
| Front matter | `# ADR-031: Misinformation Agent (OWASP LLM09:2025)` + Status (Proposed → Accepted) + Date |
| Context | Why F-2 exists; LLM09 Planned → Covered transition; BLP-01 §7 F-2 |
| Decision | Adopt new `misinformation` agent conforming to ADR-023 lean pattern; schema bump 1.6 → 1.7 with `MI` prefix |
| Heuristic A Signal-Class Rationale | Three-way scope resolution: distinct from prompt-injection (input-side attacker-controlled injection); distinct from output-integrity (F-1 scope per ADR-030 Decision 1 — downstream-execution-sanitization); scoped to factual-integrity (grounding, verification, HITL, calibration) |
| Lean-Agent Shape Conformance | ≤150 lines, single `**MANDATORY**: Read`, zero MAESTRO references, 24-file zero-edit invariant preserved |
| Cross-References | ADR-021 (determinism), ADR-023 (lean-agent shape), ADR-026 (schema bump rule), ADR-027 (taxonomy), ADR-028 (source_attribution), ADR-029 (coverage attestation), ADR-030 (F-1 + Decision 1 scope bounds + Decision 8 regex-alternation minor-bump rule — F-2 is 2nd recorded application) |
| 24-File Zero-Edit Invariant Proof | Grep-auditable enumeration of the 24 files (22 original + F-1's 2) left untouched by F-2 |
| CWE-1039 Deliberate-Exclusion Note | Model-evasion CWE (CWE-1039) is out of scope; pattern catalog focuses on factual-content primitives, not model-robustness primitives |
| Revision History | Proposed date → Accepted date → Post-merge SHA fill |
| Zero Commercial Framing | No Layer 2, no tachi Cloud, no enterprise-only features (public ADR stands on technical merits alone) |

**Invariants**:
- **Dual-commit pattern** per ADR-027/028/029/030 precedent (Proposed at Wave 1.1, Accepted at Wave 5 with provisional merge-date, post-merge SHA fill)
- **Cross-reference ADR-030 Decision 1** explicitly (establishes F-1 scope bounds leaving factual-integrity open for F-2)
- **Cross-reference ADR-030 Decision 8** explicitly (establishes regex-alternation minor-bump rule F-2's schema bump invokes as 2nd recorded application)
- **Zero commercial framing** per public-ADR governance

## State Transitions

### Finding Emission Flow

```
DFD Architecture Input
  ↓
Orchestrator Dispatch (Phase 2)
  ↓ LLM keyword match on Process component
Misinformation Agent Invoked
  ↓ Two-part emission gate (FR-011)
  ↓   - Keyword match: CHECK
  ↓   - Factual-output indicator: CHECK
  ↓ (both conditions required)
  ↓
Pattern Category Evaluation (5 categories)
  ↓ ≥1 pattern matches
MI-{N} Finding Emitted
  ↓
Orchestrator Phase 3: MAESTRO + agentic_pattern assignment
  ↓
Orchestrator Phase 4: validate_source_attribution (MUST pass)
  ↓
Orchestrator Phase 5: deduplication
  ↓
threats.md + threats.sarif rendering
```

If only keyword match (no factual-output indicator): **zero findings emitted** for that component (FR-011 zero-speculation discipline).

### Schema Version Transition

```
schema_version: "1.5" (pre-F-1)
  ↓ F-1 bump (ADR-030 Decision 8 — 1st application)
schema_version: "1.6" (post-F-1; id.pattern adds OI prefix)
  ↓ F-2 bump (ADR-030 Decision 8 — 2nd application)
schema_version: "1.7" (post-F-2; id.pattern adds MI prefix)
```

All transitions are additive regex-alternation extensions preserving backward compatibility — existing IDs remain valid against the extended pattern.

### ADR-031 Lifecycle

```
Wave 1.1: ADR-031 Proposed commit
  ↓ Body complete: Decision + Heuristic A + lean-agent conformance + cross-refs + invariant proof + Revision History
Wave 5: ADR-031 Accepted transition
  ↓ Provisional merge-date set; Revision History updated
Post-merge: SHA fill
  ↓ Squash commit hash recorded in Revision History
```

## References

- **ADR-023**: Lean-agent detection variant (authoritative pattern for F-2 agent shape)
- **ADR-026**: Minor-bump rule (base; extended by ADR-030 Decision 8 for regex-alternation prefixes)
- **ADR-030**: F-1 precedent (direct model for F-2; Decision 1 scope bounds F-1 leaving factual-integrity for F-2; Decision 8 regex-alternation rule F-2 invokes)
- **Feature 082**: Lean-agent refactor (22-file invariant origin; F-2 extends to 24-file after F-1)
- **Feature 201 (F-1)**: Second-net-new AI-tier agent precedent (F-2 mirrors structurally)
