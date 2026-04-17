---
schema_version: "1.0"
template: "executive-architecture"
date: "2026-04-16"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 112
image_generated: true
skip_image: false
---

# Infographic Specification — Executive Architecture
## Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This specification is derived from the tachi canonical MAESTRO worked example. The underlying threat model analyzes a fictional Healthcare CDSS reference architecture for teaching purposes only — not a real clinical system. No Critical findings exist in the residual risk profile; 6 High findings are present across the External and User Interface/Agent Ecosystem zones.

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Template Name | executive-architecture |
| Tier Source | compensating-controls |
| Source File | examples/maestro-reference/threats.md |
| Generation Timestamp | 2026-04-17T04:22:00Z |
| Qualifying Layer Count | 9 |
| Total Filtered Count | 6 (High-severity findings selected for callouts) |
| Skip Image | false (6 High findings qualify; image generation proceeds) |
| Fallback Used | false |
| Schema Version | 1.4 |

---

## 2. Architecture Layers

Layers ordered with most-exposed (untrusted/lowest-trust) at position 0 (top), most trusted at position 8 (bottom). Portrait orientation — designed for embedding as a full-bleed page in the security report PDF.

| Position | Layer Name | Components | Component Count | Source Kind |
|----------|------------|------------|-----------------|-------------|
| 0 | External Zone | Patient, Physician | 2 | trust_zone |
| 1 | User Interface Zone (L7) | Patient Summary Generator, Physician Clinical Portal | 2 | trust_zone |
| 2 | Agent Ecosystem Zone (L7) | Inter-Agent Communication Channel | 1 | trust_zone |
| 3 | Security and Compliance Zone (L6) | Consent and De-identification Guardrail, HIPAA RBAC + Policy Engine | 2 | trust_zone |
| 4 | Foundation Models Zone (L1) | Clinical LLM, Risk Stratification Model | 2 | trust_zone |
| 5 | Evaluation and Observability Zone (L5) | Clinical Audit Log, Outcomes Telemetry and Physician Override Audit Store | 2 | trust_zone |
| 6 | Deployment Infrastructure Zone (L4) | EHR Ingestion Queue, Model Inference API Gateway | 2 | trust_zone |
| 7 | Data Operations Zone (L2) | Clinical Guideline RAG Corpus, FHIR Resource Store, Medical Literature Vector Index | 3 | trust_zone |
| 8 | Agent Frameworks Zone (L3) | Clinical MCP Tool Server, Diagnostic Agent, Supervisor Orchestrator, Treatment Planner Agent | 4 | trust_zone |

---

## 3. Threat Callouts

One callout per layer selected at the highest residual composite score. Only 3 layers have High-severity qualifying findings (External Zone, User Interface Zone, Agent Ecosystem Zone). Remaining 6 layers have Medium-severity findings only — shown in note below.

| Layer Name | Finding ID | Severity | Raw Description | Composite Score | Affected Component |
|------------|------------|----------|-----------------|-----------------|--------------------|
| External Zone | S-1 | High | Attacker replays or forges clinical query credentials | 8.4 | Physician |
| User Interface Zone (L7) | D-1 | High | Attacker floods portal with clinical query requests | 7.1 | Physician Clinical Portal |
| Agent Ecosystem Zone (L7) | S-5 | High | Attacker spoofs supervisor delegation messages | 7.0 | Inter-Agent Communication Channel |

**Plain-English Callout Text** (rewritten to ≤25 words for executive audience):

- **S-1 / Physician**: An attacker could steal a doctor's login credentials and access confidential patient data without authorization. (18 words)
- **D-1 / Physician Clinical Portal**: An attacker could overwhelm the doctor portal with fake requests, making it unavailable to real physicians. (16 words)
- **S-5 / Inter-Agent Communication Channel**: An attacker could send fake coordination commands to AI agents, causing them to act on forged instructions. (17 words)

**Layers with Medium-only findings** (no callout box rendered; layer band appears but no red dashed border):
- Security and Compliance Zone (L6): highest finding is Medium
- Foundation Models Zone (L1): highest finding is Medium (prompt injection LLM-1 scores Medium after reachability penalties)
- Evaluation and Observability Zone (L5): highest finding is Medium (temporal_attack T-16 scores Medium)
- Deployment Infrastructure Zone (L4): highest finding is Medium
- Data Operations Zone (L2): highest finding is Medium
- Agent Frameworks Zone (L3): highest finding is Medium (agent_collusion AG-1/AG-2 score Medium after reachability penalties)

---

## 4. Severity Distribution

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 6 |

**Note**: Medium (104) and Low (2) findings are not shown in this executive template. The 6 High findings are concentrated on the three most-exposed layers (External Zone, User Interface Zone, Agent Ecosystem Zone). All internal Trusted-zone components have Medium-only residual findings due to reachability penalties in the composite scoring model.

**Pedagogical note for adopters**: In a production clinical system (as opposed to the tachi toolkit target), internal components would have compensating controls, and High/Critical findings at layers L3-L7 would be likely — the architecture itself has Critical-severity qualitative threats. This reference scenario illustrates the structural shape of an executive architecture infographic; adopters should apply the pipeline against their own target codebase to obtain meaningful callout distribution.

---

## 5. Visual Layout Directives

