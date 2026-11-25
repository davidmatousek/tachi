# T083: PR 1's completion report (W6, gate G5)

**Date:** 2026-11-24. **Lane:** CO (orchestrator), build session S3. **For:** the team-lead's sign-off.
**Delivered:** PR #423, squash-merged to `main` as `d03ee9a` at 17:48 on 2026-11-24 (-05:00). Its parent is `b040fa1` (v4.48.4), so `main` took no other commit in between.
**Release:** v4.48.5, published at 19:44 on 2026-11-24 (-05:00). Release-please PR #462, "chore(main): release 4.48.5", merged as `cb06251`, which is the tag's commit, and the release carries PR 1's notes (https://github.com/davidmatousek/tachi/releases/tag/v4.48.5).
**Parent issue:** #374, which stays open until PR 2 merges. PR 2 is the draft #425, based on `main`.

Records are under `specs/374-large-architecture-pipeline-resilience/test-results/` unless a path says otherwise. `tasks.md`, `release-notes.md`, `economy-check.md` and `security-scan.md` sit one level up, in the feature directory. Commit SHAs other than `d03ee9a` and `b040fa1` are #423's branch commits. They show in the PR's commit list and aren't on `main`, which holds the squash.

## Result: PR 1 is delivered and released; only T071, a conditional task, stays open

| Question | Answer |
|---|---|
| Tasks | 87 of 91 are checked in tasks.md at `d03ee9a` (section 1). By wave: W0 5 of 5, W1 25 of 25, W2 26 of 26, W3 14 of 14, W4 7 of 8, W5 8 of 8, W6 2 of 5. T079, T082 and T083 are done since, which makes 90 of 91 once their boxes are ticked |
| T071 | Open by design. It is conditional: TW-CI never fired on any PR 1 push, and the task stays armed for PR 2 |
| T079 | Done. The binding release notes are written (`release-notes.md`), with the PM's §5b ruling on G-1. PRD §8's bookkeeping followed the release: #357 is closed, #408 and #409 carry their updates, and #397 has N14, N15 and N16 ticked with the N17(a) note |
| T082 | Done, all six steps: merged as `d03ee9a`, release PR #462 merged as `cb06251`, v4.48.5 published, and the release carries PR 1's notes (step 6, checked with `gh release view`) |
| T083 | Done: this report, the example audit leads posted on #364 (https://github.com/davidmatousek/tachi/issues/364#issuecomment-7149052692), and the `[POST-MERGE]` tail opened as #463 |
| `.aod/` | Unchanged between `b040fa1` and `d03ee9a` (section 2) |
| Blockers | Every trip-wire, gate, checkpoint, review and scan is resolved or ruled (section 3) |
| Verified on the merge candidate | The oracle is clean, the offline end-to-end run passed on Python 3.11, 3.9 and 3.14, the census shows 0 regressions, and CI is 14 of 14 on the PR head (section 4) |
| Definition of Done | All three bars are met (section 5): the release is published, and `push:[main]` CI on `d03ee9a` is 5 of 5 green |
| Delivery against TW-0 | T0 + 2.74, against T0 + 11.0 (section 8) |

## 1. The 91 tasks

Status key: **Done**; **Done, not fired** (a conditional task whose trigger never occurred); **Open**.

### Waves, pushes and CI

From W1 on, PR 1 pushed once per wave, and every push was green. All ten head SHAs of #423 that triggered CI (four plan-stage commits and the six wave pushes) ended with every workflow run successful, so the TW-CI condition (the same gated failure red on two consecutive pushes) never arose.

| Wave | Tasks done | Push to #423 (-05:00) | CI on the push | Census, Python 3.11 in a scratch clone: passed / failed / skipped, regressions |
|---|---|---|---|---|
| W0 | 5 of 5 | none: its records went up with W1's push | n/a | 1,730 / 34 / 5, 0 (`9457a3e`) |
| W1 | 25 of 25 | `03a8f0d`, 2026-11-22 22:23 | 12 of 12 | 4,214 / 35 / 38. The 35 are the 34 pre-existing out-of-gate failures plus one ungated render flake that passed 2 of 2 on a re-run (`g1-cutline.md`) |
| W2 | 26 of 26 | `5d218af`, 2026-11-23 02:27 | 14 of 14 | 5,834 / 34 / 30, 0 |
| W3 | 14 of 14 | `f43440b`, 2026-11-23 22:45 | all 7 workflow runs green | 7,266 / 34 / 25, 0 |
| W4 | 7 of 8 | `27d58bd`, 2026-11-24 08:41 | 14 of 14 | 7,597 / 34 / 25, 0 |
| W5 | 8 of 8 | `1e3614a`, 2026-11-24 11:41 | 14 of 14 | 7,599 / 34 / 25, 0 (`867b611`) |
| W6 | 2 of 5 | `8111c5e`, 2026-11-24 17:03 (one push) | 14 of 14 | 7,656 / 34 / 25, 0 (`ad64a72`) |

The 34 pre-existing failures are T001's out-of-gate set (26 failed and 8 errors, with #365's six PDF byte-identity cases among them), identical by test ID in every wave. Per-wave census files: `wave-00/results.json` to `wave-06/results.json`.

### Phase 1.1: Setup (W0)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T001 | W0 · X · devops | Pre-state census, with the `tachi_parsers.py` ratchet floor (44.9%) | Done | `prestate.md` |
| T002 | W0 · K4 · debugger | FR-K4.3's 5 Whys on the Phase 3.5 skip | Done | `k4-five-whys.md` |
| T003 | W0 · F · tester | S-1 proxy sizes, SC-8's example, the fixture generator's skeleton | Done | `s1-proxy.md`; `tests/scripts/generate_large_arch_fixture.py` |
| T004 | W0 · G · orchestrator | Gate G0 | Done | `w0-gate.md` |
| T144 | W0 · PM · product-manager | Rule TW-K4 (b), conditional | Done, not fired: G0 ruled TW-K4 (c) | `w0-gate.md` |

