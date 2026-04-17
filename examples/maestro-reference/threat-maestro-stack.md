---
schema_version: "1.0"
template: "maestro-stack"
date: "2026-04-16"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 112
image_generated: true
---

# Infographic Specification — MAESTRO Stack
## Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This specification is derived from the tachi canonical MAESTRO worked example. The underlying threat model analyzes a fictional Healthcare CDSS reference architecture for teaching purposes only — not a real clinical system. All 7 MAESTRO layers are populated, making this the most complete MAESTRO layer coverage example in the tachi pipeline.

> **Data Source Note**: MAESTRO layer distribution is sourced directly from threats.md Section 6 "Risk by MAESTRO Layer" (canonical qualitative severity from the threat model assessment). The compensating-controls.md Tier 1 source provides the residual severity context. Since all 108 findings have 0% control coverage, qualitative severity from threats.md equals the effective residual posture for all layer-level analysis.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Healthcare Clinical Decision Support System (CDSS) |
| Scan Date | 2026-04-16 |
| Analysis Agents | 8 (S, T, R, I, D, E, AG, LLM) |
| Total Findings | 112 (108 source from threats.md + 4 from scoring deduplication artifacts) |
| Risk Posture | Residual risk — 0 Critical and 6 High findings across 20 components; all 7 MAESTRO layers populated |
| Data Source | Tier 1 — compensating-controls.md + threats.md Section 6 (MAESTRO layer distribution) |
| Schema Version | 1.4 (finding.yaml — includes agentic_pattern field) |
| MAESTRO Coverage | Full — all 7 layers populated (L1-L7) |

---

## 2. Risk Distribution

**Chart Label**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 6 | 5% | #EA580C |
| Medium | 104 | 93% | #CA8A04 |
| Low | 2 | 2% | #2563EB |
| **Total** | **112** | **100%** | — |

**Qualitative source (threats.md Section 6 — for MAESTRO layer analysis)**:

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 16 | 14.8% |
| High | 52 | 48.1% |
| Medium | 30 | 27.8% |
| Low | 8 | 7.4% |
| Note | 2 | 1.9% |
| **Total** | **108** | **100%** |

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

No Critical residual findings. Top 5 by composite score (Residual Risk):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | Physician | Attacker replays or forges clinical query credentials to gain unauthorized access | High (8.4) |
| 2 | S-2 | Patient | Attacker submits fraudulent EHR update events by spoofing patient identity | High (7.4) |
| 3 | D-1 | Physician Clinical Portal | Attacker floods portal with clinical query requests causing service disruption | High (7.1) |
| 4 | E-1 | Physician Clinical Portal | Attacker escalates from low-privilege session to gain elevated portal access | High (7.0) |
| 5 | S-5 | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messages causing agents to act on forged commands | High (7.0) |

---

## 5. Architecture Threat Overlay

### MAESTRO Layer Distribution

Source: threats.md Section 6 "Risk by MAESTRO Layer". All 7 layers populated — complete MAESTRO coverage for this reference architecture.

| Layer | Name | Finding Count | Highest Severity | Top Findings |
|-------|------|---------------|------------------|--------------|
| L3 | Agent Framework | 30 | Critical | AG-1: Autonomous delegation bypasses human oversight (Critical); AG-2: Compromised orchestrator abuses delegation authority (Critical); S-6: Attacker impersonates Supervisor Orchestrator (Critical) |
| L7 | Agent Ecosystem | 22 | Critical | S-1: Physician credential replay (Critical); S-5: Supervisor delegation spoofing (Critical); T-3: Inter-agent message tampering (Critical) |
| L1 | Foundation Model | 18 | Critical | LLM-1: Prompt injection via API Gateway (Critical); T-11: RAG corpus poisoning (Critical); T-10: FHIR record tampering corrupting AI inputs (Critical) |
| L4 | Deployment Infrastructure | 11 | High | S-12: API Gateway spoofing (Medium); T-13: Gateway config tampering (Medium); D-13: Inference gateway request floods (Medium) |
| L6 | Security and Compliance | 12 | High | S-13: HIPAA RBAC engine spoofing (Medium); T-17: RBAC policy rule tampering (Medium); D-17: RBAC request flood (Medium) |
| L2 | Data Operations | 9 | Critical | T-10: FHIR record tampering (Critical); T-11: RAG corpus poisoning (Critical); I-10: Unauthorized FHIR PHI reads (Critical) |
| L5 | Evaluation and Observability | 6 | Critical | T-16: Outcomes telemetry tampering — learning loop corruption (Critical); T-15: Clinical Audit Log tampering (High) |

