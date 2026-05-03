---

```yaml
---
schema_version: "1.0"
date: "2026-04-16"
source_file: "examples/maestro-reference/risk-scores.md"
target_path: "."
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---
```

# Compensating Controls — Healthcare Clinical Decision Support System (CDSS)

> **Reference Architecture Notice**: This report analyzes a fictional Healthcare CDSS reference architecture used as a teaching construct for the tachi threat-modeling methodology. The target codebase scanned is the tachi repository itself — a Python-based threat-modeling toolkit — which does NOT implement any clinical workflows, FHIR interfaces, or healthcare-specific security controls. The near-total absence of compensating controls in this report is the accurate, expected result of scanning an unrelated codebase against a domain-specific threat model. The value of this output is demonstrating the **shape** of a compensating-controls report: coverage matrix structure, residual risk calculation, and recommendation format. Adopters should apply this same pipeline against their own target codebase to obtain meaningful control coverage.

---

## 1. Executive Summary

**108** threats analyzed | **0** Control Found | **0** Partial Control | **108** No Control Found

**Coverage**: 0% Found | 0% Partial | 100% Missing

**Risk Reduction**: 570.6 inherent -> 570.6 residual (**0.0%** reduction)

**Highest-Risk Unmitigated Finding**: S-1 — Physician — Composite 8.4 (High)

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-16 |
| Source file | `examples/maestro-reference/risk-scores.md` |
| Target codebase | `.` (tachi repository root) |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0% |
| Partial Control | 0 | 0% |
| No Control Found | 108 | 100% |
| **Total** | **108** | **100%** |

> **Analysis Warning — Reference Architecture Mismatch**: The 108 scored findings describe threats to Healthcare CDSS components (Physician Clinical Portal, Clinical LLM, FHIR Resource Store, Supervisor Orchestrator, etc.). The target codebase is the tachi pipeline toolkit (Python data-processing scripts, shell utilities, stack scaffolds). No clinical application code, FHIR APIs, authentication middleware, or access control infrastructure is present in this repository. All 108 findings are classified as No Control Found. This is accurate — the tachi repository genuinely does not implement controls for a clinical decision support system. The 8 control categories were scanned across all non-test Python files (`scripts/tachi_parsers.py`, `scripts/extract-report-data.py`, `scripts/extract-infographic-data.py`, `scripts/install.sh`) and the stack scaffolds (`stacks/fastapi-react/`). Scaffold files were rejected during Phase B analysis because they are template code with no registered routes or running application context. No production authentication, rate limiting, CSRF, CSP, encryption, or access control patterns were found.

---

## 2. Coverage Matrix