### Phase 1.2: Foundational, the cut line (W1, push `03a8f0d`)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T005 | W1 · S · senior-backend-engineer | Shared SARIF identity reference | Done | `.claude/skills/tachi-shared/references/sarif-identity-shared.md` |
| T006 | W1 · S · senior-backend-engineer | Part-file contract reference | Done | `.claude/skills/tachi-shared/references/part-file-contract-shared.md` |
| T007 | W1 · S · senior-backend-engineer | Canonical agent roster, with the stale rosters pointed at it | Done | `.claude/skills/tachi-shared/references/agent-roster-shared.md` |
| T008 | W1 · O1 · senior-backend-engineer | N4 and N14 contract text in the orchestrator | Done | `.claude/agents/tachi/orchestrator.md` |
| T009 | W1 · O1 · senior-backend-engineer | Five platform-neutral clauses replaced; adapter headers and README warning; FR-E.17 ledger started | Done | `fr-e17-ledger.md` |
| T010 | W1 · O1 · senior-backend-engineer | W1 contract-text assertions | Done | `tests/scripts/test_contract_text_374.py` |
| T011 | W1 · R0a · senior-backend-engineer | `tachi_parts` hostile-input tests, first | Done | `tests/scripts/test_tachi_parts.py` |
| T012 | W1 · R0a · senior-backend-engineer | `tachi_parts.py`, part 1: identifier allow-lists, strict loader, validation steps | Done | `scripts/tachi_parts.py` |
| T013 | W1 · R0a · senior-backend-engineer | `tachi_parts.py`, part 2: slots, numeral ban, fallback, escaping, atomic write, stamp | Done | `scripts/tachi_parts.py` |
| T014 | W1 · R0b · senior-backend-engineer | `tachi_scoring.py`: CVSS 3.1 calculator and decimal arithmetic | Done | `scripts/tachi_scoring.py` |
| T015 | W1 · R0b · senior-backend-engineer | `sarif_common.py` as the shared emitter | Done | `scripts/sarif_common.py` |
| T016 | W1 · R0b · senior-backend-engineer | The URI resolver | Done | `scripts/sarif_common.py` |
| T017 | W1 · R0c · senior-backend-engineer | `tachi-stage.py` tests, first | Done | `tests/scripts/test_tachi_stage.py` |
| T018 | W1 · R0c · senior-backend-engineer | `tachi-stage.py` (plan, reconcile, fail) and the reference-set wrapper | Done | `scripts/tachi-stage.py` |
| T140 | W1 · R0c · senior-backend-engineer | `architecture-source` mode | Done | `scripts/tachi-stage.py` |
| T149 | W1 · R0c · senior-backend-engineer | S-11's runtime-floor test | Done | `tests/scripts/test_runtime_floor_374.py` |
| T019 | W1 · F · tester | Fixture base set | Done | `tests/scripts/fixtures/large_arch/` |
| T020 | W1 · F · tester | `test_fixture_374.py`: determinism and sizing | Done | `tests/scripts/test_fixture_374.py` |
| T141 | W1 · X · devops | Two v4.48.4 scratch adopters | Done | `w1-adopters.md` |
| T021 | W1 · L · tester | v4.48.4 baselines, live: SC-1's and SC-8's | Done | `prefix-baseline.md`; `sc8-baseline.md` |
| T022 | W1 · X · devops | W1 wiring (manifest, three f374 jobs, coverage gate, parser ratchet) and W1's push | Done | `INSTALL_MANIFEST.md`; `.github/workflows/tachi-install-fidelity.yml` |
| T023 | W1 · ADR · architect | ADR-050 D6's sizes recorded and re-amended; eight back-pointer notes | Done | ADR-050; ADR-013, 017, 018, 020, 026, 046, 048 and 049 |
| T024 | W1 · ADR · architect | System-design append for PR 1's components | Done | `docs/architecture/01_system_design/README.md` |
| T025 | W1 · X · devops | Init baseline regenerated in T024's commit | Done | `tests/fixtures/init-baseline-tree/docs/architecture/01_system_design/README.md` |
| T026 | W1 · G · orchestrator | Gate G1, the cut line | Done | `g1-cutline.md` |

### Phase 1.3: User Story 1a, scorer and controls finish complete at any size (W2 and W3)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T027 | W2 · R1t · senior-backend-engineer | Goldens for `risk-scores.md` and `.sarif`, first | Done | `tests/scripts/test_render_risk_scores.py` |
| T028 | W2 · R1 · senior-backend-engineer | `render-risk-scores.py`, the whole-file render | Done | `scripts/render-risk-scores.py` |
| T029 | W2 · C · senior-backend-engineer | `risk-scorer.md` made judgment-only | Done | `.claude/agents/tachi/risk-scorer.md` |
| T030 | W2 · C · senior-backend-engineer | `/tachi.risk-score` batch-and-resume loop | Done | `.claude/commands/tachi.risk-score.md` |
| T031 | W2 · C · senior-backend-engineer | Scorer template (schema 1.1) and references | Done | `templates/tachi/output-schemas/risk-scores.md` and `.sarif` |
| T032 | W2 · P · senior-backend-engineer | Drift forms (S-12, FR-E.16) | Done | `scripts/tachi_parsers.py` |
| T033 | W2 · P · senior-backend-engineer | Shared reference decoder | Done | `scripts/tachi_parsers.py` |
| T034 | W3 · R2t · senior-backend-engineer | Goldens for `compensating-controls.md` and `.sarif`, first | Done | `tests/scripts/test_render_compensating_controls.py` |
| T035 | W3 · R2 · senior-backend-engineer | `render-compensating-controls.py`, the whole-file render | Done | `scripts/render-compensating-controls.py` |
| T036 | W3 · R3a · senior-backend-engineer | Controls planning in `tachi-stage.py` | Done | `scripts/tachi-stage.py` |
| T037 | W3 · D · senior-backend-engineer | `control-analyzer.md` made judgment-only | Done | `.claude/agents/tachi/control-analyzer.md` |
| T038 | W3 · D · senior-backend-engineer | `/tachi.compensating-controls` batch-and-resume loop | Done | `.claude/commands/tachi.compensating-controls.md` |
| T039 | W3 · X · devops | §8 and the isolated-operation runbook updated; W3's push | Done | `docs/standards/CLAUDE_PERMISSIONS.md`; `docs/guides/ISOLATED_OPERATION_TACHI.md` |

