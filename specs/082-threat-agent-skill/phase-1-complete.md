---
feature: 082-threat-agent-skill
wave: Wave 8 (Phase 3.3 — ADR-023 Acceptance + Phase 1 Combined Checkpoint)
date: 2026-04-11
tasks_covered: [T022, T023]
gate_name: Gate C — Phase 1 Combined Checkpoint
guardian: architect
exit_criterion: E-4 (partially validated — see §2.4)
status: PASSED
phase_1_outcome: Sibling-variant pattern structurally validated on n=2 across STRIDE (spoofing) and AI (prompt-injection) tiers; Phase 4+5 rollout unblocked
branch: 082-threat-agent-skill
---

# Phase 1 Combined Checkpoint — Feature 082

**Gate**: C — Phase 1 Combined Checkpoint
**Entry criterion**: T022 complete (ADR-023 `Status: Accepted`)
**Exit criterion**: `phase-1-complete.md` (this document) written and committed; Waves 9-11 Phase 4+5 rollout unblocked
**Iteration budget**: N/A (this checkpoint is a non-iterating summary gate — Gate A/B iteration budgets are independent and already used)

---

## 1. Gate Criteria

Per plan.md §1 Technical Context, tasks.md T023 task text, and agent-assignments.md §4 Gate C definition, the Phase 1 Combined Checkpoint passes when ALL of the following are true:

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Phase 1a gate (Gate A) passed with ≥1 iteration remaining | T015 joint ruling: APPROVED_WITH_CONCERNS, iteration 1/2 used, 1 remaining | PASS |
| 2 | Phase 1b gate (Gate B) passed with ≥1 iteration remaining | T021 joint ruling: APPROVED_WITH_CONCERNS, iteration 1/2 used, 1 remaining (Phase 1b sub-budget independent of Phase 1a) | PASS |
| 3 | ADR-023 `Status: Accepted` header present | T022 complete — ADR-023 header Line 3 now reads `**Status**: Accepted`; Line 4 adds `**Accepted**: 2026-04-11 (post Phase 1 combined checkpoint / T023, Feature 082 Wave 8)` | PASS |
| 4 | E-4 exit criterion met (load-shape variant declared in ADR-023 §Decision 1) | ADR-023 §Decision 1 "Sibling Variant with Single-Point Load" declares the single-point load at the start of `## Detection Workflow`; §Phase 1 Validation item 6 scopes E-4 to "partially validated on n=2" with full n=11 generalization deferred to Phase 4+5 Waves 9-11 | PASS (see §2.4 for partial-validation scope) |
| 5 | Phase 1 Validation section appended to ADR-023 with ≥6 items (2 from T015 + 4 from T021) | ADR-023 §Phase 1 Validation contains 6 items: (1) sibling variant structurally validated on n=2 across tiers, (2) 5-section canonical shape ratified (Option A), (3) ±2 tolerance interpretation (b) ratified, (4) Option B methodology valid with asymmetry caveat, (5) overlap acceptable now with re-audit at T047 via additive-signal test, (6) E-4 partially validated with n=11 generalization deferred | PASS |
| 6 | 3 Wave 8 housekeeping items from T021 concerns landed before Wave 9 entry | H1: plan.md Technical Context §Testing amended with ±2 tolerance interpretation (b) sentence. H2: tasks.md T022 task text expanded to document 5-section canonical shape. H3: tasks.md T038 and T040 annotated with AML.T0058 duplication-allowed-until-T047 clarification. | PASS |

**Overall Gate C verdict**: **PASSED**. All 6 criteria satisfied. No iteration required. Phase 4+5 rollout (Waves 9-11) and Phase 6-8 downstream are unblocked.

---

## 2. Phase 1 Outcome Summary

### 2.1 What Phase 1 Proved

Phase 1 is a **prototype validation gate** scoped to n=2 of the 11 threat agents — one STRIDE-tier agent (`spoofing.md`) and one AI-tier agent (`prompt-injection.md`). The gate's purpose per FR-12 is to validate the sibling-variant extraction pattern in the small, before the full 11-agent rollout amplifies any pattern mismatch by 5.5×.

The following is now empirically true on n=2:

- **Structural validation (Decision 1)**: The single-point-load variant of the lean + skill references pattern applies to detection agents on both tiers. A `## Detection Workflow` section with one `**MANDATORY**: Read` directive at its start correctly loads a companion `detection-patterns.md` reference file on agent invocation. The refactored agent files (51 lines spoofing, 95 lines prompt-injection post-consistency-fix) satisfy both the STRIDE and AI tier caps (≤120 and ≤150 respectively) with substantial headroom against the 180-line hard ceiling.

- **Content equivalence (Option B methodology)**: The refactored agent + companion reference pair produces detection output equivalent to the pre-refactor self-contained file because the refactor is a pure content move — every pattern category, bullet, trigger keyword, and source citation from the pre-refactor inline content is preserved byte-verbatim in the new companion reference, or delegated to shared refs that existed pre-082. Zero content delta against the T001 baselines for both touched agents.

