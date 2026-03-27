---
schema_version: "1.1"
date: "2026-03-25"
input_format: "mermaid"
classification: "confidential"
---

# Threat Model: Agentic AI Application

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| User | External Entity | End user who submits prompts and queries to the system via HTTPS |
| Guardrails Service | Process | Input validation and filtering service that screens user prompts before forwarding to the orchestrator, rejects non-compliant prompts with reasons |
| LLM Agent Orchestrator | Process | Central agentic AI coordination service that processes validated prompts, retrieves context from the Knowledge Base, dispatches tool calls to the MCP Tool Server, generates responses, and logs decisions |
| MCP Tool Server | Process | Model Context Protocol tool execution server that receives JSON-RPC tool call requests from the orchestrator, invokes external APIs, and returns results |
| Knowledge Base | Data Store | Vector search data store used by the orchestrator for context retrieval via semantic similarity search |
| Audit Logger | Data Store | Centralized logging data store that records decision log entries from the orchestrator, tool execution logs from the MCP Tool Server, and filtering event logs from the Guardrails Service |
| External API | External Entity | Third-party external API service consumed by the MCP Tool Server over HTTPS |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| User | Guardrails Service | Prompt / Query | HTTPS |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | Not specified |
| Guardrails Service | User | Rejected Prompt + Reason | HTTPS |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval query | Vector Search |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | Vector Search |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | JSON-RPC |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | JSON-RPC |
| MCP Tool Server | External API | API Request | HTTPS |
| External API | MCP Tool Server | API Response | HTTPS |
| LLM Agent Orchestrator | User | Response | HTTPS |
| LLM Agent Orchestrator | Audit Logger | Decision Log Entry | Not specified |
| MCP Tool Server | Audit Logger | Tool Execution Log | Not specified |
| Guardrails Service | Audit Logger | Filtering Event Log | Not specified |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Protocol | HTTPS | Not specified |
| Protocol | JSON-RPC | Not specified |
| Search | Vector Search | Not specified |
| AI Framework | LLM (Language Model) | Not specified |
| Integration | Model Context Protocol (MCP) | Not specified |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| User Zone | Untrusted | User |
| Application Zone | Semi-Trusted | Guardrails Service, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger |
| External Services | Untrusted | External API |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| User to Application | User Zone | Application Zone | User, Guardrails Service | Guardrails Service input validation and filtering |
| Application to External | Application Zone | External Services | MCP Tool Server, External API | HTTPS transport encryption |
| Application to User | Application Zone | User Zone | LLM Agent Orchestrator, User | HTTPS transport encryption |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | User | Attacker impersonates a legitimate user by replaying or forging authentication credentials when submitting prompts to the Guardrails Service, because user identity verification relies solely on bearer tokens without binding to client context such as device fingerprint or IP address | MEDIUM | HIGH | High | Implement token binding using DPoP (Demonstration of Proof-of-Possession) or certificate-bound access tokens; enforce session binding to client fingerprint (IP range, user-agent, TLS session); require MFA for sensitive operations; set short token lifetimes (15 minutes) with rotation |
| S-2 | Guardrails Service | Attacker bypasses the Guardrails Service by directly accessing the LLM Agent Orchestrator endpoint, impersonating the Guardrails Service identity, because inter-service authentication between the Guardrails Service and Orchestrator is not enforced | MEDIUM | HIGH | High | Enforce mutual TLS (mTLS) between Guardrails Service and LLM Agent Orchestrator; validate service identity claims using signed JWTs with audience restriction; reject requests to the Orchestrator that do not originate from an authenticated Guardrails Service instance |
| S-3 | LLM Agent Orchestrator | Attacker forges tool call requests to the MCP Tool Server by impersonating the LLM Agent Orchestrator, because the JSON-RPC channel between orchestrator and tool server lacks mutual authentication | HIGH | HIGH | Critical | Implement mutual TLS (mTLS) with certificate pinning between the LLM Agent Orchestrator and MCP Tool Server; sign all JSON-RPC requests with a per-session HMAC key; validate caller identity on every tool call before dispatch |
| S-4 | MCP Tool Server | Attacker redirects the MCP Tool Server's outbound API requests to an attacker-controlled endpoint by spoofing DNS responses or compromising the External API's TLS certificate, because certificate pinning is not enforced on outbound HTTPS connections | MEDIUM | HIGH | High | Implement TLS certificate pinning for all outbound connections to the External API; validate DNS responses using DNSSEC; configure strict certificate chain verification; monitor for unexpected certificate changes on external endpoints |

