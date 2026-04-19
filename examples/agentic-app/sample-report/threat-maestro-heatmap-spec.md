---
schema_version: "1.0"
template: "maestro-heatmap"
date: "2026-04-19"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 69
image_generated: true
project_name: "Agentic AI Application"
fallback_note: "Extraction ran against threats.md (Tier 3 fallback); score numbers inlined from compensating-controls.md + risk-scores.md Executive Summary due to parser heading-format mismatch against current compensating-controls.md schema"
---

# Threat Infographic Specification — MAESTRO Heatmap

## 1. Metadata

- **Project**: Agentic AI Application
- **Scan Date**: 2026-04-19
- **Total Findings**: 69
- **Matrix Shape**: 6 components × 7 MAESTRO layers

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

## 4. Top Findings (MAESTRO Hotspots)

| Component | Layer | Severity | F-201 OI? |
|-----------|:-----:|:--------:|:---------:|
| LLM Agent Orchestrator | L1 | Critical | Yes — OI-1, OI-2, OI-3 |
| MCP Tool Server | L3 | Critical | — |
| Guardrails Service | L6 | Critical | — |
| Audit Logger | L5 | Critical | — |
| Knowledge Base | L2 | High | — |
| User | L7 | Critical | — |

## 5. Template-Specific Format — MAESTRO Heatmap

MAESTRO layer (L1-L7 columns) × component (rows) matrix. Cells colored by severity. LLM Agent Orchestrator × L1 cell carries red-bordered callout naming OI-1/OI-2/OI-3 (Feature 201 / OWASP LLM05:2025).

## 6. Visual Design Directives

- **Orientation**: Landscape 16:9
- **Background**: Dark navy gradient
- **Cell tiles**: Severity-colored beveled 3D tiles
- **F-201 callout**: Red dashed border overlay on LLM Agent Orchestrator × L1 cell
