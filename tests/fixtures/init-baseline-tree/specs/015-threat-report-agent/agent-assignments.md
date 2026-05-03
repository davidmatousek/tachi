# Agent Assignments: Feature 015 — Threat Report Agent & Attack Trees

**Feature**: 015-threat-report-agent
**Date**: 2026-03-23
**Status**: APPROVED
**Total Tasks**: 29
**Total Waves**: 5

---

## Feasibility Summary

| Dimension | Assessment |
|-----------|-----------|
| Effort | 29 tasks across 7 phases; all markdown/YAML deliverables (no compilation, no test framework) |
| Capacity | 2 concurrent agents at peak (Waves 3, 4); single agent otherwise |
| Timeline | Realistic: ~3-4 hours elapsed; Optimistic: ~2.5 hours; Pessimistic: ~5 hours |
| Dependencies | Linear foundation chain (Waves 1-2), then parallelism opens (Waves 3-4) |

**Verdict**: FEASIBLE

---

## Agent Assignment Matrix

### Valid Agent Pool (from `.claude/agents/_README.md`)

| Agent | Registry Role | Feature Role |
|-------|--------------|--------------|
| senior-backend-engineer | Backend Engineer | Primary: markdown file creation, YAML schemas, agent prompt authoring |
| tester | QA Engineer | Validation: end-to-end verification against sample data, output correctness |
| architect | System Architect | Advisory: orchestrator integration design review |
| code-reviewer | Code Quality Analyst | Quality gate: cross-file consistency review between waves |

### Task-to-Agent Mapping

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Create `schemas/report.yaml` | senior-backend-engineer | YAML schema authoring |
| T002 | Create `templates/threat-report.md` | senior-backend-engineer | Template/markdown creation |
| T003 | Create `agents/threat-report.md` core | senior-backend-engineer | Agent prompt file creation |
| T004 | Write Input Contract section | senior-backend-engineer | Agent prompt section authoring |
| T005 | Write Quality Standards section | senior-backend-engineer | Agent prompt section authoring |
| T006 | Write Executive Summary Template | senior-backend-engineer | Report methodology section |
| T007 | Write Architecture Overview methodology | senior-backend-engineer | Report methodology section |
| T008 | Write Threat Analysis methodology | senior-backend-engineer | Report methodology section |
| T009 | Write Cross-Cutting Theme Detection | senior-backend-engineer | Report methodology section |
| T010 | Write Correlation Group Handling | senior-backend-engineer | Report methodology section |
| T011 | Write Finding Reference Appendix | senior-backend-engineer | Report methodology section |
| T012 | Write Attack Tree Construction Rules | senior-backend-engineer | Report methodology section |
| T013 | Write Mermaid Conventions | senior-backend-engineer | Report methodology section |
| T014 | Write Mermaid Validation Checklist | senior-backend-engineer | Report methodology section |
| T015 | Add example attack trees | senior-backend-engineer | Mermaid diagram authoring (highest single-task effort) |
| T016 | Write Dual Output Location instructions | senior-backend-engineer | Report methodology section |
| T017 | Add Phase 5 definition to orchestrator | senior-backend-engineer | Orchestrator prompt modification |
| T018 | Add Phase 5 dispatch logic | senior-backend-engineer | Orchestrator prompt modification |
| T019 | Add opt-out configuration | senior-backend-engineer | Orchestrator prompt modification |
| T020 | Update orchestrator validation checklist | senior-backend-engineer | Orchestrator prompt modification |
| T021 | Write Remediation Roadmap methodology | senior-backend-engineer | Report methodology section |
| T022 | Write Effort Estimation heuristics | senior-backend-engineer | Report methodology section |
| T023 | Write Correlation Consolidation rules | senior-backend-engineer | Report methodology section |
| T024 | Run report agent against sample data | tester | End-to-end validation execution |
| T025 | Validate 12 attack trees render correctly | tester | Mermaid syntax verification |
| T026 | Verify finding completeness (19 findings) | tester | Completeness audit |
| T027 | Verify cross-cutting themes in sample | tester | Output quality verification |
| T028 | Save validated sample outputs | senior-backend-engineer | File creation (commit validated outputs) |
| T029 | Run full orchestrator pipeline (Phases 1-5) | tester | Pipeline integration test |

