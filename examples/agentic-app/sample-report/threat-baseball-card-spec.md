---
schema_version: "1.0"
template: "baseball-card"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
---

# Threat Infographic Specification — Baseball Card
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

**Chart Format**: Donut chart. Dominant segment: Medium (amber/yellow, 77%). Donut center text: "81 findings".

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

Highest residual severity per component × STRIDE+AI category (S=Spoofing, T=Tampering, R=Repudiation, I=Information Disclosure, D=Denial of Service, E=Elevation of Privilege, AG=Agentic, LLM=LLM):

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|-----|-----|
| LLM Agent Orchestrator | High | High | High | High | High | High | High | High |
| Clinical Advisory Sub-Agent | High | High | High | High | Medium | Medium | — | High |
| Specialist Agent | Medium | High | Medium | Medium | Medium | Medium | High | — |
| Long-Running Learning Loop | High | High | Medium | Medium | Medium | High | High | — |
| MCP Tool Server | High | High | Medium | Medium | High | High | High | — |
| Inter-Agent Communication Channel | Medium | High | Low | High | Medium | High | High | — |
| Guardrails Service | Medium | Medium | Medium | Medium | High | High | — | — |
| Other (User, KB, Audit Logger, External API) | High | Medium | Low | Medium | Low | — | — | — |

---

## 4. Top Critical Findings

No Critical residual-severity findings identified. Top High-residual findings shown (by residual score descending):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | Attacker replays stolen session tokens to impersonate a legitimate user, bypassing authentication | High |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions | High |
| 3 | E-2 | LLM Agent Orchestrator | Orchestrator self-authorizes elevated operations via privileged access to tools, KB, and sub-agents | High |
| 4 | R-3 | LLM Agent Orchestrator | Orchestrator denies issuing a delegation message or tool call; no non-repudiable action log | High |
| 5 | E-1 | Guardrails Service | Prompt injection bypasses Guardrails and elevates attacker to trusted Orchestrator caller privilege | High |

---

## 5. Architecture Threat Overlay

**Risk Reduction: 0.5%** (469.4 inherent → 467.2 residual — near-zero reduction; controls largely absent)

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | Medium | 18 | 11 High + 7 Medium findings; avg residual 2.6 — dominant orchestration hub with privileged access to all sub-systems |
| Guardrails Service | Medium | 6 | 1 High + 5 Medium findings; avg residual 2.2 — sole input validation barrier; bypass elevates any user to trusted caller |
| MCP Tool Server | Medium | 8 | 2 High + 6 Medium findings; avg residual 2.2 — external execution broker; tool injection enables external API abuse |
| Clinical Advisory Sub-Agent | Medium | 12 | 1 High + 11 Medium findings; avg residual 2.1 — clinical output path with no HITL; data leakage risk to audit trail |
| Specialist Agent | Medium | 10 | 1 High + 9 Medium findings; avg residual 2.1 — autonomous delegated worker; task injection achieves unauthorized tool calls |
| Inter-Agent Communication Channel | Medium | 7 | 7 Medium findings; avg residual 2.0 — shared message bus with no sender authentication |
| Long-Running Learning Loop | Medium | 9 | 9 Medium findings; avg residual 2.0 — temporal attack vector via training data poisoning |
| Other | Low | 11 | 1 High + 8 Medium + 2 Low findings; avg residual 1.9 — User, KB, Audit Logger, External API combined |

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

- Background: Dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape (1920x1080 minimum)
- Style: Premium dark-theme professional security dashboard. Sans-serif typography. Polished Figma-style aesthetic.
- 4-Zone Layout:
  1. TOP SECTION (~10%): Title "Threat Model: Agentic AI Application", date "2023-11-14", CONFIDENTIAL badge (red pill), subtitle "81 Findings — Residual Risk After Control Analysis"
  2. MIDDLE ROW (~50%): Left panel (donut chart + residual risk posture), Center panel (component × STRIDE+AI heat map), Right panel (top 5 High-residual finding cards with orange left border)
  3. BOTTOM STRIP (~30%): Architecture overlay — 3 trust zones (User Zone, Application Zone, External Services), component boxes inside zones, data flow arrows colored by highest residual severity, Risk Reduction badge "0.5% reduction"
  4. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy (#1E293B). All text: white or light gray on dark panels. Finding cards: slightly lighter panel background with orange left-border accent.

---

## 7. Gemini Prompt

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

TOP SECTION: Title "Threat Model: Agentic AI Application" with date "2023-11-14" and "CONFIDENTIAL" badge. Subtitle: "Agentic AI Application — 81 Residual Findings Across 11 Components".

LEFT PANEL: Donut chart showing residual risk distribution: 0 Critical (red), 17 High (orange), 62 Medium (amber), 2 Low (blue). Center text "81 findings". Below the donut: severity legend with counts and percentages. Below that: "RESIDUAL RISK: 0 Critical / 17 High — 0.5% risk reduction after control analysis. Near-zero control coverage detected — remediation urgently required."

CENTER PANEL: Heat map grid titled "Residual Coverage Heat Map" with components as rows and 8 threat categories as columns (S, T, R, I, D, E, AG, LLM). Each cell MUST use the exact severity from this grid — do not infer or guess cell values:
LLM Agent Orchestrator: S=High, T=High, R=High, I=High, D=High, E=High, AG=High, LLM=High
Clinical Advisory Sub-Agent: S=High, T=High, R=High, I=High, D=Medium, E=Medium, AG=—, LLM=High
Specialist Agent: S=Medium, T=High, R=Medium, I=Medium, D=Medium, E=Medium, AG=High, LLM=—
Long-Running Learning Loop: S=High, T=High, R=Medium, I=Medium, D=Medium, E=High, AG=High, LLM=—
MCP Tool Server: S=High, T=High, R=Medium, I=Medium, D=High, E=High, AG=High, LLM=—
Inter-Agent Communication Channel: S=Medium, T=High, R=Low, I=High, D=Medium, E=High, AG=High, LLM=—
Guardrails Service: S=Medium, T=Medium, R=Medium, I=Medium, D=High, E=High, AG=—, LLM=—
Other: S=High, T=Medium, R=Low, I=Medium, D=Low, E=—, AG=—, LLM=—
Color each cell: orange for High, amber for Medium, blue for Low, dark gray for no findings (—). Show severity initial in each cell.

RIGHT PANEL: Top 5 High-residual finding cards in a vertical stack. Each card has an orange left border accent, finding ID in monospace, component name in bold, and one-line threat description:
Card 1: S-1 | User | Attacker replays stolen session tokens to impersonate a legitimate user
Card 2: AG-1 | LLM Agent Orchestrator | Prompt injection causes autonomous execution of unauthorized actions
Card 3: E-2 | LLM Agent Orchestrator | Orchestrator self-authorizes elevated operations across tools and sub-agents
Card 4: R-3 | LLM Agent Orchestrator | Orchestrator denies having issued delegation messages or tool calls
Card 5: E-1 | Guardrails Service | Prompt injection bypasses Guardrails and elevates attacker privilege

BOTTOM STRIP: Architecture overlay showing 3 trust zones as labeled horizontal bands: "User Zone" (User), "Application Zone" (LLM Agent Orchestrator, Guardrails Service, MCP Tool Server, Clinical Advisory Sub-Agent, Specialist Agent, Inter-Agent Communication Channel, Long-Running Learning Loop, Knowledge Base, Audit Logger), "External Services" (External API). Data flow arrows between zones colored orange (High residual). Risk Reduction badge: "0.5% Risk Reduction — 3 of 83 findings have partial controls".

FOOTER: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
