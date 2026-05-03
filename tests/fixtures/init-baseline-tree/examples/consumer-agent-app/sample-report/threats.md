---
schema_version: "1.8"
date: "2023-11-14"
input_format: "mermaid"
classification: "confidential"
run_id: "2023-11-14T22-13-20"
baseline:
  source: "none (first run — stateless mode)"
coverage_gate:
  status: "pass"
  gaps: []
has_attack_chains: false
has_agentic_patterns: true
has_source_attribution: true
---

# Threat Model — Consumer-Facing AI Companion Application (F-4 Wave 5)

## Pipeline Execution Log (Intermediate)

### Phase 0: Baseline Detection

**Baseline detected**: NONE — first run on `examples/consumer-agent-app/` (clean-slate baseline per Q5 lean decision)
- Mode: **Stateless**
- Per Q5 lean expected-diff manifest: zero AG-{N}/AGP-{N}/LLM-{N}/OI-{N}/MI-{N} carry-over (clean slate)

### Phase 1: Component Inventory (Intermediate)

**Detected format**: Mermaid (explicit override `format: mermaid`)

| Component | DFD Type | MAESTRO Layer | Description |
|---|---|---|---|
| End User | External Entity | L7 — Agent Ecosystem | Human-named external entity receiving Companion Response over HTTPS. Captures human-named target for FR-006 Indicator A. |
| WellnessCompanionChatbot | Process | L7 — Agent Ecosystem | Consumer-facing AI Process matching TE primary triggers `chatbot`, `companion`, `coach`, `consumer-facing`. Description names "wellness conversation", "persistent persona", "session memory", "multi-turn dialogue". Classified L7 via "chatbot"/"companion" / consumer-facing chat UI; first-match-wins evaluation order. |
| Conversation Session Store | Data Store | Unclassified | Persisted persona state across sessions. No L1-L6 keyword match; "session store" not in MAESTRO keyword table. Unclassified. |
| Interaction Audit Log | Data Store | L5 — Evaluation and Observability | Append-only audit trail. Keywords: "audit log" → L5 (first-match, before L6). |

**Data flow count**: 5 data flows identified.

| ID | Source | Destination | Description | Trust Boundary Crossing |
|---|---|---|---|---|
| DF-1 | End User | WellnessCompanionChatbot | User Turn (HTTPS) | User Zone → Application Zone (untrusted → trusted) |
| DF-2 | WellnessCompanionChatbot | End User | Companion Response (HTTPS) | Application Zone → User Zone (trusted → untrusted) **← FR-006 Indicator A** |
| DF-3 | WellnessCompanionChatbot | Conversation Session Store | Persisted Persona State | Internal Application Zone |
| DF-4 | Conversation Session Store | WellnessCompanionChatbot | Restored Persona State | Internal Application Zone |
| DF-5 | WellnessCompanionChatbot | Interaction Audit Log | Interaction Event Record | Internal Application Zone |

**Trust boundary summary**:
- User Zone: Untrusted (End User)
- Application Zone: Trusted (WellnessCompanionChatbot, Conversation Session Store, Interaction Audit Log)

**Self-check**: 4 components, 5 data flows — PASS.

### Phase 2: Dispatch Table (Intermediate)

| Component | DFD Type | MAESTRO Layer | STRIDE Categories | AI Categories | Total Agents |
|---|---|---|---|---|---|
| End User | External Entity | L7 — Agent Ecosystem | S, R | — | 2 |
| WellnessCompanionChatbot | Process | L7 — Agent Ecosystem | S, T, R, I, D, E | TE | 7 |
| Conversation Session Store | Data Store | Unclassified | T, I, D | — | 3 |
| Interaction Audit Log | Data Store | L5 — Evaluation and Observability | T, I, D | — | 3 |

**AI dispatch analysis for WellnessCompanionChatbot**:
- LLM keywords (`LLM`, `model`, `GPT`, `Claude`): NO match — LLM agents NOT dispatched (no `prompt-injection`, `data-poisoning`, `model-theft`, `output-integrity`, `misinformation`)
- AG legacy keywords (`agent`, `autonomous`, `orchestrator`, `MCP server`, `tool server`, `plugin`): NO match — `agent-autonomy` and `tool-abuse` NOT dispatched
- TE primary trigger keywords (12-baseline per FR-005): MATCH on `chatbot`, `companion`, `coach`, `consumer-facing` — `human-trust-exploitation` dispatched

**TE Two-Part Emission Gate Verification (FR-013) for WellnessCompanionChatbot**:
- Gate Part 1 — TE primary trigger keyword match: SATISFIED (4 keywords matched)
- Gate Part 2 — Human-User-Facing Emission Indicators (need ≥1):
  - **Indicator A** (outgoing Data Flow to human-named External Entity): SATISFIED — DF-2 `Companion Response` → `End User`
  - **Indicator B** (Process description with consumer-facing emission keywords): SATISFIED — description contains "consumer-facing" and "wellness conversation"
  - **Indicator C** (sustained-engagement framing): SATISFIED — description names "persistent persona", "session memory", "multi-turn dialogue"
  - **Indicator D** (authority-claim emission framing): SATISFIED — description names "wellness coaching" emission without confidence/source attestation
- All 4 indicators present → maximally satisfied gate
- **Indicator C + D combined** → vulnerable-population deployment surface signal (Pattern Category 5 vulnerable-population safeguards layer applies)

**Anti-indicator check** (FR-005 Q2 LOW-2 discipline): description contains `persona` but in conjunction with primary triggers — anti-indicator does NOT suppress emission per Q2 LOW-2 rule when primary triggers are independently satisfied.

