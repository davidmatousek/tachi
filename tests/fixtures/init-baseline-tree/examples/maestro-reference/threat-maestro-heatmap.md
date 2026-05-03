---
schema_version: "1.0"
template: "maestro-heatmap"
date: "2026-04-16"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 112
image_generated: true
---

# Infographic Specification — MAESTRO Heatmap
## Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This specification is derived from the tachi canonical MAESTRO worked example. The underlying threat model analyzes a fictional Healthcare CDSS reference architecture for teaching purposes only — not a real clinical system. All 7 MAESTRO layers are populated and all 6 canonical agentic patterns are represented, making this the most complete MAESTRO heatmap in the tachi pipeline.

> **Data Source Note**: MAESTRO component-layer intersection data is sourced from threats.md Sections 3, 4, and 4a (individual finding MAESTRO Layer assignments). The compensating-controls.md Tier 1 source provides residual severity context. Since all 108 findings have 0% control coverage, qualitative severity from threats.md equals effective residual severity for all cells.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Healthcare Clinical Decision Support System (CDSS) |
| Scan Date | 2026-04-16 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 112 |
| Risk Posture | Residual risk — 0 Critical and 6 High findings across 20 components |
| Data Source | Tier 1 — compensating-controls.md + threats.md (MAESTRO layer assignments) |
| Schema Version | 1.4 |
| MAESTRO Coverage | Full — all 7 layers populated (L1-L7) |

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

### Component-Layer Intersection Grid

**Source**: threats.md individual finding MAESTRO Layer assignments from Sections 3, 4, 4a. Cell value = highest qualitative severity for findings at that component × MAESTRO layer intersection. "—" = no findings at that intersection.

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| Physician | — | — | — | — | — | — | Critical |
| Patient | — | — | — | — | — | — | High |
| Physician Clinical Portal | — | — | — | — | — | — | Critical |
| Patient Summary Generator | — | — | — | — | — | — | Medium |
| Inter-Agent Communication Channel | — | — | — | — | — | — | Critical |
| Supervisor Orchestrator | — | — | Critical | — | — | — | — |
| Diagnostic Agent | — | — | High | — | — | — | — |
| Treatment Planner Agent | — | — | High | — | — | — | — |
| Clinical MCP Tool Server | — | — | Critical | — | — | — | — |
| Clinical LLM | Critical | — | — | — | — | — | — |
| Risk Stratification Model | Critical | — | — | — | — | — | — |
| FHIR Resource Store | — | Critical | — | — | — | — | — |
| Clinical Guideline RAG Corpus | — | Critical | — | — | — | — | — |
| Medical Literature Vector Index | — | High | — | — | — | — | — |
| Model Inference API Gateway | — | — | — | High | — | — | — |
| EHR Ingestion Queue | — | — | — | High | — | — | — |
| Clinical Audit Log | — | — | — | — | High | — | — |
| Outcomes Telemetry and... | — | — | — | — | Critical | — | — |
| HIPAA RBAC + Policy Engine | — | — | — | — | — | High | — |
| Consent and De-identification... | — | — | — | — | — | Medium | — |

**Component name truncation** (for grid display — full names in all other sections):
- "Outcomes Telemetry and..." = "Outcomes Telemetry and Physician Override Audit Store"
- "Consent and De-identification..." = "Consent and De-identification Guardrail"

### Per-Layer Aggregate (for legend panel)

| Layer | Finding Count | Highest Severity | Components Covered |
|-------|---------------|------------------|-------------------|
| L1 — Foundation Model | 18 | Critical | Clinical LLM, Risk Stratification Model |
| L2 — Data Operations | 9 | Critical | FHIR Resource Store, Clinical Guideline RAG Corpus, Medical Literature Vector Index |
| L3 — Agent Framework | 30 | Critical | Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Clinical MCP Tool Server |
| L4 — Deployment Infrastructure | 11 | High | Model Inference API Gateway, EHR Ingestion Queue |
| L5 — Evaluation and Observability | 6 | Critical | Clinical Audit Log, Outcomes Telemetry and Physician Override Audit Store |
| L6 — Security and Compliance | 12 | High | HIPAA RBAC + Policy Engine, Consent and De-identification Guardrail |
| L7 — Agent Ecosystem | 22 | Critical | Physician, Patient, Physician Clinical Portal, Patient Summary Generator, Inter-Agent Communication Channel |

**Total**: 108 source findings across all 7 layers.

### Grid Density Notes

- **L7 (Agent Ecosystem)**: Most cells in this column are populated — 5 of 20 components map to L7. Includes the two external entities (Physician, Patient) which carry the highest composite scores.
- **L3 (Agent Framework)**: All 4 agent-layer components (Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Clinical MCP Tool Server) map to this layer — dense column.
- **L1 (Foundation Model)**: Both foundation models (Clinical LLM, Risk Stratification Model) map exclusively to this layer.
- **L2, L4, L5, L6**: Each has 2-3 components with exclusive layer assignment — sparse columns with clear zone clustering.
- **No cross-layer component assignments**: Each component maps to exactly one MAESTRO layer in this architecture (no mixed-layer components), producing a clean diagonal-like pattern in the grid.

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: grid cell fill for Critical intersections |
| High | #EA580C | Orange-600: grid cell fill for High intersections |
| Medium | #CA8A04 | Yellow-600: grid cell fill for Medium intersections |
| Low | #2563EB | Blue-600: grid cell fill for Low intersections |
| Empty cell | — | Subtle dark gray rounded rectangle |
| Note | #6B7280 | Gray-500: column/row header label text |

