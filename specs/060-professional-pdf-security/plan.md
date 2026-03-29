---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "All 16 FRs trace to plan components. Wave sequencing delivers P0 value in Waves 1-3. No scope creep. 2 LOW concerns: README backward compat note, phantom heading reliability validation."
  architect_signoff:
    agent: architect
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "Architecture sound. 3 concerns addressed: committed to color alias strategy in shared.typ, corrected phantom heading to use hide(), noted FR-013/SC-004 spec revision for backward compat. Import chain, data contracts, wave sequencing all validated."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "45 tasks feasible for 2-3 sessions (realistic: 2.5). 3 parallel lanes in Wave 2 yield 29% wall-clock reduction. 2 LOW concerns: T036 branded-table fallback should execute unconditionally regardless of US6 cut, T010 phantom heading fallback from plan.md Component 2 should be referenced in task description."
---

# Implementation Plan: Professional PDF Security Assessment Report with tachi Branding

**Branch**: `060-professional-pdf-security` | **Date**: 2026-03-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/060-professional-pdf-security/spec.md`

## Summary

Enhance the existing Typst-based PDF security assessment report (PRD-054) with tachi brand identity, four new industry-standard pages (Disclaimer, Table of Contents, Risk Methodology, Assessment Scope), and a modular theme architecture. The implementation modifies 8 existing `.typ` template files, creates 6 new files (`theme.typ`, `disclaimer.typ`, `toc.typ`, `methodology.typ`, `scope.typ`, `report-config.typ`), and updates the report assembler agent to extract scope data and inject brand asset paths.

## Technical Context

**Language/Version**: Typst 0.11+ (declarative document layout language, pre-1.0 API)
**Primary Dependencies**: Typst CLI (external, user-installed via `brew install typst` or `cargo install typst-cli`), no new dependencies beyond PRD-054
**Storage**: Local filesystem only — markdown artifacts parsed at generation time, no persistent state
**Testing**: Manual PDF generation and visual inspection. Compile verification via `typst compile main.typ output.pdf --root .`
**Target Platform**: macOS (primary), Linux (secondary) — same as PRD-054
**Project Type**: Template system (Typst `.typ` files + markdown agent instructions)
**Performance Goals**: PDF generation < 30 seconds for full report with 3 infographic images and all new pages
**Constraints**: Backward compatible with PRD-054 `report-data.typ` files; no custom font files; Typst `image()` for PNG/JPEG logo embedding
**Scale/Scope**: 14 template files (8 modified + 6 new), 1 agent file updated, 1 schema file updated, 1 command file updated

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose | PASS | Template enhancement, no domain-specific logic in core |
| II. API-First | N/A | No API — Typst templates and CLI tool |
| III. Backward Compatibility | PASS | Existing report-data.typ files must still compile (FR-013) |
| IV. Concurrency | N/A | Single-user compilation, no concurrent access |
| V. Privacy | PASS | Local-only, no data leaves machine |
| VI. Testing Excellence | PASS | Manual compile verification across artifact combinations |
| VII. Definition of Done | PASS | 3-step validation planned |
| VIII. Observability | N/A | CLI tool, no runtime monitoring |
| IX. Git Workflow | PASS | Feature branch `060-professional-pdf-security` |
| X. Product-Spec Alignment | PASS | spec.md PM-approved, plan requires PM+Architect |
| XI. SDLC Triad | PASS | Full triad governance active |

## Project Structure

### Documentation (this feature)

```
specs/060-professional-pdf-security/
├── plan.md              # This file
├── research.md          # Research phase output (from spec phase)
├── data-model.md        # Theme token contract and data variable definitions
├── quickstart.md        # Developer guide for theme customization
└── tasks.md             # Task breakdown (next step)
```

### Source Code (repository root)

```
templates/security-report/
├── theme.typ                  # NEW: Brand tokens (colors, logos, fonts)
├── shared.typ                 # MODIFIED: Import theme.typ, retain layout functions
├── report-config.typ          # NEW: User-configurable overrides (optional at runtime)
├── main.typ                   # MODIFIED: New page sequence, config import, heading setup
├── cover.typ                  # MODIFIED: Logo + brand colors + heading element
├── disclaimer.typ             # NEW: Legal disclaimer page
├── toc.typ                    # NEW: Table of contents via outline()
├── methodology.typ            # NEW: Risk methodology explanation
├── scope.typ                  # NEW: Assessment scope from threats.md
├── executive-summary.typ      # MODIFIED: Brand colors + heading element
├── full-bleed.typ             # MODIFIED: Phantom heading for TOC inclusion
├── findings-detail.typ        # MODIFIED: Brand colors + heading element (+ optional cards P1)
├── control-coverage.typ       # MODIFIED: Brand colors + heading element
└── remediation-roadmap.typ    # MODIFIED: Brand colors + heading element

