---
schema_version: "1.4"
template: "maestro-heatmap"
date: "2026-04-29"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 31
image_generated: false
---

# Threat Infographic Specification — MAESTRO Heatmap

**Project**: WellnessBank Mobile Banking Application
**Template**: MAESTRO Heatmap (CSA MAESTRO Component-Layer Grid)
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
| 1 | E-1 | WellnessBankDebugActivity | Debug Activity in production bypasses all authentication — any ADB user executes privileged banking operations | High (8.5) |
| 2 | E-2 | MoneyTransferActivity | Exported money-transfer screen accepts external app commands without login | High (8.3) |
| 3 | T-3 | MoneyTransferActivity | Android inter-process messages from any installed app hijack money-movement flow | High (8.1) |
| 4 | T-4 | WellnessBank Android Client | App ships without code obfuscation or tampering detection | High (7.7) |
| 5 | I-4 | WellnessBank Android Client | 4-digit PIN key derivation uses 1,000 iterations and no salt | High (7.5) |

---

## 5. Architecture Threat Overlay

### Component-Layer Intersection Grid

> **Architecture context**: This is a traditional mobile banking application with zero AI/ML/agentic components. The MAESTRO layer assignment data from the extraction script maps components to L7 and L2 only (plus Unclassified for 4 findings). L1/L3/L4/L5/L6 columns show "—" for all components because no AI/ML components exist in this architecture.

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| WellnessBank Android Client | — | — | — | — | — | — | Critical* |
| WellnessBank Backend API | — | — | — | — | — | — | High |
| WellnessBankCredentialCache | — | Critical* | — | — | — | — | — |
| WellnessBankLocalDB | — | Critical* | — | — | — | — | — |
| Mobile Banking Customer | — | — | — | — | — | — | High |
| MoneyTransferActivity | — | — | — | — | — | — | — |
| WellnessAnalyticsSDK | — | — | — | — | — | — | — |
| WellnessBankDebugActivity | — | — | — | — | — | — | — |
| WellnessPaySDK | — | — | — | — | — | — | — |

> * The extraction script reports inherent severity in the MAESTRO heatmap cells (before compensating controls). WellnessBank Android Client L7 = Critical (inherent S-1, S-2 pre-control); WellnessBankCredentialCache L2 = Critical (inherent I-7 pre-control); WellnessBankLocalDB L2 = Critical (inherent I-3 pre-control). Residual severities for these cells are Medium/High as shown in Section 3.

> **Single-column concentration**: L7 and L2 are the only columns with non-empty cells. All other columns (L1, L3, L4, L5, L6) show "—" for all components — this is architecturally correct and expected for a non-AI/ML application.

**Layer Column Annotations**:
- L1 (Foundation Model): "—" all rows — No foundation model components
- L2 (Data Operations): 2 components with findings (WellnessBankCredentialCache, WellnessBankLocalDB)
- L3 (Agent Reasoning): "—" all rows — No AI reasoning components
- L4 (Agent Memory): "—" all rows — No AI memory components
- L5 (Agent Action): "—" all rows — No AI action components
- L6 (Agent Orchestration): "—" all rows — No AI orchestration components
- L7 (Agent Ecosystem): 3 components with findings (WellnessBank Android Client, WellnessBank Backend API, Mobile Banking Customer)

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: grid cells (inherent severity shown) |
| High | #EA580C | Orange-600: grid cells |
| Medium | #CA8A04 | Yellow-600: grid cells |
| Low | #2563EB | Blue-600: grid cells |
| Note | #6B7280 | Gray-500: informational cells |
| Clean cell | #F3F4F6 | Gray-100: "—" cells (analyzed, no findings) |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders, grid lines |

### Layout Structure

- Background: dark navy
- Aspect Ratio: 16:9 landscape
- Main body: Component-layer intersection grid occupying ~70% of canvas width
- Legend panel: right ~25% — color swatches with severity labels and finding counts
- Grid: rows = components (top 5 by findings + key others), columns = L1 through L7
- Grid cells: rounded rectangles with severity-colored fill; "—" cells in subtle dark gray
- Column headers: L1 through L7 with MAESTRO layer names in small text
- Row labels: component names left-aligned

### Typography

- Title: Bold, 28-32pt equivalent
- Grid headers: Semi-bold, 14-16pt equivalent
- Grid cell labels: Bold, 12-14pt equivalent
- Legend: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B). All text white or light gray. Grid cells: rounded rectangles with generous padding; severity-filled cells use white text.

### Gemini Prompt

**PREAMBLE** (verbatim from scaffold):

Create a premium, professional MAESTRO component-layer heatmap dashboard with a polished, modern dark-theme aesthetic. This should look like a professionally designed Figma dashboard — not a data table or spreadsheet. The overall feel should be confident, sophisticated, and visually impressive — a formal security report artifact, not a presentation slide or boardroom scene. Render ONLY the dashboard itself as a flat document — no perspective, no 3D effects, no room or table context, no environmental background. The image should be the report, not a photo of the report.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical CSS specifications as visible text in the image. Only render the data labels, numbers, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: dark navy
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- Empty grid cells: subtle dark gray rounded rectangles
- All text on dark background: white or light gray
- Grid cells: rounded rectangles with generous padding
- Legend panel: right side, visually distinct section with color swatches
- Layout: 16:9 landscape

DATA CONTENT (render this as visible text):

TITLE: "CSA MAESTRO Component-Layer Heatmap: WellnessBank Mobile Banking Application" with date "2026-04-29" and "CONFIDENTIAL" badge. Subtitle: "31 Residual Findings | Traditional Mobile Application — No AI/ML Components".

GRID (components as rows, L1–L7 as columns):

Column headers: L1 (Foundation Model), L2 (Data Operations), L3 (Agent Reasoning), L4 (Agent Memory), L5 (Agent Action), L6 (Agent Orchestration), L7 (Agent Ecosystem)

Rows (use exact severity labels from this grid — do not infer):
WellnessBank Android Client: L1=—, L2=—, L3=—, L4=—, L5=—, L6=—, L7=Critical (red cell)
WellnessBank Backend API: L1=—, L2=—, L3=—, L4=—, L5=—, L6=—, L7=High (orange cell)
WellnessBankCredentialCache: L1=—, L2=Critical (red cell), L3=—, L4=—, L5=—, L6=—, L7=—
WellnessBankLocalDB: L1=—, L2=Critical (red cell), L3=—, L4=—, L5=—, L6=—, L7=—
Mobile Banking Customer: L1=—, L2=—, L3=—, L4=—, L5=—, L6=—, L7=High (orange cell)
MoneyTransferActivity: all — (dark gray cells)
WellnessAnalyticsSDK: all — (dark gray cells)
WellnessBankDebugActivity: all — (dark gray cells)
WellnessPaySDK: all — (dark gray cells)

ARCHITECTURE NOTE (below grid): "L1, L3, L4, L5, L6 columns show no findings — this is a traditional mobile banking application with no AI/ML/agentic components. Risk concentrates at L7 (runtime) and L2 (data storage)."

LEGEND PANEL (right side):
Severity swatches: Critical (red), High (orange), Medium (yellow), Low (blue), Empty (dark gray)
Finding summary: "31 total findings | 9 High | 20 Medium | 2 Low"
"Most exposed: L7 — Agent Ecosystem (21 findings)"
"Data risk: L2 — Data Operations (7 findings)"

FOOTER: "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
