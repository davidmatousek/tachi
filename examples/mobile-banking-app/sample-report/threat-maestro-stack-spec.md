---
schema_version: "1.4"
template: "maestro-stack"
date: "2026-04-29"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 31
image_generated: false
---

# Threat Infographic Specification — MAESTRO Stack

**Project**: WellnessBank Mobile Banking Application
**Template**: MAESTRO Stack (CSA MAESTRO Layer Analysis)
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
| 1 | E-1 | WellnessBankDebugActivity | Debug Activity in production bypasses all authentication — any ADB user can execute privileged banking operations | High (8.5) |
| 2 | E-2 | MoneyTransferActivity | Exported money-transfer screen accepts external app commands without login | High (8.3) |
| 3 | T-3 | MoneyTransferActivity | Android inter-process messages from any installed app hijack money-movement flow | High (8.1) |
| 4 | T-4 | WellnessBank Android Client | App ships without code obfuscation or tampering detection | High (7.7) |
| 5 | I-4 | WellnessBank Android Client | 4-digit PIN key derivation uses 1,000 iterations, no salt — exhausted in under one second | High (7.5) |

---

## 5. Architecture Threat Overlay

### MAESTRO Layer Distribution

> **Architecture note**: This is a traditional mobile banking application with no AI/ML/agentic components. MAESTRO layer assignments are skewed: the vast majority of findings fall on L7 (Agent Ecosystem — mobile app runtime and user interaction layer) and L2 (Data Operations — local storage layer). L1, L3, L4, L5, L6 have zero findings. This distribution is architecturally expected for a STRIDE analysis of a non-AI mobile application.

| Layer | Name | Finding Count (Inherent) | Highest Severity | Top Findings |
|-------|------|--------------------------|------------------|--------------|
| L7 | Agent Ecosystem | 21 | Critical (inherent) / High (residual) | S-1, S-2, S-3, S-4, S-5, T-4, R-1, R-2, R-3, I-1, I-2, I-4, I-7, I-8, I-9, D-1, D-2, E-1*, E-2*, E-3 |
| L2 | Data Operations | 7 | Critical (inherent) / Medium (residual) | T-5, T-6, I-3, I-7, D-3, D-4 |
| Unclassified | Unclassified | 4 | Critical (inherent) / High (residual) | T-1 (WellnessAnalyticsSDK), T-2 (WellnessPaySDK), T-3 (MoneyTransferActivity), E-1 (WellnessBankDebugActivity) |
| L1 | Foundation Model | 0 | — | — |
| L3 | Agent Reasoning | 0 | — | — |
| L4 | Agent Memory | 0 | — | — |
| L5 | Agent Action | 0 | — | — |
| L6 | Agent Orchestration | 0 | — | — |

> * E-1 and E-2 appear Unclassified in threats.md (MAESTRO Layer: Unclassified) but are categorized under L7 in the MAESTRO context because debug/privilege escalation findings on exported Android Activities map to the runtime app interaction tier.
>
> **Most Exposed Layer**: L7 (Agent Ecosystem) — 21 of 31 findings (68%); High residual severity

**Layer Finding Summary (Residual)**:
- L7: 21 findings — 7 High residual (S-5, I-2, I-4, I-7, D-2, E-1*, E-2*), 13 Medium, 1 Low
- L2: 7 findings — 0 High, 6 Medium, 1 Low (data storage and caching layer)
- Unclassified: 4 findings — 2 High (E-1, T-3), 2 Medium
- L1/L3/L4/L5/L6: 0 findings each (no AI/ML/agentic components)

### 1 Layer with Findings: Distribution Note

6 of 7 MAESTRO layers have zero findings. Sidebar should note: "1 Active MAESTRO Layer (L7), 5 Empty AI/ML Layers. This is a traditional mobile application with no AI components."

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: layer band accent, finding badge borders |
| High | #EA580C | Orange-600: layer band accent, finding badge borders |
| Medium | #CA8A04 | Yellow-600: layer band accent |
| Low | #2563EB | Blue-600: layer band accent |
| Note | #6B7280 | Gray-500: empty layer bands |
| Clean cell | #F3F4F6 | Gray-100: empty layer bands (muted) |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- Background: dark navy
- Aspect Ratio: 16:9 landscape
- 3-zone layout:
  1. TOP HEADER: Title, date, CONFIDENTIAL badge, subtitle
  2. MAIN BODY: Left ~65% = MAESTRO stack (L7 at top through L1 at bottom, horizontal bands); Right ~30% = sidebar with top findings cards and metrics
  3. FOOTER: Generator attribution

