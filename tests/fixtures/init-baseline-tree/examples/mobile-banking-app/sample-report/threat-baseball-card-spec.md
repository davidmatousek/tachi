---
schema_version: "1.4"
template: "baseball-card"
date: "2026-04-29"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 31
image_generated: false
---

# Threat Infographic Specification — Baseball Card

**Project**: WellnessBank Mobile Banking Application
**Template**: Baseball Card (Dark Dashboard)
**Data Source**: compensating-controls.md (residual risk tier)
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

**Chart Format**: Donut chart with proportional segments. Center text: "31 findings". Below the donut: severity legend with counts and percentages. Below that: "RESIDUAL RISK POSTURE: Residual risk — 0 Critical and 9 High findings across 12 components" in orange (High dominant).

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

> "Other" aggregates WellnessBankDebugActivity (1H+1M), WellnessPaySDK (0H+2M) — 4 findings total.

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

> Severity labels in Cell-Level Grid reflect **residual** severity from compensating-controls.md. AG and LLM columns are omitted (no AI/agentic components in this architecture).

---

## 4. Top Critical Findings

> No Critical residual findings. Listing top 5 High findings by residual score descending.

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | E-1 | WellnessBankDebugActivity | Debug Activity left in production release bypasses all authentication; any ADB user can execute privileged banking operations | High (8.5) |
| 2 | E-2 | MoneyTransferActivity | Exported money-transfer screen accepts external app commands to move funds without any login step | High (8.3) |
| 3 | T-3 | MoneyTransferActivity | Android inter-process messages from any installed app can hijack the money-movement flow | High (8.1) |
| 4 | T-4 | WellnessBank Android Client | App ships without code obfuscation or tampering detection, enabling reverse engineering and runtime hook injection | High (7.7) |
| 5 | I-4 | WellnessBank Android Client | 4-digit PIN key derivation runs only 1,000 iterations with no salt — PIN space exhausted in under one second | High (7.5) |

---

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| Mobile Banking Customer | High | 2 | 2 High findings — session replay and transaction non-repudiation |
| MoneyTransferActivity | High | 2 | 2 High findings — IPC intent hijacking and privilege escalation |
| WellnessBank Android Client | Medium | 10 | 3 High + 7 Medium — binary protection, cryptography, privacy, and auth gaps |
| WellnessBankCredentialCache | Medium | 3 | 1 High + 2 Medium — plaintext credential storage with no Keystore binding |
| Other (WellnessBankDebugActivity + WellnessPaySDK) | Medium | 4 | 1 High + 3 Medium — debug activity bypass and supply-chain integrity |
| WellnessBankLocalDB | Medium | 3 | 3 Medium — unencrypted SQLite, backup exposure, data tampering |
| WellnessBank Backend API | Low | 5 | 4 Medium + 1 Low — rate limiting, audit trail, authorization gaps |
| WellnessAnalyticsSDK | Low | 2 | 1 Medium + 1 Low — supply chain integrity and communication pinning |

