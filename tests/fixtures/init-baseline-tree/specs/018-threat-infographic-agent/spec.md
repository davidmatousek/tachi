---
prd_reference: docs/product/02_PRD/018-threat-infographic-agent-2026-03-23.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "All 8 PRD functional requirements mapped to 15 spec FRs. All 3 PRD user stories covered plus orchestrator integration elevated to P0 per Team Lead condition. All 4 open questions resolved. Architect concerns addressed. 3 low-severity non-blocking concerns: hex palette refinement, opt-out flag naming convention, SC-008 subjectivity — all addressable in plan/tasks phase."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Threat Infographic Agent

**Feature Branch**: `018-threat-infographic-agent`
**Created**: 2026-03-23
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/018-threat-infographic-agent-2026-03-23.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Visual Threat Infographic Specification for Executive Communication (Priority: P0)

As a CISO or security director, when I have a completed threat model (`threats.md`) and need to present risk posture to my board or management team, I want the findings transformed into a structured infographic specification that describes the visual layout, data points, color coding, and text content for a presentation-ready infographic so I can quickly communicate the security landscape without requiring the audience to read a full report.

**Why this priority**: The infographic specification is the primary deliverable and the foundation for all visual outputs. It bridges the gap between comprehensive text-based threat reports and the single-slide visual artifact that executives actually review during board presentations. Without the specification, neither manual design nor automated image generation is possible.

**Independent Test**: Run the infographic agent against the sample `examples/mermaid-agentic-app/threats.md` and verify it produces a `threat-infographic-spec.md` with all six required sections. Have a non-technical reader confirm the specification describes a visual that communicates risk posture within 10 seconds of viewing.

**Acceptance Scenarios**:

1. **Given** a completed `threats.md` with findings from STRIDE and AI agents, **When** the infographic agent runs, **Then** it produces `threat-infographic-spec.md` containing all six required sections: Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, and Visual Design Directives.

2. **Given** the Risk Distribution section of the specification, **When** it describes finding counts, **Then** the counts per severity level (Critical, High, Medium, Low) exactly match the aggregate counts in `threats.md` Section 6 (Risk Summary) — zero discrepancy.

3. **Given** the Coverage Heat Map section, **When** it describes the component × severity matrix, **Then** it includes all components with findings from `threats.md`, ordered by total finding count (most findings first), capped at the top 8 components if more than 8 exist.

4. **Given** the Top Critical Findings section, **When** it lists findings, **Then** it includes up to 5 findings selected from the highest severity levels (Critical first, then High), each with finding ID, component name, threat summary (one sentence), and risk level.

5. **Given** the Architecture Threat Overlay section, **When** it describes component risk, **Then** it annotates which components carry the highest cumulative risk with a description of visual weight proportional to finding severity and count.

6. **Given** the Visual Design Directives section, **When** it specifies colors, **Then** it uses CVSS severity color conventions: Critical=#DC2626 (red), High=#F97316 (orange), Medium=#EAB308 (yellow), Low=#4169E1 (blue), Informational=#6B7280 (gray).

---

### User Story 2 — Automated Image Generation via Gemini API (Priority: P0)

As a developer or DevSecOps engineer, when I want the infographic agent to produce a visual automatically from threat data, I want the agent to generate a detailed infographic specification and feed it to the Gemini image generation API so I get a presentation-ready `threat-infographic.jpg` without manual design work.

**Why this priority**: Automated image generation removes the translation step between threat analysis data and a shareable visual artifact. While the specification is the primary deliverable, the image is the artifact that gets embedded in slide decks, Confluence pages, and audit documentation. Co-equal P0 because it completes the end-to-end automation promise.

**Independent Test**: Set the `GEMINI_API_KEY` environment variable, run the infographic agent against the sample `threats.md`, and verify it produces both `threat-infographic-spec.md` and `threat-infographic.jpg`. Verify the image is a valid JPEG at minimum 1920x1080 resolution with a clean, professional layout.

**Acceptance Scenarios**:

1. **Given** a completed `threats.md` and a valid `GEMINI_API_KEY` environment variable, **When** the infographic agent runs, **Then** it produces both `threat-infographic-spec.md` (the specification) and `threat-infographic.jpg` (the rendered image).

2. **Given** the infographic specification, **When** fed to the Gemini image generation API, **Then** the resulting image uses a 16:9 landscape aspect ratio at minimum 1920x1080 resolution, suitable for presentation slides.

3. **Given** the Gemini API returns an error, times out, or rejects the prompt due to content policy, **When** the agent detects the failure, **Then** it saves the specification as a standalone deliverable and logs a warning with the specific failure reason — it does NOT fail the pipeline.

