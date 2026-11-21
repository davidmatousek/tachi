# NEXT-SESSION: F-391 after v4.48.3 and #345 (handoff H6)

**Written:** 2026-11-21, after H5, by the session that worked through the maintainer's leftover list.

**State:** Part A is delivered and released as v4.48.3, and #391 is closed. Part B (#396, B2 only) is based on `main`, with CI green at `51eaa5c`. It waits for #364, which is still at `stage:discover`. #345 is settled on `main` (#419).

## What happened after H5

- **v4.48.3.** #418 squash-merged as `b1c3369`; the release was published at 2026-11-21T20:57:53Z.
- **#396 CI at `51eaa5c`:** 10 of 10 green, both `tachi pytest` legs included.
- **#345.** Decision: the init.sh baseline does not cover `CHANGELOG.md`. It is a target only because a prose entry quotes a placeholder (line 421), and release-please rewrites it in release PRs, which run no CI. PR #419 excludes it in `regenerate-baseline.sh`, regenerates the fixture (62 targets to 61; the other 61 byte-identical) and removes the `xfail` marker. Gated set in a scratch clone of `b231d39`: 620 passed, 1 skipped (the TTY case).
- **C-9: closed by the maintainer's decision.** The article was never published. The old claim's published copies are two LinkedIn texts, the 2026-05-29 post and the tachi entry in the profile's Projects section, and the maintainer leaves them as they are (`delivery.md`, C-9).
- **Local leftovers.** The branch `391-sc-a3-evidence` and `.aod/revision-context.md` are deleted. `~/.tachi/391-w2/` is left for the maintainer, because this environment denies the agent `rm -rf`.

## What happened in the delivery session (H5)

