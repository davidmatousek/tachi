# W2-Exit TW-7 Ruling (T033)

**Task**: T033, the TW-7 part (end of W2; the `/aod.build` wave 3 checkpoint) · **Feature**: 373-adopter-install-output-fidelity · **PR**: #375
**Date (UTC)**: 2026-09-28 · **Ruled by**: `team-lead`, invoked by the `orchestrator` · **Head evaluated**: `4bea6c5` (W2 integrated, goldens committed, pushed)
**Rule**: tasks.md T033 and § TW-5 to TW-7. Group A ships early through T040 if either (a) the remaining projected work exceeds 2.0 d, or (b) any lane is more than 50% over its budget. TW-7 carves nothing.
**Conversion and counting**: T039's (`w1-exit-checkpoint.md` § 2 and § 8.1). 1 plan day = 8 hours of elapsed wall-clock. A lane's actual is its own dispatch time, failed and stalled dispatches included, with waits on other lanes' gates excluded. Full reasoning: `.aod/results/team-lead-373-t033-tw7.md` (local, gitignored).

## Ruling: NOT FIRED. T040 is not triggered

| Arm | Fires if | Actual | Ruling |
|---|---|---|---|
| **(a)** Remaining projected work | > 2.0 d | **1.72 d** at plan pace: W3 0.975 + W4 0.19 + deliver 0.50. W2 carried nothing over and added ≤ 0.05 d. The most adverse reading is 1.92 d | **NOT FIRED**. Margin 0.28 d |
| **(b)** Lane overrun | any lane > 150% of its budget | Highest: **Lane A (W2), at 47%** (52 min against 0.23 d, counting the unplanned SEC-K3-01/02 fix). B2a 18%, B2b 21%, C2 16%, test lane 16%, A′ 33% (W1 + W2). No lane is over budget at all | **NOT FIRED** |

What follows:
- **T040**: mark it `[X]` with the note "not triggered (TW-7 did not fire at T033)". The orchestrator makes the edit. There is no early branch, no second release, and no merge of `main` back into #375.
- **One release, at deliver.**
  - T038 writes PD-7's notices for that one release. P-11.2's split-release notices don't apply, and SC-6 is verified once.
  - K14's early-ship conditions (P-9.1, P-10.4) no longer apply. K14 is live-verified in W3's render session, as planned.
- **K15 can be carved only through TW-6**, using T030's late-carve procedure. TW-5 caps it at two iterations. K11 and K13-posture are past their last trip-wire (T039), so taking either out is a PM scope decision.
- **An early Group A release is still possible, but only as a PM release decision, not through the trip-wire.** The team-lead does not recommend it. Moving the maintainer's hour earlier (§ 5.1) ships the whole bundle sooner and avoids T040's costs: 0.25–0.50 d, a second release, and merging `main` back through the version conflicts.
- **Re-open conditions.** Two T033 inputs were still in flight at this ruling. The orchestrator re-invokes it before the session break only if:
  1. `tachi pytest` at `4bea6c5` is not green within two 2-OS cycles; or
  2. P0 returns fixes that are not closed in Session 1 and total more than 0.18 d at tasks.md's per-task pace. That is arm (a)'s margin with SEC-K3-03 in the bundle.

  Otherwise this ruling is final.

## 1. Inputs

**Actuals.** The orchestrator's W2 record gives each lane's figure as the sum of its own staged dispatches. I cross-checked it against commit timestamps (`git log`, UTC) and the per-stage records in `.aod/results/`: `sbe-b2a-373-s1..s4`, `sbe-b2b-373-s1..s4`, `sbe-c2-373-s1..s3`, `sbe-t-373-s1..s3`, `sbe-t-373-t032`, `sbe-a-373-t011`, `security-analyst-373-k3`, `devops-k3-373-sec` and `devops-a-373-w1`. Every stage figure matches its record's span to within about 1.5 minutes.

