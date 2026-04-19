---
schema_version: "1.0"
template: "system-architecture"
date: "2026-04-19"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 69
image_generated: true
project_name: "Agentic AI Application"
fallback_note: "Extraction ran against threats.md (Tier 3 fallback); score numbers inlined from compensating-controls.md + risk-scores.md Executive Summary due to parser heading-format mismatch against current compensating-controls.md schema"
---

# Threat Infographic Specification — System Architecture

## 1. Metadata

- **Project**: Agentic AI Application
- **Scan Date**: 2026-04-19
- **Total Findings**: 69
- **Components**: 10
- **Data Flows**: 23
- **Trust Zones**: 3

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 38 | 55% | #DC2626 |
| High | 23 | 33% | #EA580C |
| Medium | 6 | 9% | #CA8A04 |
| Low | 2 | 3% | #2563EB |

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|---------:|-----:|-------:|----:|------:|
| LLM Agent Orchestrator | 15 | 3 | 1 | 0 | 19 |
| Specialist Agent | 4 | 6 | 0 | 0 | 10 |
| Long-Running Learning Loop | 5 | 3 | 1 | 0 | 9 |
| MCP Tool Server | 5 | 3 | 0 | 0 | 8 |
| Inter-Agent Communication Channel | 5 | 1 | 0 | 1 | 7 |
| Guardrails Service | 2 | 2 | 2 | 0 | 6 |
| Audit Logger | 1 | 2 | 0 | 0 | 3 |
| Other | 1 | 3 | 2 | 1 | 7 |

## 4. Top Findings with Spatial Placement

- **LLM Agent Orchestrator (L1)** — 15C+3H incl. F-201 OI-1 (XSS), OI-2 (Server-Exec), OI-3 (SSRF)
- **MCP Tool Server (L3)** — 5C+3H — tool-call injection sink for OI-2/OI-3
- **Inter-Agent Channel** — 5C+1H — agent-in-the-middle, message tampering
- **Long-Running Learning Loop** — 5C+3H — temporal data poisoning
- **Specialist Agent** — 4C+6H — delegation-message injection

## 5. Template-Specific Format — System Architecture

Trust zone subgraphs, colored data-flow arrows, component attack-surface badges.

**Trust Zones**:
- **Application Zone** (trusted): Audit Logger, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent
- **External Services** (semi-trusted): External API
- **User Zone** (untrusted): User

**Data Flow Coloring**: flow severity = max severity of findings on source or destination
- `Response (HTTPS)` (Orchestrator→User): **red** — carries OI-1 XSS
- `Tool Call Request (JSON-RPC)` (Orchestrator→MCP Tool Server): **red** — carries OI-2, OI-3
- `Training Signal Stream` (Audit Logger→Learning Loop): **red**

## 6. Visual Design Directives

- **Orientation**: Landscape 16:9
- **Background**: Dark navy gradient; zone subgraphs dashed
- **Components**: Rounded rectangles with severity badge top-right
- **F-201**: Red callout attached to LLM Agent Orchestrator naming OI-1/OI-2/OI-3 with 'OWASP LLM05:2025' tag
