---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 4 user stories addressed. All 15 FRs covered with full traceability. Zero scope creep. US-3 composite validation through US-2+US-4 is correct approach. 2 non-blocking observations: opt-out flag naming needs reconciliation, 3 edge cases implicitly handled."
  architect_signoff:
    agent: architect
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "Technically complete. All 4 plan concerns (M-01 through M-04) addressed in specific tasks. 1 medium: TACHI_SKIP_INFOGRAPHIC env var has no Phase 5 precedent — decide parity before implementation. 4 low: T016 P marker, T014/T015 parallel opportunity, T012 section separation, output prose paragraph."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "18 tasks, 4 waves, 2.3-3.0h with parallelism. Critical path: 12 tasks (132-188 min). Phase 3||Phase 4 parallelism saves 40-60 min. 3 non-blocking: single-file bottleneck (structural constraint), approximate line references, minor parallelization understatement."
---

# Tasks: Threat Infographic Agent

**Input**: Design documents from `/specs/018-threat-infographic-agent/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not requested in feature specification — no test tasks generated.

**Organization**: Tasks grouped by user story. All 4 user stories are P0; ordered by dependency (US-1 is MVP, US-2 builds on US-1, US-4 integrates into pipeline, US-3 validated through US-2 + US-4).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Schema Foundation)

**Purpose**: Create the output schema that defines the infographic specification contract. Required before agent authoring.

- [X] T001 Create infographic output schema in `schemas/infographic.yaml` — define schema_version, output_file, required_sections (Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, Visual Design Directives), color_palette with CVSS hex codes, completeness_rule, and attack tree naming. Follow `schemas/report.yaml` structural pattern with namespaced root key and frontmatter block per architect review M-03.

**Checkpoint**: Schema foundation ready — agent authoring can begin.

---

## Phase 2: User Story 1 — Infographic Specification Generation (Priority: P0) MVP

**Goal**: The infographic agent produces a structured `threat-infographic-spec.md` with 6 required sections from `threats.md`, with data accuracy matching Section 6 exactly.

**Independent Test**: Run the infographic agent against `examples/mermaid-agentic-app/threats.md` and verify all 6 sections are present with correct severity counts (3 Critical, 9 High, 7 Medium, 0 Low).

### Implementation for User Story 1

- [X] T002 [US1] Create infographic agent prompt file `agents/threat-infographic.md` — YAML frontmatter (agent_name, category, status, version, description, references including input_schema, output_schema, output_files) following `agents/threat-report.md` pattern. Include all standard fields per architect review M-01.

- [X] T003 [US1] Add Core Mission section to `agents/threat-infographic.md` — define the agent's purpose: transform structured threat findings into a visual risk specification. Frame specification as primary deliverable, image as best-effort.

- [X] T004 [US1] Add Input Contract section to `agents/threat-infographic.md` — declare `threats.md` as sole input per `schemas/output.yaml` (v1.1). Specify which sections are consumed: YAML frontmatter, Sections 1, 3, 4, 4a, 5, 6, 7. Explicitly state: does NOT consume `threat-report.md` (fresh context isolation).

- [X] T005 [US1] Add Data Extraction Methodology section to `agents/threat-infographic.md` — define 5 extraction steps: (1) parse frontmatter for metadata, (2) extract Section 6 for risk distribution counts, (3) cross-tabulate component × risk_level from Sections 3/4/4a for heat map, (4) select top 5 findings from Section 7 by severity, (5) aggregate per-component risk for architecture overlay.

- [X] T006 [US1] Add Infographic Specification Format section to `agents/threat-infographic.md` — define the 6 required output sections: Metadata, Risk Distribution (counts + percentages), Coverage Heat Map (component × severity matrix, max 8 rows, "Other" aggregation), Top Critical Findings (max 5, Critical first then High), Architecture Threat Overlay (component risk annotations), Visual Design Directives (CVSS hex codes, three-zone layout, 16:9 landscape).

- [X] T007 [US1] Add Quality Standards / Validation Checklist section to `agents/threat-infographic.md` — all 6 sections present, risk counts match Section 6, component names match exactly, heat map ordered by total descending, CVSS hex codes correct, severity colors validated.

**Checkpoint**: Agent can generate `threat-infographic-spec.md` from any `threats.md`. US-1 independently testable.

---

## Phase 3: User Story 2 — Gemini API Image Generation (Priority: P0)

**Goal**: When `GEMINI_API_KEY` is available, the agent produces a `threat-infographic.jpg` from the specification via Gemini API. When unavailable, the specification is saved as standalone deliverable.

**Independent Test**: With `GEMINI_API_KEY` set, run agent and verify JPEG output exists with 16:9 aspect ratio. Without key, verify spec is saved and informational message logged.

### Implementation for User Story 2

- [X] T008 [US2] Add Gemini API Prompt Construction section to `agents/threat-infographic.md` — narrative scene description (not keyword list) constructed from 6 spec sections, spatial zone instructions ("top third..., middle band..., bottom section..."), explicit hex codes for severity colors, max 15-20 distinct text labels, business-oriented framing ("risk assessment summary"), avoid attack terminology. Move gemini_config from schema to agent prompt per architect review M-04.

- [X] T009 [US2] Add Gemini API Integration section to `agents/threat-infographic.md` — check `GEMINI_API_KEY` env var, call `POST .../models/{model_id}:generateContent` with `responseModalities: ["TEXT", "IMAGE"]`, `aspectRatio: "16:9"`, `imageSize: "2K"`, default model `gemini-3-pro-image-preview` (configurable), parse response for `inline_data` with image MIME type, decode base64, save as `threat-infographic.jpg`.

- [X] T010 [US2] Add Error Handling & Graceful Degradation section to `agents/threat-infographic.md` — handle 6 conditions: (1) missing GEMINI_API_KEY → log info, save spec, continue; (2) API rate limit 429 → log warning, save spec, no retry; (3) API timeout → log error, save spec; (4) content policy rejection → log reason, save spec; (5) missing Section 6 → compute counts from individual findings; (6) empty threat model → produce zero-count spec with note.

**Checkpoint**: Agent handles Gemini API integration with graceful fallback. US-2 independently testable.

---

## Phase 4: User Story 4 — Orchestrator Integration as Phase 6 (Priority: P0)

**Goal**: Phase 6 (Infographic) runs automatically after Phase 5 (Report), invoked in fresh context with only `threats.md`, with pipeline isolation guaranteeing Phases 1–5 are never blocked.

**Independent Test**: Run full orchestrator pipeline and verify `threat-infographic-spec.md` appears in output directory alongside existing Phase 4 and Phase 5 outputs.

### Implementation for User Story 4

- [X] T011 [P] [US4] Update orchestrator YAML frontmatter in `agents/orchestrator.md` — add `infographic: agents/threat-infographic.md` to `references.agents`, add `infographic: schemas/infographic.yaml` to `references.schemas`, update description to mention Phase 6.

- [X] T012 [P] [US4] Update orchestrator pipeline description in `agents/orchestrator.md` — add Phase 6 to the 5-phase list (line ~48), update output format specification (line ~80) to include `threat-infographic-spec.md` and `threat-infographic.jpg` as conditional Phase 6 outputs.

- [X] T013 [US4] Add Phase 6 dispatch section to `agents/orchestrator.md` — insert after Phase 5 section (~line 1767), following identical structure: check opt-out, fresh-context invocation with only `threats.md` path, `<infographic-input>` context isolation boundary tags, output placement in same directory, completion criteria. Include explicit pipeline isolation statement.

- [X] T014 [US4] Add Phase 6 opt-out configuration to `agents/orchestrator.md` — `--skip-infographic` flag (standardized to match `--skip-report` per architect review M-02) or `TACHI_SKIP_INFOGRAPHIC=true` env var or `infographic: false` config. Document skip behavior: no spec, no image, no warning, Phases 1–5 unchanged.

- [X] T015 [US4] Add Phase 6 output validation checks to `agents/orchestrator.md` — insert after Phase 5 validation section (~line 1204): `threat-infographic-spec.md` exists, contains 6 sections, risk counts match `threats.md` Section 6, conditional image check if GEMINI_API_KEY set.

**Checkpoint**: Full pipeline (Phases 1–6) operational. US-4 independently testable. US-3 (optionality) validated through opt-out config (T014) and error handling (T010).

---

## Phase 5: Validation & Polish

**Purpose**: End-to-end validation against sample data, sample output creation, and cross-cutting quality checks.

- [X] T016 [P] Create sample infographic specification output at `examples/mermaid-agentic-app/threat-infographic-spec.md` — run infographic agent against `examples/mermaid-agentic-app/threats.md` (19 findings: 3 Critical, 9 High, 7 Medium) and save the produced specification as the canonical sample output for validation.

- [X] T017 Validate data accuracy of sample output — verify risk distribution counts (Critical=3, High=9, Medium=7, Low=0, Total=19), coverage heat map component names match `threats.md` exactly, top findings selected from Critical/High, CVSS hex codes correct.

- [X] T018 Run quickstart.md validation at `specs/018-threat-infographic-agent/quickstart.md` — verify all documented commands and configuration options are consistent with the implemented agent and orchestrator changes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US-1 (Phase 2)**: Depends on Phase 1 (schema must exist before agent references it)
- **US-2 (Phase 3)**: Depends on Phase 2 (Gemini sections extend the agent created in US-1)
- **US-4 (Phase 4)**: Depends on Phase 2 (orchestrator references the agent file from US-1). Can run in parallel with Phase 3.
- **Validation (Phase 5)**: Depends on Phases 2, 3, and 4 (all implementation complete)

### User Story Dependencies

- **US-1 (Spec Generation)**: Foundation — no story dependencies. MVP deliverable.
- **US-2 (Gemini API)**: Depends on US-1 (extends the same agent file with API sections)
- **US-3 (Optionality)**: No separate implementation — validated through US-2 error handling (T010) + US-4 opt-out config (T014)
- **US-4 (Orchestrator)**: Depends on US-1 (agent must exist to be dispatched). Independent of US-2.

### Within Each User Story

- Schema before agent prompt
- Agent sections in logical order (mission → input → methodology → format → quality)
- Gemini prompt construction before API integration before error handling
- Orchestrator frontmatter and description before dispatch section before opt-out before validation

### Parallel Opportunities

- T011 and T012 can run in parallel (different sections of orchestrator, no overlap)
- Phase 3 (US-2) and Phase 4 (US-4) can run in parallel after Phase 2 completes
- T016 can run in parallel with T017/T018 if sample output is pre-generated

---

## Parallel Example: Phase 4 (Orchestrator Integration)

```
# These tasks modify different sections of orchestrator.md — can run in parallel:
Wave 1 (parallel):
  T011: Update orchestrator YAML frontmatter
  T012: Update orchestrator pipeline description

