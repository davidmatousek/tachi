# Gemini Prompt Construction

Rules and patterns for constructing Gemini API image generation prompts from infographic specification data. This reference covers prompt hygiene, placeholder mapping, design philosophy, prompt framing, color specification, and the fallback prompt structure.

---

## Design Template Loading — Prompt Scaffold (Option D)

The extraction script (`scripts/extract-infographic-data.py`) outputs a `prompt_scaffold` object in the JSON with two fields:
- **`preamble`**: the opening aesthetic instruction, IMPORTANT note, and STYLING DIRECTIVES block — everything up to and including the "DATA CONTENT (render this as visible text):" header.
- **`postamble`**: the FOOTER specification and closing aesthetic instruction.

### MANDATORY: Use Scaffold Verbatim

When `prompt_scaffold` is present in the JSON output, you **MUST** construct the Gemini prompt by:

1. **Copy `prompt_scaffold.preamble` VERBATIM** as the start of the prompt. Do NOT rewrite, paraphrase, or modify ANY part of it — the background color, styling directives, layout instructions, and aesthetic target are locked.
2. **Write the DATA CONTENT sections** using data from the JSON (severity counts, findings, heat map grid, etc.). This is the ONLY section where you have creative control.
3. **Copy `prompt_scaffold.postamble` VERBATIM** as the end of the prompt. Do NOT rewrite the footer text or closing instructions.

```
[preamble — VERBATIM from JSON, includes opening + IMPORTANT + STYLING DIRECTIVES + "DATA CONTENT" header]

[Your DATA CONTENT sections — written from JSON data, with specific counts, scores, finding descriptions]

[postamble — VERBATIM from JSON, includes FOOTER + closing aesthetic instruction]
```

**Why this matters**: The scaffold locks the visual design (dark navy background, severity colors, typography, layout). Previous runs where the agent rewrote the scaffold produced white-background flat images instead of the premium dark-themed 3D visuals the templates specify.

### Fallback (no scaffold)

If `prompt_scaffold` is NOT present in the JSON, route by template — this is expected only for `executive-architecture`; every other template ships a scaffold:

- **`executive-architecture`**: never fall back to this reference's dashboard prompt at the end of this document. Read `.claude/skills/tachi-infographics/references/executive-architecture.md` for both its own `## Gemini API Configuration` section (the request parameters) and its `VERBATIM PROMPT BLOCK` (the prompt text — see the Verbatim-Lock Rule below). That file *is* this template's "template file"; none exists under `templates/tachi/infographics/` for it.
- **Any other template with no scaffold** (for example, an older script version): load `templates/tachi/infographics/infographic-{name}.md` and use its **Gemini Prompt Template** section. Replace all `{placeholders}` with actual data from the infographic spec.
  - If template is `corporate-white`, map to `baseball-card`.
  - Default template: `baseball-card`.
  - If the template file is not available: use the fallback prompt structure at the end of this document.

---

## Verbatim-Lock Rule for Executive-Architecture Template

The `executive-architecture` template carries a stricter verbatim-lock contract than the scaffold-based templates above. Per spec FR-212-6 (`specs/212-improve-executive-architecture-infographic/spec.md`), the prompt block published in the **VERBATIM PROMPT BLOCK** section of `.claude/skills/tachi-infographics/references/executive-architecture.md` MUST be copied verbatim into the Gemini API request — there is NO runtime composition of aesthetic, structural, or palette language for this template.

### Why a separate rule

The scaffold path (Option D, above) ships the locked text in the JSON output of `scripts/extract-infographic-data.py` as a `prompt_scaffold` object. The executive-architecture template uses the **fallback path** (no `prompt_scaffold` object) because its prompt was historically composed at runtime from the template skill reference. F-212 inverts that: the prompt is now locked in the skill reference file rather than composed at runtime, but the lock lives in the markdown file rather than in JSON. This rule documents that distinction so consumers do not mistakenly recompose the prompt under the assumption that the scaffold path is the only locked path.

### What is locked

Everything between the `=== BEGIN VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===` and `=== END VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===` markers in `executive-architecture.md` is locked:

- The `"schematic diagram with shapes and arrows"` opening directive (FR-212-2 — defeats the text-only failure mode in current Gemini image-gen practice)
- The IMPORTANT pre-amble forbidding hex codes / pixel values as visible text
- The full STYLING DIRECTIVES block including: layer band ordering, the 5-pastel layer-fill cycle (`#F0F4FF`, `#FFF4F0`, `#F0FFF4`, `#FFF0F8`, `#F8F0FF`), severity-colored node borders (Critical `#DC2626`, High `#EA580C` — inherited unchanged from `visual-design-system.md`), inter-layer directional-arrow directive with explicit arrowhead requirement, leader-line callout anchoring directive, the compact-badge empty-layer treatment, and the single-zone fallback caption directive
- The DATA CONTENT section headers (TITLE, LAYER STACK, CALLOUTS, EMPTY-LAYER BADGES, FOOTER)
- The closing aesthetic instruction

### What is NOT locked (slot substitution only)

Only the bracketed `<<...>>` data slots inside the locked block are filled at runtime from the infographic specification payload (`threat-executive-architecture-spec.md`):

