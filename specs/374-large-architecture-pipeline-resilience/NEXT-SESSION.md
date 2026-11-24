# Session Continuation: F-374 Large-Architecture Pipeline Resilience

**Generated:** 2026-11-24 14:40
**Branch:** `374-large-architecture-pipeline-resilience`, draft PR #423 (PR 1)
**Last pushed commit:** `27d58bd`, W4's push, with CI 14 of 14 green (7 workflows). This handoff's records commit follows it locally (see "State").

## Completed in session 2 (S2)

PR 1's W3 and W4, and PR 2's W1′, are complete. S2 hit the 3-wave ceiling, as `agent-assignments.md` planned. S2's orchestrator session ran out of context during W4's close-out. A fresh session finished W4 from the orchestrator's private status log, and nothing was lost.

- **W3, with the fix lane FX0.**
  - P0-1 to P0-9 landed as ruled (`test-results/w3-p0-fixes.md`). P0-10 to P0-12 are T080 follow-ups.
  - Also done: T034–T039, T052–T056, T059, T060 and T064.
  - Pushed as `f43440b`, with CI green.
- **W4.**
  - **T065, the offline end-to-end run:** SC-4, SC-5's offline half, SC-6 (R) and US-1a #4 and #5 pass, on Python 3.11 and 3.9 (`test-results/offline-e2e-pr1.md`).
  - **T066, the oracle:** clean under the PM's W4 rulings R-A to R-J (`test-results/oracle-pr1.md`, its W4 re-run and W4-10).
    - The classes are eleven, and the example-defect table is closed at five groups.
    - The gate is confirmed again on the merge candidate in W6 (plan.md Verification 7).
  - **T067's two reviews and T068's Step 7 scan:** the 2 HIGH findings are fixed, and the scan passes its gate.
  - **T146, the fix lane:** `test-results/t146-fixes-pr1.md` maps every finding to its commit. These include:
    - U-1: each finding's MAESTRO layer comes from its own row;
    - R-F: a correlation member listed twice is reported;
    - ADR-050 D2's W4 amendment (`9bd337e`): a `carried_forward` claim needs a result that the baseline holds.
  - **T069:** one push, `27d58bd`, with CI 14 of 14 green and both pytest legs at T001's totals plus PR 1's tests. TW-CI doesn't fire (`test-results/ci-pr1.md`).
  - **T070, the P1 checkpoint:** APPROVED_WITH_CONCERNS, with 8 items: 1 MEDIUM, 5 LOW and 2 INFO. See "Next Actions".
- **PR 2's W1′,** on `374-pipeline-resilience-track-o` (draft PR #425, pushed as `b302d2d`, CI green):
  - T084: the cut at `03a8f0d`;
  - T086–T088: ADR-050 rev. 3, with O-α, O-β, O-γ and RR3;
  - T089: the TW-ADR gate passes;
  - T148: the fixture cases;
  - T093: held at the local branch `374-hold-t093-orchestrator` (`8a08fb0`) until T094, in W2′, inverts its three inertness pins in the same commit.
- **Tests on `27d58bd`.**
  - The gated set: 6271 passed, 0 failed.
  - ADR-050 D16's gate: 96.35%, against 80%.
  - The `tachi_parsers` ratchet: 83%, against its 44.9% floor.
  - The census (`test-results/wave-04`): 7597 passed, 0 regressions, and the same 34 pre-existing out-of-gate failures as T001.

## State

- **Phase:** implement. **Tasks:** 84 of 150 done (PR 1: 77 of 91; PR 2: 7 of 59, marked on its own branch).
- **ADR-050** carries:
  - the W3 and W4 rulings;
  - D2's W4 amendment;
  - D3's copy of NFR-1's eleven classes (R-A to R-J).
  `contracts/module-signatures.md` holds W3's new public names.
- **TW-N3: ARMED.** N3 hasn't merged. Any edit to an agent file that the stages load needs the private no-touch notes (see the private track).
- **The local records commit is not pushed.** It holds `ci-pr1.md`, `wave-04/results.json`, this file, and tasks.md's T069 and T070 marks. H6 forbids pushing records alone, so the next push carries it: S3's P1 batch, or an earlier W5 fix.

## Next Actions: session L, which is PR 1's W5

1. **Resume** `/aod.build 374` on the branch. The branch lives in a linked worktree, so check `git worktree list`, and never switch branches in the main checkout (H9). The handoff check finds this file.
2. **Before T073's first dispatch.** These come from P1, and none is code.
   - **P1-1 (MEDIUM): re-run T065's offline driver on the W5 install commit,** about 0.05 d. T065's evidence is from `f43440b`, before W4's shipped changes. The re-run can overlap T072.
   - **T072's record decides three dispositions in advance** (TW-L2):
     - **(a) Exit 5 is the pass state** for T073 and T074 on the fixture. Its `threats.md` has no architecture-source line, and its baseline isn't shipped. So each run warns `architecture-path:body-line:absent` and `baseline-unresolved`.
     - **(b) A main-session departure from the command text is off-contract.** Examples: a `reconcile` before every listed wave's agents report, or a render before `reconcile` exits 0. Record it, file the follow-up, and don't claim that stage's SC. T073 and T074 record each run's `reconcile` calls, and the wave each one ran after.
     - **(c) A refusal for a pipe in a Section 7 cell is a code defect.** If T076 refuses a live `threats.md` for one (P1-3), it goes to T147 as a shipped-code defect. It isn't an agent off its contract.
