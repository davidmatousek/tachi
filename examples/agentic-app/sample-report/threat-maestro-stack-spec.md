---
schema_version: "1.0"
template: "maestro-stack"
date: "2026-04-19"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 69
image_generated: true
project_name: "Agentic AI Application"
fallback_note: "Extraction ran against threats.md (Tier 3 fallback); score numbers inlined from compensating-controls.md + risk-scores.md Executive Summary due to parser heading-format mismatch against current compensating-controls.md schema"
---

# Threat Infographic Specification — MAESTRO Stack

## 1. Metadata

- **Project**: Agentic AI Application
- **Scan Date**: 2026-04-19
- **Total Findings**: 69
- **MAESTRO Layers Populated**: 6/7 (L4 empty)

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

## 4. Top Findings by Layer

**Most-exposed layer**: L1 Foundation Model (LLM Agent Orchestrator, 15C+3H) — includes all 3 Feature 201 OI findings.

| Layer | Components | Critical | High |
|-------|------------|---------:|-----:|
| L7 — Agent Ecosystem | User | 1 | 0 |
| L6 — Security and Compliance | Guardrails Service | 2 | 2 |
| L5 — Evaluation and Observability | Audit Logger | 1 | 2 |
| L4 — Deployment Infrastructure | — | 0 | 0 |
| L3 — Agent Framework | MCP Tool Server | 5 | 3 |
| L2 — Data Operations | Knowledge Base | 0 | 2 |
| L1 — Foundation Model | LLM Agent Orchestrator | 15 | 3 |

## 5. Template-Specific Format — MAESTRO Stack

7-layer vertical stack (L7 top, L1 bottom). L1 rendered as the most-exposed band in deep red, carrying a red-bordered callout box naming Feature 201 OI-1 (XSS, Critical), OI-2 (Server-Exec, Critical), OI-3 (SSRF, High) — OWASP LLM05:2025.

## 6. Visual Design Directives

- **Orientation**: Portrait 9:16
- **Background**: Dark navy gradient
- **Layer band colors**: Tint by highest-severity finding in layer (L1 deepest red)
- **F-201 callout**: Red-bordered box attached to L1 band with OI-1/OI-2/OI-3 listing
