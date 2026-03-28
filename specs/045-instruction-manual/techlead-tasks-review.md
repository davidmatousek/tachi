# Team Lead Tasks Review: 045 — End-to-End tachi Instruction Manual

**Reviewer**: team-lead
**Date**: 2026-03-28
**Artifact**: `specs/045-instruction-manual/tasks.md`
**Context**: `spec.md` (PM APPROVED), `plan.md` (PM APPROVED, Architect APPROVED_WITH_CONCERNS)

---

## 1. Feasibility Assessment (4 Dimensions)

### Effort

| Work Stream | Tasks | Estimated Effort | Notes |
|-------------|-------|-----------------|-------|
| Setup (source reading) | T001-T006 | Low (~15 min) | Reading existing files, no writing |
| Prompt Spec Update (US4) | T007-T015 | Medium (~60-90 min) | 9 tasks editing one file + rename + reference search |
| Pipeline Guide (US1+US2) | T016-T019 | Medium-High (~60-90 min) | 4 tasks but each is substantial (200-250 lines each) |
| Quick Start (US3) | T020 | Low (~10 min) | Single callout insertion |
| OpenClaw Example (US5) | T021-T023 | Medium (~30-45 min) | 3 sequential extensions to worked example |
| Appendix Updates (US6) | T024-T026 | Medium (~20-30 min) | Reference material, some parallelizable |
| Validation (Phase 7) | T027-T031 | Medium (~20-30 min) | Cross-referencing, consistency checks |

**Total estimated effort**: 3.5-5 hours (single-agent serial), 2-3 hours with parallelism.

### Capacity

This is a documentation-only feature modifying 2 primary files. Agent requirements are modest:
- **senior-backend-engineer**: Primary writer for all markdown content
- **web-researcher**: Source material reading in Phase 1
- **code-reviewer**: Validation phase cross-checks

No capacity concerns. Workload is well within agent limits.

### Timeline

| Scenario | Estimate |
|----------|----------|
| Optimistic | 2 hours (maximum parallelism, no revisions) |
| Realistic | 3.5 hours (moderate parallelism, minor revisions) |
| Pessimistic | 5 hours (serial execution, content revisions needed) |

### Dependencies

| Dependency | Type | Status | Risk |
|------------|------|--------|------|
| Features 035, 036, 039 stable | External | RESOLVED (confirmed in spec assumptions) | None |
| Command specs in adapters/ and .claude/ | Internal | Available | Low |
| Existing guide structure sound | Internal | Confirmed in spec | None |
| PM sign-off on spec | Governance | APPROVED | None |
| Architect sign-off on plan | Governance | APPROVED_WITH_CONCERNS (non-blocking) | None |

**Verdict**: FEASIBLE

**Confidence**: HIGH (90%) -- documentation-only scope with clear inputs, no code risk, no external dependencies.

---

## 2. Task Granularity Assessment

### Findings

| Finding | Severity | Details |
|---------|----------|---------|
| Phase 1 granularity is appropriate | OK | 6 read tasks map 1:1 to source files. Clear and auditable. |
| Phase 2 granularity is appropriate | OK | 9 tasks for prompt spec, one per logical section. Correctly separates content additions from factual corrections and rename. |
| Phase 3 tasks are individually large | LOW | T017, T018, T019 each produce 200-250 lines. Acceptable for docs-only work since each is a self-contained command section following the same template. |
| Phase 4 is correctly minimal | OK | Single task (T020) for a focused callout. No over-splitting. |
| Phase 5 is well-scoped | OK | 3 tasks for 3 sequential OpenClaw extension steps. Natural decomposition. |
| Phase 6 parallelism correctly identified | OK | T024 and T025 edit different appendix subsections. T026 (glossary) is separate. |
| Phase 7 validation is thorough | OK | 5 validation tasks covering path references, command accuracy, parity, links, and consistency. |

**Granularity verdict**: APPROPRIATE. The 31-task breakdown is well-sized for the scope. No tasks are too coarse (each has a clear deliverable) and none are over-split (no single-line editing tasks).