### 3.2 Tampering (T)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Guardrails Service | Attacker modifies the validation rules or filtering configuration of the Guardrails Service at runtime, because configuration files are stored in a location writable by the application process without integrity verification | MEDIUM | HIGH | High | Store Guardrails validation rules in an immutable configuration store with cryptographic integrity verification (SHA-256 checksums); enforce read-only filesystem mounts for configuration; implement change detection alerts on rule modifications; require signed configuration updates through a separate deployment pipeline |
| T-2 | LLM Agent Orchestrator | Attacker injects malicious content into the prompt context by tampering with the data flow between the Guardrails Service and the Orchestrator, because the validated prompt is not integrity-protected in transit between services | MEDIUM | HIGH | High | Sign validated prompts with an HMAC before forwarding from Guardrails Service to Orchestrator; verify signature on receipt; reject prompts with invalid or missing signatures; encrypt the inter-service channel with TLS to prevent network-level tampering |
| T-3 | MCP Tool Server | Attacker manipulates JSON-RPC tool call parameters in transit between the Orchestrator and MCP Tool Server, injecting malicious payloads such as SQL fragments or shell commands into tool arguments, because parameter integrity is not verified at the tool server boundary | HIGH | HIGH | Critical | Implement strict JSON schema validation on all incoming tool call parameters at the MCP Tool Server; enforce parameterized queries and command sanitization; sign JSON-RPC payloads with HMAC at the Orchestrator and verify at the Tool Server; reject malformed or unsigned requests |
| T-4 | Knowledge Base | Attacker injects malicious or misleading content into the Knowledge Base by exploiting write access through the orchestrator's data ingestion path, because input sanitization is not enforced before persisting data to the vector store | MEDIUM | HIGH | High | Implement content validation and sanitization on all write operations to the Knowledge Base; enforce allowlist-based content filtering; apply integrity checksums (SHA-256) on stored records; restrict write access to an authorized ingestion pipeline with audit logging; implement versioned snapshots for rollback capability |
| T-5 | Audit Logger | Attacker modifies or deletes audit log entries to cover tracks after a security incident, because the Audit Logger stores logs in a location writable by application processes that also generate the logs | MEDIUM | HIGH | High | Deploy the Audit Logger as an append-only, immutable log store (e.g., write-once S3 bucket or blockchain-anchored log); separate write permissions from read/admin permissions; forward logs to an external SIEM within 60 seconds; implement cryptographic chaining (hash chain) to detect tampering; restrict direct database access to the log store |

