---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-08
    status: APPROVED
    notes: "5 findings (0 blocking, 2 LOW, 3 INFORMATIONAL). All spec requirements addressed, user stories US-01 through US-05 have clear implementation paths, scope matches PRD, implementation phases are logical."
  architect_signoff:
    agent: architect
    date: 2026-04-08
    status: APPROVED_WITH_CONCERNS
    notes: "5 findings (1 MEDIUM, 2 LOW, 2 INFORMATIONAL). M-1 extract-report-data.py missing from file inventory — addressed by adding to project structure and Component 6. Architecture consistency verified across all 12 aspects."
  techlead_signoff: null
---

# Implementation Plan: MAESTRO Infographic Templates and PDF Report Section

**Branch**: `091-maestro-infographic-templates` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/091-maestro-infographic-templates/spec.md`

## Summary

Add two MAESTRO-specific infographic templates (maestro-stack and maestro-heatmap), a Typst PDF page for MAESTRO findings, and MAESTRO data extraction to the existing pipeline. Extends Feature 084's MAESTRO layer classification with visual output. All new sections are gated by `has-maestro-data` for backward compatibility.

## Technical Context

**Language/Version**: Python 3.x (extraction script), Typst (PDF templates), Markdown (infographic templates)
**Primary Dependencies**: tachi_parsers.py (shared parsing), Gemini API (image generation), Typst compiler (PDF)
**Storage**: File-based (markdown, JSON, Typst files)
**Testing**: Example validation against `examples/agentic-app/` output (MAESTRO data present) and pre-084 examples (MAESTRO absent)
**Target Platform**: CLI / local filesystem
**Project Type**: Methodology toolkit — templates + scripts (no application code)
**Performance Goals**: Negligible overhead — single pass over existing findings data
**Constraints**: Must follow existing template architecture patterns exactly; backward compatible with pre-084 output
**Scale/Scope**: 3 new files, 6 modified files; ~3 day estimate

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | MAESTRO templates extend existing infographic pattern; no domain-specific logic in core |
| III. Backward Compatibility | PASS | `has-maestro-data` flag gates all new sections; graceful empty state when absent |
| VII. Definition of Done | PASS | SC-001 through SC-008 define measurable validation criteria |
| IX. Git Workflow | PASS | Feature branch `091-maestro-infographic-templates` created |
| X. Product-Spec Alignment | PASS | Spec approved by PM (APPROVED_WITH_CONCERNS) |

No violations detected. Gate passed.

## Project Structure

### Documentation (this feature)

```
specs/091-maestro-infographic-templates/
├── plan.md              # This file
├── research.md          # Codebase + architecture research
├── data-model.md        # MAESTRO data extraction model
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
templates/tachi/infographics/
├── infographic-maestro-stack.md      # NEW — vertical layer stack template
├── infographic-maestro-heatmap.md    # NEW — component-layer grid template
└── INFOGRAPHIC_TEMPLATES.md          # MODIFY — add new template docs

templates/tachi/security-report/
├── maestro-findings.typ              # NEW — MAESTRO findings PDF page
└── main.typ                          # MODIFY — add import + conditional inclusion

scripts/
├── extract-infographic-data.py       # MODIFY — MAESTRO extraction + CLI choices
└── extract-report-data.py            # MODIFY — MAESTRO variable extraction, image detection, report-data.typ generation for 8 new variables

.claude/skills/tachi-infographics/
├── SKILL.md                          # MODIFY — maestro shorthand dispatch
└── references/
    └── template-specific-formats.md  # MODIFY — Section 5 formats for MAESTRO templates

