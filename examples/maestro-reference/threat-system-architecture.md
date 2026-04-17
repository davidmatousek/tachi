---
schema_version: "1.0"
template: "system-architecture"
date: "2026-04-16"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 112
image_generated: true
---

# Infographic Specification — System Architecture
## Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This specification is derived from the tachi canonical MAESTRO worked example. The underlying threat model analyzes a fictional Healthcare CDSS reference architecture for teaching purposes only — not a real clinical system. Component names, trust zones, and data flows are from the reference architecture; finding counts reflect the tachi toolkit scan result (0% control coverage).

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Healthcare Clinical Decision Support System (CDSS) |
| Scan Date | 2026-04-16 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 112 |
| Risk Posture | Residual risk — 0 Critical and 6 High findings across 20 components |
| Data Source | Tier 1 — compensating-controls.md (residual severity = inherent; 0% coverage) |
| Schema Version | 1.4 |

---

## 2. Risk Distribution

**Chart Label**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 6 | 5% | #EA580C |
| High | 104 | 93% | #CA8A04 |
| Low | 2 | 2% | #2563EB |
| **Total** | **112** | **100%** | — |

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| Supervisor Orchestrator | 0 | 0 | 11 | 0 | 11 |
| Clinical LLM | 0 | 0 | 9 | 0 | 9 |
| Risk Stratification Model | 0 | 0 | 9 | 0 | 9 |
| Diagnostic Agent | 0 | 0 | 8 | 0 | 8 |
| Inter-Agent Communication Channel | 0 | 2 | 6 | 0 | 8 |
| Treatment Planner Agent | 0 | 0 | 8 | 0 | 8 |
| Clinical MCP Tool Server | 0 | 0 | 7 | 0 | 7 |
| Other | 0 | 4 | 46 | 2 | 52 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|----|-----|
| Supervisor Orchestrator | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Clinical LLM | Medium | Medium | Medium | Medium | Medium | Medium | — | Medium |
| Risk Stratification Model | Medium | Medium | Medium | Medium | Medium | Medium | — | Medium |
| Diagnostic Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Inter-Agent Communication Channel | High | High | Medium | Medium | Medium | Medium | Medium | — |
| Treatment Planner Agent | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Clinical MCP Tool Server | Medium | Medium | Medium | Medium | Medium | Medium | Medium | — |
| Other | High | High | Medium | High | Medium | High | Medium | — |

---

## 4. Top Critical Findings

No Critical residual findings. Top 5 by composite score (Residual Risk label per compensating-controls source):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | Physician | Attacker replays or forges clinical query credentials to gain unauthorized access | High (8.4) |
| 2 | S-2 | Patient | Attacker submits fraudulent EHR update events by spoofing patient identity | High (7.4) |
| 3 | D-1 | Physician Clinical Portal | Attacker floods portal with clinical query requests causing service disruption | High (7.1) |
| 4 | E-1 | Physician Clinical Portal | Attacker escalates from low-privilege session to gain elevated portal access | High (7.0) |
| 5 | S-5 | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messages causing agents to act on forged commands | High (7.0) |

---

## 5. Architecture Threat Overlay

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| External Zone | Untrusted | Patient, Physician |
| User Interface Zone (L7) | Semi-Trusted | Patient Summary Generator, Physician Clinical Portal |
| Agent Ecosystem Zone (L7) | Semi-Trusted | Inter-Agent Communication Channel |
| Security and Compliance Zone (L6) | Trusted | Consent and De-identification Guardrail, HIPAA RBAC + Policy Engine |
| Foundation Models Zone (L1) | Trusted | Clinical LLM, Risk Stratification Model |
| Evaluation and Observability Zone (L5) | Trusted | Clinical Audit Log, Outcomes Telemetry and Physician Override Audit Store |
| Deployment Infrastructure Zone (L4) | Trusted | EHR Ingestion Queue, Model Inference API Gateway |
| Data Operations Zone (L2) | Trusted | Clinical Guideline RAG Corpus, FHIR Resource Store, Medical Literature Vector Index |
| Agent Frameworks Zone (L3) | Trusted | Clinical MCP Tool Server, Diagnostic Agent, Supervisor Orchestrator, Treatment Planner Agent |

### Component Badges (Residual Severity)

