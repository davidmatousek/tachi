---
schema_version: "1.0"
template: "executive-architecture"
date: "2026-04-10"
source_file: "threats.md"
finding_count: 10
image_generated: false
---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | Agentic AI Application |
| Scan Date | 2026-04-10 |
| Total Critical/High Findings | 10 |
| Qualifying Layers | 3 |
| Tier Source | compensating-controls |
| Risk Posture | Executive view — 10 Critical/High findings distributed across 3 architectural layers require board-level awareness and prioritized remediation budget. |

## 2. Executive Summary

**10 Critical/High findings** span 3 architectural layers (User Zone, External Services, Application Zone). Residual scoring produced no Critical-band findings — all elevated risk is in the High band.

### Risk Distribution (Critical/High only)

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 10 |
| **Total Qualifying** | **10** |

## 3. Architectural Layers

Layers derived from trust zones in the architecture. Each layer groups components by their trust position.

| Layer | Components | Source |
|-------|------------|--------|
| User Zone | User | trust_zone |
| External Services | External API | trust_zone |
| Application Zone | Audit Logger, Guardrails Service, Knowledge Base, LLM Agent Orchestrator, MCP Tool Server | trust_zone |

## 4. Layer Callouts

One callout per architectural layer, showing the highest-severity Critical/High finding affecting that layer. Executive-facing summary of the top risk per zone.

### Callout 1: User Zone

**Finding**: S-1 (High) — composite 7.4

**Affected Component**: User

**Threat**: Attacker spoofs a legitimate user identity by stealing or r…

### Callout 2: External Services

**Finding**: S-3 (High) — composite 7.4

**Affected Component**: External API

**Threat**: Compromised or spoofed external API returns malicious paylo…

### Callout 3: Application Zone

**Finding**: LLM-1 (High) — composite 8.1

**Affected Component**: LLM Agent Orchestrator

**Threat**: Indirect prompt injection via documents retrieved from the …


## 5. Visual Design Directives

**Format**: Portrait orientation (2:3 aspect ratio), print-ready at 300 DPI, 2480 x 3508 px minimum.

**Color System**:
- Critical: `#DC2626` (deep red)
- High: `#EA580C` (orange-red)
- Background: light gray `#F5F5F5` with white panels `#FFFFFF`
- Headers: dark navy `#1E293B`

**Layout**:
- Top banner (15% height): project name, scan date, Critical/High count, executive risk posture
- Layered architecture diagram (55% height): components grouped into architectural layers with trust zones as zone backgrounds
- Callouts per architectural layer (20% height, right side): one callout per layer with the highest-severity finding in that layer
- Bottom panel (10% height): executive takeaway

**Typography**: Sans-serif, 18-24pt headers, 10-12pt body. Callout titles in 16pt bold.

**Visual Style**: Executive-briefing aesthetic. Components grouped into architectural layers derived from trust zone assignments. Layer-level callouts emphasize the highest-risk finding per layer. Use ONLY the canonical CSA MAESTRO layer names: L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem.

**Prompt Hint (Gemini)**: Generate a print-quality executive infographic showing the architectural layers with their callouts. Emphasize the Critical/High findings that warrant board-level awareness. Place this infographic immediately after the executive summary in the security report.
