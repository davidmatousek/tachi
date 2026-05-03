# Agent Assignments: Feature 029 — Agent Refactoring Right-Size

**Feature Branch**: `029-agent-refactoring-right`
**Date**: 2026-03-25
**Team Lead**: team-lead
**Total Tasks**: 27 | **Estimated Duration**: 10-15 hours | **Waves**: 4

---

## Agent Selection Rationale

This is a content-refactoring feature -- all deliverables are markdown files. No runtime code is produced. The primary agents are:

- **senior-backend-engineer**: Extraction, restructuring, and modification of agent files. Selected because this work is structured file manipulation following precise specifications -- the closest analogue to backend refactoring in a content project.
- **code-reviewer**: Verification that extractions preserve content integrity, naming conventions, and structural compliance.
- **tester**: Regression testing (end-to-end `/threat-model` runs, checksum comparison, SARIF validation).
- **orchestrator**: Wave coordination and parallel dispatch.

---

## Wave 1: Preparation (Phases 1-2)

**Duration**: 1.5-2.5 hours | **Gate**: Baseline captured, capability inventory committed

### Sequential Setup

| Task | Agent | Description | Est. |
|------|-------|-------------|------|
| T001 | senior-backend-engineer | Create `adapters/claude-code/agents/references/` directory | 5m |
| T002 | senior-backend-engineer | Record baseline checksums of 11 threat agents + 2 infographic templates | 15m |

### Parallel Capability Inventory

| Task | Agent | Description | Parallel | Est. |
|------|-------|-------------|----------|------|
| T003 | senior-backend-engineer | Capability inventory: orchestrator.md | Yes | 30m |
| T004 | senior-backend-engineer | Capability inventory: threat-report.md | Yes (with T003, T005) | 20m |
| T005 | senior-backend-engineer | Capability inventory: threat-infographic.md | Yes (with T003, T004) | 20m |

### Baseline Capture (BLOCKING)

| Task | Agent | Description | Est. |
|------|-------|-------------|------|
| T006 | tester | Run `/threat-model` on example architecture, save all outputs to baseline-output/ | 30m |

**Quality Gate**: Verify baseline-output/ contains all expected files (threats.md, threats.sarif, threat-report.md, attack-trees/, infographic specs). Verify capability-inventory.md is complete for all 3 agents. Proceed to Wave 2 only after gate passes.

---

## Wave 2: Orchestrator Refactoring — MVP (Phase 3)

**Duration**: 3-4 hours | **Gate**: Orchestrator regression passes, line count ~1,100-1,200
**Dependency**: Wave 1 complete

### Sequential Extraction (same file — no parallel)

| Task | Agent | Description | Est. |
|------|-------|-------------|------|
| T007 | senior-backend-engineer | Extract SARIF generation (lines 1224-1718) to references/sarif-generation.md | 30m |
| T008 | senior-backend-engineer | Extract validation checklist (lines 1138-1223) to references/validation-checklist.md | 20m |
| T009 | senior-backend-engineer | Split error handling: extract YAML templates to references/error-templates.md, retain defensive spec | 45m |
| T010 | senior-backend-engineer | Condense verbose prose (~200 lines) — narration only, never specification | 30m |
| T011 | senior-backend-engineer | Add Reference Documents section with loading instructions table | 15m |
| T012 | code-reviewer | Verify orchestrator line count (~1,100-1,200 lines via `wc -l`) | 10m |

**Quality Gate**: Run `/threat-model` on example architecture. Compare output structure against Wave 1 baseline. Orchestrator regression must pass before proceeding to Wave 3. This is the MVP gate — if the extraction approach is flawed, it will surface here before applying to 2 more agents.

---

## Wave 3: Report + Infographic Refactoring (Phases 4-5 PARALLEL)

**Duration**: 2-3 hours (parallel) | **Gate**: Both agents pass individual regression
**Dependency**: Wave 2 MVP gate passes

### Stream A: Report Agent (US2)

| Task | Agent | Description | Parallel | Est. |
|------|-------|-------------|----------|------|
| T013 | senior-backend-engineer | Extract attack tree rules + Mermaid conventions + examples to references/report-templates.md | Yes (with Stream B) | 30m |
| T014 | senior-backend-engineer | Condense prose: dual output, remediation roadmap, executive summary, narrative template | Yes (with T013) | 25m |
| T015 | senior-backend-engineer | Add Reference Documents section with loading instructions | After T013-T014 | 10m |
| T016 | code-reviewer | Verify report agent line count (~300-400 lines) | After T015 | 10m |

