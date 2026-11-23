---
schema_version: "1.4"
date: "2026-11-23"
input_format: "free-text"
classification: "confidential"
run_id: "2026-11-23T10-00-00"
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

This file is the chain material of F-374's chain-cap variant: a threats.md cut down to the sections that attack-chains.py reads and that its outcome record lands between. The inventory it reads is beside it, under tachi-build/phase1/.

---

## 5. Coverage Matrix

The coverage tables are left out of this cut.

---

## 6. Risk Summary

The risk summary is left out of this cut.

---

## 7. Recommended Actions

All findings sorted by risk level descending, then by table order. Critical and High findings should be addressed before deployment.

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| S-2 | NEW | Spoofing | — | task-agent-249 | L3 — Agent Framework | A shared or long-lived session token on task-agent-249 lets anyone who obtains one copy authenticate as... | Critical | Replace the shared session token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| S-7 | NEW | Spoofing | — | tool-router-145 | L3 — Agent Framework | A shared or long-lived API token on tool-router-145 lets anyone who obtains one copy authenticate as every... | Critical | Replace the shared API token with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks... |
| S-16 | NEW | Spoofing | — | audit-vault-228 | L6 — Security and Compliance | A shared or long-lived session token on audit-vault-228 lets anyone who obtains one copy authenticate as... | Critical | Replace the shared session token with per-workload identities that rotate automatically, and alert when one identity authenticates from two... |
| S-19 | NEW | Spoofing | — | tool-router-85 | L3 — Agent Framework | An unauthenticated callback or health route on tool-router-85 accepts requests that downstream code treats... | Critical | Remove implicit trust in route names: authenticate every route of tool-router-85, including callbacks and health checks, and drop requests that... |
| T-2 | NEW | Tampering | — | feature-store-95 | L2 — Data Operations | Configuration of feature-store-95 can be rewritten by any service that holds the shared deployment... | Critical | Keep the configuration of feature-store-95 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-3 | NEW | Tampering | — | audit-vault-67 | L6 — Security and Compliance | Replay of an earlier valid update to job queue entries reaches audit-vault-67 because updates carry no nonce... | Critical | Add a nonce and a short expiry to every update accepted by audit-vault-67, store seen nonces for the validity window and reject any repeat. |
| T-4 | NEW | Tampering | — | task-agent-33 | L3 — Agent Framework | Configuration of task-agent-33 can be rewritten by any service that holds the shared deployment credential... | Critical | Keep the configuration of task-agent-33 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-5 | NEW | Tampering | — | deploy-hub-114 | L4 — Deployment Infrastructure | Backups and exports of feature vectors on deploy-hub-114 are writable by operators without a second... | Critical | Protect exports and backups of feature vectors with write-once storage and dual approval for restore, and verify checksums against a separately... |
| T-13 | NEW | Tampering | — | model-host-194 | L1 — Foundation Model | An attacker who can write to the channel between tool-router-195 and model-host-194 modifies model prompts... | Critical | Sign messages between tool-router-195 and model-host-194 with a per-service key and verify the signature and a monotonic counter before accepting... |
| T-16 | NEW | Tampering | — | embed-node-144 | L1 — Foundation Model | A race between concurrent writers lets an attacker overwrite feature vectors on embed-node-144 after... | Critical | Make validation and use atomic: take a version-checked write or compare-and-set on feature vectors, and reject updates whose version no longer... |
| T-17 | NEW | Tampering | — | audit-vault-171 | L6 — Security and Compliance | Unsanitised audit records reach audit-vault-171 and are processed as trusted structure, so crafted input... | Critical | Validate audit records against a strict schema at the boundary of audit-vault-171, reject unknown fields and normalise encodings before any... |
| T-20 | NEW | Tampering | — | embed-node-98 | L1 — Foundation Model | Backups and exports of partner requests on embed-node-98 are writable by operators without a second... | Critical | Protect exports and backups of partner requests with write-once storage and dual approval for restore, and verify checksums against a separately... |
| T-21 | NEW | Tampering | — | audit-vault-211 | L6 — Security and Compliance | Replay of an earlier valid update to partner requests reaches audit-vault-211 because updates carry no nonce... | Critical | Add a nonce and a short expiry to every update accepted by audit-vault-211, store seen nonces for the validity window and reject any repeat. |
| T-28 | NEW | Tampering | — | audit-vault-219 | L6 — Security and Compliance | Configuration of audit-vault-219 can be rewritten by any service that holds the shared deployment... | Critical | Keep the configuration of audit-vault-219 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-36 | NEW | Tampering | — | deploy-hub-210 | L4 — Deployment Infrastructure | Configuration of deploy-hub-210 can be rewritten by any service that holds the shared deployment credential... | Critical | Keep the configuration of deploy-hub-210 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-38 | NEW | Tampering | — | user-portal-238 | L7 — Agent Ecosystem | Serialised objects arriving from feature-store-239 are deserialised by user-portal-238 with permissive type... | Critical | Replace permissive deserialisation in user-portal-238 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-39 | NEW | Tampering | — | legacy-adapter-59 | Unclassified | Backups and exports of partner requests on legacy-adapter-59 are writable by operators without a second... | Critical | Protect exports and backups of partner requests with write-once storage and dual approval for restore, and verify checksums against a separately... |
| T-40 | NEW | Tampering | — | feature-store-200 | L2 — Data Operations | An attacker who can write to the channel between task-agent-201 and feature-store-200 modifies feature... | Critical | Sign messages between task-agent-201 and feature-store-200 with a per-service key and verify the signature and a monotonic counter before... |
| T-41 | NEW | Tampering | — | tool-router-189 | L3 — Agent Framework | An update to tool-router-189 is pulled without provenance checks, so a poisoned package can alter how audit... | Critical | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of tool-router-189 when a component lacks a... |
| T-42 | NEW | Tampering | — | partner-api-190 | L7 — Agent Ecosystem | A race between concurrent writers lets an attacker overwrite job queue entries on partner-api-190 after... | Critical | Make validation and use atomic: take a version-checked write or compare-and-set on job queue entries, and reject updates whose version no longer... |
| T-43 | NEW | Tampering | — | policy-gate-163 | L6 — Security and Compliance | Configuration of policy-gate-163 can be rewritten by any service that holds the shared deployment... | Critical | Keep the configuration of policy-gate-163 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-45 | NEW | Tampering | — | feature-store-239 | L2 — Data Operations | An update to feature-store-239 is pulled without provenance checks, so a poisoned package can alter how... | Critical | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of feature-store-239 when a component lacks... |
| T-50 | NEW | Tampering | — | vector-index-104 | L2 — Data Operations | An update to vector-index-104 is pulled without provenance checks, so a poisoned package can alter how model... | Critical | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of vector-index-104 when a component lacks a... |
| T-54 | NEW | Tampering | — | deploy-hub-66 | L4 — Deployment Infrastructure | Serialised objects arriving from audit-vault-67 are deserialised by deploy-hub-66 with permissive type... | Critical | Replace permissive deserialisation in deploy-hub-66 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-55 | NEW | Tampering | — | embed-node-96 | L1 — Foundation Model | An attacker who can write to the channel between task-agent-97 and embed-node-96 modifies job queue entries... | Critical | Sign messages between task-agent-97 and embed-node-96 with a per-service key and verify the signature and a monotonic counter before accepting any... |
| T-59 | NEW | Tampering | — | audit-vault-9 | L6 — Security and Compliance | Configuration of audit-vault-9 can be rewritten by any service that holds the shared deployment credential... | Critical | Keep the configuration of audit-vault-9 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-64 | NEW | Tampering | — | trace-sink-122 | L5 — Evaluation and Observability | Replay of an earlier valid update to feature vectors reaches trace-sink-122 because updates carry no nonce... | Critical | Add a nonce and a short expiry to every update accepted by trace-sink-122, store seen nonces for the validity window and reject any repeat. |
| T-67 | NEW | Tampering | — | partner-api-92 | L7 — Agent Ecosystem | Replay of an earlier valid update to model prompts reaches partner-api-92 because updates carry no nonce or... | Critical | Add a nonce and a short expiry to every update accepted by partner-api-92, store seen nonces for the validity window and reject any repeat. |
| T-68 | NEW | Tampering | — | user-portal-188 | L7 — Agent Ecosystem | Configuration of user-portal-188 can be rewritten by any service that holds the shared deployment... | Critical | Keep the configuration of user-portal-188 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| R-1 | NEW | Repudiation | — | eval-bench-174 | L5 — Evaluation and Observability | Clock drift between eval-bench-174 and tool-router-175 leaves events in inconsistent order, so the sequence... | Critical | Synchronise eval-bench-174 and tool-router-175 to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| R-2 | NEW | Repudiation | — | tool-router-127 | L3 — Agent Framework | Log entries from tool-router-127 can be edited or deleted by the same operators who administer it, so... | Critical | Write the records of tool-router-127 to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| R-4 | NEW | Repudiation | — | audit-vault-125 | L6 — Security and Compliance | Operators approve changes to model prompts through a chat message or ticket comment that is not bound to the... | Critical | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| R-5 | NEW | Repudiation | — | eval-bench-222 | L5 — Evaluation and Observability | Operators approve changes to job queue entries through a chat message or ticket comment that is not bound to... | Critical | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| R-10 | NEW | Repudiation | — | eval-bench-172 | L5 — Evaluation and Observability | Actions taken through eval-bench-172 are logged without the authenticated principal or a request identifier... | Critical | Log the verified principal, request identifier, source address and outcome for every state change in eval-bench-172, and ship the records to the... |
| R-14 | NEW | Repudiation | — | eval-bench-220 | L5 — Evaluation and Observability | Failed and rejected attempts against eval-bench-220 are not logged, so probing of feature vectors leaves no... | Critical | Log denied and malformed requests to eval-bench-220 at a retained severity, aggregate them per source and alert on sustained probing. |
| I-1 | NEW | Information Disclosure | — | tool-router-87 | L3 — Agent Framework | Verbose error responses from tool-router-87 reveal internal paths, query text and identifiers of model... | Critical | Return generic error codes from tool-router-87, log the detail on the server only and strip stack traces and identifiers from every external response. |
| I-8 | NEW | Information Disclosure | — | feature-store-49 | L2 — Data Operations | Backups of feature vectors taken from feature-store-49 are stored unencrypted in a shared location that... | Critical | Encrypt backups of feature vectors with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-9 | NEW | Information Disclosure | — | embed-node-102 | L1 — Foundation Model | Logs and traces emitted by embed-node-102 include raw feature vectors, so anyone with access to the logging... | Critical | Redact or tokenise sensitive fields before embed-node-102 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-10 | NEW | Information Disclosure | — | tool-router-183 | L3 — Agent Framework | Secrets such as the session token for tool-router-183 appear in process arguments and environment dumps that... | Critical | Pass the session token to tool-router-183 through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after... |
| I-12 | NEW | Information Disclosure | — | deploy-hub-15 | L4 — Deployment Infrastructure | Data in transit between task-agent-16 and deploy-hub-15 is protected only on the outer hop, which leaves... | Critical | Keep TLS end to end between task-agent-16 and deploy-hub-15, disable plaintext listeners and verify the negotiated protocol version in deployment... |
| I-13 | NEW | Information Disclosure | — | tool-router-160 | L3 — Agent Framework | partner requests held by tool-router-160 are readable by any service in the Agent Runtime Zone that shares... | Critical | Grant access to partner requests per workload identity with least privilege, enforce it at tool-router-160 and remove network-position trust... |
| I-17 | NEW | Information Disclosure | — | policy-gate-263 | L6 — Security and Compliance | Secrets such as the service credential for policy-gate-263 appear in process arguments and environment dumps... | Critical | Pass the service credential to policy-gate-263 through a secret manager mount, exclude it from process listings and diagnostics, and rotate it... |
| I-19 | NEW | Information Disclosure | — | partner-api-161 | L7 — Agent Ecosystem | audit records held by partner-api-161 are readable by any service in the Edge DMZ that shares the same... | Critical | Grant access to audit records per workload identity with least privilege, enforce it at partner-api-161 and remove network-position trust within... |
| I-22 | NEW | Information Disclosure | — | tool-router-208 | L3 — Agent Framework | Data in transit between partner-api-209 and tool-router-208 is protected only on the outer hop, which leaves... | Critical | Keep TLS end to end between partner-api-209 and tool-router-208, disable plaintext listeners and verify the negotiated protocol version in... |
| I-28 | NEW | Information Disclosure | — | partner-api-29 | L7 — Agent Ecosystem | A timing or size difference in the responses of partner-api-29 lets an observer infer whether specific... | Critical | Equalise response size and timing for existence checks in partner-api-29, and return the same status for present and absent records. |
| I-29 | NEW | Information Disclosure | — | user-portal-109 | L7 — Agent Ecosystem | audit records held by user-portal-109 are readable by any service in the Edge DMZ that shares the same... | Critical | Grant access to audit records per workload identity with least privilege, enforce it at user-portal-109 and remove network-position trust within... |
| I-34 | NEW | Information Disclosure | — | task-agent-203 | L3 — Agent Framework | Backups of trace spans taken from task-agent-203 are stored unencrypted in a shared location that wider... | Critical | Encrypt backups of trace spans with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-38 | NEW | Information Disclosure | — | runtime-pool-70 | L4 — Deployment Infrastructure | Verbose error responses from runtime-pool-70 reveal internal paths, query text and identifiers of audit... | Critical | Return generic error codes from runtime-pool-70, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-41 | NEW | Information Disclosure | — | tool-router-155 | L3 — Agent Framework | Verbose error responses from tool-router-155 reveal internal paths, query text and identifiers of policy... | Critical | Return generic error codes from tool-router-155, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-47 | NEW | Information Disclosure | — | feature-store-250 | L2 — Data Operations | Logs and traces emitted by feature-store-250 include raw model prompts, so anyone with access to the logging... | Critical | Redact or tokenise sensitive fields before feature-store-250 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-51 | NEW | Information Disclosure | — | vector-index-154 | L2 — Data Operations | Cross-tenant filters on vector-index-154 are applied in application code only, so one missing predicate... | Critical | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-57 | NEW | Information Disclosure | — | partner-api-151 | L7 — Agent Ecosystem | Backups of job queue entries taken from partner-api-151 are stored unencrypted in a shared location that... | Critical | Encrypt backups of job queue entries with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-59 | NEW | Information Disclosure | — | vector-index-13 | L2 — Data Operations | Verbose error responses from vector-index-13 reveal internal paths, query text and identifiers of trace... | Critical | Return generic error codes from vector-index-13, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-61 | NEW | Information Disclosure | — | deploy-hub-118 | L4 — Deployment Infrastructure | A timing or size difference in the responses of deploy-hub-118 lets an observer infer whether specific... | Critical | Equalise response size and timing for existence checks in deploy-hub-118, and return the same status for present and absent records. |
| I-63 | NEW | Information Disclosure | — | feature-store-106 | L2 — Data Operations | Logs and traces emitted by feature-store-106 include raw model prompts, so anyone with access to the logging... | Critical | Redact or tokenise sensitive fields before feature-store-106 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-66 | NEW | Information Disclosure | — | user-portal-52 | L7 — Agent Ecosystem | Logs and traces emitted by user-portal-52 include raw audit records, so anyone with access to the logging... | Critical | Redact or tokenise sensitive fields before user-portal-52 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-75 | NEW | Information Disclosure | — | feature-store-252 | L2 — Data Operations | Backups of audit records taken from feature-store-252 are stored unencrypted in a shared location that wider... | Critical | Encrypt backups of audit records with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-79 | NEW | Information Disclosure | — | embed-node-246 | L1 — Foundation Model | A timing or size difference in the responses of embed-node-246 lets an observer infer whether specific... | Critical | Equalise response size and timing for existence checks in embed-node-246, and return the same status for present and absent records. |
| I-81 | NEW | Information Disclosure | — | partner-api-209 | L7 — Agent Ecosystem | A timing or size difference in the responses of partner-api-209 lets an observer infer whether specific... | Critical | Equalise response size and timing for existence checks in partner-api-209, and return the same status for present and absent records. |
| D-3 | NEW | Denial of Service | — | partner-api-265 | L7 — Agent Ecosystem | Expensive queries over audit records can be triggered by any authorised caller of partner-api-265, so one... | Critical | Enforce cost limits and pagination on queries to partner-api-265, run heavy work on a separate pool and cancel queries that exceed the budget. |
| D-4 | NEW | Denial of Service | — | policy-gate-129 | L6 — Security and Compliance | A single oversized or deeply nested payload makes policy-gate-129 spend disproportionate memory and CPU... | Critical | Cap payload size, nesting depth and parse time in policy-gate-129, and reject requests that exceed the limits before allocation. |
| D-7 | NEW | Denial of Service | — | partner-api-121 | L7 — Agent Ecosystem | A burst of requests exhausts the connection pool of partner-api-121, which queues work without a bound and... | Critical | Set explicit concurrency and queue limits on partner-api-121, shed load with a clear status when saturated and apply per-caller quotas. |
| D-8 | NEW | Denial of Service | — | deploy-hub-168 | L4 — Deployment Infrastructure | A slow-read attack holds connections to deploy-hub-168 open and ties up the workers handling trace spans... | Critical | Apply idle and total timeouts on every connection to deploy-hub-168, bound workers per client and move slow clients to a separate pool. |
| D-10 | NEW | Denial of Service | — | policy-gate-177 | L6 — Security and Compliance | Expensive queries over job queue entries can be triggered by any authorised caller of policy-gate-177, so... | Critical | Enforce cost limits and pagination on queries to policy-gate-177, run heavy work on a separate pool and cancel queries that exceed the budget. |
| D-16 | NEW | Denial of Service | — | deploy-hub-72 | L4 — Deployment Infrastructure | A single oversized or deeply nested payload makes deploy-hub-72 spend disproportionate memory and CPU... | Critical | Cap payload size, nesting depth and parse time in deploy-hub-72, and reject requests that exceed the limits before allocation. |
| D-20 | NEW | Denial of Service | — | partner-api-217 | L7 — Agent Ecosystem | Unbounded growth of stored audit records on partner-api-217 fills its volume, after which writes fail for... | Critical | Set quotas and retention for audit records on partner-api-217, alert at eighty percent capacity and reserve space for control-plane writes. |
| E-3 | NEW | Elevation of Privilege | — | policy-gate-232 | L6 — Security and Compliance | Role claims carried in the API token presented to policy-gate-232 are honoured without confirmation against... | Critical | Resolve roles for policy-gate-232 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| E-5 | NEW | Elevation of Privilege | — | task-agent-206 | L3 — Agent Framework | Role claims carried in the API token presented to task-agent-206 are honoured without confirmation against... | Critical | Resolve roles for task-agent-206 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| E-7 | NEW | Elevation of Privilege | — | task-agent-20 | L3 — Agent Framework | task-agent-20 runs with broader permissions than its function needs, so a flaw in handling job queue entries... | Critical | Reduce the permissions of task-agent-20 to the minimum for job queue entries, drop capabilities it does not use and review the grants on a schedule. |
| E-9 | NEW | Elevation of Privilege | — | tool-router-110 | L3 — Agent Framework | Role claims carried in the API token presented to tool-router-110 are honoured without confirmation against... | Critical | Resolve roles for tool-router-110 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| E-15 | NEW | Elevation of Privilege | — | user-portal-235 | L7 — Agent Ecosystem | user-portal-235 runs with broader permissions than its function needs, so a flaw in handling policy... | Critical | Reduce the permissions of user-portal-235 to the minimum for policy decisions, drop capabilities it does not use and review the grants on a schedule. |
| E-16 | NEW | Elevation of Privilege | — | task-agent-83 | L3 — Agent Framework | An administrative interface of task-agent-83 is reachable from the same network as ordinary callers and... | Critical | Move the administrative interface of task-agent-83 behind a separate listener with strong authentication, network restriction and per-user accounts. |
| E-21 | NEW | Elevation of Privilege | — | partner-api-63 | L7 — Agent Ecosystem | Multi-tenant separation in partner-api-63 depends on a request header that clients can set, allowing one... | Critical | Derive the tenant for partner-api-63 from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI. |
| E-27 | NEW | Elevation of Privilege | — | tool-router-23 | L3 — Agent Framework | tool-router-23 runs with broader permissions than its function needs, so a flaw in handling partner requests... | Critical | Reduce the permissions of tool-router-23 to the minimum for partner requests, drop capabilities it does not use and review the grants on a schedule. |
| E-29 | NEW | Elevation of Privilege | — | partner-api-207 | L7 — Agent Ecosystem | A privileged maintenance task of partner-api-207 can be triggered through a queue message that any producer... | Critical | Restrict who can publish maintenance messages that partner-api-207 acts on, sign them and require an authorised approver for destructive operations. |
| E-33 | NEW | Elevation of Privilege | — | partner-api-7 | L7 — Agent Ecosystem | Role claims carried in the service credential presented to partner-api-7 are honoured without confirmation... | Critical | Resolve roles for partner-api-7 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller. |
| E-36 | NEW | Elevation of Privilege | — | audit-vault-138 | L6 — Security and Compliance | Multi-tenant separation in audit-vault-138 depends on a request header that clients can set, allowing one... | Critical | Derive the tenant for audit-vault-138 from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI. |
| E-37 | NEW | Elevation of Privilege | — | task-agent-147 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask task-agent-147 to act on feature vectors using the... | Critical | Pass the caller's authority through to task-agent-147 and evaluate the original caller's rights, never those of embed-node-146, for every... |
| E-38 | NEW | Elevation of Privilege | — | user-portal-11 | L7 — Agent Ecosystem | user-portal-11 runs with broader permissions than its function needs, so a flaw in handling partner requests... | Critical | Reduce the permissions of user-portal-11 to the minimum for partner requests, drop capabilities it does not use and review the grants on a schedule. |
| E-41 | NEW | Elevation of Privilege | — | task-agent-137 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask task-agent-137 to act on model prompts using the... | Critical | Pass the caller's authority through to task-agent-137 and evaluate the original caller's rights, never those of audit-vault-136, for every... |
| AG-1 | NEW | Agentic | — | tool-router-44 | L3 — Agent Framework | The goal or instruction set of tool-router-44 can be changed through content it reads, steering it toward... | Critical | Keep the goals of tool-router-44 in signed configuration that content cannot alter, and refuse plan changes that originate from retrieved text. |
| LLM-1 | NEW | LLM | — | embed-node-50 | L1 — Foundation Model | Instructions hidden in policy decisions reach the prompt of embed-node-50 and override its system guidance... | Critical | Separate instructions from content in the prompts of embed-node-50, delimit untrusted text and run an injection classifier before the model sees it. |
| S-3 | NEW | Spoofing | — | task-agent-133 | L3 — Agent Framework | Low-entropy identifiers accepted by task-agent-133 double as credentials, so an attacker who enumerates them... | High | Separate identifiers from secrets, generate secrets from a cryptographic random source of at least 128 bits and rate-limit failed lookups against... |
| S-8 | NEW | Spoofing | — | tool-router-193 | L3 — Agent Framework | Session fixation against tool-router-193 lets an attacker pre-seed an identifier and reuse the session after... | High | Issue a fresh session identifier on every authentication and privilege change, set strict cookie attributes and invalidate any identifier supplied... |
| S-10 | NEW | Spoofing | — | tool-router-181 | L3 — Agent Framework | An unauthenticated callback or health route on tool-router-181 accepts requests that downstream code treats... | High | Remove implicit trust in route names: authenticate every route of tool-router-181, including callbacks and health checks, and drop requests that... |
| S-12 | NEW | Spoofing | — | task-agent-229 | L3 — Agent Framework | Session fixation against task-agent-229 lets an attacker pre-seed an identifier and reuse the session after... | High | Issue a fresh session identifier on every authentication and privilege change, set strict cookie attributes and invalidate any identifier supplied... |
| S-13 | NEW | Spoofing | — | task-agent-241 | L3 — Agent Framework | A compromised peer presents a forged service identity to task-agent-241, and task-agent-241 accepts the... | High | Require mutual TLS between embed-node-240 and task-agent-241 and validate the full certificate chain, issuer and audience on every request instead... |
| S-14 | NEW | Spoofing | — | audit-vault-84 | L6 — Security and Compliance | Low-entropy identifiers accepted by audit-vault-84 double as credentials, so an attacker who enumerates them... | High | Separate identifiers from secrets, generate secrets from a cryptographic random source of at least 128 bits and rate-limit failed lookups against... |
| S-15 | NEW | Spoofing | — | legacy-adapter-56 | Unclassified | An attacker replays a captured signing key against legacy-adapter-56, which does not bind the credential to... | High | Bind each signing key to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| S-17 | NEW | Spoofing | — | tool-router-153 | L3 — Agent Framework | Session fixation against tool-router-153 lets an attacker pre-seed an identifier and reuse the session after... | High | Issue a fresh session identifier on every authentication and privilege change, set strict cookie attributes and invalidate any identifier supplied... |
| T-7 | NEW | Tampering | — | audit-vault-5 | L6 — Security and Compliance | Serialised objects arriving from runtime-pool-4 are deserialised by audit-vault-5 with permissive type... | High | Replace permissive deserialisation in audit-vault-5 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-8 | NEW | Tampering | — | partner-api-30 | L7 — Agent Ecosystem | A race between concurrent writers lets an attacker overwrite partner requests on partner-api-30 after... | High | Make validation and use atomic: take a version-checked write or compare-and-set on partner requests, and reject updates whose version no longer... |
| T-11 | NEW | Tampering | — | vector-index-24 | L2 — Data Operations | An update to vector-index-24 is pulled without provenance checks, so a poisoned package can alter how trace... | High | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of vector-index-24 when a component lacks a... |
| T-12 | NEW | Tampering | — | policy-gate-123 | L6 — Security and Compliance | An update to policy-gate-123 is pulled without provenance checks, so a poisoned package can alter how policy... | High | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of policy-gate-123 when a component lacks a... |
| T-14 | NEW | Tampering | — | policy-gate-226 | L6 — Security and Compliance | Configuration of policy-gate-226 can be rewritten by any service that holds the shared deployment... | High | Keep the configuration of policy-gate-226 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-18 | NEW | Tampering | — | policy-gate-130 | L6 — Security and Compliance | A race between concurrent writers lets an attacker overwrite policy decisions on policy-gate-130 after... | High | Make validation and use atomic: take a version-checked write or compare-and-set on policy decisions, and reject updates whose version no longer... |
| T-19 | NEW | Tampering | — | model-host-21 | L1 — Foundation Model | An update to model-host-21 is pulled without provenance checks, so a poisoned package can alter how trace... | High | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of model-host-21 when a component lacks a... |
| T-23 | NEW | Tampering | — | eval-bench-1 | L5 — Evaluation and Observability | Unsanitised policy decisions reach eval-bench-1 and are processed as trusted structure, so crafted input... | High | Validate policy decisions against a strict schema at the boundary of eval-bench-1, reject unknown fields and normalise encodings before any... |
| T-25 | NEW | Tampering | — | vector-index-191 | L2 — Data Operations | An attacker who can write to the channel between partner-api-190 and vector-index-191 modifies trace spans... | High | Sign messages between partner-api-190 and vector-index-191 with a per-service key and verify the signature and a monotonic counter before... |
| T-26 | NEW | Tampering | — | embed-node-42 | L1 — Foundation Model | Serialised objects arriving from task-agent-43 are deserialised by embed-node-42 with permissive type... | High | Replace permissive deserialisation in embed-node-42 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-27 | NEW | Tampering | — | user-portal-140 | L7 — Agent Ecosystem | Unsanitised job queue entries reach user-portal-140 and are processed as trusted structure, so crafted input... | High | Validate job queue entries against a strict schema at the boundary of user-portal-140, reject unknown fields and normalise encodings before any... |
| T-29 | NEW | Tampering | — | deploy-hub-8 | L4 — Deployment Infrastructure | Replay of an earlier valid update to trace spans reaches deploy-hub-8 because updates carry no nonce or... | High | Add a nonce and a short expiry to every update accepted by deploy-hub-8, store seen nonces for the validity window and reject any repeat. |
| T-30 | NEW | Tampering | — | audit-vault-75 | L6 — Security and Compliance | A race between concurrent writers lets an attacker overwrite policy decisions on audit-vault-75 after... | High | Make validation and use atomic: take a version-checked write or compare-and-set on policy decisions, and reject updates whose version no longer... |
| T-32 | NEW | Tampering | — | audit-vault-115 | L6 — Security and Compliance | An attacker who can write to the channel between deploy-hub-114 and audit-vault-115 modifies model prompts... | High | Sign messages between deploy-hub-114 and audit-vault-115 with a per-service key and verify the signature and a monotonic counter before accepting... |
| T-33 | NEW | Tampering | — | runtime-pool-258 | L4 — Deployment Infrastructure | A race between concurrent writers lets an attacker overwrite job queue entries on runtime-pool-258 after... | High | Make validation and use atomic: take a version-checked write or compare-and-set on job queue entries, and reject updates whose version no longer... |
| T-44 | NEW | Tampering | — | policy-gate-19 | L6 — Security and Compliance | A race between concurrent writers lets an attacker overwrite trace spans on policy-gate-19 after validation... | High | Make validation and use atomic: take a version-checked write or compare-and-set on trace spans, and reject updates whose version no longer matches. |
| T-46 | NEW | Tampering | — | task-agent-141 | L3 — Agent Framework | Replay of an earlier valid update to policy decisions reaches task-agent-141 because updates carry no nonce... | High | Add a nonce and a short expiry to every update accepted by task-agent-141, store seen nonces for the validity window and reject any repeat. |
| T-47 | NEW | Tampering | — | feature-store-143 | L2 — Data Operations | Unsanitised model prompts reach feature-store-143 and are processed as trusted structure, so crafted input... | High | Validate model prompts against a strict schema at the boundary of feature-store-143, reject unknown fields and normalise encodings before any... |
| T-48 | NEW | Tampering | — | trace-sink-170 | L5 — Evaluation and Observability | An update to trace-sink-170 is pulled without provenance checks, so a poisoned package can alter how trace... | High | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of trace-sink-170 when a component lacks a... |
| T-49 | NEW | Tampering | — | vector-index-54 | L2 — Data Operations | Serialised objects arriving from tool-router-55 are deserialised by vector-index-54 with permissive type... | High | Replace permissive deserialisation in vector-index-54 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-52 | NEW | Tampering | — | model-host-45 | L1 — Foundation Model | A race between concurrent writers lets an attacker overwrite policy decisions on model-host-45 after... | High | Make validation and use atomic: take a version-checked write or compare-and-set on policy decisions, and reject updates whose version no longer... |
| T-53 | NEW | Tampering | — | user-portal-94 | L7 — Agent Ecosystem | Configuration of user-portal-94 can be rewritten by any service that holds the shared deployment credential... | High | Keep the configuration of user-portal-94 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-61 | NEW | Tampering | — | audit-vault-178 | L6 — Security and Compliance | A race between concurrent writers lets an attacker overwrite trace spans on audit-vault-178 after validation... | High | Make validation and use atomic: take a version-checked write or compare-and-set on trace spans, and reject updates whose version no longer matches. |
| T-62 | NEW | Tampering | — | tool-router-93 | L3 — Agent Framework | Replay of an earlier valid update to model prompts reaches tool-router-93 because updates carry no nonce or... | High | Add a nonce and a short expiry to every update accepted by tool-router-93, store seen nonces for the validity window and reject any repeat. |
| T-63 | NEW | Tampering | — | embed-node-192 | L1 — Foundation Model | Unsanitised job queue entries reach embed-node-192 and are processed as trusted structure, so crafted input... | High | Validate job queue entries against a strict schema at the boundary of embed-node-192, reject unknown fields and normalise encodings before any... |
| T-66 | NEW | Tampering | — | embed-node-242 | L1 — Foundation Model | Serialised objects arriving from task-agent-243 are deserialised by embed-node-242 with permissive type... | High | Replace permissive deserialisation in embed-node-242 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-69 | NEW | Tampering | — | task-agent-237 | L3 — Agent Framework | Configuration of task-agent-237 can be rewritten by any service that holds the shared deployment credential... | High | Keep the configuration of task-agent-237 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| R-8 | NEW | Repudiation | — | trace-sink-126 | L5 — Evaluation and Observability | Actions taken through trace-sink-126 are logged without the authenticated principal or a request identifier... | High | Log the verified principal, request identifier, source address and outcome for every state change in trace-sink-126, and ship the records to the... |
| R-12 | NEW | Repudiation | — | tool-router-79 | L3 — Agent Framework | Log entries from tool-router-79 can be edited or deleted by the same operators who administer it, so... | High | Write the records of tool-router-79 to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| R-13 | NEW | Repudiation | — | audit-vault-77 | L6 — Security and Compliance | Operators approve changes to audit records through a chat message or ticket comment that is not bound to the... | High | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| R-17 | NEW | Repudiation | — | policy-gate-221 | L6 — Security and Compliance | Clock drift between policy-gate-221 and eval-bench-220 leaves events in inconsistent order, so the sequence... | High | Synchronise policy-gate-221 and eval-bench-220 to a trusted time source, record monotonic sequence numbers with every event and alert when drift... |
| I-5 | NEW | Information Disclosure | — | policy-gate-167 | L6 — Security and Compliance | Data in transit between runtime-pool-166 and policy-gate-167 is protected only on the outer hop, which... | High | Keep TLS end to end between runtime-pool-166 and policy-gate-167, disable plaintext listeners and verify the negotiated protocol version in... |
| I-6 | NEW | Information Disclosure | — | user-portal-103 | L7 — Agent Ecosystem | Verbose error responses from user-portal-103 reveal internal paths, query text and identifiers of job queue... | High | Return generic error codes from user-portal-103, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-7 | NEW | Information Disclosure | — | runtime-pool-116 | L4 — Deployment Infrastructure | Verbose error responses from runtime-pool-116 reveal internal paths, query text and identifiers of feature... | High | Return generic error codes from runtime-pool-116, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-14 | NEW | Information Disclosure | — | task-agent-69 | L3 — Agent Framework | Cross-tenant filters on task-agent-69 are applied in application code only, so one missing predicate exposes... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-16 | NEW | Information Disclosure | — | partner-api-257 | L7 — Agent Ecosystem | A timing or size difference in the responses of partner-api-257 lets an observer infer whether specific... | High | Equalise response size and timing for existence checks in partner-api-257, and return the same status for present and absent records. |
| I-18 | NEW | Information Disclosure | — | embed-node-12 | L1 — Foundation Model | Verbose error responses from embed-node-12 reveal internal paths, query text and identifiers of model... | High | Return generic error codes from embed-node-12, log the detail on the server only and strip stack traces and identifiers from every external response. |
| I-24 | NEW | Information Disclosure | — | tool-router-27 | L3 — Agent Framework | A timing or size difference in the responses of tool-router-27 lets an observer infer whether specific... | High | Equalise response size and timing for existence checks in tool-router-27, and return the same status for present and absent records. |
| I-25 | NEW | Information Disclosure | — | model-host-51 | L1 — Foundation Model | Logs and traces emitted by model-host-51 include raw model prompts, so anyone with access to the logging... | High | Redact or tokenise sensitive fields before model-host-51 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-27 | NEW | Information Disclosure | — | feature-store-156 | L2 — Data Operations | Verbose error responses from feature-store-156 reveal internal paths, query text and identifiers of trace... | High | Return generic error codes from feature-store-156, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-39 | NEW | Information Disclosure | — | tool-router-231 | L3 — Agent Framework | Cross-tenant filters on tool-router-231 are applied in application code only, so one missing predicate... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-40 | NEW | Information Disclosure | — | audit-vault-134 | L6 — Security and Compliance | Data in transit between task-agent-135 and audit-vault-134 is protected only on the outer hop, which leaves... | High | Keep TLS end to end between task-agent-135 and audit-vault-134, disable plaintext listeners and verify the negotiated protocol version in... |
| I-42 | NEW | Information Disclosure | — | tool-router-107 | L3 — Agent Framework | feature vectors held by tool-router-107 are readable by any service in the Agent Runtime Zone that shares... | High | Grant access to feature vectors per workload identity with least privilege, enforce it at tool-router-107 and remove network-position trust within... |
| I-43 | NEW | Information Disclosure | — | feature-store-149 | L2 — Data Operations | Cross-tenant filters on feature-store-149 are applied in application code only, so one missing predicate... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-45 | NEW | Information Disclosure | — | task-agent-261 | L3 — Agent Framework | Backups of policy decisions taken from task-agent-261 are stored unencrypted in a shared location that wider... | High | Encrypt backups of policy decisions with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-46 | NEW | Information Disclosure | — | vector-index-57 | L2 — Data Operations | Verbose error responses from vector-index-57 reveal internal paths, query text and identifiers of audit... | High | Return generic error codes from vector-index-57, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-48 | NEW | Information Disclosure | — | partner-api-61 | L7 — Agent Ecosystem | Cross-tenant filters on partner-api-61 are applied in application code only, so one missing predicate... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-49 | NEW | Information Disclosure | — | task-agent-213 | L3 — Agent Framework | partner requests held by task-agent-213 are readable by any service in the Agent Runtime Zone that shares... | High | Grant access to partner requests per workload identity with least privilege, enforce it at task-agent-213 and remove network-position trust within... |
| I-52 | NEW | Information Disclosure | — | partner-api-65 | L7 — Agent Ecosystem | Logs and traces emitted by partner-api-65 include raw policy decisions, so anyone with access to the logging... | High | Redact or tokenise sensitive fields before partner-api-65 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-53 | NEW | Information Disclosure | — | embed-node-196 | L1 — Foundation Model | Cross-tenant filters on embed-node-196 are applied in application code only, so one missing predicate... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-62 | NEW | Information Disclosure | — | embed-node-244 | L1 — Foundation Model | Backups of feature vectors taken from embed-node-244 are stored unencrypted in a shared location that wider... | High | Encrypt backups of feature vectors with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-64 | NEW | Information Disclosure | — | task-agent-165 | L3 — Agent Framework | Logs and traces emitted by task-agent-165 include raw partner requests, so anyone with access to the logging... | High | Redact or tokenise sensitive fields before task-agent-165 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-65 | NEW | Information Disclosure | — | task-agent-16 | L3 — Agent Framework | A timing or size difference in the responses of task-agent-16 lets an observer infer whether specific... | High | Equalise response size and timing for existence checks in task-agent-16, and return the same status for present and absent records. |
| I-67 | NEW | Information Disclosure | — | partner-api-113 | L7 — Agent Ecosystem | job queue entries held by partner-api-113 are readable by any service in the Edge DMZ that shares the same... | High | Grant access to job queue entries per workload identity with least privilege, enforce it at partner-api-113 and remove network-position trust... |
| I-68 | NEW | Information Disclosure | — | embed-node-48 | L1 — Foundation Model | Cross-tenant filters on embed-node-48 are applied in application code only, so one missing predicate exposes... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-72 | NEW | Information Disclosure | — | embed-node-100 | L1 — Foundation Model | Verbose error responses from embed-node-100 reveal internal paths, query text and identifiers of model... | High | Return generic error codes from embed-node-100, log the detail on the server only and strip stack traces and identifiers from every external response. |
| I-73 | NEW | Information Disclosure | — | tool-router-64 | L3 — Agent Framework | Cross-tenant filters on tool-router-64 are applied in application code only, so one missing predicate... | High | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-76 | NEW | Information Disclosure | — | audit-vault-86 | L6 — Security and Compliance | Secrets such as the service credential for audit-vault-86 appear in process arguments and environment dumps... | High | Pass the service credential to audit-vault-86 through a secret manager mount, exclude it from process listings and diagnostics, and rotate it... |
| I-77 | NEW | Information Disclosure | — | task-agent-256 | L3 — Agent Framework | Logs and traces emitted by task-agent-256 include raw trace spans, so anyone with access to the logging... | High | Redact or tokenise sensitive fields before task-agent-256 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-78 | NEW | Information Disclosure | — | runtime-pool-214 | L4 — Deployment Infrastructure | Verbose error responses from runtime-pool-214 reveal internal paths, query text and identifiers of feature... | High | Return generic error codes from runtime-pool-214, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-87 | NEW | Information Disclosure | — | feature-store-204 | L2 — Data Operations | A timing or size difference in the responses of feature-store-204 lets an observer infer whether specific... | High | Equalise response size and timing for existence checks in feature-store-204, and return the same status for present and absent records. |
| I-88 | NEW | Information Disclosure | — | user-portal-199 | L7 — Agent Ecosystem | Data in transit between model-host-198 and user-portal-199 is protected only on the outer hop, which leaves... | High | Keep TLS end to end between model-host-198 and user-portal-199, disable plaintext listeners and verify the negotiated protocol version in... |
| D-1 | NEW | Denial of Service | — | audit-vault-81 | L6 — Security and Compliance | A dependency of audit-vault-81 becomes unavailable and the failure cascades because audit-vault-81 waits on... | High | Isolate calls from audit-vault-81 to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health. |
| D-2 | NEW | Denial of Service | — | runtime-pool-26 | L4 — Deployment Infrastructure | Retry storms from tool-router-25 multiply the load on runtime-pool-26 when it slows down, turning a brief... | High | Add jittered exponential backoff and a retry budget to tool-router-25, and enable a circuit breaker so that runtime-pool-26 can recover. |
| D-12 | NEW | Denial of Service | — | eval-bench-224 | L5 — Evaluation and Observability | A single oversized or deeply nested payload makes eval-bench-224 spend disproportionate memory and CPU... | High | Cap payload size, nesting depth and parse time in eval-bench-224, and reject requests that exceed the limits before allocation. |
| D-15 | NEW | Denial of Service | — | partner-api-73 | L7 — Agent Ecosystem | Expensive queries over model prompts can be triggered by any authorised caller of partner-api-73, so one... | High | Enforce cost limits and pagination on queries to partner-api-73, run heavy work on a separate pool and cancel queries that exceed the budget. |
| D-21 | NEW | Denial of Service | — | tool-router-25 | L3 — Agent Framework | A slow-read attack holds connections to tool-router-25 open and ties up the workers handling model prompts... | High | Apply idle and total timeouts on every connection to tool-router-25, bound workers per client and move slow clients to a separate pool. |
| E-4 | NEW | Elevation of Privilege | — | tool-router-3 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask tool-router-3 to act on policy decisions using the... | High | Pass the caller's authority through to tool-router-3 and evaluate the original caller's rights, never those of policy-gate-2, for every delegated... |
| E-6 | NEW | Elevation of Privilege | — | tool-router-131 | L3 — Agent Framework | A privileged maintenance task of tool-router-131 can be triggered through a queue message that any producer... | High | Restrict who can publish maintenance messages that tool-router-131 acts on, sign them and require an authorised approver for destructive operations. |
| E-8 | NEW | Elevation of Privilege | — | audit-vault-90 | L6 — Security and Compliance | Role claims carried in the signing key presented to audit-vault-90 are honoured without confirmation against... | High | Resolve roles for audit-vault-90 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| E-10 | NEW | Elevation of Privilege | — | policy-gate-88 | L6 — Security and Compliance | Object identifiers in requests to policy-gate-88 are trusted without an ownership check, so a caller can... | High | Check ownership or entitlement for every object reference at policy-gate-88 on the server, and deny by default when the check cannot be made. |
| E-11 | NEW | Elevation of Privilege | — | policy-gate-184 | L6 — Security and Compliance | policy-gate-184 runs with broader permissions than its function needs, so a flaw in handling model prompts... | High | Reduce the permissions of policy-gate-184 to the minimum for model prompts, drop capabilities it does not use and review the grants on a schedule. |
| E-12 | NEW | Elevation of Privilege | — | partner-api-159 | L7 — Agent Ecosystem | A confused-deputy path lets a low-privilege caller ask partner-api-159 to act on audit records using the... | High | Pass the caller's authority through to partner-api-159 and evaluate the original caller's rights, never those of task-agent-158, for every... |
| E-13 | NEW | Elevation of Privilege | — | task-agent-10 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask task-agent-10 to act on policy decisions using the... | High | Pass the caller's authority through to task-agent-10 and evaluate the original caller's rights, never those of audit-vault-9, for every delegated... |
| E-17 | NEW | Elevation of Privilege | — | policy-gate-234 | L6 — Security and Compliance | A confused-deputy path lets a low-privilege caller ask policy-gate-234 to act on partner requests using the... | High | Pass the caller's authority through to policy-gate-234 and evaluate the original caller's rights, never those of user-portal-235, for every... |
| E-19 | NEW | Elevation of Privilege | — | user-portal-255 | L7 — Agent Ecosystem | A privileged maintenance task of user-portal-255 can be triggered through a queue message that any producer... | High | Restrict who can publish maintenance messages that user-portal-255 acts on, sign them and require an authorised approver for destructive operations. |
| E-20 | NEW | Elevation of Privilege | — | task-agent-243 | L3 — Agent Framework | Object identifiers in requests to task-agent-243 are trusted without an ownership check, so a caller can... | High | Check ownership or entitlement for every object reference at task-agent-243 on the server, and deny by default when the check cannot be made. |
| E-22 | NEW | Elevation of Privilege | — | tool-router-254 | L3 — Agent Framework | tool-router-254 runs with broader permissions than its function needs, so a flaw in handling partner... | High | Reduce the permissions of tool-router-254 to the minimum for partner requests, drop capabilities it does not use and review the grants on a schedule. |
| E-25 | NEW | Elevation of Privilege | — | task-agent-6 | L3 — Agent Framework | An administrative interface of task-agent-6 is reachable from the same network as ordinary callers and... | High | Move the administrative interface of task-agent-6 behind a separate listener with strong authentication, network restriction and per-user accounts. |
| E-31 | NEW | Elevation of Privilege | — | partner-api-187 | L7 — Agent Ecosystem | partner-api-187 runs with broader permissions than its function needs, so a flaw in handling trace spans... | High | Reduce the permissions of partner-api-187 to the minimum for trace spans, drop capabilities it does not use and review the grants on a schedule. |
| E-42 | NEW | Elevation of Privilege | — | partner-api-91 | L7 — Agent Ecosystem | Role claims carried in the session token presented to partner-api-91 are honoured without confirmation... | High | Resolve roles for partner-api-91 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| AG-2 | NEW | Agentic | — | runtime-pool-47 | L4 — Deployment Infrastructure | Tool calls made by runtime-pool-47 are not tied to the end user, so the tool server cannot tell whose... | High | Propagate a signed end-user context with each tool call from runtime-pool-47 and make the tool server authorise against it, not against the agent... |
| LLM-2 | NEW | LLM | — | feature-store-53 | L2 — Data Operations | Anyone who can write to the ingestion path of feature-store-53 can slip in documents that contradict... | High | Restrict write access to the ingestion path of feature-store-53, sign documents from authoritative sources and prefer them when answers conflict. |
| S-18 | NEW | Spoofing | — | task-agent-201 | L3 — Agent Framework | An attacker replays a captured service credential against task-agent-201, which does not bind the credential... | Medium | Bind each service credential to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a... |
| T-1 | NEW | Tampering | — | deploy-hub-34 | L4 — Deployment Infrastructure | Serialised objects arriving from policy-gate-35 are deserialised by deploy-hub-34 with permissive type... | Medium | Replace permissive deserialisation in deploy-hub-34 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-9 | NEW | Tampering | — | embed-node-240 | L1 — Foundation Model | Backups and exports of policy decisions on embed-node-240 are writable by operators without a second... | Medium | Protect exports and backups of policy decisions with write-once storage and dual approval for restore, and verify checksums against a separately... |
| T-10 | NEW | Tampering | — | embed-node-146 | L1 — Foundation Model | An attacker who can write to the channel between task-agent-147 and embed-node-146 modifies policy decisions... | Medium | Sign messages between task-agent-147 and embed-node-146 with a per-service key and verify the signature and a monotonic counter before accepting... |
| T-15 | NEW | Tampering | — | vector-index-248 | L2 — Data Operations | An update to vector-index-248 is pulled without provenance checks, so a poisoned package can alter how... | Medium | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of vector-index-248 when a component lacks a... |
| T-22 | NEW | Tampering | — | deploy-hub-162 | L4 — Deployment Infrastructure | Serialised objects arriving from policy-gate-163 are deserialised by deploy-hub-162 with permissive type... | Medium | Replace permissive deserialisation in deploy-hub-162 with a closed schema of allowed types, and reject payloads that name types outside it. |
| T-24 | NEW | Tampering | — | runtime-pool-4 | L4 — Deployment Infrastructure | Backups and exports of audit records on runtime-pool-4 are writable by operators without a second approver... | Medium | Protect exports and backups of audit records with write-once storage and dual approval for restore, and verify checksums against a separately held... |
| T-31 | NEW | Tampering | — | partner-api-236 | L7 — Agent Ecosystem | Configuration of partner-api-236 can be rewritten by any service that holds the shared deployment... | Medium | Keep the configuration of partner-api-236 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-34 | NEW | Tampering | — | vector-index-22 | L2 — Data Operations | A race between concurrent writers lets an attacker overwrite feature vectors on vector-index-22 after... | Medium | Make validation and use atomic: take a version-checked write or compare-and-set on feature vectors, and reject updates whose version no longer... |
| T-35 | NEW | Tampering | — | eval-bench-18 | L5 — Evaluation and Observability | A race between concurrent writers lets an attacker overwrite audit records on eval-bench-18 after validation... | Medium | Make validation and use atomic: take a version-checked write or compare-and-set on audit records, and reject updates whose version no longer matches. |
| T-58 | NEW | Tampering | — | policy-gate-2 | L6 — Security and Compliance | An attacker who can write to the channel between eval-bench-1 and policy-gate-2 modifies audit records in... | Medium | Sign messages between eval-bench-1 and policy-gate-2 with a per-service key and verify the signature and a monotonic counter before accepting any... |
| R-3 | NEW | Repudiation | — | tool-router-175 | L3 — Agent Framework | Actions taken through tool-router-175 are logged without the authenticated principal or a request... | Medium | Log the verified principal, request identifier, source address and outcome for every state change in tool-router-175, and ship the records to the... |
| R-6 | NEW | Repudiation | — | eval-bench-38 | L5 — Evaluation and Observability | Log entries from eval-bench-38 can be edited or deleted by the same operators who administer it, so evidence... | Medium | Write the records of eval-bench-38 to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| R-9 | NEW | Repudiation | — | tool-router-39 | L3 — Agent Framework | Failed and rejected attempts against tool-router-39 are not logged, so probing of partner requests leaves no... | Medium | Log denied and malformed requests to tool-router-39 at a retained severity, aggregate them per source and alert on sustained probing. |
| R-16 | NEW | Repudiation | — | trace-sink-78 | L5 — Evaluation and Observability | Failed and rejected attempts against trace-sink-78 are not logged, so probing of partner requests leaves no... | Medium | Log denied and malformed requests to trace-sink-78 at a retained severity, aggregate them per source and alert on sustained probing. |
| R-18 | NEW | Repudiation | — | policy-gate-173 | L6 — Security and Compliance | Operators approve changes to policy decisions through a chat message or ticket comment that is not bound to... | Medium | Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes. |
| I-2 | NEW | Information Disclosure | — | vector-index-202 | L2 — Data Operations | audit records held by vector-index-202 are readable by any service in the Data Zone that shares the same... | Medium | Grant access to audit records per workload identity with least privilege, enforce it at vector-index-202 and remove network-position trust within... |
| I-3 | NEW | Information Disclosure | — | user-portal-247 | L7 — Agent Ecosystem | Secrets such as the signing key for user-portal-247 appear in process arguments and environment dumps that... | Medium | Pass the signing key to user-portal-247 through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| I-4 | NEW | Information Disclosure | — | tool-router-37 | L3 — Agent Framework | Cross-tenant filters on tool-router-37 are applied in application code only, so one missing predicate... | Medium | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-15 | NEW | Information Disclosure | — | deploy-hub-164 | L4 — Deployment Infrastructure | Verbose error responses from deploy-hub-164 reveal internal paths, query text and identifiers of feature... | Medium | Return generic error codes from deploy-hub-164, log the detail on the server only and strip stack traces and identifiers from every external response. |
| I-20 | NEW | Information Disclosure | — | feature-store-245 | L2 — Data Operations | A timing or size difference in the responses of feature-store-245 lets an observer infer whether specific... | Medium | Equalise response size and timing for existence checks in feature-store-245, and return the same status for present and absent records. |
| I-21 | NEW | Information Disclosure | — | model-host-198 | L1 — Foundation Model | Verbose error responses from model-host-198 reveal internal paths, query text and identifiers of job queue... | Medium | Return generic error codes from model-host-198, log the detail on the server only and strip stack traces and identifiers from every external response. |
| I-23 | NEW | Information Disclosure | — | partner-api-205 | L7 — Agent Ecosystem | A timing or size difference in the responses of partner-api-205 lets an observer infer whether specific... | Medium | Equalise response size and timing for existence checks in partner-api-205, and return the same status for present and absent records. |
| I-26 | NEW | Information Disclosure | — | tool-router-112 | L3 — Agent Framework | A timing or size difference in the responses of tool-router-112 lets an observer infer whether specific... | Medium | Equalise response size and timing for existence checks in tool-router-112, and return the same status for present and absent records. |
| I-30 | NEW | Information Disclosure | — | user-portal-17 | L7 — Agent Ecosystem | Cross-tenant filters on user-portal-17 are applied in application code only, so one missing predicate... | Medium | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-31 | NEW | Information Disclosure | — | task-agent-251 | L3 — Agent Framework | Backups of policy decisions taken from task-agent-251 are stored unencrypted in a shared location that wider... | Medium | Encrypt backups of policy decisions with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-32 | NEW | Information Disclosure | — | model-host-150 | L1 — Foundation Model | Secrets such as the API token for model-host-150 appear in process arguments and environment dumps that... | Medium | Pass the API token to model-host-150 through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| I-36 | NEW | Information Disclosure | — | vector-index-197 | L2 — Data Operations | Data in transit between embed-node-196 and vector-index-197 is protected only on the outer hop, which leaves... | Medium | Keep TLS end to end between embed-node-196 and vector-index-197, disable plaintext listeners and verify the negotiated protocol version in... |
| I-37 | NEW | Information Disclosure | — | vector-index-60 | L2 — Data Operations | Verbose error responses from vector-index-60 reveal internal paths, query text and identifiers of trace... | Medium | Return generic error codes from vector-index-60, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-54 | NEW | Information Disclosure | — | audit-vault-119 | L6 — Security and Compliance | Cross-tenant filters on audit-vault-119 are applied in application code only, so one missing predicate... | Medium | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-55 | NEW | Information Disclosure | — | vector-index-101 | L2 — Data Operations | A timing or size difference in the responses of vector-index-101 lets an observer infer whether specific... | Medium | Equalise response size and timing for existence checks in vector-index-101, and return the same status for present and absent records. |
| I-56 | NEW | Information Disclosure | — | tool-router-58 | L3 — Agent Framework | Verbose error responses from tool-router-58 reveal internal paths, query text and identifiers of model... | Medium | Return generic error codes from tool-router-58, log the detail on the server only and strip stack traces and identifiers from every external response. |
| I-58 | NEW | Information Disclosure | — | embed-node-148 | L1 — Foundation Model | Data in transit between feature-store-149 and embed-node-148 is protected only on the outer hop, which... | Medium | Keep TLS end to end between feature-store-149 and embed-node-148, disable plaintext listeners and verify the negotiated protocol version in... |
| I-60 | NEW | Information Disclosure | — | task-agent-14 | L3 — Agent Framework | Cross-tenant filters on task-agent-14 are applied in application code only, so one missing predicate exposes... | Medium | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-69 | NEW | Information Disclosure | — | deploy-hub-262 | L4 — Deployment Infrastructure | Data in transit between policy-gate-263 and deploy-hub-262 is protected only on the outer hop, which leaves... | Medium | Keep TLS end to end between policy-gate-263 and deploy-hub-262, disable plaintext listeners and verify the negotiated protocol version in... |
| I-82 | NEW | Information Disclosure | — | policy-gate-182 | L6 — Security and Compliance | A timing or size difference in the responses of policy-gate-182 lets an observer infer whether specific... | Medium | Equalise response size and timing for existence checks in policy-gate-182, and return the same status for present and absent records. |
| I-83 | NEW | Information Disclosure | — | task-agent-135 | L3 — Agent Framework | Cross-tenant filters on task-agent-135 are applied in application code only, so one missing predicate... | Medium | Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants. |
| I-85 | NEW | Information Disclosure | — | audit-vault-215 | L6 — Security and Compliance | feature vectors held by audit-vault-215 are readable by any service in the Operations Zone that shares the... | Medium | Grant access to feature vectors per workload identity with least privilege, enforce it at audit-vault-215 and remove network-position trust within... |
| D-5 | NEW | Denial of Service | — | eval-bench-176 | L5 — Evaluation and Observability | A slow-read attack holds connections to eval-bench-176 open and ties up the workers handling trace spans... | Medium | Apply idle and total timeouts on every connection to eval-bench-176, bound workers per client and move slow clients to a separate pool. |
| D-14 | NEW | Denial of Service | — | deploy-hub-264 | L4 — Deployment Infrastructure | Expensive queries over partner requests can be triggered by any authorised caller of deploy-hub-264, so one... | Medium | Enforce cost limits and pagination on queries to deploy-hub-264, run heavy work on a separate pool and cancel queries that exceed the budget. |
| E-2 | NEW | Elevation of Privilege | — | task-agent-179 | L3 — Agent Framework | Role claims carried in the API token presented to task-agent-179 are honoured without confirmation against... | Medium | Resolve roles for task-agent-179 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| E-14 | NEW | Elevation of Privilege | — | audit-vault-186 | L6 — Security and Compliance | A privileged maintenance task of audit-vault-186 can be triggered through a queue message that any producer... | Medium | Restrict who can publish maintenance messages that audit-vault-186 acts on, sign them and require an authorised approver for destructive operations. |
| E-23 | NEW | Elevation of Privilege | — | partner-api-139 | L7 — Agent Ecosystem | Object identifiers in requests to partner-api-139 are trusted without an ownership check, so a caller can... | Medium | Check ownership or entitlement for every object reference at partner-api-139 on the server, and deny by default when the check cannot be made. |
| E-24 | NEW | Elevation of Privilege | — | tool-router-233 | L3 — Agent Framework | Role claims carried in the API token presented to tool-router-233 are honoured without confirmation against... | Medium | Resolve roles for tool-router-233 from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the... |
| E-28 | NEW | Elevation of Privilege | — | task-agent-158 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask task-agent-158 to act on audit records using the... | Medium | Pass the caller's authority through to task-agent-158 and evaluate the original caller's rights, never those of partner-api-159, for every... |
| E-34 | NEW | Elevation of Privilege | — | task-agent-185 | L3 — Agent Framework | A confused-deputy path lets a low-privilege caller ask task-agent-185 to act on model prompts using the... | Medium | Pass the caller's authority through to task-agent-185 and evaluate the original caller's rights, never those of policy-gate-184, for every... |
| E-35 | NEW | Elevation of Privilege | — | partner-api-111 | L7 — Agent Ecosystem | Multi-tenant separation in partner-api-111 depends on a request header that clients can set, allowing one... | Medium | Derive the tenant for partner-api-111 from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI. |
| E-39 | NEW | Elevation of Privilege | — | task-agent-89 | L3 — Agent Framework | Multi-tenant separation in task-agent-89 depends on a request header that clients can set, allowing one... | Medium | Derive the tenant for task-agent-89 from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI. |
| S-1 | NEW | Spoofing | — | task-agent-43 | L3 — Agent Framework | A compromised peer presents a forged service identity to task-agent-43, and task-agent-43 accepts the claim... | Low | Require mutual TLS between embed-node-42 and task-agent-43 and validate the full certificate chain, issuer and audience on every request instead... |
| S-4 | NEW | Spoofing | — | audit-vault-132 | L6 — Security and Compliance | A compromised peer presents a forged service identity to audit-vault-132, and audit-vault-132 accepts the... | Low | Require mutual TLS between task-agent-133 and audit-vault-132 and validate the full certificate chain, issuer and audience on every request... |
| S-5 | NEW | Spoofing | — | tool-router-55 | L3 — Agent Framework | An attacker replays a captured API token against tool-router-55, which does not bind the credential to the... | Low | Bind each API token to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different... |
| S-6 | NEW | Spoofing | — | audit-vault-180 | L6 — Security and Compliance | A compromised peer presents a forged service identity to audit-vault-180, and audit-vault-180 accepts the... | Low | Require mutual TLS between tool-router-181 and audit-vault-180 and validate the full certificate chain, issuer and audience on every request... |
| S-9 | NEW | Spoofing | — | task-agent-97 | L3 — Agent Framework | An unauthenticated callback or health route on task-agent-97 accepts requests that downstream code treats as... | Low | Remove implicit trust in route names: authenticate every route of task-agent-97, including callbacks and health checks, and drop requests that... |
| S-11 | NEW | Spoofing | — | task-agent-105 | L3 — Agent Framework | Session fixation against task-agent-105 lets an attacker pre-seed an identifier and reuse the session after... | Low | Issue a fresh session identifier on every authentication and privilege change, set strict cookie attributes and invalidate any identifier supplied... |
| T-6 | NEW | Tampering | — | partner-api-142 | L7 — Agent Ecosystem | Replay of an earlier valid update to trace spans reaches partner-api-142 because updates carry no nonce or... | Low | Add a nonce and a short expiry to every update accepted by partner-api-142, store seen nonces for the validity window and reject any repeat. |
| T-37 | NEW | Tampering | — | trace-sink-218 | L5 — Evaluation and Observability | Unsanitised trace spans reach trace-sink-218 and are processed as trusted structure, so crafted input... | Low | Validate trace spans against a strict schema at the boundary of trace-sink-218, reject unknown fields and normalise encodings before any... |
| T-51 | NEW | Tampering | — | audit-vault-259 | L6 — Security and Compliance | An update to audit-vault-259 is pulled without provenance checks, so a poisoned package can alter how trace... | Low | Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of audit-vault-259 when a component lacks a... |
| T-56 | NEW | Tampering | — | eval-bench-74 | L5 — Evaluation and Observability | Configuration of eval-bench-74 can be rewritten by any service that holds the shared deployment credential... | Low | Keep the configuration of eval-bench-74 in a versioned, access-controlled repository, require review for changes and alert on drift from the... |
| T-57 | NEW | Tampering | — | vector-index-152 | L2 — Data Operations | A race between concurrent writers lets an attacker overwrite trace spans on vector-index-152 after... | Low | Make validation and use atomic: take a version-checked write or compare-and-set on trace spans, and reject updates whose version no longer matches. |
| T-60 | NEW | Tampering | — | policy-gate-82 | L6 — Security and Compliance | Backups and exports of job queue entries on policy-gate-82 are writable by operators without a second... | Low | Protect exports and backups of job queue entries with write-once storage and dual approval for restore, and verify checksums against a separately... |
| T-65 | NEW | Tampering | — | policy-gate-35 | L6 — Security and Compliance | A race between concurrent writers lets an attacker overwrite job queue entries on policy-gate-35 after... | Low | Make validation and use atomic: take a version-checked write or compare-and-set on job queue entries, and reject updates whose version no longer... |
| R-7 | NEW | Repudiation | — | eval-bench-124 | L5 — Evaluation and Observability | Log entries from eval-bench-124 can be edited or deleted by the same operators who administer it, so... | Low | Write the records of eval-bench-124 to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| R-11 | NEW | Repudiation | — | tool-router-223 | L3 — Agent Framework | Failed and rejected attempts against tool-router-223 are not logged, so probing of audit records leaves no... | Low | Log denied and malformed requests to tool-router-223 at a retained severity, aggregate them per source and alert on sustained probing. |
| R-15 | NEW | Repudiation | — | eval-bench-76 | L5 — Evaluation and Observability | Log entries from eval-bench-76 can be edited or deleted by the same operators who administer it, so evidence... | Low | Write the records of eval-bench-76 to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system. |
| I-11 | NEW | Information Disclosure | — | audit-vault-230 | L6 — Security and Compliance | trace spans held by audit-vault-230 are readable by any service in the Operations Zone that shares the same... | Low | Grant access to trace spans per workload identity with least privilege, enforce it at audit-vault-230 and remove network-position trust within the... |
| I-33 | NEW | Information Disclosure | — | partner-api-157 | L7 — Agent Ecosystem | Secrets such as the signing key for partner-api-157 appear in process arguments and environment dumps that... | Low | Pass the signing key to partner-api-157 through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any... |
| I-35 | NEW | Information Disclosure | — | audit-vault-71 | L6 — Security and Compliance | Backups of feature vectors taken from audit-vault-71 are stored unencrypted in a shared location that wider... | Low | Encrypt backups of feature vectors with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-44 | NEW | Information Disclosure | — | runtime-pool-166 | L4 — Deployment Infrastructure | Backups of audit records taken from runtime-pool-166 are stored unencrypted in a shared location that wider... | Low | Encrypt backups of audit records with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| I-50 | NEW | Information Disclosure | — | tool-router-117 | L3 — Agent Framework | Data in transit between runtime-pool-116 and tool-router-117 is protected only on the outer hop, which... | Low | Keep TLS end to end between runtime-pool-116 and tool-router-117, disable plaintext listeners and verify the negotiated protocol version in... |
| I-70 | NEW | Information Disclosure | — | feature-store-108 | L2 — Data Operations | Data in transit between user-portal-109 and feature-store-108 is protected only on the outer hop, which... | Low | Keep TLS end to end between user-portal-109 and feature-store-108, disable plaintext listeners and verify the negotiated protocol version in... |
| I-71 | NEW | Information Disclosure | — | user-portal-253 | L7 — Agent Ecosystem | A timing or size difference in the responses of user-portal-253 lets an observer infer whether specific... | Low | Equalise response size and timing for existence checks in user-portal-253, and return the same status for present and absent records. |
| I-74 | NEW | Information Disclosure | — | runtime-pool-68 | L4 — Deployment Infrastructure | Logs and traces emitted by runtime-pool-68 include raw trace spans, so anyone with access to the logging... | Low | Redact or tokenise sensitive fields before runtime-pool-68 emits logs and traces, and restrict the logging pipeline to the roles that need it. |
| I-80 | NEW | Information Disclosure | — | vector-index-36 | L2 — Data Operations | Data in transit between tool-router-37 and vector-index-36 is protected only on the outer hop, which leaves... | Low | Keep TLS end to end between tool-router-37 and vector-index-36, disable plaintext listeners and verify the negotiated protocol version in... |
| I-84 | NEW | Information Disclosure | — | runtime-pool-260 | L4 — Deployment Infrastructure | Verbose error responses from runtime-pool-260 reveal internal paths, query text and identifiers of model... | Low | Return generic error codes from runtime-pool-260, log the detail on the server only and strip stack traces and identifiers from every external... |
| I-86 | NEW | Information Disclosure | — | deploy-hub-212 | L4 — Deployment Infrastructure | Backups of trace spans taken from deploy-hub-212 are stored unencrypted in a shared location that wider... | Low | Encrypt backups of trace spans with keys held outside the storage account, restrict the location to the recovery role and audit every read. |
| D-6 | NEW | Denial of Service | — | trace-sink-128 | L5 — Evaluation and Observability | Retry storms from policy-gate-129 multiply the load on trace-sink-128 when it slows down, turning a brief... | Low | Add jittered exponential backoff and a retry budget to policy-gate-129, and enable a circuit breaker so that trace-sink-128 can recover. |
| D-9 | NEW | Denial of Service | — | runtime-pool-216 | L4 — Deployment Infrastructure | Expensive queries over trace spans can be triggered by any authorised caller of runtime-pool-216, so one... | Low | Enforce cost limits and pagination on queries to runtime-pool-216, run heavy work on a separate pool and cancel queries that exceed the budget. |
| D-11 | NEW | Denial of Service | — | deploy-hub-120 | L4 — Deployment Infrastructure | A single oversized or deeply nested payload makes deploy-hub-120 spend disproportionate memory and CPU... | Low | Cap payload size, nesting depth and parse time in deploy-hub-120, and reject requests that exceed the limits before allocation. |
| D-13 | NEW | Denial of Service | — | audit-vault-225 | L6 — Security and Compliance | A burst of requests exhausts the connection pool of audit-vault-225, which queues work without a bound and... | Low | Set explicit concurrency and queue limits on audit-vault-225, shed load with a clear status when saturated and apply per-caller quotas. |
| D-17 | NEW | Denial of Service | — | trace-sink-40 | L5 — Evaluation and Observability | Retry storms from policy-gate-41 multiply the load on trace-sink-40 when it slows down, turning a brief... | Low | Add jittered exponential backoff and a retry budget to policy-gate-41, and enable a circuit breaker so that trace-sink-40 can recover. |
| D-18 | NEW | Denial of Service | — | partner-api-169 | L7 — Agent Ecosystem | Expensive queries over model prompts can be triggered by any authorised caller of partner-api-169, so one... | Low | Enforce cost limits and pagination on queries to partner-api-169, run heavy work on a separate pool and cancel queries that exceed the budget. |
| D-19 | NEW | Denial of Service | — | policy-gate-41 | L6 — Security and Compliance | A burst of requests exhausts the connection pool of policy-gate-41, which queues work without a bound and... | Low | Set explicit concurrency and queue limits on policy-gate-41, shed load with a clear status when saturated and apply per-caller quotas. |
| D-22 | NEW | Denial of Service | — | trace-sink-80 | L5 — Evaluation and Observability | Expensive queries over policy decisions can be triggered by any authorised caller of trace-sink-80, so one... | Low | Enforce cost limits and pagination on queries to trace-sink-80, run heavy work on a separate pool and cancel queries that exceed the budget. |
| E-1 | NEW | Elevation of Privilege | — | tool-router-46 | L3 — Agent Framework | An administrative interface of tool-router-46 is reachable from the same network as ordinary callers and... | Low | Move the administrative interface of tool-router-46 behind a separate listener with strong authentication, network restriction and per-user accounts. |
| E-18 | NEW | Elevation of Privilege | — | tool-router-195 | L3 — Agent Framework | Multi-tenant separation in tool-router-195 depends on a request header that clients can set, allowing one... | Low | Derive the tenant for tool-router-195 from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI. |
| E-26 | NEW | Elevation of Privilege | — | audit-vault-136 | L6 — Security and Compliance | A confused-deputy path lets a low-privilege caller ask audit-vault-136 to act on audit records using the... | Low | Pass the caller's authority through to audit-vault-136 and evaluate the original caller's rights, never those of task-agent-137, for every... |
| E-30 | NEW | Elevation of Privilege | — | tool-router-99 | L3 — Agent Framework | An administrative interface of tool-router-99 is reachable from the same network as ordinary callers and... | Low | Move the administrative interface of tool-router-99 behind a separate listener with strong authentication, network restriction and per-user accounts. |
| E-32 | NEW | Elevation of Privilege | — | tool-router-62 | L3 — Agent Framework | tool-router-62 runs with broader permissions than its function needs, so a flaw in handling trace spans... | Low | Reduce the permissions of tool-router-62 to the minimum for trace spans, drop capabilities it does not use and review the grants on a schedule. |
| E-40 | NEW | Elevation of Privilege | — | task-agent-227 | L3 — Agent Framework | Multi-tenant separation in task-agent-227 depends on a request header that clients can set, allowing one... | Low | Derive the tenant for task-agent-227 from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI. |

