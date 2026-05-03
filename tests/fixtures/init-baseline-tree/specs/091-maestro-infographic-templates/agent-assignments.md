# Agent Assignments: Feature 091 — MAESTRO Infographic Templates and PDF Report Section

**Feature**: 091-maestro-infographic-templates
**Generated**: 2026-04-08
**Feasibility**: APPROVED (3-day estimate, 80% confidence)
**Total Tasks**: 25 (T001-T025)
**Waves**: 5

---

## Agent Assignment Matrix

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Verify Feature 084 MAESTRO data in examples | tester | Validation of existing data |
| T002 | Verify existing infographic baseline | tester | Regression baseline verification |
| T003 | Add MAESTRO layer parsing function | senior-backend-engineer | Python script logic |
| T004 | Add component-to-layer mapping function | senior-backend-engineer | Python script logic |
| T005 | Add per-finding MAESTRO layer extraction | senior-backend-engineer | Python script logic |
| T006 | Add compute_maestro_heatmap() function | senior-backend-engineer | Python script logic |
| T007 | Add most_exposed_layer computation | senior-backend-engineer | Python script logic |
| T008 | Extend CLI --template choices | senior-backend-engineer | Python script modification |
| T009 | Add maestro-stack template data branch | senior-backend-engineer | Python script logic |
| T010 | Add maestro-heatmap template data branch | senior-backend-engineer | Python script logic |
| T011 | Add MAESTRO fallback handling | senior-backend-engineer | Python defensive logic |
| T012 | Validate extraction against examples | tester | End-to-end extraction validation |
| T013 | Create infographic-maestro-stack.md template | senior-backend-engineer | Markdown template file |
| T014 | Add maestro-stack Section 5 format | senior-backend-engineer | Reference file update |
| T015 | Create infographic-maestro-heatmap.md template | senior-backend-engineer | Markdown template file |
| T016 | Add maestro-heatmap Section 5 format | senior-backend-engineer | Reference file update |
| T017 | Create maestro-findings.typ | senior-backend-engineer | Typst template file |
| T018 | Extend extract-report-data.py | senior-backend-engineer | Python script logic |
| T019 | Extend main.typ with MAESTRO imports | senior-backend-engineer | Typst template modification |
| T020 | Update typst-template-contract.md | senior-backend-engineer | Reference file update |
| T021 | Update SKILL.md with maestro shorthand | senior-backend-engineer | Skill file update |
| T022 | Update INFOGRAPHIC_TEMPLATES.md | senior-backend-engineer | Documentation file |
| T023 | Validate all 6 example architectures | tester | Cross-example validation |
| T024 | Regression test existing templates | tester | Regression testing |
| T025 | End-to-end PDF validation | tester | Full pipeline validation |

**Summary**: 19 tasks assigned to senior-backend-engineer, 6 tasks assigned to tester.

---

## Parallel Execution Waves

### Wave 1: Setup (Phase 1)

**Purpose**: Verify prerequisites and baselines before any implementation.
**Estimated Duration**: 15 minutes
**Parallelism**: 2 tasks in parallel

| Slot | Task | Agent | Notes |
|------|------|-------|-------|
| A | T001 — Verify MAESTRO data exists | tester | Independent |
| B | T002 — Verify infographic baseline | tester | Independent |

**Quality Gate**: Both verifications pass. MAESTRO data confirmed in examples. Baseline extraction produces valid JSON.

---

### Wave 2: Extraction Foundation (Phase 2)

**Purpose**: Build all MAESTRO data extraction logic. BLOCKS all downstream visualization work.
**Estimated Duration**: 3-4 hours
**Parallelism**: Limited — sequential with two parallel pairs

| Step | Task | Agent | Dependencies |
|------|------|-------|--------------|
| 2a (parallel) | T003 — Layer parsing function | senior-backend-engineer | Wave 1 |
| 2a (parallel) | T004 — Component-to-layer mapping | senior-backend-engineer | Wave 1 |
| 2b | T005 — Per-finding layer extraction | senior-backend-engineer | T003 |
| 2c | T006 — compute_maestro_heatmap() | senior-backend-engineer | T004, T005 |
| 2d | T007 — most_exposed_layer computation | senior-backend-engineer | T003 |
| 2e | T008 — Extend CLI --template choices | senior-backend-engineer | T003 |
| 2f (parallel) | T009 — maestro-stack data branch | senior-backend-engineer | T003, T005, T007 |
| 2f (parallel) | T010 — maestro-heatmap data branch | senior-backend-engineer | T006 |
| 2g | T011 — MAESTRO fallback handling | senior-backend-engineer | T003-T010 |
| 2h | T012 — Validate extraction | tester | T011 |

