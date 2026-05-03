---
description: "Agent assignments for Feature 189 — F-A2 Source Attribution Schema Extension"
feature_id: 189
feature_name: source-attribution-schema-extension
team_lead_signoff:
  agent: team-lead
  date: 2026-04-17
  status: APPROVED_WITH_CONCERNS
  concerns_addressed_inline: 4
---

# Agent Assignments: Feature 189 — F-A2 Source Attribution Schema Extension

**Timeline envelope**: 2026-04-20 → 2026-04-22 (3 working days).
**Critical path**: T001 → T004 → T010 → T017 → T031 (≈13-15h).
**Agent registry**: All assignments reference exact names from `.claude/agents/_README.md`.

---

## Team-Lead Concerns Addressed Inline

Four concerns raised in the team-lead `APPROVED_WITH_CONCERNS` sign-off on tasks.md are resolved below so the orchestrator can execute without re-opening governance:

1. **T017 dual-agent encoding** — PRD Milestones table assigns `tester` primary + `senior-backend-engineer` secondary for the SC-2 backward-compat regression run. Encoded explicitly in the Assignment Matrix row for T017 and in Wave 4.1 notes.
2. **T001 architect bottleneck** — T001 is a single-agent `architect` task (ADR-028 Proposed body authoring + Q1/Q2/Q3 memo). Day 1 AM has no parallel critical-path work; T002 and T003 are the only concurrent tasks and both are short (≤0.5h each). Contingency: if architect availability slips, T004 CANNOT begin without T001 — Wave 2.1 slips by the same amount. This is acknowledged, not mitigable by re-assignment.
3. **Wave 3.1 / 4.1 / 5.1 fixture density** — Day 2 AM aggregates 7 fixture tasks (T006, T007, T012, T013, T018, T019, T020) plus the 5 parser/validator implementation tasks that must follow. With a single developer, US3 fixtures (T018-T020) and T027 validator implementation are the most likely to slip to Day 2 PM. **Contingency lever**: de-parallelize T027 from US1 work, re-sequence US3 after US2 SC-2 gate is green. US3 tests remain in-scope; only their wave placement slides.
4. **Earlier full-pytest gate before ADR Accepted flip** — team-lead recommends running `pytest tests/scripts/ -v` immediately after T028 (determinism verification) and BEFORE T031 (ADR Proposed→Accepted transition). This catches any regression introduced by the parser/validator work without committing the ADR transition prematurely. Encoded as new interim checkpoint **"Checkpoint 5.5"** in Wave 6.1 sequencing below. Formal task text in tasks.md does not change; the orchestrator invokes pytest as a gate verification step between T028 and T031.

---

## Agent Assignment Matrix

