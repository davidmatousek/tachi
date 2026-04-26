---
schema_version: "1.0"
date: "2026-04-25"
source_file: "examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/risk-scores.md"
target_path: "examples/agentic-app (architecture-only — no source codebase)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls — Agentic AI Application (F-3 Wave 3)

## 1. Executive Summary

**84** threats analyzed | **0** Control Found | **31** Partial Control | **53** No Control Found

**Coverage**: 0% Found | 37% Partial | 63% Missing

**Risk Reduction**: 508.8 inherent → 479.9 residual (**5.7%** reduction)

**Highest-Risk Unmitigated Finding**: S-1 — User — Composite 8.2 (High) — No authentication or access control detected at the User component.

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-25 |
| Source file | `examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/risk-scores.md` |
| Target codebase | `examples/agentic-app (architecture-only — no source codebase)` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0% |
| Partial Control | 31 | 37% |
| No Control Found | 53 | 63% |
| **Total** | **84** | **100%** |

> **Analysis Warning**: No source codebase was provided. All control detection is based solely on the architecture document (`architecture.md`). Control evidence consists of architectural signals (component descriptions, data-flow annotations) rather than implementation code. All detections are classified as Medium confidence at best and result in `partial` status. Production control analysis requires scanning actual implementation files.

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, sorted by residual score descending.

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | — | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials | 8.2 | High | No Control Found | 8.2 | High |
| AG-1 | — | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions | 7.8 | High | No Control Found | 7.8 | High |
| E-2 | — | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection | 7.8 | High | No Control Found | 7.8 | High |
| E-1 | — | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller | 7.7 | High | No Control Found | 7.7 | High |
| I-2 | — | LLM Agent Orchestrator | The Orchestrator's context window contains sensitive data exposed via inference side-channels | 7.2 | High | No Control Found | 7.2 | High |
| T-2 | — | LLM Agent Orchestrator | The Orchestrator's context window (system prompt) can be tampered with to alter behavior | 7.1 | High | No Control Found | 7.1 | High |
| E-5 | — | MCP Tool Server | The MCP Tool Server executes tools with credentials of the requesting agent without scope restriction | 7.0 | High | No Control Found | 7.0 | High |
| T-5 | — | MCP Tool Server | Tool call request parameters supplied by agents can be tampered with to achieve injection | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| R-3 | — | LLM Agent Orchestrator | The Orchestrator denies having issued a specific delegation message or tool call request | 7.8 | High | Partial Control | 5.9 | Medium |
| LLM-6 | — | LLM Agent Orchestrator | Improper output handling — server-side execution via Tool Call Request | 7.7 | High | Partial Control | 5.8 | Medium |
| OI-2 | — | LLM Agent Orchestrator | Improper output handling — server-side execution via Tool Call Request (OI category) | 7.7 | High | Partial Control | 5.8 | Medium |
| LLM-5 | — | LLM Agent Orchestrator | Improper output handling — client-side XSS via LLM-generated response content | 7.5 | High | Partial Control | 5.6 | Medium |
| OI-1 | — | LLM Agent Orchestrator | Improper output handling — client-side XSS via LLM-generated response content (OI category) | 7.5 | High | Partial Control | 5.6 | Medium |
| LLM-13 | — | Clinical Advisory Sub-Agent | Prompt injection via clinical query context injected into the Sub-Agent | 7.4 | High | Partial Control | 5.6 | Medium |
| LLM-8 | — | Specialist Agent | Prompt injection via delegation messages from the Inter-Agent Communication Channel | 7.3 | High | Partial Control | 5.5 | Medium |
| LLM-1 | — | LLM Agent Orchestrator | Direct prompt injection via the User→Guardrails boundary reaching the Orchestrator | 7.2 | High | Partial Control | 5.4 | Medium |
| LLM-4 | — | LLM Agent Orchestrator | Training data poisoning via the Long-Running Learning Loop model update cycle | 7.1 | High | Partial Control | 5.3 | Medium |
| E-7 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent operates with elevated access to sensitive clinical data | 6.9 | Medium | No Control Found | 6.9 | Medium |
| AG-5 | — | MCP Tool Server | The MCP Tool Server is vulnerable to tool call parameter injection | 6.9 | Medium | Partial Control | 5.2 | Medium |
| I-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent processes clinical data without encryption or minimization | 6.8 | Medium | No Control Found | 6.8 | Medium |
| LLM-2 | — | LLM Agent Orchestrator | Indirect prompt injection via the Knowledge Base retrieval path | 6.8 | Medium | Partial Control | 5.1 | Medium |
| D-1 | — | Guardrails Service | The Guardrails Service is vulnerable to resource exhaustion / denial-of-service | 6.7 | Medium | Partial Control | 5.0 | Medium |
| LLM-7 | — | LLM Agent Orchestrator | Improper output handling — SSRF via LLM-synthesized URL in tool call | 6.6 | Medium | Partial Control | 5.0 | Medium |
| LLM-14 | — | Clinical Advisory Sub-Agent | Training data poisoning of the Clinical Advisory Sub-Agent via poisoned KB documents | 6.6 | Medium | Partial Control | 5.0 | Medium |
| MI-2 | — | Clinical Advisory Sub-Agent | Overreliance / Missing HITL on Decision-Critical clinical outputs | 6.6 | Medium | No Control Found | 6.6 | Medium |
| T-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent's context window can be tampered with via poisoned clinical context | 6.6 | Medium | No Control Found | 6.6 | Medium |
| LLM-10 | — | Specialist Agent | Improper output handling — server-side injection via Specialist Agent tool call | 6.5 | Medium | Partial Control | 4.9 | Medium |
| MI-1 | — | Clinical Advisory Sub-Agent | Ungrounded Factual Emission — clinical claims without source attribution | 6.5 | Medium | No Control Found | 6.5 | Medium |
| MI-3 | — | Clinical Advisory Sub-Agent | Retrieval-Grounding Gap — clinical summaries not entailed by retrieved documents | 6.5 | Medium | No Control Found | 6.5 | Medium |
| OI-3 | — | LLM Agent Orchestrator | Improper output handling — SSRF via LLM-synthesized URL (OI category) | 6.5 | Medium | Partial Control | 4.9 | Medium |
| E-3 | — | Specialist Agent | The Specialist Agent receives delegated permissions beyond necessary scope | 6.4 | Medium | No Control Found | 6.4 | Medium |
| E-4 | — | Inter-Agent Communication Channel | The Channel does not enforce sender authentication — privilege escalation via impersonation | 6.4 | Medium | No Control Found | 6.4 | Medium |
| S-5 | — | Inter-Agent Communication Channel | The Channel is a shared message routing substrate vulnerable to spoofing | 6.4 | Medium | No Control Found | 6.4 | Medium |
| S-7 | — | Long-Running Learning Loop | The Learning Loop accepts a Training Signal Stream without sender verification | 6.4 | Medium | No Control Found | 6.4 | Medium |
| AG-3 | — | Specialist Agent | The Specialist Agent, once delegated a task, operates beyond its intended scope | 6.2 | Medium | Partial Control | 4.7 | Medium |
| AG-6 | — | MCP Tool Server | The MCP Tool Server acts as a privileged execution environment without action constraints | 6.2 | Medium | Partial Control | 4.7 | Medium |
| D-2 | — | LLM Agent Orchestrator | The Orchestrator's inference pipeline is a bounded resource vulnerable to token flooding | 6.2 | Medium | No Control Found | 6.2 | Medium |
| D-5 | — | MCP Tool Server | The Tool Server's capacity for concurrent External API calls can be exhausted | 6.2 | Medium | Partial Control | 4.7 | Medium |
| OI-4 | — | Clinical Advisory Sub-Agent | Improper output handling — server-side execution via Clinical Advisory output | 6.2 | Medium | Partial Control | 4.7 | Medium |
| R-1 | — | User | A user denies having submitted a particular prompt (non-repudiation gap) | 6.2 | Medium | Partial Control | 4.7 | Medium |
| S-6 | — | MCP Tool Server | An attacker in the Application Zone spoofs a valid MCP tool caller identity | 6.2 | Medium | No Control Found | 6.2 | Medium |
| AG-2 | — | LLM Agent Orchestrator | The Orchestrator and Specialist Agent can jointly exhibit emergent cascading behavior | 6.1 | Medium | No Control Found | 6.1 | Medium |
| AG-4 | — | Inter-Agent Communication Channel | The Channel is a shared substrate whose compromise enables cascading failures | 6.0 | Medium | No Control Found | 6.0 | Medium |
| E-6 | — | Long-Running Learning Loop | The Learning Loop applies model updates without cryptographic verification | 6.0 | Medium | No Control Found | 6.0 | Medium |
| S-3 | — | LLM Agent Orchestrator | The Orchestrator's identity is not cryptographically bound — impersonation risk | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-3 | — | Specialist Agent | The Specialist Agent's operational context can be tampered with via delegation messages | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-4 | — | Inter-Agent Communication Channel | Messages transiting the Channel lack integrity protection — in-transit tampering | 5.9 | Medium | No Control Found | 5.9 | Medium |
| S-8 | — | External API | The External API provider's identity is not verified by the MCP Tool Server | 5.8 | Medium | No Control Found | 5.8 | Medium |
| S-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent receives Clinical Query / Context without sender authentication | 5.8 | Medium | No Control Found | 5.8 | Medium |
| T-7 | — | Audit Logger | The Audit Logger entries can be tampered with by any component with write access | 5.8 | Medium | No Control Found | 5.8 | Medium |
| AG-7 | — | Long-Running Learning Loop | The Learning Loop's model update mechanism is vulnerable to temporal attacks | 5.6 | Medium | No Control Found | 5.6 | Medium |
| D-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent is invoked by the Orchestrator and its inference capacity is bounded | 5.6 | Medium | Partial Control | 4.2 | Medium |
| I-1 | — | Guardrails Service | The Guardrails Service leaks rejected prompt content in error responses | 5.6 | Medium | No Control Found | 5.6 | Medium |
| LLM-9 | — | Specialist Agent | Training data poisoning of the Specialist Agent's learned behavior via audit log | 5.6 | Medium | Partial Control | 4.2 | Medium |
| D-6 | — | Knowledge Base | The Knowledge Base can be rendered unavailable through targeted query flooding | 5.7 | Medium | No Control Found | 5.7 | Medium |
| LLM-11 | — | Long-Running Learning Loop | Data poisoning of the Learning Loop's training signal via audit log injection | 5.7 | Medium | No Control Found | 5.7 | Medium |
| T-8 | — | Long-Running Learning Loop | Training signal stream from Audit Logger to Learning Loop can be poisoned (temporal attack) | 5.7 | Medium | No Control Found | 5.7 | Medium |
| D-3 | — | Specialist Agent | The Specialist Agent is invoked by the Orchestrator and its inference capacity is bounded | 5.5 | Medium | Partial Control | 4.1 | Medium |
| D-4 | — | Inter-Agent Communication Channel | The Channel's message queue can be flooded by a high-volume sender | 5.5 | Medium | No Control Found | 5.5 | Medium |
| D-7 | — | Audit Logger | The Audit Logger can be overwhelmed by a log-flooding attack | 5.5 | Medium | No Control Found | 5.5 | Medium |
| AG-8 | — | Inter-Agent Communication Channel | Insecure Inter-Agent Communication — lack of authentication and integrity controls | 5.5 | Medium | No Control Found | 5.5 | Medium |
| I-6 | — | Knowledge Base | The Knowledge Base exposes its full document corpus to any component with retrieval access | 5.4 | Medium | No Control Found | 5.4 | Medium |
| I-7 | — | Audit Logger | The Audit Logger aggregates sensitive data from all pipeline components without access control | 5.4 | Medium | No Control Found | 5.4 | Medium |
| D-8 | — | Long-Running Learning Loop | The Learning Loop is a resource-intensive batch process vulnerable to resource competition | 5.3 | Medium | No Control Found | 5.3 | Medium |
| I-5 | — | MCP Tool Server | Tool results from External API calls may contain sensitive data passed through without masking | 5.3 | Medium | Partial Control | 4.0 | Medium |
| LLM-3 | — | LLM Agent Orchestrator | Model theft via systematic API probing of the Orchestrator | 5.3 | Medium | Partial Control | 4.0 | Medium |
| LLM-12 | — | Long-Running Learning Loop | Model theft via Learning Loop output monitoring | 5.3 | Medium | No Control Found | 5.3 | Medium |
| T-6 | — | Knowledge Base | The Knowledge Base corpus can be tampered with by components with write access | 5.3 | Medium | No Control Found | 5.3 | Medium |
| S-2 | — | Guardrails Service | An attacker spoofs the Guardrails Service by sending crafted validation responses | 5.2 | Medium | No Control Found | 5.2 | Medium |
| I-4 | — | Inter-Agent Communication Channel | Messages on the Channel may expose sensitive payloads to eavesdropping components | 5.1 | Medium | No Control Found | 5.1 | Medium |
| AGP-01 | — | LLM Agent Orchestrator | Multi-agent emergent behavior — cascading failure through delegation chains | 4.6 | Medium | No Control Found | 4.6 | Medium |
| I-8 | — | Long-Running Learning Loop | The Learning Loop consumes the full Audit Logger training stream without data minimization | 4.9 | Medium | No Control Found | 4.9 | Medium |
| R-7 | — | Long-Running Learning Loop | The Learning Loop denies having applied a specific model update | 4.9 | Medium | No Control Found | 4.9 | Medium |
| S-4 | — | Specialist Agent | The Specialist Agent impersonates the Orchestrator when responding via the Channel | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-3 | — | Specialist Agent | The Specialist Agent receives sensitive data via delegation messages without encryption | 4.8 | Medium | No Control Found | 4.8 | Medium |
| R-5 | — | Inter-Agent Communication Channel | The Channel denies having delivered or modified a message | 4.3 | Medium | No Control Found | 4.3 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| R-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent denies having generated a specific clinical recommendation | 5.2 | Medium | Partial Control | 3.9 | Low |
| R-8 | — | External API | The External API provider denies having returned a specific response | 5.0 | Medium | Partial Control | 3.8 | Low |
| R-2 | — | Guardrails Service | The Guardrails Service denies having logged a filtering decision | 4.4 | Medium | Partial Control | 3.3 | Low |
| R-4 | — | Specialist Agent | The Specialist Agent denies having executed a delegated task | 4.4 | Medium | Partial Control | 3.3 | Low |
| R-6 | — | MCP Tool Server | The MCP Tool Server denies having executed a specific tool call | 4.4 | Medium | Partial Control | 3.3 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 8 | 10% |
| Medium | 71 | 84% |
| Low | 5 | 6% |
| **Total** | **84** | **100%** |