schemas/
└── security-report.yaml       # MODIFIED: v1.0 → v1.1 (new pages, scope data, theme contract)

.claude/agents/tachi/
└── report-assembler.md        # MODIFIED: Scope data extraction, logo path injection, config generation

.claude/skills/
└── security-report.md         # MODIFIED: Brand asset detection in Step 1
```

**Structure Decision**: Template-only project — all changes are in `templates/security-report/`, `schemas/`, and agent/skill markdown files. No application source code.

## Components

### Component 1: Theme Token System (`theme.typ` + `shared.typ` refactoring)

**Purpose**: Centralize all brand tokens in a single file so customization requires editing only one file.

**Design**:

`theme.typ` exports `#let` bindings for:
- 7 brand colors: `brand-primary`, `brand-secondary`, `brand-accent`, `brand-highlight`, `brand-dark`, `brand-light`, `brand-muted`
- 2 logo paths: `logo-primary-path`, `logo-horizontal-path` (default values, overridden by report-data.typ at runtime)
- 3 font stacks: `font-heading`, `font-body`, `font-mono` (moved from shared.typ)

`shared.typ` changes:
- Imports `theme.typ`: `#import "theme.typ": *`
- Replaces hardcoded structural colors with theme tokens:
  - `color-header-bg`: `#1E293B` → `brand-primary` (`#1B2A4A`)
  - `color-classification-bg`: `#991B1B` → `brand-accent` (`#C93A40`)
  - `color-footer-text`: `#64748B` → `brand-muted` (`#64748B`) — same value
  - `color-rule`: `#CBD5E1` — no brand equivalent, stays as structural constant
- Severity colors remain as-is (functional constants, NOT moved to theme)
- All existing exported functions remain unchanged in signature

**Color alias strategy**: `shared.typ` retains the existing variable names (`color-header-bg`, `color-classification-bg`, `color-footer-text`) as aliases pointing to theme tokens. This avoids updating 20+ references across 6 template files:
```typst
// shared.typ — aliases for backward compatibility
#let color-header-bg = brand-primary       // was #1E293B, now #1B2A4A
#let color-classification-bg = brand-accent // was #991B1B, now #C93A40
#let color-footer-text = brand-muted       // was #64748B, unchanged
```
Page templates continue to reference `color-header-bg` etc. — no import statement changes needed.

**Backward compatibility**: Page templates that import `shared.typ` get the new colors automatically via the aliased variables. No import statement changes needed in page templates.

### Component 2: Heading Migration (all page templates)

**Purpose**: Enable Typst `outline()` to auto-generate a TOC by converting section titles from `text()` to `heading` elements.

**Design**:

Each page template that currently renders its section title via `text(font: font-heading, size: 18pt, ...)` must change to a Typst `heading(level: 1)` element. The heading will:
- Be rendered by the existing `show heading.where(level: 1)` rule in `apply-typography()`
- Be automatically picked up by `outline()` for TOC generation

**Template-specific migration**:

| Template | Current Title Rendering | Migration |
|----------|------------------------|-----------|
| `cover.typ` | `text(size: 28pt, ...)` project name | No heading — cover excluded from TOC via `header: none` page. Add a phantom `heading(level: 1, outlined: false)` if needed for page counter. |
| `executive-summary.typ` | `text(size: 18pt, ...)[Executive Summary]` | → `heading(level: 1)[Executive Summary]` |
| `findings-detail.typ` | `report-header(title: config.title)` via `text()` | → `heading(level: 1)[#config.title]` (replace text-based header title) |
| `control-coverage.typ` | `report-header(title: ...)` | → `heading(level: 1)[Control Coverage]` |
| `remediation-roadmap.typ` | `report-header(title: ...)` | → `heading(level: 1)[Remediation Roadmap]` |
| `full-bleed.typ` | None | → Add phantom `heading(level: 1, outlined: true)` with section name (e.g., "Risk Reduction Funnel") rendered invisible on the page but visible in TOC |
| `disclaimer.typ` (new) | N/A | → `heading(level: 1)[Disclaimer]` |
| `methodology.typ` (new) | N/A | → `heading(level: 1)[Risk Methodology]` |
| `scope.typ` (new) | N/A | → `heading(level: 1)[Assessment Scope]` |

**Phantom heading technique for full-bleed pages**:

Use Typst's `hide()` function to create headings that participate in `outline()` but consume no visible space:
```typst
// Inside full-bleed-page(), before the image:
#set text(size: 0pt)  // Prevent vertical space consumption
#hide(heading(level: 1)[#section-name])
```

