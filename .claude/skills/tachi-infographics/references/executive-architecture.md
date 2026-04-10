# Executive Architecture Template

Section format, data source rules, and visual directives for the `executive-architecture` infographic template. This is the only tachi infographic template rendered in **portrait** orientation; all other templates use the standard 16:9 landscape aspect ratio documented in `visual-design-system.md`. Sections 1-4 from `infographic-specifications.md` do NOT apply to this template — the executive-architecture spec uses a distinct six-section structure defined below.

---

## Purpose

Executive-level visualization of the layered system architecture with Critical and High severity threat callouts. The template serves a non-technical audience (CISO, board members, executive sponsors) who read only the first few pages of a security report and need to identify the most exposed architectural layer within their normal attention window.

Unlike the other infographic templates, which are general-purpose dashboards and analytical views, the executive-architecture template is audience-optimized: it trades exhaustive detail for narrative clarity, showing a small number of high-signal callouts anchored to a recognizable layered diagram of the system.

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

Callouts are the narrative annotations attached to layers. The extraction applies three filtering rules in order:

1. **Severity filter**: Only Critical and High severity findings are eligible. Medium, Low, and Note findings are excluded entirely.
2. **Per-layer deduplication**: At most one callout per layer. When a layer contains multiple qualifying findings, exactly one is selected using the tie-break rule below.
3. **Tie-break order**: severity descending (Critical before High), then composite score descending (when available from `risk-scores.md` or `compensating-controls.md` tiers), then finding ID ascending for deterministic ordering.

This deduplication keeps the visual uncluttered — executive audiences see one headline threat per layer rather than an exhaustive list — while the tie-break ordering guarantees reproducibility across runs on the same input data.

Layers with zero qualifying findings still appear in the diagram (to preserve the system's structural completeness) but have no callout box attached.

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

---

## Visual Directives

All visual directives are defined in `schemas/infographic.yaml` under `templates[executive-architecture].visual_directives`. Do not invent values that are not present in the schema — the list below mirrors the schema exactly:

| Directive | Value |
|-----------|-------|
| Orientation | Portrait (8.5:11 page aspect ratio) |
| Layer visualization | Horizontal bands, pastel fill per layer, thin solid border, left-aligned labels |
| Callout visualization | Red dashed 2pt border, warning triangle icon, white-with-alpha fill, leader line or anchor connecting to the affected layer |
| Callout text | ≤25 words, plain English, jargon-free |
| Severity colors | Critical `#DC2626`, High `#F97316` |
| Layer fill pastels | `#F0F4FF`, `#FFF4F0`, `#F0FFF4`, `#FFF0F8`, `#F8F0FF` (cycled per layer) |
| Typography | Large title, medium callout text, medium-bold layer labels; readable at projection or print distance |

The portrait orientation and the pastel-banded layer styling are both intentional departures from the shared visual design system — the executive-architecture template is explicitly audience-tuned rather than brand-consistent with the other templates.

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

Implements FR-036 from `specs/128-prd-128-executive/spec.md`.
