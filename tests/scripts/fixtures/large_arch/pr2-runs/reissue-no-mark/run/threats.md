---
schema_version: "1.4"
date: "2026-11-23"
input_format: "free-text"
classification: "confidential"
run_id: "2026-11-23T10-00-00"
baseline:
  source: "baseline/threats.md"
  date: "2026-11-09"
  finding_count: 40
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
| S-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. The exposure follows from how edge-gateway receives inbound API requests from auth-broker and hands them to the next stage without an independent check. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | LOW | MEDIUM | Low | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks within the rotation window. Track coverage of this control as a release criterion for edge-gateway and record any exception with an expiry date. |
| S-3 | UNCHANGED | auth-broker | L6 — Security and Compliance | A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. Because auth-broker serves the Edge DMZ, a single failure here reaches each consumer of credential assertions and session grants at once. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | MEDIUM | MEDIUM | Medium | Replace the shared refresh token with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks within the rotation window. Track coverage of this control as a release criterion for auth-broker and record any exception with an expiry date. |
| S-4 | UNCHANGED | tool-server-1 | L3 — Agent Framework | A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. tool-server-1 runs in the Agent Runtime Zone and exchanges tool call arguments and results with audit-ledger over gRPC over mTLS, so anything able to reach audit-ledger can also reach this weakness. Until the credential is revoked the attacker acts with the victim's authority, and the audit trail attributes the actions to the victim. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | HIGH | MEDIUM | High | Replace the shared tool API key with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks within the rotation window. Verify the control in a pre-production exercise and review it again after any change to tool-server-1. |
| S-6 | NEW | tool-server-1 | L3 — Agent Framework | An unauthenticated callback or health route on tool-server-1 accepts requests that downstream code treats as if they had come from audit-ledger. audit-ledger trusts tool-server-1 to pass tool call arguments and results along unchanged, which removes the second chance to catch the problem downstream. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | LOW | HIGH | Medium | Remove implicit trust in route names: authenticate every route of tool-server-1, including callbacks and health checks, and drop requests that carry no verified caller identity. Confirm the fix with a targeted test against tool-server-1, and keep the evidence with the change record for later audits. |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| T-1 | UNCHANGED | auth-broker | L6 — Security and Compliance | Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores. The weakness sits at layer Security and Compliance of the stack, so every workflow that depends on credential assertions and session grants inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Protect exports and backups of credential assertions and session grants with write-once storage and dual approval for restore, and verify checksums against a separately held manifest. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| T-2 | UNCHANGED | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour. vector-store-a runs in the Data Zone and exchanges embedded documents and metadata with worker-2 over PostgreSQL over TLS, so anything able to reach worker-2 can also reach this weakness. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | LOW | MEDIUM | Low | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| T-3 | UNCHANGED | audit-ledger | L6 — Security and Compliance | An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their own. audit-ledger runs in the Operations Zone and exchanges approval and tool call records with tool-server-1 over gRPC over mTLS, so anything able to reach tool-server-1 can also reach this weakness. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and LOW impact because the effect is contained and easy to reverse once it is noticed. | MEDIUM | LOW | Low | Sign messages between tool-server-1 and audit-ledger with a per-service key and verify the signature and a monotonic counter before accepting any change. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| T-5 | NEW | auth-broker | L6 — Security and Compliance | Unsanitised credential assertions and session grants reach auth-broker and are processed as trusted structure, so crafted input changes how later steps interpret the record. The weakness sits at layer Security and Compliance of the stack, so every workflow that depends on credential assertions and session grants inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | LOW | MEDIUM | Low | Validate credential assertions and session grants against a strict schema at the boundary of auth-broker, reject unknown fields and normalise encodings before any downstream use. Confirm the fix with a targeted test against auth-broker, and keep the evidence with the change record for later audits. |

### 3.3 Repudiation (R)

