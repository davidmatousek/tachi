---
schema_version: "1.0"
template: "maestro-heatmap"
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

## 3. MAESTRO Layer Breakdown

_No MAESTRO layer data in source file._

## 4. MAESTRO Heatmap Grid

_No heatmap grid data._

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
- MAESTRO heatmap grid (70% height, centered): rows = layers L1-L7, columns = severity bands (Critical / High / Medium / Low)
- Cell color intensity = finding count; cell number = count
- Row totals on the right, column totals on the bottom
- Bottom panel (18% height): risk-by-layer narrative

**Typography**: Same as baseball-card. Grid labels in 12pt; cell numbers in 14pt bold.

**Visual Style**: Matrix heatmap aesthetic. Use sequential color ramp from white (0 findings) through severity colors. Layer rows use canonical CSA MAESTRO names.

**Prompt Hint (Gemini)**: Generate a print-quality infographic using the layout above. Emphasize canonical MAESTRO layer naming — use ONLY the canonical CSA MAESTRO layer names: L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem.
