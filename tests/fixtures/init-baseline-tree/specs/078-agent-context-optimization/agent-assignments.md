# Agent Assignments: Feature 078 — Agent Context Optimization

**Generated**: 2026-04-01
**Source**: tasks.md + Team-Lead execution wave analysis

## Agent Assignment Matrix

| Task ID | Task Description | Assigned Agent | Rationale |
|---------|-----------------|----------------|-----------|
| T001 | Capture baseline pipeline output | `tester` | Validation/regression capture |
| T002 | Capture baseline line counts | `tester` | Measurement/verification |
| T003 | Add `model:` to 11 leaf agents | `senior-backend-engineer` | Markdown file editing |
| T004 | Add `model:` to 3 methodology agents | `senior-backend-engineer` | Markdown file editing |
| T005 | Add `model:` to 3 report agents | `senior-backend-engineer` | Markdown file editing |
| T006 | Update best practices caps | `senior-backend-engineer` | Markdown documentation |
| T007 | Create trust-zones.md | `senior-backend-engineer` | Skill reference authoring |
| T008 | Create reachability-analysis.md | `senior-backend-engineer` | Skill reference authoring |
| T009 | Create output-formatting.md | `senior-backend-engineer` | Skill reference authoring |
| T010 | Enhance cvss-vectors.md | `senior-backend-engineer` | Skill reference enhancement |
| T011 | Enhance severity-bands.md | `senior-backend-engineer` | Skill reference enhancement |
| T012 | Restructure risk-scorer.md | `senior-backend-engineer` | Agent restructuring |
| T013 | Update risk-scoring SKILL.md | `senior-backend-engineer` | Navigation table update |
| T014 | Prototype regression test | `tester` | Output equivalence verification |
| T015 | Verify risk-scorer line count | `tester` | Measurement/verification |
| T016 | Verify extracted content traceability | `tester` | Content traceability audit |
| T017-T022 | Create orchestrator references | `senior-backend-engineer` | Skill reference authoring |
| T023 | Restructure orchestrator.md | `senior-backend-engineer` | Agent restructuring |
| T024 | Update orchestration SKILL.md | `senior-backend-engineer` | Navigation table update |
| T025-T027 | Verify control-analysis references | `code-reviewer` | Content completeness audit |
| T028 | Restructure control-analyzer.md | `senior-backend-engineer` | Agent restructuring |
| T029 | Update control-analysis SKILL.md | `senior-backend-engineer` | Navigation table update |
| T030-T034 | Report-assembler skill + restructure | `senior-backend-engineer` | New skill + restructuring |
| T035-T039 | Threat-report skill + restructure | `senior-backend-engineer` | New skill + restructuring |
| T040-T045 | Infographic skill + restructure | `senior-backend-engineer` | New skill + restructuring |
| T046-T050 | Shared references | `senior-backend-engineer` | Shared content authoring |
| T051-T053 | Final regression tests | `tester` | Output equivalence verification |
| T054 | Leaf agent byte-identity check | `tester` | Verification |
| T055 | Line count verification | `tester` | Measurement |
| T056 | Finalize best practices | `senior-backend-engineer` | Documentation |
| T057 | Domain data inline check | `code-reviewer` | Content audit |
| T058 | Content traceability audit | `code-reviewer` | Traceability verification |

## Parallel Execution Waves

### Wave 1: Baseline & Setup (parallel)
**Tasks**: T001, T002, T003, T004, T005, T006
**Agents**: `tester` (T001-T002) + `senior-backend-engineer` (T003-T006)
**Parallelism**: 2 tracks
**Estimate**: 1-2 hours

### Wave 2: Risk-Scorer References (parallel)
**Tasks**: T007, T008, T009, T010, T011
**Agents**: `senior-backend-engineer` × 5 parallel
**Parallelism**: 5 tracks (independent files)
**Estimate**: 2-3 hours

### Wave 3: Risk-Scorer Restructure
**Tasks**: T012, T013
**Agents**: `senior-backend-engineer`
**Parallelism**: Sequential (T012 then T013)
**Estimate**: 1-2 hours

### Wave 4: Prototype Gate (BLOCKS remaining work)
**Tasks**: T014, T015, T016
**Agents**: `tester`
**Parallelism**: Sequential
**Estimate**: 1-2 hours
**Quality Gate**: All 3 must pass before Wave 5

### Wave 5: Orchestrator + Control-Analyzer (parallel)
**Tasks**: T017-T024 (orchestrator) + T025-T029 (control-analyzer)
**Agents**: `senior-backend-engineer` (orchestrator) + `code-reviewer` (control-analyzer verify) then `senior-backend-engineer` (restructure)
**Parallelism**: 2 tracks
**Estimate**: 3-4 hours

### Wave 6: Report Agents (3-way parallel)
**Tasks**: T030-T034 (report-assembler) + T035-T039 (threat-report) + T040-T045 (infographic)
**Agents**: `senior-backend-engineer` × 3 parallel tracks
**Parallelism**: 3 tracks (confirmed zero cross-dependencies)
**Estimate**: 3-4 hours

### Wave 7: Shared References
**Tasks**: T046-T050
**Agents**: `senior-backend-engineer`
**Parallelism**: T046-T049 parallel, T050 sequential after
**Estimate**: 1-2 hours

### Wave 8: Final Validation
**Tasks**: T051-T058
**Agents**: `tester` (T051-T055) + `code-reviewer` (T057-T058) + `senior-backend-engineer` (T056)
**Parallelism**: 3 tracks
**Estimate**: 2-3 hours

## Summary

| Metric | Value |
|--------|-------|
| Total waves | 8 (16 sub-waves with parallelism) |
| Max parallelism | 5 (Wave 2: reference file creation) |
| Critical path | Wave 1 → Wave 2 → Wave 3 → Wave 4 (gate) → Wave 5 → Wave 6 → Wave 7 → Wave 8 |
| Total sequential time | 14-22 hours |
| Total with parallelism | 14-16 hours |
| Gate risk | Wave 4 — if prototype fails, diagnose and retry (max 2 retries before architect escalation) |
| Primary agent | `senior-backend-engineer` (42/58 tasks) |
| Validation agent | `tester` (11/58 tasks) |
| Review agent | `code-reviewer` (5/58 tasks) |
