---
schema_version: "1.4"
date: "2026-04-16"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-16T12-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
has_attack_chains: true
has_agentic_patterns: true
---

# Threat Model — Healthcare Clinical Decision Support System (CDSS)

> **DISCLAIMER**: This is a security reference scenario for threat-modeling teaching purposes only. It is NOT a real clinical system and contains NO real patient data. Nothing herein constitutes medical advice, regulatory guidance, or a compliance framework recommendation.

---

## Section 1: System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Physician | External Entity | External physician user sending clinical queries via HTTPS and receiving recommendation views |
| Patient | External Entity | External patient providing EHR update events to the ingestion queue |
| Physician Clinical Portal | Process | Physician-facing web interface and user portal serving the clinical recommendation view; routes queries to Supervisor Orchestrator and enforces RBAC access decisions |
| Patient Summary Generator | Process | API endpoint generating patient-facing summaries from Supervisor Orchestrator recommendations for consumption by Patient |
| Inter-Agent Communication Channel | Process | Agent-to-agent message bus relaying delegation messages and specialist results between Supervisor Orchestrator, Diagnostic Agent, and Treatment Planner Agent; logs all inter-agent messages to Clinical Audit Log |
| Supervisor Orchestrator | Process | Supervisory orchestrator agent directing specialist agents via cascading delegation; produces emergent coordination patterns; dispatches inference to Model Inference API Gateway; writes decision logs to Clinical Audit Log; receives model updates from Outcomes Telemetry |
| Diagnostic Agent | Process | Autonomous clinical-reasoning executor performing tool dispatch over Clinical MCP Tool Server; coordinates with Treatment Planner Agent via Inter-Agent Communication Channel; queries Clinical Guideline RAG Corpus; requests risk inference via Model Inference API Gateway |
| Treatment Planner Agent | Process | Autonomous treatment-planning agent joining Supervisor-delegated tasks via Inter-Agent Communication Channel; queries Medical Literature Vector Index; dispatches tool calls via Clinical MCP Tool Server |
| Clinical MCP Tool Server | Process | MCP Tool Server providing JSON-RPC tool calls to Diagnostic Agent and Treatment Planner Agent; performs FHIR read/write on FHIR Resource Store |
| Clinical LLM | Process | Foundation language model inference endpoint for clinical reasoning; frozen base model with prompt-based adaptation; receives completion requests forwarded by Model Inference API Gateway |
| Risk Stratification Model | Process | Fine-tuned language model for patient risk stratification; foundation model adapted via supervised fine-tuning on de-identified historical cohorts; exposes an inference engine endpoint via Model Inference API Gateway |
| FHIR Resource Store | Data Store | Clinical FHIR resource database and cache storing structured patient records; accessed by Supervisor Orchestrator and Clinical MCP Tool Server; PHI read/write gated by Consent and De-identification Guardrail |
| Clinical Guideline RAG Corpus | Data Store | Retrieval-augmented generation corpus of clinical practice guidelines with dense embeddings and a vector store for semantic retrieval; queried by Diagnostic Agent |
| Medical Literature Vector Index | Data Store | Vector index of medical literature for semantic retrieval by Treatment Planner Agent |
| Model Inference API Gateway | Process | API gateway container fronting the Clinical LLM and Risk Stratification Model inference endpoints; forwards inference requests from Supervisor Orchestrator and Diagnostic Agent |
| EHR Ingestion Queue | Data Store | Queue buffering EHR update events from Patient before normalization into FHIR Resource Store |
| Clinical Audit Log | Data Store | Audit log receiving decision log entries from Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, and Inter-Agent Communication Channel; feeds Outcomes Telemetry observability stream |
| Outcomes Telemetry and Physician Override Audit Store | Data Store | Long-running learning loop and feedback loop carrier for continual learning against physician-override telemetry; monitors outcome drift; feeds periodic model update re-training signals to Supervisor Orchestrator and Clinical LLM |
| HIPAA RBAC + Policy Engine | Process | RBAC and policy engine enforcing HIPAA access control; issues access decisions to Physician Clinical Portal and compliance check decisions to Supervisor Orchestrator; logs policy events to Clinical Audit Log |
| Consent and De-identification Guardrail | Process | Guardrail enforcing patient consent and de-identification with encryption controls on PHI read/write paths on FHIR Resource Store |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Physician | Physician Clinical Portal | Clinical query | HTTPS |
| Physician Clinical Portal | Supervisor Orchestrator | Authenticated clinical intent | Internal API |
| Supervisor Orchestrator | Physician Clinical Portal | Clinical recommendation response | Internal API |
| Physician Clinical Portal | Physician | Recommendation view | HTTPS |
| Patient | EHR Ingestion Queue | EHR update event | Internal |
| EHR Ingestion Queue | FHIR Resource Store | Normalized patient record | Internal |
| FHIR Resource Store | Supervisor Orchestrator | Clinical context retrieval | Internal |
| Supervisor Orchestrator | Inter-Agent Communication Channel | Delegation message (cross-agent coordinate) | Internal |
| Inter-Agent Communication Channel | Diagnostic Agent | Delegated diagnostic task (inter-agent coordinate) | Internal |
| Diagnostic Agent | Inter-Agent Communication Channel | Specialist diagnostic result (joint reasoning) | Internal |
| Inter-Agent Communication Channel | Treatment Planner Agent | Delegated treatment task (inter-agent coordinate) | Internal |
| Treatment Planner Agent | Inter-Agent Communication Channel | Treatment plan (joint reasoning) | Internal |
| Inter-Agent Communication Channel | Supervisor Orchestrator | Aggregated specialist output | Internal |
| Supervisor Orchestrator | Model Inference API Gateway | Inference request | Internal |
| Model Inference API Gateway | Clinical LLM | Inference request forwarded | Internal |
| Clinical LLM | Model Inference API Gateway | Completion | Internal |
| Model Inference API Gateway | Supervisor Orchestrator | Completion forwarded | Internal |
| Diagnostic Agent | Model Inference API Gateway | Risk inference request | Internal |
| Model Inference API Gateway | Risk Stratification Model | Risk inference request | Internal |
| Risk Stratification Model | Model Inference API Gateway | Stratification output | Internal |
| Model Inference API Gateway | Diagnostic Agent | Stratification output | Internal |
| Diagnostic Agent | Clinical Guideline RAG Corpus | Guideline retrieval query | Internal |
| Clinical Guideline RAG Corpus | Diagnostic Agent | Retrieved guidelines | Internal |
| Treatment Planner Agent | Medical Literature Vector Index | Literature retrieval query | Internal |
| Medical Literature Vector Index | Treatment Planner Agent | Retrieved literature | Internal |
| Diagnostic Agent | Clinical MCP Tool Server | Tool call (JSON-RPC) | JSON-RPC |
| Treatment Planner Agent | Clinical MCP Tool Server | Tool call (JSON-RPC) | JSON-RPC |
| Clinical MCP Tool Server | Diagnostic Agent | Tool result | Internal |
| Clinical MCP Tool Server | Treatment Planner Agent | Tool result | Internal |
| Clinical MCP Tool Server | FHIR Resource Store | FHIR read/write | Internal |
| Physician Clinical Portal | HIPAA RBAC + Policy Engine | Access request | Internal |
| HIPAA RBAC + Policy Engine | Physician Clinical Portal | Access decision | Internal |
| Supervisor Orchestrator | HIPAA RBAC + Policy Engine | Compliance check | Internal |
| FHIR Resource Store | Consent and De-identification Guardrail | PHI read/write | Internal |
| Consent and De-identification Guardrail | FHIR Resource Store | De-identified PHI | Internal |
| Supervisor Orchestrator | Clinical Audit Log | Decision log entry | Internal |
| Diagnostic Agent | Clinical Audit Log | Decision log entry | Internal |
| Treatment Planner Agent | Clinical Audit Log | Decision log entry | Internal |
| Inter-Agent Communication Channel | Clinical Audit Log | Inter-agent message log | Internal |
| HIPAA RBAC + Policy Engine | Clinical Audit Log | Policy event log | Internal |
| Clinical Audit Log | Outcomes Telemetry and Physician Override Audit Store | Observability stream | Internal |
| Outcomes Telemetry and Physician Override Audit Store | Supervisor Orchestrator | Periodic model update (learning loop re-training) | Internal |
| Outcomes Telemetry and Physician Override Audit Store | Clinical LLM | Periodic model update (feedback loop drift correction) | Internal |
| Supervisor Orchestrator | Patient Summary Generator | Summary request | Internal |
| Patient Summary Generator | Patient | Patient-facing summary | HTTPS |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Architecture Format | Mermaid Flowchart | Unknown |
| Clinical Data Standard | HL7 FHIR | Unknown |
| Protocol | JSON-RPC | 2.0 |
| Transport | HTTPS/TLS | Unknown |
| AI Framework | Multi-agent supervisor-specialist delegation | Unknown |
| AI Pattern | Retrieval-Augmented Generation (RAG) | Unknown |
| Regulatory | HIPAA RBAC and Policy Engine | Unknown |
| Data Store | Vector index (medical literature) | Unknown |
| Data Store | Clinical FHIR database/cache | Unknown |
| AI Model | Foundation LLM (clinical reasoning) | Unknown |
| AI Model | Fine-tuned risk stratification model | Unknown |
| Infrastructure | API Gateway (model inference) | Unknown |
| Infrastructure | Ingestion queue (EHR events) | Unknown |
| Observability | Audit log and telemetry store | Unknown |
| Security | Consent and de-identification guardrail | Unknown |

---

