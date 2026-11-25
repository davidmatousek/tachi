---
schema_version: "1.4"
date: "2026-11-23"
input_format: "free-text"
classification: "confidential"
run_id: "2026-11-23T10-00-00"
baseline:
  source: "baseline/threats.md"
  date: "2026-11-09"
  finding_count: 6
  run_id: "2026-11-09T10-00-00"
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model Report

## 1. System Overview

Parsed summary of the architecture input for the Brindle Freight Platform: a multi-agent platform that turns operator requests into planned, reviewed and audited shipment actions. 10 components were identified across 5 trust zones. The inventory below is the scope of this threat model.

### Components

| Component | Type | MAESTRO Layer | Description |
|-----------|------|---------------|-------------|
| client-portal | External Entity | L7 — Agent Ecosystem | Browser front end where operators submit shipment requests and approve agent proposals |
| edge-gateway | Process | L4 — Deployment Infrastructure | Ingress proxy that terminates TLS, applies request limits and screens prompts before the intake agent |
| auth-broker | Process | L6 — Security and Compliance | Token broker that validates operator and partner credentials and mints short-lived session grants |
| intake-agent | Process | L3 — Agent Framework | LLM-backed agent that turns free-text requests into structured shipment tasks and answers operators |
| planner-agent | Process | L3 — Agent Framework | Planning agent that decomposes tasks, selects tools and assigns subtasks to the router |
| worker-2 | Process | L3 — Agent Framework | Worker agent that optimises routes and looks up carrier rates through the tool server |
| tool-server-1 | Process | L3 — Agent Framework | Tool server that exposes carrier rate, booking, label and customs tools to the agents |
| model-gateway | Process | L1 — Foundation Model | Gateway that fronts the hosted foundation models and enforces per-agent quotas |
| vector-store-a | Data Store | L2 — Data Operations | Vector database holding embedded carrier documents and ticket history |
| audit-ledger | Data Store | L6 — Security and Compliance | Append-only ledger of approvals, tool calls and administrative actions |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| client-portal | edge-gateway | Operator requests and session cookies | HTTPS (TLS 1.3) |
| edge-gateway | auth-broker | Token introspection requests | gRPC over mTLS |
| edge-gateway | intake-agent | Screened operator requests | HTTP/2 over mTLS |
| planner-agent | model-gateway | Prompts and completions | HTTPS (TLS 1.3) |
| worker-2 | tool-server-1 | Tool calls (JSON-RPC) | HTTPS (TLS 1.3) |
| worker-2 | vector-store-a | Similarity queries | PostgreSQL over TLS |
| tool-server-1 | audit-ledger | Tool call records | gRPC over mTLS |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Runtime | Python | 3.12 |
| Agent framework | Graph-based agent orchestration library | 0.2 |
| Gateway | Envoy proxy | 1.29 |
| Identity | OIDC with ES256 JWTs | RFC 7519 |
| Messaging | NATS JetStream | 2.10 |
| Database | PostgreSQL with a vector extension | 16 |
| Object storage | S3-compatible archive | unknown |
| Model hosting | Hosted foundation model API | unknown |
| Tool protocol | MCP over HTTP (JSON-RPC) | 2025-06 |
| Observability | OpenTelemetry collector | 0.98 |
| Front end | React single-page application | 18 |
| Policy | Rule-based policy engine | unknown |

---

## 2. Trust Boundaries

Trust zones group components that share a security posture. Each crossing between zones is a priority target for analysis.

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Public Internet | Untrusted | client-portal |
| Edge DMZ | Semi-trusted | edge-gateway, auth-broker |
| Agent Runtime Zone | Trusted | intake-agent, planner-agent, worker-2, tool-server-1, model-gateway |
| Data Zone | Trusted | vector-store-a |
| Operations Zone | Trusted | audit-ledger |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Public Internet to Edge DMZ | Public Internet | Edge DMZ | client-portal -> edge-gateway | TLS 1.3 termination, request size limits, webhook signature checks |
| Edge DMZ to Agent Runtime Zone | Edge DMZ | Agent Runtime Zone | edge-gateway -> intake-agent | Mutual TLS, token validation, prompt screening |
| Agent Runtime Zone to Data Zone | Agent Runtime Zone | Data Zone | worker-2 -> vector-store-a | Per-service database roles, TLS to the database, query allowlists |
| Agent Runtime Zone to Operations Zone | Agent Runtime Zone | Operations Zone | tool-server-1 -> audit-ledger | Mutual TLS, write-only trace and audit endpoints |

