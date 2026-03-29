# Research Summary: Security Assessment PDF Booklet

## Knowledge Base Findings

### Directly Applicable Patterns

- **PAT-004 (SARIF IR Mapping)**: When the intermediate representation is well-structured, adding new output formats is mechanical. The markdown artifacts serve as the IR; the Typst template system is the format mapper. Keep mapping mechanical, not creative.
- **PAT-005 (Spec-First + Graceful Degradation)**: External dependencies (Gemini API precedent) degrade gracefully. Typst follows the same pattern: install-check + clear error message. Page-inclusion logic mirrors this.
- **PAT-006 (Post-Pipeline Enrichment)**: `/security-report` is the terminal post-pipeline command. Consumes all upstream artifacts without modifying any. Use a dedicated schema (`schemas/security-report.yaml`).
- **PAT-007 (Chained Pipeline Validation)**: Feature 054 validates that the full pipeline chain's artifact contracts are stable enough for a downstream assembler.
- **PAT-009 (Source Material Audit)**: Always verify each artifact's actual structure against schema expectations before writing. Schema version differences (v1.0 lacks Section 4a) need handling.
- **PAT-011 (Numbered Template Sections)**: Each Typst page type should be a self-contained template section with predictable structure, following the infographic template contract pattern.

### Process Patterns
- **PAT-001 (Wave-Based Parallelism)**: Template authoring for different page types can parallelize after Typst POC.
- **PAT-003 (Phased Delivery)**: Natural phase boundaries: POC + scaffold, text pages, full-bleed pages, graceful degradation, integration.

## Codebase Analysis

### Existing Command Patterns
All tachi commands follow a 4-step model:
1. Parse arguments (flags: `--output-dir`, `--title`, explicit path)
2. Validate prerequisites (agent files, data sources, minimum input)
3. Run agent/processing
4. Report results (summary with file paths and next steps)

### 3-Tier Auto-Detection (from `/infographic`)
```
IF compensating-controls.md exists with "## 2. Coverage Matrix" + "Residual Score" column
  -> Use compensating-controls as primary
ELSE IF risk-scores.md exists with "## 2. Scored Threat Table" + "Composite" column
  -> Use risk-scores as primary
ELSE IF threats.md exists with "## 6. Risk Summary"
  -> Use threats as primary
ELSE -> ERROR
```
Co-located `threats.md` required when primary is risk-scores or compensating-controls.

### Existing Schemas
- `schemas/output.yaml` (v1.1) - threats.md structure
- `schemas/risk-scoring.yaml` (v1.0) - 4D scoring
- `schemas/compensating-controls.yaml` (v1.0) - controls extension
- `schemas/infographic.yaml` (v1.0) - infographic spec
- `schemas/finding.yaml` (v1.0) - atomic finding IR
- `schemas/report.yaml` (v1.0) - narrative report

### Template Organization
- Reference templates: `templates/*.md` (output structure examples)
- Infographic templates: `.claude/agents/tachi/templates/infographic-*.md`
- PRD specifies: `templates/security-report/*.typ` for Typst rendering templates

### Severity Color Palette (established)
- Critical: #DC2626 (red)
- High: #F97316 (orange)
- Medium: #EAB308 (yellow)
- Low: #4169E1 (blue)
- Note: Gray

## Architecture Constraints

### Relevant ADRs
- **ADR-016 (Infographic Pipeline Decoupling)**: Standalone command pattern; `/security-report` follows this
- **ADR-014 (Gemini API Optional)**: Spec-first architecture; template + data drives output
- **ADR-013 (SARIF Output)**: SARIF as fallback structured data source
- **ADR-006 (Non-Fatal Error Handling)**: Graceful degradation for external dependencies

### Interface Contract
- Standardized frontmatter: `schema_version`, `date`, `classification`, `input_format`
- Classification field renders on every page header/footer
- SARIF files serve as structured data fallback for tabular pages

### Key Constraints
- US Letter (8.5" x 11") portrait for text pages; custom 16:9 dimensions for infographic pages
- Typst CLI invocation only (`typst compile`) - no browser dependency
- All processing local (no network calls during PDF generation)
- Pin Typst version range 0.11.x-0.12.x

## Industry Research

### Typst for PDF Generation
- Typst is a modern typesetting system designed as a LaTeX alternative
- Supports per-page geometry changes (critical for mixed portrait/landscape)
- Native image embedding via file path references
- CLI-based compilation: `typst compile input.typ output.pdf`
- Cross-platform: macOS, Linux, Windows
- Active development; pre-1.0 with breaking changes between minors

### Security Report Design Best Practices
- Executive summary on page 2 (immediately after cover) for busy executives
- Severity-sorted findings tables with color coding
- Visual elements (charts, infographics) placed before detailed data
- Classification markings on every page for compliance
- Self-contained documents (no external references needed)

## Recommendations for Spec

- Create `schemas/security-report.yaml` defining page inclusion rules and input-to-output mapping (architect recommendation from PRD)
- Follow 4-step command pattern from `/infographic` for command structure
- Reuse 3-tier auto-detection for Findings Detail page data source
- Implement Typst POC as Wave 1 gate before full template authoring (team-lead requirement)
- Separate rendering templates (`templates/security-report/*.typ`) from reference templates with README
- Design each page type as a self-contained Typst module for parallel development
- Handle schema v1.0/v1.1 differences gracefully (omit Section 4a data, never abort)
- SARIF as fallback data source for Findings Detail table when markdown parsing fails
