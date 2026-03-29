---
schema_version: "1.0"
template: "system-architecture"
date: "2026-03-25"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 33
image_generated: true
---

# Threat Infographic Specification: System Architecture

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
| User | User Zone | 1 | 1 | #EA580C | S-1, R-1 | 2 High |
| LLM Agent Orchestrator | Application Zone | 1 | 1 | #DC2626 | S-3, T-2, R-2, I-1, D-1, E-1, AG-1, AG-2, LLM-1, LLM-2, LLM-3, LLM-4 | 13 Critical |
| MCP Tool Server | Application Zone | 1 | 2 | #DC2626 | S-4, T-3, R-4, I-2, D-2, E-2, E-4, AG-3, AG-4 | 7 Critical |
| Guardrails Service | Application Zone | 1 | 3 | #EA580C | S-2, T-1, R-3, I-5, D-4, E-3 | 5 High |
| Knowledge Base | Application Zone | 2 | 1 | #EA580C | T-4, T-6, I-3, D-3 | 3 High |
| Audit Logger | Application Zone | 2 | 2 | #EA580C | T-5, I-4, D-5 | 2 High |
| External API | External Services | 1 | 1 | #CA8A04 | S-5, R-5 | 2 Medium |

### Data Flows

| Source | Destination | Label | Arrow Color | Related Findings |
|--------|-------------|-------|-------------|-----------------|
| User | Guardrails Service | HTTPS | #EA580C | S-1, S-2 |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | #DC2626 | T-2, LLM-1 |
| Guardrails Service | User | Rejection | #CA8A04 | I-5 |
| LLM Agent Orchestrator | Knowledge Base | Vector Search | #EA580C | LLM-2, LLM-3, T-4 |
| Knowledge Base | LLM Agent Orchestrator | Documents | #EA580C | I-3, LLM-2 |
| LLM Agent Orchestrator | MCP Tool Server | JSON-RPC | #DC2626 | S-3, T-3, AG-1, AG-3 |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | #EA580C | I-2, AG-4 |
| MCP Tool Server | External API | HTTPS | #CA8A04 | S-5, R-5 |
| External API | MCP Tool Server | API Response | #EA580C | I-2 |
| LLM Agent Orchestrator | User | Response | #DC2626 | I-1, LLM-1 |
| LLM Agent Orchestrator | Audit Logger | Decision Log | #EA580C | R-2, T-5 |
| MCP Tool Server | Audit Logger | Tool Exec Log | #EA580C | R-4, T-5 |
| Guardrails Service | Audit Logger | Filtering Log | #CA8A04 | R-3 |

### Trust Boundary Crossings

| Boundary | Between Zones | Label | Finding IDs |
|----------|---------------|-------|-------------|
| TB-1 | User Zone -> Application Zone | User-to-Application | S-1, S-2, D-4, LLM-1 |
| TB-2 | Application Zone -> External Services | Application-to-External | S-5, R-5, I-2 |
| TB-3 | Application Zone -> User Zone | Application-to-User (Response) | I-1, LLM-1 |
| TB-4 | Application Zone -> User Zone | Application-to-User (Rejection) | I-5 |

### Finding Legend

ALL findings grouped by severity tier. Every finding ID on the diagram has an entry.

#### Critical

| Finding ID | Component | Short Description |
|------------|-----------|-------------------|
| S-3 | LLM Agent Orchestrator | Forged service identity impersonation via missing mTLS |
| D-1 | LLM Agent Orchestrator | Resource exhaustion from unbounded prompt requests |
| E-1 | LLM Agent Orchestrator | Privilege escalation via prompt-triggered admin operations |
| E-2 | MCP Tool Server | Unrestricted privileged tool execution without RBAC |
| AG-1 | LLM Agent Orchestrator | Unbounded agent loop without iteration or cost limits |
| AG-3 | MCP Tool Server | All tools exposed without per-user capability scoping |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection overrides system instructions |

#### High

