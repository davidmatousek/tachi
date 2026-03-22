# Threat Model Report

---

```yaml
---
schema_version: "1.0"
date: "2026-03-21"
input_format: "mermaid"
classification: "confidential"
---
```

---

## 1. System Overview

Parsed summary of the Mermaid flowchart architecture input for an agentic AI application with LLM orchestration, tool execution via MCP, RAG-based knowledge retrieval, and external API integration.

### Components

| Component | Type | Description |
|-----------|------|-------------|
| User | External Entity | End user who sends prompts and queries to the agentic application and receives responses |
| LLM Agent Orchestrator | Process | Central orchestration layer that receives user prompts, retrieves context from the knowledge base, dispatches tool calls to the MCP Tool Server, and generates responses using an LLM |
| MCP Tool Server | Process | Model Context Protocol server that executes tool calls requested by the orchestrator and interfaces with external APIs |
| Knowledge Base | Data Store | Document store used for retrieval-augmented generation (RAG), providing context documents to the orchestrator |
| External API | External Entity | Third-party service called by the MCP Tool Server to fulfill tool execution requests |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| User | LLM Agent Orchestrator | Prompt / Query | HTTPS |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval | Internal |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | Internal |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | Internal (MCP) |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | Internal (MCP) |
| MCP Tool Server | External API | API Request | HTTPS |
| External API | MCP Tool Server | API Response | HTTPS |
| LLM Agent Orchestrator | User | Response | HTTPS |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Protocol | Model Context Protocol (MCP) | unknown |
| Architecture | Retrieval-Augmented Generation (RAG) | unknown |
| Interface | LLM Agent Orchestration | unknown |
| Integration | External REST API | unknown |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| User Zone | Untrusted | User |
| Application Zone | Trusted | LLM Agent Orchestrator, MCP Tool Server, Knowledge Base |
| External Services | Untrusted | External API |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| User-to-Application | User Zone | Application Zone | User -> LLM Agent Orchestrator | Input validation, authentication, rate limiting |
| Application-to-External | Application Zone | External Services | MCP Tool Server -> External API | API key authentication, egress filtering, response validation |
| Application-to-User | Application Zone | User Zone | LLM Agent Orchestrator -> User | Output filtering, response sanitization |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | User | Attacker impersonates a legitimate user by replaying or forging authentication credentials to submit malicious prompts to the orchestrator | MEDIUM | HIGH | High | Implement multi-factor authentication and session-bound tokens with short expiry; validate user identity on every request |
| S-2 | External API | Attacker performs DNS hijacking or certificate spoofing to redirect MCP Tool Server API requests to a malicious endpoint that returns crafted responses | LOW | HIGH | Medium | Enforce certificate pinning for external API connections; validate TLS certificates and implement mutual authentication where supported |

### 3.2 Tampering (T)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | LLM Agent Orchestrator | Attacker intercepts and modifies tool call requests between the orchestrator and MCP Tool Server, altering parameters to execute unintended operations | LOW | HIGH | Medium | Enforce authenticated and integrity-protected communication channels between orchestrator and tool server; sign tool call payloads |
| T-2 | Knowledge Base | Attacker with write access modifies stored documents to inject misleading or adversarial content that corrupts RAG retrieval results | MEDIUM | HIGH | High | Implement access controls and mandatory review workflows for document modifications; maintain versioned snapshots with integrity checksums |

### 3.3 Repudiation (R)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | User | User denies submitting a prompt that triggered a harmful or costly tool execution, and the system lacks sufficient audit trail to prove the action | MEDIUM | MEDIUM | Medium | Implement immutable audit logging of all user prompts with session ID, timestamp, IP address, and user identity; retain logs for compliance period |
| R-2 | LLM Agent Orchestrator | Orchestrator executes a chain of tool calls with no record of the reasoning or decision path that led to each invocation, making post-incident analysis impossible | MEDIUM | MEDIUM | Medium | Log all orchestrator decisions including LLM reasoning traces, tool selection rationale, and intermediate outputs with correlation IDs |

### 3.4 Information Disclosure (I)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | Knowledge Base | Sensitive documents stored in the knowledge base are retrieved and included in responses to unauthorized users who craft queries targeting protected content | MEDIUM | HIGH | High | Implement document-level access controls in the knowledge base; filter retrieved documents by user authorization level before injecting into LLM context |
| I-2 | LLM Agent Orchestrator | System prompt containing internal instructions, API endpoints, or business logic is extracted by a user through crafted meta-instruction queries | HIGH | MEDIUM | High | Avoid embedding sensitive information in system prompts; implement output filtering to detect and block system prompt leakage patterns |

### 3.5 Denial of Service (D)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | LLM Agent Orchestrator | Attacker submits computationally expensive prompts that consume excessive LLM inference tokens and processing time, degrading service for legitimate users | HIGH | MEDIUM | High | Enforce per-user rate limiting and token budget caps; implement request timeout enforcement and queue management with priority levels |
| D-2 | Knowledge Base | Attacker floods the knowledge base with large volumes of documents, exhausting storage capacity and degrading retrieval performance for all users | MEDIUM | MEDIUM | Medium | Implement storage quotas and document size limits; enforce write-access controls and rate limiting on document ingestion |

