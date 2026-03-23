# Research Summary: Threat Infographic Agent (F-018)

## Knowledge Base Findings
- No existing KB entries for infographic generation or visual output
- F-015 (Threat Report Agent) is the closest predecessor — established Phase 5 pattern with optional phase, fresh context isolation, and graceful degradation
- Key lesson from F-015: context isolation boundaries are critical — each phase receives only `threats.md` as input, no accumulated pipeline context (ADR-002, ADR-010)

## Codebase Analysis

### Similar Features
- **`agents/threat-report.md`** (F-015): Closest pattern — markdown prompt agent producing narrative report + attack trees from `threats.md`
- **`agents/orchestrator.md`**: Defines 5-phase pipeline; Phase 6 integration follows Phase 5 pattern (optional, default-on, fresh context)

### Patterns to Follow
- Agent prompt file structure: YAML frontmatter → Core Mission → Input Contract → Processing Methodology → Output Specification → Quality Standards → Error Handling → References
- Phase integration pattern: check if enabled → dispatch agent with `threats.md` only → collect results → graceful failure handling
- Opt-out pattern: `--skip-{phase}` flag and/or environment variable

### Data Structures (Critical)
- **`schemas/finding.yaml`** (v1.0): Finding IR with `id`, `category`, `component`, `threat`, `likelihood`, `impact`, `risk_level` (Critical/High/Medium/Low/Note), `mitigation`, `references`
- **`schemas/output.yaml`** (v1.1): Defines `threats.md` structure — Section 6 (Risk Summary) has aggregate counts; Section 5 has Coverage Matrix; Section 7 has Recommended Actions
- **No `schemas/infographic.yaml`** exists — must be created during implementation (architect concern)

### Example Data
- `examples/mermaid-agentic-app/threats.md`: 19 findings (3 Critical, 9 High, 7 Medium, 0 Low), component × category coverage matrix, recommended actions ordered by severity

## Architecture Constraints
- **Fresh context isolation**: Phase 6 receives ONLY `threats.md` as input — no accumulated pipeline context (ADR-002, ADR-010)
- **No application code**: Agent is markdown prompt file; Gemini integration described in prompt instructions, not implemented in code
- **Pipeline isolation**: Phase 6 failures MUST NOT block Phases 1-5 outputs
- **Hub-and-spoke model**: New output schema `schemas/infographic.yaml` required for specification validation
- **Configuration**: Opt-out flag for Phase 6; naming convention follows existing `--skip-report` pattern
- **DoD exception**: Prompt files follow documentation-only DoD path (no production deployment needed)

## Industry Research

### Gemini API Image Generation
- **Recommended model**: `gemini-3-pro-image-preview` (Nano Banana Pro) — best text rendering, reasoning-based composition planning for data-dense layouts
- **Fallback model**: `gemini-3.1-flash-image-preview` — 3x cheaper, suitable for simpler layouts
- **API endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent` with `responseModalities: ["TEXT", "IMAGE"]`
- **Resolution**: 2K default (cost/quality balance), 4K optional; aspect ratio 16:9 for presentation slides
- **Limitations**: No function calling, no code execution, approximate chart proportions, text may need minor corrections
- **Deprecation**: `gemini-2.5-flash-image` scheduled for shutdown October 2, 2026 — do not use

### CVSS Severity Color Standards
- **No official CVSS color standard** — de facto industry consensus exists
- Industry standard: Critical=Red, High=Orange, Medium=Yellow, Low=Green, Info=Gray
- PRD uses Low=Blue (#4169E1) per research §10 — diverges from some industry tools that use Green
- Recommended hex codes: Critical=#DC2626, High=#F97316, Medium=#EAB308, Low=#4169E1 (matching PRD), Info=#6B7280

### Executive Visualization Best Practices
- Limit to 5-6 key visual elements per view
- Lead with business impact, not technical metrics
- Use traffic light protocol (red/yellow/green) for instant communication
- Three-zone layout: Header (risk score) → Distribution (severity breakdown) → Findings (top critical)
- Keep labels to 2-4 words; cap distinct text labels at 15-20 per infographic
- Donut/bar charts preferred over pie charts

### Prompt Engineering for Data-Rich Infographics
- Narrative scene description outperforms keyword lists
- Explicit spatial zone instructions ("top third contains..., middle shows...")
- Include exact hex codes in prompt for color accuracy
- Simplify to 5-6 key metrics rather than full threat model
- Set expectation: "presentation-ready, minor text corrections may be needed"

## Recommendations for Spec
- Frame `threat-infographic-spec.md` as PRIMARY deliverable; image as best-effort (aligns with architect concern)
- Follow F-015 agent structure exactly: YAML header, input/output contracts, methodology, quality standards
- Design three-zone infographic layout: Header → Distribution → Critical Findings
- Use `gemini-3-pro-image-preview` as default model ID (configurable, not hardcoded)
- Cap heat map display at top 8 components by total finding count (addresses open question on truncation)
- Phase 6 opt-out: `--no-infographic` flag + `TACHI_SKIP_INFOGRAPHIC=true` env var (follows PRD naming)
- `threat-report.md` is NOT passed to Phase 6 (fresh context constraint) — spec must declare `threats.md` as sole input
- Define `schemas/infographic.yaml` as implementation task (addresses architect concern)
