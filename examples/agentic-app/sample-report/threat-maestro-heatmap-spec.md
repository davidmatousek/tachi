---
schema_version: "1.0"
template: "maestro-heatmap"
date: "2026-04-26"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
has_baseline: true
delta_note: "NEW finding AG-8 (Inter-Agent Communication Channel, OWASP ASI07:2026, raw Critical — residual High after controls)"
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-04-26 |
| Analysis Agents | 8 |
| Total Findings | 81 |
| Risk Posture | Residual risk — 0 Critical and 8 High findings across 11 components |
| Baseline | 2026-04-23 (F2-wave4) |
| Delta | NEW: AG-8 (Inter-Agent Communication Channel) — OWASP ASI07:2026, raw Critical, residual High after compensating controls |
| MAESTRO Data | has_maestro_data = true; component-layer intersection grid populated for 7 components |

---

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 8 | 10% | #EA580C |
| Medium | 68 | 84% | #EAB308 |
| Low | 5 | 6% | #4169E1 |
| **Total** | **81** | **100%** | — |

**Chart Format**: Legend panel (right side) showing severity color swatches with counts.

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 4 | 15 | 0 | 19 |
| Clinical Advisory Sub-Agent | 0 | 0 | 11 | 1 | 12 |
| Specialist Agent | 0 | 0 | 9 | 1 | 10 |
| Long-Running Learning Loop | 0 | 0 | 9 | 0 | 9 |
| Inter-Agent Communication Channel | 0 | 0 | 8 | 0 | 8 |
| MCP Tool Server | 0 | 2 | 5 | 1 | 8 |
| Guardrails Service | 0 | 1 | 3 | 1 | 5 |
| Other | 0 | 1 | 8 | 1 | 10 |

### Cell-Level Grid (STRIDE+AG)

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|----|-----|
| LLM Agent Orchestrator | High | Medium | Medium | High | Medium | High | High | Medium |
| Clinical Advisory Sub-Agent | --- | Medium | Medium | Medium | Medium | --- | --- | Medium |
| Specialist Agent | --- | Medium | Medium | Medium | Medium | --- | --- | Medium |
| Long-Running Learning Loop | --- | Medium | Medium | Medium | Medium | --- | --- | Medium |
| Inter-Agent Communication Channel | --- | Medium | --- | Medium | Medium | --- | High | --- |
| MCP Tool Server | --- | High | Medium | Medium | --- | Medium | High | --- |
| Guardrails Service | --- | --- | --- | Medium | --- | High | --- | Medium |
| Other | --- | Medium | Medium | Medium | --- | High | --- | --- |

---

## 4. Top Critical Findings

No Critical residual findings identified. Top High findings shown (residual risk, post-control):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials | High (score 8.2) |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions | High (score 7.8) |
| 3 | E-2 | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection | High (score 7.8) |
| 4 | E-1 | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller | High (score 7.7) |
| 5 | I-2 | LLM Agent Orchestrator | The Orchestrator's context window contains sensitive data exposed via inference side-channels | High (score 7.2) |

---

## 5. Architecture Threat Overlay

### Component-Layer Intersection Grid (MAESTRO Heatmap)

Grid cells show the **highest residual severity** for each component-layer intersection. "—" indicates no findings mapped to that intersection. Residual severity is shown (post-control).

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| LLM Agent Orchestrator | High | — | — | — | — | — | — |
| Clinical Advisory Sub-Agent | — | — | — | — | — | — | High |
| MCP Tool Server | — | — | High | — | — | — | — |
| Guardrails Service | — | — | — | — | — | High | — |
| Audit Logger | — | — | — | — | High | — | — |
| Knowledge Base | — | High | — | — | — | — | — |
| User | — | — | — | — | — | — | High |

**Delta note**: The extraction script uses "Critical" labels in the heatmap grid for the raw per-component-layer severity (pre-control). In this residual view, those cells reflect the residual severity after controls are applied. The maestro-heatmap JSON showed "Critical" for L1-LLM Agent Orchestrator, L7-Clinical Advisory Sub-Agent, L3-MCP Tool Server, L6-Guardrails Service, L5-Audit Logger, and L7-User — these are raw severity assignments used for MAESTRO layer mapping. Post-control residual for all is High (matching the 8 High residual findings in Section 2). The grid above displays residual severity.

**AG-8 [NEW] in heatmap**: AG-8 maps to the Inter-Agent Communication Channel, which sits at L3 (Agent Framework) and L4 (Agent Application). However, AG-8's component (Inter-Agent Communication Channel) does not appear in the 7-component heatmap grid returned by the extraction script. The grid above shows the components with explicit MAESTRO layer assignments from the source data. Inter-Agent Communication Channel should be added to the grid at L3 with severity High (AG-8 residual) when the MAESTRO annotations are fully populated.

### MAESTRO Layer Distribution

Per-layer aggregate data not available for this run (`maestro_layer_distribution: []`). Refer to the component-layer grid above for intersection data.

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: grid cells (raw severity; none in residual grid) |
| High | #EA580C | Orange-600: grid cells with High residual findings |
| Medium | #CA8A04 | Yellow-600: grid cells with Medium residual findings |
| Low | #2563EB | Blue-600: grid cells with Low residual findings |
| Empty | #374151 | Dark gray: grid cells with no findings (rounded rectangles) |
| Note | #6B7280 | Gray-500: legend and decorative elements |

### Layout Structure

MAESTRO Heatmap layout (16:9 landscape, dark navy background):

- Title bar: project name, date, CONFIDENTIAL badge, "CSA MAESTRO Layer Analysis" subtitle
- Main body: Component-Layer intersection grid (components as rows, L1-L7 as columns)
- Grid cells: rounded rectangles with severity-colored fill or dark gray empty state
- Column headers: L1 through L7 with layer names as sub-labels
- Row labels: component names (left-aligned, up to 25 chars; truncate with "..." if longer)
- Right panel: legend with severity color swatches + counts; top finding cards
- AG-8 note: small annotation below the grid — "AG-8 [NEW]: Inter-Agent Communication Channel (L3) not shown — MAESTRO annotation pending"
- Footer centered

### Typography

- Title: Bold, 28-32pt equivalent
- Column/Row Headers: Semi-bold, 14-16pt equivalent
- Grid Cell Values: Bold, 12-14pt equivalent
- Legend: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard aesthetic. Grid cells use rounded rectangles with colored fills on dark background.

### Delta Emphasis Directive

A small annotation below the grid should note: "AG-8 [NEW] — Inter-Agent Communication Channel maps to L3 (Agent Framework) with residual High severity (OWASP ASI07:2026). Full layer assignment pending MAESTRO annotation in next run."
