---
schema_version: "1.0"
template: "risk-funnel"
date: "2026-04-19"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 69
image_generated: true
project_name: "Agentic AI Application"
fallback_note: "Extraction ran against threats.md (Tier 3 fallback); score numbers inlined from compensating-controls.md + risk-scores.md Executive Summary due to parser heading-format mismatch against current compensating-controls.md schema"
---

# Threat Infographic Specification — Risk Funnel

## 1. Metadata

- **Project**: Agentic AI Application
- **Scan Date**: 2026-04-19
- **Total Findings**: 70
- **Inherent Risk**: 395.6
- **Residual Risk**: 395.6
- **Risk Reduction**: 0.0% (0/70 controls implemented — reference architecture)

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

## 4. Funnel Tiers

| Tier | Label | Value | Source |
|-----:|-------|-------|--------|
| 1 | Threats Identified | 70 | threats.md Section 6 |
| 2 | Inherent Risk Scored | 395.6 | risk-scores.md §1 |
| 3 | Controls Applied | 0 implemented (0 partial, 70 missing) | compensating-controls.md §1 |
| 4 | Residual Risk | 395.6 (0.0% reduction) | compensating-controls.md §5 |

## 5. Template-Specific Format — Risk Funnel

4-tier vertical funnel. Tiers 2 and 4 have EQUAL width to visually communicate zero reduction (reference architecture has no implemented controls).

Right-side vertical callout lists Feature 201 OI findings 'carried through to residual':
- OI-1 XSS (residual 7.2 High)
- OI-2 Server-Exec (residual 6.7 Medium)
- OI-3 SSRF (residual 6.1 Medium)

## 6. Visual Design Directives

- **Orientation**: Portrait 9:16
- **Background**: Dark navy gradient
- **Funnel bands**: Glass-morphic 3D with drop shadow
- **F-201 emphasis**: Right-side vertical callout column with red accent bar
