# NEXT-SESSION: F-391 after session S2b (handoff H3)

**Written:** 2026-11-20, at the end of build session S2b, which ran wave 3 (W3).

**Next:** session S2c runs W4: T045, then T048's W4 part and T046, then `/aod.deliver` on the split path. T047 and T038b come later.

## Branches, PRs, tips

| | Branch | Tip | PR |
|---|---|---|---|
| Part A | `391-isolated-auditable-operation` | `6ade384`; records after it, the newest being this H3 commit | #392 (draft) |
| Part B | `391-isolated-auditable-operation-part-b` | `3cc8294` (BX⁗⁗) | #396 (draft, base = Part A). It now carries **B2 only** |

**CI:** pushes at `6ade384` and `3cc8294` started full runs (the macOS pytest leg takes about 35 minutes). Check both are green before T046.

**Worktree:** part-b is still at S2a's scratchpad path, `<S2a scratchpad>/wt/391-part-b`. If it is gone, run `git worktree prune`, then `git worktree add <scratchpad>/wt/391-part-b 391-isolated-auditable-operation-part-b`. Every commit is pushed.

## State

- **Tasks:** 47 of 52 done.
- **Open:**
  - W4: T045, T046, and T048's W4 part.
  - Conditional: T047 (split path, after Part A squash-merges) and T038b (after #364).
- **Path:** #364 is still an open issue. TW-A2 therefore applies: **split path**.
  - Part A ships alone as `fix(391)`.
  - Part B (B2 only) waits for #364 and ships through T047 as its own `feat(391)`.

## What S2b did (W3)

1. **T051 (G-B1R): TW-B1 fired; B1 honest-stopped.**
   - The archiver attributed every dispatched agent: 13 instances, depths 1 to 3.
   - But on 2.1.330 it detected none of the planted sandbox or classifier denials, and 2 of 5 permission-rule refusals.
   - Records: `test-results/tw-b1-w2.md`, including the observed denial layout for `delivery.md`. T035 is honest-stopped.
   - **B1 left part-b** in seven delete-and-edit commits (`be2e890` to `bc943c6`; architect ruling, local: `.aod/results/architect-b1-stop-391.md`).
   - #396 now differs from Part A in 17 paths, all B2. The runbook and ADR-019 are identical to Part A's. The B1 work is preserved in history, last intact at `fe5125a`.
2. **T021 (runbook W3 completion).** It followed the architect's rulings W3-1 to W3-8 and W3-3a (local: `.aod/results/architect-w3-findings-391.md`).
   - F1: on macOS, `/tachi.security-report` is out of the claim for runs with diagrams; a by-hand build is given.
   - F2 and F7: §3 states that shell startup files, the Keychain and the messaging variables reach sandboxed commands.
   - F11: the validated wrapper form carries its disclosure, and an argument-free form is given for shared hosts.
   - The profile gains **ten deny rules**: AR-21 (eight built-in tools that reach past the sandbox) and AR-21a (`Workflow`, `Agent(isolation:*)`, because the Agent tool offers `isolation: "remote"` on 2.1.330). The deny list goes from 8 to 18, with no new key path. The contract test changed in the same commits.
3. **The re-check of the published profile passed** (R1 to R6 with R4a; `test-results/w3-recheck.md`).
   - It was key-less, Claude-driven in tmux at the maintainer's standing instruction (the AD-12 deviation again).
   - The runbook header carries the "re-check passes" form. The claim covers macOS only, without the report step on runs with diagrams.
4. **W2 record corrections** (`w2-live.md`):
   - K1 had 8 dispatches, not 9;
   - K2 held one unplanted pre-run refusal (a per-command host list). The PM ruled it the profile's designed refusal, so SC-001's denials clause is met with a recorded qualification (local: `.aod/results/pm-w3-k2-391.md`);
   - the Bash-families census;
   - what K2's helper scripts built.
5. **X-4 (ADR-049 D3, D5, D7, Mitigation) and W3-8 (§8.1, runbook §5 and §10)** landed.
6. **T041 sweeps** passed after one fix (FR-009: 13 runbook lines cited). Pattern A had 0 hits.
7. **T042 security review** cleared with findings. W3-H1 (the by-hand build runs project scripts outside the sandbox) and W3-M1 (the macOS `ps` statements) are fixed, with four lows.
8. **T043 gated suite** passed at `b71a0d7` and `f34e0ed`: 0 regressions, #365's six only.
9. **T044:** the code review returned APPROVED_WITH_CONCERNS (10 findings). The architect's checkpoint was CHANGES_REQUESTED, and its W3 list has landed on both branches:
   - CR-1: the guard refuses ambiguous frontmatter delimiters;
   - CR-2: the manual-loop marker line handles a nested copy;
   - CR-4 to CR-9;
   - A-1 to A-4;
   - W3-L6;
   - the PM's §3 sentence.

**G3:** the full T043 re-run on `6ade384` and `3cc8294` **passed**: 0 regressions, #365's six only; Part A 988 passed, part-b 1,121; X-5 706 and `py39-floor` 132 on 3.9.6 (`test-results/w3-gated-suite.md`, "Re-run on the final W3 tips"). T044 is `[x]`. CI: #396 green at `3cc8294`; #392 green at `6ade384` except the macOS leg, which was still running at handoff, and this H3 commit starts one more records-only run. Check both are green before T046.

## S2c plan (W4)

1. Check CI on both tips and confirm that G3 closed (see above).
2. **T045 (PM, Part A).**
   - **The CHANGELOG Unreleased entry:** neutral wording; one line on the `{out}`-under-cwd precondition for `/tachi.security-report --output-dir`; no archiver.
   - **The release notes.**
   - **`delivery.md` prep**, which must carry:
     - TW-B1 fired at T051: copy `tw-b1-w2.md` §2, and its §6 layout beside the W0′ topology at 2.1.328;
     - "B1: honest-stopped (TW-B1)";
     - "Part B: B2 built, awaiting #364 (#396)";
     - SC-006 and SC-007 not met, because B1 stopped;
     - the G-B2 record text and the TW-B2 monitoring log (below);
     - W2: TW-A1 not fired (1 loop); the AD-12 deviation, in W2 and in the W3 re-check; Claude Code 2.1.328→2.1.330; the user-scope additions restored;
     - SC-A3's push-leg note;
     - the pre-existing `senior-backend-engineer` dispatch defect (AD-13);
     - the C-9 correction of published copies;
     - the debt register (CF-P8);
     - the stale checksum outside 391 (`specs/029-…/baseline-checksums.txt:23`).
   - **Follow-ups to file** (run `export AOD_REPO=davidmatousek/tachi` first; dry-run the titles, because `create-issue.sh` overwrites phrase-matched open issues):
     - **The B1 follow-up**, with the content in `architect-b1-stop-391.md` §5. Fold in X-8, the 3.13+ `DeprecationWarning`, the `egress_observed` semantics, L-3 and M-1.
     - **From T044** (`architect-t044-391.md` §7): CR-3 with W3-L4 (the extractor's clean message for a bad `TACHI_MMDC_PUPPETEER_CONFIG`), CR-10, and a Python 3.9 CI leg for Part A's installed scripts (CR-4).
     - **The macOS report path under the profile** (F1). Separately and optionally, the public Chromium feature request, which is the maintainer's call.
     - **The `--restricted` launch** as a candidate (W3-3a).
     - **The infographic agent's departures:** off-template helper scripts, "Unknown Project" titles, every MAESTRO layer rated "High", and the per-command allowed-domain field (PM).
     - **Linux validation**, including the W3-L6 measurement as an acceptance item.
     - **The other W2 items:** the SARIF `informationUri` placeholder; risk-score nondeterminism; the reachability floor.
     - **The SARIF twins** 1.7 and 1.8 (L-5).
     - **Carried from H1 and H2:**
       - a guard check that command bodies dispatch only `tachi-*` agents with a §8 row;
       - the skills' `allowed-tools` guard;
       - AR-5's two follow-ups;
       - PM FU-1 to FU-3;
       - #365 (the maestro-reference offset and the census);
       - optional zsh CI coverage.
     - **The Part B landing tracker.**
   - **Reminder for `/aod.deliver`:** its system-design README append records the B1 stop in one line and regenerates `tests/fixtures/init-baseline-tree/` in the same commit (FR-021).
3. **T048's W4 part** (SBE-D, part-b worktree): the CHANGELOG's Part B lines, **B2 only**:
   - the installed version marker;
   - `tachi_version` stamped at Step 2.6;
   - schema 1.5 as additive (feature-detect the field; treat a pre-1.5 `schema_version` as declared, not ordinal).

   No line names an archiver or a manifest.
4. **T046 (DEVOPS-E, Part A), split path:**
   - (0) the final Wording sweep over the CHANGELOG entry, the release notes and both PRs' titles and bodies;
   - (1) `/aod.analyze` clean;
   - (2) `git diff --stat main...391-isolated-auditable-operation` lists no Part B-only path;
   - (3) the hunk grep returns 0;
   - (4) no tracked example image, PDF or SARIF baseline is in the diff;
   - (5) #392 titled `fix(391): …` and marked ready.

   The squash-merge and the release-please check belong to `/aod.deliver`. **Confirm with the maintainer before any merge.**
5. **T047 (split path)**, after Part A squash-merges:
   - In the part-b worktree, run `git merge origin/main`.
   - Expect conflicts on ADR-049, §8, the README, the developer guide, `INSTALL_MANIFEST.md` and the CHANGELOG. The runbook and ADR-019 no longer conflict.
   - Run the §3.9 B1-absence grep on `main...<part-b tip>`. It must print 0.
   - Retarget #396 to `main` and re-run the gated set.
   - Mark #396 ready only after #364. Run T038b if #364 has merged.

## Maintainer decisions (nothing outward-facing was done for these)

1. **Recommended:** a private sandbox-scope question to Anthropic, through the vulnerability-disclosure route and structure-only (architect W3-2, W3-4). Its questions:
   - the Keychain is reachable from sandboxed commands without an `allowMachLookup` entry;
   - the messaging socket and token are in sandboxed commands' environment;
   - optional docs questions: `Monitor` and `allowedDomains`; the MCP resource tools outside `mcp__*`; whether the proxy substitutes the key in request bodies (T042 W3-I4).
2. **A named ref at `fe5125a`** for the built B1 work: the architect recommends none, because the history and #396's refs keep it.
3. **The six private W2 archives:** keep them until the B1 follow-up re-records (recommended).
4. **Optional:**
   - the public Chromium feature request (F1);
   - an exit-code-only check of Claude Code's own Keychain item from a sandboxed command.

## Records for `delivery.md` (T045)

- **The TW-B2 monitoring log:**
  - Part B agent wall-clock in S2b was about 120 minutes: the T051 parse and record, the B1-stop ruling, half of each T043 run and of T044, and SBE-B2 and SBE-TB.
  - With S1 and S2a's 66.0, that is about 186 minutes, against the 9.0 h re-open line. No new Part B work of 0.5 d or more appeared, so the team-lead was not re-invoked.
  - The orchestrator ran the seven stop commits itself (the architect's verbatim edits; the T044 review checked them).
- **The G-B2 record** (team-lead text, H2): "TW-B2 not fired (T050, 2026-11-20, before session L). Remaining Part B work 0.66–0.83 d against 1.5. B1 0.64 d against 1.55. B2 0.49 d against 0.83. Conversion: 6.0 h of summed lane agent wall-clock per attention-day."
- **The AD-12 deviation, W3 part:** the re-check sessions were Claude-driven in tmux, as in W2.
- **Orchestrator deviations in S2b:**
  - the B1-stop edits on part-b (§3.1 to §3.8 of the ruling) were applied by the orchestrator from the architect's verbatim texts, with every post-check, rather than dispatched to the owners;
  - one D7 sentence of the architect's was corrected from the evidence (`architect-t044-391.md` §4 confirms it).

## Mechanics (from S1, S2a and S2b)

- **Per-dispatch rules.** Agents run no git. The orchestrator commits with explicit paths, in the main tree for Part A and in the part-b worktree for part-b. A new file needs `git add -- <path>` first.
- **The #365 rule.** No pytest and no extractors in the main tree; use a scratch clone of the committed tip, with `git -C <clone> log -1` checked.
- **The pre-commit hook stashes unstaged files** during a commit. Do not commit while an agent is writing in the same tree; wait for a quiet window.
- **`rm -rf` is denied**, even in a scratchpad. Give each scratch clone a fresh path. `git rm -- <paths>` is fine.
- **CI.** A push to either PR runs the full matrix (macOS about 35 minutes). A throwaway evidence PR targets `main`.
- **Private live-run kit** (outside the repo, never committed), under `~/.tachi/391-w2/`:
  - `bin/w3-launch.sh` and `bin/w3-tmux.py` (the published-profile launcher and tmux driver);
  - `session-profile.w3.json` (the 18-rule block);
  - `RECHECK-NOTES.md`;
  - `listings/R*.json`;
  - `t051/` (the T051 re-run archives and parse results).

## Leftovers for the maintainer

- The local branch `391-sc-a3-evidence` (`git branch -D` is denied, R-8).
- `.aod/revision-context.md` (untracked, deliberately not committed).
- The private W2 and W3 material:
  - `~/.tachi/391-w2/` (the scratch adopter with its `docs/security/w3-recheck/` run folder, clones, the run sheet, the notes and the kit above);
  - `~/.tachi/runs/adopter/` (the six W2 archives).

  All of it is private. Delete it after delivery, except the archives if the B1 follow-up needs them (decision 3).
- **Carried, unchanged:** AD-13; the adapter copies' old `cp -r` hint; the 25 pre-existing Dependabot alerts.

## Resume

- `claude "Resume F-391 /aod.build (branch 391-isolated-auditable-operation). S1, S2a and S2b done; W3 complete (G3 per H3). Read specs/391-isolated-auditable-operation/NEXT-SESSION.md, then build W4, starting with T045."`
