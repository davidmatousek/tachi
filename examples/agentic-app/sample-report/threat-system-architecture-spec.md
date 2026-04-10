---
schema_version: "1.0"
template: "system-architecture"
date: "2026-04-10"
source_file: "compensating-controls.md"
finding_count: 22
image_generated: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-04-10 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 22 |
| Risk Posture | Residual risk — 0 Critical and 10 High findings across 7 components |

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0.0% | #DC2626 |
| High | 10 | 45.0% | #EA580C |
| Medium | 12 | 55.0% | #CA8A04 |
| Low | 0 | 0.0% | #2563EB |
| **Total** | **22** | **100%** | -- |

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 4 | 6 | 0 | 10 |
| MCP Tool Server | 0 | 2 | 2 | 0 | 4 |
| Guardrails Service | 0 | 2 | 0 | 0 | 2 |
| Knowledge Base | 0 | 0 | 2 | 0 | 2 |
| User | 0 | 1 | 1 | 0 | 2 |
| Audit Logger | 0 | 0 | 1 | 0 | 1 |
| External API | 0 | 1 | 0 | 0 | 1 |

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | LLM-1 | LLM Agent Orchestrator | Indirect prompt injection via documents retrieved from the … | High |
| 2 | AG-4 | MCP Tool Server | Compromised or manipulated agent triggers excessive tool in… | High |
| 3 | E-2 | Guardrails Service | Attacker bypasses guardrails validation through prompt obfu… | High |
| 4 | E-1 | LLM Agent Orchestrator | Orchestrator escalates its own tool permissions beyond the … | High |
| 5 | LLM-3 | LLM Agent Orchestrator | Attacker crafts prompts that cause the LLM to generate tool… | High |

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | High | 10 | Central coordination hub dispatching LLM inference, tool calls, and knowledge retrieval. Concentrates the majority of findings as the primary target for spoofing, tampering, information disclosure, privilege escalation, and AI-specific (LLM + agentic) threats. |
| MCP Tool Server | Medium-High | 4 | Executes tool calls on behalf of the orchestrator. Exposed to prompt-driven parameter manipulation, unauthorized tool invocation, resource exhaustion, and scope-crossing agentic actions. |
| Guardrails Service | Medium-High | 2 | Entry-point input filter screening user prompts. High-severity denial-of-service and privilege-escalation findings reflect its position as the first attacker-facing component in the application zone. |
| Knowledge Base | Medium | 2 | Vector store providing RAG context. Data integrity (embedding poisoning) and confidentiality (embedding reversal) findings reflect its role as the indirect prompt injection attack surface. |
| User | Medium-High | 2 | External entity submitting prompts. Spoofing (token replay) and repudiation (insufficient session attribution) findings reflect identity-boundary risks. |
| Audit Logger | Medium | 1 | Centralized observability and forensics store (MAESTRO L5). Tampering findings reflect accountability risks if log integrity is not cryptographically chained. |
| External API | Medium-High | 1 | Third-party service reached through the tool server. Spoofing findings reflect response-integrity risks at the trust-zone boundary. |

## 6. Visual Design Directives

**Format**: Portrait orientation (2:3 aspect ratio), print-ready at 300 DPI, 2480 x 3508 px minimum.

**Color System**:
- Critical: `#DC2626` (deep red) — urgent action required
- High: `#EA580C` (orange-red) — priority remediation
- Medium: `#CA8A04` (gold) — scheduled remediation
- Low: `#2563EB` (blue) — backlog/monitor
- Background: light gray `#F5F5F5` with white panels `#FFFFFF`
- Headers: dark navy `#1E293B`
- Accent lines: medium gray `#64748B`

**Layout**:
- Top banner (12% height): project name, scan date, total findings
- System architecture diagram (60% height, center): components as nodes, data flows as edges, trust boundaries as zone backgrounds
- Risk annotations per component overlay (finding counts in colored bubbles)
- Bottom panel (28% height): top findings legend + risk distribution bar chart

**Typography**: Same as baseball-card. Component labels in 12pt bold; data flow labels in 9pt italic.

**Visual Style**: Technical diagram aesthetic. Use flowchart conventions (boxes for processes, cylinders for data stores, parallelograms for external entities). Trust zones shown as rounded-rectangle backgrounds with subtle fill colors.

**Prompt Hint (Gemini)**: Generate a print-quality infographic using the layout above. Emphasize canonical MAESTRO layer naming — use ONLY the canonical CSA MAESTRO layer names: L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem.
