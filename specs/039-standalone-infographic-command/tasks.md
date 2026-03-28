---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "5/5 user stories covered, 14/14 FRs mapped, MVP correctly scoped at Phase 1+2. No scope creep."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "T011 may be no-op (skip-infographic refs live in orchestrator, not threat-model.md). All other dependency ordering, parallelism, and ADR compliance checks pass."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED
    notes: "Feasibility confirmed at 85% confidence. MVP (9 tasks) realistic for 1 session. Total (34 tasks) fits 1-2 sessions. Wave parallelism valid. All agent names valid."
---

# Tasks: Standalone /infographic Command

**Input**: Design documents from `specs/039-standalone-infographic-command/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story. US-1, US-2, US-3 share the command file and are combined into a single phase. US-5 (pipeline cleanup) spans two phases (canonical + adapters).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Foundational (Infographic Agent Enhancement)

**Purpose**: Add dual-path data extraction to the infographic agent — BLOCKS the `/infographic` command from consuming `risk-scores.md`

- [X] T001 Add dual-path data extraction section to `.claude/agents/tachi/threat-infographic.md` — add a new "Data Source Detection" section that detects input type from content structure: `## 2. Scored Threat Table` with `Composite` column = risk-scores.md; `## 6. Risk Summary` = threats.md
- [X] T002 Add risk-scores.md extraction methodology to `.claude/agents/tachi/threat-infographic.md` — add steps for: (1) parse Section 1 (Executive Summary) for aggregate severity distribution, (2) parse Section 2 (Scored Threat Table) for per-finding composite scores, (3) read co-located threats.md Sections 1-2 for structural/spatial data
- [X] T003 Add data merge instructions to `.claude/agents/tachi/threat-infographic.md` — document how quantitative scores from risk-scores.md replace qualitative severity counts in each of the 5 extraction steps while structural skeleton comes from threats.md
- [X] T004 Update input contract in `.claude/agents/tachi/threat-infographic.md` — extend the input contract to accept either `threats.md` (existing) or `risk-scores.md` + co-located `threats.md` (new dual-source); update the `input_schema` metadata to reference both `output.yaml` and `risk-scoring.yaml`

**Checkpoint**: Infographic agent can now consume either data source type. Command creation can begin.

---

## Phase 2: US-1/US-2/US-3 — Standalone /infographic Command (Priority: P0)

**Goal**: Create the `/infographic` command with auto-detection (US-1), explicit override (US-2), and template selection (US-3)

**Independent Test**: Run `/infographic` in a directory with `threats.md` and/or `risk-scores.md` — command detects data source, invokes agent, produces spec + optional image

- [X] T005 [US1] [US2] [US3] Create new command file `.claude/commands/infographic.md` with Step 0 (parse `--template` flag with values baseball-card/system-architecture/all, default all; parse `--output-dir` flag; parse remaining args as explicit data source path; resolve `corporate-white` alias to `baseball-card`)
- [X] T006 [US1] [US2] Add Step 1 (Validate Prerequisites) to `.claude/commands/infographic.md` — check infographic agent exists at `.claude/agents/tachi/threat-infographic.md`; implement data source detection: if explicit path provided validate and use it, else scan for `risk-scores.md` first then `threats.md`; if `risk-scores.md` is primary verify co-located `threats.md` exists; error messages for: no files found, explicit path not found, missing co-located threats.md
- [X] T007 [US1] Add Step 2 (Run Infographic Agent) to `.claude/commands/infographic.md` — read data source file(s); invoke `tachi-threat-infographic` agent in fresh context passing: data source content, data source type indicator, template name, and output directory; agent writes spec + attempts Gemini image generation
- [X] T008 [US3] Add Step 3 (Report Results) to `.claude/commands/infographic.md` — display summary including: data source used (threats.md or risk-scores.md), templates generated, output file paths, image generation status (generated/skipped with reason); add post-completion hint for `/risk-score` if only threats.md was used
- [X] T009 [US1] [US2] [US3] Add quality checklist to `.claude/commands/infographic.md` — validate: data source detection correct, risk distribution counts match source file exactly (zero discrepancy), all requested templates generated, spec files written to output directory, Gemini image generation attempted if API key available

**Checkpoint**: `/infographic` command is functional with auto-detection, explicit override, and template selection

---

## Phase 3: US-5 — Pipeline Cleanup (Priority: P0)

**Goal**: Remove Phase 6 from `/threat-model` pipeline and orchestrator

**Independent Test**: Run `/threat-model` on an architecture file — pipeline produces phases 1-5 only, no infographic files generated, post-pipeline hint displayed