| Event (2026-09-28, UTC) | Time | Source |
|---|---|---|
| T039's record committed (`2b59e05`) | 05:42:02 | git |
| **W2 starts** (build wave 3) | **05:44:25** | orchestrator |
| T010: K3 green on both `tachi-pytest` legs at the first 2-OS run, recorded (`afab3ba`) | 05:46:17 | git; run 36381945986 |
| Lane A: T011's README (`763ff0e`), then the security review | 05:50:00; ≈ 05:46 → 06:03:49 | git; records |
| Lane A: the unplanned SEC-K3-01/02 fix (`45bb8d6`, verified on the 18-module mirror: 239 passed) | ≈ 06:04 → 06:29:50 | git; record |
| The last stage records: C2 / B2b / B2a (T027, `d990f66`) / test lane (T029, `7f7cd47`) | 06:23:22 / 06:43:26 / 06:47:01 / 06:51:11 | records; git |
| Lane A's W2 wiring (`4ab1d74`, `075cca5`) | 06:52:28, 06:54:42 | git |
| T032: three golden commits, one per K-item (`5a1810e`, `3ffc3db`, `982c074`) | 07:01:28 → 07:01:51 | git |
| **W2 integrated and pushed** (`4bea6c5`) | **07:03:58** | git |
| CI at `4bea6c5` | from 07:04 | `gh run` |

CI at `4bea6c5`:
- green: the fast workflow (`manifest-completeness`, `extraction-fidelity`, `report-posture`) and the co-fired gates (`catalog-drift`, `mmdc-preflight`, `maestro-coverage`, gitleaks);
- running: `tachi pytest`, both legs, expected at about 07:32.

W2 ran **1 h 19 m 33 s** to `4bea6c5`, about 0.17 d against its 1.30 d window. The rest of T033 follows: P0, the N4 re-run, and this ruling.

## 2. Arm (b): lane budgets

| Lane | Budget (d) | Fires above: d / wall-clock | Actual | Used |
|---|---|---|---|---|
| A′ (K3: T008–T010, W1 plus W2 convergence) | 1.32 | 1.98 / 15.8 h | W1 3 h 04 m. W2: T010 green at the first run (≈ 2 min to record) plus the SEC fix (25 min). Total 3 h 32 m = 0.44 d | **33%** |
| A (W1) | 0.72 | 1.08 / 8.6 h | 0.14 d active; 0.38 d elapsed (T039) | 19% active; 53% elapsed (closed) |
| B1 | 0.97 | 1.46 / 11.6 h | 0.195 d. 0.24 d if the W2 T016 gap fix is charged back (≤ 21 min: its whole B2a stage) | 20–25% (closed) |
| C1 | 0.58 | 0.87 / 7.0 h | 0.04 d | 7% (closed) |
| B2a | 0.72 | 1.08 / 8.6 h | 17 + 21 + 12 + 10.5 = 61 min = 0.127 d | **18%** |
| B2b | 0.55 | 0.83 / 6.6 h | 16 + 13 + 15 + 12 = 56 min = 0.117 d | **21%** |
| C2 | 0.50 | 0.75 / 6.0 h | 21 + 5 + 11.5 = 38 min = 0.079 d | **16%** |
| Test lane (W2), with T032 | 0.91 | 1.37 / 10.9 h | 25.5 + 16.6 + 22.7 + 7 = 72 min = 0.150 d | **16%** |
| Lane A (W2): T039's proposed row (T011 0.15 d, plus 0.08 d of wiring) | 0.23 | 0.35 / 2.8 h | README 5 + security review 18 + SEC fix 25 + wiring 4 = 52 min = 0.108 d | **47%** (24% without the SEC fix) |

- **The unplanned SEC fix (25 min, DEVOPS-K3) is charged to both rows it could belong to.** It sits in A′, whose agent and file it is, and in Lane A (W2), whose review found it. Each row is tested at its worst.
- **The orchestrator's integration** (about 20 min of cherry-picks and verification) sits outside every lane row. No lane budget prices it; the wave window's 1.25 buffer does. Charging all of it to the smallest row, Lane A (W2), gives 72 min, or 65%, which is still under budget.
- **The record-to-record spans**, which include orchestrator turnaround, give B2a 63 min, B2b 59, C2 39 and the test lane 79. That is 16–22%.
- **Break-even conversions.** A row reaches 150% only if a plan day is worth less than:
  - 51–68 min for the four heavy W2 lanes;
  - 1 h 47 m for A′;
  - 2 h 31 m for Lane A (W2), or 3 h 29 m with all the integration time charged to it.

  The ruling basis is 8 h.