.claude/skills/tachi-report-assembly/references/
└── typst-template-contract.md        # MODIFY — new MAESTRO variables
```

**Structure Decision**: No new directories. All new files follow existing naming and placement conventions. Infographic templates in `templates/tachi/infographics/`, Typst pages in `templates/tachi/security-report/`.

## Components

### Component 1: MAESTRO Data Extraction (`extract-infographic-data.py`)

The extraction script is the data foundation. It must be extended to:

1. **Parse Section 6 "Risk by MAESTRO Layer" table** from threats.md — yields aggregate `maestro_layer_distribution` array: `(layer_id, layer_name, finding_count, highest_severity)` per layer
2. **Parse Section 1 Components table** for `MAESTRO Layer` column — builds component-to-layer mapping
3. **Parse Section 3 agent tables** for per-finding `maestro_layer` — uses existing `deduplicate_findings()` iteration pattern that handles 8-column STRIDE and 9-column AI table structures
4. **Compute `most_exposed_layer`** — layer with highest finding count
5. **Compute component-layer intersection matrix** — for heatmap: each cell = highest severity at that (component, layer) pair
6. **Add `maestro-stack` and `maestro-heatmap`** to CLI `--template` choices (line 933)
7. **Add `maestro-stack` template branch** that includes `maestro_layer_distribution`, `most_exposed_layer`, and per-layer finding summaries in `template_data`
8. **Add `maestro-heatmap` template branch** that includes component-layer intersection grid in `template_data`
9. **Tier strategy**: MAESTRO extraction uses Tier 3 (threats.md) as sole source. When higher-tier sources are present but lack MAESTRO data, fall back to threats.md for MAESTRO fields only
10. **Fallback**: When MAESTRO data is absent (pre-084 output), all MAESTRO fields default to empty/null without errors

### Component 2: Infographic Template — maestro-stack

New file: `templates/tachi/infographics/infographic-maestro-stack.md`

Follows identical structure to existing templates with all mandatory sections:

1. **Layout**: Seven horizontal bands stacked vertically (L7 at top, L1 at bottom). Each band shows layer ID, name, finding count, highest severity (color-coded), and up to 2 top finding summaries. Sidebar with aggregate stats and most-exposed-layer badge.
2. **Style**: Dark Navy (#1E293B) background, 16:9 landscape, consistent with existing templates
3. **Color Palette**: Same 5-severity palette as all templates
4. **Typography**: Same sans-serif system as existing templates
5. **Zone Specifications**: Header zone, stack zone (7 bands), sidebar zone, footer zone
6. **Gemini Prompt Template**: `{placeholder}`-based prompt with STYLING DIRECTIVES and DATA CONTENT sections
7. **Gemini API Configuration**: Same model/fallback/aspect-ratio as existing templates
8. **Accessibility**: Layer labels readable, color not sole severity indicator

**Section 5 format** (new for this template): Layer-grouped table:

```markdown
## 5. Architecture Threat Overlay

| Layer | Name | Finding Count | Highest Severity | Top Findings |
|-------|------|---------------|------------------|--------------|
| L1 | Foundation Model | {N} | {severity} | {ID}: {summary}; {ID}: {summary} |
```

### Component 3: Infographic Template — maestro-heatmap

New file: `templates/tachi/infographics/infographic-maestro-heatmap.md`

Follows identical structure with all mandatory sections:

1. **Layout**: Grid with component rows (capped at top 10 by finding count) and L1-L7 columns. Cells colored by highest severity at intersection. Legend sidebar with severity color scale.
2. **Style**: Dark Navy background, 16:9 landscape
3. **Color Palette**: Same 5-severity palette
4. **Zone Specifications**: Header zone, grid zone, legend zone, footer zone
5. **Gemini Prompt Template**: Grid-specific prompt with row/column data bindings
6. **Gemini API Configuration**: Same config as all templates
7. **Accessibility**: Grid cells use both color and text labels

**Section 5 format** (new for this template): Component-layer intersection grid:

```markdown
## 5. Architecture Threat Overlay

