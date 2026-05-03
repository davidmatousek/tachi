# Executive Architecture Template

Section format, data source rules, and visual directives for the `executive-architecture` infographic template. This is the only tachi infographic template rendered in **portrait** orientation; all other templates use the standard 16:9 landscape aspect ratio documented in `visual-design-system.md`. Sections 1-4 from `infographic-specifications.md` do NOT apply to this template — the executive-architecture spec uses a distinct six-section structure defined below.

---

## Purpose

Executive-level visualization of the layered system architecture with Critical and High severity threat callouts. The template serves a non-technical audience (CISO, board members, executive sponsors) who read only the first few pages of a security report and need to identify the most exposed architectural layer within their normal attention window.

Unlike the other infographic templates, which are general-purpose dashboards and analytical views, the executive-architecture template is audience-optimized: it trades exhaustive detail for narrative clarity, showing a small number of high-signal callouts anchored to a recognizable layered diagram of the system. The visual idiom is an OpenClaw-style system flow diagram: rounded-rectangle component nodes connected by directional arrows, with leader-lined callouts anchored to specific nodes.

---

## Output Artifacts

| Artifact | File | Notes |
|----------|------|-------|
| Specification | `threat-executive-architecture-spec.md` | Always produced when the template is invoked successfully |
| Image | `threat-executive-architecture.jpg` | Optional — NOT generated when no Critical/High findings exist (see Skip Behavior) |

Both files are written to the threat model output folder alongside the other tachi artifacts (`threats.md`, `risk-scores.md`, `compensating-controls.md`, and any other `threat-*-spec.md` / `threat-*.jpg` pairs).

---

## Invocation

| Form | Command |
|------|---------|
| Full name | `/tachi.infographic --template executive-architecture` |
| Alias | `/tachi.infographic --template exec` |
| Via shorthand | `/tachi.infographic --template all` (expansion includes `executive-architecture`) |

The target directory is the same path argument used by all tachi infographic invocations — a folder containing a tachi threat model output (at minimum `threats.md`). The command auto-detects the richest available data tier using the standard precedence: `compensating-controls.md` > `risk-scores.md` > `threats.md`.

Unlike the `maestro` compound shorthand which expands to two templates, `exec` is a single-template alias and dispatches to exactly one template.

---

## PDF Report Positioning

When the `threat-executive-architecture.jpg` image is present in the output folder, the PDF security report (`/tachi.security-report`) places the rendered image on a dedicated page **immediately after the Executive Summary page and immediately before the Attack Path Analysis section** (or, when no attack paths exist, before whatever section follows the Executive Summary). This is the only infographic template with a fixed page position in the compiled PDF — all other infographic templates appear later in the Visual Analysis section.

The positioning is gated by the `has-executive-architecture` boolean in `report-data.typ`, set by the detection logic in `scripts/extract-report-data.py`. When the image is absent, the PDF renders with no reference to the executive-architecture page and is byte-identical to the pre-F-128 baseline.

The rendered page uses the existing portrait-oriented `infographic-page()` Typst helper and carries a TOC-visible heading "Executive Threat Architecture" plus a brief descriptive caption.

---

## Layer Source

The architectural layers displayed in the diagram are sourced from the threat model output with a two-tier fallback:

| Priority | Source | Field |
|----------|--------|-------|
| Primary | `threats.md` Section 2 (Trust Boundaries / Zones) | Trust zone names and member components |
| Fallback | `threats.md` Section 1 (DFD components) | Grouping by component `type` field |

The primary path produces layers that match the security narrative of the threat model exactly (e.g., "Untrusted Zone", "DMZ", "Internal Services", "Data Tier"). The fallback path groups components by their DFD type classification (Process, Data Store, External Entity, etc.) when no trust boundaries are defined, ensuring the template works on threat models that predate trust-zone annotation.

Layers render ordered from untrusted (top of the portrait layout) to trusted (bottom), following the convention that threats originate at the top of the diagram and propagate downward through trust boundaries.

