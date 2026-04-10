---
feature: 128-prd-128-executive
generated_by: team-lead
generated_date: 2026-04-09
tasks_reference: specs/128-prd-128-executive/tasks.md
task_count: 51
wave_count: 6
estimated_hours: 19.5
estimated_sessions: 5-6
related_reviews:
  - .aod/results/team-lead-tasks-rev2.md
---

# Agent Assignments: Executive Threat Architecture Infographic

**Feature**: 128-prd-128-executive
**Tasks**: 51 (T0a-T0h, T001-T039)
**Agent registry**: `.claude/agents/_README.md` (13 agents, exact names used)
**Wave strategy**: 6 waves mapped to plan.md's 5-6 session budget
**Critical path**: 46 sequential tasks (~19.3 hours)
**Total estimate**: ~745 lines of code + docs, ~19.5 hours, 5-6 focused sessions

---

## 1. Agent Assignment Matrix

Every task is assigned to exactly one primary agent using the canonical names from `.claude/agents/_README.md`: `senior-backend-engineer`, `frontend-developer`, `tester`, `security-analyst`, `devops`, `code-reviewer`, `web-researcher`, `debugger`, `architect`, `product-manager`, `ux-ui-designer`, `orchestrator`.

### Phase 0 — Test Infrastructure Bootstrap (8 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T0a | senior-backend-engineer | Create `tests/` directory skeleton + `__init__.py` markers |
| T0b | senior-backend-engineer | Author `conftest.py` with importlib shim (Python harness code) |
| T0c | senior-backend-engineer | Edit `pyproject.toml` `[tool.pytest.ini_options]` section |
| T0d | senior-backend-engineer | Create `requirements-dev.txt` with pytest pins |
| T0e | senior-backend-engineer | Append `test:` target to existing `Makefile` |
| T0f | tester | Author smoke test `test_smoke.py` (first real test) |
| T0g | senior-backend-engineer | Run `make test`, verify exit 0; Phase 0 gate |
| T0h | senior-backend-engineer | Add "Running Tests" section to `README.md` or `CONTRIBUTING.md` |

### Phase 1 — Setup & Baselines (7 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T001 | orchestrator | 5-minute fixture verification; no code work, cross-tool check |
| T002 | architect | Baseline storage approach decision (architect L-2 observation) |
| T003a | devops | `git worktree add /tmp/tachi-pre-f128 main` |
| T003b | devops | Run `/tachi.security-report` over 5 examples in worktree |
| T003c | devops | Determinism verification via `cmp` (byte-identical check) |
| T003d | devops | Copy deterministic baselines into working tree |
| T003e | devops | `git worktree remove /tmp/tachi-pre-f128` cleanup |

### Phase 2 — Foundational Schema (1 task)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T004 | senior-backend-engineer | YAML schema edit (`schemas/infographic.yaml`) |

### Phase 3 — User Story 1: Generate Executive Architecture Infographic (11 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T005 | tester | Create 7 test fixtures (5 synthetic + 2 copied) |
| T006 | tester | Author 12 US-1 unit tests in one file |
| T007 | tester | Run tests, confirm all 12 FAIL (test-first gate) |
| T008 | senior-backend-engineer | Add `executive-architecture` to argparse `--template` choices |
| T009 | senior-backend-engineer | Add 3 helper functions (`_compute_dfd_type_layers`, `_normalize_component_name`, `_select_critical_high_callouts`) |
| T010 | senior-backend-engineer | Add `_build_executive_architecture_payload()` builder |
| T011 | senior-backend-engineer | Add dispatch branch to template selection logic |
| T012 | tester | Run tests, confirm all 12 PASS + verify ≥80% coverage |
| T013 | senior-backend-engineer | Update `threat-infographic.md` with template description (markdown agent doc edit) |
| T014 | senior-backend-engineer | Update `threat-infographic.md` with Gemini prompt guidance |
| T015 | senior-backend-engineer | Update `threat-infographic.md` with skip-image branch |

