# Agent Assignments: MAESTRO Layer Mapping (Feature 084)

**Generated**: 2026-04-07
**Source**: `specs/084-maestro-layer-mapping/tasks.md` (22 tasks, 8 phases)
**Agent**: team-lead
**Status**: APPROVED

---

## Feasibility Summary

| Dimension | Assessment |
|-----------|------------|
| Effort | 22 tasks across 8 phases; all markdown/YAML modifications, no application code |
| Capacity | Single agent (senior-backend-engineer) sufficient; no overload risk at ~3 tasks/wave average |
| Timeline | 3 days realistic (aligned with PRD estimate); 2 day optimistic, 4 day pessimistic |
| Dependencies | Linear content dependency chain is real and necessary; parallelism correctly maximized within constraints |
| Confidence | 80% (upgraded from PRD 75% — tasks.md resolves all ambiguity from deferred decisions) |

**Verdict**: FEASIBLE

---

## Agent Assignment Matrix

All 22 tasks are assigned to **senior-backend-engineer**. This is appropriate because:
- All deliverables are markdown and YAML file modifications (knowledge system project)
- No frontend, infrastructure, security analysis, or testing code involved
- senior-backend-engineer handles file-level content authoring for agent definitions, schemas, and references
- Single-agent assignment eliminates handoff overhead and context fragmentation