Threats grouped by residual severity (High first, then Medium, Low). No Critical residual findings exist in this run (no inherent Critical findings; highest inherent score is 8.4 / High). Since all reduction factors are 0.00, residual severity equals inherent severity for every finding.

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | — | Physician | Attacker replays or forges clinical query credentials | 8.4 | High | No Control Found | 8.4 | High |
| S-2 | — | Patient | Attacker submits fraudulent EHR update events | 7.4 | High | No Control Found | 7.4 | High |
| D-1 | — | Physician Clinical Portal | Attacker floods portal with clinical query requests | 7.1 | High | No Control Found | 7.1 | High |
| E-1 | — | Physician Clinical Portal | Attacker escalates from low-privilege session | 7.0 | High | No Control Found | 7.0 | High |
| S-5 | — | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messages | 7.0 | High | No Control Found | 7.0 | High |
| T-3 | — | Inter-Agent Communication Channel | Attacker tampers with delegation messages in transit | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| AG-8 | — | Inter-Agent Communication Channel | Compromised agent abuses inter-agent channel | 6.8 | Medium | No Control Found | 6.8 | Medium |
| D-3 | — | Inter-Agent Communication Channel | Delegation message flood starves specialist agents | 6.8 | Medium | No Control Found | 6.8 | Medium |
| E-2 | — | Patient Summary Generator | Attacker exploits summary generator for unauthorized patients | 6.8 | Medium | No Control Found | 6.8 | Medium |
| AGP-01 | — | Inter-Agent Communication Channel | Multi-agent coordination creates potential for coordinated action | 6.7 | Medium | No Control Found | 6.7 | Medium |
| E-8 | — | Clinical LLM | Prompt injection causes elevated reasoning authority | 6.6 | Medium | No Control Found | 6.6 | Medium |
| E-3 | — | Inter-Agent Communication Channel | Compromised channel escalates to supervisor-level authority | 6.6 | Medium | No Control Found | 6.6 | Medium |
| T-8 | — | Clinical LLM | Attacker tampers with prompt inputs forwarded by API Gateway | 6.5 | Medium | No Control Found | 6.5 | Medium |
| I-3 | — | Inter-Agent Communication Channel | PHI disclosed through unencrypted inter-agent channel | 6.4 | Medium | No Control Found | 6.4 | Medium |
| E-7 | — | Clinical MCP Tool Server | Compromised agent escalates to unauthorized FHIR operations | 6.4 | Medium | No Control Found | 6.4 | Medium |
| S-6 | — | Supervisor Orchestrator | Attacker impersonates Supervisor Orchestrator | 6.4 | Medium | No Control Found | 6.4 | Medium |
| D-13 | — | Model Inference API Gateway | Request floods saturate inference gateway | 6.2 | Medium | No Control Found | 6.2 | Medium |
| AG-7 | — | Clinical MCP Tool Server | Tool chaining achieves unauthorized FHIR output | 6.2 | Medium | No Control Found | 6.2 | Medium |
| T-7 | — | Clinical MCP Tool Server | Compromised MCP Tool Server tampers with FHIR operations | 6.2 | Medium | No Control Found | 6.2 | Medium |
| D-2 | — | Patient Summary Generator | Spurious summary requests flood Patient Summary Generator | 6.2 | Medium | No Control Found | 6.2 | Medium |
| AG-2 | — | Supervisor Orchestrator | Compromised orchestrator abuses delegation authority | 6.1 | Medium | No Control Found | 6.1 | Medium |
| D-17 | — | HIPAA RBAC + Policy Engine | RBAC request flood causes policy engine unavailability | 6.1 | Medium | No Control Found | 6.1 | Medium |
| I-1 | — | Physician Clinical Portal | PHI disclosed via insecure HTTPS config or error messages | 6.1 | Medium | No Control Found | 6.1 | Medium |
| LLM-4 | — | Risk Stratification Model | Adversarial patient records manipulate risk scores | 6.1 | Medium | No Control Found | 6.1 | Medium |
| T-10 | — | FHIR Resource Store | Attacker tampers with patient records | 6.1 | Medium | No Control Found | 6.1 | Medium |
| T-11 | — | Clinical Guideline RAG Corpus | Attacker poisons RAG corpus adversarially | 5.5 | Medium | No Control Found | 5.5 | Medium |
| LLM-5 | — | Risk Stratification Model | Fine-tuning poisoning | 5.5 | Medium | No Control Found | 5.5 | Medium |
| T-16 | — | Outcomes Telemetry and Physician Override Audit Store | Attacker injects adversarial override signals | 5.5 | Medium | No Control Found | 5.5 | Medium |
| T-17 | — | HIPAA RBAC + Policy Engine | Attacker tampers with RBAC policy rules | 5.5 | Medium | No Control Found | 5.5 | Medium |
| E-11 | — | HIPAA RBAC + Policy Engine | Attacker exploits RBAC vulnerability to admin escalation | 5.5 | Medium | No Control Found | 5.5 | Medium |
| E-12 | — | Consent and De-identification Guardrail | Attacker bypasses consent enforcement | 5.5 | Medium | No Control Found | 5.5 | Medium |
| T-2 | — | Patient Summary Generator | Attacker tampers with patient-facing summaries | 5.5 | Medium | No Control Found | 5.5 | Medium |
| T-13 | — | Model Inference API Gateway | Attacker tampers with API Gateway configuration | 5.5 | Medium | No Control Found | 5.5 | Medium |
| S-3 | — | Physician Clinical Portal | Attacker spoofs portal to intercept clinical data | 5.6 | Medium | No Control Found | 5.6 | Medium |
| T-5 | — | Diagnostic Agent | Attacker tampers with Diagnostic Agent tool calls | 5.6 | Medium | No Control Found | 5.6 | Medium |
| T-6 | — | Treatment Planner Agent | Attacker tampers with Treatment Planner Agent | 5.6 | Medium | No Control Found | 5.6 | Medium |
| AG-5 | — | Treatment Planner Agent | Treatment Planner Agent incorporates adversarial context | 5.6 | Medium | No Control Found | 5.6 | Medium |
| E-10 | — | Model Inference API Gateway | Compromised API Gateway escalates to access inference models | 5.6 | Medium | No Control Found | 5.6 | Medium |
| S-7 | — | Diagnostic Agent | Attacker spoofs Diagnostic Agent to inject false findings | 5.9 | Medium | No Control Found | 5.9 | Medium |
| S-8 | — | Treatment Planner Agent | Attacker spoofs Treatment Planner Agent responses | 5.9 | Medium | No Control Found | 5.9 | Medium |
| S-9 | — | Clinical MCP Tool Server | Attacker spoofs MCP Tool Server to return malicious data | 5.9 | Medium | No Control Found | 5.9 | Medium |
| E-5 | — | Diagnostic Agent | Compromised Diagnostic Agent escalates to unauthorized operations | 5.9 | Medium | No Control Found | 5.9 | Medium |
| E-6 | — | Treatment Planner Agent | Compromised Treatment Planner Agent escalates privileges | 5.9 | Medium | No Control Found | 5.9 | Medium |
| R-1 | — | Physician | Physician denies issuing clinical query | 5.9 | Medium | No Control Found | 5.9 | Medium |
| R-2 | — | Patient | Patient denies submitting EHR update events | 5.9 | Medium | No Control Found | 5.9 | Medium |
| AG-3 | — | Diagnostic Agent | Diagnostic Agent autonomously executes unauthorized actions | 5.8 | Medium | No Control Found | 5.8 | Medium |
| E-4 | — | Supervisor Orchestrator | Compromised orchestrator escalates to bypass delegation | 5.8 | Medium | No Control Found | 5.8 | Medium |
| E-9 | — | Risk Stratification Model | Adversarially manipulated risk scores trigger unintended actions | 5.8 | Medium | No Control Found | 5.8 | Medium |
| T-4 | — | Supervisor Orchestrator | Compromised orchestrator tampers with delegation | 5.8 | Medium | No Control Found | 5.8 | Medium |
| I-2 | — | Patient Summary Generator | Patient summaries include unauthorized PHI | 5.8 | Medium | No Control Found | 5.8 | Medium |
| AGP-03 | — | Supervisor Orchestrator | Multi-agent cascading delegation exhibits emergent behavior | 5.7 | Medium | No Control Found | 5.7 | Medium |
| AG-4 | — | Diagnostic Agent | Compromised Diagnostic Agent abuses MCP Tool Server | 5.7 | Medium | No Control Found | 5.7 | Medium |
| AG-6 | — | Treatment Planner Agent | Compromised Treatment Planner Agent abuses MCP Tool Server | 5.7 | Medium | No Control Found | 5.7 | Medium |
| D-8 | — | Clinical LLM | Large prompt floods exhaust Clinical LLM inference capacity | 5.7 | Medium | No Control Found | 5.7 | Medium |
| R-5 | — | Inter-Agent Communication Channel | Channel fails non-repudiable records of delegation | 5.7 | Medium | No Control Found | 5.7 | Medium |
| AG-1 | — | Supervisor Orchestrator | Autonomous delegation bypasses human oversight | 5.0 | Medium | No Control Found | 5.0 | Medium |
| R-6 | — | Supervisor Orchestrator | Orchestrator fails non-repudiable records of decisions | 5.0 | Medium | No Control Found | 5.0 | Medium |
| I-10 | — | FHIR Resource Store | Patient PHI disclosed via unauthorized FHIR query | 5.4 | Medium | No Control Found | 5.4 | Medium |
| D-4 | — | Supervisor Orchestrator | High-volume task result flood causes orchestrator failure | 5.4 | Medium | No Control Found | 5.4 | Medium |
| D-5 | — | Diagnostic Agent | Tool call floods disrupt Diagnostic Agent | 5.4 | Medium | No Control Found | 5.4 | Medium |
| D-7 | — | Clinical MCP Tool Server | Excessive JSON-RPC calls exhaust MCP server resources | 5.4 | Medium | No Control Found | 5.4 | Medium |
| D-10 | — | FHIR Resource Store | FHIR query floods degrade patient record availability | 5.4 | Medium | No Control Found | 5.4 | Medium |
| S-4 | — | Patient Summary Generator | Attacker spoofs Patient Summary Generator | 5.3 | Medium | No Control Found | 5.3 | Medium |
| AGP-02 | — | Outcomes Telemetry and Physician Override Audit Store | Persistent-state learning loop enables temporal attack | 5.3 | Medium | No Control Found | 5.3 | Medium |
| I-7 | — | Clinical MCP Tool Server | PHI exposed to unauthorized agents via MCP | 5.3 | Medium | No Control Found | 5.3 | Medium |
| LLM-1 | — | Clinical LLM | Clinical LLM PHI exposure | 5.3 | Medium | No Control Found | 5.3 | Medium |
| T-12 | — | Medical Literature Vector Index | Attacker injects malicious vector embeddings | 5.3 | Medium | No Control Found | 5.3 | Medium |
| T-14 | — | EHR Ingestion Queue | Attacker tampers with EHR events in ingestion queue | 5.3 | Medium | No Control Found | 5.3 | Medium |
| T-1 | — | Physician Clinical Portal | Attacker tampers with clinical recommendations | 5.2 | Medium | No Control Found | 5.2 | Medium |
| D-15 | — | Clinical Audit Log | Excessive log entries cause disk exhaustion | 5.2 | Medium | No Control Found | 5.2 | Medium |
| D-18 | — | Consent and De-identification Guardrail | PHI processing flood saturates de-id capacity | 5.2 | Medium | No Control Found | 5.2 | Medium |
| I-8 | — | Clinical LLM | Clinical LLM surfaces PHI from training data | 5.1 | Medium | No Control Found | 5.1 | Medium |
| I-9 | — | Risk Stratification Model | Risk model leaks patient cohort data | 5.1 | Medium | No Control Found | 5.1 | Medium |
| LLM-6 | — | Risk Stratification Model | Membership inference attack violates patient privacy | 5.1 | Medium | No Control Found | 5.1 | Medium |
| I-5 | — | Diagnostic Agent | Diagnostic Agent exposes patient context | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-6 | — | Treatment Planner Agent | Treatment Planner Agent discloses patient data | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-14 | — | EHR Ingestion Queue | EHR update events in queue disclosed | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-15 | — | Clinical Audit Log | Unauthorized audit log read discloses sensitive data | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-16 | — | Outcomes Telemetry and Physician Override Audit Store | Telemetry access discloses clinical patterns | 4.9 | Medium | No Control Found | 4.9 | Medium |
| R-3 | — | Physician Clinical Portal | Portal fails non-repudiable recommendation records | 4.8 | Medium | No Control Found | 4.8 | Medium |
| R-4 | — | Patient Summary Generator | Summary Generator fails non-repudiable records | 4.8 | Medium | No Control Found | 4.8 | Medium |
| R-9 | — | Clinical MCP Tool Server | MCP Tool Server fails non-repudiable FHIR records | 4.8 | Medium | No Control Found | 4.8 | Medium |
| T-15 | — | Clinical Audit Log | Attacker tampers with audit log entries | 4.8 | Medium | No Control Found | 4.8 | Medium |
| I-17 | — | HIPAA RBAC + Policy Engine | RBAC engine leaks access control policies | 4.8 | Medium | No Control Found | 4.8 | Medium |
| LLM-3 | — | Clinical LLM | Adversary extracts Clinical LLM knowledge | 4.8 | Medium | No Control Found | 4.8 | Medium |
| D-16 | — | Outcomes Telemetry and Physician Override Audit Store | Spurious override signals degrade learning loop | 4.7 | Medium | No Control Found | 4.7 | Medium |
| LLM-2 | — | Clinical LLM | Adversary poisons training data via learning loop | 4.7 | Medium | No Control Found | 4.7 | Medium |
| R-13 | — | HIPAA RBAC + Policy Engine | RBAC engine fails non-repudiable access decisions | 4.7 | Medium | No Control Found | 4.7 | Medium |
| D-9 | — | Risk Stratification Model | High-volume risk inference requests saturate model | 4.6 | Medium | No Control Found | 4.6 | Medium |
| D-6 | — | Treatment Planner Agent | Oversized retrieval queries exhaust Treatment Planner | 4.6 | Medium | No Control Found | 4.6 | Medium |
| D-11 | — | Clinical Guideline RAG Corpus | Retrieval floods saturate RAG Corpus capacity | 4.6 | Medium | No Control Found | 4.6 | Medium |
| D-12 | — | Medical Literature Vector Index | Excessive retrieval queries degrade Vector Index | 4.6 | Medium | No Control Found | 4.6 | Medium |
| D-14 | — | EHR Ingestion Queue | Malformed EHR events cause queue saturation | 4.6 | Medium | No Control Found | 4.6 | Medium |
| I-4 | — | Supervisor Orchestrator | Compromise exposes aggregated sensitive patient data | 4.3 | Medium | No Control Found | 4.3 | Medium |
| I-13 | — | Model Inference API Gateway | API Gateway exposes inference request logs | 4.2 | Medium | No Control Found | 4.2 | Medium |
| S-14 | — | Consent and De-identification Guardrail | Attacker spoofs guardrail returning raw PHI | 4.2 | Medium | No Control Found | 4.2 | Medium |
| T-9 | — | Risk Stratification Model | Attacker tampers with fine-tuning data | 4.2 | Medium | No Control Found | 4.2 | Medium |
| I-18 | — | Consent and De-identification Guardrail | Guardrail discloses raw PHI through de-identification failure | 4.5 | Medium | No Control Found | 4.5 | Medium |
| S-10 | — | Clinical LLM | Attacker spoofs Clinical LLM completion responses | 4.5 | Medium | No Control Found | 4.5 | Medium |
| S-11 | — | Risk Stratification Model | Attacker spoofs Risk Stratification Model output | 4.5 | Medium | No Control Found | 4.5 | Medium |
| S-12 | — | Model Inference API Gateway | Attacker spoofs API Gateway to return fabricated responses | 4.5 | Medium | No Control Found | 4.5 | Medium |
| S-13 | — | HIPAA RBAC + Policy Engine | Attacker spoofs RBAC engine to issue false authorization | 4.5 | Medium | No Control Found | 4.5 | Medium |
| T-18 | — | Consent and De-identification Guardrail | Attacker tampers with de-identification configuration | 4.5 | Medium | No Control Found | 4.5 | Medium |
| R-7 | — | Diagnostic Agent | Diagnostic Agent denies issuing tool calls | 4.1 | Medium | No Control Found | 4.1 | Medium |
| R-8 | — | Treatment Planner Agent | Treatment Planner Agent denies tool calls | 4.1 | Medium | No Control Found | 4.1 | Medium |
| R-10 | — | Clinical LLM | Clinical LLM fails non-repudiable prompt-completion records | 4.1 | Medium | No Control Found | 4.1 | Medium |
| R-11 | — | Risk Stratification Model | Risk model fails non-repudiable inference records | 4.1 | Medium | No Control Found | 4.1 | Medium |
| R-12 | — | Model Inference API Gateway | API Gateway fails non-repudiable inference records | 4.1 | Medium | No Control Found | 4.1 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| I-11 | — | Clinical Guideline RAG Corpus | RAG Corpus inadvertently indexes patient data | 3.7 | Low | No Control Found | 3.7 | Low |
| I-12 | — | Medical Literature Vector Index | Vector Index exposes research data | 3.7 | Low | No Control Found | 3.7 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 6 | 5.6% |
| Medium | 100 | 92.6% |
| Low | 2 | 1.9% |
| **Total** | **108** | **100%** |

