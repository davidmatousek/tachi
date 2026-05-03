# ADR-012: Deterministic Cross-Agent Correlation Detection

**Status**: Accepted
**Date**: 2026-03-22
**Deciders**: Architect
**Feature**: 010 (Deduplication & Risk Rating)

---

## Context

When STRIDE and AI threat agents analyze the same architecture, they frequently produce overlapping findings on the same component from different threat perspectives. For example, a Tampering finding and a Data-Poisoning finding on the same LLM pipeline both address data integrity -- one from the classic STRIDE lens, one from the AI-specific lens. Reporting these as independent findings inflates risk counts and obscures the actual threat landscape.

Key constraints:
- Correlation must be deterministic -- the same set of findings must always produce the same correlation groups.
- Original findings must be preserved for audit (correlation is additive, not destructive).
- The algorithm must be embeddable in a prompt file with no runtime dependencies.
- Coverage matrix and risk summary must reflect deduplicated counts.
- Single-pass execution: correlation runs once after all agents complete, before coverage matrix generation.

---

## Decision

We will use **deterministic rule-based correlation** with 5 fixed STRIDE-to-AI category pairing rules. Findings are grouped by target component first, then matched against the rule table. Each finding belongs to at most one correlation group.

**Correlation Rules**:

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

**Algorithm**:
1. Group all findings by target component
2. Within each component group, check each cross-category finding pair against the 5 rules
3. When a match is found, create a correlation group (CG-N)
4. If multiple rules match findings on the same component, merge all matched findings into one group
5. Each finding belongs to at most one correlation group
6. Self-check: verify no finding appears in more than one group

---

## Rationale

**Reasons**:
1. **Deterministic by design**: 5 fixed rules with exact category matching. No fuzzy matching, no LLM judgment, no threshold tuning. Same findings always produce the same groups.
2. **Auditable**: Each correlation group references the specific rule (CR-N) that triggered it and lists all member finding IDs. Reviewers can trace why findings were correlated.
3. **Non-destructive**: Original findings remain in their STRIDE and AI tables. Correlation groups are presented in a separate Section 4a. Deduplication affects only counts in the coverage matrix and risk summary.
4. **Embeddable**: The rule table and algorithm are expressed as structured text in the orchestrator prompt. No external correlation engine or runtime dependency required.
5. **Conservative scope**: 5 rules covering the most common cross-category overlaps. New rules can be added without modifying the algorithm or existing rules.

---

## Alternatives Considered

### Alternative 1: LLM-Judged Semantic Similarity

Let the LLM decide whether two findings on the same component are semantically similar enough to correlate.

**Pros**:
- Could detect correlations not anticipated by fixed rules
- Handles edge cases where category labels differ but threats overlap

**Cons**:
- Non-deterministic: same findings may produce different correlations across runs
- Not auditable: correlation reasoning is opaque
- Higher token cost: requires pairwise comparison reasoning
- Risk of over-correlation: similar-sounding findings may address distinct threats

**Why Not Chosen**: Determinism and auditability are critical for security analysis outputs. Fixed rules ensure reproducible, explainable correlation decisions.

### Alternative 2: Finding Deduplication by Mitigation Similarity

Correlate findings that recommend the same or similar mitigations, regardless of threat category.

**Pros**:
- Captures operational overlap (same fix addresses multiple findings)
- Category-agnostic, potentially broader coverage

**Cons**:
- Mitigation text varies significantly across agents even for the same underlying fix
- Would require fuzzy text matching or LLM judgment (non-deterministic)
- Conflates "same fix" with "same threat" -- findings with the same mitigation may address genuinely distinct attack vectors

**Why Not Chosen**: Mitigation similarity does not imply threat equivalence. The category-pairing approach directly maps the semantic relationship between threat perspectives.

### Alternative 3: No Deduplication (Status Quo)

Keep all findings as independent entries with inflated counts.

**Pros**:
- Simplest implementation (no changes needed)
- No risk of incorrectly merging distinct findings

**Cons**:
- Inflated risk counts mislead security reviewers
- Coverage matrix suggests more findings than the actual distinct threat count
- Users manually correlate findings, which is error-prone

**Why Not Chosen**: The primary PRD requirement (FR-1 through FR-11) specifically calls for deduplication to improve the accuracy and usability of threat model outputs.

---

## Consequences

### Positive
- Coverage matrix and risk summary show accurate deduplicated counts
- Correlation groups surface cross-domain threat patterns that individual agent views miss
- Schema version bump (1.0 to 1.1) with backward-compatible additive section
- Three-state coverage matrix cell model (count, "---", "n/a") improves readability

### Negative
- 5 rules cover only the most obvious cross-category overlaps; edge-case correlations may be missed
- Adding new rules requires orchestrator prompt modification
- Correlation groups add a new section (4a) that readers must understand

### Mitigation
- Rule set is extensible: new rules follow the same CR-N pattern with no algorithm changes
- Section 4a includes a "no correlations detected" message when zero groups exist, so the section is never confusing
- Self-check validation ensures no finding appears in multiple groups

---

## Related Decisions

- ADR-003: STRIDE-per-Element Dispatch (dispatch mechanism that produces the findings being correlated)

---

## References

- Feature 010 spec: `specs/010-prd-010-deduplication/spec.md`
- Feature 010 plan: `specs/010-prd-010-deduplication/plan.md`
- Interface contract (correlation rules): `docs/INTERFACE-CONTRACT.md` Section 3
- Output schema: `schemas/output.yaml` (schema_version 1.1)