### 3.3 Repudiation (R)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | User | User denies having submitted a specific prompt that triggered a harmful or policy-violating response, because the system does not capture non-repudiable evidence linking the authenticated user identity to the specific prompt submission | MEDIUM | MEDIUM | Medium | Implement non-repudiation controls: capture authenticated user ID, session ID, client IP, timestamp (UTC, sub-second precision), and cryptographic hash of the submitted prompt in an immutable audit record; require user acknowledgment for sensitive operations; retain audit records for the compliance-required retention period |
| R-2 | Guardrails Service | Guardrails Service fails to log rejected prompts with sufficient detail to reconstruct why a prompt was blocked, enabling disputes about whether legitimate prompts were incorrectly filtered, because filtering event logs lack the original prompt content, matched rule identifier, and confidence score | MEDIUM | MEDIUM | Medium | Instrument the Guardrails Service to emit structured audit events for every filtering decision: include request correlation ID, authenticated user ID, original prompt hash, matched filter rule ID, confidence score, action taken (allow/reject), and UTC timestamp; forward events to the append-only Audit Logger |
| R-3 | LLM Agent Orchestrator | LLM Agent Orchestrator executes tool calls and generates responses without logging the full decision chain, enabling operators or users to deny that specific actions were requested or authorized, because decision logs lack the originating user context, selected tool, parameters, and model reasoning trace | MEDIUM | HIGH | High | Instrument the Orchestrator to emit structured decision audit events: record authenticated user ID, session ID, input prompt hash, model reasoning trace (chain-of-thought summary), each tool call (tool name, parameters, response summary), final response hash, and UTC timestamp; forward to append-only Audit Logger within 60 seconds |
| R-4 | MCP Tool Server | MCP Tool Server executes tool operations including external API calls without recording the requesting orchestrator context, making it impossible to attribute tool executions to specific user requests in forensic investigations | MEDIUM | MEDIUM | Medium | Log every tool execution with: requesting orchestrator session ID, originating user ID (propagated from orchestrator), tool name, input parameters, execution duration, response status, External API endpoint called, and UTC timestamp; correlate with orchestrator decision logs via shared request correlation ID |
| R-5 | External API | External API interactions lack correlation identifiers that link API calls back to the originating user request, creating accountability gaps when external service calls produce unexpected or harmful results | LOW | MEDIUM | Low | Include a unique request correlation ID in all External API calls (via HTTP header); log the correlation ID alongside the originating user request ID in both the MCP Tool Server and Audit Logger; implement request-response logging for all external API interactions |

### 3.4 Information Disclosure (I)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | Guardrails Service | Guardrails Service returns detailed rejection reasons to the user that reveal internal filtering rules, regex patterns, or blocked keyword lists, enabling attackers to craft prompts that evade detection by understanding the filtering logic | HIGH | MEDIUM | High | Return generic rejection messages to users (e.g., "Your request could not be processed") without exposing filter rule details; log detailed rejection reasons only to the internal Audit Logger; implement separate user-facing and internal-facing error response schemas |
| I-2 | LLM Agent Orchestrator | LLM Agent Orchestrator leaks sensitive internal state through verbose error messages when tool calls fail or context retrieval errors occur, exposing internal service topology, Knowledge Base schema details, or model configuration parameters | MEDIUM | HIGH | High | Implement standardized error responses that strip internal details; return generic error codes to users (e.g., "Service temporarily unavailable"); route detailed error information to internal monitoring only; audit all response schemas for unintended metadata disclosure |
| I-3 | MCP Tool Server | MCP Tool Server forwards raw External API error responses to the Orchestrator without sanitization, potentially exposing third-party API keys, internal endpoint URLs, or authentication headers embedded in error payloads | MEDIUM | HIGH | High | Sanitize all External API responses before returning to the Orchestrator; strip authentication headers, internal URLs, and API keys from error payloads; implement an error response allowlist that passes only expected fields; log raw responses internally for debugging |
| I-4 | Knowledge Base | Knowledge Base returns full document contents including internal metadata, embedding vectors, and storage schema details in query responses, because field-level projection is not enforced on retrieval queries | HIGH | MEDIUM | High | Implement field-level projection on Knowledge Base query responses to return only content fields required by the Orchestrator; strip internal metadata, embedding vectors, document IDs, and storage schema details; enforce query-scoped access controls matching the requesting user's authorization level |
| I-5 | Audit Logger | Audit log entries contain sensitive data including full prompt content, user PII, and API credentials that were logged for debugging purposes, and the log store is accessible to operations staff beyond the security team | MEDIUM | HIGH | High | Implement log data classification: separate sensitive fields (prompt content, PII, credentials) into a restricted log tier with strict access controls; apply PII masking or tokenization before writing to the general log store; enforce role-based access to audit logs (security team only for sensitive tier); implement log retention policies with automatic purging of sensitive data |

