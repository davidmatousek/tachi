# NEXT-SESSION: Feature 373 build, Session 2 (build waves 4–5 = tasks.md W3–W4)

**Written**: 2026-09-28, at the end of Session 1 (T033, the `/aod.build` 3-wave standalone ceiling). This replaces the W1-exit snapshot.

- **Feature**: #373, adopter install + output fidelity fixes (K1–K3, K9–K15, #370)
- **Branch**: `373-adopter-install-output-fidelity` · **Draft PR**: #375 (`fix(373): …`)
- **Session 1 is complete**: build waves 1–3 (tasks.md W0, W1, W2). Ledger: **33 of 40** `[X]`.
- **Open (all Session 2)**: T015, T030 (the live render session), T034, T035, T036 (W3); T037, T038 (W4). T040 is `[X]`, not triggered.
- **Pushed tip**: see `git log -1 origin/373-adopter-install-output-fidelity`. The code tip is `4bea6c5`; the docs commit that carries this file sits on top of it.

## Next actions (Session 2, in dependency order)

0. **Pre-flight**
   - Start from a clean main-tree checkout of the branch, with local `HEAD` equal to `origin`.
   - Session 1's lane worktrees lived in its scratchpad. **Stale local scaffolding** remains:
     - the branches `373-w1-laneAp`, `373-w1-laneB1`, `373-w1-laneC1`, `373-w2-A`, `373-w2-B2a`, `373-w2-B2b`, `373-w2-C2` and `373-w2-T`, plus their worktree entries;
     - every one of their commits is integrated (checked by patch-id; three test modules landed byte-identical inside their wiring commits);
     - the cleanup was permission-blocked in Session 1. Delete them when convenient: `git worktree prune`, then `git branch -D` on those eight names.
   - Never run pytest, the extractors or `install.sh` in the main tree (#365); use scratch clones of committed state.
1. **The P0 required changes** (architect, `test-results/p0-architect-review.md` §9; ≈ 0.10–0.13 d). Land them with T034's W3 integration commit, before T035 and T036:
   - **RC-1 (MEDIUM, K3; owner DEVOPS-K3, the Lane A `install.sh` owner)**:
     - The residual of SEC-K3-01: two linked ancestors of 17 links each still fail mid-copy on macOS with a partial write, because the OS counts symlinks across the whole path lookup.
     - Fix: make `[ -e "$p" ] || return 1` the first statement of `resolve()`. Keep the 32-hop ceiling, and fix the comment.
     - Add a regression test: `.claude` and `.claude/skills`, each behind a 21-link chain, with `--follow-symlinks` and a plain entry listed first. Expect exit 1, the always-refused block, and ZERO writes.
     - The test must fail at `4bea6c5` on both legs and pass after the fix.
   - **RC-2 (LOW, K11; owner SBE-W3)**: in `extract-infographic-data.py`, parse `risk-scores.md` ONCE on the tier-1 path. Reuse that parse for both the composites join and the row count, and compare row counts only when the parse yields at least one row. One test.
   - **RC-3 (LOW, K9; owner SBE-W3, the only W3 writer of `tachi_parsers.py`)**: in `parse_markdown_table`, stop at `level <= max(matched_level, 2)`, and fix the docstring. One test pins a level-1 match giving `[]` (W0 behavior).
2. **T034, W3 integration (Lane A, devops)**: commit and push. Then:
   - CI must be **visibly** green on #375: `manifest-completeness`, `extraction-fidelity` and `report-posture`, both `tachi-pytest` legs, and the co-fired `mmdc-preflight`, `catalog-drift`, `maestro-coverage` and gitleaks;
   - re-run the N4 ungated modules in a scratch clone, and attribute any delta against T001 (`test-results-prestate.md`) and the W2 record (`test-results/n4-rerun-w2.md`).
3. **The render session (T030 → T015)**, **with the maintainer, about 1 hour**. This paces W3; Session 2 can start as soon as that hour is available. `tester` renders and records; SBE-W3 makes every file change.
   - **Setup**: a scratch clone of T034's commit, and a scratch copy of `examples/maestro-reference/` (`quickstart.md` §4, NFR-5 key handling).
   - **K15 ships** (TW-0/T039 NO CARVE), so the first iteration renders all six templates, with executive-architecture at 3:4. These double as K14's per-template renders. Check each image for layout-label leakage and for IDs outside `allow_list`.
   - **Then T015**: at least one render on the fallback model `gemini-3.1-flash-image`, and executive-architecture on ONE portrait page of a scratch PDF.
   - **2K latency** (`IMAGE_SIZE_RESTORED = true`): if a real 2K render takes more than about 45 s, drop 2K in ONE commit. That commit flips the six blocks, the reference, the adapter copy and `IMAGE_SIZE_RESTORED`, then re-pushes through T034.
   - **TW-5**: at most 2 prompt iterations; residual leakage goes to a follow-up issue. **TW-6**: if renders are blocked for more than 0.5 d, run T030's late-carve procedure. The K15 revert set applies cleanly: 5 commits, 0 conflicts, dry-run at T033.
   - **Records** go in the PR body and in `test-results/k15-renders.md`. No images are committed.
4. **T032 re-run**, only if a K15 iteration changed prompt text. Keep one commit per K-item.
5. **T035, the oracle post-snapshot** (`test-results-prestate.md` has the `snapshot.sh` appendix; the W0 SHA is `0ce39d0`), then `oracle-diff.md`, grouped by field class × K-item, 100% attributed. Include the P0 §3 rules:
   - `agentic-app/sample-report` at 4 NEW / 0 UPDATED / 82 UNCHANGED, and `agentic-app` tier 3 at 12 NEW / 69 UNCHANGED;
   - tier-3 badges and `top_findings[].delta_status` normalized;
   - the removed "misclassified" warning class (K11);
   - `maestro-reference`'s PDF at +2 pages (K13.1 M5; intended; the `.pdf.baseline` is NOT regenerated, NFR-8).
6. **T036**:
   - the `code-reviewer` does a full-diff review, scoped to executable code and including the RC-1/2/3 deltas. Persona injection: `stacks/knowledge-system/agents/code-reviewer.md`, with its "no application code" framing overridden;
   - fixes are made by SBE-W3;
   - then the **architect's P1 checkpoint**, which confirms N8 and N11.
7. **W4**: T037 (docs, the ADR-014 note written by the architect, CHANGELOG `Unreleased`, the PR body, the #364 draft) runs alongside T038 (the PM's release notes, PD-7). Then the P2 read, then `/aod.deliver`.

## Gate status at the end of W2 (agent-assignments.md § 3, "End of wave 3")

| Item | State |
|---|---|
| T032 golden commits, one per K-item | `5a1810e` (K11), `3ffc3db` (K13), `982c074` (K15); 47 leaves, all authorized; the K15 revert applies cleanly |
| T033 P0 approval | **APPROVED_WITH_CONCERNS**, GO for Session 2; 3 required changes (above), none blocking the break (`test-results/p0-architect-review.md`) |
| N4 re-run attributed | totals identical to W0, 0 new reds; `maestro-reference` +2 PDF pages attributed to K13.1 (M5), intended (`test-results/n4-rerun-w2.md`) |
| TW-7 ruling | **NOT FIRED**: remaining 1.72 d against 2.0; highest lane at 47% of its budget. T040 not triggered (`test-results/w2-exit-tw7.md`) |
| Wave-3 gated set | 482 passed, 0 failed, 2 skipped (known), 0 regressions (`test-results/wave-03/results.json`) |
| CI at `4bea6c5` | all green: install fidelity (3 jobs), `tachi-pytest` (macOS and ubuntu), `catalog-drift`, `mmdc-preflight`, `maestro-coverage`, gitleaks |

## Checkpoint log (the override of `/aod.build` Step 2c, per agent-assignments.md § 3)

| Checkpoint | After build wave | Reviewer | Status |
|---|---|---|---|
| (quality gate) | 1 (W0) | none (gate only) | passed |
| **T039** trip-wire re-check | 2 (W1) | team-lead, in place of Step 2c's P0 at wave 2 | **NO CARVE** |
| **P0** Go/No-Go | 3 (W2) | architect (T033) | **APPROVED_WITH_CONCERNS** (3 RCs due in W3) |
| **TW-7** | 3 (W2) | team-lead (T033) | **NOT FIRED** |
| **P1** | 4 (W3) | code-reviewer, then architect (T036) | pending |
| **P2** | 5 (W4) | architect | pending |

## Decisions and rulings made during Session 1

- **T039**: NO CARVE. K15, K11 and K13-posture all ship. Only K15 remains carvable, via TW-6.
- **T016 gap**: tier-3 `parse_threats_findings` did not normalize Status at parse. B2b found it; it was fixed in W2 (`9019528`) and ratified at P0 as a scoped AR-3 exception.
- **Installer `:145`**: the "nested, unresolved" message variant was unreachable under data-model §2.1's precedence. The precedence was kept, and the contract was amended at P0.
- **SEC-K3-01/02** (T011's security review, APPROVED_WITH_CONCERNS): the 32-hop ceiling and glob-safe splitting (`45bb8d6`) were ratified at P0. **RC-1** closes the residual partial-write mode.
- **Contracts amended at P0**, each marked "(amended at P0, 2026-09-28)": `contracts/installer-cli.md`, `data-model.md` and `contracts/extraction-data-contract.md`.
- **PDF baselines**: the tracked `examples/**/security-report.pdf.baseline` files are NOT regenerated in this feature (NFR-8). The byte-identical PDF test was already red at W0 (font-subset drift; ungated).

## Follow-up issues to file at `/aod.deliver` (after `export AOD_REPO=davidmatousek/tachi`)

- **SEC-K3-03** (LOW; pre-existing on `main`): `install.sh --version` passes the tag to `git checkout` without a leading-dash guard (P0 ruling 6c).
- **P0 A-4**: the `## Section N: Title` heading form in some tracked examples. The parsers match only `## N.`, so those funnels show Threats Identified = 0 (pre-existing, outside K9–K13).
- **N7**: a free-text `baseline.source` on a stateless run triggers PD-16's "baseline run but no Status column" warning (tasks.md deliver reminders).
- Any TW-5 residual leakage from the render session.

## Commits on the branch in W2 (after the W1 list in git history)

Lane A: `763ff0e` (T011 README), `45bb8d6` (SEC-K3-01/02).

C2:
- `508eb83` (T018)
- `346d6b3`, `1959e47` (T026)
- `5827e45` (T022 text)
- `d0eae8e`, `f57bd37` (T028, K15)

B2a:
- `fddabb2` (T017)
- `d989115` (T025)
- `9019528` (T016 gap)
- `7a0d820`, `3976870` (T021, K11)
- `d990f66` (T027, K15)

B2b:
- `a94f495`, `a4ea956` (T017)
- `7f19c35` (sweep and ledger)
- `5f415f9` (T031 docstring)
- `1e1ed70`, `fa7fa10` (T025)
- `5c460ba` (T022 caption)

Test lane and wiring:
- `808e0ea` (A11)
- `811c1e5` (US-3a)
- `4ab1d74` (sibling-parity module plus wiring)
- `56c1c9f` (T031 tests)
- `075cca5` (the posture module plus the `report-posture` job, K13)
- `eaa77a8` (T023)
- `26ba067` (K11 parity)
- `7f7cd47` (T029, K15)

Goldens: `5a1810e`, `3ffc3db`, `982c074`.

## Facts the next session needs

- **Orchestration pattern that worked**:
  - one git worktree per lane;
  - staged ~30-minute dispatches (T039 §8.2);
  - the orchestrator cherry-picks in lane order;
  - lock-step wiring squashes for new test modules;
  - one push per wave.

  W1's single large T009 dispatch failed twice (a stall, then the 64k output-token limit); staging fixed it.
- **Attribution**: the build agents run on sonnet. Session 1 prompts initially prescribed an "Opus 5.5" co-author line, so several subagent commits carry it inaccurately. Later prompts told each agent to use its own line. The squash merge at deliver carries the accurate attribution.
- **Maintainer window**: the only human input left in the build is the render session's visual check (six images plus the executive-architecture PDF page), about 1 hour, with a reserve for a TW-5 iteration.

## Resume prompt

```
claude "Resume Feature 373 implementation (branch: 373-adopter-install-output-fidelity). Waves 1-3 complete (P0 APPROVED_WITH_CONCERNS; TW-7 not fired). Run /aod.build to continue with Wave 4 (tasks.md W3), starting with P0's RC-1..RC-3 and T034."
```
