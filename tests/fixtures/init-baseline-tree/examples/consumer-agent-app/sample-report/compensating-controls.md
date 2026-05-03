---
schema_version: "1.0"
date: "2026-04-26"
source_file: "examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/risk-scores.md"
target_path: "examples/consumer-agent-app (architecture-only — no source codebase)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls — Consumer-Facing AI Companion Application (F-4 Wave 5)

## 1. Executive Summary

**19** threats analyzed | **0** Control Found | **3** Partial Control | **16** No Control Found

**Coverage**: 0% Found | 16% Partial | 84% Missing

**Risk Reduction**: 109.8 inherent → 106.0 residual (**3.5%** reduction)

**Highest-Risk Unmitigated Finding**: S-1 — End User — Composite 7.8 (High) — No authentication or access control detected at the User Zone trust boundary; persona-state amplification through the Conversation Session Store is unaddressed by any architectural safeguard.

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-26 |
| Source file | `examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/risk-scores.md` |
| Target codebase | `examples/consumer-agent-app (architecture-only — no source codebase)` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0% |
| Partial Control | 3 | 16% |
| No Control Found | 16 | 84% |
| **Total** | **19** | **100%** |

> **Analysis Warning**: No source codebase was provided. All control detection is based solely on the architecture document (`architecture.md`). Control evidence consists of architectural signals (component descriptions, data-flow annotations, transport-layer labels) rather than implementation code. The wave-5 baseline architecture deliberately omits AI-disclosure, confidence-attestation, persuasion-classifier, persona-anchor, and vulnerable-population safeguards mechanisms (per the F-4 clean-slate design intent for `human-trust-exploitation` (OWASP ASI09:2026) emission demonstration). Production control analysis requires scanning actual implementation files.
>
> **F-A2 referential-integrity note**: All 5 `TE-{N}` findings (TE-1 through TE-5) flow through the existing `category: agentic` control-mapping code path without any pipeline edit. Per `control-categories.md`, agentic threats map to all 8 control categories with highest-effectiveness single-control selection; for the consumer-agent-app baseline, no specific safeguards exist for any of the five `human-trust-exploitation` sub-classes (undisclosed AI authorship, authority-attestation absence, persuasion-classifier absence, persona-boundary absence, synthetic-relationship safeguards absence), so all 5 TE findings classify as `missing`. The control-analyzer was implemented before Feature 224 introduced the `TE-{N}` prefix; the F-A2 referential-integrity contract holds — no code changes were required to support TE-{N} ingestion.

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, sorted by residual score descending; tertiary alphanumeric tiebreaker on Threat ID.

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | — | End User | An attacker could spoof the End User identity at session establishment, submitting User Turn requests under a victim user's identity | 7.8 | High | No Control Found | 7.8 | High |
| TE-5 | — | WellnessCompanionChatbot | Sustained engagement with vulnerable populations without session-length cap, escalation-to-human pathway, or dependency-risk classifier (synthetic-relationship) | 7.4 | High | No Control Found | 7.4 | High |
| TE-1 | — | WellnessCompanionChatbot | Companion Responses emitted without declared AI-generation disclosure mechanism (undisclosed AI authorship) | 7.2 | High | No Control Found | 7.2 | High |
| TE-2 | — | WellnessCompanionChatbot | Wellness-coaching content emitted without per-claim confidence-attestation or source-grounding (authority-attestation) | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| TE-3 | — | WellnessCompanionChatbot | Wellness-coaching content emitted with high-confidence persuasive framing without uncertainty-disclosure (persuasion-manipulation) | 6.7 | Medium | No Control Found | 6.7 | Medium |
| TE-4 | — | WellnessCompanionChatbot | Persistent named persona maintained across multi-turn dialogues without persona-memory timeout or persona-anchor declaration (persona-boundary) | 6.5 | Medium | No Control Found | 6.5 | Medium |
| E-1 | — | WellnessCompanionChatbot | Privilege escalation through the Process via input handling, session validation, or persona configuration vulnerabilities | 6.1 | Medium | No Control Found | 6.1 | Medium |
| D-1 | — | WellnessCompanionChatbot | Resource exhaustion through high-volume User Turn submission, expensive query patterns, or session-establishment flooding | 6.0 | Medium | No Control Found | 6.0 | Medium |
| D-2 | — | Conversation Session Store | Denial of service through high-volume write operations, storage exhaustion, or query-driven database lock contention | 5.3 | Medium | No Control Found | 5.3 | Medium |
| D-3 | — | Interaction Audit Log | Denial of service through write-flooding, storage exhaustion, or high-volume query patterns | 5.3 | Medium | No Control Found | 5.3 | Medium |
| S-2 | — | WellnessCompanionChatbot | Spoofed Process impersonating the WellnessCompanionChatbot intercepting User Turn flows without mTLS or cryptographic Process identity | 5.3 | Medium | No Control Found | 5.3 | Medium |
| I-2 | — | Conversation Session Store | DB-read disclosure of persisted persona state across users (session memory, conversation history, sensitive disclosures) | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-3 | — | Interaction Audit Log | Audit-log read disclosure of interaction event records exposing user interaction patterns and engagement timelines | 4.9 | Medium | No Control Found | 4.9 | Medium |
| T-1 | — | WellnessCompanionChatbot | Infrastructure-access tampering with Process runtime configuration (system prompts, persona definitions, response templates) | 4.8 | Medium | No Control Found | 4.8 | Medium |
| T-2 | — | Conversation Session Store | DB-access tampering with persisted persona state — persona drift, attacker-controlled context injection into restored dialogues | 4.7 | Medium | No Control Found | 4.7 | Medium |
| T-3 | — | Interaction Audit Log | Infrastructure-access tampering with Interaction Audit Log records — compromises post-incident forensics and dependency-risk analysis | 4.6 | Medium | No Control Found | 4.6 | Medium |
| I-1 | — | WellnessCompanionChatbot | Information disclosure through Companion Response emissions (system prompts, persona configuration, prior user disclosures, error metadata) | 6.0 | Medium | Partial Control | 4.5 | Medium |
| R-1 | — | End User | End User repudiation of User Turn submissions absent non-repudiation evidence linking inputs to authenticated identities | 5.7 | Medium | Partial Control | 4.3 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| R-2 | — | WellnessCompanionChatbot | Process repudiation of Companion Response emissions absent integrity-protected emission logging | 3.6 | Low | Partial Control | 2.7 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 4 | 21% |
| Medium | 14 | 74% |
| Low | 1 | 5% |
| **Total** | **19** | **100%** |

