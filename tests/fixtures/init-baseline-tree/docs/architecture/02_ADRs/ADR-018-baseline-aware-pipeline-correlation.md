# ADR-018: Baseline-Aware Pipeline with Deterministic Fingerprint Correlation

**Status**: Accepted
**Date**: 2026-04-01
**Deciders**: Architect
**Feature**: 074 (Baseline-Aware Pipeline)

---

## Context

All three tachi pipeline steps (`/threat-model`, `/risk-score`, `/compensating-controls`) were stateless -- each run generated findings from scratch with zero awareness of previous runs. On an unchanged codebase (second-brain-mcp, March 25 vs March 31), this produced a 23% finding count drift, 0.2-0.6 score drift per finding, complete ID remapping, and 9 phantom "new" findings. This made remediation tracking, stakeholder reporting, and compliance verification unreliable.

Key constraints:
- Baseline correlation must be deterministic -- the same inputs must produce the same delta classifications across runs.
- First-run behavior (no baseline) must be identical to the existing stateless pipeline. No breaking changes.
- The correlation algorithm must be embeddable in agent prompt instructions with no runtime dependencies (no Python scripts, no databases).
- Fresh discovery must not be anchored by baseline findings -- new threats should be discovered independently.
- All changes must be additive to existing schemas, templates, and SARIF output.

---

## Decision

We will implement an **Enhanced Hybrid 4-phase baseline-aware pipeline** that combines carry-forward stability with fresh discovery quality, using SARIF `partialFingerprints` as the primary correlation mechanism.

**4-Phase Architecture**:

1. **Carry-Forward (Phase 1)**: Load previous `threats.md` as baseline, extract finding registry with fingerprints, verify each finding against current architecture, classify as UNCHANGED/UPDATED/RESOLVED.

2. **Isolated Discovery (Phase 2)**: Spawn a fresh discovery context with architecture input and a coverage summary only (component names + covered categories). Discovery agents receive NO full finding text from the baseline, preventing anchoring bias.

3. **Merge + Dedup (Phase 3)**: Match Phase 2 findings against baseline by (component, threat_category, `primaryLocationLineHash`). Duplicates discarded with baseline version winning. New findings assigned sequential IDs continuing from highest existing per category.

4. **Coverage Gate (Phase 4)**: Load `schemas/coverage-checklists.yaml`, check merged findings against required threat categories per component type (6 types including 2 AI subtypes). Flag gaps, trigger single-pass targeted re-analysis for missing categories.

**Fingerprint Correlation**:
- Primary key: `findingId/v1` (the finding ID itself, e.g., "S-3")
- Secondary key: `primaryLocationLineHash` (SHA-256 of `ruleId|component_name`, truncated to 16 hex characters)
- Deterministic tie-breaking: exact hash match > same component name > description similarity

**Delta Classification**:
- `NEW`: No baseline match. Score fresh with CVSS base bounded within +/-1.0 of category defaults.
- `UNCHANGED`: Baseline match with same assessment. Inherit all scores and control status.
- `UPDATED`: Baseline match with changed description or context. Re-score fresh.
- `RESOLVED`: Baseline finding with no current match. Retain last-known scores for audit.

---

## Rationale

**Reasons**:
1. **Deterministic by design**: Fingerprint-based correlation using SHA-256 hashing produces identical matches for identical inputs. No LLM judgment in the matching step -- only in the verification step (Phase 1) where agents assess whether a finding still applies.
2. **Anchoring bias prevention**: Phase 2 (Isolated Discovery) receives only a coverage summary, not full baseline findings. This ensures new threats are discovered based on the architecture, not influenced by what the baseline already found.
3. **Backward compatible**: When no baseline exists, the pipeline falls through to stateless mode (Phase 2 only), producing identical results to the pre-Feature-074 behavior. All schema and template changes are additive.
4. **Incremental efficiency**: UNCHANGED findings skip scoring and control re-scanning entirely. Only NEW and UPDATED findings trigger fresh analysis, reducing pipeline overhead for stable architectures.
5. **Coverage assurance**: The coverage gate catches blind spots caused by LLM non-determinism -- even if an agent fails to produce a finding for a required category, the gap is detected and targeted re-analysis is triggered.

