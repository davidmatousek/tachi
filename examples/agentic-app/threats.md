---
schema_version: "1.1"
date: "2026-03-23"
input_format: "mermaid"
classification: "confidential"
---

# Threat Model Report

## 1. System Overview

Parsed summary of the agentic AI application architecture including identified components, data flows, and technologies. This system implements a multi-agent architecture with LLM-based orchestration, MCP tool execution, guardrails-based input filtering, and audit logging across three trust zones.

### Components

| Component | Type | Description |
|-----------|------|-------------|
| User | External Entity | End user submitting prompts and receiving responses via HTTPS |
| Guardrails Service | Process | Input validation and filtering service that screens user prompts before forwarding to orchestration |
| LLM Agent Orchestrator | Process | Central orchestration process that dispatches LLM inference, retrieves context from the knowledge base, and coordinates tool calls via MCP |
| MCP Tool Server | Process | Model Context Protocol server that executes tool calls on behalf of the orchestrator and interfaces with external APIs |
| Knowledge Base | Data Store | Vector database storing document embeddings for retrieval-augmented generation (RAG) context |
| Audit Logger | Data Store | Append-only log store capturing decision logs, tool execution events, and filtering events for accountability |
| External API | External Entity | Third-party API services accessed by the MCP Tool Server for external data and actions |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| User | Guardrails Service | Prompt / Query | HTTPS |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | Internal RPC |
| Guardrails Service | User | Rejected Prompt + Reason | HTTPS |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval Query | Vector Search |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | Vector Search |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | JSON-RPC |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | JSON-RPC |
| MCP Tool Server | External API | API Request | HTTPS |
| External API | MCP Tool Server | API Response | HTTPS |
| LLM Agent Orchestrator | User | Response | HTTPS |
| LLM Agent Orchestrator | Audit Logger | Decision Log Entry | Internal |
| MCP Tool Server | Audit Logger | Tool Execution Log | Internal |
| Guardrails Service | Audit Logger | Filtering Event Log | Internal |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Transport | HTTPS / TLS 1.3 | RFC 8446 |
| Agent Protocol | Model Context Protocol (MCP) | 2025.1 |
| RPC Format | JSON-RPC 2.0 | RFC pending |
| Vector Store | Vector database (pgvector) | unknown |
| Logging | Structured append-only log | unknown |
| Input Filtering | Guardrails framework | unknown |
| LLM Provider | LLM inference API | unknown |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| User Zone | Untrusted | User |
| Application Zone | Trusted | Guardrails Service, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger |
| External Services | Untrusted | External API |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| User-to-Application | User Zone | Application Zone | User -> Guardrails Service | TLS termination, input validation, prompt filtering, rate limiting |
| Application-to-User | Application Zone | User Zone | LLM Agent Orchestrator -> User | TLS encryption, output sanitization |
| Application-to-User (rejection) | Application Zone | User Zone | Guardrails Service -> User | TLS encryption, generic rejection messages |
| Application-to-External | Application Zone | External Services | MCP Tool Server -> External API | HTTPS with API key authentication, egress filtering |
| External-to-Application | External Services | Application Zone | External API -> MCP Tool Server | Response validation, schema enforcement |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

Threats where an attacker pretends to be something or someone else.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | User | Attacker spoofs a legitimate user identity by stealing or replaying session tokens to submit unauthorized prompts | MEDIUM | HIGH | High | Implement short-lived JWT tokens with refresh rotation; bind tokens to client fingerprint; enforce MFA for sensitive operations |
| S-2 | LLM Agent Orchestrator | Attacker crafts spoofed tool call responses that mimic the MCP Tool Server, injecting fabricated results into the orchestration pipeline | LOW | HIGH | Medium | Enforce mutual TLS between orchestrator and tool server; validate message signatures on all JSON-RPC responses; implement request-response correlation IDs |
| S-3 | External API | Compromised or spoofed external API returns malicious payloads masquerading as legitimate API responses | MEDIUM | MEDIUM | Medium | Validate API response schemas before processing; implement certificate pinning for critical external endpoints; use response integrity checksums where supported |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Knowledge Base | Attacker with write access to the vector store injects or modifies document embeddings, corrupting RAG retrieval results and influencing LLM output | MEDIUM | HIGH | High | Enforce strict write access controls on vector store; implement embedding integrity checksums; log all write operations with source attribution |
| T-2 | LLM Agent Orchestrator | Attacker tampers with orchestration configuration or intermediate state to alter agent decision logic, causing the orchestrator to produce incorrect tool call sequences or bypass safety checks | LOW | HIGH | Medium | Sign orchestration configuration at deployment; validate configuration integrity at startup; implement runtime state checksums on critical decision paths |
| T-3 | Audit Logger | Attacker with elevated access modifies or truncates audit log entries to conceal malicious activity or alter the forensic record | LOW | HIGH | Medium | Use append-only log storage with cryptographic chaining (hash chains); replicate logs to an immutable external store; enforce separate access controls for log writes vs. log administration |

