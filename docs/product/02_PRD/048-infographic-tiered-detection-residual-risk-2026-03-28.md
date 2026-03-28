---
prd:
  number: "048"
  topic: infographic-tiered-detection-residual-risk
  created: 2026-03-28
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "PRD authored by PM. Closes PRD-039 Open Question #1 — compensating-controls visualization."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED
    notes: "3-tier detection hierarchy sound. Section reference fixed to ## 2. Coverage Matrix. Detection/extraction failure modes properly distinguished."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "1-session timeline realistic for P0 scope. P1 risk labels are stretch goals. Monitor agent file size growth."
source:
  idea_id: 48
  story_id: null
---

# Infographic Tiered Pipeline Auto-Detection & Residual Risk — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-28
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Source**: GitHub Issue #48

---

## Executive Summary

### The One-Liner
Extend `/infographic` to auto-detect `compensating-controls.md` as the richest data source and visualize residual risk — the true security posture after accounting for existing defenses.

### Problem Statement
After running the full tachi pipeline (`/threat-model` → `/risk-score` → `/compensating-controls`), the `/infographic` command ignores `compensating-controls.md` entirely. It visualizes inherent risk from `risk-scores.md` even when residual risk data exists — meaning infographics show what the exposure *could be* rather than what it *actually is* after defenses are counted. Users who have invested in running the full pipeline get no visual benefit from the compensating controls analysis. Additionally, users at lower pipeline tiers have no guidance on what additional commands would produce richer visualizations.

### Proposed Solution
Add `compensating-controls.md` as the highest-priority tier in the `/infographic` auto-detection hierarchy (compensating-controls.md > risk-scores.md > threats.md). When detected, extract residual risk scores instead of inherent scores, producing infographics that reflect actual security posture. At each detection tier, display an enhancement tip informing users which pipeline command would upgrade their visualization to the next tier.

### Success Criteria
- When `compensating-controls.md` exists, infographics visualize residual risk (not inherent risk)
- Users at each tier see a clear tip about which command produces richer data
- The 3-tier detection hierarchy correctly prioritizes: compensating-controls.md > risk-scores.md > threats.md
- All existing infographic outputs (baseball-card, system-architecture) remain structurally identical

### Timeline
Single-phase implementation — estimated 1 session for P0 scope. P1 items (US-3: risk labels) are stretch goals within the same session, deferrable without re-planning.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature completes the visualization layer of tachi's composable pipeline. By surfacing residual risk — the most accurate measure of actual exposure — infographics become the definitive visual artifact for security posture communication. Enhancement tips at each tier create a natural discovery path through the pipeline, helping new users understand the full toolkit without reading documentation.

### Roadmap Fit
This was explicitly deferred as Open Question #1 in PRD-039 (Standalone /infographic Command): "Should `/infographic` also accept `compensating-controls.md` as a data source for residual risk visualization?" This PRD answers that question with a yes and defines the implementation scope. It builds on the foundation of three delivered features:
- PRD-018 (Threat Infographic Agent) — provides the visualization agent and templates
- PRD-035 (Quantitative Risk Scoring) — provides `risk-scores.md` with composite scores
- PRD-036 (Compensating Controls) — provides `compensating-controls.md` with residual risk

---

## Target Users & Personas

### Primary Persona: Security Analyst (Full Pipeline)
- **Role**: Security professional who runs the complete tachi pipeline
- **Experience**: Familiar with all pipeline stages, has run `/compensating-controls`
- **Goal**: Generate visual risk summaries that reflect actual security posture after controls
- **Pain Point**: Infographics show inherent risk even when residual risk data is available, misrepresenting the actual exposure

### Secondary Persona: Pipeline Learner
- **Role**: Developer adopting tachi, learning the pipeline incrementally
- **Experience**: Has run `/threat-model` but may not know about `/risk-score` or `/compensating-controls`
- **Goal**: Understand what additional pipeline steps exist and what value they add
- **Pain Point**: No discoverability — must read documentation to learn the full pipeline sequence

---

## User Stories

### US-1: Tiered Auto-Detection with Residual Risk
**As a** security analyst who has run the full tachi pipeline,
**I want** `/infographic` to auto-detect and visualize residual risk from `compensating-controls.md` (falling back to `risk-scores.md` then `threats.md`),
**So that** my infographics reflect actual security posture after accounting for existing defenses.

**Acceptance Criteria**:
- **Given** `compensating-controls.md`, `risk-scores.md`, and `threats.md` all exist in the output directory, **when** I run `/infographic`, **then** the command uses `compensating-controls.md` as the primary data source and visualizes residual risk scores
- **Given** only `risk-scores.md` and `threats.md` exist (no `compensating-controls.md`), **when** I run `/infographic`, **then** the command uses `risk-scores.md` as the primary data source (existing behavior)
- **Given** only `threats.md` exists, **when** I run `/infographic`, **then** the command uses `threats.md` as the data source (existing behavior)
- **Given** `compensating-controls.md` is the primary source, **when** the infographic is generated, **then** risk values shown are residual scores (not inherent composite scores)

