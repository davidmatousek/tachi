# Agent Assignments: Feature 194 — Coverage Attestation Report Section

**Feature**: 194
**Timeline**: 2026-04-20 (Mon) → 2026-04-23 (Thu) — 4 days (32h envelope)
**Total tasks**: 46 (44 in-window, 1 verification checkpoint T001, 1 post-merge T044)
**Triple sign-off**: PM APPROVED (2026-04-18) + Architect APPROVED (2026-04-18) + Team-Lead APPROVED_WITH_CONCERNS (2026-04-18)
**Critical path**: T002 → T007 → T011 → T024-T027 → T012-T014 → T015 → T043 → T046 (~18-22h sequential within 32h envelope)

---

## Agent Assignment Matrix

| Task | Agent | Day | Parallel? | Notes |
|------|-------|-----|-----------|-------|
| T001 | team-lead | Day 0 | — | Verification checkpoint (feature branch already exists; no work) |
| T002 | architect | Day 1 AM | sequential | ADR-029 Proposed — 7 decision surfaces per FR-013; cites Features 128 + 141 (architect L-3) |
| T003 | architect | Day 1 AM | [P] | Q5 fallback memo at `specs/194-.../q5-visual-treatment-architect-fallback.md` (team-lead L1 safety net) |
| T004 | tester | Day 1 | [P] | 3 fixtures under `tests/scripts/fixtures/coverage_attestation/` (empty / one_primary / multi_mixed) |
| T005 | tester | Day 1 | [P] | Zero-denominator synthetic fixture — MUST NOT modify `schemas/taxonomy/` (architect M-3) |
| T006 | senior-backend-engineer | Day 1 | [P] | Typst skeleton `templates/tachi/security-report/coverage-attestation.typ` |
| T007 | senior-backend-engineer | Day 1 | [P] | `compute_has_source_attribution` stub in `scripts/extract-report-data.py` |
| T008 | tester | Day 2 AM | [P] [US3] | TDD test — `test_has_source_attribution_false_on_empty_fixture` |
| T009 | tester | Day 2 AM | [P] [US3] | TDD test — `test_has_source_attribution_true_on_one_primary_fixture` |
| T010 | tester | Day 2 AM | [P] [US3] | TDD test — `test_default_value_guard_stale_report_data` (subprocess typst compile) |
| T011 | senior-backend-engineer | Day 2 AM | sequential | Implement `compute_has_source_attribution` — uses `_typst_bool()` Feature 141 helper |
| T012 | senior-backend-engineer | Day 3 AM | sequential (main.typ) | 3 default-value guards atomic edit block ~lines 89-107 (architect L-1; re-validate line range per team-lead L2) |
| T013 | senior-backend-engineer | Day 3 AM | sequential (main.typ) | `#import "coverage-attestation.typ"` in imports block ~lines 43-47 |
| T014 | senior-backend-engineer | Day 3 AM | sequential (main.typ) | Conditional inclusion block AFTER findings-detail (~:393), BEFORE compensating-controls (:398) per architect M-1 |
| T015 | tester | Day 4 AM | BLOCKER gate | SC-002 byte-identity regression on 5 non-agentic baselines under SOURCE_DATE_EPOCH=1700000000 |
| T016 | senior-backend-engineer | Day 3 PM | sequential | `#import` byte-identity smoke (architect MED-5) — subset of T015 |
| T017 | tester | Day 2 AM | [P] [US2] | TDD test — `test_per_framework_aggregates_emits_exactly_5_records` |
| T018 | tester | Day 2 AM | [P] [US2] | TDD test — `test_partition_invariant` (covered + partial + gap == yaml_record_count) |
| T019 | tester | Day 2 AM | [P] [US2] | TDD test — `test_classification_rules_q1_a` (Q1-A 3-value classification) |
| T020 | tester | Day 2 AM | [P] [US2] | TDD test — `test_coverage_percentage_arithmetic` |
| T021 | tester | Day 2 AM | [P] [US2] | TDD test — `test_coverage_percentage_na_on_zero_denominator` |
| T022 | tester | Day 2 AM | [P] [US2] | TDD test — `test_coverage_percentage_0pct_on_zero_numerator` |
| T023 | tester | Day 2 AM | [P] [US2] | TDD test — `test_aggregator_fails_loud_on_malformed_yaml` (ADR-022 fail-loud) |
| T024 | senior-backend-engineer | Day 2 AM | sequential-within-agent | `load_framework_yaml_record_counts` — loads 5 external-framework YAMLs (same file: `scripts/extract-report-data.py`) |
| T025 | senior-backend-engineer | Day 2 PM | sequential-within-agent | `classify_framework_items` — Q1-A classification (same file) |
| T026 | senior-backend-engineer | Day 2 PM | sequential-within-agent | `build_per_framework_aggregate` — percentages + N/A + 0.00% edges (same file) |
| T027 | senior-backend-engineer | Day 2 EOD | sequential-within-agent | Wire aggregator invocation — emits `per-framework-aggregates` to Typst data contract (same file) |
| T028 | senior-backend-engineer | Day 3 AM | sequential | Per-framework matrix page body in `coverage-attestation.typ` — 5 pages always |
| T029 | senior-backend-engineer | Day 3 AM | sequential | Gap item highlighting (uses T003 architect fallback if ux-ui-designer memo absent) |
| T030 | senior-backend-engineer | Day 3 AM | sequential | MITRE per-framework split preserved — `mitre-attack` + `mitre-atlas` as 2 separate pages (architect L-2) |
| T031 | tester | Day 2 AM | [P] [US1] | TDD test — `test_per_finding_row_count_matches_finding_count` |
| T032 | tester | Day 2 AM | [P] [US1] | TDD test — `test_per_finding_row_mitre_merge_with_prefix` (ATT&CK: / ATLAS: prefix) |
| T033 | tester | Day 2 AM | [P] [US1] | TDD test — `test_per_finding_row_grouping_by_taxonomy` |
| T034 | tester | Day 2 AM | [P] [US1] | TDD test — `test_per_finding_row_preserves_input_order` |
| T035 | senior-backend-engineer | Day 2 PM-EOD | sequential-within-agent | `build_per_finding_rows` — MITRE merge with per-ref prefix (same file: `scripts/extract-report-data.py`; serialize after T024-T027 per team-lead M1) |
| T036 | senior-backend-engineer | Day 2 EOD | sequential-within-agent | Wire per-finding emission — `per-finding-rows` to Typst data contract (same file) |
| T037 | senior-backend-engineer | Day 3 PM | sequential | Per-finding attribution table in `coverage-attestation.typ` — 7 columns, bold primary / plain related/derived |
| T038 | senior-backend-engineer | Day 3 PM (Day 4 AM slip pre-approved) | sequential | Pagination smoke fixture + smoke test — **slip-to-Day-4 pre-approved** per team-lead M2 |
| T039 | team-lead | Day 2 EOD | — | F-A3 merge-order coordination check (~48h escalation runway; PRD A7 fallback pre-approved) |
| T040 | security-analyst | Day 4 AM | [P] | Zero-edit invariant grep audit — SC-009 BLOCKER gate (22-file invariant per ADR-023 + ADR-028) |
| T041 | security-analyst | Day 4 AM | [P] | Zero-dependency diff audit — SC-008 BLOCKER gate (`pyproject.toml`, `requirements*.txt`, `package.json`) |
| T042 | tester | Day 4 AM | sequential | `quickstart.md` 9-step validation walkthrough — end-to-end feature correctness |
| T043 | architect | Day 4 PM | sequential | ADR-029 Proposed → Accepted transition (provisional merge-date 2026-04-23, placeholder merge-sha) |
| T044 | architect | Post-merge | — | Post-merge SHA fill on ADR-029 (Feature 180/189 precedent; direct commit to main) |
| T045 | senior-backend-engineer | Day 4 AM | [P] | Update `docs/architecture/01_system_design/README.md` — new F-194 subsection (Feature 143/144 precedent) |
| T046 | devops | Day 4 PM | sequential | PR preparation + submission — cites triple sign-off, ADR-029 Accepted, SC-002/008/009 results, T039 outcome |

