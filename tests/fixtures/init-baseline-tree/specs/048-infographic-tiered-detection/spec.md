---
prd_reference: docs/product/02_PRD/048-infographic-tiered-detection-residual-risk-2026-03-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 3 PRD user stories covered at correct priorities (P0/P0/P1). 16 FRs decompose 4 PRD FRs completely. 6 edge cases including detection-vs-extraction failure distinction. No scope creep. Column name aligned to schema."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Infographic Tiered Pipeline Auto-Detection & Residual Risk

**Feature Branch**: `048-infographic-tiered-detection`
**Created**: 2026-03-28
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/048-infographic-tiered-detection-residual-risk-2026-03-28.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tiered Auto-Detection with Residual Risk (Priority: P0)

A security analyst has run the full tachi pipeline (`/threat-model` then `/risk-score` then `/compensating-controls`) and now runs `/infographic` to generate a visual summary. The command automatically detects that `compensating-controls.md` is available — the richest data source — and uses residual risk scores instead of inherent scores. The resulting infographic reflects the team's actual security posture after accounting for existing defenses, giving stakeholders an accurate picture rather than worst-case exposure.

**Why this priority**: This is the core value proposition. Without this, users who invest in running the full pipeline get no visual benefit from compensating controls analysis. Infographics continue to misrepresent exposure by showing inherent risk even when residual risk data exists.

**Independent Test**: Run `/infographic` in a directory containing `compensating-controls.md`, `risk-scores.md`, and `threats.md`. The generated infographic spec must use residual risk scores from `compensating-controls.md` and require co-located `threats.md` for structural data.

**Acceptance Scenarios**:

1. **Given** `compensating-controls.md`, `risk-scores.md`, and `threats.md` all exist in the output directory, **When** the user runs `/infographic`, **Then** the command selects `compensating-controls.md` as the primary data source and extracts residual risk scores for the infographic
2. **Given** only `risk-scores.md` and `threats.md` exist (no `compensating-controls.md`), **When** the user runs `/infographic`, **Then** the command selects `risk-scores.md` and produces an inherent risk infographic (existing behavior preserved)
3. **Given** only `threats.md` exists, **When** the user runs `/infographic`, **Then** the command selects `threats.md` and produces a qualitative severity infographic (existing behavior preserved)
4. **Given** `compensating-controls.md` is the detected source, **When** the infographic extracts risk data, **Then** it uses residual scores from the Coverage Matrix sub-tables (not inherent composite scores from risk-scores.md)
5. **Given** `compensating-controls.md` exists but `threats.md` does not, **When** the user runs `/infographic`, **Then** the command reports an error requiring co-located `threats.md` for structural and metadata

---

### User Story 2 - Enhancement Tips at Each Tier (Priority: P0)

A developer new to tachi runs `/threat-model` and then `/infographic`. The infographic generates successfully from `threats.md`, but also displays a single-line tip suggesting they run `/risk-score` to get quantitative scores in their next infographic. Later, after running `/risk-score`, they run `/infographic` again and see a tip about `/compensating-controls`. This progressive discovery guides them through the full pipeline without requiring them to read documentation.

**Why this priority**: Pipeline discoverability is essential for adoption. Users who stop after `/threat-model` miss the enrichment commands. Enhancement tips create a natural learning path at zero cost to experienced users.

**Independent Test**: Run `/infographic` at each pipeline tier and verify the correct tip message appears. Run with an explicit file path and verify no tip appears.

**Acceptance Scenarios**:

1. **Given** `threats.md` is the auto-detected source, **When** the command reports its data source, **Then** it displays a tip recommending `/risk-score` for quantitative scores
2. **Given** `risk-scores.md` is the auto-detected source, **When** the command reports its data source, **Then** it displays a tip recommending `/compensating-controls` for residual risk visualization
3. **Given** `compensating-controls.md` is the auto-detected source, **When** the command reports its data source, **Then** it displays a confirmation that the full pipeline is detected and residual risk is being visualized
4. **Given** the user passes an explicit file path override (`/infographic path/to/file.md`), **When** the command runs, **Then** no enhancement tip is displayed

---

### User Story 3 - Residual vs Inherent Risk Labels (Priority: P1)

