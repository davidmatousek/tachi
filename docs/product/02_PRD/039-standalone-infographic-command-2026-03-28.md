---
prd:
  number: "039"
  topic: standalone-infographic-command
  created: 2026-03-28
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "PRD authored by PM. Aligns with product vision — composable pipeline tools."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Dual-path extraction needed for risk-scores.md. Co-located threats.md required for structural data. Concerns addressed in PRD revision."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Timeline realistic at 1-2 sessions. US-5 elevated to P0. Platform adapter cleanup added. Concerns addressed in PRD revision."
source:
  idea_id: 39
  story_id: null
---

# Standalone /infographic Command — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-28
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Source**: GitHub Issue #39

---

## Executive Summary

### The One-Liner
A standalone `/infographic` command that generates visual risk diagrams from the richest available threat data, independent of the `/threat-model` pipeline.

### Problem Statement
Infographic generation is currently locked inside Phase 6 of the `/threat-model` pipeline, which creates two problems: (1) diagrams always use qualitative severity counts from `threats.md` because Phase 6 runs before `/risk-score`, meaning visualizations never reflect quantitative composite scores; and (2) as new pipeline components are added (e.g., compensating controls), the fixed ordering becomes increasingly rigid — users cannot regenerate diagrams after enriching their data.

### Proposed Solution
Extract infographic generation into a standalone `/infographic` command that accepts either `threats.md` or `risk-scores.md` as input, auto-selects the richest available data source when both exist, and supports all existing templates (baseball-card, system-architecture, all). Remove Phase 6 from the `/threat-model` pipeline to eliminate duplication.

### Success Criteria
- Users can generate infographics at any point in the workflow, not just during `/threat-model`
- When `risk-scores.md` exists, infographics reflect quantitative composite scores instead of qualitative severity counts
- The `/threat-model` pipeline no longer includes infographic generation (Phase 6 removed)
- All existing template outputs (baseball-card, system-architecture) remain identical in structure

### Timeline
Single-phase implementation — estimated 1-2 sessions.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature directly supports tachi's vision as "the default threat modeling toolkit" by making the visualization layer composable and flexible. Decoupling visualization from analysis follows the Unix philosophy of small, composable tools — a principle that resonates with tachi's target audience of developers building AI agents.

### Roadmap Fit
This is a natural evolution of PRD-018 (Threat Infographic Agent, delivered 2026-03-23) and builds on PRD-035 (Quantitative Risk Scoring, delivered 2026-03-27). The standalone command closes the gap between these two delivered features by letting infographics consume the richer data that risk scoring produces.

---

## Target Users & Personas

### Primary Persona: Security Analyst
- **Role**: Security professional running threat models on agentic AI applications
- **Experience**: Familiar with tachi pipeline, runs `/threat-model` → `/risk-score` → `/compensating-controls`
- **Goal**: Generate accurate visual risk summaries that reflect the most complete analysis available
- **Pain Point**: Must re-run the entire `/threat-model` pipeline to regenerate diagrams, and even then diagrams don't use quantitative scores

### Secondary Persona: Template Adopter
- **Role**: Developer adopting tachi for a new project, learning the pipeline
- **Experience**: New to tachi, may not understand which file to pass as input
- **Goal**: Generate useful visual outputs without memorizing pipeline internals
- **Pain Point**: Must understand the relationship between `threats.md` and `risk-scores.md` to choose the right input

---

## User Stories

### US-1: Auto-Select Richest Data Source
**When** I have completed threat analysis and optionally risk scoring,
**I want to** run `/infographic` and have it automatically choose the best available data source,
**So I can** get the most accurate visual risk picture without remembering which file to pass.

**Acceptance Criteria**:
- **Given** both `threats.md` and `risk-scores.md` exist in the output directory, **when** I run `/infographic`, **then** the command uses `risk-scores.md` as the data source
- **Given** only `threats.md` exists in the output directory, **when** I run `/infographic`, **then** the command uses `threats.md` as the data source
- **Given** neither file exists in the specified directory, **when** I run `/infographic`, **then** the command exits with a clear error message listing expected file paths

**Priority**: P0
**Effort**: M

### US-2: Explicit Data Source Override
**When** I want to generate diagrams from a specific data source regardless of what files exist,
**I want to** pass an explicit file path to `/infographic`,
**So I can** control exactly which data is visualized.

**Acceptance Criteria**:
- **Given** I run `/infographic path/to/threats.md`, **when** the file exists, **then** the command uses that specific file as the data source
- **Given** I run `/infographic path/to/risk-scores.md`, **when** the file exists, **then** the command uses that specific file as the data source
- **Given** I pass a file that does not exist, **when** the command runs, **then** it exits with a clear error message

