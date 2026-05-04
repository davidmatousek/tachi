---
schema_version: "1.0"
template: "baseball-card"
date: "2026-03-25"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 33
image_generated: true
---

# Threat Infographic Specification: Baseball Card

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

- Rows ordered by Total descending
- 7 named component rows (under 8 threshold, no "Other" aggregation needed)
- Component names match threats.md exactly
- Cell values are integer counts

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | S-3 | LLM Agent Orchestrator | Attacker forges service identity to impersonate the orchestrator in communication with downstream services due to missing inter-service authentication. | Critical |
| 2 | D-1 | LLM Agent Orchestrator | Concurrent maximum-length prompts exhaust compute and memory resources due to missing per-client rate limits and request size caps. | Critical |
| 3 | E-1 | LLM Agent Orchestrator | Prompt manipulation triggers privileged operations without RBAC enforcement on tools and Knowledge Base operations. | Critical |
| 4 | E-2 | MCP Tool Server | Standard users can execute privileged tool endpoints without access control on tool dispatch. | Critical |
| 5 | AG-1 | LLM Agent Orchestrator | Unbounded agent loop with no iteration limit, execution timeout, or cost cap allows indefinite resource consumption. | Critical |

Note: 7 Critical findings total. Showing top 5 by severity.

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | High | 13 | Highest risk concentration. 4 Critical findings across Spoofing (S-3), DoS (D-1), Elevation of Privilege (E-1), and Agentic Autonomy (AG-1). Dominant attack surface for prompt injection (LLM-1), data poisoning (LLM-2, LLM-3), and privilege escalation. Weighted score: 37. |
| MCP Tool Server | High | 7 | 2 Critical findings (E-2, AG-3) exposing unrestricted tool access. High risk from tampering (T-3), spoofing (S-4), information disclosure (I-2), and repudiation (R-4). Weighted score: 22. |
| Guardrails Service | Medium | 5 | No Critical findings but 2 High (S-2, T-1) threatening input validation bypass. Medium findings in repudiation, information disclosure, and DoS. Weighted score: 11. |
| Knowledge Base | Medium | 3 | 1 High finding (T-4) on document injection. Medium findings on adversarial embedding corruption (T-6) and expensive queries (D-3). Weighted score: 7. |
| Audit Logger | Medium | 2 | 1 High finding (T-5) on log tampering with 1 Medium (D-5) on log flooding. Integrity of audit trail at risk. Weighted score: 5. |
| User | Medium | 2 | 1 High finding (S-1) on credential theft, 1 Medium (R-1) on action repudiation. Entry point for impersonation attacks. Weighted score: 5. |
| External API | Low | 2 | 1 Medium (S-5) on DNS spoofing, 1 Low (R-5) on attribution gaps. Lowest risk component with no High or Critical findings. Weighted score: 3. |

**Visual Guidance**: Components with `High` risk weight (LLM Agent Orchestrator, MCP Tool Server) should be rendered with the largest visual emphasis (bold borders, larger icons, red highlight). `Medium` components (Guardrails Service, Knowledge Base, Audit Logger, User) receive moderate emphasis (orange highlight). `Low` components (External API) receive minimal emphasis (standard rendering).

## 6. Visual Design Directives

### Color Palette (Dark Theme — Tailwind CSS)

| Element | Hex | Tailwind | Usage |
|---------|-----|----------|-------|
| Background | #1E293B | Slate-800 | Main dashboard background |
| Card background | #334155 | Slate-700 | Finding cards, panel containers |
| Critical | #DC2626 | Red-600 | Donut segment, heat map cells, finding card borders, risk posture badge |
| High | #EA580C | Orange-600 | Donut segment, heat map cells, finding card borders |
| Medium | #CA8A04 | Yellow-600 | Donut segment, heat map cells, finding card borders |
| Low | #2563EB | Blue-600 | Donut segment, heat map cells, finding card borders |
| Note | #6B7280 | Gray-500 | Informational only (excluded from visual risk distribution) |
| Clean cell | #334155 | Slate-700 | Heat map: analyzed, no findings (subtle dark) |
| N/A cell | #1E293B | Slate-800 | Heat map: not applicable (matches background) |
| Text primary | #F8FAFC | Slate-50 | Titles, component names, finding descriptions |
| Text secondary | #94A3B8 | Slate-400 | Labels, captions, subtitles |
| Text muted | #64748B | Slate-500 | Footer, less prominent labels |
| Border | #475569 | Slate-600 | Panel borders, card borders |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Red-600 | Top section badge |

### Layout Structure

- **Background**: Dark Navy (#1E293B)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium, polished, professional report-grade dark dashboard. Sans-serif typography, Tailwind color palette.
- **Card Radius**: 12px rounded corners
- **Card Shadow**: 0 4px 12px rgba(0,0,0,0.3)
- **Spacing**: Generous whitespace — 16-24px between panels, 12px between cards
- **4-Zone Layout**:
  1. **TOP SECTION** (~10%): Title "Threat Model: Agentic AI Application", date "2026-03-25", CONFIDENTIAL badge, subtitle "33 Findings Across 8 Threat Categories"
  2. **MIDDLE ROW** (~50%): Left panel (donut chart + severity legend + risk posture badge), Center panel (7-component x 8-category coverage heat map), Right panel (top 5 critical finding cards with colored left border)
  3. **BOTTOM STRIP** (~30%): Architecture threat overlay with 3 trust zones (User Zone, Application Zone, External Services), data flow arrows colored by severity, trust boundary crossings, correlation callouts (CG-1 through CG-5)
  4. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Title | 32px | Bold | #F8FAFC |
| Subtitle | 16px | Regular | #94A3B8 |
| Section headers | 20px | Semibold | #F8FAFC |
| Body text / labels | 14px | Regular | #94A3B8 |
| Data values | 16px | Medium | Severity color |
| Finding IDs | 12px | Monospace | Severity color |
| Footer | 12px | Regular | #64748B |

### Risk Posture Badge

- Label: "RISK POSTURE: HIGH"
- Color: #DC2626 (Critical — highest severity with >20% of findings)
- Subtitle: "66.7% of findings rated High or Critical"
