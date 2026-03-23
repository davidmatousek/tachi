---
prd:
  number: "018"
  topic: threat-infographic-agent
  created: 2026-03-23
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-23, status: approved, notes: "PRD drafted by PM via ~aod-define skill with GitHub Issue #18 user stories, consumer guide F-008, and OWASP/CVSS research as primary inputs"}
  architect_signoff: {agent: architect, date: 2026-03-23, status: approved_with_concerns, notes: "14 findings (0 critical, 1 high, 7 medium, 5 low). High: Gemini image quality for data-dense infographics is unreliable — reframe spec as primary deliverable, image as best-effort. Medium: missing schemas/infographic.yaml, Phase 6 fresh-context isolation, opt-out flag naming. All resolvable in spec phase."}
  techlead_signoff: {agent: team-lead, date: 2026-03-23, status: approved_with_concerns, notes: "Feasible in 1 sprint (75% confidence, 2.0-3.5h). L/L/S sizing correct. 5-wave execution. Recommend elevating FR-7 to P0 and resolving open questions 1 and 3 before task breakdown."}
source:
  idea_id: 18
  story_id: null
---

# Threat Infographic Agent - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-23
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 2 (Reporting & Integration)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Build an infographic agent that transforms threat model data into a visual risk specification and produces a presentation-ready infographic image via Gemini API.

### Problem Statement
Developers using tachi now have a structured `threats.md` and a narrative `threat-report.md` (delivered in F-015). While the report serves CISOs and security engineers with text-based analysis, three communication gaps remain:

1. **Board presentations and stakeholder briefings** demand visual artifacts — charts, heat maps, and graphical summaries — not multi-page markdown documents. Executives scanning a deck allocate 3-5 seconds per slide; a text-heavy threat report cannot compete with a single infographic that communicates risk posture at a glance.

2. **Security dashboards and documentation portals** increasingly embed images rather than rendered markdown. Teams using Confluence, Notion, or slide decks need a `.jpg` or `.png` they can drag-and-drop, not a Mermaid diagram that requires a renderer.

3. **Cross-team communication** — sharing threat model results with product managers, QA leads, and external auditors — is friction-heavy when the deliverable is a 50+ section markdown file. A single infographic summarizing risk distribution, coverage heat map, and top critical findings is the artifact that actually gets shared.

Without a visual output layer, tachi's reporting pipeline produces comprehensive text that is underutilized outside the security team.

### Proposed Solution
Add an infographic agent (`agents/threat-infographic.md`) that operates as a new Phase 6 (Infographic) in the orchestrator pipeline, after Phase 5 (Report). The agent performs two steps:

1. **Infographic specification generation** — Reads `threats.md` (and optionally `threat-report.md`) and produces a detailed infographic specification (`threat-infographic-spec.md`) describing the layout, data points, color coding, text content, and visual hierarchy. This spec is a structured markdown document that serves as both a human-readable design brief and a machine-readable prompt for image generation.

2. **Image generation via Gemini API** — Feeds the infographic specification to Google's Gemini image generation API to produce `threat-infographic.jpg`. The specification is designed to produce a clean, professional, presentation-ready visual.

The infographic agent is a **markdown prompt file**, consistent with tachi's architecture where all agents are prompt files, not application code. Image generation is **optional and configurable** — projects without Gemini API access receive the infographic specification as a standalone deliverable for manual rendering.

### Success Criteria
- Infographic agent produces a structured `threat-infographic-spec.md` from `threats.md` in the example project
- The spec includes: risk distribution chart data, coverage heat map data, top critical findings summary, and architecture threat overlay description
- When Gemini API is available, the agent produces a `threat-infographic.jpg` that is presentation-ready
- When Gemini API is unavailable, the spec is saved as a standalone markdown document usable for manual rendering
- All tachi features remain fully functional without Gemini API access — infographic generation is additive, not required
- The infographic accurately reflects the data in `threats.md` — no misrepresentation of risk levels or finding counts