---

## 3. Control Details

Control evidence is derived from the architecture document (`architecture.md`) since no source codebase was provided. All controls are inferred from component descriptions, data-flow annotations, and structural signals in the architecture. Confidence is Medium for logging/audit (explicit architectural data flows described) and Low for input validation/rate-limiting (implied by the Guardrails component role).

### Logging/Audit

#### ARCH-LOG-01 — Centralized decision logging across all pipeline components via Audit Logger

**Category**: Logging/Audit | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:47–58`

```
Orchestrator -->|"Decision Log Entry"| AuditLog
Specialist -->|"Decision Log Entry"| AuditLog
ToolServer -->|"Tool Execution Log"| AuditLog
Guardrails -->|"Filtering Event Log"| AuditLog
ClinAdvisor -->|"Clinical Decision Log Entry"| AuditLog
```

**Effectiveness Assessment**: *Detailed effectiveness assessment available in P1 (User Story 6).*

**Threats Mitigated by This Control** (Repudiation findings — Partial, reduction factor 0.25):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| R-3 | LLM Agent Orchestrator | Orchestrator denies issuing delegation/tool call | 7.8 | 0.25 | 5.9 |
| R-1 | User | User denies submitting a prompt | 6.2 | 0.25 | 4.7 |
| R-8 | External API | External API denies returning a specific response | 5.0 | 0.25 | 3.8 |
| R-9 | Clinical Advisory Sub-Agent | ClinAdvisor denies generating a clinical recommendation | 5.2 | 0.25 | 3.9 |
| R-7 | Long-Running Learning Loop | Learning Loop denies applying a model update | 4.9 | 0.25 | 3.7 |
| R-2 | Guardrails Service | Guardrails denies having logged a filtering decision | 4.4 | 0.25 | 3.3 |
| R-4 | Specialist Agent | Specialist denies executing a delegated task | 4.4 | 0.25 | 3.3 |
| R-6 | MCP Tool Server | MCP Tool Server denies executing a tool call | 4.4 | 0.25 | 3.3 |

*Note: R-5 (Inter-Agent Communication Channel) is classified as missing — the Channel substrate has no described logging capability in the architecture.*

---

#### ARCH-LOG-02 — Guardrails Service filtering event log and audit trail

**Category**: Logging/Audit | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:50`

