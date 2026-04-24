---
schema_version: "1.0"
template: "system-architecture"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
---

# Threat Infographic Specification — System Architecture
## Project: Agentic AI Application

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2023-11-14 |
| Analysis Agents | 8 |
| Total Findings | 81 |
| Risk Posture | Residual risk — 0 Critical and 17 High findings across 11 components |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 17 | 21% | #EA580C |
| Medium | 62 | 77% | #CA8A04 |
| Low | 2 | 2% | #2563EB |
| **Total** | **81** | **100%** | — |

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| LLM Agent Orchestrator | 0 | 11 | 7 | 0 | 18 |
| Clinical Advisory Sub-Agent | 0 | 1 | 11 | 0 | 12 |
| Specialist Agent | 0 | 1 | 9 | 0 | 10 |
| Long-Running Learning Loop | 0 | 0 | 9 | 0 | 9 |
| MCP Tool Server | 0 | 2 | 6 | 0 | 8 |
| Inter-Agent Communication Channel | 0 | 0 | 7 | 0 | 7 |
| Guardrails Service | 0 | 1 | 5 | 0 | 6 |
| Other | 0 | 1 | 8 | 2 | 11 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|-----|-----|
| LLM Agent Orchestrator | High | High | High | High | High | High | High | High |
| Clinical Advisory Sub-Agent | High | High | High | High | Medium | Medium | — | High |
| Specialist Agent | Medium | High | Medium | Medium | Medium | Medium | High | — |
| Long-Running Learning Loop | High | High | Medium | Medium | Medium | High | High | — |
| MCP Tool Server | High | High | Medium | Medium | High | High | High | — |
| Inter-Agent Communication Channel | Medium | High | Low | High | Medium | High | High | — |
| Guardrails Service | Medium | Medium | Medium | Medium | High | High | — | — |
| Other | High | Medium | Low | Medium | Low | — | — | — |

---

## 4. Top Critical Findings

No Critical residual-severity findings identified. Top High-residual findings shown (by residual score descending):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | User | Attacker replays stolen session tokens to impersonate a legitimate user | High |
| 2 | AG-1 | LLM Agent Orchestrator | Prompt injection causes autonomous execution of unauthorized high-impact actions | High |
| 3 | E-2 | LLM Agent Orchestrator | Orchestrator self-authorizes elevated operations across tools and sub-agents | High |
| 4 | R-3 | LLM Agent Orchestrator | Orchestrator denies issuing delegation messages or tool calls | High |
| 5 | E-1 | Guardrails Service | Prompt injection bypasses Guardrails and elevates attacker to Orchestrator trust level | High |

---

## 5. Architecture Threat Overlay

### Trust Zones (Spatial Layout)

**Zone 1 — User Zone** (untrusted, warm red tint)
- Components: User
- Highest residual severity: High (S-1 residual score 8.2)
- Border color: orange (High)

**Zone 2 — External Services** (semi-trusted, neutral tint)
- Components: External API
- Highest residual severity: Low (R-8)
- Border color: blue (Low)

**Zone 3 — Application Zone** (trusted, cool green tint)
- Components: Guardrails Service, LLM Agent Orchestrator, Inter-Agent Communication Channel, Specialist Agent, MCP Tool Server, Knowledge Base, Audit Logger, Long-Running Learning Loop, Clinical Advisory Sub-Agent
- Highest residual severity: High (multiple)
- Border color: orange (High)

### Component Risk Badges (Residual Severity)

| Component | Badge Color | Finding Count | Badge Label |
|-----------|------------|---------------|-------------|
| LLM Agent Orchestrator | Orange (High) | 18 | 18 findings |
| Clinical Advisory Sub-Agent | Orange (High) | 12 | 12 findings |
| Specialist Agent | Orange (High) | 10 | 10 findings |
| Long-Running Learning Loop | Amber (Medium) | 9 | 9 findings |
| MCP Tool Server | Orange (High) | 8 | 8 findings |
| Inter-Agent Communication Channel | Amber (Medium) | 7 | 7 findings |
| Guardrails Service | Orange (High) | 6 | 6 findings |
| Knowledge Base | Amber (Medium) | 3 | 3 findings |
| Audit Logger | Amber (Medium) | 3 | 3 findings |
| User | Orange (High) | 3 | 3 findings |
| External API | Blue (Low) | 2 | 2 findings |

### Data Flows (Severity Colored)