---

## 3. Control Details

No compensating controls were detected in the target codebase for any of the 108 CDSS threat findings. All 8 control categories were scanned across production files in the tachi pipeline. The absence of detected controls is accurate and expected — the tachi repository does not implement a clinical decision support system.

**Scanned files (Phase A pattern matching, all Phase B rejected or no patterns found)**:

- `scripts/tachi_parsers.py` — Python parser library; `print(..., file=sys.stderr)` error output found but rejected (generic operational logging, not security audit logging)
- `scripts/extract-report-data.py` — Report data extractor; `validate()` function found but is a data-structure consistency checker, not an input security boundary validator
- `scripts/extract-infographic-data.py` — Infographic data extractor; error output via stderr only
- `scripts/install.sh` — Installation script; no security controls applicable
- `stacks/fastapi-react/scaffold/backend/app/core/middleware.py` — CORS middleware present but **rejected** (stack scaffold template, no running application context, not registered to any production route)
- `stacks/fastapi-react/scaffold/backend/app/api/deps.py` — `get_current_user()` stub present but **rejected** (explicitly marked as NotImplemented stub, not a functioning control)
- `stacks/fastapi-react/scaffold/backend/app/core/exceptions.py` — `PermissionDeniedError` class present but **rejected** (exception type definition without enforcement logic wired to any route)