- **MAESTRO boundary (Decision 2)**: Neither touched agent file nor its companion reference file contains a single MAESTRO reference (`grep -i maestro` returns zero matches across all 4 files). The orchestrator-owned boundary from ADR-020 now extends to the detection-tier reference files without leakage.

- **Enrichment is first-class (FR-7, User Story 5)**: The Phase 1b enrichment sub-phase added 5 new detection pattern categories across the two prototype agents (2 spoofing + 3 prompt-injection) drawn from the approved primary source set (OWASP, CWE, MITRE ATT&CK/ATLAS, Unicode TR, Greshake 2023). All 5 cite primary sources with canonical URLs; 5/5 fit the respective taxonomy; 4/5 are partial-overlap-justified with additive signal; 1/5 is NO-OVERLAP. Projection to 11 agents at the observed 2.5 categories/agent average yields 23-32 new categories, comfortably above the SC-006 ≥22 floor.

### 2.2 What Phase 1 Did NOT Prove

Phase 1 does **not** prove that the sibling variant applies to the remaining 9 threat agents (tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, data-poisoning, model-theft, tool-abuse, agent-autonomy). This is by design — gate sequencing is prototype-first precisely to bound the cost of discovering a pattern mismatch to 2 agents rather than 11. Full generalization is the scope of Phase 4+5 (Waves 9-11), and each sub-wave implicitly re-validates the pattern on 3 additional agents.

The pre-refactor audit identified no control-flow shape in any of the 9 remaining agents that would require a different variant — all 11 threat agents are single-pass (match → apply → emit), none are multi-phase like control-analyzer. But "no known risk" is not "zero risk", and the Phase 4+5 waves bear the burden of empirical generalization.

### 2.3 Open Concerns Carried Forward

These concerns are non-blocking for Phase 4+5 entry but are load-bearing for downstream gates. They are listed here to ensure downstream waves do not rediscover them.

| ID | Source | Concern | Wave(s) to address | Blocking? |
|----|--------|---------|---------------------|-----------|
| C-1 | T020 / T021 C4 | GCP/Azure canonical docs missing for Spoofing C7 (Cloud IAM Role Assumption Chain Abuse) — AWS-centric citations only | T048 (Wave 13 Phase 7 enrichment review) | No — non-blocking WARN |
| C-2 | T020 / T021 C4 | Unicode TR36 / TR39 citations would strengthen Prompt-Injection C8 (Evasion via Encoding) — primary source stack is already authoritative | T048 (Wave 13 Phase 7 enrichment review) | No — supplementary |
| C-3 | T020 / T021 C4 | Greshake et al. 2023 citation in Prompt-Injection C7 lacks inline arXiv URL — authoritative as named peer-reviewed work | T048 (Wave 13 Phase 7 enrichment review) | No — navigability |
| C-4 | T021 | AML.T0058 ("Agent Context Poisoning") canonical owner undecided between tool-abuse (T038) and agent-autonomy (T040). Housekeeping item 3 in Wave 8 (task-text clarification) permits duplicated extraction in the interim. | T047 (Wave 13 cross-agent overlap audit) | No — duplication-allowed-until-T047 |
| C-5 | T021 | Option B methodology has asymmetric strength. At T047 / T050 aggregate scale, Option A (live `/tachi.threat-model` invocation) is preferred if operationally feasible. | T047 (Wave 13), T050 (Wave 15 Full Regression Gate) | No — methodology preference |
| C-6 | T021 / ADR-023 §Phase 1 Validation item 6 | E-4 exit criterion is only partially validated on n=2. Full n=11 generalization is the burden of Phase 4+5. | Waves 9-11 | Partial — E-4 upgraded incrementally |
| C-7 | T021 | Agent-autonomy pre-refactor baseline is 201 lines. Target ≤150 (AI tier), hard ceiling 180. If extraction cannot hit ≤150 with inline example findings preserved, trigger Q7 contingency (migrate example findings to companion `example-findings.md`) — **inside Wave 11**, not deferred. | Wave 11 Track 3 | Watch-item |

### 2.4 E-4 Scope Clarification

Exit criterion E-4 in FR-13 reads: "sibling-variant load-shape documented in ADR-023 (exit criterion E-4)". The literal requirement — that ADR-023 declare the load-shape variant — is satisfied by ADR-023 Decision 1 as of T022. The Phase 1 Combined Checkpoint records this in the narrowest sense: the ADR says what Decision 1 says it says. Waves 9-11 inherit the burden of **validating that the declared shape actually works on the other 9 agents**. Per ADR-023 §Phase 1 Validation item 6, this is an intentional scope split: Phase 1 proves the shape is declared and prototype-validated, Phase 4+5 prove it generalizes.