### Phase 4 — User Story 2: PDF Page Positioning (10 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T016 | tester | Author 5 US-2 tests in `test_extract_report_data.py` |
| T017 | tester | Run tests, confirm all 5 FAIL (test-first gate) |
| T018 | senior-backend-engineer | Add image to `detect_images()` in `extract-report-data.py` |
| T019 | senior-backend-engineer | Emit `has-executive-architecture` Typst variables |
| T020 | senior-backend-engineer | Add conditional page block to `main.typ` (Typst template edit) |
| T021 | senior-backend-engineer | Update `report-assembler.md` artifact detection table |
| T022 | tester | Run tests, confirm all 5 PASS + coverage check |
| T023 | orchestrator | Manual end-to-end verification (pipeline invocation + PDF inspection) |
| T024 | tester | Author `test_backward_compatibility.py` (5-example byte-identical PDF test) |
| T025 | tester | Author `test_pdf_page_positioning.py` (PDF structure assertions) |

### Phase 5 — User Story 3: `all` Shorthand + `exec` Alias (3 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T026 | tester | Author 2 dispatch tests in `test_command_dispatch.py` |
| T027 | senior-backend-engineer | Update `.claude/commands/tachi.infographic.md` (markdown command edit) |
| T028 | tester | Run tests, confirm both PASS |

### Phase 6 — User Story 4: Skip-Image Graceful Handling (2 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T029 | tester | Author PDF skip test in `test_pdf_page_positioning.py` |
| T030 | senior-backend-engineer | No new implementation; integration verification delegation |

### Phase 7 — Polish, Gates & PR (9 tasks)

| Task | Primary Agent | Rationale |
|------|--------------|-----------|
| T031 | senior-backend-engineer | Create `executive-architecture.md` skill reference doc |
| T032 | senior-backend-engineer | Update `SKILL.md` infographic index |
| T033 | orchestrator | Regenerate agentic-app example via pipeline invocation (`/tachi.infographic` + `/tachi.security-report`) |
| T034 | tester | Run full test suite (`make test`) — all phases consolidated |
| T035 | code-reviewer | Full F-128 diff review against constitution + F-091/F-112 parity → `code-review.md` |
| T036 | architect | Architect implementation checkpoint → `architect-checkpoint.md` |
| T037 | security-analyst | Security review of example regeneration → `security-review.md` |
| T038 | product-manager | Usability check per SC-004 (PM owns success criteria) |
| T039 | senior-backend-engineer | PR authoring per Git Workflow constitution principle |

### Assignment Summary by Agent

| Agent | Task Count | Phases Touched |
|-------|------------|----------------|
| senior-backend-engineer | 24 | 0, 2, 3, 4, 5, 6, 7 |
| tester | 15 | 0, 3, 4, 5, 6, 7 |
| devops | 5 | 1 |
| orchestrator | 3 | 1, 4, 7 |
| architect | 2 | 1, 7 |
| code-reviewer | 1 | 7 |
| security-analyst | 1 | 7 |
| product-manager | 1 | 7 |
| **Total** | **51** | **0-7** |

No agent is assigned >50% of the 51 tasks excepting `senior-backend-engineer` at 47% (24/51), which is acceptable because 13 of those are markdown/docs/skill-reference work that can be interleaved with test-wait cycles. Workload is balanced within the 5-6 session budget.

---

## 2. Parallel Execution Waves

Tasks are grouped into 6 waves. Wave boundaries align to (a) the dependency graph in tasks.md Dependencies section and (b) natural session breakpoints in the plan.md estimate.

### Wave 1 — Bootstrap (Session 1, ~2.0 hours)

**Scope**: Phase 0 (T0a-T0h). Create pytest harness from scratch.

**Tasks (mostly sequential — same conftest/pyproject files)**:
- T0a [senior-backend-engineer] — directory skeleton
- T0b [senior-backend-engineer] — `conftest.py` importlib shim
- T0c [senior-backend-engineer] — `pyproject.toml` pytest config
- T0d [senior-backend-engineer] — `requirements-dev.txt`
- T0e [senior-backend-engineer] — `Makefile` target append
- T0f [tester] — smoke test authoring
- T0g [senior-backend-engineer] — **GATE**: `make test` must exit 0
- T0h [senior-backend-engineer] — docs section

