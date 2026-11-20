# NEXT-SESSION: F-391 after build session S2a (handoff H1b)

**Written:** 2026-11-20, at the end of S2a. S2a was a build session that ran before session L. It did the parts of build wave 3 (W3) that need no live session. W2 (T020) has **not** run.

**Next:**
- **Session L:** you (the maintainer) run W2, the live validation (gate GL, then T020). Install from the new part-b tip (see GL).
- **Session S2b:** the rest of W3, then W4. It opens with T051.

## Branches, PRs, tips
| | Branch | Tip | PR |
|---|---|---|---|
| Part A | `391-isolated-auditable-operation` | code `3921857`; records after it | #392 (draft) |
| Part B | `391-isolated-auditable-operation-part-b` | `fe5125a` (BX″: Part A at `ff5da27` merged in) | #396 (draft, base = Part A) |

**CI:** green on every S2a tip.
- #392 at `3921857` (code) and at `ff5da27` (records): all seven workflows, including `tachi-pytest` run 44754342030 (both legs) and `tachi-permissions-verify` with the guard `--self-test`.
- #396 at `fe5125a`: `tachi-pytest` run 44754343822, including `py39-floor` on `ubuntu-24.04`, plus install fidelity, mmdc preflight and permissions-verify.
- Pushing this handoff starts one more full run on #392. Check it before S2b's work.

**Worktrees** (in the S2a session scratchpad; they vanish when it is cleaned):
- The part-b worktree is `<S2a scratchpad>/wt/391-part-b`. S2a moved it there from S1's scratchpad with `git worktree move`, because `git worktree add` refuses a branch that another worktree holds. For S2b: if it still exists, move it again; otherwise run `git worktree prune`, then `git worktree add <S2b scratchpad>/wt/391-part-b 391-isolated-auditable-operation-part-b`.
- Every commit is pushed, so nothing lives only in a worktree.

