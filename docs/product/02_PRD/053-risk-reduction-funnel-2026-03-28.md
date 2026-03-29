---
prd:
  number: "053"
  topic: risk-reduction-funnel
  created: 2026-03-28
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "PRD authored by PM. New infographic template extends proven template pattern — no architectural changes."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Schema v1.1 bump needed for template-dependent section requirements. Tier 2 data path from compensating-controls.md needs clarification. Both addressable in plan.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "1-session timeline realistic (105-130 min). Include P1 in session — incremental cost far less than separate session overhead. Gemini 3D quality is acknowledged best-effort."
source:
  idea_id: 53
  story_id: null
---

# Risk Reduction Funnel Infographic Template — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-28
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Source**: GitHub Issue #53

---

## Executive Summary

### The One-Liner
Add a new `/infographic --template risk-funnel` that visualizes the narrowing pipeline from threats identified through inherent risk scoring, control application, to residual risk as a photorealistic 3D funnel.

### Problem Statement
After running the full tachi pipeline (`/threat-model` → `/risk-score` → `/compensating-controls`), users have two infographic templates: a dashboard summary (baseball-card) and an annotated architecture diagram (system-architecture). Neither communicates the **risk reduction narrative** — the story of how raw threat volume narrows through each pipeline stage into manageable residual risk. Stakeholders (CISOs, board members, auditors) frequently ask "what did we start with, what did we do about it, and where do we stand now?" No commercial threat modeling tool provides this visualization. Users must manually assemble this narrative from separate artifacts.

### Proposed Solution
Add a `risk-funnel` template to the existing infographic system. The funnel renders 4 tiers top-to-bottom, each narrower than the last, representing the progressive risk reduction pipeline:

1. **Threats Identified** (widest) — Total findings from threat model
2. **Inherent Risk Scored** — Quantitative severity distribution after risk scoring
3. **Controls Applied** — Coverage and mitigation from compensating controls analysis
4. **Residual Risk** (narrowest) — Remaining exposure after defenses

The template follows the established pattern in `.claude/agents/tachi/templates/` and uses the existing 3-tier data source auto-detection. Graceful degradation determines how many funnel tiers render: `compensating-controls.md` enables all 4 tiers, `risk-scores.md` enables 3 tiers, and `threats.md` enables 1 tier.

### Success Criteria
- Running `/infographic --template risk-funnel` produces a 4-tier funnel spec when `compensating-controls.md` is the detected data source
- Graceful degradation: 3-tier funnel from `risk-scores.md`, 1-tier summary from `threats.md`
- The funnel visually narrows from top to bottom, communicating risk reduction at a glance
- Template follows the exact pattern of existing templates (infographic-baseball-card.md, infographic-system-architecture.md)
- Gemini image generation produces a photorealistic 3D funnel when GEMINI_API_KEY is available

### Timeline
Single-phase implementation — estimated 1 session. Template authoring is the primary deliverable; agent and command updates are minimal (adding template to registry).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature extends tachi's visualization layer with a narrative-focused template that communicates risk reduction — the core value proposition of running the full pipeline. While baseball-card and system-architecture templates answer "what is the current risk posture?", the risk-funnel answers "how did we get here and how much risk did we eliminate?" This is the story stakeholders need for budget justification and compliance reporting.

### Roadmap Fit
Builds on three delivered foundations:
- **PRD-039** (Standalone /infographic Command) — template selection via `--template`, auto-detection, Gemini pipeline
- **PRD-048** (Infographic Tiered Detection & Residual Risk) — 3-tier auto-detection hierarchy, residual risk data extraction
- **PRD-018** (Threat Infographic Agent) — agent architecture, spec generation, image pipeline

The template pattern is proven and extensible. This PRD adds a new template file and registers it — no architectural changes required.

