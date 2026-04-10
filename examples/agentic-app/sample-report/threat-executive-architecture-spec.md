---
schema_version: "1.0"
template: "executive-architecture"
date: "2026-04-10"
source_file: "threats.md"
data_source_type: "compensating-controls"
finding_count: 7
image_generated: true
skip_image: false
fallback_used: false
tier_source: "compensating-controls"
qualifying_layer_count: 3
total_filtered_count: 7
---

# Threat Executive Architecture Specification

Portrait-orientation executive-audience layered architecture diagram with narrative threat callouts for Critical and High severity findings. Designed for placement immediately after the Executive Summary in the security report PDF so CISOs and board members see the most critical threat visualization within the first few pages they actually read.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-03-25 |
| Template | executive-architecture |
| Tier Source | compensating-controls (richest tier detected) |
| Source File | threats.md |
| Generation Timestamp | 2026-04-10T04:08:11Z |
| Qualifying Layer Count | 3 |
| Total Critical/High Findings | 7 (0 Critical, 7 High) |
| Callouts After Layer Dedup | 1 |
| Skip Image | false |
| Fallback Used | false (trust_zone source) |

**Risk Posture Narrative**: The executive architecture filter identified 7 High-severity findings across the system's 3 trust-boundary zones. One-callout-per-layer dedup selects the single highest-risk finding per layer for executive presentation; the Application Zone carries the top-ranked narrative callout (composite residual score 8.3), reflecting the LLM Agent Orchestrator as the system's risk concentration point.

---

## 2. Architecture Layers

Trust boundary zones parsed from `threats.md` Section 2, ordered with the most exposed zone at position 0 (top of diagram) and the most trusted at the highest position (bottom of diagram). Executive reading order mirrors "where attackers enter the system" mental model.

| Position | Layer Name | Source Kind | Component Count | Components |
|----------|-----------|-------------|-----------------|------------|
| 0 | User Zone | trust_zone | 1 | User |
| 1 | External Services | trust_zone | 1 | External API |
| 2 | Application Zone | trust_zone | 5 | Audit Logger, Guardrails Service, Knowledge Base, LLM Agent Orchestrator, MCP Tool Server |

**Layer ordering rationale**: Position 0 (User Zone) and position 1 (External Services) are untrusted perimeter layers where external actors interact with the system. Position 2 (Application Zone) contains the trusted service mesh where the agentic coordination logic executes. The diagram places untrusted layers at the TOP so the reader's eye enters the page at the attacker's starting point and flows downward into the trusted core.

---

## 3. Threat Callouts

One callout per architectural layer that has at least one Critical or High severity finding, selected deterministically via: severity descending, composite score descending, finding ID ascending. Layers without qualifying findings are shown in the diagram but carry no callout. Each callout's raw description is carried through unchanged from the source; the Gemini prompt (Section 6) is responsible for rewriting it to ≤25 words of plain English suitable for a non-technical executive audience.

### Callout 1 — Application Zone

| Field | Value |
|-------|-------|
| Layer | Application Zone |
| Affected Component | LLM Agent Orchestrator |
| Finding ID | LLM-1 |
| Severity | High |
| Composite Score | 8.3 |
| Raw Description | Adversarial prompts override system prompt |
| Plain-English Rewrite (≤25 words) | An attacker can craft a trick prompt that overrides the AI assistant's safety rules and makes it behave in unapproved ways. |

**No callout for User Zone**: The filter selected no qualifying Critical/High finding whose affected component sits in this layer.

**No callout for External Services**: The filter selected no qualifying Critical/High finding whose affected component sits in this layer.

**Note on single-callout output**: The extraction identified 7 total Critical/High findings in the threat model, but after one-callout-per-layer dedup only the Application Zone's top-ranked finding is surfaced. This is by design — executive simplicity prefers "show fewer things" over exhaustive enumeration. The other 6 filtered findings remain visible in the full threat report section of the PDF but do not clutter the executive architecture visual.

---

## 4. Severity Distribution

Filtered to Critical and High only — Medium, Low, and Note severities are excluded from the executive architecture view.

