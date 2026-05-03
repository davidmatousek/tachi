# Agent Assignments: 048 — Infographic Tiered Pipeline Auto-Detection & Residual Risk

**Generated**: 2026-03-28
**Estimated Duration**: 1 session (~45 min with parallelism, ~65 min single-agent)

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001-T005 | `senior-backend-engineer` | Read source files, extract patterns |
| T006-T010 | `senior-backend-engineer` | Command file edits (markdown prompt) |
| T011-T016 | `senior-backend-engineer` | Agent file edits (markdown prompt) |
| T017-T018 | `senior-backend-engineer` | Command file tip edits |
| T019-T022 | `senior-backend-engineer` | Agent file label/template edits |
| T023-T027 | `code-reviewer` | Backward compatibility verification |

## Parallel Execution Waves

### Wave 1: Setup (Read Sources)
**Tasks**: T001, T002, T003, T004, T005
**Agent**: `senior-backend-engineer`
**Parallel**: T002-T005 all run in parallel (different files)
**Duration**: ~5 min

**Quality Gate**: All source files read. Detection patterns and extraction formats available.

### Wave 2: US-1 Core Implementation (Detection + Extraction)
**Tasks**: T006-T016
**Agent**: `senior-backend-engineer`
**Parallel Opportunity**: Command tasks (T006-T010) and agent tasks (T011-T016) target different files — can run with two agents
**Duration**: ~20 min (parallel) / ~35 min (sequential)

| Sub-wave | Tasks | File |
|----------|-------|------|
| 2a | T006-T010 | `.claude/commands/infographic.md` |
| 2b | T011-T016 | `.claude/agents/tachi/threat-infographic.md` |

**Quality Gate**: Three-tier detection working. Residual risk extraction complete. Existing behavior preserved.

### Wave 3: US-2 + US-3 (Tips + Labels)
**Tasks**: T017-T022
**Agent**: `senior-backend-engineer`
**Parallel Opportunity**: US-2 (T017-T018, command file) and US-3 (T019-T021, agent file) target different files — can run in parallel. T022 edits command file after T017-T018.
**Duration**: ~10 min (parallel) / ~15 min (sequential)

| Sub-wave | Tasks | File | User Story |
|----------|-------|------|------------|
| 3a | T017-T018 | `.claude/commands/infographic.md` | US-2 |
| 3b | T019-T021 | `.claude/agents/tachi/threat-infographic.md` | US-3 |
| 3c | T022 | `.claude/commands/infographic.md` | US-3 |

**Quality Gate**: Enhancement tips display at each tier. Risk labels correct per source type.

### Wave 4: Validation
**Tasks**: T023-T027
**Agent**: `code-reviewer`
**Parallel**: T023-T024 and T026-T027 all run in parallel (read-only)
**Duration**: ~5 min

**Quality Gate**: Backward compatibility confirmed. No template or schema files modified. Feature ready for delivery.

## Time Estimates

| Wave | Sequential | Parallel (2 agents) |
|------|-----------|-------------------|
| Wave 1 | 5 min | 5 min |
| Wave 2 | 35 min | 20 min |
| Wave 3 | 15 min | 10 min |
| Wave 4 | 5 min | 5 min |
| **Total** | **~60 min** | **~40 min** |

## Critical Path

```
Setup (Wave 1)
  → US-1 Command (Wave 2a) → US-2 Tips (Wave 3a) → US-3 type_label (Wave 3c) → Validation (Wave 4)
  → US-1 Agent (Wave 2b)   → US-3 Labels (Wave 3b)                           → Validation (Wave 4)
```

The critical path is Wave 1 → Wave 2 → Wave 3 → Wave 4, with the two file tracks running in parallel within each wave.