---

## 8. Delta Summary

This run has no baseline, so every finding is NEW.

---

## Affected Assets

| Finding ID | Affected Assets |
|------------|-----------------|
| S-2 | [] |
| S-7 | [] |
| S-16 | [] |
| S-19 | [] |
| T-2 | [] |
| T-3 | [] |
| T-4 | [] |
| T-5 | [] |
| T-13 | [] |
| T-16 | [] |
| T-17 | [] |
| T-20 | [] |
| T-21 | [] |
| T-28 | [] |
| T-36 | [] |
| T-38 | [] |
| T-39 | [] |
| T-40 | [] |
| T-41 | [] |
| T-42 | [] |
| T-43 | [] |
| T-45 | [] |
| T-50 | [] |
| T-54 | [] |
| T-55 | [] |
| T-59 | [] |
| T-64 | [] |
| T-67 | [] |
| T-68 | [] |
| R-1 | [] |
| R-2 | [] |
| R-4 | [] |
| R-5 | [] |
| R-10 | [] |
| R-14 | [] |
| I-1 | [] |
| I-8 | [] |
| I-9 | [] |
| I-10 | [] |
| I-12 | [] |
| I-13 | [] |
| I-17 | [] |
| I-19 | [] |
| I-22 | [] |
| I-28 | [] |
| I-29 | [] |
| I-34 | [] |
| I-38 | [] |
| I-41 | [] |
| I-47 | [] |
| I-51 | [] |
| I-57 | [] |
| I-59 | [] |
| I-61 | [] |
| I-63 | [] |
| I-66 | [] |
| I-75 | [] |
| I-79 | [] |
| I-81 | [] |
| D-3 | [] |
| D-4 | [] |
| D-7 | [] |
| D-8 | [] |
| D-10 | [] |
| D-16 | [] |
| D-20 | [] |
| E-3 | [] |
| E-5 | [] |
| E-7 | [] |
| E-9 | [] |
| E-15 | [] |
| E-16 | [] |
| E-21 | [] |
| E-27 | [] |
| E-29 | [] |
| E-33 | [] |
| E-36 | [] |
| E-37 | [] |
| E-38 | [] |
| E-41 | [] |
| AG-1 | [] |
| LLM-1 | [] |
| S-3 | [] |
| S-8 | [] |
| S-10 | [] |
| S-12 | [] |
| S-13 | [] |
| S-14 | [] |
| S-15 | [] |
| S-17 | [] |
| T-7 | [] |
| T-8 | [] |
| T-11 | [] |
| T-12 | [] |
| T-14 | [] |
| T-18 | [] |
| T-19 | [] |
| T-23 | [] |
| T-25 | [] |
| T-26 | [] |
| T-27 | [] |
| T-29 | [] |
| T-30 | [] |
| T-32 | [] |
| T-33 | [] |
| T-44 | [] |
| T-46 | [] |
| T-47 | [] |
| T-48 | [] |
| T-49 | [] |
| T-52 | [] |
| T-53 | [] |
| T-61 | [] |
| T-62 | [] |
| T-63 | [] |
| T-66 | [] |
| T-69 | [] |
| R-8 | [] |
| R-12 | [] |
| R-13 | [] |
| R-17 | [] |
| I-5 | [] |
| I-6 | [] |
| I-7 | [] |
| I-14 | [] |
| I-16 | [] |
| I-18 | [] |
| I-24 | [] |
| I-25 | [] |
| I-27 | [] |
| I-39 | [] |
| I-40 | [] |
| I-42 | [] |
| I-43 | [] |
| I-45 | [] |
| I-46 | [] |
| I-48 | [] |
| I-49 | [] |
| I-52 | [] |
| I-53 | [] |
| I-62 | [] |
| I-64 | [] |
| I-65 | [] |
| I-67 | [] |
| I-68 | [] |
| I-72 | [] |
| I-73 | [] |
| I-76 | [] |
| I-77 | [] |
| I-78 | [] |
| I-87 | [] |
| I-88 | [] |
| D-1 | [] |
| D-2 | [] |
| D-12 | [] |
| D-15 | [] |
| D-21 | [] |
| E-4 | [] |
| E-6 | [] |
| E-8 | [] |
| E-10 | [] |
| E-11 | [] |
| E-12 | [] |
| E-13 | [] |
| E-17 | [] |
| E-19 | [] |
| E-20 | [] |
| E-22 | [] |
| E-25 | [] |
| E-31 | [] |
| E-42 | [] |
| AG-2 | [] |
| LLM-2 | [] |
| S-18 | [] |
| T-1 | [] |
| T-9 | [] |
| T-10 | [] |
| T-15 | [] |
| T-22 | [] |
| T-24 | [] |
| T-31 | [] |
| T-34 | [] |
| T-35 | [] |
| T-58 | [] |
| R-3 | [] |
| R-6 | [] |
| R-9 | [] |
| R-16 | [] |
| R-18 | [] |
| I-2 | [] |
| I-3 | [] |
| I-4 | [] |
| I-15 | [] |
| I-20 | [] |
| I-21 | [] |
| I-23 | [] |
| I-26 | [] |
| I-30 | [] |
| I-31 | [] |
| I-32 | [] |
| I-36 | [] |
| I-37 | [] |
| I-54 | [] |
| I-55 | [] |
| I-56 | [] |
| I-58 | [] |
| I-60 | [] |
| I-69 | [] |
| I-82 | [] |
| I-83 | [] |
| I-85 | [] |
| D-5 | [] |
| D-14 | [] |
| E-2 | [] |
| E-14 | [] |
| E-23 | [] |
| E-24 | [] |
| E-28 | [] |
| E-34 | [] |
| E-35 | [] |
| E-39 | [] |
| S-1 | [] |
| S-4 | [] |
| S-5 | [] |
| S-6 | [] |
| S-9 | [] |
| S-11 | [] |
| T-6 | [] |
| T-37 | [] |
| T-51 | [] |
| T-56 | [] |
| T-57 | [] |
| T-60 | [] |
| T-65 | [] |
| R-7 | [] |
| R-11 | [] |
| R-15 | [] |
| I-11 | [] |
| I-33 | [] |
| I-35 | [] |
| I-44 | [] |
| I-50 | [] |
| I-70 | [] |
| I-71 | [] |
| I-74 | [] |
| I-80 | [] |
| I-84 | [] |
| I-86 | [] |
| D-6 | [] |
| D-9 | [] |
| D-11 | [] |
| D-13 | [] |
| D-17 | [] |
| D-18 | [] |
| D-19 | [] |
| D-22 | [] |
| E-1 | [] |
| E-18 | [] |
| E-26 | [] |
| E-30 | [] |
| E-32 | [] |
| E-40 | [] |