| Task | Agent | File(s) Modified | Phase |
|------|-------|-------------------|-------|
| T001 | senior-backend-engineer | `.claude/skills/tachi-shared/references/maestro-layers-shared.md` (NEW) | 1 |
| T002 | senior-backend-engineer | `schemas/finding.yaml` | 1 |
| T003 | senior-backend-engineer | `.claude/skills/tachi-shared/SKILL.md` | 1 |
| T004 | senior-backend-engineer | `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | 2 |
| T005 | senior-backend-engineer | `.claude/skills/tachi-orchestration/references/output-schemas.md` | 2 |
| T006 | senior-backend-engineer | `.claude/skills/tachi-shared/references/finding-format-shared.md` | 2 |
| T007 | senior-backend-engineer | `.claude/skills/tachi-orchestration/references/sarif-specification.md` | 2 |
| T008 | senior-backend-engineer | `.claude/agents/tachi/orchestrator.md` | 3 |
| T009 | senior-backend-engineer | `.claude/agents/tachi/orchestrator.md` | 4 |
| T010 | senior-backend-engineer | `.claude/agents/tachi/orchestrator.md` | 5 |
| T011 | senior-backend-engineer | `.claude/agents/tachi/orchestrator.md` | 6 |
| T012 | senior-backend-engineer | `.claude/agents/tachi/risk-scorer.md` | 7 |
| T013 | senior-backend-engineer | `.claude/agents/tachi/control-analyzer.md` | 7 |
| T014 | senior-backend-engineer | `.claude/agents/tachi/threat-report.md` | 7 |
| T015 | senior-backend-engineer | `examples/agentic-app/threats.md` | 8 |
| T016 | senior-backend-engineer | `examples/web-app/threats.md` | 8 |
| T017 | senior-backend-engineer | `examples/microservices/threats.md` | 8 |
| T018 | senior-backend-engineer | `examples/ascii-web-api/threats.md` | 8 |
| T019 | senior-backend-engineer | `examples/free-text-microservice/threats.md` | 8 |
| T020 | senior-backend-engineer | `examples/mermaid-agentic-app/threats.md` | 8 |
| T021 | senior-backend-engineer | Validation (cross-example analysis) | 8 |
| T022 | senior-backend-engineer | Validation (diff-based regression) | 8 |

---

## Parallel Execution Waves

### Wave 1: Foundation (Phase 1 — Setup)

**Tasks**: T001, then T002 + T003 in parallel
**Agent**: senior-backend-engineer
**Estimated Duration**: 0.5 day
**Parallel Factor**: 2 (T002, T003 after T001 completes)

| Task | Description | Parallel | Depends On |
|------|-------------|----------|------------|
| T001 | Create MAESTRO shared reference file | Sequential | None |
| T002 | Extend finding IR schema | Parallel | T001 |
| T003 | Update shared references skill metadata | Parallel | T001 |

**Quality Gate**: Verify maestro-layers-shared.md exists with all 7 layers, finding.yaml has maestro_layer field, SKILL.md references new file.

---

### Wave 2: Pipeline References (Phase 2 — Foundational)

**Tasks**: T004, T005, T006, T007 (all parallel)
**Agent**: senior-backend-engineer
**Estimated Duration**: 0.5 day
**Parallel Factor**: 4 (all tasks modify different files)

| Task | Description | Parallel | Depends On |
|------|-------------|----------|------------|
| T004 | Update dispatch table format | Parallel | T001 |
| T005 | Update output schemas | Parallel | T001 |
| T006 | Update finding format shared reference | Parallel | T001 |
| T007 | Update SARIF specification | Parallel | T001 |

**Quality Gate**: All 4 pipeline reference files include MAESTRO Layer column/field definitions. schema_version references updated to "1.2" where applicable.

---

### Wave 3: Core Classification (Phases 3-4 — US2 + US1)

**Tasks**: T008, then T009 (sequential — same file, dependent sections)
**Agent**: senior-backend-engineer
**Estimated Duration**: 0.5 day
**Parallel Factor**: 1 (sequential dependency on orchestrator.md)

| Task | Description | Parallel | Depends On |
|------|-------------|----------|------------|
| T008 | Phase 1 classification in orchestrator.md | Sequential | Wave 2 |
| T009 | Phase 3-4 finding inheritance + output tables | Sequential | T008 |

**Quality Gate**: Orchestrator.md Phase 1 has MAESTRO classification step. Phase 3 has finding-to-component inheritance. Phase 4 output tables include MAESTRO Layer column. **MVP checkpoint** -- core layer tagging operational.

---

### Wave 4: SARIF + Risk Summary + Downstream (Phases 5-7 — US3, US4, US5)

**Tasks**: T010, T011, T012, T013, T014
**Agent**: senior-backend-engineer
**Estimated Duration**: 0.5 day
**Parallel Factor**: 3 (T012, T013, T014 are independent files; T010 and T011 are sequential on orchestrator.md but can overlap with T012-T014)

| Task | Description | Parallel | Depends On |
|------|-------------|----------|------------|
| T010 | SARIF layer tags in orchestrator.md | Sequential | T009 |
| T011 | Risk by MAESTRO Layer in orchestrator.md | Sequential | T009 (can parallel with T010 -- different sections) |
| T012 | risk-scorer.md passive propagation | Parallel | T009 |
| T013 | control-analyzer.md passive propagation | Parallel | T009 |
| T014 | threat-report.md layer awareness | Parallel | T009 |

**Note on T010/T011**: tasks.md marks Phases 5-6 as sequential because they modify orchestrator.md. However, T010 (Phase 4 SARIF section) and T011 (Phase 4 Section 6 output) modify different sections of the same file. In practice these can be done by the same agent in a single pass through the file. The serialization constraint is conservative but acceptable.

**Quality Gate**: All SARIF extension rules documented. Risk by MAESTRO Layer subsection specified. Downstream agents (risk-scorer, control-analyzer, threat-report) all include passive propagation instructions.

---

### Wave 5: Validation (Phase 8 — Polish)

**Tasks**: T015-T020 (parallel), then T021, T022 (sequential validation)
**Agent**: senior-backend-engineer
**Estimated Duration**: 1.0 day (bottleneck -- 6 full pipeline regenerations)
**Parallel Factor**: 6 (regeneration), then 1 (validation)

| Task | Description | Parallel | Depends On |
|------|-------------|----------|------------|
| T015 | Regenerate agentic-app | Parallel | Waves 1-4 |
| T016 | Regenerate web-app | Parallel | Waves 1-4 |
| T017 | Regenerate microservices | Parallel | Waves 1-4 |
| T018 | Regenerate ascii-web-api | Parallel | Waves 1-4 |
| T019 | Regenerate free-text-microservice | Parallel | Waves 1-4 |
| T020 | Regenerate mermaid-agentic-app | Parallel | Waves 1-4 |
| T021 | Validate SC-001 (>90% classification rate) | Sequential | T015-T020 |
| T022 | Validate SC-003 (backward compatibility) | Sequential | T015-T020 |

**Quality Gate**: All 6 examples regenerated with MAESTRO layer columns. SC-001: >90% classification rate confirmed. SC-003: zero non-MAESTRO diffs confirmed.

---

## Wave Summary

| Wave | Phase(s) | Tasks | Parallel Factor | Duration | Cumulative |
|------|----------|-------|-----------------|----------|------------|
| Wave 1 | 1 (Setup) | T001-T003 | 2 | 0.5 day | 0.5 day |
| Wave 2 | 2 (Foundational) | T004-T007 | 4 | 0.5 day | 1.0 day |
| Wave 3 | 3-4 (US2+US1) | T008-T009 | 1 | 0.5 day | 1.5 days |
| Wave 4 | 5-7 (US3+US4+US5) | T010-T014 | 3 | 0.5 day | 2.0 days |
| Wave 5 | 8 (Polish) | T015-T022 | 6+1 | 1.0 day | 3.0 days |

**Total**: 3.0 days (realistic), aligning with PRD team-lead estimate.

---

## Critical Path

```
T001 --> [T004-T007] --> T008 --> T009 --> T010 --> T011 --> [T015-T020] --> T021/T022
         (parallel)                                          (parallel)
```

Minimum serial steps: 8 (T001, one of T004-T007, T008, T009, T010, T011, one of T015-T020, T021 or T022)

**Schedule Bottleneck**: Wave 5 (example regeneration) at 1.0 day. Each regeneration requires a full pipeline run. While the 6 regenerations are independent, they are the most time-consuming tasks.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Example regeneration takes longer than estimated | Front-load regeneration of agentic-app (richest architecture) as canary; if it succeeds, remainder are lower risk |
| Orchestrator.md serialization slows Waves 3-4 | Agent can batch T010+T011 as a single file edit since they modify different sections |
| Keyword coverage below 90% threshold (SC-001) | Iterate keyword table after first example regeneration before running remaining 5 |
| Pipeline produces unexpected diffs (SC-003) | Capture pre-change baselines before Wave 1 begins |

---

## Notes

- All valid agent names sourced from `.claude/agents/_README.md` registry
- Single-agent assignment (senior-backend-engineer) is appropriate for this knowledge system project where all deliverables are markdown/YAML
- No code-reviewer wave needed -- changes are to agent instruction files, not application code; review happens at PR level
- No tester wave needed -- validation is via pipeline regeneration (T015-T020) and success criteria checks (T021-T022), not automated test suites
- Commit after each wave completion for clean git history and rollback capability