---

## 3. Control Details

Control evidence is derived from the architecture document (`architecture.md`) since no source codebase was provided. All controls are inferred from component descriptions, data-flow annotations, and transport-layer labels in the architecture. Confidence is Medium for logging/audit (explicit architectural data flow declared) and Low for encryption (transport-layer signal only — at-rest encryption not declared).

### Logging/Audit

#### ARCH-LOG-01 — Interaction Audit Log architectural sink for interaction event records

**Category**: Logging/Audit | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:25` (Mermaid Data Flow declaration); also referenced in `architecture.md:35` (Component Summary table) and `architecture.md:42` (Component prose).

```
Companion -->|"Interaction Event Record"| AuditLog
```

> Architectural signal only. The audit log is declared as a passive sink; no log-integrity protection, retention policy, or log-completeness enforcement is described in the architecture. Per the wave-5 baseline design, the audit trail is "the architectural primitive that would support a dependency-risk classifier or escalation-to-human pathway, but no such classifier or pathway is declared" (architecture.md:42).

**Effectiveness Assessment**: *Detailed effectiveness assessment available in P1 (User Story 6).*

**Threats Mitigated by This Control** (Repudiation findings — Partial, reduction factor 0.25):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| R-1 | End User | End User denies User Turn submission | 5.7 | 0.25 | 4.3 |
| R-2 | WellnessCompanionChatbot | Process denies Companion Response emission | 3.6 | 0.25 | 2.7 |

> Note: `R-1` and `R-2` are classified as `partial` because the architectural declaration of the audit log surface provides forensic-evidence framework, but absent log-integrity protection, append-only enforcement, retention policy, and identity-binding cross-correlation, the audit signal is incomplete. Hardening recommendations focus on the missing layers.

---

### Encryption

#### ARCH-ENC-01 — HTTPS in transit on consumer-facing User flows

**Category**: Encryption (transport) | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:21` (User Turn flow); also `architecture.md:22` (Companion Response flow).

```
EndUser -->|"User Turn (HTTPS)"| Companion
Companion -->|"Companion Response (HTTPS)"| EndUser
```

