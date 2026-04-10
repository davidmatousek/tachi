# Agent Assignments — Feature 136: MAESTRO Canonical Layer Correctness Fix

**Feature ID**: 136-maestro-canonical-layer
**Generated**: 2026-04-10
**Team Lead**: team-lead agent
**Source**: `specs/136-maestro-canonical-layer/tasks.md` (44 tasks)
**Plan Reference**: `specs/136-maestro-canonical-layer/plan.md` (4-wave execution)
**Prior Review**: APPROVED_WITH_CONCERNS — all high-impact concerns addressed by orchestrator

---

## 1. Workload Distribution (Plan Reference)

| Agent                     | Share | Scope |
|---------------------------|-------|-------|
| `senior-backend-engineer` | 60%   | Wave 0 discovery (T001-T010), Wave 1 foundation edits (T011-T024), W2-T32 agentic-app regeneration, W3 CHANGELOG + release-please verification |
| `devops`                  | 20%   | W2-T025 through W2-T029 PDF baseline regeneration (5 examples with `SOURCE_DATE_EPOCH=1700000000`) |
| `tester`                  | 15%   | W2-T030 and W2-T031 pytest fixture/golden updates; W3-T033/T034/T035 full-suite validation runs |
| `code-reviewer`           | 5%    | W3-T041a pre-commit review of 44-task diff before final sign-off |

**Load balance**: No single agent exceeds 60% loading. senior-backend-engineer is the anchor agent due to the text-editing nature of the work (canonical rename across 14 foundation files + downstream propagation). devops/tester/code-reviewer are wave-scoped.

---

## 2. Agent Assignment Matrix (T001-T044)

All agent names below are **exact matches** from `.claude/agents/_README.md`. No invented labels.

### Wave 0 — Discovery (10 tasks)

| Task  | Agent                   | Description                                                       | Parallel? |
|-------|-------------------------|-------------------------------------------------------------------|-----------|
| T001  | senior-backend-engineer | Bootstrap branch `136-maestro-canonical-layer` from main          | [P]       |
| T002  | senior-backend-engineer | Grep for old layer name occurrences across repository             | [P]       |
| T003  | senior-backend-engineer | Enumerate affected schemas (schemas/finding.yaml, etc.)           | [P]       |
| T004  | senior-backend-engineer | Enumerate affected shared references (maestro-layers-shared.md)   | [P]       |
| T005  | senior-backend-engineer | Enumerate affected orchestrator/pipeline scripts                  | [P]       |
| T006  | senior-backend-engineer | Enumerate affected agents (report, infographic, orchestrator)     | [P]       |
| T007  | senior-backend-engineer | Enumerate affected examples output files                          | [P]       |
| T008  | senior-backend-engineer | Enumerate affected tests/fixtures/goldens                         | [P]       |
| T009  | senior-backend-engineer | Aggregate discovery into `discovery-report.md` with file count    | Sequential|
| T010  | senior-backend-engineer | Commit discovery report, verify file count ≤45                    | Sequential|

### Wave 1 — Foundation (14 tasks, strict sequential)

| Task  | Agent                   | Description                                                       |
|-------|-------------------------|-------------------------------------------------------------------|
| T011  | senior-backend-engineer | Update `schemas/finding.yaml` enum values (canonical layer names) |
| T012  | senior-backend-engineer | Bump `schema_version` with backward-compat note                   |
| T013  | senior-backend-engineer | Rewrite `.claude/skills/tachi-shared/references/maestro-layers-shared.md` |
| T014  | senior-backend-engineer | Update `_compute_trust_zones()` layer keyword mappings            |
| T015  | senior-backend-engineer | Update orchestrator Phase 1 classification keywords               |
| T016  | senior-backend-engineer | Update risk-scorer layer inheritance                              |
| T017  | senior-backend-engineer | Update control-analyzer MAESTRO layer lookups                     |
| T018  | senior-backend-engineer | Update threat-report narrative layer references                  |
| T019  | senior-backend-engineer | Update ~5 infographic extraction touchpoints                     |
| T020  | senior-backend-engineer | Update infographic agent persona reference                        |
| T021  | senior-backend-engineer | Update report-assembler layer assembly                            |
| T022  | senior-backend-engineer | Update SARIF 2.1.0 tag generation for canonical names             |
| T023  | senior-backend-engineer | Update `.claude/commands/tachi.threat-model.md` layer table       |
| T024  | senior-backend-engineer | Update `docs/architecture/` cross-references (VERIFY LINE NUMBERS before editing) |

### Wave 2 — Regeneration (8 tasks, 3 concurrent agents)