---

## Callout Selection

Callouts are the narrative annotations attached to layers. The extraction applies these filtering rules:

1. **Severity filter**: Only Critical and High severity findings are eligible. Medium, Low, and Note findings are excluded entirely.
2. **System-wide weighted distribution** (Level 2 — F-212): The pipeline emits 6–8 callouts drawn from the system-wide pool of qualifying Critical/High findings using Largest Remainder Method allocation across layers, with a per-layer floor (every qualifying layer gets ≥1 callout when total-cap permits) and a 4-callout-per-layer ceiling.
3. **Tie-break order**: severity descending (Critical before High), then composite score descending (when available from `risk-scores.md` or `compensating-controls.md` tiers), then finding ID ascending for deterministic ordering.

The previous per-layer-dedup rule (one callout per layer) is superseded by F-212 Level 2; the current logic produces a denser, system-wide callout distribution while preserving the per-layer floor as an enforceable invariant. See `specs/212-improve-executive-architecture-infographic/spec.md` FR-212-8 through FR-212-12 for the formal allocation contract.

Raw finding descriptions are passed through unchanged during extraction. The agent instructs Gemini to rewrite each raw description to ≤25 words in plain English, stripping technical jargon, during image generation. The spec file retains the raw description for auditability.

---

## Skip Behavior

When the extraction finds zero Critical and zero High severity findings in the threat model, the template enters skip-image mode:

- The spec file is **still produced** with all six required sections present
- The `Threat Callouts` section contains an explanatory note (e.g., "No Critical or High severity findings identified. Executive architecture callouts require qualifying findings.") instead of callout entries
- The metadata payload sets `skip_image: true` to signal the agent
- **No Gemini image generation is attempted** — the `threat-executive-architecture.jpg` file is NOT created
- Downstream PDF compilation behaves as if the image is absent — the `has-executive-architecture` flag is false and the executive architecture page is omitted

This behavior keeps the pipeline exit code clean (0) on threat models that do not yet have qualifying findings, while preserving the spec file as a stable artifact that can be regenerated into an image if the threat data is later updated.

These F-128 contracts are preserved verbatim by F-212 — output filename, file format, portrait orientation, and skip behavior all remain unchanged.

---

## Visual Directives

All visual directives are defined in `schemas/infographic.yaml` under `templates[executive-architecture].visual_directives`. Do not invent values that are not present in the schema — the list below mirrors the schema exactly:

| Directive | Value |
|-----------|-------|
| Orientation | Portrait (8.5:11 page aspect ratio) |
| Layer visualization | Horizontal bands, pastel fill per layer, thin solid border, left-aligned labels |
| Component visualization | Rounded-rectangle node per component (FR-212-1) — layer-coded fill, severity-colored border, no bare text labels |
| Inter-layer flow | Top-to-bottom directional arrows with explicit arrowheads connecting layers (FR-212-2) |
| Callout visualization | Box anchored by a thin leader line to a specific node (FR-212-3) — not floating text inside a layer band |
| Empty-layer treatment | Compact factual badge at ≤15% of page height for layers with zero Critical/High findings (FR-212-5) |
| Callout text | ≤25 words, plain English, jargon-free |
| Severity colors (callout borders) | Critical `#DC2626`, High `#EA580C` (inherited unchanged from `visual-design-system.md`) |
| Layer fill pastels | `#F0F4FF`, `#FFF4F0`, `#F0FFF4`, `#FFF0F8`, `#F8F0FF` (cycled deterministically per layer index — extends the canonical palette without modifying it) |
| Typography | Large title, medium callout text, medium-bold layer labels; readable at projection or print distance |

The portrait orientation, the rounded-rectangle node visualization, and the pastel-banded layer styling are all intentional departures from the shared visual design system — the executive-architecture template is explicitly audience-tuned rather than brand-consistent with the other templates.

### Palette Provenance

