# Agent Assignments: 053 — Risk Reduction Funnel

**Feature**: Risk Reduction Funnel Infographic Template
**Date**: 2026-03-28
**Total Tasks**: 24

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001-T004 (Setup reads) | `senior-backend-engineer` | Reference file reading and pattern analysis |
| T005 (Template skeleton) | `senior-backend-engineer` | Markdown file creation following established pattern |
| T006 (Agent registry) | `senior-backend-engineer` | Markdown file editing (YAML metadata + table rows) |
| T007 (Command registry) | `senior-backend-engineer` | Markdown file editing (valid values list) |
| T008-T012 (US1 template) | `senior-backend-engineer` | Template content authoring (zones, layout, Gemini prompt) |
| T013-T014 (US1 agent) | `senior-backend-engineer` | Agent prompt file editing (data extraction logic) |
| T015, T018 (US2/3 template) | `senior-backend-engineer` | Ghost tier zone spec and Gemini prompt additions |
| T016-T017 (US2/3 agent) | `senior-backend-engineer` | Agent prompt file editing (degradation modes) |
| T019, T021 (US4 template) | `senior-backend-engineer` | Sidebar zone spec and Gemini prompt placeholder |
| T020 (US4 agent) | `senior-backend-engineer` | Agent prompt file editing (sidebar data extraction) |
| T022 (Edge cases) | `senior-backend-engineer` | Agent prompt file editing (edge case handling) |
| T023 (Backward compat) | `tester` | Verification of existing template integrity |
| T024 (Quickstart validation) | `tester` | End-to-end flow validation against examples |

## Parallel Execution Waves

### Wave 1: Setup (Read-Only)
**Tasks**: T001, T002, T003, T004 (all parallel)
**Agent**: `senior-backend-engineer`
**Estimate**: 5 minutes
**Gate**: Reference patterns understood

### Wave 2: Foundational
**Tasks**: T005 (sequential) → T006 + T007 (parallel)
**Agent**: `senior-backend-engineer`
**Estimate**: 15 minutes
**Gate**: `--template risk-funnel` recognized, template file exists

### Wave 3: MVP (Full 4-Tier Funnel)
**Tasks**: T008 → T009 → T010 → T011 → T012 → T013 → T014 (sequential, same files)
**Agent**: `senior-backend-engineer`
**Estimate**: 30 minutes
**Gate**: Full 4-tier funnel generates from compensating-controls.md

### Wave 4: Graceful Degradation + Sidebar (Parallel Tracks)
**Track A**: T015 → T016 → T017 → T018 (ghost tiers)
**Track B**: T019 → T020 → T021 (metrics sidebar)
**Agent**: `senior-backend-engineer`
**Estimate**: 25 minutes (parallel execution)
**Gate**: All 3 data source modes produce correct output

### Wave 5: Polish + Validation
**Tasks**: T022 + T023 (parallel) → T024 (sequential)
**Agents**: `senior-backend-engineer` (T022), `tester` (T023, T024)
**Estimate**: 15 minutes
**Gate**: Edge cases handled, backward compatibility confirmed, quickstart validated

## Timeline Summary

| Wave | Duration | Cumulative | Agent(s) |
|------|----------|------------|----------|
| 1: Setup | 5 min | 5 min | senior-backend-engineer |
| 2: Foundational | 15 min | 20 min | senior-backend-engineer |
| 3: MVP | 30 min | 50 min | senior-backend-engineer |
| 4: Degradation + Sidebar | 25 min | 75 min | senior-backend-engineer |
| 5: Polish + Validation | 15 min | 90 min | senior-backend-engineer, tester |
| **Total** | **~90 min** | | **Single session** |

## Quality Gates

1. **After Wave 2**: Verify `--template risk-funnel` is recognized and template file has 9-section structure
2. **After Wave 3**: Run `/infographic --template risk-funnel` with compensating-controls data — **MVP checkpoint**
3. **After Wave 4**: Test all 3 modes (4-tier, 3-tier, 1-tier) — verify ghost tiers and sidebar
4. **After Wave 5**: Run `/infographic --template all` to verify backward compatibility with existing templates
