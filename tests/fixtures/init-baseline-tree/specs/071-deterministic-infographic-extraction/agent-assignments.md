# Agent Assignments: Deterministic Infographic Extraction

## Agent Assignment Matrix

| Task Range | Agent | Rationale |
|-----------|-------|-----------|
| T001-T007 | `senior-backend-engineer` | Python module extraction, refactoring, import rewiring |
| T008-T018 | `senior-backend-engineer` | Core Python script implementation |
| T019-T020 | `senior-backend-engineer` | Baseball card template data |
| T021-T023 | `tester` | Baseball card verification and determinism testing |
| T024-T026 | `senior-backend-engineer` | System architecture template data |
| T027-T028 | `tester` | System architecture verification and determinism testing |
| T029-T032 | `senior-backend-engineer` | Risk funnel template data |
| T033-T035 | `tester` | Risk funnel verification and determinism testing |
| T036-T038 | `tester` | Cross-output consistency verification |
| T039-T041 | `senior-backend-engineer` | Agent prompt update (markdown editing) |
| T042 | `tester` | End-to-end integration test |
| T043-T044 | `tester` | Full template verification across fixtures |
| T045 | `tester` | Final regression check |
| T046 | `code-reviewer` | Schema validation and invariant spot-check |

## Parallel Execution Waves

### Wave 1: Setup (Sequential)
**Tasks**: T001 → T002 → T003 → T004 → T005 → T006 → T007
**Agent**: `senior-backend-engineer`
**Gate**: T007 must pass (byte-identical output) before Wave 2

### Wave 2: Foundational (Sequential)
**Tasks**: T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018
**Agent**: `senior-backend-engineer`
**Gate**: Core script produces valid JSON skeleton before Wave 3

### Wave 3: Templates (Parallel — 3 streams + 1 cross-cutting)

| Stream | Tasks | Agent |
|--------|-------|-------|
| 3A: Baseball Card | T019 → T020 → T021 → T022 → T023 | `senior-backend-engineer` (impl) → `tester` (verify) |
| 3B: System Architecture | T024 → T025 → T026 → T027 → T028 | `senior-backend-engineer` (impl) → `tester` (verify) |
| 3C: Risk Funnel | T029 → T030 → T031 → T032 → T033 → T034 → T035 | `senior-backend-engineer` (impl) → `tester` (verify) |
| 3D: Cross-Output | T036 → T037 → T038 | `tester` |

**Gate**: All streams complete before Wave 4

### Wave 4: Agent Update (Sequential)
**Tasks**: T039 → T040 → T041 → T042
**Agent**: `senior-backend-engineer` (prompt) → `tester` (E2E)
**Gate**: End-to-end `/infographic` works before Wave 5

### Wave 5: Polish (Parallel)
**Tasks**: T043, T044, T045, T046
**Agents**: `tester` (T043-T045), `code-reviewer` (T046)

## Quality Gates

| Gate | Location | Condition | Blocks |
|------|----------|-----------|--------|
| G1 | After T007 | `extract-report-data.py` byte-identical output | Wave 2 |
| G2 | After T018 | Core script produces valid JSON | Wave 3 |
| G3 | After Wave 3 | All templates deterministic + cross-output consistent | Wave 4 |
| G4 | After T042 | End-to-end `/infographic` works | Wave 5 |

## Time Estimates

| Wave | Estimated Duration | Notes |
|------|-------------------|-------|
| Wave 1 (Setup) | 1 session | Mechanical extraction, low risk |
| Wave 2 (Foundational) | 1 session | Core algorithms, highest complexity |
| Wave 3 (Templates) | 1 session (parallel) | 3 streams in parallel reduce wall time |
| Wave 4 (Agent Update) | 0.5 session | Prompt editing + E2E test |
| Wave 5 (Polish) | 0.5 session | Verification only |
| **Total** | **3-4 sessions** | Conservative estimate |
