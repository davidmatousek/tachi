# Infographic Templates

Tachi supports multiple infographic design templates. Each template defines the visual
layout, color palette, typography, zone specifications, and Gemini prompt structure
for infographic generation.

By default, the three core templates (`baseball-card`, `system-architecture`, `risk-funnel`) are generated on every run.

## Available Templates

| Template | File | Description |
|----------|------|-------------|
| baseball-card | `infographic-baseball-card.md` | Compact risk summary dashboard: donut chart, STRIDE+AI coverage heat map, critical finding cards, and architecture overlay strip. Stats at a glance. |
| system-architecture | `infographic-system-architecture.md` | Annotated architecture diagram: trust zones stacked by trust level, components with attack surface badges, data flow arrows colored by severity, finding IDs overlaid. |
| risk-funnel | `infographic-risk-funnel.md` | 4-tier vertical funnel showing progressive risk reduction through the pipeline stages. Risk management audience. |
| maestro-stack | `infographic-maestro-stack.md` | Vertical seven-layer stack diagram showing finding counts and highest severities per MAESTRO layer (L1-L7). CISO / security management audience. |
| maestro-heatmap | `infographic-maestro-heatmap.md` | Component-by-layer grid with severity coloring at each intersection. Identifies hotspot component-layer pairs for remediation prioritization. |

**Aliases and Shorthands**:
- `corporate-white` maps to `baseball-card` (backward compatibility)
- `all` generates `baseball-card`, `system-architecture`, `risk-funnel` (core templates)
- `maestro` generates both `maestro-stack` and `maestro-heatmap` sequentially

## Output Files

| Template | Spec File | Image File |
|----------|-----------|------------|
| baseball-card | `threat-baseball-card-spec.md` | `threat-baseball-card.jpg` |
| system-architecture | `threat-system-architecture-spec.md` | `threat-system-architecture.jpg` |
| risk-funnel | `threat-risk-funnel-spec.md` | `threat-risk-funnel.jpg` |
| maestro-stack | `threat-maestro-stack-spec.md` | `threat-maestro-stack.jpg` |
| maestro-heatmap | `threat-maestro-heatmap-spec.md` | `threat-maestro-heatmap.jpg` |

## Using Templates

### Via `/tachi.infographic` command (standalone)

```bash
# Default — generates all 3 core templates
/tachi.infographic

# Single template
/tachi.infographic --template baseball-card
/tachi.infographic --template system-architecture
/tachi.infographic --template risk-funnel

# MAESTRO templates (require MAESTRO layer data from Feature 084)
/tachi.infographic --template maestro-stack
/tachi.infographic --template maestro-heatmap
/tachi.infographic --template maestro          # shorthand: generates both MAESTRO templates

# Custom output directory
/tachi.infographic --output-dir reports/infographics/
```

### Via `/tachi.threat-model` command

```bash
# Default — generates all 3 core templates
/tachi.threat-model docs/security/architecture.md

# Only Baseball Card
/tachi.threat-model docs/security/architecture.md --infographic-template baseball-card

# Only System Architecture
/tachi.threat-model docs/security/architecture.md --infographic-template system-architecture

# Explicit all (same as default)
/tachi.threat-model docs/security/architecture.md --infographic-template all
```

### Via natural language

```
Run tachi threat analysis on my architecture. Generate only the baseball-card infographic.
```

## Creating a Custom Template

1. Copy an existing template as a starting point:
   ```bash
   cp templates/tachi/infographics/infographic-baseball-card.md \
      templates/tachi/infographics/infographic-my-design.md
   ```

2. Edit the following sections in your new template:
   - **Layout** — zone structure, proportions, arrangement
   - **Style** — background color, aesthetic description
   - **Color Palette** — severity colors (keep semantics: Critical=red, High=orange, Medium=yellow, Low=blue)
   - **Typography** — font sizes, weights
   - **Zone Specifications** — what goes in each zone, how data is presented
   - **Gemini Prompt Template** — the actual prompt sent to Gemini (most important section)

3. The template file name must follow the pattern: `infographic-{name}.md`

4. Use `{placeholders}` in the Gemini Prompt Template for dynamic data:

   | Placeholder | Source |
   |-------------|--------|
   | `{project_name}` | Spec Section 1: Metadata |
   | `{date}` | Spec Section 1: Metadata |
   | `{total_findings}` | Spec Section 2: Risk Distribution |
   | `{category_count}` | Spec Section 3: Coverage Heat Map columns |
   | `{critical_count}` | Spec Section 2: Risk Distribution |
   | `{high_count}` | Spec Section 2: Risk Distribution |
   | `{medium_count}` | Spec Section 2: Risk Distribution |
   | `{low_count}` | Spec Section 2: Risk Distribution |
   | `{risk_posture}` | Spec Section 2: Risk Posture Indicator |
   | `{posture_color}` | Spec Section 2: severity color of posture |
   | `{critical_high_pct}` | Computed: (critical+high)/total * 100 |
   | `{component_count}` | Spec Section 3: row count |
   | `{finding_cards_text}` | Spec Section 4: formatted finding summaries |
   | `{zone_count}` | Spec Section 5: trust zone count |
   | `{zone_names}` | Spec Section 5: comma-separated zone names |
   | `{zone_descriptions}` | Spec Section 5: per-zone component/flow descriptions |
   | `{flow_descriptions}` | Spec Section 5: data flow severity descriptions |
   | `{flow_annotations}` | Spec Section 5: data flow severity descriptions |
   | `{boundary_descriptions}` | Spec Section 5: trust boundary crossing descriptions |
   | `{correlation_annotations}` | Spec Section 5: correlation group descriptions |
   | `{description}` | Spec Section 1: input format or system description |
   | `{maestro_layer_distribution}` | MAESTRO layer finding counts and highest severities (maestro-stack) |
   | `{most_exposed_layer}` | Layer with highest finding count (maestro-stack) |
   | `{maestro_heatmap}` | Component-layer intersection grid with severity coloring (maestro-heatmap) |

## Template Requirements

Every template MUST include:

1. **Gemini Prompt Template** section with `{placeholders}` — this is the primary deliverable
2. **Color Palette** with hex codes for all 5 severity levels
3. **Gemini API Configuration** (model, fallback, aspect ratio)
4. **Layout** description (zones, proportions)

The infographic agent validates that these sections exist before using a template.

Custom templates survive tachi updates — `cp -r` merges without deleting your additions.
