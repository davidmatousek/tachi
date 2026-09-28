# NEXT-SESSION: Feature 373 build (snapshot at W1 exit, T039)

**Snapshot taken**: 2026-09-28, at the W1 → W2 boundary (the fallback break point of tasks.md T039). T033 at the end of W2 rewrites this file with the full Session 1 handoff; if this version is still here, Session 1 broke at W1 exit.

- **Feature**: #373, adopter install + output fidelity fixes (K1–K3, K9–K15, #370)
- **Branch**: `373-adopter-install-output-fidelity` · **Draft PR**: #375 (`fix(373): …`)
- **Build waves 1–2 complete** (tasks.md W0 and W1). Ledger: 16 of 40 tasks `[X]`. T010 stays open until both `tachi-pytest.yml` legs are green (it converges in W2).

## Next actions

1. **Wave 3 = tasks.md W2**, which T039 released (NO CARVE: K15, K11 and K13-posture all ship). Lanes and file ownership are in tasks.md § Lane / file ownership and agent-assignments.md § 1:
   - **B2a** (`extract-infographic-data.py`): T017's part, T025's emission, T021, T027;
   - **B2b** (`extract-report-data.py`, Typst, the Typst contract, the report-assembler text, the 4b sweep): T017, T025's Typst part and the posture module, T022's caption, T031's docstring;
   - **C2** (infographic text, the agent, the command, `schemas/infographic.yaml`, the adapter): T018, T026, T022's text, T028;
   - **the test lane**: T019, T023, T029, T031's tests;
   - **Lane A**: T010 convergence, T011 (README K3 section plus the `security-analyst` review) and the W2 wiring commits (sibling parity, the `report-posture` job).
   - Then T032 (goldens, one commit per K-item) and T033 (the P0 architect checkpoint, the N4 re-run, TW-7, then this file rewritten).
2. **Dispatch sizing (T039 § 8.2)**: pre-stage any task of 0.25 d or more into sequential sub-dispatches of about 30 minutes each (T021, T017-B2b, T019, T025-B2b, T028). Make edits in place, run long suites in the background into a log, and restage smaller after any failed dispatch.
3. **Keep K15's revert set clean (T039 § 8.3)**: T029's A9/A10 go in their own block in `test_gemini_request_contract.py`, apart from T019's A11. T027's `allow_list` lines stay apart from T025's posture lines.

## Gate status at W1 exit

| Wave 2 → 3 gate item (agent-assignments.md § 3) | State |
|---|---|
| T039 ruling in `test-results/w1-exit-checkpoint.md` | **NO CARVE** (TW-0 4.05 d against 5.5; TW-1 0.011 d against 0.36; TW-2 0.036 d against 0.15) |
| Any ordered revert | none ordered |
| Fast workflow green | yes, at `0448bfb`: `manifest-completeness` and `extraction-fidelity` (with the contract module), plus the co-fired `maestro-coverage`, `mmdc-preflight`, `catalog-drift` and gitleaks |
| K3's first 2-OS `tachi-pytest` run recorded | run 36381945986 at `0448bfb`; see `.aod/results/devops-a-373-w1.md` (A-3 section) for the per-leg result |
| Wave-2 gated set green (§ 4) | yes: `test-results/wave-02/results.json`, 424 passed, 0 failed, 2 skipped (the known skip and xfail), 0 regressions |
| NEXT-SESSION snapshot | this file |

## Checkpoint log (architect build-time note 3)

For this feature, `agent-assignments.md` § 3 replaces `/aod.build` Step 2c's generic checkpoint numbering:

| Checkpoint | After build wave | Reviewer | Status |
|---|---|---|---|
| (none) | 1 (W0) | quality gate only | passed: pre-state, smoke and fixtures recorded |
| **T039** trip-wire re-check | 2 (W1) | team-lead ruling, invoked by the orchestrator (in place of Step 2c's P0 architect review at wave 2) | **NO CARVE**, 2026-09-28 |
| **P0** (Go/No-Go) | 3 (W2) | `architect` (T033), plus the TW-7 team-lead ruling | pending |
| **P1** | 4 (W3) | `code-reviewer`, then `architect` (T036) | pending |
| **P2** | 5 (W4) | `architect` | pending |

## Commits on the branch (W0–W1)

| SHA | What |
|---|---|
| `0ce39d0` | BACKLOG regen (the **W0 SHA**; T035 regenerates the oracle pre-snapshot here) |
| `c45d171`, `7ac5a59`, `c4dabd7`, `8916554` | W0: fixtures, sandbox builders (a stand-alone commit, LOW-3), the pre-state and smoke records, the wave-1 gate |
| `70a9e7a` | **A-1**, the cut line: K1/K2 plus the completeness guard (green) |
| `2024ce4` | **A-2**: the extraction modules gated; PD-8 (green on bare ubuntu, no quarantine) |
| `d6e94e7`, `c688144` | C1: K14 GA chain, reference, agent, adapter, config blocks |
| `1660c10`, `1e30e90` | B1: PD-6 splitter; K9, K10 and K12 parser helpers with both call sites |
| `a837ae8` | B1: **K11** parser and join wiring (stand-alone) |
| `5328b56` | B1: **K13-posture** `compute_risk_posture` (stand-alone) |
| `c194946` | **K3** lock-step: `install.sh` pre-flight, 56 tests, `tachi-pytest.yml` wiring |
| `0448bfb` | **A-3**: K14 contract test (A1–A8, 52 cases) gated in `extraction-fidelity` |

## Facts the next session needs

- **Worktrees and scratch are session-local.** W1 used git worktrees under this session's scratchpad (`…/scratchpad/wt/lane*`). A new session gets a new scratchpad, so create fresh worktrees from the branch tip. Never run pytest, the extractors or `install.sh` in the main tree (#365); verify in scratch clones of committed state.
- **The oracle pre-snapshot**, if the scratchpad is gone: re-run the `snapshot.sh` appendix of `test-results-prestate.md` in a scratch clone at `0ce39d0`. It is deterministic; T001 checked that with two runs.
- **W0 decisions**: `IMAGE_SIZE_RESTORED = true`; 3:4 passes on both GA models; no AR-2 "other status" (`test-results/w0-smoke.md`).
- **The installer contract's `:145` "nested, unresolved" message variant is unreachable** under data-model § 2.1's precedence (unresolvable before nested). The orchestrator kept the normative precedence; the architect rules on the text at P0 (T033). T011's security review should see this.
- **K11 removed a legacy stderr warning** (raw score vs heading "misclassified"). P0 confirms it, and T035 attributes it to K11.
- **Reverting K11 alone** conflicts in one region at the end of `tests/scripts/test_tachi_parsers.py` (T020 and T024 test blocks are adjacent). Revert newest-first, or resolve by hand. After T039, only K15 remains carvable (via TW-6).
- **Agent tooling**: a single large dispatch (T009, about 400 lines of bash) stalled once and then overflowed the 64k output-token limit, twice, before making any edit. Staged ~30-minute dispatches (K3-a/b/c) each landed first time.
- **Session 2 (W3–W4)** is paced by the maintainer's visual check: about 1 hour for T030/T015 (six images plus the executive-architecture PDF page). It can start as soon as that hour is available.

## Resume prompt

```
claude "Resume Feature 373 implementation (branch: 373-adopter-install-output-fidelity). Waves 1-2 complete (T039: NO CARVE). Run /aod.build to continue with Wave 3 (tasks.md W2)."
```
