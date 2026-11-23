---
schema_version: "1.4"
date: "2026-11-23"
input_format: "free-text"
classification: "confidential"
run_id: "2026-11-23T10-00-00"
baseline:
  source: "baseline/threats.md"
  date: "2026-11-09"
  finding_count: 24
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
| S-1 | UNCHANGED | client-portal | L7 — Agent Ecosystem | An attacker replays a captured session cookie against client-portal, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller. The exposure follows from how client-portal receives operator requests and approval decisions from edge-gateway and hands them to the next stage without an independent check. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | MEDIUM | MEDIUM | Medium | Bind each session cookie to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different channel than the one it was issued to. Track coverage of this control as a release criterion for client-portal and record any exception with an expiry date. |
| S-2 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Until the credential is revoked the attacker acts with the victim's authority, and the audit trail attributes the actions to the victim. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | MEDIUM | MEDIUM | Medium | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks within the rotation window. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| T-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Sign messages between auth-broker and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting any change. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |
| T-2 | UNCHANGED | auth-broker | L6 — Security and Compliance | Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores. auth-broker runs in the Edge DMZ and exchanges credential assertions and session grants with edge-gateway over gRPC over mTLS, so anything able to reach edge-gateway can also reach this weakness. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | HIGH | MEDIUM | High | Protect exports and backups of credential assertions and session grants with write-once storage and dual approval for restore, and verify checksums against a separately held manifest. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

### 3.3 Repudiation (R)

Threats where an actor denies an action without the system being able to prove otherwise.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| R-1 | UNCHANGED | client-portal | L7 — Agent Ecosystem | Operators approve changes to operator requests and approval decisions through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed. Because client-portal serves the Public Internet, a single failure here reaches each consumer of operator requests and approval decisions at once. Without reliable records an investigation cannot establish who acted, so disputes about responsibility stay unresolved. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and LOW impact because the effect is contained and easy to reverse once it is noticed. | LOW | LOW | Note | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. Verify the control in a pre-production exercise and review it again after any change to client-portal. |
| R-2 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Without reliable records an investigation cannot establish who acted, so disputes about responsibility stay unresolved. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | LOW | MEDIUM | Low | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. Track coverage of this control as a release criterion for edge-gateway and record any exception with an expiry date. |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| I-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. The exposed material can be reused for follow-on attacks and may trigger notification duties if it covers customer data. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and LOW impact because the effect is contained and easy to reverse once it is noticed. | LOW | LOW | Note | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any exposure. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| I-2 | UNCHANGED | auth-broker | L6 — Security and Compliance | credential assertions and session grants held by auth-broker are readable by any service in the Edge DMZ that shares the same network role, because access is granted by network position. Because auth-broker serves the Edge DMZ, a single failure here reaches each consumer of credential assertions and session grants at once. Disclosure is silent, so the affected parties learn about it only when the information is misused. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | HIGH | MEDIUM | High | Grant access to credential assertions and session grants per workload identity with least privilege, enforce it at auth-broker and remove network-position trust within the Edge DMZ. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| D-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. Operators lose the ability to book or amend shipments while the condition lasts, and recovery depends on manual intervention. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and LOW impact because the effect is contained and easy to reverse once it is noticed. | HIGH | LOW | Medium | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. Track coverage of this control as a release criterion for edge-gateway and record any exception with an expiry date. |
| D-2 | UNCHANGED | auth-broker | L6 — Security and Compliance | A single oversized or deeply nested payload makes auth-broker spend disproportionate memory and CPU parsing credential assertions and session grants. Because auth-broker serves the Edge DMZ, a single failure here reaches each consumer of credential assertions and session grants at once. The outage propagates to dependent agents, which stall or retry and prolong the disruption. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | LOW | MEDIUM | Low | Cap payload size, nesting depth and parse time in auth-broker, and reject requests that exceed the limits before allocation. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| E-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others. The weakness sits at layer Deployment Infrastructure of the stack, so every workflow that depends on inbound API requests inherits the exposure. Once the boundary is crossed the attacker can reach administrative functions and persist there. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | MEDIUM | HIGH | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| E-2 | UNCHANGED | auth-broker | L6 — Security and Compliance | Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against the authoritative directory. edge-gateway trusts auth-broker to pass credential assertions and session grants along unchanged, which removes the second chance to catch the problem downstream. The caller gains rights that were never granted, which allows reading and changing data across tenants and approvals. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | MEDIUM | MEDIUM | Medium | Resolve roles for auth-broker from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. Name an owner for this control, review it each quarter and route violations to audit-ledger so that responders see them in one place. |