Threats where an actor denies an action without the system being able to prove otherwise.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| R-1 | UNCHANGED | intake-agent | L3 — Agent Framework | Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of actions on free-text shipment requests cannot be reconstructed reliably. Because intake-agent serves the Agent Runtime Zone, a single failure here reaches each consumer of free-text shipment requests at once. Without reliable records an investigation cannot establish who acted, so disputes about responsibility stay unresolved. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and LOW impact because the effect is contained and easy to reverse once it is noticed. | HIGH | LOW | Medium | Synchronise intake-agent and edge-gateway to a trusted time source, record monotonic sequence numbers with every event and alert when drift exceeds one second. Verify the control in a pre-production exercise and review it again after any change to intake-agent. |
| R-3 | UNCHANGED | tool-server-1 | L3 — Agent Framework | Operators approve changes to tool call arguments and results through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on tool call arguments and results inherits the exposure. Incident responders lose the sequence of events, which delays containment and weakens any later accountability claim. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | LOW | MEDIUM | Low | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| R-4 | UNCHANGED | tool-server-1 | L3 — Agent Framework | Actions taken through tool-server-1 are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to tool call arguments and results. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on tool call arguments and results inherits the exposure. Incident responders lose the sequence of events, which delays containment and weakens any later accountability claim. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | LOW | HIGH | Medium | Log the verified principal, request identifier, source address and outcome for every state change in tool-server-1, and ship the records to the audit ledger. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| I-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. The exposed material can be reused for follow-on attacks and may trigger notification duties if it covers customer data. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any exposure. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| I-3 | UNCHANGED | worker-2 | L3 — Agent Framework | Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to the logging pipeline can read content meant for one tenant. Because worker-2 serves the Agent Runtime Zone, a single failure here reaches each consumer of work orders and route candidates at once. Disclosure is silent, so the affected parties learn about it only when the information is misused. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | MEDIUM | MEDIUM | Medium | Redact or tokenise sensitive fields before worker-2 emits logs and traces, and restrict the logging pipeline to the roles that need it. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| I-4 | UNCHANGED | model-gateway | L1 — Foundation Model | Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes another tenant's prompts and completions. model-gateway runs in the Agent Runtime Zone and exchanges prompts and completions with planner-agent over HTTPS (TLS 1.3), so anything able to reach planner-agent can also reach this weakness. Disclosure is silent, so the affected parties learn about it only when the information is misused. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. Track coverage of this control as a release criterion for model-gateway and record any exception with an expiry date. |
| I-5 | NEW | vector-store-a | L2 — Data Operations | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position. The exposure follows from how vector-store-a receives embedded documents and metadata from worker-2 and hands them to the next stage without an independent check. The exposed material can be reused for follow-on attacks and may trigger notification duties if it covers customer data. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | HIGH | HIGH | Critical | Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove network-position trust within the Data Zone. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| D-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. Operators lose the ability to book or amend shipments while the condition lasts, and recovery depends on manual intervention. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | MEDIUM | MEDIUM | Medium | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. Track coverage of this control as a release criterion for edge-gateway and record any exception with an expiry date. |
| D-2 | UNCHANGED | intake-agent | L3 — Agent Framework | A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests. Because intake-agent serves the Agent Runtime Zone, a single failure here reaches each consumer of free-text shipment requests at once. The outage propagates to dependent agents, which stall or retry and prolong the disruption. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | HIGH | MEDIUM | High | Cap payload size, nesting depth and parse time in intake-agent, and reject requests that exceed the limits before allocation. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| D-3 | UNCHANGED | vector-store-a | L2 — Data Operations | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage. Because vector-store-a serves the Data Zone, a single failure here reaches each consumer of embedded documents and metadata at once. The outage propagates to dependent agents, which stall or retry and prolong the disruption. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and LOW impact because the effect is contained and easy to reverse once it is noticed. | HIGH | LOW | Medium | Add jittered exponential backoff and a retry budget to worker-2, and enable a circuit breaker so that vector-store-a can recover. Confirm the fix with a targeted test against vector-store-a, and keep the evidence with the change record for later audits. |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| E-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Once the boundary is crossed the attacker can reach administrative functions and persist there. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| E-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Role claims carried in the service token presented to intake-agent are honoured without confirmation against the authoritative directory. edge-gateway trusts intake-agent to pass free-text shipment requests along unchanged, which removes the second chance to catch the problem downstream. The caller gains rights that were never granted, which allows reading and changing data across tenants and approvals. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | LOW | HIGH | Medium | Resolve roles for intake-agent from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| E-3 | UNCHANGED | planner-agent | L3 — Agent Framework | planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources. Because planner-agent serves the Agent Runtime Zone, a single failure here reaches each consumer of task plans and tool selections at once. Once the boundary is crossed the attacker can reach administrative functions and persist there. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Reduce the permissions of planner-agent to the minimum for task plans and tool selections, drop capabilities it does not use and review the grants on a schedule. Verify the control in a pre-production exercise and review it again after any change to planner-agent. |