---

## 3. STRIDE Tables

One table per STRIDE category. Every row carries a delta status against the baseline run. RESOLVED findings are listed in Section 4c.

**Risk level computation (OWASP 3x3 matrix):**

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

### 3.1 Spoofing (S)

Threats where an attacker pretends to be something or someone else.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| S-1 | UNCHANGED | client-portal | L7 — Agent Ecosystem | An attacker replays a captured session cookie against client-portal, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller. The exposure follows from how client-portal receives operator requests and approval decisions from edge-gateway and hands them to the next stage without an independent check. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Bind each session cookie to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different channel than the one it was issued to. Track coverage of this control as a release criterion for client-portal and record any exception with an expiry date. |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| T-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | HIGH | HIGH | Critical | Sign messages between auth-broker and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting any change. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |

### 3.3 Repudiation (R)

Threats where an actor denies an action without the system being able to prove otherwise.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| R-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. Without reliable records an investigation cannot establish who acted, so disputes about responsibility stay unresolved. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and LOW impact because the effect is contained and easy to reverse once it is noticed. | MEDIUM | LOW | Low | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. Verify the control in a pre-production exercise and review it again after any change to edge-gateway. |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| I-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. The exposed material can be reused for follow-on attacks and may trigger notification duties if it covers customer data. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | HIGH | HIGH | Critical | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any exposure. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| D-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. Operators lose the ability to book or amend shipments while the condition lasts, and recovery depends on manual intervention. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | HIGH | MEDIUM | High | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. Track coverage of this control as a release criterion for edge-gateway and record any exception with an expiry date. |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| E-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Once the boundary is crossed the attacker can reach administrative functions and persist there. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | HIGH | MEDIUM | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

---

## 4. AI Threat Tables

Findings from the AI-specific agents. Each row adds an OWASP reference to the standard fields.

### 4.1 Agentic Threats (AG)

Threats arising from autonomous agent behavior, tool use and the way people rely on agent output.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|

### 4.2 LLM Threats (LLM)

Threats to and through the language models: injection, poisoning, extraction, unsafe output and misinformation.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|

---

## 4a. Correlated Findings

Cross-agent correlation groups link findings from different agent categories that target the same component. Original findings stay in Sections 3 and 4; groups are additive.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|

---

## 4b. Findings by Agentic Pattern

**Multi-agent gate predicate evaluation**:
- Condition (a): ≥2 agentic or LLM components: TRUE (7 components)
- Condition (b): inter-agent data flow between two agentic components: TRUE
- Condition (c): explicit multi-agent keyword in the architecture: TRUE
- **Predicate result: TRUE**

| Pattern | Count | Findings |
|---------|-------|----------|

---

## 4c. Resolved Findings

Findings from the baseline that no longer apply in the current architecture. Each keeps its original ID, description and last-known risk level.

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|

---

## 5. Coverage Matrix

Each cell is the deduplicated finding count for a component and category (a correlation group counts once). — means analyzed with no findings; n/a means the category does not apply.

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| client-portal | 1 | n/a | — | n/a | n/a | n/a | n/a | n/a | 1 |
| edge-gateway | — | 1 | 1 | 1 | 1 | 1 | n/a | — | 5 |
| auth-broker | — | — | — | — | — | — | n/a | n/a | 0 |
| intake-agent | — | — | — | — | — | — | — | — | 0 |
| planner-agent | — | — | — | — | — | — | — | — | 0 |
| worker-2 | — | — | — | — | — | — | — | — | 0 |
| tool-server-1 | — | — | — | — | — | — | — | — | 0 |
| model-gateway | — | — | — | — | — | — | n/a | — | 0 |
| vector-store-a | n/a | — | n/a | — | — | n/a | n/a | — | 0 |
| audit-ledger | n/a | — | — | — | — | n/a | n/a | n/a | 0 |
| **Total** | **1** | **1** | **1** | **1** | **1** | **1** | **0** | **0** | **6** |