---

## 4. AI Threat Tables

Findings from the AI-specific agents. Each row adds an OWASP reference to the standard fields.

### 4.1 Agentic Threats (AG)

Threats arising from autonomous agent behavior, tool use and the way people rely on agent output.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|
| AG-1 | UNCHANGED | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. The agent acts at machine speed on behalf of the operator, so a single manipulated decision can cause many unwanted changes before a person notices. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | ASI-06 | HIGH | MEDIUM | High | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. Verify the control in a pre-production exercise and review it again after any change to intake-agent. |
| AG-2 | UNCHANGED | planner-agent | L3 — Agent Framework | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful. planner-agent runs in the Agent Runtime Zone and exchanges task plans and tool selections with model-gateway over HTTPS (TLS 1.3), so anything able to reach model-gateway can also reach this weakness. Actions taken by the agent look legitimate in the logs, which slows detection and complicates rollback. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | ASI-10 | MEDIUM | HIGH | High | Set hard limits on steps, tool calls, runtime and spend for planner-agent, stop on breach and report the stop reason to the operator. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |
| AGP-01 | UNCHANGED | planner-agent | L3 — Agent Framework | Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on task plans and tool selections inherits the exposure. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | ASI-07 | MEDIUM | MEDIUM | Medium | Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate. Recommended controls: behavioural baselining of the collective agent system and alerts on coordinated bursts. |
| AGP-02 | UNCHANGED | worker-2 | L3 — Agent Framework | State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run weeks later, after the original entry has left review and the context that explained it is gone. The exposure follows from how worker-2 receives work orders and route candidates from vector-store-a and hands them to the next stage without an independent check. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | ASI-06 | MEDIUM | MEDIUM | Medium | Expire persisted instructions, re-review any state that scheduled runs read and compare behaviour against pre-run snapshots. Recommended controls: provenance attestation for stored state and audit trails for every memory write. |
| TE-1 | UNCHANGED | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants. edge-gateway trusts intake-agent to pass free-text shipment requests along unchanged, which removes the second chance to catch the problem downstream. The effect builds over time as users come to rely on the agent's tone instead of its evidence. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and LOW impact because the effect is contained and easy to reverse once it is noticed. | ASI-09 | LOW | LOW | Note | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. Track coverage of this control as a release criterion for intake-agent and record any exception with an expiry date. |
| TE-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. People defer to the agent more than its reliability justifies, which weakens the human oversight the design depends on. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | ASI-09 | HIGH | MEDIUM | High | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. Confirm the fix with a targeted test against intake-agent, and keep the evidence with the change record for later audits. |

### 4.2 LLM Threats (LLM)

