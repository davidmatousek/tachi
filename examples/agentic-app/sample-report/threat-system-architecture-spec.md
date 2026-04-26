---
schema_version: "1.0"
template: "system-architecture"
date: "2026-04-26"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
has_baseline: true
delta_note: "NEW finding AG-8 (Inter-Agent Communication Channel, OWASP ASI07:2026, raw Critical — residual High after controls)"
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-04-26 |
| Analysis Agents | 8 |
| Total Findings | 81 |
| Risk Posture | Residual risk — 0 Critical and 8 High findings across 11 components |
| Baseline | 2026-04-23 (F2-wave4) |
| Delta | NEW: AG-8 (Inter-Agent Communication Channel) — insecure inter-agent communication, OWASP ASI07:2026, raw Critical, residual High after compensating controls |

**Delta Context**: AG-8 is the sole new finding this wave. It targets the A2A trust fabric — the Inter-Agent Communication Channel connecting the Orchestrator, Specialist Agent, and Clinical Advisory Sub-Agent. The channel has no declared mTLS, no inter-agent message signing, and no nonce-based replay prevention. The Orchestrator relay does not propagate taint labels, enabling attacker-controlled content to reach Clinical Advisory Sub-Agent without an authentic-source signal.

---

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 8 | 10% | #EA580C |
| Medium | 68 | 84% | #EAB308 |
| Low | 5 | 6% | #4169E1 |
| **Total** | **81** | **100%** | — |

**Chart Format**: Horizontal bar chart or donut. Risk label: **Residual Risk Distribution**.

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 4 | 15 | 0 | 19 |
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
| LLM Agent Orchestrator | High | Medium | Medium | High | Medium | High | High | Medium |
| Clinical Advisory Sub-Agent | --- | Medium | Medium | Medium | Medium | --- | --- | Medium |
| Specialist Agent | --- | Medium | Medium | Medium | Medium | --- | --- | Medium |
| Long-Running Learning Loop | --- | Medium | Medium | Medium | Medium | --- | --- | Medium |
| Inter-Agent Communication Channel | --- | Medium | --- | Medium | Medium | --- | High | --- |
| MCP Tool Server | --- | High | Medium | Medium | --- | Medium | High | --- |
| Guardrails Service | --- | --- | --- | Medium | --- | High | --- | Medium |
| Other | --- | Medium | Medium | Medium | --- | High | --- | --- |

**Delta note**: Inter-Agent Communication Channel AG cell = High (AG-8, residual). Raw severity Critical; controls reduced residual to High.

---

## 4. Top Critical Findings

No Critical residual findings identified. Top High findings shown (residual risk, post-control):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials | High (score 8.2) |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions | High (score 7.8) |
| 3 | E-2 | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection | High (score 7.8) |
| 4 | E-1 | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller | High (score 7.7) |
| 5 | I-2 | LLM Agent Orchestrator | The Orchestrator's context window contains sensitive data exposed via inference side-channels | High (score 7.2) |

---

## 5. Architecture Threat Overlay

### Trust Zones

**User Zone** (untrusted):
- Components: User
- Highest residual severity: High (S-1)
- Border color: orange

**External Services** (semi-trusted):
- Components: External API
- Highest residual severity: none
- Border color: gray

**Application Zone** (trusted):
- Components: Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent
- Highest residual severity: High (AG-1, E-2, E-1, I-2 on LLM Agent Orchestrator; AG-8 [NEW] on Inter-Agent Communication Channel)

### Component Risk Weights

| Component | Risk Weight | Score | Annotation |
|-----------|-------------|-------|------------|
| LLM Agent Orchestrator | Medium | 2.2 | 4 High + 15 Medium findings |
| MCP Tool Server | Medium | 2.1 | 2 High + 5 Medium + 1 Low findings |
| Guardrails Service | Medium | 2.0 | 1 High + 3 Medium + 1 Low findings |
| Inter-Agent Communication Channel | Medium | 2.0 | 8 Medium findings (residual); AG-8 [NEW] raw Critical |
| Long-Running Learning Loop | Medium | 2.0 | 9 Medium findings |
| Other | Medium | 2.0 | 1 High + 8 Medium + 1 Low findings |
| Clinical Advisory Sub-Agent | Low | 1.9 | 11 Medium + 1 Low findings |
| Specialist Agent | Low | 1.9 | 9 Medium + 1 Low findings |

### Data Flows (with severity coloring)