A security analyst generates an infographic from the full pipeline and shares it with stakeholders. The infographic header and chart labels clearly indicate "Residual Risk" so readers understand they are seeing post-control exposure, not unmitigated risk. When a colleague generates an infographic from `risk-scores.md` only, their output says "Inherent Risk" — making the distinction unambiguous when both are compared.

**Why this priority**: Without clear labeling, stakeholders may misinterpret risk scores. Explicit labels prevent confusion when infographics from different pipeline tiers are compared side-by-side. This is important but secondary to the core detection and extraction (US-1).

**Independent Test**: Generate infographics from each of the three data source types and verify the header label matches the expected risk type.

**Acceptance Scenarios**:

1. **Given** the data source is `compensating-controls.md`, **When** the infographic spec is generated, **Then** risk labels read "Residual Risk"
2. **Given** the data source is `risk-scores.md`, **When** the infographic spec is generated, **Then** risk labels read "Inherent Risk"
3. **Given** the data source is `threats.md`, **When** the infographic spec is generated, **Then** risk labels read "Severity" (existing behavior)
4. **Given** the data source is `compensating-controls.md`, **When** the baseball-card template is generated, **Then** the donut chart shows residual severity distribution and finding cards show residual scores
5. **Given** the data source is `compensating-controls.md`, **When** the baseball-card template is generated, **Then** the summary zone includes a risk reduction percentage line

---

### Edge Cases

- **compensating-controls.md exists but has malformed Coverage Matrix**: Detection succeeds (header found) but extraction encounters empty or malformed rows. The command halts with a warning rather than silently falling through to `risk-scores.md`, preventing infographics with misrepresented risk values.
- **compensating-controls.md exists but lacks the Coverage Matrix header**: Detection fails for this tier, and the hierarchy naturally falls through to `risk-scores.md`. This is a detection-level failure, not an extraction-level failure.
- **All three files exist but compensating-controls.md has zero findings**: The command proceeds with compensating-controls.md (it is structurally valid) and generates an infographic showing zero residual risk findings.
- **compensating-controls.md and threats.md exist but risk-scores.md does not**: The command proceeds normally. Risk-scores.md is NOT required when compensating-controls.md is the primary source (residual scores are self-contained in the controls file).
- **No data source files exist in the directory**: The command exits with an error listing the three expected file locations and the pipeline command that produces each.
- **Explicit path points to unrecognized file format**: When a file passed via explicit path matches no known detection markers (no Coverage Matrix, no Scored Threat Table, no Risk Summary), the command reports an error indicating unrecognized file format.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `/infographic` command MUST auto-detect data sources in a three-tier priority order: `compensating-controls.md` (highest) > `risk-scores.md` > `threats.md` (lowest), selecting the first file found
- **FR-002**: When `compensating-controls.md` is detected as the primary source, the command MUST extract residual risk scores (not inherent composite scores) from the Coverage Matrix sub-tables
- **FR-003**: The Coverage Matrix extraction MUST iterate across all four severity-band sub-tables (Critical, High, Medium, Low) to collect the complete finding set
- **FR-004**: When `compensating-controls.md` is the primary source, a co-located `threats.md` MUST be required for project metadata (Section 1) and spatial/structural data (Section 2)
- **FR-005**: When `compensating-controls.md` is the primary source, `risk-scores.md` MUST NOT be required (residual scores are self-contained)
- **FR-006**: Content-based type detection MUST be used when an explicit file path is provided: compensating-controls files are identified by the `## 2. Coverage Matrix` header AND a table containing a `Residual Score` column
- **FR-007**: The command MUST display a single-line enhancement tip after data source detection, indicating which pipeline command would produce the next richer tier of data
- **FR-008**: Enhancement tips MUST be suppressed when the user provides an explicit file path override
- **FR-009**: Both existing templates (baseball-card and system-architecture) MUST support the compensating-controls data source with no structural layout changes — only data values and labels change
- **FR-010**: Detection-level failures (file exists but lacks expected headers/columns) MUST fall through to the next tier in the hierarchy gracefully
- **FR-011**: Extraction-level failures (detection succeeds but data rows are malformed or missing) MUST halt with a warning message, not silently fall through to a lower tier
- **FR-012**: All existing `/infographic` invocations (with risk-scores.md or threats.md) MUST continue to produce identical output (backward compatibility)
- **FR-013**: When the data source is `compensating-controls.md`, infographic risk labels MUST read "Residual Risk"; when `risk-scores.md`, labels MUST read "Inherent Risk"; when `threats.md`, labels MUST read "Severity"
- **FR-014**: When the data source is `compensating-controls.md`, the baseball-card template MUST include a risk reduction percentage line in the summary zone showing overall control effectiveness
- **FR-015**: The infographic output spec structure (6 sections with YAML frontmatter) MUST remain identical across all three data source types
- **FR-016**: When no recognized data source file exists in the working directory, the command MUST exit with an error listing all three expected file locations and the pipeline command that produces each