---

## Parallel Execution Waves

### Wave 1.0 — Day 1 AM (architect critical path)

**Tasks**: T002 (sequential), T003 [P]
**Agent**: architect
**Window**: ~3-4h (Day 1 AM)
**Quality gate before next wave**: T002 ADR-029 Proposed committed to feature branch

T002 is on the critical path. T003 runs in parallel on architect's own track as Q5 fallback safety net (addresses team-lead L1 audit-trail gap).

### Wave 1.1 — Day 1 (parallel scaffolding, Q-independent)

**Tasks**: T004 [P], T005 [P], T006 [P], T007 [P]
**Agents**: tester (T004, T005), senior-backend-engineer (T006, T007)
**Window**: ~2-3h (Day 1 AM-PM, concurrent with Wave 1.0)
**Quality gate before Phase 3/4/5 start**: All fixtures authored, Typst skeleton compiles, boolean stub in place

All 4 tasks touch different files — no conflicts. Zero-denominator fixture (T005) is synthetic-only per architect M-3.

### Wave 2.1 — Day 2 AM (TDD test authoring burst — 14 parallel tests)

**Tasks**: T008, T009, T010 [US3] + T017, T018, T019, T020, T021, T022, T023 [US2] + T031, T032, T033, T034 [US1]
**Agent**: tester (14 tests concurrently — same file `test_coverage_attestation.py`, distinct test functions)
**Window**: ~3-4h (Day 2 AM, pytest-safe concurrency)
**Quality gate before Wave 2.2**: All 14 tests authored and FAILING (TDD discipline); pytest collects without errors

