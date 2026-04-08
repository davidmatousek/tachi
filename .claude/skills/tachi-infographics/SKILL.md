---
name: tachi-infographics
description: "Domain knowledge for threat infographic generation — infographic specification formats, template-specific section layouts (Baseball Card, System Architecture, Risk Funnel), Gemini API prompt construction rules, and visual design system tokens. Consumed by the threat-infographic agent during specification and image generation."
---

# tachi-infographics

Domain knowledge for generating visual threat infographic specifications and images from tachi pipeline output. This skill provides the section format definitions, template-specific rendering rules, Gemini prompt construction guidelines, and visual design tokens that the threat-infographic agent uses to produce presentation-ready infographic specifications.

## Domain Overview

The infographic generation pipeline transforms structured threat model output into two deliverables per template:

1. **Infographic Specification** (`threat-{template-name}-spec.md`) -- A 6-section structured document containing all data points, color coding, layout instructions, and text content needed to render a presentation-ready infographic. This is the primary deliverable.
2. **Infographic Image** (`threat-{template-name}.jpg`) -- A JPEG image rendered from the specification via Gemini API. This is a best-effort deliverable, conditional on API key availability.

The pipeline supports five templates:

| Template | Purpose | Audience |
|----------|---------|----------|
| Baseball Card | Compact risk summary dashboard with donut chart, heat map, and finding cards | Executive overview |
| System Architecture | Annotated architecture diagram with trust zones, attack surface badges, and data flows | Security architects |
| Risk Funnel | 4-tier vertical funnel showing progressive risk reduction through the pipeline | Risk management |
| MAESTRO Stack | Vertical seven-layer stack diagram showing finding counts and highest severities per MAESTRO layer (L1-L7) | CISO / security management |
| MAESTRO Heatmap | Component-by-layer grid with severity coloring at each intersection | Security engineers |

Each template shares the same Sections 1-4 format (metadata, risk distribution, coverage heat map, top findings) but has a unique Section 5 (Architecture Threat Overlay) layout.

### Template Shorthands

| Shorthand | Expands To | Description |
|-----------|-----------|-------------|
| `all` | `baseball-card`, `system-architecture`, `risk-funnel` | Generate all three core templates |
| `maestro` | `maestro-stack`, `maestro-heatmap` | Generate both MAESTRO templates sequentially |
| `corporate-white` | `baseball-card` | Legacy alias |

When the infographic command receives `maestro` as the template value, it expands to `["maestro-stack", "maestro-heatmap"]` and generates both sequentially. The MAESTRO templates require MAESTRO layer data in threats.md (Feature 084); when MAESTRO data is absent, a graceful empty state is rendered.

## Data Source Types

The infographic agent consumes one of three data source types, auto-detected by richness:

| Data Source | Risk Label | Score Type | Pipeline Stage |
|-------------|-----------|------------|----------------|
| `compensating-controls` | Residual Risk | Post-control residual scores | After control analysis |
| `risk-scores` | Inherent Risk | Quantitative composite scores | After risk scoring |
| `threats` | Severity | Qualitative severity levels | After threat modeling |

## Loading Table

Reference files are loaded on-demand by the threat-infographic agent at specific workflow phases using the Read tool.

| Reference | File | Load When |
|-----------|------|-----------|
| Infographic Specifications | `references/infographic-specifications.md` | Generating Sections 1-4 of any template specification |
| Template-Specific Formats | `references/template-specific-formats.md` | Generating Section 5 for any template (Baseball Card, System Architecture, or Risk Funnel) |
| Gemini Prompt Construction | `references/gemini-prompt-construction.md` | Constructing the Gemini API image generation prompt after specification is complete |
| Visual Design System | `references/visual-design-system.md` | Generating Section 6 (Visual Design Directives) and populating template styling |