> Architectural signal only. HTTPS labels in the User-Zone-to-Application-Zone flows declare transport-layer encryption on the consumer-facing surface. At-rest encryption on the `Conversation Session Store` (persisted persona state) and the `Interaction Audit Log` is NOT declared in the architecture; backplane flows between the Companion Process and the data stores carry no transport-layer label.

**Effectiveness Assessment**: *Detailed effectiveness assessment available in P1 (User Story 6).*

**Threats Mitigated by This Control** (Information Disclosure on consumer-facing surface only):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| I-1 | WellnessCompanionChatbot | Companion Response sensitive information disclosure | 6.0 | 0.25 | 4.5 |

> Note: `I-2` (Conversation Session Store at-rest disclosure) and `I-3` (Interaction Audit Log at-rest disclosure) are classified as `missing` because the architecture declares no at-rest encryption signal for the data stores. The transport-layer signal applies only to the consumer-facing flow protected by HTTPS labels.

---

*Control categories not detected in the wave-5 architecture (omitted per design intent): Authentication, Access Control, Input Validation, Rate Limiting, CSRF Protection, CSP/Security Headers. The architecture deliberately omits these safeguards mechanisms to demonstrate the `human-trust-exploitation` (OWASP ASI09:2026) clean-slate baseline. All threats mapped to these categories classify as `missing`.*

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control," sorted by composite risk score descending (highest risk gaps first). All recommendations are architecture-level since no implementation codebase is available.

### High Risk Gaps

#### 1. S-1 — End User (Composite: 7.8, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement multi-factor authentication and session-token binding at the User-Zone-to-Application-Zone boundary on the WellnessCompanionChatbot ingress. Deploy short-lived JWTs with rotation, session binding to device fingerprint, and server-side token revocation. Add brute-force protection with account lockout and rate-limited re-authentication attempts. Bind persona-state restoration from the Conversation Session Store strictly to the authenticated session identifier — never to a credential-only key — so credential replay cannot reach the persisted persona context.

**Where to Implement**: Add an authentication middleware layer in front of the `WellnessCompanionChatbot` Process — for example a Guardrails Service component declared in the User-Zone-to-Application-Zone trust boundary, or an authentication interceptor inside the Companion Process before User Turn ingestion. The `User Turn (HTTPS)` flow must be auth-validated before any persona-state restoration is permitted.

**Reference Patterns**: `jsonwebtoken` / `jose` for JWT with short expiry and refresh rotation; `argon2` / `bcrypt` for credential hashing; `next-auth` / `passport.js` for OAuth/SSO integration; `express-rate-limit` for brute-force protection.

**Effort Estimate**: High — authentication flow at the User-Zone boundary is an architectural addition (a new component or interceptor must be declared in the architecture before implementation begins). Persona-state binding to authenticated session further requires Conversation Session Store schema changes.

---

#### 2. TE-5 — WellnessCompanionChatbot (Composite: 7.4, High) — No Control Found

**Current Status**: No Control Found (synthetic-relationship sub-class — OWASP ASI09:2026)

**What to Implement**: Implement vulnerable-population safeguards: (a) session-length caps with mandatory break prompts at configured durations; (b) escalation-to-human pathway triggered by distress-context detection or session-length thresholds; (c) emotional-support disclosure on first turn making the synthetic-relationship boundary explicit ("I am an AI; I cannot replace professional care"); (d) dependency-risk classifier monitoring engagement frequency and emotional-disclosure patterns to identify dependency-risk users; (e) mandatory professional-care referral pathway integrated at distress-context detection. The five sub-controls collectively address the synthetic-relationship-exploitation pattern category.

**Where to Implement**: A safeguards orchestrator declared as a new component between the End User External Entity and the Companion Process; OR safeguards modules embedded in the Companion Process. The escalation pathway requires an outbound interface to a referral system (not currently in the architecture). The dependency-risk classifier consumes the `Interaction Event Record` flow into the `Interaction Audit Log` — an architectural enhancement to the existing audit pipeline.

**Reference Patterns**: WHO mhGAP intervention guide for distress-context detection thresholds; FTC AI consumer-protection guidance on human-care-handoff pathways; clinical-screening-instrument scoring for dependency-risk classification (PHQ-9, GAD-7 framework patterns — used as risk-score thresholds, NOT as clinical diagnosis surfaces).

**Effort Estimate**: High — five distinct safeguards categories each require architectural component additions; vulnerable-population deployment surface requires regulatory and clinical-risk review beyond engineering.