---

## 3. Critical Path Analysis

### Identified Critical Path

```
Phase 1 (Setup) --> Phase 2 (Prompt Spec US4) --> Phase 3 (Pipeline Guide US1+US2)
    --> Phase 4 (Quick Start US3) --> Phase 7 (Validation)
```

**Assessment**: CORRECT. The tasks.md correctly identifies that:
1. Phase 2 (prompt spec) BLOCKS Phase 3 (guide) -- source of truth must be updated first
2. Phase 3 BLOCKS Phases 4, 5, 6 -- command sections must exist before Quick Start can reference them, OpenClaw can extend them, and Appendices can detail their outputs
3. Phase 7 depends on all prior phases

**One observation**: The critical path runs through US4 -> US1+US2 -> US3, not through US5 or US6. This is correctly reflected in the Implementation Strategy's MVP definition (Phases 1-3 satisfy P0 criteria).

---

## 4. Parallel Execution Opportunities

### Current State (from tasks.md)

The tasks.md identifies 12 tasks marked [P] for parallel execution. Let me validate and expand.

### Validated Wave Strategy

| Wave | Tasks | Parallel? | Rationale |
|------|-------|-----------|-----------|
| Wave 1 | T001 | Serial | Must read prompt spec first (primary editing target) |
| Wave 2 | T002, T003, T004, T005, T006 | PARALLEL | All read different source files. No dependencies. |
| Wave 3 | T007, T008, T009 | Serial within wave | All edit same file (GUIDE_PROMPT.md) sequentially |
| Wave 3b | T012 | PARALLEL with T010-T011 | Factual corrections are independent of workflow/artifact sections |
| Wave 4 | T010, T011 | Serial (same file, adjacent sections) | Pipeline workflow + output artifacts in prompt spec |
| Wave 5 | T013 | Serial | OpenClaw extension in prompt spec (depends on T007-T009 for context) |
| Wave 6 | T014, T015 | Serial | Rename + reference update (T015 depends on T014) |
| Wave 7 | T016 | Serial | Pipeline overview in dev guide (first insertion establishes section numbering) |
| Wave 8 | T017, T018, T019 | Serial | All insert into dev guide sequentially (section ordering matters) |
| Wave 9 | T020 | Serial | Quick Start callout (needs section references from Wave 8) |
| Wave 10 | T021, T022, T023 | Serial | OpenClaw steps 11-13 must be sequential |
| Wave 10b | T024, T025 | PARALLEL with Wave 10 | Different appendix subsections. Can run alongside OpenClaw. |
| Wave 11 | T026 | Serial | Glossary terms (depends on Appendix sections existing) |
| Wave 12 | T027, T028, T029, T030, T031 | MIXED | T028+T029 parallel; T027, T030, T031 serial (cross-cutting) |

### Parallelism Assessment

**Claim in tasks.md**: 12 tasks marked [P].

**My assessment**: The parallel opportunities are somewhat constrained by the fact that most tasks edit the same 2 files. True parallelism is limited to:
- Wave 2: 5 source-reading tasks (T002-T006) -- VALID
- Wave 3b: T012 can run with T010-T011 -- VALID but minor
- Wave 10/10b: US5 and US6 can overlap if editing different sections -- VALID but risky (same file)
- Wave 12: T028+T029 validation checks -- VALID

**Finding (LOW)**: The 12 [P] markers are optimistic for same-file editing. In practice, parallel execution on the same markdown file risks merge conflicts. However, for an agentic workflow where tasks are executed sequentially by a single agent (senior-backend-engineer), this is a documentation concern, not a blocking issue. The orchestrator should execute same-file tasks serially and only parallelize cross-file tasks.

**Recommendation**: Reduce advertised parallelism from 12 to 7-8 truly independent parallel slots. Same-file tasks should be executed serially regardless of [P] markers.

---

## 5. Time Estimates Validation