- [X] T010 [P] [US5] Remove `--infographic-template` flag parsing from Step 0 in `.claude/commands/threat-model.md` — delete the flag definition, valid values, and default assignment
- [X] T011 [P] [US5] Remove `--skip-infographic` flag and `TACHI_SKIP_INFOGRAPHIC` env var references from `.claude/commands/threat-model.md` — delete all skip condition logic and documentation
- [X] T012 [US5] Remove Phase 6 output files from output listing in `.claude/commands/threat-model.md` — delete `threat-baseball-card-spec.md`, `threat-baseball-card.jpg`, `threat-system-architecture-spec.md`, `threat-system-architecture.jpg` from output suite; update Step 2 orchestrator invocation to request 5 phases only; update Step 3 report to list 5-phase output
- [X] T013 [US5] Add post-pipeline hint to `.claude/commands/threat-model.md` — after Step 3 report output, add: "Run `/infographic` to generate visual risk diagrams from your threat analysis"
- [X] T014 [US5] Remove infographic-related quality checklist items from `.claude/commands/threat-model.md` — delete checklist items for baseball-card/system-architecture spec count validation
- [X] T015 [US5] Remove Phase 6 dispatch section from `.claude/agents/tachi/orchestrator.md` — delete the entire Phase 6: Infographic section (~lines 1785-1862) including environment loading, opt-out check, fresh-context invocation, output placement, and completion condition
- [X] T016 [US5] Update pipeline phase count in `.claude/agents/tachi/orchestrator.md` — change all references from "6 phases" to "5 phases" in phase summary, enumeration, and validation sections; remove Phase 6 from validation checklist; remove Phase 6 skip condition documentation

**Checkpoint**: `/threat-model` and orchestrator produce 5-phase output only

---

## Phase 4: US-5 — Platform Adapter Updates (Priority: P0)

**Goal**: Sync all platform adapters to reflect 5-phase pipeline and dual-path agent enhancement

**Independent Test**: Review each adapter file to confirm Phase 6 references removed and infographic agent supports dual-path extraction

### Orchestrator Adapters

- [X] T017 [P] [US5] Remove Phase 6 from `adapters/claude-code/agents/orchestrator.md` — mirror changes from T015/T016 (remove Phase 6 dispatch, update phase count to 5)
- [X] T018 [P] [US5] Remove Phase 6 from `adapters/copilot/agents/orchestrator.agent.md` — mirror changes from T015/T016
- [X] T019 [P] [US5] Remove Phase 6 from `adapters/copilot/instructions/tachi-orchestrator-context.instructions.md` — remove `--skip-infographic` flag references and Phase 6 documentation
- [X] T020 [P] [US5] Remove Phase 6 from `adapters/cursor/rules/orchestrator.mdc` — mirror changes from T015/T016
- [X] T021 [P] [US5] Remove Phase 6 from `adapters/generic/prompts/00-orchestrator.md` — mirror changes from T015/T016

### Command Adapters

- [X] T022 [P] [US5] Update `adapters/claude-code/commands/threat-model.md` — mirror changes from T010-T014 (remove infographic flags, Phase 6 output, add hint)
- [X] T023 [P] [US1] [US2] [US3] Create `adapters/claude-code/commands/infographic.md` — copy of `.claude/commands/infographic.md` for Claude Code adapter

### Infographic Agent Adapters

- [X] T024 [P] [US1] Add dual-path extraction to `adapters/claude-code/agents/threat-infographic.md` — mirror changes from T001-T004
- [X] T025 [P] [US1] Add dual-path extraction to `adapters/copilot/agents/threat-infographic.agent.md` — mirror changes from T001-T004
- [X] T026 [P] [US1] Add dual-path extraction to `adapters/cursor/rules/threat-infographic.mdc` — mirror changes from T001-T004
- [X] T027 [P] [US1] Add dual-path extraction to `adapters/generic/prompts/13-threat-infographic.md` — mirror changes from T001-T004

**Checkpoint**: All 4 adapter platforms reflect 5-phase pipeline and dual-path agent

---

## Phase 5: US-4 — Regeneration Validation (Priority: P1)

**Goal**: Verify infographics can be regenerated after enrichment with quantitative risk scoring

**Independent Test**: Generate infographics from `examples/agentic-app/sample-report/` which contains both `threats.md` and `risk-scores.md` — verify output uses quantitative composite scores

- [X] T028 [US4] Validate auto-detection with example data — run `/infographic` in `examples/agentic-app/sample-report/` directory, verify it auto-detects `risk-scores.md` as primary source and reads co-located `threats.md` for structural data
- [X] T029 [US4] Validate quantitative scores in output — inspect generated `threat-baseball-card-spec.md` and `threat-system-architecture-spec.md` to verify risk distribution reflects composite score bands (not qualitative severity counts from threats.md Section 6)
- [X] T030 [US4] Validate idempotent overwrite — run `/infographic` twice in same directory, verify second run overwrites first output cleanly