Wave 2 (sequential, depends on Wave 1):
  T013: Add Phase 6 dispatch section

Wave 3 (sequential, depends on Wave 2):
  T014: Add Phase 6 opt-out configuration
  T015: Add Phase 6 output validation checks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Schema (T001)
2. Complete Phase 2: US-1 Agent Prompt (T002–T007)
3. **STOP and VALIDATE**: Run agent against sample `threats.md`, verify 6 sections with correct data
4. The infographic specification alone delivers value — designers can render manually

### Incremental Delivery

1. Schema + US-1 → Specification generation works → MVP!
2. Add US-2 → Gemini image generation works (when API available)
3. Add US-4 → Pipeline integration works → Full feature!
4. Validation → Sample output verified → Ready for delivery

### Parallel Agent Strategy

With multiple agents:

1. Agent A completes Phase 1 (schema)
2. Agent A works on Phase 2 (US-1: agent prompt)
3. Once Phase 2 is done:
   - Agent A: Phase 3 (US-2: Gemini sections in agent prompt)
   - Agent B: Phase 4 (US-4: orchestrator integration)
4. Both complete → Phase 5 (validation)

---

## Notes

- All deliverables are markdown/YAML files — no application code
- Total: 18 tasks across 5 phases
- 3 files created (agent, schema, sample output), 1 file modified (orchestrator)
- US-3 (optionality) has no dedicated tasks — it is validated through US-2 and US-4
- Architect review concerns (M-01 through M-04) are addressed in specific tasks: M-01→T002, M-02→T014, M-03→T001, M-04→T008