### 3.5 Denial of Service (D)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | Guardrails Service | Attacker floods the Guardrails Service with high-volume prompt submissions designed to exhaust CPU on complex regex-based content filtering rules, because no rate limiting or request size caps are enforced at the entry point | HIGH | HIGH | Critical | Enforce per-client rate limiting (e.g., 30 requests/minute) at the API gateway layer before the Guardrails Service; cap prompt input size at 4096 characters; implement request timeout at 10 seconds; use compiled regex with ReDoS-safe patterns; deploy auto-scaling with circuit breaker after sustained high load |
| D-2 | LLM Agent Orchestrator | Attacker sends concurrent requests with maximum-length prompts to the Orchestrator, exhausting LLM inference compute budget and memory, blocking legitimate requests, because no per-client rate limit or token budget cap is enforced | HIGH | HIGH | Critical | Enforce per-client rate limiting of 10 requests/minute on the Orchestrator endpoint; cap prompt input at 4096 tokens; configure request timeout at 30 seconds with circuit breaker after 5 consecutive failures; set memory limit at 1GB per worker with OOM-kill restart policy; implement priority queuing for authenticated users |
| D-3 | MCP Tool Server | Attacker triggers resource exhaustion on the MCP Tool Server by causing the Orchestrator to issue a large number of concurrent tool calls, because no per-request tool call limit or concurrency cap is enforced on the tool execution path | MEDIUM | HIGH | High | Enforce a maximum of 5 concurrent tool calls per user request; implement per-tool rate limiting; configure tool execution timeout at 15 seconds; deploy circuit breaker for external API calls with exponential backoff; set memory and CPU limits per tool execution container |
| D-4 | Knowledge Base | Attacker exhausts Knowledge Base resources by triggering unbounded vector search queries with high-dimensional adversarial inputs designed to maximize computational cost, because search queries lack result limits and complexity bounds | MEDIUM | MEDIUM | Medium | Enforce maximum result count (top-k limit of 10) on all Knowledge Base queries; cap query vector dimensions; implement query timeout at 5 seconds; deploy connection pool limits; monitor query patterns for anomalous complexity spikes |
| D-5 | Audit Logger | Attacker causes audit log storage exhaustion by triggering high-volume logging events through rapid request submission, eventually filling disk and disrupting all services that depend on log writing, because no log volume throttling or storage quota is enforced | MEDIUM | MEDIUM | Medium | Implement log volume throttling with per-source rate limits; set storage quotas with automatic rotation; deploy log sampling for high-volume event sources during load spikes; monitor disk usage with alerts at 80% capacity; use external log shipping to scalable storage (S3, cloud logging service) |

