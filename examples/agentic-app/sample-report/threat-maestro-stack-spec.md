---
schema_version: "1.4"
template: "maestro-stack"
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

### MAESTRO Layer Distribution

> Note: `template_data.maestro_layer_distribution` returned empty from the extraction script — MAESTRO layer annotation for per-layer aggregate counts was not populated in the threats.md for this cycle. The component-level MAESTRO layer annotations (visible in the threats.md scope section) are present but the aggregate rollup was not produced. The per-layer summaries below are derived from the MAESTRO layer annotations in the threats.md DFD component table.

**Most Exposed Layer**: L1 — Foundation Model (LLM Agent Orchestrator maps to L1)

| Layer | Name | Finding Count | Highest Residual Severity | Top Findings |
|-------|------|---------------|---------------------------|--------------|
| L1 | Foundation Model | 23 | High | AG-1 (LLM Agent Orchestrator — prompt injection); E-2 (privilege escalation via self-authorization); D-10 [NEW] (inference-request flooding) |
| L2 | Data Operations | 2+ | High | Knowledge Base tampering (T-6 High); information disclosure (I-6) |
| L3 | Agent Framework | 8 | High | MCP Tool Server — S-6, T-5, E-3 High; tool-call spoofing and parameter tampering |
| L4 | Agent Communication | 8 | Medium | Inter-Agent Communication Channel — T-4, S-5, I-4 |
| L5 | Evaluation and Observability | 3+ | Medium | Audit Logger — T-7, I-7, R-7 |
| L6 | Security and Compliance | 5 | High | Guardrails Service — E-1 High; T-1, I-1, R-2 Medium |
| L7 | Agent Ecosystem | 22 | High | Clinical Advisory Sub-Agent, Specialist Agent — S-9 High, T-9, R-9; User (S-1 High) |

### Component-to-MAESTRO Layer Mapping

| Component | MAESTRO Layer | Notes |
|-----------|---------------|-------|
| LLM Agent Orchestrator | L1 — Foundation Model | Primary AI inference surface — 23 findings, 6 High residual |
| Knowledge Base | L2 — Data Operations | RAG retrieval path — tampering and information disclosure risks |
| MCP Tool Server | L3 — Agent Framework | Tool execution surface — 8 findings, 2 High |
| Inter-Agent Communication Channel | L4 — Agent Communication | Inter-agent delegation — 8 Medium residual |
| Audit Logger | L5 — Evaluation and Observability | Tamper-evident logging — medium residual |
| Guardrails Service | L6 — Security and Compliance | Filtering layer — 5 findings, 1 High |
| Clinical Advisory Sub-Agent | L7 — Agent Ecosystem | Downstream clinical agent — 12 findings, Medium residual |
| Specialist Agent | L7 — Agent Ecosystem | Delegation target — 10 findings, Medium residual |
| User | L7 — Agent Ecosystem | External actor — S-1 High residual |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: most-exposed layer band accent |
| High | #EA580C | Orange-600: High-residual layer band, top finding badges |
| Medium | #CA8A04 | Yellow-600: Medium-residual layer bands |
| Low | #2563EB | Blue-600: Low-residual findings |
| Note | #6B7280 | Gray-500: empty/muted layers |
| Clean cell | #F3F4F6 | Gray-100: empty layer band background |

### Layout Structure

```
- Background: dark navy
- Aspect Ratio: 16:9 landscape
- Style: Premium dark dashboard — 7-layer MAESTRO stack visualization
- 3-Zone Layout:
  1. HEADER (top, ~10%): Title "CSA MAESTRO Layer Analysis: Agentic AI Application",
     date "2026-04-27", CONFIDENTIAL badge, subtitle "85 Residual Findings — F-5 Wave 2"
  2. MAIN BODY (center, ~80%): 2-column layout:
     Left column (70%): 7 horizontal MAESTRO layer bands (L7 at top → L1 at bottom,
       or L1 at top as most-exposed — arranged with most findings first):
       - L1 Foundation Model: bright orange accent, wide border, "23 findings — 6 High" — MOST EXPOSED
       - L7 Agent Ecosystem: medium amber band, "22 findings — 2 High"
       - L3 Agent Framework: amber band, "8 findings — 2 High"
       - L4 Agent Communication: amber band, "8 findings — Medium"
       - L2 Data Operations: amber band, "2+ findings — 1 High"
       - L6 Security and Compliance: amber band, "5 findings — 1 High"
       - L5 Eval and Observability: muted gray band, "3+ findings — Medium"
     Right column (30%): Sidebar with top findings and severity distribution:
       - Donut or bar chart: 0C / 10H / 70M / 5L
       - Top 3 findings: S-1 (8.2), AG-1 (7.8), D-10 NEW (7.2)
       - "Most Exposed: L1 — Foundation Model"
       - "F-5 New: D-10, D-11, LLM-15, LLM-16"
  3. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis"
```

### Typography

- Title: Bold, 28-32pt equivalent
- Layer Band Labels: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy — premium dark dashboard aesthetic. Layer bands: horizontal bars stacked vertically with rounded corners. Most-exposed layer (L1): brighter background, wider left border accent. Empty/low-severity layers: muted darker background. All text: white or light gray.
