# NEXT-SESSION: F-391 after session L (handoff H2)

**Written:** 2026-11-20, at the end of session L. L ran gate GL and W2 (T020). The record is `test-results/w2-live.md`.

**Next:** session S2b runs the rest of W3, then W4. It opens with T051.

## Branches, PRs, tips
| | Branch | Tip | PR |
|---|---|---|---|
| Part A | `391-isolated-auditable-operation` | code `3921857`; records after it, the newest being this H2 commit | #392 (draft) |
| Part B | `391-isolated-auditable-operation-part-b` | `fe5125a` (BX″) | #396 (draft, base = Part A) |

**CI:**
- Green on `7950141` (#392, 7/7) and on `fe5125a` (#396).
- Pushing H2 starts one more full run on #392 (records only). Check it before S2b's first code push.

**Worktrees:**
- The part-b worktree is still `<S2a scratchpad>/wt/391-part-b`. If it is gone, run `git worktree prune`, then `git worktree add <S2b scratchpad>/wt/391-part-b 391-isolated-auditable-operation-part-b`.
- Every commit is pushed.

## State
- **Tasks:** 40 of 52 done (L added T020).
- **Open, by wave:**
  - W3: T051, T021, T035, T041, T042, T043, T044.
  - W4: T045, T046, T048 (its W4 part).
  - Conditional: T047 (split path), T038b (after #364).
- **T040's W3 fix list:** X-4 runs with T021, and X-5 runs inside T043. All other items are done.

## Done in session L
- **Gate GL passed**, with Linux scoped to macOS by the maintainer (D1). The profile was re-extracted: 2,908 bytes, `43496fb7…`. The file form of `--settings` honours `autoMode`, also with `--setting-sources project,local`.
- **T020 ran on macOS 26.6.2 with Claude Code 2.1.330**, in auto mode, key-less and keyed, installed from `fe5125a`. Six sessions are archived with the B1 archiver.
- **Passed:**
  - the probe table and two added probes;
  - the planted classifier denial and the SEC-A macOS probes;
  - write confinement (tachi wrote only under `{out}`) and AR-2's risk-score half;
  - SC-B3, the mask, the Gemini CA trust and the offline render check;
  - auto mode with non-essential traffic off, the Manual-mode check and `--setting-sources` without `user`.
- **Unexpected egress denials:** 0.
- **Blocked:** Chromium cannot launch inside Claude Code's macOS sandbox (F1). There is no PDF report on macOS under the profile, and the custom `report-config.typ` and AR-2's report half were not exercised.
- **TW-A1:** 1 debug loop (F1), within budget.
- **Deviation from AD-12:** at the maintainer's instruction, Claude drove the sessions as real interactive TUIs in tmux. The maintainer stays accountable. T045 records it in `delivery.md`.

## What L changes for S2b
1. **T051 (G-B1R) will likely trip TW-B1.**
   - Attribution is clean in both measured archives: every dispatch is `recorded`, no histogram is empty, and pins and served models agree.
   - But the archiver did not detect the planted sandbox denials (network and proxy) or the classifier denial on 2.1.330 transcripts. It warned of "denial markers of an unrecognised kind" (F6).
   - That is TW-B1's undetected-planted-kind condition: B1 honest-stops, and B2 continues.
   - SBE-B1 runs the parse on the archives at the archiver's default destination. They are private; never copy them into the repo.
2. **T021 (DEVOPS-R)** folds the findings into the runbook:
   - F1–F5 and F8–F12 (the list is in `w2-live.md` §7);
   - §11 from `w2-live.md`;
   - the header stamped "Last validated" with macOS only, 2.1.330, auto mode;
   - the wrapper form as recorded.
   The F1 disposition (runbook §6, macOS and the report step) and F2/F3 (Keychain reach; the MCP resource tools outside `mcp__*`) need the architect before T021 writes them. X-4 runs with T021.
3. **T035:** TW-B4 governs. F6 bears on "denial parsing from the probe sample". The K1 archive holds every denial kind as planted: sandbox (P1–P3), permission rule (P4) and classifier (CL1).
4. **T044:** add the AD-12 deviation, F3 and F7 (architect), and the archiver's `DeprecationWarning` under Python 3.14 (B1 code; CI's 3.12 and 3.9 do not show it).
5. **T045:**
   - file the follow-ups listed at the end of `w2-live.md` §7 (the SARIF `informationUri` placeholder, risk-score nondeterminism, the reachability floor, the infographic agent going off-template);
   - file a Linux validation follow-up;
   - record the AD-12 deviation.

## Decisions S2a took, for T044 to check
- **X-7 went past the literal ruling.**
  - The ruling said "align the writer to the readers" and named `/`.
  - S2a also closed three more differences: a first character `_` or `+`, more than 128 characters, and accented letters under a UTF-8 locale.
  - `contracts/version-marker.md:5` already claims full alignment.
- **X-8:** `GIT_COMMITTER_*` never matched the name list. Its exclusion was kept so the pair stays alike.
- **An observation, not changed:** a bad `TACHI_MMDC_PUPPETEER_CONFIG` value ends the extractor with an uncaught `RuntimeError`. T044 may add a docstring line or a clean message.

## Records for `delivery.md` (T045)
- **G-B2** (team-lead record text): "TW-B2 not fired (T050, 2026-11-20, before session L). Remaining Part B work 0.66–0.83 d against 1.5. B1 0.64 d against 1.55. B2 0.49 d against 0.83. Conversion: 6.0 h of summed lane agent wall-clock per attention-day." The full rulings are local: `.aod/results/team-lead-t050-391.md` and `.aod/results/pm-t050-391.md`.
- **The TW-B2 monitoring log** (team-lead §5.1, condition 2): Part B's W3 and W4 agent wall-clock so far is 66.0 min against the 9.0 h re-open line. L added no Part B agent time. Keep logging per dispatch in S2b, and re-invoke the team-lead if new Part B work of 0.5 d or more appears.
- **W2 (L):**
  - TW-A1 not fired: 1 loop, about 4 hours.
  - The AD-12 deviation (Claude-driven sessions).
  - Claude Code moved from 2.1.328 (GL) to 2.1.330: the auto-updater ran in the one session without the profile.
  - The maintainer's user-scope additions (runbook §3) were applied for W2 and restored byte for byte.
- **SC-A3's push leg:** the first push to `main` after #392 merges is the guard's first push-leg run. `/aod.deliver` records its run id in `sc-a3-evidence.md`.
- **Stale checksum, outside 391:** `specs/029-agent-refactoring-right/baseline-checksums.txt:23`. Nothing reads it.
- **Leftovers for you:**
  - the local branch `391-sc-a3-evidence` (`git branch -D` is denied, R-8);
  - `.aod/revision-context.md` (untracked, deliberately not committed);
  - the W2 scratch material outside the repo: the scratch adopter, clones, run sheet and raw notes, plus the six archives at the archiver's default destination. All of it is private. Delete it after delivery if you no longer need it.
- **Carried from H1, unchanged:**
  - AD-13; the adapter copies' old `cp -r` hint;
  - #365 (the maestro-reference offset and the census);
  - PM FU-1..FU-3; AR-5's two follow-ups and the skills' guard;
  - the SARIF twins (1.7 and 1.8); the B1 deferrals L-3 and M-1;
  - the zsh SC-A4 path that skips on CI;
  - the 25 pre-existing Dependabot alerts.

## S2b plan
1. Re-check CI on both tips. Read `w2-live.md`.
2. **T051** (G-B1R): `tester` records and SBE-B1 runs the archiver's parse on each W2 archive, giving `test-results/tw-b1-w2.md`. Expect the TW-B1 ruling above. A failure honest-stops B1 (record in `delivery.md`); B2 continues.
3. **T021** (DEVOPS-R): runbook §11, the "Last validated" stamp and the wrapper form. Confirm the PM's two conditional §1 paragraphs against T020. **X-4** goes with it (SBE-D): ADR-049 D5's last sentence, D7's decode and Mitigation bullet 3, checked against the W2 record. The architect rules F1–F3 first.
4. **T035** after T051 and T021 (TW-B4 governs). **T041** (sweeps) and **T042** (snippet review) after T021.
5. **T043** on both tips, including **X-5**: Part A's installed-script modules under Python 3.9 (baseline 12 modules, 667 passed), and the zsh manual-loop cases recorded as passed. Write the full W3 gate to `test-results/wave-03/results.json` and `w3-gated-suite.md`.
6. **T044:** `code-reviewer`, then the architect, Part A first. Include the S2a decisions above and the L items under "What L changes" (point 4).
7. **W4:** T045, then T046 (TW-A2 split unless #364 merged; the hunk check excludes `specs/**`, `docs/product/**` and the system-design README); T048's W4 part; T047 and T038b as they apply; then `/aod.deliver`.

## Mechanics (from S1 and S2a)
- **Per-dispatch worktrees.** The orchestrator commits in each worktree with explicit paths, then cherry-picks onto Part A in the main tree, or onto part-b in the part-b worktree.
- **The #365 rule.** No pytest and no extractors in the main tree; use a scratch clone of the committed tip.
- **Paths:** `rm -rf` is denied even inside the scratchpad, so give each scratch clone a fresh path. A new file needs `git add -- <path>` before `git commit -- <path>`.
- **A push to either PR runs the full CI matrix,** even a records-only commit; the macOS pytest leg takes about 35 minutes.
- **A throwaway evidence PR targets `main`, not the Part A branch.** Path filters look at the PR's whole diff, so a PR against the Part A branch would run nothing for its green leg.

## Resume
- `claude "Resume F-391 /aod.build (branch 391-isolated-auditable-operation). S1 and S2a done; W2 live session recorded in test-results/w2-live.md. Read specs/391-isolated-auditable-operation/NEXT-SESSION.md, then build the rest of wave 3, starting with T051."`
