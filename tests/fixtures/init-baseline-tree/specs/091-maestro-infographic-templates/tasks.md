---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-08
    status: APPROVED_WITH_CONCERNS
    notes: "3 findings (2 LOW, 1 INFORMATIONAL). All 5 user stories covered, all 15 FRs have implementation tasks, no scope creep, story-based organization enables independent delivery."
  architect_signoff:
    agent: architect
    date: 2026-04-08
    status: APPROVED_WITH_CONCERNS
    notes: "5 findings (1 MEDIUM T023 example assumption, 2 LOW, 2 INFORMATIONAL). Dependencies correctly ordered, file paths verified, parallel opportunities accurate, technical approach sound."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-08
    status: APPROVED_WITH_CONCERNS
    notes: "5 findings (1 MEDIUM, 1 LOW, 3 INFORMATIONAL). 3-day estimate realistic (80% confidence). Task granularity appropriate. Critical path correctly identified. 3-wave parallel execution maximized."
---

# Tasks: MAESTRO Infographic Templates and PDF Report Section

**Input**: Design documents from `/specs/091-maestro-infographic-templates/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation. US-05 (data extraction) is foundational and blocks all visualization stories.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No project scaffolding needed — extending existing codebase. Verify prerequisites and baseline.

- [X] T001 Verify Feature 084 MAESTRO data exists in `examples/agentic-app/threats.md` (Section 1 Components table has `MAESTRO Layer` column, Section 6 has "Risk by MAESTRO Layer" subsection)
- [X] T002 [P] Verify existing infographic templates are unmodified baseline — run `extract-infographic-data.py --template baseball-card` against `examples/agentic-app/sample-report/` and confirm successful JSON output

---

## Phase 2: Foundational — MAESTRO Data Extraction (US-05, Priority: P0)

**Purpose**: Core MAESTRO extraction logic that MUST be complete before ANY visualization story can be implemented

**Goal**: Extract MAESTRO layer distribution, per-finding layer assignments, component-layer intersections, and most-exposed layer from threats.md

**Independent Test**: Run `extract-infographic-data.py --template maestro-stack --target-dir examples/agentic-app/sample-report/ --output /tmp/test.json` and verify JSON contains `maestro_layer_distribution`, `most_exposed_layer`, and per-finding MAESTRO data

**CRITICAL**: No visualization work (US-01, US-02, US-03) can begin until this phase is complete

- [X] T003 [US5] Add MAESTRO layer parsing function to `scripts/extract-infographic-data.py` — parse Section 6 "Risk by MAESTRO Layer" table (header: `#### Risk by MAESTRO Layer`, columns: `MAESTRO Layer | Finding Count | Highest Severity`) into `maestro_layer_distribution` array of `(layer_id, layer_name, finding_count, highest_severity)` dicts
- [X] T004 [P] [US5] Add component-to-layer mapping function to `scripts/extract-infographic-data.py` — parse Section 1 Components table `MAESTRO Layer` column (index varies by table width) to build `{component_name: layer_string}` lookup dict
- [X] T005 [US5] Add per-finding MAESTRO layer extraction to `scripts/extract-infographic-data.py` — extend the existing finding iteration to capture `maestro_layer` from Section 3 agent tables (column index 2 in both 8-column STRIDE and 9-column AI tables)
- [X] T006 [US5] Add `compute_maestro_heatmap()` function to `scripts/extract-infographic-data.py` — build component-layer intersection matrix where each cell = highest severity at that (component, layer) pair; cap components at top 10 by total finding count
- [X] T007 [US5] Add `most_exposed_layer` computation to `scripts/extract-infographic-data.py` — layer with highest finding count from `maestro_layer_distribution`; ties broken by highest severity, then layer ID ascending
- [X] T008 [US5] Extend CLI `--template` choices at line 933 of `scripts/extract-infographic-data.py` — add `"maestro-stack"` and `"maestro-heatmap"` to the `choices` list
- [X] T009 [US5] Add `maestro-stack` template data branch in `main()` of `scripts/extract-infographic-data.py` (after line 1018) — populate `template_data` with `maestro_layer_distribution`, `most_exposed_layer`, and per-layer finding summaries (up to 2 top findings per layer)
- [X] T010 [US5] Add `maestro-heatmap` template data branch in `main()` of `scripts/extract-infographic-data.py` — populate `template_data` with `maestro_heatmap` intersection grid and `maestro_layer_distribution`
- [X] T011 [US5] Add MAESTRO fallback handling — when threats.md lacks MAESTRO data (no Section 6 "Risk by MAESTRO Layer" subsection, no `MAESTRO Layer` column in Section 1), all MAESTRO fields default to empty lists/null without errors
- [X] T012 [US5] Validate extraction against `examples/agentic-app/sample-report/` — run both `--template maestro-stack` and `--template maestro-heatmap`, verify JSON output contains correct layer distribution matching Section 6 data, correct most-exposed layer, and component-layer intersections