**Priority**: P0
**Effort**: M

### US-2: Enhancement Tips at Each Tier
**As a** pipeline learner running `/infographic` for the first time,
**I want** to see what additional pipeline commands would produce richer visualizations,
**So that** I discover the full pipeline without reading the guide.

**Acceptance Criteria**:
- **Given** I run `/infographic` and `threats.md` is the detected source, **when** the command reports its data source, **then** it displays: "Tip: Run `/risk-score` to add quantitative risk scores to your infographic"
- **Given** I run `/infographic` and `risk-scores.md` is the detected source, **when** the command reports its data source, **then** it displays: "Tip: Run `/compensating-controls` to visualize residual risk (actual exposure after defenses)"
- **Given** I run `/infographic` and `compensating-controls.md` is the detected source, **when** the command reports its data source, **then** it displays: "Full pipeline detected — visualizing residual risk (richest data available)"
- **Given** I pass an explicit file path override, **when** the command runs, **then** no enhancement tip is displayed (explicit path = intentional choice)

**Priority**: P0
**Effort**: S

### US-3: Residual vs Inherent Risk Distinction in Output
**As a** security analyst reviewing an infographic,
**I want** the visual output to clearly indicate whether it shows inherent or residual risk,
**So that** I can communicate the correct risk posture to stakeholders.

**Acceptance Criteria**:
- **Given** the data source is `compensating-controls.md`, **when** the infographic spec is generated, **then** the risk label reads "Residual Risk" (not "Risk" or "Inherent Risk")
- **Given** the data source is `risk-scores.md`, **when** the infographic spec is generated, **then** the risk label reads "Inherent Risk"
- **Given** the data source is `threats.md`, **when** the infographic spec is generated, **then** the risk label reads "Severity" (existing behavior, qualitative)
- **Given** the data source is `compensating-controls.md`, **when** the baseball-card template is generated, **then** the donut chart shows residual severity distribution and the finding cards show residual scores

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### FR-1: Three-Tier Data Source Detection

**Updated Input Resolution Order** (when no explicit path provided):
1. Scan for `compensating-controls.md` — if found, use it (richest: residual risk)
2. Scan for `risk-scores.md` — if found, use it (quantitative inherent risk)
3. Scan for `threats.md` — if found, use it (qualitative severity)
4. If none found, exit with error listing expected file locations

**Data Source Type Detection** (when explicit path provided):
- **compensating-controls indicator**: Contains `## 2. Coverage Matrix` header AND table has `Residual Score` column
- **risk-scores indicator**: Contains `## 2. Scored Threat Table` header AND table has `Composite` column (existing)
- **threats indicator**: Contains `## 6. Risk Summary` with severity count labels (existing)

**Co-location Requirements**:
- When `compensating-controls.md` is primary: require co-located `threats.md` for structural/spatial data (same requirement as risk-scores.md)
- When `compensating-controls.md` is primary: `risk-scores.md` is NOT required (residual scores are self-contained in the controls file)

### FR-2: Data Extraction from compensating-controls.md

**Note**: The Coverage Matrix in `compensating-controls.md` uses 4 sub-tables grouped by residual severity band (Critical, High, Medium, Low), not a single flat table. Extraction must iterate across all sub-tables to collect the full finding set.

| Data Point | Extraction Source |
|-----------|------------------|
| Risk distribution | Residual severity band distribution (Critical/High/Medium/Low after controls) |
| Component risk | Residual score per finding, grouped by component |
| Top findings | Highest residual score findings (most exposed after controls) |
| Architecture overlay | Component + residual risk weight mapping |
| Control effectiveness | Total risk reduction percentage (for display in summary zone) |
| Metadata (project name, agent count) | Co-located `threats.md` Section 1 (same as risk-scores path) |
| Spatial data (trust zones, data flows) | Co-located `threats.md` Section 2 (same as risk-scores path) |

### FR-3: Enhancement Tips

Display a single-line tip in the command output after data source detection:

| Detected Source | Tip Message |
|----------------|-------------|
| `threats.md` | `💡 Tip: Run /risk-score to add quantitative risk scores to your infographic` |
| `risk-scores.md` | `💡 Tip: Run /compensating-controls to visualize residual risk (actual exposure after defenses)` |
| `compensating-controls.md` | `✅ Full pipeline — visualizing residual risk (richest data available)` |

Tips are suppressed when an explicit file path is provided.

### FR-4: Template Adaptations

Both existing templates (baseball-card, system-architecture) must support the new data source with minimal structural changes:

**Baseball Card Template**:
- Donut chart: show residual severity distribution (instead of inherent)
- Finding cards: show residual score and residual severity band
- Summary zone: add "Risk Reduction: X%" line showing overall control effectiveness
- Header: label as "Residual Risk" when sourced from compensating-controls.md

**System Architecture Template**:
- Component boxes: use residual risk weight for color intensity
- Finding legend: show residual severity bands
- Header: label as "Residual Risk" when sourced from compensating-controls.md

No new templates are introduced. The structural layout remains identical — only the data values and labels change.