### 3.6 Elevation of Privilege (E)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | Guardrails Service | Attacker bypasses the Guardrails Service entirely by exploiting an alternate route to the LLM Agent Orchestrator (e.g., internal network access, API gateway misconfiguration), because authorization checks are only enforced at the Guardrails Service layer and not replicated at the Orchestrator | MEDIUM | HIGH | High | Implement defense-in-depth: enforce authorization checks at both the Guardrails Service and the Orchestrator; configure network policies to restrict Orchestrator access to only the Guardrails Service; deploy API gateway rules that block direct access to internal service endpoints; validate origin service identity on every request |
| E-2 | LLM Agent Orchestrator | Attacker escalates from a standard user role to administrative capabilities by manipulating the orchestrator's tool selection logic through prompt injection, causing it to invoke privileged tool endpoints that should be restricted to administrator roles, because the Orchestrator does not enforce role-based access control on tool dispatch | HIGH | HIGH | Critical | Implement RBAC policy on tool dispatch: map each tool to a required permission set; validate the authenticated user's role against the tool permission manifest before dispatch; reject unauthorized tool invocations with 403 and log the attempt; enforce least privilege — standard users receive a restricted tool allowlist |
| E-3 | MCP Tool Server | Authenticated user invokes administrative tool endpoints on the MCP Tool Server by manipulating the tool_name parameter, because the server does not enforce role-based access control on tool dispatch, allowing standard users to execute privileged operations such as configuration changes and data exports | HIGH | HIGH | Critical | Implement RBAC policy on the MCP Tool Server that maps each tool endpoint to a required permission set; validate caller role against the tool permission manifest before dispatch; reject unauthorized tool invocations with 403 and log the attempt with caller identity and requested tool; enforce tool-level allowlists per agent role |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| AG-1 | LLM Agent Orchestrator | LLM Agent Orchestrator executes consequential actions (external API calls via MCP Tool Server, Knowledge Base writes) without human approval gates, because no risk-tier classification distinguishes reversible read operations from irreversible write/delete/send operations, violating the principle that high-stakes agent actions require human-in-the-loop review | HIGH | HIGH | Critical | Classify all orchestrator-accessible operations into risk tiers: Tier 1 (read-only, auto-approve), Tier 2 (reversible writes, require confirmation), Tier 3 (irreversible external actions, require human approval with mandatory wait period); implement pre-execution review for Tier 2+ actions; log all tier classifications and approval decisions |
| AG-2 | LLM Agent Orchestrator | LLM Agent Orchestrator operates in an unbounded reasoning loop where the LLM decides when to terminate based on its assessment of task completion, but no maximum iteration count, execution timeout, or cost cap constrains the loop, enabling an attacker to submit ambiguous prompts that cause indefinite resource consumption | HIGH | MEDIUM | High | Implement mandatory termination constraints: maximum iteration count (25 iterations), execution timeout (5 minutes), and cumulative cost cap ($10 per request); add a circuit breaker that halts execution if the agent repeats the same action pattern for 3 consecutive iterations; log each iteration with action taken and reasoning for post-hoc analysis |
| AG-3 | MCP Tool Server | MCP Tool Server exposes all registered tools to every connected client (the LLM Agent Orchestrator) without per-agent capability scoping, violating the principle that agents should only access tools within their authorized capability set, because the tool registry does not enforce allowlists | HIGH | HIGH | Critical | Implement per-agent tool allowlists at the MCP Tool Server; each agent connection must declare its required capabilities and the server enforces that only declared tools are invocable; implement dynamic capability scoping based on the originating user's role; log all tool invocations with agent identity for audit |
| AG-4 | MCP Tool Server | Attacker manipulates the MCP Tool Server to chain individually authorized tool calls (e.g., database-query + file-export + network-send) to achieve data exfiltration that no single tool authorization would permit, because no cross-tool policy evaluates composite effects of sequential tool invocations | MEDIUM | HIGH | High | Implement a tool chain policy engine that evaluates composite effects of sequential tool calls; define forbidden tool combinations (e.g., data-read + network-send); require human approval for chains that cross trust boundaries; enforce maximum chain depth of 3 tool calls per request; log complete tool chains for post-hoc analysis |