| Component | Residual Severity | Finding Count | Badge Color |
|-----------|-------------------|---------------|-------------|
| Physician | High (8.4) | 2 | Orange border |
| Patient | High (7.4) | 2 | Orange border |
| Physician Clinical Portal | High (7.1) | 6 | Orange border |
| Inter-Agent Communication Channel | High (7.0) | 8 | Orange border |
| Patient Summary Generator | Medium | 6 | Amber border |
| Supervisor Orchestrator | Medium | 11 | Amber border |
| Diagnostic Agent | Medium | 8 | Amber border |
| Treatment Planner Agent | Medium | 8 | Amber border |
| Clinical MCP Tool Server | Medium | 7 | Amber border |
| Clinical LLM | Medium | 9 | Amber border |
| Risk Stratification Model | Medium | 9 | Amber border |
| FHIR Resource Store | Medium | 3 | Amber border |
| Clinical Guideline RAG Corpus | Medium | 3 | Amber border |
| Medical Literature Vector Index | Medium | 3 | Amber border |
| Model Inference API Gateway | Medium | 6 | Amber border |
| EHR Ingestion Queue | Medium | 3 | Amber border |
| Clinical Audit Log | Medium | 4 | Amber border |
| Outcomes Telemetry and Physician Override Audit Store | Medium | 2 | Amber border |
| HIPAA RBAC + Policy Engine | Medium | 6 | Amber border |
| Consent and De-identification Guardrail | Medium | 2 | Amber border |

### Data Flow Annotations (Key Paths — Highest Residual Severity)

| Source | Destination | Label | Severity | Arrow Color |
|--------|-------------|-------|----------|-------------|
| Supervisor Orchestrator | Inter-Agent Communication Channel | Delegation message (cross-agent coordinate) | High | Orange |
| Diagnostic Agent | Inter-Agent Communication Channel | Specialist diagnostic result (joint reasoning) | High | Orange |
| Treatment Planner Agent | Inter-Agent Communication Channel | Treatment plan (joint reasoning) | High | Orange |
| Physician Clinical Portal | Supervisor Orchestrator | Authenticated clinical intent | Medium | Amber |
| Diagnostic Agent | Clinical MCP Tool Server | Tool call (JSON-RPC) | Medium | Amber |
| Treatment Planner Agent | Clinical MCP Tool Server | Tool call (JSON-RPC) | Medium | Amber |
| Clinical Guideline RAG Corpus | Diagnostic Agent | Retrieved guidelines | Medium | Amber |
| Medical Literature Vector Index | Treatment Planner Agent | Retrieved literature | Medium | Amber |
| Model Inference API Gateway | Clinical LLM | Inference request forwarded | Medium | Amber |
| Model Inference API Gateway | Risk Stratification Model | Risk inference request | Medium | Amber |
| Outcomes Telemetry and Physician Override Audit Store | Clinical LLM | Periodic model update (feedback loop drift correction) | Medium | Amber |

### Trust Boundary Crossings

| Crossing | From Zone | To Zone | Finding Count | Annotation |
|----------|-----------|---------|---------------|------------|
| Inter-Agent Communication Channel → Diagnostic Agent, Treatment Planner Agent | Agent Ecosystem Zone | Agent Frameworks Zone | 8 | Highest-finding boundary; trust_exploitation and communication_vulnerability agentic patterns active |
| Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent → Clinical Audit Log | Agent Frameworks Zone | Evaluation and Observability Zone | 19 | High finding count at logging boundary; temporal_attack pattern (T-16) active at Outcomes Telemetry |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: component box borders, finding pill badges, zone tints |
| High | #EA580C | Orange-600: component box borders, data flow arrows, finding badges |
| Medium | #CA8A04 | Yellow-600: component box borders, data flow arrows |
| Low | #2563EB | Blue-600: component box borders |
| Note | #6B7280 | Gray-500: informational flows, neutral zone tints |
| Clean cell | #F3F4F6 | Gray-100: no-findings components |
| Card bg | #F9FAFB | Gray-50: component box fill |
| Border | #E5E7EB | Gray-200: zone boundary lines |

### Trust Zone Tints

| Zone | Tint | Rationale |
|------|------|-----------|
| External Zone | Soft warm red | Untrusted — highest exposure |
| User Interface Zone, Agent Ecosystem Zone | Neutral slate | Semi-trusted — boundary layer |
| All Trusted Zones | Cool green | Trusted internal components |

### Layout Structure