Counts reflect deduplicated findings. 0 correlation groups merged 0 individual findings.

---

## 5a. Coverage Gate Results

Coverage gate passed — all required threat categories evaluated for every component.

### Coverage Requirements Matrix

| Component | Determined Type | Required Categories | Evaluated | Gaps |
|-----------|-----------------|---------------------|-----------|------|
| client-portal | external_entity | spoofing, repudiation | 2 / 2 | None |
| edge-gateway | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, llm | 7 / 7 | None |
| auth-broker | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | 6 / 6 | None |
| intake-agent | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm | 8 / 8 | None |
| planner-agent | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm | 8 / 8 | None |
| worker-2 | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm | 8 / 8 | None |
| tool-server-1 | mcp_server | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm | 8 / 8 | None |
| model-gateway | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, llm | 7 / 7 | None |
| vector-store-a | data_store | tampering, info-disclosure, denial-of-service, llm | 4 / 4 | None |
| audit-ledger | data_store | tampering, repudiation, info-disclosure, denial-of-service | 4 / 4 | None |

---

## 6. Risk Summary

Aggregate counts of findings by risk level, computed with the OWASP 3x3 matrix (likelihood x impact).

### Risk Calibration Matrix

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L1 — Foundation Model | 0 | Analyzed — no findings this scan |
| L2 — Data Operations | 0 | Analyzed — no findings this scan |
| L3 — Agent Framework | 0 | Analyzed — no findings this scan |
| L4 — Deployment Infrastructure | 5 | Critical |
| L5 — Evaluation and Observability | 0 | Not applicable — no components map to this layer |
| L6 — Security and Compliance | 0 | Analyzed — no findings this scan |
| L7 — Agent Ecosystem | 1 | High |

Risk summary counts below reflect deduplicated findings. A correlation group counts as one threat at its group risk level.

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 2 | 33.3% |
| High | 3 | 50.0% |
| Medium | 0 | 0.0% |
| Low | 1 | 16.7% |
| Note | 0 | 0.0% |
| **Total** | **6** | **100%** |

---

## 7. Recommended Actions

All findings sorted by risk level descending, then by table order. Critical and High findings should be addressed before deployment.

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| T-1 | UNCHANGED | Tampering | — | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests... | Critical | Sign messages between auth-broker and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting any... |
| I-1 | UNCHANGED | Information Disclosure | — | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that... | Critical | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| S-1 | UNCHANGED | Spoofing | — | client-portal | L7 — Agent Ecosystem | An attacker replays a captured session cookie against client-portal, which does not bind the credential to... | High | Bind each session cookie to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| D-1 | UNCHANGED | Denial of Service | — | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it... | High | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| E-1 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read... | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. |
| R-1 | UNCHANGED | Repudiation | — | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Low | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |

---

## 8. Delta Summary

The lifecycle of every finding relative to the baseline run. Section 4c lists the resolved findings.

### Finding Lifecycle

| Status | Count | Description |
|--------|-------|-------------|
| NEW | 0 | Findings discovered in this run with no baseline match |
| UNCHANGED | 6 | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | 0 | Findings with changed context since baseline |
| RESOLVED | 0 | Baseline findings no longer applicable (see Section 4c for details) |
| **Total** | **6** | Sum of all findings (active + resolved) |

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | baseline/threats.md |
| Date | 2026-11-09 |
| Baseline Findings | 6 |
| Run ID | 2026-11-09T10-00-00 |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| T-1 | [] |
| I-1 | [] |
| S-1 | [] |
| D-1 | [] |
| E-1 | [] |
| R-1 | [] |
