# P1 Architect Checkpoint Review

**Feature**: 074 — Baseline-Aware Pipeline
**Checkpoint**: P1 (after Waves 0-4, 22/36 tasks)
**Reviewer**: Architect
**Date**: 2026-03-31
**Status**: APPROVED_WITH_CONCERNS

---

## Executive Summary

The core baseline-aware pipeline architecture is technically sound. The 4-phase pipeline (Carry-Forward, Isolated Discovery, Merge+Dedup, Coverage Gate) is well-specified with clear boundaries between phases. The deterministic similarity algorithm, bounded scoring, RESOLVED detection, and governance carry-forward are all substantially correct and implementation-ready. Two medium-severity consistency issues require resolution in Waves 5-6 before the feature ships.

---

## Checklist Results

### PASS Items

- [x] **Merge/dedup algorithm (Phase 3a) is deterministic and well-specified**
  The algorithm in `orchestrator.md` (lines 706-746) specifies a clear two-step process: exact match first via `primaryLocationLineHash`, then fuzzy similarity match. The candidate pool exhaustion rule (each carry-forward matched at most once) ensures determinism. The self-check (lines 740-745) adds a verification layer.

- [x] **Similarity threshold (>80%) is documented with rationale**
  Both the orchestrator agent (line 715) and skill SKILL.md (line 105) document `sim > 0.80` (strictly greater than) with the rationale: "accommodates minor wording variations from LLM non-determinism while filtering out genuinely different threats." The baseline-wins policy is consistently stated in both locations.

- [x] **Exact-match-first strategy correctly prioritizes primaryLocationLineHash before fuzzy matching (C-5)**
  Phase 3a step 1 (orchestrator line 710) explicitly checks `primaryLocationLineHash` exact match first, before falling through to similarity computation. The baseline-correlation reference (lines 78-93) reinforces the same priority. This fully addresses the architect C-5 concern from the plan review.

- [x] **Tie-breaking rules are unambiguous and handle all edge cases**
  Two tie-breaking scenarios are covered: (1) multiple Phase 2 findings matching one carry-forward (orchestrator lines 722-725; skill lines 111-114); (2) one Phase 2 finding matching multiple carry-forwards (orchestrator lines 727-730). Both converge on the same three-tier priority: similarity score, component name match, output order. The candidate pool removal rule prevents double-matching.

- [x] **Bounded scoring applies only to NEW findings, not UPDATED**
  The applicability table in the skill SKILL.md (lines 56-61) and the risk-scorer agent (lines 406-431) both explicitly restrict bounding to `delta_status: NEW`. UPDATED, UNCHANGED, and RESOLVED findings are excluded with documented rationale for each.

- [x] **Score bounding formula handles edge cases at CVSS extremes (0.0, 10.0)**
  The risk-scorer agent (line 435) and the skill SKILL.md (lines 63-65) both document extreme cases: category default 9.5 produces range 8.5-10.0, default 1.0 produces 0.0-2.0. The outer clamp to [0.0, 10.0] is explicit in the formula. The `score_bounds` schema in `risk-scoring.yaml` (lines 93-108) also constrains the range fields to [0.0, 10.0].

- [x] **RESOLVED detection covers component removal, category inapplicability, partial fixes, and renames**
  The orchestrator (lines 446-475) documents all four cases with explicit classification rules:
  - Component removal: RESOLVED with reason template
  - Category inapplicability: RESOLVED with reason template
  - Partial fix: Classified as UPDATED (not RESOLVED) — correct, as partial fixes do not eliminate the threat
  - Component rename: Classified as UPDATED (not RESOLVED + NEW) using `primaryLocationLineHash` matching — prevents spurious resolved/new pairs

- [x] **Governance carry-forward correctly preserves risk_owner (never auto-overwritten)**
  The risk-scorer agent (lines 503-531) and skill SKILL.md (lines 76-91) state three times that `risk_owner` is "never auto-overwritten" — for UNCHANGED (preserve), UPDATED (preserve always, including across severity band changes), and RESOLVED (retain from baseline). Line 522 adds emphasis: "Only a human can change risk_owner."