4. **Given** the infographic specification, **When** saved as markdown without Gemini API access, **Then** it is detailed enough for a designer to manually render the infographic using any design tool (Figma, Canva, PowerPoint).

5. **Given** the Gemini API prompt constructed from the specification, **When** submitted, **Then** the prompt uses business-oriented language ("risk assessment summary," "security posture overview") rather than attack-specific terminology to minimize content policy rejection risk.

---

### User Story 3 — Optional and Configurable Infographic Generation (Priority: P0)

As a tachi user, when my project does not have Gemini API access or I want to skip infographic generation entirely, I want infographic generation to be optional and configurable so I can use all other tachi features without requiring a Gemini API key.

**Why this priority**: Optionality is a prerequisite for all other user stories. If infographic generation is mandatory or breaks the pipeline when unavailable, it violates tachi's core principle that features are additive. This must be P0 because it gates the safety of deploying US-1 and US-2.

**Independent Test**: Run the full orchestrator pipeline without `GEMINI_API_KEY` set and verify Phases 1–5 complete normally. Then run with `TACHI_SKIP_INFOGRAPHIC=true` and verify Phase 6 is skipped entirely with no warning.

**Acceptance Scenarios**:

1. **Given** a project without a `GEMINI_API_KEY` environment variable, **When** the orchestrator runs, **Then** the infographic specification (`threat-infographic-spec.md`) is still generated but no image is produced. An informational message is logged: "Gemini API key not configured — infographic image generation skipped. Specification saved."

2. **Given** the orchestrator configuration with infographic generation disabled via opt-out flag (`--no-infographic`) or environment variable (`TACHI_SKIP_INFOGRAPHIC=true`), **When** the orchestrator runs, **Then** Phase 6 is skipped entirely — no specification, no image, no warning logged.

3. **Given** a project with all features enabled, **When** the orchestrator runs the full pipeline, **Then** Phases 1–5 complete and produce their outputs regardless of whether Phase 6 succeeds or fails. Phase 6 failures are isolated and never block the core pipeline.

4. **Given** the opt-out configuration, **When** both `--no-infographic` flag and `TACHI_SKIP_INFOGRAPHIC=true` are set, **Then** the flag takes precedence (either one is sufficient to skip Phase 6).

---

### User Story 4 — Orchestrator Integration as Phase 6 (Priority: P0)

As a tachi user running the threat modeling pipeline, when the orchestrator completes Phase 5 (Report), I want Phase 6 (Infographic) to automatically generate the infographic specification and optional image so I receive a complete threat model deliverable without manual intervention.

**Why this priority**: Without orchestrator integration, the infographic agent cannot be invoked as part of the standard pipeline — users would need to manually trigger infographic generation. Elevated to P0 per Team Lead condition during PRD review (FR-7 elevation).

**Independent Test**: Run the full orchestrator pipeline against the sample input and verify that Phase 6 automatically produces `threat-infographic-spec.md` (and `threat-infographic.jpg` if Gemini API is available) in the output directory alongside existing pipeline outputs.

**Acceptance Scenarios**:

1. **Given** the orchestrator completes Phase 5 (Report), **When** Phase 6 (Infographic) is enabled (default), **Then** the infographic agent is invoked with `threats.md` as its sole input and produces outputs in the same output directory.

2. **Given** Phase 6 execution, **When** the infographic agent is invoked, **Then** it runs in a fresh context with only `threats.md` as input — not the accumulated pipeline context from Phases 1–5 and not `threat-report.md`.

3. **Given** Phase 6 is set to skip via opt-out configuration, **When** the pipeline runs, **Then** it completes after Phase 5 without invoking the infographic agent. Existing Phase 1–5 behavior is unchanged.

4. **Given** a completed Phase 6, **When** the output directory is examined, **Then** the structure includes:
   ```
   YYYY-MM-DD-{phase}/
   ├── threats.md                     (Phase 4 — existing)
   ├── threats.sarif                  (Phase 4 — existing, F-012)
   ├── threat-report.md               (Phase 5 — existing, F-015)
   ├── attack-trees/                  (Phase 5 — existing, F-015)
   ├── threat-infographic-spec.md     (Phase 6 — new)
   └── threat-infographic.jpg         (Phase 6 — new, conditional on Gemini API)
   ```

---

### Edge Cases