- **Severity colors** are inherited unchanged from `visual-design-system.md` and apply to callout borders. Critical `#DC2626` and High `#EA580C` match the canonical Tailwind Red-600 and Orange-600 mappings used across all tachi infographic templates and are documented as the source of truth for severity semantics.
- **Layer-fill pastels** are an additive extension local to this template. The 5-color cycle `["#F0F4FF", "#FFF4F0", "#F0FFF4", "#FFF0F8", "#F8F0FF"]` is iterated by layer index (modulo 5) so that adjacent layers always receive distinct fills. These pastels do not replace, modify, or override any color in `visual-design-system.md` — they exist only inside the executive-architecture template's prompt block. The "EXTEND-with-additive" palette decision is documented in spec FR-212-4 and the spec's Palette Strategy section.

---

## Gemini Prompt Block — VERBATIM

The following prompt is the **single source of truth** for image generation in this template. It MUST be copied verbatim into the Gemini API request — do NOT rewrite, paraphrase, or recompose the aesthetic, structural, or palette language at runtime. Per spec FR-212-6 the text inside the BEGIN/END markers below is locked. Runtime substitution is permitted ONLY for the bracketed `<<...>>` data slots, which are populated from the infographic specification payload (`threat-executive-architecture-spec.md`). The verbatim-lock rule is documented in `gemini-prompt-construction.md` (see "Verbatim-Lock Rule for Executive-Architecture Template").

The bracketed `<<...>>` slots map to payload fields as follows:

| Slot | Source field |
|------|--------------|
| `<<project_name>>` | `metadata.project_name` |
| `<<layer_block>>` | Composed from `layers[]` — one entry per layer with `name`, `components[]` (rendered as nodes), `callouts[]` (rendered as anchored boxes), and optional `layer_overflow` text |
| `<<callout_block>>` | Rendered from `callouts[]` (6–8 entries — see Callout Selection above) — each `finding_id`, `severity`, `affected_component`, and `raw_description` (rewritten to ≤25 words by Gemini at render time) |
| `<<empty_layer_block>>` | One compact-badge line per layer with zero qualifying Critical/High findings (FR-212-5) |
| `<<single_zone_caption>>` | Caption text emitted only when exactly one layer has components (Edge Case fallback — replaces the inter-layer arrow directive) |
| `<<flow_edges_block>>` | Composed from `flow_edges[]` — one line per entry rendered as `source → destination [data via protocol]` for Gemini to draw as an explicit labeled directional arrow between two component nodes. Empty (or omitted line) when `flow_edges == []`. |
| `<<clusters_block>>` | Composed from `clusters[]` — one entry per cluster rendered as `name (trust_level): members` for Gemini to draw as a dashed sub-group boundary grouping the listed members under the cluster name label. Empty (or omitted line) when `clusters == []`. |

Slots are filled from the payload before the prompt is sent. Everything outside the slots is locked text.