Team-lead review verified 14 parallel tests (not 11+ as originally claimed). Tester Day 2 AM peak load; ~7-10h full day.

### Wave 2.2 — Day 2 AM-EOD (US2 + US1 aggregator implementation, serialized within agent)

**Tasks**: T011 → T024 → T025 → T026 → T027 → T035 → T036
**Agent**: senior-backend-engineer
**Window**: ~8-10h (Day 2 AM through Day 2 EOD)
**Quality gate before Phase 3 main.typ edits (Day 3)**: All aggregator functions land green; T024-T027 (US2) complete before T035-T036 (US1) start per team-lead M1 explicit sequencing

All tasks T011, T024-T027, T035-T036 edit the same file (`scripts/extract-report-data.py`). Single-lane serial execution per team-lead M1 resolution. If multi-lane staffing is available (per tasks.md "Parallel Team Strategy (if staffed)"), T024-T027 and T035-T036 may split to Developer B / Developer C with a merge-coordination checkpoint at Day 2 EOD.

### Wave 2.3 — Day 2 EOD (F-A3 coordination checkpoint)

**Tasks**: T039
**Agent**: team-lead
**Window**: ~30min (Day 2 EOD)
**Quality gate**: F-A3 serialization decision recorded. Two pre-approved paths: (a) hold F-B for F-A3, (b) advance F-B and accept F-A3 re-baseline cost (~0.5-1d per PRD A7).

### Wave 3.1 — Day 3 AM (main.typ atomic integration, sequential)

**Tasks**: T013 → T012 → T016 → T014
**Agent**: senior-backend-engineer
**Window**: ~1.5h (Day 3 AM, same file: `templates/tachi/security-report/main.typ`)
**Quality gate**: T016 `#import`-only byte-identity smoke green BEFORE T014 conditional block applied

Order: import (T013) → 3-guard atomic edit (T012, re-validate line range 89-107 per team-lead L2) → byte-identity smoke (T016) → conditional block at refined :393 insertion point (T014, architect M-1).

### Wave 3.2 — Day 3 AM-PM (Typst rendering — US2 + US1)

**Tasks**: T028, T029, T030 (US2 matrix) → T037 (US1 per-finding) → T038 (pagination smoke)
**Agent**: senior-backend-engineer
**Window**: ~7-9h (Day 3 AM-PM — **Day 3 load peak**, team-lead M2 concern)
**Quality gate before Day 4 SC-002 regression**: All 5 per-framework pages render on `multi_mixed_attribution.yaml`; per-finding table renders with correct MITRE merge; pagination smoke documents outcome (or defers to Day 4 AM per T038 pre-approved slip)