```
Guardrails -->|"Filtering Event Log"| AuditLog
```

**Threats Mitigated by This Control** (LLM/Agentic findings where logging provides partial audit):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection via User→Guardrails | 7.2 | 0.25 | 5.4 |
| LLM-4 | LLM Agent Orchestrator | Training data poisoning via Learning Loop | 7.1 | 0.25 | 5.3 |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via KB retrieval | 6.8 | 0.25 | 5.1 |
| LLM-7 | LLM Agent Orchestrator | SSRF via LLM-synthesized URL | 6.6 | 0.25 | 5.0 |
| LLM-10 | Specialist Agent | Server-side injection via Specialist tool call | 6.5 | 0.25 | 4.9 |
| OI-3 | LLM Agent Orchestrator | SSRF via LLM-synthesized URL (OI category) | 6.5 | 0.25 | 4.9 |
| LLM-3 | LLM Agent Orchestrator | Model theft via systematic API probing | 5.3 | 0.25 | 4.0 |

---

#### ARCH-LOG-03 — Clinical Advisory Sub-Agent clinical decision logging

**Category**: Logging/Audit | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:58`

```
ClinAdvisor -->|"Clinical Decision Log Entry"| AuditLog
```

**Threats Mitigated by This Control** (Clinical Advisory LLM/Output findings):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| LLM-13 | Clinical Advisory Sub-Agent | Prompt injection via clinical query context | 7.4 | 0.25 | 5.6 |
| LLM-14 | Clinical Advisory Sub-Agent | Training data poisoning of Clinical Advisory | 6.6 | 0.25 | 5.0 |
| OI-4 | Clinical Advisory Sub-Agent | Server-side execution via Clinical output | 6.2 | 0.25 | 4.7 |
| D-9 | Clinical Advisory Sub-Agent | Clinical Advisory inference capacity exhaustion | 5.6 | 0.25 | 4.2 |

---

### Input Validation

#### ARCH-VAL-01 — Guardrails Service prompt filtering and validation

**Category**: Input Validation | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:31–33`

```
User -->|"Prompt / Query (HTTPS)"| Guardrails
Guardrails -->|"Validated Prompt"| Orchestrator
Guardrails -->|"Rejected Prompt + Reason"| User
```

**Effectiveness Assessment**: *Detailed effectiveness assessment available in P1 (User Story 6).*

**Threats Mitigated by This Control** (LLM/Agentic input validation relevance):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| LLM-6 | LLM Agent Orchestrator | Server-side execution via Tool Call Request | 7.7 | 0.25 | 5.8 |
| OI-2 | LLM Agent Orchestrator | Server-side execution via Tool Call Request (OI) | 7.7 | 0.25 | 5.8 |
| LLM-5 | LLM Agent Orchestrator | Client-side XSS via LLM-generated response | 7.5 | 0.25 | 5.6 |
| OI-1 | LLM Agent Orchestrator | Client-side XSS via LLM response (OI) | 7.5 | 0.25 | 5.6 |
| LLM-8 | Specialist Agent | Prompt injection via delegation messages | 7.3 | 0.25 | 5.5 |
| AG-5 | MCP Tool Server | Tool call parameter injection | 6.9 | 0.25 | 5.2 |
| D-1 | Guardrails Service | Guardrails resource exhaustion (DoS) | 6.7 | 0.25 | 5.0 |
| LLM-14 | Clinical Advisory Sub-Agent | Training data poisoning of Clinical Advisory | 6.6 | 0.25 | 5.0 |
| AG-3 | Specialist Agent | Specialist Agent operating beyond intended scope | 6.2 | 0.25 | 4.7 |
| AG-6 | MCP Tool Server | MCP Tool Server as unconstrained execution env | 6.2 | 0.25 | 4.7 |
| D-5 | MCP Tool Server | Tool Server connection pool exhaustion | 6.2 | 0.25 | 4.7 |
| D-3 | Specialist Agent | Specialist Agent inference capacity exhaustion | 5.5 | 0.25 | 4.1 |
| LLM-9 | Specialist Agent | Training data poisoning via Specialist Agent | 5.6 | 0.25 | 4.2 |
| I-5 | MCP Tool Server | Sensitive data in External API tool results | 5.3 | 0.25 | 4.0 |

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control," sorted by composite risk score descending. Architecture-level recommendations since no codebase is available.

### High Risk Gaps

#### 1. S-1 — User (Composite: 8.2, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement multi-factor authentication and session token binding at the User→Guardrails boundary. Deploy short-lived JWTs with rotation, session binding to device fingerprint, and server-side token revocation. Add brute-force protection with account lockout and CAPTCHA on repeated failures.

**Where to Implement**: `guardrails/middleware/auth.{ts|py}` — authentication enforcement at the Guardrails Service ingress before prompt forwarding to the Orchestrator. The User Zone to Application Zone boundary is the critical enforcement point.

**Reference Patterns**: `jsonwebtoken` / `jose` for JWT with short expiry and refresh rotation; `argon2` / `bcrypt` for credential hashing; `next-auth` or `passport.js` for OAuth/SSO integration; `express-rate-limit` for brute-force protection.

**Effort Estimate**: High — authentication flow at the Guardrails boundary requires MFA integration, session management infrastructure, and token lifecycle management across the full user authentication path.

---

#### 2. AG-1 — LLM Agent Orchestrator (Composite: 7.8, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement agentic control guardrails: (a) structured output schema validation that rejects Orchestrator actions not conforming to approved schemas, (b) a minimal-footprint enforcement layer capping tool invocations per session, and (c) a human-in-the-loop confirmation gate for high-impact actions (bulk KB queries, External API invocations exceeding defined thresholds).

**Where to Implement**: `orchestrator/middleware/action-guard.{ts|py}` for schema validation; `orchestrator/policy/action-budget.{ts|py}` for footprint limits; `orchestrator/hitl/confirmation-gate.{ts|py}` for HITL checkpoints.

**Reference Patterns**: Structured output validation with `zod` / `pydantic`; `casbin` / `oso` for policy-as-code action budget enforcement; NeMo Guardrails for agentic behavior constraints.

**Effort Estimate**: High — multi-layer agentic control requires architectural changes to the Orchestrator's action dispatch pipeline.

---

#### 3. E-2 — LLM Agent Orchestrator (Composite: 7.8, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement least-privilege access control for the Orchestrator: (a) scope KB access to query-relevant documents only (not full-corpus access), (b) restrict tool invocation to a pre-approved whitelist per request context, and (c) implement delegation authority limits so the Orchestrator can only delegate tasks within the scope of the original user request. Use ABAC policy evaluation before each privileged operation.

**Where to Implement**: `orchestrator/access-control/permission-guard.{ts|py}` for ABAC checks; `orchestrator/kb-client/scoped-retrieval.{ts|py}` for query-scoped KB access; `orchestrator/delegation/authority-limits.{ts|py}` for delegation scope enforcement.

**Reference Patterns**: `casbin` / `oso` for ABAC policy evaluation; `casl` for capability-based access control; structured permission manifests per request context.

**Effort Estimate**: High — implementing least-privilege across all Orchestrator capabilities requires rearchitecting the permission model for KB, tools, and delegation.

---

#### 4. E-1 — Guardrails Service (Composite: 7.7, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Harden the Guardrails Service against prompt injection bypass with layered defense: (a) multi-model ensemble filtering (secondary LLM judge evaluating primary filter output), (b) structured output enforcement (Guardrails output is a typed schema, not a raw passthrough), (c) semantic similarity checks against known injection pattern libraries, and (d) rate limiting on re-submission after rejection.

**Where to Implement**: `guardrails/filters/ensemble-judge.{ts|py}` for multi-model validation; `guardrails/schema/output-schema.{ts|py}` for structured output enforcement; `guardrails/rate-limiter/rejection-throttle.{ts|py}` for post-rejection rate limiting.