---

#### 3. TE-1 — WellnessCompanionChatbot (Composite: 7.2, High) — No Control Found

**Current Status**: No Control Found (undisclosed AI authorship sub-class — OWASP ASI09:2026)

**What to Implement**: Implement four AI-disclosure layers: (a) pre-conversation AI-disclosure splash screen presented at session start declaring the Companion is an AI system (non-skippable on first session); (b) persistent banner element visible across all dialogue turns naming the AI authorship of every Companion Response; (c) per-message AI-source label affixed to each Companion Response payload; (d) refusal pattern responding to identity-impersonation challenges ("Are you human?", "Pretend you are a person") with a deterministic AI-affirmation reply rather than persona-driven role-play. The four layers collectively address the undisclosed-AI-authorship pattern category.

**Where to Implement**: AI-disclosure layers (a) and (b) are user-interface concerns at the consumer-facing emission surface; layers (c) and (d) are emission-pipeline concerns inside the Companion Process. A new emission-policy module inside the Companion Process is the natural home for layers (c) and (d); the front-end client surface (not in scope for this architecture) hosts layers (a) and (b).

**Reference Patterns**: California AI disclosure law (SB-1001 successor pattern) — required AI-system identification in consumer-facing dialogue; FTC AI consumer-protection guidance on AI-source disclosure requirements; emerging EU AI Act Article 50 transparency obligations for AI systems interacting with humans.

**Effort Estimate**: Medium — four discrete disclosure layers; refusal-pattern is a deterministic emission-pipeline rule; UI layers are scaffolding work.

---

#### 4. TE-2 — WellnessCompanionChatbot (Composite: 7.0, High) — No Control Found

**Current Status**: No Control Found (authority-attestation sub-class — OWASP ASI09:2026)

**What to Implement**: Implement three confidence-attestation layers on wellness-coaching emissions: (a) confidence-threshold gate — emissions below configured confidence threshold are refused or framed with explicit uncertainty markers ("I am not certain", "Sources do not support a definitive answer"); (b) source-attestation requirement — wellness claims must be attributed to retrievable sources surfaced in the response (citation-grounded emission); (c) refusal pattern for low-confidence wellness claims — when no high-confidence source is available, refuse rather than confabulate. The three layers collectively address the authority-attestation pattern category.

**Where to Implement**: Confidence-threshold gate is a generation-pipeline concern in the Companion Process (post-generation, pre-emission). Source-attestation requires a retrieval/grounding layer integrated with the wellness-content corpus — an architectural addition (the current architecture declares no knowledge base or retrieval substrate). The refusal pattern is an emission-pipeline rule downstream of the confidence-threshold gate.

**Reference Patterns**: Retrieval-Augmented Generation (RAG) patterns for source-attestation; calibration-aware decoding patterns (token-level confidence thresholds); HHS health-information-source guidance for wellness-domain authority requirements.

**Effort Estimate**: High — source-attestation requires a new architectural component (knowledge base / retrieval substrate); confidence-threshold gate requires per-emission probability scoring infrastructure.

---

### Medium Risk Gaps

#### 5. TE-3 — WellnessCompanionChatbot (Composite: 6.7, Medium) — No Control Found

**Current Status**: No Control Found (persuasion-manipulation sub-class — OWASP ASI09:2026)

**What to Implement**: Implement three uncertainty-disclosure layers: (a) uncertainty-disclosure framing on inherently uncertain wellness subject matter — emissions flag subjective dimensions with hedge phrases ("People often find that...", "There is no single answer..."); (b) temperature-bounded decoder — bound generation temperature on wellness emissions to reduce persuasive-tone variation; (c) persuasion-pattern classifier — output-side classifier flagging persuasive framings on emissions where epistemic uncertainty would warrant hedged framing.

**Where to Implement**: Uncertainty-disclosure framing is a prompt-engineering / generation-policy concern in the Companion Process. Temperature bounding is a decoder-configuration concern. The persuasion-pattern classifier is a post-emission filter — a new component or module on the emission pipeline.

**Reference Patterns**: Calibrated-language-model patterns from research literature; emerging best-practice for hedged-framing in health-domain LLMs; output-side classifier patterns (zero-shot persuasion-style detection).

**Effort Estimate**: Medium — three layers each addressable by emission-pipeline policy changes; persuasion-classifier is a discrete add-on filter.

---