### Key Entities

- **Data Source Tier**: Represents one level in the detection hierarchy. Attributes: priority rank (1-3), file identifier, detection markers (header + column), data type (residual/inherent/qualitative), co-location requirements
- **Enhancement Tip**: A single-line message displayed after detection. Attributes: detected tier, tip text, suppression condition (explicit path)
- **Risk Label**: The label applied to risk values in the infographic. Attributes: label text ("Residual Risk" / "Inherent Risk" / "Severity"), source tier that triggers it
- **Coverage Matrix Sub-Table**: A section within `compensating-controls.md` containing findings for one residual severity band. Attributes: severity band (Critical/High/Medium/Low), finding rows with residual scores

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When `compensating-controls.md` is the richest file present, `/infographic` selects it as the data source in 100% of auto-detection runs
- **SC-002**: Residual severity distribution counts in the generated infographic spec exactly match the counts in the source `compensating-controls.md` (zero discrepancy)
- **SC-003**: All existing infographic outputs (generated from `risk-scores.md` or `threats.md`) remain byte-identical before and after this feature is implemented
- **SC-004**: Enhancement tips display the correct message for each of the three tiers, and no tip displays when an explicit path is used
- **SC-005**: A user with no prior tachi knowledge can discover the full pipeline sequence (threat-model, risk-score, compensating-controls) by following enhancement tips across three successive `/infographic` runs
- **SC-006**: Risk labels in generated infographic specs correctly distinguish "Residual Risk", "Inherent Risk", and "Severity" based on the detected data source

## Assumptions

- `compensating-controls.md` follows the schema defined in `schemas/compensating-controls.yaml`
- Residual scores use the same 0-10 scale and severity band thresholds (Critical: 9.0-10.0, High: 7.0-8.9, Medium: 4.0-6.9, Low: 0.0-3.9) as composite scores in `risk-scores.md`
- The Coverage Matrix in `compensating-controls.md` contains `Residual Score` and `Residual Severity Band` columns across its sub-tables
- The infographic agent operates under fresh context isolation (ADR-010) — all required data must be passed via the data source file(s)
- Both existing templates (baseball-card, system-architecture) can accommodate residual risk data with label and value changes only, without structural modifications

## Scope

### In Scope
- Three-tier auto-detection hierarchy (compensating-controls.md > risk-scores.md > threats.md)
- Residual risk data extraction from compensating-controls.md Coverage Matrix (4 sub-tables)
- Enhancement tips at each detection tier with suppression on explicit path
- Co-location enforcement (threats.md required with compensating-controls.md)
- Content-based type detection for explicit file paths
- Risk label distinction (Residual Risk / Inherent Risk / Severity)
- Risk reduction percentage in baseball-card summary zone
- Backward compatibility for all existing invocations

### Out of Scope
- New infographic templates specific to compensating controls
- Side-by-side inherent vs residual risk comparison view
- Control-specific visualization (individual control effectiveness charts)
- Interactive or HTML output formats
- Per-finding inherent-to-residual delta annotations
- Target risk tier (desired state after planned controls)

## Dependencies

- **PRD-039** (Standalone /infographic Command): Delivered — provides the command, auto-detection framework, template selection
- **PRD-036** (Compensating Controls): Delivered — provides `compensating-controls.md` output format
- **PRD-035** (Risk Scoring): Delivered — provides `risk-scores.md` (tier 2 data source)
- **ADR-010** (Fresh Context Isolation): Accepted — infographic agent runs in isolated context
- **ADR-014** (Spec-First / Gemini Optional): Accepted — markdown spec always generated, image is best-effort