---

## 4. AI Threat Tables

Findings from the AI-specific agents. Each row adds an OWASP reference to the standard fields.

### 4.1 Agentic Threats (AG)

Threats arising from autonomous agent behavior, tool use and the way people rely on agent output.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|
| AG-1 | UNCHANGED | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. The agent acts at machine speed on behalf of the operator, so a single manipulated decision can cause many unwanted changes before a person notices. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | ASI-06 | HIGH | HIGH | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. Verify the control in a pre-production exercise and review it again after any change to intake-agent. |
| AG-2 | UNCHANGED | planner-agent | L3 — Agent Framework | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful. planner-agent runs in the Agent Runtime Zone and exchanges task plans and tool selections with model-gateway over HTTPS (TLS 1.3), so anything able to reach model-gateway can also reach this weakness. Actions taken by the agent look legitimate in the logs, which slows detection and complicates rollback. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | ASI-10 | HIGH | HIGH | Critical | Set hard limits on steps, tool calls, runtime and spend for planner-agent, stop on breach and report the stop reason to the operator. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| AG-3 | UPDATED | tool-server-1 | L3 — Agent Framework | Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task. audit-ledger trusts tool-server-1 to pass tool call arguments and results along unchanged, which removes the second chance to catch the problem downstream. The agent acts at machine speed on behalf of the operator, so a single manipulated decision can cause many unwanted changes before a person notices. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | ASI-06 | HIGH | HIGH | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by tool-server-1. Track coverage of this control as a release criterion for tool-server-1 and record any exception with an expiry date. |
| AG-4 | UNCHANGED | tool-server-1 | L3 — Agent Framework | tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded. The exposure follows from how tool-server-1 receives tool call arguments and results from worker-2 and hands them to the next stage without an independent check. Actions taken by the agent look legitimate in the logs, which slows detection and complicates rollback. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and LOW impact because the effect is contained and easy to reverse once it is noticed. | ASI-08 | HIGH | LOW | Medium | Make the actions of tool-server-1 idempotent with request keys, cap retries and require confirmation before repeating any action with external effects. Verify the control in a pre-production exercise and review it again after any change to tool-server-1. |
| AG-5 | UNCHANGED | tool-server-1 | L3 — Agent Framework | tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed. tool-server-1 runs in the Agent Runtime Zone and exchanges tool call arguments and results with audit-ledger over gRPC over mTLS, so anything able to reach audit-ledger can also reach this weakness. The agent acts at machine speed on behalf of the operator, so a single manipulated decision can cause many unwanted changes before a person notices. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | ASI-02 | MEDIUM | MEDIUM | Medium | Validate every argument against the tool schema in tool-server-1 before the call, enforce allowlists of values and reject free-form commands. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| AG-6 | NEW | planner-agent | L3 — Agent Framework | planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives. planner-agent runs in the Agent Runtime Zone and exchanges task plans and tool selections with model-gateway over HTTPS (TLS 1.3), so anything able to reach model-gateway can also reach this weakness. Actions taken by the agent look legitimate in the logs, which slows detection and complicates rollback. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and LOW impact because the effect is contained and easy to reverse once it is noticed. | ASI-08 | HIGH | LOW | Medium | Apply per-task and per-tool quotas to planner-agent, alert on unusual call patterns and block calls once a cost ceiling is reached. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| AGP-01 | UNCHANGED | worker-2 | L3 — Agent Framework | Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on work orders and route candidates inherits the exposure. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | ASI-07 | MEDIUM | MEDIUM | Medium | Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate. Recommended controls: behavioural baselining of the collective agent system and alerts on coordinated bursts. |
| TE-1 | UNCHANGED | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants. edge-gateway trusts intake-agent to pass free-text shipment requests along unchanged, which removes the second chance to catch the problem downstream. The effect builds over time as users come to rely on the agent's tone instead of its evidence. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | ASI-09 | LOW | HIGH | Medium | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. Track coverage of this control as a release criterion for intake-agent and record any exception with an expiry date. |
| TE-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. People defer to the agent more than its reliability justifies, which weakens the human oversight the design depends on. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and LOW impact because the effect is contained and easy to reverse once it is noticed. | ASI-09 | MEDIUM | LOW | Low | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. Confirm the fix with a targeted test against intake-agent, and keep the evidence with the change record for later audits. |

