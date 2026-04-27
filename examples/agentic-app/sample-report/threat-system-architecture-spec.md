---
schema_version: "1.4"
template: "system-architecture"
date: "2026-04-27"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 85
image_generated: true
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-04-27 |
| Analysis Agents | 8 |
| Total Findings | 85 |
| Risk Posture | Residual risk — 0 Critical and 10 High findings across 11 components |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 10 | 12% | #EA580C |
| Medium | 70 | 82% | #CA8A04 |
| Low | 5 | 6% | #2563EB |
| **Total** | **85** | **100%** | — |

**F-5 New Findings This Cycle**: D-10 (LLM Inference-Request Flooding), D-11 (Context-Window Latency Amplification), LLM-15 (Cost Amplification), LLM-16 (Denial-of-Wallet) — all introduced in Feature 229 Wave 2.

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 6 | 17 | 0 | 23 |
| Clinical Advisory Sub-Agent | 0 | 0 | 11 | 1 | 12 |
| Specialist Agent | 0 | 0 | 9 | 1 | 10 |
| Long-Running Learning Loop | 0 | 0 | 9 | 0 | 9 |
| Inter-Agent Communication Channel | 0 | 0 | 8 | 0 | 8 |
| MCP Tool Server | 0 | 2 | 5 | 1 | 8 |
| Guardrails Service | 0 | 1 | 3 | 1 | 5 |
| Other | 0 | 1 | 8 | 1 | 10 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|----|-----|
| LLM Agent Orchestrator | High | High | High | High | High | High | High | High |
| Clinical Advisory Sub-Agent | Medium | Medium | Medium | Medium | Medium | Medium | --- | Medium |
| Specialist Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | Medium |
| Long-Running Learning Loop | Medium | Medium | Medium | Medium | Medium | Medium | Medium | Medium |
| Inter-Agent Communication Channel | Medium | Medium | Low | Medium | Medium | Medium | Medium | --- |
| MCP Tool Server | High | High | Medium | Medium | High | High | High | --- |
| Guardrails Service | High | Medium | Medium | Medium | High | High | --- | --- |
| Other (User + Audit Logger) | High | Medium | Low | --- | --- | --- | --- | --- |

---

## 4. Top Critical Findings

**Risk Level Column**: Residual Risk

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials | High (8.2) |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions | High (7.8) |
| 3 | E-2 | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection | High (7.8) |
| 4 | E-1 | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller | High (7.7) |
| 5 | D-10 [NEW] | LLM Agent Orchestrator | LLM Inference-Request Flooding and Token Exhaustion without per-tenant QPS rate limiting | High (7.2) |

> **F-5 callout**: D-10 is a new finding introduced in Feature 229 Wave 2, covering OWASP LLM10:2025 Unbounded Consumption — inference-request flooding vector.

---

## 5. Architecture Threat Overlay

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Application Zone | Trusted | Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent |
| External Services | Semi-trusted | External API |
| User Zone | Untrusted | User |

### Component Risk Weights (Residual)

| Component | Risk Weight | Score | Annotation |
|-----------|-------------|-------|------------|
| LLM Agent Orchestrator | Medium | 2.3 | 6 High + 17 Medium residual; highest attack surface — prompt injection, DoS, privilege escalation, and agent autonomy; new F-5 D-10 + D-11 |
| MCP Tool Server | Medium | 2.1 | 2 High + 5 Medium + 1 Low residual; tool-call spoofing, inter-agent trust propagation |
| Guardrails Service | Medium | 2.0 | 1 High + 3 Medium + 1 Low residual; prompt injection bypass primary vector |
| Inter-Agent Communication Channel | Medium | 2.0 | 8 Medium residual; message integrity gaps |
| Long-Running Learning Loop | Medium | 2.0 | 9 Medium residual; training signal poisoning |
| Other | Medium | 2.0 | 1 High + 8 Medium + 1 Low; User (S-1 High) + Audit Logger |
| Clinical Advisory Sub-Agent | Low | 1.9 | 11 Medium + 1 Low residual |
| Specialist Agent | Low | 1.9 | 9 Medium + 1 Low residual |

### Data Flows (Severity-Colored Arrows)

