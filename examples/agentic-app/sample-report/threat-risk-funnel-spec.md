---
schema_version: "1.0"
template: "risk-funnel"
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
| Delta | NEW: AG-8 (Inter-Agent Communication Channel) — OWASP ASI07:2026, raw Critical, residual High after compensating controls. Tier 1 count reflects raw total including AG-8. |

**Delta Context**: AG-8 is accounted for in Tier 1 (raw 84 findings total, including AG-8). The compensating controls detected for AG-8 (mTLS enforcement, message signing, replay prevention, taint labeling) reduce its residual severity band to High. It appears in Tier 4 residual risk as part of the 8 High residual findings.

---

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 8 | 10% | #EA580C |
| Medium | 68 | 84% | #EAB308 |
| Low | 5 | 6% | #4169E1 |
| **Total** | **81** | **100%** | — |

**Chart Format**: Donut chart (Tier 4 residual distribution). Risk label: **Residual Risk Distribution**.

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

### Funnel Tiers (4-Tier Mode — compensating-controls)

| Tier | Label | Width (%) | Severity Counts | Render State |
|------|-------|-----------|-----------------|--------------|
| 1 | Threats Identified | 100% | 0 Critical / 8 High / 68 Medium / 5 Low (raw: includes AG-8 [NEW]) | solid |
| 2 | Inherent Risk Scored | ~100% (ghost) | Not available — risk-scores.md inherent scores absent | ghost |
| 3 | Controls Applied | ~97% | 81 findings with compensating controls assessed (96% coverage) | solid |
| 4 | Residual Risk | ~97% | 0 Critical / 8 High / 68 Medium / 5 Low | solid |

**Funnel shape note**: Tier 2 is rendered as a ghost tier with a CTA annotation. The funnel narrows only slightly from Tier 1 to Tier 4 because inherent scores are absent — risk reduction can only be shown qualitatively (no raw Critical in residual vs. the presence of AG-8 at raw Critical).

**Tier 1 detail** (from threats.md Section 6):
- Raw total: 84 findings (83 baseline + 1 NEW AG-8)
- Deduplicated (correlation groups): 75 findings after 7 correlation groups merge 16 individual findings

**Tier 3 detail** (from compensating-controls.md):
- 81 findings assessed against control inventory
- AG-8 controls: mTLS enforcement, HMAC/Ed25519 message signing, nonce-based replay prevention, taint propagation policy

**Tier 4 detail** (residual):
- 0 Critical (AG-8 raw Critical → residual High after controls)
- 8 High, 68 Medium, 5 Low

### Ghost Tier Note

Tier 2 (Inherent Risk Scored) is rendered as ghost because `risk-scores.md` is absent from this pipeline run. Run `/tachi.risk-score` to produce inherent composite scores and unlock full 4-tier risk reduction quantification.

### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Findings (raw) | 84 |
| Total Findings (residual, post-dedup) | 81 |
| Risk Reduction | Qualitative only — inherent scores not available |
| Control Coverage | Not computed (risk-scores.md absent) |
| New Findings This Wave | 1 (AG-8) |
| Resolved Findings | 0 |

### Delta Emphasis: AG-8 Journey Through the Funnel

- **Tier 1**: AG-8 appears as a Critical finding (raw severity: Critical)
- **Tier 2**: N/A (ghost tier — no inherent scores)
- **Tier 3**: AG-8 receives controls: mTLS, message signing, replay prevention, taint propagation
- **Tier 4**: AG-8 residual = High (controls reduce severity band from Critical to High)

Visual directive: In Tier 1, the "Critical" segment of the donut/bar should carry a "[+1 NEW]" badge. In Tier 4, annotate the High segment with "includes AG-8 (controlled)".

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: Tier 1 and Tier 4 Critical segment |
| High | #EA580C | Orange-600: Tier 1 and Tier 4 High segment |
| Medium | #CA8A04 | Yellow-600: Tier 1 and Tier 4 Medium segment |
| Low | #2563EB | Blue-600: Tier 1 and Tier 4 Low segment |
| Ghost | #374151 | Dark gray: Tier 2 ghost state background |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

Risk Funnel layout (16:9 landscape, dark navy background):

- 4-tier vertical funnel with 3D translucent glass trapezoids
- Tier 1 widest (100%), Tier 2 ghost, Tier 3 and Tier 4 narrow progressively (minimum 10% per tier)
- CONFIDENTIAL badge in top right
- Sidebar metrics panel on the right
- Funnel tiers labeled with count and severity breakdown text
- Footer centered below funnel

### Typography

- Title: Bold, 28-32pt equivalent
- Tier Labels: Semi-bold, 18-22pt equivalent
- Tier Counts: Bold, 14-16pt equivalent
- Sidebar: Regular, 12-14pt equivalent

### Background

Dark navy (#1E293B) — executive boardroom aesthetic. Funnel tiers use translucent 3D glass-like material with soft ambient lighting.