### Timeline
Phase 2 delivery — estimated 1 sprint

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: `docs/product/01_Product_Vision/product-vision.md`

The infographic agent extends tachi's mission as "the default threat modeling toolkit for any team building agentic AI applications" by adding the visual communication layer that executives and cross-functional teams expect. Text-based reports serve security engineers; visual artifacts serve the broader organization. This positions tachi as a complete threat intelligence platform — from structured analysis (F-005, F-007) through narrative reporting (F-015) to visual communication (F-018).

### Roadmap Fit
**Phase**: Phase 2 (Reporting & Integration)
**Dependencies**: F-001, F-003, F-005, F-007, F-010, F-015 (all delivered) — provides the complete `threats.md` and `threat-report.md` that the infographic agent consumes
**Blocks**: Future dashboard or CI/CD integration features that consume visual artifacts

---

## Target Users & Personas

### Primary Persona: Executive / CISO
- **Role**: Security leadership, board reporting, investment decisions
- **Experience**: Understands risk concepts but does not read multi-page threat reports end-to-end
- **Goals**: Communicate risk posture in board presentations and stakeholder briefings using a single visual artifact
- **Pain Points**: Must manually create slides from text-based reports; visual artifacts require design tools and security interpretation skills

**Why This Matters**: Executives make budget and priority decisions based on what they can quickly comprehend. A presentation-ready infographic removes the translation step between threat analysis and executive action.

### Secondary Persona: Developer / DevSecOps Engineer
- **Role**: Builds and operates the threat modeling pipeline
- **Experience**: Technical, comfortable with APIs and configuration
- **Goals**: Automate visual output generation as part of the threat modeling pipeline without manual design work
- **Pain Points**: Creating visual summaries requires switching to design tools; Gemini integration requires structured prompts that are hard to craft manually

### Tertiary Persona: Project Manager / Auditor
- **Role**: Cross-team coordination, compliance documentation
- **Experience**: Manages stakeholder communication, not security-specialized
- **Goals**: Share threat model results with non-technical stakeholders via a shareable image artifact
- **Pain Points**: Cannot embed markdown reports in slide decks, Confluence pages, or audit documentation without screenshots

---

## User Stories

### US-1: Visual Threat Infographic for Executive Communication
**When**: I have a completed threat model and need to present risk posture to management or a board,
**I want to**: a visual threat infographic showing risk distribution, coverage heat map, and top critical findings,
**So I can**: quickly communicate the security landscape without requiring the audience to read a full report.

**Acceptance Criteria**:
- **Given** a completed `threats.md` with findings from STRIDE and AI agents, **when** the infographic agent runs, **then** it produces `threat-infographic-spec.md` containing layout, data points, color coding, and text content for the infographic
- **Given** the infographic specification, **when** it describes risk distribution, **then** it includes finding counts per risk level (Critical, High, Medium, Low) using CVSS severity color conventions (Critical=red, High=orange, Medium=yellow, Low=blue per research §10)
- **Given** the infographic specification, **when** it describes the coverage heat map, **then** it shows which architecture components have the most findings and their severity distribution
- **Given** the infographic specification, **when** it describes the architecture threat overlay, **then** it annotates which components carry the most risk with visual weight proportional to finding severity and count
- **Given** the generated infographic (spec or image), **when** viewed by an executive, **then** the risk posture is comprehensible within 10 seconds without reading accompanying text

**Priority**: P0
**Effort**: L

### US-2: Structured Infographic Specification for Gemini Image Generation
**When**: I want the infographic agent to produce a visual automatically from threat data,
**I want to**: the agent to generate a detailed infographic specification and feed it to Gemini image generation API,
**So I can**: get a presentation-ready `threat-infographic.jpg` without manual design work.