```
=== BEGIN VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===

schematic diagram with shapes and arrows — produce a portrait-orientation security architecture infographic for "<<project_name>>" rendered as an OpenClaw-style system flow diagram. The image MUST be a structured visualization composed of geometric shapes (rounded rectangles), directional arrows with explicit arrowheads, and short text labels inside those shapes. Do NOT produce a text-only document, a bullet list, or floating labels without enclosing shapes. Every named component MUST appear inside its own rounded-rectangle node — bare text labels are not acceptable.

IMPORTANT: The styling directives in this prompt are for your interpretation only. Do NOT render any hex color codes, pixel values, or technical specifications as visible text in the image. Render only the natural-language labels, finding IDs, severity words, component names, and callout descriptions provided in the DATA CONTENT block.

STYLING DIRECTIVES (interpret these, do not display them):

- Orientation: portrait, 8.5:11 page aspect ratio.
- Background: clean off-white page surface (avoid pure white #FFFFFF and pure light-gray #F5F5F5 — use a subtle warm-neutral page tint).
- Layer bands: horizontal bands stacked top-to-bottom, ordered untrusted (top) to trusted (bottom). Each band has a pastel fill drawn deterministically from this 5-color cycle by layer index modulo 5: layer 0 = #F0F4FF (cool blue-tinted), layer 1 = #FFF4F0 (warm peach-tinted), layer 2 = #F0FFF4 (cool green-tinted), layer 3 = #FFF0F8 (cool pink-tinted), layer 4 = #F8F0FF (cool violet-tinted). These pastels are local to this template and extend — they do NOT replace — the canonical severity palette in the tachi visual design system. (FR-212-4)
- Component nodes: every component within a layer MUST render as a rounded-rectangle node (corner-radius approximately 8–12px equivalent) with the layer's pastel as the fill and a 1.5–2pt colored border. The node contains the component name in medium-bold sans-serif and (optionally) a 1-line role caption. NEVER render a component as a bare text label without an enclosing shape. (FR-212-1)
- Node border colors: when a node has at least one Critical-severity finding, its border is red #DC2626. When the node has at least one High-severity finding (and no Critical), its border is orange #EA580C. When a node has no qualifying findings, its border is the canonical gray #6B7280 desaturated to a thin neutral stroke. Severity colors are inherited unchanged from the canonical tachi palette in visual-design-system.md. (FR-212-4)
- Inter-layer arrows: between every pair of adjacent layers, draw at least one directional arrow flowing top-to-bottom from a node in the upper layer to a node in the lower layer. The arrow MUST be a solid stroke with an explicit arrowhead glyph at the destination end (filled triangle or chevron) — bare lines without arrowheads are NOT acceptable. The phrase "shapes and arrows" at the start of this prompt is a directive to defeat the text-only failure mode in image generation; honor it. (FR-212-2)
- Explicit data-flow arrows from `flow_edges`: when the DATA CONTENT block contains a FLOW EDGES section (populated from the `flow_edges[*]` payload field — fields `source`, `destination`, `data`, `protocol`), draw a directional arrow from each listed `source` component node to its `destination` component node with an explicit arrowhead, optionally labeling the arrow midline with the `data` value (and `protocol` in parentheses if present). These explicit edges are the structural source of truth for inter-component flow — render exactly the listed edges; do NOT infer additional flows from component-name proximity, alphabetic ordering, or layer adjacency. When the FLOW EDGES section is empty, fall back to the inter-layer arrow directive above for visual continuity. (FR-212-18)
- Trust-zone clusters from `clusters`: when the DATA CONTENT block contains a CLUSTERS section (populated from the `clusters[*]` payload field — fields `name`, `members`, `trust_level`), draw a dashed sub-group boundary (2pt dashed neutral-gray stroke, rounded corners) enclosing the listed `members` component nodes and label the boundary in its top-left corner with the cluster `name`. These dashed cluster boundaries OVERLAY the layer bands — they do not replace them; a component node MAY belong to both a layer band (its position) and a cluster (its trust grouping). Render exactly the listed clusters; do NOT infer additional clusters from component-name patterns, layer membership, or visual proximity. (FR-212-18)
- Callout boxes: each callout is a small rectangular box (white-with-alpha fill, dashed 2pt border in the callout's severity color, severity-colored warning triangle icon in the upper-left corner). Each callout MUST be visually anchored to a specific component node by a thin leader line (1pt solid neutral stroke) terminating on the node's edge — NEVER render a callout as floating text inside a layer band with no anchor. The callout box contains: the finding ID in monospace, the severity word in colored bold, and a ≤25-word plain-English description rewritten from the raw description with technical jargon stripped. (FR-212-3)
- Callout NON-OVERLAP rule (HARD constraint): callout boxes MUST NOT overlap any component node, any other callout box, any layer band label, any inter-layer arrow, or any flow-edge arrow label. Each callout box MUST occupy clear whitespace — preferably the left or right page margin alongside its layer band, or the inter-layer whitespace strip directly above or below the band. When a layer has multiple callouts, distribute them across both the left and right margins of that layer's band rather than stacking them on the same side; if margin space is exhausted, place additional callouts in the inter-layer whitespace strip with leader lines crossing into the band to reach their anchor node. The leader line MAY cross other leader lines if necessary to maintain box separation, but the callout BOXES themselves MUST remain disjoint from every component node and every other callout box. Reduce per-callout box footprint (smaller font, tighter padding) before allowing any overlap. (FR-212-3, T030 polish)
- Empty-layer treatment: a layer that contains components but has zero Critical/High qualifying findings MUST render as a compact factual badge — a thin horizontal pill no taller than approximately 15% of the total page height — containing the literal text "0 High/Critical findings in this layer". Do NOT expand such a layer into a full-band placeholder; do NOT add synthetic callouts to fill the band; the badge IS the layer for rendering purposes. (FR-212-5)
- Single-zone fallback: if exactly one layer has components, omit the inter-layer arrows and add a centered caption above the single layer with the text supplied in <<single_zone_caption>>. The single layer still renders all of its component nodes and callouts with leader lines normally.
- Typography: title bold 28–32pt equivalent at the top of the page; layer labels semi-bold 18–22pt equivalent left-aligned within each band; component-node labels medium-bold 12–14pt equivalent; callout text regular 12–14pt equivalent; finding IDs monospace 12–14pt equivalent. Sans-serif throughout (IBM Plex Sans, DM Sans, Manrope, or similar — avoid Inter, Roboto, Arial, Open Sans, Lato as primary).
- Composition: leave generous whitespace between layers; group component nodes within their layer with consistent intra-layer spacing (multiples of 8pt). Position callout boxes in the page margins (left or right of the active layer band) or in the inter-layer whitespace strips between bands. Component nodes MUST occupy ONLY the central column of their layer band, leaving at least 18% of the band's width clear on each side as a margin reserved for callout boxes. Leader lines MAY cross other leader lines when necessary, but no callout box, component node, or text label MAY overlap any other shape or label. Maintain reading order top-to-bottom.

DATA CONTENT (render this as visible text inside the shapes and bands):

TITLE: "Executive Threat Architecture: <<project_name>>"

LAYER STACK (top-to-bottom, untrusted at top, trusted at bottom):

<<layer_block>>

CALLOUTS (each anchored by a leader line to a specific component node — total 6–8 callouts drawn system-wide using weighted per-layer distribution; each layer with qualifying findings is represented; no layer exceeds 4 callouts):

<<callout_block>>

EMPTY-LAYER BADGES (each layer below has zero qualifying Critical/High findings — render each as a compact factual badge per the styling directive above, NOT as a full-band placeholder):

<<empty_layer_block>>

FLOW EDGES (render each entry below as an explicit directional arrow from the named `source` component node to the named `destination` component node, with an arrowhead at the destination end; optionally label the arrow midline with the `data` value — these are the structural source of truth from the `flow_edges[*]` payload field, supersede any flow inferred from component-name proximity, and MUST be rendered exactly as listed):

<<flow_edges_block>>

CLUSTERS (render each entry below as a dashed sub-group boundary enclosing the listed `members` component nodes with the cluster `name` labeled in the boundary's top-left corner — these dashed cluster boundaries from the `clusters[*]` payload field overlay the layer bands rather than replacing them, and MUST be rendered exactly as listed):

<<clusters_block>>

<<single_zone_caption>>

FOOTER: "Generated by Tachi Threat Modeling Framework — OWASP STRIDE + AI Threat Analysis"

Render this as a clean, premium, boardroom-ready security infographic. Lead with structural clarity over decoration. The reader should be able to identify the most exposed layer and the dominant threats within five seconds of looking at the page. No hex codes, color values, pixel sizes, or technical specifications should appear as visible text in the rendered image.

=== END VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===
```