## 3. Arm (a): remaining projected work

The projection is the plan's own, "about 1.7 d" at T033 (tasks.md § TW-5 to TW-7): the remaining waves and deliver at plan pace, plus whatever W2 carried over or added.

| Component | Plan days | Basis |
|---|---|---|
| W3 window. Pacing chain 0.78 × 1.25: T034 (0.05) → the render session, T030 → T015 (0.43) → a T032 re-run (0.05) → T035 (0.20) → T036's checkpoint (0.05) | 0.975 | plan |
| W4 window: T037 (0.15) × 1.25 | 0.19 | plan |
| Deliver | 0.50 | plan |
| **Carry-over from W2** | **0** | All 15 W2 tasks before T033 are `[X]`. T010 went green at the first 2-OS run. The fast workflow and the co-fired gates are green at `4bea6c5` |
| New scope: contract text (the installer `:145` variant; "40" → "32" hops at `contracts/installer-cli.md:37` and `data-model.md:41`, `:51`) | ≤ 0.05 | The architect writes it at P0, in Session 1. It is counted here in case it slips to W3 |
| New scope: SEC-K3-03 | 0 | A follow-up issue, filed at deliver within its follow-up step (§ 5.4) |
| **Remaining** | **1.72** | Under 2.0, so **not fired**. Margin 0.28 d |

| Reading | Remaining (d) | Margin to 2.0 |
|---|---|---|
| **The ruling basis** | **1.72** | **0.28** |
| SEC-K3-03 fixed in the bundle (≤ 0.10) | 1.82 | 0.18 |
| As above, with deliver read as the whole post-plan remainder of TW-0's 1.0 d constant (0.60, not 0.50) | 1.92 | 0.08 |
| Observed pace. W0–W2 ran at about 3–6× the plan's pacing chains. The wait for the maintainer's hour is excluded | ≈ 0.5–0.8 | > 1.2 |

- **T033's own open parts are excluded**, as in tasks.md's 1.7 d baseline: P0, the N4 re-run and `NEXT-SESSION.md`. They run before either release path, so they don't bear on the early-ship decision.
- **Calendar time is not work** (T039 § 8.1). The wait for the maintainer's hour, planned for the afternoon of Thursday 10-01, counts toward neither arm.

## 4. Rework signals (T039 § 8.5)

| Signal | W1 | W2 |
|---|---|---|
| Failed or stalled dispatches | 2 failed (T009); 1 stall, resumed (A-2) | **0**. Every lane was split into ~30-minute stages (§ 8.2) |
| A gap in earlier-wave work | — | 1: T016 stored tier-3 statuses raw. The fix was 7 lines plus a test (`9019528`); no golden moved |
| Security findings fixed | — | 1 MEDIUM and 1 LOW (SEC-K3-01/02), unplanned, 25 min. 1 LOW that predates F-373 is still open (SEC-K3-03) |
| Red CI cycles | 0 | 0 so far. `tachi pytest` at `4bea6c5` is in flight |
| Assertion churn | 0 | 1, deliberate: K3's hop-boundary case moved from 40/41 to 32/33 with SEC-K3-01, pending P0 |
| Golden churn outside T032 | 0 | 0 |

The signals agree with the times: W2 ran clean. Its one unplanned item, the SEC fix, was bounded and test-first, and it was verified on the full 18-module mirror.

## 5. Carry-forward notes for Session 2 (W3–W4)

### 5.1 The render session and the maintainer's hour

- **The maintainer's hour is W3's only human gate, and it paces W3.** The plan reserves two slots:
  - the afternoon of Thursday 10-01: about 1 hour, for six images plus the executive-architecture PDF page;
  - the morning of Friday 10-02: 30 minutes, held for a TW-5 iteration.
- **Book the earliest slot the maintainer can give.** Every W3 input is ready once Session 1 closes, so Session 2 should start on that slot rather than wait for Thursday.
  - M3 and M4 move day for day with it. With a Tuesday 09-29 slot, M4 lands about Wednesday 09-30, not Friday 10-02.
  - This is a scheduling choice, not a trip-wire.
