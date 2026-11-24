# T069: CI on PR 1's tip (W4)

**Date:** 2026-11-24. **Commit pushed:** `27d58bd`, W4's tip, pushed once to draft #423 at 13:41Z (TW-CI). **Pre-state:** T001's [prestate.md](prestate.md), at `1c55360` (code-identical to v4.48.4). **Earlier pushes of this PR:** W1 `03a8f0d` (T022, gate G1), W2 `5d218af` (T047) and W3 `f43440b` (T039).

## Result: PASS

- **Every check passed: 14 of 14.** That is 13 jobs in seven workflow runs, plus GitHub's code-scanning `gitleaks` check on the same commit. Both pytest legs are green, and so are the three f374 jobs and the co-fired gates.
- **No regression against T001.** No node ID that passed at T001 fails, no gate total drops and no skip is new. Three T001 node IDs no longer exist, by design: one test was retired with the generator it pinned, and two were renamed to pin the renderer that replaced it (T054).
- **TW-CI does not fire.** W3's push `f43440b` was green, and so is this one, `27d58bd`.
- **ADR-050 D16:** 96.35% line coverage over PR 1's seven gated scripts, against the 80% bar. No shortfall, so nothing goes back to T146.
- **`tachi_parsers.py`:** 83.4% against T001's floor of 44.9%. No missed line lies in the bundle's new parser functions (E3).
- This record is committed with the branch's next push, never alone (H6).

## CI on `27d58bd`, against T001's totals

Totals are passed / failed / skipped. "Run / job" are GitHub Actions IDs.

| Job | Run / job | T001 | `27d58bd` | The difference |
|---|---|---|---|---|
| `tachi-pytest.yml`, ubuntu leg | 45405985117 / 138486728796 | 670 / 0 / 5 | 895 / 0 / 5 | +225: `test_cvss_category_defaults.py` +226 (T014), `test_owasp_2026_contract.py` -1 (T054) |
| `tachi-pytest.yml`, macOS leg | 45405985117 / 138486728411 | 674 / 0 / 1 | 899 / 0 / 1 | +225, for the same two reasons |
| install-fidelity: extraction-fidelity | 45405985062 / 138486729181 | 249 / 0 / 6 | 923 / 0 / 6 | +674, all in `test_tachi_parsers.py` (48 to 722) |
| install-fidelity: report-posture | 45405985062 / 138486728741 | 84 / 0 / 0 | 107 / 0 / 0 | +23, all in `test_write_confinement.py` (78 to 101) |
| install-fidelity: manifest-completeness | 45405985062 / 138486729267 | 15 / 0 / 2 | 15 / 0 / 2 | unchanged |
| `f374-offline` (3.11): the coverage gate | 45405985062 / 138486729183 | new | 5,937 / 0 / 23 | 96.35% against 80% |
| `f374-offline`: the ratchet step | same job | new | 722 / 0 / 0 | `tachi_parsers.py` at 83.4% against 44.9% |
| `f374-py39-floor` (3.9) | 45405985062 / 138486729250 | new | 5,907 / 0 / 23 | the same list, without `test_sarif_common_affected_assets.py` (30 cases) |
| `f374-macos` | 45405985062 / 138486729063 | new | 709 / 0 / 0 | `test_sarif_identity.py`: 706 cases, plus the 3 that need a case-insensitive volume |
| permissions-verify | 45405985083 / 138486728018 | C1 to C8 pass | C1 to C8 pass | C7 counts 25 paths, T001's 21 |
| maestro-coverage | 45405985096 / 138486730473 | 11 / 0 / 2 | 11 / 0 / 2 | unchanged |
| mmdc-preflight | 45405985415 / 138486729207 | pass | pass | exit 1, all three tokens present |
| catalog-drift | 45405985079 / 138486728341 | 16 / 0 / 0 | 16 / 0 / 0 | unchanged |
| gitleaks: the full-repo scan, and GitHub's `gitleaks` check | 45405985123 / 138486731877; check 138486923028 | pass (G1) | pass | 772 commits scanned, no leaks |

