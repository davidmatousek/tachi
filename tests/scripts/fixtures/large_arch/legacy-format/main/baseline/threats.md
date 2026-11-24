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
