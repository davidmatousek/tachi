---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "All 6 user stories and 16 FRs covered. No scope creep. P0 prioritized in Phases 2-6. MVP strategy delivers P0 first. 2 LOW concerns: T035 Tier 1 field detail, Phase 9 story labels."
  architect_signoff:
    agent: architect
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered. Data contract complete. 1 MEDIUM concern addressed: T010 phantom heading updated to place(hide()) to prevent space consumption. 4 LOW concerns noted."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible in 2-3 sessions (~3.25h with parallelism). Task granularity appropriate. 2 LOW concerns addressed: T036 now unconditional, T010 references fallback. Agent assignments generated."
---

# Tasks: Professional PDF Security Assessment Report with tachi Branding

**Input**: Design documents from `/specs/060-professional-pdf-security/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No test tasks generated — visual PDF output verified through manual compilation.

**Organization**: Tasks are grouped by implementation wave (from plan.md) with user story labels for traceability. Waves align with plan phases: Foundation → New Pages → Integration → Polish.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Initialize the feature branch and verify the existing template system compiles.

- [X] T001 Verify Typst CLI is installed and `typst compile templates/security-report/main.typ /tmp/test-report.pdf --root .` compiles successfully with an existing test report-data.typ
- [X] T002 Verify brand assets exist at `brand/final/tachi-logo-primary.png` and `brand/final/tachi-logo-horizontal.png` — confirm non-zero file size and that Typst `image()` can load them

---

## Phase 2: Foundation — Theme Tokens + Heading Migration (Wave 1)

**Purpose**: Create the modular theme architecture and migrate headings for TOC support. This phase MUST complete before any new pages or brand integration can begin.

**CRITICAL**: No user story work can begin until this phase is complete.

### Theme Token System

- [X] T003 [P] [US4] Create `templates/security-report/theme.typ` with 7 brand color tokens (`brand-primary` #1B2A4A, `brand-secondary` #2D4A6F, `brand-accent` #C93A40, `brand-highlight` #B8963E, `brand-dark` #0D0D0D, `brand-light` #F5F2EB, `brand-muted` #64748B), 2 default logo path tokens, and 3 font stack tokens (moved from shared.typ). See `specs/060-professional-pdf-security/data-model.md` for full contract.
- [X] T004 [US4] Refactor `templates/security-report/shared.typ` to import `theme.typ` and replace hardcoded structural colors with aliases: `color-header-bg = brand-primary`, `color-classification-bg = brand-accent`, `color-footer-text = brand-muted`. Remove font stack definitions (now in theme.typ) and import them. Keep severity colors as-is. Keep all exported functions unchanged in signature.
- [X] T005 Verify compilation: `typst compile templates/security-report/main.typ` with existing report-data.typ still works after shared.typ refactoring — no visual regression in existing pages.

### Heading Migration

- [X] T006 [P] [US2] Migrate `templates/security-report/executive-summary.typ` section title from `text(font: font-heading, size: 18pt, ...)[Executive Summary]` to `heading(level: 1)[Executive Summary]`. Remove the manual text call and rely on the heading show rule in `apply-typography()`.
- [X] T007 [P] [US2] Migrate `templates/security-report/findings-detail.typ` section title: replace the `report-header(title: config.title)` text-based title with a `heading(level: 1)[#config.title]` element rendered before the header call. Update `report-header()` call to omit the title parameter.
- [X] T008 [P] [US2] Migrate `templates/security-report/control-coverage.typ` section title to `heading(level: 1)[Control Coverage]` — replace the existing text-based title rendering.
- [X] T009 [P] [US2] Migrate `templates/security-report/remediation-roadmap.typ` section title to `heading(level: 1)[Remediation Roadmap]` — replace the existing text-based title rendering.
- [X] T010 [US2] Migrate `templates/security-report/full-bleed.typ` to accept a `section-name` parameter and render a phantom heading using `place(hide(heading(level: 1)[#section-name]))` before the image. The `place()` wrapper removes the heading from layout flow so it doesn't consume the 0.45in vertical space from heading show rules, preventing full-bleed image cropping. The `hide()` keeps it discoverable by `outline()`. If `place(hide(...))` doesn't work with `outline()`, fall back to metadata/state approach per plan.md Component 2. Update `main.typ` calls to pass section names: "Risk Reduction Funnel", "Risk Summary Dashboard", "System Architecture".
- [X] T011 Verify compilation after heading migration: all existing pages compile and heading elements are visible. Confirm headings render with correct font/size from the `apply-typography()` show rules.

**Checkpoint**: Theme tokens centralized, headings migrated. All existing pages compile with brand colors and heading elements. Foundation ready for new pages.

---

## Phase 3: US2 — Disclaimer and Table of Contents (Priority: P0)

**Goal**: Add the disclaimer page (page 2) and auto-generated table of contents (page 3) so the PDF meets industry-standard assessment report structure.

**Independent Test**: Compile the report and verify page 2 is the disclaimer with 4 notice sections. Verify page 3 is a TOC listing all included sections with correct page numbers.

- [X] T012 [P] [US2] Create `templates/security-report/disclaimer.typ` exporting a `disclaimer-page(classification, custom-text)` function. Render 4 static notice sections (Assessment Notice, Scope Limitation, Recommendation, Confidentiality) with branded layout: Vermillion accent line at top, Tachi Indigo heading. If `custom-text` is not none, use it instead of defaults. Use portrait US Letter page with standard margins, `report-header()`, and `report-footer()`.
- [X] T013 [P] [US2] Create `templates/security-report/toc.typ` exporting a `toc-page(classification)` function. Render `heading(level: 1)[Table of Contents]` followed by `outline(indent: auto, depth: 1)`. Use branded Tachi Indigo heading, standard portrait page with header and footer.
- [X] T014 [US2] Update `templates/security-report/main.typ` to import `disclaimer.typ` and `toc.typ`. Add disclaimer page after cover (gated by `show-disclaimer` flag) and TOC page after disclaimer. Add `show-disclaimer` and `show-methodology` default variables with value `true` for backward compatibility.
- [X] T015 [US2] Verify TOC: compile with varying artifact combinations (threats-only, threats+images, all artifacts) and confirm TOC lists only included sections with correct page numbers. Confirm omitted conditional pages do not appear.

**Checkpoint**: Disclaimer and TOC pages render correctly. TOC auto-updates based on included pages.

---

## Phase 4: US3 — Risk Methodology and Assessment Scope (Priority: P0)

**Goal**: Add methodology explanation and assessment scope pages so the report is audit-ready without supplemental documentation.

**Independent Test**: Compile with threats.md alone — methodology shows qualitative approach. Add risk-scores.md — 4D scoring appears. Scope page shows components and data flows from threats.md Sections 1-2.

- [X] T016 [P] [US3] Create `templates/security-report/methodology.typ` exporting a `methodology-page(classification, has-risk-scores, has-compensating-controls)` function. Render: (1) STRIDE categories explanation, (2) AI-specific threat categories (Prompt Injection, Tool Abuse, Agent Autonomy, Data Poisoning, Model Theft), (3) visual 5x5 probability x impact matrix with severity color coding using `severity-critical/high/medium/low` colors, (4) conditional 4D scoring section when `has-risk-scores` is true, (5) conditional control analysis section when `has-compensating-controls` is true. Use branded heading and standard page layout.
- [X] T017 [P] [US3] Create `templates/security-report/scope.typ` exporting a `scope-page(classification, components, data-flows, trust-boundaries, boundary-crossings, component-count, data-flow-count, trust-boundary-count)` function. Render three sections: (1) Components Analyzed table (Name, Type, Description), (2) Data Flows table (Source, Destination, Data, Protocol), (3) Trust Boundaries table (Zone, Trust Level, Components). Show metric badges (N components, N data flows, N boundaries) at top. If all arrays are empty, show "Limited scope documentation" notice with available metadata.
- [X] T018 [US3] Update `templates/security-report/main.typ` to import `methodology.typ` and `scope.typ`. Add methodology page after TOC (gated by `show-methodology` flag) and scope page after methodology. Pass the appropriate data variables from report-data.typ.
- [X] T019 [US3] Verify methodology page: compile with threats-only (qualitative sections only visible), then with risk-scores.md (4D scoring section appears), then with compensating-controls.md (control analysis section appears). Verify the probability x impact matrix renders with correct severity colors.

**Checkpoint**: Methodology and scope pages render correctly. Content adapts based on available artifacts.

---

## Phase 5: US1 — Branded Cover Page and Running Headers (Priority: P0)

**Goal**: Integrate tachi logos into the cover page and text page headers so the PDF has consistent brand identity.

**Independent Test**: Compile with brand assets present — cover shows primary logo, text pages show horizontal logo in header. Remove brand assets — text-only fallback renders without error.

- [X] T020 [US1] Update `templates/security-report/cover.typ` to accept `has-logo-primary` and `logo-primary-path` parameters. When `has-logo-primary` is true, render the primary logo centered in the upper portion of the page above the decorative rule (using `image(logo-primary-path, width: 2.5in)`). Replace text-based "Generated by *tachi*" at bottom with logo if available. When false, keep text-only branding as fallback. Replace `color-header-bg` references with the theme alias (already done via shared.typ refactoring in T004 — verify colors render as Tachi Indigo).
- [X] T021 [US1] Update `templates/security-report/shared.typ` `report-header()` function to accept optional `has-logo` and `logo-path` parameters. When logo is available, render the horizontal logo left-aligned (height ~0.25in) in the header bar. Retain the classification bar and title rendering. When logo is not available, render header as before (text only).
- [X] T022 [US1] Update `templates/security-report/main.typ` to pass logo parameters to `cover-page()` and to page headers. Import logo variables from `report-data.typ` (`has-logo-primary`, `has-logo-horizontal`, `logo-primary-path`, `logo-horizontal-path`). Add default values (`false` and `none`) for backward compatibility.
- [X] T023 [US1] Verify brand integration: compile with brand assets in `brand/final/` — logos appear on cover and headers. Compile without brand assets — text-only fallback renders. Verify classification banner uses Vermillion color.

**Checkpoint**: Cover page shows tachi logo, text pages have branded headers. Graceful fallback works.

---

## Phase 6: US3 continued — Report Assembler and Schema Updates (Wave 3)

**Goal**: Update the report assembler agent to extract scope data, detect brand assets, and generate the updated report-data.typ with all new variables.

**Independent Test**: Run `/security-report` on a test directory — report assembler generates report-data.typ with scope data, logo paths, and config flags. Full PDF compiles with all new pages populated.

- [X] T024 [US3] Update `.claude/agents/tachi/report-assembler.md` to add Step 2h: Extract scope data from threats.md Section 1 (System Overview — components table, data flows table) and Section 2 (Trust Boundaries — trust zones table, boundary crossings table). Parse markdown tables into arrays of dictionaries matching the contract in `specs/060-professional-pdf-security/data-model.md`. Set arrays to empty `()` and log warning if sections are missing or malformed.
- [X] T025 [P] [US1] Update `.claude/agents/tachi/report-assembler.md` to add Step 2i: Detect brand assets at `brand/final/tachi-logo-primary.png` and `brand/final/tachi-logo-horizontal.png`. If found, set `has-logo-primary/horizontal = true` and compute relative paths using `../../brand/final/` pattern. If not found, set to false.
- [X] T026 Update `.claude/agents/tachi/report-assembler.md` Step 3 to add new variable sections to report-data.typ generation: scope data arrays (7 variables), brand asset variables (4 variables), and page visibility flags (2 variables). See `specs/060-professional-pdf-security/data-model.md` for the full variable list.
- [X] T027 [P] Update `.claude/commands/security-report.md` Step 1 to add brand asset detection alongside existing artifact detection. Report brand asset status in the detection summary.
- [X] T028 [P] Update `schemas/security-report.yaml` from v1.0 to v1.1: add 4 new page types (disclaimer, toc, methodology, scope) to page_sequence, add `theme_tokens` section, add `scope_data` section, add `config` section, and add `brand_assets` to artifact detection matrix.
- [X] T029 Verify end-to-end: run the full pipeline on a test directory with threats.md + risk-scores.md + compensating-controls.md + infographic images. Confirm report-data.typ contains all new variables and the PDF generates with all 12 page types.

**Checkpoint**: Report assembler generates complete report-data.typ. Full end-to-end pipeline works.

---

## Phase 7: US5 — Report Configuration (Priority: P1)

**Goal**: Enable organizational customization via `report-config.typ` without modifying template files.

**Independent Test**: Generate PDF without config file — defaults work. Create config with custom disclaimer and show-methodology=false — customizations applied.

- [X] T030 [US5] Create default `templates/security-report/report-config.typ` with 4 variables: `show-disclaimer = true`, `show-methodology = true`, `custom-disclaimer-text = none`, `custom-footer-text = none`. This file is imported by main.typ.
- [X] T031 [US5] Update `templates/security-report/main.typ` to import `report-config.typ`. Use `show-disclaimer` and `show-methodology` flags to gate disclaimer and methodology page inclusion. Pass `custom-disclaimer-text` to disclaimer-page().
- [X] T032 [US5] Update `.claude/agents/tachi/report-assembler.md` Step 2j: If a user-provided `report-config.typ` exists in the target directory, copy it to `templates/security-report/` before compilation. If not present, ensure the default file is used.
- [X] T033 [US5] Update `templates/security-report/shared.typ` `report-footer()` to accept and use `custom-footer-text` when not none, replacing the default "Generated by tachi" text.
- [X] T034 [US5] Verify: compile without config (defaults work), compile with `show-methodology: false` (methodology page omitted, not in TOC), compile with custom disclaimer text (custom text renders).

**Checkpoint**: Configuration system works. Users can customize without forking templates.

---

## Phase 8: US6 — Card-Based Findings Layout (Priority: P1, Cuttable)

**Goal**: Replace flat table rows with styled finding cards. If cut, enhance the existing table with branded colors.

**Independent Test**: Compile with 5+ findings — cards render. Compile with 15+ findings — cards flow across pages. If cards are cut, verify branded table renders.

- [X] T035 [US6] Update `templates/security-report/findings-detail.typ` to add a card-based rendering mode: each finding as a block with severity badge (colored rounded box), threat ID, component name, description text, and recommendation. For Tier 1 data, include residual risk score and control status fields. Cards use `brand-light` background with `brand-primary` border. Severity badge uses `severity-color()` function. Cards flow across pages with `block(breakable: false)` to prevent orphaning (minimum 2 per page).
- [X] T036 [US6] **Execute unconditionally** (even if card layout T035 is cut): update `templates/security-report/findings-detail.typ` table header cells to use `brand-primary` (Tachi Indigo) via the `color-header-bg` alias. Ensure severity cells retain functional severity colors. This is the minimum branded enhancement and the fallback deliverable.
- [X] T037 [US6] Verify findings rendering: compile with 5 findings (cards layout), compile with 15+ findings (multi-page flow), compile with Tier 1/2/3 data (columns adapt per tier).

**Checkpoint**: Findings display as styled cards or enhanced branded table.

---

## Phase 9: Polish & Cross-Cutting Concerns (Wave 4)

**Purpose**: Visual improvements, backward compatibility verification, and documentation.

- [X] T038 [P] Update `templates/security-report/executive-summary.typ` to use branded design elements: Tachi Indigo for panel headings, Steel Blue for secondary text, Muted Gold accent for severity panel header.
- [X] T039 [P] Update `templates/security-report/control-coverage.typ` to use branded colors for table headers and structural elements.
- [X] T040 [P] Update `templates/security-report/remediation-roadmap.typ` to use branded colors for severity group headings and action item borders.
- [X] T041 Cross-artifact combination testing: compile PDFs with 4 artifact combinations (threats-only, threats+scores, threats+scores+controls, all artifacts including infographic images). Verify each combination produces a valid PDF with correct page count and TOC.
- [X] T042 Brand token audit: search all `.typ` files in `templates/security-report/` for hardcoded hex color values (regex `#[0-9A-Fa-f]{6}`). Verify zero structural colors are hardcoded outside `theme.typ` and severity constants in `shared.typ`. (SC-001)
- [X] T043 Theme customization test: change `brand-primary` in `theme.typ` to a different color, recompile, verify all headings and structural elements update. Restore original color. (SC-005)
- [X] T044 [P] Update `templates/security-report/README.md` with: new page types, theme customization guide, configuration options, updated page sequence, breaking change note for auto-generated report-data.typ, and link to quickstart.md.
- [X] T045 Final validation: generate a full PDF with all artifacts and visually compare against PRD-054 output. Confirm clear professional improvement in branding, layout, and completeness. (SC-007)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US2: Disclaimer + TOC)**: Depends on Phase 2 (heading migration required for TOC)
- **Phase 4 (US3: Methodology + Scope templates)**: Depends on Phase 2 only — can run in PARALLEL with Phase 3
- **Phase 5 (US1: Brand Integration)**: Depends on Phase 2 (theme tokens required) — can run in PARALLEL with Phases 3-4
- **Phase 6 (Agent + Schema)**: Depends on Phases 3-5 (needs final data contract from all new pages)
- **Phase 7 (US5: Configuration)**: Depends on Phase 6 (agent generates config)
- **Phase 8 (US6: Card Findings)**: Depends on Phase 2 only — can run in PARALLEL with Phases 3-7, but LOW priority
- **Phase 9 (Polish)**: Depends on Phases 3-7 completion

