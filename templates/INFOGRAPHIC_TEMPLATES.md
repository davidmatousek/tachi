# Infographic Templates

Tachi supports multiple infographic design templates. Each template defines the visual
layout, color palette, typography, zone specifications, and Gemini prompt structure
for infographic generation.

By default, **both** built-in templates are generated on every run.

## Available Templates

| Template | File | Description |
|----------|------|-------------|
| baseball-card | `infographic-baseball-card.md` | Compact risk summary dashboard: donut chart, STRIDE+AI coverage heat map, critical finding cards, and architecture overlay strip. Stats at a glance. |
| system-architecture | `infographic-system-architecture.md` | Annotated architecture diagram: trust zones stacked by trust level, components with attack surface badges, data flow arrows colored by severity, finding IDs overlaid. |

**Alias**: `corporate-white` maps to `baseball-card` (backward compatibility).

## Output Files

| Template | Spec File | Image File |
|----------|-----------|------------|
| baseball-card | `threat-baseball-card-spec.md` | `threat-baseball-card.jpg` |
| system-architecture | `threat-system-architecture-spec.md` | `threat-system-architecture.jpg` |

## Using Templates

### Via `/threat-model` command

```bash
# Default — generates BOTH templates
/threat-model docs/security/architecture.md

# Only Baseball Card
/threat-model docs/security/architecture.md --infographic-template baseball-card

# Only System Architecture
/threat-model docs/security/architecture.md --infographic-template system-architecture

# Explicit both (same as default)
/threat-model docs/security/architecture.md --infographic-template all
```

### Via natural language

```
Run tachi threat analysis on my architecture. Generate only the baseball-card infographic.
```

## Creating a Custom Template

1. Copy an existing template as a starting point:
   ```bash
   cp .claude/agents/tachi/templates/infographic-baseball-card.md \
      .claude/agents/tachi/templates/infographic-my-design.md
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

## Template Requirements

Every template MUST include:

1. **Gemini Prompt Template** section with `{placeholders}` — this is the primary deliverable
2. **Color Palette** with hex codes for all 5 severity levels
3. **Gemini API Configuration** (model, fallback, aspect ratio)
4. **Layout** description (zones, proportions)

The infographic agent validates that these sections exist before using a template.

Custom templates survive tachi updates — `cp -r` merges without deleting your additions.
