---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 6 user stories covered with traceable labels. All 23 FRs addressed. All acceptance scenarios satisfiable. No scope creep. Priority ordering correct."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound — correct dependency ordering, well-applied parallelization, complete plan coverage. 2 moderate concerns: POC gate omits table-overflow validation; spec edge cases lack explicit Phase 7 tasks. Addressable during implementation."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Well-structured with correct phase sequencing and POC gate. 3 moderate concerns: agent file task chain (T020-T024) could merge to reduce critical path; Phase 5 is longest sequential bottleneck; timeline calibrates to 3-4 sessions. Recommended 4-wave structure."
---

# Tasks: 054 — Security Assessment PDF Booklet

**Input**: Design documents from `specs/054-security-assessment-pdf/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not required (methodology template project — validation is manual PDF review per spec).

**Organization**: Tasks grouped by implementation phase aligned with plan.md. User stories map across phases: US1 (single-command PDF) spans all phases; US2 (full-bleed) maps to Phases 1+3; US3 (graceful degradation) maps to Phase 4; US4 (professional design) maps to Phase 2; US5 (Typst prerequisite) maps to Phase 1; US6 (schema-driven assembly) maps to Phase 1.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Read Source Materials + Scaffold)

**Purpose**: Read existing patterns, create directory structure, scaffold foundational files

- [X] T001 Read existing command pattern at `.claude/commands/infographic.md` and note 4-step structure, flag parsing, artifact detection, agent invocation, result reporting
- [X] T002 [P] Read existing schema pattern at `schemas/infographic.yaml` and note frontmatter fields, required_sections structure, completeness_rule format
- [X] T003 [P] Read existing agent pattern at `.claude/agents/tachi/threat-infographic.md` (first 200 lines) and note YAML frontmatter metadata fields, input/output declarations, step structure
- [X] T004 [P] Read example artifacts at `examples/agentic-app/sample-report/` — note `threats.md` frontmatter fields, Section 6 Risk Summary format, Section 2 Coverage Matrix table structure, and `risk-scores.md` Section 2 Scored Threat Table structure
- [X] T005 [P] Read `templates/README.md` and note current content for update in Phase 4
- [X] T006 Create directory `templates/security-report/` for Typst rendering templates

**Checkpoint**: All source patterns read. Directory structure ready.

---

## Phase 2: Foundational (Schema + POC + Command Scaffold — Wave 1 Gate)

**Purpose**: Create schema, validate Typst capabilities via POC, scaffold command file. This phase is the Wave 1 gate — full template authoring in subsequent phases depends on POC success.

**CRITICAL**: POC must validate full-bleed rendering, mixed orientation, and conditional pages before proceeding.

- [X] T007 [US6] Create page assembly schema at `schemas/security-report.yaml` defining: schema_version, output_file, artifacts detection matrix (7 patterns with required/optional and enabled pages), page_sequence (8 types with layout and size), data_source_tiers for findings-detail (tier1: compensating-controls columns, tier2: risk-scores columns, tier3: threats columns), and page_dimensions (us-letter and custom-16x9)
- [X] T008 [P] [US5] Create command file scaffold at `.claude/commands/security-report.md` with: YAML frontmatter (description field), Step 0 (parse `--output-dir` and `--title` flags from `$ARGUMENTS`), Step 1 (validate Typst installation via `which typst` with platform-specific install instructions for macOS/Linux/Windows; auto-detect 7 artifact types in target directory; require `threats.md` minimum; report detected artifacts and pages to be generated), Step 2 (invoke report-assembler agent — placeholder), Step 3 (report results — placeholder)
- [X] T009 [P] [US2] Create Typst POC file at `templates/security-report/poc-test.typ` that validates: (1) US Letter portrait text page with margins, (2) custom 16:9 landscape page with zero margins and a full-bleed image, (3) conditional page inclusion via `#if` guard, (4) dynamic page counter across orientation changes. Use a sample JPEG from `examples/` or create a solid-color rectangle as image substitute
- [X] T010 [US2] Run Typst POC: execute `typst compile templates/security-report/poc-test.typ poc-test.pdf` and verify all 3 rendering capabilities pass. Document results in `specs/054-security-assessment-pdf/quickstart.md` Findings section

