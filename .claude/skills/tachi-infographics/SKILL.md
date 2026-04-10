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

The pipeline supports six templates:

| Template | Purpose | Audience |
|----------|---------|----------|
| Baseball Card | Compact risk summary dashboard with donut chart, heat map, and finding cards | Executive overview |
| System Architecture | Annotated architecture diagram with trust zones, attack surface badges, and data flows | Security architects |
| Risk Funnel | 4-tier vertical funnel showing progressive risk reduction through the pipeline | Risk management |
| MAESTRO Stack | Vertical seven-layer stack diagram showing finding counts and highest severities per MAESTRO layer (L1-L7) | CISO / security management |
| MAESTRO Heatmap | Component-by-layer grid with severity coloring at each intersection | Security engineers |
| Executive Architecture | Portrait layered architecture diagram with Critical/High threat callouts, positioned immediately after the Executive Summary in the compiled PDF | CISO / board / executive sponsors |

The first five templates share the same Sections 1-4 format (metadata, risk distribution, coverage heat map, top findings) but have a unique Section 5 (Architecture Threat Overlay) layout. Executive Architecture uses a distinct six-section structure (Metadata, Architecture Layers, Threat Callouts, Severity Distribution, Visual Layout Directives, Gemini Prompt Construction Notes) and is the only template rendered in portrait orientation — see `references/executive-architecture.md` for the full specification.

### Template Shorthands

| Shorthand | Expands To | Description |
|-----------|-----------|-------------|
| `all` | `baseball-card`, `system-architecture`, `risk-funnel`, `executive-architecture` | Generate all four core templates (conditionally extends with MAESTRO templates when MAESTRO data is present) |
| `maestro` | `maestro-stack`, `maestro-heatmap` | Generate both MAESTRO templates sequentially |
| `exec` | `executive-architecture` | Single-template alias (not a compound expansion) |
| `corporate-white` | `baseball-card` | Legacy alias |

When the infographic command receives `maestro` as the template value, it expands to `["maestro-stack", "maestro-heatmap"]` and generates both sequentially. The MAESTRO templates require MAESTRO layer data in threats.md (Feature 084); when MAESTRO data is absent, a graceful empty state is rendered.

The `executive-architecture` template (and its `exec` alias) is distinct from the other templates in two ways: it is rendered in portrait orientation rather than 16:9 landscape, and it uses a six-section structure instead of the shared Sections 1-5 format. When no Critical or High severity findings exist in the threat model, the spec file is still produced but the image is not — see `references/executive-architecture.md` for the full skip behavior specification.

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
| Infographic Specifications | `references/infographic-specifications.md` | Generating Sections 1-4 of any shared-format template (Baseball Card, System Architecture, Risk Funnel, MAESTRO Stack, MAESTRO Heatmap) |
| Template-Specific Formats | `references/template-specific-formats.md` | Generating Section 5 for any shared-format template |
| Executive Architecture | `references/executive-architecture.md` | Generating the full six-section spec for the `executive-architecture` template (or its `exec` alias) — distinct section structure, portrait orientation, and PDF positioning rules |
| Gemini Prompt Construction | `references/gemini-prompt-construction.md` | Constructing the Gemini API image generation prompt after specification is complete |
| Visual Design System | `references/visual-design-system.md` | Generating Section 6 (Visual Design Directives) and populating template styling for the shared-format templates |
