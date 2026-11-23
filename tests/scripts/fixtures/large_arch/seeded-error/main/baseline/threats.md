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
| Partner Exchange | Semi-trusted / Trusted | partner-sandbox |

---

## 4c. Resolved Findings

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| S-1 | UNCHANGED | Spoofing | — | client-portal | L7 — Agent Ecosystem | An attacker replays a captured session cookie against client-portal, which does not bind the credential to... | Critical | Bind each session cookie to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| T-7 | UNCHANGED | Tampering | — | tool-server-1 | L3 — Agent Framework | An update to tool-server-1 is pulled without provenance checks, so a poisoned package can alter how tool... | Critical | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of tool-server-1 when a component lacks a... |
| I-3 | UNCHANGED | Information Disclosure | — | intake-agent | L3 — Agent Framework | A timing or size difference in the responses of intake-agent lets an observer infer whether specific records... | Critical | Equalise response size and timing for existence checks in intake-agent, and return the same status for present and absent records. |
| D-2 | UNCHANGED | Denial of Service | — | auth-broker | L6 — Security and Compliance | A single oversized or deeply nested payload makes auth-broker spend disproportionate memory and CPU parsing... | Critical | Cap payload size, nesting depth and parse time in auth-broker, and reject requests that exceed the limits before allocation. |
| D-4 | UNCHANGED | Denial of Service | resource_competition | planner-agent | L3 — Agent Framework | A dependency of planner-agent becomes unavailable and the failure cascades because planner-agent waits on it... | Critical | Isolate calls from planner-agent to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| D-8 | UNCHANGED | Denial of Service | — | vector-store-a | L2 — Data Operations | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay... | Critical | Add jittered exponential backoff and a retry budget to worker-2, and enable a circuit breaker so that vector-store-a can recover. |
| E-5 | UNCHANGED | Elevation of Privilege | — | intake-agent | L3 — Agent Framework | Role claims carried in the service token presented to intake-agent are honoured without confirmation against... | Critical | Resolve roles for intake-agent from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| E-7 | UNCHANGED | Elevation of Privilege | — | worker-2 | L3 — Agent Framework | Role claims carried in the worker credential presented to worker-2 are honoured without confirmation against... | Critical | Resolve roles for worker-2 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| AG-2 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | intake-agent retries failed actions on its own, repeating side effects such as bookings or messages when the... | Critical | Make the actions of intake-agent idempotent with request keys, cap retries and require confirmation before repeating any action with external effects. |
| AG-3 | UNCHANGED | Agentic | emergent_behavior | planner-agent | L3 — Agent Framework | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long... | Critical | Set hard limits on steps, tool calls, runtime and spend for planner-agent, stop on breach and report the stop reason to the operator. |
| AG-4 | UNCHANGED | Agentic | emergent_behavior | planner-agent | L3 — Agent Framework | Delegation from model-gateway to planner-agent carries the full authority of the original session, so a... | Critical | Issue narrowly scoped, short-lived delegation grants to planner-agent and verify scope on every action instead of inheriting the parent session. |
| TE-5 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent speaks with an authoritative tone about customs and legal matters, and operators may defer to... | Critical | Label the output of intake-agent as machine generated, state its limits plainly and avoid wording that claims professional authority. |
| TE-8 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent builds rapport over long sessions and starts to share unprompted details about earlier operators. | Critical | Isolate sessions of intake-agent per operator, forbid recall of other operators' details and review long sessions for rapport patterns. |
| LLM-4 | UNCHANGED | LLM | — | planner-agent | L3 — Agent Framework | Indirect injection through documents retrieved for planner-agent lets the author of a retrieved page steer... | Critical | Score retrieved passages for instruction-like content before planner-agent uses them, attribute every passage to its source and cap how much any... |
| OI-3 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Markdown or HTML produced by intake-agent contains remote images that leak data when a client renders it. | Critical | Strip remote resources from the output of intake-agent before display, proxy images through a controlled service and disable automatic loading. |
| OI-6 | UNCHANGED | LLM | — | worker-2 | L3 — Agent Framework | Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it. | Critical | Strip remote resources from the output of worker-2 before display, proxy images through a controlled service and disable automatic loading. |
| MI-3 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent states carrier rules and customs requirements as fact without grounding them in a cited source... | Critical | Require intake-agent to cite a retrievable source for each factual claim, show the citations and decline to answer when none is found. |
| MI-6 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste... | Critical | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. |
| S-4 | UNCHANGED | Spoofing | — | auth-broker | L6 — Security and Compliance | A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every... | High | Replace the shared refresh token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| S-5 | UNCHANGED | Spoofing | trust_exploitation | intake-agent | L3 — Agent Framework | Session fixation against intake-agent lets an attacker pre-seed an identifier and reuse the session after... | High | Issue a fresh session identifier on every authentication and privilege change, set strict cookie attributes and invalidate any identifier supplied... |
| S-7 | UNCHANGED | Spoofing | trust_exploitation | worker-2 | L3 — Agent Framework | A shared or long-lived worker credential on worker-2 lets anyone who obtains one copy authenticate as every... | High | Replace the shared worker credential with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| S-8 | UNCHANGED | Spoofing | trust_exploitation | tool-server-1 | L3 — Agent Framework | A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every... | High | Replace the shared tool API key with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| S-9 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | An unauthenticated callback or health route on edge-gateway accepts requests that downstream code treats as... | High | Remediate as described in the baseline report. |
| S-10 | UNCHANGED | Spoofing | — | model-gateway | L1 — Foundation Model | An attacker replays a captured model API key against model-gateway, which does not bind the credential to... | High | Bind each model API key to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| T-3 | UNCHANGED | Tampering | — | auth-broker | L6 — Security and Compliance | Backups and exports of credential assertions and session grants on auth-broker are writable by operators... | High | Protect exports and backups of credential assertions and session grants with write-once storage and dual approval for restore, and verify... |
| T-4 | UNCHANGED | Tampering | — | intake-agent | L3 — Agent Framework | Replay of an earlier valid update to free-text shipment requests reaches intake-agent because updates carry... | High | Add a nonce and a short expiry to every update accepted by intake-agent, store seen nonces for the validity window and reject any repeat. |
| T-5 | UNCHANGED | Tampering | — | planner-agent | L3 — Agent Framework | Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so... | High | Validate task plans and tool selections against a strict schema at the boundary of planner-agent, reject unknown fields and normalise encodings... |
| T-8 | UNCHANGED | Tampering | — | model-gateway | L1 — Foundation Model | Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential... | High | Keep the configuration of model-gateway in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-9 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling... | High | Replace permissive deserialisation in vector-store-a with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-10 | UNCHANGED | Tampering | — | audit-ledger | L6 — Security and Compliance | An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool... | High | Sign messages between tool-server-1 and audit-ledger with a per-service key and verify the signature and a monotonic counter before accepting any... |
| R-4 | UNCHANGED | Repudiation | — | intake-agent | L3 — Agent Framework | Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of... | High | Synchronise intake-agent and edge-gateway to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| I-2 | UNCHANGED | Information Disclosure | — | auth-broker | L6 — Security and Compliance | credential assertions and session grants held by auth-broker are readable by any service in the Edge DMZ... | High | Grant access to credential assertions and session grants per workload identity with least privilege, enforce it at auth-broker and remove... |
| I-4 | UNCHANGED | Information Disclosure | — | planner-agent | L3 — Agent Framework | A timing or size difference in the responses of planner-agent lets an observer infer whether specific... | High | Equalise response size and timing for existence checks in planner-agent, and return the same status for present and absent records. |
| I-5 | UNCHANGED | Information Disclosure | — | worker-2 | L3 — Agent Framework | Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to... | High | Redact or tokenise sensitive fields before worker-2 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| D-1 | UNCHANGED | Denial of Service | — | edge-gateway | L4 — Deployment Infrastructure | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it... | High | Isolate calls from edge-gateway to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| D-7 | UNCHANGED | Denial of Service | — | model-gateway | L1 — Foundation Model | Unbounded growth of stored prompts and completions on model-gateway fills its volume, after which writes... | High | Set quotas and retention for prompts and completions on model-gateway, alert at eighty percent capacity and reserve space for control-plane writes. |
| E-2 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Role claims carried in the bearer token presented to edge-gateway are honoured without confirmation against... | High | Resolve roles for edge-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| AG-5 | UNCHANGED | Agentic | — | planner-agent | L3 — Agent Framework | planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes... | High | Apply per-task and per-tool quotas to planner-agent, alert on unusual call patterns and block calls once a cost ceiling is reached. |
| AG-6 | UNCHANGED | Agentic | — | worker-2 | L3 — Agent Framework | worker-2 retries failed actions on its own, repeating side effects such as bookings or messages when the... | High | Make the actions of worker-2 idempotent with request keys, cap retries and require confirmation before repeating any action with external effects. |
| TE-4 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent claims certainty it does not have when summarising shipment risk, and customers rely on the... | High | Attach calibrated confidence and the basis for each claim to the output of intake-agent, and block unqualified guarantees in customer-facing text. |
| TE-6 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions... | High | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. |
| TE-9 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent claims certainty it does not have when summarising shipment risk, and customers rely on the... | High | Attach calibrated confidence and the basis for each claim to the output of intake-agent, and block unqualified guarantees in customer-facing text. |
| LLM-1 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection... | High | Re-screen conversation history on each turn in edge-gateway, expire old turns and mark which turns came from untrusted sources. |
| LLM-3 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain... | High | Normalise and decode inputs before filtering in intake-agent, apply semantic checks instead of keyword lists and review filter misses weekly. |
| LLM-5 | UNCHANGED | LLM | — | worker-2 | L3 — Agent Framework | worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking... | High | Restrict what worker-2 may fetch to an allowlist of domains and types, fetch through a sandbox and present the results as untrusted data. |
| LLM-9 | UNCHANGED | LLM | — | vector-store-a | L2 — Data Operations | Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict... | High | Restrict write access to the ingestion path of vector-store-a, sign documents from authoritative sources and prefer them when answers conflict. |
| OI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field... | High | Validate the output of intake-agent against a strict schema in edge-gateway, treat it as untrusted input and reject anything that fails. |
| OI-5 | UNCHANGED | LLM | — | planner-agent | L3 — Agent Framework | Structured output from planner-agent is trusted by model-gateway as already validated, so a malformed field... | High | Validate the output of planner-agent against a strict schema in model-gateway, treat it as untrusted input and reject anything that fails. |
| OI-7 | UNCHANGED | LLM | — | worker-2 | L3 — Agent Framework | File paths or names produced by worker-2 are used to write files, letting crafted output reach locations... | High | Generate file names for worker-2 on the server, confine writes to a sandbox directory and reject any path component supplied by the model. |
| OI-8 | UNCHANGED | LLM | — | model-gateway | L1 — Foundation Model | Markdown or HTML produced by model-gateway contains remote images that leak data when a client renders it. | High | Strip remote resources from the output of model-gateway before display, proxy images through a controlled service and disable automatic loading. |
| OI-9 | UNCHANGED | LLM | — | model-gateway | L1 — Foundation Model | File paths or names produced by model-gateway are used to write files, letting crafted output reach... | High | Generate file names for model-gateway on the server, confine writes to a sandbox directory and reject any path component supplied by the model. |
| MI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste... | High | Verify identifiers and citations produced by intake-agent against authoritative systems before display, and mark unverifiable ones clearly. |
| MI-4 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Confident wording from intake-agent hides low retrieval quality, so operators cannot tell a grounded answer... | High | Expose retrieval strength alongside the answers of intake-agent and switch to an explicit uncertainty message below a threshold. |
| S-2 | UNCHANGED | Spoofing | — | client-portal | L7 — Agent Ecosystem | A compromised peer presents a forged service identity to client-portal, and client-portal accepts the claim... | Medium | Require mutual TLS between edge-gateway and client-portal and validate the full certificate chain, issuer and audience on every request instead of... |
| S-3 | UNCHANGED | Spoofing | — | edge-gateway | L4 — Deployment Infrastructure | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every... | Medium | Replace the shared bearer token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| T-1 | UNCHANGED | Tampering | — | edge-gateway | L4 — Deployment Infrastructure | An attacker who can write to the channel between partner-sandbox and edge-gateway modifies inbound API... | Medium | Sign messages between partner-sandbox and edge-gateway with a per-service key and verify the signature and a monotonic counter before accepting... |
| T-2 | UNCHANGED | Tampering | — | vector-store-a | L2 — Data Operations | Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a... | Medium | Remediate as described in the baseline report. |
| R-6 | UNCHANGED | Repudiation | — | worker-2 | L3 — Agent Framework | Operators approve changes to work orders and route candidates through a chat message or ticket comment that... | Medium | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| R-8 | UNCHANGED | Repudiation | — | model-gateway | L1 — Foundation Model | Failed and rejected attempts against model-gateway are not logged, so probing of prompts and completions... | Medium | Log denied and malformed requests to model-gateway at a retained severity, aggregate them per source and alert on sustained probing. |
| R-9 | UNCHANGED | Repudiation | — | audit-ledger | L6 — Security and Compliance | Log entries from audit-ledger can be edited or deleted by the same operators who administer it, so evidence... | Medium | Write the records of audit-ledger to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| R-10 | UNCHANGED | Repudiation | — | partner-sandbox | L7 — Agent Ecosystem | Failed and rejected attempts against partner-sandbox are not logged, so probing of trial manifests and... | Medium | Log denied and malformed requests to partner-sandbox at a retained severity, aggregate them per source and alert on sustained probing. |
| I-8 | UNCHANGED | Information Disclosure | — | vector-store-a | L2 — Data Operations | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that... | Medium | Grant access to embedded documents and metadata per workload identity with least privilege, enforce it at vector-store-a and remove... |
| D-3 | UNCHANGED | Denial of Service | — | intake-agent | L3 — Agent Framework | A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing... | Medium | Cap payload size, nesting depth and parse time in intake-agent, and reject requests that exceed the limits before allocation. |
| E-3 | UNCHANGED | Elevation of Privilege | — | auth-broker | L6 — Security and Compliance | Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against... | Medium | Resolve roles for auth-broker from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| E-4 | UNCHANGED | Elevation of Privilege | — | auth-broker | L6 — Security and Compliance | An administrative interface of auth-broker is reachable from the same network as ordinary callers and relies... | Medium | Move the administrative interface of auth-broker behind a separate listener with strong authentication, network restriction and per-user accounts. |
| E-6 | UNCHANGED | Elevation of Privilege | — | planner-agent | L3 — Agent Framework | planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and... | Medium | Reduce the permissions of planner-agent to the minimum for task plans and tool selections, drop capabilities it does not use and review the grants... |
| E-9 | UNCHANGED | Elevation of Privilege | — | model-gateway | L1 — Foundation Model | Role claims carried in the model API key presented to model-gateway are honoured without confirmation... | Medium | Resolve roles for model-gateway from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| AG-1 | UNCHANGED | Agentic | — | intake-agent | L3 — Agent Framework | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of... | Medium | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by intake-agent. |
| AG-7 | UNCHANGED | Agentic | agent_collusion | worker-2 | L3 — Agent Framework | Tool calls made by worker-2 are not tied to the end user, so the tool server cannot tell whose authority a... | Medium | Propagate a signed end-user context with each tool call from worker-2 and make the tool server authorise against it, not against the agent identity. |
| AG-8 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of... | Medium | Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by tool-server-1. |
| AG-9 | UNCHANGED | Agentic | — | tool-server-1 | L3 — Agent Framework | tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output... | Medium | Validate every argument against the tool schema in tool-server-1 before the call, enforce allowlists of values and reject free-form commands. |
| AGP-01 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | Operators and downstream agents start to accept worker output without checking it because earlier results... | Medium | Require evidence for each recommendation, sample outputs for independent review and show uncertainty to operators so that reliance stays... |
| AGP-02 | UNCHANGED | Agentic | agent_collusion | planner-agent | L3 — Agent Framework | Worker agents coordinate through the shared message bus and memory so that each stays under its individual... | Medium | Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate.... |
| AGP-03 | UNCHANGED | Agentic | resource_competition | planner-agent | L3 — Agent Framework | Several agents compete for the same carrier rate and booking tools, and the heaviest user starves the... | Medium | Give each agent a quota on shared tools, queue work fairly and alert when one agent holds a tool for longer than its slot. Recommended controls... |
| AGP-04 | UNCHANGED | Agentic | temporal_attack | worker-2 | L3 — Agent Framework | State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run... | Medium | Expire persisted instructions, re-review any state that scheduled runs read and compare behaviour against pre-run snapshots. Recommended controls... |
| AGP-05 | UNCHANGED | Agentic | communication_vulnerability | worker-2 | L3 — Agent Framework | Messages between the planner and its workers travel over a shared channel with no per-sender signature, so a... | Medium | Sign each inter-agent message with the sender's key, include a nonce and reject replays. Recommended controls: authenticated channels between... |
| AGP-06 | UNCHANGED | Agentic | emergent_behavior | tool-server-1 | L3 — Agent Framework | Interacting planning and routing agents amplify each other's outputs through feedback until their combined... | Medium | Add fail-safe stop conditions for the planning loop, bound the actions each cycle may take and evaluate collective behaviour in staging.... |
| AGP-07 | UNCHANGED | Agentic | emergent_behavior | tool-server-1 | L3 — Agent Framework | The intake and planning agents adjust to each other's phrasing over many runs until requests are structured... | Medium | Track the distribution of structured requests over time and alert on drift. Recommended controls: behavioural baselining and periodic replay... |
| TE-1 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions... | Medium | Disclose that intake-agent is an automated agent at the start of each session and avoid human-like names or personal claims. |
| TE-2 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful... | Medium | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. |
| TE-7 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful... | Medium | Neutralise urgency and pressure wording in intake-agent, present alternatives with their trade-offs and require a deliberate action to approve. |
| LLM-2 | UNCHANGED | LLM | — | edge-gateway | L4 — Deployment Infrastructure | Prompt content logged by client-portal is later replayed to edge-gateway for evaluation, carrying planted... | Medium | Mark replayed prompts as untrusted when edge-gateway processes them, and exclude logged content from any privileged instruction slot. |
| LLM-6 | UNCHANGED | LLM | — | tool-server-1 | L3 — Agent Framework | Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks... | Medium | Normalise and decode inputs before filtering in tool-server-1, apply semantic checks instead of keyword lists and review filter misses weekly. |
| LLM-7 | UNCHANGED | LLM | — | model-gateway | L1 — Foundation Model | Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer... | Medium | Score retrieved passages for instruction-like content before model-gateway uses them, attribute every passage to its source and cap how much any... |
| LLM-8 | UNCHANGED | LLM | — | model-gateway | L1 — Foundation Model | Model weights or adapters served by model-gateway are readable by operators and by any process sharing the host. | Medium | Store the weights for model-gateway encrypted with keys in a hardware-backed service, restrict loading to the serving identity and audit every access. |
| OI-1 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of... | Medium | Validate URLs from intake-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. |
| OI-4 | UNCHANGED | LLM | — | planner-agent | L3 — Agent Framework | planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of... | Medium | Validate URLs from planner-agent against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network. |
| MI-5 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Outputs from intake-agent flow into decisions without a review step, so one wrong answer is repeated across... | Medium | Route decisions based on the output of intake-agent through human review above a risk threshold and audit a subset of the remainder. |
| MI-7 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. | Medium | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. |
| MI-8 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | intake-agent states carrier rules and customs requirements as fact without grounding them in a cited source... | Medium | Require intake-agent to cite a retrievable source for each factual claim, show the citations and decline to answer when none is found. |
| MI-9 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Confident wording from intake-agent hides low retrieval quality, so operators cannot tell a grounded answer... | Medium | Expose retrieval strength alongside the answers of intake-agent and switch to an explicit uncertainty message below a threshold. |
| S-6 | UNCHANGED | Spoofing | trust_exploitation | planner-agent | L3 — Agent Framework | An unauthenticated callback or health route on planner-agent accepts requests that downstream code treats as... | Low | Remove implicit trust in route names: authenticate every route of planner-agent, including callbacks and health checks, and drop requests that... |
| S-11 | UNCHANGED | Spoofing | — | partner-sandbox | L7 — Agent Ecosystem | An unauthenticated callback or health route on partner-sandbox accepts requests that downstream code treats... | Low | Remove implicit trust in route names: authenticate every route of partner-sandbox, including callbacks and health checks, and drop requests that... |
| T-6 | UNCHANGED | Tampering | — | worker-2 | L3 — Agent Framework | An attacker who can write to the channel between vector-store-a and worker-2 modifies work orders and route... | Low | Sign messages between vector-store-a and worker-2 with a per-service key and verify the signature and a monotonic counter before accepting any change. |
| R-1 | UNCHANGED | Repudiation | — | client-portal | L7 — Agent Ecosystem | Operators approve changes to operator requests and approval decisions through a chat message or ticket... | Low | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| R-3 | UNCHANGED | Repudiation | — | auth-broker | L6 — Security and Compliance | Delegated actions performed by auth-broker on behalf of a user are recorded under the service identity... | Low | Carry the originating user and the approval reference through every delegated call made by auth-broker, and record both in the audit entry. |
| R-5 | UNCHANGED | Repudiation | — | planner-agent | L3 — Agent Framework | Clock drift between planner-agent and model-gateway leaves events in inconsistent order, so the sequence of... | Low | Synchronise planner-agent and model-gateway to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| R-7 | UNCHANGED | Repudiation | — | tool-server-1 | L3 — Agent Framework | Operators approve changes to tool call arguments and results through a chat message or ticket comment that... | Low | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| I-1 | UNCHANGED | Information Disclosure | — | edge-gateway | L4 — Deployment Infrastructure | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that... | Low | Pass the bearer token to edge-gateway through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| I-6 | UNCHANGED | Information Disclosure | — | tool-server-1 | L3 — Agent Framework | Cross-tenant filters on tool-server-1 are applied in application code only, so one missing predicate exposes... | Low | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-9 | UNCHANGED | Information Disclosure | — | audit-ledger | L6 — Security and Compliance | approval and tool call records held by audit-ledger are readable by any service in the Operations Zone that... | Low | Grant access to approval and tool call records per workload identity with least privilege, enforce it at audit-ledger and remove network-position... |
| D-5 | UNCHANGED | Denial of Service | resource_competition | worker-2 | L3 — Agent Framework | Retry storms from vector-store-a multiply the load on worker-2 when it slows down, turning a brief delay... | Low | Add jittered exponential backoff and a retry budget to vector-store-a, and enable a circuit breaker so that worker-2 can recover. |
| D-6 | UNCHANGED | Denial of Service | resource_competition | tool-server-1 | L3 — Agent Framework | A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and... | Low | Set explicit concurrency and queue limits on tool-server-1, shed load with a clear status when saturated and apply per-caller quotas. |
| D-9 | UNCHANGED | Denial of Service | — | audit-ledger | L6 — Security and Compliance | Expensive queries over approval and tool call records can be triggered by any authorised caller of... | Low | Enforce cost limits and pagination on queries to audit-ledger, run heavy work on a separate pool and cancel queries that exceed the budget. |
| E-1 | UNCHANGED | Elevation of Privilege | — | edge-gateway | L4 — Deployment Infrastructure | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read... | Low | Check ownership or entitlement for every object reference at edge-gateway on the server, and deny by default when the check cannot be made. |
| E-8 | UNCHANGED | Elevation of Privilege | — | tool-server-1 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask tool-server-1 to act on tool call arguments and... | Low | Pass the caller's authority through to tool-server-1 and evaluate the original caller's rights, never those of audit-ledger, for every delegated... |
| R-2 | UNCHANGED | Repudiation | — | edge-gateway | L4 — Deployment Infrastructure | Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence... | Note | Write the records of edge-gateway to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| I-7 | UNCHANGED | Information Disclosure | — | model-gateway | L1 — Foundation Model | Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes... | Note | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| TE-3 | UNCHANGED | Agentic | trust_exploitation | intake-agent | L3 — Agent Framework | intake-agent builds rapport over long sessions and starts to share unprompted details about earlier operators. | Note | Isolate sessions of intake-agent per operator, forbid recall of other operators' details and review long sessions for rapport patterns. |
| MI-2 | UNCHANGED | LLM | — | intake-agent | L3 — Agent Framework | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. | Note | Stamp every source used by intake-agent with an effective date, suppress answers built on expired sources and alert owners when content ages out. |

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| S-1 | [] |
| T-7 | [] |
| I-3 | [] |
| D-2 | [] |
| D-4 | [] |
| D-8 | [] |
| E-5 | [] |
| E-7 | [] |
| AG-2 | [] |
| AG-3 | [] |
| AG-4 | [] |
| TE-5 | [] |
| TE-8 | [] |
| LLM-4 | [] |
| OI-3 | [] |
| OI-6 | [] |
| MI-3 | [] |
| MI-6 | [] |
| S-4 | [] |
| S-5 | [] |
| S-7 | [] |
| S-8 | [] |
| S-9 | [] |
| S-10 | [] |
| T-3 | [] |
| T-4 | [] |
| T-5 | [] |
| T-8 | [] |
| T-9 | [] |
| T-10 | [] |
| R-4 | [] |
| I-2 | [] |
| I-4 | [] |
| I-5 | [] |
| D-1 | [] |
| D-7 | [] |
| E-2 | [] |
| AG-5 | [] |
| AG-6 | [] |
| TE-4 | [] |
| TE-6 | [] |
| TE-9 | [] |
| LLM-1 | [] |
| LLM-3 | [] |
| LLM-5 | [] |
| LLM-9 | [] |
| OI-2 | [] |
| OI-5 | [] |
| OI-7 | [] |
| OI-8 | [] |
| OI-9 | [] |
| MI-1 | [] |
| MI-4 | [] |
| S-2 | [] |
| S-3 | [] |
| T-1 | [] |
| T-2 | [] |
| R-6 | [] |
| R-8 | [] |
| R-9 | [] |
| R-10 | [] |
| I-8 | [] |
| D-3 | [] |
| E-3 | [] |
| E-4 | [] |
| E-6 | [] |
| E-9 | [] |
| AG-1 | [] |
| AG-7 | [] |
| AG-8 | [] |
| AG-9 | [] |
| AGP-01 | [] |
| AGP-02 | [] |
| AGP-03 | [] |
| AGP-04 | [] |
| AGP-05 | [] |
| AGP-06 | [] |
| AGP-07 | [] |
| TE-1 | [] |
| TE-2 | [] |
| TE-7 | [] |
| LLM-2 | [] |
| LLM-6 | [] |
| LLM-7 | [] |
| LLM-8 | [] |
| OI-1 | [] |
| OI-4 | [] |
| MI-5 | [] |
| MI-7 | [] |
| MI-8 | [] |
| MI-9 | [] |
| S-6 | [] |
| S-11 | [] |
| T-6 | [] |
| R-1 | [] |
| R-3 | [] |
| R-5 | [] |
| R-7 | [] |
| I-1 | [] |
| I-6 | [] |
| I-9 | [] |
| D-5 | [] |
| D-6 | [] |
| D-9 | [] |
| E-1 | [] |
| E-8 | [] |
| R-2 | [] |
| I-7 | [] |
| TE-3 | [] |
| MI-2 | [] |