**Checkpoint**: Wave 1 gate passed — Typst validates full-bleed, mixed orientation, conditional pages. Schema defined. Command scaffold ready. Proceed to full template authoring.

---

## Phase 3: Shared Styles + Text Page Templates (Priority: P1)

**Purpose**: Build shared style foundation and all portrait text page Typst templates

- [X] T011 [US4] Create shared styles at `templates/security-report/shared.typ` defining: severity color constants (Critical=#DC2626, High=#F97316, Medium=#EAB308, Low=#4169E1), typography rules (sans-serif headings, serif body, monospace table data), US Letter page setup with margins (top/bottom 0.75in, left/right 1in), header function (classification marking, page title), footer function (page number, "Generated by tachi"), and severity-to-color mapping function
- [X] T012 [US4] [US1] Create cover page template at `templates/security-report/cover.typ` that renders: project name (large, centered), assessment date, classification level (if available, omit if null), finding count summary (Critical/High/Medium/Low), tachi branding text, and overall risk posture label. Import shared.typ for colors and fonts
- [X] T013 [P] [US4] [US1] Create executive summary template at `templates/security-report/executive-summary.typ` with two rendering paths: (1) rich mode when `threat-report.md` narrative is available — 2-column layout with severity distribution metrics on left and narrative summary on right; (2) minimal mode using `threats.md` risk summary — single-column with severity counts and component distribution. Import shared.typ for consistent styling
- [X] T014 [P] [US4] [US1] Create findings detail template at `templates/security-report/findings-detail.typ` with 3-tier column rendering: accept a `tier` parameter (1, 2, or 3) and render the appropriate column set per data-model.md DataSourceTier definition. Table must: sort by severity (Critical first), apply severity colors to severity/risk column cells, repeat column headers on continuation pages if table exceeds one page. Import shared.typ
- [X] T015 [P] [US4] [US1] Create control coverage template at `templates/security-report/control-coverage.typ` rendering: control status matrix (found/partial/missing counts per STRIDE category), detailed control table (Component, Control Category, Status, Evidence, Effectiveness), and summary statistics. Only rendered when `compensating-controls.md` data is available. Import shared.typ
- [X] T016 [P] [US4] [US1] Create remediation roadmap template at `templates/security-report/remediation-roadmap.typ` rendering: prioritized action table with columns (Priority, Finding, Recommendation, SLA, Status), grouped by severity. Accept data from either `compensating-controls.md` Section 3 recommendations or `threat-report.md` remediation section. Import shared.typ

**Checkpoint**: All 6 text page templates complete. Each imports shared.typ for consistent design. Cover, executive summary, findings detail, control coverage, and remediation roadmap can render independently.

---

## Phase 4: Full-Bleed Template + Master Orchestrator (Priority: P0)

**Purpose**: Build the full-bleed infographic page template and the master Typst orchestrator

- [X] T017 [US2] Create full-bleed infographic template at `templates/security-report/full-bleed.typ` that: accepts an image file path parameter, sets page dimensions to 11in x 6.1875in (16:9) with zero margins, renders the image at 100% width and 100% height filling the entire page, and suppresses headers/footers on full-bleed pages. Template is reused for all 3 infographic types (risk-funnel, baseball-card, system-architecture)
- [X] T018 [US1] [US3] Create master orchestrator at `templates/security-report/main.typ` that: imports shared.typ and report-data.typ, conditionally includes each page based on data availability flags (has_threat_report, has_risk_scores, has_compensating_controls, has_funnel_image, has_baseball_image, has_architecture_image), maintains page sequence order (cover → executive-summary → risk-funnel → baseball-card → system-architecture → findings-detail → control-coverage → remediation-roadmap), handles page breaks between pages, and resets page geometry when switching between portrait text and landscape full-bleed pages
- [X] T019 [P] [US1] Delete POC test file at `templates/security-report/poc-test.typ` (no longer needed after main.typ is complete)

**Checkpoint**: Full Typst template system complete. main.typ orchestrates all page types with conditional inclusion.

---

## Phase 5: Agent File (Priority: P0)

**Purpose**: Create the report-assembler agent that parses artifacts, generates Typst data, and invokes compilation

- [X] T020 [US1] Create agent file at `.claude/agents/tachi/report-assembler.md` with YAML frontmatter (name, description, category: report-generation, input_schemas referencing schemas/security-report.yaml, output_schema, output_files: [security-report.pdf], references to relevant ADRs) following the pattern in `.claude/agents/tachi/threat-infographic.md`
- [X] T021 [US1] [US3] Write agent Step 1 (Artifact Detection) in `report-assembler.md`: scan target directory for all 7 artifact patterns per schemas/security-report.yaml; apply 3-tier data source preference for findings-detail (check compensating-controls.md first, then risk-scores.md, then threats.md using section heading + column detection from infographic pattern); verify `threats.md` exists as minimum; set boolean flags for each artifact (has_threat_report, has_risk_scores, has_compensating_controls, has_funnel_image, has_baseball_image, has_architecture_image); report detection results
- [X] T022 [US1] Write agent Step 2 (Data Extraction) in `report-assembler.md`: parse YAML frontmatter from `threats.md` (extract project_name, date, classification, schema_version); parse Section 6 Risk Summary for severity counts; parse findings table from highest-available tier source; if `threat-report.md` exists parse Section 1 for executive narrative; if `compensating-controls.md` exists parse Section 2 for coverage matrix and Section 3 for recommendations; handle schema v1.0 gracefully (omit Section 4a correlated findings from executive summary, never abort)
- [X] T023 [US1] Write agent Step 3 (Typst Data Generation) in `report-assembler.md`: generate `report-data.typ` file in the templates/security-report/ directory containing all extracted data as Typst variables — project metadata, severity counts, findings rows array, executive narrative text, control coverage rows, remediation rows, infographic image paths, data source tier, and page inclusion boolean flags. Use Typst dictionary and array syntax for structured data
- [X] T024 [US1] Write agent Step 4 (Compilation) in `report-assembler.md`: invoke `typst compile templates/security-report/main.typ {output_path}/security-report.pdf` with the `--root` flag pointing to the project root (so image paths resolve correctly); handle compilation errors with clear messages; verify output PDF exists and is non-zero size; clean up intermediate `report-data.typ` file after successful compilation; report PDF path, page count, and included page types

**Checkpoint**: Agent file complete. Full pipeline: detect → extract → generate data → compile → report.

---

## Phase 6: Command Completion + Integration (Priority: P0)

**Purpose**: Complete the command file and integrate all components end-to-end

- [X] T025 [US1] Complete command file Step 2 in `.claude/commands/security-report.md`: replace placeholder with agent invocation — pass detected artifacts list, target directory, output directory (from `--output-dir` or same as input), and title override (from `--title`) to report-assembler agent
- [X] T026 [US1] Complete command file Step 3 in `.claude/commands/security-report.md`: report results — display generated PDF path, total page count, list of included page types with their sequence numbers, and next steps suggestion

**Checkpoint**: Command file complete. `/security-report` is fully functional end-to-end.

---

## Phase 7: Graceful Degradation Validation (Priority: P0)

**Purpose**: Verify correct behavior across all artifact combinations

- [X] T027 [US3] Validate threats-only scenario: run `/security-report` on a directory containing only `threats.md` (from `examples/agentic-app/sample-report/`); verify PDF contains exactly 3 pages (cover, executive summary with minimal content, findings detail with Tier 3 qualitative columns); verify no errors or blank pages
- [X] T028 [P] [US3] Validate threats + risk-scores scenario: run `/security-report` on a directory containing `threats.md` and `risk-scores.md`; verify PDF contains cover, executive summary with severity distribution, and findings detail with Tier 2 quantitative columns; verify no control coverage or remediation roadmap pages appear
- [X] T029 [P] [US3] Validate full pipeline scenario: run `/security-report` on a directory containing all markdown artifacts plus 3 infographic JPEGs; verify all 8 page types are present in correct sequence; verify full-bleed pages render without borders
- [X] T030 [US5] Validate Typst-not-installed scenario: temporarily rename or hide the `typst` binary; run `/security-report`; verify error message names Typst, includes install instructions for macOS/Linux/Windows; restore `typst` binary

**Checkpoint**: Graceful degradation verified across all artifact combinations.

---

## Phase 8: Polish & Documentation

**Purpose**: Template documentation and cross-cutting cleanup

- [X] T031 [P] Create template README at `templates/security-report/README.md` documenting: template purpose, file inventory (8 .typ files), Typst version requirements (0.11.x-0.12.x), how main.typ orchestrates page assembly, how report-data.typ is generated by the agent, severity color palette, typography choices, and instructions for running `typst compile` manually
- [X] T032 [P] Update `templates/README.md` to distinguish rendering templates (`security-report/*.typ` — used for PDF compilation by the report-assembler agent) from reference templates (`*.md` — output structure examples used as documentation)
- [X] T033 Verify idempotency: run `/security-report` twice on the same input directory; compare output PDFs and verify they are identical (SC-005)
- [X] T034 Verify performance: run `/security-report` on `examples/agentic-app/sample-report/` with full artifacts and time the execution; verify completion in under 30 seconds (SC-006)

**Checkpoint**: All documentation complete. Performance and idempotency verified.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — read source materials
- **Phase 2 (Foundational)**: Depends on Phase 1 — creates schema, command scaffold, POC
- **Phase 3 (Text Templates)**: Depends on Phase 2 POC success — builds text page templates
- **Phase 4 (Full-Bleed + Orchestrator)**: Depends on Phase 2 POC success + Phase 3 shared.typ — builds landscape pages and main.typ
- **Phase 5 (Agent)**: Depends on Phase 4 — agent references template structure and main.typ
- **Phase 6 (Command Completion)**: Depends on Phase 5 — command invokes agent
- **Phase 7 (Validation)**: Depends on Phase 6 — validates complete pipeline
- **Phase 8 (Polish)**: Depends on Phase 7 — documentation and final checks

### Critical Path

Phase 1 → Phase 2 (POC gate) → Phase 3 (T011 shared.typ) → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

### Parallel Opportunities

- **Phase 1**: T002, T003, T004, T005 can run in parallel (different source files)
- **Phase 2**: T007 and T008 can run in parallel with T009 (different output files)
- **Phase 3**: T013, T014, T015, T016 can run in parallel after T011 (shared.typ) completes (different .typ files)
- **Phase 4**: T019 can run in parallel with T017 (different files)
- **Phase 7**: T028, T029 can run in parallel (different artifact combinations)
- **Phase 8**: T031, T032 can run in parallel (different files)

---

## Implementation Strategy

### MVP First (Phases 1-2)

1. Complete Phase 1: Read source patterns
2. Complete Phase 2: Schema + POC + command scaffold
3. **STOP and VALIDATE**: POC must pass Wave 1 gate (full-bleed, mixed orientation, conditional pages)
4. If POC fails: evaluate contingency approaches before proceeding

### Incremental Delivery

1. Phase 1-2: Foundation + POC validation → Wave 1 gate passed
2. Phase 3: Text page templates → can preview text-only PDFs
3. Phase 4: Full-bleed + orchestrator → complete template system
4. Phase 5-6: Agent + command → fully functional `/security-report`
5. Phase 7: Graceful degradation validation → all scenarios verified
6. Phase 8: Documentation + polish → feature complete

---

## Notes

- All deliverables are markdown and Typst template files — no application code
- [P] tasks = different files, no dependencies between them
- POC in Phase 2 is a hard gate — do not proceed to Phase 3+ if POC fails
- Agent file in Phase 5 is the largest single deliverable (~50-80KB of markdown instructions)
- Performance target: <30 seconds for full-pipeline PDF generation