**Parallelism**: T0d can run in parallel with T0c (different files, no dependency). T0h can run in parallel with T0g verification. Otherwise sequential.

**Exit criterion**: `make test` exits 0 and prints the smoke test passing. Without this, no downstream test work is possible.

### Wave 2 — Setup, Baselines & Schema (Session 1-2, ~2.0 hours)

**Scope**: Phase 1 (T001, T002, T003a-e) + Phase 2 (T004).

**Tasks**:
- T001 [orchestrator] — 5-min fixture severity verification (parallel with T002)
- T002 [architect] — baseline storage decision → `decisions.md` (parallel with T001)
- T003a [devops] — worktree add (after T002)
- T003b [devops] — run pipeline for 5 examples in worktree
- T003c [devops] — determinism verification via `cmp`
- T003d [devops] — copy deterministic baselines into working tree
- T003e [devops] — worktree cleanup
- T004 [senior-backend-engineer] — schema enumeration (**parallel with T003a-e** — different files, no dep)

**Parallelism**: T001 ∥ T002 (distinct checks). T004 ∥ T003 chain (distinct files). The T003a→b→c→d→e chain itself is strictly sequential.

**Exit criterion**: 5 deterministic baselines stored at the path recorded in `decisions.md`; `schemas/infographic.yaml` has the `executive-architecture` entry.

### Wave 3 — User Story 1 MVP Extraction (Session 2-3, ~7.0 hours)

**Scope**: Phase 3 (T005-T015). The single largest phase and the core of the MVP.

**Tasks (critical path, mostly sequential)**:
- T005 [tester] — 7 test fixtures
- T006 [tester] — 12 US-1 unit tests (accepted long-duration task per A-2)
- T007 [tester] — **GATE**: all 12 tests FAIL (test-first)
- T008 [senior-backend-engineer] — argparse enum
- T009 [senior-backend-engineer] — 3 helper functions
- T010 [senior-backend-engineer] — payload builder
- T011 [senior-backend-engineer] — dispatch branch
- T012 [tester] — **GATE**: all 12 tests PASS + ≥80% coverage
- T013 [senior-backend-engineer] — agent doc: template description
- T014 [senior-backend-engineer] — agent doc: Gemini prompt guidance
- T015 [senior-backend-engineer] — agent doc: skip-image branch

**Parallelism**: T013, T014, T015 can run in any order after T012 (different sections of same file but non-overlapping edits). Otherwise sequential due to intra-file dependencies.

**Exit criterion**: All 12 US-1 tests green, coverage ≥80% on new extraction code, agent doc updated with all three new sections.

### Wave 4 — User Story 2 PDF Integration + Skill Docs (Session 3-4, ~5.5 hours)

**Scope**: Phase 4 (T016-T025) + Phase 7 skill references (T031, T032 hoisted forward per parallel opportunity in tasks.md line 237).

**Tasks**:
- T016 [tester] — 5 US-2 tests in `test_extract_report_data.py`
- T017 [tester] — **GATE**: all 5 tests FAIL
- T018 [senior-backend-engineer] — `detect_images()` update
- T019 [senior-backend-engineer] — Typst variable emitter (sequential with T018, same file)
- T020 [senior-backend-engineer] — `main.typ` conditional page block
- T021 [senior-backend-engineer] — `report-assembler.md` artifact detection table
- T022 [tester] — **GATE**: all 5 tests PASS + coverage check
- T023 [orchestrator] — manual end-to-end verification (pipeline invocation + PDF inspection) → `manual-verification.md`
- T024 [tester] — backward compat test (5-example byte-identical PDF check)
- T025 [tester] — PDF page positioning test
- T031 [senior-backend-engineer] — skill reference doc (parallel with Phase 4 per tasks.md line 237)
- T032 [senior-backend-engineer] — SKILL.md index update (parallel with Phase 4)

**Parallelism**: T020 ∥ T021 (different files). T024 ∥ T025 after T023. T031 ∥ T032 can run in parallel with anything from T016 onward. T018 → T019 strictly sequential (same file).

**Exit criterion**: US-2 tests green, manual verification logged, backward compatibility proven for 5 unmodified examples, skill docs updated.

