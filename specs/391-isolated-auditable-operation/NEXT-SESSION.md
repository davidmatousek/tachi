# NEXT-SESSION: F-391, build session S1 (interim handoff H1a, mid-W1)

**Written:** 2026-11-19, during build wave 2 (W1). Superseded by H1 at the end of S1.

## Where things stand
- **Part A** `391-isolated-auditable-operation`: tip `69f6bf1`, pushed. PR #392 (draft).
- **Part B** `391-isolated-auditable-operation-part-b`: tip `97db2e6` (an empty `feat(391)` opener), pushed. Draft PR #396, with base = the Part A branch.
- **Waves:** W0 done (T003; G0 PASS; `test-results/w0-prestate.md`). W1 in progress.
- **Tasks:** 13 of 52 done: T001–T005, T007–T009, T011, T014, T022, T024, T049.
- **Gates:**
  - P0-B0 is APPROVED_WITH_CONCERNS (`test-results/p0-b0-precheck.md`, rulings P0B0-1..11).
  - TW-B1 passed at T002.

## Binding rulings made during W1 (read before dispatching)
- **PM, T005 part 2** (`test-results/field-list.md` §10): the D-3 sentence (§10.1) and the audiences text (§10.3), verbatim. PRD v1.4 is recorded.
  - Follow-ups for `delivery.md`: FU-1 "Check the Gemini infographic request against its documented field list before sending"; FU-2 "Executive-architecture callouts send mitigation text when a finding's threat text is empty"; FU-3 "Give every infographic placeholder a defined source and send only what each template draws".
- **Architect, on the T004 audit** (`test-results/w1-audit-rulings.md`): AR-1..AR-13.
  - AR-1: build-mode extractor writes go under `{out}` (in T012, plus 4 new cases in T015).
  - AR-2: risk-scorer honours the output directory (T013, plus a T020 listing step).
  - AR-3: the Gemini request and response files are pinned under `{out}/.tachi-build/` (T013).
  - AR-4: `echo` joins threat-infographic's allow-list.
  - AR-5: `Agent` transitivity goes in the §8 legend, with two follow-ups.
  - AR-6, AR-7, AR-12: §8 content (T023). AR-8: runbook only (T016). AR-10: T012's sweep lines.
- **Security analyst, T049** (`test-results/security-a.md`): ruling (a), `Read(//proc/**)` and `Read(~/.claude/.credentials.json)` denies.
  - **The architect decides at T016's profile review** whether they join the baseline profile block, which would change `contracts/session-profile.md`, `data-model.md:53` and T017's key set.
- **Architect, P0-B0**: non-tachi subagents are listed with `pinned_model: null`; `requestedModel` stays out of v1; re-archive is a no-op only if `run-manifest.json` exists; the `INSTALL_MANIFEST.md:15/:64` "4 Python files" counts change in the T032 and T039 whitelist commits.

## In flight when this was written (each in its own detached worktree under `$SCRATCH/wt/`)
| Agent | Tasks | Worktree | Notes file (`.aod/results/`) |
|---|---|---|---|
| SBE-B1 | T031, T032 (with the T032.1–.3 actuals for the TW-B3 watch), `schemas/run-manifest.yaml` | `b1` (from part-b `97db2e6`) | `sbe-b1-w1.md` |
| SBE-B2 | T036, T038a (the CF-21 churn verdict decides T039's flag) | `b2` (from part-b `97db2e6`) | `sbe-b2-w1.md` |
| DEVOPS-R | T006 (also amends `contracts/session-profile.md:31` to the §10.3 entry; pre-stages `~/.tachi/391-w2/session-profile.json`), T019 | `devops-r` (from `47a19bc`) | `devops-r-t006.md` |
| SBE-D 2a | T012 + AR-1 + AR-10 | `sbe-d2a` (from `9aa00b7`) | `sbe-d-w1b-t012.md` |
| SBE-D 2b | T013 + AR-2 + AR-3 + AR-9 | `sbe-d2b` (from `9aa00b7`) | `sbe-d-w1b-t013.md` |

If a worktree still holds uncommitted work, commit it there with explicit paths, then cherry-pick onto the right branch (see Mechanics).

## Next dispatches (dependency order)
1. **T010 + T023, SBE-E, in one writer for `CLAUDE_PERMISSIONS.md`** (T010's draft is folded into SBE-E). Needs T012 and T013 committed. Pin the §8 heading slug (no em dash), the cell syntax and the runbook §5 table shape. AR-4..AR-7 and AR-12 apply.
2. **T015, SBE-TA plus DEVOPS-E wiring.** Needs T012–T014 committed. Add AR-1's 4 cases. The wiring goes in `tachi-install-fidelity.yml`'s `report-posture` job and `&fidelity_paths`, in the same commit as the module.
3. **T016 first commit, DEVOPS-R.** Needs T006 and T023's slug. The marked profile block, the matrix-link line with its `x-release-please-version` marker, and the write-locations table from the T004 audit plus AR-1..AR-3.
   - **Second commit** after T049: also note that `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` does not cover the WebFetch domain check or the official-marketplace auto-install (found in batch 3).
   - The PM writes the framing, mapping, passivity and routes; the architect reviews the profile (including the T049 placement).
4. **Then:** T017 and T018 (after T016 #1); T025 (after T023 and T016 #1); then T026, T027 and T028; T029 (after T023; ADR-049).
5. **Part B:**
   - after T032: T033 tests (SBE-TB) and T034 (security-analyst);
   - after T036: T037 (SBE-TB);
   - after T038a: T039 (SBE-B2; its `INSTALL_MANIFEST.md` line is serialised after T032's, R-4).
   - DEVOPS-E's first Part B `tachi-pytest.yml` commit carries the 3.9 step on `ubuntu-latest`.
6. **W1 close:** G1, then BX (merge Part A into part-b), then T040 ∥ T048's W1 part, then fixes, then BX′, then H1.
7. **Optional PM wording pass** over the T007–T009 placement: the D-3 text is verbatim and PM-approved, but the lead-ins ("What leaves your machine.") were Lane D's choice. Fold it into T040, or into T041's SC-A2 sweep.

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