- **All seven workflows fired.** At W1's push, catalog-drift and mmdc-preflight did not.
- **The pytest legs run T001's 23 modules.** Their run list is unchanged, and only the `paths:` list grew.
- **No red to attribute to #365.** Nothing is red. Its six reds are in `test_backward_compatibility.py`, which no workflow runs (catalog-drift's header says it is "wired into no CI"), so they can't appear on CI.
- **Every job listed above passed all its steps,** including `f374-offline`'s two (the gate, then the ratchet) and permissions-verify's six.
- **Wall time.** The macOS leg's tests took 40 m 31 s, against T001's 32 m 32 s (36 m 07 s at W1, 25 m 45 s at W2, 24 m 00 s at W3). The ubuntu leg took 14 m 04 s, against 11 m 04 s. The counts haven't moved since W3, so added tests don't explain the extra time. The workflow sets no job timeout, and each test has its 1,080 s cap.

## Where each total differs from T001's

### The pytest legs (+225)

| Module | T001 | `27d58bd` | Added by |
|---|---|---|---|
| `test_cvss_category_defaults.py` | 22 | 248 | +226. T014 (`70c8314`, W1) moved the calculator into the shipped `tachi_scoring`, and the file grew to cover its arithmetic and tables: rounding, bands, SLA days, composites, residual scores, elevation, and the embedded tables' agreement with the schemas. All 22 original IDs (FIRST's 16 examples among them) still pass, and 226 are new |
| `test_owasp_2026_contract.py` | 34 | 33 | -1. T054 (`26826f8`, W3) retired `generate-risk-scores-sarif.py`, and with it `test_derive_owasp_reference_tokens_match_catalog_edition`, because that generator's `owasp-reference` property is not in the 1.1 template or the contracts (the PM's W3 ruling 2). The module's other tests now drive the renderer in-process, and so does `test_affected_assets_wiring.py`, which stays at 39 |
| the other 21 modules | 619 | 619 | unchanged, with the same skips |

By push, the totals were 896 / 900 at W1 and W2, and 895 / 899 from W3.

### extraction-fidelity (+674)

All of it is `test_tachi_parsers.py`, 48 to 722. The other six modules are unchanged (60, 48 plus 6 skipped, 8, 12, 66 and 7).

