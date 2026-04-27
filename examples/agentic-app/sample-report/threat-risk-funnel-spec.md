---
schema_version: "1.4"
template: "risk-funnel"
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

> **F-5 callout**: D-10 is a new finding introduced in Feature 229 Wave 2, covering OWASP LLM10:2025 Unbounded Consumption — inference-request flooding vector.

---

## 5. Architecture Threat Overlay

### Funnel Tiers

**Mode**: 4-Tier (compensating-controls data source)

> Note: Tier 2 (Inherent Risk Scored) count is 0 — the quantitative risk-scores.md pipeline stage was not run for this report cycle. The risk-scores.md enrichment is optional and was not available in the target directory. Tier 2 is rendered with its source count from threats.md Section 6 for continuity.

| Tier | Label | Width (%) | Severity Counts | Render State | Source |
|------|-------|-----------|-----------------|--------------|--------|
| 1 | Threats Identified | 100% | 88 threats (per Section 6 baseline) | Solid | threats.md Section 6 |
| 2 | Inherent Risk Scored | ghost | N/A — risk-scores.md not available | Ghost | risk-scores.md (missing) |
| 3 | Controls Applied | 97% | 85 findings with compensating controls applied; 0% coverage reduction (controls partially effective) | Solid | compensating-controls.md |
| 4 | Residual Risk | 97% | 0 Critical / 10 High / 70 Medium / 5 Low | Solid | compensating-controls.md residual |

**Tier Width Notes**: Tier 2 is ghost because risk-scores.md was not produced. Tiers 3 and 4 are at 97% (88 → 85 findings; 3 resolved). Zero risk-reduction percentage reflects that no composite-score delta is available without the inherent risk baseline.

> Enhancement tip: Run `/tachi.risk-score` before `/tachi.compensating-controls` to populate Tier 2 with quantitative inherent scores and unlock the full 4-tier reduction visualization.

### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Findings | 85 residual |
| Threats Identified | 88 (from threats.md baseline) |
| Risk Reduction | N/A — inherent baseline not scored |
| Control Coverage | Compensating controls applied to all 85 findings |
| F-5 New Findings | 4 (D-10, D-11, LLM-15, LLM-16) — LLM10 Unbounded Consumption |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: tier 1 accent if critical findings present |
| High | #EA580C | Orange-600: tier segment, sidebar metric badge |
| Medium | #CA8A04 | Yellow-600: dominant tier color (82% of residual) |
| Low | #2563EB | Blue-600: tier segment |
| Note | #6B7280 | Gray-500: ghost tier styling |
| Ghost tier | semi-transparent | Dashed border, translucent gray fill |

### Layout Structure

```
- Background: dark navy
- Aspect Ratio: 16:9 landscape
- Style: Premium 3D glass-like risk reduction funnel — CISO board presentation quality
- 4-Tier Funnel Layout:
  1. HEADER (top): Title "Risk Reduction Funnel: Agentic AI Application" + CONFIDENTIAL badge + date "2026-04-27"
  2. FUNNEL (center-left, 70% width): 4 progressive trapezoidal tiers top-to-bottom:
     - Tier 1 (100% wide, solid amber): "Threats Identified" — 88 threats
     - Tier 2 (ghost/dashed): "Inherent Risk Scored" — N/A (run /tachi.risk-score)
     - Tier 3 (97% wide, solid amber): "Controls Applied" — 85 findings, controls assessed
     - Tier 4 (97% wide, solid amber): "Residual Risk" — 0C / 10H / 70M / 5L
  3. SIDEBAR (right, 30% width): Key metrics panel
     - Total Findings: 85 residual
     - Threats Identified: 88
     - Risk Reduction: N/A (inherent baseline needed)
     - NEW in F-5: D-10, D-11, LLM-15, LLM-16
  4. FOOTER: "Generated by Tachi Threat Modeling Framework — Risk Reduction Funnel"
```

### Typography

- Title: Bold, 28-32pt equivalent
- Tier Labels: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy — premium dark executive aesthetic. Funnel tiers: translucent 3D trapezoids with glass-like material, soft ambient lighting. All text: white or light gray.
