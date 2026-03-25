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
| Guardrails Service | Process | Input validation and filtering service that screens prompts before forwarding to the orchestrator and rejects malicious or policy-violating inputs |
| LLM Agent Orchestrator | Process | Central orchestration process that coordinates LLM inference, context retrieval from the Knowledge Base, and tool invocations via the MCP Tool Server |
| MCP Tool Server | Process | Model Context Protocol server that executes tool calls on behalf of the orchestrator and communicates with external APIs |
| Knowledge Base | Data Store | Vector search-enabled document store used for context retrieval (RAG) by the orchestrator |
| Audit Logger | Data Store | Centralized logging store that receives decision logs, tool execution logs, and filtering event logs from multiple components |
| External API | External Entity | Third-party external service consumed by the MCP Tool Server via HTTPS |

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
| Framework | Model Context Protocol (MCP) | Not specified |
| AI | LLM (Large Language Model) | Not specified |

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
| Application Response to User | Application Zone | User Zone | LLM Agent Orchestrator, User | HTTPS transport encryption |

## 3. STRIDE Threat Analysis

### 3.1 Spoofing

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | User | An attacker impersonates a legitimate user by stealing or forging authentication credentials (session tokens, API keys) because the architecture does not specify authentication mechanisms at the User-to-Guardrails entry point, enabling unauthorized prompt submissions under a trusted identity. | HIGH | HIGH | Critical | Implement multi-factor authentication (MFA) at the user entry point. Issue short-lived session tokens (15-minute expiry) with HTTPS-only, Secure, SameSite=Strict cookie attributes. Enforce token binding via DPoP (Demonstrating Proof-of-Possession) to prevent token replay. |
| S-2 | Guardrails Service | An attacker bypasses the Guardrails Service by directly addressing the LLM Agent Orchestrator endpoint, because no mutual authentication exists between the Guardrails Service and the Orchestrator to verify that validated prompts originate from the legitimate Guardrails Service instance. | MEDIUM | HIGH | High | Enforce mutual TLS (mTLS) between the Guardrails Service and LLM Agent Orchestrator. The Orchestrator must reject all inbound prompt traffic not originating from a verified Guardrails Service certificate. Implement an allowlist of trusted service identities at the Orchestrator's ingress. |
| S-3 | LLM Agent Orchestrator | An attacker forges service identity tokens to impersonate the LLM Agent Orchestrator when communicating with the MCP Tool Server, because inter-service authentication between the Orchestrator and Tool Server over JSON-RPC is not specified, enabling unauthorized tool invocations under a trusted orchestrator identity. | MEDIUM | HIGH | High | Enforce mutual TLS (mTLS) with certificate pinning between the LLM Agent Orchestrator and MCP Tool Server. Validate service identity claims using signed JWTs with RS256 and audience restriction. Reject tool call requests that lack a valid service identity assertion. |
| S-4 | MCP Tool Server | An attacker spoofs the MCP Tool Server's identity when returning tool results to the Orchestrator over JSON-RPC, because response authenticity is not verified, enabling injection of fabricated tool results that the Orchestrator treats as legitimate. | MEDIUM | HIGH | High | Implement response signing on all MCP Tool Server responses using HMAC-SHA256 with a shared secret or asymmetric signatures. The Orchestrator must validate response signatures before processing tool results. Log and alert on signature verification failures. |
| S-5 | External API | An attacker performs a DNS spoofing or man-in-the-middle attack to redirect the MCP Tool Server's HTTPS requests to a malicious endpoint impersonating the External API, because certificate pinning and strict hostname verification are not specified for the outbound HTTPS connection. | LOW | HIGH | Medium | Implement certificate pinning for the External API's TLS certificate in the MCP Tool Server's HTTP client configuration. Enforce strict hostname verification. Use a DNS-over-HTTPS resolver to mitigate DNS spoofing. Monitor for certificate changes and alert on unexpected certificate rotation. |