### 4.2 LLM Threats (LLM)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | LLM Agent Orchestrator | Attacker submits adversarial prompts through the Guardrails Service that override the Orchestrator's system prompt, causing it to ignore safety constraints, disclose internal instructions, or produce harmful content, because user input is concatenated into the LLM prompt without structured boundary enforcement between system instructions and user content | HIGH | HIGH | Critical | Implement structured prompt templates with explicit delimiter tokens between system instructions and user input; deploy an input classifier that detects adversarial prompt patterns before forwarding to the model; apply output filtering to detect responses that violate expected behavior boundaries; implement canary tokens in system prompts to detect extraction attempts |
| LLM-2 | LLM Agent Orchestrator | Attacker exploits the RAG pipeline by injecting adversarial content into the Knowledge Base that, when retrieved by the Orchestrator during context retrieval, overrides system behavior — causing the model to exfiltrate data from other retrieved documents or generate misleading responses (indirect prompt injection) | MEDIUM | HIGH | High | Sanitize retrieved document content before injection into the prompt context; implement provenance tracking so the model can distinguish system instructions from retrieved content; apply content integrity checks on documents before indexing; monitor retrieval patterns for anomalous document frequency spikes |
| LLM-3 | LLM Agent Orchestrator | Attacker systematically queries the Orchestrator's inference endpoint to extract a functional copy of the model through distillation, because the API returns rich response data without per-user query volume limits or query pattern monitoring | LOW | HIGH | Medium | Restrict API output to top-k predictions only; implement per-API-key query budgets with alerts at threshold crossings; deploy query pattern analysis that detects systematic probing (uniform input distributions, grid sampling patterns); add watermarking to model outputs to enable downstream detection of extracted copies |

---

## 4a. Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-4, LLM-2 | LLM Agent Orchestrator, Knowledge Base | Tampering: Attacker injects malicious content into the Knowledge Base via the orchestrator's data ingestion path; LLM: Adversarial content in Knowledge Base overrides system behavior during RAG retrieval (indirect prompt injection). Shared basis: Data integrity compromise in the Knowledge Base enables both persistent data corruption and runtime prompt manipulation. | High |
| CG-2 | E-2, AG-1 | LLM Agent Orchestrator | Privilege-Escalation: Attacker escalates to administrative tool access through prompt injection manipulating tool selection; Agent-Autonomy: Orchestrator executes consequential actions without human approval gates. Shared basis: Excessive permissions combined with missing human oversight enable unauthorized high-privilege operations. | Critical |
| CG-3 | R-3, AG-2 | LLM Agent Orchestrator | Repudiation: Orchestrator executes tool calls without logging the full decision chain; Agent-Autonomy: Orchestrator operates in unbounded reasoning loops without termination constraints. Shared basis: Missing accountability controls (logging) combined with unconstrained autonomous operation create unauditable agent behavior. | High |
| CG-4 | D-3, AG-4 | MCP Tool Server | Denial-of-Service: Resource exhaustion through concurrent tool calls without concurrency caps; Tool-Abuse: Capability escalation through chaining individually authorized tool calls. Shared basis: Uncontrolled tool invocation enables both resource exhaustion and permission escalation through tool composition. | High |

---

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| User | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Guardrails Service | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| LLM Agent Orchestrator | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 3 | 11 |
| MCP Tool Server | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| Knowledge Base | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Audit Logger | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| External API | n/a | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 1 |
| **Total** | **4** | **5** | **5** | **5** | **5** | **3** | **4** | **3** | **34** |

Counts reflect deduplicated findings. 4 correlation groups merged 8 individual findings.

---

## 6. Risk Summary

### Risk Calibration Matrix

The following OWASP 3x3 risk matrix documents how risk levels are computed for every finding in this threat model. Impact (rows) and Likelihood (columns) determine the Risk Level at each intersection. All agents use this same matrix, ensuring consistent risk ratings across STRIDE and AI threat categories.

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

Risk summary counts below reflect deduplicated findings. When correlation groups exist, correlated findings count as one unique threat per group rather than individually.

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 8 | 26.7% |
| High | 14 | 46.7% |
| Medium | 6 | 20.0% |
| Low | 1 | 3.3% |
| Note | 0 | 0.0% |
| **Total** | **30 (34 raw)** | **100%** |