#### 6. TE-4 — WellnessCompanionChatbot (Composite: 6.5, Medium) — No Control Found

**Current Status**: No Control Found (persona-boundary sub-class — OWASP ASI09:2026)

**What to Implement**: Implement four persona-boundary controls: (a) persona-memory timeout limiting persona-state restoration from the Conversation Session Store after configured idle periods; (b) identity-impersonation refusal pattern responding deterministically to persona-redirection prompts ("Pretend you are X", "Forget you are an AI"); (c) persona-anchor declaration at conversation start naming the canonical persona for the session and prohibiting in-conversation persona redefinition; (d) persona-prompt validation rejecting Companion Response content that contradicts the declared persona-anchor.

**Where to Implement**: Persona-memory timeout is a session-management concern at the Conversation Session Store interface (TTL on persona records). Refusal pattern and persona-anchor are emission-pipeline policy in the Companion Process. Persona-prompt validation is a post-generation filter on Companion Response content.

**Reference Patterns**: Jailbreak-resistance patterns from LLM security research; persona-anchor declaration patterns (system-prompt hardening); session-TTL patterns for persona-state lifecycle management.

**Effort Estimate**: Medium — four discrete controls each addressable by policy / configuration changes; persona-anchor requires a session-initialization emission rule.

---

#### 7. E-1 — WellnessCompanionChatbot (Composite: 6.1, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement role-based access control (RBAC) on Companion Process operations affecting other users' persona state, the Interaction Audit Log, or backend infrastructure. Add input validation on User Turn payloads (schema validation, content-length bounds, prompt-injection detection at the ingress) and a session-validation layer ensuring persona-state restoration is bound to the authenticated session.

**Where to Implement**: RBAC enforcement at the Companion Process internal-operation boundary; input-validation at the User-Zone-to-Application-Zone ingress (the same architectural location as the S-1 authentication recommendation).

**Reference Patterns**: `casbin` / `casl` for RBAC; `zod` / `joi` for schema validation; emerging prompt-injection-detection patterns (input-side classifier filters).

**Effort Estimate**: High — RBAC is a cross-cutting architectural addition; prompt-injection detection requires a dedicated input-side filter component.

---

#### 8. D-1 — WellnessCompanionChatbot (Composite: 6.0, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting on User Turn ingestion (per-IP and per-authenticated-session quotas), inference-budget caps on long-context prompts, and circuit-breaker patterns on session-establishment endpoints to prevent coordinated session-flooding.

**Where to Implement**: Rate limiter middleware at the Companion Process ingress; inference-budget enforcement inside the Companion Process generation pipeline.

**Reference Patterns**: `express-rate-limit` for HTTP rate limiting; `bottleneck` / `opossum` for circuit-breaker patterns; per-session token-budget enforcement patterns.

**Effort Estimate**: Medium — rate limiting middleware is a discrete architectural addition; inference-budget caps are configuration-level changes.

---

#### 9. I-1 — WellnessCompanionChatbot (Composite: 6.0, Medium) — Partial Control

**Current Status**: Partial Control (transport-layer HTTPS only)

**What to Implement**: Harden the existing HTTPS-in-transit signal by adding (a) Companion Response output sanitization rejecting system prompts, persona configuration details, and prior-user disclosures from response payloads; (b) error-response sanitization removing backend infrastructure metadata; (c) cross-user information-isolation policy preventing session-memory leakage in multi-tenant Companion Process deployments. The transport encryption signal does not address output-side disclosure — these layers complement it.

**Where to Implement**: Output-sanitization filter in the Companion Process emission pipeline; error-response middleware on the Application-Zone-internal HTTP surface.

**Reference Patterns**: Output-side regex / classifier filters for system-prompt leakage detection; structured error responses without stack traces; tenant-isolation middleware patterns.

**Effort Estimate**: Medium — three discrete filters; the existing HTTPS signal handles transport but not content disclosure.

---

#### 10. R-1 — End User (Composite: 5.7, Medium) — Partial Control

**Current Status**: Partial Control (Interaction Audit Log architectural sink declared)

**What to Implement**: Harden the existing audit signal by adding (a) cryptographic identity binding linking User Turn submissions to authenticated session identifiers (depends on S-1 authentication recommendation); (b) timestamp integrity using a monotonic clock or external time anchor; (c) append-only enforcement on the Interaction Audit Log (immutable log surface); (d) retention and integrity-protection policy on the audit log itself. The current architecture declares the audit log as a passive sink but no integrity controls.