### 3.2 Tampering

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Guardrails Service | An attacker tampers with the Guardrails Service's validation rules or filtering configuration to disable prompt screening, allowing malicious prompts to pass through to the LLM Agent Orchestrator unchecked, because the configuration management and integrity verification of the Guardrails Service's ruleset is not specified. | MEDIUM | HIGH | High | Store Guardrails Service validation rules in an immutable configuration store with cryptographic integrity verification (SHA-256 checksums). Implement configuration drift detection that alerts on unauthorized rule modifications. Apply least-privilege access controls on the configuration store with separate read/write roles. |
| T-2 | LLM Agent Orchestrator | An attacker tampers with the prompt in transit between the Guardrails Service and the LLM Agent Orchestrator, modifying the validated prompt to inject malicious content, because the internal data flow does not specify integrity protection (no message signing or integrity checks). | MEDIUM | HIGH | High | Implement message-level integrity protection (HMAC-SHA256) on prompts forwarded from the Guardrails Service to the Orchestrator. The Orchestrator must verify the integrity signature before processing any prompt. Reject prompts with invalid or missing signatures and log the event. |
| T-3 | MCP Tool Server | An attacker modifies tool call parameters in transit between the Orchestrator and MCP Tool Server over JSON-RPC, because the JSON-RPC channel does not specify message-level integrity verification, enabling parameter injection that changes tool behavior. | MEDIUM | HIGH | High | Sign all JSON-RPC messages between the Orchestrator and MCP Tool Server using HMAC-SHA256. Enforce strict parameter schema validation at the Tool Server level before executing any tool. Reject requests with invalid signatures or schema-non-conforming parameters. |
| T-4 | Knowledge Base | An attacker injects malicious or misleading content into the Knowledge Base through the LLM Agent Orchestrator's write path, because input sanitization is not enforced before persisting user-supplied or agent-generated data to the vector store, corrupting the RAG retrieval context. | HIGH | HIGH | Critical | Implement content validation with allowlist-based filtering on all write operations to the Knowledge Base. Enforce integrity checksums (SHA-256) on stored records. Apply write-audit logging with immutable append-only storage for change history. Restrict write access to a dedicated data ingestion pipeline with review workflows. |
| T-5 | Audit Logger | An attacker tampers with audit log entries by modifying or deleting records in the Audit Logger, because the log store's integrity protection and access controls are not specified, enabling an attacker to cover their tracks after a security incident. | MEDIUM | HIGH | High | Store audit logs in an append-only, immutable storage backend (e.g., write-once S3 bucket, blockchain-anchored log, or WORM storage). Forward logs to an external SIEM within 60 seconds of generation. Implement cryptographic log chaining (hash chain) to detect any tampering with historical entries. Restrict direct access to the log store to a read-only role. |

### 3.3 Repudiation

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | User | A user denies having submitted a specific prompt or query that triggered a harmful or policy-violating action, because the system does not bind user identity to prompt submissions with sufficient non-repudiation evidence (no digital signature or strong session attribution on user requests). | MEDIUM | HIGH | High | Bind each user prompt submission to the authenticated user identity with a server-side timestamp and session correlation ID. Store the authenticated user ID, source IP, session token hash, and full prompt text in the Audit Logger as an immutable record. Implement digital signature or TLS client certificate-based non-repudiation for high-stakes operations. |
| R-2 | Guardrails Service | The Guardrails Service fails to log prompt rejection decisions with sufficient detail, allowing disputed claims about whether a prompt was legitimately rejected or wrongly passed through, because the architecture shows logging to the Audit Logger but does not specify the granularity of filtering event logs. | MEDIUM | MEDIUM | Medium | Instrument the Guardrails Service to emit structured audit events for every filtering decision: log the full input prompt, filtering rule matched, decision (accept/reject), rejection reason, authenticated user ID, and UTC timestamp with millisecond precision. Forward events to the Audit Logger within 60 seconds. |
| R-3 | LLM Agent Orchestrator | The LLM Agent Orchestrator executes tool calls to the MCP Tool Server without logging the originating user request, selected tool, input parameters, and tool response in a tamper-evident audit trail, enabling an operator or user to deny having triggered a destructive tool action because the system lacks evidence to attribute it. | HIGH | HIGH | Critical | Instrument the LLM Agent Orchestrator to emit structured audit events for every tool dispatch: record authenticated user ID, tool name, input parameters, response summary, model decision reasoning, and UTC timestamp. Forward events to the Audit Logger using append-only immutable storage. Implement log correlation IDs that chain user request to tool invocation to tool response. |
| R-4 | MCP Tool Server | The MCP Tool Server executes tool operations against the External API without logging the complete tool execution context, enabling denial of responsibility for actions taken by the tool server on behalf of the orchestrator, because tool execution logs may lack the originating user identity and full request chain. | MEDIUM | MEDIUM | Medium | Log every tool execution with the full request chain: originating user ID (forwarded from orchestrator), tool name, tool parameters, external API endpoint called, external API response status, execution duration, and UTC timestamp. Forward logs to the Audit Logger. Include a correlation ID that links back to the orchestrator's decision log entry. |
| R-5 | External API | The External API denies having received or processed a request from the MCP Tool Server, because no mutual logging or signed receipts exist between the two systems, creating a dispute scenario when external API calls fail or produce unexpected results. | LOW | MEDIUM | Low | Implement request/response logging on the MCP Tool Server side for all External API interactions, including full request payload, response payload, HTTP status code, and timing. Request signed receipts or correlation IDs from the External API where supported. Store these records in the Audit Logger as immutable entries for dispute resolution. |