- **Spend the hour on judgment, not on waiting:**
  1. T034 opens Session 2: commit, push, and CI starts. Create fresh worktrees and scratch clones from the branch tip, because scratch is session-local.
  2. About 30 minutes before the hour, the `tester` starts iteration 1 from T034's commit: the six templates, then T015's fallback render and the PDF page, timing every 2K render. A blocked model then shows up before the hour, and P-10.1's diagnosis runs outside it.
  3. The maintainer checks the set. If anything leaks, iteration 2 follows:
     - SBE-W3 edits the text in its own commit, re-runs T032 and re-pushes through T034;
     - the `tester` renders again;
     - the maintainer checks the new set, in the same sitting or in Friday's reserve slot.
- **Render and check in one Session 2 sitting.** The images exist only in that session's scratchpad, and none is committed (#365). A session break between the render and the check loses them.
- **TW-6's clock starts at the first blocked render.** Half a day is 4 h of elapsed wall-clock at this ruling's conversion. P-9.2's full path for K14 applies only after that half day plus one retry session, and only if both models stay blocked (quickstart § 4).

### 5.2 K15 can be carved only through TW-6

- **The procedure is T030's late carve.** SBE-W3 runs it:
  1. Revert T027, T028, T029 and any T030 iteration commits. At that point the architect decides whether T028's agent-section deferral stays as a routing fix; by default it is reverted too.
  2. Re-run T032 for the surviving K-items. K15's golden authorization lapses (SC-8).
  3. Hand back to the `tester`. Once renders resume, T015 renders all six templates under P-10.2 (b); otherwise it records K14 under P-9.2 and P-10.1.
  4. Move SC-5's leakage and allow-list clauses to K15's follow-up issue. Run `export AOD_REPO=davidmatousek/tachi` first.
  5. Re-push through T034.
- **The revert set is clean today.** In a scratch clone at `4bea6c5`, `git revert --no-commit 982c074 7f7cd47 d990f66 f57bd37 d0eae8e` applied with **zero conflicts** across 15 files. That is newest first: T032's K15 goldens, T029, T027 and T028's two commits. LOW-4 and T039 § 8.3 held.
- **Keep it clean in W3:**
  - each T030 iteration is its own commit, and it joins the revert set;
  - a 2K drop belongs to K14 and must survive a K15 carve. Keep it in its own commit, never mixed with a K15 iteration, even though both edit the same template files (the configuration fence and the preamble);
  - after any carve, re-run T032 rather than trusting the golden revert (F4).
- **TW-5** allows at most two iterations. Residual leakage goes to the follow-up issue decided in advance.

### 5.3 The 2K latency rule (T015)

- **Only the render session can decide it.** `IMAGE_SIZE_RESTORED` has been `true` since W0. W0's 2K response times (10.9–19.7 s) came from trivial prompts, and W0's own record says they don't predict real templates.
- **Record every real 2K render's response time.** If any exceeds about 45 s, SBE-W3 drops 2K in **one** commit that changes:
  - the six configuration blocks;
  - the reference and the adapter copy;
  - `IMAGE_SIZE_RESTORED` (PD-3).

  A1 and A4 go red on a partial drop. Record the reason in the PR and in the reference provenance, and re-push through T034 before T036 (LOW-4).
- **A blocked model** is recorded as statically verified only, with a follow-up issue. The record goes in three places: the reference provenance, the PR record and release-notes notice 6. Both GA models stay in the chain.

### 5.4 SEC-K3-03 (LOW): the team-lead's view is a follow-up issue

- **The flaw predates F-373.** `main:scripts/install.sh:119,125` has the same unguarded `git checkout "$VERSION_TAG"` behind the same tag-existence check. F-373 moved the lines (now `:279`, `:285`) without changing them. To exploit it, a tag named like a git option must already exist in the source repository, and the operator must type it.
- **It is outside F-373's FR set.** Scope belongs to the PM (the laziness ladder's first rung). File it at deliver with the other follow-ups, after `export AOD_REPO=davidmatousek/tachi`. It costs about zero on the timeline.
- **If P0 or the PM brings it in instead:**
  - DEVOPS-K3, the `install.sh` owner, adds the argument-parse guard and one negative test in their own commit, **before T034 pushes**. It then rides T034's 2-OS cycle. Landing it after T034 would cost a second 2-OS cycle (about 28 min) before T036.
  - At ≤ 0.10 d, TW-7 still does not fire (1.82 d).