## Section 2: Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| External Zone | Untrusted | Physician, Patient |
| User Interface Zone (L7) | Semi-Trusted | Physician Clinical Portal, Patient Summary Generator |
| Agent Ecosystem Zone (L7) | Semi-Trusted | Inter-Agent Communication Channel |
| Agent Frameworks Zone (L3) | Trusted | Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Clinical MCP Tool Server |
| Foundation Models Zone (L1) | Trusted | Clinical LLM, Risk Stratification Model |
| Data Operations Zone (L2) | Trusted | FHIR Resource Store, Clinical Guideline RAG Corpus, Medical Literature Vector Index |
| Deployment Infrastructure Zone (L4) | Trusted | Model Inference API Gateway, EHR Ingestion Queue |
| Evaluation and Observability Zone (L5) | Trusted | Clinical Audit Log, Outcomes Telemetry and Physician Override Audit Store |
| Security and Compliance Zone (L6) | Trusted | HIPAA RBAC + Policy Engine, Consent and De-identification Guardrail |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Physician → Portal | External Zone | User Interface Zone | Physician → Physician Clinical Portal | TLS encryption, HTTPS |
| Patient → EHR Queue | External Zone | Deployment Infrastructure Zone | Patient → EHR Ingestion Queue | TLS encryption |
| Portal → Agent Zone | User Interface Zone | Agent Frameworks Zone | Physician Clinical Portal → Supervisor Orchestrator | RBAC access decision from HIPAA RBAC + Policy Engine |
| Portal → Security Layer | User Interface Zone | Security and Compliance Zone | Physician Clinical Portal → HIPAA RBAC + Policy Engine | Internal API call |
| Inter-Agent → Agent Zone | Agent Ecosystem Zone | Agent Frameworks Zone | Inter-Agent Communication Channel → Diagnostic Agent, Treatment Planner Agent | Internal channel (no external TLS) |
| Agent → Data Zone | Agent Frameworks Zone | Data Operations Zone | Supervisor Orchestrator → FHIR Resource Store, Diagnostic Agent → Clinical Guideline RAG Corpus, Treatment Planner Agent → Medical Literature Vector Index | Internal API |
| Agent → Infra Zone | Agent Frameworks Zone | Deployment Infrastructure Zone | Supervisor Orchestrator → Model Inference API Gateway, Diagnostic Agent → Model Inference API Gateway | Internal API |
| Agent → Security Layer | Agent Frameworks Zone | Security and Compliance Zone | Supervisor Orchestrator → HIPAA RBAC + Policy Engine | Compliance check |
| Data → Security Layer | Data Operations Zone | Security and Compliance Zone | FHIR Resource Store → Consent and De-identification Guardrail | PHI de-identification |
| Agent → Observability Zone | Agent Frameworks Zone | Evaluation and Observability Zone | Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent → Clinical Audit Log | Decision log writes |
| Observability → Foundation Zone | Evaluation and Observability Zone | Foundation Models Zone | Outcomes Telemetry → Clinical LLM | Feedback loop model update |
| Observability → Agent Zone | Evaluation and Observability Zone | Agent Frameworks Zone | Outcomes Telemetry → Supervisor Orchestrator | Learning loop re-training signal |
| Portal → Patient Output | User Interface Zone | External Zone | Patient Summary Generator → Patient | HTTPS |

---

## Section 3: STRIDE Threat Tables

### 3.1 Spoofing (S)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|------------|--------|------------|------------|
| S-1 | Physician | L7 — Agent Ecosystem | — | An attacker may impersonate a legitimate physician by replaying or forging clinical query credentials, gaining unauthorized access to clinical recommendation views and patient data. | HIGH | HIGH | Critical | Implement mutual TLS authentication and short-lived signed JWT tokens with physician identity binding. Enforce step-up authentication for high-sensitivity clinical queries. |
| S-2 | Patient | L7 — Agent Ecosystem | — | An attacker may submit fraudulent EHR update events by spoofing a patient identity, injecting false patient records into the ingestion pipeline. | MEDIUM | HIGH | High | Validate EHR update events against an authoritative patient identity registry before enqueuing. Use cryptographic patient identity tokens on all ingestion events. |
| S-3 | Physician Clinical Portal | L7 — Agent Ecosystem | — | An attacker may spoof the Physician Clinical Portal to intercept clinical recommendation responses from the Supervisor Orchestrator, receiving sensitive patient data intended for legitimate physicians. | MEDIUM | HIGH | High | Enforce server certificate pinning and signed response tokens. Validate portal origin on all supervisor-to-portal responses. |
| S-4 | Patient Summary Generator | L7 — Agent Ecosystem | — | An attacker may spoof the Patient Summary Generator endpoint to intercept patient-facing summaries containing sensitive clinical recommendations. | MEDIUM | MEDIUM | Medium | Enforce HTTPS with TLS certificate validation. Require signed summary payloads to prevent interception and tampering. |
| S-5 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | trust_exploitation | An attacker who gains access to the inter-agent message bus may spoof supervisor delegation messages, causing specialist agents to act on forged orchestration commands. | HIGH | HIGH | Critical | Authenticate all inter-agent messages with HMAC signatures using per-session keys. Implement message source validation before specialist agents process delegation commands. |
| S-6 | Supervisor Orchestrator | L3 — Agent Framework | trust_exploitation | An attacker may impersonate the Supervisor Orchestrator to issue unauthorized delegation commands to specialist agents, bypassing orchestration controls and routing fabricated clinical tasks. | HIGH | HIGH | Critical | Require cryptographic attestation of supervisor identity on all delegation messages. Implement zero-trust peer authentication between orchestrator and specialist agents. |
| S-7 | Diagnostic Agent | L3 — Agent Framework | trust_exploitation | An attacker may spoof the Diagnostic Agent's identity to inject fraudulent diagnostic results into the Inter-Agent Communication Channel, polluting the treatment planning process. | MEDIUM | HIGH | High | Sign all inter-agent result messages with agent-specific identity keys. Implement result origin validation at the Inter-Agent Communication Channel before forwarding to other specialists. |
| S-8 | Treatment Planner Agent | L3 — Agent Framework | trust_exploitation | An attacker may spoof Treatment Planner Agent responses to inject malicious treatment plans into the inter-agent coordination flow. | MEDIUM | HIGH | High | Sign all treatment plan outputs with agent-specific identity keys. Implement origin verification at the Inter-Agent Communication Channel before delivery to Supervisor Orchestrator. |
| S-9 | Clinical MCP Tool Server | L3 — Agent Framework | — | An attacker may spoof the Clinical MCP Tool Server to return malicious tool results to Diagnostic Agent or Treatment Planner Agent, corrupting clinical decision inputs. | MEDIUM | HIGH | High | Authenticate MCP Tool Server responses with server-side identity tokens. Implement response integrity checks on agent-side before consuming tool results. |
| S-10 | Clinical LLM | L1 — Foundation Model | — | An attacker may spoof Clinical LLM completion responses by intercepting the API Gateway channel, returning fabricated clinical reasoning outputs. | LOW | HIGH | Medium | Enforce TLS with mutual authentication on the API Gateway to Clinical LLM path. Implement response integrity signatures for all completion payloads. |
| S-11 | Risk Stratification Model | L1 — Foundation Model | — | An attacker may spoof Risk Stratification Model outputs to inject false risk stratification results, causing the Diagnostic Agent to base decisions on falsified patient risk levels. | LOW | HIGH | Medium | Sign all risk stratification outputs with model service credentials. Implement Diagnostic Agent-side signature verification before consuming risk scores. |
| S-12 | Model Inference API Gateway | L4 — Deployment Infrastructure | — | An attacker may spoof the Model Inference API Gateway to intercept inference requests and return fabricated completions, bypassing the real foundation models. | LOW | HIGH | Medium | Enforce gateway identity verification with server certificates. Require mutual TLS on all agent-to-gateway connections. |
| S-13 | HIPAA RBAC + Policy Engine | L6 — Security and Compliance | — | An attacker may spoof the HIPAA RBAC + Policy Engine to issue false access-grant decisions to the Physician Clinical Portal, enabling unauthorized clinical data access. | LOW | HIGH | Medium | Sign all RBAC policy decisions with the policy engine's identity key. Implement portal-side verification of signed access decisions before granting access. |
| S-14 | Consent and De-identification Guardrail | L6 — Security and Compliance | — | An attacker may spoof the Consent and De-identification Guardrail response, returning raw PHI to components that expected de-identified data, bypassing consent enforcement. | LOW | HIGH | Medium | Authenticate all guardrail responses with service-level credentials. Upstream components must verify guardrail response integrity before processing returned data. |

### 3.2 Tampering (T)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|------------|--------|------------|------------|
| T-1 | Physician Clinical Portal | L7 — Agent Ecosystem | — | An attacker may tamper with clinical recommendation responses in transit between Supervisor Orchestrator and the Physician Clinical Portal, altering displayed recommendations without physician awareness. | MEDIUM | HIGH | High | Implement end-to-end message signing for recommendation responses. Use Content Security Policy and sub-resource integrity to detect tampering at the portal layer. |
| T-2 | Patient Summary Generator | L7 — Agent Ecosystem | — | An attacker with access to the summary generation pipeline may tamper with patient-facing summaries, injecting dangerous or false clinical guidance into patient communications. | MEDIUM | HIGH | High | Implement integrity verification of summary content before delivery. Use signed summary payloads and audit all summary generation events. |
| T-3 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | communication_vulnerability | An attacker with access to the inter-agent message bus may tamper with delegation messages or specialist results in transit, corrupting clinical reasoning across the multi-agent pipeline. | HIGH | HIGH | Critical | Implement message-level integrity (HMAC or digital signatures) on all inter-agent messages. Use tamper-evident logging for all channel activity. |
| T-4 | Supervisor Orchestrator | L3 — Agent Framework | — | An attacker who compromises the Supervisor Orchestrator may tamper with the delegation logic, routing clinical tasks to adversary-controlled specialist implementations or corrupting aggregated outputs before returning them to the portal. | MEDIUM | HIGH | High | Implement immutable audit logging of all orchestration decisions. Use runtime integrity monitoring for orchestrator process state. Apply least-privilege access for orchestrator configuration changes. |
| T-5 | Diagnostic Agent | L3 — Agent Framework | — | An attacker may tamper with the Diagnostic Agent's tool call requests to Clinical MCP Tool Server, injecting malicious FHIR operations or corrupting guideline retrieval queries. | MEDIUM | HIGH | High | Validate and sanitize all outgoing tool call parameters. Implement allowlist-based tool call schemas enforced by the MCP Tool Server before execution. |
| T-6 | Treatment Planner Agent | L3 — Agent Framework | — | An attacker may tamper with the Treatment Planner Agent's literature retrieval queries or tool calls, injecting adversarially crafted inputs that corrupt treatment plan generation. | MEDIUM | HIGH | High | Apply strict input validation to all retrieval queries. Implement schema-enforced tool call validation before MCP Tool Server execution. |
| T-7 | Clinical MCP Tool Server | L3 — Agent Framework | — | An attacker who compromises the Clinical MCP Tool Server may tamper with FHIR read/write operations, modifying patient records without authorization or returning corrupted data to agents. | HIGH | HIGH | Critical | Enforce signed FHIR operation requests from authorized agents only. Implement FHIR resource integrity checksums and audit all write operations with non-repudiable logs. |
| T-8 | Clinical LLM | L1 — Foundation Model | — | An attacker may tamper with the Clinical LLM prompt inputs forwarded by the API Gateway, injecting adversarial tokens that corrupt the clinical reasoning completion. | MEDIUM | HIGH | High | Implement prompt input validation and sanitization at the API Gateway layer. Log all prompt inputs for forensic review. |
| T-9 | Risk Stratification Model | L1 — Foundation Model | — | An attacker may tamper with fine-tuning data or inference inputs to the Risk Stratification Model, causing systematically biased risk scores that lead to incorrect clinical decisions. | MEDIUM | HIGH | High | Implement training data provenance attestation and integrity checks. Validate all inference inputs against a canonical schema before forwarding. |
| T-10 | FHIR Resource Store | L2 — Data Operations | — | An attacker with access to the FHIR Resource Store may tamper with patient records, injecting false clinical data that corrupts all downstream clinical decision processes. | HIGH | HIGH | Critical | Implement row-level integrity checksums on FHIR resources. Enforce write access via the Consent and De-identification Guardrail only. Audit all write operations. |
| T-11 | Clinical Guideline RAG Corpus | L2 — Data Operations | — | An attacker may poison the Clinical Guideline RAG Corpus by injecting adversarially crafted guideline embeddings, causing the RAG retrieval to surface malicious clinical guidance to the Diagnostic Agent. | HIGH | HIGH | Critical | Implement provenance verification for all corpus documents before indexing. Deploy adversarial embedding detection and monitor retrieval patterns for anomalous queries. |
| T-12 | Medical Literature Vector Index | L2 — Data Operations | — | An attacker may inject malicious vector embeddings into the Medical Literature Vector Index, causing Treatment Planner Agent to retrieve and incorporate adversarial literature recommendations. | MEDIUM | HIGH | High | Implement document provenance attestation before indexing. Apply anomaly detection on retrieval patterns and validate retrieved content before agent consumption. |
| T-13 | Model Inference API Gateway | L4 — Deployment Infrastructure | — | An attacker may tamper with the Model Inference API Gateway configuration, rerouting inference requests to adversary-controlled model endpoints or modifying prompts before forwarding. | LOW | HIGH | Medium | Enforce infrastructure-as-code for gateway configuration with change auditing. Apply gateway integrity monitoring and alert on configuration deviations. |
| T-14 | EHR Ingestion Queue | L4 — Deployment Infrastructure | — | An attacker may tamper with EHR update events in the ingestion queue before normalization, injecting false patient data that propagates into the FHIR Resource Store. | MEDIUM | HIGH | High | Implement message integrity signatures on all enqueued EHR events. Validate event integrity at dequeue time before FHIR normalization. |
| T-15 | Clinical Audit Log | L5 — Evaluation and Observability | — | An attacker who gains write access to the Clinical Audit Log may tamper with decision log entries, covering tracks for unauthorized actions or injecting false audit evidence. | MEDIUM | HIGH | High | Implement append-only audit log storage with cryptographic chaining. Apply write-access restrictions limiting audit log writes to authenticated service identities only. |
| T-16 | Outcomes Telemetry and Physician Override Audit Store | L5 — Evaluation and Observability | temporal_attack | An attacker may tamper with the Outcomes Telemetry and Physician Override Audit Store, injecting adversarial physician-override signals that corrupt the learning loop re-training process and cause model drift toward attacker-preferred outputs. | HIGH | HIGH | Critical | Implement provenance attestation on all physician-override records before ingestion into the learning loop. Apply behavioral baselining to detect drift in model outputs after re-training cycles. Restrict write access to verified physician identity tokens. |
| T-17 | HIPAA RBAC + Policy Engine | L6 — Security and Compliance | — | An attacker may tamper with RBAC policy rules in the policy engine, granting unauthorized access to clinical data or escalating privileges for compromised accounts. | LOW | HIGH | Medium | Enforce policy-as-code with immutable policy history. Implement change approval workflow for all RBAC policy modifications with dual-control signing. |
| T-18 | Consent and De-identification Guardrail | L6 — Security and Compliance | — | An attacker may tamper with the de-identification guardrail configuration, disabling or weakening de-identification rules to expose raw PHI to downstream components. | LOW | HIGH | Medium | Enforce immutable guardrail configuration with change auditing. Implement runtime PHI detection alerts downstream to detect guardrail bypass. |