### 3.4 Information Disclosure

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | Guardrails Service | The Guardrails Service returns detailed rejection reasons to the User that reveal internal filtering rules, regular expression patterns, or classification thresholds, enabling an attacker to iteratively refine prompts to bypass the filter by learning exactly what patterns are blocked. | HIGH | MEDIUM | High | Return generic rejection messages to users (e.g., "Your request could not be processed") without exposing specific filtering rules or patterns. Log detailed rejection reasons to the Audit Logger for internal review only. Implement rate limiting on rejection responses to slow iterative probing. |
| I-2 | LLM Agent Orchestrator | The LLM Agent Orchestrator leaks sensitive internal context (system prompts, tool descriptions, Knowledge Base metadata, or internal API endpoints) in its responses to the User, because output filtering does not strip internal system information before returning the model's response over HTTPS. | HIGH | HIGH | Critical | Implement output filtering on the LLM Agent Orchestrator's response path that strips system prompt fragments, tool descriptions, internal URLs, API keys, and Knowledge Base metadata before returning responses to users. Apply a response classifier that detects and blocks outputs containing internal system information. Log filtered content for security review. |
| I-3 | MCP Tool Server | The MCP Tool Server includes verbose error messages in tool results returned to the Orchestrator, revealing internal stack traces, database connection strings, or file paths when tool execution fails, which may then be forwarded to the User in the Orchestrator's response. | MEDIUM | MEDIUM | Medium | Implement generic error responses at the MCP Tool Server level that do not expose internal system details. Return standardized error codes and messages. Route detailed error diagnostics to the Audit Logger only. Ensure the Orchestrator's output filter also strips any residual error details from tool results before responding to users. |
| I-4 | Knowledge Base | The Knowledge Base returns full document contents including internal metadata, embedding vectors, document classification labels, and storage schema details in query responses to the LLM Agent Orchestrator, enabling extraction of sensitive information through crafted retrieval queries. | HIGH | MEDIUM | High | Implement field-level projection on Knowledge Base query responses to return only content fields required by the Orchestrator. Strip internal metadata, embedding vectors, document classification labels, and storage identifiers. Enforce query-scoped access controls matching the requesting user's authorization level. |
| I-5 | Audit Logger | The Audit Logger stores sensitive data (user credentials, full prompt contents, PII) in log entries that are accessible to operations staff or monitoring systems with broader access than necessary, because log content filtering and access controls on the log store are not specified. | MEDIUM | HIGH | High | Implement data classification and redaction on log entries before storage: mask or hash PII fields, credentials, and sensitive prompt content. Apply role-based access controls on the Audit Logger with separate roles for write (application services) and read (security analysts only). Encrypt log data at rest using AES-256. |
| I-6 | Audit Logger | Audit log data flows from multiple components (Guardrails Service, LLM Agent Orchestrator, MCP Tool Server) to the Audit Logger over internal channels without encryption, enabling a network-level attacker within the Application Zone to intercept log traffic containing sensitive operational data. | LOW | MEDIUM | Low | Encrypt all internal data flows to the Audit Logger using TLS 1.3. Implement mutual TLS between logging clients and the Audit Logger to authenticate log sources. Monitor for unencrypted log traffic on internal network segments. |