### Phase 1.4: User Story 5, carried scores are recomputed and every change is flagged (W2)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T040 | W2 · F · tester | PR 1's fixture variants, each with expected outcomes | Done | `tests/scripts/fixtures/large_arch/` |
| T041 | W2 · R1t · senior-backend-engineer | SC-4 goldens on the variants, first | Done | `tests/scripts/test_render_risk_scores.py` |
| T042 | W2 · R1b · senior-backend-engineer | `tachi_scoring_rules.py`, part 1: baseline resolver and tolerant reader | Done | `scripts/tachi_scoring_rules.py` |
| T043 | W2 · R1b · senior-backend-engineer | `tachi_scoring_rules.py`, part 2: asset outcome, vector check, peers, tag-driven bands | Done | `scripts/tachi_scoring_rules.py` |
| T044 | W2 · R1b · senior-backend-engineer | Scorer planning in `tachi-stage.py` | Done | `scripts/tachi-stage.py` |
| T045 | W2 · R1 · senior-backend-engineer | Recompute and flag, part 1 | Done | `scripts/render-risk-scores.py` |
| T046 | W2 · R1 · senior-backend-engineer | Recompute and flag, part 2: governance, peers, §2a, §6 | Done | `scripts/render-risk-scores.py` |
| T047 | W2 · X · devops | W2 wiring, coverage-gate extension and W2's push | Done | `INSTALL_MANIFEST.md`; `.github/workflows/tachi-install-fidelity.yml` |