### Wave 5 — User Stories 3 + 4 (Session 4-5, ~0.8 hours)

**Scope**: Phase 5 (T026-T028) + Phase 6 (T029-T030). Both stories are P2 and can run in parallel once Wave 4 completes.

**Tasks**:
- T026 [tester] — 2 US-3 dispatch tests
- T027 [senior-backend-engineer] — `.claude/commands/tachi.infographic.md` edits (all + exec alias)
- T028 [tester] — **GATE**: both US-3 tests PASS
- T029 [tester] — US-4 PDF skip test
- T030 [senior-backend-engineer] — integration verification delegation (no new code)

**Parallelism**: T026 ∥ T029 (different files, independent tests). T027 ∥ T030 (different surfaces). The T026→T027→T028 chain and T029→T030 chain can run concurrently on two agents, collapsing this wave to ~0.5 hours on the critical path.

**Exit criterion**: All US-3 and US-4 tests green; `exec` alias dispatches correctly; skip-image behavior confirmed end-to-end.

### Wave 6 — Polish, Gates & PR (Session 5-6, ~3.0 hours)

**Scope**: Phase 7 remainder (T033-T039).

**Tasks**:
- T033 [orchestrator] — regenerate agentic-app example via pipeline invocation
- T034 [tester] — **GATE**: full test suite `make test` green
- T035 [code-reviewer] — diff review → `code-review.md` (parallel with T036, T037)
- T036 [architect] — implementation checkpoint → `architect-checkpoint.md` (parallel with T035, T037)
- T037 [security-analyst] — security review → `security-review.md` (parallel with T035, T036)
- T038 [product-manager] — usability check (parallel with T035/T036/T037, non-blocking SLA)
- T039 [senior-backend-engineer] — PR authoring (after T034, T035, T036, T037)

**Parallelism**: T035 ∥ T036 ∥ T037 ∥ T038 is the key parallelism window — four independent reviewers working on four different deliverables simultaneously after T034 passes. This collapses ~2.0 hours of sequential review work into ~0.7 hours wall-clock.

**Exit criterion**: PR open, all gates documented, tests green, agentic-app regenerated.

### Wave Summary

| Wave | Tasks | Sessions | Hours | Critical-Path Time | Parallelism Gain |
|------|-------|----------|-------|--------------------|------------------|
| 1 | T0a-T0h (8) | 1 | 2.0 | 2.0 | Low (sequential) |
| 2 | T001-T004 (8) | 1-2 | 2.0 | 1.5 | 0.5h saved (T004 ∥ T003) |
| 3 | T005-T015 (11) | 2-3 | 7.0 | 6.5 | 0.5h saved (T013/T014/T015 reordering) |
| 4 | T016-T025, T031, T032 (12) | 3-4 | 5.5 | 5.0 | 0.5h saved (T031/T032 hoisted) |
| 5 | T026-T030 (5) | 4-5 | 0.8 | 0.5 | 0.3h saved (two chains parallel) |
| 6 | T033-T039 (7) | 5-6 | 3.0 | 2.0 | 1.0h saved (4-way parallel gates) |
| **Total** | **51** | **5-6** | **20.3** | **17.5** | **2.8h saved** |

Wall-clock critical path (~17.5 hours) vs. nominal work (~20.3 hours including skill-doc inflation) yields ~2.8 hours of parallelism savings, landing the realistic estimate at 5 sessions (17.5h ÷ 3.5h/session = 5.0). The plan.md estimate of 5-6 sessions is defensible with slack.

---

## 3. Quality Gates Between Waves

Each wave has an explicit exit criterion that must be satisfied before the next wave begins. Skipping a gate creates downstream rework risk.