### 3.5 Denial of Service

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | Guardrails Service | An attacker floods the Guardrails Service with high-volume prompt submissions, exhausting compute resources allocated to input validation and blocking legitimate users from submitting prompts, because the architecture does not specify rate limiting or request throttling at the entry point. | HIGH | HIGH | Critical | Implement per-client rate limiting (e.g., 10 requests/minute for unauthenticated, 60 requests/minute for authenticated users) at the Guardrails Service entry point. Deploy request size limits (maximum 4096 tokens per prompt). Add a WAF or DDoS protection layer upstream of the Guardrails Service. Configure circuit breaker with automatic recovery. |
| D-2 | LLM Agent Orchestrator | An attacker submits maximum-length prompts that trigger expensive LLM inference and multiple Knowledge Base retrieval cycles, exhausting memory, compute, and API token budgets on the Orchestrator, because no per-request resource caps or inference timeouts are specified. | HIGH | HIGH | Critical | Enforce per-request resource caps: maximum prompt length (4096 tokens), inference timeout (30 seconds), maximum tool calls per request (5), and maximum Knowledge Base retrievals per request (3). Implement per-client rate limiting. Configure memory limits per worker (1GB) with OOM-kill restart policy. Set monthly API token budget caps with alerts at 80% threshold. |
| D-3 | MCP Tool Server | An attacker causes the MCP Tool Server to make excessive outbound API requests to the External API by triggering rapid tool invocations, exhausting connection pools and potentially incurring financial costs from external API usage, because no per-request or per-client tool invocation limits are specified. | MEDIUM | MEDIUM | Medium | Implement per-client tool invocation rate limits (maximum 10 tool calls/minute). Configure connection pool limits and timeouts on outbound HTTP clients (maximum 20 connections, 10-second timeout). Implement a circuit breaker that disables External API calls after 5 consecutive failures. Set External API usage budget caps with alerts. |
| D-4 | Knowledge Base | An attacker triggers resource-intensive vector search queries through crafted prompts that cause the Knowledge Base to perform full-index scans or return excessively large result sets, degrading search performance for all users. | MEDIUM | MEDIUM | Medium | Implement query complexity limits on Knowledge Base vector searches: maximum result set size (10 documents), query timeout (5 seconds), and minimum similarity threshold to prevent full-index scans. Apply per-client query rate limiting through the Orchestrator. Monitor query performance and alert on anomalous latency spikes. |
| D-5 | Audit Logger | An attacker triggers a flood of log entries by sending high-volume requests that each generate multiple log events across the Guardrails Service, Orchestrator, and MCP Tool Server, filling the Audit Logger's storage capacity and potentially causing log loss or system degradation. | MEDIUM | MEDIUM | Medium | Implement log volume rate limiting at each logging client (maximum 1000 log entries/minute per source). Configure Audit Logger storage with automatic rotation and retention policies (90-day retention, archive to cold storage). Set storage capacity alerts at 80% utilization. Implement log sampling for high-volume low-severity events during traffic spikes. |

### 3.6 Elevation of Privilege

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | Guardrails Service | An attacker exploits a bypass vulnerability in the Guardrails Service to escalate from a filtered/restricted user context to an unfiltered context, submitting prompts that should be blocked but are processed by the Orchestrator with full privileges, because the Guardrails Service does not enforce role-based access controls that differentiate between user privilege levels for different prompt categories. | MEDIUM | HIGH | High | Implement role-based prompt filtering policies in the Guardrails Service that enforce different validation rules based on user role (e.g., standard user, power user, admin). Validate user role claims server-side before applying filtering rules. Ensure the Orchestrator independently verifies the user's authorization level and does not solely rely on the Guardrails Service's pass/reject decision. |
| E-2 | LLM Agent Orchestrator | An attacker achieves privilege escalation through the LLM Agent Orchestrator by manipulating the model into requesting elevated tool permissions or accessing administrative tool endpoints on the MCP Tool Server, because the Orchestrator's tool dispatch does not enforce least-privilege constraints based on the originating user's authorization level. | HIGH | HIGH | Critical | Implement a permission boundary layer between the Orchestrator and MCP Tool Server that maps each user's authorization level to an allowlist of permitted tools. The Orchestrator must forward the authenticated user's role with every tool call request. The MCP Tool Server must validate that the requested tool is within the caller's permitted tool set. Reject unauthorized tool requests with HTTP 403 and log the attempt. |
| E-3 | MCP Tool Server | An authenticated user invokes administrative or privileged tool endpoints on the MCP Tool Server by manipulating tool_name or tool parameters, because the MCP Tool Server does not enforce role-based access control on tool dispatch, allowing standard users to execute privileged operations such as configuration changes and data exports. | HIGH | HIGH | Critical | Implement an RBAC policy on the MCP Tool Server that maps each tool endpoint to a required permission set. Validate the caller's role (propagated from the Orchestrator) against the tool's permission manifest before dispatch. Reject unauthorized tool invocations with 403 and log the attempt with caller identity and requested tool. Classify tools into tiers: read-only (auto-approve), write (require confirmation), administrative (require human approval). |

