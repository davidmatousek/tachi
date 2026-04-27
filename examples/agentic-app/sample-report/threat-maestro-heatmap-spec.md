---
schema_version: "1.4"
template: "maestro-heatmap"
date: "2026-04-27"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 85
image_generated: true
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-04-27 |
| Analysis Agents | 8 |
| Total Findings | 85 |
| Risk Posture | Residual risk — 0 Critical and 10 High findings across 11 components |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 10 | 12% | #EA580C |
| Medium | 70 | 82% | #CA8A04 |
| Low | 5 | 6% | #2563EB |
| **Total** | **85** | **100%** | — |

**F-5 New Findings This Cycle**: D-10 (LLM Inference-Request Flooding), D-11 (Context-Window Latency Amplification), LLM-15 (Cost Amplification), LLM-16 (Denial-of-Wallet) — Feature 229 Wave 2.

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 6 | 17 | 0 | 23 |
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
| LLM Agent Orchestrator | High | High | High | High | High | High | High | High |
| Clinical Advisory Sub-Agent | Medium | Medium | Medium | Medium | Medium | Medium | --- | Medium |
| Specialist Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | Medium |
| Long-Running Learning Loop | Medium | Medium | Medium | Medium | Medium | Medium | Medium | Medium |
| Inter-Agent Communication Channel | Medium | Medium | Low | Medium | Medium | Medium | Medium | --- |
| MCP Tool Server | High | High | Medium | Medium | High | High | High | --- |
| Guardrails Service | High | Medium | Medium | Medium | High | High | --- | --- |
| Other | High | Medium | Low | --- | --- | --- | --- | --- |

---

## 4. Top Critical Findings

**Risk Level Column**: Residual Risk

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials | High (8.2) |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions | High (7.8) |
| 3 | E-2 | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection | High (7.8) |
| 4 | E-1 | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller | High (7.7) |
| 5 | D-10 [NEW] | LLM Agent Orchestrator | LLM Inference-Request Flooding and Token Exhaustion without per-tenant QPS rate limiting | High (7.2) |

> **F-5 callout**: D-10 is a new finding introduced in Feature 229 Wave 2, covering OWASP LLM10:2025 Unbounded Consumption.

---

## 5. Architecture Threat Overlay

### Component-Layer Intersection Grid

The grid cells use the highest-severity finding at each component × MAESTRO-layer intersection. Source: `template_data.maestro_heatmap[]` from the extraction script.

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| LLM Agent Orchestrator | Critical* | — | — | — | — | — | — |
| Clinical Advisory Sub-Agent | — | — | — | — | — | — | Critical* |
| MCP Tool Server | — | — | Critical* | — | — | — | — |
| Guardrails Service | — | — | — | — | — | Critical* | — |
| Audit Logger | — | — | — | — | Critical* | — | — |
| Knowledge Base | — | High | — | — | — | — | — |
| User | — | — | — | — | — | — | Critical* |

> Note: The extraction script returned "Critical" for these intersection cells based on the MAESTRO layer classification assigned in threats.md. These cells reflect the per-finding layer annotation (e.g., LLM Agent Orchestrator is classified as L1 — Foundation Model; some findings are tagged Critical at the inherent level before controls). The residual-level heat map (Section 3) uses post-controls severity which shows 0 Critical / 10 High residual. The MAESTRO heatmap grid uses the pre-control threat classification (inherent severity at each layer intersection) per the extraction script logic.

### Layer Legend (from maestro_layer_distribution — aggregate rollup)

> Note: `template_data.maestro_layer_distribution` is empty for this report cycle. Layer names use canonical CSA MAESTRO taxonomy.

| Layer | Name | Components in This Report |
|-------|------|--------------------------|
| L1 | Foundation Model | LLM Agent Orchestrator |
| L2 | Data Operations | Knowledge Base |
| L3 | Agent Framework | MCP Tool Server |
| L4 | Agent Communication | Inter-Agent Communication Channel |
| L5 | Evaluation and Observability | Audit Logger |
| L6 | Security and Compliance | Guardrails Service |
| L7 | Agent Ecosystem | Clinical Advisory Sub-Agent, Specialist Agent, User |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: heatmap grid cells with Critical intersections |
| High | #EA580C | Orange-600: heatmap grid cells with High intersections |
| Medium | #CA8A04 | Yellow-600: heatmap grid cells with Medium intersections |
| Low | #2563EB | Blue-600: heatmap grid cells with Low intersections |
| Note | #6B7280 | Gray-500: empty grid cells |
| Clean cell | #F3F4F6 | Gray-100: "—" (no finding) grid cells |

### Layout Structure

```
- Background: dark navy
- Aspect Ratio: 16:9 landscape
- Style: Premium MAESTRO component-layer heatmap dashboard
- Main Layout:
  1. HEADER (top, ~10%): Title "MAESTRO Component-Layer Heatmap: Agentic AI Application",
     date "2026-04-27", CONFIDENTIAL badge, subtitle "85 Residual Findings — F-5 Wave 2"
  2. GRID (center, ~75%): Component × Layer intersection matrix:
     Rows: components (7 shown from maestro_heatmap)
     Columns: L1, L2, L3, L4, L5, L6, L7
     Each cell: rounded rectangle, colored by severity (Critical=red, High=orange, Medium=amber, Low=blue, empty=dark gray)
     Cell label: severity word (Critical/High/Medium/Low) or "—" if empty
     Column headers: L1 through L7 with full layer name below
     Row labels: component names left-aligned
  3. LEGEND PANEL (right sidebar, ~15%):
     - Severity color swatches: Critical (red), High (orange), Medium (amber), Low (blue), None (gray)
     - Total: 85 residual findings
     - "F-5 New: D-10, D-11, LLM-15, LLM-16"
  4. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis"
```

### Typography

- Title: Bold, 28-32pt equivalent
- Grid Headers: Semi-bold, 14-16pt equivalent
- Cell Labels: Regular, 12-14pt equivalent
- Legend: Regular, 12-14pt equivalent

### Background

Dark navy — premium dark dashboard aesthetic. Grid cells: rounded rectangles with generous padding. Empty cells: subtle dark gray. All text: white or light gray on dark background.