### 4.2 LLM Threats (LLM)

Threats to and through the language models: injection, poisoning, extraction, unsafe output and misinformation.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|
| LLM-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. The answers or side effects of the model then serve the attacker's goal, and the behaviour can be repeated against every user of the component. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM01:2026 | HIGH | HIGH | Critical | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. Verify the control in a pre-production exercise and review it again after any change to edge-gateway. |
| LLM-2 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Prompt content logged by auth-broker is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. The answers or side effects of the model then serve the attacker's goal, and the behaviour can be repeated against every user of the component. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM01:2026 | HIGH | MEDIUM | High | Mark replayed prompts as untrusted when edge-gateway processes them, and exclude logged content from any privileged instruction slot. Track coverage of this control as a release criterion for edge-gateway and record any exception with an expiry date. |
| LLM-3 | UNCHANGED | intake-agent | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text. Because intake-agent serves the Agent Runtime Zone, a single failure here reaches each consumer of free-text shipment requests at once. The failure is probabilistic, so it may pass pre-release testing and appear only under adversarial input. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM01:2026 | HIGH | MEDIUM | High | Normalise and decode inputs before filtering in intake-agent, apply semantic checks instead of keyword lists and review filter misses weekly. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| LLM-4 | UNCHANGED | tool-server-1 | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks plain English text. audit-ledger trusts tool-server-1 to pass tool call arguments and results along unchanged, which removes the second chance to catch the problem downstream. The failure is probabilistic, so it may pass pre-release testing and appear only under adversarial input. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and LOW impact because the effect is contained and easy to reverse once it is noticed. | OWASP LLM01:2026 | MEDIUM | LOW | Low | Normalise and decode inputs before filtering in tool-server-1, apply semantic checks instead of keyword lists and review filter misses weekly. Confirm the fix with a targeted test against tool-server-1, and keep the evidence with the change record for later audits. |
| LLM-5 | UNCHANGED | model-gateway | L1 — Foundation Model | Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system. The weakness sits at layer Foundation Model of the stack, so every workflow that depends on prompts and completions inherits the exposure. The failure is probabilistic, so it may pass pre-release testing and appear only under adversarial input. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM01:2026 | MEDIUM | HIGH | High | Score retrieved passages for instruction-like content before model-gateway uses them, attribute every passage to its source and cap how much any one source contributes. Track coverage of this control as a release criterion for model-gateway and record any exception with an expiry date. |
| LLM-6 | UPDATED | vector-store-a | L2 — Data Operations | Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict authoritative sources. vector-store-a runs in the Data Zone and exchanges embedded documents and metadata with worker-2 over PostgreSQL over TLS, so anything able to reach worker-2 can also reach this weakness. The failure is probabilistic, so it may pass pre-release testing and appear only under adversarial input. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM05:2026 | HIGH | HIGH | Critical | Restrict write access to the ingestion path of vector-store-a, sign documents from authoritative sources and prefer them when answers conflict. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| LLM-7 | NEW | worker-2 | L3 — Agent Framework | worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on work orders and route candidates inherits the exposure. The failure is probabilistic, so it may pass pre-release testing and appear only under adversarial input. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM01:2026 | HIGH | HIGH | Critical | Restrict what worker-2 may fetch to an allowlist of domains and types, fetch through a sandbox and present the results as untrusted data. Confirm the fix with a targeted test against worker-2, and keep the evidence with the change record for later audits. |
| OI-1 | UNCHANGED | intake-agent | L3 — Agent Framework | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests. edge-gateway trusts intake-agent to pass free-text shipment requests along unchanged, which removes the second chance to catch the problem downstream. The unsafe output reaches an interpreter that trusts it, turning a text generation problem into code or request execution. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and LOW impact because the effect is contained and easy to reverse once it is noticed. | OWASP LLM10:2026 | MEDIUM | LOW | Low | Validate URLs from intake-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. Track coverage of this control as a release criterion for intake-agent and record any exception with an expiry date. |
| OI-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field flows straight into business logic. Because intake-agent serves the Agent Runtime Zone, a single failure here reaches each consumer of free-text shipment requests at once. Downstream components cannot tell the model's output from validated input, so no later layer is likely to catch it. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM10:2026 | MEDIUM | MEDIUM | Medium | Validate the output of intake-agent against a strict schema in edge-gateway, treat it as untrusted input and reject anything that fails. Verify the control in a pre-production exercise and review it again after any change to intake-agent. |
| OI-3 | UNCHANGED | worker-2 | L3 — Agent Framework | Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it. vector-store-a trusts worker-2 to pass work orders and route candidates along unchanged, which removes the second chance to catch the problem downstream. The unsafe output reaches an interpreter that trusts it, turning a text generation problem into code or request execution. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and LOW impact because the effect is contained and easy to reverse once it is noticed. | OWASP LLM10:2026 | LOW | LOW | Note | Strip remote resources from the output of worker-2 before display, proxy images through a controlled service and disable automatic loading. Verify the control in a pre-production exercise and review it again after any change to worker-2. |
| MI-1 | UNCHANGED | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. The mistake looks authoritative, so it is rarely questioned until a downstream party objects. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM07:2026 | LOW | MEDIUM | Low | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. Confirm the fix with a targeted test against intake-agent, and keep the evidence with the change record for later audits. |
| MI-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. Operators act on the wrong information, and the error is copied into shipments, documents and customer communication. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM07:2026 | LOW | MEDIUM | Low | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

