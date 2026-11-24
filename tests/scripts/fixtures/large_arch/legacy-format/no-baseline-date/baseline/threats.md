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
| S-1 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every... | High | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| I-1 | UNCHANGED | Information Disclosure | — | vector-store-a | L2 — Data Operations | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that... | High | Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove... |
| R-1 | UNCHANGED | Repudiation | — | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Medium | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| T-1 | UNCHANGED | Tampering | — | intake-agent | L3 — Agent Framework | Replay of an earlier valid update to free-text shipment requests reaches intake-agent because updates carry... | Low | Add a nonce and a short expiry to every update accepted by intake-agent, store seen nonces for the validity window and reject any repeat. |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| S-1 | [] |
| I-1 | [] |
| R-1 | [] |
| T-1 | [] |