Threats to and through the language models: injection, poisoning, extraction, unsafe output and misinformation.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|
| LLM-1 | UNCHANGED | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns. Because edge-gateway serves the Edge DMZ, a single failure here reaches each consumer of inbound API requests at once. The answers or side effects of the model then serve the attacker's goal, and the behaviour can be repeated against every user of the component. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM01:2026 | MEDIUM | HIGH | High | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. Verify the control in a pre-production exercise and review it again after any change to edge-gateway. |
| LLM-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on free-text shipment requests inherits the exposure. The answers or side effects of the model then serve the attacker's goal, and the behaviour can be repeated against every user of the component. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM01:2026 | LOW | HIGH | Medium | Normalise and decode inputs before filtering in intake-agent, apply semantic checks instead of keyword lists and review filter misses weekly. Track coverage of this control as a release criterion for intake-agent and record any exception with an expiry date. |
| OI-1 | UNCHANGED | intake-agent | L3 — Agent Framework | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests. edge-gateway trusts intake-agent to pass free-text shipment requests along unchanged, which removes the second chance to catch the problem downstream. The unsafe output reaches an interpreter that trusts it, turning a text generation problem into code or request execution. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM10:2026 | MEDIUM | MEDIUM | Medium | Validate URLs from intake-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. Track coverage of this control as a release criterion for intake-agent and record any exception with an expiry date. |
| OI-2 | UNCHANGED | planner-agent | L3 — Agent Framework | planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests. Because planner-agent serves the Agent Runtime Zone, a single failure here reaches each consumer of task plans and tool selections at once. Downstream components cannot tell the model's output from validated input, so no later layer is likely to catch it. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse. | OWASP LLM10:2026 | HIGH | HIGH | Critical | Validate URLs from planner-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. Verify the control in a pre-production exercise and review it again after any change to planner-agent. |
| MI-1 | UNCHANGED | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. The mistake looks authoritative, so it is rarely questioned until a downstream party objects. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM07:2026 | MEDIUM | MEDIUM | Medium | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. Confirm the fix with a targeted test against intake-agent, and keep the evidence with the change record for later audits. |
| MI-2 | UNCHANGED | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. The exposure follows from how intake-agent receives free-text shipment requests from edge-gateway and hands them to the next stage without an independent check. Operators act on the wrong information, and the error is copied into shipments, documents and customer communication. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort. | OWASP LLM07:2026 | MEDIUM | MEDIUM | Medium | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. Add a regression test for this abuse path to the CI suite and alert through audit-ledger when the control fires. |

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
| trust_exploitation | 2 | TE-1, TE-2 |
| agent_collusion | 1 | AGP-01 |
| emergent_behavior | 1 | AG-2 |
| temporal_attack | 1 | AGP-02 |

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
| client-portal | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| edge-gateway | 1 | 1 | 1 | 1 | 1 | 1 | n/a | 1 | 7 |
| auth-broker | — | 1 | — | 1 | 1 | 1 | n/a | n/a | 4 |
| intake-agent | — | — | — | — | — | — | 3 | 4 | 7 |
| planner-agent | — | — | — | — | — | — | 2 | 1 | 3 |
| worker-2 | — | — | — | — | — | — | 1 | — | 1 |
| tool-server-1 | — | — | — | — | — | — | — | — | 0 |
| model-gateway | — | — | — | — | — | — | n/a | — | 0 |
| vector-store-a | n/a | — | n/a | — | — | n/a | n/a | — | 0 |
| audit-ledger | n/a | — | — | — | — | n/a | n/a | n/a | 0 |
| **Total** | **2** | **2** | **2** | **2** | **2** | **2** | **6** | **6** | **24** |

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
| L3 — Agent Framework | 11 | Critical |
| L4 — Deployment Infrastructure | 7 | High |
| L5 — Evaluation and Observability | 0 | Not applicable — no components map to this layer |
| L6 — Security and Compliance | 4 | High |
| L7 — Agent Ecosystem | 2 | Medium |

Risk summary counts below reflect deduplicated findings. A correlation group counts as one threat at its group risk level.

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 1 | 4.2% |
| High | 8 | 33.3% |
| Medium | 10 | 41.7% |
| Low | 2 | 8.3% |
| Note | 3 | 12.5% |
| **Total** | **24** | **100%** |

---

## 7. Recommended Actions