**Reference Patterns**: NeMo Guardrails; LangChain GuardrailsHub; `rebuff` prompt injection detection; structured output with `instructor` / `outlines`.

**Effort Estimate**: High — multi-layer ensemble filtering requires additional LLM inference resources and structured validation pipelines.

---

#### 5. LLM-6 — LLM Agent Orchestrator (Composite: 7.7, High) — Partial Control

**Current Status**: Partial Control (Guardrails filters user input but not LLM-generated tool parameters)

**What to Implement**: Extend the existing Guardrails input validation to cover LLM-synthesized JSON-RPC parameters flowing to the MCP Tool Server. Implement a tool parameter sanitization layer at the Tool Server ingress that validates each parameter against the tool's declared JSON Schema and strips injection payloads (SQL fragments, shell metacharacters, template expressions) before dispatch.

**Where to Implement**: `tool-server/middleware/param-sanitizer.{ts|py}` — server-side validation at MCP Tool Server ingress on all JSON-RPC `params`; extend `orchestrator/output-validator.{ts|py}` to cover Orchestrator-generated tool invocations.

**Reference Patterns**: JSON Schema validation with `ajv`; `zod` for strict TypeScript parameter schemas; parameterized query enforcement for database-backed tools.

**Effort Estimate**: Medium — extending existing validation infrastructure to the tool parameter path requires schema definitions for each registered tool.

---

#### 6. OI-2 — LLM Agent Orchestrator (Composite: 7.7, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Implement a dedicated output sanitization layer treating all LLM-generated content destined for server-side execution sinks as untrusted input. Validate parameter schemas, strip injection metacharacters, and require parameterized invocations for all database and shell tool calls. This is the OI-category complement to LLM-6 and should be implemented together.

**Where to Implement**: `orchestrator/output-sanitizer/tool-params.{ts|py}` — intercept all `Tool Call Request (JSON-RPC)` messages before emission to the Tool Server.

**Reference Patterns**: `instructor` for structured LLM outputs; JSON Schema enforcement; parameterized tool invocations with strict type validation.

**Effort Estimate**: Medium — output sanitization interceptor in the Orchestrator's tool dispatch path; implement together with LLM-6 remediation.

---

#### 7. LLM-5 — LLM Agent Orchestrator (Composite: 7.5, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Implement client-side XSS prevention: (a) apply HTML output encoding to all LLM-generated content before client rendering, (b) deploy a Content Security Policy (CSP) header restricting script execution to approved sources, and (c) use a DOM sanitization library to strip executable markup from LLM responses. The architecture passes LLM output directly to the User without client-side sanitization.

**Where to Implement**: `api-gateway/middleware/response-sanitizer.{ts|py}` for server-side output encoding; HTTP response CSP header configuration; `frontend/utils/sanitize.ts` for DOM-level sanitization.

**Reference Patterns**: `DOMPurify` for DOM sanitization; `helmet` with `contentSecurityPolicy` for CSP enforcement; `sanitize-html` for HTML stripping.

**Effort Estimate**: Medium — CSP and output encoding require coordination between backend response headers and frontend rendering pipeline.

---

#### 8. OI-1 — LLM Agent Orchestrator (Composite: 7.5, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: OI-1 covers the same XSS attack vector as LLM-5 from the Output Integrity taxonomy perspective. Implementing the LLM-5 remediation (output encoding + CSP + DOM sanitization) fully addresses OI-1 with no additional changes required.

**Where to Implement**: Same as LLM-5 remediation — `api-gateway/middleware/response-sanitizer.{ts|py}` and CSP header configuration.

**Reference Patterns**: `DOMPurify`; `helmet` CSP; `sanitize-html`.

**Effort Estimate**: Low — OI-1 is resolved by the LLM-5 remediation; no standalone implementation required.

---

#### 9. LLM-13 — Clinical Advisory Sub-Agent (Composite: 7.4, High) — Partial Control

**Current Status**: Partial Control (logging present; input validation for clinical context missing)

**What to Implement**: Extend the logging-based partial control to include clinical query input validation: (a) implement a clinical context schema validator enforcing structured clinical query formats and rejecting free-form injection attempts, (b) add a prompt integrity check detecting instruction-override patterns in clinical context messages, and (c) require HMAC-signed clinical context objects from the Orchestrator to the Sub-Agent to prevent in-transit tampering.

**Where to Implement**: `clinical-advisor/middleware/query-validator.{ts|py}` for input schema enforcement; `clinical-advisor/integrity/context-signature.{ts|py}` for signed context verification.

**Reference Patterns**: `pydantic` / `zod` for clinical query schema validation; HMAC-SHA256 for inter-agent message integrity; NeMo Guardrails for clinical domain injection detection.

**Effort Estimate**: High — clinical context signing and structured query enforcement require protocol changes in the Orchestrator-to-ClinAdvisor communication path.

---

#### 10. LLM-8 — Specialist Agent (Composite: 7.3, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend logging to include delegation message validation: implement HMAC signature verification on all messages received via the Channel. The Specialist Agent must verify that delegation messages originated from the Orchestrator, not from an injected source. Additionally, implement a scope constraint validator rejecting delegation messages requesting actions beyond the Agent's configured authority.

**Where to Implement**: `specialist-agent/middleware/delegation-validator.{ts|py}` for signature verification; `specialist-agent/policy/scope-guard.{ts|py}` for authority scope enforcement.

**Reference Patterns**: HMAC signing with `crypto` built-in; `casbin` for delegation scope policy; structured delegation schemas with `zod`.

**Effort Estimate**: High — cryptographic signing of delegation messages and scope policy enforcement require cross-component protocol changes.

---

#### 11. I-2 — LLM Agent Orchestrator (Composite: 7.2, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement context window data minimization and masking: (a) strip PII, credentials, and patient data from context window contents before and after each inference call, (b) encrypt persisted context window storage (e.g., vector store sessions), and (c) implement field-level masking for sensitive values in Audit Logger entries produced by the Orchestrator.

**Where to Implement**: `orchestrator/context/minimizer.{ts|py}` for data minimization pre-inference; `orchestrator/logging/masked-logger.{ts|py}` for log data masking.

**Reference Patterns**: PII detection with `presidio`; AES-256 encryption for persisted context; context window scrubbing with rule-based pattern matching.

**Effort Estimate**: High — context window data minimization requires classifying all sensitive data types in flight and implementing runtime scrubbing.

---

#### 12. LLM-1 — LLM Agent Orchestrator (Composite: 7.2, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend the Guardrails Service input filtering to include semantic injection detection (adversarial instruction patterns, role-override attempts, delimiter escaping). Deploy a secondary LLM-based intent classifier as a second filter stage alongside the existing pattern matching. Also implement prompt structure canonicalization normalizing prompts before injection pattern matching.

**Where to Implement**: `guardrails/filters/semantic-detector.{ts|py}` for intent classification; `guardrails/canonicalize/prompt-normalizer.{ts|py}` for structure normalization.

**Reference Patterns**: NeMo Guardrails; LangChain GuardrailsHub; `rebuff` prompt injection detection.

**Effort Estimate**: Medium — extends existing Guardrails infrastructure with additional filter stages.

---

#### 13. T-2 — LLM Agent Orchestrator (Composite: 7.1, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement system prompt integrity protection: (a) store the system prompt in an immutable, signed configuration store, (b) verify the system prompt hash before each inference call, (c) implement access control restricting system prompt modification to authorized operators, and (d) log all system prompt access and modification events.

**Where to Implement**: `orchestrator/config/system-prompt-store.{ts|py}` — signed immutable prompt storage; `orchestrator/integrity/prompt-verifier.{ts|py}` — hash verification pre-inference.

**Reference Patterns**: HMAC signing with secret keys; HashiCorp Vault for secrets management; `crypto.createHash('sha256')` for prompt integrity verification.

**Effort Estimate**: Medium — signed prompt storage with pre-inference hash verification is a well-understood pattern.

---

#### 14. E-5 — MCP Tool Server (Composite: 7.0, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement least-privilege credential management: issue per-invocation scoped credentials to tools rather than long-lived service account credentials, implement tool execution sandboxing restricting each tool to its declared scope, and require explicit capability declarations in tool schemas enforced at execution time.