---

## Alternatives Considered

### Alternative 1: Full Re-Run with Post-Hoc Diff

Run the pipeline fresh every time, then diff the results against the previous run to compute deltas.

**Pros**:
- Simplest implementation (no pipeline modification needed)
- Every finding is freshly scored (no inheritance questions)

**Cons**:
- 23% drift on unchanged codebases means phantom NEW/RESOLVED findings on every run
- No stable IDs -- finding IDs are reassigned each run, breaking remediation tracking
- Score drift makes compliance reporting unreliable (same finding, different scores)
- Full pipeline cost on every run (no incremental optimization)

**Why Not Chosen**: The core problem IS the drift from full re-runs. Post-hoc diffing cannot eliminate the variance inherent in LLM-based analysis; it can only report it.

### Alternative 2: Database-Backed Finding Registry

Store findings in a persistent database (SQLite or similar), correlate by database primary key.

**Pros**:
- Strong correlation guarantees via database-managed identifiers
- Efficient querying for historical trends
- Standard tooling for data management

**Cons**:
- Violates the file-based, local-first constraint (constitutional requirement)
- Introduces a runtime dependency (database engine)
- Cannot be embedded in agent prompt instructions
- Adds deployment complexity for adopters (database setup, migration management)

**Why Not Chosen**: tachi is a methodology template with no application code. All state must be representable in markdown, YAML, and SARIF files on the local filesystem.

### Alternative 3: Carry-Forward Only (No Fresh Discovery)

Load the baseline and only update existing findings. Skip independent discovery entirely.

**Pros**:
- Maximum stability (zero drift by definition)
- Simple implementation (one phase, no merge logic)

**Cons**:
- New threats introduced by architecture changes would never be discovered
- Coverage gaps from LLM non-determinism in the original run would persist forever
- Stale findings accumulate with no mechanism to discover new attack vectors
- Fundamentally undermines the purpose of threat modeling (finding NEW threats)

**Why Not Chosen**: A threat model that never discovers new threats is not a threat model. Fresh discovery is essential; the challenge is combining it with stability.

---

## Consequences

### Positive
- Zero drift on unchanged codebases (UNCHANGED findings inherit stable IDs and scores)
- Fix tracking works (RESOLVED findings retain stable IDs for audit trail)
- Coverage gate catches blind spots that LLM non-determinism would otherwise create
- Incremental efficiency for stable architectures (skip scoring and control scanning for UNCHANGED findings)
- All existing pipeline behavior preserved (stateless mode when no baseline)

### Negative
- Pipeline complexity increased (4 phases vs 1 phase in stateless mode)
- Coverage gate requires maintaining `schemas/coverage-checklists.yaml` configuration
- Baseline file must be parseable -- corrupted baselines trigger graceful degradation to stateless mode
- Sequential ID assignment creates ordering dependency (highest existing ID per category must be tracked)

### Mitigation
- Graceful degradation: unparseable baselines fall back to stateless mode with a warning
- Coverage checklist is static configuration with sensible defaults for all standard DFD types
- Sequential ID algorithm is deterministic and documented in `baseline-correlation.md` reference
- 4-phase pipeline only activates when a baseline is detected; first-run overhead is zero

---

## Related Decisions

- ADR-003: STRIDE-per-Element Dispatch (dispatch mechanism producing findings that are correlated)
- ADR-012: Cross-Agent Correlation Detection (intra-run correlation; ADR-018 addresses inter-run correlation)
- ADR-013: SARIF Output Format Adoption (SARIF `partialFingerprints` used as the correlation mechanism)

---

## References

- Feature 074 PRD: `docs/product/02_PRD/074-baseline-aware-pipeline-2026-03-31.md`
- Feature 074 spec: `specs/074-baseline-aware-pipeline/spec.md`
- Feature 074 plan: `specs/074-baseline-aware-pipeline/plan.md`
- Coverage checklists schema: `schemas/coverage-checklists.yaml`
- Baseline correlation reference: `.claude/skills/tachi-orchestration/references/baseline-correlation.md`
- Finding schema (v1.1 with delta fields): `schemas/finding.yaml`