**Checkpoint**: Infographic regeneration after enrichment produces quantitative-score-based output

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates and final quality validation

- [X] T031 [P] Update `.claude/skills/threat-model/SKILL.md` (if exists) to remove Phase 6 references and document `/infographic` as separate command — N/A: no SKILL.md exists for threat-model (18 SKILL.md files found, none for threat-model)
- [X] T032 [P] Update `README.md` or relevant documentation files referencing the 6-phase pipeline to reflect 5 phases — updated 4 files: `docs/architecture/01_system_design/README.md`, `docs/architecture/00_Tech_Stack/README.md`, `docs/devops/01_Local/README.md`, `docs/guides/prompts/GUIDE_PROMPT.md`
- [X] T033 Validate quickstart workflow: run `/threat-model` → `/risk-score` → `/infographic` end-to-end against `examples/agentic-app/sample-report/` and verify all outputs are correct
- [X] T034 Run `/infographic` with `--template baseball-card` and `--template system-architecture` separately to verify single-template generation works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — start immediately
- **Phase 2 (Command Creation)**: Depends on Phase 1 completion (agent must support dual-path before command can use it)
- **Phase 3 (Pipeline Cleanup)**: No dependency on Phase 1 or 2 — can start in **parallel** with Phase 1
- **Phase 4 (Adapter Sync)**: Depends on Phase 1 + Phase 3 completion (canonical files must be final before adapter sync)
- **Phase 5 (Validation)**: Depends on Phase 1 + Phase 2 completion
- **Phase 6 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US-1/US-2/US-3 (P0)**: Depend on Phase 1 (agent enhancement) — combined in Phase 2
- **US-4 (P1)**: Depends on Phase 1 + Phase 2 — validation in Phase 5
- **US-5 (P0)**: Independent of US-1/US-2/US-3 — can start immediately in Phase 3

### Parallel Opportunities

- **Wave 1**: Phase 1 (T001-T004) + Phase 3 (T010-T016) — different files, no dependencies
- **Wave 2**: Phase 2 (T005-T009) — after Phase 1 completes
- **Wave 3**: Phase 4 (T017-T027) — all [P] tasks can run in parallel across adapter platforms
- **Wave 4**: Phase 5 (T028-T030) + Phase 6 (T031-T034) — validation and polish

---

## Parallel Example: Wave 1

```
# Launch agent enhancement and pipeline cleanup simultaneously:
Agent: "Add dual-path data extraction to .claude/agents/tachi/threat-infographic.md" (T001-T004)
Agent: "Remove Phase 6 from .claude/commands/threat-model.md" (T010-T014)
Agent: "Remove Phase 6 from .claude/agents/tachi/orchestrator.md" (T015-T016)
```

## Parallel Example: Wave 3

```
# Launch all adapter updates simultaneously (all [P], different files):
Agent: "Update adapters/claude-code/agents/orchestrator.md" (T017)
Agent: "Update adapters/copilot/agents/orchestrator.agent.md" (T018)
Agent: "Update adapters/cursor/rules/orchestrator.mdc" (T020)
Agent: "Update adapters/generic/prompts/00-orchestrator.md" (T021)
Agent: "Update adapters/claude-code/commands/threat-model.md" (T022)
Agent: "Create adapters/claude-code/commands/infographic.md" (T023)
Agent: "Update adapters/claude-code/agents/threat-infographic.md" (T024)
# ... etc.
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Complete Phase 1: Agent enhancement (dual-path extraction)
2. Complete Phase 2: `/infographic` command creation
3. **STOP and VALIDATE**: Run `/infographic` against example data
4. Users can immediately use `/infographic` — even before pipeline cleanup

### Full Delivery (All Phases)

1. Complete Phase 1 + Phase 3 in parallel (agent + pipeline cleanup)
2. Complete Phase 2 (command creation)
3. Complete Phase 4 (adapter sync) — all adapters in parallel
4. Complete Phase 5 + Phase 6 (validation + polish)
5. Full feature delivered with clean 5-phase pipeline across all platforms

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 34 |
| Phase 1 (Foundational) | 4 tasks |
| Phase 2 (US-1/US-2/US-3) | 5 tasks |
| Phase 3 (US-5 Pipeline) | 7 tasks |
| Phase 4 (US-5 Adapters) | 11 tasks |
| Phase 5 (US-4 Validation) | 3 tasks |
| Phase 6 (Polish) | 4 tasks |
| Parallel waves | 4 |
| Max parallel tasks (Wave 3) | 11 |
| MVP scope | Phase 1 + Phase 2 (9 tasks) |

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No test tasks generated (not requested in spec)
- Agent adapter updates (T024-T027) mirror canonical agent changes — can be automated
- Orchestrator adapter updates (T017-T021) mirror canonical orchestrator changes — can be automated