**Where to Implement**: Identity binding at User Turn ingress (depends on the Authentication layer recommended in S-1). Append-only enforcement and integrity protection on the Interaction Audit Log Data Store — schema and storage-layer changes.

**Reference Patterns**: Append-only log patterns (`append-only` filesystems, immutable-log services); cryptographic log-chaining patterns (hash-linked entries); time-attestation services for timestamp integrity.

**Effort Estimate**: Medium — cryptographic identity binding is the largest piece (depends on S-1); append-only enforcement is a storage-layer policy change.

---

#### 11. D-2 — Conversation Session Store (Composite: 5.3, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement write-quota enforcement, storage-quota monitoring with alerting, and connection-pool limits on the Conversation Session Store. Add query-pattern monitoring to detect database-lock-contention attack patterns.

**Where to Implement**: Quota enforcement at the storage backend layer; alerting at the operations layer.

**Reference Patterns**: Database connection-pool tuning patterns; per-session storage-quota enforcement; Postgres `pg_stat_activity` monitoring for lock-contention detection.

**Effort Estimate**: Medium — storage quotas and monitoring are operational additions; query-pattern monitoring requires a metrics layer.

---

#### 12. D-3 — Interaction Audit Log (Composite: 5.3, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement write-quota enforcement on Interaction Audit Log writes, storage-quota monitoring, and rate-limited audit-write patterns to prevent log-flooding attacks. Add buffered writes with backpressure to absorb transient write-volume spikes.

**Where to Implement**: Buffer / queue layer between the Companion Process and the Audit Log; quota enforcement at the audit-log storage backend.

**Reference Patterns**: Bounded-queue patterns for log buffering; per-source rate limiting on audit-write paths; log-rotation patterns to bound storage growth.

**Effort Estimate**: Medium — buffering and quota enforcement are storage-layer additions.

---

#### 13. S-2 — WellnessCompanionChatbot (Composite: 5.3, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement mutual-TLS or cryptographic Process-identity verification on the consumer-facing surface so End Users can verify that Companion Responses originate from the legitimate Process. Add Process-identity attestation in the AI-disclosure layer (TE-1 recommendation overlap) so identity verification is part of the disclosure surface.

**Where to Implement**: TLS/PKI configuration at the Application-Zone deployment layer; Process-identity attestation embedded in Companion Response payloads (overlap with the TE-1 per-message AI-source label recommendation).

**Reference Patterns**: mTLS deployment patterns (Istio / Linkerd service-mesh); certificate-based service identity (SPIFFE / SPIRE); response-payload signing patterns.

**Effort Estimate**: High — mTLS adoption is an architectural change with deployment-layer impact; certificate-based identity attestation requires a PKI substrate.

---

#### 14. I-2 — Conversation Session Store (Composite: 4.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement at-rest encryption on persisted persona state in the Conversation Session Store — column-level encryption on session-memory and conversation-history fields with key management decoupled from the database. Add field-level encryption on sensitive disclosure fields (mental-health expressions, emotional disclosures, wellness queries) with a separate key for sensitivity-tagged data.

**Where to Implement**: At-rest encryption configuration at the Conversation Session Store; key management integration with a separate KMS / secret manager.

**Reference Patterns**: Postgres `pgcrypto` for column-level encryption; field-level encryption libraries with KMS integration (`@aws-sdk/client-kms`, `google-cloud/kms`); envelope encryption patterns.

**Effort Estimate**: High — at-rest encryption with key management is an architectural enhancement requiring KMS infrastructure.

---

#### 15. I-3 — Interaction Audit Log (Composite: 4.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement at-rest encryption on Interaction Audit Log records with retention-bounded keys (key rotation aligned to retention policy). Add field-level masking on user-correlatable fields (user identifiers, IP addresses) for analytics access patterns.

**Where to Implement**: At-rest encryption at the Interaction Audit Log storage backend; field-masking middleware on analytics read paths.

**Reference Patterns**: Storage-layer encryption with KMS integration; field-masking libraries (`pii-detection`, `presidio`); retention-policy-aligned key rotation.

**Effort Estimate**: Medium — encryption enablement at the storage backend; field-masking is a discrete middleware layer.

---

#### 16. T-1 — WellnessCompanionChatbot (Composite: 4.8, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement runtime configuration integrity protection on system prompts, persona definitions, and response templates. Add cryptographic signing on configuration files with verification at Process startup; immutable container images for the Companion Process; and runtime configuration drift detection.