- [x] **SLA recalculation triggers only on severity band change**
  The risk-scorer agent (lines 516-522) explicitly defines the trigger: compare baseline severity band to current band. Same band = preserve all governance fields. Band changed = recalculate SLA, review_date, and disposition (but never risk_owner). The disposition threshold (Critical/High = Mitigate, Medium/Low = Review) is consistent with `risk-scoring.yaml` (lines 66-72).

- [x] **Isolated discovery context excludes finding text but includes coverage summary**
  The orchestrator (lines 598-633) provides a clear inclusion/exclusion table. Finding descriptions, risk scores, mitigation text, and finding IDs are all excluded. Coverage summary (component names + covered categories only) is included as a "hint, not a constraint." The rationale (preventing anchoring bias) references SC-004.

- [x] **Delta summary section is additive (only present with baseline)**
  The orchestrator (line 1110) states: "When no baseline is present: Do not include the delta summary section. The output ends after Section 7 as in pre-baseline behavior." This preserves backward compatibility.

- [x] **Resolved findings section (4b) preserves audit trail fields**
  The threats.md template (lines 356-382) defines Section 4b with all required audit fields: ID, Component, Threat, Last Risk Level, Resolution Reason. The conditional rendering rules are clear: omit entirely on first run, include header with empty message when baseline present but nothing resolved.

- [x] **No breaking changes to existing pipeline behavior without baseline**
  Multiple files confirm stateless mode equivalence: orchestrator (line 58), skill SKILL.md (lines 39, 68), risk-scorer (line 77), control-analyzer (line 128). All converge on: "no baseline = identical to pre-baseline behavior."

### CONCERN Items (2 Medium)

#### C-1 (Medium): Similarity Algorithm Inconsistency Between Orchestrator and Skill

**Files**: `orchestrator.md` line 714 vs. `SKILL.md` lines 96-101

The orchestrator agent defines the similarity formula as:

```
1.0 - (levenshtein_distance(tokens_a, tokens_b) / max(len(tokens_a), len(tokens_b)))
```

Where `tokens_a` and `tokens_b` are token lists, and `len()` operates on list length (token count).

The skill SKILL.md defines the similarity formula as:

```
sim = 1.0 - (dist / max(len(str_A), len(str_B)))
```

Where `str_A` and `str_B` are joined strings, and `len()` operates on string character length.

These are mathematically different operations:
- Token-list Levenshtein measures edit distance in token units (insertions/deletions/substitutions of whole tokens), normalized by token count.
- String Levenshtein measures edit distance in character units, normalized by character count.

The skill SKILL.md preprocessing pipeline (steps 1-4) is more detailed and specifies the join step (step 1 of Similarity Computation), which the orchestrator omits. The orchestrator appears to describe a token-level algorithm while the skill describes a character-level algorithm on joined tokens.

**Impact**: An LLM executing the orchestrator instructions could produce different similarity scores than one executing the skill instructions. This violates the determinism guarantee.

**Recommendation**: Align the orchestrator's Phase 3a description to reference the skill's algorithm as authoritative. The orchestrator should state: "Compute description similarity per the Deterministic Similarity Algorithm in the tachi-orchestration skill" and remove the inline formula. The skill already provides the complete specification. Alternatively, update the orchestrator's inline formula to match the skill (character-level Levenshtein on joined sorted tokens).

#### C-2 (Medium): Category Default Mismatch Between Risk-Scorer and Schema

**Files**: `risk-scorer.md` lines 415-429 vs. `risk-scoring.yaml` lines 111-119

The risk-scorer agent's bounded scoring table lists 11 categories with numeric CVSS defaults:

```
spoofing: 7.5, tampering: 7.0, repudiation: 4.0, info-disclosure: 6.5,
denial-of-service: 6.0, privilege-escalation: 8.0, prompt-injection: 8.5,
data-poisoning: 7.0, model-theft: 7.5, agent-autonomy: 7.0, tool-abuse: 7.5
```

