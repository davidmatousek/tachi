---
schema_version: "1.0"
template: "executive-architecture"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
---

# Threat Infographic Specification — Executive Architecture
## Project: Agentic AI Application

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Template Name | executive-architecture |
| Tier Source | compensating-controls |
| Source File | threats.md |
| Generation Timestamp | 2026-04-24T01:43:38Z |
| Qualifying Layer Count | 3 |
| Total Filtered Count | 17 |
| Skip Image | false |
| Fallback Used | false |

---

## 2. Architecture Layers

Layers ordered with most-exposed (lowest-trust) at position 0 (top of diagram).

| Position | Layer Name | Components | Component Count | Source Kind |
|----------|-----------|-----------|-----------------|-------------|
| 0 | User Zone | User | 1 | trust_zone |
| 1 | External Services | External API | 1 | trust_zone |
| 2 | Application Zone | Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent | 9 | trust_zone |

---

## 3. Threat Callouts

Callouts derived from top-scored Critical and High findings, limited to 2 per-layer to preserve visual clarity. Raw descriptions preserved verbatim below; Gemini prompt instructs rewriting to ≤25 words of plain English.

| Layer | Finding ID | Severity | Raw Description | Composite Score | Affected Component |
|-------|-----------|----------|-----------------|-----------------|---------------------|
| User Zone | S-1 | High | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials to bypass authentication at the User→Guardrails boundary, gaining unauthorized access to the system under a victim identity. | 8.2 | User |
| Application Zone | AG-1 | High | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions (mass data exfiltration from KB, bulk tool invocations against External API) beyond the scope of the user's original request, exploiting the Orchestrator's broad access to system capabilities. | 7.8 | LLM Agent Orchestrator |

**Note**: External Services zone has no qualifying High/Critical findings (R-8 is Low residual severity). Two callouts displayed, one per affected zone with qualifying findings.

---

## 4. Severity Distribution

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 17 |
| **Total qualifying (Critical + High)** | **17** |

Medium and Low findings are not shown in this template; they appear in full detail in the baseball-card and system-architecture templates.

---

## 5. Visual Layout Directives

- **Orientation**: Portrait (8.5×11 aspect ratio), full-bleed, suitable for embedding as a security report page
- **Layer arrangement**: Horizontal bands stacked vertically, top-to-bottom in order of exposure:
  - Position 0 (TOP): User Zone — most exposed / untrusted
  - Position 1 (MIDDLE): External Services — semi-trusted
  - Position 2 (BOTTOM): Application Zone — most trusted internal zone
- **Layer band fill colors** (pastel palette, cycling):
  - User Zone: #F0F4FF (pastel blue)
  - External Services: #FFF4F0 (pastel peach)
  - Application Zone: #F0FFF4 (pastel green)
- **Callout boxes**: Red dashed border (2pt, color #DC2626), warning triangle icon, connected to affected component via leader line
- **Callout text**: ≤25 words plain English (rewritten by Gemini), no technical jargon
- **Typography**: Layer names 24pt+, callout text 14pt+, legible at printed letter size
- **CONFIDENTIAL badge**: Red pill with white text, top-right corner

---

## 6. Gemini Prompt Construction Notes

The Gemini prompt for this template is built from the JSON payload fields above and must follow executive-architecture conventions:

**Orientation**: Portrait (8.5×11), full-bleed for security report embedding.

**Layer bands** (horizontal, untrusted-first from top):
- TOP: "User Zone" band — pastel blue fill — 1 component: User
- MIDDLE: "External Services" band — pastel peach fill — 1 component: External API
- BOTTOM: "Application Zone" band — pastel green fill — 9 components: Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent

**Callout boxes** (red dashed border, warning triangle, leader line to affected component):

Callout 1 — User Zone → User:
Raw: "An attacker impersonates a legitimate user by replaying stolen session tokens..."
REWRITE to ≤25 words: "An attacker could steal a user's login credentials and access the system as that person, bypassing all security checks."

Callout 2 — Application Zone → LLM Agent Orchestrator:
Raw: "Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions..."
REWRITE to ≤25 words: "An attacker could trick the AI coordinator into taking harmful actions — like stealing data or sending unauthorized requests — without any human approval."

**Full Gemini Prompt**:

Create a premium executive security architecture diagram in portrait orientation (8.5×11 ratio), full-bleed, suitable for printing as a full page in a security report. This should look like a professionally designed security brief — clean, formal, and immediately understandable by a non-technical executive audience.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, border specifications, or technical CSS values as visible text. Only render the layer names, component names, callout text, and labels specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Portrait orientation: tall, not wide — full 8.5x11 page proportions
- Layer bands: horizontal pastel-filled rectangles, stacked from top (most exposed) to bottom (most trusted)
- User Zone fill: very light blue-white
- External Services fill: very light peach-white
- Application Zone fill: very light green-white
- Callout boxes: dashed red borders, red warning triangle icon, leader line connecting to the named component
- Typography: large readable fonts, layer names prominent, callout text must be readable when printed
- Background: clean white page

DATA CONTENT (render this as visible text):

HEADER: "Executive Architecture Brief: Agentic AI Application" — "Security Posture Summary — 2023-11-14" — "CONFIDENTIAL"

LAYER 1 (TOP BAND — widest exposure): Label: "User Zone" — Components: User — Severity badge: "17 High Findings Across System"

LAYER 2 (MIDDLE BAND): Label: "External Services" — Components: External API — Severity badge: "2 Low Findings"

LAYER 3 (BOTTOM BAND): Label: "Application Zone" — Components listed: Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent — Severity badge: "17 High / 62 Medium Findings"

CALLOUT 1 (red dashed box, warning triangle, leader line to "User" in User Zone band):
"An attacker could steal a user's login credentials and access the system as that person, bypassing all security checks."
Label: "Finding S-1 — High Risk"

CALLOUT 2 (red dashed box, warning triangle, leader line to "LLM Agent Orchestrator" in Application Zone band):
"An attacker could trick the AI coordinator into taking harmful actions — like stealing data or sending unauthorized requests — without any human approval."
Label: "Finding AG-1 — High Risk"

SUMMARY BOX (bottom of diagram):
"Risk Summary: 0 Critical / 17 High / 62 Medium / 2 Low residual findings. No production-grade security controls detected. Risk reduction: 0.5%. Immediate remediation required."

FOOTER: "Generated by Tachi Threat Modeling Framework — Executive Architecture Summary"

The overall impression should be a clean, serious, board-ready security briefing document. Layer bands should be clearly separated with readable labels. Callout boxes should stand out visually with their red dashed borders. Text must be legible at normal reading distance when printed on letter-size paper. No technical jargon in visible text — use plain language throughout.