The block delimited by `=== BEGIN VERBATIM PROMPT BLOCK ===` and `=== END VERBATIM PROMPT BLOCK ===` is the consumer copy target. The Gemini prompt builder MUST emit exactly the text inside these markers (after slot substitution) — no rewriting, no aesthetic recomposition, no runtime construction of the styling directives.

---

## Payload schema

The executive-architecture payload emitted by `_build_executive_architecture_payload()` in `scripts/extract-infographic-data.py` carries the following top-level keys consumed by the slot-substitution pass before the prompt is sent. The L1 keys (`metadata`, `layers`, `callouts`, `severity_distribution`) are documented in the F-128 contract; the L3 keys `flow_edges` and `clusters` are added by F-212 and documented here. The full schema lives in `specs/212-improve-executive-architecture-infographic/data-model.md`; the producer/consumer contract surface is locked in `specs/212-improve-executive-architecture-infographic/contracts/payload-schema.md`.

### `flow_edges[]` (FR-212-13, FR-212-14, FR-212-16, FR-212-17)

Array of explicit data-flow records, each with the fields:

| Field | Type | Source |
|-------|------|--------|
| `source` | str | Producer field `data_flows[].source` (component name) |
| `destination` | str | Producer field `data_flows[].destination` (component name — NOT `target`; Architect MEDIUM-2 lock) |
| `data` | str | Producer field `data_flows[].data` (may be empty string) |
| `protocol` | str | Producer field `data_flows[].protocol` (may be empty string) |