### 3.6 Elevation of Privilege (E)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | LLM Agent Orchestrator | Attacker escalates from a standard user role to administrative capabilities by manipulating the orchestrator into executing privileged tool calls through crafted prompts | MEDIUM | HIGH | High | Enforce role-based access controls on tool invocation; validate user authorization level before dispatching each tool call regardless of LLM output |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| AG-1 | LLM Agent Orchestrator | Orchestrator autonomously executes multi-step tool call chains including data modifications and external API calls without requiring human approval for consequential actions. No distinction exists between low-stakes read operations and high-stakes write or delete operations, enabling the orchestrator to take irreversible actions based solely on LLM reasoning. | ASI-01 | HIGH | HIGH | Critical | Classify all tool operations into risk tiers: Tier 1 (read-only, auto-approve), Tier 2 (reversible writes, require confirmation), Tier 3 (irreversible or external actions, require human approval). Implement mandatory human-in-the-loop checkpoints before Tier 2 and Tier 3 operations. Add maximum iteration limits and execution timeouts on orchestrator loops. |
| AG-2 | MCP Tool Server | MCP Tool Server exposes all registered tools to the orchestrator without per-session capability scoping. The orchestrator can invoke any tool available on the server regardless of the user's authorization level or the current task's requirements. An attacker who achieves prompt injection can leverage this unrestricted access to invoke tools outside the intended operation scope. | MCP-03 | HIGH | HIGH | Critical | Implement per-session tool allowlists at the MCP Tool Server level scoped to the current user's role and the active task context. Enforce tool invocation authorization checks that validate each call against the user's permission set. Log all tool invocations with caller identity and user context for audit. |
| AG-3 | MCP Tool Server | MCP Tool Server forwards tool call parameters constructed from LLM output directly to the External API without parameter validation or sanitization. An attacker can manipulate the orchestrator via prompt injection to craft tool calls with malicious parameters (SQL fragments, shell commands, path traversal) that the External API processes as trusted input. | MCP-03 | MEDIUM | HIGH | High | Enforce strict parameter schema validation at the MCP Tool Server for every tool call before execution. Validate all parameters against declared types, ranges, and patterns. Reject tool calls with parameters that do not conform to the registered tool schema. Implement an output classifier on LLM-generated tool calls to detect suspicious parameter patterns. |
| AG-4 | LLM Agent Orchestrator | Orchestrator enters an unbounded reasoning-action loop where the LLM repeatedly determines that the task is incomplete and issues additional tool calls. Without maximum iteration count, execution timeout, or cost cap, the loop consumes unbounded API credits and compute resources while potentially generating cascading side effects through repeated tool invocations. | ASI-01 | MEDIUM | MEDIUM | Medium | Implement mandatory termination constraints: maximum iteration count (e.g., 25 iterations), execution timeout (e.g., 5 minutes), and cumulative cost cap per session. Add a circuit breaker that halts execution if the orchestrator repeats the same action pattern for 3 consecutive iterations. Log each iteration with action taken for post-hoc analysis. |

### 4.2 LLM Threats (LLM)

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | LLM Agent Orchestrator | User submits a prompt containing adversarial instructions that override the orchestrator's system prompt. The injected instructions cause the orchestrator to exfiltrate sensitive data from retrieved knowledge base documents or system configuration by encoding it in tool call parameters sent to the External API. Direct injection succeeds because user input is concatenated into the LLM context without boundary enforcement or input classification. | OWASP LLM01:2025 | HIGH | HIGH | Critical | Implement structured prompt templates with explicit delimiter tokens between system instructions and user input. Deploy an input classifier that detects adversarial prompt patterns before forwarding to the LLM. Apply output filtering to detect tool calls that contain data patterns matching exfiltration (encoded data, URLs, email addresses). Enforce egress network controls limiting external API request payloads. |
| LLM-2 | LLM Agent Orchestrator | Adversarial instructions embedded in documents stored in the Knowledge Base are retrieved during RAG and injected into the orchestrator's context window. The poisoned context causes the orchestrator to ignore its system prompt, execute unauthorized tool calls, or generate responses containing attacker-controlled content. Indirect injection succeeds because retrieved documents enter the LLM context without content sanitization. | OWASP LLM01:2025 | MEDIUM | HIGH | High | Sanitize retrieved document content before injection into the prompt context. Implement provenance tracking so the LLM can distinguish system instructions from retrieved content. Apply content integrity checks on documents before indexing. Monitor retrieval patterns for anomalous document frequency spikes that may indicate poisoning. |
| LLM-3 | Knowledge Base | Attacker with document upload access poisons the knowledge base by inserting documents containing factually incorrect, misleading, or adversarially crafted content. These documents rank highly for targeted queries due to embedding similarity, causing the RAG pipeline to consistently retrieve and present attacker-controlled information as authoritative answers across all user sessions. | OWASP LLM03:2025 | MEDIUM | HIGH | High | Implement content validation and adversarial content detection on all documents before indexing. Apply document-level access controls restricting write access to authorized roles. Add provenance metadata to indexed documents tracking author, source, and review status. Establish a document review workflow requiring approval before new content enters the retrieval index. |
| LLM-4 | LLM Agent Orchestrator | Attacker systematically queries the orchestrator API to extract proprietary model configuration, fine-tuning data, or system prompt contents. The orchestrator API lacks per-user query volume limits and returns responses with sufficient detail to reconstruct model behavior through distillation. Error messages from the orchestrator reveal model framework version and parameter details. | OWASP LLM10:2025 | LOW | HIGH | Medium | Restrict API output to essential response content only. Implement per-user query budgets with alerts at threshold crossings. Deploy query pattern analysis that detects systematic probing. Implement generic error responses that do not expose model architecture details. Add rate limiting on prompt submissions per user session. |