Should a Phase 4+5 wave surface an agent whose control flow cannot fit single-point-load (low-probability per the pre-refactor source audit), the escalation path is to amend ADR-023 Decision 1 in place (still Accepted, revision tracked in git history) or to open a new ADR sibling-to-023 for the third variant. In either case, the Phase 1 Combined Checkpoint does NOT need to be re-run — it already accepted the partial-validation framing.

---

## 3. Gate Progression Summary

### Gates Passed Before This Checkpoint

| Gate | Wave | Iteration Used | Reserve | Ruling | Artifact |
|------|------|----------------|---------|--------|----------|
| A — Phase 1a refactor-only (T015) | 5 | 1 of 2 | 1 | APPROVED_WITH_CONCERNS | `specs/082-threat-agent-skill/phase-1a-regression.md` §T015 |
| B — Phase 1b enrichment (T021) | 7 | 1 of 2 (Phase 1b sub-budget, independent of A) | 1 | APPROVED_WITH_CONCERNS | `specs/082-threat-agent-skill/phase-1b-regression.md` §T021 |
| C — Phase 1 combined checkpoint (T023) | 8 (this wave) | 0 of 1 (no iteration budget — single-run summary gate) | N/A | **PASSED** | This document |

### Gates Remaining

| Gate | Wave | Purpose |
|------|------|---------|
| D — Full Regression Gate (T050) | 15 | SC-005 thresholds on all 6 examples post full 11-agent rollout |
| Informal — Phase 6 single-writer checkpoint | 12 | Shared-ref consolidation byte-level diff verification |
| Informal — Phase 7 aggregate enrichment floor | 14 | T049 tally ≥22 against T003 baseline |
| Informal — Phase 8 PDF re-baseline | 17 | 5 baselines regenerated under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 |

---

## 4. Downstream Wave Unblock Status

Per the gate passage above, the following are now unblocked:

- **Wave 9 Phase 4+5 Sub-Wave A** (T024+T025 tampering, T034+T035 data-poisoning, T036+T037 model-theft) — 3 parallel `senior-backend-engineer` tracks
- **Wave 10 Phase 4+5 Sub-Wave B** (T026+T027 repudiation, T028+T029 info-disclosure, T038+T039 tool-abuse with ATLAS Oct 2025 focus)
- **Wave 11 Phase 4+5 Sub-Wave C** (T030+T031 denial-of-service, T032+T033 privilege-escalation, T040+T041 agent-autonomy with tier-cap watch per C-7 above)

Wave 12 (Phase 6 serial single-writer shared-ref consolidation) and beyond remain gated on Wave 11 completion — their entry conditions are downstream and do not require this checkpoint to be re-run.

---

## 5. Traceability

| Artifact | Path | Role |
|----------|------|------|
| ADR-023 (Accepted) | `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` | Architectural decision record, Status: Accepted as of 2026-04-11 |
| Phase 1a regression + T015 ruling | `specs/082-threat-agent-skill/phase-1a-regression.md` | Gate A evidence |
| Phase 1b regression + T021 ruling | `specs/082-threat-agent-skill/phase-1b-regression.md` | Gate B evidence |
| This checkpoint | `specs/082-threat-agent-skill/phase-1-complete.md` | Gate C evidence |
| Plan amendment (±2 tolerance b) | `specs/082-threat-agent-skill/plan.md` Technical Context §Testing | Wave 8 housekeeping 1 |
| T022 task text expansion | `specs/082-threat-agent-skill/tasks.md` L103 | Wave 8 housekeeping 2 |
| T038 / T040 AML.T0058 clarification | `specs/082-threat-agent-skill/tasks.md` T038, T040 | Wave 8 housekeeping 3 |
| Architect T015 ruling (local) | `.aod/results/architect-t015-phase-1a-gate.md` | Local-only reviewer evidence |
| Team-lead T015 ruling (local) | `.aod/results/team-lead-t015-phase-1a-gate.md` | Local-only reviewer evidence |
| Architect T021 ruling (local) | `.aod/results/architect-t021-phase-1b-gate.md` | Local-only reviewer evidence |
| Team-lead T021 ruling (local) | `.aod/results/team-lead-t021-phase-1b-gate.md` | Local-only reviewer evidence |

---

## 6. Signed Approval

```yaml
gate: C — Phase 1 Combined Checkpoint
feature: 082-threat-agent-skill
status: PASSED
date: 2026-04-11
guardian: architect
exit_criterion_e_4: PASSED (partially validated on n=2; full n=11 generalization deferred to Waves 9-11 per ADR-023 §Phase 1 Validation item 6)
housekeeping_complete:
  h1_plan_fr13_amendment: true
  h2_t022_task_text_expansion: true
  h3_aml_t0058_clarification: true
adr_023_status: Accepted
phase_4_plus_5_unblocked: true
next_gate: D — Full Regression Gate (T050) at end of Wave 15 (post Phase 7 aggregate enrichment floor confirmation at T049 Wave 14)
```

**Phase 1 complete.** Feature 082 proceeds to Phase 4+5 rollout (Waves 9-11) on 9 remaining threat agents.