**Team-lead M2 saturation**: senior-backend-engineer Day 3 projected 9-11h (~90-110% load). Mitigations pre-approved: (a) T038 slip-to-Day-4 AM, (b) multi-lane staffing with T028 and T037 in parallel.

### Wave 4.1 — Day 4 AM (SC-002 regression + parallel audits)

**Tasks**: T015 (BLOCKER gate) + T042 (quickstart) + T040 [P] + T041 [P] + T045 [P]
**Agents**: tester (T015, T042), security-analyst (T040, T041), senior-backend-engineer (T045)
**Window**: ~2h (Day 4 AM, parallel tracks)
**Quality gate before Wave 4.2**: T015 green (SC-002 baselines byte-identical) + T040 green (zero-edit invariant) + T041 green (zero-dep diff empty) + T042 green (all 9 quickstart steps)

Stop-ship gates: Any regression on T015, T040, or T041 halts the PR. T038 pagination smoke also resolves here if slipped from Day 3.

### Wave 4.2 — Day 4 PM (ADR transition + PR submission)

**Tasks**: T043 → T046
**Agents**: architect (T043), devops (T046)
**Window**: ~1h (Day 4 PM, sequential)
**Quality gate before merge**: T043 ADR-029 Accepted committed (provisional merge-date 2026-04-23, placeholder merge-sha); T046 PR description cites all sign-offs + SC results + T039 outcome

### Post-merge

**Tasks**: T044
**Agent**: architect
**Window**: ~15min (immediate after squash-merge)
**Action**: Amend ADR-029 `merge-sha:` placeholder with actual squash commit SHA; direct commit to main per Feature 180 / 189 precedent.

---

## Time Estimates per Wave

| Wave | Agent | Estimated Hours | Day-Level Capacity (8h) |
|------|-------|-----------------|--------------------------|
| Wave 1.0 | architect | 3-4h | 40-50% Day 1 |
| Wave 1.1 | tester | 1-2h | 15-25% Day 1 |
| Wave 1.1 | senior-backend-engineer | 1-2h | 15-25% Day 1 |
| Wave 2.1 | tester | 3-4h | 40-50% Day 2 AM |
| Wave 2.2 | senior-backend-engineer | 8-10h | **100-125% Day 2** (full load peak) |
| Wave 2.3 | team-lead | 0.5h | 6% Day 2 EOD |
| Wave 3.1 | senior-backend-engineer | 1.5h | part of Day 3 load |
| Wave 3.2 | senior-backend-engineer | 7-9h | **Day 3 peak: 90-110% when combined with Wave 3.1** (team-lead M2) |
| Wave 4.1 | tester | 1h | 12% Day 4 AM |
| Wave 4.1 | security-analyst | 0.5h | 6% Day 4 AM |
| Wave 4.1 | senior-backend-engineer | 0.5h (T045) | 6% Day 4 AM |
| Wave 4.2 | architect | 0.5h | 6% Day 4 PM |
| Wave 4.2 | devops | 0.5h | 6% Day 4 PM |

### Per-Agent 4-Day Totals

| Agent | Total Hours | % of 32h envelope |
|-------|-------------|---------------------|
| senior-backend-engineer | ~19-23h | 60-72% (Day 3 peak 90-110% — **flagged M2**) |
| tester | ~10-14h | 31-44% (Day 2 AM peak ~50%) |
| architect | ~4-5h | 13-16% |
| team-lead | ~0.5h | 2% |
| security-analyst | ~0.5h | 2% |
| devops | ~0.5h | 2% |
| ux-ui-designer | 0h (fallback covered by T003) | 0% — optional |

**Flagged agent (>80% Day-level capacity)**: senior-backend-engineer on Day 3 (Wave 3.1 + Wave 3.2 combined). Mitigations pre-approved in tasks.md (T038 slip or multi-lane split).

---

## Quality Gates

### Gate 1 — Phase 2 Foundation complete (Day 1 EOD)
- T002 ADR-029 Proposed committed
- T004, T005 fixtures present at `tests/scripts/fixtures/coverage_attestation/`
- T006 Typst skeleton compiles
- T007 `compute_has_source_attribution` stub in place
- **Unblocks**: Phase 3 US3 + Phase 4 US2 + Phase 5 US1 test authoring

