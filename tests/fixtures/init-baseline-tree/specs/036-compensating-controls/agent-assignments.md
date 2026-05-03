# Agent Assignments: Compensating Controls Analysis

**Feature**: 036-compensating-controls
**Generated**: 2026-03-27
**Source**: Team-Lead review

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001 | senior-backend-engineer | Schema authoring (extends risk-scoring.yaml) |
| T002 | senior-backend-engineer | Markdown template creation |
| T003 | senior-backend-engineer | SARIF template creation |
| T004 | senior-backend-engineer | Agent file creation and structure |
| T005 | senior-backend-engineer | Agent phase authoring (parse input) |
| T006 | senior-backend-engineer | Agent phase authoring (discover codebase) |
| T007 | senior-backend-engineer | STRIDE mapping table (embedded in agent) |
| T008 | senior-backend-engineer | Agent phase authoring (detect controls — critical path) |
| T009 | senior-backend-engineer | Agent phase authoring (map and classify) |
| T010 | senior-backend-engineer | Agent batching instructions |
| T011 | senior-backend-engineer | Agent recommendation logic |
| T012 | senior-backend-engineer | Agent residual risk calculation |
| T013 | senior-backend-engineer | Agent coverage matrix generation |
| T014 | senior-backend-engineer | Agent markdown output generation |
| T015 | senior-backend-engineer | Agent SARIF output generation |
| T016 | senior-backend-engineer | Command orchestrator file |
| T017 | tester | Run pipeline against example app |
| T018 | tester | SARIF schema validation |
| T019 | tester | SARIF supersession chain verification |
| T020 | tester | Acceptance criteria validation |
| T021 | tester | Quickstart walkthrough |

## Quality Gates

| Gate | Agent | Trigger |
|------|-------|---------|
| Security review of detection patterns | security-analyst | After Wave 3 (Phase 3 complete) |
| Code quality review of agent + command | code-reviewer | After Wave 5 (Phase 6 complete) |

## Parallel Execution Waves

### Wave 1 — Setup (Phase 1)
**Duration**: 1.0-1.5h | **Agent**: senior-backend-engineer

| Task | Description | Parallel? |
|------|-------------|-----------|
| T001 | Create schema `schemas/compensating-controls.yaml` | Yes |
| T002 | Create MD template `templates/compensating-controls.md` | Yes |
| T003 | Create SARIF template `templates/compensating-controls.sarif` | Yes |

### Wave 2 — Agent Foundation (Phase 2)
**Duration**: 1.5-2.0h | **Agent**: senior-backend-engineer

| Task | Description | Parallel? |
|------|-------------|-----------|
| T004 | Create agent skeleton | No (first) |
| T005 | Write Phase 1 (Parse Input) | No (after T004) |
| T006 | Write Phase 2 (Discover Codebase) | No (after T005) |
| T007 | Embed STRIDE mapping table | No (after T004) |

### Wave 3 — Control Detection (Phase 3, US1)
**Duration**: 3.0-4.0h | **Agent**: senior-backend-engineer

| Task | Description | Parallel? |
|------|-------------|-----------|
| T008 | Write Phase 3 (Detect Controls — 8 categories) | No |
| T009 | Write Phase 4 (Map and Classify) | No (after T008) |
| T010 | Add batching instructions | No (after T008) |

**Quality Gate**: security-analyst reviews detection patterns.

### Wave 4 — Recommendations + Residual Risk (Phase 4+5, US2+US3)
**Duration**: 1.0-1.5h | **Agent**: senior-backend-engineer

| Task | Description | Parallel? |
|------|-------------|-----------|
| T011 | Write recommendation logic (US2) | Yes |
| T012 | Write residual risk calculation (US3) | Yes |

### Wave 5 — Output Pipeline (Phase 6, US4+US5)
**Duration**: 2.0-2.5h | **Agent**: senior-backend-engineer

| Task | Description | Parallel? |
|------|-------------|-----------|
| T013 | Write coverage matrix (US4) | No (first) |
| T014 | Write markdown output (US5) | No (after T013) |
| T015 | Write SARIF output (US5) | No (after T013) |
| T016 | Create command orchestrator | No (after T014+T015) |

**Quality Gate**: code-reviewer reviews agent + command files.

### Wave 6 — Validation (Phase 7)
**Duration**: 1.0-1.5h | **Agent**: tester

| Task | Description | Parallel? |
|------|-------------|-----------|
| T017 | Run pipeline against example app | Yes |
| T018 | Validate SARIF against 2.1.0 schema | Yes (with T017) |
| T019 | Verify SARIF supersession chain | No (after T018) |
| T020 | Review output against acceptance criteria | No (after T017) |
| T021 | Run quickstart.md validation | No (after T017) |

## Wave Summary

| Wave | Phase | Duration | Agent | Tasks | Parallel? |
|------|-------|----------|-------|-------|-----------|
| 1 | Setup | 1.0-1.5h | senior-backend-engineer | T001-T003 | Yes (all 3) |
| 2 | Foundation | 1.5-2.0h | senior-backend-engineer | T004-T007 | Sequential |
| 3 | Detection | 3.0-4.0h | senior-backend-engineer | T008-T010 | Sequential |
| 4 | Recommend+Risk | 1.0-1.5h | senior-backend-engineer | T011-T012 | Yes (both) |
| 5 | Output | 2.0-2.5h | senior-backend-engineer | T013-T016 | Mostly sequential |
| 6 | Validation | 1.0-1.5h | tester | T017-T021 | Partial |
| **Total** | | **9.5-13.0h** | | **21 tasks** | |
