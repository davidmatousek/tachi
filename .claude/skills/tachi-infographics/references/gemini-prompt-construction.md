# Gemini Prompt Construction

Rules and patterns for constructing Gemini API image generation prompts from infographic specification data. This reference covers prompt hygiene, placeholder mapping, design philosophy, prompt framing, color specification, and the fallback prompt structure.

---

## Design Template Loading

After generating the specification (`threat-{template-name}-spec.md`), construct a Gemini image generation prompt using the active design template.

### Template Location

Load `templates/tachi/infographics/infographic-{name}.md` and use its **Gemini Prompt Template** section. Replace all `{placeholders}` with actual data from the infographic spec.

- If template is `corporate-white`, map to `baseball-card`
- Default template: `baseball-card`
- If the template file is not available: use the fallback prompt structure at the end of this document

### Heat Map Cell Grid Placeholder

**`{heat_map_cell_grid}` placeholder**: Populate from the Cell-Level Grid in Section 3. Format as a plain-text grid listing each component row with its per-category severity:

```
MCP Server: S=High, T=High, R=—, I=Medium, D=—, E=High, AG=—, LLM=—
```

One line per component. This explicit enumeration prevents Gemini from inferring incorrect severity labels.

---

## Prompt Hygiene (Mandatory)

When constructing the Gemini prompt from specification data, follow these rules to prevent technical metadata from appearing as visible text in the generated image:

### Rule 1: Strip Hex Color Codes

Never include `#RRGGBB` values in data placeholder text. Use severity names only: "Critical", "High", "Medium", "Low". The template's STYLING DIRECTIVES block already tells Gemini which colors to use -- repeating hex codes in data text causes Gemini to render them as visible characters.

### Rule 2: Strip CSS Values

Never include pixel sizes (`12px`, `32px`), opacity values (`20% opacity`), Tailwind class names (`Slate-600`), or shadow specs in data placeholder text.

### Rule 3: Strip the Color Column

When extracting data from Section 2 (Risk Distribution) tables, exclude the `Color` column entirely. Only use Severity, Count, and Percentage columns.

### Rule 4: Strip the Hex/Tailwind Columns

When extracting from Section 6 (Visual Design Directives) color palette tables, do NOT copy these values into data placeholders. The template already encodes the color mapping.

### Rule 5: Data Placeholders Are for Content Only

`{tier_N_data}`, `{sidebar_metrics}`, `{finding_cards_text}`, `{flow_annotations}`, `{zone_descriptions}`, `{finding_legend_entries}` -- these should contain ONLY labels, numbers, percentages, finding IDs, component names, and natural-language descriptions.

### Correct Example

```
Tier 1 (widest, 100% width): "Threats Identified" — 39 findings: 8 Critical, 10 High, 13 Medium, 3 Low. Dominant color: yellow (Medium is highest count).
```

### Incorrect Example (hex codes leak into image)

```
Tier 1 (widest, 100% width): "Threats Identified" — 39 findings — 8C #DC2626 / 10H #EA580C / 13M #CA8A04 / 3L #2563EB. Dominant Color: #CA8A04 (Yellow-600).
```

---

## Prompt Framing

Frame the entire prompt as a business document visualization request. Use language such as "risk assessment summary," "security posture overview," and "organizational risk dashboard."

**DO NOT** use attack-specific terminology (e.g., "exploit," "vulnerability chain," "attack vector," "privilege escalation") in the image prompt -- this minimizes content policy rejection risk from the Gemini API.

---

## Design Philosophy

Every Gemini prompt should lead with the visual quality target before any data. The prompt communicates two things:

1. **Aesthetic intent** (first paragraph): How the final image should FEEL -- polished, premium, boardroom-ready
2. **Data content** (remaining paragraphs): What data to include and where

Never send a data-only prompt. Gemini interprets dense technical specifications literally, producing flat, spreadsheet-like output. Leading with aesthetic language primes the model for visual quality.

---

## Color Specification

Hex codes belong ONLY in the template's STYLING DIRECTIVES block -- never in data content placeholders. The design templates already encode the severity-to-color mapping in their styling preamble.

**Reference palette** (for template STYLING DIRECTIVES only -- never in data text):

