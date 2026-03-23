# Agent Assignments: Threat Infographic Agent (F-018)

**Generated**: 2026-03-23
**Total Tasks**: 18
**Estimated Duration**: 2.3–3.0 hours (with parallelism)

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001 | `senior-backend-engineer` | Schema authoring (YAML) |
| T002 | `senior-backend-engineer` | Agent prompt file creation (markdown) |
| T003 | `senior-backend-engineer` | Agent prompt section authoring |
| T004 | `senior-backend-engineer` | Agent prompt section authoring |
| T005 | `senior-backend-engineer` | Agent prompt section authoring |
| T006 | `senior-backend-engineer` | Agent prompt section authoring |
| T007 | `senior-backend-engineer` | Agent prompt section authoring |
| T008 | `senior-backend-engineer` | Agent prompt section authoring (Gemini) |
| T009 | `senior-backend-engineer` | Agent prompt section authoring (API) |
| T010 | `senior-backend-engineer` | Agent prompt section authoring (error handling) |
| T011 | `senior-backend-engineer` | Orchestrator modification (frontmatter) |
| T012 | `senior-backend-engineer` | Orchestrator modification (pipeline description) |
| T013 | `senior-backend-engineer` | Orchestrator modification (Phase 6 dispatch) |
| T014 | `senior-backend-engineer` | Orchestrator modification (opt-out config) |
| T015 | `senior-backend-engineer` | Orchestrator modification (validation checks) |
| T016 | `senior-backend-engineer` | Sample output generation |
| T017 | `code-reviewer` | Data accuracy validation |
| T018 | `code-reviewer` | Quickstart consistency validation |

## Parallel Execution Waves

### Wave 1: Schema Foundation
**Duration**: ~15 min | **Agents**: 1

| Task | Agent | Description |
|------|-------|-------------|
| T001 | `senior-backend-engineer` (A) | Create `schemas/infographic.yaml` |

**Quality Gate**: Schema file exists and follows `report.yaml` structural pattern.

---

### Wave 2: Core Agent Prompt (US-1)
**Duration**: ~55–80 min | **Agents**: 1

| Task | Agent | Description |
|------|-------|-------------|
| T002 | `senior-backend-engineer` (A) | Create agent file with YAML frontmatter |
| T003 | `senior-backend-engineer` (A) | Core Mission section |
| T004 | `senior-backend-engineer` (A) | Input Contract section |
| T005 | `senior-backend-engineer` (A) | Data Extraction Methodology |
| T006 | `senior-backend-engineer` (A) | Infographic Specification Format |
| T007 | `senior-backend-engineer` (A) | Quality Standards / Validation Checklist |

**Quality Gate**: Agent can produce `threat-infographic-spec.md` with correct 6-section structure. US-1 MVP testable.

---

### Wave 3: Gemini + Orchestrator (US-2 || US-4)
**Duration**: ~37–60 min | **Agents**: 2 (parallel)

**Track A — Gemini API (US-2)**:

| Task | Agent | Description |
|------|-------|-------------|
| T008 | `senior-backend-engineer` (A) | Gemini prompt construction |
| T009 | `senior-backend-engineer` (A) | Gemini API integration |
| T010 | `senior-backend-engineer` (A) | Error handling & graceful degradation |

**Track B — Orchestrator Integration (US-4)**:

| Task | Agent | Description |
|------|-------|-------------|
| T011 | `senior-backend-engineer` (B) | Update orchestrator frontmatter |
| T012 | `senior-backend-engineer` (B) | Update pipeline description |
| T013 | `senior-backend-engineer` (B) | Add Phase 6 dispatch section |
| T014 | `senior-backend-engineer` (B) | Add opt-out configuration |
| T015 | `senior-backend-engineer` (B) | Add output validation checks |

**Quality Gate**: Agent handles Gemini API with graceful fallback. Orchestrator dispatches Phase 6. US-2 and US-4 independently testable.

---

### Wave 4: Validation & Polish
**Duration**: ~30–45 min | **Agents**: 2 (parallel)

| Task | Agent | Description |
|------|-------|-------------|
| T016 | `senior-backend-engineer` (A) | Generate sample infographic spec |
| T017 | `code-reviewer` (C) | Validate data accuracy |
| T018 | `code-reviewer` (C) | Validate quickstart consistency |

**Quality Gate**: Sample output passes data accuracy checks. Quickstart documentation consistent. Feature ready for delivery.

---

## Time Estimates

| Scenario | Duration | Notes |
|----------|----------|-------|
| Optimistic (2 agents, parallel) | 2.3 hours | Waves 3 tracks run in parallel |
| Realistic (2 agents, parallel) | 3.0 hours | Account for context loading and review |
| Pessimistic (2 agents, parallel) | 4.1 hours | Account for Gemini API issues |
| Sequential (1 agent) | 3.25–4.75 hours | All tasks serial |

## Notes

- All tasks are markdown/YAML authoring — `senior-backend-engineer` is the correct agent for file creation/editing
- Wave 3 is the key parallelization opportunity: two agents working on different files simultaneously
- `code-reviewer` validates output quality in Wave 4 — separate from authoring agent for independence
- Single-file bottleneck in Wave 2 (T002-T007 all target same file) is a structural constraint, not mitigable