| Source | Destination | Label | Severity Color |
|--------|-------------|-------|----------------|
| Audit Logger | Long-Running Learning Loop | Training Signal Stream | Medium (amber) |
| Clinical Advisory Sub-Agent | Audit Logger | Clinical Decision Log Entry | Neutral (gray) |
| Clinical Advisory Sub-Agent | Knowledge Base | Context Retrieval (Vector Search) | Neutral (gray) |
| Clinical Advisory Sub-Agent | LLM Agent Orchestrator | Clinical Summary + Recommendations | High (orange) |
| External API | MCP Tool Server | API Response | High (orange) |
| Guardrails Service | Audit Logger | Filtering Event Log | Neutral (gray) |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | High (orange) |
| Guardrails Service | User | Rejected Prompt + Reason | Neutral (gray) |
| Inter-Agent Communication Channel | LLM Agent Orchestrator | Aggregated Result | High (orange) |
| Inter-Agent Communication Channel | Specialist Agent | Delegated Task | Medium (amber) |
| Knowledge Base | Clinical Advisory Sub-Agent | Retrieved Documents | Medium (amber) |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | High (orange) |
| LLM Agent Orchestrator | Audit Logger | Decision Log Entry | Neutral (gray) |
| LLM Agent Orchestrator | Clinical Advisory Sub-Agent | Clinical Query / Context | Medium (amber) |
| LLM Agent Orchestrator | Inter-Agent Communication Channel | Delegation Message | Medium (amber) |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval (Vector Search) | Neutral (gray) |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | High (orange) |
| LLM Agent Orchestrator | User | Response | Neutral (gray) |
| Long-Running Learning Loop | Clinical Advisory Sub-Agent | Periodic Model Update | Medium (amber) |
| Long-Running Learning Loop | LLM Agent Orchestrator | Periodic Model Update | High (orange) |
| Long-Running Learning Loop | Specialist Agent | Periodic Model Update | Medium (amber) |
| MCP Tool Server | Audit Logger | Tool Execution Log | Neutral (gray) |
| MCP Tool Server | External API | API Request | Neutral (gray) |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | High (orange) |
| MCP Tool Server | Specialist Agent | Tool Result | Medium (amber) |
| Specialist Agent | Audit Logger | Decision Log Entry | Neutral (gray) |
| Specialist Agent | Inter-Agent Communication Channel | Specialist Result | Medium (amber) |
| Specialist Agent | MCP Tool Server | Tool Call Request | High (orange) |
| User | Guardrails Service | Prompt / Query | High (orange) |

### Trust Boundary Crossings

| Crossing Point | From Zone | To Zone | Finding Count |
|----------------|-----------|---------|---------------|
| User → Guardrails Service | User Zone | Application Zone | 0 (managed by Guardrails) |
| LLM Agent Orchestrator → User | Application Zone | User Zone | 0 |
| Guardrails Service → User | Application Zone | User Zone | 0 |
| MCP Tool Server → External API | Application Zone | External Services | 0 |
| External API → MCP Tool Server | External Services | Application Zone | 0 |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: component borders, finding badges, legend |
| High | #EA580C | Orange-600: component borders, data flow arrows, finding badges |
| Medium | #CA8A04 | Yellow-600: component borders, data flow arrows |
| Low | #2563EB | Blue-600: component borders |
| Note | #6B7280 | Gray-500: neutral data flows, clean component borders |
| Clean cell | #F3F4F6 | Gray-100: component background with no findings |
| Card bg | #F9FAFB | Gray-50: component box fill |
| Border | #E5E7EB | Gray-200: zone boundary lines |

### Layout Structure

```
- Background: clean white
- Aspect Ratio: 16:9 landscape
- Style: Polished architecture poster — professional security consultancy artifact
- Trust Zone Layout:
  - User Zone (top-left, soft red/warm tint): User component — orange border (High residual)
  - External Services (top-right, neutral slate tint): External API component — gray border
  - Application Zone (center, cool green tint): 9 components with severity-colored borders
    - LLM Agent Orchestrator: orange border (High — 6 findings)
    - MCP Tool Server: orange border (High — 2 findings)
    - Guardrails Service: orange border (High — 1 finding)
    - Inter-Agent Comm Channel: amber border (Medium)
    - Knowledge Base: amber border (Medium)
    - Long-Running Learning Loop: amber border (Medium)
    - Clinical Advisory Sub-Agent: amber border (Medium)
    - Specialist Agent: amber border (Medium)
    - Audit Logger: amber border (Medium)
- Data flow arrows: smooth curved, colored by highest residual severity on path
- Finding ID badges: pill-shaped, severity-colored background, white text
- Legend: bottom-right, severity color swatches + residual counts
- Header: "Residual Risk" label per risk label mapping
```

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Clean white — polished card styling with subtle drop shadows. Dark text throughout.