| Gate | Before Wave | Validation | Owner | Blocking? |
|------|-------------|------------|-------|-----------|
| **G0**: Harness bootstrap | Wave 2 | `make test` exits 0 with smoke test green (T0g) | senior-backend-engineer | Yes |
| **G1**: Baselines deterministic | Wave 3 | 5 `.baseline` PDFs exist at decisions.md path; T003c `cmp` passed byte-identical | devops | Yes |
| **G2**: Schema ready | Wave 3 | `schemas/infographic.yaml` has `executive-architecture` entry (T004) | senior-backend-engineer | Yes |
| **G3**: US-1 MVP green | Wave 4 | 12 US-1 tests pass (T012); coverage ≥80% on new extraction code; agent doc updated (T013-T015) | tester + senior-backend-engineer | Yes |
| **G4**: US-2 PDF integration green | Wave 5 | 5 US-2 tests pass (T022); backward compat test passes (T024); PDF positioning asserted (T025); manual verification logged (T023) | tester + orchestrator | Yes |
| **G5**: US-3 + US-4 green | Wave 6 | 2 US-3 tests pass (T028); 1 US-4 PDF test passes (T029); exec alias dispatches correctly | tester | Yes |
| **G6**: Full suite + all reviews | PR merge | `make test` green (T034); code review filed (T035); architect checkpoint filed (T036); security review OR `--no-security` justification (T037) | tester, code-reviewer, architect, security-analyst | Yes |
| **G7**: Usability validated | Post-merge (SLA 5 business days) | Non-technical reviewer correctly identifies most exposed layer within 30 seconds (T038) | product-manager | No (post-merge) |

**Special handling**:
- **G0 is the master gate**: failure here blocks all downstream work (no harness = no tests = no Principle VI compliance). Budget 2.0 hours, escalate if >3.0 hours.
- **G1 determinism**: if T003c reveals non-determinism in the existing pipeline, escalate to architect + debugger for a decision on comparison strategy. Do not degrade to "close enough" comparison without architect sign-off.
- **G6 parallelism**: T035, T036, T037, T038 all run in parallel. No single-reviewer bottleneck.
- **G7 is the only non-blocking gate** per the 5-business-day SLA in tasks.md T038.

---

## 4. Time Estimates Per Wave

Derived from tasks.md estimation table (~745 lines, ~19.5 hours, 5-6 sessions). Sessions are assumed 3.5 hours each (midpoint of 3-4 hour focused session convention).

| Wave | Nominal Hours | Critical-Path Hours | Sessions Consumed | Cumulative Sessions |
|------|---------------|---------------------|-------------------|---------------------|
| 1 — Bootstrap | 2.0 | 2.0 | 0.6 | 0.6 |
| 2 — Setup + Baselines + Schema | 2.0 | 1.5 | 0.4 | 1.0 |
| 3 — US-1 Extraction | 7.0 | 6.5 | 1.9 | 2.9 |
| 4 — US-2 PDF + Skill Docs | 5.5 | 5.0 | 1.4 | 4.3 |
| 5 — US-3 + US-4 | 0.8 | 0.5 | 0.1 | 4.4 |
| 6 — Polish + Gates + PR | 3.0 | 2.0 | 0.6 | 5.0 |
| **Total** | **20.3** | **17.5** | **5.0** | **5.0** |

**Interpretation**:
- **Nominal hours (20.3)**: total work if all tasks ran sequentially by one agent.
- **Critical-path hours (17.5)**: wall-clock time on the longest dependency chain, assuming parallelism is exploited where possible.
- **5.0 sessions**: best case with full parallelism. The 5-6 session range in plan.md covers the 6-session contingency for any slippage (e.g., T003c determinism escalation, Gemini API retries in T023, reviewer latency in T035/T036/T037).

**Phase-to-Wave mapping vs. tasks.md estimation table**:

| tasks.md Phase | Wave | Phase Hours | Wave Hours | Delta |
|----------------|------|-------------|------------|-------|
| Phase 0 | Wave 1 | 2.0 | 2.0 | 0 |
| Phase 1 | Wave 2 | 1.5 | 1.5 | 0 |
| Phase 2 | Wave 2 | 0.5 | 0.5 | 0 |
| Phase 3 | Wave 3 | 7.0 | 7.0 | 0 |
| Phase 4 | Wave 4 | 5.0 | 5.0 | 0 |
| Phase 5 | Wave 5 | 0.5 | 0.5 | 0 |
| Phase 6 | Wave 6 (math) | 0.3 | 0.3 | 0 |
| Phase 7 | Waves 4 + 6 | 3.0 | 3.0 (split: 0.5 for T031/T032, 2.5 for T033-T039) | 0 |
| **Total** | — | **19.8** | **19.8** | **0** |

