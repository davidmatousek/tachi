---
schema_version: "1.0"
template: "system-architecture"
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

**Chart Format**: Suitable for annotated architecture diagram with severity-colored component borders.

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
| 1 | S-3 | LLM Agent Orchestrator | Attacker forges service identity to issue unauthorized tool calls to downstream services | Critical |
| 2 | D-1 | LLM Agent Orchestrator | Concurrent maximum-length prompts exhaust compute and memory without rate limiting | Critical |
| 3 | E-1 | LLM Agent Orchestrator | Prompt manipulation triggers privileged operations without RBAC | Critical |
| 4 | E-2 | MCP Tool Server | Standard users execute privileged tool endpoints without authorization | Critical |
| 5 | AG-1 | LLM Agent Orchestrator | Unbounded agent loop with no iteration limit or cost cap | Critical |

## 5. Architecture Layout

### Zones (top-to-bottom)

| Zone | Trust Level | Position | Components |
|------|-------------|----------|------------|
| User Zone | Untrusted | Top | User |
| Application Zone | Trusted | Middle | Guardrails Service, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger |
| External Services | Semi-Trusted | Bottom | External API |

### Component Placement

| Component | Zone | Row | Position | Border Color | Finding IDs | Badge |
|-----------|------|-----|----------|--------------|-------------|-------|
| User | User Zone | 1 | 1 | #EA580C | S-1, R-1 | 2 findings |
| LLM Agent Orchestrator | Application Zone | 1 | 1 | #DC2626 | S-3, T-2, R-2, I-1, D-1, E-1, AG-1, AG-2, LLM-1, LLM-2, LLM-3, LLM-4 | 12 findings (3 Critical) |
| MCP Tool Server | Application Zone | 1 | 2 | #DC2626 | S-4, T-3, R-4, I-2, D-2, E-2, E-4, AG-3, AG-4 | 9 findings (2 Critical) |
| Guardrails Service | Application Zone | 1 | 3 | #EA580C | S-2, T-1, R-3, I-5, D-4, E-3 | 6 findings (3 High) |
| Knowledge Base | Application Zone | 2 | 1 | #EA580C | T-4, T-6, I-3, D-3 | 4 findings (2 High) |
| Audit Logger | Application Zone | 2 | 2 | #EA580C | T-5, I-4, D-5 | 3 findings (2 High) |
| External API | External Services | 1 | 1 | #CA8A04 | S-5, R-5 | 2 findings (1 Medium) |

### Data Flows

| Source | Destination | Label | Arrow Color | Related Findings |
|--------|-------------|-------|-------------|-----------------|
| User | Guardrails Service | HTTPS | #EA580C | S-1, S-2 |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | #EA580C | T-2, S-2 |
| Guardrails Service | User | Rejection | #CA8A04 | I-5 |
| LLM Agent Orchestrator | Knowledge Base | Vector Search | #EA580C | T-4, I-3, LLM-3 |
| Knowledge Base | LLM Agent Orchestrator | Documents | #EA580C | LLM-2, I-3 |
| LLM Agent Orchestrator | MCP Tool Server | JSON-RPC | #DC2626 | S-3, T-3, E-1, AG-1 |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | #EA580C | I-2, T-3 |
| MCP Tool Server | External API | HTTPS | #CA8A04 | S-5, R-5 |
| LLM Agent Orchestrator | User | Response | #DC2626 | LLM-1, I-1 |
| LLM Agent Orchestrator | Audit Logger | Decision Log | #EA580C | R-2, T-5 |
| MCP Tool Server | Audit Logger | Tool Exec Log | #EA580C | R-4, T-5 |
| Guardrails Service | Audit Logger | Filter Log | #EA580C | R-3, T-5 |

### Trust Boundary Crossings

| Boundary | Between Zones | Label | Finding IDs |
|----------|---------------|-------|-------------|
| TB-1 | User Zone -> Application Zone | User-to-Application | S-1, S-2, D-4, LLM-1 |
| TB-2 | Application Zone -> External Services | Application-to-External | S-5, R-5, E-4 |
| TB-3 | Application Zone -> User Zone | Application-to-User (Response) | I-1, I-5, LLM-1 |

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: component border, flow arrow, badge background |
| High | #EA580C | Orange-600: component border, flow arrow, badge background |
| Medium | #CA8A04 | Yellow-600: component border, flow arrow, badge background |
| Low | #2563EB | Blue-600: component border, flow arrow, badge background |
| Clean | #10B981 | Emerald-500: component border for clean components |
| Zone background | #F8FAFC | Slate-50: trust zone region fill |
| Zone border | #CBD5E1 | Slate-300: trust zone dashed border |
| Trust boundary | #94A3B8 | Slate-400: dashed line between zones |

### Layout Structure

- **Background**: White (#FFFFFF)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Clean, modern, annotated architecture diagram. Sans-serif typography, Tailwind color palette.
- **Zone-Stacked Layout**:
  1. **HEADER** (~10%): Title "Agentic AI Application -- Threat Model", subtitle, date, CONFIDENTIAL badge, finding count
  2. **ZONE STACK** (~80%): Three zones stacked vertically (User Zone top, Application Zone middle, External Services bottom) with components placed inside zones, data flow arrows between components, trust boundary dashed lines between zones
  3. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework -- OWASP STRIDE + AI Threat Analysis"

### Typography

- **Title**: Bold, 28px
- **Zone Labels**: Semi-bold, 18px
- **Component Names**: Medium, 13px
- **Finding IDs**: Monospace, 11px, severity-colored
- **Badge Text**: Bold, 11px, white on severity background
- **Footer**: Regular, 12px, Gray-500