### 3.3 Repudiation (R)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|------------|--------|------------|------------|
| R-1 | Physician | L7 — Agent Ecosystem | — | A physician may deny issuing a clinical query or claim that a recommendation view they acted upon was different from what the system recorded, creating liability disputes. | MEDIUM | MEDIUM | Medium | Implement non-repudiable logging of all physician clinical queries and recommendation views with cryptographic timestamps and physician identity binding. |
| R-2 | Patient | L7 — Agent Ecosystem | — | A patient may deny submitting EHR update events that were used as the basis for clinical decisions, complicating audit trails. | LOW | MEDIUM | Low | Implement signed EHR update event receipts. Log all patient-submitted events with non-repudiable identity binding and timestamps. |
| R-3 | Physician Clinical Portal | L7 — Agent Ecosystem | — | The Physician Clinical Portal may fail to provide non-repudiable records of which clinical recommendations were displayed to a physician, making it impossible to reconstruct the basis for a physician's clinical decision. | MEDIUM | MEDIUM | Medium | Implement tamper-evident session logs capturing every recommendation view with physician identity, timestamp, and recommendation content hash. |
| R-4 | Patient Summary Generator | L7 — Agent Ecosystem | — | The Patient Summary Generator may fail to maintain non-repudiable records of summaries delivered to patients, creating gaps in clinical accountability. | LOW | MEDIUM | Low | Log all generated summaries with content hash, patient identifier, and delivery timestamp in the Clinical Audit Log. |
| R-5 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | — | The Inter-Agent Communication Channel may fail to provide non-repudiable records of all delegation messages and specialist results, allowing agents to deny actions taken during the coordination flow. | MEDIUM | HIGH | High | Enforce tamper-evident inter-agent message logging with per-message cryptographic receipts. All delegation commands and specialist results must be logged in the Clinical Audit Log before acting. |
| R-6 | Supervisor Orchestrator | L3 — Agent Framework | — | The Supervisor Orchestrator may fail to maintain non-repudiable records of which delegation commands it issued and which specialist results it aggregated, making agent accountability impossible. | MEDIUM | HIGH | High | Implement mandatory pre-action audit logging for all orchestration decisions. Use append-only audit storage with cryptographic chaining to prevent retroactive modification. |
| R-7 | Diagnostic Agent | L3 — Agent Framework | — | The Diagnostic Agent may deny issuing specific tool calls to the Clinical MCP Tool Server or deny the guideline retrieval queries it submitted, preventing investigation of erroneous diagnoses. | MEDIUM | MEDIUM | Medium | Log all Diagnostic Agent tool calls and retrieval queries with non-repudiable identity binding before execution. Implement agent-level audit trails in the Clinical Audit Log. |
| R-8 | Treatment Planner Agent | L3 — Agent Framework | — | The Treatment Planner Agent may deny issuing specific literature retrieval queries or tool calls that contributed to harmful treatment plans, obstructing clinical accountability. | MEDIUM | MEDIUM | Medium | Log all Treatment Planner Agent retrievals and tool calls with non-repudiable identity binding. Audit all inputs that contributed to each generated treatment plan. |
| R-9 | Clinical MCP Tool Server | L3 — Agent Framework | — | The Clinical MCP Tool Server may fail to maintain non-repudiable records of which FHIR operations were executed in response to agent tool calls, making it impossible to trace patient record modifications to their source. | MEDIUM | HIGH | High | Implement mandatory audit logging of all MCP tool calls with requesting agent identity, operation type, and affected FHIR resources. |
| R-10 | Clinical LLM | L1 — Foundation Model | — | The Clinical LLM may fail to maintain non-repudiable logs of which prompts were submitted and which completions were returned, making it impossible to audit the basis of clinical reasoning outputs. | MEDIUM | MEDIUM | Medium | Log all prompt-completion pairs with request ID, timestamp, and submitting agent identity at the API Gateway layer. |
| R-11 | Risk Stratification Model | L1 — Foundation Model | — | The Risk Stratification Model may fail to maintain non-repudiable records of which patient inputs produced which risk scores, preventing audit of risk stratification decisions. | MEDIUM | MEDIUM | Medium | Log all inference inputs and outputs with patient context ID and timestamp at the API Gateway layer. |
| R-12 | Model Inference API Gateway | L4 — Deployment Infrastructure | — | The Model Inference API Gateway may fail to maintain non-repudiable records of all inference requests forwarded to foundation models, making it impossible to reconstruct the chain of clinical AI decisions. | MEDIUM | MEDIUM | Medium | Implement mandatory access logging at the API Gateway for all inference requests with requesting agent identity, target model, and request/response hashes. |
| R-13 | HIPAA RBAC + Policy Engine | L6 — Security and Compliance | — | The HIPAA RBAC + Policy Engine may fail to maintain non-repudiable records of all access decisions, preventing post-incident review of which access grants were issued to which entities. | LOW | HIGH | Medium | Implement immutable policy event logging in the Clinical Audit Log for all RBAC access decisions with requestor identity, resource, decision, and timestamp. |