**Sort order**: ascending by `(source.casefold(), destination.casefold())`. **Truncation**: first 50 entries after sort retained; producer counts above 50 trigger a stderr warning (`Warning: flow_edges truncated to 50 entries (N emitted by producer)`). **Empty-semantics**: always present on every payload — `[]` when the source key is absent or empty (never `null`, never missing). **Slot rendering**: substituted into the `<<flow_edges_block>>` marker as one line per record so Gemini draws an explicit directional arrow per entry.

### `clusters[]` (FR-212-13, FR-212-15, FR-212-16)

Array of trust-zone cluster records, each with the fields:

| Field | Type | Source |
|-------|------|--------|
| `name` | str | Producer field `trust_boundaries[].zone` (zone name) |
| `members` | list[str] | Producer field `trust_boundaries[].components` (parsed from comma-separated string, stripped, sorted ascending case-insensitively) |
| `trust_level` | str | Producer field `trust_boundaries[].trust-level` (renamed via hyphen→underscore and lowercased to match the `_TRUST_LEVEL_ORDER` lookup convention used by `_compute_trust_zones`) |

**Sort order**: ascending by `(_TRUST_LEVEL_ORDER.get(trust_level, 99), name.casefold())` mirroring `_compute_trust_zones:784` — `trusted` (0) before `semi-trusted` (1) before `untrusted` (2); unknown levels sort last (99). **Empty-semantics**: always present on every payload — `[]` when the source key is absent or empty (never `null`, never missing). **Slot rendering**: substituted into the `<<clusters_block>>` marker as one line per record so Gemini draws a dashed sub-group boundary per cluster.

---

## Schema Reference

The canonical section list, alias, purpose, positioning, and visual directives for this template live in `schemas/infographic.yaml` under the `templates[]` enumeration. Consult the schema when the directives in this reference conflict with the schema — the schema is the source of truth.

## Implementation Reference

| Concern | Location |
|---------|----------|
| Extraction dispatch | `scripts/extract-infographic-data.py` (executive-architecture branch) |
| Agent spec generation | `.claude/agents/tachi/threat-infographic.md` |
| Command registration | `.claude/commands/tachi.infographic.md` |
| PDF page integration | `scripts/extract-report-data.py` (detection), `templates/tachi/security-report/main.typ` (positioning) |
| Report artifact table | `.claude/agents/tachi/report-assembler.md` |
| Verbatim-lock rule | `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` (Verbatim-Lock Rule for Executive-Architecture Template) |

Implements FR-036 from `specs/128-prd-128-executive/spec.md` and FR-212-1 through FR-212-7 from `specs/212-improve-executive-architecture-infographic/spec.md`.