The `hide()` approach is preferred over content-flow overlay because heading elements consume vertical space (0.45in+ from heading show rules), which would cause visible cropping on full-bleed pages. `hide()` keeps the heading in the document flow for `outline()` discovery while rendering it invisible.

Fallback if `hide()` doesn't work with `outline()`:
- Use `metadata()` or `state` to manually add TOC entries
- Test during implementation and document which approach works

**`report-header()` function update**: The `title` parameter in `report-header()` currently renders as `text()`. For pages that use `report-header(title: "...")`, the heading element should be rendered separately before calling `report-header()` (which can then omit the title parameter or retain it for the visual header bar).

### Component 3: New Page Templates

#### 3a: `disclaimer.typ`

**Content** (static template text, four sections):
1. **Assessment Notice**: Automated threat modeling toolkit notice
2. **Scope Limitation**: Limited to architecture description provided
3. **Recommendation**: Complement with manual security review
4. **Confidentiality**: Distribution limited to authorized personnel

**Layout**: Portrait US Letter, branded header (Vermillion accent line at top, Tachi Indigo heading), standard footer. No runtime data needed — all text is hardcoded defaults unless overridden by `report-config.typ`.

**Config override**: If `report-config.typ` defines `custom-disclaimer-text`, use it instead of defaults.

#### 3b: `toc.typ`

**Implementation**: Single call to Typst `outline()` function with branded styling:
```typst
heading(level: 1)[Table of Contents]
outline(
  indent: auto,
  depth: 1,  // Only level-1 headings
)
```

**Conditional page handling**: `outline()` naturally excludes headings inside `#if false { ... }` blocks. Headings for omitted conditional pages simply don't exist in the document, so they won't appear in the TOC. No special handling needed.

**Styling**: Apply Tachi Indigo to the "Table of Contents" heading. Use standard body font for outline entries. Typst handles dot leaders and page numbers automatically.

#### 3c: `methodology.typ`

**Content structure** (static template text with conditional sections):

1. **Threat Identification** (always): STRIDE categories + AI-specific categories — static explanation text.
2. **Probability x Impact Matrix** (always): Visual 2D grid with severity color coding. 5x5 matrix with rows (Impact: Negligible, Low, Moderate, High, Critical) and columns (Probability: Rare, Unlikely, Possible, Likely, Almost Certain). Cells colored by resulting severity level.
3. **Quantitative Scoring** (conditional: `has-risk-scores`): 4D scoring methodology — CVSS 3.1, Exploitability, Scalability, Reachability. Composite score formula. Static explanation text.
4. **Control Analysis** (conditional: `has-compensating-controls`): Compensating control detection methodology. Residual risk calculation. Static explanation text.

**Data needed from report-data.typ**: Only `has-risk-scores` and `has-compensating-controls` booleans (already exported).

#### 3d: `scope.typ`

**Data contract** (new variables in `report-data.typ`):

```typst
// Scope data — extracted from threats.md Sections 1-2
#let scope-components = (
  (name: "API Gateway", type: "Process", description: "Routes API requests"),
  (name: "Auth Service", type: "Process", description: "Handles authentication"),
  // ...
)

#let scope-data-flows = (
  (source: "Client", destination: "API Gateway", data: "API Requests", protocol: "HTTPS"),
  // ...
)

#let scope-trust-boundaries = (
  (zone: "Public Internet", trust-level: "Untrusted", components: "Client App"),
  // ...
)

#let scope-boundary-crossings = (
  (crossing: "Internet → DMZ", from-zone: "Public", to-zone: "DMZ", components: "API Gateway", controls: "WAF, TLS"),
  // ...
)

// Counts for quick reference
#let scope-component-count = 5
#let scope-data-flow-count = 8
#let scope-trust-boundary-count = 3
```

**Graceful degradation**: If scope arrays are empty (schema v1.0 or minimal threats.md), display frontmatter metadata (assessment date, classification, total findings) with "Limited scope documentation" notice.

**Layout**: Portrait US Letter. Three sections: Components Analyzed (table), Data Flows (table), Trust Boundaries (table). Assessment statistics (N components, N data flows, N trust boundaries) displayed as metric badges similar to executive summary.

### Component 4: Report Assembler Updates

**New parsing requirements** (added to existing Step 2):

**Step 2h: Extract Scope Data from threats.md**
1. Parse Section 1 ("System Overview" / "Architecture Description"):
   - Find the components table (headers: Component, Type, Description)
   - Extract each row as a dictionary: `{name, type, description}`
   - Find the data flows table (headers: Source, Destination, Data, Protocol)
   - Extract each row as a dictionary: `{source, destination, data, protocol}`
