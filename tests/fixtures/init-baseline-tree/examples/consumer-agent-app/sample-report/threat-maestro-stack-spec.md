---
schema_version: "1.0"
template: "maestro-stack"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 19
image_generated: true
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Consumer-Facing AI Companion Application |
| Scan Date | 2023-11-14 |
| Analysis Agents | 0 |
| Total Findings | 19 |
| Risk Posture | Residual risk — 0 Critical and 4 High findings across 0 components |
| Baseline | none (first run — stateless mode for Feature 224 wave 5 regen) |

---

## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 4 | 21% | #EA580C |
| Medium | 14 | 74% | #CA8A04 |
| Low | 1 | 5% | #2563EB |
| **Total** | **19** | **100%** | — |

**Chart Format**: Donut chart. Risk label: **Residual Risk Distribution** (post-control exposure after control analysis).

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| WellnessCompanionChatbot | 0 | 3 | 7 | 1 | 11 |
| Conversation Session Store | 0 | 0 | 3 | 0 | 3 |
| Interaction Audit Log | 0 | 0 | 3 | 0 | 3 |
| End User | 0 | 1 | 1 | 0 | 2 |

### Cell-Level Grid

| Component | S | T | R | I | D | E | TE |
|-----------|---|---|---|---|---|---|----|
| WellnessCompanionChatbot | High | Medium | Medium | Medium | Medium | High | High |
| Conversation Session Store | — | Medium | — | Medium | Medium | — | — |
| Interaction Audit Log | — | Medium | — | Medium | Medium | — | — |
| End User | High | — | Medium | — | — | — | — |

**Note on TE category column**: TE-{N} findings (Wellness Companion Chatbot, OWASP ASI09:2026) appear in the dedicated TE column. The five TE-{N} findings (TE-1..TE-5) all anchor to the WellnessCompanionChatbot Process — three High residual (TE-1 undisclosed AI authorship, TE-3 persuasive-tone manipulation, TE-5 synthetic-relationship exploitation) plus two Medium residual (TE-2, TE-4).

---

## 4. Top Critical Findings

Top High residual findings shown (no Critical residual findings in this baseline):

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | S-1 | End User | An attacker could spoof the End User identity at session establishment, submitting User Turn requests under a victim user's identity | High (score 7.8) |
| 2 | TE-5 | WellnessCompanionChatbot | Sustained engagement with vulnerable populations without session-length cap, escalation-to-human pathway, or dependency-risk classifier (synthetic-relationship) | High (score 7.4) |
| 3 | TE-1 | WellnessCompanionChatbot | Companion Responses emitted without declared AI-generation disclosure mechanism (undisclosed AI authorship) | High (score 7.2) |
| 4 | TE-2 | WellnessCompanionChatbot | Wellness-coaching content emitted without per-claim confidence-attestation or source-grounding (authority-attestation) | High (score 7.0) |
| 5 | TE-3 | WellnessCompanionChatbot | Wellness-coaching content emitted with high-confidence persuasive framing without uncertainty-disclosure (persuasion-manipulation) | Medium (score 6.7) |

---

## 5. Architecture Threat Overlay

### MAESTRO Layer Stack

| Layer | Layer Name | Components | Finding Count | Highest Severity |
|-------|-----------|-----------|---------------|------------------|
| L7 | Agent Ecosystem | WellnessCompanionChatbot, End User | 13 | High |
| L5 | Evaluation & Observability | Interaction Audit Log | 3 | Medium |
| Unclassified | (no MAESTRO layer assignment) | Conversation Session Store | 3 | Medium |

**MAESTRO Data Status**: The extraction script reports `has_maestro_data: false` and `maestro_layer_distribution: []` because threats.md does not include the canonical `#### Risk by MAESTRO Layer` table in Section 6 — this Feature 224 baseline uses the simpler Phase 1/2 intermediate format. The per-layer summary above is reconstructed from the Phase 1 Component Inventory's MAESTRO Layer column and is provided manually for spec completeness; the JPEG render reflects the same data via the natural-language DATA CONTENT block.

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

Vertical 7-Layer Stack (16:9 landscape):

1. **TITLE BAND (~10%)**: Project name + total finding count + residual risk summary
2. **STACK CANVAS (~85%)**: L7 (Agent Ecosystem) at top, L1 (Foundation Models) at bottom; each layer shows occupied components and residual finding counts; empty layers shown as compact badges
3. **FOOTER (~5%)**: "Generated by Tachi Threat Modeling Framework"


### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Per template (see template file).

### TE-Pattern Emphasis Directive

The five TE-{N} findings on WellnessCompanionChatbot represent the OWASP ASI09:2026 (`human-trust-exploitation`) communication-axis pattern surface — the first multi-instance TE-{N} emission on a clean-slate consumer-facing baseline. Designers may emphasize TE-1 (undisclosed AI authorship), TE-3 (persuasive-tone manipulation), and TE-5 (synthetic-relationship exploitation) as the three High residual findings that dominate the residual risk profile.
