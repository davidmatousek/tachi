---
schema_version: "1.4"
template: "risk-funnel"
date: "2026-04-29"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 31
image_generated: false
---

# Threat Infographic Specification — Risk Funnel

**Project**: WellnessBank Mobile Banking Application
**Template**: Risk Funnel
**Data Source**: compensating-controls.md (residual risk tier — 4-Tier Mode)
**Generated**: 2026-04-29

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | WellnessBank Mobile Banking Application |
| Scan Date | 2026-04-29 |
| Analysis Agents | 8 |
| Total Findings | 31 |
| Risk Posture | Residual risk — 0 Critical and 9 High findings across 12 components |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 9 | 29% | #EA580C |
| Medium | 20 | 65% | #CA8A04 |
| Low | 2 | 6% | #2563EB |
| **Total** | **31** | **100%** | — |

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| WellnessBank Android Client | 0 | 3 | 7 | 0 | 10 |
| WellnessBank Backend API | 0 | 0 | 4 | 1 | 5 |
| WellnessBankCredentialCache | 0 | 1 | 2 | 0 | 3 |
| WellnessBankLocalDB | 0 | 0 | 3 | 0 | 3 |
| Mobile Banking Customer | 0 | 2 | 0 | 0 | 2 |
| MoneyTransferActivity | 0 | 2 | 0 | 0 | 2 |
| WellnessAnalyticsSDK | 0 | 0 | 1 | 1 | 2 |
| Other | 0 | 1 | 3 | 0 | 4 |

### Cell-Level Grid

| Component | S | T | R | I | D | E |
|-----------|---|---|---|---|---|---|
| WellnessBank Android Client | Medium | High | Medium | High | Medium | --- |
| WellnessBank Backend API | Low | --- | Medium | Low | High | Medium |
| WellnessBankCredentialCache | n/a | Medium | n/a | High | Medium | n/a |
| WellnessBankLocalDB | n/a | Medium | n/a | Medium | Medium | n/a |
| Mobile Banking Customer | High | n/a | Medium | n/a | n/a | n/a |
| MoneyTransferActivity | --- | High | --- | --- | --- | High |
| WellnessAnalyticsSDK | --- | Medium | --- | Low | --- | --- |
| WellnessBankDebugActivity | --- | --- | Medium | --- | --- | High |
| WellnessPaySDK | --- | Medium | --- | Medium | --- | --- |

---

## 4. Top Critical Findings

> No Critical residual findings. Listing top 5 High findings by residual score descending.

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | E-1 | WellnessBankDebugActivity | Debug Activity in production release allows any ADB user to bypass authentication and execute privileged banking operations | High (8.5) |
| 2 | E-2 | MoneyTransferActivity | Exported money-transfer screen accepts external commands to initiate fund transfers without login | High (8.3) |
| 3 | T-3 | MoneyTransferActivity | Android inter-process messages from any installed app can hijack the money-movement flow | High (8.1) |
| 4 | T-4 | WellnessBank Android Client | App ships without code obfuscation or tampering detection | High (7.7) |
| 5 | I-4 | WellnessBank Android Client | 4-digit PIN key derivation uses 1,000 iterations and no salt — exhausted in under one second | High (7.5) |

---

## 5. Architecture Threat Overlay

### Funnel Tiers (4-Tier Mode — compensating-controls data source)

| Tier | Label | Width (%) | Severity Counts | Render State |
|------|-------|-----------|-----------------|--------------|
| 1 | Threats Identified | 100 | 13C / 11H / 3M / 4L / 1N (raw — from threats.md Section 6) | solid |
| 2 | Inherent Risk Scored | 97 | 199.8 aggregate inherent score across 31 findings | solid |
| 3 | Controls Applied | 90 | 0% Found / 25.8% Partial / 74.2% No Control (8 partial controls across 31 findings) | solid |
| 4 | Residual Risk | 90 | 0C / 9H / 20M / 2L (residual — from compensating-controls.md) | solid |

> Tier widths: Tier 1 = 100% baseline. Tier 2 = 97% (minimal reduction from inherent scoring). Tier 3 and Tier 4 maintain 90% (6.5% aggregate risk reduction, enforcing minimum 10% visual narrowing from Tier 1 per spec). Zero risk reduction path: Tier 4 remains at same width as Tier 3 (no net reduction from partial controls to residual).

