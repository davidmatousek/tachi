# Agent Assignments: Feature 001 — Project Skeleton & Interface Contract

**Date**: 2026-03-21
**Assigned by**: team-lead
**Feasibility**: APPROVED_WITH_CONCERNS (see `.aod/results/team-lead.md`)

---

## Agent Assignment Matrix

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Create schemas/ directory | senior-backend-engineer | Directory creation |
| T002 | Create LICENSE (Apache 2.0) | senior-backend-engineer | Standard file creation |
| T003 | Create schemas/README.md | senior-backend-engineer | Documentation authoring |
| T004 | Create schemas/finding.yaml | senior-backend-engineer | YAML schema authoring (follow spec FR-011 for 10 fields) |
| T005 | Create schemas/input.yaml | senior-backend-engineer | YAML schema authoring |
| T006 | Create schemas/output.yaml | senior-backend-engineer | YAML schema authoring |
| T007 | Update adapters/ContextLoading.yaml | senior-backend-engineer | Config path corrections |
| T008 | Update adapters/ProjectMeta.yaml | senior-backend-engineer | Config population |
| T009 | Update adapters/ScoringRubric.md | security-analyst | OWASP 3x3 risk scoring domain expertise |
| T010 | Create agents/stride/spoofing.md | senior-backend-engineer | Templated agent file |
| T011 | Create agents/stride/tampering.md | senior-backend-engineer | Templated agent file |
| T012 | Create agents/stride/repudiation.md | senior-backend-engineer | Templated agent file |
| T013 | Create agents/stride/info-disclosure.md | senior-backend-engineer | Templated agent file |
| T014 | Create agents/stride/denial-of-service.md | senior-backend-engineer | Templated agent file |
| T015 | Create agents/stride/privilege-escalation.md | senior-backend-engineer | Templated agent file |
| T016 | Create agents/ai/prompt-injection.md | senior-backend-engineer | Templated agent file |
| T017 | Create agents/ai/tool-abuse.md | senior-backend-engineer | Templated agent file |
| T018 | Create agents/ai/data-poisoning.md | senior-backend-engineer | Templated agent file |
| T019 | Create agents/ai/model-theft.md | senior-backend-engineer | Templated agent file |
| T020 | Create agents/ai/agent-autonomy.md | senior-backend-engineer | Templated agent file |
| T021 | Update agents/ai/README.md | senior-backend-engineer | Documentation update (5-to-2 mapping) |
| T022 | Create agents/orchestrator.md | senior-backend-engineer | Placeholder file creation |
| T023 | Create docs/INTERFACE-CONTRACT.md | security-analyst | Deep threat modeling domain expertise required (STRIDE normalization, AI dispatch rules, OWASP references) |
| T024 | Create templates/threats.md | security-analyst | Domain expertise required (STRIDE tables, AI threat tables, OWASP 3x3 risk matrix, coverage matrix) |
| T025 | Verify schemas/ completeness | tester | Validation activity: cross-reference check between schemas, agents, and template |
| T026 | Create examples/ascii-web-api/input.md | senior-backend-engineer | Architecture diagram authoring |
| T027 | Create examples/mermaid-agentic-app/input.md | senior-backend-engineer | Mermaid diagram authoring |
| T028 | Create examples/free-text-microservice/input.md | senior-backend-engineer | Prose description authoring |
| T029 | Create examples/ascii-web-api/threats.md | security-analyst | Expected output requires threat modeling domain expertise |
| T030 | Create examples/mermaid-agentic-app/threats.md | security-analyst | Expected output requires AI threat agent domain expertise |
| T031 | Create examples/free-text-microservice/threats.md | security-analyst | Expected output requires STRIDE domain expertise |
| T032 | Update root README.md | senior-backend-engineer | Documentation update (quickstart links) |
| T033 | Run cross-reference validation | tester | Validation activity: path resolution, structural integrity |

---

## Agent Workload Summary

| Agent | Task Count | Task IDs |
|-------|-----------|----------|
| senior-backend-engineer | 22 | T001-T008, T010-T022, T026-T028, T032 |
| security-analyst | 7 | T009, T023, T024, T029-T031 |
| tester | 2 | T025, T033 |
| code-reviewer | 0 (quality gates only) | Post-wave reviews |
| **Total** | **33** | (2 agents excluded from task count: code-reviewer does wave gates, orchestrator coordinates) |

**Load Assessment**: No agent exceeds 80% capacity within any single wave. senior-backend-engineer has the highest count (22) but these are spread across 5 waves and most are templated files in Wave 3. security-analyst has 7 tasks but only 4 are in the same wave (T009 in Wave 2, T023/T024 in Wave 3, T029-T031 in Wave 5b).

---

## Parallel Execution Waves

### Wave 1: Setup (Phase 1)

**Duration**: ~5 minutes
**Gate**: Directories and root files exist

| Task | Agent | Parallel | Depends On |
|------|-------|----------|------------|
| T001 | senior-backend-engineer | Yes | None |
| T002 | senior-backend-engineer | Yes | None |

**Quality Gate**: Verify `schemas/` directory exists and `LICENSE` file is present.

---

### Wave 2: Foundational (Phase 2)

**Duration**: ~30-45 minutes
**Gate**: All schemas and config files populated with correct content