**Risk Reduction**: 6.5% (199.8 inherent → 186.9 residual) — 8 partial controls; 23 findings with no control found

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: donut segment, heat map cells, finding card borders, risk posture badge |
| High | #EA580C | Orange-600: donut segment, heat map cells, finding card borders |
| Medium | #CA8A04 | Yellow-600: donut segment, heat map cells, finding card borders |
| Low | #2563EB | Blue-600: donut segment, heat map cells, finding card borders |
| Note | #6B7280 | Gray-500: informational only, excluded from visual risk distribution |
| Clean cell | #F3F4F6 | Gray-100: heat map analyzed with no findings |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- Background: dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape (1920x1080 minimum)
- Style: premium dark dashboard aesthetic, Figma-quality, modern corporate security report
- 4-Zone Layout:
  1. TOP SECTION (~10%): Title "Threat Model: WellnessBank Mobile Banking Application", date 2026-04-29, CONFIDENTIAL badge, subtitle "31 Residual Findings Across 12 Components"
  2. MIDDLE ROW (~50%): Left panel (donut chart — 0 Critical / 9 High / 20 Medium / 2 Low + residual risk posture), Center panel (component × STRIDE heat map grid), Right panel (top 5 High finding cards with orange left border)
  3. BOTTOM STRIP (~30%): Architecture threat overlay with 4 trust zones, risk weight bars, 6.5% risk reduction callout
  4. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy (#1E293B). All text white or light gray. Cards and panels: rounded corners, subtle drop shadows, generous whitespace.

### Gemini Prompt

**PREAMBLE** (verbatim from scaffold):

Create a premium, professional security risk dashboard with a polished, modern dark-theme aesthetic. This should look like a professionally designed Figma dashboard — not a data table or spreadsheet. The overall feel should be confident, sophisticated, and visually impressive — a formal security report artifact, not a presentation slide or boardroom scene. Render ONLY the dashboard itself as a flat document — no perspective, no 3D effects, no room or table context, no environmental background. The image should be the report, not a photo of the report.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical CSS specifications as visible text in the image. Only render the data labels, numbers, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: dark navy
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- All text on dark background: white or light gray
- Cards and panels: rounded corners, subtle drop shadows, generous whitespace
- Layout: 16:9 landscape
- Empty heat map cells: subtle dark gray

DATA CONTENT (render this as visible text):

TOP SECTION: Title "Threat Model: WellnessBank Mobile Banking Application" with date "2026-04-29" and "CONFIDENTIAL" badge. Subtitle: "31 Residual Findings Across 12 Components — OWASP Mobile Top 10:2024".

LEFT PANEL: Donut chart showing residual risk distribution: 0 Critical (red), 9 High (orange), 20 Medium (yellow), 2 Low (blue). Center text "31 findings". Below the donut: severity legend with counts and percentages (High 29%, Medium 65%, Low 6%). Below that: "RESIDUAL RISK POSTURE: 0 Critical and 9 High findings across 12 components. 6.5% risk reduction achieved via 8 partial controls."

CENTER PANEL: Heat map grid titled "Residual Risk Coverage Heat Map" with 8 component rows and 6 STRIDE threat categories as columns (S, T, R, I, D, E). Each cell MUST use the exact severity from this grid — do not infer or guess cell values:
WellnessBank Android Client: S=Medium, T=High, R=Medium, I=High, D=Medium, E=—
WellnessBank Backend API: S=Low, T=—, R=Medium, I=Low, D=High, E=Medium
WellnessBankCredentialCache: S=n/a, T=Medium, R=n/a, I=High, D=Medium, E=n/a
WellnessBankLocalDB: S=n/a, T=Medium, R=n/a, I=Medium, D=Medium, E=n/a
Mobile Banking Customer: S=High, T=n/a, R=Medium, I=n/a, D=n/a, E=n/a
MoneyTransferActivity: S=—, T=High, R=—, I=—, D=—, E=High
WellnessAnalyticsSDK: S=—, T=Medium, R=—, I=Low, D=—, E=—
Other: S=—, T=Medium, R=Medium, I=—, D=—, E=High
Color each cell by residual severity: orange for High, yellow/amber for Medium, blue for Low, dark gray for analyzed clean (—), charcoal for n/a.

RIGHT PANEL: Top 5 High finding cards in a vertical stack. Each card has an orange left border accent, finding ID in monospace, component name in bold, and a one-line threat description:
Card 1: "E-1" — WellnessBankDebugActivity — "Debug Activity in production release bypasses all authentication"
Card 2: "E-2" — MoneyTransferActivity — "Exported money-transfer screen accepts external commands to move funds"
Card 3: "T-3" — MoneyTransferActivity — "Android inter-process messages can hijack the money-movement flow"
Card 4: "T-4" — WellnessBank Android Client — "App ships without obfuscation or tampering detection"
Card 5: "I-4" — WellnessBank Android Client — "4-digit PIN key derivation exhausted in under one second"

BOTTOM STRIP: Architecture threat overlay showing 4 trust zones: User Zone (untrusted) with Mobile Banking Customer; Device Zone (semi-trusted) with WellnessBank Android Client, WellnessBankDebugActivity, MoneyTransferActivity, WellnessAnalyticsSDK, WellnessPaySDK, WellnessBankLocalDB, WellnessBankCredentialCache; Backend Zone (trusted) with WellnessBank Backend API, BackendUserAccountStore; External Services (untrusted) with Third-Party Analytics Provider, Third-Party Payment Provider. Risk weight bars: Mobile Banking Customer=High, MoneyTransferActivity=High, WellnessBank Android Client=Medium. Risk reduction callout: "6.5% residual risk reduction — 8 partial controls detected".

FOOTER: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