| Task  | Agent                   | Description                                                       | Concurrency Group |
|-------|-------------------------|-------------------------------------------------------------------|-------------------|
| T025  | devops                  | Regenerate `examples/web-app/security-report.pdf.baseline` with `SOURCE_DATE_EPOCH=1700000000` | devops |
| T026  | devops                  | Regenerate `examples/microservices/security-report.pdf.baseline` | devops |
| T027  | devops                  | Regenerate `examples/ascii-web-api/security-report.pdf.baseline` | devops |
| T028  | devops                  | Regenerate `examples/mermaid-agentic-app/security-report.pdf.baseline` | devops |
| T029  | devops                  | Regenerate `examples/free-text-microservice/security-report.pdf.baseline` | devops |
| T030  | tester                  | Update `tests/scripts/fixtures/exec_arch/` with canonical layer strings | tester |
| T031  | tester                  | Update `tests/scripts/fixtures/golden/` JSON files               | tester |
| T032  | senior-backend-engineer | Regenerate agentic-app example outputs (threats.md + downstream: risk-scores, controls, report, infographic, PDF) — longest task (~45-60 min) | sbe |

**Concurrency**: 3 parallel agents (devops for PDF baselines, tester for fixtures/goldens, senior-backend-engineer for agentic-app). Not 8-way parallel despite [P] markers on all Wave 2 tasks — the three logical groups run independently but tasks within each group remain sequential due to shared working directories and tooling state.

### Wave 3 — Validation + Documentation (10 tasks, strict sequential)

| Task  | Agent                   | Description                                                       |
|-------|-------------------------|-------------------------------------------------------------------|
| T033  | tester                  | Run full pytest suite (`make test`) — confirm 150+ tests pass    |
| T034  | tester                  | Run baseline byte-comparison test for 5 non-agentic examples     |
| T035  | tester                  | Run coverage report, verify no regression                        |
| T036  | **HUMAN REQUIRED**      | Visual QA of regenerated agentic-app PDF + infographic JPEG      |
| T037  | senior-backend-engineer | Run `/aod.analyze` cross-artifact consistency check              |
| T038  | senior-backend-engineer | Final grep sweep — zero occurrences of old layer names           |
| T039  | senior-backend-engineer | Draft CHANGELOG entry under v4.9.x unreleased section            |
| T040  | senior-backend-engineer | Verify release-please metadata (no manual version bump needed)   |
| T041  | senior-backend-engineer | Stage all changes, prepare commit groups                         |
| T041a | code-reviewer           | Pre-commit review of 44-task diff (5% workload envelope)         |
| T042  | senior-backend-engineer | Split into 4 atomic commits within single PR: (1) foundation rename, (2) regeneration outputs, (3) fixtures/goldens, (4) CHANGELOG + docs |

### Polish — Post-Merge (2 tasks)

| Task  | Agent                   | Description                                                       | Trigger |
|-------|-------------------------|-------------------------------------------------------------------|---------|
| T043  | senior-backend-engineer | Post-merge smoke test against `main` HEAD                        | Post-merge |
| T044  | senior-backend-engineer | (Optional) File backlog entry for cross-template layer consistency | Deferrable |

---

## 3. Parallel Execution Waves

### Wave 0 — Discovery (10 tasks)
- **Entry criteria**: Branch `136-maestro-canonical-layer` created from latest `main`
- **Execution**: T001 bootstrap, then T002-T008 run in parallel (7-way [P]), then T009-T010 sequential aggregation
- **Exit criteria**: `discovery-report.md` committed; file count ≤45 confirmed

### Wave 1 — Foundation (14 tasks, strict sequential)
- **Entry criteria**: W0 exit gate passed
- **Execution**: T011 through T024 executed one-at-a-time by single senior-backend-engineer thread. Sequential ordering is deliberate — edits cascade through schema → shared refs → scripts → agents → commands → architecture docs, and each layer depends on the prior layer being canonical.
- **Exit criteria**: Grep across 14 foundation files returns zero occurrences of old layer names

### Wave 2 — Regeneration (8 tasks, 3 concurrent agents)
- **Entry criteria**: W1 exit gate passed (foundation is canonical)
- **Execution**: Three agents run in parallel concurrency groups:
  - **devops thread**: T025 → T026 → T027 → T028 → T029 (PDF baselines, sequential within group)
  - **tester thread**: T030 → T031 (fixtures/goldens, sequential within group)
  - **senior-backend-engineer thread**: T032 (longest task, standalone)
- **Wall-clock duration** determined by longest critical path: T032 at ~45-60 minutes
- **Exit criteria**: All regenerated files show canonical layer names; byte-determinism confirmed for 5 baselines

### Wave 3 — Validation + Documentation (10 tasks, strict sequential)
- **Entry criteria**: W2 exit gate passed (all outputs canonical)
- **Execution**: T033-T035 test runs sequential; T036 HUMAN REQUIRED gate; T037-T042 documentation + commit prep sequential. T041a inserted as code-reviewer gate before final commits.
- **Exit criteria**: All tests green, CHANGELOG committed, `/aod.analyze` returns clean, code-reviewer signed off

### Polish
- **T043** post-merge smoke test (runs after PR merge to main)
- **T044** optional backlog entry (non-blocking, deferrable)

---

## 4. Quality Gates Between Waves