| Push | Cases | The task |
|---|---|---|
| W1 | 69 (+21) | T018's parser cases |
| W2 | 443 (+374) | T033 (the shared reference decoder), T048 and T142 (`parse_correlation_groups`, the SARIF fallback reader), T032, T057 and T143 (drift forms, both controls formats, persisted inputs) |
| W3 | 616 (+173) | P0-1 and P0-4 (the `~` escape, `forbidden_character`), P0-3 (the fallback reader's own result per member), the readers that find headings outside fences, T054's two pins, and the fallback reader's severity, singular location and refused surrogates |
| W4 | 722 (+106) | T146's reference-set, section 7 and `recommendation_text` cases, the MAESTRO layer from each finding's own row, and R-F's repeated-member report |

- **46 of T001's 48 cases are unchanged,** and 226 new test functions carry the other 676 of the 722.
- **Two T001 IDs are gone because T054 renamed them.** The generator's two pins became `test_pin_render_risk_scores_*`, and each now runs in two call forms (default and keep-bold), which gives 4 of the 676 cases. The old IDs are `test_pin_generate_risk_scores_sarif_scored_threat_table_unaffected` and `test_pin_generate_risk_scores_sarif_governance_fields_unaffected`.

### report-posture (+23)

`test_write_confinement.py`, 78 to 101. `test_report_posture_contract.py` stays at 6.

| Push | Cases | The task |
|---|---|---|
| W1 | 84 (+6) | T022: the confinement group for `tachi-stage.py` |
| W2 | 94 (+10) | T047: `render-risk-scores.py`, and the populator that it loads by path |
| W3 | 101 (+7) | T039: `render-compensating-controls.py` |
| W4 | 101 | no change |

### The f374 jobs (new, so no T001 total)

Counts on `f374-offline` (passed; skips in brackets), by push. The py39 job is the same list without `test_sarif_common_affected_assets.py`.

| Module | Added by | W1 `03a8f0d` | W2 `5d218af` | W3 `f43440b` | W4 `27d58bd` |
|---|---|---|---|---|---|
| `test_tachi_parts.py` | T011 | 1,272 | 1,467 | 1,808 | 1,871 |
| `test_tachi_stage.py` | T017 | 255 | 310 | 451 | 521 |
| `test_tachi_scoring_rules.py` | T042 | n/a | 310 | 417 | 429 |
| `test_render_risk_scores.py` | T027 | n/a | 371 | 559 | 568 |
| `test_render_compensating_controls.py` | T034 | n/a | n/a | 277 | 292 |
| `test_runtime_floor_374.py` | T149 | 44 (33) | 53 (25) | 59 (20) | 59 (20) |
| `test_tachi_parsers.py` | T018 onward | 69 | 443 | 616 | 722 |
| `test_sarif_identity.py` | T015, T016 | 354 (1) | 503 (1) | 659 (3) | 706 (3) |
| `test_fixture_374.py` | T020 | 68 | 175 | 175 | 175 |
| `test_contract_text_374.py` | T010 | 236 | 273 | 307 | 316 |
| `test_cvss_category_defaults.py` | T014 | 248 | 248 | 248 | 248 |
| `test_sarif_common_affected_assets.py` | existed at T001 | 30 | 30 | 30 | 30 |
| **Total** | | 2,576 (34) | 4,183 (26) | 5,606 (23) | **5,937 (23)** |

`f374-macos` runs `test_sarif_identity.py` alone, and its 709 are the 706 above plus the 3 case-insensitive-volume cases (355, 504, 662 and 709 by push).

### permissions-verify

C1 to C6 print T001's counts (21 agents, 6 commands, 3 Bash-capable agents), and C8's five planted mutations are all detected (M1 by C2, M2 to M5 by C1). C7 counts 25 paths, T001's 21, because T039 (`ec551ed`) added four Writes tokens to section 8 and the runbook together: the two `.tachi-build/` stage directories and the two `{plan-id}/parts/` directories. C7 holds those two tables equal, and it passes.

## Skips

- **Equal to T001's, by node ID,** in every job that T001 recorded: the pytest legs (5 on ubuntu, 1 on macOS), extraction-fidelity (6), report-posture (0) and manifest-completeness (2). maestro-coverage skips the same two intermediate-format sample reports.
- **The f374 jobs' 23 skips** are 20 `test_runtime_floor_374.py` cases for four PR 2 scripts that do not exist yet (`join-threats-md.py`, `attack-chains.py`, `assemble-report.py` and `check-threat-model.py`, 5 cases each), and 3 `test_sarif_identity.py` cases that need a case-insensitive volume, which `f374-macos` runs.
- **They fell from 34 at W1.** W2 and W3 created three of the seven scripts that `PLANNED` then named, and their cases now run.

## TW-CI

**It does not fire.** It needs the same gated failure red on two consecutive pushes. This PR has had no red run on any workflow at any push.

| Push | Commit | Workflows that fired | Result |
|---|---|---|---|
| W1 | `03a8f0d` | 5 | all green |
| W2 | `5d218af` | 7 | all green |
| W3 | `f43440b` | 7 | all green |
| W4 | `27d58bd` | 7 | all green |

- T071's root-cause analysis isn't needed, and `ci-rca.md` isn't written.
- **The push wasn't records-only.** It carried 28 commits since W3's push: W4's fixes (T146 and the oracle's rulings) in seven shipped scripts, eight test modules, three command files, an agent and a skill file, and W4's records.

## ADR-050 D16: the coverage gate

`f374-offline` ran `--cov --cov-config=tests/scripts/coverage-f374.ini` over its 12 modules, in-process (H15). The job log ends the table with `Required test coverage of 80.0% reached. Total coverage: 96.35%`.

| Gated script | Statements | Missed | Cover |
|---|---|---|---|
| `render-compensating-controls.py` | 1,247 | 92 | 92.62% |
| `render-risk-scores.py` | 1,182 | 90 | 92.39% |
| `sarif_common.py` | 640 | 15 | 97.66% |
| `tachi-stage.py` | 801 | 0 | 100.00% |
| `tachi_parts.py` | 970 | 18 | 98.14% |
| `tachi_scoring.py` | 180 | 0 | 100.00% |
| `tachi_scoring_rules.py` | 864 | 0 | 100.00% |
| **Total** | **5,884** | **215** | **96.35%** |

