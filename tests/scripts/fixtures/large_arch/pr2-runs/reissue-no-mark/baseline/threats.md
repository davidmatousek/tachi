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

This file is a baseline run's threats.md, cut down to Section 4c and Section 7. It has no ID high-water mark line, as every baseline that an earlier release wrote.

## 4c. Resolved Findings

Findings from the baseline that no longer apply in the current architecture. Each keeps its original ID, description and last-known risk level.

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|
| S-6 | label-printer-1 | A shared batch credential for label-printer-1 is accepted from any caller that can reach its callback route, so one leaked copy authenticates as the batch job. | Medium | Component 'label-printer-1' removed from architecture |
| T-4 | label-printer-1 | Label files that label-printer-1 renders can be replaced in storage before they print, so a shipment may carry the wrong destination. | Low | Component 'label-printer-1' removed from architecture |

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| AG-1 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of... | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. |
| AG-2 | UNCHANGED | Agentic | emergent_behavior | planner-agent | L3 — Agent Framework | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long... | Critical | Set hard limits on steps, tool calls, runtime and spend for planner-agent, stop on breach and report the stop reason to the operator. |
| AG-3 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of... | Critical | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by tool-server-1. |
| LLM-1 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection... | Critical | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. |
| LLM-6 | UNCHANGED | LLM | — | vector-store-a | L2 — Data Operations | Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict... | Critical | Restrict write access to the ingestion path of vector-store-a, sign documents from authoritative sources and prefer them when answers conflict. |
| S-2 | UNCHANGED | Spoofing | — | legacy-batch-1 | L4 — Deployment Infrastructure | An unauthenticated callback or health route on legacy-batch-1 accepts requests that downstream code treats... | High | Remediate as described in the baseline report. |
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
| R-1 | UNCHANGED | Repudiation | — | intake-agent | L3 — Agent Framework | Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of... | Medium | Synchronise intake-agent and edge-gateway to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| R-4 | UNCHANGED | Repudiation | — | tool-server-1 | L3 — Agent Framework | Actions taken through tool-server-1 are logged without the authenticated principal or a request identifier... | Medium | Log the verified principal, request identifier, source address and outcome for every state change in tool-server-1, and ship the records to the... |
| I-2 | UNCHANGED | Information Disclosure | — | report-export-2 | L7 — Agent Ecosystem | Secrets such as the export credential for report-export-2 appear in process arguments and environment dumps... | Medium | Remediate as described in the baseline report. |
| I-3 | UNCHANGED | Information Disclosure | — | worker-2 | L3 — Agent Framework | Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to... | Medium | Redact or tokenise sensitive fields before worker-2 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| D-1 | UNCHANGED | Denial of Service | — | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it... | Medium | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| D-3 | UNCHANGED | Denial of Service | — | vector-store-a | L2 — Data Operations | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay... | Medium | Add jittered exponential backoff and a retry budget to worker-2, and enable a circuit breaker so that vector-store-a can recover. |
| E-2 | UNCHANGED | Elevation of Privilege | — | intake-agent | L3 — Agent Framework | Role claims carried in the service token presented to intake-agent are honoured without confirmation against... | Medium | Resolve roles for intake-agent from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| AG-4 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when... | Medium | Make the actions of tool-server-1 idempotent with request keys, cap retries and require confirmation before repeating any action with external... |
| AG-5 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output... | Medium | Validate every argument against the tool schema in tool-server-1 before the call, enforce allowlists of values and reject free-form commands. |
| AGP-01 | UNCHANGED | Agentic | agent_collusion | worker-2 | L3 — Agent Framework | Worker agents coordinate through the shared message bus and memory so that each stays under its individual... | Medium | Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate.... |
| TE-1 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions... | Medium | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. |
| OI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field... | Medium | Validate the output of intake-agent against a strict schema in edge-gateway, treat it as untrusted input and reject anything that fails. |
| S-1 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every... | Low | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| T-2 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | Low | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-3 | UNCHANGED | Tampering | — | audit-ledger | L6 — Security and Compliance | An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool... | Low | Sign messages between tool-server-1 and audit-ledger with a per-service key and verify the signature and a monotonic counter before accepting any... |
| R-2 | UNCHANGED | Repudiation | — | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Low | Remediate as described in the baseline report. |
| R-3 | UNCHANGED | Repudiation | — | tool-server-1 | L3 — Agent Framework | Operators approve changes to tool call arguments and results through a chat message or ticket comment that... | Low | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| TE-2 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful... | Low | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. |
| LLM-4 | UNCHANGED | LLM | — | tool-server-1 | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks... | Low | Normalise and decode inputs before filtering in tool-server-1, apply semantic checks instead of keyword lists and review filter misses weekly. |
| OI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of... | Low | Validate URLs from intake-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. |
| MI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste... | Low | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. |
| MI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. | Low | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. |
| OI-3 | UNCHANGED | LLM | — | worker-2 | L3 — Agent Framework | Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it. | Note | Strip remote resources from the output of worker-2 before display, proxy images through a controlled service and disable automatic loading. |