### Component-Layer Intersection Grid

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| {name} | {severity|—} | {severity|—} | ... | ... | ... | ... | ... |
```

### Component 4: Typst PDF Page — maestro-findings.typ

New file: `templates/tachi/security-report/maestro-findings.typ`

Follows `findings-detail.typ` single-export-function pattern:

1. **Export function**: `maestro-findings-page(classification: none, maestro-findings-by-layer: (), has-maestro-data: false)`
2. **Rendering**: Groups findings by MAESTRO layer (L1-L7 + Unclassified). Each layer section shows:
   - Layer heading with ID and full name
   - CSA description (brief)
   - Finding cards: ID, component, severity badge, threat summary
   - Finding count per layer
3. **Empty state**: If `has-maestro-data` is false, function renders nothing (guard in main.typ)
4. **Sorting**: Layers in L1-L7 order, findings within each layer sorted by severity rank

### Component 5: main.typ Integration

Modify `templates/tachi/security-report/main.typ`:

1. **Add import** (line ~44): `#import "maestro-findings.typ": maestro-findings-page`
2. **Add backward-compat defaults** (Section 2b, ~line 80):
   ```typst
   #let has-maestro-data = if has-maestro-data != none { has-maestro-data } else { false }
   #let maestro-findings-by-layer = if maestro-findings-by-layer != none { maestro-findings-by-layer } else { () }
   #let most-exposed-layer = if most-exposed-layer != none { most-exposed-layer } else { "" }
   #let has-maestro-stack-image = if has-maestro-stack-image != none { has-maestro-stack-image } else { false }
   #let maestro-stack-image-path = if maestro-stack-image-path != none { maestro-stack-image-path } else { "" }
   #let has-maestro-heatmap-image = if has-maestro-heatmap-image != none { has-maestro-heatmap-image } else { false }
   #let maestro-heatmap-image-path = if maestro-heatmap-image-path != none { maestro-heatmap-image-path } else { "" }
   #let maestro-layer-distribution = if maestro-layer-distribution != none { maestro-layer-distribution } else { () }
   ```
3. **Add MAESTRO infographic pages** (after System Architecture, before "Detailed Findings" divider):
   ```typst
   #if has-maestro-stack-image {
     infographic-page(maestro-stack-image-path, section-name: "MAESTRO Layer Risk Distribution", ...)
   }
   #if has-maestro-heatmap-image {
     infographic-page(maestro-heatmap-image-path, section-name: "MAESTRO Component-Layer Heatmap", ...)
   }
   ```
4. **Add MAESTRO findings page** (after MAESTRO infographics, before "Detailed Findings" divider):
   ```typst
   #if has-maestro-data {
     page(...)[#maestro-findings-page(classification: classification, maestro-findings-by-layer: maestro-findings-by-layer, has-maestro-data: has-maestro-data)]
   }
   ```

### Component 6: report-data.typ Contract Extension and Report Data Extraction

Update `typst-template-contract.md` to document new variables.

Update `scripts/extract-report-data.py` to generate MAESTRO variables in report-data.typ:
- Extend `detect_images()` to detect `threat-maestro-stack.jpg` and `threat-maestro-heatmap.jpg`
- Add MAESTRO parsing: Section 6 "Risk by MAESTRO Layer" for aggregate distribution, Section 3 per-finding MAESTRO layer for findings-by-layer grouping
- Extend `generate_report_data_typ()` to emit all 8 new MAESTRO variables

New variables to add:

```typst
// --- MAESTRO Data (from threats.md MAESTRO layer classification) --------
#let has-maestro-data = {true/false}
#let maestro-layer-distribution = (
  (layer-id: "L1", layer-name: "Foundation Model", finding-count: 8, highest-severity: "Critical"),
  // ... one tuple per layer with findings
)
#let most-exposed-layer = "L1 — Foundation Model"
#let maestro-findings-by-layer = (
  (layer-id: "L1", layer-name: "Foundation Model", findings: (
    (id: "S-1", component: "LLM Engine", severity: "Critical", threat: "..."),
  )),
)
#let has-maestro-stack-image = {true/false}
#let maestro-stack-image-path = "../../{target_dir}/threat-maestro-stack.jpg"
#let has-maestro-heatmap-image = {true/false}
#let maestro-heatmap-image-path = "../../{target_dir}/threat-maestro-heatmap.jpg"
```

### Component 7: Infographic Skill Dispatch Update

