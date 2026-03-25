---
schema_version: "1.0"
template: "baseball-card"
date: "2026-03-25"
source_file: "threats.md"
finding_count: 34
image_generated: true
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-03-25 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 34 |
| Risk Posture | Elevated risk -- 8 Critical and 14 High findings across 7 components require immediate attention. The LLM Agent Orchestrator concentrates 11 findings as the system's highest-risk nexus. |

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 8 | 23.5% | #DC2626 |
| High | 14 | 41.2% | #EA580C |
| Medium | 6 | 17.6% | #EAB308 |
| Low | 1 | 2.9% | #4169E1 |
| **Total** | **34** | **100%** | -- |

Note: 5 findings (14.7%) have risk level Note or are excluded from the visual distribution. Percentages computed over all 34 findings. The visual donut chart segments represent Critical (8), High (14), Medium (6), Low (1). Remaining 5 findings at Note level are excluded.

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 4 | 5 | 2 | 0 | 11 |
| MCP Tool Server | 2 | 4 | 1 | 0 | 7 |
| Guardrails Service | 1 | 3 | 1 | 0 | 5 |
| Knowledge Base | 0 | 2 | 1 | 0 | 3 |
| Audit Logger | 0 | 2 | 1 | 0 | 3 |
| User | 0 | 1 | 1 | 0 | 2 |
| External API | 0 | 0 | 0 | 1 | 1 |

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | S-3 | LLM Agent Orchestrator | Attacker forges tool call requests by impersonating the Orchestrator on unauthenticated JSON-RPC channel | Critical |
| 2 | T-3 | MCP Tool Server | Malicious payload injection into tool call parameters without schema validation | Critical |
| 3 | D-1 | Guardrails Service | CPU exhaustion via high-volume prompt flooding without rate limiting | Critical |
| 4 | D-2 | LLM Agent Orchestrator | LLM inference compute exhaustion via concurrent maximum-length prompts | Critical |
| 5 | E-2 | LLM Agent Orchestrator | Privilege escalation to admin tool access via prompt injection manipulating tool selection | Critical |

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | High | 11 | Highest-risk component: subject to all STRIDE categories plus LLM and Agentic threats. Critical findings in spoofing (S-3), denial of service (D-2), privilege escalation (E-2), agent autonomy (AG-1), and prompt injection (LLM-1). Central coordination hub with access to Knowledge Base, MCP Tool Server, and direct user communication. |
| MCP Tool Server | High | 7 | High-risk execution layer: critical findings in tampering (T-3) and privilege escalation (E-3), plus agentic threats (AG-3, AG-4). Exposes all registered tools without capability scoping. |
| Guardrails Service | High | 5 | Entry point with critical DoS risk (D-1). Information disclosure through detailed rejection messages (I-1). Configuration tampering risk (T-1). Authorization bypass possible via alternate routes (E-1). |
| Knowledge Base | Medium | 3 | Data integrity risk from content poisoning (T-4) correlating with indirect prompt injection (LLM-2, CG-1). Information disclosure through unfiltered metadata (I-4). |
| Audit Logger | Medium | 3 | Accountability infrastructure at risk: log tampering (T-5), sensitive data exposure (I-5), and storage exhaustion (D-5). |
| User | Low | 2 | External entity with token replay risk (S-1) and repudiation gap (R-1). |
| External API | Low | 1 | Minimal direct risk: correlation ID gap (R-5) only. |

## 6. Visual Design Directives

### Color Palette (Dark Theme)

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
| Border | #475569 | Slate-600 | Panel borders, card borders |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Red-600 | Top section badge |

### Layout Structure

- **Background**: Dark Navy (#1E293B)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium, polished, boardroom-ready dark dashboard. Sans-serif typography, Tailwind color palette.
- **Card Radius**: 12px rounded corners
- **Card Shadow**: 0 4px 12px rgba(0,0,0,0.3)
- **4-Zone Layout**:
  1. **TOP SECTION** (~10%): Title "Threat Model: Agentic AI Application", date "2026-03-25", CONFIDENTIAL badge, subtitle "mermaid -- 34 Findings Across 8 Threat Categories"
  2. **MIDDLE ROW** (~50%): Left panel (donut chart + risk posture), Center panel (7-component x 8-category heat map), Right panel (5 critical finding cards)
  3. **BOTTOM STRIP** (~30%): Simplified architecture: 3 trust zones (User Zone, Application Zone, External Services), data flow arrows colored by severity, trust boundary crossings with finding IDs, 4 correlation callouts (CG-1 through CG-4)
  4. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework -- OWASP STRIDE + AI Threat Analysis"

### Typography

- **Title**: Bold, 32px
- **Section Headers**: Semibold, 20px
- **Data Labels**: Regular, 14px
- **Data Values**: Medium, 16px, severity color
- **Finding IDs**: Monospace, 12px, severity color
- **Footer**: Regular, 12px, Gray-500
