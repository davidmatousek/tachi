---
schema_version: "1.0"
template: "maestro-stack"
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
- MAESTRO seven-layer stack diagram (70% height, centered): horizontal bars representing L1-L7, stacked vertically with L1 at bottom and L7 at top
- Per-layer finding count badge (colored by max severity in the layer)
- Layer descriptions on the right side
- Bottom panel (18% height): legend + unclassified bucket if present

**Typography**: Same as baseball-card. Layer labels in 16pt bold; finding counts in 14pt; layer descriptions in 10pt.

**Visual Style**: Stack diagram with canonical CSA MAESTRO layer naming (L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem). Each layer bar colored by highest-severity finding in that layer.

**Prompt Hint (Gemini)**: Generate a print-quality infographic using the layout above. Emphasize canonical MAESTRO layer naming — use ONLY the canonical CSA MAESTRO layer names: L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem.