**Acceptance Criteria**:
- **Given** a completed `threats.md`, **when** the infographic agent runs with Gemini API access configured, **then** it produces both `threat-infographic-spec.md` (the specification) and `threat-infographic.jpg` (the rendered image)
- **Given** the infographic specification, **when** fed to Gemini image generation API, **then** the resulting image is clean, professional, and suitable for presentation slides (minimum 1920x1080 resolution)
- **Given** the infographic specification, **when** saved as markdown, **then** it is detailed enough for a designer to manually render the infographic if Gemini is unavailable
- **Given** the Gemini API returns an error or is unavailable, **when** the agent detects the failure, **then** it saves the specification as a standalone deliverable and logs a warning — it does NOT fail the pipeline

**Priority**: P0
**Effort**: L

### US-3: Optional and Configurable Infographic Generation
**When**: my project does not have Gemini API access or I want to skip infographic generation,
**I want to**: infographic generation to be optional and configurable,
**So I can**: use all other tachi features without requiring a Gemini API key.

**Acceptance Criteria**:
- **Given** a project without a `GEMINI_API_KEY` environment variable set, **when** the orchestrator runs, **then** infographic image generation is skipped gracefully with an informational message — the spec is still generated but no image is produced
- **Given** the orchestrator configuration, **when** infographic generation is disabled (opt-out flag), **then** Phase 6 is skipped entirely — no spec, no image
- **Given** a project with all features enabled, **when** the orchestrator runs the full pipeline, **then** Phases 1-5 complete regardless of whether Phase 6 succeeds or fails — infographic generation never blocks the core pipeline

**Priority**: P0
**Effort**: S

---

## Functional Requirements

### FR-1: Infographic Agent Prompt Definition

**Description**: Create `agents/threat-infographic.md` as a markdown prompt file defining the infographic agent's analysis methodology, specification format, and image generation instructions.

**Agent Responsibilities**:
- Parse `threats.md` for risk data: finding counts per severity, component-level finding distribution, top critical/high findings
- Optionally parse `threat-report.md` for cross-cutting themes and remediation priorities
- Generate a structured infographic specification with layout, data points, colors, and text
- Interface with Gemini API for image generation when available
- Gracefully handle missing API access

**Agent Prompt Structure** (follows existing agent pattern from F-015):
- YAML header with agent metadata, input contract, output contract
- Data extraction methodology
- Infographic specification format
- Gemini API prompt construction guidelines
- Fallback behavior for no-API scenarios

### FR-2: Infographic Specification Format

**Description**: Define the `threat-infographic-spec.md` output structure.

**Required Specification Sections**:

| Section | Content | Source |
|---------|---------|--------|
| **Metadata** | Project name, scan date, agent count, total findings | `threats.md` YAML frontmatter and Section 6 |
| **Risk Distribution** | Finding counts per severity level with percentages | Computed from Section 3-4 finding tables |
| **Coverage Heat Map** | Component × severity matrix showing finding density | Computed from component field across all findings |
| **Top Critical Findings** | Summary of up to 5 most severe findings with component and threat | Filtered from Critical/High findings |
| **Architecture Threat Overlay** | Description of which components carry highest risk and why | Derived from component-level aggregation |
| **Visual Design Directives** | Color palette, layout structure, font hierarchy, spacing | CVSS severity colors (§10) + clean professional style |
| **Gemini Prompt** | The exact prompt to send to Gemini API for image generation | Constructed from all above sections |

### FR-3: CVSS Severity Color Coding

**Description**: Use standardized CVSS severity color conventions throughout the infographic specification.

**Color Mapping** (from research §10):

| Severity | Color | Hex | Usage |
|----------|-------|-----|-------|
| Critical | Red | `#FF0000` | Chart segments, heat map cells, finding badges |
| High | Orange | `#FFA500` | Chart segments, heat map cells, finding badges |
| Medium | Yellow | `#FFD700` | Chart segments, heat map cells, finding badges |
| Low | Blue | `#4169E1` | Chart segments, heat map cells, finding badges |
| Informational | Gray | `#808080` | Background elements, de-emphasized items |