### Gate 2 — TDD Red (Day 2 AM)
- All 14 tests (T008-T010, T017-T023, T031-T034) authored and FAILING
- **Unblocks**: Wave 2.2 implementation burst

### Gate 3 — US2 + US1 aggregator green (Day 2 EOD)
- T011, T024-T027, T035-T036 implemented
- All 11 implementation-side tests pass (14 tests minus 3 default-value-guard tests that unblock in Gate 5)
- **Unblocks**: Day 3 main.typ integration + Typst rendering

### Gate 4 — F-A3 coordination (Day 2 EOD)
- T039 decision recorded in PR draft description
- **Unblocks**: Day 3 continues at full speed OR serialization hold activates

### Gate 5 — main.typ integration byte-identity (Day 3 AM)
- T016 `#import`-only byte-identity smoke green
- T012 + T013 + T014 atomic edits landed
- **Unblocks**: Day 3 PM Typst rendering

### Gate 6 — SC-002 BLOCKER gate (Day 4 AM)
- T015: all 5 non-agentic baseline PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000
- **Unblocks**: Phase 4 continues; any regression HALTS PR

### Gate 7 — SC-008 + SC-009 BLOCKER gates (Day 4 AM)
- T040: zero-edit grep output empty on 22-file invariant
- T041: zero-dep diff empty on runtime/dev requirements files
- **Unblocks**: T043 ADR Accepted; any non-empty output HALTS PR

### Gate 8 — Quickstart end-to-end (Day 4 AM)
- T042: all 9 quickstart steps green
- **Unblocks**: T043 ADR-029 Accepted → T046 PR preparation

### Gate 9 — ADR Accepted → PR merge (Day 4 PM)
- T043 ADR-029 Status: Accepted committed
- T046 PR opened with full sign-off citations
- **Unblocks**: External review + squash-merge

### Gate 10 — Post-merge SHA fill (immediate post-merge)
- T044: `merge-sha:` placeholder replaced with actual squash SHA on main

---

## Critical Path

**Sequential chain** (~18-22h within 32h envelope):

```
T002 ADR-029 Proposed (Day 1 AM, ~3h)
  ↓
T007 has-source-attribution stub (Day 1 PM, ~0.5h)
  ↓
T011 Boolean emission (Day 2 AM, ~1h)
  ↓
T024 load_framework_yaml_record_counts (Day 2 AM, ~1-2h)
  ↓
T025 classify_framework_items (Day 2 PM, ~2-3h)
  ↓
T026 build_per_framework_aggregate (Day 2 PM, ~1-2h)
  ↓
T027 Wire aggregator invocation (Day 2 EOD, ~1h)
  ↓
T013 #import (Day 3 AM, ~15min)
  ↓
T016 #import byte-identity smoke (Day 3 AM, ~15min)
  ↓
T012 Default-value guards atomic block (Day 3 AM, ~0.5h)
  ↓
T014 Conditional inclusion block (Day 3 AM, ~0.5h)
  ↓
T028 Per-framework matrix page body (Day 3 AM-PM, ~2-3h)
  ↓
T037 Per-finding table Typst (Day 3 PM, ~2-3h)
  ↓
T038 Pagination smoke (Day 3 PM or Day 4 AM slip, ~1h)
  ↓
T015 SC-002 byte-identity regression (Day 4 AM, ~15min automated)
  ↓
T042 Quickstart validation (Day 4 AM, ~1h)
  ↓
T040 + T041 zero-edit + zero-dep audits (Day 4 AM, ~15min parallel)
  ↓
T043 ADR-029 Accepted (Day 4 PM, ~30min)
  ↓
T046 PR preparation (Day 4 PM, ~30min)
```

**Cumulative time**: 18-22h critical path. Buffer: 10-14h for Q5 memo slip, F-A3 coordination round-trip, TDD iteration rounds on aggregator, or T028/T037 rendering slip.

**Critical path agents**: architect (T002, T043) → senior-backend-engineer (T007 through T038 backbone, T045) → tester (T015, T042) → architect (T043) → devops (T046).