| Source | Destination | Flow Label | Arrow Color |
|--------|-------------|-----------|-------------|
| User | Guardrails Service | Prompt / Query | Orange (High) |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | Orange (High) |
| Guardrails Service | User | Rejected Prompt + Reason | Gray (clean) |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval (Vector Search) | Gray (clean) |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | Orange (High) |
| LLM Agent Orchestrator | Inter-Agent Communication Channel | Delegation Message | Amber (Medium) |
| Inter-Agent Communication Channel | Specialist Agent | Delegated Task | Orange (High) |
| Specialist Agent | Inter-Agent Communication Channel | Specialist Result | Amber (Medium) |
| Inter-Agent Communication Channel | LLM Agent Orchestrator | Aggregated Result | Orange (High) |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | Orange (High) |
| Specialist Agent | MCP Tool Server | Tool Call Request | Orange (High) |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | Orange (High) |
| MCP Tool Server | Specialist Agent | Tool Result | Orange (High) |
| MCP Tool Server | External API | API Request | Gray (clean) |
| External API | MCP Tool Server | API Response | Orange (High) |
| LLM Agent Orchestrator | User | Response | Gray (clean) |
| LLM Agent Orchestrator | Audit Logger | Decision Log Entry | Gray (clean) |
| Specialist Agent | Audit Logger | Decision Log Entry | Gray (clean) |
| MCP Tool Server | Audit Logger | Tool Execution Log | Gray (clean) |
| Guardrails Service | Audit Logger | Filtering Event Log | Gray (clean) |
| Audit Logger | Long-Running Learning Loop | Training Signal Stream | Amber (Medium) |
| Long-Running Learning Loop | LLM Agent Orchestrator | Periodic Model Update | Orange (High) |
| Long-Running Learning Loop | Specialist Agent | Periodic Model Update | Orange (High) |
| Long-Running Learning Loop | Clinical Advisory Sub-Agent | Periodic Model Update | Orange (High) |
| LLM Agent Orchestrator | Clinical Advisory Sub-Agent | Clinical Query / Context | Orange (High) |
| Clinical Advisory Sub-Agent | Knowledge Base | Context Retrieval (Vector Search) | Gray (clean) |
| Knowledge Base | Clinical Advisory Sub-Agent | Retrieved Documents | Orange (High) |
| Clinical Advisory Sub-Agent | LLM Agent Orchestrator | Clinical Summary + Recommendations | Orange (High) |
| Clinical Advisory Sub-Agent | Audit Logger | Clinical Decision Log Entry | Gray (clean) |

### Trust Boundary Crossings

| Boundary | From Zone | To Zone | Finding Count | Notes |
|----------|-----------|---------|---------------|-------|
| User → Guardrails Service | User Zone | Application Zone | 0 direct boundary findings | Highest-risk entry point (S-1 at boundary) |
| Guardrails Service → User | Application Zone | User Zone | 0 direct boundary findings | Rejection path |
| LLM Agent Orchestrator → User | Application Zone | User Zone | 0 direct boundary findings | Response path |
| MCP Tool Server → External API | Application Zone | External Services | 0 direct boundary findings | Outbound API call |
| External API → MCP Tool Server | External Services | Application Zone | 0 direct boundary findings | API response return |

### Finding Legend (Residual Severity Bands)

**High Residual (17 findings)**: S-1, AG-1, E-2, R-3, E-1, LLM-6, OI-2, LLM-5, OI-1, LLM-13, LLM-8, I-2, LLM-1, LLM-4, T-2, E-5, T-5

**Medium Residual (62 findings)**: All remaining findings including AG-5, E-7, I-9, LLM-2, D-1, LLM-7, LLM-14, MI-2, and 54 additional Medium-band findings

**Low Residual (2 findings)**: R-5, R-8

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: component box borders, finding ID pill badges, data flow arrows |
| High | #EA580C | Orange-600: component box borders, finding ID pill badges, data flow arrows |
| Medium | #CA8A04 | Yellow-600: component box borders, finding ID pill badges, data flow arrows |
| Low | #2563EB | Blue-600: component box borders, finding ID pill badges, data flow arrows |
| Clean | #10B981 | Emerald: components with no findings — clean state |
| Note | #6B7280 | Gray-500: data flows with no associated findings |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- Background: Clean white (#FFFFFF)
- Aspect Ratio: 16:9 landscape
- Style: Professional architecture poster — Figma/Miro aesthetic, clean and authoritative
- Trust zones as labeled rectangular regions with tinted fills:
  - User Zone: soft warm red tint (untrusted)
  - External Services: neutral slate tint (semi-trusted)
  - Application Zone: cool green tint (trusted internal)