| Finding ID | Component | Short Description |
|------------|-----------|-------------------|
| S-1 | User | Credential theft enables user impersonation |
| S-2 | Guardrails Service | Guardrails bypass via spoofed inter-service identity |
| S-4 | MCP Tool Server | Tool server identity spoofing intercepts requests |
| T-1 | Guardrails Service | Validation rule tampering weakens input screening |
| T-2 | LLM Agent Orchestrator | Prompt modified in transit without integrity protection |
| T-3 | MCP Tool Server | JSON-RPC message tampering alters tool parameters |
| T-4 | Knowledge Base | Document injection corrupts context retrieval |
| T-5 | Audit Logger | Log entry tampering conceals malicious activity |
| R-2 | LLM Agent Orchestrator | Incomplete decision chain logging prevents attribution |
| R-4 | MCP Tool Server | Tool execution lacks complete audit context |
| I-2 | MCP Tool Server | Sensitive API data forwarded unfiltered to orchestrator |
| I-3 | Knowledge Base | Full document metadata returned without field filtering |
| I-4 | Audit Logger | Sensitive data in logs exposed via unauthorized access |
| D-2 | MCP Tool Server | Excessive tool calls exhaust connection pool |
| D-4 | Guardrails Service | High-volume prompt flood blocks legitimate requests |
| AG-2 | LLM Agent Orchestrator | Consequential actions executed without human approval |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via poisoned KB documents |
| LLM-3 | LLM Agent Orchestrator | Data poisoning corrupts context retrieval pipeline |
| E-4 | MCP Tool Server | Lateral movement via overly broad network policies |

#### Medium

| Finding ID | Component | Short Description |
|------------|-----------|-------------------|
| S-5 | External API | DNS spoofing redirects API requests |
| T-6 | Knowledge Base | Adversarial content injection modifies embeddings |
| R-1 | User | User denies submitting consequential prompt |
| R-3 | Guardrails Service | Insufficient rejection logging for accountability |
| I-1 | LLM Agent Orchestrator | Verbose error messages expose internal state |
| I-5 | Guardrails Service | Rejection responses reveal validation rule details |
| D-3 | Knowledge Base | Expensive vector searches exhaust database resources |
| D-5 | Audit Logger | Log flooding exhausts storage capacity |
| E-3 | Guardrails Service | Admin endpoint exploitation modifies validation rules |
| AG-4 | MCP Tool Server | No tool call depth limit enables cascading invocations |
| LLM-4 | LLM Agent Orchestrator | Systematic querying extracts model behavior patterns |

#### Low

| Finding ID | Component | Short Description |
|------------|-----------|-------------------|
| R-5 | External API | External API actions not attributable to originating user |

## 6. Visual Design Directives

### Color Palette (Tailwind CSS — White Theme)

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
| Card shadow | rgba(0,0,0,0.1) | -- | Subtle drop shadow on component cards |
| Text primary | #111827 | Gray-900 | Component names, zone labels |
| Text secondary | #6B7280 | Gray-500 | Flow labels, legend |
| Arrow default | #374151 | Gray-700 | Data flow arrows without findings |
| CONFIDENTIAL badge | #DC2626 bg, #FFFFFF text | Red-600 | Header badge |
| Finding legend bg | #F9FAFB | Gray-50 | Legend panel background |
| Finding legend border | #E5E7EB | Gray-200 | Legend panel border |

### Layout Structure

- **Background**: White (#FFFFFF)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Premium, polished, consultancy-grade architecture poster. Sans-serif typography, Tailwind color palette.
- **Card Radius**: 8px rounded corners on all component boxes
- **Card Shadow**: 0 2px 8px rgba(0,0,0,0.1) subtle drop shadow
- **Spacing**: 16px minimum between components, 24px between zones
- **Layout Zones**:
  1. **HEADER**: Title "Agentic AI Application — Threat Model", subtitle "Architecture with attack surface annotations", date "2026-03-25", CONFIDENTIAL badge, "33 Findings Across 8 Threat Categories"
  2. **ARCHITECTURE DIAGRAM**: 3 trust zones stacked vertically (User Zone top, Application Zone middle, External Services bottom). Components placed inside their zones with severity-colored 3px solid borders. Data flow arrows between components colored by highest severity. Trust boundary dashed lines between zones labeled TB-1 through TB-4.
  3. **FINDING LEGEND**: Light gray panel (#F9FAFB) below architecture diagram. All 33 findings grouped by severity tier (Critical, High, Medium, Low) with colored left accent bars. 3 columns per tier, 10px text.
  4. **FOOTER**: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"

### Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Title | 28px | Bold | #111827 |
| Subtitle | 14px | Regular | #6B7280 |
| Zone label | 18px | Semibold | #374151 |
| Zone trust level | 14px | Regular italic | #6B7280 |
| Component name | 13px | Medium | #111827 |
| Finding IDs | 11px | Monospace | Severity color |
| Badge text | 11px | Bold | #FFFFFF on severity background |
| Flow label | 10px | Regular | #6B7280 |
| Trust boundary label | 12px | Regular | #94A3B8 |
| Legend text | 10px | Regular | #111827 |
| Footer | 12px | Regular | #6B7280 |

### Finding Legend Scaling

- Total findings: 33 (21-40 range)
- Columns per tier: 3
- Text size: 10px
- Description length: ~5-8 words
