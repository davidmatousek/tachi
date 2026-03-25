---
schema_version: "1.0"
template: "baseball-card"
date: "2026-03-25"
source_file: "threats.md"
finding_count: 38
image_generated: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-03-25 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 38 |
| Risk Posture | Elevated risk — 11 Critical and 16 High findings across 7 components require immediate attention. 71% of findings rated High or Critical. |

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 11 | 28.9% | #DC2626 |
| High | 16 | 42.1% | #EA580C |
| Medium | 9 | 23.7% | #EAB308 |
| Low | 2 | 5.3% | #4169E1 |
| **Total** | **38** | **100%** | — |

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 5 | 6 | 2 | 0 | 13 |
| MCP Tool Server | 2 | 4 | 2 | 0 | 8 |
| Guardrails Service | 1 | 3 | 1 | 0 | 5 |
| Audit Logger | 0 | 2 | 1 | 1 | 4 |
| Knowledge Base | 1 | 1 | 1 | 0 | 3 |
| User | 1 | 1 | 0 | 0 | 2 |
| External API | 0 | 0 | 1 | 1 | 2 |

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | S-1 | User | Attacker impersonates legitimate user via stolen or forged credentials at unprotected entry point | Critical |
| 2 | T-4 | Knowledge Base | Malicious content injected into Knowledge Base corrupts RAG retrieval context for all users | Critical |
| 3 | R-3 | LLM Agent Orchestrator | Tool calls executed without logging originating user, enabling denial of destructive actions | Critical |
| 4 | I-2 | LLM Agent Orchestrator | Sensitive internal context leaked in model responses including system prompts and API endpoints | Critical |
| 5 | D-1 | Guardrails Service | High-volume prompt flooding exhausts compute resources blocking all legitimate users | Critical |

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | High | 13 | Highest-risk component. Subject to all 8 threat categories including prompt injection (LLM-1), privilege escalation (E-2), and unbounded autonomy (AG-1). Central convergence point for 4 correlation groups. |
| MCP Tool Server | High | 8 | Second highest-risk component. Missing tool access controls (AG-3, E-3) and vulnerable to tool chain exploitation (AG-4). Gateway to external services. |
| Guardrails Service | High | 5 | Entry point security control. Vulnerable to bypass (S-2), configuration tampering (T-1), and flooding (D-1). Filter rule disclosure (I-1) enables iterative bypass. |
| Audit Logger | Medium | 4 | Critical infrastructure for accountability. Vulnerable to log tampering (T-5) and sensitive data exposure (I-5). Essential for forensic investigation capability. |
| Knowledge Base | High | 3 | Data integrity critical. Content injection (T-4) and poisoning (LLM-4) affect all downstream RAG responses. Metadata exposure (I-4) aids secondary attacks. |
| User | Medium | 2 | Entry point. Missing authentication (S-1) and non-repudiation (R-1) at the trust boundary. |
| External API | Low | 2 | External dependency. Low-severity findings for DNS spoofing (S-5) and mutual logging (R-5). |

## 6. Visual Design Directives

### Color Palette (Dark Theme — Baseball Card)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: donut segment, heat map cells, finding card borders, risk posture badge |
| High | #EA580C | Orange-600: donut segment, heat map cells, finding card borders |
| Medium | #CA8A04 | Yellow-600: donut segment, heat map cells, finding card borders |
| Low | #2563EB | Blue-600: donut segment, heat map cells, finding card borders |
| Note | #6B7280 | Gray-500: informational only, excluded from visual risk distribution |
| Background | #1E293B | Slate-800: main dashboard background |
| Card bg | #334155 | Slate-700: finding cards, panel containers |
| Clean cell | #334155 | Slate-700: heat map analyzed with no findings |
| N/A cell | #1E293B | Slate-800: heat map not applicable |
| Text primary | #F8FAFC | Slate-50: titles, component names |
| Text secondary | #94A3B8 | Slate-400: labels, captions |
| Border | #475569 | Slate-600: panel and card borders |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Red-600 |

### Layout Structure

- **Background**: Dark Navy (#1E293B)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium, polished, boardroom-ready dark dashboard. Sans-serif typography, Tailwind color palette.
- **4-Zone Layout**:
  1. **TOP SECTION** (~10%): Title "Threat Model: Agentic AI Application", date "2026-03-25", CONFIDENTIAL badge, subtitle "Mermaid — 38 Findings Across 8 Threat Categories"
  2. **MIDDLE ROW** (~50%): Left panel (donut chart + risk posture), Center panel (7-component x 8-category heat map), Right panel (5 critical finding cards)
  3. **BOTTOM STRIP** (~30%): Architecture threat overlay with 3 trust zones (User Zone, Application Zone, External Services), data flow arrows colored by severity, 5 correlation group callouts
  4. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework — OWASP STRIDE + AI Threat Analysis"

### Typography

- **Title**: Bold, 32px
- **Subtitle**: Regular, 16px
- **Section Headers**: Semibold, 20px
- **Data Labels**: Regular, 14px
- **Data Values**: Medium, 16px, severity color
- **Finding IDs**: Monospace, 12px, severity color
- **Footer**: Regular, 12px, Gray-500