### FR-4: Risk Distribution Chart Data

**Description**: Extract and format finding counts for a risk distribution visualization.

**Data Structure**:
- Count of findings per severity level (Critical, High, Medium, Low)
- Percentage of total findings per severity level
- Total finding count
- Formatted for both pie chart and bar chart representation

**Source**: Aggregate from `threats.md` Sections 3 (STRIDE Findings) and 4 (AI Agent Findings), using the `risk_level` field from each finding.

### FR-5: Coverage Heat Map Data

**Description**: Generate a component × severity matrix for heat map visualization.

**Data Structure**:
- Rows: Architecture components (from `component` field in findings)
- Columns: Severity levels (Critical, High, Medium, Low)
- Cells: Finding count for each component-severity combination
- Row ordering: By total finding count (most findings first)

**Source**: Cross-tabulate `component` and `risk_level` fields across all findings in `threats.md`.

### FR-6: Gemini API Integration

**Description**: Interface with Google Gemini API for image generation from the infographic specification.

**Integration Flow**:
1. Check for `GEMINI_API_KEY` environment variable
2. If present: construct Gemini prompt from `threat-infographic-spec.md`, call Gemini image generation API, save result as `threat-infographic.jpg`
3. If absent: log informational message, save spec as standalone deliverable, continue pipeline

**API Requirements**:
- Use Gemini's image generation endpoint
- Request minimum 1920x1080 resolution
- Request professional, clean design style suitable for business presentations
- Include error handling for API rate limits, timeouts, and content policy rejections

**Fallback Behavior**:
- API unavailable → save spec only, log warning, continue pipeline
- API error → save spec only, log error with details, continue pipeline
- API content policy rejection → save spec only, log rejection reason, continue pipeline

### FR-7: Orchestrator Integration

**Description**: Integrate the infographic agent into the orchestrator pipeline as Phase 6 (Infographic).

**Integration Points**:
- Phase 6 runs after Phase 5 (Report) completes
- Infographic agent receives `threats.md` as primary input and `threat-report.md` as optional secondary input
- Output is written to the same output directory as other pipeline outputs
- Phase 6 is optional — configurable via orchestrator settings or command-line flag

**Output Directory Structure** (after Phase 6):
```
YYYY-MM-DD-{phase}/
├── threats.md              # Phase 4 output (existing)
├── threats.sarif            # Phase 4 output (existing, F-012)
├── threat-report.md         # Phase 5 output (existing, F-015)
├── attack-trees/            # Phase 5 output (existing, F-015)
├── threat-infographic-spec.md  # Phase 6 output (new)
└── threat-infographic.jpg      # Phase 6 output (new, conditional on Gemini API)
```

### FR-8: Opt-Out Configuration

**Description**: Allow users to disable infographic generation entirely.

**Configuration Options**:
- Command-line flag: `--no-infographic` on orchestrator invocation to skip Phase 6 entirely
- Environment variable: `TACHI_SKIP_INFOGRAPHIC=true` as persistent configuration
- When opted out: Phase 6 is not invoked, no spec or image is generated, no warning is logged

---

## Non-Functional Requirements

### Data Accuracy
- Risk distribution counts MUST exactly match the finding counts in `threats.md` — no rounding errors, no omitted findings
- Component names in the heat map MUST match the component names in `threats.md` exactly
- Severity colors MUST follow the CVSS convention defined in FR-3 — no ad-hoc color choices

### Pipeline Resilience
- Phase 6 failures MUST NOT block or invalidate Phases 1-5 outputs
- Gemini API failures MUST be handled gracefully — the spec is always saved regardless of API availability
- Phase 6 MUST complete within 60 seconds (excluding Gemini API call time)

### Portability
- The infographic specification MUST be self-contained — a designer can render the infographic from the spec alone without access to `threats.md`
- The specification MUST be valid markdown readable by any markdown renderer
- The generated image MUST be a standard JPEG — no proprietary formats