### 3.3 Repudiation (R)

Threats where an attacker denies having performed an action without the system being able to prove otherwise.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | User | User denies submitting a harmful or policy-violating prompt because session logs lack sufficient attribution to tie the prompt to a specific authenticated identity | MEDIUM | MEDIUM | Medium | Log authenticated user identity, session ID, timestamp, and client IP for every prompt submission; retain logs for compliance-mandated retention period |
| R-2 | LLM Agent Orchestrator | Orchestrator makes autonomous multi-step decisions that cannot be attributed to a specific triggering prompt or user action because decision chain logging is incomplete | MEDIUM | HIGH | High | Log complete decision chains including triggering prompt, intermediate reasoning steps, tool calls issued, and final response; implement correlation IDs across the full request lifecycle |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | LLM Agent Orchestrator | Orchestrator leaks sensitive context from the knowledge base or prior conversation turns in its responses to the user, exposing confidential documents or other users' data | HIGH | HIGH | Critical | Implement output filtering to detect and redact sensitive data patterns before response delivery; enforce per-user context isolation; apply retrieval access controls in the knowledge base |
| I-2 | Knowledge Base | Unauthorized access to vector store contents exposes confidential document embeddings that can be reversed to reconstruct source document content | LOW | HIGH | Medium | Encrypt embeddings at rest; enforce role-based access controls on vector queries; implement query auditing; rate-limit bulk retrieval operations |
| I-3 | MCP Tool Server | Tool server includes API credentials, internal endpoint URLs, or stack traces in error responses returned to the orchestrator, which may propagate to the user | MEDIUM | MEDIUM | Medium | Implement structured error handling that returns generic error codes; log detailed diagnostics server-side only; scrub error responses of credentials and internal paths before returning to orchestrator |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access to the system.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | Guardrails Service | Attacker floods the guardrails service with complex prompts designed to maximize validation processing time, exhausting CPU and blocking legitimate requests | HIGH | MEDIUM | High | Enforce per-user and per-IP rate limiting; set maximum prompt length and complexity thresholds; implement request timeouts; deploy horizontal scaling with circuit breakers |
| D-2 | MCP Tool Server | Attacker triggers recursive or excessively long tool call chains through crafted prompts, exhausting tool server resources and causing cascading timeouts across the application | MEDIUM | HIGH | High | Enforce maximum tool call depth and chain length limits; set per-request resource budgets; implement circuit breakers on tool execution; monitor and alert on anomalous call patterns |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | LLM Agent Orchestrator | Orchestrator escalates its own tool permissions beyond the user's authorization level by dynamically requesting elevated scopes from the MCP Tool Server, accessing tools the invoking user is not authorized to use | MEDIUM | HIGH | High | Implement per-user permission scoping on all tool calls; validate tool permissions against user authorization at the tool server, not just the orchestrator; enforce least-privilege tool allowlists |
| E-2 | Guardrails Service | Attacker bypasses guardrails validation through prompt obfuscation techniques (encoding, unicode manipulation, payload splitting) to access restricted orchestrator capabilities | MEDIUM | HIGH | High | Layer multiple validation strategies (regex, semantic analysis, LLM-based classification); maintain an evolving bypass pattern database; implement defense-in-depth with secondary validation at the orchestrator |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

