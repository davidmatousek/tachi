---
schema_version: "1.0"
template: "executive-architecture"
date: "2023-11-14"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 4
image_generated: true
has_baseline: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| template_name | executive-architecture |
| tier_source | compensating-controls |
| source_file | /Users/david/Projects/tachi/examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/threats.md |
| generation_timestamp | 2026-04-27T01:34:26Z |
| qualifying_layer_count | 2 |
| total_filtered_count | 4 |
| skip_image | false |
| fallback_used | false |

**Context**: Feature 224 wave 5 regen for the Consumer-Facing AI Companion Application baseline. The executive-architecture extraction is sourced from the threats.md `### Trust Zones` table (added under `## Section 1: Architecture Overview` to enable executive-architecture rendering on this single-component clean-slate baseline). Two layers emerge: User Zone (untrusted, position 0, contains End User) and Application Zone (trusted, position 1, contains WellnessCompanionChatbot, Conversation Session Store, Interaction Audit Log). 4 qualifying High-severity findings populate the callout pool: S-1, TE-5, TE-1, TE-2 (no Critical residual; the human-trust-exploitation pattern surface dominates with three TE-{N} High residual findings on WellnessCompanionChatbot).

---

## 2. Architecture Layers

Ordered top-to-bottom (position 0 = most exposed / untrusted):

### Layer 0 — User Zone (untrusted, position 0)

- **Components**: End User
- **Component count**: 1
- **Source kind**: trust_zone
- **Overflow**: none

### Layer 1 — Application Zone (trusted, position 1)

- **Components**: Conversation Session Store, Interaction Audit Log, WellnessCompanionChatbot
- **Component count**: 3
- **Source kind**: trust_zone
- **Overflow**: none

---

## 3. Threat Callouts

Selected via Largest Remainder Method (FR-212 Level 2): system-wide weighted distribution, severity descending, composite-score descending, finding ID ascending tiebreaker.

| # | Layer | Anchor Component | Finding ID | Severity | Score | Plain-English Description (≤25 words) |
|---|-------|-------------------|------------|----------|-------|------------------------------------------|
| 1 | User Zone | End User | S-1 | High | 7.8 | An attacker could spoof the End User identity at session establishment, submitting User Turn requests under a victim user's identity |
| 2 | Application Zone | WellnessCompanionChatbot | TE-5 | High | 7.4 | Sustained engagement with vulnerable populations without session-length cap, escalation-to-human pathway, or dependency-risk classifier |
| 3 | Application Zone | WellnessCompanionChatbot | TE-1 | High | 7.2 | Companion Responses emitted without declared AI-generation disclosure mechanism |
| 4 | Application Zone | WellnessCompanionChatbot | TE-2 | High | 7.0 | Wellness-coaching content emitted without per-claim confidence-attestation or source-grounding |

**TE-Pattern Concentration**: Three of the four callouts are `TE-{N}` findings (TE-5 synthetic-relationship, TE-1 undisclosed AI authorship, TE-2 authority-claim emission) — the OWASP ASI09:2026 (`human-trust-exploitation`) communication-axis pattern surface. The fourth callout (S-1) anchors to End User and is a STRIDE Spoofing finding on the user-side trust boundary.

---

## 4. Severity Distribution

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 4 |

(Medium/Low/Note are excluded from the executive-architecture template per F-128 contract.)

---

## 5. Visual Layout Directives

Portrait orientation (8.5:11 page aspect ratio); pastel layer-band fills cycling `#F0F4FF`, `#FFF4F0`, `#F0FFF4`, `#FFF0F8`, `#F8F0FF` by layer index; severity-colored callout borders (Critical `#DC2626`, High `#EA580C`); leader-line callout anchoring per FR-212-3; non-overlap rule per FR-212-3 / T030 polish.

Layer 0 (User Zone, untrusted) renders with `#F0F4FF` fill at the top of the page; Layer 1 (Application Zone, trusted) renders with `#FFF4F0` fill below it. Inter-layer arrows flow top-to-bottom from User Zone to Application Zone via the User Turn (HTTPS) edge. Companion Response (HTTPS) flows back from Application Zone to User Zone, marked as the FR-006 Indicator A boundary crossing.

---

## 6. Gemini Prompt Construction Notes

Prompt source: `.claude/skills/tachi-infographics/references/executive-architecture.md` — `=== BEGIN VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===` block, copied verbatim with `<<...>>` slot substitution from the extraction payload.

**Slot substitutions performed**:
- `<<project_name>>` → "Consumer-Facing AI Companion Application"
- `<<layer_block>>` → 2-line layer enumeration (User Zone position 0, Application Zone position 1)
- `<<callout_block>>` → 4-callout block (S-1, TE-5, TE-1, TE-2 — all High severity)
- `<<empty_layer_block>>` → "(no empty layers)" (both layers have qualifying findings)
- `<<flow_edges_block>>` → 5 flow edges from `flow_edges[]` payload
- `<<clusters_block>>` → 2 clusters (User Zone untrusted, Application Zone trusted)
- `<<single_zone_caption>>` → empty (multi-zone topology — 2 occupied layers)

**Image generation**: succeeded — JPEG written to `threat-executive-architecture.jpg`.

**Verbatim-lock compliance**: This run honors FR-212-6 — the prompt was copied byte-identical from the verbatim block, with only slot substitutions applied. No directive rewriting, no aesthetic recomposition.
