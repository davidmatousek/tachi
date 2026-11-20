# NEXT-SESSION: F-391, build session S1 (interim handoff H1a, mid-W1)

**Written:** 2026-11-19, during build wave 2 (W1); refreshed later the same day. Superseded by H1 at the end of S1.

## Where things stand (refreshed late in W1)
- **Part A** `391-isolated-auditable-operation`: tip `3da1ec4` or later, pushed. PR #392 (draft).
- **Part B** `391-isolated-auditable-operation-part-b`: tip `ceea019`, pushed. Draft PR #396 (base = Part A). It holds:
  - T036 `b4888e9`; T038a `df37b4b`;
  - T031 `093be0a`; T032 (with the schema doc) `f9b5c0a`;
  - T039 code `f76e238`; T037 with its wiring and the `py39-floor` job `ceea019`.
- **Tasks:** 24 of 52 done:
  - Setup and W0: T001–T003.
  - Foundational: T004–T006.
  - US1: T007–T011.
  - US2 and US3 so far: T012–T014, T019, T022–T024.
  - Part B so far: T031, T032, T036, T037, T038a.
  - SEC-A: T049.
  - **T015 is committed (`1be9716`) but stays open** until the AR-14 follow-on lands.
- **Gates:** P0-B0 is APPROVED_WITH_CONCERNS (P0B0-1..11). TW-B1 passed. TW-B3 has not fired.

## Binding rulings (read before dispatching)
- **PM, T005 part 2** (`test-results/field-list.md` §10): the D-3 sentence and the audiences text, verbatim. PRD v1.4.
  - Follow-ups: FU-1 "Check the Gemini infographic request against its documented field list before sending"; FU-2 "Executive-architecture callouts send mitigation text when a finding's threat text is empty"; FU-3 "Give every infographic placeholder a defined source and send only what each template draws".
- **Architect, AR-1..AR-14** (`test-results/w1-audit-rulings.md`). AR-14: a `sys.dont_write_bytecode` guard in the three scripts that import `tachi_parsers`.
- **Security analyst:**
  - T049 (`security-a.md`): ruling (a), the Read denies. Placement is AR-15, in flight.
  - T034 (`security-b1.md`): PASS_WITH_FINDINGS, H-1..H-3 and M-1..M-4. SC-007 is not met until H-1, M-1 and M-2 are fixed. The fix pass is in flight.
- **P0-B0:** non-tachi subagents are listed with `pinned_model: null`; `requestedModel` stays out of v1; a re-archive is a no-op only if the manifest exists; the `INSTALL_MANIFEST.md` counts are now 6 on part-b.
- **CF-21 churn:** `--schema-version-from-template` is not built (`t038a-measurement.md`).
- **§8 pins (T023):**
  - heading `## 8. Agent and command privilege matrix`, slug `8-agent-and-command-privilege-matrix`;
  - cell syntax: backticked tokens separated by `, `, with `—` for an empty set;
  - runbook §5: `## 5. Write locations`, header `| Path | Written by | Condition |`, copied from §8.5.
- **T039 deviations for T040:**
  - the `--check` exit codes follow the house convention (1 = drift, 2 = error), the reverse of `cli-contracts.md:27`;
  - the value is quoted;
  - `--json` is kept;
  - the marker regex rejects `/`.

