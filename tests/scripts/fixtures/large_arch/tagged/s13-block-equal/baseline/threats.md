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
| E-1 | UNCHANGED | Elevation of Privilege | — | model-gateway | L1 — Foundation Model | Role claims carried in the model API key presented to model-gateway are honoured without confirmation... | Critical | Resolve roles for model-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| S-1 | UNCHANGED | Spoofing | trust_exploitation | tool-server-1 | L3 — Agent Framework | A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every... | High | Replace the shared tool API key with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| D-1 | UNCHANGED | Denial of Service | resource_competition | tool-server-1 | L3 — Agent Framework | A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and... | High | Set explicit concurrency and queue limits on tool-server-1, shed load with a clear status when saturated and apply per-caller quotas. |
| T-1 | UNCHANGED | Tampering | — | model-gateway | L1 — Foundation Model | Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential... | Medium | Keep the configuration of model-gateway in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-2 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | Low | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| I-1 | UNCHANGED | Information Disclosure | — | vector-store-a | L2 — Data Operations | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that... | Low | Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove... |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| E-1 | [] |
| S-1 | [] |
| D-1 | [] |
| T-1 | [] |
| T-2 | [] |
| I-1 | [] |