### Phase 1.5: User Story 6a, scorer and controls alerts keep their identity (W2 and W3)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T048 | W2 · P · senior-backend-engineer | `parse_correlation_groups` | Done | `scripts/tachi_parsers.py` |
| T142 | W2 · P · senior-backend-engineer | SARIF fallback reader | Done | `scripts/tachi_parsers.py` |
| T049 | W2 · R1t · senior-backend-engineer | FR-E.2's two-run tests for `risk-scores.sarif`, first | Done | `tests/scripts/test_sarif_identity.py` |
| T050 | W2 · R1 · senior-backend-engineer | `risk-scores.sarif` through the shared emitter | Done | `scripts/render-risk-scores.py` |
| T051 | W2 · C · senior-backend-engineer | PR 1's `/tachi.threat-model` edits: presence check and `architecture-source` | Done | `.claude/commands/tachi.threat-model.md` |
| T052 | W3 · R3a · senior-backend-engineer | Tests for `compensating-controls.sarif`, first | Done | `tests/scripts/test_sarif_identity.py` |
| T053 | W3 · R2 · senior-backend-engineer | `compensating-controls.sarif` through the shared emitter | Done | `scripts/render-compensating-controls.py` |
| T054 | W3 · R3a · senior-backend-engineer | `generate-risk-scores-sarif.py` retired (#357); the three modules that pinned it migrated | Done | the script is gone from `scripts/`; `tests/scripts/test_owasp_2026_contract.py` and `test_affected_assets_wiring.py` drive the renderer |
| T055 | W3 · X · devops | FR-E.11 edit in both Code Scanning snippets | Done | `docs/guides/DEVELOPER_GUIDE_TACHI.md` |

### Phase 1.6: User Story 3, one controls schema, every recommendation joined (W2 and W3)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T056 | W3 · R2t · senior-backend-engineer | R-34's goldens, first | Done | `tests/scripts/test_render_compensating_controls.py` |
| T057 | W2 · P · senior-backend-engineer | `parse_compensating_controls_md` reads both formats | Done | `scripts/tachi_parsers.py` |
| T143 | W2 · P · senior-backend-engineer | Reader for §7's persisted controls inputs | Done | `scripts/tachi_parsers.py` |
| T058 | W2 · P · senior-backend-engineer | Lane P's data-layer oracle: 0 of 168 files differ | Done | `parser-oracle-pr1.md` |
| T059 | W3 · R2 · senior-backend-engineer | §2 and §4 rendered under R-34 | Done | `scripts/render-compensating-controls.py` |
| T060 | W3 · D · senior-backend-engineer | Controls template to 1.1 | Done | `templates/tachi/output-schemas/compensating-controls.md` and `.sarif` |

### Phase 1.7: Validation (W2 exit to W5)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T061 | W2 · ADR · architect | P0 checkpoint (M3): APPROVED_WITH_CONCERNS | Done | `w3-p0-fixes.md`; see section 3 below |
| T062 | W2 · G · orchestrator | TW-ESC at M3: does not fire | Done | `tw-esc.md` |
| T063 | W2 · PM · product-manager | Option A or B, conditional | Done, not fired | `tw-esc.md` |
| T064 | W3 · SEC · security-analyst | Advisory review of part validation and path handling | Done | `security-advisory-pr1.md` |
| T065 | W4 · E2E · tester | Offline end-to-end run on the fixture | Done | `offline-e2e-pr1.md` |
| T066 | W4 · OR · tester | Small-run oracle (NFR-1) | Done | `oracle-pr1.md` |
| T067 | W4 · REV · code-reviewer | Review of PR 1's diff, run as two reviews | Done | `t146-fixes-pr1.md` maps each finding to its commit |
| T068 | W4 · SEC · security-analyst | Step 7 security scan | Done | `security-scan.md` |
| T146 | W4 · FX · senior-backend-engineer | Fix lane for T064 to T068's findings, conditional | Done | `t146-fixes-pr1.md` |
| T069 | W4 · X · devops | W4's push, CI against T001's totals, coverage figures | Done | `ci-pr1.md` |
| T070 | W4 · ADR · architect | P1 checkpoint (M4): APPROVED_WITH_CONCERNS | Done | `followups-pr1.md` (d); see section 3 below |
| T071 | W4 · CI · debugger | TW-CI root-cause analysis, conditional | **Open**, by design: TW-CI never fired, and it stays armed for PR 2 | none, because no `ci-rca.md` is owed |
| T072 | W5 · X · devops | W5's scratch adopters; the runbook's "Last validated" header | Done | `w5-setup-pr1.md`; `docs/guides/ISOLATED_OPERATION_TACHI.md` |
| T073 | W5 · L1 · tester | `/tachi.risk-score` live at default and max effort | Done | `live-risk-score-{default,max}.md` (attempt 1) and `-a2.md` (attempt 2) |
| T074 | W5 · L2 · tester | `/tachi.compensating-controls` live at both efforts | Done | `live-compensating-controls-{default,max}.md` and `-a2.md` |
| T075 | W5 · L1 · tester | SC-8's post-fix runs | Done | `sc8.md` |
| T076 | W5 · L2 · tester | R-27's smoke run under the session profile | Done | `r27-smoke-pr1.md` |
| T147 | W5 · FX · senior-backend-engineer | TW-L2's fix-and-rerun for attempt 1's text defects, conditional | Done | `t147-fixes-pr1.md` (`1e3614a`) |
| T077 | W5 · G · orchestrator | W5 gate (M5a): passes with one return | Done | `w5-gate-pr1.md` |
| T078 | W5 · PM · product-manager | The PM's ruling on that return: option A | Done | `w5-gate-pr1.md` §5a |

### Phase 1.8: Close-out (W6)

| Task | Wave, lane, agent | What | Status | Evidence |
|---|---|---|---|---|
| T079 | W6 · CO · product-manager | Binding release notes; then PRD §8's bookkeeping | Done: the notes are written, and the bookkeeping (close #357, update #408 and #409, tick N14, N15 and N16 on #397 with the N17(a) note, keep "Refs #374") ran after the release published | `release-notes.md`; #357, #408, #409 and #397 |
| T080 | W6 · CO · architect | KB Entry 27, the CI guide's f374 jobs, and the follow-ups | Done: 35 issues, #427 to #461 | `docs/INSTITUTIONAL_KNOWLEDGE.md`; `docs/devops/CI_CD_GUIDE.md`; `followups-pr1.md` |
| T081 | W6 · CO · devops | Init baseline regenerated in T080's commit | Done: the two named targets, and the system-design README's baseline copy again after T080's `score_source` edit | `tests/fixtures/init-baseline-tree/docs/INSTITUTIONAL_KNOWLEDGE.md`, `.../devops/CI_CD_GUIDE.md` and `.../architecture/01_system_design/README.md` |
| T082 | W6 · CO · devops | Deliver PR 1 (M6a) | Done, all six steps: the ledger is in the PR body, the title is `fix(374): ...`, the branch was current, `gh pr ready` and the squash-merge ran, release PR #462 opened and merged as `cb06251`, and v4.48.5 published with PR 1's notes (step 6, checked with `gh release view`) | PR #423; PR #462; release v4.48.5 |
| T083 | W6 · CO · orchestrator | This report, then the `[POST-MERGE]` tail as one issue (KB 7) | Done: this file is the report. The example audit leads are posted on #364 ([comment](https://github.com/davidmatousek/tachi/issues/364#issuecomment-7149052692)), and the tail issue is open as #463, with its first item ticked and linked to that comment | this file; #364; #463 |

Check on the named outputs: 171 repo paths named in PR 1's task lines were checked against `main` (outputs under a gitignored path are left out), and all exist except three that are absent by design: the retired generator (T054), the conditional `ci-rca.md` (T071), and this report before it was written.

Tasks by agent (PR 1's 91): senior-backend-engineer 50, devops 11, tester 11, architect 5, orchestrator 5, product-manager 4, debugger 2, security-analyst 2, code-reviewer 1. Planned effort by task estimates: 23.52 eng-days, of which 22.57 are the base and 0.95 the six conditional tasks (T144, T063, T071, T146, T147, T078).

## 2. No `.aod/` changes

```
git diff --name-only b040fa1 d03ee9a -- .aod/
```

The result is empty: no output, 0 paths.

The whole diff is 432 files, +206,946 and -2,219 lines: 348 `.md`, 41 `.py`, 24 `.json`, 12 `.sarif`, 2 `.yml`, 2 `.jsonl`, and one each of `.yaml`, `.ini` and `.txt`.
- None is under `.aod/`, `examples/`, `brands/` or `stacks/`.
- None is a PDF, a PNG or a baseline file (H2).
- None is a UI file, so Step 6 (the Design Quality Gate) was skipped.
- The shipped scripts: 6 added (`render-compensating-controls.py`, `render-risk-scores.py`, `tachi-stage.py`, `tachi_parts.py`, `tachi_scoring.py`, `tachi_scoring_rules.py`), 4 changed (`extract-infographic-data.py`, `extract-report-data.py`, `sarif_common.py`, `tachi_parsers.py`) and 1 retired (`generate-risk-scores-sarif.py`).

## 3. Blockers resolved

### Trip-wires

| Trip-wire | Outcome | Evidence |
|---|---|---|
| TW-0 (PR 1's bound) | Fired at `/aod.tasks` (the central was 10.05, above 9.0) and was re-based once, to T0 + 11.0, by the PM's pre-armed Option A. It didn't fire again: delivery is at T0 + 2.74 (section 8) | `tasks.md`, "Estimate and trip-wires" |
| TW-ESC (T062) | Does not fire at M3. The re-projected central was T0 + 6.45 (floor 4.95, ceiling 10.05) against T0 + 11.0, and the highest lane ran at 1.1x its budget (the ADR lane, kept as a watch item). T063 didn't run | `tw-esc.md` |
| TW-K4 (G0) | Ruled (c), record and proceed. T144 didn't run | `w0-gate.md` |
| TW-CI (T071) | Never fired (see "Waves, pushes and CI"). T071 stays armed for PR 2 | `ci-pr1.md` |
| TW-N3 | Armed through PR 1 at each gate (G0, G1, T062), and never triggered: no PR 1 lane edited what it protects. It stays armed for PR 2 | `w0-gate.md`, `g1-cutline.md`, `tw-esc.md` |
| TW-L2, the PM's fallback return and the SC-8 overage (T077) | Every live cell has a final attempt that earns its claims (two cells after T078's ruling). The highest narrative-fallback rate was 1.3% (1 of 80 controls fields, in one run), so no follow-up is owed on rate (above 10%) and nothing returned to the PM on rate (above 25%). SC-8 had no overage | `w5-gate-pr1.md` sections 1 to 3 |

### Gates and checkpoints

| Gate or checkpoint | Outcome | Evidence |
|---|---|---|
| G0 (T004) | PASS: the pre-state is frozen, TW-K4 is ruled, the sizes and SC-8's example are named, and #400 carries P-2's conflict list | `w0-gate.md` |
| G1 (T026), the cut line | PASS at `03a8f0d`: ADR-050 accepted, shared references and contract text committed, core unit tests green, fixture sizing green, CI 12 of 12 against T001's totals | `g1-cutline.md` |
| P0 (T061, M3) | APPROVED_WITH_CONCERNS: 1 HIGH, 5 MEDIUM, 6 LOW. P0-1 to P0-10 landed in W3, through the fix lane FX0. P0-11 went partly to W3 (the controls command names its five helpers) and partly to #453. P0-12's `module-signatures.md` half landed in W3, and `fail`'s `counts.open` is in #450 | `w3-p0-fixes.md`; `followups-pr1.md` (e) |
| P1 (T070, M4) | APPROVED_WITH_CONCERNS, 8 items. Each landed in W6's P1 batch or was filed by T080: the tables below cite both | `followups-pr1.md` (d) |
| M5a (T077) with T078 | PASSES with one return. The PM's T078 ruling (option A, §5a) classes the scorer's skipped reference reads at default effort (R1) and the controls agents' reads outside their list at max (R2) as agents off their contract, and withdraws no claim, because no signed criterion measures read scope. Follow-ups: #433 (R1) and #434 (R2). The notes carry one known-limitation line, on R1 | `w5-gate-pr1.md` sections 4, 5 and 5a |
| G-1 (the W5 gate's build clause) | The gate says that a W6 edit to an agent, command, reference, template or script reopens the live cells it reaches. The PM's §5b ruling closes G-1 for W6's edits: the text edits only define `score_source`, which the renderer computes and no agent writes, the script edits stop short of every live input, and the offline re-run and the oracle show the scripts' output unchanged. No live cell stays reopened, and the claims stand. §5b sits on a lane commit that isn't part of the merge: the gate record at `d03ee9a` ends at §5a (section 9) | the PR body, "What ran on which commit" |
| P2 (W6) | APPROVED_WITH_CONCERNS, final, 6 items. P2-1, P2-3 and P2-5 were fixed in W6, P2-2 is #460, P2-6 is #461, and P2-4 is informational (the P2 table below) | `followups-pr1.md` (l) |

**P1's items.** All eight landed in PR 1:

| Item | Landed in W6, or earlier where stated | Filed by T080 |
|---|---|---|
| P1-1 (MEDIUM): re-run T065's offline driver on the install commit | `offline-e2e-pr1.md` section 12 (W5, on `27d58bd`) and section 13 (the merge candidate `ad64a72`): PASS on Python 3.11, 3.9 and 3.14 | none owed |
| P1-2: SA-4, file modes through the renderers' `os.replace` and `fail`'s restore | `843ea01`: `atomic_write` gains `mode_of`; `contracts/module-signatures.md` | none |
| P1-3: GFM's escaped pipe in a Section 7 cell | `843ea01`, after the PM's W6 ruling Q1 moved it into PR 1; ADR-050 D3 | none: its writer half stays PR 2's |
| P1-4: the effort-estimate check and D2's standing rule | `843ea01` (the check reads the validated body) and `501b258` (D2's and D4's from-disk rule) | none |
| P1-5: `score-source`'s wording | `843ea01` (template, reference and the summary line), with the scoring skill's lines following in `20ed9eb` | none |
| P1-6: the spec erratum on R-H (D2's held condition) | The PM's erratum `f3a89bc`. The oracle derives the accepted set (81), equal to the harness's claims (`oracle-pr1.md` W6-4) | none |
| P1-7 (INFO): D3's copy, two nits (ruling 4's quote and naming classes 1 to 3) | `501b258` (ADR-050 D3, and the same word in plan.md's Verification 7); the commit message and the ADR's W6 history row cite P1-7 | none |
| P1-8: a test docstring quoting D2's old rule | `843ea01` | none |

The items the checkpoint passed on are in this table:

| Passed on by the checkpoint | Landed in W6 | Filed by T080 |
|---|---|---|
| SA-1's residual: a malformed persisted controls item | ADR-050's Known-limitations line (`501b258`) | #445 |
| SA-3's remainder: forbidden characters in values that reach no batch unit | `t146-fixes-pr1.md`'s SA-1 and SA-3 row corrected (`843ea01`) | #444 |
| The `https%3A//` edge | ADR-050 D7's note (`501b258`) | #450, the optional hardening |
| The read-back widening, with T067a's L8 and the legacy-prose question | P1-4's standing rule covers each copied value | #446 |
| The ADR text edits: D2, D3's quote and classes 1 to 3, D4, D7, and P1-3's D3 text | `501b258`, `d4462d3` and `bbe5d87` | none |

**P2's items.**

| Item | Disposition |
|---|---|
| P2-1 (LOW): the escaped-pipe rule is stricter than GitHub's, but its words call it GitHub's | Fixed in W6 (`20ed9eb`): the docstrings, `module-signatures.md`'s phrase and a test docstring |
| P2-2 (LOW): a Section 7 pipe can reach the controls agent's `matrix_row`, which can't hold one | Filed: #460, for PR 2 or the first patch |
| P2-3: `contracts/part-files.md`'s `atomic_write` mode line, and the `score_source` lines in the scoring skill and the system-design README | Fixed in W6 (`20ed9eb`; the README's lines in T080's commit) |
| P2-4 (INFO): the layer chain's Section 7 step | Informational: ruled right, no action |
| P2-5 (INFO): ADR-050's W6 revision entry didn't name W6's contract additions | Fixed in W6 (`afcaf0a`) |
| P2-6 (INFO, pre-existing): an unreadable output makes `plan` end in a traceback | Filed: #461 |

### Reviews, scans and the economy gate

| Item | Outcome | Evidence |
|---|---|---|
| T064 advisory (W3) | 0 CRITICAL, 0 HIGH, 2 MEDIUM, 11 LOW, 5 INFO. The two MEDIUM findings are fixed: SA-2 at W3 and SA-1 in T146 (its residual is #445). The other findings are fixed in T146 or filed | `security-advisory-pr1.md`; `t146-fixes-pr1.md`; `followups-pr1.md` (i) |
| T067's two reviews (W4) | The 2 HIGH findings (H1, H2) are fixed in T146, with the MEDIUM findings. The LOW and INFO findings are folded into follow-ups | `t146-fixes-pr1.md`; `followups-pr1.md` (i) |
| Step 7, T068's scan | PASSED on the W3 tip `f43440b`: 0 CRITICAL, 0 HIGH, 2 MEDIUM (S7-1, S7-2), 1 LOW (S7-3), 1 INFO (S7-4). All four are fixed in T146 (`a6c5687`, `cbba1e5`, `e51c1df`, `c129e78`). Its observations O-1, O-3 and O-4 are in #443 and #454. O-2 (CI dependency pins) and O-5 (an earlier scan-log entry that doesn't verify) are pre-existing and aren't filed. Code changed after the scan (T146's fixes, T147's four text files and a test, W6's batch and its docstring commit) was reviewed at P1 and P2 and not re-scanned | `security-scan.md`; `t146-fixes-pr1.md` |
| Step 8, the economy gate | Advisory: 13 findings (EC-1 to EC-13), none blocking. EC-2, the one that corrected behavior, was fixed before merge (`843ea01`). EC-1, 3, 4, 6 and 11 to 13 are in #443, one change at PR 2's start. EC-5 and 7 to 10 are in #447, post-merge and item by item | `economy-check.md`; `followups-pr1.md` (j) |
| Step 6, the Design Quality Gate | Skipped: no UI file changed (section 2) | section 2 |

## 4. Verification on the merge candidate

The merge candidate is `ad64a72`. After it, the branch gained records, the release notes, the follow-ups, docs (KB Entry 27, the CI guide's f374 jobs, the system-design README's `score_source` lines, ADR-050's W6 entry; the init baseline regenerated) and one text commit, `20ed9eb`. That commit rewords docstrings and comments in `scripts/tachi_parsers.py` and `tests/scripts/test_tachi_parsers.py`, two contract notes and the scoring skill's `score_source` lines. For this report, both Python files were parsed at `ad64a72` and at the PR head `8111c5e`, and their syntax trees are equal once docstrings are set aside. Nothing was imported or run.

| Check | Result | Ran on | Record |
|---|---|---|---|
| The oracle (plan.md Verification 7), five shipped examples | **CLEAN.** Run A: 3,834 diffs, 0 unattributed. Run B: 1,930 value diffs, 0 returned to the PM, 0 aggregated entries. No value moved since the W4 re-run: 28 of 28 rendered files are byte-identical, and so is every attribution record. P1-6's accepted set is 81, equal to the harness's claims. The taxa pin passes (709) and S-12 (a) to (d) hold | `ad64a72` | `oracle-pr1.md`, W6-1 to W6-7 |
| P1-1's second run: T065's offline driver | **PASS.** 2,592 checks per interpreter, 0 failed, on Python 3.11, 3.9 (the floor) and 3.14. 15 of 15 deliberate defects are caught and the 3 clean controls pass. The 63 stage runs write byte-identical files on all three | `ad64a72` (section 12 ran on `27d58bd`) | `offline-e2e-pr1.md` section 13 |
| W6's census, `tests/scripts` and `tests/schemas`, Python 3.11 | 7,656 passed, 34 failed, 25 skipped. **0 regressions, 0 new failures.** The 34 are T001's out-of-gate set. +57 passes over W5 are the tests of W6's P1 batch. Lane runs: the f374 list 5,999 passed and 20 skipped (D16 coverage 96.37%, the `tachi_parsers.py` ratchet 83.6% against its 44.9% floor); the `tachi-pytest.yml` gated set 899 passed and 1 skipped | `ad64a72` | `wave-06/results.json` |
| CI on the PR head | **14 of 14** checks pass (7 workflow runs): both pytest legs, `f374-offline`, `f374-py39-floor`, `f374-macos`, install-fidelity's three jobs, permissions-verify, maestro-coverage, mmdc-preflight, catalog-drift and both gitleaks scans | `8111c5e` | `gh pr checks 423` |
| Live matrix and R-27 (W5) | **PASS.** See "What PR 1 claims" below | `27d58bd` (attempt 1); `1e3614a` (attempt 2, SC-8, R-27) | `w5-gate-pr1.md` |
| The merge itself | #423 merged at 22:48 UTC on 2026-11-24 with `d03ee9a`. Its parent is `b040fa1`, so the squash applied directly on the pre-state. PR 2 (#425) stayed open on base `main` | | `gh pr view 423` |
| The release | v4.48.5 is published (00:44 UTC on 2026-11-25, which is 19:44 -05:00 on 2026-11-24). Release PR #462 merged as `cb06251`, the tag's commit, and its diff bumps `scripts/tachi_parts.py`'s `VERSION` marker with the other release files. The release body carries PR 1's section of `release-notes.md` | `cb06251` | `gh release view v4.48.5`; `gh pr view 462` |

- **`push:[main]` CI on `d03ee9a`:** 5 of 5 green: tachi pytest (run 45504393186), tachi permissions-verify (45504392784), release-please (45504392998), tachi catalog-drift (45504392811) and tachi install fidelity (45504392689).

### What PR 1 claims (from the W5 gate, §5 and §5a)

- **Claimed:**
  - US-1a #1, #2, #3 and #7; and #6 in every cell, stated only as its listed items and never as "on-contract execution";
  - US-3 #5, SC-5 on a live run and R-27;
  - SC-8's "cheaper", for both stages and only on the small example at the default (medium) effort: output tokens are 64.9% (scorer) and 71.0% (controls) below the v4.48.4 baselines, one batch each.
- **Offline, PASS:** SC-4, SC-5's offline half, SC-6 (Track R), and US-1a #4 and #5.
- **Not claimed:**
  - that agents read their references or keep to their read list, at any effort;
  - tachi's overflow path at max, live;
  - score parity with v4.48.4;
  - the threat-model stage's on-contract execution.

## 5. Definition of Done

| Bar (tasks.md) | Evidence | Status |
|---|---|---|
| 1. Pushed to Production: the PR squash-merged to `main`, and its `fix(374)` patch release published. PR 1 refers to #374 | Merged as `d03ee9a`; the PR body says "Refs #374" and #374 stays open. The release v4.48.5 is published: release PR #462 merged as `cb06251`, bumping `scripts/tachi_parts.py`'s `VERSION` marker through T022's `extra-files` entry, and the release carries PR 1's notes | **Met** |
| 2. Tested: every f374 job and every existing gate green on the PR and on `push:[main]`, against the PR's literal pre-state, with the offline end-to-end run and the oracle recorded. Unit coverage at least 80% on the gated modules, and `tachi_parsers.py` at or above its ratchet floor | On the PR: 14 of 14 on `8111c5e`, and every earlier push green, each compared with T001's totals (`g1-cutline.md`, `ci-pr1.md`). The offline run and the oracle are recorded (section 4). D16's gate: 96.37% against 80% (W6's lane run; CI's `f374-offline` passes on `8111c5e`). `tachi_parsers.py`: 83.6% against 44.9% | **Met**, on the PR and on `push:[main]` (5 of 5 green on `d03ee9a`, section 4) |
| 3. User Validated: the live matrix recorded with its dispositions decided in advance (W5), and R-27's smoke run recorded. SC-9 is tracked outside this feature | The dispositions (a) to (c) are in `w5-setup-pr1.md`. The eight live records, `sc8.md` and `r27-smoke-pr1.md` (PASS at the first attempt) are recorded, and `w5-gate-pr1.md` rules on them | **Met** |

## 6. Departures from the plan

1. **One W6 push instead of two.** The handoff planned P1's batch (with the merge-candidate oracle and P1-1's second run) as S3's first push, and the close-out as a second. W6 pushed once, `8111c5e`, after both. It is the only head SHA after `1e3614a`, and the census, the oracle and the offline run all ran on the committed merge candidate (H6).
2. **The Step 8 economy gate ran on PR 1 at W6.** tasks.md maps no such gate to PR 1. The run is advisory, with 13 findings, and EC-2 was taken before merge (section 3).
3. **A P2 checkpoint ran.** tasks.md has P0 and P1 for PR 1. The architect also reviewed W6's final batch, as P2: APPROVED_WITH_CONCERNS, 6 items, none blocking.
4. **The PM moved P1-3's fix into PR 1** (W6 ruling Q1). The checkpoint had planned it for T080 unless the PM moved it. The reader half is PR 1's, and the writer half stays PR 2's.
5. **EC-2 was added to PR 1.** It is the one economy-gate finding that corrected behavior: both renderers and the planner now use one snapshot key for the undeclared-paths check.
6. **The squash commit's co-author trailer names Claude Sonnet 5.5**, the delivering agent. The branch's earlier commits and recent `main` commits name Opus 5.5.

Also recorded earlier:
- The P0 fixes ran as a fix lane (FX0) inside W3, not as a serial wave before it, and T067's review ran as two reviews, as the team-lead's session plan asked (`tw-esc.md`).
- Session 1 added work beyond the plan: a calibration Write with D6 re-amended per stage, about 25 architect rulings, the PM's erratum that makes "foreground" a completion rule, a plan-schema bundle in W2 and a fixture fixed-point fix (`tw-esc.md`).
- Incidents: six lanes overflowed their context in session 1, so later waves ran one task per agent instance (`tw-esc.md`). Session 2's orchestrator ran out of context during W4's close-out, and a fresh session finished W4 from the orchestrator's status log with nothing lost (session 2's handoff).
- **Incident in W6: the project board's Status values were cleared, then restored.** Two `create-issue.sh` runs from fresh lane worktrees, at T080's filing and again at T083's, found no board cache. Each re-ran the board setup, which rewrote the Status field's options, and that cleared the Status of every board item. All 181 items were restored from each item's own event history, with only empty values set. The restored values agree with the issues' `stage:` labels for 179 of 181; the other two were in Build, which has no label. The checkouts that run AOD's board commands now hold a board cache checked against the live field, so the setup can't run again from them. The defect is filed as #464.

## 7. Follow-ups

35 issues, #427 to #461, all open and all `stage:discover`: 23 enhancements and 12 defects. T080 filed 33, and the P2 checkpoint added two (#460, #461). `followups-pr1.md` lists each with its source and records where every deferred item went. Two more issues opened at close-out: #463, the `[POST-MERGE]` tail, and #464, the board-setup defect found during the filing.

| Group | Issues |
|---|---|
| The task line and the spec ask for them | #427 (R-17, the adapter's superseded copies); #428, #429 and #430 (S-16's three); #432 (controls §2 and §4 rendered from the part) |
| From W5's live matrix and the PM's rulings | #431, #433, #434, #435, #436, #439, #440, #441, #442, #459 |
| Deferred from the reviews, the scan, the economy gate, the checkpoints and W3's rulings | #443 to #455 and #458 |
| Output-contract alignments and ideas | #437, #438, #456, #457 |
| From the P2 checkpoint | #460, #461 |

Recorded as not filed, by decision: SV-1's issue (TW-K4 ruled (c)); P1-3 (moved into PR 1); the early-`reconcile` warning (accepted as is); and P-11 (adopted in PR 2's D12).

## 8. For the team-lead

### Delivery against TW-0

PR 1 merged at **T0 + 2.74**, where T0 is 2026-11-22. TW-0 for PR 1 is T0 + 11.0, so delivery came 8.26 days inside it. The planned central for M6a was T0 + 10.05, and TW-ESC's re-projection at M3 put the central at T0 + 6.45. The release published about two hours after the merge, at T0 + 2.82 (19:44 on 2026-11-24).

| Milestone | Planned (central) | Actual | When (-05:00) |
|---|---|---|---|
| M1, tasks.md v1.4 signed | T0 + 1.0 | T0 + 0.80 | 2026-11-22 19:05 |
| M2, G1, the cut line | T0 + 2.95 | T0 + 0.96 | 2026-11-22 23:01 |
| M3, T062 | T0 + 5.35 | T0 + 1.13 | 2026-11-23 03:09 |
| M4, T070 | T0 + 7.9 | T0 + 2.40 | 2026-11-24 09:40 |
| M5a, T077 and T078 | T0 + 9.15 | T0 + 2.59 | 2026-11-24 14:16 |
| M6a, the squash-merge | T0 + 10.05 | T0 + 2.74 | 2026-11-24 17:48 |

How to read it. The figures use `tw-esc.md`'s convention: elapsed days from T0 (2026-11-22, 00:00 local) to a commit's timestamp. That reading gives M3 as T0 + 1.13, which `tw-esc.md` states as 1.15 with T062's own tail. Elapsed time includes idle gaps, so each figure is an upper bound on worked eng-days. Read the strictest way, with every elapsed hour since T0 counted as a worked hour at 8 per eng-day, delivery is about 8.2 eng-days (65.8 hours), still inside T0 + 11.0. From M1 to M6a, delivery took 1.94 elapsed days against 9.05 planned (a ratio of 0.21). At M3, `tw-esc.md`'s own ratio, on worked hours at 8 per eng-day, was 0.20.

### Metrics

- **Sessions and waves:** four build sessions ran seven waves: S1 (W0 to W2), S2 (W3 and W4, with PR 2's W1′), L (W5) and S3 (W6). W1 to W6 each pushed once, and each push was green.
- **Tasks:** 87 of 91 checked at `d03ee9a`, and T079, T082 and T083 done since. The six conditional tasks: T144 and T063 not fired, T071 not fired and still open, T146, T147 and T078 ran.
- **Agents:** the counts are in section 1. The `tachi-*` agents were test subjects only.
- **Follow-ups:** 35, all open (section 7).

### PR 2

PR 2 (#425, draft, base `main`) had 7 of 59 tasks done at S3's start, and its bound stays T0 + 15.0. This report doesn't re-project it: T122 does that at W3′'s end. PR 2's branch rebases onto `main` once, after PR 1's squash, with a full-tree diff (KB 18).

### Sign-off

G5 asks the team-lead to sign off PR 1's delivery. The sign-off doesn't cover the items in section 9.

**STATUS: APPROVED_WITH_CONCERNS.** Team-lead, 2026-11-24.

1. **Checked with `git` and `gh`.** The 91 rows match tasks.md and agent-assignments.md, and GitHub confirms T079, T082 and T083. `.aod/` has 0 paths, #423's ten CI heads are green, `push:[main]` is green on `d03ee9a` (5 of 5) and on the release commit `cb06251` (4 of 4), and no board item has a blank Status.
2. **TW-0 is read right:** T0 + 2.74 at the merge and T0 + 2.82 at the release, 8.26 d inside T0 + 11.0, and inside it too on the strict 8-hour reading (8.2 eng-days). Rounding nit only: M1 to M6a is 1.95 d unrounded.
3. **Add TW-N3 to section 3's trip-wires:** armed through PR 1 and never triggered, because N3's fix hadn't merged and PR 1 squashed directly onto `b040fa1`. It stays armed for PR 2 (T089, T122), like T071.
4. **Close the bookkeeping in one push:** tick T079, T082 and T083 in tasks.md (90 of 91), and push this report with §5b and ADR-050's status edit, H11 first. Those two are separate commits today, so either fold them into one or make section 9's "the post-merge docs commit" plural. Then tick #463's ADR item.
5. **File the board incident before PR 2's W6′.** It is fairly recorded, but no follow-up exists: AOD's board setup rewrites the Status field from any checkout without a board cache, and W6′ (T136, T139) files issues again. Until it's fixed, file only from a checkout whose cache is checked.

## 9. What stays open

1. **The release.** Done: v4.48.5 is published, and the release carries PR 1's notes (T082 step 6).
2. **PRD §8's bookkeeping (T079).** Done after the release: #357 is closed, #408 and #409 carry their updates, and #397 has N14, N15 and N16 ticked with the N17(a) note. #374 stays open ("Refs #374").
3. **The `[POST-MERGE]` tail (T083).** Opened as #463 (KB 7), with the example audit leads posted on #364 ([comment](https://github.com/davidmatousek/tachi/issues/364#issuecomment-7149052692)) and its first item ticked and linked to that comment. Its other four items stay unticked in #463: R-17's follow-up (#427) and S-16's follow-ups (#428, #429, #430), which the issue lists as links; the optional Code Scanning scratch-repository check (quickstart §5); and ADR-050's accepted-commit SHA. That item is done in the post-merge docs PR that carries this report: the ADR's Status line now names `d03ee9a`, and a history row records the merge and v4.48.5.
4. **`push:[main]` CI on `d03ee9a`.** Done: 5 of 5 green (section 4).
5. **§5b of the W5 gate record.** The PM's ruling that closes G-1 lands with this report, in the post-merge docs PR.
6. **T071.** It stays open and armed. It runs only if TW-CI fires at a push of PR 2, before that PR's next push.

## Hygiene

- H1: this lane ran no pytest, extractor or renderer. It ran `git` and `gh` reads, the two posts noted below, and one parse (never an import or a run) of two Python files at two commits.
- H8: this record names no local or absolute user path, real-world target name or finding content. It cites issues, pull requests, commits and two GitHub links. The fixtures and examples it mentions are tachi's synthetic ones.
- Written by lane CO without a commit. After the release published, the lane posted the #364 comment and opened #463.