## 4. AI Threat Analysis

### 4.1 Agentic Threats (AG)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| AG-1 | LLM Agent Orchestrator | The LLM Agent Orchestrator operates with excessive autonomy, executing tool calls and Knowledge Base retrievals without constraints on iteration count, execution timeout, or cumulative cost, because no termination constraints or resource budgets are configured. An attacker can submit an ambiguous prompt that causes the Orchestrator to loop indefinitely, consuming API credits and generating cascading side effects through repeated tool invocations. | ASI-01 | HIGH | HIGH | Critical | Implement mandatory termination constraints: maximum iteration count (25 iterations), execution timeout (120 seconds), and cumulative cost cap ($5 per request). Add a circuit breaker that halts execution if the Orchestrator repeats the same action pattern for 3 consecutive iterations. Require human-in-the-loop approval for operations exceeding 10 tool calls in a single session. |
| AG-2 | LLM Agent Orchestrator | The LLM Agent Orchestrator makes consequential decisions (tool invocations that modify external state, data deletions, external communications) without human review or approval gates, because no distinction exists between low-stakes actions (read, analyze) and high-stakes actions (write, delete, send). A single misinterpreted prompt can trigger irreversible actions with no rollback path. | ASI-08 | MEDIUM | HIGH | High | Classify all agent-accessible actions into reversibility tiers: Tier 1 (read-only, auto-approve), Tier 2 (reversible writes, require confirmation), Tier 3 (irreversible actions, require human approval with mandatory wait period). Implement a pre-execution review step for Tier 2 and Tier 3 actions. Log all action classifications and approval decisions in the Audit Logger. |
| AG-3 | MCP Tool Server | The MCP Tool Server exposes all registered tools to the Orchestrator without per-agent or per-user capability scoping, because no tool allowlist or deny-list mechanism enforces which tools are accessible to which callers. An attacker who achieves prompt injection on the Orchestrator can invoke any tool the server offers, including privileged tools intended only for administrative use. | ASI-02, MCP-03 | HIGH | HIGH | Critical | Implement per-caller tool allowlists at the MCP Tool Server level. Each connection from the Orchestrator should declare the user's authorization scope, and the server should enforce that only permitted tools are invocable. Log all tool invocations with caller identity for audit purposes. Implement tool capability declarations that are validated against the caller's permission set before execution. |
| AG-4 | MCP Tool Server | An attacker manipulates tool call sequences through the Orchestrator to chain individually authorized tool operations into a capability that exceeds intended permissions (e.g., database-query + file-write = data exfiltration), because no cross-tool authorization policy evaluates the composite effect of sequential tool calls. | ASI-04, MCP-03 | MEDIUM | HIGH | High | Implement a tool chain policy engine that evaluates composite effects of sequential tool calls. Define forbidden tool combinations (e.g., data-read + network-send) and require human approval for chains that cross trust boundaries. Enforce a maximum tool chain depth of 5 sequential calls per request. Log the complete tool call sequence for each request. |

