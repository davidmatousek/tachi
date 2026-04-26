---
schema_version: "1.0"
template: "maestro-stack"
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
| MAESTRO Data | has_maestro_data = true; per-layer summaries and layer distribution not populated (empty arrays from extraction) |

**MAESTRO Data Status**: The extraction script reports `has_maestro_data: true` but `maestro_layer_distribution: []` and `per_layer_summaries: []`. This indicates that MAESTRO layer annotations are present in the source data (schema 1.4) but per-finding layer assignments were not parsed into the summary arrays by the script for this run. The Component-Layer data (used by maestro-heatmap) is populated; the per-layer aggregate summaries used by this template are not. The spec renders with available data and notes the partial state.

---

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 8 | 10% | #EA580C |
| Medium | 68 | 84% | #EAB308 |
| Low | 5 | 6% | #4169E1 |
| **Total** | **81** | **100%** | — |

**Chart Format**: Donut chart (sidebar, Residual Risk Distribution).

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

### Cell-Level Grid

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

### MAESTRO Layer Stack

Per-layer summary data is not fully populated for this run (`per_layer_summaries: []`). The layer table below uses partial data inferred from the available component-level heat map data and cross-referenced against the maestro-heatmap extraction which does contain per-component layer assignments.

| Layer | Name | Finding Count (approx) | Highest Residual Severity | Notes |
|-------|------|----------------------|--------------------------|-------|
| L1 | Foundation Model | ~19 | High | LLM Agent Orchestrator — highest finding concentration (19 findings) |
| L2 | Data Operations | ~12 | High | Knowledge Base (High per maestro-heatmap), data retrieval path |
| L3 | Agent Framework | ~8 | High | MCP Tool Server (2 High + 5 Medium + 1 Low) |
| L4 | Agent Application | ~9 | Medium | Long-Running Learning Loop (9 Medium) |
| L5 | Data Plane | ~12 | Medium | Clinical Advisory Sub-Agent (11 Medium + 1 Low) |
| L6 | Security Controls | ~5 | High | Guardrails Service (1 High + 3 Medium + 1 Low) |
| L7 | Agent Interface | ~16 | High | User (S-1 High), Clinical Advisory Sub-Agent interface |

**Most Exposed Layer**: L1 (Foundation Model) — 19 residual findings, 4 High. The LLM Agent Orchestrator at L1 carries the broadest attack surface across STRIDE+AG categories.

**Delta Emphasis — AG-8 [NEW]**: AG-8 targets the Inter-Agent Communication Channel, which maps primarily to L3 (Agent Framework) and L4 (Agent Application). Its raw Critical severity (reduced to High residual) makes L3 the second-most-exposed layer this wave. The [NEW] badge should appear on the L3 row in the stack visualization.

### Layer Component Mapping

| Layer | Primary Components | Delta |
|-------|-------------------|-------|
| L1 — Foundation Model | LLM Agent Orchestrator | — |
| L2 — Data Operations | Knowledge Base | — |
| L3 — Agent Framework | MCP Tool Server, Inter-Agent Communication Channel | AG-8 [NEW] |
| L4 — Agent Application | Long-Running Learning Loop, Specialist Agent | — |
| L5 — Data Plane | Clinical Advisory Sub-Agent, Audit Logger | — |
| L6 — Security Controls | Guardrails Service | — |
| L7 — Agent Interface | User, External API | — |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: layer band highlight (none in residual) |
| High | #EA580C | Orange-600: layer band accent, finding badge fills |
| Medium | #CA8A04 | Yellow-600: layer band muted accent |
| Low | #2563EB | Blue-600: layer band low accent |
| Note | #6B7280 | Gray-500: empty layer bands |
| Card bg | #F9FAFB | Gray-50: layer band background (light layers) |

### Layout Structure

MAESTRO Stack layout (16:9 landscape, dark navy background):

- Top header: project name, date, CONFIDENTIAL badge, tier source
- Main body: Left zone = L7 (top) through L1 (bottom) horizontal layer bands stacked vertically; Right sidebar = residual risk donut + top findings
- Each layer band: left-aligned layer ID + name label, center = top 2 finding IDs as orange pills, right = finding count
- Most-exposed layer band (L1 — Foundation Model): brighter background, wider left border accent in orange
- Empty or low-severity layers: muted darker background, grayed text
- AG-8 [NEW] badge on L3 (Agent Framework): orange outline, "NEW" text in white
- Footer centered

### Typography

- Title: Bold, 28-32pt equivalent
- Layer Labels: Semi-bold, 18-22pt equivalent
- Finding ID Pills: Monospace, 12-14pt
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard aesthetic. Layer bands use slightly lighter card backgrounds for contrast.
