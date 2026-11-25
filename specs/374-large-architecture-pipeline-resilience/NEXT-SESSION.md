# Session Continuation: F-374 PR 2 (Track O), from session S1′'s W2′ close to W3′

**Generated:** 2026-11-25, when session S1′ closed W2′.
**PR 1:** delivered as `d03ee9a` (v4.48.5).
**PR 2:** branch `374-pipeline-resilience-track-o`, draft #425 (base `main`), pushed at `ab1e3cc`. W2′ is done. W3′ to W6′ remain.

## Completed in session S1′

**The W2′ entry** ruled two things, recorded in `test-results/w2-entry-pr2.md`:
- **T085, re-scoped.** T127's integration now runs at W2′'s entry, through a merge of PR 1's final head and then a marker merge of `origin/main`. `origin/main` is an ancestor of the branch, so later integrations are plain merges.
- **#443's items 1–4.** The hoist (T151, T152, and R3b-1's shared argument checks) moved the stage-entry path into `tachi_parts`, behavior-preserving:
  - E1–E5 green;
  - E4's oracle finds 0 differences;
  - PR 2 refers to #443 and leaves it open.

**Pushes:**
- the pre-hoist push, CI 8 of 8;
- the hoist push, CI 10 of 10;
- W2′'s push at `ab1e3cc`, CI see below.

**Planning:**
- tasks.md v1.5, then v1.6, with the new tasks T151–T162;
- rulings S1P-A1 to S1P-A103 (architect), S1P-T1 to S1P-T16 (team-lead) and S1P-PM1 to S1P-PM12 (PM), in the contracts, ADR-050 and tasks.md;
- PR 2 projects at T0 + 14.55 against its bound of T0 + 15.0.

**W2′ delivered:**
- **The planner,** T092: the run-level plan, `close`, `id-mark`, the batch stages, and `fail`'s PR 2 fold.
- **The Phase 2 watch,** T156.
- **The joiner,** T106 and T107.
- **The chain script,** T116 and T117.
- **The assembler,** T108 to T110.
- **The rewritten `threats.sarif` generator,** T100, with its migrated modules (T158).
- **The overflow detector and the dispatch templates,** T093, T094, T111 and T157.
- **`tachi_parts`' PR 2 key sets,** T091.
- **Two parser functions,** T116's slice and T159.
- **The fixture's PR 2 runs,** T103.
- **The runtime floor,** T150, and the wiring, T114.
- **The S-9 spike,** T104, and its rulings, T090.
- **The ADR lane's contract work,** T162.

**Evidence at W2′'s tip:**
- the full census: 12,117 passed, and against the integrated tip 0 regressions and 0 new failures. The 34 pre-existing out-of-gate failures are unchanged;
- the coverage gate is 98.31%;
- the `tachi_parsers.py` ratchet is 84.2%, against its floor of 44.9;
- the 3.9 floor passes 10,427.

**W2′'s CI:** W2′'s push (`ab1e3cc`) reached the branch, but GitHub never synced PR #425: after an hour its head still read `28531ae`, and no workflow ran. This handoff commit is pushed to re-trigger the sync, as a recorded exception to H6. **Before W3′ starts, confirm that #425's head is this commit or later, and that its CI is green.** Watch it bound to the head SHA (`gh run list --commit <sha>`), because `gh pr checks` returned the previous push's green checks. T114 stays open until then.

## State

- **TW-N3: ARMED,** unchanged. O2's and T's W3′ edits to agent files the stages load need the private no-touch notes.
- **H14's two-PR clauses are retired,** because PR 1 is delivered. Its usage clause stands.
- **The board:** #374 is in Build. This session made no board writes.
- **Disk.** Each helper test run makes a fresh scratch clone, about 140 MB, and deleting them is permission-denied. Free space ran out once mid-wave. Keep the number of runs small. The owner decides on a clone-reuse policy.
- **Durability.** A wipe of the temporary directory once destroyed the lane worktrees mid-wave. Committed lane work survived, and uncommitted work was rebuilt from the agents' transcripts. Commit returned lane work promptly, and prefer a durable scratch path.

## Next Actions: W3′ (a fresh session)

1. **Resume `/aod.build 374`** on PR 2's branch, in a linked worktree.
   - Never switch branches in the main checkout (H9).
   - Seed the board cache before any AOD board command (#464).
2. **Run W3′'s lanes,** per tasks.md v1.6:
   - OC: T095, then T096;
   - O3: T097, T101 and T119;
   - X: T098 and T102;
   - O2: T112 and T118 (TW-N3 applies);
   - T: T113 (TW-N3 applies);
   - P′: T120, then T121;
   - G: T122, the bound check, with the team-lead's re-projection and the handoff.
3. **Rule early in W3′,** with the architect:
   - `check`'s move-aside renames onto an occupied `attack-chains.inconsistent.md`, overwriting it, as D13's rewrite always did. A fixed `--output-dir` with alternating outcomes can lose the oldest copy, which sits uneasily with "an earlier run's file is never deleted".
   - The assembler escapes file names through `ascii()` in messages (RD-29). A directory under a planned tree name fails at write time, with exit 4, rather than early.
   - T103's synthetic runs follow T's readings for the plan input names, so T096 confirms them.
4. **T096 depends on two rulings:** the four `coverage-gap:unrecovered:<reason>` codes (S1P-A103), and S1P-A19's repeated-member report (exit 5).

## Notes for later waves

- **T135, the release notes for PR 2.** The items so far:
  - the four batch stages stay unbounded under S1P-PM11, with each command's remedy and the 90-minute hang sign;
  - `fail` restores a recorded pre-image for every stage, including the scorer and controls (S1P-A55, S1P-PM12);
  - `threats.sarif`'s kept and dropped properties (S1P-A28);
  - the alert text from Section 7;
  - the tool version (#412);
  - #443's bookkeeping: leave it open, and tick only the finished items.
- **T136's follow-ups:**
  - bounding the batch stages (S1P-PM11), as a standalone fix after PR 2;
  - whether `fail` should refuse a plan whose `plan.json` names another plan;
  - call-site wiring tests for both renderers (8 hoist mutants are pinned only by probes);
  - #364 would lose 47 committed example tags unless it regenerates those examples' `threats.md` first.
- **T160,** in W5′: the live `watch` demonstration. Its first check is whether the watch's exit wakes a waiting orchestrator. If not, fallback (b) applies and the watch is removed before merge.
- **Delivery (T138):**
  - a `fix(374):` title;
  - `--match-head-commit`;
  - an explicit squash subject and body;
  - "Refs #443" only;
  - only PR 2 closes #374.
