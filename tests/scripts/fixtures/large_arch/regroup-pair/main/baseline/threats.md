---
schema_version: "1.4"
date: "2026-11-09"
input_format: "free-text"
classification: "confidential"
run_id: "2026-11-09T10-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model Report

This file is the baseline run's threats.md, cut down to the sections that a baseline reader uses.

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Public Internet | Untrusted | client-portal |
| Edge DMZ | Semi-trusted | edge-gateway, auth-broker |
| Agent Runtime Zone | Trusted | intake-agent, planner-agent, worker-2, tool-server-1, model-gateway |
| Data Zone | Trusted | vector-store-a |
| Operations Zone | Trusted | audit-ledger |

---

## 4c. Resolved Findings

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| AG-1 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of... | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. |
| S-1 | UNCHANGED | Spoofing | — | client-portal | L7 — Agent Ecosystem | An attacker replays a captured session cookie against client-portal, which does not bind the credential to... | High | Bind each session cookie to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| E-1 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read... | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. |
| T-1 | UNCHANGED | Tampering | — | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests... | Medium | Sign messages between auth-broker and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting any... |
| R-1 | UNCHANGED | Repudiation | — | intake-agent | L3 — Agent Framework | Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of... | Medium | Synchronise intake-agent and edge-gateway to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| LLM-1 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection... | Medium | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. |
| T-2 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | Low | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| I-1 | UNCHANGED | Information Disclosure | — | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that... | Low | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| S-2 | UNCHANGED | Spoofing | — | auth-broker | L6 — Security and Compliance | A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every... | Note | Replace the shared refresh token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| AG-1 | [] |
| S-1 | [] |
| E-1 | [] |
| T-1 | [] |
| R-1 | [] |
| LLM-1 | [] |
| T-2 | [] |
| I-1 | [] |
| S-2 | [] |