| Severity | Count | Visual Treatment |
|----------|-------|------------------|
| Critical | 0 | n/a (no Critical findings in this threat model) |
| High | 7 | Red dashed-border callout boxes with warning triangle icons |
| **Total Qualifying** | **7** | — |
| **After Layer Dedup** | **1** | Single callout rendered on diagram |

**Dedup ratio**: 7 qualifying findings distilled to 1 rendered callout (14% of qualifying findings surfaced). This is a consequence of the threat model's risk concentration — 7 of the High-severity findings affect components within a single architectural layer (the Application Zone), so the one-per-layer rule elevates the highest-scored finding and suppresses the rest.

---

## 5. Visual Layout Directives

### Page Orientation

- **Orientation**: Portrait
- **Page Aspect Ratio**: 8.5:11 (letter size)
- **Intended Placement**: Full-bleed page immediately after Executive Summary in PDF report

### Layer Visualization

- **Style**: Horizontal bands stacked vertically
- **Fill**: Pastel per-layer, cycling through the palette below
- **Border**: Thin solid outline separating each band
- **Label Position**: Left-aligned layer name beside each band
- **Vertical Ordering**: Position 0 at the TOP of the page (most exposed / untrusted), increasing position toward the BOTTOM (most trusted)

### Callout Visualization