---

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-3 | LLM Agent Orchestrator | Attacker forges tool call requests to the MCP Tool Server by impersonating the LLM Agent Orchestrator | Critical | Implement mutual TLS (mTLS) with certificate pinning between the LLM Agent Orchestrator and MCP Tool Server; sign all JSON-RPC requests with a per-session HMAC key; validate caller identity on every tool call before dispatch |
| T-3 | MCP Tool Server | Attacker manipulates JSON-RPC tool call parameters in transit, injecting malicious payloads | Critical | Implement strict JSON schema validation on all incoming tool call parameters at the MCP Tool Server; enforce parameterized queries and command sanitization; sign JSON-RPC payloads with HMAC and verify; reject malformed or unsigned requests |
| D-1 | Guardrails Service | Attacker floods the Guardrails Service to exhaust CPU on regex-based filtering | Critical | Enforce per-client rate limiting at the API gateway layer; cap prompt input size at 4096 characters; implement request timeout at 10 seconds; use compiled regex with ReDoS-safe patterns; deploy auto-scaling with circuit breaker |
| D-2 | LLM Agent Orchestrator | Attacker sends concurrent maximum-length prompts to exhaust LLM inference compute | Critical | Enforce per-client rate limiting of 10 requests/minute; cap prompt input at 4096 tokens; configure request timeout at 30 seconds with circuit breaker; set memory limit at 1GB per worker with OOM-kill restart policy |
| E-2 | LLM Agent Orchestrator | Attacker escalates to administrative tool access through prompt injection manipulating tool selection | Critical | Implement RBAC policy on tool dispatch; map each tool to a required permission set; validate user role against tool permission manifest; reject unauthorized invocations with 403; enforce least privilege tool allowlists |
| E-3 | MCP Tool Server | User invokes administrative tool endpoints by manipulating tool_name parameter | Critical | Implement RBAC policy mapping each tool endpoint to required permissions; validate caller role before dispatch; reject unauthorized invocations with 403 and log; enforce tool-level allowlists per agent role |
| AG-1 | LLM Agent Orchestrator | Orchestrator executes consequential actions without human approval gates | Critical | Classify operations into risk tiers; require human approval for irreversible external actions; implement pre-execution review for Tier 2+ actions; log all tier classifications and approval decisions |
| AG-3 | MCP Tool Server | MCP Tool Server exposes all tools to every client without capability scoping | Critical | Implement per-agent tool allowlists; enforce capability scoping based on originating user role; log all tool invocations with agent identity |
| LLM-1 | LLM Agent Orchestrator | Adversarial prompts override system prompt, bypassing safety constraints | Critical | Implement structured prompt templates with delimiter tokens; deploy input classifier for adversarial patterns; apply output filtering; implement canary tokens in system prompts |
| S-1 | User | Attacker impersonates legitimate user by replaying or forging authentication credentials | High | Implement token binding using DPoP; enforce session binding to client fingerprint; require MFA for sensitive operations; set short token lifetimes with rotation |
| S-2 | Guardrails Service | Attacker bypasses Guardrails by directly accessing Orchestrator, impersonating Guardrails identity | High | Enforce mutual TLS between Guardrails Service and Orchestrator; validate service identity with signed JWTs; reject unauthenticated requests |
| S-4 | MCP Tool Server | Attacker redirects outbound API requests by spoofing DNS or compromising TLS certificates | High | Implement TLS certificate pinning for outbound connections; validate DNS with DNSSEC; configure strict certificate chain verification |
| T-1 | Guardrails Service | Attacker modifies validation rules at runtime without integrity verification | High | Store rules in immutable configuration store with SHA-256 checksums; enforce read-only mounts; implement change detection alerts; require signed updates |
| T-2 | LLM Agent Orchestrator | Attacker injects malicious content by tampering with data flow between Guardrails and Orchestrator | High | Sign validated prompts with HMAC; verify signature on receipt; encrypt inter-service channel with TLS |
| T-4 | Knowledge Base | Attacker injects malicious content into Knowledge Base via orchestrator's ingestion path | High | Implement content validation and sanitization; enforce allowlist-based filtering; apply integrity checksums; restrict write access; implement versioned snapshots |
| T-5 | Audit Logger | Attacker modifies or deletes audit log entries to cover tracks | High | Deploy append-only immutable log store; separate write from admin permissions; forward logs to external SIEM; implement cryptographic chaining |
| R-3 | LLM Agent Orchestrator | Orchestrator executes tool calls without logging full decision chain | High | Emit structured decision audit events with user ID, tool calls, reasoning trace, and timestamps; forward to append-only Audit Logger |
| I-1 | Guardrails Service | Rejection reasons reveal internal filtering rules to attackers | High | Return generic rejection messages; log detailed reasons only to internal Audit Logger; implement separate error response schemas |
| I-2 | LLM Agent Orchestrator | Verbose error messages leak internal service topology and model configuration | High | Implement standardized error responses; return generic error codes; route detailed errors to internal monitoring only |
| I-3 | MCP Tool Server | Raw External API error responses forwarded without sanitization, exposing API keys | High | Sanitize all External API responses; strip authentication headers and internal URLs; implement error response allowlist |
| I-4 | Knowledge Base | Query responses include internal metadata, embedding vectors, and storage schema | High | Implement field-level projection; strip internal metadata and embedding vectors; enforce query-scoped access controls |
| I-5 | Audit Logger | Audit logs contain sensitive data accessible beyond the security team | High | Implement log data classification with restricted tiers; apply PII masking; enforce role-based access; implement retention policies |
| D-3 | MCP Tool Server | Resource exhaustion through concurrent tool calls without concurrency cap | High | Enforce maximum 5 concurrent tool calls per request; implement per-tool rate limiting; configure tool execution timeout; deploy circuit breaker |
| E-1 | Guardrails Service | Attacker bypasses Guardrails via alternate route to Orchestrator | High | Implement defense-in-depth; enforce authorization at both Guardrails and Orchestrator; configure network policies; validate origin service identity |
| AG-2 | LLM Agent Orchestrator | Orchestrator operates in unbounded reasoning loop without termination constraints | High | Implement termination constraints: max 25 iterations, 5-minute timeout, $10 cost cap; add circuit breaker for repeated action patterns |
| AG-4 | MCP Tool Server | Tool call chaining enables capability escalation beyond individual permissions | High | Implement tool chain policy engine; define forbidden tool combinations; require human approval for cross-boundary chains; enforce max chain depth of 3 |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via adversarial content in Knowledge Base during RAG retrieval | High | Sanitize retrieved content before prompt injection; implement provenance tracking; apply content integrity checks; monitor retrieval patterns |
| R-1 | User | User denies having submitted a specific prompt without non-repudiable evidence | Medium | Capture user ID, session ID, client IP, timestamp, and prompt hash in immutable audit record; require acknowledgment for sensitive operations |
| R-2 | Guardrails Service | Insufficient detail in filtering event logs prevents reconstruction of rejection decisions | Medium | Emit structured audit events with correlation ID, user ID, prompt hash, rule ID, confidence score, action, and timestamp |
| R-4 | MCP Tool Server | Tool executions lack requesting orchestrator context for forensic attribution | Medium | Log tool executions with orchestrator session ID, user ID, tool name, parameters, duration, and response status; correlate via request ID |
| D-4 | Knowledge Base | Unbounded vector search queries with adversarial inputs exhaust resources | Medium | Enforce top-k limit of 10; cap query dimensions; implement 5-second timeout; deploy connection pool limits |
| D-5 | Audit Logger | High-volume logging events cause storage exhaustion | Medium | Implement log volume throttling; set storage quotas with rotation; deploy log sampling during load spikes; monitor disk usage |
| LLM-3 | LLM Agent Orchestrator | Systematic querying enables model extraction through distillation | Medium | Restrict API output to top-k predictions; implement per-key query budgets; deploy query pattern analysis; add output watermarking |
| R-5 | External API | External API interactions lack correlation identifiers for accountability | Low | Include request correlation ID in all External API calls; log alongside originating user request ID |