---

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| User | 1 |  | 1 |  |  |  |  |  | 2 |
| LLM Agent Orchestrator | - | 1 | 1 | 1 | 1 | 1 | 2 | 3 | 10 |
| MCP Tool Server | - | - | - | - | - | - | 2 |  | 2 |
| Knowledge Base |  | 1 |  | 1 | 1 |  |  | 1 | 4 |
| External API | 1 |  | - |  |  |  |  |  | 1 |
| **Total** | **2** | **2** | **2** | **2** | **2** | **1** | **4** | **4** | **19** |

---

## 6. Risk Summary

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 3 | 15.8% |
| High | 9 | 47.4% |
| Medium | 7 | 36.8% |
| Low | 0 | 0% |
| Note | 0 | 0% |
| **Total** | **19** | **100%** |

---

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| AG-1 | LLM Agent Orchestrator | Autonomous execution of consequential tool calls without human approval | Critical | Classify tool operations into risk tiers; require human approval for irreversible and external actions; add iteration limits and timeouts |
| AG-2 | MCP Tool Server | Unrestricted tool access without per-session capability scoping | Critical | Implement per-session tool allowlists scoped to user role and task context; enforce per-call authorization checks |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection causing data exfiltration via tool calls | Critical | Structured prompt templates with boundary delimiters; input classifier for adversarial patterns; output filtering for exfiltration indicators; egress controls |
| S-1 | User | Authentication credential replay or forgery for user impersonation | High | Multi-factor authentication; session-bound tokens with short expiry |
| T-2 | Knowledge Base | Unauthorized document modification corrupting RAG retrieval | High | Access controls; mandatory review workflows; versioned snapshots with integrity checksums |
| I-1 | Knowledge Base | Sensitive document retrieval by unauthorized users | High | Document-level access controls; filter retrieved documents by user authorization before LLM context injection |
| I-2 | LLM Agent Orchestrator | System prompt extraction via crafted meta-instruction queries | High | Avoid sensitive data in system prompts; output filtering for prompt leakage patterns |
| D-1 | LLM Agent Orchestrator | Resource exhaustion via computationally expensive prompts | High | Per-user rate limiting; token budget caps; request timeouts; queue management |
| E-1 | LLM Agent Orchestrator | Privilege escalation via prompt-manipulated tool calls | High | Role-based access controls on tool invocation; validate user authorization before each tool dispatch |
| AG-3 | MCP Tool Server | Unsanitized tool call parameters forwarded to External API | High | Strict parameter schema validation; type and pattern checks; output classifier on LLM-generated tool calls |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via poisoned RAG documents | High | Sanitize retrieved content; provenance tracking; content integrity checks; retrieval monitoring |
| LLM-3 | Knowledge Base | Knowledge base poisoning with adversarial documents | High | Content validation before indexing; write-access restrictions; provenance metadata; document review workflow |
| T-1 | LLM Agent Orchestrator | Tool call request tampering between orchestrator and tool server | Medium | Authenticated communication channels; signed tool call payloads |
| S-2 | External API | DNS hijacking or certificate spoofing on external API connection | Medium | Certificate pinning; TLS certificate validation; mutual authentication |
| R-1 | User | Repudiation of prompts that triggered costly tool executions | Medium | Immutable audit logging of all prompts with session context |
| R-2 | LLM Agent Orchestrator | Missing decision audit trail for tool call chains | Medium | Log reasoning traces, tool selection rationale, and intermediate outputs with correlation IDs |
| D-2 | Knowledge Base | Storage exhaustion via document flooding | Medium | Storage quotas; document size limits; write-access rate limiting |
| AG-4 | LLM Agent Orchestrator | Unbounded reasoning-action loop consuming resources | Medium | Maximum iteration count; execution timeout; cost cap; circuit breaker for repeated action patterns |
| LLM-4 | LLM Agent Orchestrator | Model configuration extraction via systematic querying | Medium | Restrict output content; per-user query budgets; query pattern analysis; generic error responses |
