---
schema_version: "1.4"
date: "2026-11-23"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-11-23T10-00-00"
baseline:
  source: "baseline/threats.md"
  date: "2026-11-09"
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model — Brindle Freight Platform

## Section 1: Architecture Overview

A multi-agent platform that turns operator requests into planned, reviewed and audited shipment actions.

### Components

| Component | Type | Description |
|-----------|------|-------------|
| client-portal | External Entity | Browser front end where operators submit shipment requests and approve agent proposals |
| edge-gateway | Process | Ingress proxy that terminates TLS, applies request limits and screens prompts before the intake agent |
| auth-broker | Process | Token broker that validates operator and partner credentials and mints short-lived session grants |
| intake-agent | Process | LLM-backed agent that turns free-text requests into structured shipment tasks and answers operators |
| planner-agent | Process | Planning agent that decomposes tasks, selects tools and assigns subtasks to the router |
| worker-2 | Process | Worker agent that optimises routes and looks up carrier rates through the tool server |
| tool-server-1 | Process | Tool server that exposes carrier rate, booking, label and customs tools to the agents |
| model-gateway | Process | Gateway that fronts the hosted foundation models and enforces per-agent quotas |
| vector-store-a | Data Store | Vector database holding embedded carrier documents and ticket history |
| audit-ledger | Data Store | Append-only ledger of approvals, tool calls and administrative actions |

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Public Internet | Untrusted | client-portal |
| Edge DMZ | Semi-trusted | edge-gateway, auth-broker |
| Agent Runtime Zone | Trusted | intake-agent, planner-agent, worker-2, tool-server-1, model-gateway |
| Data Zone | Trusted | vector-store-a |
| Operations Zone | Trusted | audit-ledger |

---

## Section 2: STRIDE Findings

### Spoofing (S)

#### S-1 — A shared or long-lived tool API key on tool-server-1...

| Field | Value |
|---|---|
| **id** | S-1 |
| **category** | stride |
| **component** | tool-server-1 |
| **dfd_element_type** | Process |
| **threat** | A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. The exposure follows from how tool-server-1 receives tool call arguments and results from worker-2 and hands them to the next stage without an independent check. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. |
| **likelihood** | MEDIUM |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Replace the shared tool API key with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks within the rotation window. Track coverage of this control as a release criterion for tool-server-1 and record any exception with an expiry date. |

### Tampering (T)

#### T-1 — Configuration of model-gateway can be rewritten by any...

| Field | Value |
|---|---|
| **id** | T-1 |
| **category** | stride |
| **component** | model-gateway |
| **dfd_element_type** | Process |
| **threat** | Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential, silently changing how prompts and completions are handled. The weakness sits at layer Foundation Model of the stack, so every workflow that depends on prompts and completions inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. |
| **likelihood** | MEDIUM |
| **impact** | MEDIUM |
| **risk_level** | Medium |
| **mitigation** | Keep the configuration of model-gateway in a versioned, access-controlled repository, require review for changes and alert on drift from the approved revision. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |

#### T-2 — Serialised objects arriving from worker-2 are...

| Field | Value |
|---|---|
| **id** | T-2 |
| **category** | stride |
| **component** | vector-store-a |
| **dfd_element_type** | Data Store |
| **threat** | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour. vector-store-a runs in the Data Zone and exchanges embedded documents and metadata with worker-2 over PostgreSQL over TLS, so anything able to reach worker-2 can also reach this weakness. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and LOW impact because the effect is contained and easy to reverse once it is noticed. |
| **likelihood** | MEDIUM |
| **impact** | LOW |
| **risk_level** | Low |
| **mitigation** | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

### Information Disclosure (I)

#### I-1 — embedded documents and metadata held by vector-store-a...

| Field | Value |
|---|---|
| **id** | I-1 |
| **category** | stride |
| **component** | vector-store-a |
| **dfd_element_type** | Data Store |
| **threat** | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position. Because vector-store-a serves the Data Zone, a single failure here reaches each consumer of embedded documents and metadata at once. The exposed material can be reused for follow-on attacks and may trigger notification duties if it covers customer data. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. |
| **likelihood** | LOW |
| **impact** | MEDIUM |
| **risk_level** | Low |
| **mitigation** | Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove network-position trust within the Data Zone. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

### Denial of Service (D)

#### D-1 — A burst of requests exhausts the connection pool of...

| Field | Value |
|---|---|
| **id** | D-1 |
| **category** | stride |
| **component** | tool-server-1 |
| **dfd_element_type** | Process |
| **threat** | A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and blocks legitimate use of tool call arguments and results. Because tool-server-1 serves the Agent Runtime Zone, a single failure here reaches each consumer of tool call arguments and results at once. Operators lose the ability to book or amend shipments while the condition lasts, and recovery depends on manual intervention. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. |
| **likelihood** | MEDIUM |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Set explicit concurrency and queue limits on tool-server-1, shed load with a clear status when saturated and apply per-caller quotas. Track coverage of this control as a release criterion for tool-server-1 and record any exception with an expiry date. |

### Elevation of Privilege (E)

#### E-1 — Role claims carried in the model API key presented to...

| Field | Value |
|---|---|
| **id** | E-1 |
| **category** | stride |
| **component** | model-gateway |
| **dfd_element_type** | Process |
| **threat** | Role claims carried in the model API key presented to model-gateway are honoured without confirmation against the authoritative directory. The weakness sits at layer Foundation Model of the stack, so every workflow that depends on prompts and completions inherits the exposure. Once the boundary is crossed the attacker can reach administrative functions and persist there. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. |
| **likelihood** | HIGH |
| **impact** | HIGH |
| **risk_level** | Critical |
| **mitigation** | Resolve roles for model-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

---

## Section 4a: Correlated Findings

**Cross-agent correlations detected**: NONE in this baseline.

---

## Section 6: Carry-Forward / Resolved (Baseline Mode)

**Mode**: BASELINE.

| Lifecycle Status | Count |
|------------------|-------|
| `[UNCHANGED]` | 6 |
| `[NEW]` | 0 |
| `[UPDATED]` | 0 |
| `[RESOLVED]` | 0 |

---

## Section 7: Recommended Actions (Prioritized)

### CRITICAL Priority (immediate action)

1. **E-1 — Role claims carried in the model API key presented to...**: Resolve roles for model-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller.

### HIGH Priority (within sprint)

2. **S-1 — A shared or long-lived tool API key on tool-server-1...**: Replace the shared tool API key with per-workload identities that rotate automatically, and alert when one identity authenticates from two...
3. **D-1 — A burst of requests exhausts the connection pool of...**: Set explicit concurrency and queue limits on tool-server-1, shed load with a clear status when saturated and apply per-caller quotas.

### MEDIUM Priority (next quarter)

4. **T-1 — Configuration of model-gateway can be rewritten by any...**: Keep the configuration of model-gateway in a versioned, access-controlled repository, require review for changes and alert on drift from the...

### LOW Priority (backlog)

5. **T-2 — Serialised objects arriving from worker-2 are...**: Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it.
6. **I-1 — embedded documents and metadata held by vector-store-a...**: Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove...

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