**Priority**: P0
**Effort**: S

### US-3: Template Selection
**When** I want to generate a specific type of visual diagram,
**I want to** select which template(s) to generate,
**So I can** produce exactly the output I need.

**Acceptance Criteria**:
- **Given** I run `/infographic --template baseball-card`, **when** execution completes, **then** only the baseball-card spec and optional image are generated
- **Given** I run `/infographic --template system-architecture`, **when** execution completes, **then** only the system-architecture spec and optional image are generated
- **Given** I run `/infographic --template all` (or omit --template), **when** execution completes, **then** both templates are generated
- **Given** I pass an unrecognized template name, **when** the command runs, **then** it exits with an error listing valid template names

**Priority**: P0
**Effort**: S

### US-4: Regenerate After Enrichment
**When** I have run `/compensating-controls` or `/risk-score` after my initial threat model,
**I want to** regenerate infographics to reflect the updated analysis,
**So I can** present visuals that show residual risk rather than inherent risk.

**Acceptance Criteria**:
- **Given** `risk-scores.md` was generated after `threats.md`, **when** I run `/infographic`, **then** the output reflects quantitative composite scores from risk scoring
- **Given** I previously generated infographics during `/threat-model`, **when** I run `/infographic` again, **then** the new outputs overwrite the previous spec and image files in the same directory

**Priority**: P1
**Effort**: M

### US-5: Pipeline Cleanup
**When** I run `/threat-model`,
**I want to** the pipeline to no longer include Phase 6 (infographic generation),
**So I can** use the decoupled `/infographic` command at the right point in my workflow.

**Acceptance Criteria**:
- **Given** I run `/threat-model` on an architecture file, **when** the pipeline completes, **then** it produces phases 1-5 only (no infographic spec or image files)
- **Given** `/threat-model` previously accepted `--infographic-template` and `--skip-infographic` flags, **when** these flags are removed, **then** the command help/documentation no longer references them
- **Given** the existing `/threat-model` usage examples reference Phase 6, **when** the command is updated, **then** all documentation reflects the 5-phase pipeline
- **Given** platform adapter files (Copilot, Cursor, generic) reference Phase 6, **when** the pipeline is updated, **then** all adapter documentation reflects the 5-phase pipeline

**Priority**: P0
**Effort**: M

---

## Functional Requirements

### FR-1: Data Source Detection and Selection

**Input Resolution Order** (when no explicit path provided):
1. Scan current working directory for `risk-scores.md` — if found, use it (richest data)
2. Scan current working directory for `threats.md` — if found, use it (fallback)
3. If neither found, exit with error listing expected file locations

**Input Resolution** (when explicit path provided):
1. Validate file exists at provided path
2. Detect file type from content (threats.md vs risk-scores.md) based on section structure
3. Use detected file as data source

**Data Extraction by Source Type**:

| Data Point | From threats.md | From risk-scores.md |
|-----------|-----------------|---------------------|
| Risk distribution | Section 6 severity counts (Critical/High/Medium/Low) | Composite score distribution bands |
| Component risk | Finding count per component | Weighted composite score per component |
| Top findings | Highest severity findings | Highest composite score findings |
| Architecture overlay | Component + severity mapping | Component + quantitative risk weight |
| Metadata (project name, agent count) | Section 1 (System Overview) | **Not available** — requires co-located threats.md |
| Spatial data (trust zones, data flows) | Section 2 (Trust Boundaries) | **Not available** — requires co-located threats.md |

**Dual-Source Strategy**: When `risk-scores.md` is the primary data source, the command MUST also read co-located `threats.md` for structural/spatial data not present in risk scores (project metadata, trust zones, component relationships, data flows). The quantitative scores from `risk-scores.md` replace qualitative severity counts; the structural skeleton comes from `threats.md`.

### FR-2: Template Generation

Extend existing infographic agent with dual-path data extraction (threats.md path and risk-scores.md path):
- **baseball-card**: Dark navy theme, 4-zone layout (donut chart, heat map, finding cards, architecture strip)
- **system-architecture**: White theme, zone-stacked architecture with component boxes, data flows, finding legend
- **all** (default): Generate both templates sequentially

Output files per template:
- `threat-{template-name}-spec.md` — structured specification (always generated)
- `threat-{template-name}.jpg` — Gemini API image (best-effort, graceful degradation)

### FR-3: Gemini API Image Generation

Identical behavior to current Phase 6 implementation:
- Check `GEMINI_API_KEY` env var, then `.env` file
- If unavailable: save spec as standalone deliverable, log info message
- Graceful degradation for rate limits, timeouts, content policy rejections
- No pipeline blocking on image generation failure