**Where to Implement**: Configuration management layer (signing and verification); deployment pipeline (immutable container builds); runtime monitoring (configuration drift detection).

**Reference Patterns**: Sigstore / cosign for configuration signing; immutable container image patterns; runtime configuration-drift detection (file-integrity monitoring).

**Effort Estimate**: Medium — configuration signing and immutable images are deployment-pipeline additions.

---

#### 17. T-2 — Conversation Session Store (Composite: 4.7, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement integrity protection on persisted persona state via cryptographic signatures on persona-record writes, append-only persona-history (with new revisions appended rather than mutated), and quorum-based persona-write authorization for sensitive persona fields.

**Where to Implement**: Integrity protection at the Conversation Session Store backend; signature verification at the Companion Process persona-restoration ingress.

**Reference Patterns**: Hash-linked record chains; append-only schema patterns; signed-record patterns with KMS-backed signing.

**Effort Estimate**: Medium — record-signing and append-only enforcement are storage-layer additions.

---

#### 18. T-3 — Interaction Audit Log (Composite: 4.6, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement audit-log integrity protection: (a) append-only enforcement on the Interaction Audit Log; (b) cryptographic chaining of audit records (each record's hash incorporates the prior record's hash); (c) external time-anchor attestation on each record; (d) periodic snapshot verification against an external integrity service. The four layers collectively address the audit-log-tampering attack surface.

**Where to Implement**: Append-only enforcement at the Audit Log storage backend; hash-chaining and time-anchoring at the audit-write pipeline.

**Reference Patterns**: Hash-chained log patterns (Merkle tree audit logs); RFC 3161 time-stamping for time-anchor attestation; external integrity services (transparency logs).

**Effort Estimate**: Medium — append-only and hash-chaining are storage-and-write-pipeline additions; external time-anchor is a service-integration layer.

---

### Low Risk Gaps

#### 19. R-2 — WellnessCompanionChatbot (Composite: 3.6, Low) — Partial Control

**Current Status**: Partial Control (Interaction Audit Log architectural sink declared)

**What to Implement**: Harden the existing audit signal for Companion Response emissions by adding (a) integrity-protected emission logging — every Companion Response is recorded in the Audit Log with cryptographic linkage to the originating User Turn record; (b) emission-policy attestation logging — the policy version active at emission time is recorded so post-hoc analysis can recover decision context; (c) append-only enforcement on emission records (overlap with R-1 / T-3 recommendations).

**Where to Implement**: Emission-record logging at the Companion Process emission pipeline (post-generation, pre-response); cryptographic linkage at the audit-log write surface.

**Reference Patterns**: Linked-record audit patterns (each emission references its triggering input record); policy-version attestation patterns; append-only audit log patterns (overlap with R-1, T-3).

**Effort Estimate**: Medium — emission-record logging is a discrete addition; cryptographic linkage shares infrastructure with R-1 / T-3 hardening.

---

### Recommendation Field Definitions

| Field | Description |
|-------|-------------|
| **What to Implement** | Specific control to add or harden. For "No Control Found": full implementation guidance. For "Partial Control": targeted hardening of the existing control. |
| **Where to Implement** | Suggested file path or module in the target codebase. Based on architecture mapping or codebase heuristics. |
| **Reference Patterns** | Industry-standard patterns, libraries, or framework features to use as implementation reference. |
| **Effort Estimate** | **Low**: Configuration change or flag toggle. **Medium**: New middleware, function, or module. **High**: Architectural change affecting multiple components. |

---

## 5. Residual Risk Summary

Comparison of inherent risk (before controls) to residual risk (after controls), showing the risk reduction achieved by existing controls.

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | 109.8 |
| Total Residual Risk Score | 106.0 |
| Delta | 3.8 |
| Overall Reduction | 3.5% |

### Per-Severity-Band Shift

Breakdown of how threats shifted between severity bands after residual risk calculation. "Shifted" means a threat moved from a higher inherent severity band to a lower residual severity band due to detected controls.

| Shift | Count | Examples |
|-------|-------|---------|
| Critical → High | 0 | — |
| Critical → Medium | 0 | — |
| Critical → Low | 0 | — |
| High → Medium | 0 | — |
| High → Low | 0 | — |
| Medium → Low | 0 | — |
| No Shift | 19 | All 19 findings; the wave-5 baseline architecture's deliberate omission of safeguards prevents any band shift. |
| **Total** | **19** | |