- **Empty threat model**: If `threats.md` contains zero findings, the infographic agent produces a specification with zero-count risk distribution, empty heat map, and a note stating "No threats identified in this threat model." No image generation is attempted.
- **No Critical or High findings**: If all findings are Medium or Low, the Top Critical Findings section states "No Critical or High findings identified" and lists the top 5 Medium findings instead. The specification is still complete and valid.
- **Large threat model (>30 findings)**: The specification always includes all findings in the Risk Distribution counts and Coverage Heat Map. The Top Critical Findings section remains capped at 5 entries regardless of total count.
- **More than 8 components**: The Coverage Heat Map displays the top 8 components by total finding count. Remaining components are aggregated into an "Other" row with combined counts.
- **Single component**: If all findings target a single component, the Coverage Heat Map shows one row. The Architecture Threat Overlay notes the concentration risk.
- **Gemini API rate limit**: If the API returns a rate limit error (429), the agent logs the error, saves the specification, and continues the pipeline without retrying.
- **Gemini content policy rejection**: If the API rejects the prompt, the agent logs the rejection reason, saves the specification, and continues. The prompt is designed to use business language to minimize this risk.
- **Missing Section 6 in threats.md**: If `threats.md` lacks a Risk Summary section, the agent computes severity counts directly from individual findings in Sections 3 and 4.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an infographic agent defined as a markdown prompt file (`agents/threat-infographic.md`) that consumes the structured `threats.md` and produces a structured infographic specification (`threat-infographic-spec.md`).

- **FR-002**: The infographic specification MUST contain six required sections: (1) Metadata, (2) Risk Distribution, (3) Coverage Heat Map, (4) Top Critical Findings, (5) Architecture Threat Overlay, (6) Visual Design Directives.

- **FR-003**: The Metadata section MUST include: project name, scan date, total agent count, total finding count, and overall risk posture summary (one sentence). All values derived from `threats.md` YAML frontmatter and Section 6.

- **FR-004**: The Risk Distribution section MUST include finding counts per severity level (Critical, High, Medium, Low) with percentages of total, formatted for both donut chart and bar chart representation. Counts MUST exactly match `threats.md` Section 6 — zero discrepancy.

- **FR-005**: The Coverage Heat Map section MUST present a component × severity matrix showing finding density per component. Rows ordered by total finding count (descending), capped at top 8 components with remaining aggregated as "Other." Component names MUST match `threats.md` exactly.

- **FR-006**: The Top Critical Findings section MUST list up to 5 findings selected from the highest severity levels (Critical first, then High). Each entry includes: finding ID, component name, one-sentence threat summary, and risk level.

- **FR-007**: The Architecture Threat Overlay section MUST describe which components carry the highest cumulative risk, with visual weight guidance proportional to finding severity and count. This section enables a designer or AI model to annotate an architecture diagram.