### User Story Dependencies

- **US4 (Theme Architecture)**: Foundation phase — no story dependencies, enables all others
- **US2 (Disclaimer + TOC)**: Depends on heading migration (Phase 2) — independent of other stories
- **US3 (Methodology + Scope)**: Depends on foundation — independent of US1, US2
- **US1 (Cover + Headers)**: Depends on foundation — independent of US2, US3
- **US5 (Configuration)**: Depends on agent updates (Phase 6) — sequential after core features
- **US6 (Card Findings)**: Independent of all others — cuttable

### Parallel Opportunities

- **Within Phase 2**: T003, T006-T009 can all run in parallel (different files)
- **Phases 3, 4, 5 can run in parallel**: Each creates different new .typ files with no cross-dependencies
- **Within Phase 6**: T025, T027, T028 can run in parallel (different files)
- **Within Phase 9**: T038, T039, T040, T044 can all run in parallel (different files)

---

## Parallel Example: Wave 2 (New Pages)

```
# After Phase 2 foundation completes, launch all 4 new page templates in parallel:
Agent: "Create disclaimer.typ" (T012)
Agent: "Create toc.typ" (T013)
Agent: "Create methodology.typ" (T016)
Agent: "Create scope.typ" (T017)

# Then integrate into main.typ sequentially:
Agent: "Update main.typ for disclaimer + TOC" (T014)
Agent: "Update main.typ for methodology + scope" (T018)
```