- **Border**: Red dashed 2pt weight (#DC2626)
- **Icon**: Warning triangle glyph at callout corner
- **Fill**: White with partial alpha so the underlying layer band remains visible
- **Connection to Layer**: Leader line or anchor pointing from the callout to the affected component within its layer
- **Text Maximum Words**: 25 per callout
- **Text Style**: Plain English, no technical jargon, one-sentence-per-callout

### Color Palette

| Element | Hex | Usage |
|---------|-----|-------|
| Critical severity | #DC2626 | Callout border, warning icon (when Critical present) |
| High severity | #F97316 | Callout accent (optional secondary tint) |
| Layer fill 1 | #F0F4FF | Position 0 band — applied to User Zone |
| Layer fill 2 | #FFF4F0 | Position 1 band — applied to External Services |
| Layer fill 3 | #F0FFF4 | Position 2 band — applied to Application Zone |
| Layer fill 4 | #FFF0F8 | Reserved (cycle back if more than 5 layers) |
| Layer fill 5 | #F8F0FF | Reserved (cycle back if more than 5 layers) |

### Typography

- **Title Size**: Large (24pt or greater)
- **Callout Text Size**: Medium (14pt or greater)
- **Layer Label Size**: Medium bold
- **Font Intent**: Readable for projection or print on letter-size paper; no serifs on body copy; executive-dashboard feel

### Design Philosophy

Executive dashboards prioritize "show fewer things" over exhaustive enumeration. The single callout on this page is intentional — the reader is a CISO or board member who has 30 seconds of attention for this page. The visual must communicate "here is the layered system; here is the single highest-priority exposure; here is plain English about what that exposure means" without forcing the reader to parse a matrix of finding IDs.

---

## 6. Gemini Prompt Construction Notes

The following prompt text is constructed deterministically from the payload fields and passed to the Gemini image generation API to render the JPEG. The prompt avoids attack-specific terminology ("exploit," "vulnerability," "injection") in favor of executive-friendly business language ("risk assessment summary," "organizational risk overview") per the prompt-framing rules in `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md`.

### Gemini Prompt

```
Create a premium, consultancy-grade risk assessment summary infographic in
PORTRAIT orientation with an 8.5:11 letter-size aspect ratio. The style is a
clean, executive boardroom dashboard — sans-serif typography, pastel fills,
generous whitespace. No attack-specific terminology in visible text; this is
a business-audience security posture overview.

LAYOUT: Three horizontal pastel bands stacked vertically, one per
architectural layer, spanning the full width of the page. The topmost band
represents the most exposed layer (where external actors interact with the
system) and the bottom band represents the most trusted internal service
layer. Each band is labeled with its layer name in medium-bold 18-22pt text
on the left side, with the contained component names listed as small chips
inside the band.

BAND ORDER (top to bottom):
  Band 1 (top)    — "User Zone"           fill #F0F4FF
                    Components: User
  Band 2 (middle) — "External Services"   fill #FFF4F0
                    Components: External API
  Band 3 (bottom) — "Application Zone"    fill #F0FFF4
                    Components: Audit Logger, Guardrails Service,
                                Knowledge Base, LLM Agent Orchestrator,
                                MCP Tool Server

CALLOUTS: Place ONE narrative callout box next to the Application Zone band,
anchored visually to the "LLM Agent Orchestrator" chip. The callout is a
white rectangle with partial alpha, a 2pt RED DASHED border (use color
#DC2626), and a warning triangle icon in the upper-left corner of the box.
A thin leader line connects the callout box to the LLM Agent Orchestrator
chip inside the Application Zone band.

CALLOUT TEXT (rewrite to ≤25 words, plain English, no jargon):
  "An attacker can craft a trick prompt that overrides the AI assistant's
  safety rules and makes it behave in unapproved ways."

  Severity label inside the callout: "High"
  Finding reference (small text, bottom-right of callout): "LLM-1"

TYPOGRAPHY:
  Title (top of page, 28-32pt bold):
    "Executive Threat Architecture"
  Subtitle (14-16pt regular, gray):
    "Agentic AI Application — Risk Assessment Summary"
  Layer labels: 20-22pt medium-bold, dark gray
  Component chips: 12-14pt medium, dark gray
  Callout body text: 14-16pt regular, dark gray
  Callout severity label: 14pt bold, red (#DC2626)

BACKGROUND: White (#FFFFFF). Each pastel band is a full-width rectangle
stacked on the next with a thin gray separator. No drop shadows, no
gradients — flat polished executive-dashboard style.

DO NOT include: hex color codes as visible text, pixel values, Tailwind
class names, SARIF identifiers, the word "exploit," the word "vulnerability,"
the word "injection," or technical acronyms without definition. The audience
is a non-technical board member.
```

### Prompt Construction Rules Followed

- **Rule 1 (hygiene)**: Hex values (#F0F4FF, #FFF4F0, etc.) appear in the *directive* portions of the prompt but never in the visible text content blocks.
- **Rule 2 (no CSS)**: No pixel, rem, or percentage values in visible text content.
- **Rule 3 (no color column)**: Severity is referenced by name ("High"), not by hex.
- **Rule 4 (hygiene from Section 6)**: The color palette table in Section 5 of this spec is *used* to populate the prompt's layer fills, but its Hex column is not copied verbatim into the visible prompt text.
- **Rule 5 (data placeholders are content only)**: The `{layer_name}`, `{components}`, `{callout_text}`, `{finding_id}`, and `{severity}` placeholders in the prompt template are substituted with natural-language content only — no metadata.

### Callout Rewriting Guidance

Each callout's `raw_description` is the unmodified source text from the finding's Threat column in `threats.md`. The Gemini prompt MUST rewrite each description to ≤25 words of plain English suitable for a non-technical executive. Examples of the rewriting transformation:

| Raw Description (source) | Plain-English Rewrite (≤25 words) |
|--------------------------|-----------------------------------|
| Adversarial prompts override system prompt | An attacker can craft a trick prompt that overrides the AI assistant's safety rules and makes it behave in unapproved ways. |

Words to avoid in the rewrite: `endpoint`, `payload`, `injection`, `JWT`, `RBAC`, `IAM`, `SQL`, `XSS`, `CSRF`, `authentication`, `authorization` (unless paired with a plain-English definition). Prefer verbs like "attacker could steal," "system could leak," "user could impersonate," "assistant could be tricked into."

### Skip Image Edge Case

When `metadata.skip_image == true` (i.e., zero Critical AND zero High findings), the agent MUST NOT invoke Gemini. This spec file is produced with the Threat Callouts section carrying an explanatory note, and no JPEG is generated. Downstream PDF compilation omits the executive architecture page because the `threat-executive-architecture.jpg` file does not exist. For this threat model, `skip_image == false` and the Gemini invocation IS permitted (7 High-severity findings qualify).