## In flight when this was written (each in a detached worktree under `$SCRATCH/wt/`)
| Agent | Work | Worktree | Notes (`.aod/results/`) |
|---|---|---|---|
| architect | T016 profile review plus AR-15 (Read-deny placement); may amend `contracts/session-profile.md` and `data-model.md` | `arch-t016` | `architect-t016-profile-391.md` |
| SBE-D | T029 ADR-049 draft (Part A) | `sbe-d-t029` | `sbe-d-t029.md` |
| SBE-B1 | the T034 fix pass on the archiver | `b1-fix` (from part-b `ceea019`) | `sbe-b1-fix.md` |
| SBE-TB | T033 test module (written against the pre-fix archiver; must then cover the fixes and T034's "Tests to add") | `tb-t033` | `sbe-tb-t033.md` |
| SBE-TB | T039 contract test | `tb-t039` | `sbe-tb-t039.md` |
| SBE-D+TA | AR-14 follow-on (3 script guards, plus T015 harness without `-B`) | `ar14` | `ar14-followon.md` |

## Next dispatches
1. **T016 first commit, DEVOPS-R**, after AR-15: the profile block (from the final contract), the matrix link (slug above, with an `x-release-please-version` marker), and the §5 table. Then the **second commit**:
   - PM framing, mapping, passivity and routes;
   - AR-8 precondition for all outputs;
   - the nonessential-traffic gaps (the WebFetch domain check, marketplace auto-install);
   - the D-1 same-family exception (DEVOPS-R flag);
   - the T006 statements.
2. **After T016 #1:** T017 (SBE-TA plus DEVOPS-E wiring in `tachi-pytest.yml` on Part A), T018 (SBE-D, `INSTALL_MANIFEST.md`), T025 (SBE-E guard).
3. **After T025:** T026 and T027; then T028 (after T018).
4. **Part B:**
   - T033 tests updated for the B1 fixes, then DEVOPS-E appends T033 and T039's modules to `tachi-pytest.yml` (main run plus `py39-floor`) with their inputs;
   - T039's checkbox closes when its contract test is wired;
   - T034's checkbox closes after the fix pass.
5. **W1 close:** G1 (CI green on #392), then BX, then T040 ∥ T048 W1 part, then BX′, then H1.

## Mechanics adopted in this session (deviations from agent-assignments.md §5, for safety)
- **Per-dispatch worktrees.** Every agent that edits tracked files works in its own detached worktree at the branch tip. The orchestrator commits there with explicit paths and then `git cherry-pick`s onto the branch: in the main tree for Part A, in `$SCRATCH/wt/391-part-b` for Part B.
  - Reason: pre-commit stashes unstaged changes during a commit, so a concurrent agent write to a tracked file in the same tree can be silently lost.
  - Cherry-pick runs no pre-commit hook.
  - Branch semantics, the part separation and the commit granularity are unchanged.
- **T010** is written by SBE-E together with T023 (one writer for `CLAUDE_PERMISSIONS.md`), instead of SBE-D drafting and SBE-E committing.
- **T006's doc research** is done by DEVOPS-R with citations (the web-researcher role folded in).
- **The Bash tool is zsh.** An unquoted `$VAR` holding a list is NOT split, so a loop over SHAs once silently did nothing. Use explicit lists or `${=VAR}`.

## Follow-ups and records for `delivery.md` (T045)
- **AD-13:** a pre-existing defect. `/tachi.security-report` dispatched `senior-backend-engineer`; fixed in `c068ddc`.
- **Adapter copies:** `adapters/claude-code/commands/tachi.{threat-model,risk-score,infographic}.md` still print the old `cp -r` repair hint. Out of scope (#369's adapter roster).
- **#365:** maestro-reference's first divergence moved from 828878 to 52 (page count 86 → 88) since F-362 T024. Pre-existing, masked by the red; worth a note on #365 (outward-facing; ask the maintainer).
- **Census:** 35 out-of-gate failures and errors at `46aec8d` (`wave-01/census-failing.txt`).
- **Dependabot:** pushes report 25 Dependabot alerts on the default branch (5 critical). Pre-existing; not this feature's scope.

## Hygiene
- `/aod.build --no-tests`. Gated sets run in scratch clones of committed tips; check `git -C <clone> log -1`.
- `git status --short` in the main tree after every agent returns.
- `.aod/revision-context.md` is a stale untracked leftover from the tasks-revision loop. It is deliberately not committed.

## Resume
`claude "Resume F-391 /aod.build (branch 391-isolated-auditable-operation). W0 done; W1 in progress. Read specs/391-isolated-auditable-operation/NEXT-SESSION.md, then continue W1."`
