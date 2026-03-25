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
| User | External Entity | End user submitting prompts and queries to the agentic AI system via HTTPS |
| Guardrails Service | Process | Input validation and filtering service that screens user prompts before forwarding to the orchestrator, rejects disallowed prompts with reason |
| LLM Agent Orchestrator | Process | Central agentic process that coordinates LLM inference, context retrieval from the Knowledge Base, and tool execution via the MCP Tool Server |
| MCP Tool Server | Process | Model Context Protocol tool server that executes tool calls requested by the orchestrator and interfaces with external APIs |
| Knowledge Base | Data Store | Vector database storing documents for context retrieval via semantic search |
| Audit Logger | Data Store | Centralized logging data store recording decision logs, tool execution logs, and filtering events from multiple components |
| External API | External Entity | Third-party external API service accessed by the MCP Tool Server over HTTPS |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| User | Guardrails Service | Prompt / Query | HTTPS |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | Not specified |
| Guardrails Service | User | Rejected Prompt + Reason | Not specified |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval Query | Vector Search |
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
| AI Framework | LLM (Large Language Model) | Not specified |
| Protocol | MCP (Model Context Protocol) | Not specified |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| User Zone | Untrusted | User |
| Application Zone | Trusted | Guardrails Service, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger |
| External Services | Semi-Trusted | External API |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| User-to-Application | User Zone | Application Zone | User, Guardrails Service | HTTPS encryption, Guardrails input validation |
| Application-to-External | Application Zone | External Services | MCP Tool Server, External API | HTTPS encryption |
| Application-to-User (Response) | Application Zone | User Zone | LLM Agent Orchestrator, User | HTTPS encryption |
| Application-to-User (Rejection) | Application Zone | User Zone | Guardrails Service, User | Not specified |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | User | Attacker impersonates a legitimate user by stealing or forging authentication credentials (session tokens, API keys) to submit prompts and queries to the Guardrails Service, because no multi-factor authentication or token-binding mechanism is specified at the system entry point | MEDIUM | HIGH | High | Implement multi-factor authentication for user sessions; bind session tokens to client fingerprints (IP, TLS certificate, device ID) using DPoP or certificate-bound tokens; enforce token expiration with sliding window of 15 minutes |
| S-2 | Guardrails Service | Attacker bypasses the Guardrails Service by directly accessing the LLM Agent Orchestrator endpoint, spoofing the identity of the Guardrails Service in inter-service communication, because mutual authentication between internal services is not specified | MEDIUM | HIGH | High | Enforce mutual TLS (mTLS) between the Guardrails Service and LLM Agent Orchestrator; validate service identity certificates on every request; reject any request to the orchestrator that does not originate from the authenticated Guardrails Service |
| S-3 | LLM Agent Orchestrator | Attacker forges service identity to impersonate the LLM Agent Orchestrator when communicating with the MCP Tool Server or Knowledge Base, because inter-service authentication between application zone components is not specified | HIGH | HIGH | Critical | Implement mTLS with certificate pinning between the LLM Agent Orchestrator and all downstream services (MCP Tool Server, Knowledge Base); use signed JWTs with RS256 and audience restriction for service-to-service authentication |
| S-4 | MCP Tool Server | Attacker spoofs the identity of the MCP Tool Server to intercept or redirect tool call requests from the LLM Agent Orchestrator, because service discovery and identity verification for the MCP Tool Server endpoint are not specified | MEDIUM | HIGH | High | Implement service identity verification using mTLS certificates for the MCP Tool Server; pin the server certificate in the orchestrator's configuration; validate server identity on every JSON-RPC connection |
| S-5 | External API | Attacker performs DNS spoofing or man-in-the-middle attack to redirect API requests from the MCP Tool Server to an attacker-controlled endpoint impersonating the External API | LOW | HIGH | Medium | Implement certificate pinning for the External API endpoint in the MCP Tool Server; validate TLS certificate chain on every HTTPS connection; monitor for certificate transparency log anomalies |