2. Parse Section 2 ("Trust Boundaries"):
   - Find the trust zones table (headers: Zone, Trust Level, Components)
   - Extract each row as a dictionary: `{zone, trust_level, components}`
   - Find the boundary crossings table (headers: Crossing, From Zone, To Zone, Components, Controls)
   - Extract each row as a dictionary: `{crossing, from_zone, to_zone, components, controls}`
3. Count totals for each category.
4. If Section 1 or 2 cannot be parsed (missing, malformed, schema v1.0 without expected headers): set arrays to empty `()` and log warning.

**Step 2i: Detect Brand Assets**
1. Check for `brand/final/tachi-logo-primary.png` and `brand/final/tachi-logo-horizontal.png`
2. If found: set `has-logo-primary = true`, `has-logo-horizontal = true` and compute relative paths using the same `../../` pattern as infographic images
3. If not found: set to false, log info message

**Step 3 additions** (new variables in report-data.typ):
```typst
// --- Scope Data ---------------------------------------------------------------
#let scope-components = (...)
#let scope-data-flows = (...)
#let scope-trust-boundaries = (...)
#let scope-boundary-crossings = (...)
#let scope-component-count = N
#let scope-data-flow-count = N
#let scope-trust-boundary-count = N

// --- Brand Assets -------------------------------------------------------------
#let has-logo-primary = true
#let has-logo-horizontal = true
#let logo-primary-path = "../../brand/final/tachi-logo-primary.png"
#let logo-horizontal-path = "../../brand/final/tachi-logo-horizontal.png"

// --- Page Visibility (config overrides) ---------------------------------------
#let show-disclaimer = true
#let show-methodology = true
```

**Step 2j: Generate report-config.typ** (optional)
- If user has placed a `report-config.typ` in the target directory, copy it to `templates/security-report/` before compilation.
- If not present, generate a minimal default with all values set to defaults.
- This file is imported by `main.typ` alongside `report-data.typ`.

**Backward compatibility**: When an existing PRD-054 `report-data.typ` is used (lacking new variables), `main.typ` must provide default values:
```typst
// In main.typ, after importing report-data.typ:
#let scope-components = if "scope-components" in ??? { scope-components } else { () }
```

The approach is:
- `main.typ` imports `report-data.typ` which defines ALL variables
- The report assembler ALWAYS generates the full set of variables (including new ones)
- `report-data.typ` is auto-generated and transient (deleted after compilation) — it is never hand-authored or reused across versions
- **Spec update needed**: FR-013 and SC-004 (backward compatibility with old report-data.typ) should be revised to reflect that backward compatibility applies to the pipeline (same command interface, same artifact inputs) rather than to the intermediate generated file. Document this in README.

### Component 5: Updated Page Sequence in main.typ

**New sequence** (12 page types, up from 8):

```
1.  Cover                (always)
2.  Disclaimer           (always, unless show-disclaimer == false)
3.  Table of Contents    (always)
4.  Risk Methodology     (always, unless show-methodology == false)
5.  Assessment Scope     (always)
6.  Executive Summary    (always)
7.  Risk Funnel          (conditional: has-funnel-image)
8.  Baseball Card        (conditional: has-baseball-image)
9.  System Architecture  (conditional: has-architecture-image)
10. Findings Detail      (always)
11. Control Coverage     (conditional: has-compensating-controls)
12. Remediation Roadmap  (conditional)
```

**New imports in main.typ**:
```typst
#import "disclaimer.typ": disclaimer-page
#import "toc.typ": toc-page
#import "methodology.typ": methodology-page
#import "scope.typ": scope-page
```

**Config import**: `#import "report-config.typ": *` (optional file — Typst errors if missing, so report assembler must always generate it).

### Component 6: Schema Update (security-report.yaml v1.1)

**Changes from v1.0**:
- `schema_version`: `"1.0"` → `"1.1"`
- New artifact: `brand/final/*.png` (logo assets, enables branded cover/headers)
- New page types in `page_sequence`: `disclaimer`, `toc`, `methodology`, `scope`
- New `theme_tokens` section documenting the brand color contract
- New `scope_data` section documenting the scope variable contract
- New `config` section documenting `report-config.typ` variables

### Component 7: Security Report Command Updates

**Step 1 additions** (artifact detection in `security-report.md`):
- Detect brand assets: `brand/final/tachi-logo-primary.png`, `brand/final/tachi-logo-horizontal.png`
- Report brand asset status alongside other artifacts
- No change to required artifacts — brand assets are optional