### Agent Workload Summary

| Agent | Task Count | % of Total | Wave(s) Active |
|-------|-----------|------------|----------------|
| senior-backend-engineer | 24 | 83% | 1, 2, 3, 4, 5 |
| tester | 5 | 17% | 5 |
| code-reviewer | 0 (quality gates only) | -- | Between waves |
| architect | 0 (advisory only) | -- | Wave 3 review |

**Workload Note**: senior-backend-engineer carries the bulk because this feature is entirely content authoring (markdown/YAML). No frontend, no application code, no infrastructure. The tester handles the validation phase where outputs must be verified against sample data. This distribution is appropriate for the deliverable type.

---

## Wave Execution Strategy

### Wave 1: Setup (Parallel)

**Purpose**: Create foundational schema and template files
**Estimated Duration**: 15-20 minutes
**Parallelism**: 2 agents on independent files

| Slot | Task(s) | Agent | File(s) | Dependencies |
|------|---------|-------|---------|-------------|
| A | T001 | senior-backend-engineer | `schemas/report.yaml` | None |
| B | T002 | senior-backend-engineer | `templates/threat-report.md` | None |

**Quality Gate**: Schema defines 7 required sections. Template contains all 7 section headings with placeholders. File naming convention for attack trees established.

---

### Wave 2: Foundation (Sequential)

**Purpose**: Create report agent core structure with frontmatter, mission, input contract, quality standards
**Estimated Duration**: 25-35 minutes
**Parallelism**: None (all tasks write to same file, sequential within `agents/threat-report.md`)

| Slot | Task(s) | Agent | File(s) | Dependencies |
|------|---------|-------|---------|-------------|
| A | T003 -> T004 -> T005 | senior-backend-engineer | `agents/threat-report.md` | Wave 1 complete |

**Quality Gate**: Agent file has valid YAML frontmatter, Core Mission section, Input Contract referencing `schemas/output.yaml` and `schemas/report.yaml`, and Quality Standards checklist. code-reviewer verifies cross-references between agent frontmatter and schema files from Wave 1.

---

### Wave 3: User Stories — Parallel Across Files

**Purpose**: Build US1 (narrative report) and US4 (orchestrator integration) simultaneously
**Estimated Duration**: 45-60 minutes (longest wave, critical path)
**Parallelism**: 2 agents on independent files

| Slot | Task(s) | Agent | File(s) | Dependencies |
|------|---------|-------|---------|-------------|
| A | T006 -> T007 -> T008 -> T009 -> T010 -> T011 | senior-backend-engineer | `agents/threat-report.md` (US1 sections) | Wave 2 complete |
| B | T017 -> T018 -> T019 -> T020 | senior-backend-engineer | `agents/orchestrator.md` (US4 sections) | Wave 2 complete |

**Quality Gate**: US1: All 6 narrative methodology sections present in report agent. Executive summary template specifies 500-word cap and 5 required elements. Cross-cutting theme detection has 4 criteria. Finding appendix specifies zero-loss rule. US4: Phase 5 definition follows existing phase pattern in orchestrator. Dispatch logic specifies fresh-context isolation. Opt-out flag documented. Validation checklist updated. architect advisory review on orchestrator integration pattern (T017-T020).

**Note on Slot A sequencing**: T006-T011 are sequential because they write to the same file. However, each task adds a distinct section, so file contention risk is low if managed as append-only operations.

---

### Wave 4: Attack Trees + Roadmap (Sequential, Same File)

**Purpose**: Build US2 (attack trees) and US3 (remediation roadmap) in the report agent
**Estimated Duration**: 40-55 minutes
**Parallelism**: None (all tasks target `agents/threat-report.md`)

| Slot | Task(s) | Agent | File(s) | Dependencies |
|------|---------|-------|---------|-------------|
| A | T012 -> T013 -> T014 -> T015 -> T016 -> T021 -> T022 -> T023 | senior-backend-engineer | `agents/threat-report.md` (US2 + US3 sections) | Wave 3 Slot A complete |