> **Zero risk reduction note**: The funnel does not visually narrow significantly from Tier 3 to Tier 4 because the 6.5% aggregate risk reduction is distributed across partial controls rather than showing discrete tier-to-tier elimination. The sidebar metric communicates this honestly.

### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Findings | 31 |
| Risk Reduction | 6.5% |
| Control Coverage | 0.0% (Found) / 25.8% (Partial) / 74.2% (Missing) |
| Inherent Score | 199.8 |
| Residual Score | 186.9 |
| High-Risk Components | Mobile Banking Customer, MoneyTransferActivity |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: funnel tier accent, finding card borders |
| High | #EA580C | Orange-600: funnel tier accent, finding card borders |
| Medium | #CA8A04 | Yellow-600: funnel tier accent |
| Low | #2563EB | Blue-600: funnel tier accent |
| Note | #6B7280 | Gray-500: informational tiers |
| Clean cell | #F3F4F6 | Gray-100: empty tier states |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- Background: dark navy
- Aspect Ratio: 16:9 landscape
- Style: premium executive boardroom quality, 3D glass funnel aesthetic
- Layout zones:
  1. TOP HEADER (~10%): Title, date, CONFIDENTIAL badge
  2. MAIN FUNNEL (~60%): 4 translucent 3D trapezoid tiers stacked vertically, widest at top, each labeled with tier name and finding counts; severity-colored gradient connectors between tiers
  3. SIDEBAR (~25%): Risk metrics panel — total findings, risk reduction %, control coverage breakdown, key risk callouts
  4. FOOTER (~5%): Generator attribution

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy. All text white or light gray. Funnel tiers: translucent 3D trapezoids with glass-like material, soft ambient lighting. CONFIDENTIAL badge: red pill with white text.

### Gemini Prompt

**PREAMBLE** (verbatim from scaffold):

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

TOP SECTION: Title "Threat Model Risk Reduction Funnel: WellnessBank Mobile Banking Application" with date "2026-04-29", "CONFIDENTIAL" badge. Subtitle: "OWASP Mobile Top 10:2024 — 31 Findings Analyzed".

FUNNEL TIERS (4 solid tiers, widest at top, each labeled):
Tier 1 (widest, 100% width): "Threats Identified" — 32 findings: 13 Critical, 11 High, 3 Medium, 4 Low, 1 Note. Label: "Raw threat model output before scoring"
Tier 2 (slightly narrower): "Inherent Risk Scored" — 31 findings scored; aggregate inherent score 199.8. Distribution: 0 Critical, 9 High, 20 Medium, 2 Low (residual bands). Label: "Quantitative composite scoring applied"
Tier 3 (narrower): "Controls Applied" — 8 partial controls detected; 0 controls fully effective; 74.2% findings with no control. Coverage: 0.0% Found / 25.8% Partial / 74.2% Missing. Label: "Compensating controls assessed from architecture"
Tier 4 (narrowest, 90% of Tier 1 width): "Residual Risk" — 0 Critical, 9 High, 20 Medium, 2 Low. Aggregate residual score 186.9. Label: "Post-control residual exposure"

SIDEBAR METRICS:
"Total Findings: 31"
"Risk Reduction: 6.5%"
"Control Coverage: 25.8% Partial / 74.2% Missing"
"Highest-Risk Unmitigated: E-1 (WellnessBankDebugActivity)"
"Architecture: OWASP Mobile Top 10:2024 — M1 through M10 covered"

RISK REDUCTION NOTE (below funnel): "6.5% risk reduction achieved via 8 partial controls. 9 High-severity findings remain unmitigated. Priority: eliminate WellnessBankDebugActivity from production build and gate MoneyTransferActivity with signature-level permission."

FOOTER (bottom): "Generated by Tachi Threat Modeling Framework — Risk Reduction Funnel" in small light gray text, centered.

The overall impression should be a polished, premium risk reduction narrative — confident, clear, and visually sophisticated. Professional business language throughout, no technical jargon or color codes. Render as a flat, full-bleed graphic filling the entire 16:9 frame.