No authentication, rate limiting, encryption, CSRF, CSP/security headers, or access control patterns were confirmed as active controls. The tachi pipeline operates as a local CLI tool that reads and writes markdown files — it does not expose HTTP endpoints, manage user sessions, or process patient data.

---

## 4. Recommendations

All 108 findings have No Control Found status. The recommendations below address the reference CDSS architecture — they describe what the clinical system being modeled would need to implement. Recommendations are grouped by inherent severity and sorted by composite score descending within each group.

> **Adopter Note**: These recommendations describe controls for the Healthcare CDSS reference architecture, not for the tachi toolkit itself. When running this pipeline against your own codebase, recommendations will reference your actual file structure and technology stack.

### High Risk Gaps

#### 1. S-1 — Physician (Composite: 8.4, High)

**Current Status**: No Control Found

**What to Implement**: Implement multi-factor authentication (MFA) and credential replay protection for the physician authentication endpoint. Deploy a short-lived JWT or OAuth 2.0 token scheme with cryptographic binding to session context. Add token replay detection using a nonce or jti claim validated against a server-side token store.

**Where to Implement**: `src/auth/physician-auth.middleware.ts` — physician-facing API gateway authentication layer; add PKCE or DPoP binding to the OAuth flow for the clinical portal.

**Reference Patterns**: `jsonwebtoken` (JWT with jti-based replay detection), `passport-oauth2` (OAuth 2.0 PKCE flow), `redis`-based nonce store for replay prevention.

**Effort Estimate**: High — requires designing and deploying a token management service with replay detection infrastructure.

---

#### 2. S-2 — Patient (Composite: 7.4, High)

**Current Status**: No Control Found

**What to Implement**: Implement patient identity verification with signed event envelopes on the EHR ingestion endpoint. Each incoming EHR update event should carry a verifiable patient identity token (e.g., SMART on FHIR patient context) and a message authentication code preventing tampering. Deploy input schema validation to reject malformed or unexpected event structures.

**Where to Implement**: `src/ingestion/ehr-ingest.handler.ts` — EHR ingestion endpoint; add SMART on FHIR patient context validation before accepting update events.

**Reference Patterns**: SMART on FHIR Patient Context, `zod` or `joi` schema validation on event payloads, HMAC-signed event envelopes.

**Effort Estimate**: High — SMART on FHIR integration requires HL7 FHIR server configuration and identity provider federation.

---

#### 3. D-1 — Physician Clinical Portal (Composite: 7.1, High)

**Current Status**: No Control Found

**What to Implement**: Implement request rate limiting on the physician clinical portal API endpoints. Configure a per-IP and per-session rate limiter with thresholds calibrated to expected clinical usage patterns. Add a circuit breaker wrapping the downstream CDSS orchestration layer to prevent cascade failures under load.

**Where to Implement**: `src/middleware/rate-limiter.ts` — apply rate limiting middleware to all portal API routes; add circuit breaker around CDSS query dispatch.

**Reference Patterns**: `express-rate-limit` (per-IP window with 429 response), `opossum` or `cockatiel` (circuit breaker for downstream orchestration), Nginx upstream rate limiting at load balancer layer.

**Effort Estimate**: Medium — rate limiting middleware is a single-file addition; circuit breaker requires wrapping the existing orchestration dispatch.

---

#### 4. E-1 — Physician Clinical Portal (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement role-based access control (RBAC) enforcing per-physician data scope on all portal data retrieval endpoints. Add resource ownership validation that prevents horizontal privilege escalation to other physicians' or patients' data. Every data fetch endpoint must assert that the requesting session's physician ID matches the requested resource scope.

**Where to Implement**: `src/middleware/authorization.middleware.ts` — add RBAC guard enforcing physician-to-patient scope; `src/routes/clinical-data.routes.ts` — apply guard to all data retrieval handlers.