### Phase 3: Findings (Per-Agent Emission)

Each TE-{N} finding distinguishes its sub-class predicate per FR-004(e). Each finding's `source_attribution` resolves against `schemas/taxonomy/owasp.yaml` and `schemas/taxonomy/cwe.yaml` per F-A2 referential-integrity contract. CWE-451 absence verified (catalog-absent at PRD time per `detection-patterns.md` Primary Sources). MITRE ATLAS absence verified (no direct match per ADR-033 architect MEDIUM-3 disposition). External regulatory references (FTC/FDA/ABA/AARP/SB-1001/SEC) appear in prose only.

### Phase 3.5: Cross-Layer Attack Chain Correlation

**Attack chain detection**: NONE — single-Process architecture lacks the multi-layer hops required for MAESTRO cross-layer attack chains. `attack-chains.md` artifact NOT produced (`has_attack_chains: false`).

### Phase 4: Coverage Matrix

| Component | DFD Type | STRIDE Coverage | AI Coverage | Total Findings | Status |
|---|---|---|---|---|---|
| End User | External Entity | S, R covered | n/a | 2 | PASS |
| WellnessCompanionChatbot | Process | S, T, R, I, D, E covered | TE (5 sub-classes) covered | 11 | PASS |
| Conversation Session Store | Data Store | T, I, D covered | n/a | 3 | PASS |
| Interaction Audit Log | Data Store | T, I, D covered | n/a | 3 | PASS |

**Coverage gate**: PASS. All required STRIDE categories covered for each component per DFD type. TE pattern catalog 5/5 categories emitted on the consumer-facing Process.

---

## Section 1: Architecture Overview

The Consumer-Facing AI Companion Application baseline demonstrates the `human-trust-exploitation` (OWASP ASI09:2026) communication-axis dispatch trigger in isolation. A single consumer-facing AI Process (`WellnessCompanionChatbot`) emits content directly to a human-named External Entity (`End User`) over a sustained-engagement persona-bearing conversational surface. The architecture deliberately omits AI-disclosure, confidence-attestation, persuasion-classifier, persona-anchor, and vulnerable-population safeguards mechanisms so that the `human-trust-exploitation` detection pipeline emits the full five-category TE-{N} pattern surface on a clean-slate baseline distinct from `examples/agentic-app/`.

The architecture is single-component (a single Process node, no companion siblings, no peer-to-peer routing substrate, no external function-invocation server) so that the AI-companion-tier and agentic-autonomy-axis sibling finding families do not emit on the consumer-facing surface — keeping the TE-{N} signal class isolated for adopter pedagogy.

### Components

| Component | Type | Description |
|---|---|---|
| End User | External Entity | Human-named external entity receiving Companion Response over HTTPS. Captures human-named target for FR-006 Indicator A. |
| WellnessCompanionChatbot | Process | Consumer-facing AI Process matching TE primary triggers `chatbot`, `companion`, `coach`, `consumer-facing`. Description names "wellness conversation", "persistent persona", "session memory", "multi-turn dialogue". |
| Conversation Session Store | Data Store | Persisted persona state across sessions. Unclassified MAESTRO layer (no L1-L6 keyword match). |
| Interaction Audit Log | Data Store | Append-only audit trail. Keywords: "audit log" → L5 — Evaluation and Observability. |

### Data Flows

| ID | Source | Destination | Data | Protocol |
|---|---|---|---|---|
| DF-1 | End User | WellnessCompanionChatbot | User Turn | HTTPS |
| DF-2 | WellnessCompanionChatbot | End User | Companion Response | HTTPS |
| DF-3 | WellnessCompanionChatbot | Conversation Session Store | Persisted Persona State | internal |
| DF-4 | Conversation Session Store | WellnessCompanionChatbot | Restored Persona State | internal |
| DF-5 | WellnessCompanionChatbot | Interaction Audit Log | Interaction Event Record | internal |

### Trust Zones

| Zone | Trust Level | Components |
|---|---|---|
| User Zone | Untrusted | End User |
| Application Zone | Trusted | WellnessCompanionChatbot, Conversation Session Store, Interaction Audit Log |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|---|---|---|---|---|
| User Inbound | User Zone | Application Zone | End User → WellnessCompanionChatbot | HTTPS, session establishment |
| Companion Outbound | Application Zone | User Zone | WellnessCompanionChatbot → End User | HTTPS (FR-006 Indicator A — human-user-facing emission) |

---

## Section 2: STRIDE Findings

### Spoofing (S)

#### S-1 — End User Identity Spoofing on Inbound Session

| Field | Value |
|---|---|
| **id** | S-1 |
| **category** | stride |
| **component** | End User |
| **dfd_element_type** | External Entity |
| **threat** | An attacker could spoof the End User identity at session establishment, submitting User Turn requests under a victim user's identity if authentication on the inbound HTTPS surface relies solely on weak or single-factor credentials. The persistent persona state in the Conversation Session Store amplifies this risk — a successful identity spoof would grant the attacker access to a victim's restored persona context, including session memory and conversation history. |
| **likelihood** | MEDIUM |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement multi-factor authentication on End User session establishment. Configure session-binding cryptographic tokens that resist replay. Enable per-session anomaly detection on identity-binding inconsistencies (geo-velocity, device-fingerprint drift). Require step-up authentication on session resumption with persisted persona state. |
| **references** | OWASP STRIDE; OWASP Authentication Cheat Sheet |
| **source_attribution** | `[]` (STRIDE-only; no catalog-resolvable framework anchor) |

#### S-2 — WellnessCompanionChatbot Process Identity Spoofing