### 3.4 Information Disclosure (I)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|------------|--------|------------|------------|
| I-1 | Physician Clinical Portal | L7 — Agent Ecosystem | — | Sensitive clinical recommendation data including patient PHI may be disclosed through the Physician Clinical Portal via insecure HTTPS configuration, excessive error messages, or missing access controls on recommendation views. | MEDIUM | HIGH | High | Enforce TLS 1.3 minimum. Sanitize all error messages to prevent PHI leakage. Implement field-level access control on displayed recommendation data. |
| I-2 | Patient Summary Generator | L7 — Agent Ecosystem | — | Patient-facing summaries may inadvertently include sensitive clinical details beyond the authorized disclosure scope, or may be delivered to wrong patients due to missing identity validation. | MEDIUM | HIGH | High | Implement patient identity verification before summary delivery. Apply disclosure-scope filtering to summary content. Audit all summary deliveries. |
| I-3 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | communication_vulnerability | Sensitive clinical context including patient PHI and clinical reasoning may be disclosed through the inter-agent message bus if messages are transmitted without encryption or if channel access is insufficiently restricted. | HIGH | HIGH | Critical | Encrypt all inter-agent messages in transit. Restrict channel access to authenticated specialist agents only. Implement message-level access controls. |
| I-4 | Supervisor Orchestrator | L3 — Agent Framework | — | The Supervisor Orchestrator aggregates sensitive patient data from FHIR, specialist results, and model outputs. A compromise may expose this aggregated clinical context, which is more sensitive than any individual component's data. | MEDIUM | HIGH | High | Implement minimal-exposure context windows — pass only data necessary for each specialist task. Sanitize aggregated context before logging. Apply memory isolation between clinical sessions. |
| I-5 | Diagnostic Agent | L3 — Agent Framework | — | The Diagnostic Agent may expose sensitive patient context retrieved from Clinical Guideline RAG Corpus and risk stratification results through tool call parameters, error responses, or insufficient isolation between patient sessions. | MEDIUM | HIGH | High | Implement session isolation for each clinical query. Sanitize all tool call parameters and error responses. Apply output filtering before logging diagnostic results. |
| I-6 | Treatment Planner Agent | L3 — Agent Framework | — | The Treatment Planner Agent may disclose sensitive patient data retrieved from the Medical Literature Vector Index through insufficient session isolation or unfiltered error responses. | MEDIUM | HIGH | High | Implement session isolation for each treatment planning task. Apply output filtering on all retrieval results before incorporating into treatment plans. |
| I-7 | Clinical MCP Tool Server | L3 — Agent Framework | — | The Clinical MCP Tool Server may expose PHI from FHIR read operations to unauthorized agents through insufficient access controls on tool results, or through overly broad FHIR queries returning more data than requested. | HIGH | HIGH | Critical | Implement resource-level access controls on all FHIR operations. Enforce minimum-necessary data principle on all tool responses. Validate requesting agent authorization before returning PHI. |
| I-8 | Clinical LLM | L1 — Foundation Model | — | The Clinical LLM may memorize and surface sensitive training data including patient records in its completions, disclosing PHI to agents that did not have authorization to access it. | MEDIUM | HIGH | High | Apply differential privacy techniques during model training. Implement output monitoring for PHI pattern detection in completions. Use data minimization in training set construction. |
| I-9 | Risk Stratification Model | L1 — Foundation Model | — | The Risk Stratification Model may leak patient cohort data from its fine-tuning training set through membership inference attacks or through overfitted responses that reveal individual patient characteristics. | MEDIUM | HIGH | High | Apply differential privacy during fine-tuning. Implement model output monitoring for membership inference signals. Restrict fine-tuning dataset access to authorized data science personnel. |
| I-10 | FHIR Resource Store | L2 — Data Operations | — | Patient PHI stored in the FHIR Resource Store may be disclosed through unauthorized read operations by agents with overly broad access, SQL/FHIR injection attacks, or missing PHI encryption at rest. | HIGH | HIGH | Critical | Enforce encryption at rest for all FHIR resources. Apply resource-level RBAC for all read operations. Implement FHIR injection prevention and audit all data access. |
| I-11 | Clinical Guideline RAG Corpus | L2 — Data Operations | — | The Clinical Guideline RAG Corpus may inadvertently index sensitive patient data if clinical guidelines incorporate patient examples, disclosing this data through semantic retrieval to the Diagnostic Agent. | LOW | MEDIUM | Low | Sanitize all corpus documents for PHI before indexing. Implement PHI detection scanning on all new corpus additions. |
| I-12 | Medical Literature Vector Index | L2 — Data Operations | — | The Medical Literature Vector Index may expose sensitive research data or cross-contaminate patient-specific retrieval results if insufficient session isolation is implemented. | LOW | MEDIUM | Low | Implement strict session isolation for all retrieval operations. Apply content filtering on retrieved vectors before returning to Treatment Planner Agent. |
| I-13 | Model Inference API Gateway | L4 — Deployment Infrastructure | — | The Model Inference API Gateway may expose inference request logs containing patient PHI or clinical context through insufficient log access controls or log retention policies. | MEDIUM | MEDIUM | Medium | Apply PHI-aware log filtering before storing inference request logs. Implement access controls on inference logs. Enforce data retention limits. |
| I-14 | EHR Ingestion Queue | L4 — Deployment Infrastructure | — | Patient EHR update events in the ingestion queue may be disclosed through insufficient queue access controls, allowing unauthorized parties to read enqueued patient records. | MEDIUM | HIGH | High | Encrypt all queued messages. Restrict queue read access to authorized consumers only. Implement queue-level access auditing. |
| I-15 | Clinical Audit Log | L5 — Evaluation and Observability | — | The Clinical Audit Log accumulates highly sensitive clinical decision trails. Unauthorized read access could disclose PHI, clinical reasoning, and agent decision patterns to adversaries. | MEDIUM | HIGH | High | Restrict audit log read access to authorized compliance personnel only. Encrypt audit log storage. Apply data retention and access audit controls. |
| I-16 | Outcomes Telemetry and Physician Override Audit Store | L5 — Evaluation and Observability | — | Physician override telemetry may contain implicit patient data. Unauthorized access to the Outcomes Telemetry store could disclose sensitive clinical patterns or be used for re-identification of de-identified training data. | MEDIUM | HIGH | High | Restrict access to Outcomes Telemetry to the learning loop and authorized data science personnel. Apply re-identification risk assessment before using telemetry in model updates. |
| I-17 | HIPAA RBAC + Policy Engine | L6 — Security and Compliance | — | The HIPAA RBAC + Policy Engine may leak access control policies through detailed error messages or API responses, enabling attackers to enumerate permissions and plan privilege escalation. | LOW | MEDIUM | Low | Sanitize all RBAC API error responses to prevent policy enumeration. Return generic access-denied messages. |
| I-18 | Consent and De-identification Guardrail | L6 — Security and Compliance | — | The Consent and De-identification Guardrail may disclose raw PHI through implementation flaws in the de-identification process, or expose de-identification rule logic that enables re-identification attacks. | LOW | HIGH | Medium | Audit de-identification logic against established standards (HIPAA Safe Harbor). Implement output validation to detect residual PHI before releasing de-identified data. |

### 3.5 Denial of Service (D)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|------------|--------|------------|------------|
| D-1 | Physician Clinical Portal | L7 — Agent Ecosystem | — | An attacker may flood the Physician Clinical Portal with clinical query requests, degrading availability for legitimate physicians during critical clinical decision periods. | MEDIUM | HIGH | High | Implement rate limiting on clinical query submission. Apply adaptive throttling based on session anomaly detection. Use circuit breakers to prevent cascade to backend agents. |
| D-2 | Patient Summary Generator | L7 — Agent Ecosystem | — | An attacker may flood the Patient Summary Generator with spurious summary requests, degrading availability for legitimate patient summary delivery. | MEDIUM | MEDIUM | Medium | Implement rate limiting per patient session. Apply queue depth monitoring and alert on abnormal summary generation volume. |
| D-3 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | resource_competition | An attacker may flood the Inter-Agent Communication Channel with spurious delegation messages, starving legitimate specialist agent task processing and disrupting the multi-agent coordination flow. | MEDIUM | HIGH | High | Implement channel capacity limits with per-agent message rate controls. Apply message origin validation before enqueuing. Monitor channel queue depth for anomalous saturation. |
| D-4 | Supervisor Orchestrator | L3 — Agent Framework | resource_competition | An attacker who compromises one specialist agent may flood the Supervisor Orchestrator with high-volume task results or error responses, causing resource exhaustion that renders the orchestrator unable to coordinate legitimate clinical queries. | MEDIUM | HIGH | High | Implement circuit breakers on specialist agent result processing. Apply per-agent response rate limits at the orchestrator. Monitor orchestrator resource utilization. |
| D-5 | Diagnostic Agent | L3 — Agent Framework | — | An attacker may target the Diagnostic Agent with resource-exhausting tool call floods or retrieval storms against the Clinical Guideline RAG Corpus, disrupting diagnostic capabilities for legitimate clinical queries. | MEDIUM | HIGH | High | Implement tool call rate limits per clinical session. Apply circuit breakers on guideline retrieval. Monitor Diagnostic Agent resource utilization. |
| D-6 | Treatment Planner Agent | L3 — Agent Framework | — | An attacker may exhaust Treatment Planner Agent resources through oversized literature retrieval queries or excessive tool call sequences, disrupting treatment planning for legitimate patients. | MEDIUM | MEDIUM | Medium | Implement retrieval query size limits and tool call rate limits per session. Apply resource quotas for the Treatment Planner Agent. |
| D-7 | Clinical MCP Tool Server | L3 — Agent Framework | — | An attacker who compromises an agent may flood the Clinical MCP Tool Server with excessive JSON-RPC tool calls or FHIR operations, exhausting server resources and denying tool access to legitimate agents. | MEDIUM | HIGH | High | Implement per-agent rate limits on MCP tool calls. Apply FHIR operation quotas. Use circuit breakers to isolate runaway agents from the tool server. |
| D-8 | Clinical LLM | L1 — Foundation Model | — | An attacker may exhaust Clinical LLM inference capacity through large prompt floods via the API Gateway, preventing legitimate clinical reasoning requests from being served. | MEDIUM | HIGH | High | Implement inference request rate limiting at the API Gateway per authenticated session. Apply queue-based load shedding under high-demand conditions. |
| D-9 | Risk Stratification Model | L1 — Foundation Model | — | An attacker may target the Risk Stratification Model with high-volume risk inference requests, saturating the model's inference capacity and degrading diagnostic availability. | MEDIUM | MEDIUM | Medium | Implement per-session inference rate limiting at the API Gateway. Apply load balancing and auto-scaling for risk inference capacity. |
| D-10 | FHIR Resource Store | L2 — Data Operations | — | An attacker may execute resource-exhausting FHIR queries or write floods against the FHIR Resource Store, degrading availability for all components dependent on patient record retrieval. | MEDIUM | HIGH | High | Implement query complexity limits and rate throttling on FHIR operations. Apply resource monitoring with automated circuit breakers. Implement read/write operation quotas per component. |
| D-11 | Clinical Guideline RAG Corpus | L2 — Data Operations | — | An attacker may issue retrieval floods against the Clinical Guideline RAG Corpus, saturating retrieval capacity and preventing the Diagnostic Agent from accessing clinical guidelines. | LOW | MEDIUM | Low | Implement retrieval rate limits per session. Apply caching for commonly retrieved guidelines to reduce corpus load. |
| D-12 | Medical Literature Vector Index | L2 — Data Operations | — | An attacker may flood the Medical Literature Vector Index with excessive retrieval queries, degrading vector search availability for the Treatment Planner Agent. | LOW | MEDIUM | Low | Implement retrieval rate limits per session. Apply result caching to reduce index load under high demand. |
| D-13 | Model Inference API Gateway | L4 — Deployment Infrastructure | — | An attacker may saturate the Model Inference API Gateway through request floods, denying inference access to all agents dependent on foundation model capabilities. | MEDIUM | HIGH | High | Implement rate limiting and request quotas at the gateway. Apply adaptive load balancing across model inference instances. Use circuit breakers to protect backend model services. |
| D-14 | EHR Ingestion Queue | L4 — Deployment Infrastructure | — | An attacker may flood the EHR Ingestion Queue with malformed or oversized EHR events, causing queue saturation and blocking legitimate patient record ingestion. | MEDIUM | MEDIUM | Medium | Implement queue depth monitoring with automatic backpressure. Apply message size limits and per-source rate controls on ingestion. |
| D-15 | Clinical Audit Log | L5 — Evaluation and Observability | — | An attacker may flood the Clinical Audit Log with excessive log entries, causing disk exhaustion that prevents legitimate audit log writes and destroys accountability coverage. | LOW | HIGH | Medium | Implement write rate limiting on audit log ingestion. Apply storage quota monitoring with alerting. Use log rotation and archival to prevent disk exhaustion. |
| D-16 | Outcomes Telemetry and Physician Override Audit Store | L5 — Evaluation and Observability | — | An attacker may flood the Outcomes Telemetry store with spurious override signals, degrading the learning loop's ability to incorporate legitimate physician feedback and corrupting model re-training. | MEDIUM | MEDIUM | Medium | Implement rate limiting on physician override ingestion. Apply anomaly detection to flag abnormal override volumes before incorporating into the learning loop. |
| D-17 | HIPAA RBAC + Policy Engine | L6 — Security and Compliance | — | An attacker may flood the HIPAA RBAC + Policy Engine with access decision requests, causing policy engine unavailability and potentially blocking all clinical data access during the outage. | LOW | HIGH | Medium | Implement access decision caching for recently evaluated policies. Apply rate limiting on policy evaluation requests. Design fallback-deny behavior during policy engine unavailability. |
| D-18 | Consent and De-identification Guardrail | L6 — Security and Compliance | — | An attacker may flood the Consent and De-identification Guardrail with PHI processing requests, saturating de-identification capacity and blocking access to patient records for legitimate clinical workflows. | LOW | HIGH | Medium | Implement processing rate limits on guardrail requests. Apply queue-based load balancing with circuit breakers. Implement caching for de-identified records with appropriate TTL. |

