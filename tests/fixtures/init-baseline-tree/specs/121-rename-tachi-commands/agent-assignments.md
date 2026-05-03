# Agent Assignments: Rename Tachi Commands to tachi.* Namespace

**Feature**: 121 | **Date**: 2026-04-09 | **Tasks**: 72
**Strategy**: Single orchestrator for atomicity (FR-016), parallel sub-agents within waves.

---

## Execution Strategy

**Primary executor**: `orchestrator` owns the full lifecycle, sequencing phases and enforcing quality gates between them.

**Sub-agents per wave**: `senior-backend-engineer` handles all file renames, content edits, script modifications, and markdown/YAML updates. `tester` handles all grep verifications and acceptance checks.

**Rationale**: This is a file-rename and content-update project. All 72 tasks involve markdown, YAML, bash, or Typst file operations. `senior-backend-engineer` is the correct agent for config files, markdown creation/editing, and script work. No frontend, security, or architecture agents are needed for execution.

---

## Agent Assignment Matrix

| Task ID | Agent | Parallel | Phase | Notes |
|---------|-------|----------|-------|-------|
| T001 | senior-backend-engineer | - | 1 | Prototype rename |
| T002 | senior-backend-engineer | - | 1 | Prototype cross-ref update |
| T003 | tester | - | 1 | Grep verification |
| T004 | tester | - | 1 | Command resolution test |
| T005 | senior-backend-engineer | P | 2 | File rename |
| T006 | senior-backend-engineer | P | 2 | File rename |
| T007 | senior-backend-engineer | P | 2 | File rename |
| T008 | senior-backend-engineer | P | 2 | File rename |
| T009 | senior-backend-engineer | - | 2 | New file creation |
| T010 | senior-backend-engineer | P | 2 | Adapter rename |
| T011 | senior-backend-engineer | P | 2 | Adapter rename |
| T012 | senior-backend-engineer | P | 2 | Adapter rename |
| T013 | senior-backend-engineer | P | 2 | Adapter rename |
| T014 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T015 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T016 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T017 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T018 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T019 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T020 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T021 | senior-backend-engineer | P | 2 | Internal cross-ref |
| T022 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T023 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T024 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T025 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T026 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T027 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T028 | senior-backend-engineer | P | 3 | Tier 1 slash refs (11 agent files) |
| T029 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T030 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T031 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T032 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T033 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T034 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T035 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T036 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T037 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T038 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T039 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T040 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T041 | senior-backend-engineer | P | 3 | Tier 1 slash refs |
| T042 | senior-backend-engineer | P | 3 | Tier 2 path refs |
| T043 | senior-backend-engineer | P | 3 | Tier 2 path refs |
| T044 | senior-backend-engineer | P | 3 | Tier 2 path refs |
| T045 | senior-backend-engineer | P | 3 | Tier 2 path refs |
| T046 | senior-backend-engineer | - | 3 | Tier 3 manual review |
| T047 | senior-backend-engineer | - | 3 | Tier 3 manual review |
| T048 | senior-backend-engineer | - | 3 | Tier 3 manual review |
| T049 | senior-backend-engineer | - | 4 | Install script cleanup |
| T050 | senior-backend-engineer | - | 4 | Deprecated files list |
| T051 | senior-backend-engineer | - | 4 | Cleanup loop impl |
| T052 | senior-backend-engineer | P | 4 | Manifest table |
| T053 | senior-backend-engineer | P | 4 | Manifest machine section |
| T054 | senior-backend-engineer | P | 4 | Manifest file count |
| T055 | senior-backend-engineer | P | 4 | CHANGELOG entry |
| T056 | senior-backend-engineer | P | 4 | CLAUDE.md refs |
| T057 | senior-backend-engineer | P | 4 | README.md refs |
| T058 | senior-backend-engineer | P | 4 | Developer guide |
| T059 | senior-backend-engineer | P | 4 | Consumer guide |
| T060 | senior-backend-engineer | P | 4 | Consumer guide (AOD) |
| T061 | senior-backend-engineer | P | 4 | Consumer guide (research) |
| T062 | senior-backend-engineer | P | 4 | Dev guide prompt |
| T063 | senior-backend-engineer | P | 4 | Remaining docs |
| T064 | tester | - | 5 | Grep: /threat-model |
| T065 | tester | - | 5 | Grep: /risk-score |
| T066 | tester | - | 5 | Grep: /compensating-controls |
| T067 | tester | - | 5 | Grep: /infographic (regex) |
| T068 | tester | - | 5 | Grep: /security-report |
| T069 | tester | - | 5 | File existence check |
| T070 | tester | - | 5 | Manifest verification |
| T071 | tester | - | 5 | Adapter VERSION check |
| T072 | tester | - | 5 | Example spot-check |

---

## Parallel Execution Waves

### Wave 1: Prototype Gate (Phase 1)

**Tasks**: T001-T004 (4 tasks, sequential)
**Agent**: orchestrator -> senior-backend-engineer (T001-T002), tester (T003-T004)
**Estimate**: 5 minutes
**Parallelism**: None (sequential validation gate)

```
T001 (rename) -> T002 (update refs) -> T003 (grep verify) -> T004 (invoke verify)
```

**Quality Gate**: T003 returns zero matches for old name. T004 confirms command resolves.
**Exit Criteria**: Prototype validated. Proceed to bulk renames.

---

### Wave 2: Command File Renames (Phase 2)

**Tasks**: T005-T021 (17 tasks)
**Agent**: orchestrator -> senior-backend-engineer (all)
**Estimate**: 15 minutes
**Parallelism**: 3 sub-waves

