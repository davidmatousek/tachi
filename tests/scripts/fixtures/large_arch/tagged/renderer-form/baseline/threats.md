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
| T-1 | UNCHANGED | Tampering | — | planner-agent | L3 — Agent Framework | Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so... | Critical | Validate task plans and tool selections against a strict schema at the boundary of planner-agent, reject unknown fields and normalise encodings... |
| D-2 | UNCHANGED | Denial of Service | — | vector-store-a | L2 — Data Operations | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay... | Critical | Add jittered exponential backoff and a retry budget to worker-2, and enable a circuit breaker so that vector-store-a can recover. |
| T-2 | UNCHANGED | Tampering | — | planner-agent | L3 — Agent Framework | An attacker who can write to the channel between model-gateway and planner-agent modifies task plans and... | High | Sign messages between model-gateway and planner-agent with a per-service key and verify the signature and a monotonic counter before accepting any... |
| T-4 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | High | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-6 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Unsanitised embedded documents and metadata reach vector-store-a and are processed as trusted structure, so... | High | Validate embedded documents and metadata against a strict schema at the boundary of vector-store-a, reject unknown fields and normalise encodings... |
| D-1 | UNCHANGED | Denial of Service | resource_competition | tool-server-1 | L3 — Agent Framework | A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and... | High | Set explicit concurrency and queue limits on tool-server-1, shed load with a clear status when saturated and apply per-caller quotas. |
| E-1 | UNCHANGED | Elevation of Privilege | — | model-gateway | L1 — Foundation Model | Role claims carried in the model API key presented to model-gateway are honoured without confirmation... | High | Resolve roles for model-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| T-5 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a... | Medium | Protect exports and backups of embedded documents and metadata with write-once storage and dual approval for restore, and verify checksums against... |
| D-3 | UNCHANGED | Denial of Service | — | audit-ledger | L6 — Security and Compliance | Expensive queries over approval and tool call records can be triggered by any authorised caller of... | Medium | Enforce cost limits and pagination on queries to audit-ledger, run heavy work on a separate pool and cancel queries that exceed the budget. |
| S-1 | UNCHANGED | Spoofing | — | model-gateway | L1 — Foundation Model | An attacker replays a captured model API key against model-gateway, which does not bind the credential to... | Low | Bind each model API key to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| T-3 | UNCHANGED | Tampering | — | model-gateway | L1 — Foundation Model | Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential... | Low | Keep the configuration of model-gateway in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-7 | UNCHANGED | Tampering | — | audit-ledger | L6 — Security and Compliance | An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool... | Note | Sign messages between tool-server-1 and audit-ledger with a per-service key and verify the signature and a monotonic counter before accepting any... |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| T-1 | [] |
| D-2 | [] |
| T-2 | [] |
| T-4 | [] |
| T-6 | [] |
| D-1 | [safety] |
| E-1 | [secrets] |
| T-5 | [] |
| D-3 | [financial] |
| S-1 | [secrets] |
| T-3 | [secrets] |
| T-7 | [financial] |