### 3.6 Elevation of Privilege (E)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|------------|--------|------------|------------|
| E-1 | Physician Clinical Portal | L7 — Agent Ecosystem | — | An attacker who gains access to a low-privilege physician session may escalate to access clinical data belonging to other physicians or patients by exploiting broken access controls in the portal's recommendation view logic. | MEDIUM | HIGH | High | Implement strict session isolation and resource-level RBAC enforcement. Apply role-based data filtering on all recommendation views. Audit privilege escalation attempts. |
| E-2 | Patient Summary Generator | L7 — Agent Ecosystem | — | An attacker may exploit the Patient Summary Generator to request summaries for patients other than the authorized recipient, escalating access to unauthorized patient records. | MEDIUM | HIGH | High | Validate requesting identity against authorized patient scope before generating summaries. Implement patient-scope enforcement at the Supervisor Orchestrator level. |
| E-3 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | trust_exploitation | An attacker who compromises the Inter-Agent Communication Channel may escalate channel access to issue supervisor-level delegation commands to specialist agents, bypassing the Supervisor Orchestrator's authority and performing unauthorized clinical operations. | MEDIUM | HIGH | High | Implement role-based message authorization on the inter-agent channel. Specialist agents must verify delegation command authority level before execution. |
| E-4 | Supervisor Orchestrator | L3 — Agent Framework | — | A compromised Supervisor Orchestrator may escalate its own privilege to bypass RBAC checks enforced by the HIPAA Policy Engine, or grant escalated permissions to specialist agents beyond their authorized scope. | MEDIUM | HIGH | High | Enforce external RBAC validation for all Supervisor Orchestrator actions affecting patient data. Apply principle of least privilege for orchestrator service account. Audit all privilege escalation events. |
| E-5 | Diagnostic Agent | L3 — Agent Framework | — | A compromised Diagnostic Agent may escalate beyond its authorized scope by issuing FHIR operations that exceed its data access permissions via the Clinical MCP Tool Server, accessing patient records outside the current clinical query. | MEDIUM | HIGH | High | Enforce resource-level FHIR access scoping for Diagnostic Agent operations via the MCP Tool Server. Apply per-session access tokens with minimal-necessary permissions. |
| E-6 | Treatment Planner Agent | L3 — Agent Framework | — | A compromised Treatment Planner Agent may escalate its access to FHIR resources beyond the current patient's authorized scope through the Clinical MCP Tool Server. | MEDIUM | HIGH | High | Apply per-session FHIR access scoping for Treatment Planner Agent tool calls. Enforce resource-level access boundaries at the MCP Tool Server layer. |
| E-7 | Clinical MCP Tool Server | L3 — Agent Framework | — | A compromised agent may exploit the Clinical MCP Tool Server to escalate FHIR access beyond the calling agent's authorized scope, performing privileged FHIR operations (e.g., bulk data export, schema modifications) not authorized for the requesting agent. | HIGH | HIGH | Critical | Implement strict per-agent permission checks for each FHIR operation. Enforce operation-level authorization at the MCP Tool Server. Prohibit bulk export and administrative FHIR operations from agent tool calls. |
| E-8 | Clinical LLM | L1 — Foundation Model | — | An attacker may exploit prompt injection in the Clinical LLM to gain elevated reasoning authority, causing the model to output instructions that the Supervisor Orchestrator interprets as authorized system commands with elevated privilege. | MEDIUM | HIGH | High | Implement prompt injection detection at the API Gateway layer. Apply output filtering to prevent completions that contain system command patterns. Enforce completion output schema validation. |
| E-9 | Risk Stratification Model | L1 — Foundation Model | — | An attacker may manipulate Risk Stratification Model inputs to produce falsely elevated risk scores that trigger automated escalation workflows, gaining access to high-privilege clinical interventions. | LOW | HIGH | Medium | Implement risk score range validation before triggering escalation workflows. Apply anomaly detection on risk score distribution to flag outliers. |
| E-10 | Model Inference API Gateway | L4 — Deployment Infrastructure | — | An attacker who compromises the Model Inference API Gateway may escalate to access inference endpoints for models not authorized for the requesting agent, circumventing model-level access controls. | LOW | HIGH | Medium | Implement per-agent model access authorization at the gateway. Enforce allowlist-based model routing for each authenticated agent. |
| E-11 | HIPAA RBAC + Policy Engine | L6 — Security and Compliance | — | An attacker who exploits a vulnerability in the HIPAA RBAC + Policy Engine may escalate to administrative access, modifying policy rules to grant themselves or other entities unauthorized clinical data access. | LOW | HIGH | Medium | Apply multi-factor authentication and dual-control approval for all policy engine administrative operations. Enforce immutable audit logging of all policy changes. |
| E-12 | Consent and De-identification Guardrail | L6 — Security and Compliance | — | An attacker who compromises the Consent and De-identification Guardrail may escalate to bypass consent enforcement, accessing raw PHI without the patient's consent for unauthorized clinical or research purposes. | LOW | HIGH | Medium | Implement strict access controls on guardrail configuration and bypass mechanisms. Apply runtime enforcement of de-identification guarantees with downstream PHI detection monitoring. |

---

## Section 4: AI Threat Tables

### 4.1 Agentic Threats (AG)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|-----------------|------------|--------|------------|------------|
| AG-1 | Supervisor Orchestrator | L3 — Agent Framework | agent_collusion | The Supervisor Orchestrator may autonomously execute consequential clinical delegation commands without adequate human oversight, routing clinical tasks based on AI-generated orchestration logic that bypasses physician review or RBAC compliance checks. | ASI-01 | HIGH | HIGH | Critical | Implement human-in-the-loop confirmation gates for high-consequence clinical delegation decisions. Enforce RBAC compliance checks before all agent delegation commands. Apply maximum action scope limits per orchestration cycle. |
| AG-2 | Supervisor Orchestrator | L3 — Agent Framework | agent_collusion | A compromised Supervisor Orchestrator may abuse its privileged position as the delegation authority to issue unauthorized tool calls or FHIR operations through specialist agents, circumventing per-agent access controls by delegating to agents with broader permissions. | MCP-03 | HIGH | HIGH | Critical | Implement orchestrator-level tool call allowlisting restricting delegation to explicitly authorized agent-tool pairs. Apply cross-agent audit trails linking all delegated tool calls back to the originating orchestration command. |
| AG-3 | Diagnostic Agent | L3 — Agent Framework | — | The Diagnostic Agent may autonomously execute FHIR write operations via the Clinical MCP Tool Server beyond its authorized clinical scope, persisting adversarial or erroneous diagnostic data to patient records without physician authorization. | ASI-01 | MEDIUM | HIGH | High | Restrict Diagnostic Agent FHIR write access to explicitly authorized resource types and patient scope. Apply mandatory physician approval for any Diagnostic Agent FHIR write operations. |
| AG-4 | Diagnostic Agent | L3 — Agent Framework | — | A compromised Diagnostic Agent may abuse the Clinical MCP Tool Server as a tool abuse vector, issuing malicious FHIR operations (bulk reads, unauthorized writes) that exceed the agent's authorized scope. | MCP-03 | MEDIUM | HIGH | High | Implement operation-level authorization checks in the MCP Tool Server for all Diagnostic Agent requests. Enforce FHIR resource scope restrictions per session token. |
| AG-5 | Treatment Planner Agent | L3 — Agent Framework | — | The Treatment Planner Agent may autonomously incorporate adversarially retrieved medical literature into treatment plans without human validation, resulting in dangerous or contraindicated treatment recommendations delivered to physicians. | ASI-01 | MEDIUM | HIGH | High | Implement mandatory evidence validation before incorporating retrieved literature into treatment plans. Apply physician review gates for treatment plans flagged as high-consequence. |
| AG-6 | Treatment Planner Agent | L3 — Agent Framework | — | A compromised Treatment Planner Agent may abuse the Clinical MCP Tool Server to perform unauthorized FHIR operations, writing false treatment prescriptions or accessing patient records outside the current patient scope. | MCP-03 | MEDIUM | HIGH | High | Enforce patient-scope and resource-type restrictions on all Treatment Planner Agent MCP tool calls. Implement operation-level FHIR access controls at the MCP Tool Server. |
| AG-7 | Clinical MCP Tool Server | L3 — Agent Framework | — | A malicious or compromised agent may exploit the Clinical MCP Tool Server to perform privilege escalation via tool chaining — executing a sequence of individually-permitted FHIR operations that collectively achieves an unauthorized outcome (e.g., bulk patient data export or unauthorized record modification). | MCP-03 | HIGH | HIGH | Critical | Implement tool chain monitoring to detect sequences of permitted operations that collectively violate access policy. Apply transaction-level audit logging for all multi-step FHIR operation sequences. Define and enforce prohibited operation chain patterns. |
| AG-8 | Inter-Agent Communication Channel | L7 — Agent Ecosystem | communication_vulnerability | A compromised or rogue agent may abuse the Inter-Agent Communication Channel to flood specialist agents with excessive delegation messages, executing a resource exhaustion attack that disrupts multi-agent coordination across all clinical sessions. | MCP-03 | MEDIUM | HIGH | High | Implement per-agent message rate limits on the inter-agent channel. Apply message source validation and circuit breakers to isolate flooding agents from the channel. |

### 4.2 LLM Threats (LLM)

| ID | Component | MAESTRO Layer | Agentic Pattern | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|-----------------|--------|-----------------|------------|--------|------------|------------|
| LLM-1 | Clinical LLM | L1 — Foundation Model | — | An attacker may inject adversarial prompts into the clinical context window passed to the Clinical LLM via the API Gateway, causing the model to generate harmful, false, or clinically dangerous completions that the Supervisor Orchestrator incorporates into clinical recommendations. | OWASP LLM01:2025 | HIGH | HIGH | Critical | Implement prompt injection detection and sanitization at the API Gateway before forwarding to the Clinical LLM. Apply output validation to detect clinically dangerous completions. Use system prompt hardening to resist instruction injection. |
| LLM-2 | Clinical LLM | L1 — Foundation Model | — | An adversary may poison the training data or fine-tuning feedback incorporated into the Clinical LLM via the Outcomes Telemetry learning loop, causing the model to produce systematically biased or manipulated clinical completions after re-training. | OWASP LLM03:2025 | MEDIUM | HIGH | High | Implement training data provenance attestation and integrity verification before learning loop incorporation. Apply behavioral baselining to detect post-training output drift. Implement emergency model rollback capability. |
| LLM-3 | Clinical LLM | L1 — Foundation Model | — | An adversary may extract the Clinical LLM's learned clinical knowledge through repeated targeted queries via the API Gateway, enabling model theft or reconstruction of proprietary medical AI capabilities. | OWASP LLM10:2025 | LOW | MEDIUM | Low | Implement query rate limiting and anomaly detection for systematic extraction patterns. Apply output perturbation to reduce model extraction fidelity. Monitor query patterns for systematic knowledge extraction behavior. |
| LLM-4 | Risk Stratification Model | L1 — Foundation Model | — | An attacker may craft adversarial patient record inputs passed to the Risk Stratification Model to generate manipulated risk scores, causing incorrect clinical triage and resource allocation decisions. | OWASP LLM01:2025 | MEDIUM | HIGH | High | Implement input validation and anomaly detection for adversarial patient record patterns. Apply ensemble validation by cross-checking risk scores against clinical rules. |
| LLM-5 | Risk Stratification Model | L1 — Foundation Model | — | An adversary may poison the supervised fine-tuning dataset used to train the Risk Stratification Model, embedding adversarial patterns that cause the model to systematically misclassify high-risk patients as low-risk after re-training. | OWASP LLM03:2025 | MEDIUM | HIGH | High | Implement fine-tuning dataset integrity verification and provenance attestation. Apply behavioral testing against known high-risk cases after each model update. Monitor risk score distribution for systematic drift. |
| LLM-6 | Risk Stratification Model | L1 — Foundation Model | — | An adversary may conduct membership inference attacks against the Risk Stratification Model to determine which patients were included in the fine-tuning dataset, violating patient privacy even when the model is deployed without direct data access. | OWASP LLM10:2025 | MEDIUM | HIGH | High | Apply differential privacy during model fine-tuning to provide formal privacy guarantees. Implement query auditing to detect membership inference attack patterns. |