### Market Differentiation
No commercial threat modeling tool (Iriusrisk, ThreatModeler, OWASP Threat Dragon, Microsoft TMT) provides a risk reduction funnel visualization. This is a confirmed market gap. The funnel metaphor is universally understood by non-technical stakeholders, making it tachi's strongest executive communication artifact.

---

## Target Users & Personas

### Primary Persona: Security Leader (CISO / VP Security)
- **Role**: Executive responsible for security posture reporting to board and auditors
- **Experience**: Non-technical; needs visual narratives, not raw data
- **Goal**: One image that tells the story: "We found X threats, scored them, applied controls, and reduced risk to Y"
- **Pain Point**: Must manually assemble this narrative from separate pipeline outputs across multiple artifacts

### Secondary Persona: Security Analyst (Full Pipeline User)
- **Role**: Security professional who runs the complete tachi pipeline
- **Experience**: Technical; familiar with all pipeline stages
- **Goal**: Generate executive-ready artifact that justifies the work done across the pipeline
- **Pain Point**: Existing templates show current state but not the improvement journey

### Tertiary Persona: Compliance Auditor
- **Role**: External or internal auditor reviewing security posture
- **Experience**: Process-oriented; needs evidence of systematic risk reduction
- **Goal**: Visual evidence that threats were identified, assessed, mitigated, and residual risk quantified
- **Pain Point**: No single artifact demonstrates the end-to-end risk management process

---

## User Stories

### US-1: Full Pipeline Funnel (4 Tiers)
**As a** security leader who has run the full tachi pipeline,
**I want** `/infographic --template risk-funnel` to render a 4-tier funnel showing threats identified → inherent risk scored → controls applied → residual risk,
**So that** I can present a single image to stakeholders showing our complete risk reduction journey.

**Acceptance Criteria**:
- **Given** `compensating-controls.md`, `risk-scores.md`, and `threats.md` all exist in the output directory, **when** I run `/infographic --template risk-funnel`, **then** the spec contains 4 funnel tiers with progressively narrowing widths
- **Given** the data source is `compensating-controls.md`, **when** the funnel is generated, **then** Tier 1 shows total threat count, Tier 2 shows inherent severity distribution, Tier 3 shows control coverage percentage and mitigation counts, and Tier 4 shows residual severity distribution
- **Given** the funnel is generated, **when** I compare Tier 1 width to Tier 4 width, **then** Tier 4 is visually narrower, representing risk reduction
- **Given** GEMINI_API_KEY is available, **when** the spec is generated, **then** a photorealistic 3D funnel image is produced alongside the spec

**Priority**: P0
**Effort**: L

### US-2: Partial Pipeline Funnel (3 Tiers)
**As a** security analyst who has run `/threat-model` and `/risk-score` but not `/compensating-controls`,
**I want** the risk funnel to show 3 populated tiers with the 4th tier indicated as "not yet available",
**So that** I get a useful visualization and a clear signal to run `/compensating-controls` for the full picture.

**Acceptance Criteria**:
- **Given** `risk-scores.md` and `threats.md` exist but `compensating-controls.md` does not, **when** I run `/infographic --template risk-funnel`, **then** the spec renders 3 solid tiers (Threats Identified, Inherent Risk Scored, and a combined "Unmitigated Risk" summary) with the 4th tier shown as a dashed outline labeled "Run /compensating-controls to complete the funnel"
- **Given** 3-tier mode, **when** the funnel is rendered, **then** the bottom tier uses inherent risk data (same as Tier 2 severity distribution) since no control reduction has been applied
- **Given** 3-tier mode, **when** the enhancement tip is displayed, **then** it reads: "Run `/compensating-controls` to unlock the full 4-tier risk reduction funnel"

**Priority**: P0
**Effort**: M

### US-3: Minimal Pipeline Funnel (1 Tier)
**As a** developer who has run only `/threat-model`,
**I want** the risk funnel to show a single-tier summary with guidance toward the full funnel,
**So that** I understand my starting point and the pipeline path ahead.