**Most Exposed Layer**: L3 — Agent Framework (30 findings, highest count; Critical findings include autonomous delegation and compromised orchestrator patterns)

**Layer Ordering for Stack Visual** (most exposed at top, most trusted at bottom):
- L7 Agent Ecosystem (22 findings, Critical) — position 1 in visual stack
- L3 Agent Framework (30 findings, Critical) — position 2
- L1 Foundation Model (18 findings, Critical) — position 3
- L2 Data Operations (9 findings, Critical) — position 4
- L5 Evaluation and Observability (6 findings, Critical) — position 5
- L6 Security and Compliance (12 findings, High) — position 6
- L4 Deployment Infrastructure (11 findings, High) — position 7

**Pedagogical Note**: This reference architecture is the most complete MAESTRO coverage example in the tachi pipeline — all 7 canonical CSA MAESTRO layers receive findings, and all 6 agentic patterns are represented. The L3 Agent Framework has the highest finding count (30), reflecting the multi-agent supervisor-specialist delegation architecture. The learning loop (L5 Evaluation and Observability) and the inter-agent communication channel (L7 Agent Ecosystem) surface MAESTRO-specific threats not present in traditional STRIDE-only models.

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: layer band border accent, finding badge background |
| High | #EA580C | Orange-600: layer band border accent |
| Medium | #CA8A04 | Yellow-600: layer band border accent |
| Low | #2563EB | Blue-600: layer band border accent |
| Note | #6B7280 | Gray-500: informational only |
| Clean cell | #F3F4F6 | Gray-100: empty layer bands |
| Card bg | #F9FAFB | Gray-50: sidebar card fill |
| Border | #E5E7EB | Gray-200: layer band borders |

### Layout Structure

