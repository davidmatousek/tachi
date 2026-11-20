# NEXT-SESSION: F-391 after build session S1 (handoff H1)

**Written:** 2026-11-20, at the end of S1. Build waves 1 (W0) and 2 (W1) are complete.

**Next:**
- **Session L:** you (the maintainer) run W2, the live validation (gate GL, then T020).
- **Session S2:** opens with T050, then W3 and W4.

## Branches, PRs, tips
| | Branch | Tip | PR |
|---|---|---|---|
| Part A | `391-isolated-auditable-operation` | `4fd4813` | #392 (draft) |
| Part B | `391-isolated-auditable-operation-part-b` | `270ddb5` (BX′: Part A merged in) | #396 (draft, base = Part A) |

**Worktrees** (all in the S1 session scratchpad; they will vanish when it is cleaned):
- For S2, run `git worktree prune`, then `git worktree add <S2 scratchpad>/wt/391-part-b 391-isolated-auditable-operation-part-b`.
- Every commit is pushed, so nothing lives only in a worktree.

## State
- **Tasks:** 37 of 52 done.
- **T048** is done for its W1 part; its W4 part (the CHANGELOG's Part B lines) is open.
- **Open, by wave:**
  - W2: T020 ([MANUAL]).
  - W3: T021, T030, T035, T041, T042, T043, T044, T050, T051.
  - W4: T045, T046, T048 (W4 part).
  - Conditional: T047 (split path), T038b (after #364).

**Gates:**
- G0: PASS.
- P0-B0: APPROVED_WITH_CONCERNS.
- W1 carve check: not triggered (T025 + T026 ≈ 75 min).
- **G1: PASS** (evidence below).
- BX and BX′: done.
- **T040 / P0: APPROVED_WITH_CONCERNS.** 7 PASS, 3 PASS with concern, 0 FAIL. W2 entry and Part B past W1 are approved. Must-fix items F-1..F-4 are all done (`4fd4813`, `20b28fa`/`8da464a`, `44d8ae0`). **W3 items X-1..X-9** are listed in `test-results/p0-architect-checkpoint.md`.

**Trip-wires:**
- TW-B1 passed at T002; re-confirmed at T051.
- TW-B3 not fired: parser rework about 10 min, no layout change.
- TW-A2: #364 is still open, so Part A ships alone as `fix(391)` unless #364 merges first.

## G1 evidence
**Scratch-clone gated sets vs the T003 pre-state** (`test-results/wave-02/results.json`):

| Tip | Set | Result |
|---|---|---|
| Part A `8273669` | `tachi-pytest`, 21 modules | 592 passed |
| | manifest-completeness | 17 |
| | extraction-fidelity | 255 |
| | report-posture + write-confinement | 63 |
| | guard `--self-test` | pass |
| | coverage attestation | 16 |
| part-b `7e64fd7` | `tachi-pytest`, 22 modules | 1203 passed |
| | `py39-floor` on real Python 3.9.6 | 942 passed |

The byte-identity suite fails on the same six #365 node ids at the same offsets on both tips.

**CI:**
- **#392 at `8273669`:** all green, incl. `tachi-pytest` run 44655803140 (both legs), and `tachi-permissions-verify` with the guard `--self-test`.
- **#396 at `8d390ce` (BX):** `tachi-pytest` run 44657883796, success, incl. `py39-floor` on `ubuntu-24.04`. Re-check CI on the later tips (`270ddb5` on part-b; `4fd4813` on Part A) before S2 work.

## Inputs for T050 (G-B2) and the TW-B2 rule
The v1.1 budgets are in attention-days (B1 1.03 d, B2 0.55 d; TW-B2 fires above 1.55 / 0.83 d, or with more than 1.5 d of Part B work remaining). The actuals below are **agent wall-clock**, run in parallel, and not directly comparable; the team-lead rules on the conversion.

| Lane | Work done in S1 | Agent wall-clock |
|---|---|---|
| B1 | T031+T032+schema 42 min; T034 review 31 min; fix pass 41 min; T033 tests 58 + 21 min; T033 wiring 37 min | ≈ 3.8 h |
| B2 | T036+T038a 40 min; T037 tests 18 min + wiring 11 min; T039 code 20 min, test 34 min, wiring 18 min; py39 fix 13 min; F-4 test 12 + wiring 11 min | ≈ 3.0 h |

- **T032 checkpoints** (TW-B3 watch, UTC 2026-11-19): T032.1 22:26, T032.2 22:29, T032.3 22:29. Rework: two small fixes, about 10 min.
- **Remaining Part B work:** T035 (0.20 d), T051 (0.05 d), T048 W4 lines, T047 and T038b (conditional), and the part-b X-items from T040. Per the plan's figures that is about 0.5 d, below the 1.5 d line.

## Gate GL: before T020 (you, the maintainer)
- **Install source: the part-b tip `270ddb5`** (B1 and B2 passed P0), so the SC-B3 live check runs. Record both SHAs (Part A `4fd4813`, part-b `270ddb5`).
- **Claude Code:** check `claude --version` (≥ v2.1.285; W0' ran 2.1.328) and the status-bar model before a measured run. A stale CLI once resolved the pins to older models. Check that auto mode is available.
- **Profile:**
  - **REGENERATE the pre-staged profile.** The architect's review (AR-15..AR-20) changed the block after T006, so the pre-staged `~/.tachi/391-w2/session-profile.json` (SHA-256 `e3fdf5bf…`) is STALE. Extract the block from the runbook's `<!-- BEGIN/END TACHI SESSION PROFILE -->` markers. The new block is SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`, 2908 bytes. `test-results/profile-prestage.md` has the extraction recipe.
  - Check the `claude --settings <file> auto-mode config` output against `profile-prestage.md`. Whether a *file* passed to `--settings` honours `autoMode` is undocumented, so use the recorded fail-closed comparison recipe (inline JSON is the fallback).
- **Key and retention:** confirm the Gemini key item in the secret store by name only; never print it. Confirm `cleanupPeriodDays` is not lowered in any settings scope.
- **Linux:** a Linux VM for the Linux/WSL2 leg, or the platform claim is scoped (R-4).
- **Budget:** TW-A1 allows at most 3 debug loops or 1.0 d.

## T020 checklist additions from this session (beyond tasks.md T020)
- The runbook's §4 probe table, including AR-18's proxied-`curl` strictAllowlist probe and the Linux seccomp step.
- T049's `/proc` probes, key-less configuration only, with a non-secret dummy variable (`test-results/security-a.md`).
- AR-2: one write listing with `--output-dir` set differently from the input directory (risk-scorer).
- The write listing per configuration must show nothing under `scripts/__pycache__/` (AR-14) and nothing under `templates/tachi/`.
- **Archiving:** archive each session from a plain shell under the same secret-injection wrapper, with `python3 -I -B scripts/archive-run-transcripts.py …`. Keep the raw notes private.
- **H2:** a curated, structure-only `test-results/w2-live.md`.

## S2 plan (after H2)
1. **T050 first:** the `team-lead` ruling on TW-B2 from the table above. The PM rules on the lane clause.
2. **W3:**
   - T051 (G-B1R), then T035 (recorded fixture; TW-B4);
   - T021 (runbook §11, the "Last validated" stamp, the wrapper form; confirm the PM's two conditional §1 paragraphs against T020);
   - T030 (SC-A3 evidence on a throwaway branch; `git branch -D` is denied, so leave the local branch);
   - T041 (sweeps), T042 (snippet review), T043 (gated suites, both tips), T044 (code review, then the architect);
   - plus T040's X-1..X-9.
3. **W4:** T045, then T046 (TW-A2 split unless #364 merged; the hunk check excludes `specs/**`, `docs/product/**` and the system-design README); T048's W4 part; T047/T038b as applicable; then `/aod.deliver`.

## Mechanics used in S1 (deviations from agent-assignments.md, with reasons)
- **Per-dispatch worktrees.** Agents that edit tracked files worked in their own detached worktree at the branch tip. The orchestrator committed there with explicit paths and cherry-picked: onto Part A in the main tree, onto part-b in the part-b worktree. Reason: pre-commit stashes unstaged changes during a commit, so a concurrent agent write could be lost. Cherry-pick runs no hook.
- **Combined writers:**
  - T010 was written with T023 by SBE-E (one writer for `CLAUDE_PERMISSIONS.md`).
  - The AR-14 follow-on was done by one SBE-D+TA writer.
  - F-1 and F-2 were one writer, because both touch `cli-contracts.md`.
- **T006's doc research** was done by DEVOPS-R with citations.
- **T048:** the README and developer-guide marker lines went in one commit, because `test_manual_install_loop` is red between the two files.
- **`py39-floor` is a separate job pinned to `ubuntu-24.04`, not `ubuntu-latest`.** `ubuntu-latest` is now 26.04, and `actions/setup-python` has no Python 3.9 build for it (`7e64fd7`; T040 ratified it). Expiry: when `ubuntu-24.04` is retired (no date announced). The orchestrator corrected the job's display name to match.
- **The Bash tool is zsh,** so an unquoted `$VAR` holding a list is not split. Use explicit lists or `${=VAR}`.

## Follow-ups and records for `delivery.md` (T045)
- **AD-13:** a pre-existing defect. `/tachi.security-report` dispatched `senior-backend-engineer`; fixed in `c068ddc`.
- **Adapter copies:** `adapters/claude-code/commands/tachi.{threat-model,risk-score,infographic}.md` still print the old `cp -r` hint (#369's adapter roster).
- **#365:**
  - maestro-reference's first divergence moved from 828878 to 52 (page count 86 → 88) after F-362 T024, masked by the red. Worth a comment on #365; that is outward-facing, so the maintainer decides.
  - Census: 35 out-of-gate failures and errors at `46aec8d` (`wave-01/census-failing.txt`).
- **PM (T005):**
  - FU-1 "Check the Gemini infographic request against its documented field list before sending".
  - FU-2 "Executive-architecture callouts send mitigation text when a finding's threat text is empty".
  - FU-3 "Give every infographic placeholder a defined source and send only what each template draws".
- **Guards:**
  - AR-5: two follow-ups on `Agent` transitivity (spawning restriction; a guard check that command bodies dispatch only `tachi-*` agents with a §8 row).
  - The skills' `allowed-tools`/`model` guard (ADR-049 limitation 1).
- **SARIF:** the agentic-app sample-report twin says 1.7 while its input says 1.4; the consumer-agent-app twin says "1.8" (the L-5 list).
- **Deferred:**
  - B1 deferrals per T040: L-3 (a path token rule) and M-1 (a long host-label cap).
  - The guard `--self-test` exit-2 edge case.
  - The untested `semanticVersion` sourcing.
  - The four stale docs describing `report-posture`.
  - T043's stale "18 modules": now 21 on Part A, and 24 merged.
- **CI coverage:** the zsh SC-A4 path skips on CI's Ubuntu images; it is covered locally on macOS only.
- **Dependabot:** pushes report 25 Dependabot alerts (5 critical) on the default branch. Pre-existing and outside this feature.
- `.aod/revision-context.md` is a stale untracked leftover from the tasks-revision loop. It is deliberately not committed.

## Resume
- **After W2:** `claude "Resume F-391 /aod.build (branch 391-isolated-auditable-operation). S1 done (waves 1-2); W2 live session recorded in test-results/w2-live.md. Read specs/391-isolated-auditable-operation/NEXT-SESSION.md, run T050, then build wave 3."`
