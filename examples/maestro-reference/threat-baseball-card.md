---
schema_version: "1.0"
template: "baseball-card"
date: "2026-04-16"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 112
image_generated: true
---

# Infographic Specification — Baseball Card
## Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This specification is derived from the tachi canonical MAESTRO worked example. The underlying threat model analyzes a fictional Healthcare CDSS reference architecture for teaching purposes only — not a real clinical system. All 108 source findings scored as no-control-found because the target codebase (tachi pipeline toolkit) does not implement clinical application controls. This infographic illustrates the structural shape of a compensating-controls output.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Healthcare Clinical Decision Support System (CDSS) |
| Scan Date | 2026-04-16 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 112 |
| Risk Posture | Residual risk — 0 Critical and 6 High findings across 20 components |
| Data Source | Tier 1 — compensating-controls.md (0% control coverage; residual equals inherent) |
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

**Chart Format**: Donut chart. Dominant segment: Medium (amber, 93%). The four-dimensional composite scoring model applies reachability penalties — internal Trusted-zone components carry a reachability floor of 1.0, moderating composite scores substantially for all 20 internal components. Highest-risk finding: S-1 (Physician, composite 8.4 — credential replay).

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

Per-component highest residual severity by STRIDE+AI category (sourced from compensating-controls.md; residual severity equals inherent severity — 0% control coverage):

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|----|-----|
| Supervisor Orchestrator | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Clinical LLM | Medium | Medium | Medium | Medium | Medium | Medium | — | Medium |
| Risk Stratification Model | Medium | Medium | Medium | Medium | Medium | Medium | — | Medium |
| Diagnostic Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Inter-Agent Communication Channel | High | High | Medium | Medium | Medium | Medium | Medium | — |
| Treatment Planner Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Clinical MCP Tool Server | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Other (13 additional components) | High | High | Medium | High | Medium | High | Medium | — |

---

## 4. Top Critical Findings

No Critical residual findings exist (all inherent Critical findings score as residual High or Medium under 0% control coverage, with composite scoring driven by reachability penalties for internal zone components). Top 5 by composite score descending:

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | Physician | Attacker replays or forges clinical query credentials to gain unauthorized access | High (8.4) |
| 2 | S-2 | Patient | Attacker submits fraudulent EHR update events by spoofing patient identity | High (7.4) |
| 3 | D-1 | Physician Clinical Portal | Attacker floods portal with clinical query requests causing service disruption | High (7.1) |
| 4 | E-1 | Physician Clinical Portal | Attacker escalates from low-privilege session to gain elevated portal access | High (7.0) |
| 5 | S-5 | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messages causing specialist agents to act on forged commands | High (7.0) |

---

## 5. Architecture Threat Overlay

**Risk Reduction Summary**: Risk Reduction: 0.0% (inherent score 570.6 → residual score 570.6). Control Coverage: 0% Found / 0% Partial / 100% Missing. This is the accurate, expected result of scanning the tachi toolkit against a CDSS threat model — no clinical controls are present in the target codebase.

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| Inter-Agent Communication Channel | Medium | 8 | 2 High + 6 Medium findings; highest-scoring internal component due to trust_exploitation and communication_vulnerability agentic patterns; Spoofing (S-5, composite 7.0) and Tampering (T-3, composite 7.0) are top findings |
| Supervisor Orchestrator | Medium | 11 | 11 Medium findings; highest finding-count component; agent_collusion patterns (AG-1, AG-2) flagged; autonomous delegation without oversight is primary concern |
| Clinical LLM | Medium | 9 | 9 Medium findings; prompt injection (LLM-1) and data poisoning (LLM-2) are primary AI-specific threats; reachability floor of 1.0 (internal Trusted zone) moderates composite scores |
| Risk Stratification Model | Medium | 9 | 9 Medium findings; adversarial fine-tuning data poisoning (LLM-5) and membership inference (LLM-6) are highest-concern AI threats |
| Diagnostic Agent | Medium | 8 | 8 Medium findings; tool abuse (AG-3, AG-4) and unauthorized FHIR write operations are primary concerns |
| Treatment Planner Agent | Medium | 8 | 8 Medium findings; autonomous literature incorporation without validation (AG-5) is primary agentic risk |
| Clinical MCP Tool Server | Medium | 7 | 7 Medium findings; tool chaining privilege escalation (AG-7) and FHIR tampering (T-7) are highest-severity findings in this component |
| Other (13 components) | Medium | 52 | 4 High + 46 Medium + 2 Low findings across 13 remaining components; includes external entities Physician (High, S-1 composite 8.4) and Patient (High, S-2 composite 7.4) |

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
- Style: Premium dark dashboard — Figma-quality, not spreadsheet-like
- 4-Zone Layout:
  1. TOP SECTION (~10%): Title "Threat Model: Healthcare CDSS (Reference Scenario)", date 2026-04-16, CONFIDENTIAL badge, subtitle "112 Findings — MAESTRO Canonical Worked Example — Not a Real Clinical System"
  2. MIDDLE ROW (~55%): Left panel (donut chart — residual risk distribution), Center panel (component × STRIDE+AI heat map), Right panel (top 5 residual risk finding cards with severity-colored left border)
  3. BOTTOM STRIP (~25%): Architecture threat overlay with trust zones, component risk weight annotations, agentic pattern callout (trust_exploitation on Inter-Agent Communication Channel)
  4. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard aesthetic. All text: white or light gray on dark background.

