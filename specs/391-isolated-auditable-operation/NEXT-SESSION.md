# NEXT-SESSION: F-391 after build session S2c (handoff H4)

**Written:** 2026-11-21, at the end of build session S2c, which ran wave 4 (W4).

**Next:** `/aod.deliver` for Part A on the split path. The maintainer confirmed the merge on 2026-11-21, to run once CI is green on the final tip. After it: T047 (Part B, after the squash-merge) and T038b (after #364).

## Branches, PRs, tips

| | Branch | Tip | PR |
|---|---|---|---|
| Part A | `391-isolated-auditable-operation` | this H4 records commit; the last code commit is `97208fe` (EC-5) | #392, **ready for review**, titled `fix(391): isolated and auditable operation (Part A)` |
| Part B | `391-isolated-auditable-operation-part-b` | `923c802` (T048's Part B CHANGELOG entry) | #396 (draft, base = Part A). B2 only |

**CI:** check #392 on the H4 tip, and #396 at `923c802`, before the merge.

**Worktree:** part-b is still at S2a's scratchpad path (`git worktree list` shows it). If it is gone, run `git worktree prune`, then `git worktree add <scratchpad>/wt/391-part-b 391-isolated-auditable-operation-part-b`. Every commit is pushed.

## State

- **Tasks:** 50 of 52 done. Open: T047 (split path, after Part A squash-merges) and T038b (after #364). #364 is still open.
- **W4:**
  - **T045:** the CHANGELOG entry, the release notes and `delivery.md`. Follow-ups #399 to #415, then #416 and #417.
  - **T048's W4 part:** the Part B CHANGELOG entry, B2 only, at `923c802`, after BX `1763bbc`.
  - **T046:** the Wording sweep is clean; `/aod.analyze` is clean (5 low); no AD-14 Part B-only path; the hunk grep and baseline checks are 0. #392 is retitled and ready.
- **Build gates:**
  - **Step 5:** the architect returned APPROVED_WITH_CONCERNS (0 critical, 0 high), and its fix texts are applied.
  - **Step 6:** skipped, because no UI files changed.
  - **Step 7:** the security scan PASSED (`security-scan.md`), with one LOW, the build-mode symlink refusal (#416).
  - **Step 8:** the Economy Gate found 5 advisories (`economy-check.md`). EC-5 is fixed in `97208fe` (`test_write_confinement.py` 78 passed in a scratch clone), and EC-1 to EC-4 are #417.

## Maintainer decisions taken on 2026-11-21

1. **The merge:** run `/aod.deliver` after green CI.
2. **The fixture:** regenerate the init-baseline fixture's copy of the system-design README in the same commit as the README note (the plan's FR-021 rule), and comment on #345.
3. **CR-10:** file it as a public issue: #416.
4. **The Economy Gate:** fix EC-5 now and file EC-1 to EC-4: #417.

## Still open for the maintainer

- **Close #391 at Part A's delivery?** The PM recommends it, because #399 (B1) and #400 (the Part B landing) carry the rest.
- **Carried from H3:**
  - the private sandbox-scope question to Anthropic (recommended, structure-only);
  - no named ref at `fe5125a`;
  - keep the six W2 archives until #399 re-records;
  - the optional Chromium feature request;
  - C-9, correcting published copies of the old data-locality claim (`delivery.md`, "Maintainer action: C-9").

## `/aod.deliver` (split path)

- **The merge.** Squash-merge #392 under its `fix(391): …` title; the PR has many commits, so the PR title becomes the commit subject. Confirm that a release-please PR opens (v4.48.3 expected). If none opens, push a `fix(391)` marker commit.
- **The release notes.** The release's notes take the text of `release-notes.md`.
- **The system-design README.** Append F-7's note (the text is in `delivery.md`, "Reminder for /aod.deliver"). Regenerate the init-baseline fixture's copy in the same commit, and comment on #345.
- **SC-003.** Record the run id of the guard's first `push:[main]` run in `test-results/sc-a3-evidence.md` and in `delivery.md`.
- **The rest.** Fill `delivery.md`'s TBD fields. The architect's F-10 (18 paths) is already applied.

## T047 (after the squash-merge)

- In the part-b worktree, run `git merge origin/main` (no force push).
  - Conflicts are expected on ADR-049, §8, the README, the developer guide, `INSTALL_MANIFEST.md` and the CHANGELOG.
  - In the CHANGELOG, keep Part B's entry above Part A's.
- Run §3.9's B1-absence grep on `main...<part-b tip>`. It must print 0.
- Retarget #396 to `main`. Then:
  - re-run the gated set in a scratch clone;
  - run `/aod.analyze` and the Wording sweep over the PR text;
  - **run `/security` on part-b**, because Part A's scan did not cover B2's code.
- Mark #396 ready only after #364 merges, and run T038b if #364 has merged.
- `delivery.md` then records "Part B: merged", and #400 closes.

## Mechanics (from S1 to S2c)

- **Per-dispatch rules.** Agents run no git in the main tree. The orchestrator commits with explicit paths: in the main tree for Part A, and in the part-b worktree for part-b. A new file needs `git add -- <path>` first.
- **The #365 rule.** No pytest and no extractors in the main tree. Use a scratch clone of the committed tip, with `git -C <clone> log -1` checked.
- **The pre-commit hook stashes unstaged files** during a commit. Do not commit while an agent is writing in the same tree.
- **`rm -rf` is denied,** even in a scratchpad. Give each scratch clone a fresh path.
- **CI.** A push to either PR runs the full matrix; macOS takes about 35 minutes.
- **Issue filing.** Run `export AOD_REPO=davidmatousek/tachi` first. Dry-run each title against the open issues, because `create-issue.sh` overwrites a phrase match. Add type labels afterwards with `gh issue edit --add-label`.

## Leftovers for the maintainer

- The local branch `391-sc-a3-evidence`, and `.aod/revision-context.md` (untracked, deliberately not committed).
- The private W2 and W3 material under `~/.tachi/391-w2/` and `~/.tachi/runs/adopter/`. Delete it after delivery, except the archives while #399 may need them.
- **Carried, unchanged:** AD-13's adapter copies' old `cp -r` hint (#369); the 25 pre-existing Dependabot alerts.

## Resume

- `claude "Resume F-391 delivery (branch 391-isolated-auditable-operation). W4 complete (H4); the maintainer confirmed the merge on 2026-11-21. Read specs/391-isolated-auditable-operation/NEXT-SESSION.md, then run /aod.deliver once CI is green."`
