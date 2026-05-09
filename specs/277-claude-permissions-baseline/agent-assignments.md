# Agent Assignments — F-4 Claude Code Permissions Baseline (BLP-02 Wave 4)

**Feature**: 277 (Issue #277) | **Branch**: `277-claude-permissions-baseline` | **Date**: 2026-05-08

## Execution Model

Single-maintainer project (davidmatousek). All 30 tasks execute serially in a single ~8-9h focused work block per PRD §Estimate-and-Timeline / SC-008. The wave structure below is **notional** — it provides `/aod.build` orchestration semantics (phase-gated checkpoints, `[P]`-marker grouping, dependency edges) but does **not** imply multi-agent parallelism. Every wave runs single-runner serial; "parallel" markers indicate tasks that *could* be reordered freely but are still executed one-after-the-other by the maintainer.

F-4 is documentation + settings-file rewrite + new ADR — no source code, no automated tests. Verification is via the AC-2 cross-check + AC-6 sub-checks + AC-7 manual probe + AC-12 manual smoke-test + post-merge `/security` re-scan. Eight `[MANUAL-ONLY]` interactive Claude Code probes (T009-T012, T014, T018, T025-T026).

The F-4 envelope (~8-9h) vs F-3's (~3-4h) is driven by ADR-041 authoring + ~250 LOC CLAUDE_PERMISSIONS.md + four-category settings.json rewrite. Wave structure mirrors F-3's W4-W15 single-maintainer pattern, scaled for ADR-041 + paired-P1 deny+ask interactive probes.

## Agent Assignment Matrix

| Task | Agent | Type | Wave | Notes |
|------|-------|------|------|-------|
| T001 | senior-backend-engineer | Setup | 1 | Branch + artifact verification (`pwd`, `git branch`, frontmatter checks) |
| T002 | senior-backend-engineer | Setup | 1 | ADR-041 number freshness check; marked `[P]` |
| T003 | senior-backend-engineer | Setup | 1 | H-4 absolute-path baseline grep against pre-rewrite `.claude/settings.json`; marked `[P]` |
| T004 | senior-backend-engineer | Setup | 1 | release-please state cross-check (manifest + tags + open release-PR); marked `[P]` |
| T005 | architect | US1 | 2 | Author ADR-041 (~100 LOC, ceiling ~150). Architect-owned per `.claude/agents/_README.md` (architecture decisions = architect). Mirrors ADR-040 structure; ≥6 alternatives-considered |
| T006 | senior-backend-engineer | US1 | 3 | Author CLAUDE_PERMISSIONS.md (~250 LOC, ceiling ~350); 7 sections per plan §D-2; depends on T005 framing |
| T007 | senior-backend-engineer | US1 | 4 | Rewrite `.claude/settings.json` (~80 LOC); strict JSON; deny → ask → allow ordering; depends on T006 per-rule table |
| T008 | senior-backend-engineer | US1 | 5 | Run AC-1 + AC-2 + AC-9 cross-checks (`jq -e empty`, H-4 grep, rule-vs-doc diff one-liner) |
| T009 | tester | US2 | 6 | `[MANUAL-ONLY]` AC-6b — verify `Bash(git status)` auto-approves (built-in read-only regression); marked `[P]` |
| T010 | tester | US2 | 6 | `[MANUAL-ONLY]` AC-6c — verify `Bash(git push --force …)` deny prompt surfaces; marked `[P]` |
| T011 | tester | US2 | 6 | `[MANUAL-ONLY]` Tier-3a deny enumeration (4 ops: rm -rf, git reset --hard, gh release delete, npm publish); marked `[P]` |
| T012 | tester | US2 | 6 | `[MANUAL-ONLY]` Tier-3b ask enumeration (force-with-lease, brew install, npm install -g); marked `[P]` |
| T013 | senior-backend-engineer | US3 | 7 | FR-003 file-untouched check (`git diff` empty + `git check-ignore` confirms gitignored) |
| T014 | tester | US3 | 7 | `[MANUAL-ONLY]` AC-12 cross-file deny precedence with fixture-and-cleanup (CREATE → ATTEMPT → REMOVE → CONFIRM); marked `[P]` |
| T015 | tester | US4 | 8 | Validate CLAUDE_PERMISSIONS.md against US-4 acceptance scenarios (5 sub-checks: sections, precedence, built-ins, opt-outs, limitations) |
| T016 | tester | US5 | 8 | External-review rubric on full artifact suite (`jq` deny array length, T015 result, ≥6 alternatives grep) |
| T017 | senior-backend-engineer | Polish | 9 | Append CHANGELOG entry under `## Unreleased → ### Features`; marked `[P]` |
| T018 | tester | Polish | 9 | `[MANUAL-ONLY]` AC-7 subdomain-matching probe (`WebFetch(api.github.com/…)`); both outcomes valid; marked `[P]` |
| T019 | senior-backend-engineer | Polish | 10 | Stage four files + commit with `feat(277):` conventional-commit subject (release-please trigger) |
| T020 | devops | Polish | 11 | Push branch + open draft PR via `gh pr create --draft --title "feat(277): …"` per FR-013 |
| T021 | devops | Polish | 12 | Mark PR ready (`gh pr ready <PR#>`); confirm `isDraft=false` |
| T022 | devops | Polish | 13 | Squash-merge PR (`gh pr merge <PR#> --squash`); verify squash subject retains `feat(277):` |
| T023 | devops | Polish | 14 | Verify release-please PR opens within ~30s; F-212 recovery flow inline if empty (empty marker commit) |
| T024 | security-analyst | Polish | 14 | Post-merge `/security` re-scan per FR-014; regression-only (no finding closed by F-4) |
| T025 | tester | Polish | 15 | `[MANUAL-ONLY]` Defense-in-depth re-run AC-6b on fresh post-merge clone (`git status` auto-approve); marked `[P]` |
| T026 | tester | Polish | 15 | `[MANUAL-ONLY]` Defense-in-depth re-run AC-6c on same fresh clone (`Bash(rm -rf:*)` deny); marked `[P]` |
| T027 | senior-backend-engineer | Polish | 15 | File AC-15 follow-up Issue (pre-commit hook for jq + AC-2 cross-check); marked `[P]` |
| T028 | senior-backend-engineer | Polish | 15 | File AC-16 follow-up Issue (CI integration for verification recipe); marked `[P]` |
| T029 | senior-backend-engineer | /aod.deliver | (deferred) | INDEX.md row 277 status flip `Approved → Delivered` + PR link; handled at /aod.deliver time |
| T030 | senior-backend-engineer | /aod.deliver | (deferred) | BLP-02 enterprise-hardening memory file update (Wave 4 → DELIVERED 4-of-5); handled at /aod.deliver time |

**Total**: 30 tasks across 15 notional waves; T029-T030 deferred to `/aod.deliver`.

### Agent rationale (cite `.claude/agents/_README.md` roster)

- **architect**: Owns T005 ADR-041 authoring. Architecture-decision records are first-class architect artifacts per `.claude/agents/_README.md` (architect = "Technical design, architecture decisions, technology selection"). T005 freezes the four-category architectural framing that T006 + T007 depend on.
- **senior-backend-engineer**: Default for markdown / config / docs writing per CLAUDE.md fallback table. Owns CLAUDE_PERMISSIONS.md (T006), settings.json rewrite (T007), AC-2 cross-check script execution (T008), file-untouched check (T013), CHANGELOG entry (T017), git commit (T019), follow-up Issue creation (T027/T028), and deferred governance updates (T029/T030). Also owns Setup phase shell-command tasks (T001-T004).
- **tester**: Owns all post-write verification + acceptance-scenario validation that requires reading artifact content or interactive Claude Code session probes — T009-T012 (US2 deny+ask interactive verification), T014 (US3 cross-file deny precedence), T015 (US4 sections/precedence/built-ins/opt-outs/limitations checks), T016 (US5 external-review rubric), T018 (AC-7 subdomain probe), T025-T026 (post-merge defense-in-depth). Eight `[MANUAL-ONLY]` interactive probes total live here.
- **devops**: Owns branch push + PR open (T020), PR-ready (T021), squash-merge (T022), and release-please verification + F-212 recovery (T023). Same surface as F-3's devops scope (git/gh remote operations + PR lifecycle).
- **security-analyst**: Owns T024 post-merge `/security` re-scan. F-4 is regression-only (no finding directly closed); the re-scan confirms no new HIGH/MEDIUM findings introduced.

No agent is assigned outside the registry. No `file-agent`, `doc-agent`, `qa-agent`, or other invented labels.

## Parallel Execution Waves

15 notional waves; serial in practice. `[P]` markers within a wave indicate tasks that the maintainer may freely reorder. Mirrors F-3 W1-W15 pattern with US1 split across W2-W5 (ADR → docs → settings → verification) instead of F-3's single W4 SECURITY.md write.

| Wave | Phase | Tasks | Notional parallelism | Blocking input |
|------|-------|-------|----------------------|----------------|
| 1 | Setup | T001 → T002 `[P]` ‖ T003 `[P]` ‖ T004 `[P]` | T002 ‖ T003 ‖ T004 (different commands, no shared state) | None |
| 2 | US1 ADR-041 | T005 (architect) | None (single task) | T002 number-freshness |
| 3 | US1 CLAUDE_PERMISSIONS.md | T006 | None | T005 framing |
| 4 | US1 settings.json | T007 | None | T006 per-rule table |
| 5 | US1 verification | T008 | None | T005 + T006 + T007 |
| 6 | US2 interactive verification | T009 `[P]` ‖ T010 `[P]` ‖ T011 `[P]` ‖ T012 `[P]` | All four `[MANUAL-ONLY]` against same fresh Claude Code session — logically independent, practically sequential within one session | T007 (new settings loaded) |
| 7 | US3 verification | T013 ‖ T014 `[P]` | T013 (file-untouched) ‖ T014 (cross-file fixture); independent surfaces | T007 |
| 8 | US4 + US5 verification | T015 → T016 | T015 prerequisite for T016 (T016 cites T015 result); both could run in parallel against same artifact suite | T006 + T007 |
| 9 | File appends + AC-7 probe | T017 `[P]` ‖ T018 `[P]` | T017 (CHANGELOG) ‖ T018 (manual subdomain probe); independent | T007 |
| 10 | Stage + commit | T019 | None (sequential) | T005 + T006 + T007 + T017 |
| 11 | Push + draft PR | T020 | None | T019 |
| 12 | PR ready | T021 | None | T020 + (T008-T016, T018 verifications all green) |
| 13 | Squash-merge | T022 | None | T021 |
| 14 | release-please verify + post-merge re-scan | T023 ‖ T024 | T023 (release-please) ‖ T024 (`/security` re-scan); both post-merge, independent | T022 |
| 15 | Defense-in-depth + follow-up Issues | T025 `[P]` ‖ T026 `[P]` ‖ T027 `[P]` ‖ T028 `[P]` | T025 ‖ T026 (same fresh clone session, two operations); T027 ‖ T028 (separate `gh issue create` calls) | T022 (post-merge anchor) |

**Parallelism summary**: ~6 task-pair / triple parallel opportunities (T002‖T003‖T004, T009‖T010‖T011‖T012, T013‖T014, T017‖T018, T025‖T026, T027‖T028). For single-runner serial execution, parallelism reduces to sequencing flexibility within a wave, not wall-clock savings.

## Quality Gates

Four governance gates separate substantive deliverable boundaries.

### Gate A — Between US1 ADR-041 (Wave 2) and CLAUDE_PERMISSIONS.md (Wave 3): Architecture-freezes-first gate

**Criterion**: ADR-041 must be authored with all four categories enumerated and ≥6 alternatives-considered **before** CLAUDE_PERMISSIONS.md authoring begins (T006 references ADR-041 framing; reverse-engineering the rationale post-hoc is the anti-pattern).

**Why**: Per plan §D-7, the architecture-decision must freeze before the policy-decision-log is written. CLAUDE_PERMISSIONS.md cites ADR-041 reciprocally; if T006 starts with a half-written ADR, the cross-references drift.

**Pass condition**: T005 produces a complete ADR-041 with Status / Context / Decision / Alternatives / Consequences / Related Findings / References sections; ≥6 alternatives have Pros/Cons/Why-Not-Chosen blocks.

### Gate B — Between US1 verification (Wave 5) and US2 interactive verification (Wave 6): AC-2 cross-check passes

**Criterion**: AC-2 cross-check (T008) — every non-built-in rule from `.claude/settings.json` appears in CLAUDE_PERMISSIONS.md per-rule table; every table row references a rule in settings.json or is flagged as built-in. Empty `diff` between extracted-rules-list and table-rules-list. Plus `jq -e empty` exit 0 + H-4 grep zero matches.

**Why**: If T008 fails, returning to T006/T007 mid-build is cheaper than discovering orphaned rules during interactive deny+ask probes (T009-T012). The cross-check is the structural integrity test for the entire US1 suite.

**Pass condition**: AC-1 (`jq -e empty`) PASS; AC-9 (H-4 grep) PASS; AC-2 (rule-vs-doc diff) empty. Diff captured for PR description.

### Gate C — At PR-ready (Wave 12): All-pre-commit-verifications-green gate

**Criterion**: T009-T012 (US2 deny+ask), T013+T014 (US3 file-untouched + cross-file precedence), T015 (US4 sections), T016 (US5 rubric), T018 (AC-7 probe outcome captured), T008 (AC-2 cross-check) — all must record PASS or expected-anomaly outcomes **before** T021 marks PR ready.

**Why**: The PR title says "claude permissions baseline" — merging to `main` while any `[MANUAL-ONLY]` deny/ask probe is unverified would ship a baseline that may not behave as documented. FR-005 + FR-006 + FR-007 + FR-011 + FR-012 must all be satisfied before T022 squash-merges.

**Pass condition**: PR description Verification (pre-commit) checklist (T020 body) shows all 9 items checked; `gh pr view <PR#> --json isDraft` returns `false`.

### Gate D — Post-merge (Wave 14): No-regression gate

**Criterion**: Post-merge `/security` re-scan (T024) records no new HIGH or MEDIUM findings in `.aod/results/security-scan.md`. release-please PR opens within ~30s of squash-merge (T023); F-212 recovery flow invoked if empty.

**Why**: F-4 is posture-gap-closure (not vuln-closure); the re-scan is regression-only — confirming the `.claude/settings.json` rewrite did not introduce new findings. release-please verification is the BLP-02 release-cadence gate; missing it produces F-212-class silent-skip incidents.

**Pass condition**: `.aod/results/security-scan.md` HIGH/MEDIUM count = 0; LOW/INFO side-effects acceptable. release-please PR present with target version (v4.34.0 if F-3 has merged its release marker; v4.33.0 if F-3 still in flight).

## Time Estimates per Wave

Calibrated to single-runner serial execution by the maintainer; ~8-9h active total per PRD §Estimate-and-Timeline / SC-008. T005+T006 dominate the cost; verification + delivery are linear-in-tasks.

| Wave | Tasks | Estimated active time | Notes |
|------|-------|------------------------|-------|
| 1 | T001-T004 | ~10-15 min | Four short shell commands (T002‖T003‖T004 read-only); trivial |
| 2 | T005 | ~2-3h | ADR-041 authoring (~100 LOC, ceiling ~150); 6 alternatives × ~15-20 LOC each + Status/Context/Decision/Consequences/Refs |
| 3 | T006 | ~2.5-3h | CLAUDE_PERMISSIONS.md authoring (~250 LOC, ceiling ~350); 7 sections; per-rule rationale table dominant |
| 4 | T007 | ~45-60 min | settings.json rewrite (~80 LOC); deny → ask → allow ordering; mechanical given T006 per-rule table |
| 5 | T008 | ~10-15 min | AC-1 + AC-2 + AC-9 cross-check one-liner; jq + grep + diff |
| 6 | T009-T012 | ~20-30 min | Four `[MANUAL-ONLY]` interactive probes; single Claude Code session; ~5min each + reload time |
| 7 | T013-T014 | ~10-15 min | T013 git diff/check-ignore; T014 fixture create-attempt-remove-confirm |
| 8 | T015-T016 | ~10-15 min | T015 read-and-confirm 5 sub-checks; T016 jq + grep + T015-cite |
| 9 | T017-T018 | ~10-15 min | T017 CHANGELOG append (entry blueprint in plan); T018 single `[MANUAL-ONLY]` WebFetch probe |
| 10 | T019 | ~3-5 min | `git add` four files, heredoc commit, log verify subject |
| 11 | T020 | ~5 min | `git push -u`, `gh pr create --draft` with body heredoc |
| 12 | T021 | ~1 min | `gh pr ready <PR#>`; one command |
| 13 | T022 | ~2-5 min | `gh pr merge --squash`, then `git pull && git log --oneline -1` to confirm subject |
| 14 | T023-T024 | ~10-15 min | T023 `gh pr list` (~1min standard, ~5min if F-212 recovery); T024 `/security` re-scan + REMEDIATED check |
| 15 | T025-T028 | ~15-20 min | T025+T026 fresh-clone two-op session; T027+T028 two `gh issue create` calls |

**Subtotals**: ADR-041 authoring 2-3h · CLAUDE_PERMISSIONS.md authoring 2.5-3h · settings.json rewrite 45-60 min · Verification gates ~1h cumulative (T008+T009-T012+T013-T014+T015-T016) · Polish + delivery ~30-45 min · Post-merge ~25-35 min.

**Active total**: ~8h45m core work; ~9h with context-switch overhead. Matches PRD §Estimate-and-Timeline (~8-9h envelope) and SC-008 next-day cap (start morning, complete by end of next business day with sleep break in between).

**Two-session split likely**: Per team-lead M-2 observation, the maintainer will likely break across two sessions — Session 1: T001-T008 (Setup + ADR-041 + CLAUDE_PERMISSIONS.md + settings.json + AC-2 cross-check, ~5-6h); Session 2: T009-T028 (US2-US5 verification + delivery + post-merge, ~3-3.5h). Wave structure preserves this split cleanly.

**Deferred (not counted)**: T029 + T030 are `/aod.deliver`-time governance updates; they lag the squash-merge by minutes-to-hours but do not extend the F-4 active build window.

---

**Sign-off readiness**: Triple Triad approval received 2026-05-08 (PM APPROVED, Architect APPROVED, Team-Lead APPROVED_WITH_CONCERNS — 3 minor non-blockers per tasks.md frontmatter). All assignments use `.claude/agents/_README.md` roster names exclusively. `/aod.build` may proceed.
