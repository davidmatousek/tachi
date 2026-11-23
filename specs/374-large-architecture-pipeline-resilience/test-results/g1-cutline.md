# Gate G1: the cut line (T026, M2)

**Date:** 2026-11-23. **Commit gated:** `03a8f0d`, W1's single push to draft #423 (TW-CI). **Pre-state:** T001's [prestate.md](prestate.md), at `1c55360` (code-identical to v4.48.4).

## Result: PASS, and the cut line is `03a8f0d`

PR 2 may branch from it (T084), and the story phases begin. This record and the W1 test record follow in a records-only commit, which goes up with W2's push and never alone (H6).

| plan.md Verification item 2 | Outcome |
|---|---|
| ADR-050 accepted | Yes, Accepted (provisional pre-PR). D6's sizes were amended at W0 and again at W1 from T021's calibration (`risk-score` 13, `compensating-controls` 11, `trees` 12), and D2, D3, D4, D5 and the contracts record the architect's W1 rulings |
| Shared references and contract text committed (T005–T010) | Yes. The architect's review of T005–T009 was APPROVED_WITH_CONCERNS, and both fixes landed in W1 |
| CVSS on FIRST's 16 examples | Green: `tachi_scoring.self_test()`, and `test_cvss_category_defaults.py` at 248 passed |
| The part validator's hostile-input cases | Green: `test_tachi_parts.py`, 1,272 passed on Python 3.11 and 3.9 |
| The emitter's shape tests | Green: `test_sarif_identity.py`, 355 passed, including on `f374-macos` |
| The planner and reconciler's stale-part case | Green: `test_tachi_stage.py`, 255 passed, with `tachi-stage.py` at 100% line coverage |
| Fixture sizing and determinism | Green: `test_fixture_374.py` |
| Both CI legs green on the committed HEAD | Yes, as below |

## CI on `03a8f0d`, against T001's totals

Every check on the PR passed: 12 of 12.

| Job | T001 (pass / fail / skip) | `03a8f0d` | The difference |
|---|---|---|---|
| `tachi-pytest.yml`, ubuntu leg | 670 / 0 / 5 | 896 / 0 / 5 | +226: T014 moved the calculator into `tachi_scoring` and grew `test_cvss_category_defaults.py` from 22 cases to 248 |
| `tachi-pytest.yml`, macOS leg | 674 / 0 / 1 | 900 / 0 / 1 | +226, for the same reason |
| install-fidelity: extraction-fidelity | 249 / 0 / 6 | 270 / 0 / 6 | +21: T018's parser cases in `test_tachi_parsers.py` |
| install-fidelity: report-posture | 84 / 0 / 0 | 90 / 0 / 0 | +6: T022's confinement cases |
| install-fidelity: manifest-completeness | 15 / 0 / 2 | 15 / 0 / 2 | unchanged |
| `f374-offline` (3.11) | new | passed | W1's module list, ADR-050 D16's coverage gate (at least 80% over the four gated scripts), and the `tachi_parsers.py` ratchet (at least T001's 44.9%) |
| `f374-py39-floor` (3.9) | new | 2,546 / 0 / 34 | the same module list, on the floor interpreter |
| `f374-macos` | new | 355 / 0 / 0 | `test_sarif_identity.py`, on a case-insensitive volume |
| permissions-verify | C1–C8 pass | pass | — |
| maestro-coverage (co-fired by the orchestrator edit) | 11 / 0 / 2 | pass | — |
| gitleaks, both scans | pass | pass | — |

- **Not triggered.** mmdc-preflight and catalog-drift didn't run, because W1 touched none of their paths. Their T001 results stand.
- **No gated module fails** on either leg.

## The local scratch-clone run (W1's post-wave check)

The full `tests/scripts` and `tests/schemas` census at `03a8f0d`, on Python 3.11 in a scratch clone (H1), is in [wave-01/results.json](wave-01/results.json).
- **Totals:** 4,214 passed, 27 failed, 8 errors and 38 skipped. The 34 pre-existing failures and errors are identical, by test ID, to T001's and W0's, and all sit in ungated modules.
- **One flake.** `test_pdf_page_positioning.py`'s skip-image case failed once in Mermaid rendering during the full run, then passed 2 of 2 when re-run alone at the same commit. It is ungated, and W1 didn't touch its render path. It is recorded as a soft-gate skip with warning.

## TW-N3 at W2's entry

- **ARMED.** N3's fix hasn't merged: `origin/main` is still `b040fa1`.
- **Affected W2 lane** (from the private notes): **C**.
- No other W2 lane owns a spec the N3 fix edits.

## The cut-line SHA, for T084

**`03a8f0d`.** PR 2's branch `374-pipeline-resilience-track-o` is cut from this commit (T084, W1′).