---

## 4a. Correlated Findings

Cross-agent correlation groups link findings from different agent categories that target the same component. Original findings stay in Sections 3 and 4; groups are additive.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | I-1, LLM-1, LLM-2 | edge-gateway | Info-Disclosure: Secrets such as the bearer token for edge-gateway appear in...; Prompt-Injection: edge-gateway passes conversation history from earlier turns into...; Prompt-Injection: Prompt content logged by auth-broker is later replayed to... | Critical |
| CG-2 | R-1, E-2, AG-1 | intake-agent | Repudiation: Clock drift between intake-agent and edge-gateway leaves events in...; Privilege-Escalation: Role claims carried in the service token presented to intake-agent...; Agent-Autonomy: Memory written by intake-agent is trusted on later runs, so one... | Critical |
| CG-3 | E-3, AG-2 | planner-agent | Privilege-Escalation: planner-agent runs with broader permissions than its function...; Agent-Autonomy: planner-agent runs without a budget on steps or spend, so a loop... | Critical |
| CG-4 | I-3, LLM-7 | worker-2 | Info-Disclosure: Logs and traces emitted by worker-2 include raw work orders and...; Prompt-Injection: worker-2 follows links and files named in work orders and route... | Critical |
| CG-5 | R-3, AG-3 | tool-server-1 | Repudiation: Operators approve changes to tool call arguments and results...; Agent-Autonomy: Memory written by tool-server-1 is trusted on later runs, so one... | Critical |
| CG-6 | I-4, LLM-5 | model-gateway | Info-Disclosure: Cross-tenant filters on model-gateway are applied in application...; Prompt-Injection: Indirect injection through documents retrieved for model-gateway... | High |
| CG-7 | T-2, LLM-6 | vector-store-a | Tampering: Serialised objects arriving from worker-2 are deserialised by...; Data-Poisoning: Anyone who can write to the ingestion path of vector-store-a can... | Critical |

