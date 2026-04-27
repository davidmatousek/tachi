---
schema_version: "1.4"
template: "executive-architecture"
date: "2026-04-27"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 85
tier_source: "compensating-controls"
qualifying_layer_count: 3
total_filtered_count: 10
skip_image: false
image_generated: true
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Template Name | executive-architecture |
| Tier Source | compensating-controls |
| Source File | /Users/david/Projects/tachi/examples/agentic-app/sample-report/threats.md |
| Generation Timestamp | 2026-04-27T18:28:07Z |
| Qualifying Layer Count | 3 |
| Total Filtered Count | 10 (Critical + High residual findings) |
| Skip Image | false |
| Fallback Used | false |
| Scan Date | 2026-04-27 |
| Project Name | Agentic AI Application |

---

## 2. Architecture Layers

Layers are ordered untrusted-first (position 0 = most exposed) to trusted-last.

| Position | Layer Name | Source Kind | Component Count | Components |
|----------|------------|-------------|-----------------|------------|
| 0 | User Zone | trust_zone | 1 | User |
| 1 | External Services | trust_zone | 1 | External API |
| 2 | Application Zone | trust_zone | 9 | Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent |

> Note: Application Zone has 9 components displayed + layer_overflow: "+ 5 more in this layer" (full list above includes all 9).

---

## 3. Threat Callouts

5 callouts selected from 10 qualifying High-severity findings. Callouts distributed across qualifying layers with per-layer floor of 1. Application Zone carries the largest allocation given concentration of 9 High findings there.

| Layer | Finding ID | Severity | Composite Score | Affected Component | Raw Description |
|-------|-----------|----------|-----------------|-------------------|-----------------|
| User Zone | S-1 | High | 8.2 | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials |
| Application Zone | AG-1 | High | 7.8 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions |
| Application Zone | E-2 | High | 7.8 | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection |
| Application Zone | E-1 | High | 7.7 | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller |
| Application Zone | D-10 | High | 7.2 | LLM Agent Orchestrator | LLM Inference-Request Flooding and Token Exhaustion without per-tenant QPS rate limiting |

> **F-5 callout**: D-10 is a new finding introduced in Feature 229 Wave 2 (OWASP LLM10:2025 Unbounded Consumption). Gemini will rewrite raw descriptions to ≤25 words in plain English at render time.

**Empty Layers**: External Services (External API) — 0 Critical/High findings. Renders as compact badge: "0 High/Critical findings in this layer".

---

## 4. Severity Distribution

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 10 |
| Total qualifying (Critical + High) | 10 |
| Total after layer dedup | 5 (one callout per unique layer + additional Application Zone callouts per Largest Remainder Method) |

---

## 5. Visual Layout Directives

- **Orientation**: Portrait (8.5:11 page aspect ratio)
- **Layer ordering**: Untrusted at top (User Zone → External Services → Application Zone)
- **Layer fills**: 5-color pastel cycle by position index — User Zone: #F0F4FF (cool blue), External Services: #FFF4F0 (warm peach), Application Zone: #F0FFF4 (cool green)
- **Component nodes**: Rounded-rectangle nodes within each layer band; severity-colored borders
  - User (S-1 High): orange border (#EA580C)
  - LLM Agent Orchestrator (AG-1, E-2, D-10 High): orange border (#EA580C)
  - Guardrails Service (E-1 High): orange border (#EA580C)
  - External API, other Application Zone components: gray border (#6B7280)
- **Callout boxes**: Red dashed-border boxes (#DC2626, 2pt), warning triangle icon, leader lines to anchor nodes; left/right page margins
- **Empty layer**: External Services renders as compact badge: "0 High/Critical findings in this layer"
- **Inter-layer arrows**: Directional arrows flowing top-to-bottom between adjacent layers
- **Typography**: Portrait-optimized — title 28-32pt, layer labels 18-22pt, callout text 12-14pt

---

## 6. Gemini Prompt Construction Notes

**Template**: executive-architecture (FR-212-6 VERBATIM LOCK applies)

The prompt is constructed by copying the verbatim block from `.claude/skills/tachi-infographics/references/executive-architecture.md` and substituting the `<<...>>` data slots:

- `<<project_name>>`: Agentic AI Application
- `<<layer_block>>`: 3 layers (User Zone → External Services → Application Zone)
- `<<callout_block>>`: 5 callouts (S-1, AG-1, E-2, E-1, D-10) with raw descriptions for Gemini rewrite
- `<<empty_layer_block>>`: "External Services: 0 High/Critical findings in this layer"
- `<<single_zone_caption>>`: (empty — more than one layer has components)
- `<<flow_edges_block>>`: 29 explicit flow edges from flow_edges[] payload
- `<<clusters_block>>`: 3 clusters from clusters[] payload (Application Zone, External Services, User Zone)

All slots populated. Verbatim lock enforced — no aesthetic recomposition.
