# Research Summary: Risk Reduction Funnel Infographic Template

## Knowledge Base Findings
- No KB entries found (KB not yet set up for this project)

## Codebase Analysis

### Existing Templates (Pattern to Follow)
- **Baseball Card**: `.claude/agents/tachi/templates/infographic-baseball-card.md` (220 lines) — dark theme (#1E293B), horizontal 4-zone dashboard
- **System Architecture**: `.claude/agents/tachi/templates/infographic-system-architecture.md` (422 lines) — white theme, vertical zone stack with annotated architecture

### Mandatory Template Structure (9 sections)
1. Frontmatter comment with purpose statement
2. ASCII layout diagram (16:9 landscape, zones with percentages)
3. Style table (8-10 rows: background, aspect ratio, font, palette, aesthetic, radius, shadow, spacing)
4. Color palette table (severity colors: Critical=#DC2626, High=#EA580C, Medium=#CA8A04, Low=#2563EB, Note=#6B7280 + background/text/border)
5. Typography table (title, subtitle, headers, body, data, IDs, footer)
6. Zone specifications (detailed per-zone content, placement rules)
7. Gemini Prompt Template (code block, all `{placeholders}`, aesthetic-first, no attack terminology)
8. Gemini API Configuration (model: gemini-3-pro-image-preview, fallback: gemini-3.1-flash-image-preview, 16:9, 2K)
9. Accessibility section (color+label distinction, 4.5:1 contrast)

### Agent Registry
- **Agent**: `.claude/agents/tachi/threat-infographic.md` (916 lines)
- Template registry format: `templates: {name}: .claude/agents/tachi/templates/infographic-{name}.md`
- Must add: `risk-funnel: .claude/agents/tachi/templates/infographic-risk-funnel.md`

### Command Registry
- **Command**: `.claude/commands/infographic.md` (241 lines)
- Valid `--template` values: `baseball-card`, `system-architecture`, `all` (+ alias `corporate-white`)
- Must add `risk-funnel` as valid value

### Output Schema
- **Schema**: `schemas/infographic.yaml` v1.0 (126 lines, 6 required sections)
- Frontmatter: schema_version, template, date, source_file, data_source_type, finding_count, image_generated
- Sections: 1.Metadata, 2.Risk Distribution, 3.Coverage Heat Map, 4.Top Critical Findings, 5.Architecture Threat Overlay, 6.Visual Design Directives

### Data Source Auto-Detection (3-tier hierarchy)
1. `compensating-controls.md` → residual risk (richest)
2. `risk-scores.md` → quantitative composite scores
3. `threats.md` → qualitative severity counts

### Output Naming Convention
- Spec: `threat-{template-name}-spec.md`
- Image: `threat-{template-name}.jpg`

## Architecture Constraints

### ADRs Directly Relevant
- **ADR-010**: Fresh context isolation — agent receives only input file content, not pipeline state
- **ADR-014**: Spec-first architecture — markdown spec is primary deliverable; image is best-effort
- **ADR-016**: Pipeline decoupling — `/infographic` is standalone command, not pipeline phase

### Key Constraints
- Co-located `threats.md` required when primary source is `risk-scores.md` or `compensating-controls.md`
- Gemini prompt must lead with aesthetic intent before data (prevents flat/spreadsheet output)
- No attack terminology in prompts (content policy compliance)
- Max 15-20 distinct text labels per infographic
- All 6 spec sections required and non-empty per schema

### Dependencies
- PRD-018 (Threat Infographic Agent): agent architecture, spec generation, Gemini pipeline
- PRD-035 (Quantitative Risk Scoring): composite scores, severity bands
- PRD-036 (Compensating Controls): control coverage, residual risk, reduction factors
- PRD-039 (Standalone /infographic Command): command framework, --template flag, auto-detection
- PRD-048 (Tiered Detection & Residual Risk): 3-tier auto-detection, residual risk extraction

## Industry Research

### Funnel Visualization Best Practices
- 4-6 tiers recommended (3 minimum, 7 maximum) — PRD's 4 tiers in sweet spot
- Left-aligned labels + right sidebar follows executive dashboard conventions
- Proportional tier widths mandatory; minimum visual narrowing is valid when actual reduction is small
- Gradient connectors between tiers preferred over hard edges

### Executive Risk Communication
- "What? So what? Now what?" narrative maps to funnel tiers
- 5-6 metrics maximum in executive dashboards
- Business language, not technical jargon
- Trend/improvement narrative is what stakeholders want

### Market Gap Confirmed
- No commercial tool (IriusRisk, ThreatModeler, Microsoft TMT, OWASP Threat Dragon) provides risk reduction funnel
- Closest academic framework: bow-tie risk model (before/after controls)
- PRD-053's design is a novel synthesis confirmed as differentiated

### Color Strategy Note
- Standard funnels use single-hue gradient; PRD uses severity-mapped colors
- Severity colors add domain-appropriate information density — reasonable divergence

## Recommendations for Spec
- Follow the exact 9-section template structure from existing templates
- Use dark theme (consistent with baseball-card for premium aesthetic)
- Section 5 needs new "funnel-tier" format (alongside existing tabular and spatial formats)
- Graceful degradation is a genuine innovation — no industry precedent for ghost tiers
- Specify Gemini prompt with photorealistic 3D funnel, executive boardroom aesthetic
- Register template in both agent and command files
- Schema v1.0 is sufficient — no modifications needed for new template