3. **W5.**
   - T072: the adopters.
   - T073 and T074: the scorer and the controls stage, live, at the default effort and at `effort=max`.
   - T075: SC-8's post-fix runs.
   - T076: R-27's smoke run.
   - Then T077, the W5 gate (M5a). T078 runs only on a return from T077.
4. **Session L ends at T077 (M5a).** S3 follows, with PR 1's W6.
   - **First, P1's batch:** about 0.14 d, in one push.
     - P1-2: SA-4's file modes, through the renderers' `os.replace` and `fail`'s restore.
     - P1-4: the effort-estimate check, and D2's standing rule.
     - P1-5: `score-source`'s wording.
     - The ADR text: D2 near `:146`, D4's step 5, D3's two nits and D7's `%3A` note.
     - Four Known-limitations lines: SA-1's residual, SA-9, SA-14 and SA-15.
     - The same push carries the merge-candidate oracle (Verification 7) and P1-1's second run.
   - **Then** T079–T083.
5. **PR 2's S1′** (W2′ and W3′) can run beside L and S3, in PR 2's own worktree. T085 opens W2′, and T094 lands T093's held commit.

## How S2 ran, and what L should repeat

- **S1's rules held** (H9):
  - lane worktrees and cherry-picks;
  - agents never commit;
  - one task per agent instance;
  - a lane's worktree is created before its agent is dispatched.
- **Resume, don't re-brief.** A finished agent, resumed with one short message, did its follow-up with its context intact: T066's tester recorded R-J, and P1's architect took CI's result.
- **Keep the orchestrator light.** S2's main session ran three waves and about 65 agents in one context, and ran out at W4's close-out.
  - Keep agent returns short and tool outputs small.
  - Append to a private status log at every step. That log is what let a fresh session finish W4.
  - If the context runs long, start a fresh session at a wave boundary.
- **H1:** no pytest, extractor or renderer runs in a tracked tree. `rm -rf` is blocked here, so give every scratch clone a new name.

## Notes for later tasks

- **W5 (T072–T077).** S1's notes stand:
  - **The adopters** run under a neutral path that doesn't embed the source checkout's path. T072 and T075 reproduce SC-8's arrangement.
  - **The controls target** is the fixture's stub codebase at `c84ff16`, passed as `--target`. Its tree digest is in `sc8-baseline.md`.
  - **The SC-8 ceilings** are 29,753 output tokens for the scorer and 38,720 for controls.
  - **Pricing.** F17 is about 132–152 dispatches, and each effort level runs 26 scorer and 38 controls batches (P1). Controls has no margin at size 11, so check each live part's size.
  - **The completion rule** replaces "foreground" (ADR-050 D6's dated note).
- **T079 (W6's release notes):**
  - **O1 (T065):** an upgrading adopter's first run warns and exits 5 until the next `/tachi.threat-model` writes the architecture-source line, even at the default path.
  - **P1-3:** a raw or GFM-escaped pipe in a Section 7 cell now stops the run (exit 2, with the `&#124;` remedy).
  - **Item 4's lines:** the W4 ones from the PM's rulings, and the re-run line (`CF` is 1.0's column, now filled by the renderer). Whether to add "a `CF` mark needs a result that the baseline holds" is the PM's call.
  - **S1's notes stand:** the response cap depends on the environment; `&amp;`-style text now reads as the character; and the ASI01 taxa name stays in PR 1.
- **T080 follow-ups:**
  - S1's list, and `t146-fixes-pr1.md`'s "Deferred" list.
  - From P1: SA-1's residual (an issue), the `https%3A//` hardening, P1-3 unless it moves into PR 1, the read-back widening with T067a's L8, and SA-3's remainder.
  - U-2's colon-form title.
  - A list-form Section 7 with no baseline, which is a PM question when filed.
  - Merging correlation groups that share a member (an idea).
  - T065's O4: the fixture's stale `source_file`.
- **T066 at W6:**
  - the merge-candidate confirmation (Verification 7);
  - P1-6: spec `:588` and D3's quote state D2's pre-W4 rule, so a one-line PM erratum is needed;
  - either add D2's held condition to the oracle's derivation, or record the equivalence.
- **#364 at delivery:**
  - the example-defect table at the re-run's counts: U-4 178, U-12 6, U-15 1, U-17 10, and Reachability 7 findings;
  - `agentic-app`'s controls file, which claims 84 carried with no `CF` marked.
- **PR 2.** S1's notes stand: T114, R3b, O2's Phase 3.6, O3 and FR-K5.6. From T148:
  - 45 of the 120 chains need undirected reachability, so T116 confirms that reading;
  - the reissue check for an unused ID under a seeded mark is unruled;
  - the AGP mark's spelling goes to T092.

## Context files

`tasks.md` (W5 and W6), `agent-assignments.md`, `test-results/offline-e2e-pr1.md`, `test-results/sc8-baseline.md`, `test-results/oracle-pr1.md`, `test-results/t146-fixes-pr1.md`, `test-results/ci-pr1.md`, ADR-050, `contracts/`, `plan.md` and `quickstart.md`.

## Resume command

```bash
claude "Resume F-374 implementation (branch: 374-large-architecture-pipeline-resilience). PR 1's W0-W4 complete (77/91 PR 1 tasks; W4 pushed 27d58bd, CI 14/14 green; P1 APPROVED_WITH_CONCERNS). Run /aod.build 374 to continue with session L: P1-1's offline re-run and T072's three pre-decided dispositions, then W5's live matrix (T072-T077)."
```
