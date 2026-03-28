---
prd_reference: docs/product/02_PRD/039-standalone-infographic-command-2026-03-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 5 PRD user stories fully covered with correct priorities. 14 atomic FRs with clean traceability. No scope creep. All success criteria measurable and technology-agnostic."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Standalone /infographic Command

**Feature Branch**: `039-standalone-infographic-command`
**Created**: 2026-03-28
**Status**: Approved
**PRD Reference**: `docs/product/02_PRD/039-standalone-infographic-command-2026-03-28.md`

## User Scenarios & Testing

### User Story 1 - Auto-Detect Richest Data Source (Priority: P0)

A security analyst has completed threat analysis and risk scoring on an agentic AI application. They want to generate visual risk diagrams that reflect the most accurate data available without needing to remember which file to specify.

**Why this priority**: This is the core value proposition — users get the best possible visualization automatically. Without auto-detection, users must understand the internal data model to choose the right input, which defeats the purpose of a standalone command.

**Independent Test**: Can be fully tested by placing `threats.md` and/or `risk-scores.md` in a directory and running `/infographic` without arguments. Delivers value by producing the most accurate infographic possible from available data.

**Acceptance Scenarios**:

1. **Given** both `threats.md` and `risk-scores.md` exist in the output directory, **When** the user runs `/infographic`, **Then** the command uses `risk-scores.md` as the primary data source and reads co-located `threats.md` for structural data (project metadata, trust zones, data flows)
2. **Given** only `threats.md` exists in the output directory, **When** the user runs `/infographic`, **Then** the command uses `threats.md` as the sole data source
3. **Given** neither `threats.md` nor `risk-scores.md` exists in the specified directory, **When** the user runs `/infographic`, **Then** the command exits with a clear error message listing the expected file names and paths
4. **Given** `risk-scores.md` exists but co-located `threats.md` does not, **When** the user runs `/infographic`, **Then** the command exits with an error explaining that `threats.md` is required alongside `risk-scores.md` for structural data

---

### User Story 2 - Explicit Data Source Override (Priority: P0)

A security analyst wants to generate diagrams from a specific file — perhaps an older `threats.md` from a previous analysis run, or a `risk-scores.md` from a different output directory.

**Why this priority**: Explicit override gives users full control and supports advanced workflows where auto-detection would choose the wrong file.

**Independent Test**: Can be fully tested by passing an explicit file path argument and verifying the command uses that specific file regardless of what other files exist in the directory.

**Acceptance Scenarios**:

1. **Given** the user runs `/infographic path/to/threats.md`, **When** the file exists, **Then** the command uses that specific file as the data source
2. **Given** the user runs `/infographic path/to/risk-scores.md`, **When** the file exists, **Then** the command uses that file as primary source and reads co-located `threats.md` for structural data
3. **Given** the user passes a file path that does not exist, **When** the command runs, **Then** it exits with a clear error message stating the file was not found

---

### User Story 3 - Template Selection (Priority: P0)

A security analyst wants to generate only a specific type of visual diagram — either the executive-focused baseball card or the technical system architecture view — rather than both.

**Why this priority**: Template selection enables targeted output for specific audiences (executives vs. engineers) and avoids generating unnecessary artifacts.

**Independent Test**: Can be fully tested by running `/infographic --template baseball-card` and verifying only the baseball card output is produced.

**Acceptance Scenarios**:

1. **Given** the user runs `/infographic --template baseball-card`, **When** execution completes, **Then** only the baseball-card specification and optional image are generated
2. **Given** the user runs `/infographic --template system-architecture`, **When** execution completes, **Then** only the system-architecture specification and optional image are generated
3. **Given** the user runs `/infographic --template all` or omits the `--template` flag, **When** execution completes, **Then** both templates are generated
4. **Given** the user passes an unrecognized template name, **When** the command runs, **Then** it exits with an error listing valid template names: `baseball-card`, `system-architecture`, `all`

---

### User Story 4 - Regenerate After Enrichment (Priority: P1)

A security analyst has already run `/threat-model` and later enriched the analysis with `/risk-score` or `/compensating-controls`. They want to regenerate infographics so the visuals reflect the updated, richer data.

**Why this priority**: This is the key workflow improvement — users can now regenerate diagrams at any point rather than being locked to the initial pipeline run. However, it depends on the auto-detection and override capabilities from US-1 and US-2.

**Independent Test**: Can be tested by generating infographics before and after running `/risk-score`, then comparing the output to verify quantitative scores replace qualitative severity counts.

**Acceptance Scenarios**:

1. **Given** `risk-scores.md` was generated after `threats.md`, **When** the user runs `/infographic`, **Then** the output reflects quantitative composite scores from risk scoring rather than qualitative severity counts
2. **Given** infographics were previously generated, **When** the user runs `/infographic` again, **Then** the new outputs overwrite the previous specification and image files in the same directory

---

### User Story 5 - Pipeline Cleanup (Priority: P0)

The `/threat-model` pipeline currently includes Phase 6 (infographic generation), which duplicates the standalone command's functionality and forces infographics to use only qualitative data. Phase 6 must be removed to complete the decoupling.

**Why this priority**: Without removing Phase 6, users face confusing duplication — infographics generated in two places with different data quality. This is a prerequisite for clean adoption of the standalone command.