- `<<project_name>>` — from `metadata.project_name`
- `<<layer_block>>` — composed from `layers[]`
- `<<callout_block>>` — composed from `callouts[]` (6–8 entries)
- `<<empty_layer_block>>` — one badge line per layer with zero qualifying findings
- `<<single_zone_caption>>` — emitted only on the single-zone edge case

### What is NOT permitted

- Rewriting, paraphrasing, condensing, or expanding any directive inside the locked block.
- Substituting alternate severity colors, alternate layer-fill pastels, or alternate font choices.
- Reordering the directives or moving the styling block.
- Composing the prompt from snippets stored elsewhere (e.g., `infographic-specifications.md`).
- Suppressing the `"schematic diagram with shapes and arrows"` opening — this directive is structurally load-bearing for arrow rendering.

### How to consume

1. Read `.claude/skills/tachi-infographics/references/executive-architecture.md`.
2. Locate the `=== BEGIN VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===` marker.
3. Copy the text between the BEGIN and END markers verbatim.
4. Substitute the bracketed `<<...>>` slots with payload data per the slot-mapping table in `executive-architecture.md`.
5. Send as the Gemini API `text` part. Do NOT modify any text outside the slots.

### Cross-reference

- Source-of-truth file: `.claude/skills/tachi-infographics/references/executive-architecture.md` (Gemini Prompt Block — VERBATIM section)
- Spec rule: `specs/212-improve-executive-architecture-infographic/spec.md` FR-212-6
- Palette source: `.claude/skills/tachi-infographics/references/visual-design-system.md` (severity colors, inherited)
- Palette extension rationale: `specs/212-improve-executive-architecture-infographic/spec.md` Palette Strategy section (EXTEND-with-additive)

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
  chain:
    - "gemini-3-pro-image"      # primary
    - "gemini-3.1-flash-image"  # fallback
  default_model: "gemini-3-pro-image"
```

- **chain**: the image models to try, in order. `default_model` is always `chain[0]`.
- **Walk set (plan PD-14)**: the chain is walked — the next model in `chain` is tried — only when a model is unavailable **to the calling key**: HTTP 404 `NOT_FOUND` or 403 `PERMISSION_DENIED`. Every other non-2xx (400, 429, 5xx, …) is **not walked** — see Error Guidance below. When every chain model returns 404 or 403, the chain is exhausted: this is logged at Error, and the final summary names each model tried with its status and message.
- Both chain entries are current GA image-generation models, distinct from their base text-model counterparts (a `-pro` or `-flash` text model does not support image-generation output). Always send the exact ID from `chain`, never a shortened or aliased form.

**Key → field table** (the agent maps the *active template's* `## Gemini API Configuration` block through this table to build the request):

| Template key | Request |
|---|---|
| `model` | `models/{model}:generateContent` |
| `fallback_model` | the next model, tried only when the model is unavailable to the key: 404 `NOT_FOUND` or 403 `PERMISSION_DENIED` |
| `response_modalities` | `generationConfig.responseModalities` |
| `aspect_ratio` | `generationConfig.imageConfig.aspectRatio` |
| `image_size` | `generationConfig.imageConfig.imageSize` |