**Reference Patterns**: `casl` (ability-based authorization), `casbin` (RBAC policy engine), `@nestjs/passport` with `RolesGuard`, resource ownership check pattern `req.user.id === resource.physicianId`.

**Effort Estimate**: High — requires RBAC policy design across all data retrieval endpoints and consistent enforcement throughout the portal API surface.

---

#### 5. S-5 — Inter-Agent Communication Channel (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement message authentication on the inter-agent communication channel. Each delegation message must carry a cryptographic signature from the originating supervisor agent, verified by the receiving specialist agent before execution. Use a shared asymmetric key infrastructure where the supervisor holds the private signing key and specialist agents hold the corresponding verification key.

**Where to Implement**: `src/agent-bus/message-auth.ts` — add HMAC-SHA256 or Ed25519 signature generation on outbound delegation messages; add signature verification on inbound message receipt.

**Reference Patterns**: `tweetnacl` or `@noble/ed25519` (Ed25519 message signing), JOSE JWS (JSON Web Signature) for structured agent messages, mutual TLS for transport-level channel authentication.

**Effort Estimate**: High — requires a key distribution and rotation infrastructure for the multi-agent message bus.

---

#### 6. T-3 — Inter-Agent Communication Channel (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement message integrity protection on all inter-agent delegation messages and specialist results. Encrypt the message bus channel using TLS with mutual authentication, and add per-message HMAC integrity tokens that detect tampering in transit. Log all message integrity failures to the clinical audit log.

**Where to Implement**: `src/agent-bus/transport.ts` — enforce TLS with certificate pinning on the agent bus transport; add HMAC verification on message ingestion.

**Reference Patterns**: TLS 1.3 with mutual certificate authentication, `crypto.createHmac` (Node.js built-in), structured logging of integrity failures via `winston` or `pino`.

**Effort Estimate**: High — TLS mutual auth on an internal message bus requires certificate management infrastructure and impacts all agent-to-agent communication paths.

---

### Medium Risk Gaps

#### 7. AG-8 — Inter-Agent Communication Channel (Composite: 6.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement per-agent message quotas and channel-level rate limiting to prevent resource exhaustion by a compromised agent. Each agent instance should have a configurable message-per-second budget on the inter-agent bus. Deploy a circuit breaker that isolates an agent flooding the channel, preventing cascade to downstream specialist agents.

**Where to Implement**: `src/agent-bus/quota-enforcer.ts` — per-agent rate limiter with configurable thresholds; quarantine mechanism for agents exceeding burst limits.

**Reference Patterns**: Token bucket algorithm per agent identity, `rate-limiter-flexible` (per-key rate limiting), circuit breaker pattern (`opossum`) isolating misbehaving agents.

**Effort Estimate**: Medium — requires per-agent identity tracking on the bus and quota enforcement logic.

---

#### 8. D-3 — Inter-Agent Communication Channel (Composite: 6.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement channel-level message rate limiting and backpressure on the inter-agent delegation bus. Set maximum delegation message ingestion rates and queue depth limits. Add message priority queuing so clinical-critical delegation messages are processed ahead of non-urgent agent coordination traffic.

**Where to Implement**: `src/agent-bus/rate-limiter.ts` — channel-wide ingestion rate limit; queue depth monitoring with overflow shedding.

**Reference Patterns**: Token bucket rate limiting, priority queue with configurable depth limits, dead letter queue for shed messages.

**Effort Estimate**: Medium — message bus backpressure is a configuration and middleware concern at the bus layer.

---

#### 9. E-2 — Patient Summary Generator (Composite: 6.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement patient-scope authorization on the Patient Summary Generator. All summary requests must be validated against the requesting session's authorized patient list. Add an ABAC policy check verifying that the requestor has an active care relationship with the requested patient before generating the summary.

**Where to Implement**: `src/services/patient-summary.service.ts` — add patient-scope authorization check before processing summary requests; `src/middleware/patient-authz.middleware.ts` — ABAC policy guard.

**Reference Patterns**: `casbin` (ABAC policy with patient-scope rules), `casl` (ability-based scoping), care-relationship verification against FHIR CareTeam resources.

**Effort Estimate**: High — requires integrating with FHIR CareTeam data to establish authorized patient relationships per physician session.

---

#### 10. E-8 — Clinical LLM (Composite: 6.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement prompt input validation and output sanitization for the Clinical LLM inference endpoint. Add a prompt injection detection layer that scans input for known injection patterns before forwarding to the model. Enforce strict output schema validation to detect anomalous reasoning responses that deviate from expected clinical recommendation formats.

**Where to Implement**: `src/llm/prompt-guard.ts` — pre-inference prompt validation; `src/llm/output-validator.ts` — post-inference output schema check.

**Reference Patterns**: Prompt injection regex/pattern library, input sanitization with allowlist-based token filtering, Pydantic or Zod schema validation on structured LLM outputs, secondary classification model for injection detection.

**Effort Estimate**: High — prompt injection is an evolving threat class; implementing a robust detection layer requires ongoing pattern maintenance and may require a secondary classification model.

---

#### 11. E-3 — Inter-Agent Communication Channel (Composite: 6.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement least-privilege access controls on the inter-agent communication channel. Each agent should only be able to send message types appropriate to its role (specialist agents cannot send delegation messages; only the supervisor can initiate delegation). Enforce role-based message type restrictions at the bus level.

**Where to Implement**: `src/agent-bus/access-control.ts` — message type allowlist per agent role; enforce at bus ingestion point.

**Reference Patterns**: Role-based message type enforcement, agent identity tokens signed by the orchestrator, message schema registry with per-role permitted message types.

**Effort Estimate**: Medium — requires agent identity management and per-role message type allowlists at the bus level.

---

#### 12. T-8 — Clinical LLM (Composite: 6.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement request signing and integrity verification on prompts forwarded by the Model Inference API Gateway to the Clinical LLM. The gateway must attest that the prompt content has not been modified in transit from the originating agent. Add an HMAC on each prompt payload that the LLM endpoint verifies before processing.

**Where to Implement**: `src/gateway/prompt-integrity.ts` — HMAC signing on outbound prompt payloads; `src/llm/prompt-verifier.ts` — HMAC verification on inbound prompts.

**Reference Patterns**: `crypto.createHmac` (Node.js built-in), request signing with shared symmetric key between gateway and LLM endpoint, audit logging of all prompt-completion pairs.