**Independent Test**: Can be tested by running `/threat-model` on an architecture file and verifying the pipeline produces only phases 1-5 output (no infographic spec or image files).

**Acceptance Scenarios**:

1. **Given** the user runs `/threat-model` on an architecture file, **When** the pipeline completes, **Then** it produces phases 1-5 only — no infographic specification or image files are generated
2. **Given** the `/threat-model` command previously accepted `--infographic-template` and `--skip-infographic` flags, **When** these flags are removed, **Then** the command no longer recognizes or documents them
3. **Given** existing documentation and platform adapters reference Phase 6, **When** the pipeline is updated, **Then** all documentation and adapters reflect the 5-phase pipeline
4. **Given** the `/threat-model` pipeline completes, **When** the summary is displayed, **Then** it includes a hint directing users to run `/infographic` for visual risk diagrams

---

### Edge Cases

- What happens when `risk-scores.md` exists but `threats.md` is missing? The command must error because `risk-scores.md` lacks structural data needed for infographic generation.
- What happens when input files exist but are malformed or empty? The command should exit with a clear error describing the expected file structure.
- What happens when `GEMINI_API_KEY` is unavailable? The specification file is always generated; image generation is skipped with an informational message.
- What happens when the Gemini API returns a rate limit, timeout, or content policy rejection? The specification is saved as the deliverable; the error is logged but does not block the command.
- What happens when the `corporate-white` template alias is used? It should resolve to `baseball-card` (preserving backward compatibility).

## Requirements

### Functional Requirements

- **FR-001**: The system MUST auto-detect the richest available data source when no explicit path is provided, preferring `risk-scores.md` over `threats.md`
- **FR-002**: The system MUST accept an explicit file path argument to override auto-detection
- **FR-003**: The system MUST support template selection via `--template` flag with values: `baseball-card`, `system-architecture`, `all` (default: `all`)
- **FR-004**: The system MUST extract quantitative composite scores from `risk-scores.md` when it is the primary data source, replacing qualitative severity counts
- **FR-005**: The system MUST read co-located `threats.md` for structural and spatial data (project metadata, trust zones, component relationships, data flows) when `risk-scores.md` is the primary source
- **FR-006**: The system MUST error with a clear message when `risk-scores.md` is selected but co-located `threats.md` is not found
- **FR-007**: The system MUST generate a markdown specification file (`threat-{template-name}-spec.md`) for each selected template — this is the primary deliverable
- **FR-008**: The system MUST attempt image generation via Gemini API when the API key is available, with graceful degradation on failure
- **FR-009**: The `/threat-model` pipeline MUST be updated to remove Phase 6 (infographic generation), producing only phases 1-5
- **FR-010**: The `/threat-model` pipeline MUST remove the `--infographic-template` flag, the `--skip-infographic` flag, and the `TACHI_SKIP_INFOGRAPHIC` environment variable
- **FR-011**: The `/threat-model` pipeline MUST display a post-completion hint directing users to `/infographic`
- **FR-012**: All platform adapter files MUST be updated to reflect the 5-phase pipeline (removing Phase 6 references)
- **FR-013**: The `corporate-white` template alias MUST resolve to `baseball-card` for backward compatibility
- **FR-014**: Re-running `/infographic` MUST overwrite previous output files in the same directory (idempotent behavior)

### Key Entities

- **Data Source**: The input file used for infographic generation — either `threats.md` (qualitative severity counts + structural data) or `risk-scores.md` (quantitative composite scores, requires co-located `threats.md` for structural data)
- **Template**: A visual layout specification defining the infographic structure — `baseball-card` (executive-focused, dark theme, 4-zone layout) or `system-architecture` (technical-focused, white theme, zone-stacked architecture)
- **Infographic Specification**: The primary markdown output file containing structured data for rendering — metadata, risk distribution, coverage heat map, top findings, architecture overlay, and visual design directives
- **Infographic Image**: The optional JPEG output generated via Gemini API from the specification — best-effort, not guaranteed

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can generate infographics at any point in the workflow — not just during `/threat-model` execution
- **SC-002**: When `risk-scores.md` exists, infographic risk distribution values reflect quantitative composite scores rather than qualitative severity counts
- **SC-003**: The `/threat-model` pipeline completes without generating infographic files (phases 1-5 only)
- **SC-004**: Specification generation completes in under 30 seconds regardless of data source
- **SC-005**: All existing template outputs (baseball-card, system-architecture) remain structurally identical — same 6 sections, same schema version
- **SC-006**: The command produces a usable specification even when Gemini API is unavailable or fails
- **SC-007**: Users who previously relied on Phase 6 can achieve the same result by running `/infographic` as a follow-up command

### Assumptions

- The existing infographic agent prompt and templates are reusable; the agent requires enhancement for dual-path data extraction but not a rewrite
- The infographic specification format (6 sections with YAML frontmatter) remains unchanged
- `risk-scores.md` does not contain structural/spatial data; co-located `threats.md` is always required when `risk-scores.md` is the primary source
- The Gemini API integration pattern (key detection, model selection, graceful degradation) remains unchanged
- Example outputs in `examples/` remain valid references and do not require regeneration