---

## Section 4a: Correlated Findings

Correlation rules applied: CR-1 (Tampering + Data-Poisoning), CR-2 (Privilege-Escalation + Agent-Autonomy), CR-3 (Info-Disclosure + Prompt-Injection), CR-4 (Repudiation + Agent-Autonomy), CR-5 (Denial-of-Service + Tool-Abuse).

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-7, AG-7 | Clinical MCP Tool Server | Tampering: MCP Tool Server FHIR operations tampered by compromised agents; Agentic: Tool chaining privilege escalation via permitted FHIR operation sequences | Critical |
| CG-2 | E-7, AG-7 | Clinical MCP Tool Server | Privilege-Escalation: Escalation to unauthorized FHIR operations; Agentic: Tool abuse via chained permitted operations achieving unauthorized outcomes | Critical |
| CG-3 | I-7, LLM-1 | Clinical LLM | Info-Disclosure: Clinical LLM may surface PHI from training data; LLM: Prompt injection causing harmful completions; combined risk of information leakage via adversarial prompting | Critical |
| CG-4 | R-6, AG-1 | Supervisor Orchestrator | Repudiation: Supervisor Orchestrator fails to maintain non-repudiable delegation records; Agentic: Autonomous delegation without oversight creating accountability gaps | Critical |
| CG-5 | D-3, AG-8 | Inter-Agent Communication Channel | Denial-of-Service: Channel flood disrupting multi-agent coordination; Agentic: Tool-abuse message flood from compromised agent via channel | High |
| CG-6 | T-11, LLM-5 | Clinical Guideline RAG Corpus / Risk Stratification Model | Tampering: RAG corpus poisoning with adversarial embeddings; LLM Data-Poisoning: Fine-tuning dataset poisoning causing systematic misclassification | Critical |

Note: CG-6 involves findings at different components but shares the data poisoning threat basis — adversarial data injection corrupting AI model outputs.

---

## Section 4b: Findings by Agentic Pattern

| Pattern | Count | Findings |
|---------|-------|----------|
| trust_exploitation | 5 | S-5, S-6, S-7, S-8, E-3 |
| agent_collusion | 4 | AG-1, AG-2, AGP-01, AGP-03 |
| communication_vulnerability | 3 | T-3, I-3, AG-8 |
| temporal_attack | 2 | T-16, AGP-02 |
| resource_competition | 2 | D-3, D-4 |
| emergent_behavior | 1 | AGP-03 |

Note: AGP-03 appears under both agent_collusion and emergent_behavior due to net-new finding assignment targeting Supervisor Orchestrator cascading delegation.

---

## Section 5: Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| Physician | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Patient | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Physician Clinical Portal | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| Patient Summary Generator | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| Inter-Agent Communication Channel | 1 | 1 | 1 | 1 | 1 | 1 | 1 | n/a | 7 |
| Supervisor Orchestrator | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| Diagnostic Agent | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| Treatment Planner Agent | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| Clinical MCP Tool Server | 1 | 1 | 1 | 1 | 1 | 1 | 2 | n/a | 8 |
| Clinical LLM | 1 | 1 | 1 | 1 | 1 | 1 | n/a | 3 | 9 |
| Risk Stratification Model | 1 | 1 | 1 | 1 | 1 | 1 | n/a | 3 | 9 |
| FHIR Resource Store | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Clinical Guideline RAG Corpus | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Medical Literature Vector Index | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Model Inference API Gateway | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| EHR Ingestion Queue | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Clinical Audit Log | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| Outcomes Telemetry and Physician Override Audit Store | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| HIPAA RBAC + Policy Engine | 1 | 1 | 1 | 1 | 1 | 1 | n/a | n/a | 6 |
| Consent and De-identification Guardrail | 1 | 1 | --- | 1 | 1 | 1 | n/a | n/a | 5 |
| **Total** | **14** | **18** | **13** | **18** | **18** | **12** | **9** | **6** | **108** |

Counts reflect deduplicated findings. 6 correlation groups merged 9 individual findings into 6 group representatives.

Net-new AGP findings: AGP-01 (agent_collusion on Inter-Agent Communication Channel), AGP-02 (temporal_attack on Outcomes Telemetry), AGP-03 (emergent_behavior on Supervisor Orchestrator).

### Section 5a: Coverage Gate Results

Coverage gate status: **PASS**

| Component | Determined Type | Required Categories | Covered Categories | Status |
|-----------|----------------|--------------------|--------------------|--------|
| Physician | external_entity | S, R | S, R | Pass |
| Patient | external_entity | S, R | S, R | Pass |
| Physician Clinical Portal | process | S, T, R, I, D, E | S, T, R, I, D, E | Pass |
| Patient Summary Generator | process | S, T, R, I, D, E | S, T, R, I, D, E | Pass |
| Inter-Agent Communication Channel | mcp_server (AG dispatch) | S, T, R, I, D, E, AG | S, T, R, I, D, E, AG | Pass |
| Supervisor Orchestrator | mcp_server (AG dispatch) | S, T, R, I, D, E, AG | S, T, R, I, D, E, AG | Pass |
| Diagnostic Agent | mcp_server (AG dispatch) | S, T, R, I, D, E, AG | S, T, R, I, D, E, AG | Pass |
| Treatment Planner Agent | mcp_server (AG dispatch) | S, T, R, I, D, E, AG | S, T, R, I, D, E, AG | Pass |
| Clinical MCP Tool Server | mcp_server | S, T, R, I, D, E, AG | S, T, R, I, D, E, AG | Pass |
| Clinical LLM | llm_process | S, T, R, I, D, E, LLM | S, T, R, I, D, E, LLM | Pass |
| Risk Stratification Model | llm_process | S, T, R, I, D, E, LLM | S, T, R, I, D, E, LLM | Pass |
| FHIR Resource Store | data_store | T, I, D | T, I, D | Pass |
| Clinical Guideline RAG Corpus | data_store | T, I, D | T, I, D | Pass |
| Medical Literature Vector Index | data_store | T, I, D | T, I, D | Pass |
| Model Inference API Gateway | process | S, T, R, I, D, E | S, T, R, I, D, E | Pass |
| EHR Ingestion Queue | data_store | T, I, D | T, I, D | Pass |
| Clinical Audit Log | data_store | T, I, D | T, I, D | Pass |
| Outcomes Telemetry and Physician Override Audit Store | data_store | T, I, D | T, I, D | Pass |
| HIPAA RBAC + Policy Engine | process | S, T, R, I, D, E | S, T, R, I, D, E | Pass |
| Consent and De-identification Guardrail | process | S, T, R, I, D, E | S, T, I, D, E | Pass (R clean) |

---

## Section 6: Risk Summary

### Risk Calibration Matrix

|                  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|------------------|----------------|-------------------|-----------------|
| **HIGH Impact**  | Medium         | High              | Critical        |
| **MEDIUM Impact**| Low            | Medium            | High            |
| **LOW Impact**   | Note           | Low               | Medium          |

### Risk Distribution

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 16 | 14.8% |
| High | 52 | 48.1% |
| Medium | 30 | 27.8% |
| Low | 8 | 7.4% |
| Note | 2 | 1.9% |
| **Total** | **108** | **100%** |

Note: Deduplicated counts reflect 6 correlation groups (CG-1 through CG-6) contributing 1 each at the group's highest severity, plus 3 net-new AGP findings.

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L3 — Agent Framework | 30 | Critical |
| L1 — Foundation Model | 18 | Critical |
| L7 — Agent Ecosystem | 22 | Critical |
| L2 — Data Operations | 9 | Critical |
| L5 — Evaluation and Observability | 6 | Critical |
| L6 — Security and Compliance | 12 | High |
| L4 — Deployment Infrastructure | 11 | High |

