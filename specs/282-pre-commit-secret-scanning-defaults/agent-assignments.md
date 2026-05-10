---
feature: F-5 — Pre-commit Secret-Scanning Defaults
issue: 282
branch: 282-pre-commit-secret-scanning-defaults
initiative: BLP-02 Wave 4+ (5/5 — final)
generated_by: team-lead
generated_date: 2026-05-10
tasks_signoff: APPROVED_WITH_CONCERNS (PM + Architect + Team-Lead)
execution_model: single-maintainer
target_wallclock: 2026-05-10 (Saturday) with 2026-05-11 slack
total_active_envelope: 12-15h
---

# Agent Assignments — F-5 Pre-commit Secret-Scanning Defaults

**Source of truth**: [tasks.md](tasks.md) (37 tasks: T001-T036 + T014a sub-task)
**Wave structure**: 5 waves matching plan §Wave-Sequencing
**Agent registry**: `.claude/agents/_README.md` (validated 2026-05-10 — 13 agents)

This document maps every task ID in `tasks.md` to a specific subagent_type from the registry, organizes them into 5 parallel-execution waves, defines quality gates between waves, and captures execution notes calibrated for single-maintainer Saturday delivery.

---

## 1. Agent Assignment Matrix

### Phase 1: Setup (T001-T002)

| Task ID | Description summary | Agent | Notes |
|---------|---------------------|-------|-------|
| T001 | Verify branch current; rebase on main if upstream drifted | `senior-backend-engineer` | git mechanics — pre-flight before any task |
| T002 | Create draft PR with `feat(282):` title + PRD/spec/plan body links | `senior-backend-engineer` | gh pr create --draft per `.claude/rules/git-workflow.md`; conventional-commit title is HARD requirement |

### Phase 2: Foundational — Wave 1 (T003-T007)

| Task ID | Description summary | Agent | Notes |
|---------|---------------------|-------|-------|
| T003 | Create `.gitleaks.toml` (~50-80 LOC) — `[extend] useDefault`, `[[allowlists]]` v8.25+ schema, 2 custom `[[rules]]` warn-only | `senior-backend-engineer` | TOML config authoring; inline rationale comments mandatory (per AC-10 cross-link to PRECOMMIT_HOOKS.md) |
| T004 | Create `.aod/personalization.env.example` (~10-20 LOC) | `senior-backend-engineer` | Path MUST appear in T003 allow-list; placeholder values only (NO real credentials) |
| T005 | Create `.aod/scripts/bash/precommit-wrap.sh` (~30-60 LOC) — wrapper with FM-5 exit-code-capture pattern | `senior-backend-engineer` | **Pre-Mortem FM-5 spike candidate** — bash quoting around stderr augmentation; covers FR-008 + FR-009 (PM-3 consolidation) |
| T006 | Create `.pre-commit-config.yaml` (~30-50 LOC) — gitleaks rev tag, then autoupdate --freeze to SHA | `senior-backend-engineer` | Depends on T005 (wrapper exists); pre-commit autoupdate freeze step pins SHA in-place |
| T007 | Wave 1 smoke test — install hook, stage fake credential, verify refusal with 4-item stderr | `tester` | Empirical Wave 1 verification — depends on T003-T006 |

### Phase 3-6: User Stories 1-4 — Wave 2 + Wave 3 init.sh (T008-T021)