The authoritative schema (`risk-scoring.yaml`) lists 8 categories with CVSS *vectors* (not numeric scores):

```
spoofing, tampering, repudiation, info-disclosure, denial-of-service,
privilege-escalation, agentic, llm
```

Two discrepancies exist:

1. **Category granularity mismatch**: The schema uses `agentic` (single category) and `llm` (single category), while the risk-scorer uses `agent-autonomy`, `tool-abuse` (splitting agentic) and `prompt-injection`, `data-poisoning`, `model-theft` (splitting llm). The finding.yaml schema (line 30-38) uses `agentic` and `llm` as the canonical category enum values, consistent with the risk-scoring.yaml.

2. **Default representation**: The risk-scorer cites numeric defaults (e.g., "spoofing: 7.5"), but the schema stores CVSS vectors. The numeric scores must be derived from the vectors, and the derivation is not documented. The risk-scorer correctly notes "authoritative values in `schemas/risk-scoring.yaml`", but the inline table uses a finer category granularity than the schema supports.

**Impact**: An agent scoring a finding with `category: "agentic"` (per finding.yaml) would not find a matching entry in the risk-scorer's 11-category bounded scoring table, which uses `agent-autonomy` and `tool-abuse` instead. The agent would need to infer which sub-category applies, introducing non-determinism.

**Recommendation**: Either (a) add the 11 sub-category defaults to `risk-scoring.yaml` as a `bounded_scoring_defaults` section distinct from `category_defaults`, making the schema the single source of truth for both vector defaults and bounding ranges; or (b) align the risk-scorer's table to use the 8 canonical categories from finding.yaml, applying the `agentic` vector default to both agent-autonomy and tool-abuse findings, and the `llm` vector default to prompt-injection, data-poisoning, and model-theft findings.

### LOW Items (2 Informational)

#### L-1 (Low): Stopword Lists Should Be Cross-Referenced

The stopword list appears in three locations: orchestrator.md (line 713), SKILL.md (line 90), and nowhere in a schema file. If the list ever needs to change, it must be updated in multiple places. Consider extracting the canonical stopword list to a schema or reference file, with both the orchestrator and skill referencing it.

#### L-2 (Low): Delta Summary Grouping Order Rationale

The delta summary grouping order (RESOLVED first, then NEW, UPDATED, UNCHANGED) in orchestrator line 1108 is described as "most actionable to least actionable." This rationale is sound, but the skill SKILL.md does not mention grouping order. If a future implementer references only the skill, they would miss this ordering requirement. Consider adding the grouping order to the skill's baseline-correlation reference.

---

## Previous Architect Concerns — Status

| ID | Concern | Status | Evidence |
|----|---------|--------|----------|
| C-3 | primaryLocationLineHash role documented as validation signal | RESOLVED | Orchestrator skill SKILL.md lines 68-76: "secondary signal, not a primary key" |
| C-5 | >80% similarity must specify deterministic algorithm | PARTIALLY RESOLVED | Algorithm specified in skill SKILL.md lines 83-116 (fully deterministic). Residual issue: orchestrator describes a different formula (see C-1 above) |

---

## Verdict

**STATUS: APPROVED_WITH_CONCERNS**

The architecture is sound and implementation can proceed to Waves 5-6. The two medium concerns (C-1: similarity formula inconsistency, C-2: category default mismatch) must be resolved before the feature ships but do not block ongoing work, as they affect merge/dedup behavior and bounded scoring — both of which are already implemented and can be corrected in a follow-up task.

**Blocking for ship (not for continued development)**:
- C-1: Align similarity formula between orchestrator and skill
- C-2: Resolve category granularity mismatch between risk-scorer and schema

**Non-blocking (informational)**:
- L-1: Extract stopword list to a single source of truth
- L-2: Add delta summary grouping order to skill reference