### Configurability
- All three infographic sections (risk distribution, heat map, top findings) MUST be present in every specification
- Gemini API integration MUST be opt-in via environment variable presence, not a required configuration step
- The opt-out flag MUST completely skip Phase 6 with no residual side effects

---

## Success Metrics

### Primary Metrics

**Infographic Specification Quality**: Spec contains all required sections with accurate data
- **Baseline**: N/A (no visual output exists)
- **Target**: Every generated spec includes risk distribution, coverage heat map, top findings, architecture overlay, and Gemini prompt
- **Timeline**: At delivery

**Data Accuracy**: 100% match between spec data and `threats.md` finding counts
- **Baseline**: N/A
- **Target**: Zero discrepancy between risk distribution counts in spec and actual finding counts in `threats.md`
- **Timeline**: At delivery

**Pipeline Resilience**: Phase 6 never blocks pipeline completion
- **Baseline**: N/A
- **Target**: Zero pipeline failures caused by infographic agent errors or Gemini API failures
- **Timeline**: At delivery

**Gemini Integration**: Image generated successfully when API is available
- **Baseline**: N/A
- **Target**: `threat-infographic.jpg` produced with presentation-ready quality when `GEMINI_API_KEY` is set
- **Timeline**: At delivery

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Infographic agent prompt file (`agents/threat-infographic.md`)
- Infographic specification generation (`threat-infographic-spec.md`) with risk distribution, coverage heat map, top critical findings, and architecture threat overlay
- CVSS severity color coding per research §10
- Gemini API integration for image generation (when API key is available)
- Graceful fallback when Gemini API is unavailable (spec saved as standalone deliverable)
- Pipeline isolation — Phase 6 failures never block Phases 1-5

**Should Have (P1)**:
- Orchestrator integration as Phase 6 (Infographic)
- Opt-out configuration (`--no-infographic` flag and `TACHI_SKIP_INFOGRAPHIC` environment variable)
- Architecture threat overlay in specification

### Out of Scope

**Won't Have**:
- Interactive or animated infographic visualization
- Multiple image output formats (PNG, SVG, PDF) — JPEG only for MVP
- Custom infographic templates or branding options
- Alternative image generation APIs (DALL-E, Midjourney, Stable Diffusion) — Gemini only for MVP
- Real-time infographic updates when `threats.md` changes
- Infographic comparison across multiple threat model runs
- Embedding infographic in `threat-report.md` (separate file output)

### Assumptions
- Gemini API supports image generation with sufficient quality for business presentations
- The infographic specification format is detailed enough for Gemini to produce useful output
- `threats.md` structure (finding IR schema) remains stable from F-010/F-012
- A single infographic image is sufficient — no multi-page or multi-image output needed
- JPEG format meets presentation needs (no transparency required)

### Constraints
- **No application code**: Infographic agent is a prompt file, consistent with tachi's architecture
- **Gemini API dependency**: Image generation requires external API access — this is an optional enhancement, not a core capability
- **Single image format**: JPEG only for MVP to limit scope
- **Pipeline dependency**: Requires `threats.md` from Phase 4 — cannot run independently

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Gemini image generation quality for data-rich infographics
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Design the infographic specification to be as explicit as possible — exact text, exact colors, exact layout positions. Include example infographic descriptions in the agent prompt.
- **Contingency**: If Gemini produces low-quality images, the specification serves as the primary deliverable — users render manually or use design tools. Image generation becomes a "nice to have" rather than a core feature.

**Risk 2**: Gemini API content policy rejection for security-related content
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Frame the infographic as a "risk assessment summary" or "security posture overview" using business language, not attack-specific terminology. Avoid words that might trigger content filters (e.g., "exploit", "attack" in the image prompt).
- **Contingency**: Specification-only output if content policy consistently rejects security infographic prompts.