Threats arising from autonomous agent behavior, including uncontrolled tool use, excessive autonomy, and agent-to-agent trust violations.

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| AG-1 | LLM Agent Orchestrator | Orchestrator autonomously escalates its own action scope by chaining multiple tool calls into a privileged operation sequence that no single tool call would permit, bypassing per-tool authorization boundaries | ASI03 | MEDIUM | HIGH | High | Enforce cumulative permission budgets across tool call chains; require human-in-the-loop approval when cumulative scope exceeds single-tool authorization; implement chain-level authorization checks |
| AG-2 | MCP Tool Server | Attacker manipulates prompt context to cause the tool server to invoke tools outside the intended scope, executing unauthorized file system operations, network calls, or data mutations | ASI02 | MEDIUM | HIGH | High | Enforce strict tool allowlists with per-tool parameter validation; sandbox tool execution environments; implement input schema validation on all tool call parameters |
| AG-3 | LLM Agent Orchestrator | Orchestrator generates and executes multi-step plans without checkpoints, making irreversible changes across multiple tools before any human review occurs | ASI01 | LOW | HIGH | Medium | Require explicit human approval for multi-step plans; implement checkpoints between steps with rollback capability; enforce maximum autonomous step count |
| AG-4 | MCP Tool Server | Compromised or manipulated agent triggers excessive tool invocations in rapid succession, exhausting external API quotas, compute resources, and downstream service capacity | ASI02 | HIGH | MEDIUM | High | Enforce per-agent rate limits on tool invocations; set resource budgets per request; implement circuit breakers on external API calls; monitor and alert on tool call velocity anomalies |

### 4.2 LLM Threats (LLM)

Threats targeting the LLM itself, including prompt injection, training data poisoning, and insecure output handling.

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | LLM Agent Orchestrator | Indirect prompt injection via documents retrieved from the knowledge base causes the orchestrator to execute attacker-controlled instructions, exfiltrating sensitive context or invoking unauthorized tool calls | MCP10 | HIGH | HIGH | Critical | Sanitize all retrieved documents before inclusion in LLM context; implement instruction-data separation boundaries; apply output filtering to detect and block exfiltration patterns; deploy canary tokens in knowledge base |
| LLM-2 | LLM Agent Orchestrator | Attacker poisons knowledge base documents with adversarial content designed to persistently corrupt LLM reasoning, causing the orchestrator to consistently produce incorrect or malicious outputs for specific query patterns | MCP03 | LOW | HIGH | Medium | Implement document ingestion validation with content integrity checks; maintain provenance metadata for all knowledge base entries; deploy periodic automated testing against known-good query-response pairs; enable rollback of recent ingestion batches |
| LLM-3 | LLM Agent Orchestrator | Attacker crafts prompts that cause the LLM to generate tool call parameters containing injection payloads (SQL, shell commands, JSON-RPC manipulation) that execute on downstream systems through the MCP Tool Server | MCP05 | MEDIUM | HIGH | High | Validate and sanitize all LLM-generated tool call parameters before execution; enforce strict parameter schemas on the tool server; implement parameterized interfaces that prevent injection; log all tool call parameters for audit |

---

## 4a. Correlated Findings

Cross-agent correlation groups linking findings from different agent categories that target the same component for related threats. Each group represents a single underlying issue identified from multiple security perspectives. Original findings remain unchanged in their respective tables (Sections 3 and 4) — correlation groups are additive, not replacements.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-2, LLM-2 | LLM Agent Orchestrator | Tampering: unauthorized modification of orchestration configuration or intermediate state to alter decision logic; Data-Poisoning: adversarial corruption of knowledge base documents to persistently degrade orchestrator reasoning | Medium |
| CG-2 | E-1, AG-1 | LLM Agent Orchestrator | Privilege-Escalation: orchestrator escalates tool permissions beyond user authorization via dynamic scope requests; Agent-Autonomy: orchestrator chains tool calls into privileged operation sequences that bypass per-tool authorization | High |

---

## 5. Coverage Matrix

Cross-reference matrix showing which components were analyzed for which threat categories. Each cell uses a three-state model:

- **Integer**: Deduplicated finding count for that component-category pair. When findings belong to a correlation group, the group contributes 1 to the count collectively rather than individually.
- **`—`** (em dash): The component was analyzed for that category but no threats were found (analyzed but clean).
- **`n/a`**: The category does not apply to this component — it was not dispatched for analysis.

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| User | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Guardrails Service | — | — | — | — | 1 | 1 | n/a | n/a | 2 |
| LLM Agent Orchestrator | 1 | 1 | 1 | 1 | — | 1 | 2 | 3 | 10 |
| MCP Tool Server | — | — | — | 1 | 1 | — | 2 | n/a | 4 |
| Knowledge Base | n/a | 1 | n/a | 1 | — | n/a | n/a | n/a | 2 |
| Audit Logger | n/a | 1 | n/a | — | — | n/a | n/a | n/a | 1 |
| External API | 1 | n/a | — | n/a | n/a | n/a | n/a | n/a | 1 |
| **Total** | **3** | **3** | **2** | **3** | **2** | **2** | **4** | **3** | **22** |

Counts reflect deduplicated findings. 2 correlation groups merged 4 individual findings.

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
| Critical | 2 | 10.0% |
| High | 10 (11 raw) | 50.0% |
| Medium | 8 (9 raw) | 40.0% |
| Low | 0 | 0.0% |
| Note | 0 | 0.0% |
| **Total** | **20 (22 raw)** | **100%** |

---

## 7. Recommended Actions

Prioritized list of all findings sorted by risk level descending, providing a remediation roadmap. Critical and High findings should be addressed before deployment. Medium findings should be addressed within the current development cycle.

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| I-1 | LLM Agent Orchestrator | Context leakage exposing confidential documents or other users' data in responses | Critical | Implement output filtering to detect and redact sensitive data patterns; enforce per-user context isolation; apply retrieval access controls |
| LLM-1 | LLM Agent Orchestrator | Indirect prompt injection via retrieved documents exfiltrating context or invoking unauthorized tools | Critical | Sanitize retrieved documents before LLM context inclusion; implement instruction-data separation; deploy output filtering and canary tokens |
| S-1 | User | Spoofed user identity via stolen or replayed session tokens | High | Short-lived JWT tokens with refresh rotation; client fingerprint binding; MFA for sensitive operations |
| T-1 | Knowledge Base | Poisoned document embeddings corrupting RAG retrieval results | High | Strict write access controls on vector store; embedding integrity checksums; write operation logging |
| R-2 | LLM Agent Orchestrator | Autonomous multi-step decisions not attributable to specific user actions | High | Log complete decision chains with correlation IDs; capture triggering prompts, reasoning steps, and tool calls |
| D-1 | Guardrails Service | Resource exhaustion via complex prompt flooding | High | Per-user and per-IP rate limiting; prompt length and complexity thresholds; request timeouts; horizontal scaling |
| D-2 | MCP Tool Server | Recursive tool call chains exhausting resources and causing cascading timeouts | High | Maximum tool call depth and chain length limits; per-request resource budgets; circuit breakers |
| E-1 | LLM Agent Orchestrator | Orchestrator escalates tool permissions beyond user authorization | High | Per-user permission scoping on tool calls; server-side authorization at tool server; least-privilege allowlists |
| E-2 | Guardrails Service | Guardrails bypass via prompt obfuscation enabling access to restricted capabilities | High | Layered validation strategies; evolving bypass pattern database; defense-in-depth with secondary orchestrator validation |
| AG-1 | LLM Agent Orchestrator | Autonomous privilege escalation through chained tool calls bypassing per-tool authorization | High | Cumulative permission budgets; human-in-the-loop for scope escalation; chain-level authorization checks |
| AG-2 | MCP Tool Server | Unauthorized tool invocations executing file system, network, or data mutation operations | High | Strict tool allowlists; sandboxed execution; input schema validation on all tool call parameters |
| AG-4 | MCP Tool Server | Excessive tool invocations exhausting API quotas and downstream capacity | High | Per-agent rate limits; resource budgets per request; circuit breakers on external API calls |
| LLM-3 | LLM Agent Orchestrator | LLM-generated tool call parameters containing injection payloads targeting downstream systems | High | Validate and sanitize LLM-generated parameters; strict parameter schemas; parameterized interfaces; audit logging |
| S-2 | LLM Agent Orchestrator | Spoofed tool call responses injecting fabricated results into orchestration pipeline | Medium | Mutual TLS between orchestrator and tool server; message signatures; request-response correlation IDs |
| S-3 | External API | Spoofed external API returning malicious payloads | Medium | Response schema validation; certificate pinning; response integrity checksums |
| T-2 | LLM Agent Orchestrator | Tampered orchestration configuration altering agent decision logic | Medium | Signed configuration at deployment; integrity validation at startup; runtime state checksums |
| T-3 | Audit Logger | Modified or truncated audit log entries concealing malicious activity | Medium | Append-only storage with cryptographic hash chaining; immutable external replication; separate access controls |
| R-1 | User | User repudiates harmful prompts due to insufficient session attribution | Medium | Log user identity, session ID, timestamp, and client IP for all prompt submissions |
| I-2 | Knowledge Base | Unauthorized vector store access exposing reversible document embeddings | Medium | Encrypt embeddings at rest; role-based access controls; query auditing; rate-limit bulk retrieval |
| I-3 | MCP Tool Server | API credentials and internal paths exposed in tool server error responses | Medium | Structured error handling with generic error codes; server-side diagnostic logging; error response scrubbing |
| LLM-2 | LLM Agent Orchestrator | Knowledge base poisoning persistently corrupting LLM reasoning for specific queries | Medium | Document ingestion validation; provenance metadata; automated regression testing; ingestion batch rollback |
| AG-3 | LLM Agent Orchestrator | Uncontrolled multi-step plan execution making irreversible changes without human review | Medium | Human approval for multi-step plans; inter-step checkpoints with rollback; maximum autonomous step count |