### Gemini Prompt

Construct the prompt using the scaffold from the JSON output (preamble + data content + postamble):

**PREAMBLE** (verbatim from JSON prompt_scaffold.preamble):
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

**DATA CONTENT** (agent-populated from JSON data):

TOP SECTION: Title "Healthcare CDSS — Residual Risk Dashboard" with date "2026-04-16" and "CONFIDENTIAL" badge. Subtitle: "Teaching Reference Scenario — Not a Real Clinical System — 112 Findings Across 8 Threat Categories".

LEFT PANEL: Donut chart titled "Residual Risk Distribution". Segments: 0 Critical (red), 6 High (orange), 104 Medium (amber), 2 Low (blue). Center text "112 findings". Below donut: legend with counts and percentages (0C / 6H / 104M / 2L). Below legend: "RISK POSTURE: Residual risk — 0 Critical and 6 High findings across 20 components." Below posture: "Risk Reduction: 0.0% — No controls detected in target codebase. Reference scenario only."

CENTER PANEL: Heat map grid titled "Coverage Heat Map — Residual Severity by Component". Rows (sorted by total descending): Supervisor Orchestrator (11), Clinical LLM (9), Risk Stratification Model (9), Diagnostic Agent (8), Inter-Agent Communication Channel (8), Treatment Planner Agent (8), Clinical MCP Tool Server (7), Other (52). Columns: S, T, R, I, D, E, AG, LLM. Cell values by highest residual severity — use exactly this grid (do not infer):
Supervisor Orchestrator: S=Medium, T=Medium, R=Medium, I=Medium, D=Medium, E=Medium, AG=Medium, LLM=—
Clinical LLM: S=Medium, T=Medium, R=Medium, I=Medium, D=Medium, E=Medium, AG=—, LLM=Medium
Risk Stratification Model: S=Medium, T=Medium, R=Medium, I=Medium, D=Medium, E=Medium, AG=—, LLM=Medium
Diagnostic Agent: S=Medium, T=Medium, R=Medium, I=Medium, D=Medium, E=Medium, AG=Medium, LLM=—
Inter-Agent Communication Channel: S=High, T=High, R=Medium, I=Medium, D=Medium, E=Medium, AG=Medium, LLM=—
Treatment Planner Agent: S=Medium, T=Medium, R=Medium, I=Medium, D=Medium, E=Medium, AG=Medium, LLM=—
Clinical MCP Tool Server: S=Medium, T=Medium, R=Medium, I=Medium, D=Medium, E=Medium, AG=Medium, LLM=—
Other: S=High, T=High, R=Medium, I=High, D=Medium, E=High, AG=Medium, LLM=—

RIGHT PANEL: Top 5 residual risk finding cards (vertical stack). Each card has severity-colored left border, finding ID in monospace, component in bold, one-line threat description:
Card 1 (orange border): "S-1 | Physician — Attacker forges or replays clinical query credentials (Residual: High, 8.4)"
Card 2 (orange border): "S-2 | Patient — Attacker submits fraudulent EHR update events (Residual: High, 7.4)"
Card 3 (orange border): "D-1 | Physician Clinical Portal — Attacker floods portal with clinical query requests (Residual: High, 7.1)"
Card 4 (orange border): "E-1 | Physician Clinical Portal — Attacker escalates from low-privilege session (Residual: High, 7.0)"
Card 5 (orange border): "S-5 | Inter-Agent Communication Channel — Attacker spoofs supervisor delegation messages (Residual: High, 7.0)"

BOTTOM STRIP: Simplified trust zone architecture. Zones: External (Physician, Patient) → User Interface (Physician Clinical Portal, Patient Summary Generator) → Agent Ecosystem (Inter-Agent Communication Channel) → Agent Framework (Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Clinical MCP Tool Server) → Foundation Models (Clinical LLM, Risk Stratification Model). Data flow arrows colored by highest residual severity on each path (orange for High paths through Inter-Agent Communication Channel; amber for Medium paths elsewhere). Annotation: "6 agentic patterns detected: trust_exploitation (5 findings), agent_collusion (4), communication_vulnerability (3), temporal_attack (2), resource_competition (2), emergent_behavior (1)."

**POSTAMBLE** (verbatim from JSON prompt_scaffold.postamble):
FOOTER: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
