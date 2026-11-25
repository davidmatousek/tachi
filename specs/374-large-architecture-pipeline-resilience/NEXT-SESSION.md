# Session Continuation: F-374 Large-Architecture Pipeline Resilience

**Generated:** 2026-11-24, at session S3's close
**PR 1:** delivered. #423 was squash-merged as `d03ee9a`, and v4.48.5 is published (`cb06251`, #462) with PR 1's binding notes. Its branch is deleted on origin.
**PR 2:** branch `374-pipeline-resilience-track-o`, draft PR #425, base `main`, pushed at `b302d2d`. W1′ is done: 7 of 59 tasks.

## Completed in session S3 (PR 1's W6)

- **P1's batch** (`843ea01`, text follow-up `20ed9eb`):
  - P1-2: file modes survive the render and `fail`;
  - P1-3: GFM's escaped pipe in a Section 7 cell reads as a literal pipe. The PM's W6 ruling Q1 moved it into PR 1;
  - P1-4: the effort check reads its source;
  - P1-5: `score-source` is defined by its inputs;
  - P1-8: a test docstring;
  - EC-2, from the Step 8 economy gate: one snapshot key for the undeclared-paths check.
  - Also: ADR-050's text (D2, D3, D4 step 5, D7, Known limitations, history) and the PM's P1-6 erratum.
- **Verification on the merge candidate `ad64a72`:**
  - the oracle is CLEAN (Verification 7);
  - P1-1's second run passed on Python 3.11, 3.9 and 3.14;
  - the census shows 0 regressions (7656 passed);
  - P2 is APPROVED_WITH_CONCERNS, with 6 items: 3 fixed, 2 filed (#460, #461) and 1 informational.
- **Gates:** Step 6 was skipped (no UI files). Step 8 is advisory, with 13 findings (`economy-check.md`).
- **T080 and T081:** KB Entry 27, the CI guide's f374 jobs, and 35 follow-ups, #427–#461 (`test-results/followups-pr1.md`). The init baseline was regenerated for three targets.
- **T079:** the release notes; the PM's G-1 ruling (`w5-gate-pr1.md` §5b); and PRD §8's bookkeeping: #357 closed, #408 and #409 updated, N14 to N16 ticked on #397.
- **T082:** W6's one push, `8111c5e`, with CI 14 of 14 green; the merge `d03ee9a`; push CI on `main` green; #462 merged; v4.48.5 published with the notes.
- **T083:** `test-results/completion-pr1.md` with the team-lead's sign-off, the `[POST-MERGE]` tail #463, and the example audit leads on #364.

## State

- **Phase:** PR 1 done, 90 of 91 tasks; T071 is conditional and stays armed for PR 2. PR 2 is at 7 of 59, on its own branch.
- **TW-N3: ARMED**, unchanged. Any edit to an agent file the stages load needs the private no-touch notes (see the private track).
- **The board hazard (new in S3).** When a checkout has no `.aod/memory/github-project.json`, AOD's `create-issue.sh` and its stage updates run the board setup. That setup rewrites the Status field's options and clears every board item's Status.
  - It happened twice in S3, and the board was restored from each item's event history.
  - The main checkout, the integration worktree and PR 2's worktree now hold a cache that matches the live board.
  - Before any AOD board command in a NEW worktree, copy that cache into it first. The defect is filed as #464.
- **Usage:** the week resets on Nov 26 at 9pm ET.

## Next Actions: PR 2's session S1′ (W2′ and W3′)

1. **Resume** `/aod.build 374` on PR 2's branch, in its linked worktree. Check `git worktree list`, and never switch branches in the main checkout (H9). Confirm that the worktree's board cache exists before Step 1's stage update.
2. **Decide first, with the architect and the team-lead:**
   - The economy gate's EC-1 (#443) advises hoisting the shared entry plumbing into `tachi_parts` at PR 2's start, before W2′'s new entry scripts copy it.
   - PR 2's branch predates PR 1's renderers. So either T127's merge of `main` moves earlier, or #443 waits until W4′.
3. **W2′:** T085 opens it. T094 lands T093's held commit (the local branch `374-hold-t093-orchestrator`).
4. **When PR 2 merges `main` (T127),** expect conflicts:
   - in this feature's records (`tasks.md`, this file);
   - in ADR-050: W6's edits and the merge status against revision 3.

   Keep both sides: `main`'s PR 1 records and PR 2's marks.

## Notes for PR 2

- T078's reading binds T133.
- **W5′'s max runs** launch with `CLAUDE_CODE_EFFORT_LEVEL=max` plus `--effort max`. Check the agents' effort in the transcripts (KB Entry 27).
- **PR 2's follow-ups and halves:**
  - #460 (P2-2);
  - P1-3's writer half, the threat-model writer's line on Section 7 pipes;
  - #430's triggers.
- **S2's notes for PR 2 stand:**
  - T114, R3b, O2's Phase 3.6, O3 and FR-K5.6;
  - 45 of the 120 chains need undirected reachability;
  - the reissue check for an unused ID under a seeded mark is unruled;
  - the AGP mark's spelling goes to T092.
- **#463's open items:** the optional Code Scanning check (quickstart §5) can join T139's, with `threats.sarif`.
- **Delivery (T138):**
  - a `fix(374):` title;
  - `--match-head-commit`;
  - an explicit squash subject and body;
  - only PR 2 closes #374.

  Release PRs' workflows wait at `action_required`, so follow the #422 and #462 precedent, after `push:[main]` is green.

## How S3 ran

- **One push per wave (H6).** The P1 batch, the records, T080, T081 and T079 went in one push, so W6 cost one CI cycle.
- **The init-baseline tests clone the committed HEAD** (`init_sh_helpers`). An uncommitted overlay needs a commit inside the scratch clone before they can see it.
- **In zsh, `set -- $var` doesn't word-split.** A CI watcher built on it never exited, and the pipeline sat idle for about 20 minutes. Parse in Python.
- **Use literal `gh` commands for issues in fresh worktrees,** or seed the board cache first (see "State").

## Context files

`tasks.md` (Part 2), `agent-assignments.md`, `test-results/completion-pr1.md`, `test-results/followups-pr1.md`, `economy-check.md`, ADR-050, `contracts/`, `plan.md` and `quickstart.md`.

## Resume command

```bash
claude "Resume F-374 PR 2 (branch 374-pipeline-resilience-track-o, draft #425). PR 1 is delivered (d03ee9a, v4.48.5). Run /aod.build 374 for PR 2's session S1′ (W2′–W3′). First decide, with the architect and the team-lead, whether #443's hoist and T127's merge of main move to W2′'s start."
```