**Risk 3**: Infographic specification too complex for consistent Gemini output
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Use a structured prompt format with clear sections — Gemini performs better with well-organized prompts. Include layout grid coordinates and precise color hex codes.
- **Contingency**: Simplify the infographic to 2-3 core visualizations (risk distribution + top findings) rather than attempting all four sections.

**Risk 4**: Data accuracy in visual representation
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**: The infographic specification includes exact numeric data — finding counts, percentages, component names. The spec is verifiable against `threats.md` before image generation. Include a data verification section in the spec.
- **Contingency**: Add a "Data Source: threats.md" watermark or footnote to the infographic so viewers know to verify against the source document.

### Dependencies

**Internal Dependencies**:
- **F-003 (Orchestrator)**: Delivered — pipeline where Phase 6 is added
- **F-005 (STRIDE Agents)**: Delivered — produces STRIDE findings
- **F-007 (AI Agents)**: Delivered — produces AI findings
- **F-010 (Deduplication & Risk Rating)**: Delivered — provides calibrated risk levels
- **F-015 (Threat Report Agent)**: Delivered — Phase 5 output; infographic agent runs after report
- **`schemas/finding.yaml`**: Defines finding IR parsed by the infographic agent
- **`schemas/output.yaml`**: Defines `threats.md` structure consumed by the infographic agent

**External Dependencies**:
- **Google Gemini API**: Image generation capability — optional dependency, feature works without it
- **`GEMINI_API_KEY` environment variable**: Required for image generation, not for specification generation

**Dependency Graph**:
```
F-018 (Threat Infographic Agent)
  ├── Depends on: F-003 (Orchestrator) ✅ Delivered
  ├── Depends on: F-005 (STRIDE Agents) ✅ Delivered
  ├── Depends on: F-007 (AI Agents) ✅ Delivered
  ├── Depends on: F-010 (Dedup & Risk) ✅ Delivered
  ├── Depends on: F-015 (Threat Report Agent) ✅ Delivered
  ├── Optional: Google Gemini API (image generation)
  └── Blocks: Future dashboard/CI integration features
```

---

## Open Questions

- [ ] What Gemini model and endpoint should be used for image generation? (e.g., `gemini-2.0-flash-exp` with `generateImage`) — architect — Decide in spec phase
- [ ] Should the infographic specification include an SVG fallback description for environments where Gemini is unavailable long-term? — PM — Deferred to future feature
- [ ] What is the maximum number of components to display in the coverage heat map before truncating to "top N"? — architect — Decide in spec phase
- [ ] Should the agent support multiple infographic layouts (landscape vs. portrait) or standardize on one? — PM — Standardize on landscape (16:9) for MVP

---

## References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- Consumer Guide: `docs/guides/CONSUMER_GUIDE_TACHI.md` § F-008
- Threat Report PRD: `docs/product/02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md`

### Technical Documentation
- Output Schema: `schemas/output.yaml` (defines `threats.md` structure)
- Finding Schema: `schemas/finding.yaml` (finding IR)
- Orchestrator: `agents/orchestrator.md` (pipeline phases)
- Example Output: `examples/mermaid-agentic-app/threats.md` (sample threat model)

### Research References
- §8 — Risk Rating Matrices (OWASP risk levels and severity scales for visual risk distribution charts)
- §10 — CVSS (severity color conventions — Critical=red, High=orange, Medium=yellow, Low=blue)

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-03-23 | PRD drafted with GitHub Issue #18 stories, consumer guide F-008, and CVSS/OWASP research |
| Architect | architect | ⚠ Approved with Concerns | 2026-03-23 | 1 high (Gemini quality), 7 medium, 5 low — all resolvable in spec phase |
| Engineering Lead | team-lead | ⚠ Approved with Concerns | 2026-03-23 | 1 sprint feasible (75% confidence, 2.0-3.5h). Elevate FR-7 to P0; resolve open questions before tasks |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-23 | product-manager | Initial PRD |