**Checkpoint**: MAESTRO extraction complete — visualization stories can now begin in parallel

---

## Phase 3: User Story 1 — View Layer Risk Distribution (Priority: P0)

**Goal**: Create maestro-stack infographic template that renders a vertical seven-layer stack diagram

**Independent Test**: Run `/infographic` with `maestro-stack` template against agentic-app example and verify spec file and image are generated with L1-L7 layers, finding counts, and severity indicators

- [X] T013 [P] [US1] Create `templates/tachi/infographics/infographic-maestro-stack.md` — follow existing template pattern with all mandatory sections (Layout, Style, Color Palette, Typography, Zone Specifications, Gemini Prompt Template, Gemini API Configuration, Accessibility). Layout: seven horizontal bands (L7 top, L1 bottom), each with layer ID/name, finding count, highest severity, top 2 finding summaries. Sidebar with aggregate stats and most-exposed-layer badge. Dark Navy background, 16:9 landscape.
- [X] T014 [US1] Add maestro-stack Section 5 format to `.claude/skills/tachi-infographics/references/template-specific-formats.md` — layer-grouped table format: `| Layer | Name | Finding Count | Highest Severity | Top Findings |`

**Checkpoint**: maestro-stack template ready for end-to-end testing

---

## Phase 4: User Story 2 — View Component-Layer Heatmap (Priority: P0)

**Goal**: Create maestro-heatmap infographic template that renders a component-by-layer grid with severity coloring

**Independent Test**: Run `/infographic` with `maestro-heatmap` template against agentic-app example and verify grid image with correct component-layer intersections

- [X] T015 [P] [US2] Create `templates/tachi/infographics/infographic-maestro-heatmap.md` — follow existing template pattern with all mandatory sections. Layout: grid with component rows (capped at top 10) and L1-L7 columns, cells colored by highest severity at intersection, legend sidebar with severity color scale. Dark Navy background, 16:9 landscape.
- [X] T016 [US2] Add maestro-heatmap Section 5 format to `.claude/skills/tachi-infographics/references/template-specific-formats.md` — component-layer intersection grid format: `| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |`

**Checkpoint**: maestro-heatmap template ready for end-to-end testing

---

## Phase 5: User Story 3 — PDF Report MAESTRO Section (Priority: P0)

**Goal**: Add MAESTRO Findings page to the PDF security assessment report with findings grouped by layer

**Independent Test**: Generate PDF report from agentic-app example and verify MAESTRO Findings page appears with findings grouped by L1-L7 layers

- [X] T017 [P] [US3] Create `templates/tachi/security-report/maestro-findings.typ` — single export function `maestro-findings-page(classification: none, maestro-findings-by-layer: (), has-maestro-data: false)`. Group findings by MAESTRO layer (L1-L7 + Unclassified). Each layer section: heading with layer ID and name, finding count, finding cards (ID, component, severity badge, threat summary). Sort layers L1-L7, findings within each layer by severity rank. Empty state when no data.
- [X] T018 [US3] Extend `scripts/extract-report-data.py` — add MAESTRO data extraction: parse Section 6 "Risk by MAESTRO Layer" for `maestro-layer-distribution`, group findings by layer for `maestro-findings-by-layer`, detect `threat-maestro-stack.jpg` and `threat-maestro-heatmap.jpg` in `detect_images()`, compute `has-maestro-data` boolean, emit all 8 new MAESTRO variables in `generate_report_data_typ()`
- [X] T019 [US3] Extend `templates/tachi/security-report/main.typ` — add import for `maestro-findings.typ`, add backward-compat defaults in Section 2b (8 new `#let` bindings with `if x != none` pattern), add conditional MAESTRO infographic pages after System Architecture (lines ~223), add conditional MAESTRO findings page before "Detailed Findings" section divider (line ~227). Page order: maestro-stack image, maestro-heatmap image, maestro findings detail.
- [X] T020 [US3] Update `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` — add MAESTRO Data section documenting all 8 new variables: `has-maestro-data`, `maestro-layer-distribution`, `most-exposed-layer`, `maestro-findings-by-layer`, `has-maestro-stack-image`, `maestro-stack-image-path`, `has-maestro-heatmap-image`, `maestro-heatmap-image-path`

**Checkpoint**: PDF report with MAESTRO page ready for validation

---

## Phase 6: User Story 4 — Generate Both MAESTRO Templates Together (Priority: P1)