**Where to Implement**: `tool-server/auth/scoped-credentials.{ts|py}` — per-invocation credential issuance; `tool-server/sandbox/execution-policy.{ts|py}` — tool sandbox enforcement.

**Reference Patterns**: AWS IAM roles with temporary STS credentials; OPA (Open Policy Agent) for execution policy; tool capability schemas with enforcement at dispatch time.

**Effort Estimate**: High — per-invocation credential scoping requires integration with identity infrastructure and changes to tool registration.

---

#### 15. T-5 — MCP Tool Server (Composite: 7.0, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement tool call parameter validation at the MCP Tool Server: each registered tool must declare a strict JSON Schema for its parameters; the Tool Server validates all incoming JSON-RPC parameters against the schema before dispatch. Reject any tool call with non-conforming parameters.

**Where to Implement**: `tool-server/validation/param-schema-validator.{ts|py}` — JSON Schema enforcement on all tool call parameters before dispatch.

**Reference Patterns**: JSON Schema with `ajv`; `zod` for TypeScript; parameterized query pattern for database-backed tools.

**Effort Estimate**: Medium — JSON Schema validation is well-established; requires schema definition for each registered tool.

---

### Medium Risk Gaps

#### 16. E-7 — Clinical Advisory Sub-Agent (Composite: 6.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement scope-limited access control for the Sub-Agent's KB access: restrict retrieval to the clinical document partition only, not the full Knowledge Base corpus. Implement ABAC policy enforcement at the KB retrieval interface with clinical namespace filters.

**Where to Implement**: `clinical-advisor/kb-client/scoped-retrieval.{ts|py}` — query-scoped KB access with clinical partition filters.

**Reference Patterns**: `casbin` ABAC; vector store namespace isolation; query-time metadata filters restricting document scope.

**Effort Estimate**: Medium — KB partition filtering is typically configurable in vector store clients.

---

#### 17. I-9 — Clinical Advisory Sub-Agent (Composite: 6.8, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement clinical data encryption at rest in the KB partition, field-level PII masking in clinical query contexts before logging, and enforce HIPAA-aligned data retention limits on clinical context stored in the Audit Logger.

**Where to Implement**: `knowledge-base/encryption/field-encryptor.{ts|py}`; `clinical-advisor/logging/clinical-masker.{ts|py}`.

**Reference Patterns**: AES-256 field-level encryption; `presidio` for PII masking; HIPAA-compliant data retention configuration.

**Effort Estimate**: High — field-level encryption across clinical data requires schema changes in the Knowledge Base.

---

#### 18. LLM-2 — LLM Agent Orchestrator (Composite: 6.8, Medium) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Harden Knowledge Base retrieval against indirect prompt injection: (a) implement document content sanitization before retrieval results are injected into the Orchestrator's context window, (b) apply secondary content validation detecting embedded injection patterns in retrieved documents, and (c) enforce retrieval result size limits to prevent context window stuffing.

**Where to Implement**: `orchestrator/kb-client/retrieval-sanitizer.{ts|py}` — post-retrieval content sanitization before context injection.

**Reference Patterns**: Content filtering with `rebuff`; retrieval result size limits; document sanitization middleware.

**Effort Estimate**: Medium — post-retrieval sanitization hooks into the existing KB retrieval path.

---

#### 19. D-1 — Guardrails Service (Composite: 6.7, Medium) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Implement rate limiting at the Guardrails Service ingress to prevent resource exhaustion from high-volume prompt flooding. Configure per-user and per-IP token-per-minute limits, implement circuit breaker logic for graceful degradation under load, and add a queue depth limit to prevent memory exhaustion.

**Where to Implement**: `guardrails/rate-limiter/prompt-throttle.{ts|py}` — rate limiter at the User→Guardrails ingress.

**Reference Patterns**: `express-rate-limit` with sliding window; `rate-limiter-flexible` for distributed deployments; `opossum` circuit breaker.

**Effort Estimate**: Medium — rate limiting middleware is standard infrastructure; circuit breaker configuration is additional.

---

#### 20. MI-2 — Clinical Advisory Sub-Agent (Composite: 6.6, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement a mandatory HITL review gate for all clinical decision outputs before they reach the end user. Clinical recommendations must include a confidence score; outputs below a defined threshold or involving high-stakes decisions (medication dosing, diagnosis) must be routed to a clinical professional review queue before delivery.

**Where to Implement**: `clinical-advisor/hitl/review-gate.{ts|py}` — confidence scoring and routing; `clinical-advisor/workflow/approval-queue.{ts|py}` — human review integration.

**Reference Patterns**: Calibrated model confidence scoring; clinical CDSS workflow integration; mandatory approval gates per clinical decision category.

**Effort Estimate**: High — HITL integration requires clinical workflow infrastructure and process design with clinical domain expertise.

---

#### 21. T-9 — Clinical Advisory Sub-Agent (Composite: 6.6, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement context integrity verification: sign all Clinical Query / Context messages from the Orchestrator using HMAC-SHA256, and verify signatures at the Sub-Agent before processing. This prevents in-transit tampering with clinical context injected into the Sub-Agent.

**Where to Implement**: `orchestrator/delegation/clinical-context-signer.{ts|py}`; `clinical-advisor/integrity/context-verifier.{ts|py}`.

**Reference Patterns**: HMAC-SHA256 message signing; inter-service message integrity with signed JWTs; mTLS for mutual authentication.

**Effort Estimate**: Medium — message signing and verification is a standard pattern; requires key distribution infrastructure.

---

#### 22. MI-1 — Clinical Advisory Sub-Agent (Composite: 6.5, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement source attribution enforcement for clinical factual outputs: all clinical factual claims must cite a retrieved Knowledge Base document. Implement a citation completeness checker that rejects clinical summaries lacking source attribution for factual claims, and add a structured output schema requiring a mandatory `sources` field.

**Where to Implement**: `clinical-advisor/output/citation-enforcer.{ts|py}` — post-generation citation completeness check; update clinical output schema to require `sources[]`.

**Reference Patterns**: RAG-based citation tracking; `instructor` for structured LLM outputs with mandatory fields; clinical output schemas with required source attribution.

**Effort Estimate**: Medium — citation enforcement requires clinical output schema changes and post-generation validation.

---

#### 23. MI-3 — Clinical Advisory Sub-Agent (Composite: 6.5, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement retrieval quality metrics and grounding gap detection: (a) track retrieval confidence scores per clinical query, (b) flag responses where retrieval confidence falls below a defined threshold as "low-confidence — requires verification," and (c) implement NLI-based grounding verification confirming the clinical summary is entailed by retrieved documents.

**Where to Implement**: `clinical-advisor/grounding/retrieval-quality.{ts|py}` — retrieval confidence scoring; `clinical-advisor/grounding/entailment-check.{ts|py}` — NLI grounding verification.

**Reference Patterns**: RAG evaluation with `RAGAS`; NLI-based grounding checks with DeBERTa NLI models; retrieval score thresholds.

**Effort Estimate**: High — NLI-based entailment checking requires additional model inference and calibration.

---

#### 24. E-3 — Specialist Agent (Composite: 6.4, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement delegation authority scoping: all delegation messages from the Orchestrator must explicitly enumerate permitted actions (tool calls, KB queries), and the Specialist Agent must enforce these scopes, refusing to execute actions outside the declared delegation authority.

**Where to Implement**: `specialist-agent/policy/delegation-scope.{ts|py}` — per-delegation authority enforcement.

**Reference Patterns**: `casbin` delegation policy; capability token pattern (signed token encoding permitted actions); OAuth2 scope enforcement applied to agent delegation.

**Effort Estimate**: High — delegation scope enforcement requires protocol changes to the inter-agent communication format and delegation message schema.

---

#### 25. E-4 — Inter-Agent Communication Channel (Composite: 6.4, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement sender authentication on the Inter-Agent Communication Channel: all messages must include a signed sender identity token (agent-issued JWT or HMAC-signed envelope) that the Channel verifies before routing. Unauthenticated messages are rejected at the Channel ingress.

**Where to Implement**: `inter-agent-channel/middleware/sender-auth.{ts|py}` — message sender authentication at Channel ingress.

**Reference Patterns**: JWT-based agent identity tokens; HMAC message signatures; mTLS for agent-to-Channel connections; SPIFFE/SPIRE for workload identity.