### 3.2 Tampering (T)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Guardrails Service | Attacker tampers with validation rules or filter configuration of the Guardrails Service to weaken or disable input screening, allowing malicious prompts to pass through to the orchestrator | MEDIUM | HIGH | High | Store Guardrails configuration in immutable, version-controlled storage with cryptographic integrity checks (SHA-256 checksums); implement change detection with alerts on any configuration modification; require multi-party approval for rule changes |
| T-2 | LLM Agent Orchestrator | Attacker modifies the validated prompt in transit between the Guardrails Service and the LLM Agent Orchestrator, because the internal data flow lacks integrity protection | MEDIUM | HIGH | High | Sign validated prompts with HMAC-SHA256 at the Guardrails Service; verify signature at the LLM Agent Orchestrator before processing; reject any request with an invalid or missing signature |
| T-3 | MCP Tool Server | Attacker tampers with JSON-RPC tool call requests or responses between the LLM Agent Orchestrator and MCP Tool Server to alter tool parameters or inject malicious payloads | MEDIUM | HIGH | High | Implement message-level integrity protection (HMAC signatures) on all JSON-RPC messages between the orchestrator and tool server; validate message integrity before processing; enforce strict JSON schema validation on tool call parameters |
| T-4 | Knowledge Base | Attacker injects or modifies documents in the Knowledge Base to corrupt the context retrieval pipeline, causing the orchestrator to reason over poisoned data | MEDIUM | HIGH | High | Implement write access controls restricting Knowledge Base modifications to authorized administrative roles only; enforce integrity checksums (SHA-256) on all stored documents; maintain an immutable audit trail of all document changes with author attribution |
| T-5 | Audit Logger | Attacker tampers with audit log entries to conceal malicious activity, modifying or deleting decision logs, tool execution logs, or filtering event records | MEDIUM | HIGH | High | Store audit logs in append-only, immutable storage (write-once-read-many); implement cryptographic log chaining (hash chain) where each entry includes the hash of the previous entry; forward logs to an external SIEM within 60 seconds for independent verification |
| T-6 | Knowledge Base | Attacker exploits insufficient input validation on the LLM Agent Orchestrator's write path to inject adversarial content into the Knowledge Base, modifying vector embeddings to bias retrieval results | LOW | HIGH | Medium | Implement content validation and adversarial content filtering on all write operations to the Knowledge Base; sanitize document content before embedding generation; enforce allowlist-based content type restrictions |

### 3.3 Repudiation (R)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | User | User denies having submitted a specific prompt or query that triggered a consequential action (data modification, external API call, or sensitive information retrieval), because user-level action attribution is insufficient to prove the specific prompt was submitted by the authenticated user | MEDIUM | MEDIUM | Medium | Implement request-level audit logging that records authenticated user identity, full prompt text hash, timestamp (UTC), source IP, and session ID for every submitted prompt; store in append-only audit storage with cryptographic integrity |
| R-2 | LLM Agent Orchestrator | The LLM Agent Orchestrator executes tool calls and context retrievals without logging the complete decision chain — the originating user prompt, model reasoning, selected tool, parameters, and tool response — making it impossible to attribute or reconstruct the decision path after the fact | MEDIUM | HIGH | High | Implement structured decision logging in the orchestrator that records: authenticated user ID, input prompt hash, model reasoning summary, tool selection rationale, tool call parameters, tool response summary, and final output; forward all decision logs to the Audit Logger within 60 seconds |
| R-3 | Guardrails Service | The Guardrails Service processes prompt rejections without sufficient logging detail, making it impossible to determine which specific rule triggered the rejection or whether the rejection was correct — an operator can claim a legitimate prompt was improperly blocked without evidence | MEDIUM | MEDIUM | Medium | Log every Guardrails filtering decision with: input prompt hash, matching rule ID, rejection reason, timestamp, and user session ID; include both accepted and rejected prompts in the audit trail for complete decision accountability |
| R-4 | MCP Tool Server | The MCP Tool Server executes external API calls without logging the complete execution context — which agent requested the call, what parameters were sent, and what response was received — enabling operators to deny responsibility for consequential external actions | MEDIUM | HIGH | High | Implement comprehensive tool execution logging that records: requesting agent identity, tool name, full parameter payload, external API endpoint, response status code, response body hash, execution duration, and UTC timestamp; forward to Audit Logger with correlation ID linking to the originating orchestrator decision |
| R-5 | External API | Actions performed against the External API by the MCP Tool Server cannot be attributed to the originating user because the API request chain does not propagate user identity context from the application zone to external services | LOW | MEDIUM | Low | Include a correlation header (X-Request-ID) in all outbound API requests from the MCP Tool Server that links to the originating user session and orchestrator decision ID; log the correlation at both the MCP Tool Server and Audit Logger for end-to-end traceability |

