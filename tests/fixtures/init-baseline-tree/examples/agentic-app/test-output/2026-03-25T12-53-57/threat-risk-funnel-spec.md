---
schema_version: "1.0"
template: "risk-funnel"
date: "2026-03-25"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 33
image_generated: true
---

# Threat Infographic Specification: Risk Reduction Funnel

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-03-25 |
| Analysis Agents | 8 |
| Total Findings | 33 |
| Severity Posture | Elevated risk — 7 Critical and 15 High findings across 7 components require immediate attention. 66.7% of findings rated High or Critical. |

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 7 | 21.2% | #DC2626 |
| High | 15 | 45.5% | #EA580C |
| Medium | 10 | 30.3% | #CA8A04 |
| Low | 1 | 3.0% | #2563EB |
| **Total** | **33** | **100%** | — |

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 4 | 6 | 3 | 0 | 13 |
| MCP Tool Server | 2 | 4 | 1 | 0 | 7 |
| Guardrails Service | 0 | 2 | 3 | 0 | 5 |
| Knowledge Base | 0 | 1 | 2 | 0 | 3 |
| Audit Logger | 0 | 1 | 1 | 0 | 2 |
| User | 0 | 1 | 1 | 0 | 2 |
| External API | 0 | 0 | 1 | 1 | 2 |

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | S-3 | LLM Agent Orchestrator | Attacker forges service identity to impersonate the orchestrator in communication with downstream services due to missing inter-service authentication. | Critical |
| 2 | D-1 | LLM Agent Orchestrator | Concurrent maximum-length prompts exhaust compute and memory resources due to missing per-client rate limits and request size caps. | Critical |
| 3 | E-1 | LLM Agent Orchestrator | Prompt manipulation triggers privileged operations without RBAC enforcement on tools and Knowledge Base operations. | Critical |
| 4 | E-2 | MCP Tool Server | Standard users can execute privileged tool endpoints without access control on tool dispatch. | Critical |
| 5 | AG-1 | LLM Agent Orchestrator | Unbounded agent loop with no iteration limit, execution timeout, or cost cap allows indefinite resource consumption. | Critical |

## 5. Architecture Threat Overlay

### Funnel Tiers

| Tier | Label | Width (%) | Severity Counts | Render State |
|------|-------|-----------|-----------------|--------------|
| 1 | Threats Identified | 100 | 7C / 15H / 10M / 1L | solid |
| 2 | Inherent Risk Scored | 75 | — | ghost |
| 3 | Controls Applied | 50 | — | ghost |
| 4 | Residual Risk | 30 | — | ghost |

### Tier Details

**Tier 1 — Threats Identified (solid)**
- Width: 100%
- Color: #EA580C (High is dominant severity at 45.5%)
- Data: "33 findings — 7C / 15H / 10M / 1L"
- Data source: threats.md Section 6 (Risk Summary)

**Tier 2 — Inherent Risk Scored (ghost)**
- Width: 75%
- Border: 2px dashed #475569
- Fill: #475569 at 20% opacity
- CTA: "Run /risk-score"

**Tier 3 — Controls Applied (ghost)**
- Width: 50%
- Border: 2px dashed #475569
- Fill: #475569 at 20% opacity
- CTA: "Run /compensating-controls"

**Tier 4 — Residual Risk (ghost)**
- Width: 30%
- Border: 2px dashed #475569
- Fill: #475569 at 20% opacity
- CTA: "Complete the pipeline"

### Tier Width Calculation

Tier widths use default proportional spacing for 1-tier mode:
- Tier 1: 100% (baseline — total threats identified, solid)
- Tier 2: 75% (ghost — preserves funnel shape)
- Tier 3: 50% (ghost — preserves funnel shape)
- Tier 4: 30% (ghost — preserves funnel shape)
- Minimum 10% narrowing per tier enforced
- Absolute floor: 10% width

### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Findings | 33 |
| Critical | 7 |
| High | 15 |
| Medium | 10 |
| Low | 1 |

### Enhancement Tip

Run `/risk-score` to begin quantifying your risk reduction funnel.

## 6. Visual Design Directives

### Color Palette (Dark Theme — Tailwind CSS)

| Element | Hex | Tailwind | Usage |
|---------|-----|----------|-------|
| Background | #1E293B | Slate-800 | Main dashboard background |
| Critical | #DC2626 | Red-600 | Tier fill when Critical is dominant severity |
| High | #EA580C | Orange-600 | Tier fill when High is dominant severity |
| Medium | #CA8A04 | Yellow-600 | Tier fill when Medium is dominant severity |
| Low | #2563EB | Blue-600 | Tier fill when Low is dominant severity |
| Note | #6B7280 | Gray-500 | Informational (excluded from visual risk distribution) |
| Ghost tier border | #475569 | Slate-600 | Dashed border for unavailable tiers |
| Ghost tier fill | #475569 at 20% opacity | Slate-600/20 | Translucent fill for ghost tiers |
| Sidebar background | #334155 | Slate-700 | Metrics sidebar card background |
| Text primary | #F8FAFC | Slate-50 | Titles, tier labels, metric values |
| Text secondary | #94A3B8 | Slate-400 | Subtitles, captions, footer |
| Text muted | #64748B | Slate-500 | Footer, less prominent labels |
| Border | #475569 | Slate-600 | Panel borders |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Red-600 | Header badge |
| Gradient connector | Linear blend between adjacent tier colors | -- | Flowing transition between tiers |

### Layout Structure

- **Background**: Dark Navy (#1E293B)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium executive boardroom, photorealistic 3D funnel with glass-like translucent material. Sans-serif typography, Tailwind color palette.
- **Card Radius**: 12px rounded corners
- **Card Shadow**: 0 4px 12px rgba(0,0,0,0.3)
- **Spacing**: Generous whitespace — 16-24px between zones, 12px internal padding
- **Layout Zones**:
  1. **HEADER** (~8%): Title "Risk Reduction Funnel", project "Agentic AI Application", date "2026-03-25", CONFIDENTIAL badge
  2. **FUNNEL ZONE** (~62%, ~75% width): 4 trapezoid tiers narrowing top-to-bottom. Tier 1 solid (orange, High dominant). Tiers 2-4 ghost (dashed borders, translucent fill, CTA labels).
  3. **METRICS SIDEBAR** (~20% width, right-aligned): Dark card (#334155) with total findings and qualitative severity counts.
  4. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework — Risk Reduction Funnel"

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Title | 32px | Bold | #F8FAFC |
| Subtitle (project name) | 16px | Regular | #94A3B8 |
| Section headers | 20px | Semibold | #F8FAFC |
| Tier labels | 18px | Semibold | #F8FAFC |
| Tier data values | 16px | Medium | Severity color |
| Body text / metrics | 14px | Regular | #94A3B8 |
| CTA text (ghost tiers) | 14px | Regular | #FFFFFF |
| Footer | 12px | Regular | #94A3B8 |

### Funnel Rendering Notes

- 1-tier mode: Only Tier 1 is solid. Tiers 2-4 are ghost tiers with CTA labels.
- Ghost tiers maintain funnel shape (proportional widths preserved).
- Gradient connectors between tiers blend solid tier color into ghost tier appearance.
- CTA labels are centered within ghost tiers in white text.
