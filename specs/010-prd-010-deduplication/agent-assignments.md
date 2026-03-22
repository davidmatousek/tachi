# Agent Assignments: Deduplication & Risk Rating (Feature 010)

**Generated**: 2026-03-22
**Total Tasks**: 24
**Estimated Duration**: ~1.75 hours (85% confidence)

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001-T004 | `senior-backend-engineer` | Schema YAML modifications |
| T005-T008 | `senior-backend-engineer` | Orchestrator prompt authoring (correlation detection) |
| T009 | `senior-backend-engineer` | Template markdown authoring (Section 4a) |
| T010-T014 | `senior-backend-engineer` | Orchestrator prompt authoring (Phase 4 dedup) |
| T015-T016 | `senior-backend-engineer` | Template markdown modifications |
| T017-T018 | `senior-backend-engineer` | Template + orchestrator prompt authoring (risk calibration) |
| T019-T020 | `senior-backend-engineer` | Interface contract markdown updates |
| T021-T022 | `senior-backend-engineer` | Orchestrator validation checklist + frontmatter |
| T023 | `tester` | Integration validation (agentic architecture) |
| T024 | `tester` | Integration validation (non-AI architecture) |

## Parallel Execution Waves

### Wave 1: Schema Foundation
**Tasks**: T001, T002 (sequential)
**Agent**: `senior-backend-engineer`
**Duration**: ~10 min
**Quality Gate**: Schema validates — Correlated Findings section present, version 1.1

### Wave 2: Schema Refinements
**Tasks**: T003, T004 (serialize — both target same YAML block per Team-Lead F-1)
**Agent**: `senior-backend-engineer`
**Duration**: ~5 min
**Quality Gate**: Coverage Matrix schema has three-state cell model and dedup_note

### Wave 3: Correlation + Template (partial parallel)
**Tasks**: T005-T008 (sequential), T009 (parallel with T005-T008), T017 (parallel — US3 independent)
**Agents**: `senior-backend-engineer` × 2 (if parallel capacity available)
**Duration**: ~25 min
**Quality Gate**: Orchestrator has complete correlation detection logic; Template has Section 4a; Template has Risk Calibration Matrix

### Wave 4: Dedup Counts + Template Updates
**Tasks**: T010-T014 (sequential), T015-T016 (parallel after T014), T018 (after T014 per Team-Lead F-2)
**Agent**: `senior-backend-engineer`
**Duration**: ~25 min
**Quality Gate**: Orchestrator Phase 4 produces deduplicated counts; Template reflects dedup format

### Wave 5: Polish (mostly parallel)
**Tasks**: T019 [P], T020 [P], T021, T022
**Agent**: `senior-backend-engineer`
**Duration**: ~15 min
**Quality Gate**: `code-reviewer` review of all 4 modified files before integration testing

### Wave 6: Integration Validation
**Tasks**: T023, T024 (sequential)
**Agent**: `tester`
**Duration**: ~15 min
**Quality Gate**: Both example architectures produce correct output per success criteria SC-001 through SC-007

## Quality Gates Between Waves

| Gate | Between | Check |
|------|---------|-------|
| G1 | Wave 2 → Wave 3 | Schema v1.1 complete with all new fields |
| G2 | Wave 3 → Wave 4 | Correlation detection self-check passes; Section 4a present |
| G3 | Wave 4 → Wave 5 | Coverage matrix and risk summary produce dedup counts |
| G4 | Wave 5 → Wave 6 | `code-reviewer` validates all modified files |
| G5 | Wave 6 → Done | Integration tests pass on both example architectures |

## Critical Path

```
T001 → T002 → T005 → T006 → T007 → T008 → T010 → T011 → T012 → T013 → T014 → T021 → T023 → T024
```

**Critical path length**: 14 tasks (~1.5 hours)
**Parallel savings**: T003/T004, T009, T015-T016, T017-T018, T019-T020 run off critical path

## Implementation Notes

- **Schema version propagation** (Architect M-02): When executing T015, T016, and T021, also update schema_version references from "1.0" to "1.1" in the files being modified.
- **T003/T004 serialization** (Team-Lead F-1): Execute T003 before T004 — both modify Coverage Matrix in output.yaml.
- **T018 sequencing** (Team-Lead F-2): Execute T018 after T014 completes — both modify orchestrator.md Risk Summary area.