---

## 4b. Findings by Agentic Pattern

**Multi-agent gate predicate evaluation**:
- Condition (a): ≥2 agentic or LLM components: TRUE (7 components)
- Condition (b): inter-agent data flow between two agentic components: TRUE
- Condition (c): explicit multi-agent keyword in the architecture: TRUE
- **Predicate result: TRUE**

| Pattern | Count | Findings |
|---------|-------|----------|
| trust_exploitation | 4 | S-4, S-6, TE-1, TE-2 |
| agent_collusion | 1 | AGP-01 |
| emergent_behavior | 1 | AG-2 |

---

## 4c. Resolved Findings

Findings from the baseline that no longer apply in the current architecture. Each keeps its original ID, description and last-known risk level.

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|
| S-2 | legacy-batch-1 | An unauthenticated callback or health route on legacy-batch-1 accepts requests that downstream code treats... | High | Component 'legacy-batch-1' removed from architecture |
| R-2 | edge-gateway | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Low | Threat category no longer applicable to 'edge-gateway' (request logging moved to trace-collector) |
| I-2 | report-export-2 | Secrets such as the export credential for report-export-2 appear in process arguments and environment dumps... | Medium | Component 'report-export-2' removed from architecture |

---

## 5. Coverage Matrix

Each cell is the deduplicated finding count for a component and category (a correlation group counts once). — means analyzed with no findings; n/a means the category does not apply.

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| client-portal | — | n/a | — | n/a | n/a | n/a | n/a | n/a | 0 |
| edge-gateway | 1 | — | — | 1 | 1 | 1 | n/a | 1 | 5 |
| auth-broker | 1 | 2 | — | — | — | — | n/a | n/a | 3 |
| intake-agent | — | — | 1 | — | 1 | 1 | 3 | 5 | 11 |
| planner-agent | — | — | — | — | — | 1 | 2 | — | 3 |
| worker-2 | — | — | — | 1 | — | — | 1 | 2 | 4 |
| tool-server-1 | 2 | — | 2 | — | — | — | 3 | 1 | 8 |
| model-gateway | — | — | — | 1 | — | — | n/a | 1 | 2 |
| vector-store-a | n/a | 1 | n/a | 1 | 1 | n/a | n/a | 1 | 4 |
| audit-ledger | n/a | 1 | — | — | — | n/a | n/a | n/a | 1 |
| **Total** | **4** | **4** | **3** | **4** | **3** | **3** | **9** | **11** | **41** |

Counts reflect deduplicated findings. 7 correlation groups merged 16 individual findings.

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
| L1 — Foundation Model | 1 | High |
| L2 — Data Operations | 3 | Critical |
| L3 — Agent Framework | 21 | Critical |
| L4 — Deployment Infrastructure | 4 | Critical |
| L5 — Evaluation and Observability | 0 | Not applicable — no components map to this layer |
| L6 — Security and Compliance | 4 | High |
| L7 — Agent Ecosystem | 0 | Analyzed — no findings this scan |

Risk summary counts below reflect deduplicated findings. A correlation group counts as one threat at its group risk level.

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 7 | 21.2% |
| High | 6 (10 raw) | 18.2% |
| Medium | 11 (14 raw) | 33.3% |
| Low | 8 (10 raw) | 24.3% |
| Note | 1 | 3.0% |
| **Total** | **33 (42 raw)** | **100%** |

---

## 7. Recommended Actions