(Sum of 19.8 vs. tasks.md 19.5 is rounding noise in the per-phase estimates; both are within the 5-6 session budget.)

---

## 5. Critical Path

The critical path is the longest chain of dependent tasks that determines wall-clock delivery time. Tasks off the critical path (T031, T032, T038) can slip without extending the delivery date.

### Critical Path Chain

```
T0a → T0b → T0c → T0d → T0e → T0f → T0g → T0h
 → T002 → T003a → T003b → T003c → T003d → T003e
 → T004
 → T005 → T006 → T007
 → T008 → T009 → T010 → T011 → T012
 → T015
 → T016 → T017
 → T018 → T019 → T020 → T022 → T023 → T025
 → T029
 → T033 → T034 → T036 → T039
```

**46 tasks on the critical path**, out of 51 total. Off-critical tasks: T001 (parallel with T002), T013/T014 (parallel with T015), T021 (parallel with T020), T024 (parallel with T025), T026/T027/T028 (parallel with T029/T030 in Wave 5), T031, T032 (hoisted parallelism), T035/T037/T038 (parallel with T036).

### Critical Path Time (~17.5 hours)

| Chain Segment | Tasks | Hours |
|---------------|-------|-------|
| Bootstrap | T0a-T0h | 2.0 |
| Setup | T001/T002/T003a-e/T004 | 1.5 |
| US-1 extraction | T005-T012 | 5.5 |
| US-1 agent doc (longest of T013/T014/T015) | T015 | 0.5 |
| US-2 tests + impl | T016-T023 | 3.5 |
| US-2 positioning + backward compat | T025 (T024 parallel) | 1.0 |
| US-4 PDF test | T029 | 0.2 |
| Regeneration | T033 | 0.5 |
| Full suite | T034 | 0.3 |
| Architect checkpoint (longest of T035/T036/T037) | T036 | 1.0 |
| PR | T039 | 1.5 |
| **Total** | — | **17.5** |

### Critical Path Risks

Any task on the critical path that slips delays the entire feature. The three highest-leverage risks are:
1. **T0g** (Phase 0 gate): if the importlib shim doesn't work, Phase 0 is not complete and no downstream test work is possible. Mitigation: A-1 concern from rev2 review (the `exec_module` step) is inlined in T0b.
2. **T003c** (determinism verification): if byte-identical fails, the feature team must choose between fixing an existing non-determinism bug (potentially scope-expanding) or adopting a fuzzy comparison (weakens backward compat guarantee). Mitigation: escalate to architect within 30 minutes of failure.
3. **T006** (12 US-1 tests in one sitting): accepted A-2 violation. 1.5 hours of concentrated authoring. Mitigation: tester should pre-read fixtures from T005 to identify edge cases before authoring.

---

## 6. Risk Mitigation

### High-Risk Waves

**Wave 1 (Bootstrap)** — HIGH

- **Risk**: tachi has never had a pytest harness. The importlib shim for hyphenated script names is correct but untested in this repository. If the smoke test fails at T0g, Phase 0 is stuck.
- **Mitigation**: (a) A-1 concern inlined in T0b (includes `spec.loader.exec_module(module)` explicitly); (b) T0f writes the simplest possible smoke test (`assert module is not None`); (c) escalation path: if T0g fails, invoke `debugger` agent for 5 Whys analysis before attempting ad-hoc fixes.
- **Contingency**: +1 hour absorbed in Session 1 slack. If bootstrap exceeds 3.0 hours total, escalate to architect for importlib alternative (e.g., converting hyphenated scripts to snake_case with wrappers).

**Wave 3 (US-1 Extraction)** — HIGH

