# W1-Exit Trip-Wire Checkpoint (T039)

**Task**: T039 (W1 exit; the `/aod.build` wave 2 → 3 checkpoint) · **Feature**: 373-adopter-install-output-fidelity · **PR**: #375
**Date (UTC)**: 2026-09-28 · **Ruled by**: `team-lead`, invoked by the `orchestrator` · **Head evaluated**: `0448bfb` (A-3, W1's last commit)
**Rule**: PM ruling P-11.3. TW-0, TW-1 and TW-2 are re-evaluated once, on the W0/W1 actuals, with PRD §10's thresholds and the fixed carve order K15 → K11 → K13-posture.

## Ruling: NO CARVE

No trip-wire fires under any defensible conversion of agent wall-clock to plan days. No revert is ordered, so SBE-B has no T039 work. W2 may launch on this ruling; § 7 lists the gate items that are still open.

| Trip-wire | Fires if | Actual (1 plan day = 8 h of elapsed wall-clock) | Ruling |
|---|---|---|---|
| **TW-0** (aggregate) | W0 + W1 > 2.04 d, which makes the projected duration > 5.5 d | W0 + W1 ≤ **0.58 d** (≤ 4 h 40 m, T039 included); projected **4.05 d** | **NOT FIRED**. Margin 1.45 d (0.29 d at sign-off) |
| **TW-1** (K11) | T020 > 0.36 d, which makes K11 > 1.2 d | T020 = **0.011 d** (5 m 19 s); K11 re-summed **0.85 d** | **NOT FIRED**. Margin 0.35 d |
| **TW-2** (K13-posture) | T024 > 0.15 d, which makes K13-posture > 0.6 d | T024 = **0.036 d** (17 m 16 s); K13-posture re-summed **0.49 d** | **NOT FIRED**. Margin 0.11 d |

What follows from the ruling:
- **K15 goes ahead in W2** (T027–T029). From here on it can be carved only through TW-6 in W3, using T030's late-carve procedure. TW-5 caps it at two prompt iterations.
- **K11 and K13-posture stay in the bundle.** This was their last trip-wire evaluation (P-11.3: "once"). Taking either out later is a PM scope decision. § 6 keeps the carve mechanics on record.
- **P-9.5 and P-10.2 hold.** S-9 ships with K11. K15 ships, so its first-iteration renders double as K14's per-template renders (P-10.2 (a)).
- **TW-3 and TW-4 are outside T039.** TW-3 stays not fired, because its triggers (OQ-4 and P-2) are closed. TW-4 is judged when T031 runs in W2.

## 1. Inputs

**Rule text**:
- tasks.md: T039; § Trip-Wire Evaluation (the TW-0 pacing table and formula, the TW-1 and TW-2 limits, the lane budgets); § PM rulings (P-11.3).
- agent-assignments.md § 3 (the checkpoint map) and § 5 (the per-wave windows).
- feasibility-check.md § 2 (the day unit) and § 7 (the TW definitions).
- PRD-373 § 10.

**Actuals**: the orchestrator's wall-clock record, cross-checked against commit timestamps (`git log`, UTC) and the lane records in `.aod/results/`. B1's per-task spans come from `sbe-b-373-w1.md`; the other records are `sbe-t-373-t008.md`, `devops-k3{a,b,c}-373.md`, `devops-a-373-w1.md` and `sbe-c-373-w1.md`.

| Event (2026-09-28, UTC) | Time | Source |
|---|---|---|
| W0 starts (build wave 1) | 01:45:24 | orchestrator |
| T003's fixture and builder commits, and the T001/T002 record (`c45d171`, `7ac5a59`, `c4dabd7`) | 02:17:32 | git |
| **W0 closes; W1 starts** (build wave 2) | **02:20:41** | orchestrator |
| C1: T012 and T013 committed in their lane (`d6e94e7`, `c688144`) | 02:39:31, 02:39:46 | git (author time) |
| B1: T007 | 02:44:06 → 02:51:14 | B1 record |
| A-1 `70a9e7a`, green on #375 | 03:00:12 | git; Lane A record |
| A-2 `2024ce4`, green on bare ubuntu with no quarantine | 03:23:18 (green ≈ 03:27) | git; orchestrator |
| B1: T016 | 02:51:14 → 03:28:01 | B1 record |
| B1: **T020** (`a837ae8`) | **03:28:01 → 03:33:20** | B1 record; git author time 03:33:17 |
| B1: **T024** (`5328b56`) | **03:33:20 → 03:50:36** | B1 record; git author time 03:50:47 |
| B1's four commits replayed onto the branch | 03:54:28 | git (committer time) |
| A′: T008 | 02:20:41 → ≈ 02:54 | orchestrator; T008 record |
| A′: two failed T009 dispatches (a stream stall, then a 64k output-token overflow, both before any edit) | ≈ 02:54 → ≈ 04:22 | orchestrator; K3-a record |
| A′: T009 restaged as K3-a, K3-b and K3-c | ≈ 04:22 → ≈ 05:23 (12 + 30 + 18 min) | orchestrator; K3 records |
| A′: the lock-step commit `c194946` (T008–T010) | 05:24:26 | git |
| **A-3 `0448bfb`, W1's last commit** | **05:25:23** | git |
| T039 (this ruling) | after A-3; an allowance of up to 1 h, until the record is committed | — |

## 2. Converting agent wall-clock to plan days, and what the re-check can still tell us

**The conversion: 1 plan day = 1 working day = 8 hours of elapsed wall-clock.**
- **The unit.** A plan day is the feasibility check's "attention-day at the AOD agent-orchestrated pace, measured from branch to merge" (§ 2).
  - It was calibrated on delivery records in elapsed working days. F-362, the one multi-lane precedent, took 5 working days.
  - Those builds were paced by the maintainer's attention: when sessions ran, and how long reviews and checks waited.
  - W0 and W1 ran autonomously and met no human gate, so they came in far ahead of plan. That is a difference in pacing, not an error in the unit.
- **Why 8 hours and not 24.** An 8-hour day counts every hour of this overnight run (EDT) as working time. That makes the actuals three times larger than a calendar-day reading would, so it is the conservative choice: it leans toward firing.
- **What is measured.**
  - TW-0 tests duration. Each wave counts as elapsed wall-clock from its start to its closing commit, including stalls, failed dispatches and waits on gates inside the wave. Parallel lanes are not summed.
  - W1's plan chain ends with T039 (0.03 d), so W1's actual includes this ruling, at an allowance of up to 1 hour.
  - TW-1 and TW-2 test effort on one sequential lane. They use each task's own span in B1's sequence, checked against wider attributions (§ 4, § 5).
- **The plan-native cross-check agrees.** tasks.md restates TW-0 on the calendar: it fires if "W1 is still open at the start of Wednesday 09-30". W1 closed on Monday 09-28 at 05:25Z (01:25 EDT).

**Is the re-check still meaningful? It is valid and robust, but it no longer discriminates.**
- **Valid and robust.** The formula mixes units. W0 and W1 are actuals, while W2–W4 stay at plan pace, which W0–W1 beat by 3–4×. That mix pushes the projection toward firing, so a no-fire under it is safe. TW-0 would fire only if a plan day were worth 2.3 hours of wall-clock or less (§ 3).
- **No longer discriminating.** At this pace, W0 + W1 could pass 2.0 d only if the build stalled for more than a working day. The check can no longer tell a healthy build from a slipping one. The same holds for TW-1 and TW-2: their break-evens (2 h 53 m and 72 min) sit far above the actuals.
- **What it still says.** W0–W1 did not slip. K11 and K13-posture also showed none of the hidden complexity the item limits exist to catch: both landed first try with their tests green, no existing assertion changed, and the goldens stayed byte-identical (`.aod/results/sbe-b-373-w1.md`).
- **Where the risk sits now.** It sits in serial verification, which is bound by wall-clock and by people, not by agent execution:
  - the 2-OS CI cycles, at 22–29 min each (K3's convergence is W2 work);
  - the triad checkpoints;
  - the maintainer's visual checks in W3.

  TW-5 to TW-7 and the P0/P1 checkpoints cover these.

## 3. TW-0 (aggregate)

**Formula** (tasks.md § TW-0): projected duration = Σ wave windows (pacing chain × 1.25) + 1.0 d for plan and deliver.
- At T039, W0 and W1 take their actual durations. W2–W4 and the 1.0 d constant stay as planned.
- An actual duration already contains the friction the 1.25 buffer prices, so it replaces the window directly. The sensitivity table below also shows it re-buffered.

| Wave | Planned pacing | Planned window | Re-check input | Basis |
|---|---|---|---|---|
| W0 | 0.20 | 0.25 | **0.07** (35 m 17 s) | actual |
| W1 | 1.20 | 1.50 | **≤ 0.51** (3 h 04 m 42 s to A-3, plus T039's ≤ 1 h) | actual |
| W2 | 1.04 | 1.30 | 1.30 | plan |
| W3 | 0.78 | 0.975 | 0.975 | plan |
| W4 | 0.15 | 0.19 | 0.19 | plan |
| Σ windows | 3.37 | 4.21 | 3.05 | |
| + plan and deliver | | 1.00 | 1.00 | plan |
| **Projected** | | **5.21** | **4.05** | ≤ 5.5, so **not fired** |

- **Threshold on W0 + W1**: 5.5 − 1.0 − 2.46 (the planned W2–W4 windows) = **2.04 d**. tasks.md rounds this to "about 2.0", against 1.75 planned. The actual is **≤ 0.58 d**.
- Closing W1 at A-3 instead, as the orchestrator's record does, gives 0.46 d and a projection of 3.92 d.
- TW-0 fits before the first carve step, so the carve order is never reached.

**Sensitivity** (W0 + W1 = ≤ 4 h 40 m, T039 included):

| Conversion | W0 + W1 (d) | Projected (d) | Margin to 5.5 d |
|---|---|---|---|
| 1 d = 24 h (a calendar day) | 0.19 | 3.66 | 1.84 |
| **1 d = 8 h (the ruling basis)** | **0.58** | **4.05** | **1.45** |
| 1 d = 8 h, with the actuals re-buffered × 1.25 | 0.73 | 4.19 | 1.31 |
| 1 d = 4 h (a stress case) | 1.17 | 4.63 | 0.87 |
| Break-even | 2.04 | 5.50 | 0, which needs 1 d ≤ 2.29 h |

## 4. TW-1 (K11)

**Limit.** K11 summed to 1.14 d at sign-off, against a 1.2 d limit. T020's planned 0.30 d plus that 0.06 d margin gives T039's threshold of 0.36 d. The re-sum is 1.14 − 0.30 + T020's actual.

| T020 attribution | Wall-clock | Plan days | K11 re-sum | Against 1.2 d |
|---|---|---|---|---|
| **Its own span, 03:28:01 → 03:33:20 (the ruling basis)** | 5 m 19 s | 0.011 | **0.85** | not fired (margin 0.35) |
| Plus all of T016, in case K11 design work happened there | 42 m 06 s | 0.088 | 0.93 | not fired (margin 0.27) |
| All of Lane B1, W1 start → replay (an upper bound) | 1 h 33 m 47 s | 0.195 | 1.04 | not fired (margin 0.16) |
| Break-even for T020 alone | 2 h 53 m | 0.36 | 1.20 | — |

**Why the wider rows.** Five minutes is fast for T020's scope, so the actual was checked against the commit before it was accepted.
- `a837ae8` is +366/−50 across `scripts/tachi_parsers.py`, both extractors and `tests/scripts/test_tachi_parsers.py`, with 7 new tests.
- It covers every T020 bullet: the inherent read and composite join; both tier-1 call sites; `classify_control_status` replacing both row idioms; the clamp; the missing-residual default; and the band fallbacks.
- T016 had already added the inherent and control-status aliases to `HEADER_ALIASES`. Some K11 groundwork therefore sat in T016's span, and the wider rows cover it.
- No K11 scope moved into W2 beyond the plan. The Section 1 comparand and row-count warnings were always T021's (data-model § 4.5).

## 5. TW-2 (K13-posture)

**Limit.** K13-posture summed to 0.50 d, against a 0.6 d limit. T024's planned 0.05 d plus the 0.10 d margin gives 0.15 d. The re-sum is 0.50 − 0.05 + T024's actual.

| T024 attribution | Wall-clock | Plan days | K13-posture re-sum | Against 0.6 d |
|---|---|---|---|---|
| **Its own span, 03:33:20 → 03:50:36 (the ruling basis; it includes a 35 s gated-suite run)** | 17 m 16 s | 0.036 | **0.49** | not fired (margin 0.11) |
| Plus the replay onto the branch (to 03:54:28) | 21 m 08 s | 0.044 | 0.49 | not fired (margin 0.11) |
| Break-even for T024 | 72 m | 0.15 | 0.60 | — |

`5328b56` is +67/−2 in two files, with 3 new tests. No existing assertion changed.

## 6. Carve orders

**None.** SBE-B makes no revert.

For the record (NM-2), the carve map stays executable. The evidence is the orchestrator's dry runs in scratch clones at `5328b56`:

| Item | Mechanics | Dry-run evidence |
|---|---|---|
| K15 | Nothing has landed. At `0448bfb` there is no `allow_list`, `compute_allow_list`, `ALLOWED IDS AND NAMES` line or K15 amendment note, and no K15 commit. A carve would mean not dispatching T027–T029, and T015 would then render all six templates (P-10.2 (b)). | Free |
| K11 | `git revert a837ae8` (T020). The three product files revert cleanly. There is one conflict region at the end of `tests/scripts/test_tachi_parsers.py`, where T020's and T024's test blocks are adjacent; resolve it by hand, keeping the posture tests. If K11 and K13-posture ever go together, revert newest-first (`5328b56`, then `a837ae8`) and the conflict does not arise. | Resolvable by hand |
| K13-posture | `git revert 5328b56` (T024) | Clean; 219 passed / 2 skipped on the gated set |

W2's K11 and K13-posture commits extend these revert sets: T021–T023, T025–T026, the `report-posture` job, and their T032 golden commits. Keep the own-commit rule for them. T032's per-K-item golden commits, and any carve the PM orders, depend on it.

## 7. Wave 2 → 3 gate (agent-assignments.md § 3)

| Item | Status |
|---|---|
| T039's ruling recorded | **Done**: this file. The orchestrator commits it |
| Any ordered revert made and verified | Not applicable: none was ordered |
| The fast workflow green on the W1 head (`manifest-completeness`; `extraction-fidelity` with the contract module) | Open: A-3's push is in flight. `manifest-completeness` re-runs, because `scripts/install.sh` changed |
| K3's first 2-OS `tachi-pytest` run recorded | Open: in flight. Local evidence at `c194946`: 56/56 K3 tests, and 237 passed / 1 skipped / 1 xfailed on the 18-module mirror |
| The wave-2 gated set (§ 4) green in a scratch clone of `0448bfb` | Open: orchestrator |
| The NEXT-SESSION snapshot | Open: orchestrator. It is T039's second deliverable, not part of this ruling |

**Launch clause.**
- W2 lanes may be dispatched on this ruling.
- Before the first W2 commit lands on the branch:
  - the gated set is recorded green at `0448bfb`;
  - both fast-workflow jobs are green on the pushed head. P-9.1 still applies: a red cut-line job stops every commit;
  - the NEXT-SESSION snapshot exists.
- K3's 2-OS run is recorded when it completes. A red there goes to DEVOPS-K3 under T010, and it holds only Lane A's K3 work, whose files no other lane touches.

## 8. Notes for W2 and for T033 (TW-7)

### 8.1 Lane budgets for TW-7, with the W1 actuals (1 d = 8 h)

TW-7's lane arm fires when a lane runs more than 50% over its budget, that is, above 1.5 × budget.

| Lane | Budget (d) | TW-7 fires above (d) | The same, in wall-clock | W1 actual | Budget used |
|---|---|---|---|---|---|
| A′ | 1.32 (1.17 in W1, plus 0.15 of W2 convergence) | 1.98 | 15.8 h | 3 h 04 m = 0.38 d: T008 ≈ 33 m; the two failed T009 dispatches ≈ 1 h 30 m; K3-a, K3-b and K3-c ≈ 1 h 01 m | 29% |
| A (W1) | 0.72 | 1.08 | 8.6 h | ≈ 1 h 06 m of active work = 0.14 d (SBE-A ≈ 30 m; A-1 ≈ 8 m; A-2 ≈ 26 m, with one stall and resume; the A-3 wiring ≈ 2 m). Elapsed, it was 3 h 05 m = 0.38 d, mostly A-3's rule-imposed wait for A′ | 19% active; 53% elapsed |
| B1 | 0.97 | 1.46 | 11.6 h | 1 h 34 m, from W1's start to the replay = 0.20 d | 20% (closed) |
| C1 | 0.58, T014's module included | 0.87 | 7.0 h | ≈ 20 m = 0.04 d | 7% (closed) |
| B2a | 0.72 | 1.08 | 8.6 h | W2 | — |
| B2b | 0.55 | 0.83 | 6.6 h | W2 | — |
| C2 | 0.50 | 0.75 | 6.0 h | W2 | — |
| Test lane (W2) | 0.91 (0.77, plus T032's 0.14) | 1.37 | 10.9 h | W2 | — |
| Lane A (W2): a proposed row | ≈ 0.23 (T011's 0.15, plus ≈ 0.08 of DEVOPS-A wiring, from the W2 load table) | ≈ 0.35 | ≈ 2.8 h | W2 | — |

**Recommended rules for T033's ruling:**
- **Use the same conversion**: 1 d = 8 h of elapsed wall-clock.
- **What counts toward a lane.** A lane's actual is the elapsed time of its own dispatches, failed and stalled ones included. Waits imposed by another lane's gate are excluded, such as A-3's wait for A′. Where the two readings differ, report both, as the Lane A row does.
- **Test each row as a whole.** A′'s row is 1.32 d.
  - Its W2 convergence part on its own (0.15 d, which is 1.8 h at +50%: about four 25-minute CI cycles with their fixes) is a watch item for T034's float, not a trigger.
  - Lane A's W2 work (T011 and the W2 wiring commits) has no row in tasks.md. The proposed row above takes its budget from the W2 load table.
- **The first arm.** Remaining projected work at T033 is about 1.7 d at central, as tasks.md computes it: W3 0.975, plus W4 0.19, plus about 0.5 d of deliver. It fires only if W2 leaves W3 more than about 0.3 d of carry-over or new scope, for example T010 still unconverged.
- **Calendar time is not work.**
  - At this pace, Session 1 (W0–W2) should end on 09-28, about two days before M2 (Wed 09-30).
  - W3 is then paced by the maintainer's visual check: about 1 hour, planned for the afternoon of Thursday 10-01, with the morning of Friday 10-02 in reserve.
  - TW-7 measures work, so waiting for that window does not fire it. Whether the wait justifies shipping Group A early through T040 is a PM release decision, not a trip-wire.
  - Record in `NEXT-SESSION.md` that Session 2 can start as soon as the maintainer can give that hour. Pulling the window forward pulls M3 and M4 forward.

### 8.2 Dispatch sizing: the A′ lesson

**What happened.**
- T009 was W1's largest task: 0.62 d, and about 400 changed lines of bash. It went out as one dispatch.
- The first attempt stalled mid-stream. The second overflowed the 64k output-token limit. Both failed before making any edit, and together they cost about 1.5 h, about half of A′'s W1 wall-clock.
- It was restaged as K3-a, K3-b and K3-c (12, 30 and 18 min). Each was a bounded step with small in-place edits, named exit tests and a written handoff, and each landed first try.
- A′ still finished at 29% of its budget, and it paced W1, as the plan predicted. Lane A also had one stream stall, on A-2, and resumed.

**The rule for W2:**
1. **Pre-stage any multi-file task, or any task of 0.25 d or more**, into sequential sub-dispatches of about 30 minutes each. Give each one a single file cluster, the named tests it must turn green, and a handoff note in its results file. The W2 candidates:
   - **T021** (0.45 d): `compute_risk_funnel`; then S-9's baseball-card fields; then the Section 1 comparand and row-count warnings and the `source` strings.
   - **T017**, B2b's part: the K12 wiring; then K13.1's per-tier table; then the eight-file 4b sweep with its ledger.
   - **T019** (0.34 d): the K9, K10, K12 and K13.1 regression tests; then the sibling-parity module; then the K11 join-path parity case, in its own K11 commit.
   - **T025** (0.32 d), B2b's part: the Typst changes and the `main.typ` guard; then the stale-data module.
   - **T028** (0.25 d): the five preambles and the reference; then the executive-architecture amendment and the lock-rule note; then the agent text.
2. **Edit files in place.** Never regenerate a whole file in one response.
3. **Keep test logs out of the transcript.** Run long suites in the background into a log file, and report the totals. K3-c did this with the 11.5-minute `tachi-pytest` mirror.
4. **Restage at once after a failed dispatch.** If a dispatch stalls or overflows before editing, split it smaller. Do not resend the same prompt: T009's second attempt failed in a new way at the same size.
5. **Failed-dispatch time counts** toward the lane's TW-7 actual.

### 8.3 Keep K15's revert set clean

- The NM-2 dry run showed that stand-alone commits are necessary but not sufficient for a clean revert. T020's and T024's test blocks were appended back to back at the end of `test_tachi_parsers.py`, so reverting T020 alone conflicts there.
- The only trip-wire carve left is K15's, through TW-6: T030 reverts T027, T028, T029 and any iteration commits. In W2, keep K15's additions out of contact with other items' additions in shared files:
  - in `tests/scripts/test_gemini_request_contract.py`, T029's A9 and A10 go in a block of their own, separated by unchanged lines from T019's A11 (a K9 test, which is not carvable);
  - in `scripts/extract-infographic-data.py`, T027's `allow_list` lines stay apart from T025's posture lines (LOW-4, already in T027).
- Where contact can't be avoided, name the expected hand resolution in the commit body.

### 8.4 Items for T033 (the P0 checkpoint) and T035

- **Installer contract `:145`.** K3-b and K3-c kept data-model § 2.1's literal precedence, in which a link is judged unresolvable before nested.
  - So the "nested, unresolved" message variant at `contracts/installer-cli.md:145` can't be reached, and no test exercises a dangling nested link.
  - The orchestrator marked the phrase as superseded, pending the architect's P0 ruling (`.aod/results/devops-k3c-373.md`).
  - T011's security review should see the same note.
- **A warning class K11 removed.** T020 dropped the legacy raw-score-vs-heading "misclassified" warning, which the clamp-then-band rule supersedes. No gated test pinned it.
  - P0's parser-semantics review should confirm the removal.
  - T035 should expect that stderr class to disappear wherever inputs carried it, and attribute the change to K11.
- **T010 stays open** until both OS legs are green on #375, in W2.

### 8.5 Retro input for `/aod.deliver`

Time-based trip-wires stated in plan attention-days stopped discriminating once the build ran autonomously. The break-evens for TW-0, TW-1 and TW-2 sat 3.5–32× above the actuals. W1's real information came from rework signals instead: failed dispatches, red CI cycles and assertion churn.

This is a candidate KB entry for autonomous builds: state build-time trip-wires in the observed pace, or in wall-clock hours, and add rework signals beside them.