---

## Non-Functional Requirements

### Performance
- No additional latency beyond current command execution (compensating-controls.md is similar size to risk-scores.md)
- Data extraction from compensating-controls.md: < 5 seconds
- Overall command execution: < 30 seconds (unchanged)

### Reliability
- **Detection-level failure**: If `compensating-controls.md` exists but lacks the `## 2. Coverage Matrix` header or `Residual Score` column, the tiered hierarchy naturally falls through to `risk-scores.md` (the file fails detection, not extraction)
- **Extraction-level failure**: If detection succeeds but data extraction encounters empty/malformed rows mid-extraction, the command should warn and halt (not silently fall through) to prevent infographics with misrepresented risk values
- All existing error handling for risk-scores.md and threats.md paths remains unchanged

### Compatibility
- Output spec structure (6 sections with YAML frontmatter) remains identical
- Existing template definitions are extended, not replaced
- Explicit file path override continues to work for all three source types
- Existing example outputs in `examples/` remain valid references

---

## Scope & Boundaries

### In Scope (P0 — Must Have)
- Three-tier auto-detection hierarchy: compensating-controls.md > risk-scores.md > threats.md
- Data extraction from compensating-controls.md for residual risk visualization
- Enhancement tips at each detection tier
- Co-location requirement for threats.md when compensating-controls.md is primary

### In Scope (P1 — Should Have)
- Risk label distinction (Residual Risk / Inherent Risk / Severity) in generated specs
- Risk reduction percentage display in baseball-card summary zone

### Out of Scope
- New infographic templates specific to compensating controls
- Side-by-side inherent vs residual risk comparison view
- Control-specific visualization (individual control effectiveness charts)
- Interactive or HTML output formats

### Assumptions
- `compensating-controls.md` follows the schema defined in `schemas/compensating-controls.yaml`
- Residual scores in `compensating-controls.md` use the same 0-10 scale as composite scores in `risk-scores.md`
- The Coverage Matrix table in `compensating-controls.md` contains `Residual Score` and `Residual Severity Band` columns

### Constraints
- **Fresh context isolation** (ADR-010): The infographic agent runs in isolated context — all needed data must be passed via the data source file(s)
- **Specification-first**: Markdown spec is the primary deliverable; Gemini image is best-effort
- **No breaking changes**: All existing `/infographic` invocations must continue to work identically

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: `compensating-controls.md` structure differs significantly from `risk-scores.md`, requiring complex extraction logic
- **Likelihood**: Low — both use markdown tables with numeric scores on the same 0-10 scale
- **Impact**: Medium (more implementation effort if table structure diverges)
- **Mitigation**: Schema validation via `schemas/compensating-controls.yaml` guarantees field presence

**Risk 2**: Residual risk values may cluster differently than inherent risk, producing less visually distinct infographics
- **Likelihood**: Medium — controls reduce risk, so residual scores trend lower and may cluster around Low/Medium
- **Impact**: Low (infographic is still accurate, just potentially less dramatic)
- **Mitigation**: No action needed — accurate representation is more valuable than visual impact

### Dependencies

**Internal Dependencies**:
- **PRD-039** (Standalone /infographic Command): Delivered — provides the command, auto-detection framework, and template selection
- **PRD-036** (Compensating Controls): Delivered — provides `compensating-controls.md` output format with residual risk fields
- **PRD-035** (Quantitative Risk Scoring): Delivered — provides `risk-scores.md` (tier 2 data source)
- **Infographic agent**: `.claude/agents/tachi/threat-infographic.md` — requires data extraction updates
- **Infographic command**: `.claude/commands/infographic.md` — requires detection hierarchy update

---

## Open Questions

- [ ] Should the explicit path override (`/infographic path/to/file.md`) also display enhancement tips for lower tiers? — PM — During implementation

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- PRD-039 (Standalone /infographic Command): [039-standalone-infographic-command-2026-03-28.md](039-standalone-infographic-command-2026-03-28.md)
- PRD-036 (Compensating Controls): [036-compensating-controls-2026-03-27.md](036-compensating-controls-2026-03-27.md)
- PRD-035 (Quantitative Risk Scoring): [035-quantitative-risk-scoring-2026-03-27.md](035-quantitative-risk-scoring-2026-03-27.md)
- PRD-018 (Threat Infographic Agent): [018-threat-infographic-agent-2026-03-23.md](018-threat-infographic-agent-2026-03-23.md)

### Technical Documentation
- Constitution: [constitution.md](../../../.aod/memory/constitution.md)
- Infographic Command: `.claude/commands/infographic.md`
- Infographic Agent: `.claude/agents/tachi/threat-infographic.md`
- Compensating Controls Schema: `schemas/compensating-controls.yaml`
- Templates: `.claude/agents/tachi/templates/infographic-baseball-card.md`, `.claude/agents/tachi/templates/infographic-system-architecture.md`

### Source
- GitHub Issue: #48 — Enhance /infographic with tiered pipeline auto-detection and residual risk support
- PRD-039 Open Question #1: Deferred compensating-controls visualization