---

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-1 | Physician | Attacker impersonates physician via credential replay | Critical | Implement mutual TLS authentication and short-lived signed JWT tokens with physician identity binding. Enforce step-up authentication for high-sensitivity clinical queries. |
| S-5 | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messages on inter-agent bus | Critical | Authenticate all inter-agent messages with HMAC signatures using per-session keys. Implement message source validation before specialist agents process delegation commands. |
| S-6 | Supervisor Orchestrator | Attacker impersonates Supervisor Orchestrator to issue unauthorized delegation commands | Critical | Require cryptographic attestation of supervisor identity on all delegation messages. Implement zero-trust peer authentication between orchestrator and specialist agents. |
| T-3 | Inter-Agent Communication Channel | Attacker tampers with delegation messages or specialist results in transit | Critical | Implement message-level integrity (HMAC or digital signatures) on all inter-agent messages. Use tamper-evident logging for all channel activity. |
| T-7 | Clinical MCP Tool Server | Compromised MCP Tool Server tampers with FHIR read/write operations | Critical | Enforce signed FHIR operation requests from authorized agents only. Implement FHIR resource integrity checksums and audit all write operations. |
| T-10 | FHIR Resource Store | Attacker tampers with patient records, corrupting all downstream clinical decisions | Critical | Implement row-level integrity checksums on FHIR resources. Enforce write access via the Consent and De-identification Guardrail only. Audit all write operations. |
| T-11 | Clinical Guideline RAG Corpus | Attacker poisons RAG corpus with adversarial embeddings, causing malicious guidance retrieval | Critical | Implement provenance verification for all corpus documents before indexing. Deploy adversarial embedding detection and monitor retrieval patterns. |
| T-16 | Outcomes Telemetry and Physician Override Audit Store | Attacker injects adversarial override signals corrupting learning loop re-training | Critical | Implement provenance attestation on all physician-override records. Apply behavioral baselining to detect drift after re-training. Restrict write access to verified physician identity tokens. |
| I-3 | Inter-Agent Communication Channel | PHI disclosed through unencrypted inter-agent messages | Critical | Encrypt all inter-agent messages in transit. Restrict channel access to authenticated specialist agents only. |
| I-7 | Clinical MCP Tool Server | PHI exposed to unauthorized agents through insufficient MCP tool result access controls | Critical | Implement resource-level access controls on all FHIR operations. Enforce minimum-necessary data principle on all tool responses. |
| I-10 | FHIR Resource Store | Patient PHI disclosed through unauthorized FHIR reads or injection attacks | Critical | Enforce encryption at rest for all FHIR resources. Apply resource-level RBAC for all read operations. Implement FHIR injection prevention. |
| E-7 | Clinical MCP Tool Server | Compromised agent escalates to unauthorized FHIR operations via tool chaining | Critical | Implement strict per-agent permission checks for each FHIR operation. Prohibit bulk export and administrative FHIR operations from agent tool calls. |
| AG-1 | Supervisor Orchestrator | Autonomous delegation bypasses human oversight and RBAC checks | Critical | Implement human-in-the-loop confirmation gates for high-consequence clinical delegation decisions. Enforce RBAC compliance checks before all agent delegation commands. |
| AG-2 | Supervisor Orchestrator | Compromised orchestrator abuses delegation authority to circumvent per-agent access controls | Critical | Implement orchestrator-level tool call allowlisting. Apply cross-agent audit trails linking delegated tool calls to originating commands. |
| AG-7 | Clinical MCP Tool Server | Tool chaining achieves unauthorized FHIR outcomes via individually-permitted operation sequences | Critical | Implement tool chain monitoring to detect sequences violating access policy. Apply transaction-level audit logging for multi-step FHIR sequences. |
| LLM-1 | Clinical LLM | Prompt injection causes harmful clinical completions via API Gateway | Critical | Implement prompt injection detection and sanitization at the API Gateway. Apply output validation to detect clinically dangerous completions. |
| AGP-01 | Inter-Agent Communication Channel | Multi-agent coordination creates potential for coordinated malicious action across specialist agents | Critical | Implement inter-agent rate limits, coordination throttles, and per-flow audit logging. |
| S-2 | Patient | Attacker submits fraudulent EHR events by spoofing patient identity | High | Validate EHR update events against authoritative patient identity registry. Use cryptographic patient identity tokens. |
| S-3 | Physician Clinical Portal | Attacker spoofs portal to intercept clinical recommendation responses | High | Enforce server certificate pinning and signed response tokens. |
| S-7 | Diagnostic Agent | Attacker spoofs Diagnostic Agent to inject fraudulent diagnostic results | High | Sign all inter-agent result messages with agent-specific identity keys. |
| S-8 | Treatment Planner Agent | Attacker spoofs Treatment Planner Agent to inject malicious treatment plans | High | Sign all treatment plan outputs with agent-specific identity keys. |
| S-9 | Clinical MCP Tool Server | Attacker spoofs MCP Tool Server to return malicious tool results | High | Authenticate MCP Tool Server responses. Implement response integrity checks. |
| T-1 | Physician Clinical Portal | Attacker tampers with clinical recommendation responses in transit | High | Implement end-to-end message signing for recommendation responses. |
| T-2 | Patient Summary Generator | Attacker tampers with patient-facing summaries, injecting dangerous clinical guidance | High | Implement integrity verification of summary content before delivery. |
| T-4 | Supervisor Orchestrator | Compromised orchestrator tampers with delegation logic or aggregated outputs | High | Implement immutable audit logging of all orchestration decisions. Use runtime integrity monitoring. |
| T-5 | Diagnostic Agent | Attacker tampers with Diagnostic Agent tool call requests to inject malicious FHIR operations | High | Validate and sanitize all outgoing tool call parameters. Implement allowlist-based tool call schemas. |
| T-6 | Treatment Planner Agent | Attacker tampers with Treatment Planner Agent inputs corrupting treatment plan generation | High | Apply strict input validation to all retrieval queries. Implement schema-enforced tool call validation. |
| T-8 | Clinical LLM | Attacker tampers with prompt inputs to inject adversarial tokens | High | Implement prompt input validation and sanitization at the API Gateway. Log all prompt inputs. |
| T-9 | Risk Stratification Model | Attacker tampers with fine-tuning data causing biased risk scores | High | Implement training data provenance attestation. Validate all inference inputs against canonical schema. |
| T-12 | Medical Literature Vector Index | Attacker injects malicious vector embeddings corrupting literature retrieval | High | Implement document provenance attestation before indexing. Apply anomaly detection on retrieval patterns. |
| T-14 | EHR Ingestion Queue | Attacker tampers with EHR events in ingestion queue before normalization | High | Implement message integrity signatures on all enqueued EHR events. Validate event integrity at dequeue. |
| T-15 | Clinical Audit Log | Attacker tampers with audit log entries, covering tracks for unauthorized actions | High | Implement append-only audit log storage with cryptographic chaining. |
| R-5 | Inter-Agent Communication Channel | Channel fails to provide non-repudiable records of delegation messages | High | Enforce tamper-evident inter-agent message logging with per-message cryptographic receipts. |
| R-6 | Supervisor Orchestrator | Orchestrator fails non-repudiable records of delegation commands and aggregated results | High | Implement mandatory pre-action audit logging for all orchestration decisions. |
| R-9 | Clinical MCP Tool Server | MCP Tool Server fails non-repudiable records of FHIR operations | High | Implement mandatory audit logging of all MCP tool calls with requesting agent identity. |
| I-1 | Physician Clinical Portal | PHI disclosed through insecure HTTPS configuration or excessive error messages | High | Enforce TLS 1.3 minimum. Sanitize all error messages. Implement field-level access control. |
| I-2 | Patient Summary Generator | Patient summaries include unauthorized PHI or delivered to wrong patients | High | Implement patient identity verification before summary delivery. Apply disclosure-scope filtering. |
| I-4 | Supervisor Orchestrator | Compromise exposes aggregated sensitive patient context across specialists | High | Implement minimal-exposure context windows. Sanitize aggregated context before logging. |
| I-5 | Diagnostic Agent | Diagnostic Agent exposes patient context through tool call parameters or error responses | High | Implement session isolation for each clinical query. Sanitize all tool call parameters and error responses. |
| I-6 | Treatment Planner Agent | Treatment Planner Agent discloses patient data through insufficient session isolation | High | Implement session isolation for each treatment planning task. Apply output filtering. |
| I-8 | Clinical LLM | Clinical LLM surfaces PHI from training data in completions | High | Apply differential privacy during model training. Implement output monitoring for PHI pattern detection. |
| I-9 | Risk Stratification Model | Risk Stratification Model leaks patient cohort data through membership inference | High | Apply differential privacy during fine-tuning. Implement model output monitoring. |
| I-13 | Model Inference API Gateway | API Gateway exposes inference request logs containing patient PHI | Medium | Apply PHI-aware log filtering. Implement access controls on inference logs. |
| I-14 | EHR Ingestion Queue | EHR update events in queue disclosed through insufficient access controls | High | Encrypt all queued messages. Restrict queue read access to authorized consumers only. |
| I-15 | Clinical Audit Log | Unauthorized audit log read access discloses sensitive clinical decision trails | High | Restrict audit log read access to authorized compliance personnel only. Encrypt audit log storage. |
| I-16 | Outcomes Telemetry and Physician Override Audit Store | Telemetry access discloses clinical patterns or enables re-identification | High | Restrict access to Outcomes Telemetry. Apply re-identification risk assessment before model updates. |
| D-1 | Physician Clinical Portal | Clinical query request flood degrades availability for legitimate physicians | High | Implement rate limiting on clinical query submission. Apply adaptive throttling. |
| D-3 | Inter-Agent Communication Channel | Delegation message flood starves specialist agent processing | High | Implement channel capacity limits with per-agent message rate controls. |
| D-4 | Supervisor Orchestrator | High-volume task result flood causes orchestrator resource exhaustion | High | Implement circuit breakers on specialist agent result processing. Apply per-agent response rate limits. |
| D-5 | Diagnostic Agent | Tool call floods or retrieval storms disrupt Diagnostic Agent availability | High | Implement tool call rate limits per clinical session. Apply circuit breakers on guideline retrieval. |
| D-7 | Clinical MCP Tool Server | Excessive JSON-RPC tool calls exhaust MCP Tool Server resources | High | Implement per-agent rate limits on MCP tool calls. Apply FHIR operation quotas. |
| D-8 | Clinical LLM | Large prompt floods exhaust Clinical LLM inference capacity | High | Implement inference request rate limiting at the API Gateway per authenticated session. |
| D-10 | FHIR Resource Store | FHIR query or write floods degrade patient record availability | High | Implement query complexity limits and rate throttling on FHIR operations. |
| D-13 | Model Inference API Gateway | Request floods saturate inference gateway, denying all agents foundation model access | High | Implement rate limiting and request quotas at the gateway. Apply adaptive load balancing. |
| E-1 | Physician Clinical Portal | Attacker escalates from low-privilege session to access other physicians' data | High | Implement strict session isolation and resource-level RBAC enforcement. |
| E-2 | Patient Summary Generator | Attacker exploits summary generator to access unauthorized patient records | High | Validate requesting identity against authorized patient scope before generating summaries. |
| E-3 | Inter-Agent Communication Channel | Compromised channel allows escalation to supervisor-level delegation authority | High | Implement role-based message authorization on the inter-agent channel. |
| E-4 | Supervisor Orchestrator | Compromised orchestrator escalates to bypass RBAC or grant unauthorized permissions | High | Enforce external RBAC validation for all orchestrator actions affecting patient data. |
| E-5 | Diagnostic Agent | Compromised Diagnostic Agent escalates to unauthorized FHIR operations | High | Enforce resource-level FHIR access scoping for Diagnostic Agent operations. |
| E-6 | Treatment Planner Agent | Compromised Treatment Planner Agent escalates to unauthorized FHIR resources | High | Apply per-session FHIR access scoping for Treatment Planner Agent tool calls. |
| E-8 | Clinical LLM | Prompt injection causes elevated reasoning authority in Clinical LLM output | High | Implement prompt injection detection at the API Gateway. Apply output filtering. |
| AG-3 | Diagnostic Agent | Diagnostic Agent autonomously executes unauthorized FHIR write operations | High | Restrict Diagnostic Agent FHIR write access. Apply mandatory physician approval for FHIR write operations. |
| AG-4 | Diagnostic Agent | Compromised Diagnostic Agent abuses MCP Tool Server for malicious FHIR operations | High | Implement operation-level authorization checks in MCP Tool Server. |
| AG-5 | Treatment Planner Agent | Treatment Planner Agent autonomously incorporates adversarial literature without validation | High | Implement mandatory evidence validation before incorporating retrieved literature. |
| AG-6 | Treatment Planner Agent | Compromised Treatment Planner Agent abuses MCP Tool Server for unauthorized FHIR operations | High | Enforce patient-scope and resource-type restrictions on all Treatment Planner Agent MCP tool calls. |
| AG-8 | Inter-Agent Communication Channel | Compromised agent abuses inter-agent channel for resource exhaustion attack | High | Implement per-agent message rate limits on the inter-agent channel. |
| LLM-2 | Clinical LLM | Adversary poisons training data via learning loop causing systematic bias | High | Implement training data provenance attestation. Apply behavioral baselining to detect post-training output drift. |
| LLM-4 | Risk Stratification Model | Adversarial patient records manipulate risk scores causing incorrect triage | High | Implement input validation and anomaly detection for adversarial patient record patterns. |
| LLM-5 | Risk Stratification Model | Poisoned fine-tuning dataset causes systematic high-risk patient misclassification | High | Implement fine-tuning dataset integrity verification. Apply behavioral testing against known high-risk cases after model updates. |
| LLM-6 | Risk Stratification Model | Membership inference attack violates patient privacy for fine-tuning participants | High | Apply differential privacy during model fine-tuning. Implement query auditing to detect membership inference patterns. |
| AGP-02 | Outcomes Telemetry and Physician Override Audit Store | Architecture's persistent-state learning loop enables temporal attacks via gradual corruption | High | Implement training-data provenance attestation, memory-write audit trails, and periodic behavioral baselining against pre-training snapshots. |
| AGP-03 | Supervisor Orchestrator | Multi-agent cascading delegation exhibits potential for emergent behavior | High | Implement fail-safe shutdown circuits, bounded action scopes per agent, and behavioral baselining of the collective agent system. |
| S-4 | Patient Summary Generator | Attacker spoofs Patient Summary Generator to intercept patient summaries | Medium | Enforce HTTPS with TLS certificate validation. Require signed summary payloads. |
| S-10 | Clinical LLM | Attacker spoofs Clinical LLM completion responses via API Gateway interception | Medium | Enforce TLS with mutual authentication on API Gateway to Clinical LLM path. |
| S-11 | Risk Stratification Model | Attacker spoofs risk stratification outputs with falsified results | Medium | Sign all risk stratification outputs with model service credentials. |
| S-12 | Model Inference API Gateway | Attacker spoofs API Gateway to intercept and fabricate model completions | Medium | Enforce gateway identity verification with server certificates. Require mutual TLS on agent-to-gateway connections. |
| S-13 | HIPAA RBAC + Policy Engine | Attacker spoofs RBAC engine to issue false access-grant decisions | Medium | Sign all RBAC policy decisions with the policy engine's identity key. |
| S-14 | Consent and De-identification Guardrail | Attacker spoofs guardrail response returning raw PHI to expecting de-identified data | Medium | Authenticate all guardrail responses with service-level credentials. |
| T-13 | Model Inference API Gateway | Attacker tampers with API Gateway configuration to reroute inference requests | Medium | Enforce infrastructure-as-code for gateway configuration with change auditing. |
| T-17 | HIPAA RBAC + Policy Engine | Attacker tampers with RBAC policy rules granting unauthorized access | Medium | Enforce policy-as-code with immutable policy history. Implement dual-control signing for policy changes. |
| T-18 | Consent and De-identification Guardrail | Attacker tampers with de-identification configuration exposing raw PHI | Medium | Enforce immutable guardrail configuration with change auditing. |
| R-1 | Physician | Physician denies issuing clinical query or claims different recommendation was shown | Medium | Implement non-repudiable logging of clinical queries and recommendation views with cryptographic timestamps. |
| R-3 | Physician Clinical Portal | Portal fails to provide non-repudiable records of displayed recommendations | Medium | Implement tamper-evident session logs capturing every recommendation view. |
| R-7 | Diagnostic Agent | Diagnostic Agent denies issuing specific tool calls or retrieval queries | Medium | Log all Diagnostic Agent tool calls and retrieval queries with non-repudiable identity binding. |
| R-8 | Treatment Planner Agent | Treatment Planner Agent denies issuing retrieval queries or tool calls | Medium | Log all Treatment Planner Agent retrievals and tool calls with non-repudiable identity binding. |
| R-10 | Clinical LLM | Clinical LLM fails to maintain non-repudiable prompt-completion logs | Medium | Log all prompt-completion pairs with request ID and submitting agent identity at the API Gateway. |
| R-11 | Risk Stratification Model | Risk Stratification Model fails non-repudiable records of which patient inputs produced risk scores | Medium | Log all inference inputs and outputs with patient context ID and timestamp at the API Gateway. |
| R-12 | Model Inference API Gateway | API Gateway fails non-repudiable records of inference requests forwarded to foundation models | Medium | Implement mandatory access logging at the API Gateway for all inference requests. |
| R-13 | HIPAA RBAC + Policy Engine | RBAC engine fails non-repudiable records of all access decisions | Medium | Implement immutable policy event logging in the Clinical Audit Log for all RBAC access decisions. |
| I-17 | HIPAA RBAC + Policy Engine | RBAC engine leaks access control policies through detailed error messages | Low | Sanitize all RBAC API error responses to prevent policy enumeration. |
| I-18 | Consent and De-identification Guardrail | Guardrail discloses raw PHI through de-identification implementation flaws | Medium | Audit de-identification logic against HIPAA Safe Harbor. Implement output validation to detect residual PHI. |
| D-2 | Patient Summary Generator | Spurious summary requests flood Patient Summary Generator | Medium | Implement rate limiting per patient session. Apply queue depth monitoring. |
| D-6 | Treatment Planner Agent | Oversized retrieval queries or excessive tool calls exhaust Treatment Planner Agent resources | Medium | Implement retrieval query size limits and tool call rate limits per session. |
| D-9 | Risk Stratification Model | High-volume risk inference requests saturate Risk Stratification Model capacity | Medium | Implement per-session inference rate limiting at the API Gateway. |
| D-14 | EHR Ingestion Queue | Malformed EHR events cause queue saturation blocking legitimate patient record ingestion | Medium | Implement queue depth monitoring with automatic backpressure. Apply message size limits. |
| D-15 | Clinical Audit Log | Excessive log entries cause disk exhaustion preventing legitimate audit log writes | Medium | Implement write rate limiting on audit log ingestion. Apply storage quota monitoring. |
| D-16 | Outcomes Telemetry and Physician Override Audit Store | Spurious override signals degrade learning loop's ability to incorporate legitimate feedback | Medium | Implement rate limiting on physician override ingestion. Apply anomaly detection to flag abnormal override volumes. |
| D-17 | HIPAA RBAC + Policy Engine | RBAC request flood causes policy engine unavailability blocking clinical data access | Medium | Implement access decision caching for recently evaluated policies. Apply rate limiting on policy evaluation requests. |
| D-18 | Consent and De-identification Guardrail | PHI processing request flood saturates de-identification capacity | Medium | Implement processing rate limits on guardrail requests. Apply queue-based load balancing. |
| E-9 | Risk Stratification Model | Adversarially manipulated risk scores trigger automated escalation to high-privilege interventions | Medium | Implement risk score range validation before triggering escalation workflows. |
| E-10 | Model Inference API Gateway | Compromised API Gateway escalates to access unauthorized model endpoints | Medium | Implement per-agent model access authorization at the gateway. |
| E-11 | HIPAA RBAC + Policy Engine | Attacker exploits RBAC engine vulnerability to escalate to administrative access | Medium | Apply multi-factor authentication and dual-control approval for all policy engine administrative operations. |
| E-12 | Consent and De-identification Guardrail | Attacker compromises guardrail to bypass consent enforcement accessing raw PHI | Medium | Implement strict access controls on guardrail configuration. Apply runtime enforcement of de-identification guarantees. |
| R-2 | Patient | Patient denies submitting EHR update events used as clinical decision basis | Low | Implement signed EHR update event receipts. Log all patient-submitted events. |
| R-4 | Patient Summary Generator | Summary Generator fails non-repudiable records of summaries delivered to patients | Low | Log all generated summaries with content hash and delivery timestamp in Clinical Audit Log. |
| I-11 | Clinical Guideline RAG Corpus | RAG Corpus inadvertently indexes patient data from clinical guidelines | Low | Sanitize all corpus documents for PHI before indexing. |
| I-12 | Medical Literature Vector Index | Vector Index exposes research data or cross-contaminates retrieval results | Low | Implement strict session isolation for all retrieval operations. |
| D-11 | Clinical Guideline RAG Corpus | Retrieval floods saturate Clinical Guideline RAG Corpus capacity | Low | Implement retrieval rate limits per session. Apply caching for commonly retrieved guidelines. |
| D-12 | Medical Literature Vector Index | Excessive retrieval queries degrade Medical Literature Vector Index availability | Low | Implement retrieval rate limits per session. Apply result caching. |
| I-17 | HIPAA RBAC + Policy Engine | RBAC engine leaks access control policies through error messages | Low | Sanitize all RBAC API error responses to prevent policy enumeration. |
| LLM-3 | Clinical LLM | Adversary extracts Clinical LLM clinical knowledge through targeted query patterns | Low | Implement query rate limiting and anomaly detection for systematic extraction patterns. |