**Effort Estimate**: High — PKI-based agent identity across all agents requires key management infrastructure.

---

#### 26. S-5 — Inter-Agent Communication Channel (Composite: 6.4, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement anti-spoofing controls on the Channel: cryptographic sender authentication (as per E-4) combined with message sequence numbers and replay prevention using a sliding window nonce check on message timestamps.

**Where to Implement**: `inter-agent-channel/middleware/anti-replay.{ts|py}` — nonce tracking and replay prevention alongside sender authentication.

**Reference Patterns**: Nonce-based replay prevention; signed message envelopes; HMAC-authenticated message channels.

**Effort Estimate**: High — replay prevention requires stateful nonce tracking in the Channel substrate; implement together with E-4.

---

#### 27. S-7 — Long-Running Learning Loop (Composite: 6.4, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement training signal authentication: the Learning Loop must verify the integrity and provenance of the Training Signal Stream from the Audit Logger before incorporating it into training. Implement a signed training batch manifest that the Learning Loop verifies before each training run.

**Where to Implement**: `learning-loop/intake/signal-verifier.{ts|py}` — signed manifest verification before training data consumption.

**Reference Patterns**: HMAC-signed training batches; dataset integrity verification with checksums; signed dataset cards.

**Effort Estimate**: High — signed training pipeline requires infrastructure changes in the Audit Logger → Learning Loop data path.

---

#### 28. D-2 — LLM Agent Orchestrator (Composite: 6.2, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement token budget enforcement and context size limits: (a) cap maximum token count per user request before forwarding to inference, (b) implement circuit breaker detecting recursive tool invocation chains (depth > N) and terminating with an error, and (c) apply per-session concurrency limits.

**Where to Implement**: `orchestrator/middleware/token-budget.{ts|py}` — token counting and capping; `orchestrator/middleware/recursion-guard.{ts|py}` — tool chain depth limiting.

**Reference Patterns**: Token counting with `tiktoken`; circuit breaker with `opossum`; LLM inference quota management.

**Effort Estimate**: Medium — token budget enforcement is a configuration-level control in most LLM frameworks.

---

#### 29. R-1 — User (Composite: 6.2, Medium) — Partial Control

**Current Status**: Partial Control (Guardrails logs filtering events, but pre-rejection user input logging is not explicitly described)

**What to Implement**: Extend the Guardrails logging to include all user prompt submissions (including pre-filtering) with unique session ID, user identifier, timestamp, and content hash logged to the Audit Logger. This creates complete non-repudiation evidence for all user interactions.

**Where to Implement**: `guardrails/logging/user-action-logger.{ts|py}` — pre-filtering user input logging at the Guardrails ingress.

**Reference Patterns**: Structured logging with `winston` / `pino`; immutable audit log with content hashing; HMAC-signed log entries.

**Effort Estimate**: Low — extending Guardrails logging to capture all user input pre-filtering is a configuration and code addition.

---

#### 30. S-6 — MCP Tool Server (Composite: 6.2, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement caller authentication on the MCP Tool Server: all JSON-RPC tool call requests must include a signed caller identity token (JWT or HMAC); the Tool Server verifies the token before dispatching any tool. This prevents Application Zone attackers from spoofing valid agent identities.

**Where to Implement**: `tool-server/middleware/caller-auth.{ts|py}` — JWT/HMAC caller identity verification at Tool Server ingress.

**Reference Patterns**: JWT caller tokens; mTLS for agent-to-Tool Server connections; API key scoped to agent identity.

**Effort Estimate**: Medium — caller identity verification on an internal service endpoint is a standard pattern.

---

#### 31. AG-2 — LLM Agent Orchestrator (Composite: 6.1, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement emergent behavior detection through observability: deploy an anomaly detector watching the Orchestrator + Specialist Agent delegation chain for unusual patterns (recursive loops, unexpected tool sequences, cross-session interference). Alert and circuit-break on detected emergent behavior.

**Where to Implement**: `orchestrator/monitoring/behavior-monitor.{ts|py}` — delegation chain anomaly detection with alerting.

**Reference Patterns**: Behavioral monitoring with OpenTelemetry distributed traces; circuit breaker on anomalous delegation depth; alert integration with PagerDuty or equivalent.

**Effort Estimate**: High — behavioral anomaly detection requires baseline establishment and real-time pattern monitoring infrastructure.

---

#### 32. AG-4 — Inter-Agent Communication Channel (Composite: 6.0, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement Channel isolation and rate limiting to prevent cascading failures: (a) per-sender message rate limits preventing queue flooding, (b) dead-letter queues for failed message routing, and (c) priority queuing deprioritizing bulk traffic from a single sender.

**Where to Implement**: `inter-agent-channel/rate-limiter/sender-throttle.{ts|py}` — per-sender rate limiting on the Channel substrate.

**Reference Patterns**: Message queue rate limiting (RabbitMQ prefetch; Kafka consumer group limits); dead-letter queues; priority queuing configuration.

**Effort Estimate**: Medium — rate limiting in a message queue substrate is typically a configuration-level change.

---

#### 33. E-6 — Long-Running Learning Loop (Composite: 6.0, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement cryptographic verification for model updates: all model update packages from the Learning Loop must be signed with the Learning Loop's private key, and the Orchestrator / Specialist Agent / ClinAdvisor must verify the signature before applying any update.

**Where to Implement**: `learning-loop/signing/update-signer.{ts|py}`; `orchestrator/model-update/update-verifier.{ts|py}`; `specialist-agent/model-update/update-verifier.{ts|py}`.

**Reference Patterns**: Model signing with `sigstore` / `cosign`; HMAC-signed update manifests; checksum verification before model loading.

**Effort Estimate**: High — model update signing requires PKI infrastructure and integration with the model loading path in all three agent components.

---

#### 34. S-3 — LLM Agent Orchestrator (Composite: 5.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement cryptographic identity binding for the Orchestrator: issue the Orchestrator a service identity certificate (mTLS) or signed JWT identity token that all downstream components require before accepting requests. Deploy a service mesh (Istio or Linkerd) to enforce mutual TLS across the Application Zone.

**Where to Implement**: `orchestrator/identity/service-cert.{ts|py}` — mTLS identity provisioning; service mesh configuration for internal TLS enforcement.

**Reference Patterns**: mTLS with Istio / Linkerd service mesh; SPIFFE/SPIRE for workload identity; signed JWT service identities.

**Effort Estimate**: High — service mesh identity provisioning requires infrastructure deployment.

---

#### 35. T-3 — Specialist Agent (Composite: 5.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement delegation message integrity verification for the Specialist Agent: apply HMAC verification on all delegation messages received via the Channel (extending LLM-8 remediation to cover the Tampering STRIDE category). The Specialist Agent must refuse to process any delegation message failing integrity verification.

**Where to Implement**: `specialist-agent/middleware/message-integrity.{ts|py}` — HMAC verification at delegation message ingress.

**Reference Patterns**: HMAC-SHA256 verification; signed message envelopes; structured delegation schemas with mandatory signature fields.

**Effort Estimate**: Medium — if LLM-8 HMAC signing is implemented, T-3 adds only the Tampering-category enforcement path.

---

#### 36. T-4 — Inter-Agent Communication Channel (Composite: 5.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement message integrity protection on the Channel: all messages must include an HMAC or digital signature over message content. The Channel verifies integrity before routing; messages with invalid signatures are rejected and logged.

**Where to Implement**: `inter-agent-channel/middleware/message-integrity.{ts|py}` — HMAC verification at Channel message processing.

**Reference Patterns**: HMAC-SHA256 over message payload; signed message envelopes; TLS for transport-layer integrity.

**Effort Estimate**: High — channel-level message integrity requires signing infrastructure for all message producers.

---

#### 37. S-8 — External API (Composite: 5.8, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement TLS certificate pinning and API response signing verification at the MCP Tool Server for all External API calls. The Tool Server must verify the External API's TLS certificate against a pinned certificate or trusted CA, and validate response signatures if the External API supports signed responses.

**Where to Implement**: `tool-server/external-api/tls-pinning.{ts|py}` — certificate pinning configuration for External API connections.

**Reference Patterns**: TLS certificate pinning; HPKP (deprecated) or custom pinning logic; External API response HMAC verification.

**Effort Estimate**: Medium — TLS certificate pinning is a configuration change in the HTTP client used by the Tool Server.

