---
schema_version: "1.0"
template: "baseball-card"
date: "2026-03-25"
source_file: "threats.md"
finding_count: 38
image_generated: true
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-03-25 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 38 |
| Risk Posture | Elevated risk -- 7 Critical and 19 High findings across 7 components require immediate attention. 68.4% of findings rated High or Critical. |

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 7 | 18.4% | #DC2626 |
| High | 19 | 50.0% | #EA580C |
| Medium | 11 | 28.9% | #EAB308 |
| Low | 1 | 2.6% | #4169E1 |
| **Total** | **38** | **100%** | -- |

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 3 | 6 | 3 | 0 | 12 |
| MCP Tool Server | 2 | 5 | 2 | 0 | 9 |
| Guardrails Service | 0 | 3 | 3 | 0 | 6 |
| Knowledge Base | 0 | 2 | 2 | 0 | 4 |
| Audit Logger | 0 | 2 | 1 | 0 | 3 |
| User | 0 | 1 | 1 | 0 | 2 |
| External API | 0 | 0 | 1 | 1 | 2 |

## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | S-3 | LLM Agent Orchestrator | Attacker forges service identity to issue unauthorized tool calls to downstream services due to absent inter-service authentication | Critical |
| 2 | D-1 | LLM Agent Orchestrator | Concurrent maximum-length prompts exhaust compute and memory resources without rate limiting | Critical |
| 3 | E-1 | LLM Agent Orchestrator | Prompt manipulation triggers privileged operations without role-based access control enforcement | Critical |
| 4 | E-2 | MCP Tool Server | Standard users execute privileged tool endpoints without per-tool authorization | Critical |
| 5 | AG-1 | LLM Agent Orchestrator | Unbounded agent loop with no iteration limit, timeout, or cost cap enables infinite resource consumption | Critical |

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | High | 12 | Central risk nexus: 3 Critical findings spanning Spoofing, DoS, Privilege Escalation, Agent Autonomy, and Prompt Injection. Converges all major attack vectors. |
| MCP Tool Server | High | 9 | 2 Critical findings in Privilege Escalation and Agent Autonomy. Unscoped tool access and missing RBAC create direct path to unauthorized operations. |
| Guardrails Service | Medium | 6 | No Critical findings but 3 High findings in Spoofing, Tampering, and DoS. System entry point vulnerable to bypass and flooding. |
| Knowledge Base | Medium | 4 | 2 High findings in Tampering and Information Disclosure. Context retrieval pipeline vulnerable to poisoning and metadata exposure. |
| Audit Logger | Medium | 3 | 2 High findings in Tampering and Information Disclosure. Sole forensic evidence source vulnerable to tampering and data exposure. |
| User | Low | 2 | 1 High finding in Spoofing. Credential theft risk mitigated by implementing MFA and token binding. |
| External API | Low | 2 | 1 Medium and 1 Low finding. Limited attack surface with HTTPS protection. |

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: donut segment, heat map cells, finding card borders, risk posture badge |
| High | #EA580C | Orange-600: donut segment, heat map cells, finding card borders |
| Medium | #CA8A04 | Yellow-600: donut segment, heat map cells, finding card borders |
| Low | #2563EB | Blue-600: donut segment, heat map cells, finding card borders |
| Note | #6B7280 | Gray-500: informational only, excluded from visual risk distribution |
| Clean cell | #F3F4F6 | Gray-100: heat map analyzed with no findings |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- **Background**: White (#FFFFFF)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Clean, modern, corporate security report. Sans-serif typography, Tailwind color palette.
- **4-Zone Layout**:
  1. **TOP SECTION** (~10%): Title "Threat Model: Agentic AI Application", date 2026-03-25, CONFIDENTIAL badge, subtitle with 38 findings across 8 threat categories
  2. **MIDDLE ROW** (~50%): Left panel (donut chart + risk posture), Center panel (7-component x 8-category heat map), Right panel (5 critical finding cards with colored left border)
  3. **BOTTOM STRIP** (~30%): Architecture threat overlay with 3 trust zones (User Zone, Application Zone, External Services), data flow arrows by severity, 5 correlation callouts (CG-1 through CG-5)
  4. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework -- OWASP STRIDE + AI Threat Analysis"

### Typography

- **Title**: Bold, 28-32pt equivalent
- **Section Headers**: Semi-bold, 18-22pt equivalent
- **Data Labels**: Regular, 12-14pt equivalent
- **Data Values**: Bold, 14-16pt equivalent

### Background

- Dark theme: Navy (#1E293B) with white text
- Light theme: White (#FFFFFF) with dark text
- Either theme is acceptable; dark theme preferred for presentation impact
