---
schema_version: "1.0"
date: "2026-03-21"
source_file: "threats.md"
finding_count: 19
image_generated: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application (Mermaid Architecture) |
| Scan Date | 2026-03-21 |
| Analysis Agents | 8 |
| Total Findings | 19 |
| Risk Posture | Elevated risk — 3 Critical and 9 High findings across 5 components require immediate attention. |

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 3 | 15.8% | #DC2626 |
| High | 9 | 47.4% | #F97316 |
| Medium | 7 | 36.8% | #EAB308 |
| Low | 0 | 0.0% | #4169E1 |
| **Total** | **19** | **100%** | — |

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 2 | 4 | 4 | 0 | 10 |
| Knowledge Base | 0 | 3 | 1 | 0 | 4 |
| MCP Tool Server | 1 | 1 | 0 | 0 | 2 |
| User | 0 | 1 | 1 | 0 | 2 |
| External API | 0 | 0 | 1 | 0 | 1 |

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | AG-1 | LLM Agent Orchestrator | Autonomous execution of consequential tool calls without human approval for irreversible actions | Critical |
| 2 | AG-2 | MCP Tool Server | Unrestricted tool access without per-session capability scoping enables out-of-scope invocations | Critical |
| 3 | LLM-1 | LLM Agent Orchestrator | Direct prompt injection causing data exfiltration via crafted tool call parameters | Critical |
| 4 | S-1 | User | Authentication credential replay or forgery enabling unauthorized user impersonation | High |
| 5 | T-2 | Knowledge Base | Unauthorized document modification corrupting RAG retrieval results | High |

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | High | 10 | Highest-risk component with 2 Critical and 4 High findings spanning privilege escalation, prompt injection, information disclosure, and denial of service. Central attack surface due to orchestration role. |
| Knowledge Base | High | 4 | Elevated risk with 3 High findings covering data integrity, unauthorized access, and knowledge poisoning. Primary data store targeted for indirect attacks on downstream LLM context. |
| MCP Tool Server | Medium | 2 | Moderate risk with 1 Critical finding on unrestricted tool access and 1 High finding on unsanitized parameter forwarding. Attack surface concentrated on tool invocation controls. |
| User | Medium | 2 | Moderate risk with 1 High finding on authentication bypass and 1 Medium finding on action repudiation. External entry point requiring identity verification controls. |
| External API | Low | 1 | Low risk with 1 Medium finding on connection spoofing. Attack surface limited to outbound API communication channel. |

**Visual Guidance**: Components with `High` risk weight should be rendered with the largest visual emphasis (bold borders, larger icons, red highlight). `Medium` components receive moderate emphasis (orange highlight). `Low` components receive minimal emphasis (standard rendering).

## 6. Visual Design Directives

### Color Palette (CVSS Severity)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Highest severity indicators, urgent findings |
| High | #F97316 | High severity indicators, priority findings |
| Medium | #EAB308 | Medium severity indicators, planned remediation |
| Low | #4169E1 | Low severity indicators, accepted risk |
| Informational | #6B7280 | Neutral elements, labels, secondary text |

### Layout Structure

- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Three-Zone Layout**:
  1. **Header Zone** (top ~20%): Project name, scan date, total findings, risk posture summary, overall risk score
  2. **Distribution Zone** (middle ~40%): Risk distribution chart (donut or bar) on the left, coverage heat map on the right
  3. **Findings Zone** (bottom ~40%): Top critical findings list on the left, architecture threat overlay on the right

### Typography

- **Title**: Bold, 28-32pt equivalent
- **Section Headers**: Semi-bold, 18-22pt equivalent
- **Data Labels**: Regular, 12-14pt equivalent
- **Data Values**: Bold, 14-16pt equivalent

### Background

- Dark theme: Navy (#1E293B) with white text
- Light theme: White (#FFFFFF) with dark text
- Either theme is acceptable; dark theme preferred for presentation impact