**Goal**: Add `maestro` shorthand that generates both maestro-stack and maestro-heatmap in one invocation

**Independent Test**: Run `/infographic` with `maestro` template and verify both spec+image pairs are generated

- [X] T021 [US4] Update `.claude/skills/tachi-infographics/SKILL.md` — add `maestro` shorthand dispatch: when template is `maestro`, expand to `["maestro-stack", "maestro-heatmap"]` and generate both sequentially. Add `maestro-stack` and `maestro-heatmap` as individual valid template names in dispatch table.

**Checkpoint**: All four user stories complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and regression testing

- [X] T022 [P] Update `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md` — add maestro-stack and maestro-heatmap to Available Templates table, add to Output Files table, document `maestro` shorthand in Using Templates section, document MAESTRO-specific placeholders. Also fix pre-existing risk-funnel documentation gap (noted in PRD).
- [X] T023 [P] Validate all 6 example architectures — run extraction against each example in `examples/` (agentic-app, ascii-web-api, free-text-microservice, mermaid-agentic-app, microservices, web-app). Those with MAESTRO data should produce valid MAESTRO JSON. Those without should produce empty MAESTRO fields without errors.
- [X] T024 [P] Regression test existing templates — run `extract-infographic-data.py --template baseball-card`, `--template system-architecture`, and `--template risk-funnel` against `examples/agentic-app/sample-report/` and verify output is identical to baseline (zero regression)
- [X] T025 End-to-end PDF validation — generate complete PDF report from agentic-app example with MAESTRO infographic images present; verify page sequence, conditional inclusion, and backward-compat defaults

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational / US-05 (Phase 2)**: Depends on Phase 1 — BLOCKS all visualization stories
- **US-01 (Phase 3)**: Depends on Phase 2 completion
- **US-02 (Phase 4)**: Depends on Phase 2 completion — can run in PARALLEL with Phase 3
- **US-03 (Phase 5)**: Depends on Phase 2 completion — can run in PARALLEL with Phases 3-4
- **US-04 (Phase 6)**: Depends on Phases 3 + 4 (both templates must exist for shorthand)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US-05 (P0, extraction)**: Foundational — no dependencies on other stories, blocks all others
- **US-01 (P0, maestro-stack)**: Depends on US-05 only — independent of US-02, US-03, US-04
- **US-02 (P0, maestro-heatmap)**: Depends on US-05 only — independent of US-01, US-03, US-04
- **US-03 (P0, PDF page)**: Depends on US-05 only — independent of US-01, US-02, US-04
- **US-04 (P1, shorthand)**: Depends on US-01 + US-02 (templates must exist for shorthand dispatch)

### Parallel Opportunities

- T001 and T002 can run in parallel (Setup)
- T003 and T004 can run in parallel (both are parsing functions, different data sources)
- **Phases 3, 4, and 5 can run fully in parallel** after Phase 2 completes — this is the primary parallelization opportunity (3 waves working simultaneously on different files)
- T013 and T014 are in different files — T013 can start first
- T015 and T016 are in different files — T015 can start first
- T017, T018, T019, T020 are all in different files — T017 and T018 can run in parallel
- T022, T023, T024 are independent — all can run in parallel

---

## Implementation Strategy

### MVP First (Extraction + Stack Template)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: MAESTRO data extraction (US-05)
3. Complete Phase 3: maestro-stack template (US-01)
4. **STOP and VALIDATE**: Run `/infographic` with `maestro-stack` template — verify layer stack diagram
5. This alone delivers the primary CISO persona value

### Incremental Delivery

1. Extraction + Stack → Test → maestro-stack works independently
2. Add Heatmap → Test → maestro-heatmap works independently
3. Add PDF page → Test → MAESTRO Findings page renders in report
4. Add Shorthand → Test → `maestro` generates both templates
5. Polish → Documentation + regression testing → Ship

### Parallel Team Strategy (3-Wave)

After Phase 2 (extraction) completes:
- **Wave A**: US-01 (maestro-stack template) — T013, T014
- **Wave B**: US-02 (maestro-heatmap template) — T015, T016
- **Wave C**: US-03 (PDF report integration) — T017, T018, T019, T020

Waves A, B, C work on completely different files with no cross-dependencies.

---

## Notes

- All new infographic template files follow identical structure to existing templates
- All new Typst page follows single-export-function pattern from findings-detail.typ
- MAESTRO Layer column is at index 2 in both STRIDE (8-col) and AI (9-col) agent tables
- Component cap at 10 for heatmap (vs 13 for baseball-card heat map) due to 7-column grid constraint
- Backward-compat defaults use `if x != none { x } else { default }` pattern matching main.typ lines 67-80