## State
- **Tasks:** 39 of 52 done (S2a added T030 and T050).
- **Open, by wave:**
  - W2: T020 ([MANUAL]).
  - W3: T051, T021, T035, T041, T042, T043, T044.
  - W4: T045, T046, T048 (its W4 part: the CHANGELOG's Part B lines).
  - Conditional: T047 (split path), T038b (after #364).
- **T040's W3 fix list:** X-1, X-2, X-3, X-6, X-7, X-8 and X-9 are done (table below). X-4 runs with T021, and X-5 runs inside T043.

## Done in S2a
| Item | Result | Commit |
|---|---|---|
| T050 (G-B2) | TW-B2 **not fired**; Part B proceeds; nothing deferred. The PM rules the lane clause per lane (not exercised). Record text below | `eed5650` |
| T030 (SC-A3) | Throwaway PR #398 against `main`: adding `WebFetch` to `tachi-spoofing` turned the guard, install fidelity (SC-A4) and pytest red; the revert turned all seven workflows green. Closed unmerged; remote branch deleted | `ff5da27` (`test-results/sc-a3-evidence.md`) |
| X-1 | `test_write_confinement.py` pins `TACHI_MMDC_PUPPETEER_CONFIG`: unset, valid, and four bad values at both mmdc call sites. 69 passed on 3.12 and 3.9.6 | `99b81ff` |
| X-2 | The guard's `--self-test` reports an already-red mutation as drift (exit 1), not infra; M1 targets only agents with a §8 row; `--json` gains `already_red` per mutation. 154 passed on 3.12 and 3.9.6; the live tree's output is unchanged | `3921857` |
| X-3 | The four `report-posture` doc lines name `test_write_confinement.py` | `41c998e` |
| X-6 | Three tests of the SARIF generator's `semanticVersion` sourcing | `8e7b4c3` (part-b) |
| X-7 | The installer's marker filter now equals the readers' rule in full, not only for `/` (see below) | `ec12218` (part-b) |
| X-8 | The archiver's secret scan excludes `GIT_AUTHOR_*`, `GIT_COMMITTER_*` and `XAUTHORITY` by name; `AUTH` itself is not loosened. `schemas/run-manifest.yaml` and `data-model.md` list the exclusions | `c46b6a8` (part-b), `992f01a` |
| X-9 | `schemas/output.yaml`'s header says the generator reads the input's `schema_version` first | `0d9e4a1` (part-b) |
| BX″ | Part A merged into part-b, cleanly | `fe5125a` |
| Records | T043's module count is 21 on Part A and 24 on part-b (P0 row 14), in tasks.md and agent-assignments.md | `eed5650` |

**Scratch-clone runs** (details in `test-results/wave-03/results-part1.json`):
- Part A `3921857`: guard `--self-test` exit 0 (3.12, 3.9.6); guard, profile and manifest modules 358 passed; report-posture and write confinement with Typst 75 passed; those plus the guard module on 3.9.6, 229 passed.
- part-b `fe5125a`: guard exit 0; Part B modules 959 passed (3.12), and 957 passed with 2 pre-existing skips (3.9.6); Part A modules 358; report-posture 75; installer suites 74.

## Decisions S2a took, for T044 to check
- **X-7 went past the literal ruling.** The ruling said "align the writer to the readers" and named `/`, the one difference the architect had seen. The writer agent found three more: a first character `_` or `+`, more than 128 characters, and accented letters under a UTF-8 locale through the bracket ranges. `contracts/version-marker.md:5` already claims full alignment, so S2a closed all of them; the contract text stands. The filter spells out the letters and digits. It agrees with the readers on 7,269 candidates under `/bin/bash` 3.2.57 in the C locale and in every UTF-8 locale on the build Mac. The case covers `rel/v1.0.0`, `_x`, `+x`, a 129-character tag and `vé1`, plus a 128-character control.
- **X-8:** `GIT_COMMITTER_*` never matched the name list, so its exclusion has no effect today. It was kept, as ruled, so the pair stays alike.
- **An observation, not changed:** a bad `TACHI_MMDC_PUPPETEER_CONFIG` value ends the extractor with an uncaught `RuntimeError` (a traceback, exit 1). That is the mmdc preflight's existing channel, and the contract says only "fails loud". The extractor's docstring lists exit 1 only for "missing required artifact". T044 may take a docstring line or a clean message.

## Records for `delivery.md` (T045)
- **G-B2** (team-lead record text): "TW-B2 not fired (T050, 2026-11-20, before session L). Remaining Part B work 0.66–0.83 d against 1.5. B1 0.64 d against 1.55. B2 0.49 d against 0.83. Conversion: 6.0 h of summed lane agent wall-clock per attention-day." The full ruling is local: `.aod/results/team-lead-t050-391.md`; the PM's is `.aod/results/pm-t050-391.md`.
- **The TW-B2 monitoring log** (team-lead §5.1, condition 2). Part B's W3 agent wall-clock so far:
  - B2 writer (X-7, X-9; three passes): 38.9 min;
  - B1 writer (X-8): 14.2 min;
  - TB (X-6): 12.9 min.

  Part B's W3 and W4 total is 66.0 min against the 9.0 h re-open line. The B2 lane plus TB is 51.8 min against B2's 2.0 h headroom. Keep logging per dispatch in S2b. The team-lead is re-invoked if new Part B work of 0.5 d or more appears, for example from H2 or a W3 review.
- **SC-A3's push leg:** the first push to `main` after #392 merges is the first push-leg run of the guard. `/aod.deliver` records its run id in `sc-a3-evidence.md`.
- **Stale checksum, outside 391:** `specs/029-agent-refactoring-right/baseline-checksums.txt:23` holds an old SHA-256 of `schemas/output.yaml`. Nothing reads it, and it was not touched.
- **Leftovers for you:**
  - the local branch `391-sc-a3-evidence` (`git branch -D` is denied, R-8);
  - `.aod/revision-context.md`, a stale untracked leftover from the tasks loop, deliberately not committed.
- **Carried from H1, unchanged:** AD-13; the adapter copies' old `cp -r` hint; #365 (the maestro-reference offset and the census); PM FU-1..FU-3; AR-5's two follow-ups and the skills' guard; the SARIF twins (1.7 and 1.8); the B1 deferrals L-3 and M-1; the zsh SC-A4 path that skips on CI; the 25 pre-existing Dependabot alerts.
- **H1's other deferred items are closed:** the guard's exit-2 edge case (X-2), the untested `semanticVersion` sourcing (X-6), the four stale `report-posture` docs (X-3) and T043's module count.

## Gate GL: before T020 (you, the maintainer)
- **Install source: the part-b tip `fe5125a`.** It carries X-7 (the marker filter, which SC-B3's field check reads) and X-8 (the archiver's name scan, which archiving uses), so L validates the code that ships (team-lead §5.3). #396 is green on `fe5125a` (run 44754343822, including `py39-floor`). If a later push moves the part-b tip, install the new tip only once #396 is green on it. Record the SHAs: part-b `fe5125a`, Part A code `3921857`.
- **Claude Code:** `claude --version` (≥ v2.1.285; W0' ran 2.1.328) and the status-bar model before a measured run. Check that auto mode is available.
- **Profile:** S2a did not touch the runbook, so H1's instruction holds. **Regenerate** the pre-staged profile from the runbook's `<!-- BEGIN/END TACHI SESSION PROFILE -->` block: SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`, 2,908 bytes (`test-results/profile-prestage.md` has the recipe). The copy at `~/.tachi/391-w2/session-profile.json` (`e3fdf5bf…`) is stale. Check `claude --settings <file> auto-mode config` with the recorded fail-closed comparison; inline JSON is the fallback.
- **Key and retention:** confirm the Gemini key item by name only; never print it. Confirm `cleanupPeriodDays` is not lowered in any scope.
- **Linux:** a Linux VM for the Linux/WSL2 leg, or the platform claim is scoped (R-4).
- **Budget:** TW-A1 allows at most 3 debug loops or 1.0 d.

## T020 checklist additions (carried from H1)
- The runbook's §4 probe table, including AR-18's proxied-`curl` strictAllowlist probe and the Linux seccomp step.
- T049's `/proc` probes, in the key-less configuration only, with a non-secret dummy variable (`test-results/security-a.md`).
- AR-2: one write listing with `--output-dir` set differently from the input directory (risk-scorer).
- The write listing for each configuration shows nothing under `scripts/__pycache__/` (AR-14) and nothing under `templates/tachi/`.
- **Archiving:** archive each session from a plain shell under the same secret-injection wrapper, with `python3 -I -B scripts/archive-run-transcripts.py …`. Keep the raw notes private.
- **H2:** a curated, structure-only `test-results/w2-live.md`.

## S2b plan (after H2)
1. Re-check CI on both tips. Read `w2-live.md`.
2. **T051** (G-B1R): `tester` records, SBE-B1 runs the archiver on each W2 archive → `test-results/tw-b1-w2.md`. A failure honest-stops B1 (record in `delivery.md`); B2 continues.
3. **T021** (DEVOPS-R): runbook §11, the "Last validated" stamp, the wrapper form; confirm the PM's two conditional §1 paragraphs against T020. **X-4** with it (SBE-D): ADR-049 D5's last sentence, D7's decode and Mitigation bullet 3 against the W2 record.
4. **T035** after T051 and T021 (TW-B4 governs). **T041** (sweeps) and **T042** (snippet review) after T021.
5. **T043** on both tips, including **X-5**: Part A's installed-script modules under Python 3.9 (baseline 12 modules, 667 passed) and the zsh manual-loop cases recorded as passed. Write the full W3 gate to `test-results/wave-03/results.json` and `w3-gated-suite.md`.
6. **T044:** `code-reviewer`, then the architect, Part A first. Include the three S2a decisions above.
7. **W4:** T045, then T046 (TW-A2 split unless #364 merged; the hunk check excludes `specs/**`, `docs/product/**` and the system-design README); T048's W4 part; T047 and T038b as they apply; then `/aod.deliver`.

## Mechanics used in S2a (deviations from agent-assignments.md, with reasons)
- **Per-dispatch worktrees, as in S1.** The orchestrator committed in each worktree with explicit paths and cherry-picked onto Part A in the main tree, or onto part-b in the part-b worktree.
- **The orchestrator wrote three small pieces itself:**
  - X-3's four one-line doc edits (assigned to DEVOPS-E);
  - T030's git and `gh` steps, because agents run no git;
  - the `run-manifest.yaml` sentence in the X-8 commit (the writer's brief excluded docs).
- **T030's PR base was `main`, not the Part A branch.** Path-filtered `pull_request` workflows look at the PR's whole diff. Against the Part A branch the reverted PR would have had none, so no workflow would have run for the green leg.
- **Combined writers:** X-2 (SBE-E with SBE-TA), X-7 + X-9 (SBE-B2 with SBE-TB), X-8 (SBE-B1 with SBE-TB).
- **`rm -rf` is denied even inside the scratchpad.** Give each scratch clone a fresh path.
- **A new file needs `git add -- <path>` before `git commit -- <path>`.**
- **A push to either PR runs the full CI matrix.** The path filters look at the PR's whole diff against its base, so even a records-only commit triggers a run, and the macOS pytest leg takes about 35 minutes.

## Resume
- **After L:** `claude "Resume F-391 /aod.build (branch 391-isolated-auditable-operation). S1 and S2a done; W2 live session recorded in test-results/w2-live.md. Read specs/391-isolated-auditable-operation/NEXT-SESSION.md, then build the rest of wave 3, starting with T051."`