**Acceptance Criteria**:
- **Given** only `threats.md` exists, **when** I run `/infographic --template risk-funnel`, **then** the spec renders a single wide tier showing total threat count and qualitative severity distribution
- **Given** 1-tier mode, **when** the tier is rendered, **then** below it are 3 grayed-out/dashed tiers labeled with the pipeline commands needed to unlock them
- **Given** 1-tier mode, **when** the enhancement tip is displayed, **then** it reads: "Run `/risk-score` to begin quantifying your risk reduction funnel"

**Priority**: P0
**Effort**: S

### US-4: Funnel Metrics Sidebar
**As a** security leader presenting to stakeholders,
**I want** key metrics displayed alongside the funnel (total threats, risk reduction %, control coverage %),
**So that** the numbers reinforce the visual narrative without requiring separate data lookup.

**Acceptance Criteria**:
- **Given** 4-tier mode (compensating-controls source), **when** the funnel spec is generated, **then** a metrics sidebar shows: Total Findings, Risk Reduction %, Control Coverage %, and severity breakdown per tier
- **Given** 3-tier mode, **when** the sidebar is generated, **then** metrics show: Total Findings, severity distribution, and "Risk Reduction: N/A — run /compensating-controls"
- **Given** 1-tier mode, **when** the sidebar is generated, **then** metrics show: Total Findings and qualitative severity counts only

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### FR-1: Template File