### 5.5 Other items for P0 and Session 2

- **The 32-hop ceiling and the contract text.** P0 ratifies `45bb8d6` in Session 1. It also amends the three "40 hops" lines and the `:145` variant. If the architect rejects 32, don't simply revert `45bb8d6`: that re-opens a confirmed MEDIUM, a partial install on Darwin through a chain of 33–40 hops.
- **The T016 gap fix and AR-3.** `9019528` edited `scripts/tachi_parsers.py` in W2, although AR-3 gives that file no W2 writer.
  - The writer was the file's W1 owner, SBE-B, in one stand-alone 7-line commit. No other W2 lane touched the file, and no golden moved, so the single-writer intent held.
  - P0's parser-semantics review should ratify it.
  - In W3, only SBE-W3 writes this file, and only for fixes T035 or T036 require.
- **Split T036's code review into stages.** The branch diff is 56 commits across 103 files. 37 of those files are code, at +7,851/−425 lines. Following § 8.2, split the review into three dispatches:
  1. the K3 installer and its tests;
  2. the parsers, extractors, Typst and #370 (K9–K13);
  3. the infographic text and the contract tests (K14–K15).

  Each writes its part of `.aod/results/code-reviewer-373.md`. The first can start at T034's commit.
- **Dispatch sizing held.** W2 had no failed dispatch with ~30-minute stages. Keep § 8.2's rule for SBE-W3 and T035.

## 6. Recommended NEXT-SESSION "Next actions" (W3, in dependency order)

**Before the session break (Session 1):**
- P0 is APPROVED, including the 32-hop ratification and the contract text. Any CHANGES_REQUESTED item is fixed by its owning lane.
- The N4 re-run is attributed against T001.
- `tachi pytest` is green on both legs at `4bea6c5`.
- T033 is `[X]`, and T040 is `[X]` with "not triggered (TW-7 did not fire at T033)".
- `NEXT-SESSION.md` carries this list.

**Session 2, W3:**
1. **Book the maintainer's hour** at the earliest available slot, and start Session 2 on it (§ 5.1).
2. **T034** (DEVOPS-A):
   - fold in SEC-K3-03 only if P0 brought it into scope;
   - commit and push, and CI starts;
   - re-run the N4 modules in a scratch clone, and attribute any delta against T001.

   T036's first review dispatch may start here.
3. **The render session**, in one sitting. The `tester` runs it, and SBE-W3 is the only writer. It works in a scratch clone of T034's commit, on a scratch copy of `examples/maestro-reference/`, through the agent end to end:
   1. T030's iteration 1: all six templates, executive-architecture at 3:4, every 2K render timed;
   2. T015: the fallback-model render, and executive-architecture on one portrait page of a scratch PDF. Apply the 2K rule (§ 5.3);
   3. the maintainer's visual check;
   4. if needed, one more T030 iteration (TW-5): its own commit, then T032 for the scaffolded goldens, a re-push through T034, a new render and a new check;
   5. TW-6's late carve, if renders stay blocked for more than half a day (§ 5.2);
   6. the records: `test-results/k15-renders.md`, and the PR-body fields for T015 and T030.
4. **Re-run T032** (SBE-W3) if a K15 iteration changed prompt text, or after a carve, for the surviving K-items.
5. **T035** (SBE-B), after the last text change:
   - the oracle post-snapshot;
   - `oracle-diff.md`, by field class × K-item, with per-example counts. The expected movers include NM-1's 4/0/82 and 12/69, the stderr class K11 removed, and the N7 warning;
   - 100% of the diff attributed.
6. **T036.**
   - Finish the staged code review. SBE-W3 makes any fix, and re-runs T032 or T035 if an output changes.
   - Then the architect's P1, after T035. CI must be visibly green on the final W3 head: every fast-workflow job, both `tachi-pytest.yml` legs, and the co-fired gates.
7. **W4**: T037 ∥ T038 (notes for the single release) → P2 → `/aod.deliver`. At deliver:
   - apply KB Entry 18's checks before any merge;
   - file the follow-ups: SEC-K3-03, any TW-5 residual, any blocked model, and N7.