- Layer bands ordered L7 (top, most-exposed) through L1 (bottom):
  - L7: fully highlighted (brighter background, wider left border accent — orange) — 21 findings
  - L2: highlighted (moderate emphasis — yellow) — 7 findings
  - Unclassified: moderate emphasis — 4 findings
  - L1, L3, L4, L5, L6: muted dark backgrounds, grayed text, labeled with "0 findings"

### Typography

- Title: Bold, 28-32pt equivalent
- Layer Labels: Semi-bold, 18-22pt equivalent
- Finding counts: Bold, 14-16pt equivalent
- Data Labels: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B). All text white or light gray. Layer bands: horizontal bars with rounded left accent strips.

### Gemini Prompt

**PREAMBLE** (verbatim from scaffold):

Create a premium, professional security risk dashboard with a polished, modern dark-theme aesthetic. This should look like a professionally designed Figma dashboard — not a data table or spreadsheet. The overall feel should be confident, sophisticated, and visually impressive — a formal security report artifact, not a presentation slide or boardroom scene. Render ONLY the dashboard itself as a flat document — no perspective, no 3D effects, no room or table context, no environmental background. The image should be the report, not a photo of the report.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical CSS specifications as visible text in the image. Only render the data labels, numbers, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: dark navy
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- All text on dark background: white or light gray
- Cards and bands: rounded corners, subtle drop shadows, generous whitespace
- Layout: 16:9 landscape, 3-zone (top header, main body split into stack + sidebar, footer)
- Layer bands: horizontal bars stacked vertically, L7 at top through L1 at bottom
- Most-exposed layer band: brighter background, wider left border accent
- Empty layer bands: muted, darker background, grayed text

DATA CONTENT (render this as visible text):

TOP SECTION: Title "CSA MAESTRO Layer Analysis: WellnessBank Mobile Banking Application" with date "2026-04-29" and "CONFIDENTIAL" badge. Subtitle: "31 Residual Findings | OWASP Mobile Top 10:2024 | Traditional Mobile Application — No AI Components".

MAESTRO STACK (7 horizontal bands, L7 at top, L1 at bottom):

L7 — Agent Ecosystem (MOST EXPOSED): 21 findings — 7 High, 13 Medium, 1 Low. Top findings: S-5 (session token replay), I-4 (weak cryptography), I-2 (privacy controls), I-7 (credential storage), D-2 (rate limiting). Wide orange left accent border. Full-brightness band.

L2 — Data Operations: 7 findings — 0 High, 6 Medium, 1 Low. Top findings: T-5 (database tampering), T-6 (credential cache), I-3 (local database backup exposure). Yellow left accent border. Medium-brightness band.

Unclassified: 4 findings — 2 High, 2 Medium. Findings: T-1 (supply chain — analytics SDK), T-2 (supply chain — payment SDK), T-3 (intent hijacking), E-1 (debug activity bypass). Orange accent.

L6 — Agent Orchestration: 0 findings. Empty band — "No AI orchestration components in this architecture". Gray/muted.
L5 — Agent Action: 0 findings. Empty band — "No AI agent action components". Gray/muted.
L4 — Agent Memory: 0 findings. Empty band — "No AI memory components". Gray/muted.
L3 — Agent Reasoning: 0 findings. Empty band — "No AI reasoning components". Gray/muted.
L1 — Foundation Model: 0 findings. Empty band — "No foundation model components". Gray/muted.

SIDEBAR — Top Findings:
"E-1" (High 8.5) — WellnessBankDebugActivity — Debug Activity bypasses authentication
"E-2" (High 8.3) — MoneyTransferActivity — External commands can initiate fund transfers
"T-3" (High 8.1) — MoneyTransferActivity — Intent hijacking into money movement
"T-4" (High 7.7) — WellnessBank Android Client — No tampering detection
"I-4" (High 7.5) — WellnessBank Android Client — Weak PIN cryptography

SIDEBAR — Architecture Note:
"1 Active MAESTRO Layer (L7), 5 Empty AI/ML Layers. This is a traditional mobile application with no AI components — MAESTRO mapping shows concentrated risk at the app runtime tier."

FOOTER: "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