---

#### 38. S-9 — Clinical Advisory Sub-Agent (Composite: 5.8, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement sender authentication for Clinical Query / Context messages: the Sub-Agent must verify that context messages originated from the Orchestrator (via HMAC or mTLS). This prevents context injection from other Application Zone components.

**Where to Implement**: `clinical-advisor/middleware/sender-auth.{ts|py}` — sender identity verification at Sub-Agent ingress.

**Reference Patterns**: HMAC-SHA256 sender verification; JWT-based sender identity; mTLS mutual authentication.

**Effort Estimate**: Medium — implement together with T-9 (context integrity) remediation.

---

#### 39. T-7 — Audit Logger (Composite: 5.8, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement append-only audit log storage with cryptographic hash chaining: each log entry includes the hash of the previous entry, making tampering detectable through hash chain verification. Restrict write access to the Audit Logger to only the designated logging paths (Orchestrator, Specialist, ToolServer, Guardrails, ClinAdvisor) via access control on the logging interface.

**Where to Implement**: `audit-logger/storage/hash-chain.{ts|py}` — hash-chained append-only log storage; `audit-logger/access-control/write-policy.{ts|py}` — write access enforcement.

**Reference Patterns**: Hash-chained audit logs (Merkle tree structure); WORM storage integration; `casbin` for write access policy.

**Effort Estimate**: High — hash chaining requires changes to the Audit Logger's storage layer and all log writers.

---

#### 40. AG-7 — Long-Running Learning Loop (Composite: 5.6, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement temporal attack detection in the Learning Loop: (a) log all training runs with before/after model behavior snapshots, (b) implement model behavior drift detection comparing post-training model outputs against a behavioral baseline, and (c) require human review and sign-off before any model update is applied in production.

**Where to Implement**: `learning-loop/monitoring/drift-detector.{ts|py}` — behavioral drift detection; `learning-loop/workflow/update-approval.{ts|py}` — human sign-off gate.

**Reference Patterns**: Model behavioral monitoring; automated regression testing pre-deployment; human-in-the-loop model update approval.

**Effort Estimate**: High — behavioral drift detection and approval gates require significant ML infrastructure investment.

---

#### 41. I-1 — Guardrails Service (Composite: 5.6, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement sanitized rejection responses from the Guardrails Service: rejected prompt reasons must not echo user-supplied content. Implement a templated rejection response describing the category of violation without returning offending content. Mask any PII detected in rejection context before logging.

**Where to Implement**: `guardrails/response/sanitized-rejection.{ts|py}` — rejection response templating without content echo.

**Reference Patterns**: Generic rejection codes with lookup tables; content masking before response emission; `presidio` for PII detection in rejection reasons.

**Effort Estimate**: Low — rejection response sanitization is a configuration-level change in the Guardrails response template.

---

#### 42. LLM-9 — Specialist Agent (Composite: 5.6, Medium) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend the existing logging controls to include training data provenance tracking: implement signed training data manifests for the Specialist Agent's learning path, and add anomaly detection on the Specialist Agent's behavioral outputs to detect signs of data poisoning between training cycles.

**Where to Implement**: `specialist-agent/monitoring/behavior-monitor.{ts|py}` — behavioral drift detection; `learning-loop/intake/specialist-signal-validator.{ts|py}` — provenance validation for Specialist Agent training data.

**Reference Patterns**: Behavioral drift detection; signed training manifests; anomaly detection on model output distributions.

**Effort Estimate**: High — training data provenance and behavioral monitoring require ML infrastructure.

---

#### 43. D-6 — Knowledge Base (Composite: 5.7, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement query rate limiting on the Knowledge Base retrieval interface: enforce per-caller query rate limits (queries per minute) and apply circuit breaker logic to prevent query flooding from degrading retrieval availability for all callers.

**Where to Implement**: `knowledge-base/rate-limiter/query-throttle.{ts|py}` — per-caller retrieval rate limiting.

**Reference Patterns**: Rate limiting middleware on the KB query interface; `rate-limiter-flexible` for distributed rate limiting; `opossum` circuit breaker.

**Effort Estimate**: Medium — query rate limiting on a vector store interface is a middleware addition.

---

#### 44. LLM-11 — Long-Running Learning Loop (Composite: 5.7, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement training signal integrity verification: validate the content and provenance of the audit log training stream before ingestion. Use cryptographic signing of training batches and implement anomaly detection on incoming training signal distributions to detect adversarial injection.

**Where to Implement**: `learning-loop/intake/signal-validator.{ts|py}` — training signal provenance and integrity checking.

**Reference Patterns**: Signed training batches; statistical anomaly detection on training signal distributions; ML data provenance frameworks.

**Effort Estimate**: High — training signal anomaly detection requires statistical baseline modeling.

---

#### 45. T-8 — Long-Running Learning Loop (Composite: 5.7, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement hash-chained integrity verification on the Training Signal Stream from the Audit Logger: each training batch includes a Merkle root of the included audit entries, and the Learning Loop verifies the Merkle root before incorporating the batch. This detects adversarial insertion of fake audit entries.

**Where to Implement**: `audit-logger/export/signed-training-batch.{ts|py}` — Merkle-signed training batch export; `learning-loop/intake/batch-verifier.{ts|py}` — Merkle root verification.

**Reference Patterns**: Merkle tree hash chains; signed dataset exports; content-addressed storage.

**Effort Estimate**: High — Merkle-signed training batches require changes to both the Audit Logger export and Learning Loop intake paths.

---

#### 46. D-3 — Specialist Agent (Composite: 5.5, Medium) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend the existing input filtering controls to include Specialist Agent inference capacity protection: implement per-delegation-task token budget limits and circuit breaker logic on the Specialist Agent's inference path to prevent capacity exhaustion from high-complexity delegated tasks.

**Where to Implement**: `specialist-agent/middleware/token-budget.{ts|py}` — per-task token budget enforcement.

**Reference Patterns**: Token counting with `tiktoken`; circuit breaker with `opossum`; per-task inference quota management.

**Effort Estimate**: Medium — token budget enforcement is a configuration addition to the Specialist Agent's inference path.

---

#### 47. D-4 — Inter-Agent Communication Channel (Composite: 5.5, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement message queue flooding prevention on the Channel: per-sender message rate limits, maximum queue depth limits, and priority queuing that deprioritizes bulk sender traffic. Implement dead-letter queues for undeliverable messages.

**Where to Implement**: `inter-agent-channel/rate-limiter/queue-guard.{ts|py}` — queue flooding prevention.

**Reference Patterns**: Message queue rate limiting; dead-letter queues; priority queuing in RabbitMQ or Kafka.

**Effort Estimate**: Medium — queue flooding prevention is a configuration-level change in most messaging substrates.

---

#### 48. D-7 — Audit Logger (Composite: 5.5, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement log flooding protection on the Audit Logger: enforce per-caller log entry rate limits, implement async buffering with backpressure, and add a circuit breaker that switches to compressed-format logging under high load rather than dropping entries.

**Where to Implement**: `audit-logger/rate-limiter/entry-throttle.{ts|py}` — per-caller log rate limiting with backpressure.

**Reference Patterns**: Log rate limiting with `winston` rate limiting transport; async log buffering; circuit breaker for graceful degradation.

**Effort Estimate**: Medium — log rate limiting is a transport-level configuration in most logging frameworks.

---

#### 49. AG-8 — Inter-Agent Communication Channel (Composite: 5.5, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement comprehensive inter-agent communication security per OWASP ASI07:2026: (a) mutual authentication between all agent pairs, (b) message integrity verification (HMAC or digital signatures), (c) replay prevention (nonce + sliding window), and (d) message content validation against declared schemas. This remediation encompasses E-4, S-5, T-4, and AG-8.

**Where to Implement**: `inter-agent-channel/security/secure-channel.{ts|py}` — unified secure channel implementation combining authentication, integrity, and replay prevention.

**Reference Patterns**: Secure messaging protocol with mutual auth + integrity + replay prevention; protocol buffers with signing; TLS 1.3 mutual authentication.

**Effort Estimate**: High — comprehensive inter-agent security is an architectural change affecting all agent-to-channel interactions.

---