- Background: Dark navy (#1E293B)
- Aspect Ratio: 16:9 landscape
- Style: Premium dark dashboard — Figma-quality
- 3-Zone Layout:
  1. TOP HEADER (~10%): Title "Healthcare CDSS — MAESTRO Layer Stack", date 2026-04-16, CONFIDENTIAL badge, subtitle "7 Layers Populated — Full MAESTRO Coverage — MAESTRO Canonical Worked Example"
  2. MAIN BODY (~80%): Left/Center: Horizontal layer bands stacked vertically (L7 at top through L1 at bottom per CSA MAESTRO ordering). Each band shows: layer label, finding count, highest severity bar, top 2-3 finding IDs as badges. Most-exposed layer (L3 — Agent Framework, 30 findings) has brighter background and wider left border accent. Empty layers: none (all 7 populated). Right sidebar: agentic patterns distribution + layer summary statistics
  3. FOOTER (~5%): "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis"

### Layer Band Visual Emphasis

| Layer | Finding Count | Highest Severity | Visual Emphasis |
|-------|---------------|------------------|-----------------|
| L3 — Agent Framework | 30 | Critical | Brightest band — widest left border, red/orange gradient |
| L7 — Agent Ecosystem | 22 | Critical | High emphasis — orange left border |
| L1 — Foundation Model | 18 | Critical | High emphasis — orange left border |
| L4 — Deployment Infrastructure | 11 | High | Moderate emphasis — amber left border |
| L6 — Security and Compliance | 12 | High | Moderate emphasis — amber left border |
| L2 — Data Operations | 9 | Critical | High emphasis — orange left border |
| L5 — Evaluation and Observability | 6 | Critical | High emphasis — orange left border |

### Typography

- Title: Bold, 28-32pt equivalent
- Layer Names: Semi-bold, 18-22pt equivalent
- Finding Badges: Bold, 10-12pt equivalent
- Sidebar Labels: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard. All text: white or light gray. Layer bands: horizontal bars with slightly lighter dark background + colored left border accent.

### Gemini Prompt

**PREAMBLE** (verbatim from JSON prompt_scaffold.preamble):
Create a premium, professional security risk dashboard with a polished, modern dark-theme aesthetic. This should look like a professionally designed Figma dashboard — not a data table or spreadsheet. The overall feel should be confident, sophisticated, and visually impressive — a formal security report artifact, not a presentation slide or boardroom scene. Render ONLY the dashboard itself as a flat document — no perspective, no 3D effects, no room or table context, no environmental background. The image should be the report, not a photo of the report.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical CSS specifications as visible text in the image. Only render the data labels, numbers, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: dark navy
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue
- All text on dark background: white or light gray
- Cards and bands: rounded corners, subtle drop shadows, generous whitespace
- Layout: 16:9 landscape, 3-zone (top header, main body split into stack + sidebar, footer)
- Layer bands: horizontal bars stacked vertically, L7 at top through L1 at bottom
- Most-exposed layer band: brighter background, wider left border accent
- Empty layer bands: muted, darker background, grayed text

DATA CONTENT (render this as visible text):

**DATA CONTENT**:

TOP HEADER: Title "Healthcare CDSS — CSA MAESTRO Layer Stack" with date "2026-04-16" and "CONFIDENTIAL" badge. Subtitle: "7 of 7 MAESTRO Layers Populated — Full Coverage — Teaching Reference Scenario."

LAYER STACK (7 horizontal bands, L7 at top, L1 at bottom):

Band 1 (top, L7 — Agent Ecosystem): "L7 — Agent Ecosystem: 22 findings — Highest: Critical. Top findings: S-1 (Physician, credential replay), S-5 (Inter-Agent Channel, delegation spoofing), T-3 (Inter-Agent Channel, message tampering). Agentic patterns: trust_exploitation, communication_vulnerability."

Band 2 (L3 — Agent Framework — MOST EXPOSED, brightest): "L3 — Agent Framework: 30 findings — Highest: Critical — MOST EXPOSED LAYER. Top findings: AG-1 (Supervisor, autonomous delegation bypass), AG-2 (Supervisor, orchestrator abuse), AG-7 (MCP Tool Server, tool chaining escalation). Agentic patterns: agent_collusion, emergent_behavior."

Band 3 (L1 — Foundation Model): "L1 — Foundation Model: 18 findings — Highest: Critical. Top findings: LLM-1 (Clinical LLM, prompt injection), T-11 (RAG Corpus, data poisoning), LLM-5 (Risk Model, fine-tuning poisoning). Agentic patterns: none (LLM-specific)."

Band 4 (L2 — Data Operations): "L2 — Data Operations: 9 findings — Highest: Critical. Top findings: T-10 (FHIR Store, record tampering), T-11 (RAG Corpus, embedding poisoning), I-10 (FHIR Store, PHI disclosure)."

Band 5 (L5 — Evaluation and Observability): "L5 — Evaluation and Observability: 6 findings — Highest: Critical. Top findings: T-16 (Outcomes Telemetry, learning loop tampering — temporal_attack pattern), T-15 (Audit Log tampering)."

Band 6 (L6 — Security and Compliance): "L6 — Security and Compliance: 12 findings — Highest: High. Top findings: S-13 (HIPAA RBAC, policy engine spoofing), T-17 (RBAC policy rule tampering), D-17 (RBAC request flood)."

Band 7 (bottom, L4 — Deployment Infrastructure): "L4 — Deployment Infrastructure: 11 findings — Highest: High. Top findings: S-12 (API Gateway spoofing), T-14 (EHR Ingestion Queue tampering), D-13 (inference gateway flood)."

RIGHT SIDEBAR:
"MAESTRO Layer Summary:
Total: 108 source findings
Layers populated: 7 of 7 (full coverage)
Most exposed: L3 — Agent Framework (30 findings)
Critical layers: L7, L3, L1, L2, L5 (5 layers)
High layers: L6, L4 (2 layers)

Agentic Patterns Detected (6 of 6):
trust_exploitation: 5 findings
agent_collusion: 4 findings
communication_vulnerability: 3 findings
temporal_attack: 2 findings
resource_competition: 2 findings
emergent_behavior: 1 finding

Cross-Layer Attack Chains:
3 chains identified (CHAIN-001: 5 layers, CHAIN-002: 4 layers, CHAIN-003: 4 layers)"

**POSTAMBLE** (verbatim from JSON prompt_scaffold.postamble):
FOOTER: "Generated by Tachi Threat Modeling Framework — CSA MAESTRO Layer Analysis" in small light gray text, centered.

The overall impression should be a polished professional report — confident, clear, and visually sophisticated. No hex codes, color values, or technical specifications should appear as visible text. Render the dashboard as a flat, full-bleed graphic filling the entire 16:9 frame. No perspective, no 3D, no boardroom, no table, no environmental context.
