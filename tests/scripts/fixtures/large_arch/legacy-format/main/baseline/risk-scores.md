---
schema_version: "1.0"
date: "2026-11-09"
source_file: "baseline/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores Report

## Section 1: Executive Summary

**24** threats scored | **0** Critical | **7** High | **17** Medium | **0** Low

## Section 2: Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------------|-------------|--------------|-----------|----------|-----|-------------|
| E-2 | auth-broker | Role claims carried in the refresh token presented to... | 9.9 | 7.5 | 8.5 | 7.0 | 8.4 | Medium | — | Review |
| S-1 | client-portal | An attacker replays a captured session cookie against... | 7.5 | 9.0 | 9.0 | 8.5 | 8.2 | High | 7d | Mitigate |
| S-2 | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 8.2 | 9.0 | 7.5 | 7.0 | 8.1 | High | 7d | Mitigate |
| E-1 | edge-gateway | Object identifiers in requests to edge-gateway are trusted... | 5.6 | 7.0 | 8.0 | 7.0 | 7.7 | High | 7d | Mitigate |
| T-2 | auth-broker | Backups and exports of credential assertions and session... | 4.6 | 8.0 | 7.0 | 6.5 | 7.4 | High | 7d | Mitigate |
| LLM-1 | edge-gateway | edge-gateway passes conversation history from earlier turns... | 7.6 | 9.0 | 7.5 | 7.0 | 7.4 | High | 7d | Mitigate |
| D-2 | auth-broker | A single oversized or deeply nested payload makes... | 6.5 | 8.5 | 8.0 | 6.5 | 7.3 | Medium | 30d | Review |
| T-1 | edge-gateway | An attacker who can write to the channel between auth-broker... | 5.8 | 7.0 | 7.0 | 5.5 | 7.1 | High | 7d | Mitigate |
| D-1 | edge-gateway | A dependency of edge-gateway becomes unavailable and the... | 5.3 | 9.5 | 8.0 | 7.0 | 7.1 | High | 7d | Mitigate |
| OI-2 | planner-agent | planner-agent emits URLs that downstream services fetch, so... | 8.7 | 8.0 | 6.5 | 2.0 | 6.8 | Medium | 30d | Review |
| R-1 | client-portal | Operators approve changes to operator requests and approval... | 5.3 | 5.0 | 7.0 | 9.5 | 6.7 | Medium | 30d | Review |
| I-2 | auth-broker | credential assertions and session grants held by auth-broker... | 4.9 | 8.0 | 8.0 | 6.0 | 6.5 | Medium | 30d | Review |
| AG-1 | intake-agent | Memory written by intake-agent is trusted on later runs, so... | 10.0 | 4.0 | 5.5 | 2.5 | 6.5 | Medium | 30d | Review |
| AGP-02 | worker-2 | State persisted across runs lets a sleeper instruction... | 10.0 | 5.0 | 5.5 | 3.5 | 6.5 | Medium | 30d | Review |
| MI-2 | intake-agent | Stale data in the knowledge base lets intake-agent present... | 6.9 | 7.5 | 7.5 | 3.5 | 6.5 | Medium | 30d | Review |
| LLM-2 | intake-agent | Encoded or multilingual payloads bypass the keyword filter... | 6.3 | 8.0 | 7.0 | 3.0 | 6.3 | Medium | 30d | Review |
| MI-1 | intake-agent | intake-agent fabricates reference numbers and clause... | 7.6 | 8.5 | 7.0 | 2.0 | 6.3 | Medium | 30d | Review |
| I-1 | edge-gateway | Secrets such as the bearer token for edge-gateway appear in... | 1.6 | 8.5 | 9.0 | 5.5 | 6.2 | Medium | 30d | Review |
| OI-1 | intake-agent | intake-agent emits URLs that downstream services fetch, so... | 4.1 | 7.0 | 7.5 | 3.5 | 6.2 | Medium | 30d | Review |
| TE-2 | intake-agent | Persuasive phrasing from intake-agent pushes operators to... | 9.1 | 6.0 | 5.5 | 2.0 | 6.2 | Medium | 30d | Review |
| R-2 | edge-gateway | Log entries from edge-gateway can be edited or deleted by... | 5.5 | 5.5 | 7.5 | 5.5 | 5.8 | Medium | 30d | Review |
| AG-2 | planner-agent | planner-agent runs without a budget on steps or spend, so a... | 8.2 | 5.0 | 6.0 | 2.0 | 5.7 | Medium | 30d | Review |
| AGP-01 | planner-agent | Worker agents coordinate through the shared message bus and... | 10.0 | 5.0 | 5.5 | 2.0 | 5.7 | Medium | 30d | Review |
| TE-1 | intake-agent | intake-agent adopts a persona that presents itself as a... | 6.6 | 4.5 | 4.5 | 3.5 | 5.6 | Medium | 30d | Review |

## Section 3: Dimensional Breakdown

### E-2 — auth-broker

**Threat**: Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against the authoritative directory.

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

### S-1 — client-portal

**Threat**: An attacker replays a captured session cookie against client-portal, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

### S-2 — edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

### E-1 — edge-gateway

**Threat**: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

### T-2 — auth-broker

**Threat**: Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H`

### LLM-1 — edge-gateway

**Threat**: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L`

### D-2 — auth-broker

**Threat**: A single oversized or deeply nested payload makes auth-broker spend disproportionate memory and CPU parsing credential assertions and session grants.

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L`

### T-1 — edge-gateway

**Threat**: An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own.

### D-1 — edge-gateway

**Threat**: A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H`

### OI-2 — planner-agent

**Threat**: planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

### R-1 — client-portal

**Threat**: Operators approve changes to operator requests and approval decisions through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

### I-2 — auth-broker

**Threat**: credential assertions and session grants held by auth-broker are readable by any service in the Edge DMZ that shares the same network role, because access is granted by network position.

### AG-1 — intake-agent

**Threat**: Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L`

### AGP-02 — worker-2

**Threat**: State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run weeks later, after the original entry has left review and the context that explained it is gone.

**Score**: 10.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H`

### MI-2 — intake-agent

**Threat**: Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes.

**CVSS Vector**: `CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:L`

### LLM-2 — intake-agent

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N`

### MI-1 — intake-agent

**Threat**: intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N`

### I-1 — edge-gateway

**Threat**: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

### OI-1 — intake-agent

**Threat**: intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

### TE-2 — intake-agent

**Threat**: Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

### R-2 — edge-gateway

**Threat**: Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

### AG-2 — planner-agent

**Threat**: planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L`

### AGP-01 — planner-agent

**Threat**: Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour.

### TE-1 — intake-agent

**Threat**: intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

## Section 4: Governance Fields

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| E-2 | Medium | Unassigned | — | Review | 2026-12-09 |
| S-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| E-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| T-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| D-2 | Medium | Unassigned | 30d | Review | — |
| T-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| OI-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AGP-02 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AGP-01 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
