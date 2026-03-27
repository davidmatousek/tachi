---
schema_version: "1.0"
template: "system-architecture"
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

## 5. Architecture Layout

### Zones (top-to-bottom)

| Zone | Trust Level | Position | Components |
|------|-------------|----------|------------|
| User Zone | Untrusted | Top | User |
| Application Zone | Semi-Trusted | Middle | LLM Agent Orchestrator, MCP Tool Server, Guardrails Service, Knowledge Base, Audit Logger |
| External Services | Untrusted | Bottom | External API |

### Component Placement

| Component | Zone | Row | Position | Border Color | Finding IDs | Badge |
|-----------|------|-----|----------|--------------|-------------|-------|
| User | User Zone | 1 | 1 | #EA580C | S-1, R-1 | 2 High |
| LLM Agent Orchestrator | Application Zone | 1 | 1 | #DC2626 | S-3, T-2, R-3, I-2, D-2, E-2, AG-1, AG-2, LLM-1, LLM-2, LLM-3 | 4 Critical |
| MCP Tool Server | Application Zone | 1 | 2 | #DC2626 | S-4, T-3, R-4, I-3, D-3, E-3, AG-3, AG-4 | 2 Critical |
| Guardrails Service | Application Zone | 1 | 3 | #DC2626 | S-2, T-1, R-2, I-1, D-1, E-1 | 1 Critical |
| Knowledge Base | Application Zone | 2 | 1 | #EA580C | T-4, I-4, D-4 | 2 High |
| Audit Logger | Application Zone | 2 | 2 | #EA580C | T-5, I-5, D-5 | 2 High |
| External API | External Services | 1 | 1 | #2563EB | R-5 | 1 Low |

### Data Flows

| Source | Destination | Label | Arrow Color | Related Findings |
|--------|-------------|-------|-------------|-----------------|
| User | Guardrails Service | HTTPS | #EA580C | S-1, S-2 |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | #EA580C | T-2, S-2 |
| Guardrails Service | User | Rejected Prompt | #EA580C | I-1 |
| LLM Agent Orchestrator | Knowledge Base | Vector Search | #EA580C | T-4, I-4, LLM-2 |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Docs | #EA580C | I-4, LLM-2 |
| LLM Agent Orchestrator | MCP Tool Server | JSON-RPC | #DC2626 | S-3, T-3, E-2, AG-1 |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | #EA580C | I-3, AG-4 |
| MCP Tool Server | External API | HTTPS | #EA580C | S-4 |
| LLM Agent Orchestrator | Audit Logger | Decision Log | #EA580C | R-3, T-5 |
| MCP Tool Server | Audit Logger | Tool Log | #EA580C | R-4, T-5 |
| Guardrails Service | Audit Logger | Filter Log | #EA580C | R-2, T-5 |

### Trust Boundary Crossings

| Boundary | Between Zones | Label | Finding IDs |
|----------|---------------|-------|-------------|
| TB-1 | User Zone -> Application Zone | User to Application | S-1, S-2, D-1, E-1 |
| TB-2 | Application Zone -> External Services | Application to External | S-4, R-5 |

## 6. Visual Design Directives

### Color Palette (White Theme)

| Element | Hex | Tailwind | Usage |
|---------|-----|----------|-------|
| Background | #FFFFFF | White | Main diagram background |
| Critical | #DC2626 | Red-600 | Component border, flow arrow, badge background |
| High | #EA580C | Orange-600 | Component border, flow arrow, badge background |
| Medium | #CA8A04 | Yellow-600 | Component border, flow arrow, badge background |
| Low | #2563EB | Blue-600 | Component border, flow arrow, badge background |
| Clean | #10B981 | Emerald-500 | Component border (analyzed, no findings) |
| Zone untrusted | #FEF2F2 | Red-50 | Untrusted zone subtle background tint |
| Zone application | #F8FAFC | Slate-50 | Application/semi-trusted zone background |
| Zone trusted | #F0FDF4 | Green-50 | Trusted zone subtle background tint |
| Zone border | #CBD5E1 | Slate-300 | Trust zone dashed border |
| Trust boundary | #94A3B8 | Slate-400 | Dashed line between zones, label text |
| Card fill | #FFFFFF | White | Component card background |
| Text primary | #111827 | Gray-900 | Component names, zone labels |
| Text secondary | #6B7280 | Gray-500 | Finding IDs, flow labels, legend |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Red-600 | Header badge |

### Layout Structure

- **Background**: White (#FFFFFF)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium, polished, consultancy-grade architecture poster. Sans-serif typography, Tailwind CSS palette.
- **Card Radius**: 8px rounded corners on all component boxes
- **Card Shadow**: 0 2px 8px rgba(0,0,0,0.1) subtle drop shadow
- **Spacing**: 16px minimum between components, 24px between zones
- **Zone Arrangement**: 3 zones stacked top-to-bottom by trust level (Untrusted top, Semi-Trusted middle, Untrusted bottom)
- **Components Per Row**: Maximum 5 before wrapping
- **Data Flow Arrows**: Smooth curves, colored by highest severity, labeled with protocol

### Typography

- **Title**: Bold, 28px, #111827
- **Subtitle**: Regular, 14px, #6B7280
- **Zone Label**: Semibold, 18px, #374151
- **Zone Trust Level**: Regular italic, 14px, #6B7280
- **Component Name**: Medium, 13px, #111827
- **Finding IDs**: Monospace, 11px, severity color
- **Badge Text**: Bold, 11px, #FFFFFF on severity background
- **Footer**: Regular, 12px, #6B7280
