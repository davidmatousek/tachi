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
| S-1 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every... | Critical | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| MI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste... | Critical | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. |
| I-1 | UNCHANGED | Information Disclosure | — | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that... | High | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| E-1 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read... | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. |
| AG-1 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of... | High | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. |
| T-1 | UNCHANGED | Tampering | — | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests... | Medium | Sign messages between auth-broker and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting any... |
| D-1 | UNCHANGED | Denial of Service | — | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it... | Medium | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| LLM-1 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection... | Medium | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. |
| R-1 | UNCHANGED | Repudiation | — | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Low | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| S-1 | [] |
| MI-1 | [] |
| I-1 | [] |
| E-1 | [] |
| AG-1 | [] |
| T-1 | [] |
| D-1 | [] |
| LLM-1 | [] |
| R-1 | [] |