This is a documentation-only feature. Time estimates should reflect:
- Reading: ~2-5 min per source file
- Writing new sections: ~10-20 min per section (agentic markdown generation)
- Validation: ~5-10 min per check

The plan estimates ~1,000-1,400 lines of new content across 2 files. For an AI agent generating documentation, this is achievable in a single session.

**Assessment**: Realistic estimates align with a 3.5-hour window. No timeline inflation needed.

---

## 6. Agent Assignments

### Valid Agent Registry (from `.claude/agents/_README.md`)

Available `subagent_type` names:
- architect, code-reviewer, debugger, devops, frontend-developer, orchestrator
- product-manager, security-analyst, senior-backend-engineer, team-lead
- tester, ux-ui-designer, web-researcher

### Task-to-Agent Mapping

| Task | Agent (`subagent_type`) | Rationale |
|------|------------------------|-----------|
| T001 | senior-backend-engineer | Read and analyze prompt spec structure |
| T002 | senior-backend-engineer | Read and analyze developer guide structure |
| T003 | senior-backend-engineer | Read risk-score command spec |
| T004 | senior-backend-engineer | Read compensating-controls command spec |
| T005 | senior-backend-engineer | Read infographic command spec |
| T006 | senior-backend-engineer | Read interface contract |
| T007 | senior-backend-engineer | Write risk-score section in prompt spec |
| T008 | senior-backend-engineer | Write compensating-controls section in prompt spec |
| T009 | senior-backend-engineer | Write infographic section in prompt spec |
| T010 | senior-backend-engineer | Write post-pipeline workflow section in prompt spec |
| T011 | senior-backend-engineer | Update output artifacts section in prompt spec |
| T012 | senior-backend-engineer | Correct factual errors in prompt spec |
| T013 | senior-backend-engineer | Extend OpenClaw example in prompt spec |
| T014 | senior-backend-engineer | Execute git mv rename |
| T015 | senior-backend-engineer | Search and update references to old filename |
| T016 | senior-backend-engineer | Insert pipeline workflow section in dev guide |
| T017 | senior-backend-engineer | Insert risk-score section in dev guide |
| T018 | senior-backend-engineer | Insert compensating-controls section in dev guide |
| T019 | senior-backend-engineer | Insert infographic section in dev guide |
| T020 | senior-backend-engineer | Add Quick Start callout in dev guide |
| T021 | senior-backend-engineer | Extend OpenClaw Step 11 (risk-score) |
| T022 | senior-backend-engineer | Extend OpenClaw Step 12 (compensating-controls) |
| T023 | senior-backend-engineer | Extend OpenClaw Step 13 (infographic) |
| T024 | senior-backend-engineer | Expand Appendix B (risk-scores structure) |
| T025 | senior-backend-engineer | Expand Appendix B (compensating-controls structure) |
| T026 | senior-backend-engineer | Add glossary terms to Appendix C |
| T027 | code-reviewer | Verify internal file path references |
| T028 | code-reviewer | Verify command invocations match specs |
| T029 | code-reviewer | Verify prompt spec and guide parity |
| T030 | code-reviewer | Verify README.md link resolution |
| T031 | code-reviewer | Review full guide consistency |

### Agent Load Summary

| Agent | Task Count | Load % | Status |
|-------|-----------|--------|--------|
| senior-backend-engineer | 26 | ~84% | ACCEPTABLE (docs-only, sequential by design) |
| code-reviewer | 5 | ~16% | LIGHT |
| web-researcher | 0 | 0% | NOT NEEDED (source files are local, not web) |

**Note on senior-backend-engineer load**: At 84% this slightly exceeds the 80% target. However, this is a documentation-only feature where all tasks are markdown editing. The senior-backend-engineer is the only appropriate agent for this work (no frontend, no infra, no security code). The 84% reflects task count, not complexity. Each task is bounded and well-defined. This is acceptable.

**Note on web-researcher**: Initially considered for Phase 1 (reading source materials), but all source files are local repository files, not web resources. The senior-backend-engineer reads local files as part of its normal workflow. web-researcher is not needed.