### Layout Structure

- Background: Dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape
- Style: Premium dark MAESTRO heatmap dashboard — Figma-quality
- Layout:
  1. TOP HEADER (~10%): Title "Healthcare CDSS — MAESTRO Component-Layer Heatmap", date, CONFIDENTIAL badge, subtitle "7 of 7 MAESTRO Layers × 20 Components — Full Coverage"
  2. MAIN GRID (~70%): Component names as rows (20 rows, left-aligned); MAESTRO layers L1-L7 as columns (7 columns). Each grid cell: rounded rectangle, severity-colored fill or dark gray empty. Cell text: severity label (Critical/High/Medium/Low) or "—"
  3. LEGEND PANEL (~20%): Right side. Per-layer aggregate bar chart showing finding counts; layer names; highest severity per layer; total finding count
  4. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis"

### Grid Visual Guidance

- Grid cells: rounded rectangles, generous padding, severity-colored fill
- Critical cells: bright red fill, white text
- High cells: orange fill, white text
- Medium cells: amber fill, white text
- Low cells: blue fill, white text
- Empty cells: subtle dark gray fill, no text
- Row labels (component names): white text, left-aligned, right-border line separating from grid
- Column headers (L1-L7 with layer name): white bold text, centered, top-border line separating from grid
- Most-populated layer column (L3, 30 findings): slightly brighter column header indicator

### Typography

- Title: Bold, 28-32pt equivalent
- Column Headers: Semi-bold, 14-16pt equivalent
- Row Labels: Regular, 12-14pt equivalent (truncate to 25 chars if needed)
- Cell Text: Bold, 10-12pt equivalent
- Legend Labels: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard. All text: white or light gray. Grid cells colored by severity; empty cells: subtle dark gray.

### Gemini Prompt

**PREAMBLE** (verbatim from JSON prompt_scaffold.preamble):
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

**DATA CONTENT**:

TOP HEADER: Title "Healthcare CDSS — MAESTRO Component-Layer Heatmap" with date "2026-04-16" and "CONFIDENTIAL" badge. Subtitle: "7 of 7 MAESTRO Layers × 20 Components — Full Coverage — Teaching Reference Scenario."

GRID MAIN SECTION: A 20-row × 7-column heatmap grid. Column headers (left to right): "L1 Foundation Model", "L2 Data Operations", "L3 Agent Framework", "L4 Deployment Infra", "L5 Eval & Observ.", "L6 Security", "L7 Agent Ecosystem". Row labels (top to bottom, 20 components): Physician, Patient, Physician Clinical Portal, Patient Summary Generator, Inter-Agent Comm. Channel, Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Clinical MCP Tool Server, Clinical LLM, Risk Stratification Model, FHIR Resource Store, Clinical Guideline RAG Corpus, Medical Literature Vector Index, Model Inference API Gateway, EHR Ingestion Queue, Clinical Audit Log, Outcomes Telemetry Store, HIPAA RBAC Engine, Consent Guardrail.

GRID CELL VALUES (render each non-empty cell with severity text; render empty cells as subtle gray with no text):
Row Physician: L7=Critical (red), all others empty
Row Patient: L7=High (orange), all others empty
Row Physician Clinical Portal: L7=Critical (red), all others empty
Row Patient Summary Generator: L7=Medium (amber), all others empty
Row Inter-Agent Comm. Channel: L7=Critical (red), all others empty
Row Supervisor Orchestrator: L3=Critical (red), all others empty
Row Diagnostic Agent: L3=High (orange), all others empty
Row Treatment Planner Agent: L3=High (orange), all others empty
Row Clinical MCP Tool Server: L3=Critical (red), all others empty
Row Clinical LLM: L1=Critical (red), all others empty
Row Risk Stratification Model: L1=Critical (red), all others empty
Row FHIR Resource Store: L2=Critical (red), all others empty
Row Clinical Guideline RAG Corpus: L2=Critical (red), all others empty
Row Medical Literature Vector Index: L2=High (orange), all others empty
Row Model Inference API Gateway: L4=High (orange), all others empty
Row EHR Ingestion Queue: L4=High (orange), all others empty
Row Clinical Audit Log: L5=High (orange), all others empty
Row Outcomes Telemetry Store: L5=Critical (red), all others empty
Row HIPAA RBAC Engine: L6=High (orange), all others empty
Row Consent Guardrail: L6=Medium (amber), all others empty

RIGHT LEGEND PANEL:
"Per-Layer Finding Count:
L3 Agent Framework: 30 findings — Critical
L7 Agent Ecosystem: 22 findings — Critical
L1 Foundation Model: 18 findings — Critical
L4 Deployment Infra: 11 findings — High
L6 Security: 12 findings — High
L2 Data Operations: 9 findings — Critical
L5 Eval & Observ.: 6 findings — Critical
Total: 108 source findings | 7 of 7 layers populated

Severity Legend:
Red = Critical | Orange = High | Amber = Medium | Blue = Low | Gray = No findings

Agentic Patterns Present (6 of 6):
trust_exploitation, agent_collusion,
communication_vulnerability, temporal_attack,
resource_competition, emergent_behavior"

**POSTAMBLE** (verbatim from JSON prompt_scaffold.postamble):
FOOTER: "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
