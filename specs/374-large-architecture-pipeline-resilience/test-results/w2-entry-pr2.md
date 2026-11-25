# W2′ entry: PR 1 integrated into PR 2's branch (T085)

**Date:** 2026-11-24, session S1′, lane X (devops). **Branch:** `374-pipeline-resilience-track-o` (draft PR #425).

**Result:** PR 1's final head is merged into PR 2's branch, `origin/main` is an ancestor of it, and the parity check passes (KB 18).
- **Method:** T127's two legs, as ruled at S1P-A1 and S1P-A2. Leg 1 is M1 (`7abc02a`), a merge of `8111c5e`. Leg 2 is M2 (`bb0154b`), a merge of a marker (`bed95a9`) built on `origin/main` (`47a4f95`).
- **Conflicts:** 5 conflicted files, 4 in leg 1 and 1 in leg 2 (7 hunks in all). They are the 5 that S1P-A3 predicted. Each was resolved by its rule, and no text was added or edited.
- **Result of the merges:** the branch now differs from `origin/main` in 18 paths (+8546/−36). Those are PR 2's own 19 paths without `NEXT-SESSION.md`. A trial merge of the branch into `origin/main` is clean, so #425's `dirty` state should clear at the entry push.
- **Not done here:**
  - nothing was pushed, and no test, script, extractor or renderer ran (H1);
  - the byte check of the merged fixture generator (S1P-A5) is T103's first step, in lane F;
  - the cross-read of the merged ADR and contracts (S1P-A4) is the architect's;
  - the census at the entry (S1P-A6) is the orchestrator's.

## Method and SHAs

| Item | Commit | Tree | Notes |
|---|---|---|---|
| PR 2's head before T085 | `9fd2266` | `c746793` | Clean, one commit ahead of its remote |
| PR 1's final head | `8111c5e` | `d888c71` | `refs/pull/423/head`. Its tree equals the squash `d03ee9a`'s: `git diff 8111c5e d03ee9a` is empty |
| `origin/main` | `47a4f95` | `d6e168e` | Fetched at the start, and as expected. Local `main` (`b040fa1`) was never used (H11, KB 18) |
| **M1** | `7abc02a` | `4054d92` | Leg 1: `git merge --no-ff --no-commit 8111c5e`. Parents `9fd2266`, `8111c5e` |
| **Marker** | `bed95a9` | `d6e168e` | `git commit-tree 'origin/main^{tree}' -p origin/main -p 8111c5e`. Parents `47a4f95`, then `8111c5e`. Its tree equals `origin/main`'s. No branch points to it, and M2's second parent keeps it reachable |
| **M2** | `bb0154b` | `6ae1713` | Leg 2: `git merge --no-ff --no-commit bed95a9`. Parents M1, then the marker |

The steps, in order:
1. `git fetch origin`, then `origin/main` read `47a4f95`, the expected SHA.
2. Before each merge, a read-only `git merge-tree --write-tree` preview gave the conflict set that S1P-A3 predicts: 4 files, then 1.
3. Leg 1 ran, and the conflicts were resolved by rule with a scratch script outside the repository. The script recombines whole lines that the two sides already hold, and it asserts that no line was added or lost. The four paths were staged by explicit path (H3), and M1 was committed.
4. The marker was built by plumbing: no checkout, no scratch worktree, and no ref moved. Its tree and parents were checked.
5. Leg 2 ran the same way and gave M2.
6. The parity check ran (below).

The pre-commit hook (gitleaks) passed for M1 and M2, and `--no-verify` was not used. There was no push, rebase, reset, stash, branch checkout or force.

## Conflicts and how each was resolved

| Leg | File | Hunks | Rule (S1P-A3) | Result |
|---|---|---|---|---|
| 1 | `docs/architecture/02_ADRs/ADR-050-large-architecture-output-authority.md` | 1: Revision History | Keep every row, in date order. Rows with the same date go in the order they were made | PR 1's W2 and W3 amendment rows (both 2026-11-23), then PR 2's rev. 3 row (2026-11-23). No row was edited |
| 1 | `specs/374-large-architecture-pipeline-resilience/contracts/cli.md` | 1: the end of the file | Keep all three "Readings ruled at" sections | W2 and W3 (PR 1), then rev. 3 (PR 2). The earlier W1 section was already in place |
| 1 | `specs/374-large-architecture-pipeline-resilience/contracts/part-files.md` | 2 | In §3, keep each side's edit. After §4, PR 1's W2 readings, then PR 2's two payloads | (a) §3's table: PR 2's `units` row (the `threats-md` and `report` unit shapes) with PR 1's `refs` row (its W2 sentence). The unedited base row on each side was dropped. (b) After "The batch plan (§4), as T017's tests pin it for T018": "Readings ruled at W2 (2026-11-23, before T045 and T046)", then "Stage payload: `threats-md`" and "Stage payload: `report`" |
| 1 | `specs/374-large-architecture-pipeline-resilience/NEXT-SESSION.md` | 2: add/add | Take PR 2's side whole | PR 2's file (blob `31e9e3e`), which is the same blob as `origin/main`'s handoff |
| 2 | ADR-050 | 1: the end of the table | Keep both appended rows | Rev. 3's row (2026-11-23), then main's "Merged (PR 1)" row (2026-11-24). The status line auto-merged to main's text: line 3 equals `origin/main`'s |

## Auto-merged files, looked over (S1P-A3)

- **`tasks.md`.** The two PRs' hunks don't overlap.
  - Leg 1: PR 1's marks come in as 8 hunks (58 lines), all in Part 1 (Phases 1.1 to 1.8). The result differs from PR 1's head in 4 hunks (7 lines), all in Part 2, which are PR 2's own.
  - Leg 2: main's change from #465 (2 hunks, 3 lines) lands in Part 1.
  - At M2, `git diff origin/main M2 -- tasks.md` is those same 4 Part 2 hunks.
- **The generator.** `PARTS` keeps `"id-reuse": part_id_reuse_pr1_pr2`. That function calls PR 1's `part_id_reuse` and adds PR 2's `id_reuse_pr2_files`. The other twelve entries match PR 1's table.
- **`test_fixture_374.py`.** PR 2's +405 lines sit on PR 1's version, and no hunk overlaps.
- **The fixture tree (S1P-A5).** PR 1 added 71 files under `tests/scripts/fixtures/large_arch/` and PR 2 added 9. The two sets share no path, so there was nothing to hand-merge, and T085's "take PR 2's side" had nothing to apply to. The merged generator must still reproduce the union of 80 files byte for byte. That check runs the generator (H1), so it stays T103's first step, and it must land before the first push (condition 2).
- **Release-commit files.** The release commit `cb06251` changed 6 files: `.release-please-manifest.json`, `CHANGELOG.md`, `README.md`, `docs/guides/ISOLATED_OPERATION_TACHI.md`, `scripts/install.sh` and `scripts/tachi_parts.py`. PR 2 touches none of them, so leg 2 took all six from main. With #465's 5 files, that is main's 11.
- **`scripts/`.** PR 2 changes nothing there. After M1, `scripts/` equals `8111c5e`'s. The staged deletion of `scripts/generate-risk-scores-sarif.py` is PR 1's. PR 2 never touched that file. After M2, `scripts/` equals `origin/main`'s.

## Parity (S1P-A2 step 5, KB 18)

All list comparisons ran in Python, because zsh doesn't word-split.

| Check | Result |
|---|---|
| REF = `git diff --name-only 8111c5e M1` | 19 paths, equal to PR 2's own paths (`git diff --name-only 03a8f0d 9fd2266`) |
| `git diff --name-only origin/main M2` | 18 paths: REF without `NEXT-SESSION.md`, with nothing extra on either side |
| `-U0` +/− lines, per path | Equal for all 18 paths. ADR-050 and `tasks.md` match too, so there is no context-only difference to excuse |
| `scripts/` | `git diff 8111c5e M1 -- scripts/` is empty, and so is `git diff origin/main M2 -- scripts/` |
| `tests/` | 11 paths in both diffs, the same list, with equal +/− lines per path (explained below) |
| The 12 paths that only PR 2 touched | Byte-identical to `9fd2266` at M1 and at M2 |
| PR 2's edits in the 6 files that both PRs touched (`NEXT-SESSION.md` apart) | `git diff -U0 03a8f0d 9fd2266` and `git diff -U0 8111c5e M1` carry the same +/− lines for each. No edit of PR 2's or of PR 1's was lost or altered by a resolution |
| Conflict markers; `.orig` or `.rej` files | None |
| `git merge-base --is-ancestor origin/main HEAD` | Yes, and `git merge-base origin/main HEAD` is `47a4f95` |
| Trial merge of the branch into `origin/main` (`git merge-tree --write-tree`) | Clean. Its tree equals M2's (`6ae1713`) |
| GitHub's diff after a push (`git diff origin/main...HEAD`) | 18 files, +8546/−36 |

**The `tests/` paths PR 2 owns.** All 11 come from `544e4f1`, T148's chain-cap and id-reuse fixture cases: nine fixture files under `tests/scripts/fixtures/large_arch/` (`chain-cap/main/`, `id-reuse/pr2/` and `id-reuse/pr2-no-mark/`, three each), the generator and `test_fixture_374.py`. Main changed nothing under `tests/` after `8111c5e`, so both diffs hold PR 2's T148 change and nothing else.

**The numbers at this entry**, for T127's re-check if `origin/main` moves. The columns are +/− in `git diff 8111c5e M1` and in `git diff origin/main M2`, and the two are equal for every path. `S` is `specs/374-large-architecture-pipeline-resilience`, and `F` is `tests/scripts/fixtures/large_arch`.

| Path | +/− |
|---|---|
| `docs/architecture/02_ADRs/ADR-050-large-architecture-output-authority.md` | +146/−7 |
| `S/contracts/cli.md` | +22/−5 |
| `S/contracts/part-files.md` | +243/−10 |
| `S/contracts/threat-model-records.md` | +83/−5 |
| `S/tasks.md` | +7/−7 |
| `S/test-results/prestate-pr2.md` | +194/−0 |
| `S/test-results/tw-adr-pr2.md` | +43/−0 |
| `F/chain-cap/main/expected-outcomes.json` | +2108/−0 |
| `F/chain-cap/main/run/tachi-build/phase1/inventory.json` | +2736/−0 |
| `F/chain-cap/main/run/threats.md` | +577/−0 |
| `F/id-reuse/pr2-no-mark/baseline/threats.md` | +75/−0 |
| `F/id-reuse/pr2-no-mark/expected-outcomes.json` | +176/−0 |
| `F/id-reuse/pr2-no-mark/run/threats.md` | +457/−0 |
| `F/id-reuse/pr2/baseline/threats.md` | +77/−0 |
| `F/id-reuse/pr2/expected-outcomes.json` | +213/−0 |
| `F/id-reuse/pr2/run/threats.md` | +457/−0 |
| `tests/scripts/generate_large_arch_fixture.py` | +527/−2 |
| `tests/scripts/test_fixture_374.py` | +405/−0 |

`S/NEXT-SESSION.md` is the 19th path of REF. PR 2's copy is byte-identical to main's, so it drops out of the second diff.

## Departures (S1P-A8)

These are departures from documents that still say otherwise. The team-lead edits `tasks.md`, and `plan.md` gets a note.

1. **The W3-tip merge is retired.** T085 said to merge PR 1's committed W3 tip once its push (T039) is green. That tip, `f43440b`, is an ancestor of `8111c5e`, and 59 later commits changed 7 scripts by +834/−174 lines. They are `tachi-stage.py` (219), `tachi_parsers.py` (375), `tachi_parts.py` (136), `sarif_common.py` (52), and three smaller files. They are W2′'s own files, so a merge of the W3 tip would have started the lanes on stale versions (S1P-A1).
2. **`plan.md`, PR 2's Branch bullet and the first Risks bullet.** They say PR 2's branch is "rebased onto `origin/main`… once, after PR 1's squash". It is now a marker merge at W2′'s entry (this record), then plain merges at later wave boundaries. The "Superseded at `/aod.tasks`" note gains a line saying so. The spec's "merge `origin/main`" (§ The split) is met by the marker merge (F5).
3. **T085.** It changes in six ways:
   - the method is T127's two legs, not a one-leg merge;
   - the gate is PR 1's merge, rather than T039's push;
   - the record is this file;
   - the effort is about 0.2 d, from 0.1 d;
   - the fixture clause is no hand-merge, because the two sets are disjoint, and T103's regeneration and byte check land before the first push (S1P-A5);
   - the pre-state is re-based (the last section).
4. **T127.** It loses its first merge and the marker. It keeps S1P-A7's list:
   - a plain re-merge of `origin/main`, only if main moved since the last integration, with H11's fetch first;
   - KB 18's parity re-check against the current `origin/main`;
   - ADR-050 D16's coverage figures for PR 2's gated modules, and `tachi_parsers.py`'s ratchet (G3′);
   - the push and TW-CI, when W4′ has a commit that isn't records.

   "Against T084's totals" becomes "against the entry's totals". Its effort is about 0.1 to 0.15 d, from 0.25 d.
5. **T124, T125 and T126 (AR-T8's two clauses).** T124's re-run becomes conditional: it runs only if T127's re-merge changed a path outside this feature's records. T125 reviews `git diff origin/main...HEAD`. From this entry on, that is GitHub's diff, so "against PR 1's final head" no longer applies. T126's Step 7 scan and its Step 8 economy gate diff against `origin/main` too.
6. **The DoD's "(T001, T084)".** T084 is read as re-based at the entry.
7. **"Dependencies & Execution Order".** T085 waits for PR 1's merge, not for T039's push. "T127 merges `origin/main` after PR 1's squash" becomes "T085 merged it; T127 re-merges if main moved". W2′'s "First:" line gains the hoist (S1P-A14).
8. **H6.** If the entry push is taken, it is the one exception to one push per wave (S1P-A15, S1P-T11).
9. **Later integrations.** `47a4f95` is now an ancestor of the branch. So any later integration (TW-N3's merge, #396, a patch release) is a plain `git merge origin/main` with this parity check, and no second marker is needed (S1P-A2).

## Pre-state at the entry (S1P-A6)

T084's totals were taken at the cut line (`03a8f0d`), before PR 1's W2–W6 tests existed. At that line f374-offline ran 2,576 tests, and PR 1's W4 record shows 5,937. A reading against T084's totals can't see a regression in the later tests. The entry commit's literal totals (KB 15, KB 16) replace T084's as PR 2's pre-state, for T114, T098, T127, T138 and the DoD's item 2. They come from a scratch-clone census and from the entry push's CI (S1P-A15).

- **The integrated state T085 leaves:** M2, `bb0154b` (tree `6ae1713`). The orchestrator names the entry commit when it runs the census.
- **The reading rule stands:** a run regresses only if a node id that passes at the baseline fails later, or if a gate total drops. Skips are named, so that a new skip is visible. Only the baseline changes.

Totals: pending, filled by the orchestrator from the entry census
