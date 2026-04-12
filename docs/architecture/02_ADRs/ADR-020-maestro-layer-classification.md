# ADR-020: MAESTRO Layer Classification for Threat Findings

**Status**: Accepted
**Date**: 2026-04-08
**Deciders**: Architect
**Feature**: 084 (MAESTRO Layer Mapping)

---

## Context

tachi's threat model pipeline classifies components by DFD element type (External Entity, Process, Data Store, Data Flow) during Phase 1 (Scope), then dispatches STRIDE and AI threat agents accordingly. However, the pipeline had no awareness of where components sit within an agentic AI architecture stack. This limited the ability to:

1. **Identify architectural concentration risk**: Threats clustered at one layer (e.g., many threats against Foundation Model components) were invisible without manual review.
2. **Align with industry taxonomy**: Security teams using CSA's MAESTRO framework could not map tachi findings to their existing layer-based security controls.
3. **Enable layer-based risk aggregation**: The Risk Summary section could not break down findings by architectural layer, making it harder to prioritize remediation across system tiers.

**Constraints**:
- Classification must not require user-provided layer annotations -- it must be automatic.
- Classification must be deterministic and auditable (no LLM-based classification of component types).
- The new field must propagate through the entire pipeline without breaking existing consumers.
- Classification must handle components that do not fit any layer gracefully (no errors for unclassifiable components).

---

## Decision

We will adopt the **CSA MAESTRO seven-layer taxonomy** as the architectural layer classification framework, implemented via **keyword-based substring matching** during Phase 1 with ordered evaluation (L1 through L7, first match wins).

The implementation adds:
1. A shared reference file (`maestro-layers-shared.md`) with the canonical keyword-to-layer mapping table.
2. An optional `maestro_layer` field on the finding IR schema (`schemas/finding.yaml`, schema_version 1.1 to 1.2).
3. Phase 1 classification: after DFD type assignment, each component is classified by matching its name, description, and DFD type against layer keywords.
4. Phase 3 inheritance: each finding inherits `maestro_layer` from its target component.
5. Passive propagation through downstream agents (risk-scorer, control-analyzer, threat-report).

---

## Rationale

**Reasons**:
1. **Industry alignment**: CSA MAESTRO is the only published seven-layer taxonomy specifically designed for agentic AI architectures. Using it provides a shared vocabulary with the broader security community.
2. **Keyword matching reuses proven pattern**: The AI dispatch mechanism (Feature 007) already uses case-insensitive keyword matching to classify components. MAESTRO classification follows the same pattern, reducing implementation risk.
3. **Deterministic and auditable**: Keyword matching produces the same result every run for the same input, unlike LLM-based classification which could vary between invocations. The keyword table is inspectable and versioned.
4. **Non-breaking schema extension**: The `maestro_layer` field defaults to "Unclassified", making it backward-compatible with existing threat models and consumers that do not use it.
5. **Shared reference prevents drift**: Following ADR-019 (shared definitions), the keyword table lives in `tachi-shared` as a single source of truth consumed by all agents that need layer awareness.

---

## Alternatives Considered

### Alternative 1: LLM-Based Component Classification
**Pros**:
- Could handle ambiguous component names more intelligently
- No keyword table maintenance

**Cons**:
- Non-deterministic: same component could be classified differently across runs
- Not auditable: no inspectable mapping table
- Adds inference cost and latency to Phase 1
- Conflicts with tachi's deterministic pipeline design principle

**Why Not Chosen**: Determinism and auditability are critical for security tooling. Keyword matching provides both while handling the vast majority of real-world component names correctly.

### Alternative 2: User-Provided Layer Annotations
**Pros**:
- Most accurate classification possible
- No false positives from keyword matching

**Cons**:
- Adds mandatory input burden on every threat model run
- Breaks the current zero-configuration input contract
- Users unfamiliar with MAESTRO would produce inaccurate annotations

**Why Not Chosen**: Automatic classification with graceful fallback ("Unclassified") delivers value without requiring users to learn a new taxonomy.

### Alternative 3: Custom Layer Taxonomy
**Pros**:
- Could be tailored exactly to tachi's needs
- No dependency on external framework updates

**Cons**:
- Reinvents an existing standard without adding value
- No shared vocabulary with the security community
- Additional maintenance burden to keep custom taxonomy current

**Why Not Chosen**: CSA MAESTRO is well-aligned with tachi's target domain (agentic AI). A custom taxonomy would duplicate effort without meaningful benefit.

---

## Consequences

### Positive
- Threat models now include architectural layer context for every component and finding
- Risk Summary includes a "Risk by MAESTRO Layer" breakdown enabling layer-based prioritization
- SARIF output tags findings with MAESTRO layer for downstream tooling integration
- Aligns tachi with CSA's industry-standard framework for agentic AI security

### Negative
- Keyword matching can misclassify components with ambiguous names (e.g., "API Gateway" could be L4 or L7)
- Evaluation order (L1-L7) is load-bearing -- reordering keywords changes classification
- Adding new layers or modifying keywords requires regression testing against all example outputs