**Effort Estimate**: Medium — HMAC signing on prompt payloads is a tractable addition to the API gateway layer.

---

#### 13. I-3 — Inter-Agent Communication Channel (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement end-to-end encryption on the inter-agent communication channel for all messages containing PHI. Enforce TLS 1.3 on the transport layer and add application-layer field-level encryption for patient identifiers and clinical data payloads within delegation messages.

**Where to Implement**: `src/agent-bus/transport.ts` — TLS 1.3 with certificate verification; `src/agent-bus/phi-encryptor.ts` — field-level encryption for PHI fields in message payloads.

**Reference Patterns**: TLS 1.3 mutual authentication, `@aws-sdk/client-kms` (key management for field-level encryption), NaCl secretbox for symmetric payload encryption.

**Effort Estimate**: High — field-level encryption requires key management infrastructure and schema changes to message formats.

---

#### 14. E-7 — Clinical MCP Tool Server (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement tool-call authorization on the Clinical MCP Tool Server. All FHIR tool operations must be authorized against the requesting agent's permitted tool scope. Add a policy engine that validates tool call intent (operation type, resource type, patient scope) against the agent's declared role before executing.

**Where to Implement**: `src/mcp-server/tool-authz.ts` — per-operation authorization policy; enforce before dispatching to FHIR endpoints.

**Reference Patterns**: `casbin` (ABAC with tool-operation policy), JSON schema validation on tool call parameters, FHIR SMART scopes (`patient/*.read`, `patient/*.write`).

**Effort Estimate**: High — requires a policy engine integrated with the MCP Tool Server's dispatch layer and synchronized with agent identity tokens.

---

#### 15. S-6 — Supervisor Orchestrator (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement cryptographic identity verification for the Supervisor Orchestrator. The orchestrator must present a verifiable identity credential (signed JWT or mutual TLS certificate) when establishing connections with specialist agents and when receiving connections from external components. Specialist agents must verify orchestrator identity before accepting delegation messages.

**Where to Implement**: `src/orchestrator/identity.ts` — orchestrator identity token issuance; `src/agents/delegation-verifier.ts` — orchestrator identity verification on inbound delegation.

**Reference Patterns**: Ed25519 signed identity tokens, mutual TLS with orchestrator-specific certificate, JWT with `iss` claim bound to the orchestrator service identity.

**Effort Estimate**: High — orchestrator identity infrastructure requires PKI setup and propagation to all specialist agent components.

---

#### 16. D-13 — Model Inference API Gateway (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement request rate limiting and adaptive throttling on the Model Inference API Gateway. Configure per-caller rate limits, total inference concurrency caps, and request queue depth limits. Add a circuit breaker that drops non-urgent inference requests when the gateway approaches capacity saturation.

**Where to Implement**: `src/gateway/rate-limiter.ts` — per-caller rate limiting with window-based token buckets; circuit breaker on inference dispatch.

**Reference Patterns**: `express-rate-limit` or `rate-limiter-flexible`, Nginx upstream rate limiting, `opossum` circuit breaker with failure threshold configuration.

**Effort Estimate**: Medium — API gateway rate limiting is a well-understood middleware pattern.

---

#### 17. T-10 — FHIR Resource Store (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement write integrity controls on the FHIR Resource Store. All patient record write operations must be authorized via the RBAC policy engine and logged to the immutable clinical audit log. Add optimistic locking (ETag/version-based) on FHIR resources to detect concurrent modification attacks.

**Where to Implement**: `src/fhir/write-guard.ts` — write authorization check + audit logging; ETag validation middleware on FHIR update operations.

**Reference Patterns**: FHIR ETag-based optimistic locking (`If-Match` header), SMART on FHIR write scopes, immutable audit log via append-only log store.

**Effort Estimate**: High — requires RBAC integration with the FHIR server and audit log infrastructure.

---

#### 18. I-1 — Physician Clinical Portal (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Enforce HTTPS with HSTS on the Physician Clinical Portal and configure Content Security Policy to prevent information leakage through error responses. Implement generic error handling that does not expose PHI or stack traces. Add X-Content-Type-Options, X-Frame-Options, and Referrer-Policy headers.

**Where to Implement**: `src/middleware/security-headers.ts` — apply `helmet()` with strict CSP directives; configure generic error handler to strip sensitive information.

**Reference Patterns**: `helmet` (Node.js security headers middleware), CSP `default-src 'self'` with explicit allowlists, generic error handler returning `{ error: 'An error occurred' }` without detail.

**Effort Estimate**: Low — security headers are a configuration change; generic error handling is a single middleware addition.

---

#### 19. LLM-4 — Risk Stratification Model (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement adversarial input detection for the Risk Stratification Model. Add a pre-inference validation layer that checks incoming patient record feature vectors for statistical anomalies indicative of adversarial perturbation. Log detected anomalies and route suspicious inputs for human review rather than automated risk stratification.

**Where to Implement**: `src/risk-model/input-validator.ts` — statistical anomaly detection on feature vectors; anomaly logging to clinical audit trail.

**Reference Patterns**: Statistical outlier detection (Z-score, isolation forest) on feature distributions, input schema validation with range constraints per clinical field, human-in-the-loop review queue for flagged inputs.

**Effort Estimate**: High — adversarial ML input detection requires domain-specific feature engineering and ongoing model monitoring.

---

#### 20. T-11 — Clinical Guideline RAG Corpus (Composite: 5.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement content integrity verification for the Clinical Guideline RAG Corpus. All documents added to the corpus must be cryptographically hashed on ingestion and periodically re-verified. Add provenance metadata tracking source, timestamp, and ingestion authority for each document chunk. Deploy anomaly detection on embedding distributions to detect injected adversarial content.

**Where to Implement**: `src/rag/corpus-integrity.ts` — document hash registry and re-verification schedule; `src/rag/embedding-monitor.ts` — distribution drift detection.

**Reference Patterns**: SHA-256 document fingerprinting, content integrity Merkle tree, vector distribution monitoring with cosine similarity thresholds.

**Effort Estimate**: High — corpus integrity requires ongoing monitoring infrastructure and integration with the RAG ingestion pipeline.

---

#### 21. T-17 — HIPAA RBAC + Policy Engine (Composite: 5.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement change control and integrity verification for RBAC policy rules. All policy changes must be authorized through a workflow requiring approval from an authorized administrator, logged to an immutable audit log, and cryptographically signed. Deploy policy version control with rollback capability.

