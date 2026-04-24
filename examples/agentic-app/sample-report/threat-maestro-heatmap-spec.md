---
schema_version: "1.0"
template: "maestro-heatmap"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
---

# Threat Infographic Specification — MAESTRO Heatmap
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

### Cell-Level Grid (STRIDE+AI)

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
| 4 | R-3 | LLM Agent Orchestrator | Orchestrator denies issuing delegation messages or tool calls | High |
| 5 | E-1 | Guardrails Service | Prompt injection bypasses Guardrails and elevates attacker to Orchestrator trust level | High |

---

## 5. Architecture Threat Overlay

### Component-Layer Intersection Grid

MAESTRO layer labels: L1 = Foundation Model, L2 = Data Operations, L3 = Agent Framework, L4 = Deployment and Infrastructure (not populated), L5 = Evaluation and Observability, L6 = Security and Compliance, L7 = Agent Ecosystem

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| LLM Agent Orchestrator | Critical | — | — | — | — | — | — |
| Clinical Advisory Sub-Agent | — | — | — | — | — | — | Critical |
| MCP Tool Server | — | — | Critical | — | — | — | — |
| Guardrails Service | — | — | — | — | — | Critical | — |
| Audit Logger | — | — | — | — | Critical | — | — |
| Knowledge Base | — | High | — | — | — | — | — |
| User | — | — | — | — | — | — | Critical |

**Empty components** (zero MAESTRO-classified findings): Specialist Agent, Inter-Agent Communication Channel, Long-Running Learning Loop, External API — displayed as muted empty rows.

**MAESTRO Layer Distribution** (from extraction — per-layer aggregate not independently populated in extraction output; derived from grid):

| MAESTRO Layer | Components with Findings | Highest Severity |
|---------------|-------------------------|------------------|
| L1 — Foundation Model | LLM Agent Orchestrator | Critical |
| L2 — Data Operations | Knowledge Base | High |
| L3 — Agent Framework | MCP Tool Server | Critical |
| L4 — Deployment and Infrastructure | (none) | — |
| L5 — Evaluation and Observability | Audit Logger | Critical |
| L6 — Security and Compliance | Guardrails Service | Critical |
| L7 — Agent Ecosystem | Clinical Advisory Sub-Agent, User | Critical |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: grid cell fill (highest severity for component-layer intersection) |
| High | #EA580C | Orange-600: grid cell fill |
| Medium | #CA8A04 | Yellow-600: grid cell fill |
| Low | #2563EB | Blue-600: grid cell fill |
| Note | #6B7280 | Gray-500: informational only |
| Empty cell | Dark gray | Grid cells with no findings at that intersection |

### Layout Structure

- Background: Dark navy
- Aspect Ratio: 16:9 landscape
- Main body: Component-layer grid (center), legend panel (right side), top findings (bottom strip or left sidebar)
- Grid cells: Rounded rectangles, severity-colored fill, component name truncated to ≤25 chars
- Empty layer bands: Muted dark gray cells with no color
- MAESTRO layer column headers: L1 through L7 with descriptive tooltip names below
- Legend panel: Right side, color swatches with severity labels + component row labels

### Typography

- Title: Bold, 28-32pt equivalent
- Layer Column Headers: Semi-bold, 14pt
- Component Row Labels: Regular, 12-13pt
- Cell Severity Labels: Bold, 11pt, white text on colored cell
- Legend: Regular, 11pt

### Background

Dark navy. Grid cells use severity color fills on dark panel background. Empty cells use subtle dark gray rounded rectangles.

---

## 7. Gemini Prompt

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

TOP SECTION: Title "MAESTRO Layer Heatmap: Agentic AI Application" with date "2023-11-14" and "CONFIDENTIAL" badge. Subtitle: "Component × MAESTRO Layer Intersection — Residual Severity".

MAIN GRID (rows = components, columns = MAESTRO layers L1–L7):
Column headers: L1 Foundation Model | L2 Data Operations | L3 Agent Framework | L4 Infrastructure | L5 Observability | L6 Security | L7 Agent Ecosystem

Row data (color the cell with the severity, show severity initial in cell, gray if no finding):
LLM Agent Orchestrator: L1=red(Critical), L2=gray, L3=gray, L4=gray, L5=gray, L6=gray, L7=gray
Clinical Advisory Sub-Agent: L1=gray, L2=gray, L3=gray, L4=gray, L5=gray, L6=gray, L7=red(Critical)
MCP Tool Server: L1=gray, L2=gray, L3=red(Critical), L4=gray, L5=gray, L6=gray, L7=gray
Guardrails Service: L1=gray, L2=gray, L3=gray, L4=gray, L5=gray, L6=red(Critical), L7=gray
Audit Logger: L1=gray, L2=gray, L3=gray, L4=gray, L5=red(Critical), L6=gray, L7=gray
Knowledge Base: L1=gray, L2=orange(High), L3=gray, L4=gray, L5=gray, L6=gray, L7=gray
User: L1=gray, L2=gray, L3=gray, L4=gray, L5=gray, L6=gray, L7=red(Critical)
Specialist Agent: L1=gray, L2=gray, L3=gray, L4=gray, L5=gray, L6=gray, L7=gray (muted — no MAESTRO classification)
Inter-Agent Communication Channel: (muted — no MAESTRO classification)
Long-Running Learning Loop: (muted — no MAESTRO classification)

LEGEND PANEL (right side):
"SEVERITY LEGEND"
Red cell = Critical
Orange cell = High
Amber cell = Medium
Blue cell = Low
Dark gray cell = No finding at this intersection

"MOST EXPOSED LAYERS"
L1 Foundation Model: 1 component (LLM Agent Orchestrator — Critical)
L7 Agent Ecosystem: 2 components (Clinical Advisory Sub-Agent, User — Critical)
L3 Agent Framework: 1 component (MCP Tool Server — Critical)
L6 Security and Compliance: 1 component (Guardrails Service — Critical)
L5 Evaluation and Observability: 1 component (Audit Logger — Critical)
L2 Data Operations: 1 component (Knowledge Base — High)
L4 Infrastructure: No findings classified

TOP FINDINGS (bottom strip):
S-1 | User | L7 | Session token replay attack — High
AG-1 | LLM Orchestrator | L1 | Prompt injection autonomous action — High
E-2 | LLM Orchestrator | L1 | Orchestrator privilege self-escalation — High
E-1 | Guardrails | L6 | Guardrail bypass privilege elevation — High
LLM-13 | Clinical Advisory | L7 | Clinical prompt injection system override — High

FOOTER: "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