### Mitigation
- Evaluation order follows a specificity gradient (most specific first) to minimize ambiguity
- "Unclassified" default ensures graceful degradation for unrecognized components
- All 6 example outputs were regenerated and validated after implementation
- Keyword table changes are documented with a warning about ordering sensitivity

---

## Related Decisions

- [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md): Shared definitions pattern that governs where the MAESTRO keyword table lives
- [ADR-003](ADR-003-stride-per-element-dispatch.md): STRIDE-per-Element dispatch pattern that MAESTRO classification extends

---

## References

- `.claude/skills/tachi-shared/references/maestro-layers-shared.md` -- Canonical keyword-to-layer mapping
- `schemas/finding.yaml` -- Finding IR schema with `maestro_layer` field (v1.3)
- Cloud Security Alliance, "MAESTRO: Multi-Agent Environment, Security, Threat, Risk, and Outcome", February 2025

---

## Revision History

**2026-04-10 (Feature 136)**: Layer names for L5, L6, L7 aligned with canonical CSA MAESTRO taxonomy per the Ken Huang authoritative definition. L5 renamed from "Security" to "Evaluation and Observability", L6 renamed from "Agent Ecosystem" to "Security and Compliance", L7 renamed from "User Interface" to "Agent Ecosystem". Acronym expansion corrected to "Multi-Agent Environment, Security, Threat, Risk, and Outcome". Schema version bumped from 1.2 to 1.3 to signal the breaking enum-value change. See `docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md` for full context.

**Schema versioning rule** (established for this feature): Enum-value-only breaking changes to `schemas/finding.yaml` warrant a minor schema bump (x.y+1), not a major bump, provided the schema shape and required fields are unchanged. The CHANGELOG migration note is the accountability mechanism for downstream consumers. This rule applies to future enum-value corrections.

**2026-04-12 (Feature 141)**: Phase 2 — Cross-Layer Attack Chain Analysis. Transitions MAESTRO from passive taxonomy overlay to active cross-layer correlation analysis. See "Phase 2: Cross-Layer Correlation" section below. Decision section updated to reflect both passive layer tagging (Phase 1) and active cross-layer correlation (Phase 3.5). New schema: `schemas/attack-chain.yaml` v1.0.

---

## Phase 2: Cross-Layer Correlation

Feature 141 extends MAESTRO classification from a passive taxonomy overlay (Phase 1 keyword matching) to an active cross-layer correlation engine (Phase 3.5) that identifies attack chains spanning multiple MAESTRO layers.

### Architecture

**Pipeline Placement**: Phase 3.5 runs after Phase 3 deduplication and Section 4a intra-component correlation, and before Phase 4 assessment. It operates on the deduplicated finding intermediate representation (IR) — not raw agent output — bounding input size for context management.

**Input Contract**:
- Phase 1 component inventory (names, types, MAESTRO layer assignments)
- Data flow graph (source → target component relationships)
- Deduplicated findings with `maestro_layer` assignments

**Output Contract**:
- `attack-chains.md` artifact (conditional on chain detection)
- `has-attack-chains` boolean for downstream consumption

**Independence Invariant**: Phase 3.5 cross-layer chains and Phase 3 Section 4a intra-component correlation groups are independent grouping mechanisms. A finding may appear in both without conflict.

### Correlation Algorithm

Rule-based pattern matching using a deterministic transition lookup table stored in `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md`. The table maps (STRIDE category, MAESTRO layer) pairs to valid successor pairs with causal vocabulary.

**Correlation signals** (priority order):
1. **Component lineage**: Findings target components connected by data flows
2. **Data flow dependency**: Findings on components sharing data flow paths
3. **Layer adjacency + structural**: Adjacent MAESTRO layers with at least one structural relationship

**Chain assembly**:
1. Group findings by component and MAESTRO layer
2. Validate against transition lookup table (table-based, no probabilistic scoring)
3. Verify structural evidence (component lineage or data flow dependency required)
4. Assemble ordered sequences, filter to 2+ layers with Critical/High finding
5. Rank by severity desc, chain length desc, chain ID alpha asc
6. Cap surfaced chains at top 5; all chains recorded in artifact

**Determinism**: Same input produces identical output via deterministic lookup, three-key sort with no tie possibility, and sequential chain ID assignment.

### Chain Schema

New schema file: `schemas/attack-chain.yaml` v1.0. Chains are cross-finding aggregates, separate from the finding schema. Each chain contains: chain_id, title, ordered layer progression, member findings with roles, causal narrative, chain-breaking controls, and surfaced flag.

### Downstream Propagation

- **Threat report agent**: New Section 6 (Cross-Layer Attack Chains) with 150-300 word narratives per surfaced chain, conditional on `has-attack-chains`
- **PDF security report**: Chain diagram pages with vertical MAESTRO layer stack (Mermaid flowchart TD), rendered via existing mmdc pipeline (ADR-022)
- **Correlation pattern reference**: `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md`

### Scope Boundary

The transition lookup table covers the 6 STRIDE categories only. AG and LLM findings are excluded from chain formation to avoid redundant chains (Phase 3 Section 4a handles STRIDE+AI co-location). AG/LLM findings can appear indirectly when their target component also has a STRIDE finding that participates in a chain.