**Where to Implement**: `src/rbac/policy-change-control.ts` — approval workflow for policy mutations; append-only audit log of all policy changes with digital signatures.

**Reference Patterns**: `casbin` (policy versioning), signed policy bundles (OPA/Rego), immutable audit trail with HMAC-chained entries.

**Effort Estimate**: High — requires a policy change management workflow and immutable audit infrastructure.

---

#### 22. E-11 — HIPAA RBAC + Policy Engine (Composite: 5.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Harden the HIPAA RBAC Policy Engine against privilege escalation by implementing strict separation of duties: no single role should be able to both modify policies and hold admin-level permissions. Add immutable policy evaluation logging and enforce defense-in-depth with secondary authorization checks on sensitive operations.

**Where to Implement**: `src/rbac/policy-engine.ts` — separation of duties enforcement; secondary authorization gate on admin-level operations.

**Reference Patterns**: `casbin` with role hierarchy constraints, separation of duties policy pattern (no policy-admin role can hold data-access privileges), OPA Rego policy with constraint validation.

**Effort Estimate**: High — separation of duties requires redesigning the role hierarchy and enforcing it consistently.

---

#### 23. E-12 — Consent and De-identification Guardrail (Composite: 5.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement multi-layer consent enforcement with a defense-in-depth approach. The guardrail should not be a single bypass-able gate. Add secondary consent verification at the data layer and implement tamper-evident consent records that are cryptographically linked to the patient identity.

**Where to Implement**: `src/consent/guardrail.ts` — primary consent check; `src/data/consent-secondary-check.ts` — secondary layer at data access; `src/consent/consent-ledger.ts` — cryptographically chained consent records.

**Reference Patterns**: Merkle-chained consent records, dual-approval pattern for consent bypass, SMART on FHIR consent scope validation.

**Effort Estimate**: High — multi-layer consent requires architectural changes to data access paths.

---

#### 24. AG-2 — Supervisor Orchestrator (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement delegation authority limits on the Supervisor Orchestrator. The orchestrator's delegation permissions should be defined at deployment time and enforced at runtime — the orchestrator cannot grant capabilities it does not possess. Add a human-in-the-loop checkpoint for high-impact clinical delegations (e.g., treatment recommendations above a risk threshold).

**Where to Implement**: `src/orchestrator/delegation-limits.ts` — capability boundary enforcement; `src/orchestrator/human-review-gate.ts` — high-impact action checkpoint.

**Reference Patterns**: Capability-based security model, OAuth 2.0 scope restriction on agent tokens, human approval queue for high-stakes decisions.

**Effort Estimate**: High — capability-bounded delegation requires redesigning the orchestrator's authority model.

---

#### 25. R-1 — Physician (Composite: 5.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement immutable audit logging for all physician clinical queries. Each query must be logged with a cryptographically non-repudiable record including physician identity (authenticated session token hash), query parameters, timestamp, and response identifiers. Store audit logs in an append-only log store that cannot be modified by the physician or clinical portal application.

**Where to Implement**: `src/audit/clinical-query-log.ts` — structured audit log entry on every physician query; append-only log store integration.

**Reference Patterns**: `winston` with append-only transport, structured log entries with HMAC-chained integrity, centralized SIEM integration.

**Effort Estimate**: Medium — structured audit logging is a well-understood pattern; the append-only store is the key infrastructure requirement.

---

#### 26. R-5 — Inter-Agent Communication Channel (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement non-repudiable message logging for all inter-agent delegation messages. Each delegation and response must be logged with the sending agent's cryptographic signature in an append-only audit log. The log must be independent of the agent bus so that a compromised channel cannot erase its own audit trail.

**Where to Implement**: `src/agent-bus/audit-logger.ts` — signed delegation log entries; independent append-only log store outside the agent bus trust boundary.

**Reference Patterns**: Signed log entries with Ed25519, independent log forwarder, write-once log storage (AWS CloudTrail, append-only S3 bucket policy).

**Effort Estimate**: Medium — requires integrating the agent bus with an independent logging infrastructure.

---

#### 27. AGP-01 — Inter-Agent Communication Channel (Composite: 6.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement behavioral monitoring for coordinated agent activity patterns. Deploy a cross-agent telemetry aggregator that detects statistical anomalies in multi-agent coordination (synchronized message timing, unusual delegation fan-out, correlated output deviations across specialist agents). Trigger human-in-the-loop review when collusion indicators are detected.

**Where to Implement**: `src/monitoring/agent-telemetry.ts` — cross-agent behavioral aggregation; anomaly detection with configurable thresholds; alerting to human oversight queue.

**Reference Patterns**: Statistical process control on agent messaging patterns, cross-agent correlation analysis, human oversight escalation queue.

**Effort Estimate**: High — behavioral monitoring requires a telemetry infrastructure and domain-specific anomaly thresholds.

---

#### 28. AGP-02 — Outcomes Telemetry and Physician Override Audit Store (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement temporal integrity controls on the learning loop feedback pathway. Validate that override signals in the telemetry store are consistent with contemporaneous clinical events (timestamp validation, signal provenance verification). Add rate limiting on override signal ingestion to prevent flooding the learning loop with adversarial signals.

**Where to Implement**: `src/telemetry/override-validator.ts` — temporal consistency check on incoming override signals; rate limiting on telemetry ingestion.

**Reference Patterns**: Timestamp validation with configurable staleness thresholds, signal provenance cryptographic binding, statistical anomaly detection on override signal distributions.

**Effort Estimate**: Medium — temporal validation is an addition to the telemetry ingestion pipeline.

---

#### 29. AGP-03 — Supervisor Orchestrator (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement delegation depth limits and cycle detection on the Supervisor Orchestrator to prevent emergent cascading delegation behaviors. Set a maximum delegation depth (e.g., 3 hops) and enforce it at runtime. Add monitoring for unexpected delegation fan-out patterns that may indicate emergent coordination.

**Where to Implement**: `src/orchestrator/delegation-limiter.ts` — depth counter and cycle detection on delegation chains; monitoring alerts on abnormal fan-out.

**Reference Patterns**: Delegation depth counter propagated in message headers, directed acyclic graph validation on delegation chains, fan-out monitoring with configurable thresholds.

**Effort Estimate**: Medium — depth limiting is a counter mechanism in the orchestration logic.

---