- Component boxes: rounded corners, subtle drop shadow, white fill, colored border matching highest residual severity
- Finding ID pills: severity-colored background, white monospace text, overlaid on or beside component boxes
- Data flow arrows: smooth curved arrows, colored by highest residual severity on path
- Reference legend: bottom-right corner, severity color swatches with labels

### Typography

- Title: Bold, 28-32pt equivalent
- Zone Labels: Semi-bold, 18-22pt equivalent
- Component Names: Bold, 14-16pt equivalent
- Flow Labels: Regular, 11-12pt equivalent
- Finding IDs: Monospace bold, 11pt, white on colored pill

### Background

Clean white. Trust zones use subtle color tints (not solid fills). Arrows and borders provide the severity color signal.

---

## 7. Gemini Prompt

Create a premium, professionally designed system architecture diagram showing security threat analysis findings. This should look like an architecture poster from a top-tier security consultancy — clean, authoritative, and visually sophisticated. The feel should be modern and polished, like a Figma or Miro design artifact.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical CSS specifications as visible text in the image. Only render the data labels, component names, finding IDs, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: clean white
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue, Clean = emerald green
- Trust zone tints: untrusted = soft warm red tint, application = neutral slate tint, trusted = cool green tint
- Component boxes: rounded corners, subtle drop shadow, white fill, full colored border matching highest severity
- Finding IDs: rendered as individual pill badges with severity-colored background and white text
- Data flow arrows: smooth curved arrows, colored by highest severity on that path
- Layout: 16:9 landscape, professional spacing between components

DATA CONTENT (render this as visible text):

TOP SECTION: Title "System Architecture — Threat Analysis: Agentic AI Application" with date "2023-11-14" and "CONFIDENTIAL" badge. Subtitle: "Residual Risk Map — 81 Findings, 11 Components".

TRUST ZONES (labeled rectangular regions, left-to-right or nested):

Zone 1 — "User Zone" (untrusted, warm red tint): Contains: User (orange border, finding count badge "3"). Primary finding: S-1 pill badge (orange).

Zone 2 — "External Services" (semi-trusted, slate tint): Contains: External API (blue border, finding count badge "2").

Zone 3 — "Application Zone" (trusted, cool green tint): Contains 9 components:
- LLM Agent Orchestrator (orange border, badge "18") — finding pills: AG-1, E-2, R-3, LLM-1, LLM-4 (top 5 shown)
- Guardrails Service (orange border, badge "6") — finding pill: E-1
- Inter-Agent Communication Channel (amber border, badge "7")
- Specialist Agent (orange border, badge "10")
- MCP Tool Server (orange border, badge "8") — finding pill: E-5, T-5
- Knowledge Base (amber border, badge "3")
- Audit Logger (amber border, badge "3")
- Long-Running Learning Loop (amber border, badge "9")
- Clinical Advisory Sub-Agent (orange border, badge "12") — finding pill: LLM-13, I-9

DATA FLOW ARROWS (colored by highest residual severity on path):
Orange arrows (High residual): User→Guardrails, Guardrails→Orchestrator, KB→Orchestrator, Channel→Specialist, Channel→Orchestrator, Orchestrator→MCP, Specialist→MCP, MCP→Orchestrator, MCP→Specialist, ExternalAPI→MCP, LearningLoop→Orchestrator, LearningLoop→Specialist, LearningLoop→ClinAdvisor, Orchestrator→ClinAdvisor, KB→ClinAdvisor, ClinAdvisor→Orchestrator
Amber arrows (Medium residual): Orchestrator→Channel, Specialist→Channel, AuditLogger→LearningLoop
Gray arrows (clean/informational): Guardrails→User, Orchestrator→KB, Orchestrator→AuditLogger, Specialist→AuditLogger, MCP→AuditLogger, Guardrails→AuditLogger, Orchestrator→User, MCP→ExternalAPI, ClinAdvisor→KB, ClinAdvisor→AuditLogger

FINDING LEGEND (bottom-right panel, compact):
Orange pill = High Residual (17 findings): S-1, AG-1, E-1, E-2, R-3, LLM-6, LLM-5, OI-1, OI-2, LLM-13, LLM-8, I-2, LLM-1, LLM-4, T-2, E-5, T-5
Amber pill = Medium Residual (62 findings)
Blue pill = Low Residual (2 findings): R-5, R-8

FOOTER: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis" in small gray text, centered.

The overall impression should be a polished, authoritative architecture diagram with a complete reference legend — the kind you'd see in a professional security audit deliverable. Prioritize readability — component names, finding IDs, and legend entries must be legible. No hex codes, color values, or technical specifications should appear as visible text. Every element should feel intentionally designed.