| Task ID | Description summary | Agent | Notes |
|---------|---------------------|-------|-------|
| T008 | Create fixture directory tree (4 subdirs under `tests/fixtures/gitleaks-rule-interaction/`) | `tester` | Test fixture scaffold |
| T009 | 6 should-fire credential fixtures + header comments naming expected gitleaks rule IDs | `tester` | PM-PLAN-1 carry-forward (rule-ID assertion comments); fixtures #1-#6 |
| T010 | 4 should-NOT-fire placeholder fixtures + allow-list mechanism comments | `tester` | Fixtures #7-#10 |
| T011 | 4 should-NOT-fire path-allow-listed fixtures + fixture #14 PM-PLAN-3 schema-out-of-scope header | `tester` | Fixtures #11-#14; PM-PLAN-3 header on fixture #14 |
| T012 | 2 should-NOT-fire excluded-path fixtures + temp-relocation harness note | `tester` | Fixtures #15-#16 |
| T013 | Test runner `run.sh` (~30-50 LOC) co-located with fixtures | `tester` | Architect CONCERN-1 (HIGH) — bash runner co-located, NOT under tests/scripts/ |
| T014 | pytest matrix test `test_init_precommit_matrix.py` (6 cases × ~5-15min) | `tester` | Architect CONCERN-2 (MEDIUM); pytest convention; uses `run_init_in_clone(timeout_sec=900)` |
| T014a | Update `.github/workflows/tachi-pytest.yml` `paths:` + invocation lock-step | `devops` | F-256 lock-step pattern (KB Entry 3); CI workflow modification |
| T015 | Modify `scripts/init.sh` (~10-20 LOC delta) — opt-in prompt block at line 177-185 region | `senior-backend-engineer` | Bash + raw `read -p` per Q10 ADR-042 §Consequences waiver |
| T016 | Add `pre-commit --version` floor check (>= 3.5.0) to init.sh | `senior-backend-engineer` | Architect CONCERN-3 (MEDIUM); WARN logging on missing/below-floor |
| T017 | Empirically verify FR-004 — 5 init.sh scenarios on fresh clones | `tester` | Empirical AC-6/AC-7 verification; depends on T015+T016 |
| T018 | Verify FR-002 default-deny via T013 runner (fixtures #1-#5 fire) | `tester` | Subsumed under T013 runner; trivial confirmation pass |
| T019 | Empirically verify FR-010/AC-9 existing-adopter no-surprise — pre/post `git pull` state | `tester` | [MANUAL-ONLY]; results to `.aod/results/ac9-existing-adopter-verification.md` |
| T020 | Empirically verify FR-002/AC-4 baseline — `pre-commit run --all-files` zero findings | `tester` | Five Whys per Constitution Principle VIII if any findings appear |
| T021 | Verify placeholder + path-allow-list cases via T013 runner (fixtures #7-#16) | `tester` | Subsumed under T013 runner; confirmation pass |

### Phase 7: Wave 4 — Documentation & ADR (T022-T026)

| Task ID | Description summary | Agent | Notes |
|---------|---------------------|-------|-------|
| T022 | Author `docs/standards/PRECOMMIT_HOOKS.md` (~150-250 LOC, 9 sections) | `senior-backend-engineer` | **§Known-Limitations LOC budget ~30 LOC** — 7 explicit items (CONCERN-3 + PM-PLAN-2 + 5 originals); per-rule rationale catalog cross-links 1:1 with `.gitleaks.toml` per AC-10 |
| T023 | Author `ADR-042-pre-commit-secret-scanning-default.md` (~130-180 LOC) | `senior-backend-engineer` | Status `Proposed` initially; **MUST correct PRD comparison-matrix error: trufflehog runtime is Go, not Python**; 9 alternatives rejected with rationale |
| T024 | Modify `CHANGELOG.md` Unreleased — sibling-h3 entry (NOT under `### Features`) | `senior-backend-engineer` | N-4 carry-forward through F-2/F-3/F-4; KB Entry 4 §Pattern 3 |
| T025 | Modify `README.md` — one-line pointer to PRECOMMIT_HOOKS.md in Security subsection | `senior-backend-engineer` | Q7 resolution; F-3/F-4 placement parity |
| T026 | Update `docs/standards/README.md` index — insert PRECOMMIT_HOOKS.md row alphabetically after CLAUDE_PERMISSIONS.md | `senior-backend-engineer` | Single-row table edit |

### Phase 8: Wave 3 — CI Parity Workflow (T027-T028)

| Task ID | Description summary | Agent | Notes |
|---------|---------------------|-------|-------|
| T027 | Create `.github/workflows/gitleaks.yml` (~25-40 LOC) — gitleaks binary direct, SARIF upload, checksum verify, full-repo scan | `devops` | NOT proprietary `gitleaks-action@v2` (license trap); native binary + checksum; uploads to GitHub Code Scanning via `github/codeql-action/upload-sarif@v3` |
| T028 | Empirically verify FR-007 via PR test — bad-credential push with `--no-verify`, observe GHA fail; cleanup, observe pass | `devops` | Architect A-10 cleanup discipline — bad-credential commit MUST be removed before /aod.deliver merge |

### Phase 9: Wave 5 — Delivery Verification (T029-T036)

| Task ID | Description summary | Agent | Notes |
|---------|---------------------|-------|-------|
| T029 | Pre-merge final verification suite — 5-part: `pre-commit run --all-files`, runner 16/16, pytest 6/6, GHA green, AC-10 catalog parity | `tester` | [MANUAL-ONLY] reviewer cross-check on (e); document in `.aod/results/wave5-pre-merge-verification.md` |
| T030 | /aod.deliver: PR title verify + retitle if needed; `gh pr ready`; `gh pr merge --squash` | `senior-backend-engineer` | Conventional-commit title belt-and-suspenders per `.claude/rules/git-workflow.md` Deliver-stage check |
| T031 | /aod.deliver: post-merge release-please verification within 30s; push empty marker if missing | `senior-backend-engineer` | FR-015/SC-006; `gh pr list --state open --search "release-please"`; document in `.aod/results/release-please-verification-282.md` |
| T032 | /aod.deliver: post-merge `/security` re-scan on F-5 file surface | `tester` | FR-014/AC-16; document in `.aod/results/security-rescan-282.md` |
| T033 | /aod.deliver: file 3 post-merge follow-up Issues (AC-18 + AC-19 + Architect CONCERN-4 pin-bump cadence) | `senior-backend-engineer` | `chore(282):` title prefix to avoid release-please trigger; `--label maintenance` |
| T034 | /aod.deliver: flip ADR-042 status `Proposed` → `Accepted` with post-merge date | `senior-backend-engineer` | F-1/F-2/F-4 ADR-acceptance precedent |
| T035 | /aod.deliver: update memory entries — BLP-02 5/5 closed, BLP-01 cross-ref, LinkedIn-thread 3/3 closed | `senior-backend-engineer` | mcp__second-brain-mcp__update_thought on `project_blp02_enterprise_hardening.md`, etc. |
| T036 | /aod.deliver: regenerate BACKLOG.md via `bash .aod/scripts/bash/backlog-regenerate.sh` | `senior-backend-engineer` | Post-Issue-#282-closure refresh |

**Total**: 37 tasks (T001-T036 + T014a) — 22× `senior-backend-engineer`, 12× `tester`, 3× `devops`.

**Stand-by agents** (NOT assigned to wave-level tasks; invoked only at /aod.deliver boundary or on Pre-Mortem realization):
- `architect` — ADR-042 acceptance review at /aod.deliver (T034 status flip is mechanical; structural review is invoked by /aod.deliver harness)
- `product-manager` — /aod.deliver scope review only
- `debugger` — invoked on FM-5 wrapper failure (T005 stderr augmentation bug) per Pre-Mortem spike contingency
- `code-reviewer` — covered by tasks.md sign-off + draft-PR review surface; not a wave-level assignment

---

## 2. Parallel Execution Waves

### Wave 1 — Foundation: Pre-commit Hook Surface (~3h)

**Tasks**: T001 → T002 → [T003, T004, T005] (parallel) → T006 → T007

**Sequencing**:
1. T001 (branch verify, ~5 min, `senior-backend-engineer`)
2. T002 (draft PR, ~25 min, `senior-backend-engineer`)
3. **PARALLEL** [T003, T004, T005] file-disjoint authoring (~2h, all `senior-backend-engineer`)
   - T003 `.gitleaks.toml` is the longest-running (~50-80 LOC + inline rationale)
   - T005 carries Pre-Mortem FM-5 spike risk (bash quoting around stderr) — budget +60 min if FM-5 realizes
4. T006 `.pre-commit-config.yaml` (~10 min, depends on T005)
5. T007 smoke test (~25 min, `tester`)

**Parallel opportunities**: T003 + T004 + T005 file-disjoint, parallel-safe per tasks.md §Parallel-Opportunities.

### Wave 2 — Verification Surface: Fixtures + Runner + pytest Matrix (~3h)

**Tasks**: [T008, then T009/T010/T011/T012 in parallel] → T013 → T014 (parallel with T015-T017) → T014a

**Sequencing**:
1. T008 fixture directory scaffold (~10 min, `tester`)
2. **PARALLEL** [T009, T010, T011, T012] fixture authoring (~1.5-2h total, all `tester`) — file-disjoint, parallel-safe
3. T013 runner authoring (~30-45 min, `tester`) — depends on T008-T012
4. T014 pytest matrix test (~1.5h, `tester`) — can begin in parallel with T015 (different files); CI runtime ~30-90 min for 6 matrix cases
5. T014a workflow lock-step (~15 min, `devops`) — depends on T014; F-256 KB Entry 3 lesson

**Parallel opportunities**: T009-T012 fixture creation file-disjoint; T014 authoring parallel with Wave 3 init.sh delta authoring (T015).

### Wave 3 — init.sh Delta + CI Parity (~2-3h)

**Tasks**: [T015, T016] (sequential init.sh delta) + T017 (empirical verify) + [T027, T028] (CI workflow + empirical verify)

**Sequencing**:
1. T015 init.sh prompt block + flag handling (~45 min, `senior-backend-engineer`)
2. T016 version-check addition (~30 min, `senior-backend-engineer`) — depends on T015
3. T017 empirical 5-scenario verification (~30-45 min, `tester`) — depends on T015+T016
4. T027 CI workflow authoring (~20-30 min, `devops`) — depends on T003 (`.gitleaks.toml` exists)
5. T028 CI empirical with bad-credential push/cleanup (~30 min, `devops`) — depends on T027

**Cross-cutting**: T018 + T019 + T020 + T021 (verification rollups) execute opportunistically after T013/T017 complete.

### Wave 4 — Documentation & ADR (~3-4h)

**Tasks**: [T022, T023, T024, T025] in parallel → T026

**Sequencing**:
1. **PARALLEL** [T022, T023, T024, T025] file-disjoint authoring (~3-4h total, all `senior-backend-engineer`)
   - T022 PRECOMMIT_HOOKS.md (~150-250 LOC) — longest task in Wave 4
   - T023 ADR-042 (~130-180 LOC) — second-longest
   - T024 CHANGELOG.md sibling-h3 entry (~10 min)
   - T025 README.md one-line pointer (~5 min)
2. T026 standards index update (~5 min, `senior-backend-engineer`) — depends on T022 (filename stable)

**Parallel opportunities**: T022 + T023 + T024 + T025 file-disjoint, parallel-safe per tasks.md §Parallel-Opportunities.

### Wave 5 — Delivery (~30-45min /aod.deliver-time)

**Tasks**: T029 (pre-merge consolidation) → /aod.deliver invocation → T030 → T031 → T032 → [T033, T034, T035, T036] cleanup

**Sequencing**:
1. T029 pre-merge final verification consolidation (~30 min, `tester`)
2. /aod.deliver invocation begins; harness calls `architect` + `product-manager` for scope/structural review
3. T030 PR title verify + squash-merge (~5 min, `senior-backend-engineer`)
4. T031 release-please verification within 30s; empty marker if missing (~5 min, `senior-backend-engineer`)
5. T032 `/security` re-scan (~10 min, `tester`)
6. **PARALLEL** [T033, T034, T035, T036] cleanup (~15 min total, all `senior-backend-engineer`)

**Parallel opportunities**: Wave 5 cleanup tasks T033-T036 file-disjoint at /aod.deliver-time.

---

## 3. Quality Gates Between Waves

| Gate | Wave Boundary | Pass Criteria | Failure Action |
|------|---------------|---------------|----------------|
| **Gate 1** | Wave 1 → Wave 2 | T007 smoke test PASS — fake credential refused with all 4 stderr items (rule ID + file:line + bypass guidance + docs link) | `debugger` agent invoked on T005 wrapper failure (FM-5 realization); spike budget +60 min |
| **Gate 2** | Wave 2 → Wave 3 | T013 runner exits 0 on all 16 fixtures (6 should-fire pass + 10 should-NOT-fire pass) AND T014/T014a workflow lock-step committed in same git revision | `tester` re-authors fixture rule-ID assertions (PM-PLAN-1); F-256 lock-step pattern enforced per KB Entry 3 |
| **Gate 3** | Wave 3 → Wave 4 | T017 init.sh empirical 5/5 scenarios PASS (TTY default-Y, non-TTY skip, --no-precommit skip, --precommit force, missing-pre-commit WARN) AND T028 CI parity PR test verified (bad-credential push fails GHA, cleanup passes GHA) | T015/T016 re-work; FM-3 (init.sh prompt regression) realization triggers `debugger` |
| **Gate 4** | Wave 4 → Wave 5 | T029 pre-merge verification consolidation PASS — 5 parts: (a) `pre-commit run --all-files` zero findings, (b) runner 16/16, (c) pytest 6/6, (d) GHA green, (e) AC-10 catalog parity reviewer cross-check | T029 5-part suite must pass IN ORDER; reviewer cross-check on (e) is [MANUAL-ONLY] — `architect` review at /aod.deliver covers structural validity |
| **Gate 5** | Wave 5 → /aod.deliver close | T030 PR ready + squash-merge SUCCESS AND T031 release-please PR opens within 30s (or empty marker pushed) | If release-please skips: empty `feat(282):` marker per `.claude/rules/git-workflow.md` Deliver-stage post-merge verification (F-212 incident precedent) |

---

## 4. Time Estimates per Wave

Calibrated against Team-Lead `team-lead-tasks-282.md` §Single-Maintainer-Realistic-Ordering breakdown for 2026-05-10 single-maintainer envelope.

| Wave | Cumulative | Wave Span | Active Hours | Calendar Notes |
|------|-----------|-----------|--------------|----------------|
| Wave 1 | ~3h | ~3h | T001 (5 min) + T002 (25 min) + [T003+T004+T005 parallel] (~2h) + T006 (10 min) + T007 (25 min) | Foundation surface; parallel opportunity in T003-T005 |
| Wave 2 | ~3h | ~6h | T008 (10 min) + [T009-T012 parallel] (~1.5h) + T013 (~45 min) + T014 (~1.5h auth + ~30-90 min CI) + T014a (~15 min) | Verification surface; T014 pytest CI runtime can extend wall-clock without adding active maintainer time |
| Wave 3 | ~2-3h | ~9h | T015 (~45 min) + T016 (~30 min) + T017 (~30-45 min) + T027 (~20-30 min) + T028 (~30 min) | init.sh + CI; T028 cleanup discipline is HARD requirement before /aod.deliver |
| Wave 4 | ~3-4h | ~12-13h | [T022 + T023 + T024 + T025 parallel] (~3-4h) + T026 (~5 min) | Docs + ADR; T022 §Known-Limitations LOC budget ~30 LOC (7 explicit items per CONCERN-3 + PM-PLAN-2 + 5 originals) |
| Wave 5 | ~30-45 min | ~12-15h | T029 (~30 min) + /aod.deliver (T030-T036, ~15-30 min total) | Delivery; /aod.deliver-time tasks compressed |

**Total active envelope**: ~12-15h matching `team-lead-tasks-282.md` calibration. Wall-clock target 2026-05-10 (Saturday) with 2026-05-11 slack pre-booked.

**Envelope-hit probability** (per `team-lead-tasks-282.md`):
- ~75% for 12-15h tasks.md envelope (with slack)
- ~70% for 2026-05-10 wall-clock with 2026-05-11 slack
- Material downward revision from PRD A-1 (~70%) and PRD A-5 (~80%) — driven by carry-forward concerns inflating ~1-2h: T014a workflow lock-step (~30 min) + T016 version check (~30 min) + T022 §Known-Limitations expansion (~30 min) + T009 fixture header comments (~10 min)

---

## 5. Execution Notes

### Single-Maintainer Execution Model

This feature is executed by a **single maintainer** (no orchestrator agent) on Saturday 2026-05-10 with 2026-05-11 slack already booked. No multi-agent parallel wave orchestration is used; the `senior-backend-engineer`, `tester`, and `devops` assignments are **role-disambiguation labels** for the single human-in-the-loop maintainer to invoke the correct subagent persona for each task type — NOT independent concurrent execution.

**Implication**: Wave-level parallelism (e.g., T003+T004+T005 in Wave 1, T009-T012 in Wave 2, T022-T025 in Wave 4) is **opportunistic file-disjoint task batching** within a single maintainer session — useful for context efficiency and Claude Code multi-file edit batching, but does NOT compress wall-clock by 4x. The ~12-15h envelope assumes serial-with-batching execution.

**Why no orchestrator**: Single-day, single-maintainer feature with 37 tasks of mixed type; orchestrator overhead exceeds wave-coordination benefit. F-2/F-3/F-4 precedents all used single-maintainer execution; F-5 follows the same pattern.

### Pre-Mortem FM-5 Spike Budget Allocation

**FM-5** (Wrapper script bash quoting bug around stderr augmentation) is the highest-risk failure mode for Wave 1 per `team-lead-tasks-282.md` §Pre-Mortem-Findings.

**Budget allocation**:
- Base T005 estimate: ~30-45 min
- FM-5 spike contingency: +60 min if exit-code-capture pattern fails on first author
- Trigger: T007 smoke test rejects (commit succeeds when it should refuse, OR stderr items missing)
- Recovery action: invoke `debugger` agent to apply 5 Whys on bash quoting; common root causes:
  - Exit code captured AFTER stderr augmentation (gitleaks rc lost in `>&2` redirect)
  - Subshell creation by `{ ... } >&2` swallows `set -e`
  - Heredoc quoting expanding `$rc` prematurely

**Mitigation in tasks.md**: T005 explicitly mandates the `gitleaks ...; rc=$?; { stderr augmentation; } >&2; exit $rc` pattern from `.aod/scripts/bash/init-input.sh` precedent. If the pattern is followed verbatim, FM-5 spike risk drops to ~20%. If T005 author improvises, spike risk rises to ~50%.

**Spike budget total**: 60 min worst case; 0 min best case. Already incorporated into the 12-15h envelope upper bound.

### T022 §Known-Limitations LOC Budget Guidance

**Recommended LOC budget**: ~30 LOC for §Known-Limitations section within the ~150-250 LOC PRECOMMIT_HOOKS.md total.

**Rationale**: 7 explicit items must be enumerated:
1. `--no-verify` honest disclosure (~3 LOC)
2. Pre-commit framework distribution risk (~3 LOC)
3. Custom rule limits (~3 LOC)
4. Staged-content-only scope (~3 LOC)
5. Post-history-rewrite leaks (~3 LOC)
6. GH-Actions-secret-in-logs out of scope (~3 LOC)
7. **Pre-commit framework version drift** with explicit minimum >= v3.5.0 floor + justification (per Architect CONCERN-3 carry-forward) — longer item ~6-8 LOC: "tachi's `.pre-commit-config.yaml` schema requires v3.5.0+ for stable hook resolution; below this version, hook installation may silently partial-install or runtime-crash on first invocation."

**Total**: 7 × ~3 LOC + 1 × ~6-8 LOC + section header/intro (~3 LOC) = ~30 LOC.

**Anti-pattern**: Compressing §Known-Limitations to <20 LOC sacrifices honest-disclosure intent (FR-005/AC-10 SecOps reviewer audit needs); expanding to >40 LOC bloats the operator handbook beyond the 250-LOC ceiling and pushes the per-rule rationale catalog or §Adopter-Customization out of budget.

### Calibration Caveats (Non-Blocking)

Per `team-lead-tasks-282.md` 6 Pre-Mortem failure modes + 4 non-blocking recommendations:
- **T014 pytest matrix**: 6 cases × ~5-15min runtime via `run_init_in_clone(timeout_sec=900)` may need `pytest.mark.slow` if total runtime exceeds 30 min wall-clock; **not blocking — recommendation only**
- **T029 pre-merge verification**: AC-10 reviewer cross-check on per-rule rationale catalog parity may underrun the ~30-min budget if reviewer is fluent in gitleaks rule-ID conventions; **not blocking — recommendation only**

These are execution-calibration recommendations; no tasks.md revision required. Maintainer should monitor and adjust during execution.

---

## 6. References

- Source tasks: [tasks.md](tasks.md)
- Plan: [plan.md](plan.md)
- Spec: [spec.md](spec.md)
- PRD: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
- Agent registry: [.claude/agents/_README.md](../../.claude/agents/_README.md)
- Team-Lead tasks review: [.aod/results/team-lead-tasks-282.md](../../.aod/results/team-lead-tasks-282.md)
- Architect tasks review: [.aod/results/architect-tasks-282.md](../../.aod/results/architect-tasks-282.md)
- PM tasks review: [.aod/results/product-manager-tasks-282.md](../../.aod/results/product-manager-tasks-282.md)
- F-3 agent-assignments precedent: [specs/272-security-md-disclosure/agent-assignments.md](../272-security-md-disclosure/agent-assignments.md) (if present)
- F-4 agent-assignments precedent: [specs/277-claude-permissions-baseline/agent-assignments.md](../277-claude-permissions-baseline/agent-assignments.md) (if present)
- Git workflow: [.claude/rules/git-workflow.md](../../.claude/rules/git-workflow.md) (conventional-commit PR titles, draft-PR lifecycle, post-merge release-please verification)
