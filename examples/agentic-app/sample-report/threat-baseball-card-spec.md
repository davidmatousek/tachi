---
schema_version: "1.4"
template: "baseball-card"
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

**Chart Format**: Donut chart (proportional segments). Center text: "85 findings". Residual risk posture note below donut: "0 Critical — 10 High — controls applied".

**F-5 New Findings This Cycle**: D-10 (LLM Inference-Request Flooding), D-11 (Context-Window Latency Amplification), LLM-15 (Cost Amplification), LLM-16 (Denial-of-Wallet) — all introduced in Feature 229 Wave 2.

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

> Note: Cell-Level Grid reflects residual severity bands post-compensating controls. LLM Agent Orchestrator retains High residual findings across all 8 STRIDE+AI categories. MCP Tool Server and Guardrails Service are secondary risk concentrations.

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

> **F-5 callout**: D-10 is a new finding introduced in Feature 229 Wave 2, covering OWASP LLM10:2025 Unbounded Consumption — inference-request flooding vector. D-11 (context-window latency amplification) and LLM-15/LLM-16 (economic denial vectors) complete the LLM10 coverage set.

---

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | Medium (2.3) | 23 | 6 High + 17 Medium residual; highest attack surface — prompt injection, privilege escalation, DoS, and agent autonomy threats concentrated here; new F-5 findings D-10 + D-11 add unbounded consumption vectors |
| MCP Tool Server | Medium (2.1) | 8 | 2 High + 5 Medium + 1 Low residual; tool-call spoofing, parameter tampering, and inter-agent trust propagation risks |
| Guardrails Service | Medium (2.0) | 5 | 1 High + 3 Medium + 1 Low residual; bypass via prompt injection remains primary unmitigated vector |
| Inter-Agent Communication Channel | Medium (2.0) | 8 | 8 Medium residual; message integrity and replay-prevention gaps across agent delegation flows |
| Long-Running Learning Loop | Medium (2.0) | 9 | 9 Medium residual; training signal poisoning and temporal attack patterns require data provenance controls |
| Other | Medium (2.0) | 10 | 1 High + 8 Medium + 1 Low; includes User (S-1 High) and Audit Logger components |
| Clinical Advisory Sub-Agent | Low (1.9) | 12 | 11 Medium + 1 Low residual; clinical context injection and non-repudiation gaps managed by partial controls |
| Specialist Agent | Low (1.9) | 10 | 9 Medium + 1 Low residual; delegation integrity and tool-call authorization risks at managed level |

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

```
- Background: dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape
- Style: Premium dark dashboard — polished Figma-quality security report artifact
- 4-Zone Layout:
  1. TOP SECTION (~10%): Title "Threat Model: Agentic AI Application", date "2026-04-27", CONFIDENTIAL badge,
     subtitle "85 Residual Findings — F-5 Wave 2: LLM10 Unbounded Consumption Coverage Added"
  2. MIDDLE ROW (~50%): Left panel (donut chart 0C/10H/70M/5L + residual risk posture),
     Center panel (component × STRIDE+AI heat map — residual severity, Cell-Level Grid),
     Right panel (5 top finding cards — orange left border for High residual)
  3. BOTTOM STRIP (~30%): Architecture threat overlay table — 8 components with risk weight, count, annotation
  4. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"
```

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard aesthetic. All text: white or light gray on dark background. Cards and panels: rounded corners, subtle drop shadows, generous whitespace.