#### 50. I-6 — Knowledge Base (Composite: 5.4, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement access control on Knowledge Base retrieval: enforce namespace-based document scoping so each caller can only retrieve documents in its authorized partition (e.g., Clinical Advisory only retrieves clinical documents; Orchestrator retrieves general documents). Implement ABAC policy evaluation at the retrieval interface.

**Where to Implement**: `knowledge-base/access-control/retrieval-policy.{ts|py}` — ABAC-enforced retrieval namespace access control.

**Reference Patterns**: `casbin` ABAC; vector store namespace isolation; query-time metadata filters with caller identity context.

**Effort Estimate**: Medium — namespace-based access control is typically configurable in vector store clients with query-time filtering.

---

#### 51. I-7 — Audit Logger (Composite: 5.4, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement access control on the Audit Logger: restrict read access to authorized audit consumers only (e.g., Learning Loop, security monitoring). All other components (Orchestrator, Specialist Agent) should have write-only access. Implement data masking for PII in audit log entries before storage.

**Where to Implement**: `audit-logger/access-control/read-policy.{ts|py}` — RBAC read access enforcement; `audit-logger/masking/pii-masker.{ts|py}` — PII masking before storage.

**Reference Patterns**: `casbin` RBAC for log access; `presidio` for PII masking; write-only access patterns for log producers.

**Effort Estimate**: Medium — RBAC-based log access control is a standard authorization pattern.

---

#### 52–84. Additional Medium/Low Gap Recommendations

Remaining findings follow established architectural control patterns:

- **D-8 (Learning Loop)**: Implement resource quotas and scheduling isolation for Learning Loop training jobs to prevent resource competition with production inference. Effort: Medium.
- **I-5 (MCP Tool Server)**: Extend MCP Tool Server logging to include PII masking of External API response content before forwarding results. Implement a response content sanitizer. Effort: Medium.
- **LLM-3 (Orchestrator model theft)**: Implement output rate limiting and response variance reduction to prevent systematic model behavior extraction via API probing. Effort: Medium.
- **LLM-12 (Learning Loop model theft)**: Restrict Learning Loop output monitoring access; implement differential privacy on model update outputs to prevent model theft via output observation. Effort: High.
- **T-6 (Knowledge Base tampering)**: Implement write access control on the Knowledge Base: only authorized indexing services may write documents. Read-write separation with RBAC enforcement. Effort: Medium.
- **S-2 (Guardrails spoofing)**: Implement mTLS between the Guardrails Service and downstream components (Orchestrator) to prevent Guardrails identity spoofing. Effort: High.
- **I-4 (Channel eavesdropping)**: Enforce TLS encryption for all messages transiting the Inter-Agent Communication Channel. Effort: Medium.
- **AGP-01 (Emergent behavior)**: Implement comprehensive multi-agent behavioral monitoring with circuit breakers on delegation depth and cross-component anomaly correlation. Effort: High.
- **I-8 (Learning Loop data minimization)**: Implement selective audit log export for Learning Loop training — filter out PII and sensitive fields before training signal export. Effort: Medium.
- **R-7 (Learning Loop repudiation)**: Implement signed model update manifests with a verifiable update audit trail. Effort: High (aligned with E-6 remediation).
- **S-4 (Specialist Agent spoofing)**: Implement mTLS agent identity for the Specialist Agent; the Channel must verify Specialist Agent identity before routing responses. Effort: High.
- **I-3 (Specialist Agent data exposure)**: Encrypt delegation messages containing sensitive data; the Specialist Agent should decrypt only the fields required for its delegated task. Effort: Medium.
- **R-5 (Channel repudiation)**: Implement message delivery receipts with signed acknowledgments on the Channel to create non-repudiation evidence. Effort: High.

---

## 5. Residual Risk Summary

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total inherent risk (sum of composite scores) | 508.8 |
| Total residual risk (sum of residual scores) | 479.9 |
| Risk delta | 28.9 |
| Overall reduction percentage | 5.7% |

### Per-Severity-Band Shift

| Shift | Count |
|-------|-------|
| High → Medium | 9 |
| High → Low | 0 |
| Medium → Low | 5 |
| Medium → Medium (no change band) | 62 |
| High → High (no change band) | 8 |
| **Total severity shifts** | **14** |

### Severity Distribution Comparison

| Severity Band | Inherent Count | Residual Count | Delta |
|---------------|---------------|----------------|-------|
| Critical | 0 | 0 | 0 |
| High | 17 | 8 | −9 |
| Medium | 67 | 71 | +4 |
| Low | 0 | 5 | +5 |
| **Total** | **84** | **84** | — |

### Reduction Factor Reference

| Control Status | Reduction Factor | Interpretation |
|----------------|-----------------|----------------|
| Control Found | 0.50 | Risk reduced by 50% |
| Partial Control | 0.25 | Risk reduced by 25% |
| No Control Found | 0.00 | No risk reduction |

*P1 note: Detailed 4-dimension effectiveness assessment (Coverage, Configuration, Currency, Completeness) is deferred to P1 (User Story 6). Current ratings use the P0 binary model: found → strong, partial → moderate, missing → none.*

---

## 6. Methodology

### Control Detection Approach

This analysis uses the tachi compensating controls pipeline (P0 binary model):

1. **Input parsing**: 84 scored findings extracted from `risk-scores.md`. Composite scores range from 4.3 (R-5) to 8.2 (S-1). Severity distribution: 17 High, 67 Medium, 0 Critical, 0 Low.

2. **Codebase discovery**: No source codebase provided. Analysis target is `architecture.md`, which describes component roles, data flows, and trust boundaries for a multi-agent AI application with 11 components across 3 trust zones (User Zone, Application Zone, External Services).

3. **Control detection**: Architecture signals analyzed for each of the 8 control categories. Detected partial controls:
   - **Logging/Audit**: Explicit data flows to Audit Logger from Orchestrator, Specialist, MCP Tool Server, Guardrails, and Clinical Advisory. All classified as partial (integrity of Audit Logger itself is unverified per T-7; no described cryptographic signing).
   - **Input Validation**: Guardrails Service described as filtering/validating user prompts. Classified as partial (no code-level evidence of validation schema depth or bypass resistance).
   - No other control categories have architectural signals sufficient for even partial classification.

4. **Classification**: STRIDE-to-control-category mapping applied per the control-categories reference. 31 findings receive Partial Control; 53 receive No Control Found; 0 receive Control Found.

5. **Residual risk calculation**: `residual_score = composite_score × (1 − reduction_factor)`. Reduction factors: found=0.50, partial=0.25, missing=0.00. All residual scores clamped to [0.0, 10.0] and rounded to 1 decimal place.

6. **Recommendations**: Generated for all 53 missing and 31 partial findings, sorted by composite score descending.

### Control Categories Assessed

| Category | Detection Result | Architectural Signal |
|----------|-----------------|---------------------|
| Authentication | No detection | No auth middleware, JWT, or session management described |
| Input Validation | Partial (Guardrails only) | Guardrails described as filtering/validating user prompts |
| Rate Limiting | No detection | No rate limiting described; Guardrails may imply throttling |
| Encryption | No detection | HTTPS transport described but no at-rest encryption or TLS config detail |
| Logging/Audit | Partial (5 components) | Explicit data flows to Audit Logger from 5 components |
| CSRF Protection | No detection | No CSRF mechanism described |
| CSP/Security Headers | No detection | No HTTP security headers described |
| Access Control | No detection | No RBAC, ABAC, or permission model described |

### Limitations

- **No source code available**: All control classifications are architectural inferences. Production analysis requires scanning implementation files. All partial detections should be treated as unverified assumptions pending code-level review.
- **Architecture signals are high-level**: The architecture describes intended behavior, not implemented behavior. A "Guardrails Service" may have stronger or weaker actual filtering than the architecture implies.
- **HTTPS implied, not verified**: The architecture describes `User -->|"Prompt / Query (HTTPS)"| Guardrails` and `ToolServer -->|"API Request (HTTPS)"| ExtAPI`, implying TLS in transport. However, without TLS configuration details, encryption cannot be classified as even a partial control.
- **Repudiation partial rating**: The Audit Logger provides partial non-repudiation evidence, but T-7 notes that audit log entries themselves can be tampered with — this gap means the logging control is inherently partial regardless of implementation detail.

### Schema Version

tachi compensating controls schema version 1.0 | Pipeline: threat-model → risk-score → compensating-controls