**Quality Gate**: Extraction validated. Both `--template maestro-stack` and `--template maestro-heatmap` produce correct JSON from `examples/agentic-app/sample-report/`. Fallback returns empty fields without errors on MAESTRO-less inputs.

---

### Wave 3: Templates + PDF (Phases 3, 4, 5 — PARALLEL)

**Purpose**: Build all three visualization stories in parallel. This is the primary parallelization opportunity.
**Estimated Duration**: 2-3 hours (wall clock, running 3 streams in parallel)
**Parallelism**: 3 independent streams on different files

| Stream | Task | Agent | Dependencies |
|--------|------|-------|--------------|
| **Stream A: US-01 maestro-stack** | | | |
| A1 | T013 — Create infographic-maestro-stack.md | senior-backend-engineer | Wave 2 |
| A2 | T014 — Add stack Section 5 format | senior-backend-engineer | T013 |
| **Stream B: US-02 maestro-heatmap** | | | |
| B1 | T015 — Create infographic-maestro-heatmap.md | senior-backend-engineer | Wave 2 |
| B2 | T016 — Add heatmap Section 5 format | senior-backend-engineer | T015 |
| **Stream C: US-03 PDF report** | | | |
| C1 (parallel) | T017 — Create maestro-findings.typ | senior-backend-engineer | Wave 2 |
| C1 (parallel) | T018 — Extend extract-report-data.py | senior-backend-engineer | Wave 2 |
| C2 | T019 — Extend main.typ | senior-backend-engineer | T017 |
| C3 | T020 — Update typst-template-contract.md | senior-backend-engineer | T018 |

**Quality Gate**: All three streams complete. maestro-stack template renders. maestro-heatmap template renders. PDF MAESTRO Findings page appears with correct layer groupings.

---

### Wave 4: Shorthand (Phase 6)

**Purpose**: Add convenience shorthand that depends on both templates existing.
**Estimated Duration**: 30 minutes
**Parallelism**: Single task

| Slot | Task | Agent | Dependencies |
|------|------|-------|--------------|
| A | T021 — Update SKILL.md with maestro shorthand | senior-backend-engineer | T013, T015 (Streams A + B) |

**Quality Gate**: Running `/infographic` with `maestro` template generates both maestro-stack and maestro-heatmap spec+image pairs.

---

### Wave 5: Polish + Validation (Phase 7)

**Purpose**: Documentation, cross-example validation, and regression testing.
**Estimated Duration**: 1-1.5 hours
**Parallelism**: 3 tasks in parallel, then 1 sequential

| Step | Task | Agent | Dependencies |
|------|------|-------|--------------|
| 5a (parallel) | T022 — Update INFOGRAPHIC_TEMPLATES.md | senior-backend-engineer | Wave 4 |
| 5a (parallel) | T023 — Validate all 6 examples | tester | Wave 4 |
| 5a (parallel) | T024 — Regression test existing templates | tester | Wave 2 |
| 5b | T025 — End-to-end PDF validation | tester | Waves 3 + 4 |

**Quality Gate**: All 6 examples produce correct output. Zero regression on existing templates. Full PDF report generates with MAESTRO section in correct page sequence.

---

## Execution Summary

| Wave | Phase | Duration | Tasks | Parallel Slots | Agents |
|------|-------|----------|-------|----------------|--------|
| 1 | Setup | 15 min | 2 | 2 | tester |
| 2 | Extraction | 3-4 hrs | 10 | 2 (limited) | senior-backend-engineer, tester |
| 3 | Templates + PDF | 2-3 hrs | 8 | 3 streams | senior-backend-engineer |
| 4 | Shorthand | 30 min | 1 | 1 | senior-backend-engineer |
| 5 | Polish + Validation | 1-1.5 hrs | 4 | 3 + 1 | senior-backend-engineer, tester |

**Total Wall Clock**: 7-9 hours (optimistic-realistic range)
**Critical Path**: Wave 1 -> Wave 2 -> Wave 3 Stream C -> Wave 4 -> Wave 5 T025

---

## Agent Workload

| Agent | Task Count | Waves Active | Load |
|-------|-----------|-------------|------|
| senior-backend-engineer | 19 | 2, 3, 4, 5 | Primary — 76% of tasks |
| tester | 6 | 1, 2, 5 | Supporting — 24% of tasks |

---

**End of Agent Assignments**