## Data Flow

```
threats.md (Sections 1-2)  ──┐
brand/final/*.png           ──┤
risk-scores.md (optional)   ──┤ Report Assembler Agent
compensating-controls.md    ──┤   ├── Parses markdown tables + frontmatter
threat-report.md (optional) ──┤   ├── Detects brand assets
infographic JPEGs (optional)──┘   ├── Generates report-data.typ (all variables)
                                  ├── Generates report-config.typ (defaults or user overrides)
                                  └── Invokes: typst compile main.typ output.pdf --root .
                                        │
                                        ├── main.typ imports:
                                        │     theme.typ → shared.typ → all page templates
                                        │     report-data.typ (runtime data)
                                        │     report-config.typ (user overrides)
                                        │
                                        └── Outputs: security-report.pdf
                                              (up to 12 page types)
```

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Typst | 0.11+ | PDF rendering engine |
| Typst `outline()` | built-in | Auto-generated table of contents |
| Typst `image()` | built-in | PNG/JPEG logo embedding |
| PNG images | N/A | Brand logo assets |
| YAML | N/A | Schema definitions |
| Markdown | N/A | Agent instructions, artifact format |

## Implementation Phases

### Wave 1: Foundation (theme.typ + shared.typ refactoring + heading migration)

**Rationale**: Theme tokens and heading migration are prerequisites for all subsequent work. Every new and modified page depends on theme tokens. TOC depends on headings.

**Deliverables**:
1. Create `theme.typ` with 7 brand colors, 2 logo path defaults, 3 font stacks
2. Refactor `shared.typ` to import `theme.typ` and replace hardcoded colors
3. Migrate section titles from `text()` to `heading()` in all 5 existing page templates
4. Verify compilation: `typst compile main.typ` with existing `report-data.typ` still works

**Gate**: All existing pages compile and render with brand colors. Heading elements visible. No regression in existing layout.

### Wave 2: New Pages (disclaimer, toc, methodology, scope)

**Rationale**: New page templates can be developed in parallel since they have no cross-dependencies. Each is a standalone `.typ` file.

**Deliverables**:
1. Create `disclaimer.typ` with static legal content and branded layout
2. Create `toc.typ` with `outline()` function call and branded heading
3. Create `methodology.typ` with STRIDE + AI categories, visual matrix, conditional scoring sections
4. Create `scope.typ` with component/data-flow/trust-boundary tables and graceful degradation
5. Update `main.typ` to include new pages in correct sequence with conditional guards

**Parallel opportunity**: All 4 new page templates are independent — can be built simultaneously.

**Gate**: All 4 new pages render. TOC lists all sections with correct page numbers. Methodology adapts based on `has-risk-scores` and `has-compensating-controls` flags.

### Wave 3: Agent + Schema + Brand Integration

**Rationale**: Report assembler changes and schema updates depend on understanding the final data contract from Wave 2.

**Deliverables**:
1. Update `report-assembler.md` with Steps 2h (scope extraction), 2i (brand detection), 2j (config generation)
2. Update `security-report.md` command with brand asset detection
3. Update `schemas/security-report.yaml` to v1.1
4. Update `cover.typ` with logo integration and text-only fallback
5. Update `report-header()` in `shared.typ` with horizontal logo in header bar
6. Update `full-bleed.typ` with phantom headings for TOC entries

**Gate**: Full end-to-end generation works — from `threats.md` through report assembler to branded PDF with all new pages.

### Wave 4: Polish + P1 Features + Validation

**Rationale**: Visual refinements and optional features after core functionality is stable.

**Deliverables**:
1. Create `report-config.typ` support with 4 configurable values
2. Card-based findings layout (P1, cuttable) — implement or confirm enhanced table fallback
3. Visual polish: improved layouts for executive summary, control coverage, remediation pages
4. Backward compatibility testing: compile with PRD-054 report-data.typ
5. Cross-artifact combination testing: threats-only, threats+scores, threats+controls, all artifacts
6. README updates for templates directory

**Gate**: All acceptance scenarios from spec pass. SC-001 through SC-007 verified.

## Complexity Tracking

No constitution violations — all work is within a single template directory with no new external dependencies, no database changes, and no API modifications.

| Concern | Resolution |
|---------|-----------|
| Heading migration scope | 5 existing templates + 4 new = 9 files with heading elements. Manageable in Wave 1. |
| Backward compatibility | report-data.typ is auto-generated, not hand-authored. Missing variables cause compile error — acceptable because users always regenerate. Documented in README. |
| Card-based findings (P1) | Marked cuttable per team lead recommendation. Enhanced branded table is the fallback. |
