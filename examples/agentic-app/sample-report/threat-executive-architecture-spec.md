---
schema_version: "1.0"
template: "executive-architecture"
date: "2026-04-19"
source_file: "threats.md"
data_source_type: "threats"
finding_count: 61
image_generated: true
project_name: "Agentic AI Application"
fallback_note: "Extraction ran against threats.md (Tier 3 fallback); score numbers inlined from compensating-controls.md + risk-scores.md Executive Summary due to parser heading-format mismatch against current compensating-controls.md schema"
---

# Threat Infographic Specification — Executive Architecture

## 1. Metadata

- **Project**: Agentic AI Application
- **Scan Date**: 2026-04-19
- **Template**: executive-architecture
- **Tier Source**: threats
- **Qualifying Layers**: 3
- **Total Filtered (Critical+High)**: 61
- **Skip Image**: False
- **Fallback Used**: False
- **Generation Timestamp**: 2026-04-19T04:28:04Z

## 2. Architecture Layers

Layers from trust-zone groups (untrusted at position 0):

### Layer 0: User Zone
- **Component Count**: 1
- **Components**: User
- **Source Kind**: trust_zone

### Layer 1: External Services
- **Component Count**: 1
- **Components**: External API
- **Source Kind**: trust_zone

### Layer 2: Application Zone
- **Component Count**: 8
- **Components**: Audit Logger, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent
- **Source Kind**: trust_zone

## 3. Threat Callouts

One callout per qualifying layer:

### User Zone — S-1 (Critical)
- **Affected Component**: User
- **Composite Score**: None
- **Raw Description**: Attacker impersonates legitimate user via replayed session tokens

### External Services — S-8 (High)
- **Affected Component**: External API
- **Composite Score**: None
- **Raw Description**: DNS hijacking/BGP attack redirects External API calls to attacker-controlled server

### Application Zone — AG-1 (Critical)
- **Affected Component**: LLM Agent Orchestrator
- **Composite Score**: None
- **Raw Description**: Prompt injection causes autonomous unauthorized high-impact actions

### Feature 201 Supplementary Callout — Application Zone / LLM Agent Orchestrator

In addition to the AG-1 layer-primary callout, the Application Zone carries three Feature 201 Output-Integrity findings:

- **OI-1** (inherent Critical; residual 7.2 High): Client-side XSS via LLM response to User browser. OWASP LLM05:2025, CWE-79.
- **OI-2** (inherent Critical; residual 6.7 Medium): Server-side code/command execution via LLM-synthesized Tool Call parameters. OWASP LLM05:2025, CWE-89 + CWE-78.
- **OI-3** (inherent High; residual 6.1 Medium): SSRF via LLM-synthesized URL in Tool Call Request. OWASP LLM05:2025, CWE-918.

Rendered as a red-bordered supplementary callout adjacent to the Application Zone band with the label 'OUTPUT INTEGRITY (F-201 / OWASP LLM05:2025)'.

## 4. Severity Distribution

- **Critical**: 38
- **High**: 23
- **Total Qualifying (Critical + High)**: 61

## 5. Visual Layout Directives

- **Orientation**: Portrait 8.5x11 (full-bleed PDF page)
- **Layer stacking**: Horizontal bands stacked vertically, untrusted layer at TOP
- **Pastel fills**: #F0F4FF, #FFF4F0, #F0FFF4 (cycled per schema `visual_directives`)
- **Callout boxes**: Red dashed 2pt border #DC2626 with warning triangle icon
- **Leader lines**: Connect each callout to its affected_component within its layer band
- **Typography**: 24pt layer names, 14pt callout body
- **F-201 supplementary callout**: Red-bordered box right of Application Zone listing OI-1/OI-2/OI-3

## 6. Gemini Prompt Construction Notes

The image prompt rewrites each callout's raw_description to ≤25 words plain English (no technical jargon — no 'JWT', 'payload', 'RBAC'; prefer 'attacker could', 'system could leak', 'user could impersonate'). Prompt is built from payload fields, not hardcoded.
