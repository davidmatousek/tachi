# Agent Assignments: Large-Architecture Pipeline Resilience (F-374)

**Source**: `tasks.md` v1.5 (2026-11-24), which folds session S1′'s W2′-entry rulings (S1P-T1 to T16, S1P-A1 to A17 and S1P-PM1 to PM6) into v1.4. v1.4 came after the `/aod.analyze` gate, which re-ran clean, and carries the triple sign-off of 2026-11-22 (PM and Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED). Produced by `/aod.tasks` Step 6. Where this file and tasks.md differ, tasks.md governs.

**Agents**: only exact names from `.claude/agents/_README.md`.
- The `tachi-*` agents are subjects under test, never assignees.
- The team-lead assigns and signs off, and is never an assignee.
- The `orchestrator` runs every wave and holds the gates.

**Scope**: 154 tasks in two PRs. PR 1 is 91 tasks (Tracks S and R, #423, delivered as `d03ee9a`). PR 2 is 63 tasks (Track O, #425, base `main`): v1.5 adds T151, T152, T154 and T155, and leaves T153 unused. Task IDs aren't monotonic after v1.0, so phase and wave carry the order.

## 1. Agent Assignment Matrix

One row per task, grouped by PR and then by wave. Estimates are in eng-days. "c" marks a conditional task, and "k" a contingency.

### PR 1

**W0** (5 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T001 | — | X | `devops` | 0.12 | Take the pre-state census in a scratch clone of the committed branch tip (H1, P-10) |
| T002 | — | K4 | `debugger` | 0.25 | Run FR-K4.3's 5 Whys on Run A's Phase 3.5 skip, time-boxed at 0.25 d |
| T003 | — | F | `tester` | 0.25 | S-1's proxy sizes, SC-8's named example, and the fixture generator's skeleton (scratch clone, H1) |
| T004 | — | G | `orchestrator` | 0.10 | Run gate G0 at W0's end |
| T144 | — | PM | `product-manager` | 0.10 c | Conditional, only if T004 records TW-K4 (b): rule what the outcome record and its… |

**W1** (25 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T005 | — | S | `senior-backend-engineer` | 0.20 | Write FR-E.1's shared reference for all three SARIF files, from ADR-050 D7 and D8 |
| T006 | — | S | `senior-backend-engineer` | 0.25 | Write the part-file contract reference (D3, D6, FR-E.3) |
| T007 | — | S | `senior-backend-engineer` | 0.20 | S runs this first, because T008 waits for it (TL-T15) |
| T008 | — | O1 | `senior-backend-engineer` | 0.30 | After T007, write N4's and N14's text in the orchestrator (US-4's text; FR-N4.1,… |
| T009 | — | O1 | `senior-backend-engineer` | 0.30 | After T008, remove or rewrite the five other platform-neutral clauses and state the… |
| T010 | — | O1 | `senior-backend-engineer` | 0.15 | After T005–T009, T013, T015 and T016 (AR-T12), write `test_contract_text_374.py`'s W1… |
| T011 | — | R0a | `senior-backend-engineer` | 0.35 | Write the tests first for `tachi_parts`, D16's hostile-input matrix: **Structure and… |
| T012 | — | R0a | `senior-backend-engineer` | 0.40 | Write `tachi_parts.py`, part 1, to T011 |
| T013 | — | R0a | `senior-backend-engineer` | 0.35 | Write `tachi_parts.py`, part 2: slots, numeral ban and fallback, escaping, guards, atomic write, stamp |
| T014 | — | R0b | `senior-backend-engineer` | 0.45 | Write `tachi_scoring.py` (D5, D10) |
| T015 | — | R0b | `senior-backend-engineer` | 0.30 | After T016, make `sarif_common.py` the installed shared emitter (D7, D8) |
| T016 | — | R0b | `senior-backend-engineer` | 0.25 | Before T015 and after T012's identifier slice (AR-T1), add D7's URI resolver to… |
| T017 | — | R0c | `senior-backend-engineer` | 0.35 | Write the tests first for `tachi-stage.py`, on the gated subset, with small sizes… |
| T018 | — | R0c | `senior-backend-engineer` | 0.40 | After T012 and T017, write `tachi-stage.py` to T017 (D3, D4, D6; `contracts/cli.md`):… |
| T019 | — | F | `tester` | 0.50 | Generate the fixture's base set (S-4) |
| T020 | — | F | `tester` | 0.20 | Write `test_fixture_374.py` |
| T021 | — | L | `tester` | 0.35 | After T019, run the v4.48.4 baselines live in T141's scratch adopters, before any… |
| T022 | — | X | `devops` | 0.40 | Wire W1, module by module in lock-step (H7): **Manifest:** add `tachi_parts.py`,… |
| T023 | — | ADR | `architect` | 0.30 | At W1's start, record T004's sizes as D6's "Amended at W0" table, with a Revision… |
| T024 | — | ADR | `architect` | 0.10 | Write the system-design append that `/aod.project-plan` Step 6 deferred to W1:… |
| T025 | — | X | `devops` | 0.10 | In T024's commit: run `tests/fixtures/regenerate-baseline.sh` in the integration tree… |
| T026 | — | G | `orchestrator` | 0.10 | Run gate G1, the cut line (M2) |
| T140 | — | R0c | `senior-backend-engineer` | 0.10 | After T016 and T018, add `architecture-source` to `tachi-stage.py`, last (AR-T1, TL-T2) |
| T141 | — | X | `devops` | 0.10 | At W1's start, before T021, set up two scratch adopters at v4.48.4 with… |
| T149 | — | R0c | `senior-backend-engineer` | 0.15 | Write S-11's `test_runtime_floor_374.py` (split from T017, TL-T8): `ast.parse(...,… |

**W2** (26 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T027 | US1a | R1t | `senior-backend-engineer` | 0.25 | Before T028, write goldens for the whole `risk-scores.md` and `.sarif` |
| T028 | US1a | R1 | `senior-backend-engineer` | 0.45 | After T027, T033 and T042 (AR-T12): Write `render-risk-scores.py`, the whole-file… |
| T029 | US1a | C | `senior-backend-engineer` | 0.45 | Make `risk-scorer.md` judgment-only (D2, D3; FR-N14.1, FR-K6.3) |
| T030 | US1a | C | `senior-backend-engineer` | 0.45 | Write `/tachi.risk-score`'s batch-and-resume loop (D4) |
| T031 | US1a | C | `senior-backend-engineer` | 0.30 | Update the scorer's template and references (D2, D5, D9, D15) |
| T032 | US1a | P | `senior-backend-engineer` | 0.35 | Add the drift forms (S-12, FR-E.16) |
| T033 | US1a | P | `senior-backend-engineer` | 0.20 | Add the shared reference decoder (D3): one closed decoder that runs after a row splits… |
| T040 | US5 | F | `tester` | 0.45 | Build S-4's PR 1 variants, each with an expected-outcomes file: **seeded-error:** per… |
| T041 | US5 | R1t | `senior-backend-engineer` | 0.35 | Before T045 and T046, write SC-4's goldens on T040's variants |
| T042 | US5 | R1b | `senior-backend-engineer` | 0.50 | Write `tachi_scoring_rules.py`, part 1 (D5, D9) |
| T043 | US5 | R1b | `senior-backend-engineer` | 0.40 | Write `tachi_scoring_rules.py`, part 2 (D9, D10): R-25's asset outcome, `max(assessed,… |
| T044 | US5 | R1b | `senior-backend-engineer` | 0.20 | After T042, add scorer planning to `tachi-stage.py` (D2) |
| T045 | US5 | R1 | `senior-backend-engineer` | 0.35 | Write recompute and flag in `render-risk-scores.py`, part 1 (D9 steps 1–4, D10):… |
| T046 | US5 | R1 | `senior-backend-engineer` | 0.35 | After T048 (AR-T12): Write recompute and flag, part 2: **Governance.** Overrides are… |
| T047 | US5 | X | `devops` | 0.20 | Wire W2 in lock-step (H7): add `render-risk-scores.py` and `tachi_scoring_rules.py` to… |
| T048 | US6a | P | `senior-backend-engineer` | 0.15 | Write `parse_correlation_groups` (D8) and its tests |
| T049 | US6a | R1t | `senior-backend-engineer` | 0.25 | Write the tests first: FR-E.2's two-run model for `risk-scores.sarif` |
| T050 | US6a | R1 | `senior-backend-engineer` | 0.45 | Emit `risk-scores.sarif` through the shared emitter (D7, D8, FR-K6.2) |
| T051 | US6a | C | `senior-backend-engineer` | 0.15 | Make PR 1's edits to `/tachi.threat-model`, under P-2's anchors: Step 2.5 and Step 3… |
| T057 | US3 | P | `senior-backend-engineer` | 0.25 | Make `parse_compensating_controls_md` read both formats to the same rows (FR-K8.2;… |
| T058 | US3 | P | `senior-backend-engineer` | 0.20 | Run lane P's data-layer oracle in a scratch clone (H1, H2) |
| T061 | — | ADR | `architect` | 0.15 | Hold the P0 checkpoint at W2's end (M3) |
| T062 | — | G | `orchestrator` | 0.10 | Evaluate TW-ESC at the end of session 1 (W0–W2), as the PM restated it |
| T063 | — | PM | `product-manager` | 0.10 c | Conditional, only if T062 fires: the PM chooses Option A or B for TW-ESC |
| T142 | US6a | P | `senior-backend-engineer` | 0.20 | Add D8's SARIF fallback reader to `tachi_parsers`, with its tests (AR-T2) |
| T143 | US3 | P | `senior-backend-engineer` | 0.15 | Add the reader for §7's persisted controls inputs (AR-T3): one `tachi_parsers`… |

**W3** (14 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T034 | US1a | R2t | `senior-backend-engineer` | 0.20 | Before T035, write goldens for the whole `compensating-controls.md` and `.sarif` |
| T035 | US1a | R2 | `senior-backend-engineer` | 0.50 | Write `render-compensating-controls.py`, the whole-file render (D2, D4, FR-K7.2, FR-K7.3) |
| T036 | US1a | R3a | `senior-backend-engineer` | 0.30 | Add controls planning to `tachi-stage.py` |
| T037 | US1a | D | `senior-backend-engineer` | 0.40 | Make `control-analyzer.md` judgment-only (D2; FR-K7.4, FR-K8.1) |
| T038 | US1a | D | `senior-backend-engineer` | 0.50 | Write `/tachi.compensating-controls`' batch-and-resume loop (D4, FR-K7.4): its first… |
| T039 | US1a | X | `devops` | 0.40 | Update §8 and the runbook in one commit (C7; D3, D4) |
| T052 | US6a | R3a | `senior-backend-engineer` | 0.25 | Before T053, write the tests for `compensating-controls.sarif` |
| T053 | US6a | R2 | `senior-backend-engineer` | 0.25 | Emit `compensating-controls.sarif` through the shared emitter |
| T054 | US6a | R3a | `senior-backend-engineer` | 0.35 | Retire `generate-risk-scores-sarif.py` (#357), and migrate the three modules that pin… |
| T055 | US6a | X | `devops` | 0.10 | Make PR 1's FR-E.11 edit in both Code Scanning snippets… |
| T056 | US3 | R2t | `senior-backend-engineer` | 0.25 | Before T059, write R-34's goldens |
| T059 | US3 | R2 | `senior-backend-engineer` | 0.30 | Render §2 and §4 under R-34 in `render-compensating-controls.py` |
| T060 | US3 | D | `senior-backend-engineer` | 0.15 | Bring the controls template to 1.1 (D15): K8's Section 2 schema with MAESTRO Layer and… |
| T064 | — | SEC | `security-analyst` | 0.20 | Give an advisory review of part validation and path handling (NFR-10, C-9) in… |

**W4** (8 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T065 | — | E2E | `tester` | 0.30 | Run the offline end-to-end test on the fixture, in a scratch clone of the committed W3… |
| T066 | — | OR | `tester` | 0.40 | Run the small-run oracle (NFR-1) in a scratch clone over every shipped example that… |
| T067 | — | REV | `code-reviewer` | 0.30 | Review PR 1's full diff |
| T068 | — | SEC | `security-analyst` | 0.15 | Run the Step 7 security scan, and name every new script in it |
| T069 | — | X | `devops` | 0.10 | Push the W4 tip once |
| T070 | — | ADR | `architect` | 0.15 | Hold the P1 checkpoint (M4), after T065–T069 |
| T071 | — | CI | `debugger` | 0.15 c | Conditional, at any push of either PR. If TW-CI fires (the same gated failure red on… |
| T146 | — | FX | `senior-backend-engineer` | 0.25 c | Conditional, PR 1's fix lane: fix T065–T068's findings in the owning lane's files… |

**W5** (8 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T072 | — | X | `devops` | 0.15 | Set up W5's scratch adopters: install the committed branch build with… |
| T073 | US1a | L1 | `tester` | 0.35 | Run `/tachi.risk-score` live on the fixture's precomputed `threats.md`, at the adopter… |
| T074 | US1a | L2 | `tester` | 0.35 | Run `/tachi.compensating-controls` live on the fixture with the stub codebase, at both… |
| T075 | US1a | L1 | `tester` | 0.15 | Run SC-8's post-fix runs on T004's example, under P-7's conditions: the scorer, then… |
| T076 | — | L2 | `tester` | 0.20 | Run R-27's smoke run under the session profile: `/tachi.threat-model` on a shipped… |
| T077 | — | G | `orchestrator` | 0.10 | Run the W5 gate (M5a) |
| T078 | — | PM | `product-manager` | 0.10 c | Conditional, only on a return from T077 |
| T147 | — | FX | `senior-backend-engineer` | 0.25 c | Conditional, PR 1's fix lane in W5: TW-L2's fix-and-rerun for a shipped-code defect… |

**W6** (5 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T079 | — | CO | `product-manager` | 0.30 | After T080 (PM-T6), write PR 1's binding release notes (R-1) |
| T080 | — | CO | `architect` | 0.25 | Write S-16's KB entry on output-cap overflow (Entry 27), and add the f374 jobs to the… |
| T081 | — | CO | `devops` | 0.10 | In T080's commit, run `regenerate-baseline.sh` in the integration tree that holds… |
| T082 | — | CO | `devops` | 0.25 | Deliver PR 1 (M6a): (1) Put FR-E.17's ledger in the PR body: one disposition per Track… |
| T083 | — | CO | `orchestrator` | 0.15 | Write PR 1's completion report for the team-lead's sign-off: every PR 1 task checked,… |

### PR 2

**W1′** (7 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T084 | — | X | `devops` | 0.15 | After T026, cut PR 2's branch `374-pipeline-resilience-track-o` from the cut-line… |
| T086 | — | ADR | `architect` | 0.15 | Rule O-α (`phase2`) |
| T087 | — | ADR | `architect` | 0.15 | Rule O-β (`threats-md`) |
| T088 | — | ADR | `architect` | 0.20 | Rule O-γ, the `report` payload: a findings part's item keys; the rows that D14 says… |
| T089 | — | G | `orchestrator` | 0.10 | Run the TW-ADR gate before W2′. T086–T088 must be committed as ADR-050 rev |
| T093 | US4 | O2 | `senior-backend-engineer` | 0.45 | Once T086 commits, write the orchestrator's Phases 1–3 (D11) |
| T148 | — | F | `tester` | 0.25 | Build PR 2's fixture cases that wait on no ruling: S-4's chain-cap variant (more than… |

**W2′** (24 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T085 | — | X | `devops` | 0.20 | Done (v1.5): T127's integration at W2′'s entry: M1 `7abc02a`, the marker `bed95a9`, M2 `bb0154b`; parity PASS |
| T090 | — | ADR | `architect` | 0.10 | Rule O-α's end-marker predicate from T104's layout table (deferral condition 3), and… |
| T091 | — | R3b | `senior-backend-engineer` | 0.30 | Add PR 2's key sets to `tachi_parts.py` (D15, RR5), with validator cases: **Records**… |
| T092 | — | OS | `senior-backend-engineer` | 0.50 | Add `tachi-stage.py`'s PR 2 modes, with their tests: the run-level `threat-model` plan… |
| T094 | US4 | O2 | `senior-backend-engineer` | 0.20 | Finalize `dispatch-rules.md` and `dispatch-record-brief-shared.md` as the templates PR… |
| T099 | US6b | R3b | `senior-backend-engineer` | 0.30 | Write the `threats.sarif` tests first, with the identity cases and FR-E.13's pin |
| T100 | US6b | R3b | `senior-backend-engineer` | 0.40 | Rewrite `generate-threats-sarif.py` as the installed generator, on the shared emitter… |
| T103 | US1b | F | `tester` | 0.45 | First, regenerate `fixtures/large_arch/` from the merged generator, since T148 and… |
| T104 | US1b | L | `tester` | 0.30 | With W2′'s step-3 dispatches (H14's throttle is retired), run S-9's spike live, under the… |
| T105 | US1b | OS | `senior-backend-engineer` | 0.30 k | Contingency O-α: not fired at T089, so it doesn't run |
| T106 | US1b | HL | `senior-backend-engineer` | 0.25 | Write `join-threats-md.py` on the shared path (moved from OS, v1.5) |
| T107 | US1b | HL | `senior-backend-engineer` | 0.30 k | Contingency O-β, fired at T089: the joiner's manifest and payload checks (moved from OS, v1.5) |
| T108 | US1b | T | `senior-backend-engineer` | 0.40 | Write `assemble-report.py trees`, tests first (D14) |
| T109 | US1b | T | `senior-backend-engineer` | 0.50 | Write `assemble-report.py report`, tests first (D14) |
| T110 | US1b | T | `senior-backend-engineer` | 0.25 k | Contingency O-γ, fired at T089: the richer report payload's validator cases… |
| T114 | US1b | X | `devops` | 0.35 | W2′'s three pushes (H6's two entry exceptions, then the wave) and its lock-step wiring (H7) |
| T115 | US2 | OCt | `tester` | 0.35 | Write the tests first for `attack-chains.py` (D13): two `plan` runs are… |
| T116 | US2 | OC | `senior-backend-engineer` | 0.50 | First, while OCt writes T115 and OC would otherwise idle, land… |
| T117 | US2 | OC | `senior-backend-engineer` | 0.40 | Write `attack-chains.py render` and `check` (D13, FR-K4.1, FR-K4.1b, R-24) |
| T150 | US6b | R3b | `senior-backend-engineer` | 0.10 | Extend S-11's `test_runtime_floor_374.py` for PR 2 (E1) |
| T151 | — | HL | `senior-backend-engineer` | 0.45 | #443's hoist, part 1 (v1.5): the shared stage-entry path in `tachi_parts`, with the controls renderer on it (S1P-A10 to S1P-A12) |
| T152 | — | HL | `senior-backend-engineer` | 0.30 | #443's hoist, part 2: the planner, the risk renderer and the scoring rules on the shared path, then E1–E5 and S1P-PM2's check |
| T154 | — | ADR | `architect` | 0.15 | W2′'s entry: the cross-read (S1P-A4), and the hoist's contract text (S1P-A16) |
| T155 | — | G | `orchestrator` | 0.10 | W2′'s entry gate: the census (PR 2's pre-state), the dispatch gates and TW-HL |

**W3′** (14 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T095 | US4 | OC | `senior-backend-engineer` | 0.35 | Before T096, write the tests for `check-threat-model.py` (D12): carried, renumbered,… |
| T096 | US4 | OC | `senior-backend-engineer` | 0.45 | Write `check-threat-model.py` (D12, FR-N4.5, FR-N4.6, FR-E.10, FR-E.19): the three… |
| T097 | US4 | O3 | `senior-backend-engineer` | 0.40 | Add `/tachi.threat-model`'s PR 2 steps, under P-2's anchors, following D4's table:… |
| T098 | US4 | X | `devops` | 0.40 | Update §8 and the runbook in one commit (C7): §8.3: the orchestrator's writes under… |
| T101 | US6b | O3 | `senior-backend-engineer` | 0.30 | Point `sarif-specification.md`'s identity and membership sections (`:197-280`,… |
| T102 | US6b | X | `devops` | 0.10 | Make PR 2's FR-E.11 edit |
| T111 | US1b | O2 | `senior-backend-engineer` | 0.35 | Handle Phase 2's overflow (FR-N4.7, D6, S-8) |
| T112 | US1b | O2 | `senior-backend-engineer` | 0.40 | Write Phases 3.6, 4 and 5 (D4 steps 5–8, D14): Phase 3.6 and Phase 4 come before any… |
| T113 | US1b | T | `senior-backend-engineer` | 0.45 | Update the report and tree agents (D14, FR-K5.1, FR-K5.4): `threat-report.md` writes… |
| T118 | US2 | O2 | `senior-backend-engineer` | 0.25 | Write Phase 3.5's text (D13; `orchestrator.md:395-554`) |
| T119 | US2 | O3 | `senior-backend-engineer` | 0.20 | Update the record's schema text: `output-schemas.md`: `:285`'s stale 1.2 becomes 1.4,… |
| T120 | US2 | P′ | `senior-backend-engineer` | 0.40 | Add FR-K4.1's readers (D13), with cases in both chain test modules: T116's… |
| T121 | US2 | P′ | `senior-backend-engineer` | 0.20 | Run lane P′'s data-layer oracle for T120's readers, in a scratch clone |
| T122 | — | G | `orchestrator` | 0.10 | Check PR 2's bound at W3′'s end |

**W4′** (6 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T123 | — | PM | `product-manager` | 0.10 c | Conditional, only if T089 or T122 fires: rule on PR 2's projection above its bound |
| T124 | — | E2E | `tester` | 0.40, +0.10 c | Run the threat-model stage's offline end-to-end test on the fixture, in a scratch clone. The re-run after T127 is conditional (v1.5) |
| T125 | — | REV | `code-reviewer` | 0.35 | Review PR 2's delta, `git diff origin/main...HEAD` (GitHub's diff since T085), with the hoist included |
| T126 | — | SEC | `security-analyst` | 0.25 | Run the Step 7 scan on `git diff origin/main...HEAD`, naming PR 2's scripts and the hoisted helpers |
| T127 | — | X | `devops` | 0.15 | The integration's residual (v1.5): a plain re-merge only if `main` moved, the parity re-check, D16's figures, the push and TW-CI |
| T128 | — | ADR | `architect` | 0.15 | Hold the P1′ checkpoint, after T124–T127 |

**W5′** (7 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T129 | — | X | `devops` | 0.15 | Set up W5′'s scratch adopters: the branch build installed with `scripts/install.sh`;… |
| T130 | US1b | L | `tester` | 0.45 | Run `/tachi.threat-model` baseline-aware on the fixture, at the adopter default effort… |
| T131 | US1b | L | `tester` | 0.50 | Unless TW-L1 fired, run `/tachi.threat-model` at `effort=max`, covering the report… |
| T132 | US4 | L | `tester` | 0.30 | Check the typed-agent stop: a small threat-model run with one roster agent uninstalled… |
| T133 | — | G | `orchestrator` | 0.10 | Run the W5′ gate (M5b) |
| T134 | — | PM | `product-manager` | 0.10 c | Conditional, only on a return from T130 or T133 |
| T145 | US1b | L | `tester` | 0.30 | After T111, plant a truncation in a live run of the built branch, by S-9's method (PM-T2) |

**W6′** (5 tasks)

| Task | Story | Lane | Agent | Est. (d) | Task, in brief |
|---|---|---|---|---|---|
| T135 | — | CO | `product-manager` | 0.30 | After T136 (PM-T6), write PR 2's release notes: items 1, 2 and 5, each for PR 2's scope |
| T136 | — | CO | `architect` | 0.20 | Add the system-design extract's Track O rows; T137 lands in the same commit (H4) |
| T137 | — | CO | `devops` | 0.15 | In T136's commit, run `regenerate-baseline.sh` in the integration tree that holds… |
| T138 | — | CO | `devops` | 0.25 | Deliver PR 2 (M6b): (1) Put FR-E.17's last row in the PR body |
| T139 | — | CO | `orchestrator` | 0.15 | Write PR 2's completion report for the team-lead's sign-off |

## 2. Parallel Execution Waves

### PR 1

| Wave | Session | Lanes: agent instance (base effort in d) | Pacing chain + tail | Window (d) |
|---|---|---|---|---|
| W0 | S1 | X: `devops` (0.12); K4: `debugger` (0.25); F: `tester` (0.25); G: `orchestrator` (0.10); PM: `product-manager` (0.00, +0.10 c/k) | T002 or T003, 0.25 | 0.35 |
| W1 | S1 | S: `senior-backend-engineer` (0.65); O1: `senior-backend-engineer` (0.75); R0a: `senior-backend-engineer` (1.10); R0b: `senior-backend-engineer` (1.00); R0c: `senior-backend-engineer` (1.00); F: `tester` (0.70); L: `tester` (0.35); X: `devops` (0.60); ADR: `architect` (0.40); G: `orchestrator` (0.10) | T011 → T012's slice → T016 → T015 → T010, and T017 → T018 → T140: 1.25 + 0.2 | 1.6 |
| W2 | S1 | R1t: `senior-backend-engineer` (0.85); R1: `senior-backend-engineer` (1.60); C: `senior-backend-engineer` (1.35); P: `senior-backend-engineer` (1.50); F: `tester` (0.45); R1b: `senior-backend-engineer` (1.10); X: `devops` (0.20); ADR: `architect` (0.15); G: `orchestrator` (0.10); PM: `product-manager` (0.00, +0.10 c/k) | T027 → T028 → T050 → T045 → T046: 1.9 + 0.35 | 2.4 |
| W3 | S2 | R2t: `senior-backend-engineer` (0.45); R2: `senior-backend-engineer` (1.05); R3a: `senior-backend-engineer` (0.90); D: `senior-backend-engineer` (1.05); X: `devops` (0.50); SEC: `security-analyst` (0.20) | T034 → T035 → T053 → T059: 1.3 + 0.1 | 1.65 |
| W4 | S2 | E2E: `tester` (0.30); OR: `tester` (0.40); REV: `code-reviewer` (0.30); SEC: `security-analyst` (0.15); X: `devops` (0.10); ADR: `architect` (0.15); CI: `debugger` (0.00, +0.15 c/k); FX: `senior-backend-engineer` (0.00, +0.25 c/k) | T066 → T146 → T069 → T070: 0.65 + 0.25 | 0.9 |
| W5 | L | X: `devops` (0.15); L1: `tester` (0.50); L2: `tester` (0.55); G: `orchestrator` (0.10); PM: `product-manager` (0.00, +0.10 c/k); FX: `senior-backend-engineer` (0.00, +0.25 c/k) | the live matrix's wall clock | 1.25 |
| W6 | S3 | CO: `product-manager` (0.30); CO: `architect` (0.25); CO: `devops` (0.35); CO: `orchestrator` (0.15) | T080 → T081 → T082: 0.6 + 0.15 | 0.75 (+0.15 coordination) |

### PR 2

| Wave | Session | Lanes: agent instance (base effort in d) | Pacing chain + tail | Window (d) |
|---|---|---|---|---|
| W1′ | S2 | X: `devops` (0.15); ADR: `architect` (0.50); G: `orchestrator` (0.10); O2: `senior-backend-engineer` (0.45); F: `tester` (0.25) | the rulings T086–T088 → T089; T093 during PR 1's W3 | inside PR 1's W2–W3 |
| W2′ | S1′ | X: `devops` (0.55); ADR: `architect` (0.25); G: `orchestrator` (0.10); HL: `senior-backend-engineer` (1.00, +0.30 k, fired); R3b: `senior-backend-engineer` (1.10); OS: `senior-backend-engineer` (0.50, +0.30 k, not fired); O2: `senior-backend-engineer` (0.20); F: `tester` (0.45); L: `tester` (0.30); T: `senior-backend-engineer` (0.90, +0.25 k, fired); OCt: `tester` (0.35); OC: `senior-backend-engineer` (0.90) | v1.5: T085 → the entry gate → T151 → T152 (E1–E5) → T116 → T117 → T150: 2.0 with TW-ADR's increments, + 0.1 | 2.5 |
| W3′ | S1′ | OC: `senior-backend-engineer` (0.80); O3: `senior-backend-engineer` (0.90); X: `devops` (0.50); O2: `senior-backend-engineer` (1.00); T: `senior-backend-engineer` (0.45); P′: `senior-backend-engineer` (0.60); G: `orchestrator` (0.10) | T111 → T112 → T118: 1.12 with TW-ADR's increments, and no throttle (H14 is retired, v1.5), + 0.2 | 1.4 |
| W4′ | S2′ | PM: `product-manager` (0.00, +0.10 c/k); E2E: `tester` (0.40, +0.10 c/k); REV: `code-reviewer` (0.35); SEC: `security-analyst` (0.25); X: `devops` (0.15); ADR: `architect` (0.15) | v1.5: T124 (0.4) → T127's residual (0.15): 0.55 + 0.15 | 0.7 |
| W5′ | L′ | X: `devops` (0.15); L: `tester` (1.55); G: `orchestrator` (0.10); PM: `product-manager` (0.00, +0.10 c/k) | the live matrix's wall clock, with T145 | 2.0 |
| W6′ | S3′ | CO: `product-manager` (0.30); CO: `architect` (0.20); CO: `devops` (0.40); CO: `orchestrator` (0.15) | T136 → T137 → T138: 0.6 + 0.15 | 0.75 (+0.15 coordination) |

### Sessions (`/aod.build`, at most three waves per session)

| Session | Waves | Ends with |
|---|---|---|
| S1 | PR 1's W0, W1, W2 | the NEXT-SESSION handoff at T062 (M3) |
| S2 | PR 1's W3 and W4, plus PR 2's W1′ | a handoff after T070 (M4) |
| L | PR 1's W5 | the W5 gate, T077 (M5a) |
| S3 | PR 1's W6 | PR 1 delivered, T082 and T083 (M6a) |
| S1′ | PR 2's W2′ and W3′, in PR 2's own worktree. W2′ includes its entry: T085, the entry gate, the hoist and the two entry pushes. Two waves, so it stays under the three-wave ceiling | the NEXT-SESSION handoff at T122 |
| S2′ | PR 2's W4′ | P1′, T128 |
| L′ | PR 2's W5′ | the W5′ gate, T133 (M5b) |
| S3′ | PR 2's W6′ | PR 2 delivered, T138 and T139 (M6b) |

**Lane CO** (W6, W6′) runs one agent per close-out task: `product-manager` for the notes and bookkeeping, `architect` for the KB entry, design rows and follow-ups, `devops` for the regeneration and delivery, and `orchestrator` for the completion report and the tail (F4). Lane X holds W5's and W5′'s adopter setup (T072, T129). Lane F regenerates the fixture at the start of T103 (C2), inside W2′'s entry gate and before the pre-hoist push (S1P-A5). Lane X also makes W2′'s three pushes (T114). Lane HL (v1.5) runs #443's hoist at W2′'s entry (T151, T152), then the joiner (T106, T107).

## 3. Quality Gates Between Waves

| Gate | Task | At | Checks | Trip-wires evaluated |
|---|---|---|---|---|
| G0 | T004 (orchestrator) | W0's end | the pre-state, the 5 Whys outcome, the S-1 sizes and the SC-8 example are recorded; #400's conflict list | TW-K4 (→ T144 on (b)), TW-N3 |
| G1, the cut line | T026 (orchestrator) | W1's end (M2) | plan.md's Verification item 2; both CI legs green on the committed HEAD; the cut-line SHA for T084 | TW-N3 at W2's entry; TW-CI (T022's push) |
| G2 | T061 (architect), then T062 (orchestrator, invoking the team-lead) | W2's end (M3) | P0 checkpoint; PR 1 re-projected from actual lane times, and PR 2 against its bound under each option | TW-ESC as the PM restated it (→ T063), TW-N3, TW-CI (T047) |
| G3 | T069 (devops), then T070 (architect) | W4's end (M4) | one push, both legs green against T001's totals; ADR-050 D16's coverage gate, with its figures recorded (a shortfall goes to T146); P1 checkpoint | TW-CI (→ T071) |
| G4 | T077 (orchestrator) | W5's end (M5a) | the live matrix's dispositions | TW-L2, the PM's 25% fallback return and the SC-8 overage (→ T078) |
| G5 | T083 (orchestrator) | after PR 1 merges (M6a) | the completion report for the team-lead's sign-off; the `[POST-MERGE]` tail issue | — |
| G1′ | T089 (orchestrator) | W1′'s end | O-α, O-β, O-γ and RR3 ruled as ADR-050 rev. 3; contingencies marked fired or not | TW-ADR; PR 2's bound, the all-three case included (→ PM with T123); TW-N3 |
| G1′e (v1.5) | T155 (orchestrator) | W2′'s entry | T085's parity (done); T154's cross-read; T103's regeneration slice; the entry census, which is PR 2's pre-state (S1P-PM5); T152's E1–E5 and S1P-PM2's check before any code against the hoist | TW-HL; TW-CI at the pre-hoist push and at the entry push (T114); TW-N3 |
| G2′ | T122 (orchestrator, invoking the team-lead) | W3′'s end | PR 2 re-projected from actual lane times | PR 2's bound (→ T123), TW-N3, TW-CI (T098) |
| G3′ | T127 (devops), then T128 (architect) | W4′'s end | T127's residual (v1.5): a plain re-merge only if `main` moved, and the parity re-check; one push green against the entry's totals; ADR-050 D16's coverage gate, with its figures recorded (the owning lanes close any shortfall); P1′ | TW-CI (→ T071) |
| G4′ | T133 (orchestrator) | W5′'s end (M5b) | the live matrix's dispositions | TW-L1 (from T130 → T134), TW-L2, TW-L3, TW-CTX, the PM's 25% fallback return (→ T134) |
| G5′ | T139 (orchestrator) | after PR 2 merges (M6b) | the completion report for the team-lead's sign-off; the `[POST-MERGE]` tail issue | — |

**ADR-050 D16's coverage gate** (v1.3, D1):
- **Wiring.** T022 wires it (W1, checked at G1). It is extended by T047 (W2, G2), T039 (W3), T114 (W2′) and T098 (W3′, G2′), each in the same commit as its wave's gated modules. The wiring also uses "F-373's S-13 import gate" for the stdlib-only import check (F2).
- **Records.** The figures are recorded at G3 (T069) and G3′ (T127). Since v1.5 they are also recorded at W2′'s entry, by T152's E2.
- **The DoD.** tasks.md's DoD item 2 now requires unit coverage of at least 80% on the gated modules, per ADR-050 D16 (constitution VI, VII).

## 4. Time Estimates (copied from tasks.md)

Each window is max(longest stated chain × 1.25, chain + push-and-gate tail), rounded up to 0.05.

| PR | Plan | W0 | W1 | W2 | W3 | W4 | W5 | W6 | Coordination | Central | Floor / ceiling |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 | 0.35 | 1.6 | 2.4 | 1.65 | 0.9 | 1.25 | 0.75 | 0.15 | **T0 + 10.05** | 7.95 / 15.6 |

| PR | Start | W2′ | W3′ | W4′ | W5′ | W6′ | Coordination | Central | Floor / ceiling |
|---|---|---|---|---|---|---|---|---|---|
| 2 | T0 + 7.0 (PR 1's W3 end) | 1.8 | 1.35 | 0.95 | 2.0 | 0.75 | 0.15 | **T0 + 14.0** | 10.95 / 22.15 |
| 2, v1.5 | T0 + 7.0 (the plan's basis) | 2.5 | 1.4 | 0.7 | 2.0 | 0.75 | 0.15 | **T0 + 14.5** | 11.45 / 22.95 |

- **PR 1** against TW-0, re-based to **T0 + 11.0** (condition 4, Option A): a margin of 0.95.
- **PR 2** against its bound, **T0 + 15.0**:
  - all three contingencies: T0 + 14.6 (margin 0.4);
  - T150's runtime floor (+0.1) lengthens W2′'s chain (re-run F10);
  - W3′'s throttle (+0.1) and T124's re-run (+0.05) are now in the central (F8). v1.5 removes both: H14 is retired, and T124's re-run is conditional;
  - **v1.5:** T0 + 14.5 on the plan's basis, a margin of 0.5. On the measured basis it is about T0 + 10.15. Across the hoist's estimate band it runs from T0 + 14.25 to 14.85, and TW-HL caps the fallback at about T0 + 14.75.
- **Ratio.** PR 1 implies 0.45, on 22.57 base eng-days. Confidence LOW–MEDIUM.
- **W1′** runs inside PR 1's W2–W3 (T0 + 2.95 to 7.0), off PR 2's critical path.

## 5. Binding Dispatch Overrides

- **Lanes F and OCt (`tester`).** Their output is pytest under `tests/scripts/`, with `conftest.py`. No Gherkin, no `.feature` files, and no `tests/features/`. The orchestrator rejects any such output at integration (TL-T5).
- **Reviewer tasks T064, T067, T068, T125 and T126.** Review and scan the new scripts as production code. This overrides the knowledge-system supplement's "no application code" framing, as F-373 and F-391 did (C-9). T125 and T126 diff `origin/main...HEAD`, which since T085 is GitHub's own diff, #443's hoist included (v1.5, S1P-A7).
- **Lane HL (`senior-backend-engineer`), #443's hoist (T151, T152; v1.5):**
  - **Scope:** exactly S1P-A10's list, under S1P-A11 and S1P-A12. Anything beyond it goes to the PM (S1P-PM1).
  - **No user-visible change** for any caller (S1P-PM2).
  - **E1–E5 must be green** before any lane writes code against the hoist (condition 5).
  - **References:** commits and the PR say "Refs #443", never a closing keyword (S1P-PM3).
- **Team-lead re-projections.** The orchestrator invokes the team-lead for T062 and T122. The team-lead is never dispatched as a task's assignee.
- **The H-rules**, in brief (tasks.md holds the full text):
  - **H1:** no pytest, extractor or renderer runs in the main tree. Use a scratch clone of the committed tip, run `/aod.build` with `--no-tests`, and check `git status` after every agent returns.
  - **H2:** no PDF baseline is regenerated, and no re-rendered PNG is committed.
  - **H3:** stage explicit paths only.
  - **H4:** an init-baseline target edit regenerates the baseline in the same commit. Run the script in the integration tree, then Test-1 in a scratch clone.
  - **H5:** no commit while a dispatched agent is still writing. For a mid-wave hand-off, the orchestrator commits a returned task's paths on its lane branch, in that lane's own worktree, and dependents cherry-pick it. The wave still integrates once.
  - **H9:** each lane works in its own worktree and is integrated by cherry-pick. Never read another lane's uncommitted files, and never switch branches in the main checkout.
  - **H6:** commit before gating; push once per wave, and never a records-only push. v1.5 adds two exceptions in W2′, and all three of W2′'s pushes are T114's:
    - the pre-hoist push: T085's merges with T103's slice, before T151 commits. It is the pre-state's CI half;
    - the entry push: the hoist, once E1–E5 are green.
  - **H14:** retired for PR 2 at v1.5 (S1P-T7). PR 1 is delivered, so the throttle, its escalation and the five-lane fallback no longer apply, and T104 triggers nothing. Two parts stay:
    - the cap: five senior-backend-engineer lanes in flight;
    - the usage clause: an interruption is never a TW-L2 attempt.

## 6. Capacity

- **The cap.** At most five `senior-backend-engineer` lanes have agents in flight at once:
  - W1, W2 and W3′ reach five, and W3 has four;
  - W2′ has six lanes (HL, R3b, OS, T, OC and O2), but never more than five in flight (v1.5). It reaches five at the hoist's start and again from about W2′ + 1.17 to 1.53, with fewer in between;
  - W1′ added O2's T093 only during PR 1's W3.
- **The conditional fix lane (FX).** T146 covers W4's review findings, and T147 covers W5's TW-L2 fix-and-rerun (0.25 d each). It counted toward the cap. PR 1 is delivered, so it can't run again (v1.5).
- **The five-lane fallback (H14)** is retired at v1.5: with no FX lane, PR 2 yields nothing. It used to make O2 hold T094 in W2′, and P′ slip first in W3′.
- **The load rule.** No agent instance runs above 80% of its wave window.

### Load by agent

| Agent | Tasks | Effort (d), conditional and contingency included |
|---|---|---|
| `senior-backend-engineer` | 78 | 24.50 |
| `tester` | 20 | 6.90 |
| `devops` | 20 | 3.92 |
| `architect` | 12 | 2.05 |
| `product-manager` | 7 | 1.10 |
| `orchestrator` | 10 | 1.10 |
| `code-reviewer` | 2 | 0.65 |
| `security-analyst` | 3 | 0.60 |
| `debugger` | 2 | 0.40 |