### 3.4 Information Disclosure (I)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | LLM Agent Orchestrator | The orchestrator returns verbose error messages containing internal system state — model configuration, service endpoints, stack traces, or prompt template structure — when processing errors occur, exposing architectural details to external users | MEDIUM | MEDIUM | Medium | Implement standardized error responses that return only user-facing error codes without internal details; route detailed error information to internal logging only; sanitize all error responses before returning to the user |
| I-2 | MCP Tool Server | The MCP Tool Server exposes sensitive data from External API responses to the LLM Agent Orchestrator without filtering, allowing confidential API response data (API keys, internal identifiers, PII) to be included in the orchestrator's context and potentially surfaced in user-facing responses | MEDIUM | HIGH | High | Implement response filtering at the MCP Tool Server that strips sensitive fields (credentials, internal identifiers, PII patterns) from External API responses before returning tool results to the orchestrator; define an allowlist of permitted response fields per tool |
| I-3 | Knowledge Base | The Knowledge Base returns full document contents including internal metadata, embedding vectors, and storage identifiers in query responses, because field-level filtering is not applied — sensitive training data, internal classifications, or document provenance information could be extracted through crafted queries | HIGH | MEDIUM | High | Implement field-level projection on Knowledge Base query responses to return only content fields required by the orchestrator; strip internal metadata, embedding vectors, and storage identifiers from all query responses |
| I-4 | Audit Logger | Audit log entries contain sensitive data (full prompt text, user PII, API credentials, tool parameters) that could be exposed through unauthorized access to the log storage or log management interface | MEDIUM | HIGH | High | Encrypt audit log entries at rest using AES-256; implement field-level encryption for sensitive data within log entries (prompt content, user PII, credentials); enforce role-based access control on log storage with principle of least privilege; mask sensitive fields in log viewing interfaces |
| I-5 | Guardrails Service | The Guardrails rejection response includes overly detailed information about which validation rule was triggered and the specific pattern that matched, enabling an attacker to iteratively refine malicious prompts to bypass the filtering rules | MEDIUM | MEDIUM | Medium | Return generic rejection messages to users without revealing which specific rule or pattern triggered the rejection; log detailed rejection information internally for security team review only |

### 3.5 Denial of Service (D)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | LLM Agent Orchestrator | Attacker sends concurrent requests with maximum-length prompts to the orchestrator, exhausting compute and memory resources for LLM inference, because no per-client rate limit or request size cap is enforced | HIGH | HIGH | Critical | Enforce per-client rate limiting (10 requests/minute); cap prompt input at 4,096 tokens; configure request timeout at 30 seconds; set memory limit per worker with OOM-kill restart policy; implement circuit breaker after 5 consecutive failures |
| D-2 | MCP Tool Server | Attacker triggers excessive tool calls through the orchestrator by submitting prompts designed to produce many parallel tool invocations, exhausting the tool server's connection pool and compute resources | HIGH | MEDIUM | High | Implement per-request tool call limits (maximum 10 tool calls per orchestrator request); enforce tool server connection pool limits with timeouts; implement backpressure signaling from tool server to orchestrator when capacity threshold is reached |
| D-3 | Knowledge Base | Attacker submits queries designed to trigger expensive vector similarity searches across the entire Knowledge Base, exhausting database compute resources and blocking legitimate context retrieval requests | MEDIUM | MEDIUM | Medium | Implement query complexity limits on vector search operations (maximum result set size, similarity threshold floor); enforce per-client query rate limits; add query timeout of 5 seconds; implement result caching for repeated queries |
| D-4 | Guardrails Service | Attacker floods the Guardrails Service with high-volume prompt submissions, exhausting its validation processing capacity and blocking legitimate user prompts from reaching the orchestrator | HIGH | MEDIUM | High | Deploy rate limiting at the network edge before the Guardrails Service (API gateway or WAF); implement per-IP and per-session rate limits; add request size limits; deploy horizontal scaling with auto-scale triggers based on queue depth |
| D-5 | Audit Logger | Attacker triggers high-volume logging events by submitting many requests that generate multiple log entries each (rejected prompts, tool calls, decision logs), flooding the Audit Logger and exhausting storage capacity or write throughput | MEDIUM | MEDIUM | Medium | Implement log rate limiting with aggregation for repeated events; set storage capacity alerts at 80% threshold; implement automatic log rotation with configurable retention periods; use buffered writes with backpressure to prevent storage exhaustion |