- **Against the bar:** 80% total (`fail_under = 80`, compared after rounding to two places). The margin is 16.35 points, and the lowest script is 92.39%.
- **The gated set** is the seven scripts that D16 names for PR 1, and `coverage-f374.ini`'s `include` lists the same seven.
- **By push:** 98.17% at W1 (4 scripts, 2,184 statements), 95.39% at W2 (6 scripts, 4,210), 96.04% at W3 (7 scripts, 5,759) and 96.35% at W4 (7 scripts, 5,884).
- **The orchestrator's local run agrees.** It gave 96.35% over 6,271 passed and 20 skipped. Those counts reconcile exactly with the whole install-fidelity workflow's module list on macOS: the 5,937 above, plus the 3 case-insensitive-volume cases that run there, plus 331 for the workflow's other nine modules (207 in extraction-fidelity, 107 in report-posture, 17 in manifest-completeness).

## `tachi_parsers.py` against its floor (E3)

| | T001 (the floor) | `27d58bd` |
|---|---|---|
| Statements | 917 | 1,496 |
| Missed | 505 | 248 |
| Covered | 412 | 1,248 |
| Cover | **44.9%** | **83.4%** (83.42%) |
| Tests measured | 48 | 722 |

The ratchet step passed with `--fail-under=44.9`, a margin of 38.5 points. By push: 52.2% at W1, 81.7% at W2, 82.2% at W3 and 83.4% at W4.

**No missed line is in a new parser function.** The CI log's `--show-missing` list, for diffs at T127:

```
390, 394-396, 544, 602, 608-609, 633, 648, 661-664, 673-695, 706-727, 760-776, 785-809, 831-890, 904-909, 927,
931, 936, 944-951, 968-982, 1028, 1246-1248, 1275-1278, 1285, 1292, 1299, 2333-2335, 2349-2372, 2379-2380,
2407-2414, 2426-2475, 2584, 2660, 2698, 2743, 2928, 2941, 2946, 3021, 3052, 3058, 3060, 3065, 3138-3175,
3186-3189, 3199-3213, 3223-3226
```

The new functions were found by parsing `scripts/tachi_parsers.py` at T001's tip `1c55360` and at `27d58bd`, and comparing definitions by name and by syntax tree. The base is `1c55360`, whose parser is identical to `main` at `b040fa1`. It is not `03a8f0d~`, which already carries W1's parser changes.

| Definitions | With statements | Statements | Missed |
|---|---|---|---|
| **New** (35 functions, `ReferenceSetError` and its `__init__`) | 36 | 556 | **0** |
| Existing, changed by F-374 | 8 | 398 | 18 |
| Existing, unchanged | 45 | 465 | 230 |
| Module level | n/a | 77 | 0 |
| **Total** | | 1,496 | 248 |

- **None of the 364 line numbers in the list above** falls inside any of the 37 new definitions.
- **All 611 statements that sit on lines F-374 added or changed are covered.** That count comes from the diff of the file between `1c55360` and `27d58bd`.
- **All 248 missed statements are on lines the diff doesn't touch.** They are in 29 existing definitions: 23 that F-374 left unchanged (230 statements: the frontmatter, project-name, artifact-detection, severity-accumulation, scope-data, component-asset-map and source-attribution readers, among others) and 6 that it changed (18 statements, each a single line in a legacy branch, such as a `break`, a `continue` or an early `return`).
- **The new definitions are** `decode_references`, the reference-set readers, `parse_finding_layers`, `parse_correlation_groups`, the SARIF fallback reader, `parse_controls_assessment_inputs` and `recommendation_text`, with their helpers.

## The scratch-clone check

The same measurement ran in a helper-made scratch clone at `27d58bd` (`t069-1`, Python 3.11, H1): `--cov=scripts --cov-report=term-missing tests/scripts/test_tachi_parsers.py`. It gave 722 passed in 7.14 s, 1,496 statements and 248 missed, and its `Missing` list equals CI's character for character. Exact per-line data for the table above came from `coverage json` on that clone's data file. Nothing ran in a tracked tree, and the lane worktree stayed clean (nothing under `examples/`, H2).

## For later gates

- **T127 and PR 2:** compare the missing-lines list above. The 20 `test_runtime_floor_374.py` skips should turn into passes as PR 2's four scripts land, each wave moving its script from `PLANNED` to `REQUIRED_NOW`.
- **The floor stays 44.9** (D16: never lowered within the bundle).