*Recommendations 30–108 follow the same pattern as above. For brevity, the remaining 79 Medium and Low risk gap recommendations are summarized below by component group. Each would receive the same structure (What / Where / Reference Patterns / Effort) in a production report.*

**Remaining unaddressed components requiring full recommendation blocks**:
- Diagnostic Agent (S-7, E-5, AG-3, AG-4, I-5, R-7, D-5, T-5): authentication, access control, logging, rate limiting
- Treatment Planner Agent (S-8, E-6, AG-5, AG-6, I-6, R-8, D-6, T-6): authentication, access control, logging, rate limiting
- Clinical MCP Tool Server (S-9, AG-7, T-7, I-7, R-9, D-7, E-7): access control, input validation, logging
- FHIR Resource Store (T-10, I-10, D-10): encryption, access control, input validation
- Risk Stratification Model (LLM-4, LLM-5, LLM-6, E-9, T-9, I-9, D-9, S-11, R-11): input validation, logging, encryption
- Clinical LLM (E-8, T-8, D-8, I-8, LLM-1, LLM-2, LLM-3, S-10, R-10): input validation, logging, rate limiting
- Model Inference API Gateway (D-13, E-10, T-13, I-13, S-12, R-12): rate limiting, access control, logging
- HIPAA RBAC + Policy Engine (T-17, E-11, D-17, I-17, S-13, R-13): access control, logging, input validation
- Consent and De-identification Guardrail (E-12, D-18, T-18, I-18, S-14): access control, encryption, logging
- Clinical Audit Log (D-15, T-15, I-15): encryption, access control, logging (self-referential — audit log integrity protection)
- EHR Ingestion Queue (T-14, D-14, I-14): input validation, authentication, encryption
- Medical Literature Vector Index (T-12, D-12, I-12): input validation, encryption
- Clinical Guideline RAG Corpus (T-11, D-11, I-11): input validation, encryption
- Outcomes Telemetry Store (T-16, D-16, I-16, AGP-02): encryption, input validation, rate limiting

---

### Low Risk Gaps

#### 107. I-11 — Clinical Guideline RAG Corpus (Composite: 3.7, Low)

**Current Status**: No Control Found

**What to Implement**: Implement PHI detection and prevention controls on the RAG corpus ingestion pipeline. Screen all documents before indexing to detect and redact any incidentally included patient data. Add an automated PHI scanner (NER-based) as a pre-ingestion gate.

**Where to Implement**: `src/rag/phi-screener.ts` — NER-based PHI detection on documents before vector indexing.

**Reference Patterns**: Presidio (Microsoft PHI detection), AWS Comprehend Medical (PHI entity recognition), regex-based PHI pattern matching as a secondary layer.

**Effort Estimate**: Medium — PHI detection requires integrating an NER service into the corpus ingestion pipeline.

---

#### 108. I-12 — Medical Literature Vector Index (Composite: 3.7, Low)

**Current Status**: No Control Found

**What to Implement**: Implement access controls and namespace isolation on the Medical Literature Vector Index. Research literature should be stored in a separate namespace from patient-adjacent data. Add read authorization checks on vector search queries to prevent cross-namespace data leakage.

**Where to Implement**: `src/vector-index/namespace-guard.ts` — namespace isolation enforcement; read authorization on vector search.

**Reference Patterns**: Pinecone/Weaviate namespace isolation, vector store read ACLs, query-level authorization middleware.

**Effort Estimate**: Low — namespace isolation is a configuration-level change in most vector store implementations.

---

## 5. Residual Risk Summary

Since all 108 findings have No Control Found status (reduction factor 0.00), residual scores equal inherent scores. This section documents the baseline state before any controls are implemented.

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | 570.6 |
| Total Residual Risk Score | 570.6 |
| Delta | 0.0 |
| Overall Reduction | 0.0% |

### Per-Severity-Band Shift

No severity shifts occur because all findings have No Control Found status (reduction factor 0.00).

| Shift | Count | Examples |
|-------|-------|---------|
| Critical -> High | 0 | — |
| Critical -> Medium | 0 | — |
| Critical -> Low | 0 | — |
| High -> Medium | 0 | — |
| High -> Low | 0 | — |
| Medium -> Low | 0 | — |
| No Shift | 108 | S-1, S-2, D-1, E-1, S-5, T-3, AG-8, D-3, E-2, AGP-01 (and 98 more) |
| **Total** | **108** | |

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | 0 | 0 | 0 |
| High | 6 | 6 | 0 |
| Medium | 100 | 100 | 0 |
| Low | 2 | 2 | 0 |
| **Total** | **108** | **108** | |

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent * 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent * 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent * 1.00 | No matching control detected. Residual equals inherent. |

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
Residual Score = Inherent Score * (1 - Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0] and mapped to severity bands using the same thresholds as risk scoring:

| Severity | Residual Score Range |
|----------|---------------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 -- 8.9 |
| **Medium** | 4.0 -- 6.9 |
| **Low** | < 4.0 |

### 6.4 Data Sources

Analysis draws on the following inputs:

- **Scored threats**: Parsed from `examples/maestro-reference/risk-scores.md` (108 findings, schema v1.4, all 7 MAESTRO layers populated).
- **Target codebase**: Scanned at `.` (tachi repository root). No architecture document provided; heuristic directory discovery applied. Priority security directories scanned: no `auth/`, `middleware/`, `security/`, `validators/`, `guards/`, `interceptors/` directories found in production code paths. Stack scaffolds in `stacks/` rejected per Phase B (template code, no running application context).
- **STRIDE-to-control mapping**: Canonical mapping from threat categories to control categories drives which controls are searched for each threat.
- **File read budget**: 7 production files read (within 200-file budget). Stack scaffold files (18 files) were read but rejected during Phase B semantic analysis.

### 6.5 Limitations

- Static analysis only — runtime control behavior is not evaluated
- 200-file read budget — large codebases may have directories skipped with warnings
- Files > 5,000 tokens are truncated to security-relevant sections
- Binary reduction factors (P0) approximate control impact; effectiveness-aware factors available in P1
- AI-specific control patterns (agentic, LLM) limited to general categories in P0; specialized patterns in P1
- **Reference architecture mismatch**: This report analyzes a reference Healthcare CDSS threat model against the tachi toolkit codebase. The 0% coverage result is a feature of this demonstration run, not a bug. Real adopters scanning their own clinical codebase will see meaningful control coverage.