| Severity | Hex Code | Natural Language |
|----------|----------|------------------|
| Critical | `#DC2626` | red |
| High | `#EA580C` | orange |
| Medium | `#EAB308` | yellow |
| Low | `#4169E1` | blue |
| Informational/neutral | `#6B7280` | gray |
| Background (dark theme) | `#1E293B` | dark navy |
| Text on dark | `#FFFFFF` | white |

**In data content**: Use natural language color names: "red", "orange", "yellow", "blue". Gemini reliably interprets these when the STYLING DIRECTIVES block has already established the mapping.

---

## Risk Label Mapping

Apply these labels in the Gemini prompt based on `metadata.data_source_type`:

| Data Source Type | Risk Label |
|------------------|-----------|
| `compensating-controls` | Residual Risk |
| `risk-scores` | Inherent Risk |
| `threats` | Severity |

---

## Gemini API Configuration

```yaml
gemini_config:
  default_model: "gemini-3-pro-image-preview"
  resolution: "2K"
```

- **default_model**: The primary Gemini model for image generation. Configurable -- do not hardcode.
- **resolution**: Target output resolution. "2K" produces images at approximately 1920x1080 for 16:9 aspect ratio.

---

## Image Generation Parameters

### API Request

**Endpoint**:
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent
```

Where `{model_id}` is the configured model (default: `gemini-3-pro-image-preview`).

**Request Headers**:
```
Content-Type: application/json
x-goog-api-key: {GEMINI_API_KEY}
```

**Request Body**:
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "{constructed_narrative_prompt}"
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "aspectRatio": "16:9",
    "imageSize": "2K"
  }
}
```

### Response Parsing

1. Check that the response contains a `candidates` array with at least one entry
2. Iterate through `candidates[0].content.parts[]`
3. Find the part where `inline_data` is present and `inline_data.mime_type` starts with `image/`
4. Extract the `inline_data.data` field (base64-encoded image data)
5. Decode the base64 data
6. Save the decoded bytes as `threat-{template-name}.jpg` in the output directory alongside the specification
7. Set `image_generated: true` in the specification frontmatter

If no `inline_data` part with an image MIME type is found in the response, treat this as an API error (see Error Handling in the agent prompt).

---

## Fallback Prompt Structure

This fallback is used ONLY if the design template file cannot be loaded. It follows the same hygiene rules -- no hex codes in data content.

```
Create a professional security threat infographic for "{project_name}" with the following layout:

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, or technical specifications as visible text in the image.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: clean white
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- Layout: 16:9 landscape, modern corporate aesthetic

DATA CONTENT (render this as visible text):

TOP SECTION: Title "Threat Model: {project_name}" with date "{date}" and "CONFIDENTIAL" badge. Subtitle: "{description} — {total_findings} Findings Across {category_count} Threat Categories".

LEFT PANEL: Donut chart showing risk distribution: {critical_count} Critical (red), {high_count} High (orange), {medium_count} Medium (amber), {low_count} Low (blue). Center text "{total_findings} findings". Below the donut: severity legend with counts and percentages. Below that: "RISK POSTURE: {risk_posture}" in {posture_color}, with "{critical_high_pct}% of findings rated High or Critical".

CENTER PANEL: Heat map grid titled "Coverage Heat Map" with {component_count} components as rows and 8 threat categories as columns (S, T, R, I, D, E, AG, LLM). Each cell MUST use the exact severity from this grid — do not infer or guess cell values:
{heat_map_cell_grid}
Color each cell by its severity: red for Critical, orange for High, amber for Medium, blue for Low, light gray for analyzed with no findings ("—"), white for not applicable. Components sorted by finding count descending. Show finding count or severity letter in each cell.

RIGHT PANEL: {critical_count} critical finding cards in a vertical stack. Each card has: a severity-colored left border accent, finding ID in monospace (e.g., "S-1"), component name in bold, and a one-line threat description. Cards: {finding_cards_text}.

BOTTOM STRIP: Simplified architecture diagram showing {zone_count} trust zones ({zone_names}) as labeled boxes. Components placed inside their zones. Data flow arrows between zones colored by highest severity: {flow_annotations}. Trust boundary crossings annotated with finding IDs. Correlation callouts where cross-category threats overlap: {correlation_annotations}.

FOOTER: "Generated by Tachi Threat Modeling Framework — OWASP STRIDE + AI Threat Analysis"

No hex codes, color values, or technical specifications should appear as visible text.
```