| Source | Destination | Label | Severity Color |
|--------|-------------|-------|---------------|
| User | Guardrails Service | Prompt / Query | orange (High) |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | orange (High) |
| Guardrails Service | User | Rejected Prompt + Reason | gray |
| Guardrails Service | Audit Logger | Filtering Event Log | gray |
| LLM Agent Orchestrator | Clinical Advisory Sub-Agent | Clinical Query / Context | yellow (Medium) |
| LLM Agent Orchestrator | Inter-Agent Communication Channel | Delegation Message | yellow (Medium) |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval (Vector Search) | gray |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | orange (High) |
| LLM Agent Orchestrator | User | Response | gray |
| LLM Agent Orchestrator | Audit Logger | Decision Log Entry | gray |
| Inter-Agent Communication Channel | Specialist Agent | Delegated Task | yellow (Medium) |
| Inter-Agent Communication Channel | LLM Agent Orchestrator | Aggregated Result | orange (High) |
| Specialist Agent | Inter-Agent Communication Channel | Specialist Result | yellow (Medium) |
| Specialist Agent | MCP Tool Server | Tool Call Request | orange (High) |
| Specialist Agent | Audit Logger | Decision Log Entry | gray |
| MCP Tool Server | External API | API Request | gray |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | orange (High) |
| MCP Tool Server | Specialist Agent | Tool Result | yellow (Medium) |
| MCP Tool Server | Audit Logger | Tool Execution Log | gray |
| External API | MCP Tool Server | API Response | orange (High) |
| Clinical Advisory Sub-Agent | LLM Agent Orchestrator | Clinical Summary + Recommendations | orange (High) |
| Clinical Advisory Sub-Agent | Knowledge Base | Context Retrieval (Vector Search) | gray |
| Clinical Advisory Sub-Agent | Audit Logger | Clinical Decision Log Entry | gray |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | orange (High) |
| Knowledge Base | Clinical Advisory Sub-Agent | Retrieved Documents | yellow (Medium) |
| Long-Running Learning Loop | LLM Agent Orchestrator | Periodic Model Update | orange (High) |
| Long-Running Learning Loop | Clinical Advisory Sub-Agent | Periodic Model Update | yellow (Medium) |
| Long-Running Learning Loop | Specialist Agent | Periodic Model Update | yellow (Medium) |
| Audit Logger | Long-Running Learning Loop | Training Signal Stream | yellow (Medium) |

### Trust Boundary Crossings

| Crossing | From Zone | To Zone | Finding Count |
|----------|-----------|---------|---------------|
| User → Guardrails Service | User Zone | Application Zone | 0 (boundary crossing, findings on User component itself) |
| LLM Agent Orchestrator → User | Application Zone | User Zone | 0 |
| Guardrails Service → User | Application Zone | User Zone | 0 |
| MCP Tool Server → External API | Application Zone | External Services | 0 |
| External API → MCP Tool Server | External Services | Application Zone | 0 |

### Delta Emphasis: AG-8 [NEW]

Inter-Agent Communication Channel — AG-8 (OWASP ASI07:2026, AML.T0060):

- **What it means**: No mutual authentication (mTLS), no HMAC/Ed25519 message signing, no nonce-based replay window, no taint propagation across Orchestrator relay. A compromised process in the Application Zone can intercept and replay delegation messages to the Specialist Agent or inject attacker-controlled content into the Clinical Advisory Sub-Agent via the Orchestrator relay without detection.
- **Visual directive**: The Inter-Agent Communication Channel component box MUST display an orange dashed border (2pt) with a "[NEW]" badge in the upper-right corner. The delegation flows to/from this component (Orchestrator → Channel → Specialist Agent, and Channel → Orchestrator) are annotated with a small "AG-8" finding ID pill badge in orange.

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: component borders, data flow arrows |
| High | #EA580C | Orange-600: component borders, data flow arrows, finding badge fills |
| Medium | #CA8A04 | Yellow-600: component borders, data flow arrows |
| Low | #2563EB | Blue-600: component borders, data flow arrows |
| Note | #6B7280 | Gray-500: neutral flows, clean components |
| Clean cell | #F3F4F6 | Gray-100: components with no findings |
| Card bg | #F9FAFB | Gray-50: component box fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Trust Zone Tints

- User Zone (untrusted): soft warm red tint
- External Services (semi-trusted): neutral slate tint
- Application Zone (trusted): cool green tint

### Layout Structure

System Architecture spatial layout (16:9 landscape, white background):

- Three trust zones rendered as labeled bounding boxes with zone-specific background tints
- Components placed as rounded-rectangle boxes inside their zone, border color = highest residual severity
- Finding ID pills rendered as severity-colored badges on each component
- Data flow arrows: smooth curved arrows colored by highest residual severity on that path
- Finding legend (bottom right): groups by residual severity band
- Header label: "Residual Risk"

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Clean white (#FFFFFF) — polished card styling with subtle drop shadows. Dark text.