| Task ID | Description (abbreviated) | Primary Agent | Secondary / Reviewer | Wave | Est. Hours |
|---------|---------------------------|---------------|---------------------|------|------------|
| T001 | ADR-028 Proposed body (Q1/Q2/Q3 memo + 6 FR-014 items) | architect | — | 1.1 | 3-4 |
| T002 | Fixture directory + .gitkeep | senior-backend-engineer | — | 1.1 | 0.25 |
| T003 | Baseline git diff verification | senior-backend-engineer | — | 1.1 | 0.25 |
| T004 | Schema bump 1.4→1.5 + `source_attribution` field | senior-backend-engineer | architect (review) | 2.1 | 1.5 |
| T005 | Schema comment block (v1.5 section header) | senior-backend-engineer | — | 2.1 | 0.5 |
| T006 | Fixture: `valid_multi_record.md` | tester | — | 3.1 | 1 |
| T007 | Fixture: `valid_single_record.md` | tester | — | 3.1 | 0.5 |
| T008 | Test: `test_round_trip_multi_record` | tester | senior-backend-engineer (pair) | 3.1 | 1 |
| T009 | Test: `test_round_trip_single_record` | tester | senior-backend-engineer (pair) | 3.1 | 0.5 |
| T010 | Parser: `_extract_source_attribution` helper | senior-backend-engineer | tester (test-driven) | 3.1 | 3-4 |
| T011 | Parser-tier shape validation | senior-backend-engineer | — | 3.1 | 1 |
| T012 | Fixture: `valid_absent.md` | tester | — | 4.1 | 0.5 |
| T013 | Fixture: `valid_empty_array.md` | tester | — | 4.1 | 0.5 |
| T014 | Test: `test_absent_omits_key` | tester | senior-backend-engineer (pair) | 4.1 | 0.5 |
| T015 | Test: `test_empty_array_preserved` | tester | senior-backend-engineer (pair) | 4.1 | 0.5 |
| T016 | Parser: absent-vs-empty refinement (V6) | senior-backend-engineer | — | 4.1 | 1 |
| T017 | SC-2 backward-compat regression (5 PDF baselines) | tester | senior-backend-engineer (diagnostics) | 4.1 | 1.5 |
| T018 | Fixture: `invalid_taxonomy.md` | tester | — | 5.1 | 0.5 |
| T019 | Fixture: `invalid_relationship.md` | tester | — | 5.1 | 0.5 |
| T020 | Fixture: `invalid_id.md` | tester | — | 5.1 | 0.5 |
| T021 | Test: `test_invalid_taxonomy_rejected` | tester | senior-backend-engineer (pair) | 5.1 | 0.5 |
| T022 | Test: `test_invalid_relationship_rejected` | tester | senior-backend-engineer (pair) | 5.1 | 0.5 |
| T023 | Test: `test_relationship_defaults_to_primary` | tester | senior-backend-engineer (pair) | 5.1 | 0.5 |
| T024 | Test: `test_invalid_id_detected` (validator) | tester | senior-backend-engineer (pair) | 5.1 | 1 |
| T025 | Test: `test_fixtures_self_consistent` | tester | senior-backend-engineer (pair) | 5.1 | 0.5 |
| T026 | Parser: enum validation V1/V2/V3 | senior-backend-engineer | — | 5.1 | 1.5 |
| T027 | Validator: `validate_source_attribution` helper | senior-backend-engineer | architect (signature review) | 5.1 | 3-4 |
| T028 | Determinism audit (no HTTP/env/timestamp/module state) | senior-backend-engineer | — | 5.1 | 0.5 |
| **5.5** | **Interim full pytest gate** (team-lead concern #4) | tester | senior-backend-engineer | 6.1 pre-flight | 0.5 |
| T029 | `README.md` Recent Changes line | senior-backend-engineer | — | 6.1 | 0.25 |
| T030 | `docs/architecture/00_Tech_Stack/README.md` timeline | senior-backend-engineer | — | 6.1 | 0.25 |
| T031 | ADR-028 Proposed → Accepted transition | architect | — | 6.1 | 0.5 |
| T032 | SC grep audit (SC-001/006/007, 22-file zero-edit) | senior-backend-engineer | code-reviewer | 6.1 | 1 |
| T033 | Quickstart walk-through validation | tester | — | 6.1 | 1 |
| T034 | Full pytest run (final gate) | tester | senior-backend-engineer | 6.1 | 0.5 |
| T035 | PR submission with audit + pytest summaries | senior-backend-engineer | — | 6.1 | 0.5 |
| T036 | Post-merge ADR SHA fill | architect | — | post-merge | 0.25 |

**Agent load summary** (over 3 days, excluding post-merge T036):
- `architect`: 4-5h primary (T001, T031) + 1h review (T004, T027) = **5-6h total**
- `senior-backend-engineer`: 12-14h primary (T002-T005, T010, T011, T016, T026-T030, T032, T035) + 6-8h secondary/pairing (T008, T009, T014, T015, T017, T021-T025, T034, Checkpoint 5.5) = **18-22h total**
- `tester`: 11-13h primary (T006-T009, T012-T015, T017, T018-T025, T033, T034, Checkpoint 5.5) = **11-13h total**
- `code-reviewer`: 0.5h (T032 secondary review)

No agent exceeds the 80% target load across the 3-day envelope. `senior-backend-engineer` carries the heaviest load — this is expected given the parser/validator implementation concentration and tracks the PRD Milestones primary-agent column.

---

## Parallel Execution Waves

### Wave 1.1 — Day 1 AM (Tuesday 2026-04-20)

**Goal**: Unblock everything. ADR-028 Proposed body with Q1/Q2/Q3 resolved.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T001 | architect | serial (critical path) |
| T002 | senior-backend-engineer | parallel with T001 |
| T003 | senior-backend-engineer | parallel with T001 |

**Bottleneck note (team-lead concern #2)**: T001 is a single-agent `architect` task of 3-4h. T002 and T003 are short parallel work (≤0.5h each) and will complete well before T001. The Day 1 AM critical path is bounded by `architect` availability — no re-assignment mitigates this.

### Wave 2.1 — Day 1 PM (Tuesday 2026-04-20)

**Goal**: Schema lock. 1.4 → 1.5 with `source_attribution` field.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T004 | senior-backend-engineer (architect reviewer) | serial |
| T005 | senior-backend-engineer | same-file-as-T004; tasks.md flags [P] as authoring-prep-only |

### Wave 3.1 — Day 2 AM (Wednesday 2026-04-21)

**Goal**: US1 MVP — multi-framework citation round-trip.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T006 | tester | parallel fixture pair |
| T007 | tester | parallel fixture pair |
| T008 | tester (senior-backend-engineer pair) | serial after T006/T007 |
| T009 | tester (senior-backend-engineer pair) | serial after T006/T007 |
| T010 | senior-backend-engineer (tester test-driven) | serial — drives T008/T009 from red to green |
| T011 | senior-backend-engineer | serial after T010 |

### Wave 4.1 — Day 2 AM/PM (Wednesday 2026-04-21)

**Goal**: US2 — absent-vs-empty refinement + SC-2 backward-compat gate.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T012 | tester | parallel fixture pair |
| T013 | tester | parallel fixture pair |
| T014 | tester (senior-backend-engineer pair) | serial after T012/T013 |
| T015 | tester (senior-backend-engineer pair) | serial after T012/T013 |
| T016 | senior-backend-engineer | serial — drives T014/T015 to green |
| **T017** | **tester primary / senior-backend-engineer secondary (diagnostics)** | serial SC-2 gate — concern #1 encoding |

### Wave 5.1 — Day 2 PM / Day 3 AM (Wed 2026-04-21 PM → Thu 2026-04-22 AM)

**Goal**: US3 — closed-enum + referential integrity + determinism audit.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T018 | tester | parallel fixture triple |
| T019 | tester | parallel fixture triple |
| T020 | tester | parallel fixture triple |
| T021 | tester (senior-backend-engineer pair) | serial after T018 |
| T022 | tester (senior-backend-engineer pair) | serial after T019 |
| T023 | tester (senior-backend-engineer pair) | serial after T007 |
| T024 | tester (senior-backend-engineer pair) | serial after T020 + T027 |
| T025 | tester (senior-backend-engineer pair) | serial after T027 |
| T026 | senior-backend-engineer | serial — drives T021/T022 to green |
| T027 | senior-backend-engineer (architect signature review) | serial/parallel — can author from T001 onward per tasks.md dependencies |
| T028 | senior-backend-engineer | serial after T027 |

**Contingency lever (team-lead concern #3)**: if Day 2 AM fixture volume slips, de-couple T027 from US1 and begin authoring from T001 onward per the tasks.md dependency graph. US3 fixtures (T018-T020) slide to Day 2 PM; T021-T025 follow; US3 remains in-scope. T017 SC-2 gate placement is unchanged (early Day 2 PM) — US2 is the critical-path baseline protection and cannot be deferred for US3 parallelism.

### Interim Checkpoint 5.5 — Day 3 AM Pre-flight (Thursday 2026-04-22)

**Team-lead concern #4 encoding**: Run `pytest tests/scripts/ -v` BEFORE T031 ADR transition. This catches any regression introduced by T010/T016/T026/T027/T028 before committing the ADR Proposed→Accepted flip. If any test fails, halt Wave 6.1 until the regression is resolved; T031 does not transition the ADR on a red test state.

| Task | Agent | Notes |
|------|-------|-------|
| **Interim pytest gate** | tester (senior-backend-engineer diagnostics) | Post-T028, pre-T031 — gate verification step, not a new formal task |

### Wave 6.1 — Day 3 PM (Thursday 2026-04-22)

**Goal**: ADR transition, docs sync, SC audit, PR.

| Task | Agent | Parallel? |
|------|-------|-----------|
| T029 | senior-backend-engineer | parallel with T030 |
| T030 | senior-backend-engineer | parallel with T029 |
| T031 | architect | serial — requires Checkpoint 5.5 green |
| T032 | senior-backend-engineer (code-reviewer secondary) | parallel with T033 |
| T033 | tester | parallel with T032 |
| T034 | tester (senior-backend-engineer pair) | serial — final pytest gate, post-T032 |
| T035 | senior-backend-engineer | serial after T034 |

### Post-merge (after 2026-04-22 squash)

| Task | Agent | Notes |
|------|-------|-------|
| T036 | architect | ADR-028 SHA fill — mirrors F-A1 Wave 5.2 post-merge precedent |

---

## Quality Gates Between Waves

| Gate | Precondition (wave just completed) | Green means (next wave may begin) |
|------|-----------------------------------|-----------------------------------|
| Checkpoint 1 (post-Wave 1.1) | ADR-028 Proposed body committed with Q1/Q2/Q3 resolved | Schema authoring (Wave 2.1) may begin |
| Checkpoint 2 (post-Wave 2.1) | `schemas/finding.yaml` carries `schema_version: "1.5"` + new field | US1 fixture authoring + parser implementation (Wave 3.1) may begin |
| Checkpoint 3 (post-Wave 3.1) | T008, T009 pass; multi-framework round-trip green | US2 (Wave 4.1) and US3 parallel authoring (T027 path) may begin |
| Checkpoint 4 (post-Wave 4.1) | **SC-002 byte-identity gate green** — 5/5 PDF baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000` | US3 closing tasks (T026-T028) may begin |
| Checkpoint 5 (post-Wave 5.1) | T021-T025 pass; T028 determinism verified; two-tier validation functional | Interim pytest gate (Checkpoint 5.5) may begin |
| **Checkpoint 5.5** (team-lead concern #4) | **Full `pytest tests/scripts/ -v` green post-T028, pre-T031** | ADR Proposed→Accepted transition (T031) may proceed |
| Checkpoint 6 (post-Wave 6.1) | All 7 SC gates green, PR submitted | Merge and schedule T036 post-merge fill |

---

## Time Estimates per Wave

| Wave | Day / Slot | Total Hours | Critical-Path Hours | Notes |
|------|-----------|-------------|---------------------|-------|
| 1.1 | Day 1 AM | 3-4.5h | 3-4h (T001) | T002/T003 parallel absorbed |
| 2.1 | Day 1 PM | 2h | 1.5h (T004) | T005 same-file; batched |
| 3.1 | Day 2 AM | 7-8h | 5-6h (T010→T011 tail) | 7 tasks; fixture pairs parallel |
| 4.1 | Day 2 AM/PM | 4.5h | 3.5h (T016→T017) | SC-2 gate is concern #1 dual-agent |
| 5.1 | Day 2 PM / Day 3 AM | 9-10h | 5-6h (T027→T028 tail) | Concern #3 contingency applies |
| 5.5 | Day 3 AM pre-flight | 0.5h | 0.5h | Concern #4 interim gate |
| 6.1 | Day 3 PM | 4h | 2.5h (T031→T034→T035) | Docs parallel; SC audit parallel |
| post-merge | After squash | 0.25h | 0.25h | T036 single-line SHA fill |
| **Total** | 3 days | **30-32.5h** | **21-23h critical path** | Fits envelope with buffer |

Timeline envelope validation: 21-23h critical-path hours over 3 working days (≈24h of productive time at 8h/day) fits with a 1-3h buffer. The buffer absorbs: T001 architect-availability slips (concern #2), Day 2 AM fixture density (concern #3), and SC-2 gate diagnostic work (T017 secondary agent activation).

---

## Handoff to Orchestrator

**Feasibility status**: APPROVED_WITH_CONCERNS (4 concerns encoded above).
**Wave strategy**: 6 sequential waves + 1 interim checkpoint + post-merge fill.
**Critical path**: T001 → T004 → T010 → T017 → T031 (≈13-15h of the 21-23h critical path).
**Agent registry compliance**: All 36 tasks mapped to exact names from `.claude/agents/_README.md`; zero invented agent labels.
**MVP boundary**: Checkpoint 3 (US1 complete) is the earliest stakeholder-demo-ready point; Checkpoint 4 (SC-002 green) is the earliest regression-safe ship-ready point; Checkpoint 5.5 is the ADR-transition-safe point.

**Orchestrator expected deliverables on completion report**:
1. All 36 tasks marked [X] in tasks.md
2. `.aod/results/sc-audit.md` (from T032) + `.aod/results/quickstart-validation.md` (from T033)
3. PR URL with pytest summary + 22-file zero-edit confirmation
4. Confirmation that Checkpoint 5.5 interim pytest gate was invoked before T031 (team-lead concern #4 enforcement)
5. Confirmation that T017 was executed by `tester` primary with `senior-backend-engineer` diagnostics engagement if required (team-lead concern #1 enforcement)

---

**End of Agent Assignments — Feature 189**