---

## Same-File Coordination (team-lead M1 explicit sequencing)

Two file hotspots require sequential-within-agent discipline:

### Hotspot 1 — `scripts/extract-report-data.py`

Tasks editing this file: **T007, T011, T024, T025, T026, T027, T035, T036**

- All assigned to **senior-backend-engineer** (single-lane default)
- **Serial order**: T007 → T011 → T024 → T025 → T026 → T027 → T035 → T036
- Rationale: T024-T027 (US2 aggregator functions `build_per_framework_aggregate`) must land BEFORE T035-T036 (US1 aggregator function `build_per_finding_rows`) to minimize merge conflict surface per team-lead M1
- **Multi-lane fallback** (if staffed per tasks.md "Parallel Team Strategy"): Developer B takes T024-T027, Developer C takes T035-T036, with merge-coordination checkpoint at Day 2 EOD before T027/T036 final commits

### Hotspot 2 — `templates/tachi/security-report/main.typ`

Tasks editing this file: **T012, T013, T014**

- All assigned to **senior-backend-engineer** (single-lane; these are tight interdependent atomic edits)
- **Serial order**: T013 (import, ~lines 43-47) → T012 (3-guard atomic block, ~lines 89-107; re-validate line range per team-lead L2) → T014 (conditional block AFTER findings-detail ~:393, BEFORE compensating-controls :398 per architect M-1)
- Rationale: Order dictated by Typst evaluation model — imports must precede references; defaults must precede conditional use

### Hotspot 3 — `templates/tachi/security-report/coverage-attestation.typ`

Tasks editing this file: **T006, T028, T029, T030, T037**

- All assigned to **senior-backend-engineer** (single-lane)
- **Serial order**: T006 (skeleton, Day 1) → T028 (matrix body, Day 3) → T029 (Gap highlighting, Day 3) → T030 (MITRE split verification, Day 3) → T037 (per-finding table, Day 3)

---

## Risk Mitigations (from team-lead tasks review findings)

| Finding | Mitigation Active | Owner |
|---------|-------------------|-------|
| M1: Same-file aggregator discipline | Explicit serial sequencing documented (Hotspot 1 above) | senior-backend-engineer |
| M2: Day 3 senior-backend-engineer 90-110% load | T038 slip-to-Day-4 AM pre-approved in tasks.md; multi-lane fallback documented | team-lead (monitor EOD Day 2) |
| L1: ux-ui-designer Q5 memo no explicit task ID | T003 architect fallback memo pre-authored Day 1 AM; Q5 visual treatment covered unconditionally | architect (T003) |
| L2: T012 line-range 89-107 may drift | Re-validate instruction added to T012 task description (defensive re-validate before atomic edit) | senior-backend-engineer |

---

## Agent Registry Compliance

All agent assignments use EXACT names from `.claude/agents/_README.md`:

- **senior-backend-engineer** — Python (aggregator functions, `_typst_bool` wiring), Typst templates (`coverage-attestation.typ`), `main.typ` integration, synthetic fixture generator script (T038)
- **tester** — fixtures (T004, T005), 14 TDD pytest tests (Wave 2.1), SC-002 regression (T015), quickstart validation (T042)
- **architect** — ADR-029 authoring + dual-commit Proposed → Accepted governance (T002, T043, T044), Q5 fallback memo (T003)
- **team-lead** — feature-branch verification (T001), F-A3 coordination check (T039), agent-assignments maintenance (this file)
- **security-analyst** — zero-edit invariant grep audit (T040, SC-009 BLOCKER), zero-dep diff audit (T041, SC-008 BLOCKER)
- **devops** — PR submission mechanics (T046)

Roles NOT required in-feature:
- **ux-ui-designer**: Q5 memo deferred (architect T003 fallback is the effective default per Assumptions A6)
- **code-reviewer**: PR review handled by external reviewer at squash-merge gate
- **product-manager**: sign-off complete at spec.md + tasks.md; no in-feature PM work
- **web-researcher, frontend-developer, debugger, orchestrator**: not applicable to this feature scope

---

**End of Agent Assignments — Feature 194**