### 4.2 LLM Threats (LLM)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | LLM Agent Orchestrator | User-supplied prompts are forwarded through the Guardrails Service to the LLM Agent Orchestrator where they are concatenated into the model's context window without structural separation between system instructions and user content. An attacker can inject adversarial instructions that override the system prompt, causing the model to ignore safety constraints, execute unauthorized tool calls, or exfiltrate data through crafted responses. | OWASP LLM01:2025 | HIGH | HIGH | Critical | Implement structured prompt templates with explicit delimiter tokens between system instructions and user input. Add an input classifier at the Guardrails Service that detects adversarial prompt patterns (instruction override, role-play injection, DAN-style prompts) before forwarding to the Orchestrator. Apply output filtering to detect responses that violate expected behavior boundaries. Monitor prompt patterns for known jailbreak taxonomies. |
| LLM-2 | LLM Agent Orchestrator | The RAG pipeline retrieves documents from the Knowledge Base where content may have been injected by upstream users or automated processes. An attacker with write access to the Knowledge Base can embed adversarial instructions in documents that, when retrieved and injected into the LLM context window, override system behavior to exfiltrate data from other retrieved documents, generate misleading answers, or trigger unauthorized tool calls. | OWASP LLM01:2025 | MEDIUM | HIGH | High | Sanitize retrieved document content before injection into the prompt context. Implement provenance tracking so the model can distinguish system instructions from retrieved content. Apply content integrity checks on documents before indexing. Add structural delimiters between retrieved content and system instructions in the prompt template. Monitor retrieval patterns for anomalous document frequency spikes. |
| LLM-3 | LLM Agent Orchestrator | An attacker exploits the absence of output monitoring to systematically probe the model API through iterative prompt variations designed to extract the system prompt, internal tool descriptions, Knowledge Base schema, or API endpoint configurations, because no rate limiting on prompt submissions or prompt pattern monitoring is implemented at the model inference level. | OWASP LLM07:2025 | MEDIUM | MEDIUM | Medium | Implement rate limiting on prompt submissions per user session. Deploy a prompt classifier that flags known extraction patterns (meta-instruction queries, "repeat your instructions" variants, system prompt reflection attacks). Log all prompts for post-hoc analysis and establish alerting on anomalous prompt pattern clusters. Add output classifiers that detect responses containing system prompt fragments. |
| LLM-4 | LLM Agent Orchestrator | An attacker poisons the Knowledge Base content that feeds the RAG pipeline, injecting misleading or biased information that systematically corrupts the model's retrieval-augmented responses, because no content validation or adversarial content filtering is performed on documents before they are indexed into the vector store. | OWASP LLM03:2025 | MEDIUM | HIGH | High | Implement content validation and adversarial content detection on all documents before indexing in the Knowledge Base. Apply document-level access controls so that user-uploaded content is retrievable only within the uploader's trust boundary. Add provenance metadata to indexed documents. Monitor retrieval patterns for anomalous document frequency spikes. Implement periodic integrity audits on Knowledge Base content. |
| LLM-5 | LLM Agent Orchestrator | An attacker systematically queries the LLM Agent Orchestrator's model API with crafted inputs to extract model behavior patterns, reconstruct proprietary fine-tuning data, or distill a functional copy of the model, because no per-user query volume limits, query diversity analysis, or output restrictions (e.g., logprob suppression) are enforced at the inference endpoint. | OWASP LLM10:2025 | LOW | HIGH | Medium | Restrict API output to top-k predictions only (k <= 5) rather than full vocabulary logprobs. Implement per-API-key query budgets with alerts at threshold crossings. Deploy query pattern analysis that detects systematic probing (uniform input distributions, grid sampling patterns). Add watermarking to model outputs to enable downstream detection of extracted copies. |

## 4a. Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-4, LLM-4 | Knowledge Base | Tampering: Attacker injects malicious content into the Knowledge Base corrupting RAG retrieval context; Data-Poisoning: Attacker poisons Knowledge Base content feeding the RAG pipeline with misleading information — both exploit data integrity gaps in the vector store write path. | Critical |
| CG-2 | E-2, AG-1 | LLM Agent Orchestrator | Privilege-Escalation: Attacker manipulates model into requesting elevated tool permissions bypassing user authorization; Agent-Autonomy: Orchestrator operates with excessive autonomy executing tool calls without constraints — both exploit insufficient permission boundaries on agent-initiated actions. | Critical |
| CG-3 | I-2, LLM-1 | LLM Agent Orchestrator | Information-Disclosure: Orchestrator leaks sensitive internal context in responses to users; Prompt-Injection: Attacker injects adversarial instructions overriding system prompt to exfiltrate data — both exploit the absence of output filtering and prompt boundary enforcement. | Critical |
| CG-4 | R-3, AG-2 | LLM Agent Orchestrator | Repudiation: Orchestrator executes tool calls without logging originating user request enabling denial of actions; Agent-Autonomy: Orchestrator makes consequential decisions without human review — both exploit accountability gaps in autonomous agent operations. | Critical |
| CG-5 | D-3, AG-4 | MCP Tool Server | Denial-of-Service: Attacker causes excessive outbound API requests exhausting connection pools; Tool-Abuse: Attacker chains individually authorized tools into capability-escalating sequences — both exploit the absence of resource and policy constraints on tool invocations. | High |

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| LLM Agent Orchestrator | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 10 |
| MCP Tool Server | 1 | 1 | 1 | 1 | 1 | 1 | 1 | n/a | 7 |
| Guardrails Service | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 7 |
| Audit Logger | n/a | 1 | n/a | 2 | 1 | n/a | n/a | n/a | 4 |
| Knowledge Base | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| User | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| External API | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| **Total** | **5** | **5** | **5** | **6** | **5** | **3** | **2** | **3** | **34** |

