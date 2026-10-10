<!--
F-373 M-2/K15 fixture — `maestro_top_findings`
Exercises: maestro-stack's per_layer_summaries[].top_findings and the K15
allow_list for a fixture that, unlike maestro_partial and agentic_app, DOES
carry a "MAESTRO Layer" column on its Section 3 STRIDE tables (so
parse_per_finding_maestro actually populates a layer per finding).
Layout: 6 findings spread across 3 of the 7 canonical layers --
  L7 — Agent Ecosystem: S-1 (Critical), S-2 (High), S-4 (Medium)
  L3 — Agent Framework: T-1 (Critical), S-3 (High)
  L1 — Foundation Model: T-2 (High)
Expected per_layer_summaries[].top_findings (up to 2, severity desc then id
asc): L7 -> [S-1, S-2] (S-4 is the 3rd-ranked finding in its layer and MUST
be excluded by the 2-per-layer cap); L3 -> [T-1, S-3]; L1 -> [T-2];
L2/L4/L5/L6 -> [] (no finding maps to them). So
allow_list.finding_ids == sorted({S-1, S-2, S-3, T-1, T-2}), excluding S-4 --
the fixture that catches a cap or branch regression the all-empty
maestro_partial/agentic_app golden cannot (its own per_finding_maestro is
always [], so its allow_list.finding_ids is already [] before any fix).
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-373 MAESTRO Top-Findings Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Agent Orchestrator | Process | Agent coordination service |
| Foundation Model API | Process | Hosted LLM inference endpoint |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Agent Orchestrator | Foundation Model API | Completion Request | HTTPS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|--------|------------|--------|------------|------------|
| S-1 | Agent Orchestrator | L7 — Agent Ecosystem | Attacker impersonates a peer agent to inject forged delegation messages | HIGH | HIGH | Critical | Authenticate inter-agent messages with per-session HMAC keys |
| S-2 | Agent Orchestrator | L7 — Agent Ecosystem | Attacker spoofs a tool server response to the orchestrator | MEDIUM | HIGH | High | Sign tool server responses; verify on receipt |
| S-3 | Agent Orchestrator | L3 — Agent Framework | Attacker forges orchestrator-to-agent delegation commands | MEDIUM | HIGH | High | Require cryptographic attestation of orchestrator identity |
| S-4 | Agent Orchestrator | L7 — Agent Ecosystem | Attacker spoofs a low-confidence telemetry heartbeat | LOW | MEDIUM | Medium | Sign heartbeat payloads with a service identity key |

### 3.2 Tampering (T)

| ID | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|--------|------------|--------|------------|------------|
| T-1 | Agent Orchestrator | L3 — Agent Framework | Attacker tampers with the orchestrator's delegation logic | HIGH | HIGH | Critical | Immutable audit logging of orchestration decisions |
| T-2 | Foundation Model API | L1 — Foundation Model | Attacker tampers with completion requests in transit to the model API | MEDIUM | HIGH | High | Sign requests with HMAC; verify on receipt |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Agent Orchestrator | Attacker impersonates a peer agent to inject forged delegation messages | Critical | Authenticate inter-agent messages with per-session HMAC keys |
| S-2 | NEW | Agent Orchestrator | Attacker spoofs a tool server response to the orchestrator | High | Sign tool server responses; verify on receipt |
| S-3 | NEW | Agent Orchestrator | Attacker forges orchestrator-to-agent delegation commands | High | Require cryptographic attestation of orchestrator identity |
| S-4 | NEW | Agent Orchestrator | Attacker spoofs a low-confidence telemetry heartbeat | Medium | Sign heartbeat payloads with a service identity key |
| T-1 | NEW | Agent Orchestrator | Attacker tampers with the orchestrator's delegation logic | Critical | Immutable audit logging of orchestration decisions |
| T-2 | NEW | Foundation Model API | Attacker tampers with completion requests in transit to the model API | High | Sign requests with HMAC; verify on receipt |
