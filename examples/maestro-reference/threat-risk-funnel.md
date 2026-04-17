---
schema_version: "1.0"
template: "risk-funnel"
date: "2026-04-16"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 112
image_generated: true
---

# Infographic Specification — Risk Funnel
## Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This specification is derived from the tachi canonical MAESTRO worked example. The underlying threat model analyzes a fictional Healthcare CDSS reference architecture for teaching purposes only — not a real clinical system. The 0% risk reduction and 0% control coverage are the accurate, expected results of scanning the tachi toolkit against a CDSS threat model: no clinical application controls are present in the target codebase.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Healthcare Clinical Decision Support System (CDSS) |
| Scan Date | 2026-04-16 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 112 |
| Risk Posture | Residual risk — 0 Critical and 6 High findings across 20 components |
| Data Source | Tier 1 — compensating-controls.md (4-tier mode, 0% risk reduction) |
| Schema Version | 1.4 |

---

## 2. Risk Distribution

**Chart Label**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 6 | 5% | #EA580C |
| Medium | 104 | 93% | #CA8A04 |
| Low | 2 | 2% | #2563EB |
| **Total** | **112** | **100%** | — |

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| Supervisor Orchestrator | 0 | 0 | 11 | 0 | 11 |
| Clinical LLM | 0 | 0 | 9 | 0 | 9 |
| Risk Stratification Model | 0 | 0 | 9 | 0 | 9 |
| Diagnostic Agent | 0 | 0 | 8 | 0 | 8 |
| Inter-Agent Communication Channel | 0 | 2 | 6 | 0 | 8 |
| Treatment Planner Agent | 0 | 0 | 8 | 0 | 8 |
| Clinical MCP Tool Server | 0 | 0 | 7 | 0 | 7 |
| Other | 0 | 4 | 46 | 2 | 52 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|----|-----|
| Supervisor Orchestrator | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Clinical LLM | Medium | Medium | Medium | Medium | Medium | Medium | — | Medium |
| Risk Stratification Model | Medium | Medium | Medium | Medium | Medium | Medium | — | Medium |
| Diagnostic Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Inter-Agent Communication Channel | High | High | Medium | Medium | Medium | Medium | Medium | — |
| Treatment Planner Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Clinical MCP Tool Server | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Other | High | High | Medium | High | Medium | High | Medium | — |

---

## 4. Top Critical Findings

No Critical residual findings. Top 5 by composite score (Residual Risk):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | Physician | Attacker replays or forges clinical query credentials to gain unauthorized access | High (8.4) |
| 2 | S-2 | Patient | Attacker submits fraudulent EHR update events by spoofing patient identity | High (7.4) |
| 3 | D-1 | Physician Clinical Portal | Attacker floods portal with clinical query requests causing service disruption | High (7.1) |
| 4 | E-1 | Physician Clinical Portal | Attacker escalates from low-privilege session to gain elevated portal access | High (7.0) |
| 5 | S-5 | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messages causing agents to act on forged commands | High (7.0) |

---

## 5. Architecture Threat Overlay

### Funnel Tiers (4-Tier Mode — compensating-controls source)

| Tier | Label | Width (%) | Severity Counts | Render State |
|------|-------|-----------|-----------------|--------------|
| 1 | Threats Identified | 100% | 16 Critical / 52 High / 30 Medium / 8 Low / 2 Note (108 source findings) | solid |
| 2 | Inherent Risk Scored | 90% | 0 Critical / 6 High / 104 Medium / 2 Low (112 scored; composite model applies reachability penalties, promoting source Critical/High to Medium for internal Trusted-zone components) | solid |
| 3 | Controls Applied | 80% | 0% control coverage / 0 mitigated / 112 unmitigated (reference scenario — tachi toolkit has no clinical controls) | solid |
| 4 | Residual Risk | 80% | 0 Critical / 6 High / 104 Medium / 2 Low (residual equals inherent — 0% risk reduction) | solid |

**Note on Tier 1 vs Tier 2 count difference**: threats.md Section 6 reports 108 findings (deduplication applied: 6 correlation groups counted at group highest severity, plus 3 net-new AGP pattern findings). risk-scores.md and compensating-controls.md report 112 findings (pre-deduplication total). The funnel displays 108 at Tier 1 (source truth from threats.md) and 112 at Tiers 2-4 (quantitative scoring artifact count).

**Note on Tier 3→4 width**: Per zero-risk-reduction edge case rule — "Tier 4 width equals Tier 2 width when all controls missing." Tiers 2, 3, and 4 are rendered at same width to visually communicate no risk reduction.

**Sidebar Note**: "0% risk reduction — no effective controls detected. This is the accurate result for the tachi toolkit target; apply this pipeline to a real clinical codebase to obtain meaningful coverage."

### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Source Findings | 108 (threats.md, deduplicated) |
| Total Scored Findings | 112 (risk-scores.md / compensating-controls.md) |
| Inherent Score (sum) | 570.6 |
| Residual Score (sum) | 570.6 |
| Risk Reduction | 0.0% |
| Control Coverage | 0% Found / 0% Partial / 100% Missing |
| Highest Residual | S-1 — Physician, composite 8.4 (High) |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: donut segment, funnel tier segment, finding card borders |
| High | #EA580C | Orange-600: donut segment, funnel tier dominant color |
| Medium | #CA8A04 | Yellow-600: donut segment, funnel tier dominant color (largest segment) |
| Low | #2563EB | Blue-600: donut segment |
| Note | #6B7280 | Gray-500: informational only |
| Clean cell | #F3F4F6 | Gray-100: empty tier background |
| Card bg | #F9FAFB | Gray-50: sidebar card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Funnel Visual Guidance

- Tier 1: Full width (100%), multi-color segments representing STRIDE finding distribution by severity. Dominant color: red/orange (Critical+High segments from threats.md)
- Tier 2: Slightly narrower (90%), amber-dominated (Medium is 93% after composite scoring applies reachability penalties)
- Tier 3: Same width as Tier 2 (80%) — no narrowing because 0% controls applied
- Tier 4: Same width as Tier 3 (80%) — no narrowing because 0% risk reduction
- Sidebar: right-side panel with key metrics and note about reference scenario
- Visual emphasis: Tiers 3 and 4 being the same width as Tier 2 communicates visually that controls provided zero risk reduction — this is the pedagogically important feature of this infographic

### Layout Structure

- Background: Dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape
- Style: Premium executive boardroom quality — 3D glass-like funnel with translucent material and soft ambient lighting
- Layout: Vertical funnel centered in the frame; sidebar metrics on right; top header with title and CONFIDENTIAL badge; tier labels on left side of funnel; severity counts inside each tier band
- Ghost tiers: none (all 4 tiers are solid — compensating-controls source provides all data)

### Typography

- Title: Bold, 28-32pt equivalent
- Tier Labels: Semi-bold, 18-22pt equivalent
- Metric Values: Bold, 14-16pt equivalent
- Sidebar Labels: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B) — premium executive aesthetic. All text: white or light gray.

### Gemini Prompt

**PREAMBLE** (verbatim from JSON prompt_scaffold.preamble):
Create a premium, photorealistic 3D risk reduction funnel with glass-like translucent material, soft ambient lighting, and executive boardroom quality. This should look like a professionally designed data visualization for a CISO's board presentation — sophisticated, confident, and visually impressive. Render ONLY the infographic itself as a flat document — no perspective, no room context, no environmental background.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, percentages-of-height, or technical CSS specifications as visible text in the image. Only render the data labels, numbers, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: dark navy
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- Ghost tier style: translucent gray with dashed border
- All text on dark background: white or light gray
- Panels: rounded corners, subtle drop shadows, generous whitespace
- Layout: 16:9 landscape, premium executive aesthetic
- Funnel tiers: translucent 3D trapezoids with glass-like material, soft ambient lighting, gradient connectors between tiers
- CONFIDENTIAL badge: red pill with white text

DATA CONTENT (render this as visible text):

**DATA CONTENT**:

HEADER: Title "Healthcare CDSS — Risk Reduction Funnel" with date "2026-04-16" and "CONFIDENTIAL" badge. Subtitle: "Teaching Reference Scenario — Not a Real Clinical System — Full 4-Tier Pipeline."

FUNNEL (4 tiers, vertical, widest at top):

Tier 1 — "Threats Identified" (full width, widest): "108 Source Findings — 16 Critical / 52 High / 30 Medium / 8 Low / 2 Note. All 7 MAESTRO layers populated. 3 cross-layer attack chains identified. 6 agentic patterns present."

Tier 2 — "Inherent Risk Scored" (slightly narrower): "112 Scored Findings — Composite Model: (0.35 × CVSS) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability). Result: 0 Critical / 6 High / 104 Medium / 2 Low. Reachability penalties moderate internal component scores substantially. Highest: S-1 composite 8.4."

Tier 3 — "Controls Applied" (same width as Tier 2): "0% Control Coverage — 0 Found / 0 Partial / 112 No Control Found. Reference scenario: tachi toolkit target has no clinical application controls. Inherent score: 570.6."

Tier 4 — "Residual Risk" (same width as Tier 3): "0% Risk Reduction — Residual score: 570.6 (equals inherent). 0 Critical / 6 High / 104 Medium / 2 Low. No effective controls detected."

SIDEBAR METRICS PANEL (right side):
"Total Findings: 108 source / 112 scored
Risk Reduction: 0.0%
Control Coverage: 0%
Highest Residual: S-1, Physician (8.4, High)
Note: Tiers 3 and 4 equal width = zero risk reduction — apply pipeline to real target codebase for meaningful results."

**POSTAMBLE** (verbatim from JSON prompt_scaffold.postamble):
FOOTER (bottom): "Generated by Tachi Threat Modeling Framework — Risk Reduction Funnel" in small light gray text, centered.

The overall impression should be a polished, premium risk reduction narrative — confident, clear, and visually sophisticated. Professional business language throughout, no technical jargon or color codes. Render as a flat, full-bleed graphic filling the entire 16:9 frame.