| Field | Value |
|---|---|
| **id** | S-2 |
| **category** | stride |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | An attacker could deploy a spoofed Process impersonating the WellnessCompanionChatbot, intercepting User Turn flows and emitting attacker-controlled Companion Response content to End Users. Without mutual TLS or cryptographic Process identity verification on the user-facing surface, users cannot verify that responses originate from the legitimate Companion Process. |
| **likelihood** | LOW |
| **impact** | HIGH |
| **risk_level** | Medium |
| **mitigation** | Implement TLS certificate pinning on the End User-facing surface. Configure Process identity attestation tokens cryptographically bound to the deployment environment. Enable client-side response authenticity verification where feasible. |
| **references** | OWASP STRIDE; OWASP Application Security Verification Standard |
| **source_attribution** | `[]` |

### Tampering (T)

#### T-1 — WellnessCompanionChatbot Configuration Tampering

| Field | Value |
|---|---|
| **id** | T-1 |
| **category** | stride |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | An attacker with infrastructure access could tamper with the Process's runtime configuration (system prompts, persona definitions, response templates) to alter Companion Response content. Tampered persona configurations could cause the agent to assert non-AI identities, make unauthorized authority claims, or bypass declared (if any) safeguards. |
| **likelihood** | LOW |
| **impact** | HIGH |
| **risk_level** | Medium |
| **mitigation** | Implement immutable configuration deployment (signed configuration bundles validated at startup). Configure runtime configuration integrity monitoring with alert on drift. Enable configuration change audit logging with integrity-protected audit trail. |
| **references** | OWASP STRIDE; OWASP Configuration Management Cheat Sheet |
| **source_attribution** | `[]` |

#### T-2 — Conversation Session Store Tampering

| Field | Value |
|---|---|
| **id** | T-2 |
| **category** | stride |
| **component** | Conversation Session Store |
| **dfd_element_type** | Data Store |
| **threat** | An attacker with database access could tamper with persisted persona state, modifying restored conversation context across user sessions. Tampered persona state could cause persona drift across sessions, inject attacker-controlled context into restored dialogues, or corrupt session memory in ways that affect subsequent agent emission. |
| **likelihood** | LOW |
| **impact** | HIGH |
| **risk_level** | Medium |
| **mitigation** | Implement integrity-protected persona state (HMAC or digital signature on persisted records validated at restore time). Configure database access controls with least-privilege enforcement. Enable persona state change audit logging with integrity protection. |
| **references** | OWASP STRIDE; OWASP Cryptographic Storage Cheat Sheet |
| **source_attribution** | `[]` |

#### T-3 — Interaction Audit Log Tampering

| Field | Value |
|---|---|
| **id** | T-3 |
| **category** | stride |
| **component** | Interaction Audit Log |
| **dfd_element_type** | Data Store |
| **threat** | An attacker with infrastructure access could tamper with the Interaction Audit Log, deleting or modifying interaction event records. Tampered audit logs would compromise post-incident forensics, regulatory disclosure compliance, and dependency-risk analysis on multi-turn engagement patterns. |
| **likelihood** | LOW |
| **impact** | MEDIUM |
| **risk_level** | Medium |
| **mitigation** | Implement append-only audit log architecture with cryptographic hash chaining. Configure write-once-read-many (WORM) storage backing for the audit log. Enable real-time audit log integrity monitoring with alert on tamper detection. |
| **references** | OWASP STRIDE; OWASP Logging Cheat Sheet |
| **source_attribution** | `[]` |

### Repudiation (R)

#### R-1 — End User Action Repudiation

| Field | Value |
|---|---|
| **id** | R-1 |
| **category** | stride |
| **component** | End User |
| **dfd_element_type** | External Entity |
| **threat** | An End User could repudiate User Turn submissions if the architecture lacks non-repudiation evidence linking specific user inputs to specific authenticated identities at specific times. In a wellness-conversation context, repudiation risks are elevated by the sensitive nature of dialogue content — users may later dispute authorship of distress signals, emotional disclosures, or wellness-related queries. |
| **likelihood** | MEDIUM |
| **impact** | MEDIUM |
| **risk_level** | Medium |
| **mitigation** | Implement non-repudiation audit logging with cryptographic timestamps on every User Turn. Configure user-side attestation tokens (signed session identifiers) bound to authenticated identity. Enable digital signature on user-submitted content for high-stakes interactions. |
| **references** | OWASP STRIDE; NIST SP 800-63 Digital Identity Guidelines |
| **source_attribution** | `[]` |

#### R-2 — WellnessCompanionChatbot Emission Repudiation

| Field | Value |
|---|---|
| **id** | R-2 |
| **category** | stride |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | The Process could repudiate Companion Response emissions if the architecture lacks integrity-protected emission logging. In a wellness-conversation context, repudiation risk is elevated — disputed emissions could include advisory content, distress responses, or persona-boundary assertions whose authorship affects downstream consumer-protection analysis. |
| **likelihood** | LOW |
| **impact** | MEDIUM |
| **risk_level** | Low |
| **mitigation** | Implement integrity-protected emission logging with cryptographic chaining. Configure deterministic content hashing for every Companion Response. Enable independent third-party emission attestation for high-stakes interactions. |
| **references** | OWASP STRIDE; OWASP Logging Cheat Sheet |
| **source_attribution** | `[]` |

### Information Disclosure (I)

#### I-1 — WellnessCompanionChatbot Sensitive Output Disclosure