### Stream B: Infographic Agent (US3)

| Task | Agent | Description | Parallel | Est. |
|------|-------|-------------|----------|------|
| T017 | senior-backend-engineer | Extract Gemini API prompt + integration to references/infographic-gemini-api.md | Yes (with Stream A) | 25m |
| T018 | senior-backend-engineer | Extract error handling + graceful degradation to references/infographic-error-handling.md | Yes (with T017) | 20m |
| T019 | senior-backend-engineer | Add Reference Documents section with loading instructions | After T017-T018 | 10m |
| T020 | code-reviewer | Verify infographic agent line count (~300-400 lines) | After T019 | 10m |

**Quality Gate**: Both stream agents independently pass regression check (output structure matches baseline sections for report and infographic respectively). Both line counts verified within target range or deviation justified.

---

## Wave 4: Final Validation (Phase 6)

**Duration**: 1.5-2 hours | **Gate**: All validation passes, feature complete
**Dependency**: Waves 2 and 3 complete (all 3 agents refactored)

### Parallel Verification

| Task | Agent | Description | Parallel | Est. |
|------|-------|-------------|----------|------|
| T021 | tester | Verify 11 threat agents byte-identical against baseline checksums | Yes | 15m |
| T022 | tester | Verify 2 infographic templates unchanged | Yes (with T021) | 10m |
| T023 | tester | Verify all schemas unchanged | Yes (with T021, T022) | 10m |
| T026 | code-reviewer | Verify all 6 reference documents load correctly via Read tool | Yes (with T021-T023) | 15m |

### Sequential Regression

| Task | Agent | Description | Est. |
|------|-------|-------------|------|
| T024 | tester | End-to-end `/threat-model` regression: compare output against baseline (finding count, risk distribution, SARIF result count, section presence) | 30m |
| T025 | tester | Validate SARIF output against SARIF 2.1.0 schema structure | 15m |

### Polish

| Task | Agent | Description | Est. |
|------|-------|-------------|------|
| T027 | senior-backend-engineer | Update capability-inventory.md with post-refactoring results, final line counts, deviations | 20m |

**Quality Gate**: All 27 tasks marked complete. Zero regression on threat agents. SARIF validates. End-to-end output structurally equivalent. Feature complete.

---

## Workload Distribution

| Agent | Tasks | Wave 1 | Wave 2 | Wave 3 | Wave 4 | Load |
|-------|-------|--------|--------|--------|--------|------|
| senior-backend-engineer | 17 | T001-T005 | T007-T011 | T013-T015, T017-T019 | T027 | 65% |
| code-reviewer | 4 | -- | T012 | T016, T020 | T026 | 15% |
| tester | 5 | T006 | -- | -- | T021-T025 | 20% |
| orchestrator | -- | Coordinate | Coordinate | Parallel dispatch | Coordinate | Overhead |

**Load Assessment**: senior-backend-engineer carries the bulk of extraction work (65%), which is appropriate -- this is a refactoring feature where most tasks are structured file manipulation. No agent exceeds 80% capacity. code-reviewer and tester are concentrated in verification phases, preventing bottlenecks during extraction waves.

---

## Execution Notes

1. **Wave 2 is the MVP gate**: Do not proceed to Wave 3 until the orchestrator regression passes. A failed extraction approach must be corrected before applying to report and infographic agents.
2. **Wave 3 parallelization**: Stream A and Stream B operate on entirely different files with zero overlap. The orchestrator should dispatch both streams simultaneously.
3. **T009 is the highest-risk task**: Error handling split requires judgment to distinguish pure templates from defensive specification. The plan provides explicit classification. Allow extra time.
4. **Phase vs. Wave terminology**: tasks.md uses "Phase" (1-6); plan.md uses "Wave" (1-4). The mapping is Phase 1+2 = Wave 1, Phase 3 = Wave 2, Phase 4+5 = Wave 3, Phase 6 = Wave 4. The orchestrator should follow tasks.md Phase numbering.
5. **Report agent floor**: If threat-report.md exceeds 400 lines after extraction, document justification per T016 -- the plan acknowledges ~448 lines as a realistic floor.

---

**End of Agent Assignments**