**Routing.** Each of the five scaffolded templates carries its own `## Gemini API Configuration` block in `templates/tachi/infographics/infographic-{name}.md`; `executive-architecture` carries its own block in `executive-architecture.md` (see "Fallback (no scaffold)" above, and that file's own "Gemini API Configuration" section). The agent reads the *active template's* block and maps it through the table above — it never sends one hard-coded body for every template.

**Provenance** (endpoint `models/{model}:generateContent`; verified live per PM ruling P-10.3 / plan PD-3):

- `Verified: models/gemini-3-pro-image:generateContent · gemini-3-pro-image · 2026-09-28 · aspectRatio 16:9 · imageSize 2K`
- `Verified: models/gemini-3-pro-image:generateContent · gemini-3-pro-image · 2026-09-28 · aspectRatio 3:4 · imageSize 2K`
- `Verified: models/gemini-3.1-flash-image:generateContent · gemini-3.1-flash-image · 2026-09-28 · aspectRatio 16:9 · imageSize 2K`
- `Verified: models/gemini-3.1-flash-image:generateContent · gemini-3.1-flash-image · 2026-09-28 · aspectRatio 3:4 · imageSize 2K`

Retired models: `gemini-3-pro-image-preview` and `gemini-3.1-flash-image-preview` shut down 2026-06-25; `gemini-2.5-flash-image` shuts down 2026-10-02.

---

## Image Generation Parameters

### API Request

**Endpoint**:
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

`{model}` is the active template's configured model, mapped through the table above. Try `chain[0]` first; walk to the next chain model only on a 404 `NOT_FOUND` or 403 `PERMISSION_DENIED` for that model (see "Walk set" above, and Error Guidance below).

**Request Headers**:
```
Content-Type: application/json
x-goog-api-key: {GEMINI_API_KEY}
```

The key is read from the environment and sent only as this header — never as a `?key=` query parameter, never echoed, and never passed to a verbose/trace flag.

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
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

`aspectRatio` and `imageSize` live under `generationConfig.imageConfig` — never as top-level `generationConfig` keys, and no other size-shaped key names this setting. `imageSize` is sent only when the active template's block carries an `image_size` key (true for all six templates today, live-verified honored at every shipped model × ratio combination — see Provenance above); when absent, the API defaults to its standard size.

### Response Parsing

1. Check that the response contains a `candidates` array with at least one entry
2. Iterate through `candidates[0].content.parts[]`
3. Find the part where **`inlineData`** is present and `inlineData.mimeType` starts with `image/`. The SDK spelling (`inline_data` / `inline_data.mime_type`) is accepted too, for callers going through a client library instead of the raw REST body.
4. Extract the `inlineData.data` field (base64-encoded image data)
5. Decode the base64 data
6. Save the decoded bytes as `threat-{template-name}.{ext}` where `{ext}` is derived from the MIME type:
   - `image/jpeg` or `image/jpg` → `.jpg`
   - `image/png` → `.png`
   - Any other `image/*` → the subtype as the extension
   **Do not use a fixed `.jpg` extension for all outputs** — different chain models return different image formats, and writing the wrong bytes under the wrong extension produces a file whose magic bytes and extension disagree (downstream consumers that trust the extension then mislabel the MIME type).
7. Set `image_generated: true` in the specification frontmatter

If no `inlineData` part with an image MIME type is found in a 2xx response, treat this as an API error — the catch-all row in Error Guidance below.

### Error Guidance

The full conditions and their spec/log/chain behavior are the agent's "Error Handling & Graceful Degradation" table (`.claude/agents/tachi/threat-infographic.md`). Summary, per plan PD-14:

| Condition | Chain |
|---|---|
| HTTP 400 (including `FAILED_PRECONDITION`, e.g. an unsupported location) | **Not walked** — every model would reject the same body, and walking would hide the cause. Logged at Error with the API's message and the request-body keys sent |
| HTTP 404 `NOT_FOUND` or 403 `PERMISSION_DENIED` | **Walked**, in chain order |
| Chain exhausted (every model returned 404 or 403) | Logged at Error; the summary names each model tried with its status and message |
| 429 `RESOURCE_EXHAUSTED` | Not walked (single attempt). If this key has no quota for the current model, set that template's `model` to its `fallback_model` in its `## Gemini API Configuration` block |
| Any other non-2xx (5xx and other 4xx), or a 2xx with no image part | Not walked. Logged at Error with the status and the API's message, or "no image part in the response" |

The pipeline is never blocked by an image-generation failure — the specification is always saved.

---

## Fallback Prompt Structure

This fallback is used ONLY if the design template file cannot be loaded. It follows the same hygiene rules -- no hex codes in data content.

```
Create a professional security threat infographic for "{project_name}" with the following layout:

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, or technical specifications as visible text in the image.

The uppercase section labels in this prompt, such as DATA CONTENT and FOOTER, are layout instructions. Do not render them, or any other instruction text, as visible text in the image.
Every finding ID in the image must be one listed on the ALLOWED IDS AND NAMES line below, and every component name must refer to a component listed there. Never show any other ID, and never invent an ID or a component.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: clean white
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- Layout: 16:9 landscape, modern corporate aesthetic

DATA CONTENT (render this as visible text):

TOP SECTION: Title "Threat Model: {project_name}" with date "{date}" and "CONFIDENTIAL" badge. Subtitle: "{description} — {total_findings} Findings Across {category_count} Threat Categories".

LEFT PANEL: Donut chart showing risk distribution: {critical_count} Critical (red), {high_count} High (orange), {medium_count} Medium (amber), {low_count} Low (blue). Center text "{total_findings} findings". Below the donut: severity legend with counts and percentages. Below that: "{risk_posture_label}" in {posture_color}, with "{critical_high_pct}% of findings rated High or Critical".

CENTER PANEL: Heat map grid titled "Coverage Heat Map" with {component_count} components as rows and 8 threat categories as columns (S, T, R, I, D, E, AG, LLM). Each cell MUST use the exact severity from this grid — do not infer or guess cell values:
{heat_map_cell_grid}
Color each cell by its severity: red for Critical, orange for High, amber for Medium, blue for Low, light gray for analyzed with no findings ("—"), white for not applicable. Components sorted by finding count descending. Show finding count or severity letter in each cell.

RIGHT PANEL: {critical_count} critical finding cards in a vertical stack. Each card has: a severity-colored left border accent, finding ID in monospace (e.g., "S-1"), component name in bold, and a one-line threat description. Cards: {finding_cards_text}.

BOTTOM STRIP: Simplified architecture diagram showing {zone_count} trust zones ({zone_names}) as labeled boxes. Components placed inside their zones. Data flow arrows between zones colored by highest severity: {flow_annotations}. Trust boundary crossings annotated with finding IDs. Correlation callouts where cross-category threats overlap: {correlation_annotations}.

FOOTER: "Generated by Tachi Threat Modeling Framework — OWASP STRIDE + AI Threat Analysis"

No hex codes, color values, or technical specifications should appear as visible text.
```