Counts reflect deduplicated findings. 5 correlation groups merged 10 individual findings into 5 group entries.

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
| Critical | 9 (11 raw) | 27.3% |
| High | 14 (16 raw) | 42.4% |
| Medium | 8 (9 raw) | 24.2% |
| Low | 2 | 6.1% |
| Note | 0 | 0.0% |
| **Total** | **33 (38 raw)** | **100%** |

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-1 | User | Attacker impersonates legitimate user via stolen/forged credentials at entry point | Critical | Implement MFA, short-lived session tokens with DPoP binding, HTTPS-only Secure SameSite=Strict cookies |
| T-4 | Knowledge Base | Malicious content injection into Knowledge Base corrupting RAG retrieval context | Critical | Content validation with allowlist filtering, SHA-256 integrity checksums, write-audit logging, restricted write access with review workflows |
| R-3 | LLM Agent Orchestrator | Tool calls executed without logging originating user, tool, parameters, or response | Critical | Structured audit events for every tool dispatch with user ID, tool name, parameters, response, reasoning, UTC timestamp; append-only SIEM forwarding |
| I-2 | LLM Agent Orchestrator | Sensitive internal context leaked in responses to users | Critical | Output filtering to strip system prompt fragments, tool descriptions, internal URLs, API keys; response classifier to block outputs containing system information |
| D-1 | Guardrails Service | High-volume prompt flooding exhausting compute resources | Critical | Per-client rate limiting, request size limits, WAF/DDoS protection upstream, circuit breaker with auto-recovery |
| D-2 | LLM Agent Orchestrator | Maximum-length prompts exhausting memory, compute, and API token budgets | Critical | Per-request resource caps (prompt length, inference timeout, tool call limit, retrieval limit), per-client rate limiting, memory limits with OOM-kill restart |
| E-2 | LLM Agent Orchestrator | Model manipulated into requesting elevated tool permissions | Critical | Permission boundary layer mapping user authorization to tool allowlists; user role forwarded with tool calls; MCP Tool Server validates against permitted tool set |
| E-3 | MCP Tool Server | Standard users invoking administrative tool endpoints via parameter manipulation | Critical | RBAC policy on Tool Server mapping tools to permission sets; caller role validation; tool tier classification (read-only, write, administrative) |
| AG-1 | LLM Agent Orchestrator | Unbounded agent loop consuming API credits and generating cascading side effects | Critical | Maximum iteration count (25), execution timeout (120s), cost cap ($5/request), circuit breaker on repeated action patterns, human-in-the-loop for >10 tool calls |
| AG-3 | MCP Tool Server | All tools exposed without per-user capability scoping enabling unauthorized tool invocation | Critical | Per-caller tool allowlists, user authorization scope declaration, tool capability validation against permission set, audit logging |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection overriding system prompt and safety constraints | Critical | Structured prompt templates with delimiter tokens, input classifier for adversarial patterns, output filtering, jailbreak taxonomy monitoring |
| S-2 | Guardrails Service | Attacker bypasses Guardrails by directly addressing Orchestrator endpoint | High | Mutual TLS between Guardrails and Orchestrator; allowlist of trusted service identities at Orchestrator ingress |
| S-3 | LLM Agent Orchestrator | Forged service identity tokens impersonating Orchestrator to Tool Server | High | mTLS with certificate pinning, signed JWTs with RS256 and audience restriction |
| S-4 | MCP Tool Server | Spoofed Tool Server identity injecting fabricated tool results | High | Response signing (HMAC-SHA256) on all Tool Server responses; Orchestrator validates signatures before processing |
| T-1 | Guardrails Service | Tampering with validation rules to disable prompt screening | High | Immutable configuration store with SHA-256 checksums, drift detection, least-privilege access controls |
| T-2 | LLM Agent Orchestrator | Prompt tampered in transit between Guardrails and Orchestrator | High | Message-level HMAC-SHA256 integrity protection on forwarded prompts |
| T-3 | MCP Tool Server | Tool call parameters modified in transit over JSON-RPC | High | JSON-RPC message signing (HMAC-SHA256), strict parameter schema validation |
| T-5 | Audit Logger | Audit log entries tampered or deleted to cover tracks | High | Append-only immutable storage, external SIEM forwarding, cryptographic log chaining, read-only access restriction |
| R-1 | User | User denies submitting harmful prompt without non-repudiation evidence | High | Server-side identity binding with timestamp and session correlation ID; immutable audit records |
| I-1 | Guardrails Service | Detailed rejection reasons reveal internal filtering rules | High | Generic rejection messages to users; detailed reasons logged internally only; rate limiting on rejections |
| I-4 | Knowledge Base | Full document contents with internal metadata returned in query responses | High | Field-level projection on query responses; strip metadata, vectors, classifications; query-scoped access controls |
| I-5 | Audit Logger | Sensitive data in logs accessible to operations staff with overly broad access | High | Data classification and redaction on log entries; RBAC on log store; AES-256 encryption at rest |
| E-1 | Guardrails Service | Bypass vulnerability escalating from filtered to unfiltered user context | High | Role-based prompt filtering policies; server-side role validation; independent Orchestrator authorization check |
| AG-2 | LLM Agent Orchestrator | Consequential decisions made without human review or approval gates | High | Action reversibility tiers, pre-execution review for write/delete operations, approval decision logging |
| AG-4 | MCP Tool Server | Tool chaining escalates individually authorized operations beyond intended permissions | High | Tool chain policy engine evaluating composite effects; forbidden combination definitions; human approval for cross-boundary chains |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via poisoned RAG documents in Knowledge Base | High | Sanitize retrieved content, provenance tracking, content integrity checks, structural delimiters in prompt template |
| LLM-4 | LLM Agent Orchestrator | Knowledge Base content poisoning corrupting RAG responses | High | Content validation and adversarial detection before indexing, document-level access controls, provenance metadata, integrity audits |
| R-2 | Guardrails Service | Insufficient logging detail on prompt rejection decisions | Medium | Structured audit events with full prompt, rule matched, decision, reason, user ID, timestamp |
| R-4 | MCP Tool Server | Tool execution context not fully logged enabling denial of responsibility | Medium | Complete request chain logging with originating user ID, tool details, API response, correlation ID |
| I-3 | MCP Tool Server | Verbose error messages revealing internal stack traces and connection strings | Medium | Generic error responses; standardized error codes; detailed diagnostics routed to Audit Logger only |
| D-3 | MCP Tool Server | Excessive outbound API requests exhausting connection pools | Medium | Per-client tool invocation rate limits, connection pool limits and timeouts, circuit breaker, usage budget caps |
| D-4 | Knowledge Base | Resource-intensive vector search queries degrading performance | Medium | Query complexity limits, result set size caps, query timeout, per-client rate limiting, latency monitoring |
| D-5 | Audit Logger | Log flooding from high-volume requests filling storage capacity | Medium | Log volume rate limiting per source, automatic rotation and retention, storage capacity alerts, log sampling |
| LLM-3 | LLM Agent Orchestrator | Iterative prompt probing to extract system prompt and tool descriptions | Medium | Rate limiting per session, prompt classifier for extraction patterns, post-hoc prompt analysis, output classifiers for system prompt fragments |
| S-5 | External API | DNS spoofing redirecting HTTPS requests to malicious impersonation endpoint | Medium | Certificate pinning, strict hostname verification, DNS-over-HTTPS resolver, certificate change monitoring |
| LLM-5 | LLM Agent Orchestrator | Systematic querying to extract model behavior or distill model copy | Medium | Restrict to top-k output, per-API-key query budgets, query pattern analysis, output watermarking |
| R-5 | External API | External API denies receiving request without mutual logging | Low | Request/response logging on MCP Tool Server side, signed receipts where supported, immutable Audit Logger records |
| I-6 | Audit Logger | Internal log data flows intercepted due to lack of encryption | Low | TLS 1.3 encryption on all internal log flows, mutual TLS between logging clients and Audit Logger |