- **Risk**: largest wave (7.0 hours, 11 tasks), deepest dependency chain, first feature-specific implementation work. Architect L-1 (component name normalization, orphaned findings) and L-2 (baseline storage) must be addressed correctly.
- **Mitigation**: (a) test-first gate at T007 catches miswritten fixtures before implementation drift; (b) coverage gate at T012 catches under-tested code paths; (c) three helpers in T009 are small and independently testable; (d) architect L-1/L-2 fixtures (`mixed_case_components`, `orphaned_finding`) are explicit in T005 and explicit in T006 test list.
- **Contingency**: Wave 3 can absorb +1 hour without breaking the 6-session ceiling. If T012 coverage falls short of ≥80%, add targeted tests before advancing to Wave 4 — do not defer coverage work.

**Wave 6 (Polish + Gates + PR)** — MEDIUM

- **Risk**: four review gates (code review, architect checkpoint, security review, usability) could serialize if agents are unavailable. T033 regeneration depends on the Gemini API being reachable.
- **Mitigation**: (a) T035/T036/T037/T038 are explicitly parallelized; (b) T038 has a 5-business-day SLA and is non-blocking per tasks.md line 211; (c) T033 can be retried if Gemini API fails (reference F-091/F-112 pattern reuse means the infrastructure is known-good).
- **Contingency**: if any single reviewer blocks >1 hour, T039 (PR) can open without T038 (usability) per the SLA exception. Security review (T037) has the `--no-security` justification path per tasks.md line 210.

### Medium-Risk Waves

**Wave 4 (US-2 PDF)** — MEDIUM

- **Risk**: Typst template edits (T020) are fragile. T024 backward compat test is the hard gate — if any of the 5 unmodified examples produce non-byte-identical PDFs, the feature is blocked.
- **Mitigation**: (a) T020 explicitly reuses `infographic-page()` from `full-bleed.typ:40-86` — no new Typst function; (b) T021 updates `report-assembler.md` in parallel with T020 (different files, no conflict); (c) T024 runs in Wave 4, not Wave 6, so backward compat is proven before Polish begins.
- **Contingency**: if T024 fails, invoke `debugger` for 5 Whys on the byte-diff. Architect T036 will need to re-checkpoint the main.typ insertion point.

### Low-Risk Waves

**Waves 2 and 5** — LOW. Short waves with simple tasks and clear gates. Wave 2 risk limited to T003c determinism (escalation path above). Wave 5 is the smallest wave and can run in parallel across two agents.

### Cross-Wave Risks

- **Agent availability**: `senior-backend-engineer` is loaded with 24 tasks (47% of work). Mitigation: wave structure places senior-backend-engineer peak load in Wave 3 (5 tasks) and Wave 4 (5 tasks) — distributed across sessions rather than concentrated. `tester` is the second-most-loaded agent (15 tasks, 29%) with peak in Waves 3 and 4 where test authoring dominates.
- **Context drift across sessions**: 5-6 sessions introduces risk that state is lost between sessions. Mitigation: each wave's exit criterion is a concrete verifiable artifact (test pass, baseline file, PR URL). Picking up mid-wave is straightforward by reading the last gate status.
- **Scope creep from Phase 0 discoveries**: building a harness for F-128 also builds it for every future feature. Resist the temptation to expand scope (e.g., "while we're here, let's add coverage for the existing scripts"). Phase 0 is explicitly scoped to the smoke test + importlib shim.

---

## Handoff to Orchestrator

**Feasibility status**: APPROVED_WITH_CONCERNS (see `.aod/results/team-lead-tasks-rev2.md` for the 3 minor concerns A-1, A-2, A-3, all non-blocking).

**Tasks.md location**: `specs/128-prd-128-executive/tasks.md` (51 tasks, triple-signed).

**Wave strategy**: 6 waves, 5-6 sessions, ~17.5 hour critical path.

**Ready for execution**: Yes. Orchestrator should begin with Wave 1 (Phase 0 bootstrap) and enforce the exit criterion at G0 before proceeding.

**Watchpoints for orchestrator**:
1. Enforce G0 (`make test` exit 0) before any Wave 2 task begins.
2. Verify T003c determinism before accepting baselines.
3. Ensure T007, T017, T028 test-first gates actually report FAIL before corresponding implementation starts.
4. Run T035/T036/T037/T038 in parallel, not sequentially.
5. Do not open the PR (T039) until all four gates have artifacts in `specs/128-prd-128-executive/`.

---

**End of Agent Assignments**
