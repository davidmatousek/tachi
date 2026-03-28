# Agent Assignments: Quantitative Risk Scoring

**Feature**: 035-quantitative-risk-scoring
**Generated**: 2026-03-27
**Total Tasks**: 29
**Estimated Duration**: 5.5h (optimistic) / 7h (realistic) / 9.5h (pessimistic)

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001 | `senior-backend-engineer` | Schema/YAML file creation |
| T002 | `senior-backend-engineer` | Agent markdown file creation |
| T003 | `senior-backend-engineer` | Template markdown file creation |
| T004 | `senior-backend-engineer` | Agent section authoring (threat parsing) |
| T005 | `senior-backend-engineer` | Agent section authoring (SARIF parsing) |
| T006 | `senior-backend-engineer` | SARIF template JSON structure |
| T007 | `senior-backend-engineer` | Agent section authoring (CVSS scoring) |
| T008 | `senior-backend-engineer` | Agent section authoring (exploitability) |
| T009 | `senior-backend-engineer` | Agent section authoring (scalability) |
| T010 | `senior-backend-engineer` | Agent section authoring (composite calc) |
| T011 | `senior-backend-engineer` | Agent section authoring (governance fields) |
| T012 | `senior-backend-engineer` | Agent section authoring (markdown output) |
| T013 | `senior-backend-engineer` | Agent section authoring (SARIF output) |
| T014 | `senior-backend-engineer` | Template content population |
| T015 | `senior-backend-engineer` | Template content population |
| T016 | `senior-backend-engineer` | Agent section authoring (trust zones) |
| T017 | `senior-backend-engineer` | Agent section authoring (reachability) |
| T018 | `senior-backend-engineer` | Agent section update (composite) |
| T019 | `senior-backend-engineer` | Template content authoring (methodology) |
| T020 | `senior-backend-engineer` | Command markdown file creation |
| T021 | `senior-backend-engineer` | File copy (adapter agent) |
| T022 | `senior-backend-engineer` | File copy (adapter command) |
| T023 | `senior-backend-engineer` | Reference doc update (SARIF) |
| T024 | `senior-backend-engineer` | Schema file update |
| T025 | `senior-backend-engineer` | Example output generation |
| T026 | `senior-backend-engineer` | Example output generation |
| T027 | `security-analyst` | Security-domain score validation |
| T028 | `code-reviewer` | Cross-format consistency review |
| T029 | `tester` | End-to-end command validation |

## Parallel Execution Waves

### Wave 1: Setup (Phase 1)
**Duration**: ~30 min | **Gate**: Schema + skeleton files exist

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 1a | T001 | `senior-backend-engineer` | Sequential (schema first) |
| 1b | T002 | `senior-backend-engineer` | [P] after T001 |
| 1c | T003 | `senior-backend-engineer` | [P] after T001 |

### Wave 2: Foundation (Phase 2)
**Duration**: ~45 min | **Gate**: Agent can parse both input formats

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 2a | T004 | `senior-backend-engineer` | Sequential |
| 2b | T005 | `senior-backend-engineer` | [P] with T004 |
| 2c | T006 | `senior-backend-engineer` | [P] with T004 |

### Wave 3: Core Scoring (Phase 3 — US1)
**Duration**: ~1.5h | **Gate**: Agent scores all 4 dimensions + composite

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 3a | T007 | `senior-backend-engineer` | Sequential (CVSS first) |
| 3b | T008 | `senior-backend-engineer` | [P] with T007 |
| 3c | T009 | `senior-backend-engineer` | [P] with T007 |
| 3d | T010 | `senior-backend-engineer` | Sequential (after T007-T009) |

**MVP CHECKPOINT**: Stop and validate scoring against example data

### Wave 4a: Governance + Independent Stories (Phases 4, 6, 7)
**Duration**: ~1h | **Gate**: Governance fields, reachability, methodology all complete

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 4a-1 | T011 | `senior-backend-engineer` | Sequential (governance) |
| 4a-2 | T016 | `senior-backend-engineer` | [P] with T011 |
| 4a-3 | T019 | `senior-backend-engineer` | [P] with T011 |
| 4a-4 | T017 | `senior-backend-engineer` | After T016 |
| 4a-5 | T018 | `senior-backend-engineer` | After T010 + T017 |

### Wave 4b: Output Generation (Phase 5 — US3)
**Duration**: ~1h | **Gate**: Both output formats generate correctly

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 4b-1 | T012 | `senior-backend-engineer` | Sequential |
| 4b-2 | T013 | `senior-backend-engineer` | After T012 |
| 4b-3 | T014 | `senior-backend-engineer` | [P] with T012 |
| 4b-4 | T015 | `senior-backend-engineer` | [P] with T012 |

### Wave 5: Command + Integration (Phase 8)
**Duration**: ~45 min | **Gate**: /risk-score command executes end-to-end

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 5a | T020 | `senior-backend-engineer` | Sequential (command first) |
| 5b | T021 | `senior-backend-engineer` | [P] after T020 |
| 5c | T022 | `senior-backend-engineer` | [P] after T020 |
| 5d | T023 | `senior-backend-engineer` | [P] after T020 |
| 5e | T024 | `senior-backend-engineer` | [P] after T020 |

### Wave 6: Validation (Phase 9)
**Duration**: ~1h | **Gate**: All success criteria validated

| Slot | Task | Agent | Parallel |
|------|------|-------|----------|
| 6a | T025 | `senior-backend-engineer` | Sequential |
| 6b | T026 | `senior-backend-engineer` | [P] with T025 |
| 6c | T027 | `security-analyst` | After T025 |
| 6d | T028 | `code-reviewer` | [P] with T027 |
| 6e | T029 | `tester` | After T027 + T028 |

## Quality Gates

| Gate | Location | Criteria |
|------|----------|----------|
| G1 | After Wave 1 | Schema validates, agent skeleton has all section stubs |
| G2 | After Wave 2 | Agent can parse threats.md and threats.sarif, template structures exist |
| G3 | After Wave 3 | **MVP**: Agent produces 4 dimension scores + composite for all example findings |
| G4a | After Wave 4a | Governance fields, reachability, methodology sections complete |
| G4b | After Wave 4b | Both risk-scores.md and risk-scores.sarif generate correctly |
| G5 | After Wave 5 | /risk-score command runs end-to-end with correct output summary |
| G6 | After Wave 6 | SC-001 differentiation >= 80%, SC-005 parity 100%, SARIF validates |

## Timeline Summary

| Wave | Tasks | Duration (realistic) | Cumulative |
|------|-------|---------------------|------------|
| Wave 1 | 3 | 30 min | 0:30 |
| Wave 2 | 3 | 45 min | 1:15 |
| Wave 3 | 4 | 1:30 | 2:45 |
| Wave 4a | 5 | 1:00 | 3:45 |
| Wave 4b | 4 | 1:00 | 4:45 |
| Wave 5 | 5 | 0:45 | 5:30 |
| Wave 6 | 5 | 1:00 | 6:30 |
| **Total** | **29** | **~6.5h** | |

## Risk Notes

- **Bottleneck**: T007 (CVSS scoring) is the most complex individual task — category defaults + per-threat refinement logic. Allow extra time.
- **Wave 4 overload**: Split into 4a/4b with independent sub-waves. Orchestrator should checkpoint between 4a and 4b.
- **Validation dependency**: T029 (end-to-end) depends on all prior tasks. If any wave runs long, validation is the first to slip.
