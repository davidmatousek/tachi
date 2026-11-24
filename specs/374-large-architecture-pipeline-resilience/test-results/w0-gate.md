# Gate G0: W0's end (T004)

**Date:** 2026-11-22. **Base:** the branch tip at `1c55360` (code-identical to v4.48.4, `b040fa1`). **Inputs:** T001's [prestate.md](prestate.md), T002's [k4-five-whys.md](k4-five-whys.md) and T003's [s1-proxy.md](s1-proxy.md).

## Result: PASS. G0 doesn't hold W1.

TW-K4 affects PR 2 only, and TW-N3's rule starts at W2 (T004).

| Check | Outcome |
|---|---|
| The pre-state is frozen (T001) | Yes. No gated module fails on either CI leg. The ratchet floor is 44.9% |
| TW-K4, ruled from T002 | **(c)**: record it and proceed |
| TW-N3 | **ARMED**: N3's fix hasn't merged |
| #400 carries P-2's conflict list | It didn't, so G0 posted it ([#400 comment](https://github.com/davidmatousek/tachi/issues/400#issuecomment-7088729797)) |
| T003's sizes and SC-8's example, for T023, T018 and T021 | Recorded below. The sizes reading goes to T023 at W1's start |
| Does T075 double as R-27's smoke run (PM-T7)? | **No.** T076 is R-27's own run, in lane L2 |
| T144 | **Not fired**, since TW-K4 is (c), not (b) |

## TW-K4: (c), record and proceed

- **T002's verdicts:**
  - Context pressure: UNDETERMINED.
  - Instruction ordering: UNDETERMINED.
  - A skipped conditional: CONFIRMED as why the failure was silent, and UNDETERMINED as its trigger.
  - Link criteria that legitimately yield zero: RULED OUT. The run's retained inputs form chains under the same text.
- **Evidence (C-13).** Run A's orchestrator transcript wasn't retained. Its saved outputs were, and they settle candidate 4.
- **The disposition** (the build-time table, verbatim): "(c) Record it and proceed; PR 2's fixture runs serve as the reproduction (C-13)."
  - So T144 doesn't fire.
  - D13 stands as ruled, and T115–T118 keep their scope.
- **R-21 doesn't fire.** No finding changes which findings join chains.
- **Erratum, recorded here.**
  - The PRD and `feasibility-check.md` C-13 date Run A to late September, on v4.48.0. The private run notes date it to July 2026, on v4.47.0. The skip was spotted in late September, from the saved outputs.
  - Phase 3.5's text is byte-identical at v4.47.0, at v4.48.0 and at the branch tip. So nothing that depends on the version changes, and C-13's caution about evidence retention held.
  - The signed texts stay as signed, and this record is the correction.

## TW-N3: ARMED

- N3's fix hasn't merged, and no PR for it is open at this gate.
- **W1.** The text lanes (T008, T009) edit agent specs before the trigger. They check the private notes and record any overlap privately.
- **From W2's start,** the rule binds. T026 records only which W2 lanes it affects.

## T003's sizes, for T023, T018 and T021

D6's W0 measure is a proxy taken from the v4.48.4 outputs of the shipped examples. T021(a) confirms it on the pre-fix fixture run.

| Stage | u (tokens) | Size | Plan size | Reading |
|---|---|---|---|---|
| `risk-score` | 802 | **9** | 40 | Row A, D6's literal proxy: the heavier file as committed, with two files per unit |
| `compensating-controls` | 844 | **9** | 30 | Row A |
| `trees` | 656 | **12** | 12 | One write per tree |
| `threats.md` rows | 298 (Sections 3 and 4), 84 (Section 7) | 26, 94 | — | For PR 2's O-β |
| Report findings | 326 | 24 | — | For PR 2's O-γ |

- **Sensitivity** (s1-proxy.md §4). The proxy is an upper bound on a part item, since the new agents write a JSON part without tables or a SARIF envelope.
  - The other readings give scorer and controls sizes of 5 and 6 (both files summed), 13 and 13 (compact SARIF), 14 and 17 (the markdown only), and 21 and 14 (a contract-shaped part item, a model that only W5's live runs can confirm).
- **SC-8's example (P-7).**
  - No shipped example has 9 or fewer open findings, so none is "below both stages' batching thresholds" at the literal sizes.
  - **`ascii-web-api`** (11 open findings, `threats.md` only) is single-batch if both constants are at least 11.
  - **`consumer-agent-app`** (19, with committed scorer and controls output) needs both at least 19.
- **Routing, decided at G0:**
  1. **T023 (architect) rules first in W1,** before T018 fixes the constants and before T021(b) runs. It rules which reading D6's "Amended at W0" table adopts, and T021(a) confirms the result before W1's push.
  2. **If both ruled constants are at least 11,** SC-8's example is `ascii-web-api`, named here before W1's baseline run.
  3. **If either is below 11,** no shipped example meets P-7 as worded. P-7's example then returns to the PM before T021(b) runs, recorded under T021.
- **Cost, for T062.**
  - At 9 and 9, the base set plans 44 to 50 batches per stage, about four times the plan sizes' 10 to 15. At 21 and 14 it plans 19 to 22 and 28 to 33.
  - F17 (T073, T074) and W5's window need re-pricing. T062 prices them with the team-lead at M3.

## R-27 and SC-8's session conditions (PM-T7)

- T075's post-fix runs don't double as R-27's smoke run, because T076 runs R-27 under the session profile in its own lane (L2).
- So T021(b)'s SC-8 baselines run **without** the session profile, at the adopter default effort, and T075 runs under the same conditions (P-7).

## The pre-state that G1 compares against (from T001)

| Gate | Totals (pass / fail / skip) | Source |
|---|---|---|
| `tachi-pytest.yml` | ubuntu 670 / 0 / 5; macOS 674 / 0 / 1 | CI run 44962377970; a local macOS run matches |
| `tachi-install-fidelity.yml` | manifest-completeness 15 / 0 / 2; extraction-fidelity 249 / 0 / 6; report-posture 84 / 0 / 0 | CI; local runs agree, apart from the shells and mmdc that are present locally |
| `tachi-permissions-verify.yml` | C1 to C8 pass | CI run 44962378072, and locally |
| Co-fired | maestro-coverage 11 / 0 / 2; mmdc-preflight passes; catalog-drift 16 / 0 / 0 | the latest runs on an identical surface |
| #365 | six known reds in `test_backward_compatibility.py` | local |
| Full `tests/scripts/` (no gate) | 1,730 passed, 26 failed, 8 errors, 5 skipped, of 1,769 | local, Python 3.11; every failure and error is in the 31 ungated modules |

- **The ratchet floor (E3):** 44.9% for `scripts/tachi_parsers.py` under `test_tachi_parsers.py` (917 statements, 505 missed). T022 wires it into `f374-offline`. A floor of 44.9 tolerates about one extra uncovered statement.
- **Out of scope:** T001 also found a pre-existing defect: `scripts/check-citation-urls.py` imports `yaml` at module level. It is held for the close-out follow-ups (T080).