- **FR-008**: The Visual Design Directives section MUST specify: CVSS severity color palette with hex codes (Critical=#DC2626, High=#F97316, Medium=#EAB308, Low=#4169E1, Info=#6B7280), layout structure (three-zone: header, distribution, findings), font hierarchy, spacing guidance, and 16:9 landscape aspect ratio.

- **FR-009**: The infographic agent MUST construct a Gemini API prompt from the specification sections, using business-oriented language ("risk assessment summary," "security posture overview"), explicit hex color codes, spatial zone descriptions, and short text labels (2-4 words per element, maximum 15-20 distinct text labels total).

- **FR-010**: When a `GEMINI_API_KEY` environment variable is present, the agent MUST submit the constructed prompt to the Gemini image generation API (model: configurable, default `gemini-3-pro-image-preview`) requesting a 16:9 landscape image at 2K resolution, and save the result as `threat-infographic.jpg`.

- **FR-011**: When `GEMINI_API_KEY` is absent or the API returns an error (rate limit, timeout, content policy rejection), the agent MUST save the specification as a standalone deliverable, log the specific condition, and continue the pipeline without failure.

- **FR-012**: The orchestrator MUST integrate the infographic agent as Phase 6 (Infographic) that runs after Phase 5 (Report) completes. Phase 6 is default-on with opt-out via `--no-infographic` flag or `TACHI_SKIP_INFOGRAPHIC=true` environment variable.

- **FR-013**: Phase 6 MUST invoke the infographic agent in a fresh context with only `threats.md` as input — not the accumulated pipeline context from Phases 1–5 and not `threat-report.md` or attack tree files.

- **FR-014**: Phase 6 failures MUST NOT block or invalidate Phases 1–5 outputs. The pipeline completes successfully regardless of Phase 6 outcome.

- **FR-015**: An infographic output schema (`schemas/infographic.yaml`) MUST be defined specifying the required sections, data accuracy constraints, color palette, and file naming conventions for structural validation.

### Key Entities

- **Infographic Specification** (`threat-infographic-spec.md`): The primary output document containing six sections that describe the visual layout, data points, color coding, and text content for a threat infographic. Authored by the infographic agent, consumed by designers, Gemini API, or presentation authors.

- **Infographic Image** (`threat-infographic.jpg`): A JPEG image rendered from the specification via Gemini API. Optional output — produced only when `GEMINI_API_KEY` is available and the API call succeeds. 16:9 landscape format at minimum 1920x1080 resolution.

- **Risk Distribution**: Aggregated finding counts per severity level with percentages. Source: `threats.md` Section 6 (Risk Summary). Primary visualization in the infographic.

- **Coverage Heat Map**: A component × severity matrix showing finding density across architecture components. Source: cross-tabulation of `component` and `risk_level` fields across all findings. Capped at top 8 components.

- **Gemini Prompt**: A structured text prompt constructed from the infographic specification, designed for the Gemini image generation API. Uses business language, explicit colors, spatial layout instructions, and short labels.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The infographic agent produces a complete `threat-infographic-spec.md` from the sample `examples/mermaid-agentic-app/threats.md` containing all six required sections with non-empty content in each.

- **SC-002**: Risk distribution counts in the specification exactly match `threats.md` Section 6 — zero discrepancy when compared field by field (Critical, High, Medium, Low counts and percentages).

- **SC-003**: The Coverage Heat Map includes all components with findings from the sample `threats.md`, ordered by total finding count, with correct per-severity counts cross-validated against individual findings.

- **SC-004**: When `GEMINI_API_KEY` is configured, the agent produces a `threat-infographic.jpg` that is a valid JPEG file with 16:9 aspect ratio at minimum 1920x1080 resolution.

- **SC-005**: When `GEMINI_API_KEY` is not configured, the specification is saved as a standalone deliverable and the pipeline completes without error — no pipeline failure, no missing Phase 1–5 outputs.

- **SC-006**: The full orchestrator pipeline (Phases 1–6) completes successfully against the sample input, with Phase 6 producing `threat-infographic-spec.md` alongside existing Phase 4 and Phase 5 outputs.

- **SC-007**: Phase 6 (Infographic) can be skipped via `--no-infographic` or `TACHI_SKIP_INFOGRAPHIC=true` without affecting Phase 1–5 behavior — backward compatibility preserved.

- **SC-008**: The infographic specification is self-contained — a designer can render the infographic from the spec alone without access to `threats.md`, validated by having a designer confirm all necessary data and design direction is present.

## Assumptions

- `threats.md` is complete and valid, produced by the orchestrator with all Phases 1–4 (and optionally Phase 5) complete.
- The finding IR schema (`schemas/finding.yaml`) and output schema (`schemas/output.yaml`) remain stable at their current versions.
- The Gemini image generation API (`gemini-3-pro-image-preview`) is available and supports 16:9 landscape output at 2K resolution. The model ID is configurable for future model updates.
- AI-generated images are "presentation-ready with possible minor text corrections needed" — the specification is the authoritative reference for data accuracy, not the image.
- A single infographic image is sufficient for MVP — no multi-page or multi-image output needed.
- JPEG format meets presentation needs (no transparency required).
- The infographic agent runs within the same LLM context infrastructure as other tachi agents.
- Phase 6 receives only `threats.md` as input (fresh context), not the accumulated orchestrator pipeline context from Phases 1–5.
- CVSS severity colors follow de facto industry convention as no official standard exists. The chosen palette (red/orange/yellow/blue) matches the PRD specification.

## Scope Boundaries

### In Scope
- Infographic agent prompt file (`agents/threat-infographic.md`)
- Infographic output schema (`schemas/infographic.yaml`)
- Infographic specification generation with all six sections
- CVSS severity color coding with explicit hex codes
- Gemini API integration for image generation (optional, when API key available)
- Graceful fallback when Gemini API is unavailable (spec saved as standalone)
- Orchestrator integration as Phase 6 (default-on, opt-out via flag or env var)
- Fresh context isolation for Phase 6 (threats.md only)
- Pipeline isolation — Phase 6 failures never block Phases 1–5
- Three-zone infographic layout (header, distribution, findings) in 16:9 landscape
- Heat map truncation to top 8 components

### Out of Scope
- Interactive or animated infographic visualization
- Multiple image output formats (PNG, SVG, PDF) — JPEG only for MVP
- Custom infographic templates or branding options
- Alternative image generation APIs (DALL-E, Midjourney, Stable Diffusion) — Gemini only for MVP
- Real-time infographic updates when `threats.md` changes
- Infographic comparison across multiple threat model runs
- Embedding infographic in `threat-report.md` (separate file output)
- SVG fallback generation for environments without Gemini (deferred per PRD open question)
- Attack tree visualization in the infographic (too granular for executive audience)
- Retry/regeneration logic for Gemini API failures (single attempt for MVP)