**Quality Gate**: US2: Attack tree construction rules specify 3-level minimum for Critical, 2-level for High. Mermaid conventions define `flowchart TD`, node ID format, color scheme. Two example trees render valid Mermaid syntax. Dual output location specifies inline + standalone. US3: Roadmap orders by risk level (Critical first). Effort estimation defines Low/Medium/High heuristics. Correlation consolidation references Section 4a.

**Note on T015**: This is the highest-effort single task (authoring two complete example attack trees with valid Mermaid syntax). Allow extra time.

---

### Wave 5: Validation (Sequential)

**Purpose**: End-to-end verification against sample data, then save validated outputs
**Estimated Duration**: 30-45 minutes
**Parallelism**: None (sequential validation pipeline)

| Slot | Task(s) | Agent | File(s) | Dependencies |
|------|---------|-------|---------|-------------|
| A | T024 -> T025 -> T026 -> T027 | tester | Sample outputs from `examples/mermaid-agentic-app/` | Waves 1-4 complete |
| B | T028 | senior-backend-engineer | `examples/mermaid-agentic-app/threat-report.md`, `examples/mermaid-agentic-app/attack-trees/` | T024-T027 pass |
| C | T029 | tester | Full pipeline output | T028 complete |

**Quality Gate (Final)**: T024: `threat-report.md` generated with all 7 sections. T025: All 12 attack trees (3 Critical + 9 High) render valid Mermaid. T026: All 19 finding IDs appear in appendix (zero loss). T027: At least 1 cross-cutting theme identified. T028: Validated outputs committed to examples directory. T029: Full pipeline (Phases 1-5) produces report alongside `threats.md` and `threats.sarif`.

---

## Wave Dependency Diagram

```
Wave 1 (Setup)          T001 || T002
       |                     |
       v                     v
Wave 2 (Foundation)     T003 -> T004 -> T005
       |                         |
       v                         v
Wave 3 (Parallel)       T006-T011 (Slot A)  ||  T017-T020 (Slot B)
       |                    |                        |
       v                    v                        |
Wave 4 (Attack+Road)   T012-T016 -> T021-T023       |
       |                         |                   |
       v                         v                   v
Wave 5 (Validation)     T024-T027 -> T028 -> T029
```

---

## Time Estimates

| Wave | Tasks | Duration (Optimistic) | Duration (Realistic) | Duration (Pessimistic) |
|------|-------|-----------------------|---------------------|----------------------|
| Wave 1 | 2 | 10 min | 15 min | 25 min |
| Wave 2 | 3 | 20 min | 30 min | 40 min |
| Wave 3 | 10 | 35 min | 50 min | 70 min |
| Wave 4 | 8 | 30 min | 45 min | 60 min |
| Wave 5 | 6 | 25 min | 35 min | 50 min |
| **Total** | **29** | **2h 00min** | **2h 55min** | **4h 05min** |

**Note**: Times assume content-as-code workflow (no compilation, no test harness, no deployment). Wave 3 is the critical path due to 6 sequential sections in Slot A. Wave 4 includes T015 (example attack trees), the highest-effort single task.

---

## Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| T015 Mermaid syntax errors in example trees | Medium | Medium | Use Mermaid Live Editor to validate before committing |
| Wave 3 file contention (threat-report.md) | Low | Low | Sequential execution within slot; no parallel writes |
| Orchestrator integration pattern mismatch | Low | Medium | architect advisory review after Wave 3 Slot B |
| Sample data missing expected findings | Low | High | Verify `examples/mermaid-agentic-app/threats.md` has 19 findings before Wave 5 |

---

## Notes

- All 29 tasks produce markdown or YAML files. No application code, no compilation, no automated test framework.
- The single largest deliverable is `agents/threat-report.md` (Waves 2-4, tasks T003-T016, T021-T023).
- The only modified existing file is `agents/orchestrator.md` (Wave 3 Slot B, tasks T017-T020).
- Validation phase (Wave 5) uses existing sample data at `examples/mermaid-agentic-app/threats.md` (19 findings).
- code-reviewer participates at quality gates between waves, not as a task assignee.
- architect provides advisory review on orchestrator integration (Wave 3 Slot B) but has no assigned tasks.

---

**End of Agent Assignments**
