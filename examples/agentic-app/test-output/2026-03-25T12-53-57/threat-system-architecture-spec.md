---
schema_version: "1.0"
template: "system-architecture"
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

**Chart Format**: Suitable for annotated architecture diagram with severity-colored component borders and data flow arrows.

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

## 5. Architecture Layout

### Zones (top-to-bottom)

| Zone | Trust Level | Position | Components |
|------|-------------|----------|------------|
| User Zone | Untrusted | Top | User |
| External Services | Untrusted | Top | External API |
| Application Zone | Semi-Trusted | Middle | Guardrails Service, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger |

### Component Placement

| Component | Zone | Row | Position | Border Color | Finding IDs | Badge |
|-----------|------|-----|----------|--------------|-------------|-------|
| User | User Zone | 1 | 1 | #DC2626 | S-1, R-1 | 1 Critical |
| External API | External Services | 1 | 1 | #CA8A04 | S-5, R-5 | 2 Medium |
| LLM Agent Orchestrator | Application Zone | 1 | 1 | #DC2626 | S-3, T-2, R-3, I-2, D-2, E-2, AG-1, AG-2, LLM-1, LLM-2, LLM-3, LLM-4, LLM-5 | 5 Critical |
| MCP Tool Server | Application Zone | 1 | 2 | #DC2626 | S-4, T-3, R-4, I-3, D-3, E-3, AG-3, AG-4 | 2 Critical |
| Guardrails Service | Application Zone | 1 | 3 | #DC2626 | S-2, T-1, R-2, I-1, D-1, E-1 | 1 Critical |
| Knowledge Base | Application Zone | 2 | 1 | #DC2626 | T-4, I-4, D-4 | 1 Critical |
| Audit Logger | Application Zone | 2 | 2 | #EA580C | T-5, I-5, I-6, D-5 | 2 High |

### Data Flows

| Source | Destination | Label | Arrow Color | Related Findings |
|--------|-------------|-------|-------------|-----------------|
| User | Guardrails Service | HTTPS | #DC2626 | S-1, S-2, D-1 |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | #EA580C | T-2, S-2 |
| Guardrails Service | User | Rejected Prompt | #EA580C | I-1 |
| LLM Agent Orchestrator | Knowledge Base | Vector Search | #DC2626 | T-4, I-4, LLM-4 |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | #DC2626 | LLM-2, I-4 |
| LLM Agent Orchestrator | MCP Tool Server | JSON-RPC | #DC2626 | S-3, T-3, E-2, AG-1 |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | #EA580C | S-4 |
| MCP Tool Server | External API | HTTPS | #CA8A04 | S-5, D-3 |
| LLM Agent Orchestrator | User | HTTPS Response | #DC2626 | I-2, LLM-1 |
| LLM Agent Orchestrator | Audit Logger | Decision Log | #DC2626 | R-3 |
| MCP Tool Server | Audit Logger | Tool Log | #CA8A04 | R-4 |
| Guardrails Service | Audit Logger | Filter Log | #CA8A04 | R-2 |

### Trust Boundary Crossings

| Boundary | Between Zones | Label | Finding IDs |
|----------|---------------|-------|-------------|
| TB-1 | User Zone → Application Zone | User to Application | S-1, S-2, D-1, R-1 |
| TB-2 | Application Zone → External Services | Application to External | S-5, D-3, R-5 |
| TB-3 | Application Zone → User Zone | Application Response to User | I-2, LLM-1, I-1 |

## 6. Visual Design Directives

### Color Palette (White Theme — System Architecture)

| Element | Hex | Usage |
|---------|-----|-------|
| Background | #FFFFFF | Main diagram background |
| Critical | #DC2626 | Component border, flow arrow, badge background |
| High | #EA580C | Component border, flow arrow, badge background |
| Medium | #CA8A04 | Component border, flow arrow, badge background |
| Low | #2563EB | Component border, flow arrow, badge background |
| Clean | #10B981 | Component border for analyzed, no findings |
| Zone untrusted | #FEF2F2 | Untrusted zone subtle background tint |
| Zone application | #F8FAFC | Application zone background |
| Zone trusted | #F0FDF4 | Trusted zone background tint |
| Zone border | #CBD5E1 | Trust zone dashed border |
| Trust boundary | #94A3B8 | Dashed line between zones |
| Card fill | #FFFFFF | Component card background |
| Text primary | #111827 | Component names, zone labels |
| Text secondary | #6B7280 | Finding IDs, flow labels |
| Arrow default | #374151 | Data flow arrows without findings |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Header badge |

### Layout Structure

- **Background**: White (#FFFFFF)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium, polished, consultancy-grade architecture poster. Sans-serif typography, Tailwind CSS palette.
- **Zone-Stacked Layout**:
  1. **HEADER**: Title "Agentic AI Application — Threat Model", subtitle "Architecture with attack surface annotations", date "2026-03-25", CONFIDENTIAL badge, "38 Findings Across 8 Threat Categories"
  2. **ZONE 1 (Top)**: User Zone (Untrusted) + External Services (Untrusted) — User component with Critical border, External API with Medium border
  3. **TB-1**: Trust boundary dashed line "User to Application" with finding annotations S-1, S-2, D-1, R-1
  4. **ZONE 2 (Middle)**: Application Zone (Semi-Trusted) — Row 1: LLM Agent Orchestrator (Critical), MCP Tool Server (Critical), Guardrails Service (Critical); Row 2: Knowledge Base (Critical), Audit Logger (High)
  5. **TB-2**: Trust boundary dashed line "Application to External" with finding annotations S-5, D-3, R-5
  6. **FOOTER**: "Generated by Tachi Threat Modeling Framework — OWASP STRIDE + AI Threat Analysis"

### Typography

- **Title**: Bold, 28px, #111827
- **Subtitle**: Regular, 14px, #6B7280
- **Zone label**: Semibold, 18px, #374151
- **Zone trust level**: Regular italic, 14px, #6B7280
- **Component name**: Medium, 13px, #111827
- **Finding IDs**: Monospace, 11px, severity color
- **Badge text**: Bold, 11px, #FFFFFF on severity background
- **Flow label**: Regular, 10px, #6B7280
- **Trust boundary label**: Regular, 12px, #94A3B8
- **Footer**: Regular, 12px, #6B7280