- Background: Clean white (#FFFFFF)
- Aspect Ratio: 16:9 landscape
- Style: Architecture poster from a top-tier security consultancy — Figma/Miro quality
- Layout: Trust zones as labeled region boxes; components as rounded-corner cards inside zones; data flow arrows as smooth curved lines; finding ID pills overlaid on component cards; legend panel at right side
- Component cards: rounded corners, subtle drop shadow, white fill, full colored border by residual severity
- Finding ID badges: severity-colored pill background, white text
- Trust zone labels: large, semi-bold, positioned at zone header

### Typography

- Title: Bold, 28-32pt equivalent
- Trust Zone Labels: Semi-bold, 18-22pt equivalent
- Component Names: Regular, 12-14pt equivalent
- Finding ID Badges: Bold, 10-12pt equivalent

### Background

Clean white (#FFFFFF) — polished architecture diagram aesthetic. Dark text on white background. Zone regions use subtle tinted fills (not solid).

### Gemini Prompt

**PREAMBLE** (verbatim from JSON prompt_scaffold.preamble):
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

**DATA CONTENT**:

HEADER: Title "Healthcare CDSS — System Architecture Threat Map" with date "2026-04-16" and "CONFIDENTIAL" badge. Subtitle: "Residual Risk View — Teaching Reference Scenario — 112 Findings."

ARCHITECTURE ZONES (render as labeled region boxes with tinted backgrounds):

Zone 1 — "External Zone" (untrusted, red tint): Components: Physician (orange border, finding badge "S-1 High"), Patient (orange border, finding badge "S-2 High").

Zone 2 — "User Interface Zone (L7)" (semi-trusted, slate tint): Components: Physician Clinical Portal (orange border, badges "D-1 High" "E-1 High"), Patient Summary Generator (amber border, 6 findings).

Zone 3 — "Agent Ecosystem Zone (L7)" (semi-trusted, slate tint): Component: Inter-Agent Communication Channel (orange border, badges "S-5 High" "T-3 High" — highest-risk internal component).

Zone 4 — "Agent Frameworks Zone (L3)" (trusted, green tint): Components: Supervisor Orchestrator (amber border, 11 findings), Diagnostic Agent (amber border, 8 findings), Treatment Planner Agent (amber border, 8 findings), Clinical MCP Tool Server (amber border, 7 findings).

Zone 5 — "Foundation Models Zone (L1)" (trusted, green tint): Components: Clinical LLM (amber border, 9 findings), Risk Stratification Model (amber border, 9 findings).

Zone 6 — "Data Operations Zone (L2)" (trusted, green tint): Components: FHIR Resource Store (amber border, 3 findings), Clinical Guideline RAG Corpus (amber border, 3 findings), Medical Literature Vector Index (amber border, 3 findings).

Zone 7 — "Deployment Infrastructure Zone (L4)" (trusted, green tint): Components: Model Inference API Gateway (amber border, 6 findings), EHR Ingestion Queue (amber border, 3 findings).

Zone 8 — "Evaluation and Observability Zone (L5)" (trusted, green tint): Components: Clinical Audit Log (amber border, 4 findings), Outcomes Telemetry and Physician Override Audit Store (amber border, 2 findings).

Zone 9 — "Security and Compliance Zone (L6)" (trusted, green tint): Components: HIPAA RBAC + Policy Engine (amber border, 6 findings), Consent and De-identification Guardrail (amber border, 2 findings).

KEY DATA FLOWS (draw as arrows colored by severity):
- Supervisor Orchestrator → Inter-Agent Communication Channel: orange arrow (High — delegation spoofing risk)
- Diagnostic Agent → Inter-Agent Communication Channel: orange arrow (High — result injection risk)
- Treatment Planner Agent → Inter-Agent Communication Channel: orange arrow (High — treatment plan injection risk)
- Physician Clinical Portal → Supervisor Orchestrator: amber arrow (Medium)
- Diagnostic Agent → Clinical MCP Tool Server: amber arrow (Medium — tool abuse risk)
- Treatment Planner Agent → Clinical MCP Tool Server: amber arrow (Medium — tool abuse risk)
- Model Inference API Gateway → Clinical LLM: amber arrow (Medium — prompt injection path)
- Outcomes Telemetry → Clinical LLM: amber arrow (Medium — learning loop drift risk)

FINDING LEGEND (right side panel): "Total: 112 findings — 0 Critical / 6 High / 104 Medium / 2 Low. Risk Reduction: 0.0% (reference scenario — no controls in target codebase). Highest-risk boundary: Agent Ecosystem → Agent Frameworks (8 findings, trust_exploitation pattern). Agentic patterns: trust_exploitation, agent_collusion, communication_vulnerability, temporal_attack, resource_competition, emergent_behavior."

**POSTAMBLE** (verbatim from JSON prompt_scaffold.postamble):
FOOTER: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis" in small gray text, centered.

The overall impression should be a polished, authoritative architecture diagram with a complete reference legend — the kind you'd see in a professional security audit deliverable. Prioritize readability — component names, finding IDs, and legend entries must be legible. No hex codes, color values, or technical specifications should appear as visible text. Every element should feel intentionally designed.
