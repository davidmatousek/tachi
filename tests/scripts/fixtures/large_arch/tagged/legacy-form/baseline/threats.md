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
| T-3 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | Critical | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| E-1 | UNCHANGED | Elevation of Privilege | — | model-gateway | L1 — Foundation Model | Role claims carried in the model API key presented to model-gateway are honoured without confirmation... | Critical | Resolve roles for model-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| S-2 | UNCHANGED | Spoofing | — | model-gateway | L1 — Foundation Model | A compromised peer presents a forged service identity to model-gateway, and model-gateway accepts the claim... | High | Require mutual TLS between planner-agent and model-gateway and validate the full certificate chain, issuer and audience on every request instead... |
| T-1 | UNCHANGED | Tampering | — | planner-agent | L3 — Agent Framework | Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so... | High | Validate task plans and tool selections against a strict schema at the boundary of planner-agent, reject unknown fields and normalise encodings... |
| D-1 | UNCHANGED | Denial of Service | — | vector-store-a | L2 — Data Operations | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay... | High | Add jittered exponential backoff and a retry budget to worker-2, and enable a circuit breaker so that vector-store-a can recover. |
| T-2 | UNCHANGED | Tampering | — | model-gateway | L1 — Foundation Model | Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential... | Medium | Keep the configuration of model-gateway in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-4 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a... | Medium | Protect exports and backups of embedded documents and metadata with write-once storage and dual approval for restore, and verify checksums against... |
| S-1 | UNCHANGED | Spoofing | — | model-gateway | L1 — Foundation Model | An attacker replays a captured model API key against model-gateway, which does not bind the credential to... | Low | Bind each model API key to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| T-3 | [] |
| E-1 | [] |
| S-2 | [] |
| T-1 | [] |
| D-1 | [] |
| T-2 | [] |
| T-4 | [] |
| S-1 | [] |