- **`/aod.deliver` for Part A.** #392 squash-merged to `main` as `e83ca6b` (2026-11-21T18:35:56Z). release-please opened #418 (v4.48.3); it is open for the maintainer. CI at merge: every push-leg workflow green (`tachi permissions-verify` 44936411660, the SC-003 push leg; `tachi pytest` 44936411639, both legs; `tachi install fidelity` 44936411674; `tachi catalog-drift` 44936411675). Closure commit `7ae5e35`: the three documentation agents' updates (product 3 files, architecture 3, devops 2), KB Entry 25, the system-design README's F-7 status note with `tests/fixtures/init-baseline-tree/` regenerated in the same commit (62 targets, 17 changed, 8 added; `test_personalized_tree_bytes_match_baseline` XPASS in a scratch clone; #345 told), the SC-003 push-leg record, BACKLOG.md. CI-record commit `0b54bb5`. #391 closed at `stage:done` on the PM's recommendation, with the metrics comment. The delivery lock is released.
- **The stacked PR.** `gh pr merge --squash --delete-branch` on Part A closed #396, and GitHub refuses to retarget or reopen a closed PR whose base is gone. Recovery: the ref pushed back at `1b8f0ac`, #396 reopened, retargeted to `main`, the ref deleted again; the PR body's Base line updated. KB Entry 25 records the mechanic.
- **T047 merge phase**, in the part-b worktree: `git merge origin/main` → `644f12f`. 16 conflicts: 13 files that carry no Part B change took `main`'s version (checked: part-b equals the Part B base `107c0a4` for each); ADR-049 and `CLAUDE_PERMISSIONS.md` took part-b's (checked: `main` equals that base for both); the CHANGELOG was hand-merged, the Part B entry above Part A's, purely additive (52 lines, equal to the Part B block). Checks: `git diff origin/main HEAD` names exactly the 18 Part B paths and every patch is byte-identical to `107c0a4..923c802`; B1 files 0 and B1 tokens 0; Wording Pattern A 0 and Pattern B 0 over the diff and over #396's text. Pushed.
- **`/security` on part-b** (B2 scope: 5 code files): PASSED, 0 findings, SCA skipped (no manifest changed). Report `specs/391-isolated-auditable-operation/security-scan-part-b.md`, scan-log entry (chain verified against the Part A entry), SARIF `.security/reports/644f12f49bbc.sarif`. Commit `51eaa5c`, pushed.
- **Gated set** in a scratch clone of `644f12f`: guard `--self-test` exit 0; the 23-module run list plus the install-fidelity modules and the coverage attestation: 1124 passed, 1 skipped (the TTY case), 1 xfailed (`test_personalized_tree_bytes_match_baseline`: the Part B CHANGELOG entry re-stales the fixture on part-b, because `CHANGELOG.md` is a substitution target through a literal placeholder at its line 421; #345 knows); `py39-floor` 132 passed, 1 skipped on Python 3.9.6; the clone stayed clean.
- **`/aod.analyze`** (the T047 step): clean. 0 critical, 0 high, 1 medium (DoD step 1 reads "released", and v4.48.3 is published only when #418 merges), 7 low, all records-level.
- **CI on #396 at `51eaa5c`:** 8 of 10 checks green at this handoff; the two `tachi pytest` legs were still running (`gh pr checks 396`).

## What remains

| Item | Owner | When |
|---|---|---|
| T038b: `examples/agentic-app/threats.md:2` "1.7" and `examples/consumer-agent-app/sample-report/threats.md:2` "1.8" → "1.4", frontmatter-only, measured first in a scratch clone; the SARIF twin's "1.8" is #413 | SBE-B2 | after #364 merges |
| Merge `origin/main` into part-b first. It brings #419 without conflicts (no shared paths), and the init-baseline test then passes on part-b, because Part B's only substitution target is `CHANGELOG.md`, now excluded. Then mark #396 ready. After its squash-merge, confirm the release-please PR (`feat(391)`, a minor), record "Part B: merged" with the PR number in `delivery.md`, and close #400 | DEVOPS-E + product-manager | after #364 |
| Delete the private W2 and W3 material under `~/.tachi/391-w2/`; keep the six archives under `~/.tachi/runs/adopter/` while #399 may need them | maintainer | any time |

## Mechanics

- **part-b worktree:** `<scratchpad of the S2a session>/wt/391-part-b` (`git worktree list` shows it), branch `391-isolated-auditable-operation-part-b` at `51eaa5c`, clean and pushed. If it is gone: `git worktree prune`, then `git worktree add <scratchpad>/wt/391-part-b 391-isolated-auditable-operation-part-b`.
- `main` has moved past `0b54bb5`: the H5 handoff commit, v4.48.3 (`b1c3369`), #419 and this handoff. part-b contains `main` up to `0b54bb5`; spec, plan and tasks are identical on both branches.
- #345 is settled on `main` by #419: `CHANGELOG.md` is out of the init.sh baseline and the `xfail` marker is gone. part-b keeps the marker and the old fixture until it merges `origin/main`, so #396 reports the test as XFAIL until then. Do not regenerate the fixture on part-b; the merge brings #419's.
- With the marker gone, an edit to a placeholder-bearing file needs a same-commit regen (`tests/fixtures/regenerate-baseline.sh`). That includes `docs/INSTITUTIONAL_KNOWLEDGE.md`, `docs/devops/*.md` and the system-design README at `/aod.deliver`. Those paths do not trigger `tachi pytest`, so a missed regen surfaces at the next run that does.
- The #365 rule (no pytest and no extractors in the main tree; scratch clones of the committed tip), explicit-path commits and the pre-commit stash hazard still apply.
- Stacked PRs: retarget the dependent PR to `main` before deleting its base branch (KB Entry 25, "How to apply").
- The `/aod.deliver` lock is keyed by the branch name at acquisition; a run that starts on `main` after the merge must hold `FEATURE=391-isolated-auditable-operation` in context for the release.

## Resume

- `claude "Resume F-391 Part B (branch 391-isolated-auditable-operation-part-b, PR #396). Read specs/391-isolated-auditable-operation/NEXT-SESSION.md (H6). If #364 has merged: merge origin/main into part-b, run T038b in the part-b worktree, re-run the gated set in a scratch clone, mark #396 ready, and after the merge confirm its release-please PR and record 'Part B: merged' in delivery.md."`