### 3.6 Elevation of Privilege (E)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | LLM Agent Orchestrator | Attacker exploits the orchestrator to access administrative functions or elevated tool capabilities by manipulating prompt content to trigger privileged operations, because the orchestrator does not enforce role-based access control on which tools or Knowledge Base operations are available per user role | HIGH | HIGH | Critical | Implement RBAC policy on the orchestrator that maps each user role to permitted tool categories and Knowledge Base access scopes; validate caller role before dispatching any tool call or context retrieval; reject unauthorized operations with 403 and log the attempt |
| E-2 | MCP Tool Server | Authenticated user invokes administrative or privileged tool endpoints on the MCP Tool Server by manipulating tool call parameters, because the server does not enforce role-based access control on tool dispatch — standard users can execute privileged operations such as configuration changes, data exports, or system commands | HIGH | HIGH | Critical | Implement per-tool RBAC policy on the MCP Tool Server that maps each tool endpoint to required permissions; validate the calling agent's authorization context (propagated from the authenticated user) before tool execution; maintain a tool permission manifest defining access tiers |
| E-3 | Guardrails Service | Attacker discovers and exploits an administrative or configuration endpoint on the Guardrails Service to modify validation rules, disable filtering, or add bypass entries — effectively granting themselves unrestricted access to the orchestrator | LOW | HIGH | Medium | Restrict administrative endpoints to a separate management network not accessible from the user-facing interface; require separate administrative authentication with MFA; implement change audit logging for all configuration modifications |
| E-4 | MCP Tool Server | Attacker achieves lateral movement from the MCP Tool Server to other application zone components by exploiting overly broad network policies and shared service credentials that allow the tool server to access internal services beyond the External API | MEDIUM | HIGH | High | Implement network segmentation with per-service firewall rules limiting the MCP Tool Server's outbound connections to only the External API and Audit Logger; use unique service credentials per component; enforce zero-trust network policies within the application zone |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| AG-1 | LLM Agent Orchestrator | The orchestrator operates in an iterative agent loop where the LLM decides when to terminate based on task completion assessment, but no maximum iteration count, execution timeout, or cost cap is enforced — an attacker submits an ambiguous prompt that causes the agent to loop indefinitely, consuming API credits, generating unintended tool calls on each iteration, and blocking the execution queue | HIGH | HIGH | Critical | Implement mandatory termination constraints: maximum iteration count (25 iterations), execution timeout (5 minutes), and cumulative cost cap per request; add circuit breaker that halts execution if the agent repeats the same action pattern for 3 consecutive iterations |
| AG-2 | LLM Agent Orchestrator | The orchestrator executes tool calls to the MCP Tool Server — including data modifications, external API calls, and system operations — without human approval gates for consequential actions, because the system does not distinguish between reversible (read) and irreversible (write, delete, send) operations | MEDIUM | HIGH | High | Classify tool operations into tiers: Tier 1 (read-only, auto-approve), Tier 2 (reversible writes, require confirmation), Tier 3 (irreversible actions, require human approval with mandatory wait period); implement pre-execution review for Tier 2 and Tier 3 actions | ASI-01, ASI-08 |
| AG-3 | MCP Tool Server | The MCP Tool Server exposes all registered tools to the orchestrator without per-agent or per-user capability scoping — any user can trigger any tool through prompt manipulation, violating the principle of least privilege for tool access | HIGH | HIGH | Critical | Implement per-user tool allowlists at the MCP Tool Server; scope available tools based on the authenticated user's role propagated from the orchestrator; log all tool invocations with user identity and tool name for audit | ASI-01, ASI-02 |
| AG-4 | MCP Tool Server | The MCP Tool Server does not enforce maximum tool call depth or recursion limits — an attacker can craft a prompt that causes the orchestrator to enter a tool call loop where each tool result triggers another tool call, creating cascading resource consumption across the orchestrator and tool server | MEDIUM | MEDIUM | Medium | Implement maximum tool call chain depth (5 calls per request); add circuit breaker between orchestrator and tool server; enforce per-request resource budgets; implement dead-letter handling for stuck tool executions | ASI-01, ASI-10 |