| Task | Agent | Parallel | Depends On |
|------|-------|----------|------------|
| T003 | senior-backend-engineer | Yes | T001 |
| T004 | senior-backend-engineer | Yes | T001 |
| T005 | senior-backend-engineer | Yes | T001 |
| T006 | senior-backend-engineer | Yes | T001 |
| T007 | senior-backend-engineer | Yes | None |
| T008 | senior-backend-engineer | Yes | None |
| T009 | security-analyst | Yes | None |

**Quality Gate**: Verify all schema files have correct field counts and types. Verify ContextLoading.yaml paths use post-scaffold format. Verify ScoringRubric.md contains OWASP 3x3 dimensions.

---

### Wave 3: Core Content (Phases 3-5) -- MAXIMUM PARALLELISM

**Duration**: ~60-90 minutes
**Gate**: All agent files, interface contract, and output template complete

**ORCHESTRATOR NOTE**: Start T023 and T024 FIRST in this wave. They are on the critical path and any rework must be absorbed within the wave.

| Task | Agent | Parallel | Depends On | Priority |
|------|-------|----------|------------|----------|
| T023 | security-analyst | Yes | Wave 2 | START FIRST |
| T024 | security-analyst | Yes | Wave 2 | START FIRST |
| T010 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T011 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T012 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T013 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T014 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T015 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T016 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T017 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T018 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T019 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T020 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T021 | senior-backend-engineer | Yes | Wave 2 | Normal |
| T022 | senior-backend-engineer | Yes | Wave 2 | Normal |

**Quality Gate**: Verify all 11 agent files have correct frontmatter format referencing schemas/finding.yaml. Verify INTERFACE-CONTRACT.md has all 7 sections. Verify templates/threats.md has all 7 sections with examples.

---

### Wave 4: Schema Verification (Phase 6)

**Duration**: ~10-15 minutes
**Gate**: Schemas validated against template and agents

| Task | Agent | Parallel | Depends On |
|------|-------|----------|------------|
| T025 | tester | No | Wave 3 (specifically T006 + T024) |

**Quality Gate**: Confirm finding.yaml has all 10 fields per spec FR-011. Confirm output.yaml sections match templates/threats.md sections exactly. Confirm schemas/README.md cross-references are valid.

---

### Wave 5a: Example Inputs (Phase 7, Part 1)

**Duration**: ~15-20 minutes
**Gate**: All 3 input files valid in their stated format

| Task | Agent | Parallel | Depends On |
|------|-------|----------|------------|
| T026 | senior-backend-engineer | Yes | Wave 3 |
| T027 | senior-backend-engineer | Yes | Wave 3 |
| T028 | senior-backend-engineer | Yes | Wave 3 |

**Quality Gate**: Each input.md is a valid architecture description in the correct format (ASCII, Mermaid, free-text).

---

### Wave 5b: Example Outputs (Phase 7, Part 2)

**Duration**: ~30-40 minutes
**Gate**: All 3 output files follow template structure with all 7 sections

| Task | Agent | Parallel | Depends On |
|------|-------|----------|------------|
| T029 | security-analyst | Yes | T026 + T024 |
| T030 | security-analyst | Yes | T027 + T024 |
| T031 | security-analyst | Yes | T028 + T024 |

**NOTE**: T029, T030, T031 CAN run in parallel (different directories, no cross-dependencies). Override the missing [P] markers in tasks.md.

**Quality Gate**: Each threats.md follows templates/threats.md structure. STRIDE tables have at least 1 finding per category. AI tables populated where applicable. Coverage matrix complete.

---

### Wave 6: Polish (Phase 8)

**Duration**: ~15-20 minutes
**Gate**: README updated, all cross-references valid

| Task | Agent | Parallel | Depends On |
|------|-------|----------|------------|
| T032 | senior-backend-engineer | No (first) | Wave 5b |
| T033 | tester | No (after T032) | T032 |

**Quality Gate (FINAL)**: All 9 ContextLoading.yaml paths resolve. All agent files reference schemas/finding.yaml. All cross-file references valid. Every top-level directory has README.md. Naming conventions correct (PascalCase directories, kebab-case agent files).

---

## Wave Timeline Summary

| Wave | Tasks | Wall-Clock Estimate | Cumulative |
|------|-------|---------------------|------------|
| Wave 1 | 2 | 5 min | 5 min |
| Wave 2 | 7 | 30-45 min | 35-50 min |
| Wave 3 | 15 | 60-90 min | 1h 35m - 2h 20m |
| Wave 4 | 1 | 10-15 min | 1h 45m - 2h 35m |
| Wave 5a | 3 | 15-20 min | 2h 00m - 2h 55m |
| Wave 5b | 3 | 30-40 min | 2h 30m - 3h 35m |
| Wave 6 | 2 | 15-20 min | 2h 45m - 3h 55m |
| **Total** | **33** | | **~3-4 hours** |

**Optimistic**: 2h 45m (clean execution, no rework)
**Realistic**: 3h 30m (1 revision cycle on T023 or T024)
**Pessimistic**: 5h (multiple rework cycles on domain content)

---

## Orchestrator Handoff Instructions

1. Execute waves sequentially (Wave 1 -> 2 -> 3 -> 4 -> 5a -> 5b -> 6)
2. Within each wave, maximize parallelism per the tables above
3. In Wave 3, start T023 and T024 BEFORE the 13 agent file tasks
4. In Wave 5b, run T029/T030/T031 in parallel (override missing [P] markers)
5. Run quality gate checks between each wave before proceeding
6. Commit after each wave completion
7. Report completion metrics after Wave 6 for team-lead sign-off

---

**End of Agent Assignments**