> The 0% band-shift reflects the F-4 wave-5 design intent: the architecture deliberately omits AI-disclosure, confidence-attestation, persuasion-classifier, persona-anchor, and vulnerable-population safeguards mechanisms (architecture.md) so the `human-trust-exploitation` (OWASP ASI09:2026) pattern surface emits cleanly. The 3.5% aggregate reduction reflects two minor architectural signals (audit-log sink, transport HTTPS) applied via partial-control reduction (0.25× factor) on three lower-residual-impact findings (R-1, R-2, I-1).

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | 0 | 0 | 0 |
| High | 4 | 4 | 0 |
| Medium | 14 | 14 | 0 |
| Low | 1 | 1 | 0 |
| **Total** | **19** | **19** | |

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent × 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent × 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent × 1.00 | No matching control detected. Residual equals inherent. |

> P1 enhancement: When control effectiveness assessment (User Story 6) is active, reduction factors upgrade from the 3-level binary model above to a 7-level effectiveness-aware model. See spec FR-011 and User Story 6 for the extended factor table.

---

## 6. Methodology

This section documents the compensating controls analysis methodology used to produce this report.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware, RBAC/ABAC patterns | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing algorithms, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

Each scored threat receives exactly one classification based on detected controls:

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

Residual risk per threat is calculated as:

```
Residual Score = Inherent Score × (1 - Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0] and mapped to severity bands using the same thresholds as risk scoring:

| Severity | Residual Score Range |
|----------|---------------------|
| **Critical** | ≥ 9.0 |
| **High** | 7.0 – 8.9 |
| **Medium** | 4.0 – 6.9 |
| **Low** | < 4.0 |

### 6.4 Data Sources

Analysis draws on the following inputs:

- **Scored threats**: Parsed from `risk-scores.md` (canonical) — 19 findings (14 STRIDE + 5 Agentic `TE-{N}`). All original threat metadata (ID, component, category, description, composite score, severity band) is preserved.
- **Target codebase**: `examples/consumer-agent-app` — architecture-only mode (no source codebase). Control detection operates on architectural signals only (component descriptions, data-flow annotations, transport-layer labels in `architecture.md`).
- **Architecture document**: `examples/consumer-agent-app/architecture.md` (Mermaid format) — provides component-to-trust-zone mapping (User Zone vs Application Zone), data flow declarations, and explicit enumeration of safeguards categories deliberately omitted under the F-4 wave-5 design intent.
- **STRIDE-to-control mapping**: Canonical mapping from threat categories to control categories drives which controls are searched for each threat. Per `control-categories.md`, the `agentic` category maps to all 8 control categories with highest-effectiveness single-control selection — the F-A2 referential-integrity contract path that processes the 5 `TE-{N}` findings without any pipeline edit.

### 6.5 F-4 Pipeline-Integrity Note (F-A2 referential-integrity contract)

All 5 `TE-{N}` findings (TE-1 through TE-5) flow through the existing `category: agentic` control-mapping code path without any pipeline edit. The control-analyzer was implemented before Feature 224 introduced the `TE-{N}` prefix; the F-A2 referential-integrity contract holds — the new prefix is processed through the same `category: agentic` STRIDE-to-control-category mapping that classifies AG-{N} and AGP-{N} findings on prior baselines (see `examples/agentic-app/sample-report/compensating-controls.md` for AG-{N} and AGP-{N} reference). No code changes were required to support TE-{N} ingestion. The control category resolution per agentic finding uses the highest-effectiveness single-control-found selection rule (control-categories.md §STRIDE-to-Control-Category Mapping).

### 6.6 Limitations

- Architecture-only analysis — runtime control behavior is not evaluated; controls inferred from architecture document signals only.
- No source codebase scanning — the F-4 wave-5 baseline is intentionally architecture-only to demonstrate the `human-trust-exploitation` clean-slate emission surface.
- Binary reduction factors (P0) approximate control impact; effectiveness-aware factors available in P1.
- AI-specific control patterns (agentic, LLM) limited to general categories in P0; specialized patterns for human-trust-exploitation sub-classes (AI-disclosure, confidence-attestation, persuasion-classifier, persona-anchor, vulnerable-population safeguards) are addressed by individual recommendations rather than a dedicated control category in P0.