### 4.2 LLM Threats (LLM)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | LLM Agent Orchestrator | User-supplied prompts are forwarded from the Guardrails Service to the orchestrator where they are concatenated into the LLM context window without structural boundary enforcement between system instructions and user input — an attacker can inject adversarial instructions that override system prompts, causing the model to ignore safety constraints, exfiltrate data through tool calls, or produce harmful content | HIGH | HIGH | Critical | Implement structured prompt templates with explicit delimiter tokens between system instructions and user input; add an input classifier that detects adversarial prompt patterns before forwarding to the model; apply output filtering to detect responses that violate behavior boundaries | OWASP LLM01:2025 |
| LLM-2 | LLM Agent Orchestrator | The RAG pipeline retrieves documents from the Knowledge Base and injects them into the LLM context window without content sanitization — an attacker who can write to the Knowledge Base can embed adversarial instructions in documents that, when retrieved, override system behavior through indirect prompt injection | MEDIUM | HIGH | High | Sanitize retrieved document content before injection into the prompt context; implement provenance tracking so the model distinguishes system instructions from retrieved content; apply content integrity checks on documents before indexing | OWASP LLM01:2025 |
| LLM-3 | LLM Agent Orchestrator | Attacker manipulates Knowledge Base content to inject poisoned data that corrupts the orchestrator's context retrieval pipeline — documents containing deliberately incorrect, biased, or misleading information are indexed and returned as authoritative context, causing the model to produce inaccurate or harmful outputs | MEDIUM | HIGH | High | Implement content validation and adversarial content detection on all documents before indexing in the Knowledge Base; apply document-level access controls; add provenance metadata for source trustworthiness scoring; monitor retrieval patterns for anomalous document frequency | OWASP LLM03:2025 |
| LLM-4 | LLM Agent Orchestrator | The orchestrator's LLM inference endpoint lacks query volume monitoring, enabling an attacker to systematically query the model with crafted inputs to extract model behavior patterns, system prompt content, or reconstruct model capabilities through distillation | MEDIUM | MEDIUM | Medium | Implement per-user query volume limits with alerts at threshold crossings; restrict API output to necessary response fields only; deploy query pattern analysis to detect systematic probing; add watermarking to model outputs | OWASP LLM10:2025 |

---

## 4a. Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-2, LLM-3 | LLM Agent Orchestrator | Tampering: Attacker modifies validated prompt in transit between Guardrails and Orchestrator; Data-Poisoning: Knowledge Base content poisoned to corrupt context retrieval pipeline — both exploit data integrity weaknesses in the orchestrator's input processing chain | High |
| CG-2 | E-1, AG-1 | LLM Agent Orchestrator | Elevation of Privilege: Attacker exploits orchestrator to access administrative functions via prompt manipulation; Agent-Autonomy: Orchestrator operates without iteration limits or human approval gates — combined excessive permissions and unconstrained autonomy enable unrestricted action execution | Critical |
| CG-3 | I-1, LLM-1 | LLM Agent Orchestrator | Information Disclosure: Orchestrator returns verbose error messages exposing internal state; Prompt-Injection: Direct injection via user prompts overrides system behavior — prompt injection enables targeted extraction of disclosed internal information | Critical |
| CG-4 | R-4, AG-3 | MCP Tool Server | Repudiation: Tool execution lacks complete audit context; Agent-Autonomy: Tool server exposes all tools without per-user scoping — accountability gaps combined with excessive tool access create unattributable privileged operations | Critical |
| CG-5 | D-2, AG-4 | MCP Tool Server | Denial of Service: Excessive tool calls exhaust connection pool; Tool-Abuse: No tool call depth limit enables cascading tool invocations — resource exhaustion amplified by unconstrained tool chaining | High |

