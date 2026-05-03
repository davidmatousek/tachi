# Research Summary: Professional PDF Security Assessment Report with tachi Branding

## Knowledge Base Findings
- No existing KB entries for PDF/Typst/branding patterns (KB not yet populated)

## Codebase Analysis

### Existing Template System (PRD-054 Delivered)
8 Typst template files in `templates/security-report/`:
- **main.typ**: Master orchestrator — imports all templates and report-data.typ, conditional page sequence
- **shared.typ**: Design tokens (severity colors, structural colors, typography), layout functions (`report-header()`, `report-footer()`, `apply-typography()`, `apply-page-setup()`)
- **cover.typ**: Cover page — project name, classification banner, risk posture badge, severity counts. Currently uses `color-header-bg` (#1E293B) not brand colors
- **executive-summary.typ**: Rich mode (narrative + metrics) or minimal mode (metrics + component distribution)
- **findings-detail.typ**: 3-tier findings table with severity sorting, tier-based column configuration
- **control-coverage.typ**: STRIDE coverage matrix, control status table
- **remediation-roadmap.typ**: Severity-grouped remediation actions with SLA targets
- **full-bleed.typ**: Full-bleed infographic pages (16:9 custom dimensions, zero margins)

### Current Color Definitions (shared.typ)
**Structural colors needing brand migration:**
- `color-header-bg`: `#1E293B` (dark slate) → should be Tachi Indigo `#1B2A4A`
- `color-classification-bg`: `#991B1B` (dark red) → should be Vermillion `#C93A40`
- `color-footer-text`: `#64748B` (slate gray) — matches Ash Gray, can stay
- `color-rule`: `#CBD5E1` (light gray) — no brand equivalent, can stay

**Severity colors (must NOT change):**
- Critical: `#DC2626`, High: `#F97316`, Medium: `#EAB308`, Low: `#4169E1`

### Brand Assets (brand/final/)
6 PNG logo variants available:
- `tachi-logo-primary.png` — vertical lockup, for cover pages
- `tachi-logo-primary-dark.png` — vertical lockup, dark backgrounds
- `tachi-logo-horizontal.png` — horizontal lockup, for headers
- `tachi-logo-horizontal-dark.png` — horizontal lockup, dark backgrounds
- `tachi-icon.png` — squircle icon, light mode
- `tachi-icon-dark.png` — squircle icon, dark mode

### Report Assembler Agent
- Located at `.claude/agents/tachi/report-assembler.md`
- 4-step pipeline: artifact detection → data extraction → report-data.typ generation → Typst compilation
- Generates `report-data.typ` with `#let` bindings for all runtime data
- Deletes report-data.typ after successful compilation
- Currently parses: threats.md (frontmatter, Sections 6-7), risk-scores.md (Section 2), compensating-controls.md (Sections 2-3), threat-report.md (Section 1, remediation)
- **New parsing needed**: threats.md Section 1 (Architecture Description) and Section 2 (Trust Boundaries) for Scope page

### Current Page Sequence (main.typ)
1. Cover (always) → 2. Executive Summary (always) → 3. Risk Funnel (conditional) → 4. Baseball Card (conditional) → 5. System Architecture (conditional) → 6. Findings Detail (always) → 7. Control Coverage (conditional) → 8. Remediation Roadmap (conditional)

### Typst TOC Requirement
- `outline()` function requires content to be `heading` elements
- Current templates use `text()` for section titles — must migrate to `heading()` for TOC
- `outlined: false` parameter can exclude specific headings from TOC
- Full-bleed pages need phantom headings for TOC inclusion

## Architecture Constraints
- **Typst 0.11+**: No new external dependencies
- **Data injection pattern**: report-data.typ generated at runtime, imported by main.typ
- **Per-page geometry**: Portrait (US Letter) for text pages, custom 16:9 for infographics
- **No persistent state**: All data parsed at generation time
- **Image paths**: Relative from templates/security-report/ using `../../{target_dir}/` pattern
- **Compilation**: `typst compile templates/security-report/main.typ "{output_path}/security-report.pdf" --root .`

## Industry Research

### Standard Security Assessment Report Sections
Industry best practices (SANS, NIST, ISO 27001) require:
1. **Cover Page** — Title, dates, assessor, classification
2. **Disclaimer** — Legal notice, scope limitations, methodology caveats
3. **Table of Contents** — Navigation for multi-page reports
4. **Methodology** — Assessment approach, tools, frameworks used
5. **Scope** — Systems assessed, boundaries, exclusions
6. **Executive Summary** — Key findings for leadership
7. **Findings** — Detailed vulnerability/threat descriptions with severity
8. **Remediation** — Prioritized action items with timelines
9. **Appendices** — Supporting data, evidence

### Professional Report Presentation
- Severity charts for visual ranking (low-to-high)
- Consistent format and branding throughout
- Tailored to audience (executive vs. technical)
- Charts/graphs to illustrate data trends

### Typst TOC Best Practices
- Use `outline()` with `depth` parameter for level control
- `outlined: false` on decorative headings to exclude from TOC
- State management for conditional content in outlines

## Recommendations for Spec

### Must Address (Architect Concerns from PRD Review)
1. **Heading migration**: All section titles must become `heading()` elements for `outline()` to work. Specify migration approach for existing templates.
2. **Scope data contract**: Define exact data structure for threats.md Section 1 and 2 parsing — component list, data flow list, trust boundary list.
3. **Logo path strategy**: Logos should be injected via report-data.typ (consistent with existing image path pattern) rather than hardcoded in theme.typ.
4. **Full-bleed TOC phantom headings**: Infographic pages need invisible headings for TOC entries without disrupting full-bleed layout.

### Must Address (Team Lead Concerns from PRD Review)
5. **Brand asset format verification**: Spec should require format validation (PNG magic bytes check) before compilation.
6. **Card-based findings**: Mark as P1/cuttable with enhanced table as fallback. Define clear cut criteria.
7. **TOC heading restructuring**: Explicitly call out as implementation requirement — not just adding TOC page, but restructuring all existing templates to use heading elements.

### Additional Recommendations
8. **Backward compatibility**: Existing report-data.typ files must still compile (new pages may be empty)
9. **report-config.typ**: Keep simple — 4 boolean/string overrides, not a full configuration system
10. **Methodology content**: Static template text, not extracted from artifacts — only conditional section inclusion is dynamic