All findings sorted by risk level descending, then by table order. Critical and High findings should be addressed before deployment.

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| I-5 | NEW | Information Disclosure | — | vector-store-a | L2 — Data Operations | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that... | Critical | Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove... |
| AG-1 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of... | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. |
| AG-2 | UNCHANGED | Agentic | emergent_behavior | planner-agent | L3 — Agent Framework | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long... | Critical | Set hard limits on steps, tool calls, runtime and spend for planner-agent, stop on breach and report the stop reason to the operator. |
| AG-3 | UPDATED | Agentic | — | tool-server-1 | L3 — Agent Framework | Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of... | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by tool-server-1. |
| LLM-1 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection... | Critical | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. |
| LLM-6 | UPDATED | LLM | — | vector-store-a | L2 — Data Operations | Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict... | Critical | Restrict write access to the ingestion path of vector-store-a, sign documents from authoritative sources and prefer them when answers conflict. |
| LLM-7 | NEW | LLM | — | worker-2 | L3 — Agent Framework | worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking... | Critical | Restrict what worker-2 may fetch to an allowlist of domains and types, fetch through a sandbox and present the results as untrusted data. |
| S-4 | UNCHANGED | Spoofing | trust_exploitation | tool-server-1 | L3 — Agent Framework | A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every... | High | Replace the shared tool API key with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| T-1 | UNCHANGED | Tampering | — | auth-broker | L6 — Security and Compliance | Backups and exports of credential assertions and session grants on auth-broker are writable by operators... | High | Protect exports and backups of credential assertions and session grants with write-once storage and dual approval for restore, and verify... |
| I-1 | UNCHANGED | Information Disclosure | — | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that... | High | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| I-4 | UNCHANGED | Information Disclosure | — | model-gateway | L1 — Foundation Model | Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| D-2 | UNCHANGED | Denial of Service | — | intake-agent | L3 — Agent Framework | A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing... | High | Cap payload size, nesting depth and parse time in intake-agent, and reject requests that exceed the limits before allocation. |
| E-1 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read... | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. |
| E-3 | UNCHANGED | Elevation of Privilege | — | planner-agent | L3 — Agent Framework | planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and... | High | Reduce the permissions of planner-agent to the minimum for task plans and tool selections, drop capabilities it does not use and review the grants... |
| LLM-2 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | Prompt content logged by auth-broker is later replayed to edge-gateway for evaluation, carrying planted... | High | Mark replayed prompts as untrusted when edge-gateway processes them, and exclude logged content from any privileged instruction slot. |
| LLM-3 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain... | High | Normalise and decode inputs before filtering in intake-agent, apply semantic checks instead of keyword lists and review filter misses weekly. |
| LLM-5 | UNCHANGED | LLM | — | model-gateway | L1 — Foundation Model | Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer... | High | Score retrieved passages for instruction-like content before model-gateway uses them, attribute every passage to its source and cap how much any... |
| S-3 | UNCHANGED | Spoofing | — | auth-broker | L6 — Security and Compliance | A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every... | Medium | Replace the shared refresh token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| S-6 | NEW | Spoofing | trust_exploitation | tool-server-1 | L3 — Agent Framework | An unauthenticated callback or health route on tool-server-1 accepts requests that downstream code treats as... | Medium | Remove implicit trust in route names: authenticate every route of tool-server-1, including callbacks and health checks, and drop requests that... |
| R-1 | UNCHANGED | Repudiation | — | intake-agent | L3 — Agent Framework | Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of... | Medium | Synchronise intake-agent and edge-gateway to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| R-4 | UNCHANGED | Repudiation | — | tool-server-1 | L3 — Agent Framework | Actions taken through tool-server-1 are logged without the authenticated principal or a request identifier... | Medium | Log the verified principal, request identifier, source address and outcome for every state change in tool-server-1, and ship the records to the... |
| I-3 | UNCHANGED | Information Disclosure | — | worker-2 | L3 — Agent Framework | Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to... | Medium | Redact or tokenise sensitive fields before worker-2 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| D-1 | UNCHANGED | Denial of Service | — | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it... | Medium | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| D-3 | UNCHANGED | Denial of Service | — | vector-store-a | L2 — Data Operations | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay... | Medium | Add jittered exponential backoff and a retry budget to worker-2, and enable a circuit breaker so that vector-store-a can recover. |
| E-2 | UNCHANGED | Elevation of Privilege | — | intake-agent | L3 — Agent Framework | Role claims carried in the service token presented to intake-agent are honoured without confirmation against... | Medium | Resolve roles for intake-agent from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| AG-4 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when... | Medium | Make the actions of tool-server-1 idempotent with request keys, cap retries and require confirmation before repeating any action with external... |
| AG-5 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output... | Medium | Validate every argument against the tool schema in tool-server-1 before the call, enforce allowlists of values and reject free-form commands. |
| AG-6 | NEW | Agentic | — | planner-agent | L3 — Agent Framework | planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes... | Medium | Apply per-task and per-tool quotas to planner-agent, alert on unusual call patterns and block calls once a cost ceiling is reached. |
| AGP-01 | UNCHANGED | Agentic | agent_collusion | worker-2 | L3 — Agent Framework | Worker agents coordinate through the shared message bus and memory so that each stays under its individual... | Medium | Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate.... |
| TE-1 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions... | Medium | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. |
| OI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field... | Medium | Validate the output of intake-agent against a strict schema in edge-gateway, treat it as untrusted input and reject anything that fails. |
| S-1 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every... | Low | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| T-2 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | Low | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-3 | UNCHANGED | Tampering | — | audit-ledger | L6 — Security and Compliance | An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool... | Low | Sign messages between tool-server-1 and audit-ledger with a per-service key and verify the signature and a monotonic counter before accepting any... |
| T-5 | NEW | Tampering | — | auth-broker | L6 — Security and Compliance | Unsanitised credential assertions and session grants reach auth-broker and are processed as trusted... | Low | Validate credential assertions and session grants against a strict schema at the boundary of auth-broker, reject unknown fields and normalise... |
| R-3 | UNCHANGED | Repudiation | — | tool-server-1 | L3 — Agent Framework | Operators approve changes to tool call arguments and results through a chat message or ticket comment that... | Low | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| TE-2 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful... | Low | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. |
| LLM-4 | UNCHANGED | LLM | — | tool-server-1 | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks... | Low | Normalise and decode inputs before filtering in tool-server-1, apply semantic checks instead of keyword lists and review filter misses weekly. |
| OI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of... | Low | Validate URLs from intake-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. |
| MI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste... | Low | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. |
| MI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. | Low | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. |
| OI-3 | UNCHANGED | LLM | — | worker-2 | L3 — Agent Framework | Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it. | Note | Strip remote resources from the output of worker-2 before display, proxy images through a controlled service and disable automatic loading. |

