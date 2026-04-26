---
schema_version: "1.0"
template: "baseball-card"
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

**Delta Context**: This run introduced finding AG-8, a new Critical-raw finding against the Inter-Agent Communication Channel. Controls were detected (mTLS enforcement, message signing policy, nonce-based replay prevention), reducing residual severity to High. AG-8 remains the single most structurally significant new finding in this wave — it targets the A2A trust fabric connecting the Orchestrator, Specialist Agent, and Clinical Advisory Sub-Agent without authenticated relay.

---

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 8 | 10% | #EA580C |
| Medium | 68 | 84% | #EAB308 |
| Low | 5 | 6% | #4169E1 |
| **Total** | **81** | **100%** | — |

**Chart Format**: Donut chart. Risk label: **Residual Risk Distribution** (post-control exposure after accounting for detected compensating controls).

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

**Delta note**: Inter-Agent Communication Channel AG cell = High (AG-8, residual). Raw severity was Critical; compensating controls reduced residual to High.

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

**Note on AG-8**: Finding AG-8 (Inter-Agent Communication Channel — insecure inter-agent communication, OWASP ASI07:2026) carries raw Critical severity. Its residual score places it just outside the top-5 after compensating controls reduce its residual band to High. Designers should consider adding an AG-8 callout to the architecture overlay strip to emphasize the NEW status of this finding.

---

## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| LLM Agent Orchestrator | Medium (2.2) | 19 | 4 High + 15 Medium findings. Dominant threat categories: Spoofing (S), Elevation-of-Privilege (E), Agentic (AG), Information-Disclosure (I). Central orchestration hub with widest attack surface. |
| MCP Tool Server | Medium (2.1) | 8 | 2 High + 5 Medium + 1 Low findings. Dominant: Tampering (T), Agentic (AG). Outbound API call path; tool-abuse risk vector. |
| Guardrails Service | Medium (2.0) | 5 | 1 High + 3 Medium + 1 Low findings. Dominant: Elevation-of-Privilege (E). Bypass risk elevates privilege to trusted caller. |
| Inter-Agent Communication Channel | Medium (2.0) | 8 | 8 Medium findings (residual); AG-8 [NEW] raw Critical reduced to High residual. OWASP ASI07:2026 — no mTLS, no message signing, no replay prevention across A2A fabric. Highest delta-significance component this wave. |
| Long-Running Learning Loop | Medium (2.0) | 9 | 9 Medium findings. Dominant: training signal poisoning, model update integrity. Persistent risk with no inherent score available. |
| Other | Medium (2.0) | 10 | 1 High + 8 Medium + 1 Low. Mixed components with moderate residual exposure. |
| Clinical Advisory Sub-Agent | Low (1.9) | 12 | 11 Medium + 1 Low findings. No High residual; clinical decision integrity controls effective. |
| Specialist Agent | Low (1.9) | 10 | 9 Medium + 1 Low findings. No High residual; delegation controls applied. |

**Risk Reduction**: Control coverage percentage not available from this pipeline run (risk-scores.md inherent scores absent).

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: donut segment, heat map cells, finding card borders, risk posture badge |
| High | #EA580C | Orange-600: donut segment, heat map cells, finding card borders |
| Medium | #CA8A04 | Yellow-600: donut segment, heat map cells, finding card borders |
| Low | #2563EB | Blue-600: donut segment, heat map cells, finding card borders |
| Note | #6B7280 | Gray-500: informational only, excluded from visual risk distribution |
| Clean cell | #F3F4F6 | Gray-100: heat map analyzed with no findings |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

Standard 4-Zone Layout (16:9 landscape, dark navy background):

1. **TOP SECTION (~10%)**: Title "Threat Model: Agentic AI Application", date 2026-04-26, CONFIDENTIAL badge, subtitle "81 Residual Findings Across 11 Components — Baseline Comparison Active"
2. **MIDDLE ROW (~50%)**: Left panel (donut chart — 0 Critical / 8 High / 68 Medium / 5 Low; center text "81 findings"), Center panel (Coverage Heat Map — component x STRIDE+AG category, Cell-Level Grid above), Right panel (top finding cards with orange left borders — High residual risk)
3. **BOTTOM STRIP (~30%)**: Architecture threat overlay showing trust zones (User Zone, External Services, Application Zone), data flow arrows, AG-8 callout on Inter-Agent Communication Channel marked [NEW]
4. **FOOTER (~5%)**: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis"

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Dark navy (#1E293B) — premium dark dashboard aesthetic. All text white or light gray on dark background.

### Delta Emphasis Directive

The [NEW] AG-8 finding on Inter-Agent Communication Channel MUST receive visual distinction:
- In the heat map, the Inter-Agent Communication Channel AG cell renders with an orange (High) fill AND a small "NEW" badge overlay in white text on a dark accent.
- In the architecture overlay strip, the Inter-Agent Communication Channel component box has an orange dashed border (2pt) instead of the standard solid border, with a "NEW" callout label.
- If space permits, a small annotation beneath the architecture strip reads: "AG-8 (NEW): Inter-Agent Communication Channel — OWASP ASI07:2026 — no mTLS / no message signing / no replay prevention."
