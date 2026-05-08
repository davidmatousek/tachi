# Agent Assignments — F-3 SECURITY.md and Private Disclosure Channel (BLP-02 Wave 3)

**Feature**: 272 (Issue #272) | **Branch**: `272-security-md-disclosure` | **Date**: 2026-05-08

## Execution Model

Single-maintainer project (davidmatousek). All 25 tasks execute serially in a single ~3-4h focused work block per SC-008. The wave structure below is **notional** — it provides `/aod.build` orchestration semantics (phase-gated checkpoints, `[P]`-marker grouping, dependency edges) but does **not** imply multi-agent parallelism. Every wave runs single-runner serial; "parallel" markers indicate tasks that *could* be reordered freely but are still executed one-after-the-other by the maintainer.

F-3 is documentation + repo-settings-toggle only — no source code, no automated tests. Verification is via post-merge `/security` re-scan plus three `[MANUAL-ONLY]` browser inspections.

## Agent Assignment Matrix

| Task | Agent | Type | Wave | Notes |
|------|-------|------|------|-------|
| T001 | senior-backend-engineer | Setup | 1 | Branch + artifact verification (`pwd`, `git branch`, frontmatter checks) |
| T002 | senior-backend-engineer | Setup | 1 | AC-2 cross-check (`.release-please-manifest.json`, `git tag`, `gh pr list`); capture latest tag for T004 |
| T003 | senior-backend-engineer | Setup | 1 | README line-number re-check (`grep -n "## Community\|Security vulnerabilities"`); marked `[P]` |
| T004 | senior-backend-engineer | US1 | 2 | SECURITY.md complete rewrite (~80 LOC, 5 sections per plan.md lines 155–186); MVP-delivering task |
| T005 | tester | US1 | 3 | Verify Sections 2-5 against US1 acceptance scenarios from spec §User-Story-1 |
| T006 | devops | US2 | 4 | `[MANUAL-ONLY]` Toggle ON in GitHub UI (`Settings → Code security and analysis → Advanced Security → Private vulnerability reporting`) |
| T007 | devops | US2 | 4 | `[MANUAL-ONLY]` Capture screenshot + plain-text "Toggle confirmed ON …" string per D-5 |
| T008 | tester | US2 | 5 | `[MANUAL-ONLY]` Verify *Report a vulnerability* button visible on Security tab; marked `[P]` |
| T009 | tester | US2 | 5 | `[MANUAL-ONLY]` Smoke-test advisory submission URL form load (no submit); marked `[P]` |
| T010 | tester | US3 | 6 | Verify SECURITY.md Section 1 against US3 acceptance scenarios |
| T011 | tester | US4 | 6 | Verify Section 2 footer (R-2 wording per D-3) + Section 3 SLA (5 business days per FR-005) |
| T012 | tester | US5 | 6 | Validate against CAIQ/SIG-Lite-style procurement questionnaire rubric |
| T013 | senior-backend-engineer | Polish | 7 | Append CHANGELOG entry under `## Unreleased → ### Features` per plan.md lines 189–211; marked `[P]` |
| T014 | senior-backend-engineer | Polish | 7 | Append README pointer under `## Community` per FR-008 + D-1; marked `[P]` |
| T015 | senior-backend-engineer | Polish | 8 | Stage three files + commit with `feat(272):` conventional-commit subject (release-please trigger) |
| T016 | devops | Polish | 9 | Push branch + open draft PR via `gh pr create --draft --title "feat(272): …"` per FR-014 |
| T017 | senior-backend-engineer | Polish | 10 | Edit PR description to attach T007 screenshot + plain-text confirmation evidence |
| T018 | devops | Polish | 11 | Mark PR ready (`gh pr ready <PR#>`) |
| T019 | devops | Polish | 12 | Squash-merge PR (`gh pr merge <PR#> --squash`); verify squash subject retains `feat(272):` |
| T020 | devops | Polish | 13 | Verify release-please PR opens within ~30s; F-212 recovery flow inline if empty |
| T021 | security-analyst | Polish | 14 | Post-merge `/security` re-scan; confirm TACHI-VULN-05abc41ad4cc → REMEDIATED per FR-013 |
| T022 | senior-backend-engineer | Polish | 15 | File AC-13 follow-up Issue (PVR-toggle posture probe); marked `[P]` |
| T023 | senior-backend-engineer | Polish | 15 | File AC-14 follow-up Issue (release-please manifest-vs-tag discrepancy); marked `[P]` |
| T024 | senior-backend-engineer | /aod.deliver | (deferred) | INDEX.md row 272 status flip `Approved → Delivered`; handled at /aod.deliver time |
| T025 | senior-backend-engineer | /aod.deliver | (deferred) | BLP-02 enterprise-hardening memory file update (Wave 3 → DELIVERED 3-of-5); handled at /aod.deliver time |

**Total**: 25 tasks across 15 notional waves; T024-T025 deferred to `/aod.deliver`.

### Agent rationale (cite `.claude/agents/_README.md` roster)

- **senior-backend-engineer**: Default for markdown / docs writing per CLAUDE.md fallback table. Owns SECURITY.md (T004), CHANGELOG entry (T013), README pointer (T014), commit (T015), PR-description edit (T017), follow-up Issue creation (T022/T023), and deferred governance updates (T024/T025).
- **tester**: Owns all post-write verification + acceptance-scenario validation (T005, T008, T009, T010, T011, T012). Includes the three `[MANUAL-ONLY]` UI checks against the live GitHub Security tab.
- **devops**: Owns out-of-tree GitHub repo-settings UI work (T006, T007), branch push + PR open (T016), PR-ready (T018), squash-merge (T019), and release-please verification + F-212 recovery (T020). Repo-settings UI is not script-accessible from agents → devops handles the human-in-loop steps.
- **security-analyst**: Owns T021 post-merge `/security` re-scan and TACHI-VULN-05abc41ad4cc REMEDIATED check.

No agent is assigned outside the registry. No `file-agent`, `doc-agent`, `qa-agent`, or other invented labels.

## Parallel Execution Waves

15 notional waves; serial in practice. `[P]` markers within a wave indicate tasks that the maintainer may freely reorder.

| Wave | Phase | Tasks | Notional parallelism | Blocking input |
|------|-------|-------|----------------------|----------------|
| 1 | Setup | T001 → T002 → T003 `[P]` | T002 ‖ T003 (different commands, no shared state) | None |
| 2 | US1 implementation | T004 | None (single task) | T002 latest tag |
| 3 | US1 verification | T005 | None | T004 file |
| 4 | US2 toggle + evidence | T006 → T007 | None (T007 depends on T006 UI state) | None (independent of US1) |
| 5 | US2 UI verifications | T008 `[P]` ‖ T009 `[P]` | T008 ‖ T009 (different URLs) | T006 toggle ON |
| 6 | US3 + US4 + US5 verifications | T010 → T011 → T012 | All three could run in parallel against the same SECURITY.md | T004 + T006 |
| 7 | File appends | T013 `[P]` ‖ T014 `[P]` | T013 ‖ T014 (different files) | T002 (CHANGELOG copy), T003 (README line numbers) |
| 8 | Stage + commit | T015 | None (sequential) | T004 + T013 + T014 |
| 9 | Push + draft PR | T016 | None | T015 |
| 10 | PR description w/ evidence | T017 | None | T007 + T016 |
| 11 | PR ready | T018 | None | T017 |
| 12 | Squash-merge | T019 | None | T018 |
| 13 | release-please verify | T020 | None | T019 |
| 14 | Post-merge re-scan | T021 | None (could run in parallel with T020 wait) | T019 |
| 15 | Follow-up Issues | T022 `[P]` ‖ T023 `[P]` | T022 ‖ T023 (separate `gh issue create` calls) | T019 (post-merge anchor) |

**Parallelism summary**: ~5 task-pair parallel opportunities (T002‖T003, T008‖T009, T010‖T011‖T012, T013‖T014, T022‖T023). For single-runner serial execution, parallelism reduces to sequencing flexibility within a wave, not wall-clock savings.

## Quality Gates

Three governance gates separate substantive deliverable boundaries.

### Gate A — Between US1 (Wave 3) and US2 (Wave 4): SECURITY.md content gate

**Criterion**: SECURITY.md must be GitHub-canonical (5 sections in correct order, R-2 footer verbatim per D-3, 5-business-day SLA verbatim per FR-005, credit clause preserved) **before** the maintainer pivots to the GitHub UI for the toggle work.

**Why**: If SECURITY.md sections fail T005 verification, returning to T004 mid-wave is cheaper than discovering content gaps after the toggle is ON and a researcher arrives at a misshapen document via the live button. The toggle is reversible; a half-broken merge is not.

**Pass condition**: T005 confirms all three US1 acceptance scenarios from spec §User-Story-1.

### Gate B — At PR-ready (Wave 11): Toggle-must-be-ON gate

**Criterion**: `[MANUAL-ONLY]` toggle (T006) must be ON, evidence (T007) captured **and** attached to the PR description (T017), before T018 marks the PR ready for merge.

**Why**: The PR title says "private disclosure channel" — merging to `main` while the toggle is OFF would ship documentation for a channel that does not exist (404 on the *Report a vulnerability* button). FR-010 + FR-011 + FR-012 must all be satisfied before T019 squash-merges.

**Pass condition**: PR description contains the screenshot and the plain-text "Toggle confirmed ON at HH:MM UTC YYYY-MM-DD" string per D-5; `gh pr view <PR#> --json isDraft` returns `false`.

### Gate C — Post-merge (Wave 14): TACHI-VULN-05abc41ad4cc REMEDIATED gate

**Criterion**: Post-merge `/security` re-scan (T021) must record TACHI-VULN-05abc41ad4cc → REMEDIATED in `.aod/results/security-scan.md`. No new HIGH or MEDIUM findings introduced.

**Why**: F-3's primary closure metric is the original A05 Security Misconfiguration finding flipping to REMEDIATED. Without this verification, the BLP-02 Wave 3 Initiative Tracker line cannot be marked closed. This gate also satisfies SC-001 from spec.md.

**Pass condition**: `.aod/results/security-scan.md` shows the finding ID with REMEDIATED status; HIGH/MEDIUM count = 0; LOW/INFO side-effects acceptable.

**Bonus gate (FR-014 release-please)**: Wave 13 has its own internal pass/fail (release-please PR appears within ~30s); if empty, the F-212 recovery flow inline at T020 is invoked. Not a hard gate (F-3 still ships even if release-please needs a marker push), but the maintainer must not move to T021 with an unconfirmed release-please state.

## Time Estimates per Wave

Calibrated to single-runner serial execution by the maintainer; ~3-4h active total per SC-008.

| Wave | Tasks | Estimated active time | Notes |
|------|-------|------------------------|-------|
| 1 | T001-T003 | ~5-10 min | Three short shell commands; trivial |
| 2 | T004 | ~30-45 min | The substantive write — 5 sections, ~80 LOC, blueprint already in plan.md lines 155–186 |
| 3 | T005 | ~5-10 min | Read-and-confirm pass against US1 acceptance |
| 4 | T006-T007 | ~10-15 min | UI toggle + screenshot + plain-text capture; one browser session |
| 5 | T008-T009 | ~5 min | Two URL loads in fresh tabs; no submission |
| 6 | T010-T012 | ~10-15 min | Three verification reads against the same file (cumulative ~5 min each) |
| 7 | T013-T014 | ~5-10 min | Two short markdown appends (CHANGELOG entry copy already in plan.md) |
| 8 | T015 | ~3-5 min | `git add`, heredoc commit, log verify |
| 9 | T016 | ~5 min | `git push -u`, `gh pr create --draft` with body heredoc |
| 10 | T017 | ~5 min | `gh pr edit --body-file` to attach evidence |
| 11 | T018 | ~1 min | `gh pr ready`; one command |
| 12 | T019 | ~2-5 min | `gh pr merge --squash`, then `git pull && git log --oneline -1` to confirm subject |
| 13 | T020 | ~1 min standard, ~5 min if F-212 recovery is needed | `sleep 30 && gh pr list`; recovery flow only if empty |
| 14 | T021 | ~5 min | `/security` invocation + REMEDIATED confirmation read |
| 15 | T022-T023 | ~5-10 min | Two `gh issue create` calls with prepared body strings |

**Subtotals**: Substantive write 30-45 min · UI toggle work ~15-20 min · Verifications ~20-30 min total · File appends 5-10 min · Commit/push/PR/merge ~15-20 min · Post-merge ~10-15 min · Follow-up Issues 5-10 min.

**Active total**: ~2.5-3.5h core work; ~3-4h with context-switch overhead. Matches PRD §Estimate-and-Timeline (3-4h cap) and SC-008 same-day-or-next-day delivery target.

**Deferred (not counted)**: T024 + T025 are `/aod.deliver`-time governance updates; they lag the squash-merge by minutes-to-hours but do not extend the F-3 active build window.

---

**Sign-off readiness**: Triple Triad approval received 2026-05-08 (PM, Architect, Team-Lead per tasks.md frontmatter). All assignments use `.claude/agents/_README.md` roster names exclusively. `/aod.build` may proceed.
