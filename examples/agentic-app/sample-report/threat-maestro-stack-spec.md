---
schema_version: "1.0"
template: "maestro-stack"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
---

# Threat Infographic Specification — MAESTRO Stack
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

### MAESTRO Layer Distribution (Per-Layer Stack)

MAESTRO 7-layer model (L7 top through L1 bottom per stack convention):

| Layer | Name | Finding Count | Highest Severity | Top Findings |
|-------|------|---------------|------------------|--------------|
| L7 | Agent Ecosystem | 18 (S-9, T-9, R-9, I-9, D-9, E-7, S-1, R-1 + Clinical LLM/OI/MI) | Critical (inherent) / High (residual) | S-9: ClinAdvisor receives unauthenticated clinical queries; E-7: Clinical sub-agent self-authorizes elevated KB access |
| L6 | Security and Compliance | 8 (S-2, T-1, R-2, I-1, D-1, E-1) | Critical (inherent) / High (residual) | E-1: Guardrails bypass elevates attacker; D-1: Guardrails resource exhaustion |
| L5 | Evaluation and Observability | 3 (T-7, D-7, I-7) | Critical (inherent) / Medium (residual) | I-7: Audit Logger unauthorized read exposes full agent operational history; T-7: Log tampering corrupts training signals |
| L4 | Deployment and Infrastructure | 0 | — | No findings classified to L4 |
| L3 | Agent Framework | 6 (S-6, T-5, R-6, D-5, E-5, AG-5, AG-6) | Critical (inherent) / High (residual) | E-5: Tool Server executes with credentials accessible to unauthorized callers; AG-5: Tool call injection from compromised LLM output |
| L2 | Data Operations | 3 (T-6, D-6, I-6) | High (inherent and residual) | T-6: Knowledge Base corpus poisoning via write-access compromise; I-6: Full corpus exfiltration via vector search |
| L1 | Foundation Model | 22 (S-3, T-2, R-3, I-2, D-2, E-2, AG-1, AG-2, AG-7, LLM-1 through LLM-12) | Critical (inherent) / High (residual) | AG-1: Prompt injection causes autonomous unauthorized actions; E-2: Orchestrator self-authorizes elevated operations |

**Most Exposed Layer**: L1 — Foundation Model (22 findings, all High or Critical inherent severity, 11 High residual)

**Unclassified**: 24 findings carry "Unclassified" MAESTRO layer — distributed across S-4, S-5, S-7, S-8, T-3, T-4, T-8, R-4, R-5, R-7, R-8, I-3, I-4, I-8, D-3, D-4, D-7, D-8, E-3, E-4, E-6, AG-3, AG-4, AG-7.

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: layer band accent, most-exposed band highlight |
| High | #EA580C | Orange-600: layer band accent, finding badges |
| Medium | #CA8A04 | Yellow-600: layer band accent |
| Low | #2563EB | Blue-600: layer band accent |
| Note | #6B7280 | Gray-500: informational only |
| Empty band | Dark muted bg | Layers with zero findings — grayed text, darker background |

### Layout Structure

- Background: Dark navy
- Aspect Ratio: 16:9 landscape
- 3-zone layout:
  - TOP HEADER: Title, date, CONFIDENTIAL badge, risk posture summary
  - MAIN BODY: Left 65% = MAESTRO layer stack (horizontal bands L7 top → L1 bottom), Right 35% = sidebar (risk summary, top findings)
  - FOOTER: Attribution
- Layer bands: Horizontal bars stacked vertically, L7 at top, L1 at bottom
- Most-exposed layer band (L1): Brighter background, wider left border accent in orange (High residual)
- Empty layer bands (L4): Muted darker background, grayed text
- Unclassified band: Listed separately at bottom of stack with gray accent

### Typography

- Title: Bold, 28-32pt equivalent
- Layer Name Labels: Semi-bold, 16-18pt equivalent
- Finding Count Labels: Bold, 14pt
- Sidebar Text: Regular, 12pt
- Footer: Light gray, 10pt

### Background

Dark navy. Layer bands use slightly varied background tones (most-exposed brighter). Sidebar has distinct panel background.

---

## 7. Gemini Prompt

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

TOP SECTION: Title "MAESTRO Stack Analysis: Agentic AI Application" with date "2023-11-14" and "CONFIDENTIAL" badge. Subtitle: "CSA MAESTRO Layer Threat Distribution — 81 Residual Findings".

MAIN STACK (left 65%, horizontal bands stacked L7 top to L1 bottom):

L7 — Agent Ecosystem (HIGHLIGHT — bright orange left border accent, 18 findings):
"18 findings | Highest: High | Components: Clinical Advisory Sub-Agent (13), User (2), Specialist Agent (3)"
Top: "S-9: Unauthenticated clinical queries to sub-agent" | "E-7: Sub-agent self-authorizes elevated KB access"

L6 — Security and Compliance (8 findings, orange accent):
"8 findings | Highest: High | Component: Guardrails Service"
Top: "E-1: Prompt injection bypasses Guardrails" | "D-1: Guardrails resource exhaustion via prompt flooding"

L5 — Evaluation and Observability (3 findings, amber accent):
"3 findings | Highest: Medium | Component: Audit Logger"
Top: "I-7: Unauthorized Audit Logger read exposes full agent history" | "T-7: Log tampering corrupts training data"

L4 — Deployment and Infrastructure (muted — no findings):
"0 findings | No threats classified to infrastructure layer"

L3 — Agent Framework (7 findings, orange accent):
"7 findings | Highest: High | Component: MCP Tool Server"
Top: "E-5: Tool Server executes with exposed credentials" | "AG-5: Tool call injection from compromised agent output"

L2 — Data Operations (3 findings, orange accent):
"3 findings | Highest: High | Component: Knowledge Base"
Top: "T-6: Knowledge Base corpus poisoning" | "I-6: Full corpus exfiltration via vector search"

L1 — Foundation Model (MOST EXPOSED — brightest band, orange accent, 22 findings):
"22 findings | Highest: High | Component: LLM Agent Orchestrator (all 22)"
Top: "AG-1: Prompt injection causes autonomous unauthorized actions" | "E-2: Orchestrator self-authorizes elevated operations"

UNCLASSIFIED (bottom, gray accent):
"24 findings | Unclassified MAESTRO layer | Distributed across 12 components"

SIDEBAR (right 35%):
"RISK SUMMARY"
Total Residual Findings: 81
Most Exposed Layer: L1 Foundation Model (22 findings)
Second Exposed: L7 Agent Ecosystem (18 findings)
Empty Layers: 1 (L4 Infrastructure)
Unclassified: 24 findings

"TOP RESIDUAL FINDINGS"
S-1 | User | L7 — Session token replay (score 8.2)
AG-1 | LLM Orchestrator | L1 — Prompt injection autonomy (score 7.8)
E-2 | LLM Orchestrator | L1 — Orchestrator privilege escalation (score 7.8)
R-3 | LLM Orchestrator | L1 — Denial of delegation traceability (score 7.8)
E-1 | Guardrails | L6 — Guardrail bypass elevation (score 7.7)

FOOTER: "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