---

## Implementation Strategy

### MVP First (P0 User Stories Only — Waves 1-3)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Foundation (theme + headings) — CRITICAL path
3. Complete Phases 3-5 in parallel: Disclaimer/TOC + Methodology/Scope + Cover/Headers
4. Complete Phase 6: Agent + Schema integration
5. **STOP and VALIDATE**: Full end-to-end PDF with all P0 features
6. Deploy MVP — professional branded report with all new pages

### Incremental Delivery (P1 Features — Wave 4)

7. Add US5: Report configuration
8. Add US6: Card findings (or confirm cuttable)
9. Complete Phase 9: Polish and validation
10. Final side-by-side comparison with PRD-054 output

### Cut Decision for US6 (Card Findings)

If schedule pressure occurs after Wave 3:
- **Cut**: Skip T035-T037 entirely. Existing branded table (with Tachi Indigo headers from T036) is the deliverable.
- **Keep**: Implement cards only if Waves 1-3 complete within 1 session.

---

## Summary

| Phase | Tasks | Parallel | Story Coverage |
|-------|-------|----------|----------------|
| 1. Setup | 2 | 0 | — |
| 2. Foundation | 9 | 5 | US2, US4 |
| 3. Disclaimer + TOC | 4 | 2 | US2 |
| 4. Methodology + Scope | 4 | 2 | US3 |
| 5. Cover + Headers | 4 | 0 | US1 |
| 6. Agent + Schema | 6 | 3 | US1, US3 |
| 7. Configuration | 5 | 0 | US5 |
| 8. Card Findings | 3 | 0 | US6 (cuttable) |
| 9. Polish | 8 | 4 | Cross-cutting |
| **Total** | **45** | **16** | **US1-US6** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No test tasks — visual PDF output verified through manual compilation at each checkpoint
- Card-based findings (US6) is explicitly cuttable per team lead recommendation
- All brand colors must reference theme.typ tokens — zero hardcoded hex values in page templates