---

## 8. Delta Summary

The lifecycle of every finding relative to the baseline run. Section 4c lists the resolved findings.

### Finding Lifecycle

| Status | Count | Description |
|--------|-------|-------------|
| NEW | 5 | Findings discovered in this run with no baseline match |
| UNCHANGED | 35 | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | 2 | Findings with changed context since baseline |
| RESOLVED | 3 | Baseline findings no longer applicable (see Section 4c for details) |
| **Total** | **45** | Sum of all findings (active + resolved) |

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | baseline/threats.md |
| Date | 2026-11-09 |
| Baseline Findings | 40 |
| Run ID | 2026-11-09T10-00-00 |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| I-5 | [] |
| AG-1 | [] |
| AG-2 | [] |
| AG-3 | [] |
| LLM-1 | [] |
| LLM-6 | [] |
| LLM-7 | [] |
| S-4 | [] |
| T-1 | [] |
| I-1 | [] |
| I-4 | [] |
| D-2 | [] |
| E-1 | [] |
| E-3 | [] |
| LLM-2 | [] |
| LLM-3 | [] |
| LLM-5 | [] |
| S-3 | [] |
| S-6 | [] |
| R-1 | [] |
| R-4 | [] |
| I-3 | [] |
| D-1 | [] |
| D-3 | [] |
| E-2 | [] |
| AG-4 | [] |
| AG-5 | [] |
| AG-6 | [] |
| AGP-01 | [] |
| TE-1 | [] |
| OI-2 | [] |
| S-1 | [] |
| T-2 | [] |
| T-3 | [] |
| T-5 | [] |
| R-3 | [] |
| TE-2 | [] |
| LLM-4 | [] |
| OI-1 | [] |
| MI-1 | [] |
| MI-2 | [] |
| OI-3 | [] |