---

## Appendix: OWASP Framework Cross-References

This appendix maps each finding to applicable OWASP framework categories across three classification systems: OWASP Top 10 Web 2025 (for STRIDE findings), OWASP Agentic Top 10 2026 (for AG findings), and OWASP MCP Top 10 2025 (for LLM findings targeting MCP-related threats).

| Finding ID | OWASP Category | Category Name | Notes |
|------------|----------------|---------------|-------|
| S-1 | A07 | Authentication Failures | Stolen/replayed session tokens exploiting weak authentication controls |
| S-2 | A08 | Software or Data Integrity Failures | Spoofed inter-service responses lacking integrity verification |
| S-3 | A08 | Software or Data Integrity Failures | Unvalidated external API responses accepted without integrity checks |
| T-1 | A08 | Software or Data Integrity Failures | Knowledge base write operations lacking integrity validation |
| T-2 | A02 | Security Misconfiguration | Orchestration configuration vulnerable to unauthorized modification |
| T-3 | A09 | Security Logging and Alerting Failures | Audit log integrity not protected with cryptographic controls |
| R-1 | A09 | Security Logging and Alerting Failures | Insufficient session attribution in prompt submission logs |
| R-2 | A09 | Security Logging and Alerting Failures | Incomplete decision chain logging for autonomous agent actions |
| I-1 | A01 | Broken Access Control | Cross-user context leakage due to insufficient access controls on retrieval |
| I-2 | A01 | Broken Access Control | Unauthorized access to vector store contents |
| I-3 | A04 | Cryptographic Failures | Credentials and internal paths exposed in unencrypted error responses |
| D-1 | A06 | Insecure Design | No resource consumption limits on prompt validation processing |
| D-2 | A06 | Insecure Design | Unbounded recursive tool call chains by design |
| E-1 | A01 | Broken Access Control | Dynamic privilege escalation bypassing user-level authorization |
| E-2 | A05 | Injection | Prompt obfuscation bypassing input validation via encoding techniques |
| AG-1 | ASI03 | Identity and Privilege Abuse | Agent chains tool calls to accumulate privileges beyond any single tool authorization |
| AG-2 | ASI02 | Tool Misuse and Exploitation | Tool server executes unauthorized operations via manipulated tool call parameters |
| AG-3 | ASI01 | Agent Goal Hijack | Agent executes multi-step plans without human oversight, deviating from intended goals |
| AG-4 | ASI02 | Tool Misuse and Exploitation | Excessive tool invocations exhausting resources through uncontrolled agent behavior |
| LLM-1 | MCP10 | Context Injection and Over-Sharing | Indirect prompt injection through retrieved documents injected into LLM context |
| LLM-2 | MCP03 | Tool Poisoning | Adversarial content in knowledge base persistently corrupting tool-mediated LLM reasoning |
| LLM-3 | MCP05 | Command Injection and Execution | LLM-generated tool parameters containing injection payloads targeting downstream execution |