### Wave 0 Exit Gate
- [ ] `specs/136-maestro-canonical-layer/discovery-report.md` committed to feature branch
- [ ] Enumerated affected file count documented and ≤45
- [ ] Discovery report references all 7 enumeration categories (schemas, shared refs, scripts, agents, examples, tests, architecture docs)
- [ ] Branch protection confirmed — feature branch, not `main`

### Wave 1 Exit Gate
- [ ] Grep pattern matching old MAESTRO layer names returns **zero** results across the 14 foundation files touched in T011-T024
- [ ] `schemas/finding.yaml` schema_version bumped with backward-compatibility note
- [ ] `maestro-layers-shared.md` rewritten with canonical taxonomy
- [ ] Orchestrator, risk-scorer, control-analyzer, threat-report, infographic, report-assembler all updated
- [ ] No downstream regeneration has started yet (clean foundation before W2 launches)

### Wave 2 Exit Gate
- [ ] All 5 `.baseline` PDFs regenerated with `SOURCE_DATE_EPOCH=1700000000` (byte-determinism confirmed via diff of two consecutive builds)
- [ ] agentic-app example outputs regenerated in full (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic JPEG, security-report.pdf)
- [ ] pytest fixtures in `tests/scripts/fixtures/exec_arch/` show canonical layer strings
- [ ] golden JSON files in `tests/scripts/fixtures/golden/` updated with canonical taxonomy
- [ ] No old layer name appears in any regenerated artifact (full-repo grep sweep)

### Wave 3 Exit Gate
- [ ] `make test` returns green across 150+ tests
- [ ] Baseline byte-comparison test passes for 5 non-agentic examples (byte-identical to committed baselines)
- [ ] pytest coverage report shows no regression
- [ ] **Human QA** of agentic-app regenerated PDF + infographic JPEG completed (T036)
- [ ] `/aod.analyze` returns clean across spec/plan/tasks
- [ ] CHANGELOG.md updated under v4.9.x unreleased section
- [ ] release-please metadata unchanged (no manual `.release-please-manifest.json` edits)
- [ ] code-reviewer pre-commit review (T041a) returned APPROVED or APPROVED_WITH_CONCERNS
- [ ] All changes staged into 4 atomic commits within single PR

---

## 5. Time Estimates Per Wave

Honest estimates, not optimistic. Includes edit time, verification time, and context switching.

| Wave   | Task Count | Wall-Clock Duration    | Notes |
|--------|-----------:|------------------------|-------|
| Wave 0 | 10         | **1-2 hours**          | Parallel discovery keeps this short; main cost is grep-and-enumerate across multiple domain areas |
| Wave 1 | 14         | **3-4 hours**          | Sequential careful editing. Each foundation file must be verified before next edit. T024 requires line-number verification before editing `docs/architecture/` cross-references |
| Wave 2 | 8          | **1-1.5 hours**        | Parallel execution with 3 concurrent agents. Wall-clock bounded by longest task T032 (~45-60 min) for agentic-app full regeneration including PDF assembly |
| Wave 3 | 10         | **2-3 hours**          | Validation, HUMAN gate (T036), CHANGELOG, release-please verification, commit splitting into 4 atomic commits, code-reviewer pre-commit gate |

**Pure execution total**: **~9.25-10.5 hours**

**Realistic delivery**: **2-3 working days** including:
- Triad review cycles (pre-merge PM/Architect/Team-Lead sign-offs)
- Context switches between editing, testing, visual QA
- HUMAN REQUIRED gate at T036 (may introduce calendar delay)
- code-reviewer turnaround at T041a
- PR review cycle before merge

---

## 6. Blockers and Risk Mitigation

| Risk | Mitigation |
|------|------------|
| T024 line-number drift after editing earlier W1 tasks | Task flagged — senior-backend-engineer must re-verify line numbers immediately before editing architecture cross-references |
| T032 longest-task bottleneck in Wave 2 | Isolated to single agent thread; devops + tester run in parallel, so wall-clock not blocked |
| T036 HUMAN gate stalls Wave 3 | Schedule human QA slot at W2 exit to avoid idle time; regenerated agentic-app artifacts must be visually inspected before commit |
| Old layer name occurrences missed in Wave 1 | W1 exit gate enforces repository-wide grep returning zero results |
| Byte-determinism failure in T034 | Fallback: regenerate baseline with fresh `SOURCE_DATE_EPOCH=1700000000` environment, document in CHANGELOG if root cause is upstream tooling change |
| release-please version bump conflicts | T040 verifies no manual manifest edits; release-please workflow handles v4.9.x tagging automatically on merge |

---

## 7. Sign-off Authority

| Artifact                | Approver          | Status |
|-------------------------|-------------------|--------|
| Feasibility             | team-lead         | APPROVED (this document) |
| Agent Assignments       | team-lead         | APPROVED (this document) |
| tasks.md (prior review) | team-lead         | APPROVED_WITH_CONCERNS (all resolved by orchestrator) |
| Final phase sign-off    | team-lead         | Deferred to W3 exit validation |

---

**Agent Registry**: All agents referenced above are valid entries in `.claude/agents/_README.md`. No invented labels used.

**End of Agent Assignments**