### FR-4: /threat-model Pipeline Update

- Remove Phase 6 (Infographic) from the pipeline
- Remove `--infographic-template` flag
- Remove `--skip-infographic` flag and `TACHI_SKIP_INFOGRAPHIC` env var
- Update pipeline summary output to reference 5 phases
- Add post-pipeline hint: "Run `/infographic` to generate visual risk diagrams"

---

## Non-Functional Requirements

### Performance
- Command execution (spec generation): < 30 seconds
- Gemini API image generation: < 60 seconds timeout (existing behavior)
- No degradation from current Phase 6 performance

### Reliability
- Graceful degradation: spec always saved even if image generation fails
- Input validation: clear error messages for missing/malformed input files
- Idempotent: re-running overwrites previous output cleanly

### Compatibility
- Output format: identical spec structure to current Phase 6 output
- Template files: no changes to existing template definitions
- Gemini API integration: no changes to API interaction pattern
- Existing example outputs in `examples/` remain valid references

---

## Scope & Boundaries

### In Scope (P0 — Must Have)
- Standalone `/infographic` command with auto-detection of richest data source
- Explicit file path override for manual data source selection
- Template selection (`--template baseball-card|system-architecture|all`)
- Dual-path data extraction in infographic agent (threats.md path + risk-scores.md path with co-located threats.md for structural data)
- Remove Phase 6 from `/threat-model` pipeline (including platform adapter updates)
- Update `/threat-model` documentation to reflect 5-phase pipeline

### In Scope (P1 — Should Have)
- Post-pipeline hint in `/threat-model` output suggesting `/infographic`

### Out of Scope
- New infographic templates (future feature)
- Compensating controls visualization (future feature — would require new data extraction logic)
- Interactive/HTML infographic output (different output format entirely)

### Assumptions
- The infographic agent's existing template files are reusable; the agent prompt requires dual-path extraction logic for risk-scores.md input
- The spec output format (6 sections with YAML frontmatter) remains unchanged
- `risk-scores.md` does NOT contain structural/spatial data (project metadata, trust zones, data flows); co-located `threats.md` is required when risk-scores.md is the primary source

### Constraints
- **Fresh context isolation** (ADR-010): The infographic agent must run in isolated context with only the selected data source file as input
- **Specification-first**: The markdown spec is the primary deliverable; Gemini image is best-effort
- **Platform neutral**: Command must work with any LLM, not IDE-specific

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: `risk-scores.md` does not contain structural/spatial data needed for spec generation
- **Likelihood**: Confirmed — `risk-scores.md` lacks project metadata, trust zone data, and component relationship mapping
- **Impact**: Medium (system-architecture template requires spatial data for zone layout)
- **Mitigation**: Dual-source strategy — use `risk-scores.md` for quantitative scores, co-located `threats.md` for structural skeleton. Error if `threats.md` not co-located when `risk-scores.md` is primary source

**Risk 2**: Removing Phase 6 from `/threat-model` may break existing user workflows
- **Likelihood**: Medium (users who relied on automatic infographic generation)
- **Impact**: Low (users can run `/infographic` as a follow-up command)
- **Mitigation**: Add clear post-pipeline hint directing users to `/infographic`

### Dependencies

**Internal Dependencies**:
- **PRD-018** (Threat Infographic Agent): Delivered — provides the agent, templates, and spec format
- **PRD-035** (Quantitative Risk Scoring): Delivered — provides `risk-scores.md` output format
- **Infographic templates**: `.claude/agents/tachi/templates/infographic-*.md` must remain stable

---

## Open Questions

- [ ] Should `/infographic` also accept `compensating-controls.md` as a data source for residual risk visualization? — PM — Deferred to future feature
- [ ] Should the `corporate-white` alias be preserved or deprecated in the standalone command? — Architect — During implementation

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- PRD-018 (Threat Infographic Agent): [018-threat-infographic-agent-2026-03-23.md](018-threat-infographic-agent-2026-03-23.md)
- PRD-035 (Quantitative Risk Scoring): [035-quantitative-risk-scoring-2026-03-27.md](035-quantitative-risk-scoring-2026-03-27.md)

### Technical Documentation
- Constitution: [constitution.md](../../../.aod/memory/constitution.md)
- Infographic Agent: `.claude/agents/tachi/threat-infographic.md`
- Templates: `.claude/agents/tachi/templates/infographic-baseball-card.md`, `.claude/agents/tachi/templates/infographic-system-architecture.md`
- Schema: `schemas/infographic.yaml`

### Source
- GitHub Issue: #39 — Standalone /infographic command
