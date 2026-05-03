# Agent Assignments: 054 — Security Assessment PDF Booklet

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001-T006 | `senior-backend-engineer` | Read source patterns, create directory structure |
| T007 | `senior-backend-engineer` | YAML schema authoring |
| T008 | `senior-backend-engineer` | Command file markdown authoring |
| T009 | `senior-backend-engineer` | Typst POC template authoring |
| T010 | `tester` | POC validation — verify rendering capabilities |
| T011-T016 | `senior-backend-engineer` | Typst template authoring (shared styles + text pages) |
| T017 | `senior-backend-engineer` | Typst full-bleed template authoring |
| T018-T019 | `senior-backend-engineer` | Master orchestrator + cleanup |
| T020-T024 | `senior-backend-engineer` | Agent file authoring (largest deliverable) |
| T025-T026 | `senior-backend-engineer` | Command file completion |
| T027-T030 | `tester` | Graceful degradation + prerequisite validation |
| T031-T032 | `senior-backend-engineer` | Template and README documentation |
| T033-T034 | `tester` | Idempotency and performance verification |

## Parallel Execution Waves

### Wave 1: Research + Setup (Phase 1)
**Duration**: ~15 minutes
**Agents**: 1x `senior-backend-engineer`

| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| Read sources | T001, T002, T003, T004, T005 | `senior-backend-engineer` |
| Scaffold | T006 | `senior-backend-engineer` |

**Quality Gate**: All source patterns understood. Directory created.

### Wave 2: Schema + Command + POC (Phase 2 — Wave 1 Gate)
**Duration**: ~45 minutes
**Agents**: 1x `senior-backend-engineer`, 1x `tester`

| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| Schema | T007 | `senior-backend-engineer` |
| Command scaffold | T008 | `senior-backend-engineer` |
| POC template | T009 | `senior-backend-engineer` |

Then sequentially:
| Task | Agent |
|------|-------|
| POC validation | T010 | `tester` |

**Quality Gate**: POC MUST pass (full-bleed, mixed orientation, conditional pages). STOP if POC fails.

### Wave 3: Templates + Full-Bleed (Phases 3-4)
**Duration**: ~90 minutes
**Agents**: 1x `senior-backend-engineer`

Sequential first:
| Task | Agent |
|------|-------|
| Shared styles | T011 | `senior-backend-engineer` |

Then parallel:
| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| Text pages | T012, T013, T014, T015, T016 | `senior-backend-engineer` |
| Full-bleed | T017 | `senior-backend-engineer` |

Then sequential:
| Task | Agent |
|------|-------|
| Master orchestrator | T018 | `senior-backend-engineer` |
| POC cleanup | T019 | `senior-backend-engineer` |

**Quality Gate**: All Typst templates compile independently. main.typ assembles all pages.

### Wave 4: Agent + Command + Validation (Phases 5-8)
**Duration**: ~90 minutes
**Agents**: 1x `senior-backend-engineer`, 1x `tester`

Sequential (agent + command):
| Task | Agent |
|------|-------|
| Agent file (Steps 1-4) | T020, T021, T022, T023, T024 | `senior-backend-engineer` |
| Command completion | T025, T026 | `senior-backend-engineer` |

Then parallel (validation + docs):
| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| Graceful degradation | T027, T028, T029, T030 | `tester` |
| Documentation | T031, T032 | `senior-backend-engineer` |

Then sequential:
| Task | Agent |
|------|-------|
| Idempotency check | T033 | `tester` |
| Performance check | T034 | `tester` |

**Quality Gate**: End-to-end validation passes all artifact combinations. Performance <30s.

## Timeline Estimate

| Wave | Duration | Cumulative |
|------|----------|-----------|
| Wave 1 (Research) | ~15 min | 15 min |
| Wave 2 (POC Gate) | ~45 min | 1 hour |
| Wave 3 (Templates) | ~90 min | 2.5 hours |
| Wave 4 (Agent + Validation) | ~90 min | 4 hours |

**Total Estimate**: 3-4 sessions (aligned with team-lead's calibration)
**Confidence**: 70% at 3 sessions, 90% at 4 sessions

## Risk Factors

- **Wave 2 POC gate**: If Typst capabilities don't validate, contingency evaluation adds ~1 session
- **Wave 4 agent file**: Largest single deliverable; T020-T024 are sequential chain
- **Validation surprises**: Edge cases in markdown parsing may require template adjustments