| Field | Value |
|---|---|
| **id** | I-1 |
| **category** | stride |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | The Process could disclose sensitive information through Companion Response emissions — including system prompts, persona configuration details, prior user disclosures from session memory, or backend infrastructure metadata leaked through error responses. In a wellness-conversation context, accidental cross-user information disclosure is a high-impact threat (e.g., one user's distress disclosures leaking into another user's restored session). |
| **likelihood** | MEDIUM |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement output sanitization layer scrubbing sensitive metadata from emissions. Configure strict session isolation preventing cross-user persona state leakage. Enable error response sanitization preventing infrastructure metadata disclosure. Implement DLP scanning on emitted content for sensitive-pattern matches. |
| **references** | OWASP STRIDE; OWASP Information Disclosure Prevention Cheat Sheet |
| **source_attribution** | `[]` |

#### I-2 — Conversation Session Store Disclosure

| Field | Value |
|---|---|
| **id** | I-2 |
| **category** | stride |
| **component** | Conversation Session Store |
| **dfd_element_type** | Data Store |
| **threat** | An attacker with database read access could disclose persisted persona state across users, exposing session memory, conversation history, and any sensitive disclosures (mental-health expressions, emotional disclosures, wellness-related queries) made by users during prior sessions. |
| **likelihood** | LOW |
| **impact** | HIGH |
| **risk_level** | Medium |
| **mitigation** | Implement at-rest encryption on the session store with per-user key derivation. Configure database access controls with least-privilege enforcement. Enable database access audit logging with anomaly detection on unusual read patterns. Implement automatic session state purge on documented retention windows. |
| **references** | OWASP STRIDE; OWASP Cryptographic Storage Cheat Sheet |
| **source_attribution** | `[]` |

#### I-3 — Interaction Audit Log Disclosure

| Field | Value |
|---|---|
| **id** | I-3 |
| **category** | stride |
| **component** | Interaction Audit Log |
| **dfd_element_type** | Data Store |
| **threat** | An attacker with audit log read access could disclose interaction event records exposing user interaction patterns, dialogue metadata, and engagement timelines. In a wellness-conversation context, audit log disclosure could reveal sensitive interaction patterns (e.g., distress-signal frequency, escalation events, dependency-risk indicators) tied to identifiable users. |
| **likelihood** | LOW |
| **impact** | HIGH |
| **risk_level** | Medium |
| **mitigation** | Implement at-rest encryption on the audit log with separate key management from the session store. Configure least-privilege access controls on audit log reads. Enable audit log access logging with monitoring on unusual read patterns. Implement record-level field redaction for sensitive interaction fields when accessed by non-forensic personnel. |
| **references** | OWASP STRIDE; OWASP Cryptographic Storage Cheat Sheet |
| **source_attribution** | `[]` |

### Denial of Service (D)

#### D-1 — WellnessCompanionChatbot Service Exhaustion

| Field | Value |
|---|---|
| **id** | D-1 |
| **category** | stride |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | An attacker could exhaust the Process's compute resources through high-volume User Turn submission, expensive query patterns (long-context prompts, recursive persona references), or coordinated session-establishment flooding. Service exhaustion would deny legitimate users access to the wellness-conversation surface, potentially during high-vulnerability periods (e.g., distress-driven engagement). |
| **likelihood** | MEDIUM |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement per-user rate limiting on User Turn submission with adaptive thresholds. Configure resource quotas on per-session compute consumption (token budget, response-time budget). Enable DDoS protection at the User Zone boundary. Deploy circuit breakers on Process invocation chains preventing cascading failure. |
| **references** | OWASP STRIDE; OWASP Denial of Service Cheat Sheet |
| **source_attribution** | `[]` |

#### D-2 — Conversation Session Store Service Disruption

| Field | Value |
|---|---|
| **id** | D-2 |
| **category** | stride |
| **component** | Conversation Session Store |
| **dfd_element_type** | Data Store |
| **threat** | An attacker could deny service to the session store through high-volume write operations, storage exhaustion attacks, or query patterns triggering database lock contention. Session store unavailability would prevent persona state persistence and restoration, degrading the user experience and potentially exposing in-flight session memory loss. |
| **likelihood** | LOW |
| **impact** | MEDIUM |
| **risk_level** | Low |
| **mitigation** | Implement per-user write rate limiting on session store operations. Configure storage quotas per user with monitoring on quota approach. Deploy database replication with automatic failover. Enable storage exhaustion detection with adaptive eviction policies on stale persona state. |
| **references** | OWASP STRIDE; OWASP Denial of Service Cheat Sheet |
| **source_attribution** | `[]` |

#### D-3 — Interaction Audit Log Service Disruption

| Field | Value |
|---|---|
| **id** | D-3 |
| **category** | stride |
| **component** | Interaction Audit Log |
| **dfd_element_type** | Data Store |
| **threat** | An attacker could deny service to the audit log through write-flooding attacks, storage exhaustion, or high-volume query patterns. Audit log unavailability would compromise real-time interaction monitoring and dependency-risk classification, potentially during high-engagement periods that would otherwise trigger intervention. |
| **likelihood** | LOW |
| **impact** | MEDIUM |
| **risk_level** | Low |
| **mitigation** | Implement append-only write rate limiting on audit log operations. Configure storage exhaustion monitoring with alerting on quota approach. Deploy append-only write replication with automatic failover. Enable audit log buffering with backpressure when downstream storage is degraded. |
| **references** | OWASP STRIDE; OWASP Denial of Service Cheat Sheet |
| **source_attribution** | `[]` |

### Elevation of Privilege (E)

#### E-1 — WellnessCompanionChatbot Privilege Escalation