```
Sub-wave 2a: T005, T006, T007, T008 (parallel - primary renames)
             T009 (new file creation, can run with renames)
Sub-wave 2b: T010, T011, T012, T013 (parallel - adapter renames)
Sub-wave 2c: T014, T015, T016, T017, T018, T019, T020, T021 (parallel - internal cross-refs)
```

**Quality Gate**: All 6 `tachi.*` files exist in `.claude/commands/`. Old unprefixed files are gone. `ls .claude/commands/tachi.*` returns exactly 6 results.
**Exit Criteria**: Wave 1 file renames complete. Ready for cross-reference sweep.

---

### Wave 3: Cross-Reference Updates (Phase 3)

**Tasks**: T022-T048 (27 tasks)
**Agent**: orchestrator -> senior-backend-engineer (all)
**Estimate**: 30 minutes
**Parallelism**: 3 sub-waves by tier

```
Sub-wave 3a: T022-T041 (20 tasks, parallel - Tier 1 slash refs, all independent file surfaces)
Sub-wave 3b: T042-T045 (4 tasks, parallel - Tier 2 path-qualified refs)
Sub-wave 3c: T046-T048 (3 tasks, sequential - Tier 3 manual review, requires human judgment)
```

**Quality Gate**: Grep for old slash command patterns across codebase returns zero matches outside immutable artifacts (`specs/*/`, `docs/product/02_PRD/`).
**Exit Criteria**: All 3 tiers complete. Cross-reference integrity confirmed.

---

### Wave 4: Infrastructure and Documentation (Phase 4)

**Tasks**: T049-T063 (15 tasks)
**Agent**: orchestrator -> senior-backend-engineer (all)
**Estimate**: 20 minutes
**Parallelism**: 2 sub-waves

```
Sub-wave 4a: T049, T050, T051 (sequential - install script, order-dependent)
             T052, T053, T054 (parallel with each other, sequential after T049-T051 - manifest)
Sub-wave 4b: T055-T063 (9 tasks, parallel - documentation updates, all independent files)
```

Note: Sub-wave 4b can start in parallel with Sub-wave 4a since documentation tasks are independent of install script changes.

**Quality Gate**: `scripts/install.sh` contains deprecated-file cleanup section. `INSTALL_MANIFEST.md` lists 6 `tachi.*` command files. CHANGELOG contains migration mapping table.
**Exit Criteria**: Install script, manifest, and all documentation updated.

---

### Wave 5: Verification and Polish (Phase 5)

**Tasks**: T064-T072 (9 tasks, sequential)
**Agent**: orchestrator -> tester (all)
**Estimate**: 10 minutes
**Parallelism**: T064-T068 can run in parallel (independent grep checks). T069-T072 sequential.

```
Sub-wave 5a: T064, T065, T066, T067, T068 (parallel - grep verifications)
Sub-wave 5b: T069, T070, T071, T072 (sequential - structural verifications)
```

**Quality Gate**: All grep checks return zero matches. All 6 command files confirmed. Manifest verified. Examples spot-checked.
**Exit Criteria**: Feature verified. Ready for PR.

---

## Wave Summary

| Wave | Phase | Tasks | Parallel | Agent(s) | Estimate |
|------|-------|-------|----------|----------|----------|
| 1 | 1 (Prototype) | 4 | 0 | senior-backend-engineer, tester | 5 min |
| 2 | 2 (Renames) | 17 | 13 | senior-backend-engineer | 15 min |
| 3 | 3 (Cross-refs) | 27 | 24 | senior-backend-engineer | 30 min |
| 4 | 4 (Infra+Docs) | 15 | 12 | senior-backend-engineer | 20 min |
| 5 | 5 (Verify) | 9 | 5 | tester | 10 min |
| **Total** | | **72** | **54** | | **80 min** |

---

## Agent Workload Distribution

| Agent | Task Count | Phases | Load |
|-------|-----------|--------|------|
| orchestrator | 72 (coordination) | 1-5 | Primary executor, sequences waves |
| senior-backend-engineer | 59 (execution) | 1-4 | All file operations |
| tester | 13 (verification) | 1, 5 | Grep checks, acceptance tests |
| code-reviewer | 1 (post-build) | Post-5 | PR review before merge |

No agent exceeds 80% load. `senior-backend-engineer` is the heaviest-loaded executor but tasks are small file edits (median <2 minutes each). Parallel execution within waves reduces wall-clock time.

---

## Timeline Estimates

| Scenario | Duration | Notes |
|----------|----------|-------|
| Optimistic | 60 min | Maximum parallelism, no rework |
| Realistic | 80 min | Some Tier 3 manual review iteration |
| Pessimistic | 120 min | Tier 3 edge cases, T067 regex refinement, rework |

**Confidence**: HIGH (85%). This is a mechanical rename project with well-defined patterns. The tiered pattern strategy reduces risk of output artifact corruption.

---

## Orchestrator Handoff

**Feasibility**: APPROVED
**Tasks file**: `specs/121-rename-tachi-commands/tasks.md`
**Wave strategy**: 5 waves, sequential phases, parallel within waves
**Agent assignments**: senior-backend-engineer (execution), tester (verification), code-reviewer (post-PR)
**Atomicity requirement**: All 72 tasks must complete before single PR to main (FR-016)
**Critical path**: Wave 1 (prototype) -> Wave 2 (renames) -> Wave 3 (cross-refs) -> Wave 5 (verify)
**Partial overlap**: Wave 4 documentation can start during Wave 3 Tier 1/2 execution