Create `.claude/agents/tachi/templates/infographic-risk-funnel.md` following the established template pattern:
- Frontmatter comment with purpose statement
- ASCII layout diagram showing funnel zones
- Style table (dark theme, 16:9 landscape)
- Color palette (consistent with existing templates: Critical=#DC2626, High=#EA580C, Medium=#CA8A04, Low=#2563EB)
- Typography table
- Zone specifications for each funnel tier
- Gemini Prompt Template section with all placeholders
- Gemini API configuration (same as existing templates)
- Accessibility section

### FR-2: Funnel Layout Design

**Layout**: Vertical funnel, 16:9 landscape orientation (1920x1080 minimum)

| Zone | Height | Content |
|------|--------|---------|
| Header | 8% | Title: "Risk Reduction Funnel", subtitle: project name + date |
| Funnel | 62% | 4 trapezoid tiers, widest at top, narrowest at bottom |
| Metrics Sidebar | — | Right-aligned panel overlapping funnel zone (20% width) |
| Tier Labels | — | Left-aligned labels for each tier with stage name |
| Footer | 5% | Attribution line |

**Funnel Tier Specifications**:

| Tier | Label | Width | Data Source | Content |
|------|-------|-------|-------------|---------|
| 1 (top) | Threats Identified | 100% | threats.md Section 6 | Total finding count, qualitative severity distribution |
| 2 | Inherent Risk Scored | ~75% | risk-scores.md Section 2 | Composite score distribution, severity counts |
| 3 | Controls Applied | ~50% | compensating-controls.md Section 1 | Control coverage %, findings with controls, mitigation stats |
| 4 (bottom) | Residual Risk | ~30% | compensating-controls.md Section 2 | Residual severity distribution, residual score range |

**Width Proportionality**: Tier widths are proportional to the finding count or risk volume at each stage. The percentages above are defaults; actual widths derive from data. The narrowing MUST be visually apparent — if risk reduction is minimal, the funnel still narrows (minimum 10% reduction per tier) to maintain the visual metaphor.

**Tier Connectors**: Gradient transitions between tiers (not hard edges) to convey the flowing pipeline narrative.

### FR-3: Graceful Degradation

| Data Source | Tiers Rendered | Behavior |
|-------------|---------------|----------|
| `compensating-controls.md` | 4 (full funnel) | All tiers solid with data |
| `risk-scores.md` | 3 solid + 1 ghost | Tiers 1-2 populated, Tier 3 shows "Unmitigated Risk" (same data as Tier 2 severity), Tier 4 dashed outline with CTA |
| `threats.md` | 1 solid + 3 ghost | Tier 1 populated, Tiers 2-4 dashed outlines with CTAs |

**Ghost Tiers**: Rendered as dashed outlines (no fill) with the pipeline command needed to unlock them. Ghost tiers maintain the funnel shape to show users what the complete visualization looks like.

### FR-4: Template Registration

Register `risk-funnel` in the infographic system:
1. Add to the agent's template registry in `.claude/agents/tachi/threat-infographic.md`
2. Add `risk-funnel` as a valid `--template` value in `.claude/commands/infographic.md`
3. Output files follow naming convention: `threat-risk-funnel-spec.md` + `threat-risk-funnel.jpg`

### FR-5: Data Extraction Paths

| Tier | compensating-controls.md | risk-scores.md | threats.md |
|------|-------------------------|----------------|------------|
| 1 — Threats Identified | Co-located threats.md Section 6 | Co-located threats.md Section 6 | Section 6 risk summary |
| 2 — Inherent Risk Scored | Co-located risk-scores.md Section 2 (or recalculate from controls file) | Section 2 scored threat table | N/A (ghost tier) |
| 3 — Controls Applied | Section 1 executive summary + Section 2 coverage matrix | N/A (ghost tier) | N/A (ghost tier) |
| 4 — Residual Risk | Section 2 residual severity bands | N/A (ghost tier) | N/A (ghost tier) |

**Note on Tier 2 in compensating-controls mode**: The compensating-controls.md file contains both composite scores (inherent) and residual scores. Tier 2 uses the composite scores; Tier 4 uses the residual scores. The delta between them IS the risk reduction story.

### FR-6: Gemini Prompt Design

The Gemini prompt MUST:
- Lead with aesthetic intent: "photorealistic 3D funnel", "premium glass-like material", "executive boardroom quality"
- Specify exact hex colors per severity tier
- Enumerate tier labels, widths, and data values explicitly (no inference)
- Include sidebar metrics as explicit text overlay instructions
- Specify gradient transitions between tiers
- Use professional business language (avoid security attack terminology per existing convention)
- Include `{funnel_tier_data}` placeholder populated from spec sections

---

## Non-Functional Requirements

### Performance
- Template loading: < 1 second (single markdown file read)
- Spec generation: < 10 seconds (data extraction + spec writing)
- Overall command execution: < 30 seconds (unchanged from existing templates)
- Gemini image generation: < 60 seconds (consistent with existing templates)

### Reliability
- Graceful degradation is deterministic — tier count is derived solely from data source type
- Ghost tiers render with correct CTA text regardless of available data
- Template follows same error handling as existing templates (spec always produced, image best-effort)

### Compatibility
- Output spec structure follows `schemas/infographic.yaml` v1.0 (6 sections)
- Spec frontmatter includes `template: "risk-funnel"` for identification
- Existing templates unaffected — `risk-funnel` is additive
- Works with `--template all` (generates all three templates)
- Explicit path override continues to work

---

## Scope & Boundaries

### In Scope (P0 — Must Have)
- Template file `.claude/agents/tachi/templates/infographic-risk-funnel.md` with full design specification
- 4-tier funnel layout with data-driven tier widths
- Graceful degradation (4/3/1 tier modes based on data source)
- Ghost tier rendering with pipeline CTAs
- Template registration in agent and command files
- Gemini prompt template for photorealistic 3D funnel image
- Spec output following infographic.yaml schema

### In Scope (P1 — Should Have)
- Metrics sidebar with key risk reduction statistics
- Tier connector gradients in Gemini prompt
- Percentage annotations between tiers showing reduction at each stage

### Out of Scope
- Animated funnel (static image only)
- Interactive HTML output
- Comparison mode (two funnels side by side for before/after)
- Custom tier labels or user-configurable tier count
- Portrait orientation variant

### Assumptions
- The existing 3-tier auto-detection hierarchy (implemented in PRD-048) correctly identifies data source type
- `compensating-controls.md` contains both composite scores (inherent) and residual scores per finding
- Gemini image generation can render 3D funnel shapes with photorealistic quality at 16:9 resolution
- The `--template all` flag will include `risk-funnel` alongside `baseball-card` and `system-architecture`

### Constraints
- **Fresh context isolation** (ADR-010): All data must be passed to the agent via data source files
- **Specification-first**: Markdown spec is primary deliverable; Gemini image is best-effort
- **Template pattern compliance**: Must follow exact structure of existing templates (sections, frontmatter, Gemini config)
- **No breaking changes**: All existing `/infographic` invocations must continue to work identically

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Gemini may struggle with photorealistic 3D funnel rendering
- **Likelihood**: Medium — 3D funnels are more complex than flat dashboards or architecture diagrams
- **Impact**: Low — spec is primary deliverable; image is best-effort with graceful degradation
- **Mitigation**: Design Gemini prompt with detailed 3D rendering cues (lighting, material, perspective). Fall back to high-quality 2D funnel if 3D proves unreliable across runs.

**Risk 2**: Funnel width proportionality may not convey meaningful reduction when risk reduction is small
- **Likelihood**: Medium — if controls only reduce 10-15% of risk, the funnel barely narrows
- **Impact**: Medium — undermines the visual narrative
- **Mitigation**: Enforce minimum 10% visual narrowing per tier (independent of actual data) to maintain the funnel metaphor while showing real numbers in labels

**Risk 3**: Ghost tier rendering (dashed outlines) may look cluttered in 1-tier mode
- **Likelihood**: Low — design template controls visual weight of ghost tiers
- **Impact**: Low — aesthetic concern, not functional
- **Mitigation**: Ghost tiers use light opacity (20%) and thin dashed borders to stay unobtrusive

### Dependencies

**Internal Dependencies**:
- **PRD-048** (Infographic Tiered Detection & Residual Risk): Delivered — provides 3-tier auto-detection and residual risk extraction
- **PRD-039** (Standalone /infographic Command): Delivered — provides command framework, `--template` flag, auto-detection
- **PRD-018** (Threat Infographic Agent): Delivered — provides agent architecture, spec generation, Gemini pipeline
- **Infographic agent**: `.claude/agents/tachi/threat-infographic.md` — requires template registry update
- **Infographic command**: `.claude/commands/infographic.md` — requires `risk-funnel` as valid template value

---

## Open Questions

- [ ] Should the funnel include a "Risk Eliminated" annotation showing threats fully mitigated (residual score = 0.0)? — PM — During implementation
- [ ] Should `--template all` include risk-funnel by default or require explicit opt-in for the first release? — Architect — During implementation

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- PRD-048 (Infographic Tiered Detection): [048-infographic-tiered-detection-residual-risk-2026-03-28.md](048-infographic-tiered-detection-residual-risk-2026-03-28.md)
- PRD-039 (Standalone /infographic Command): [039-standalone-infographic-command-2026-03-28.md](039-standalone-infographic-command-2026-03-28.md)
- PRD-036 (Compensating Controls): [036-compensating-controls-2026-03-27.md](036-compensating-controls-2026-03-27.md)
- PRD-035 (Quantitative Risk Scoring): [035-quantitative-risk-scoring-2026-03-27.md](035-quantitative-risk-scoring-2026-03-27.md)

### Technical Documentation
- Constitution: [constitution.md](../../../.aod/memory/constitution.md)
- Infographic Command: `.claude/commands/infographic.md`
- Infographic Agent: `.claude/agents/tachi/threat-infographic.md`
- Existing Templates: `.claude/agents/tachi/templates/infographic-baseball-card.md`, `.claude/agents/tachi/templates/infographic-system-architecture.md`
- Infographic Schema: `schemas/infographic.yaml`
- Compensating Controls Schema: `schemas/compensating-controls.yaml`

### Source
- GitHub Issue: #53 — Risk Reduction Funnel infographic template