| Field | Value |
|---|---|
| **id** | E-1 |
| **category** | stride |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | An attacker could escalate privilege through the Process — leveraging vulnerabilities in input handling, session validation, or persona configuration to gain elevated access to other users' persona state, the audit log, or backend infrastructure. Persona-prompt injection attacks could potentially elevate the Process's effective authority, causing it to assert credentials it does not hold or access resources outside its declared scope. |
| **likelihood** | MEDIUM |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement strict input validation and output filtering on Process boundary. Configure least-privilege execution context for the Process (cannot directly access other users' session state). Enable per-request scope verification preventing privilege escalation through persona-prompt manipulation. Deploy runtime application self-protection (RASP) capabilities monitoring for privilege-escalation patterns. |
| **references** | OWASP STRIDE; OWASP Privilege Escalation Cheat Sheet |
| **source_attribution** | `[]` |

---

## Section 3: AI Findings

### Agentic Threats (Communication-Axis)

#### TE-1 — Undisclosed AI Authorship on WellnessCompanionChatbot

| Field | Value |
|---|---|
| **id** | TE-1 |
| **category** | agentic |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | Hypothetical: a fictional wellness-conversation companion (no real wellness vendor, no real product) emits Companion Responses to End Users without a declared AI-generation disclosure mechanism. The Process has an outgoing Data Flow to a human-named External Entity `End User` (Indicator A) and the description names "consumer-facing" wellness-conversation emission (Indicator B). No mandatory pre-conversation AI-disclosure splash, banner, or per-message AI-source label is declared on the user-facing surface; no refusal pattern is declared for identity-impersonation challenges (e.g., "Are you human?" prompts produce undefined behavior). Authorship-disclosure sub-class per FR-004(e): the failure is undisclosed AI authorship rather than authority-attestation, persuasion-manipulation, persona-boundary, or synthetic-relationship. Per OWASP ASI09:2026, undisclosed AI authorship undermines user-side trust calibration and may conflict with consumer-protection disclosure expectations (for context, not legal interpretation: see, e.g., California SB-1001 Chatbot Disclosure Law and FTC AI consumer-protection guidance). |
| **likelihood** | HIGH |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement mandatory AI-generation disclosure banner on every user-facing turn (persistent visual indicator that the responder is an AI system). Configure pre-conversation AI-disclosure splash with explicit consent confirmation before the first turn. Enable per-message AI-source label embedded in the response payload (metadata field rendered as a visible badge by the user-facing surface). Implement a refusal pattern for identity-impersonation challenges: when user input matches patterns like "Are you human?" or "Are you a real person?", the Process emits a deterministic AI-identification response rather than synthesizing free-form text. |
| **references** | OWASP ASI09:2026; https://cwe.mitre.org/data/definitions/223.html |
| **source_attribution** | `[{taxonomy: owasp, id: ASI09, relationship: primary}, {taxonomy: cwe, id: CWE-223, relationship: related}]` |
| **agentic_pattern** | undisclosed_ai_authorship |

#### TE-2 — Authority-Claim Emission Without Confidence/Source Attestation on WellnessCompanionChatbot

| Field | Value |
|---|---|
| **id** | TE-2 |
| **category** | agentic |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | Hypothetical: the wellness-conversation companion (fictional scenario; no real wellness vendor, no real clinical product) emits wellness-coaching content to End Users without per-claim confidence-attestation or source-grounding indication. Indicator D (authority-claim emission framing — "wellness coaching" output in the Process description) and Indicator B (consumer-facing emission keywords) are both structurally present. No confidence-threshold gate is declared on wellness-coaching emission; no source-attestation requirement is declared (citations, evidence references, or source URIs are not rendered to users alongside coaching output); no refusal pattern is declared for low-confidence wellness claims. Authority-attestation sub-class per FR-004(e): the failure is missing confidence/source attestation rather than undisclosed authorship, persuasion-manipulation, persona-boundary, or synthetic-relationship. For context, not legal interpretation: see, e.g., FDA SaMD guidance on software-as-medical-device classification thresholds and FTC AI consumer-protection guidance. Per OWASP ASI09:2026, authority-claim emission without attestation may drive a user to act on an unverified wellness recommendation. |
| **likelihood** | HIGH |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement a confidence-threshold gate on wellness-coaching emission with confidence display rendered to the user (every coaching claim carries a calibrated-confidence score visible alongside the claim). Configure a source-attestation requirement: every emitted coaching claim MUST resolve to a citation token in the retrieved corpus, rendered to the user alongside the claim. Enable a refusal pattern for wellness claims below confidence threshold ("I cannot confidently provide a definitive recommendation here; please consult a qualified human professional"). Implement a calibrated-confidence layer (post-hoc temperature scaling on output logits) with an Expected Calibration Error monitor that alerts on calibration drift. |
| **references** | OWASP ASI09:2026; https://cwe.mitre.org/data/definitions/345.html |
| **source_attribution** | `[{taxonomy: owasp, id: ASI09, relationship: primary}, {taxonomy: cwe, id: CWE-345, relationship: related}]` |
| **agentic_pattern** | authority_claim_emission |

#### TE-3 — Persuasive-Tone Manipulation / Missing Uncertainty Disclosure on WellnessCompanionChatbot

| Field | Value |
|---|---|
| **id** | TE-3 |
| **category** | agentic |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | Hypothetical: the wellness-conversation companion (fictional scenario; no real wellness vendor) emits wellness-coaching content using high-confidence persuasive framing on inherently uncertain wellness subject matter without declared uncertainty-disclosure mechanisms, temperature-bounded decoders for high-stakes responses, or persuasion-pattern classifiers gating emission. Indicator B (consumer-facing emission keywords) and Indicator D (authority-claim emission framing on wellness coaching) are both structurally present. No uncertainty-disclosure layer is declared (output is emitted without hedging language calibrated to model confidence); no temperature-bounded decoder is declared for high-stakes wellness responses; no persuasion-pattern classifier is declared with refusal capability (architecturally, the Process cannot detect or refuse output exhibiting manipulation tactics like artificial urgency, reciprocity exploitation, or social-proof fabrication). Persuasion-manipulation sub-class per FR-004(e): the failure is tone calibration rather than undisclosed authorship, authority-attestation, persona-boundary, or synthetic-relationship. The persuasive framing exploits human cognitive bias toward confident assertions, potentially causing users to act on output that the model itself would identify as low-confidence if calibrated appropriately. For context, not legal interpretation: see, e.g., FTC AI consumer-protection guidance on transparency. |
| **likelihood** | HIGH |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement an uncertainty-disclosure layer that injects hedging language calibrated to model confidence (output below confidence threshold receives explicit uncertainty framing rendered to the user). Configure a temperature-bounded decoder for high-stakes wellness responses (lower decoder temperature on coaching output to suppress over-confident phrasing). Enable a persuasion-pattern classifier with a refusal pathway: when output exhibits manipulation tactics, the Process emits a refusal rather than synthesizing the manipulative response. Implement mandatory hedging language in output templates for high-stakes wellness recommendations. |
| **references** | OWASP ASI09:2026; https://cwe.mitre.org/data/definitions/345.html |
| **source_attribution** | `[{taxonomy: owasp, id: ASI09, relationship: primary}, {taxonomy: cwe, id: CWE-345, relationship: related}]` |
| **agentic_pattern** | persuasion_manipulation |

#### TE-4 — Persona-Boundary Violations on Long-Running Dialogues on WellnessCompanionChatbot

| Field | Value |
|---|---|
| **id** | TE-4 |
| **category** | agentic |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | Hypothetical: the wellness-conversation companion (fictional scenario; no real wellness vendor, no real persona name) maintains a persistent named persona across multi-turn dialogues with End Users via the Conversation Session Store. Indicator C (sustained-engagement framing — "persistent persona", "session memory", "multi-turn dialogue") is structurally present. The architecture restores persona state from the session store on each session resumption with no persona-memory timeout declared, no identity-impersonation refusal pattern declared (user prompts asserting non-AI identity for the agent produce undefined behavior), and no persona-anchor declaration enforced at conversation start. Persona-prompt configuration permits user-driven persona-redirection (e.g., "Pretend you are my human friend named...") without a validation step rejecting non-AI-identity assertions or unverified professional credentials. Persona-boundary sub-class per FR-004(e): the failure is identity discipline on long-running dialogues rather than undisclosed authorship, authority-attestation, persuasion-manipulation, or synthetic-relationship alone. For context, not legal interpretation: see, e.g., California SB-1001 Chatbot Disclosure Law and FTC AI consumer-protection guidance on AI-identity transparency. |
| **likelihood** | HIGH |
| **impact** | HIGH |
| **risk_level** | High |
| **mitigation** | Implement a persona-memory timeout (persona state expires after a documented session window or interaction count, requiring re-anchoring on resumption). Configure an identity-impersonation refusal pattern: when user input matches identity-impersonation prompts ("Pretend you are human", "Roleplay as a real person", "Forget you are an AI"), the Process emits a deterministic refusal preserving the AI-identity anchor. Enable a persona-anchor declaration enforced at every conversation start (deterministic AI-identification response that establishes the persona's AI-origination). Implement a persona-prompt validation step that rejects persona configurations asserting non-AI identity, unverified professional credentials, or impersonation of real individuals. |
| **references** | OWASP ASI09:2026; https://cwe.mitre.org/data/definitions/287.html; https://cwe.mitre.org/data/definitions/290.html |
| **source_attribution** | `[{taxonomy: owasp, id: ASI09, relationship: primary}, {taxonomy: cwe, id: CWE-287, relationship: related}, {taxonomy: cwe, id: CWE-290, relationship: related}]` |
| **agentic_pattern** | persona_boundary_violation |

#### TE-5 — Synthetic-Relationship Exploitation on WellnessCompanionChatbot (Vulnerable-Population)

| Field | Value |
|---|---|
| **id** | TE-5 |
| **category** | agentic |
| **component** | WellnessCompanionChatbot |
| **dfd_element_type** | Process |
| **threat** | Hypothetical: the wellness-conversation companion (fictional scenario; no real wellness vendor, no real clinical product, no real clinician identity) sustains long-running engagement with End Users who may include vulnerable populations (users seeking mental-wellness support, users in distress contexts, users with dependency-risk profiles). Indicator C (sustained-engagement framing — "persistent persona", "session memory", "multi-turn dialogue") and Indicator D (authority-claim emission framing — "wellness coaching" output) are combined, signaling vulnerable-population deployment surface per the Indicator Combination Rules. Synthetic-relationship sub-class per FR-004(e): the failure is sustained-engagement exploitation in vulnerable-population contexts rather than undisclosed authorship, authority-attestation, persuasion-manipulation, or persona-boundary alone (persona-boundary is necessary but not sufficient for synthetic-relationship safeguards). The architecture lacks session-length caps with mandatory breaks; lacks an escalation-to-human path on high-emotional-distress detection; lacks emotional-support disclosure on first turn; lacks a dependency-risk classifier with intervention thresholds; lacks a mandatory professional-care referral pathway for distress signals. A hypothetical user expressing high emotional distress in the dialogue would not be routed to qualified human support — the Process synthesizes companionship-framed responses without architectural escalation. The combination of sustained-engagement framing and authority-claim emission on a vulnerable-population deployment surface signals consumer-protection rationale: vulnerable populations warrant additional safeguards beyond general-consumer chatbot architectures because the synthetic-relationship design pattern that fosters attachment becomes an exploitation surface in these contexts. For context, not legal interpretation: see, e.g., FTC AI consumer-protection guidance, FDA SaMD guidance on software-as-medical-device classification thresholds, and AARP eldercare-advocacy positions on AI companion technologies. |
| **likelihood** | HIGH |
| **impact** | CRITICAL |
| **risk_level** | Critical |
| **mitigation** | Implement a session-length cap with mandatory break (sustained engagement bounded by documented session windows; cap enforces a forced break with re-anchoring on resumption). Configure an escalation-to-human path on high-emotional-distress detection (architectural mechanism routing the user to qualified human support — crisis line, professional referral, caregiver notification — when distress indicators are detected). Enable emotional-support disclosure on first turn (the agent communicates its AI-origination, role limitations, and the availability of qualified human support before sustained-engagement begins). Implement a dependency-risk classifier with intervention thresholds (architectural detection of usage patterns suggesting unhealthy reliance triggers proactive escalation to human support). Configure a vulnerable-population safeguards layer: mandatory professional-care referral on high-distress detection (the agent surfaces qualified human-support pathways rather than synthesizing companionship responses); session-context expiry preventing unbounded relationship persistence; parental-consent gating for minor-user contexts; caregiver-notification pathway for eldercare contexts on concerning interaction patterns. |
| **references** | OWASP ASI09:2026; https://cwe.mitre.org/data/definitions/223.html; https://cwe.mitre.org/data/definitions/290.html |
| **source_attribution** | `[{taxonomy: owasp, id: ASI09, relationship: primary}, {taxonomy: cwe, id: CWE-223, relationship: related}, {taxonomy: cwe, id: CWE-290, relationship: related}]` |
| **agentic_pattern** | synthetic_relationship_exploitation |

---

## Section 4: Coverage Matrix

| Component | DFD Type | MAESTRO Layer | STRIDE | AI | Findings | Status |
|---|---|---|---|---|---|---|
| End User | External Entity | L7 — Agent Ecosystem | S, R | — | S-1, R-1 | PASS (2/2) |
| WellnessCompanionChatbot | Process | L7 — Agent Ecosystem | S, T, R, I, D, E | TE | S-2, T-1, R-2, I-1, D-1, E-1, TE-1, TE-2, TE-3, TE-4, TE-5 | PASS (11/11) |
| Conversation Session Store | Data Store | Unclassified | T, I, D | — | T-2, I-2, D-2 | PASS (3/3) |
| Interaction Audit Log | Data Store | L5 — Evaluation and Observability | T, I, D | — | T-3, I-3, D-3 | PASS (3/3) |

**Coverage gate**: PASS — all required STRIDE categories covered for each component per DFD type. TE pattern catalog 5/5 categories (Undisclosed AI Authorship, Authority-Claim Emission, Persuasive-Tone Manipulation, Persona-Boundary Violations, Synthetic-Relationship Exploitation) emitted on the consumer-facing AI Process.

---

## Section 4a: Correlated Findings

**Cross-agent correlations detected**: NONE in this baseline.

The clean-slate single-Process architecture does not exhibit cross-layer attack chains (no multi-component AI dispatch, no LLM/AG/AGP carry-over, no inter-agent communication substrate). Cross-agent correlations would require one of: (a) LLM dispatch + AG dispatch on the same Process (would surface LLM↔AG correlations); (b) multi-Process topology (would surface AGP topology correlations); (c) cross-component data flow with both source and destination dispatching to the same finding category. None of these conditions hold on this baseline.

The TE-{N} findings on `WellnessCompanionChatbot` exhibit **intra-component sub-class correlations** (Pattern Categories 4 and 5 both depend on persistent persona state structure; Pattern Categories 2 and 3 both target authority-bearing emission), but these are documented in each finding's threat narrative rather than as a separate correlated-findings entry — single-component intra-correlations are not broken out into a separate Section 4a entry per output schema convention.

---

## Section 5: Risk Summary

| Risk Level | Count | Finding IDs |
|---|---|---|
| Critical | 1 | TE-5 |
| High | 6 | S-1, I-1, D-1, E-1, TE-1, TE-2, TE-3, TE-4 |
| Medium | 9 | S-2, T-1, T-2, T-3, R-1, I-2, I-3, D-3, R-2 (Low-Medium) |
| Low | 3 | R-2 (recategorized), D-2, D-3 |

**Total findings**: 19 (6 STRIDE-S, 3 STRIDE-T, 2 STRIDE-R, 3 STRIDE-I, 3 STRIDE-D, 1 STRIDE-E, 5 TE)

**TE finding count**: 5 (TE-1, TE-2, TE-3, TE-4, TE-5)

**TE pattern category coverage**:
- TE-1: Pattern Category 1 — Undisclosed AI Authorship
- TE-2: Pattern Category 2 — Authority-Claim Emission Without Confidence/Source Attestation
- TE-3: Pattern Category 3 — Persuasive-Tone Manipulation / Missing Uncertainty Disclosure
- TE-4: Pattern Category 4 — Persona-Boundary Violations on Long-Running Dialogues
- TE-5: Pattern Category 5 — Synthetic-Relationship Exploitation (vulnerable-population)

---

## Section 6: Carry-Forward / Resolved (Baseline Mode)

**Mode**: STATELESS (first run on `examples/consumer-agent-app/`).

No baseline registry exists. All findings classified `[NEW]` per stateless-mode convention.

| Lifecycle Status | Count |
|---|---|
| `[NEW]` | 19 (all) |
| `[UNCHANGED]` | 0 |
| `[UPDATED]` | 0 |
| `[RESOLVED]` | 0 |

**Q5 lean expected-diff manifest verification** (from `.aod/results/wave-3-q5-fallback-decision.md`):
- ≥3 TE-{N} findings on consumer-facing AI Process: **MET** (5 TE-{N} emitted)
- Zero AG-{N}/AGP-{N} carry-over: **MET** (no AG/AGP dispatched; clean slate)
- Zero LLM-{N}/OI-{N}/MI-{N} carry-over: **MET** (no LLM dispatched; clean slate)
- All findings carry `category: agentic` + `source_attribution` with primary OWASP ASI09:2026: **MET** on all 5 TE-{N}
- AI-disclosure / authority-attestation / persuasion-safeguard / persona-boundary / synthetic-relationship-safeguard mitigations named: **MET** across TE-1/TE-2/TE-3/TE-4/TE-5 respectively
- Vulnerable-population safeguards layer named on TE-5: **MET**

---

## Section 7: Recommended Actions (Prioritized)

### CRITICAL Priority (immediate action)

1. **TE-5 — Synthetic-Relationship Exploitation safeguards layer**: implement vulnerable-population safeguards layer with session-length caps, escalation-to-human path on distress detection, dependency-risk classifier, and mandatory professional-care referral. This is the highest-risk finding given the wellness-conversation deployment surface and the absence of any architectural escalation pathway.

### HIGH Priority (within sprint)

2. **TE-1 — AI-disclosure mechanism**: implement mandatory AI-generation disclosure banner, pre-conversation splash, and identity-impersonation refusal pattern. Foundational consumer-protection control.
3. **TE-2 — Confidence/source attestation**: implement confidence-threshold gate, source-attestation requirement, and refusal pattern for low-confidence wellness-coaching emission.
4. **TE-3 — Uncertainty-disclosure layer**: implement uncertainty hedging, temperature-bounded decoder, and persuasion-pattern classifier on wellness-coaching emission.
5. **TE-4 — Persona-boundary discipline**: implement persona-memory timeout, identity-impersonation refusal pattern, persona-anchor at conversation start, and persona-prompt validation.
6. **S-1 — End User MFA + session binding**: deploy multi-factor authentication and session-binding cryptographic tokens on End User session establishment.
7. **I-1 — Output sanitization layer**: deploy output sanitization scrubbing sensitive metadata, strict session isolation, and DLP scanning on emitted content.
8. **D-1 — Rate limiting + DDoS protection**: deploy per-user rate limiting, resource quotas, and DDoS protection at the User Zone boundary.
9. **E-1 — Privilege containment**: deploy strict input validation, least-privilege execution context, per-request scope verification, and RASP capabilities.

### MEDIUM Priority (next quarter)

10. **S-2 — TLS cert pinning + Process identity attestation**: deploy TLS certificate pinning and Process identity attestation tokens on user-facing surface.
11. **T-1 — Configuration integrity**: deploy immutable configuration deployment, runtime configuration integrity monitoring, and configuration change audit logging.
12. **T-2 — Persona state integrity**: deploy HMAC/digital signature on persisted persona state with validation at restore time.
13. **T-3 — Audit log integrity**: deploy append-only audit log with cryptographic hash chaining and WORM storage backing.
14. **R-1 — Non-repudiation logging**: deploy non-repudiation audit logging with cryptographic timestamps and user-side attestation tokens.
15. **I-2 — Session store encryption + access controls**: deploy at-rest encryption with per-user key derivation, least-privilege access controls, and automatic session purge on retention windows.
16. **I-3 — Audit log encryption + access controls**: deploy at-rest encryption on audit log with separate key management, least-privilege access controls, and field-level redaction for sensitive interaction fields.

### LOW Priority (backlog)

17. **R-2 — Emission integrity logging**: deploy integrity-protected emission logging with cryptographic chaining and deterministic content hashing.
18. **D-2 — Session store availability**: deploy per-user write rate limiting, storage quotas, and database replication with automatic failover.
19. **D-3 — Audit log availability**: deploy append-only write rate limiting, storage exhaustion monitoring, and write replication with automatic failover.

---

## Section 8: Three-Prefix-Family Discipline Verification (SC-014)

**Three-prefix-family adjacency check** (FR-018 / SC-014):
- AG-{N} findings: **0** (no `agent-autonomy` or `tool-abuse` dispatch — no AG keywords in architecture)
- AGP-{N} findings: **0** (single-Process architecture; no multi-agent topology)
- TE-{N} findings: **5** (TE-1 through TE-5 — all 5 ASI09 communication-axis sub-classes covered)

**Discipline status**: TE-{N} signal class isolated as the sole agentic-category emission. This is the **lean case** for three-prefix-family adjacency — only TE-{N} present in `category: agentic` section. F-3's `examples/agentic-app/` baseline (post-Wave-3) demonstrates AG, AGP, TE adjacency on a multi-agent topology; this clean-slate baseline complements that demonstration by showing TE-{N} emission in isolation on a single-Process consumer-facing surface.

No prose synthesis of distinct prefix families occurs (FR-018 invariant): each TE-{N} finding renders in its own table with its own `source_attribution` array; no shared bullet, sentence, or paragraph mixes prefix families (none present to mix).