| Directive | Value |
|-----------|-------|
| Orientation | Portrait (8.5×11 aspect ratio) |
| Layer ordering | Untrusted (position 0) at TOP; most trusted (position 8) at BOTTOM |
| Layer band fills | Pastel, cycling palette: #F0F4FF (External), #FFF4F0 (User Interface), #F0FFF4 (Agent Ecosystem), #FFF0F8 (Security/Compliance), #F8F0FF (Foundation Models), then cycle: #F0F4FF (Evaluation/Observability), #FFF4F0 (Deployment Infrastructure), #F0FFF4 (Data Operations), #FFF0F8 (Agent Frameworks) |
| Callout borders | Red dashed border, 2pt, color #DC2626 |
| Callout icon | Warning triangle |
| Leader lines | From callout box to affected component within layer band |
| Layer name typography | 24pt+, bold |
| Callout text typography | 14pt+, plain English (≤25 words per callout) |
| Component text typography | 12pt, regular |

---

## 6. Gemini Prompt Construction Notes

### Portrait Orientation and Layer Band Layout

The Gemini prompt for this template MUST specify:
- Portrait orientation, 8.5×11 aspect ratio, suitable for embedding as a full-bleed page in the security report PDF
- Architectural layers as horizontal bands stacked vertically; External Zone (most exposed, position 0) at the TOP; Agent Frameworks Zone (most trusted, position 8) at the BOTTOM
- Each layer band uses a distinct pastel fill color cycling through the 5-color palette defined in schemas/infographic.yaml visual_directives
- Red dashed-border callout boxes (2pt, #DC2626) with warning triangle icons for the 3 High-severity layers
- Leader lines connecting each callout to its affected_component within the layer band
- Callout text rewritten to ≤25 words in plain English per executive audience requirement

### Full Gemini Prompt

Create a professional executive security architecture overview in portrait orientation (8.5 × 11 proportions), suitable for embedding as a full-page insert in a formal security report PDF.

IMPORTANT: The directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical specifications as visible text in the image. Only render the data labels, component names, and natural-language callout text specified in the DATA CONTENT sections.

DESIGN DIRECTIVES (interpret these, do not display them):
- Layout: portrait orientation, 8.5 × 11 proportions
- Horizontal layer bands stacked vertically, most exposed layer at TOP, most trusted at BOTTOM
- Layer band fills: cycle through soft pastel colors (light blue, light peach, light green, light pink, light lavender)
- Callout boxes: red dashed border (2pt weight), warning triangle icon, connected to affected component by a thin leader line
- Typography: layer names 24pt+ bold; callout text 14pt+; component names 12pt regular
- All text must be legible at letter-size print resolution

DATA CONTENT (render this as visible text):

DOCUMENT HEADER (top of page): "Healthcare CDSS — Executive Threat Architecture" with "2026-04-16" and "REFERENCE SCENARIO — NOT A REAL CLINICAL SYSTEM" subtitle in smaller text below.

LAYER BANDS (stacked top-to-bottom, labeled on left edge, components listed inside):

Layer 1 (TOP — light blue band): "External Zone" — Components: Physician, Patient
RED DASHED CALLOUT for Physician: Warning icon + "S-1: An attacker could steal a doctor's login credentials and access confidential patient data without authorization."

Layer 2 (light peach band): "User Interface Zone" — Components: Physician Clinical Portal, Patient Summary Generator
RED DASHED CALLOUT for Physician Clinical Portal: Warning icon + "D-1: An attacker could overwhelm the doctor portal with fake requests, making it unavailable to real physicians."

Layer 3 (light green band): "Agent Ecosystem Zone" — Components: Inter-Agent Communication Channel
RED DASHED CALLOUT for Inter-Agent Communication Channel: Warning icon + "S-5: An attacker could send fake coordination commands to AI agents, causing them to act on forged instructions."

Layer 4 (light pink band): "Security and Compliance Zone" — Components: HIPAA RBAC + Policy Engine, Consent and De-identification Guardrail
(No callout — Medium severity findings only in this layer)

Layer 5 (light lavender band): "Foundation Models Zone" — Components: Clinical LLM, Risk Stratification Model
(No callout — Medium severity findings only)

Layer 6 (light blue band, cycling): "Evaluation and Observability Zone" — Components: Clinical Audit Log, Outcomes Telemetry and Physician Override Audit Store
(No callout — Medium severity findings only)

Layer 7 (light peach band, cycling): "Deployment Infrastructure Zone" — Components: EHR Ingestion Queue, Model Inference API Gateway
(No callout — Medium severity findings only)

Layer 8 (light green band, cycling): "Data Operations Zone" — Components: FHIR Resource Store, Clinical Guideline RAG Corpus, Medical Literature Vector Index
(No callout — Medium severity findings only)

Layer 9 (BOTTOM — light pink band, cycling): "Agent Frameworks Zone" — Components: Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Clinical MCP Tool Server
(No callout — Medium severity findings only; highest-concern agentic patterns present but score Medium after composite reachability modeling)

SEVERITY SUMMARY (bottom of page, above footer): "Residual Risk Summary: 0 Critical / 6 High / 104 Medium / 2 Low — 112 total findings. High-severity findings concentrated on externally exposed layers. All internal AI agent and model components score Medium after composite risk modeling. Reference scenario only — apply to real clinical codebase for production-representative results."

FOOTER (bottom): "Generated by Tachi Threat Modeling Framework — MAESTRO Canonical Worked Example — Healthcare CDSS Reference Architecture" in small gray text, centered.

All callout text must be written in plain English for a non-technical executive audience. No technical jargon. Large readable typography throughout. Image must be legible when printed on a letter-size page.
