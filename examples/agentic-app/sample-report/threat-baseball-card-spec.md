---
schema_version: "1.0"
template: "baseball-card"
date: "2026-04-19"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 69
image_generated: true
project_name: "Agentic AI Application"
fallback_note: "Extraction ran against threats.md (Tier 3 fallback); score numbers inlined from compensating-controls.md + risk-scores.md Executive Summary due to parser heading-format mismatch against current compensating-controls.md schema"
---

# Threat Infographic Specification — Baseball Card

## 1. Metadata

- **Project**: Agentic AI Application
- **Scan Date**: 2026-04-19
- **Schema Version**: 1.6
- **Data Source Tier**: 3 (threats)
- **Total Findings**: 69 (70 in source; parser yields 69 unique after dedup)
- **Components**: 10
- **Risk Posture**: Severity assessment — 38 Critical and 23 High findings across 10 components
- **Inherent Risk**: 395.6
- **Residual Risk**: 395.6 (0.0% reduction)
- **Control Coverage**: 0.0% (reference architecture)

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

## 4. Top Findings

Top 5 critical findings (with OI-1 surfaced for Feature 201 visibility):

| Rank | Finding ID | Component | Risk | Threat Summary |
|-----:|------------|-----------|------|----------------|
| 1 | AG-1 | LLM Agent Orchestrator | Critical | Prompt injection causes autonomous unauthorized high-impact actions |
| 2 | AG-2 | LLM Agent Orchestrator | Critical | Orchestrator+Specialist coordinate for policy circumvention above per-agent limits |
| 3 | AG-3 | Specialist Agent | Critical | Adversarial delegation causes autonomous prohibited cumulative tool call sequence |
| 4 | AG-4 | Inter-Agent Communication Channel | Critical | Agent-in-the-middle intercepts and modifies delegation messages |
| 5 | OI-1 | LLM Agent Orchestrator | Critical | Client-side XSS via LLM response to User browser (F-201, OWASP LLM05:2025) |

### Feature 201 Output-Integrity Findings

- **OI-1** (inherent Critical / residual 7.2 High): Client-side XSS via LLM response rendered in User browser
- **OI-2** (inherent Critical / residual 6.7 Medium): Server-side code/command execution via LLM-synthesized Tool Call parameters
- **OI-3** (inherent High / residual 6.1 Medium): SSRF via LLM-synthesized URL in Tool Call Request

## 5. Template-Specific Format — Baseball Card

Compact dashboard, four zones: (1) top header strip; (2) left-center risk donut; (3) right-center heat map; (4) bottom strip of 5 critical-finding cards (OI-1 included).

## 6. Visual Design Directives

- **Orientation**: Landscape 16:9
- **Background**: Dark navy gradient (#0F172A → #1E293B)
- **Severity palette**: Critical #DC2626, High #EA580C, Medium #CA8A04, Low #2563EB
- **Typography**: 32pt titles, 18pt labels
- **F-201 emphasis**: OI-1 card red-orange accent border, small 'F-201' tag