---

## 9. Source Attribution


Per-finding attribution to external taxonomy frameworks (OWASP, CWE, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF). Populated by F-241 Wave 5.2 / T053 baseline regen. Each entry resolves against `schemas/taxonomy/*.yaml` per F-A2 referential-integrity contract.


```yaml
S-1:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-5:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-6:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
T-3:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-7:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-10:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-11:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-16:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
I-3:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-7:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-10:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
E-7:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
AG-1:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AG-2:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AG-7:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
LLM-1:
  - {taxonomy: owasp, id: LLM01, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
AGP-01:
  - {taxonomy: owasp, id: ASI06, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
S-2:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-3:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-7:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-8:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-9:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
T-1:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-2:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-4:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-5:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-6:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-8:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-9:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-12:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-14:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-15:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
R-5:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-6:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-9:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
I-1:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-2:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-4:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-5:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-6:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-8:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-9:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-13:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-14:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-15:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-16:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
D-1:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-3:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-4:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-5:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-7:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-8:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-10:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-13:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
E-1:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-2:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-3:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-4:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-5:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-6:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-8:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
AG-3:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AG-4:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AG-5:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AG-6:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AG-8:
  - {taxonomy: owasp, id: ASI01, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
LLM-2:
  - {taxonomy: owasp, id: LLM01, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
LLM-4:
  - {taxonomy: owasp, id: LLM01, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
LLM-5:
  - {taxonomy: owasp, id: LLM01, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
LLM-6:
  - {taxonomy: owasp, id: LLM01, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
AGP-02:
  - {taxonomy: owasp, id: ASI06, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
AGP-03:
  - {taxonomy: owasp, id: ASI06, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
S-4:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-10:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-11:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-12:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-13:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-14:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
T-13:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-17:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-18:
  - {taxonomy: owasp, id: A03, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
R-1:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-3:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-7:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-8:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-10:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-11:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-12:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-13:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
I-17:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-18:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
D-2:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-6:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-9:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-14:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-15:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-16:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-17:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-18:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
E-9:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-10:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-11:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-12:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
R-2:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-4:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
I-11:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-12:
  - {taxonomy: owasp, id: A02, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
D-11:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-12:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
LLM-3:
  - {taxonomy: owasp, id: LLM01, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
```