---

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| User | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Guardrails Service | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| LLM Agent Orchestrator | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 4 | 12 |
| MCP Tool Server | 1 | 1 | 1 | 1 | 1 | 2 | 2 | n/a | 9 |
| Knowledge Base | n/a | 2 | n/a | 1 | 1 | n/a | n/a | n/a | 4 |
| Audit Logger | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| External API | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| **Total** | **5** | **6** | **5** | **5** | **5** | **4** | **4** | **4** | **38** |

Counts reflect deduplicated findings. 5 correlation groups merged 10 individual findings.

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
| Critical | 7 | 20.6% |
| High | 15 | 44.1% |
| Medium | 10 | 29.4% |
| Low | 1 | 2.9% |
| Note | 0 | 0.0% |
| **Total** | **33 (38 raw)** | **100%** |

---

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-3 | LLM Agent Orchestrator | Attacker forges service identity to impersonate the orchestrator in communication with downstream services | Critical | Implement mTLS with certificate pinning between the LLM Agent Orchestrator and all downstream services; use signed JWTs with RS256 and audience restriction |
| D-1 | LLM Agent Orchestrator | Concurrent maximum-length prompts exhaust compute and memory resources | Critical | Enforce per-client rate limiting (10 req/min); cap prompt input at 4,096 tokens; configure 30s timeout; set memory limits with OOM-kill restart |
| E-1 | LLM Agent Orchestrator | Prompt manipulation triggers privileged operations without RBAC enforcement | Critical | Implement RBAC mapping user roles to permitted tool categories and KB access scopes; validate caller role before dispatch |
| E-2 | MCP Tool Server | Standard users execute privileged tool endpoints without access control | Critical | Implement per-tool RBAC policy; validate calling agent's authorization context; maintain tool permission manifest |
| AG-1 | LLM Agent Orchestrator | Unbounded agent loop with no iteration limit, timeout, or cost cap | Critical | Implement max iteration count (25), execution timeout (5 min), cost cap per request; add circuit breaker for repeated actions |
| AG-3 | MCP Tool Server | All tools exposed to all users without per-agent capability scoping | Critical | Implement per-user tool allowlists; scope tools by authenticated user role; log all invocations with identity |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection via user prompts overrides system instructions | Critical | Implement structured prompt templates with delimiters; add input classifier for adversarial patterns; apply output filtering |
| S-1 | User | Credential theft or forging enables user impersonation | High | Implement MFA; bind session tokens to client fingerprints using DPoP; enforce 15-minute sliding window expiration |
| S-2 | Guardrails Service | Attacker bypasses Guardrails by spoofing inter-service identity | High | Enforce mTLS between Guardrails and Orchestrator; validate service identity certificates on every request |
| S-4 | MCP Tool Server | Attacker spoofs MCP Tool Server identity to intercept tool calls | High | Implement mTLS certificates for Tool Server; pin server certificate in orchestrator config |
| T-1 | Guardrails Service | Tampering with validation rules weakens input screening | High | Store config in immutable version-controlled storage with SHA-256 checksums; implement change detection with alerts |
| T-2 | LLM Agent Orchestrator | Prompt modified in transit between Guardrails and Orchestrator | High | Sign validated prompts with HMAC-SHA256 at Guardrails; verify signature at Orchestrator |
| T-3 | MCP Tool Server | JSON-RPC messages tampered to alter tool parameters | High | Implement HMAC message-level integrity on JSON-RPC; validate before processing; enforce strict schema validation |
| T-4 | Knowledge Base | Document injection corrupts context retrieval pipeline | High | Implement write access controls; enforce SHA-256 checksums on stored documents; maintain immutable audit trail |
| T-5 | Audit Logger | Log entries tampered to conceal malicious activity | High | Store logs in append-only immutable storage with cryptographic hash chaining; forward to external SIEM within 60 seconds |
| R-2 | LLM Agent Orchestrator | Incomplete decision chain logging prevents action attribution | High | Implement structured decision logging recording user ID, prompt hash, reasoning, tool selection, parameters, response |
| R-4 | MCP Tool Server | Tool execution lacks complete audit context for accountability | High | Implement comprehensive tool execution logging with agent identity, parameters, response, duration, correlation ID |
| I-2 | MCP Tool Server | Sensitive External API data forwarded unfiltered to orchestrator | High | Implement response filtering stripping sensitive fields; define allowlist of permitted response fields per tool |
| I-3 | Knowledge Base | Full document contents with metadata returned without filtering | High | Implement field-level projection returning only required content fields; strip metadata and embeddings |
| I-4 | Audit Logger | Sensitive data in logs exposed through unauthorized access | High | Encrypt logs at rest (AES-256); field-level encryption for PII; RBAC on log storage; mask sensitive fields in viewers |
| D-2 | MCP Tool Server | Excessive tool calls exhaust connection pool and compute | High | Implement per-request tool call limits (10 max); enforce connection pool limits with timeouts; implement backpressure |
| D-4 | Guardrails Service | High-volume prompt flood blocks legitimate requests | High | Deploy edge rate limiting (API gateway/WAF); per-IP and per-session limits; request size limits; auto-scaling |
| AG-2 | LLM Agent Orchestrator | Consequential actions executed without human approval gates | High | Classify tools into reversibility tiers; implement pre-execution review for irreversible actions |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via poisoned Knowledge Base documents | High | Sanitize retrieved content; implement provenance tracking; apply content integrity checks before indexing |
| LLM-3 | LLM Agent Orchestrator | Data poisoning corrupts context retrieval with misleading content | High | Implement content validation before indexing; document-level access controls; provenance metadata; retrieval monitoring |
| E-4 | MCP Tool Server | Lateral movement from tool server to other internal services | High | Network segmentation with per-service firewall rules; unique credentials per component; zero-trust network policies |
| S-5 | External API | DNS spoofing redirects API requests to attacker endpoint | Medium | Certificate pinning for External API; validate TLS certificate chain; monitor certificate transparency logs |
| T-6 | Knowledge Base | Adversarial content injection modifies vector embeddings | Medium | Content validation and adversarial filtering on writes; sanitize before embedding; allowlist content types |
| R-1 | User | User denies submitting a specific consequential prompt | Medium | Request-level audit logging with user identity, prompt hash, timestamp, source IP, session ID |
| R-3 | Guardrails Service | Insufficient rejection logging prevents decision accountability | Medium | Log every filtering decision with prompt hash, rule ID, rejection reason, timestamp, session ID |
| I-1 | LLM Agent Orchestrator | Verbose error messages expose internal system state | Medium | Standardized error responses with user-facing codes only; route details to internal logging |
| I-5 | Guardrails Service | Rejection responses reveal validation rule details | Medium | Return generic rejection messages; log detailed information internally for security review only |
| D-3 | Knowledge Base | Expensive vector searches exhaust database resources | Medium | Query complexity limits; per-client query rate limits; 5-second timeout; result caching |
| D-5 | Audit Logger | Log flooding exhausts storage capacity | Medium | Log rate limiting with aggregation; 80% storage alerts; automatic rotation; buffered writes with backpressure |
| E-3 | Guardrails Service | Administrative endpoint exploitation modifies validation rules | Medium | Restrict admin endpoints to management network; separate admin auth with MFA; change audit logging |
| AG-4 | MCP Tool Server | No tool call depth limit enables cascading invocations | Medium | Max tool call chain depth (5); circuit breaker; per-request resource budgets; dead-letter handling |
| LLM-4 | LLM Agent Orchestrator | Systematic querying extracts model behavior patterns | Medium | Per-user query volume limits; restrict response fields; query pattern analysis; output watermarking |
| R-5 | External API | External API actions not attributable to originating user | Low | Include X-Request-ID correlation header in outbound requests; log correlation at both Tool Server and Audit Logger |