All findings sorted by risk level descending, then by table order. Critical and High findings should be addressed before deployment.

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| OI-2 | UNCHANGED | LLM | — | planner-agent | L3 — Agent Framework | planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of... | Critical | Validate URLs from planner-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. |
| T-1 | UNCHANGED | Tampering | — | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests... | High | Sign messages between auth-broker and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting any... |
| T-2 | UNCHANGED | Tampering | — | auth-broker | L6 — Security and Compliance | Backups and exports of credential assertions and session grants on auth-broker are writable by operators... | High | Protect exports and backups of credential assertions and session grants with write-once storage and dual approval for restore, and verify... |
| I-2 | UNCHANGED | Information Disclosure | — | auth-broker | L6 — Security and Compliance | credential assertions and session grants held by auth-broker are readable by any service in the Edge DMZ... | High | Grant access to credential assertions and session grants per workload identity with least privilege, enforce it at auth-broker and remove... |
| E-1 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read... | High | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. |
| AG-1 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of... | High | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. |
| AG-2 | UNCHANGED | Agentic | emergent_behavior | planner-agent | L3 — Agent Framework | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long... | High | Set hard limits on steps, tool calls, runtime and spend for planner-agent, stop on breach and report the stop reason to the operator. |
| TE-2 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful... | High | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. |
| LLM-1 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection... | High | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. |
| S-1 | UNCHANGED | Spoofing | — | client-portal | L7 — Agent Ecosystem | An attacker replays a captured session cookie against client-portal, which does not bind the credential to... | Medium | Bind each session cookie to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| S-2 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every... | Medium | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| D-1 | UNCHANGED | Denial of Service | — | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it... | Medium | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| E-2 | UNCHANGED | Elevation of Privilege | — | auth-broker | L6 — Security and Compliance | Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against... | Medium | Resolve roles for auth-broker from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| AGP-01 | UNCHANGED | Agentic | agent_collusion | planner-agent | L3 — Agent Framework | Worker agents coordinate through the shared message bus and memory so that each stays under its individual... | Medium | Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate.... |
| AGP-02 | UNCHANGED | Agentic | temporal_attack | worker-2 | L3 — Agent Framework | State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run... | Medium | Expire persisted instructions, re-review any state that scheduled runs read and compare behaviour against pre-run snapshots. Recommended controls... |
| LLM-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain... | Medium | Normalise and decode inputs before filtering in intake-agent, apply semantic checks instead of keyword lists and review filter misses weekly. |
| OI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of... | Medium | Validate URLs from intake-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. |
| MI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste... | Medium | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. |
| MI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. | Medium | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. |
| R-2 | UNCHANGED | Repudiation | — | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Low | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| D-2 | UNCHANGED | Denial of Service | — | auth-broker | L6 — Security and Compliance | A single oversized or deeply nested payload makes auth-broker spend disproportionate memory and CPU parsing... | Low | Cap payload size, nesting depth and parse time in auth-broker, and reject requests that exceed the limits before allocation. |
| R-1 | UNCHANGED | Repudiation | — | client-portal | L7 — Agent Ecosystem | Operators approve changes to operator requests and approval decisions through a chat message or ticket... | Note | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| I-1 | UNCHANGED | Information Disclosure | — | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that... | Note | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| TE-1 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions... | Note | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. |

---

## 8. Delta Summary

The lifecycle of every finding relative to the baseline run. Section 4c lists the resolved findings.

### Finding Lifecycle

| Status | Count | Description |
|--------|-------|-------------|
| NEW | 0 | Findings discovered in this run with no baseline match |
| UNCHANGED | 24 | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | 0 | Findings with changed context since baseline |
| RESOLVED | 0 | Baseline findings no longer applicable (see Section 4c for details) |
| **Total** | **24** | Sum of all findings (active + resolved) |

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | baseline/threats.md |
| Date | 2026-11-09 |
| Baseline Findings | 24 |
| Run ID | 2026-11-09T10-00-00 |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| OI-2 | [] |
| T-1 | [] |
| T-2 | [] |
| I-2 | [] |
| E-1 | [] |
| AG-1 | [] |
| AG-2 | [] |
| TE-2 | [] |
| LLM-1 | [] |
| S-1 | [] |
| S-2 | [] |
| D-1 | [] |
| E-2 | [] |
| AGP-01 | [] |
| AGP-02 | [] |
| LLM-2 | [] |
| OI-1 | [] |
| MI-1 | [] |
| MI-2 | [] |
| R-2 | [] |
| D-2 | [] |
| R-1 | [] |
| I-1 | [] |
| TE-1 | [] |
