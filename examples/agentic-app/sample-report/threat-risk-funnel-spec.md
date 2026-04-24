---
schema_version: "1.0"
template: "risk-funnel"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
---

# Threat Infographic Specification — Risk Funnel
## Project: Agentic AI Application

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2023-11-14 |
| Analysis Agents | 8 |
| Total Findings | 81 |
| Risk Posture | Residual risk — 0 Critical and 17 High findings across 11 components |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 17 | 21% | #EA580C |
| Medium | 62 | 77% | #CA8A04 |
| Low | 2 | 2% | #2563EB |
| **Total** | **81** | **100%** | — |

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 11 | 7 | 0 | 18 |
| Clinical Advisory Sub-Agent | 0 | 1 | 11 | 0 | 12 |
| Specialist Agent | 0 | 1 | 9 | 0 | 10 |
| Long-Running Learning Loop | 0 | 0 | 9 | 0 | 9 |
| MCP Tool Server | 0 | 2 | 6 | 0 | 8 |
| Inter-Agent Communication Channel | 0 | 0 | 7 | 0 | 7 |
| Guardrails Service | 0 | 1 | 5 | 0 | 6 |
| Other | 0 | 1 | 8 | 2 | 11 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|-----|-----|
| LLM Agent Orchestrator | High | High | High | High | High | High | High | High |
| Clinical Advisory Sub-Agent | High | High | High | High | Medium | Medium | — | High |
| Specialist Agent | Medium | High | Medium | Medium | Medium | Medium | High | — |
| Long-Running Learning Loop | High | High | Medium | Medium | Medium | High | High | — |
| MCP Tool Server | High | High | Medium | Medium | High | High | High | — |
| Inter-Agent Communication Channel | Medium | High | Low | High | Medium | High | High | — |
| Guardrails Service | Medium | Medium | Medium | Medium | High | High | — | — |
| Other | High | Medium | Low | Medium | Low | — | — | — |

---

## 4. Top Critical Findings

No Critical residual-severity findings identified. Top High-residual findings shown (by residual score descending):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | Attacker replays stolen session tokens to impersonate a legitimate user | High |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes autonomous execution of unauthorized high-impact actions | High |
| 3 | E-2 | LLM Agent Orchestrator | Orchestrator self-authorizes elevated operations across tools and sub-agents | High |
| 4 | R-3 | LLM Agent Orchestrator | Orchestrator denies issuing delegation messages or tool calls; no non-repudiable log | High |
| 5 | E-1 | Guardrails Service | Prompt injection bypasses Guardrails and elevates attacker to Orchestrator trust level | High |

---

## 5. Architecture Threat Overlay

### Funnel Tiers (4-Tier Mode — compensating-controls data source)

| Tier | Label | Width (%) | Severity Counts | Render State |
|------|-------|-----------|-----------------|--------------|
| 1 | Threats Identified | 100 | 57C / 22H / 4M / 0L (raw: 83 findings) | solid |
| 2 | Inherent Risk Scored | 100 | Inherent total 469.4 composite score — risk-scores.md not independently available; recalculated from compensating-controls.md inherent scores | solid |
| 3 | Controls Applied | 100 | 0% coverage Found, 4% Partial, 96% Missing — 3 partial controls, 80 no-control findings | solid |
| 4 | Residual Risk | 97 | 0C / 17H / 62M / 2L (81 residual findings) | solid |

**Note on Tier widths**: Tier 4 width calculated as (81 / 83) × 100 = 97.6% ≈ 97%. Minimum 10% narrowing enforced — applied for Tier 4 relative to Tier 3 (97% < 100%). Tier 2 shows same volume as Tier 1 because all 83 raw threats passed through risk scoring.

**Risk reduction**: 0.5% (469.4 inherent → 467.2 residual composite). Near-zero reduction indicates controls are largely absent.

### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Findings | 81 (residual) / 83 (raw) |
| Risk Reduction | 0.5% |
| Control Coverage | 0% Found / 4% Partial / 96% Missing |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: funnel tier accent, finding card borders |
| High | #EA580C | Orange-600: funnel tier accent, finding card borders |
| Medium | #CA8A04 | Yellow-600: funnel tier accent, finding card borders |
| Low | #2563EB | Blue-600: funnel tier accent, finding card borders |
| Note | #6B7280 | Gray-500: informational only, excluded from visual risk distribution |
| Clean cell | #F3F4F6 | Gray-100: heat map analyzed with no findings |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- Background: Dark navy
- Aspect Ratio: 16:9 landscape
- Premium executive aesthetic — 3D glass-like translucent funnel tiers, soft ambient lighting
- Main body: Vertical funnel (left 60%) + sidebar metrics (right 40%)
- Funnel tiers ordered top-to-bottom: Tier 1 widest (100%), tapering to Tier 4 (97%)
- CONFIDENTIAL badge: red pill with white text

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy. All text white or light gray. Funnel tiers: translucent 3D trapezoids with glass-like material. Ghost tiers (if any): translucent gray with dashed border.

---

## 7. Gemini Prompt

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

TOP SECTION: Title "Risk Reduction Funnel: Agentic AI Application" with date "2023-11-14" and "CONFIDENTIAL" badge. Subtitle: "Full Pipeline — Threats → Risk Scoring → Controls → Residual Risk".

FUNNEL (center-left, vertical stack, widest at top):

Tier 1 (widest, 100% width): "Threats Identified" — 83 raw findings: 57 Critical, 22 High, 4 Medium, 0 Low. Dominant color: red (Critical majority in raw model). This tier represents all findings before scoring.

Tier 2 (full width, 100%): "Inherent Risk Scored" — Total inherent composite: 469.4. Distribution driven by quantitative scoring across 11 components. Dominant exposure: LLM Agent Orchestrator (avg score 2.6), Guardrails Service (avg 2.2), MCP Tool Server (avg 2.2).

Tier 3 (full width, 100%): "Controls Applied" — 83 findings analyzed. Control coverage: 0% Found, 4% Partial (3 findings), 96% No Control. Near-zero reduction at this stage.

Tier 4 (narrow, 97% width): "Residual Risk" — 81 findings: 0 Critical, 17 High, 62 Medium, 2 Low. Dominant color: amber (Medium majority). Risk reduction: 0.5%.

GRADIENT CONNECTORS between tiers showing near-zero narrowing (tiers nearly equal width).

SIDEBAR (right panel):
"RISK METRICS"
Total Raw Findings: 83
Residual Findings: 81
Risk Reduction: 0.5%
Control Coverage Found: 0%
Partial Controls: 3 of 83
No Controls: 80 of 83

"TOP RESIDUAL EXPOSURE"
S-1 | User — Session token replay (score 8.2)
AG-1 | LLM Orchestrator — Prompt injection autonomy (score 7.8)
E-2 | LLM Orchestrator — Orchestrator privilege escalation (score 7.8)
R-3 | LLM Orchestrator — Denial of action traceability (score 7.8)
E-1 | Guardrails — Guardrail bypass privilege escalation (score 7.7)

ADVISORY NOTE (bottom of sidebar): "Near-maximum inherent residual risk. Urgent remediation required across all 11 components. No production-grade controls detected."

FOOTER (bottom): "Generated by Tachi Threat Modeling Framework — Risk Reduction Funnel" in small light gray text, centered.

The overall impression should be a polished, premium risk reduction narrative — confident, clear, and visually sophisticated. Professional business language throughout, no technical jargon or color codes. Render as a flat, full-bleed graphic filling the entire 16:9 frame.