---

## 7. Wave Execution Strategy

### Recommended Waves for Orchestrator

```
WAVE 1: Setup (Read Sources)
  Agent: senior-backend-engineer
  Tasks: T001 (serial), then T002-T006 (parallel -- different files)
  Checkpoint: All source materials read

WAVE 2: Prompt Spec Content (US4)
  Agent: senior-backend-engineer
  Tasks: T007 -> T008 -> T009 -> T010 -> T011 (serial, same file)
  Parallel slot: T012 can run with T010-T011 (factual corrections)
  Tasks: T013 (after T007-T009, needs context)
  Checkpoint: Prompt spec content complete

WAVE 3: Prompt Spec Rename (US4)
  Agent: senior-backend-engineer
  Tasks: T014 -> T015 (serial, rename then update references)
  Checkpoint: Prompt spec renamed, references updated

WAVE 4: Developer Guide Core (US1+US2)
  Agent: senior-backend-engineer
  Tasks: T016 -> T017 -> T018 -> T019 (serial, same file, section order matters)
  Checkpoint: All 4 command sections in dev guide

WAVE 5: Quick Start + OpenClaw + Appendices (US3+US5+US6)
  Agent: senior-backend-engineer
  Tasks:
    - T020 (Quick Start callout)
    - T021 -> T022 -> T023 (OpenClaw steps, serial)
    - T024, T025 (Appendix B, can interleave with OpenClaw)
    - T026 (Glossary)
  Note: All edit same file but different sections. Execute serially for safety.
  Checkpoint: All content complete

WAVE 6: Validation
  Agent: code-reviewer
  Tasks:
    - T027 (path references -- serial, cross-cutting)
    - T028 + T029 (parallel -- different validation targets)
    - T030 (README link -- serial)
    - T031 (full consistency review -- serial, must be last)
  Checkpoint: All validation passed
```

---

## 8. Findings Summary

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | LOW | Parallel markers [P] on same-file tasks are optimistic | Orchestrator should execute same-file tasks serially; true parallelism is cross-file only |
| 2 | LOW | senior-backend-engineer load at 84% exceeds 80% target | Acceptable for docs-only feature. No alternative agent is more appropriate. |
| 3 | INFO | Phase 1 tasks (T001-T006) are reading tasks, not writing | These could be absorbed into the first writing task of each phase, but explicit read tasks improve auditability. Keep as-is. |
| 4 | INFO | No web-researcher tasks needed | All source materials are local files. Initial expectation of web-researcher usage does not apply. |
| 5 | INFO | Architect concern noted in plan review (compensating-controls command path) | Tasks T004 and T028 should verify both `.claude/commands/` and `adapters/` locations per Architect feedback |

---

## 9. Compliance Checks

| Check | Status |
|-------|--------|
| All 31 tasks have clear deliverables | PASS |
| All tasks map to spec FRs (FR-001 through FR-015) | PASS |
| All 6 user stories have task coverage | PASS |
| MVP scope (Phases 1-3) correctly identified | PASS |
| Phase dependencies correctly sequenced | PASS |
| Critical path identified and correct | PASS |
| No code changes (docs-only confirmed) | PASS |
| No deployment required | PASS |
| Agent assignments use only valid subagent_type names | PASS |

---

## 10. Sign-off

**Verdict**: APPROVED

**Rationale**: The 31-task breakdown is well-structured for a documentation-only feature. Task granularity is appropriate -- neither too coarse nor over-split. The critical path through US4 -> US1+US2 -> US3 is correctly identified. Phase dependencies are sound. Time estimates are realistic. The two LOW findings (optimistic parallelism markers and slightly high agent load) are non-blocking and do not affect deliverability. Agent assignments map cleanly to senior-backend-engineer (content) and code-reviewer (validation) using valid registry names.

**Conditions**: None (both LOW findings are informational).

---

**End of Team Lead Tasks Review**