Update `.claude/skills/tachi-infographics/SKILL.md` to handle `maestro` shorthand:
- `maestro` expands to `["maestro-stack", "maestro-heatmap"]`
- Individual `maestro-stack` and `maestro-heatmap` dispatch to respective template files

Update `.claude/skills/tachi-infographics/references/template-specific-formats.md`:
- Add Section 5 format definitions for maestro-stack (layer-grouped table)
- Add Section 5 format definitions for maestro-heatmap (component-layer intersection grid)

### Component 8: Documentation Update

Update `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md`:
- Add maestro-stack and maestro-heatmap to Available Templates table
- Add new rows to Output Files table
- Document `maestro` shorthand in Using Templates section
- Document MAESTRO-specific placeholders

## Data Flow

```
threats.md (with MAESTRO data)
    │
    ├─→ extract-infographic-data.py --template maestro-stack
    │     │
    │     ├─→ Parse Section 6 "Risk by MAESTRO Layer" → maestro_layer_distribution
    │     ├─→ Parse Section 1 Components → component-to-layer map
    │     ├─→ Parse Section 3 findings → per-finding maestro_layer
    │     ├─→ Compute most_exposed_layer
    │     └─→ infographic-data.json (maestro-stack template_data)
    │           └─→ Infographic agent → threat-maestro-stack-spec.md → Gemini → threat-maestro-stack.jpg
    │
    ├─→ extract-infographic-data.py --template maestro-heatmap
    │     │
    │     ├─→ Same parsing as above
    │     ├─→ Compute component-layer intersection matrix
    │     └─→ infographic-data.json (maestro-heatmap template_data)
    │           └─→ Infographic agent → threat-maestro-heatmap-spec.md → Gemini → threat-maestro-heatmap.jpg
    │
    └─→ extract-report-data.py (report assembly)
          │
          ├─→ Detect MAESTRO data → set has-maestro-data = true
          ├─→ Extract maestro_layer_distribution, maestro_findings_by_layer
          ├─→ Detect MAESTRO images → set has-maestro-stack-image, has-maestro-heatmap-image
          └─→ report-data.typ
                └─→ main.typ → maestro-findings.typ → PDF page
                     + full-bleed infographic pages for MAESTRO images
```

## Tech Stack

- **Python**: Extraction script extension (regex parsing, JSON output)
- **Typst**: PDF page template (typesetting, conditional page inclusion)
- **Markdown**: Infographic template definitions (Gemini prompt templates)
- **JSON**: Intermediate data format between extraction and rendering
- **Gemini API**: Image generation (same dependency as existing templates)

## Implementation Phases

### Phase 1: Data Extraction (Foundation)
- Extend `extract-infographic-data.py` with MAESTRO parsing functions
- Add CLI choices for `maestro-stack` and `maestro-heatmap`
- Add template-specific data branches
- Validate against `examples/agentic-app/` output

### Phase 2: Infographic Templates
- Create `infographic-maestro-stack.md` following existing template pattern
- Create `infographic-maestro-heatmap.md` following existing template pattern
- Update `template-specific-formats.md` with Section 5 definitions
- Update `INFOGRAPHIC_TEMPLATES.md` documentation

### Phase 3: PDF Report Integration
- Create `maestro-findings.typ` page template
- Extend `main.typ` with imports, defaults, and conditional pages
- Update `typst-template-contract.md` with new variable definitions
- Update report data extraction for MAESTRO variables

### Phase 4: Skill Dispatch + Validation
- Update infographic skill dispatch for `maestro` shorthand
- End-to-end validation against all 6 example architectures
- Regression testing on existing templates

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Section 3 column variation (8 vs 9 columns) | Reuse existing `deduplicate_findings()` pattern that already handles column count variation |
| Heatmap readability with many components | Cap at top 10 components by finding count, consistent with existing heat_map cap |
| Gemini image quality for new visual formats | Reuse proven prompt engineering patterns from existing templates |
| Backward compatibility with pre-084 output | `has-maestro-data` boolean gates all MAESTRO sections; defaults in main.typ |

## Complexity Tracking

No constitution violations detected. No complexity justifications needed.
