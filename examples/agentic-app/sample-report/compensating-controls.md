---
schema_version: "1.0"
date: "2026-04-27"
source_file: "examples/agentic-app/sample-report/risk-scores.md"
target_path: "examples/agentic-app (architecture-only — no source codebase)"
classification: "security"
rescan_scope: "incremental"
carry_forward_count: 84
---

# Compensating Controls — Agentic AI Application (F-5 Wave 2)

## 1. Executive Summary

**88** threats analyzed | **0** Control Found | **33** Partial Control | **55** No Control Found

**Coverage**: 0% Found | 38% Partial | 63% Missing (rounding adjusts to 100%)

**Risk Reduction**: 537.6 inherent → 505.1 residual (**6.0%** reduction)

**Highest-Risk Unmitigated Finding**: S-1 — User — Composite 8.2 (High) — No authentication or access control detected at the User component.

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-27 |
| Source file | `examples/agentic-app/sample-report/risk-scores.md` |
| Target codebase | `examples/agentic-app (architecture-only — no source codebase)` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0% |
| Partial Control | 33 | 38% |
| No Control Found | 55 | 63% |
| **Total** | **88** | **100%** |

> **Analysis Warning**: No source codebase was provided. All control detection is based solely on the architecture document (`architecture.md`). Control evidence consists of architectural signals (component descriptions, data-flow annotations) rather than implementation code. All detections are classified as Medium confidence at best and result in `partial` status. Production control analysis requires scanning actual implementation files.
>
> **Incremental scan**: 84 findings carried forward from baseline (2026-04-26T03-39-12). 4 NEW findings (D-10, D-11, LLM-15, LLM-16) freshly analyzed for controls in this wave.

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
| D-10 | — | LLM Agent Orchestrator | LLM Inference-Request Flooding and Token Exhaustion without per-tenant QPS rate limiting | 7.2 | High | No Control Found | 7.2 | High |
| D-11 | — | LLM Agent Orchestrator | Context-Window Exhaustion — Latency-Driven Variant without max-context-window enforcement | 7.2 | High | No Control Found | 7.2 | High |
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
| LLM-15 | — | LLM Agent Orchestrator | Cost Amplification via Recursive or Cost-Asymmetric Prompting without output-token caps | 7.2 | High | Partial Control | 5.4 | Medium |
| LLM-16 | — | LLM Agent Orchestrator | Denial-of-Wallet via Context-Window Cost Amplification without per-tenant token budget hard-cap | 7.2 | High | Partial Control | 5.4 | Medium |
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
| I-1 | — | Guardrails Service | The Guardrails Service leaks rejected prompt content in error responses | 5.6 | Medium | No Control Found | 5.6 | Medium |
| S-3 | — | LLM Agent Orchestrator | The Orchestrator's identity is not cryptographically bound — impersonation risk | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-3 | — | Specialist Agent | The Specialist Agent's operational context can be tampered with via delegation messages | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-4 | — | Inter-Agent Communication Channel | Messages transiting the Channel lack integrity protection — in-transit tampering | 5.9 | Medium | No Control Found | 5.9 | Medium |
| S-8 | — | External API | The External API provider's identity is not verified by the MCP Tool Server | 5.8 | Medium | No Control Found | 5.8 | Medium |
| S-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent receives Clinical Query / Context without sender authentication | 5.8 | Medium | No Control Found | 5.8 | Medium |
| T-7 | — | Audit Logger | The Audit Logger entries can be tampered with by any component with write access | 5.8 | Medium | No Control Found | 5.8 | Medium |
| AG-7 | — | Long-Running Learning Loop | The Learning Loop's model update mechanism is vulnerable to temporal attacks | 5.6 | Medium | No Control Found | 5.6 | Medium |
| D-9 | — | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent is invoked by the Orchestrator and its inference capacity is bounded | 5.6 | Medium | Partial Control | 4.2 | Medium |
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
| I-8 | — | Long-Running Learning Loop | The Learning Loop consumes the full Audit Logger training stream without data minimization | 4.9 | Medium | No Control Found | 4.9 | Medium |
| R-7 | — | Long-Running Learning Loop | The Learning Loop denies having applied a specific model update | 4.9 | Medium | No Control Found | 4.9 | Medium |
| S-4 | — | Specialist Agent | The Specialist Agent impersonates the Orchestrator when responding via the Channel | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-3 | — | Specialist Agent | The Specialist Agent receives sensitive data via delegation messages without encryption | 4.8 | Medium | No Control Found | 4.8 | Medium |
| AGP-01 | — | LLM Agent Orchestrator | Multi-agent emergent behavior — cascading failure through delegation chains | 4.6 | Medium | No Control Found | 4.6 | Medium |
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
| High | 10 | 11% |
| Medium | 73 | 83% |
| Low | 5 | 6% |
| **Total** | **88** | **100%** |

---

## 3. Control Details

Control evidence is derived from the architecture document (`architecture.md`) since no source codebase was provided. All controls are inferred from component descriptions, data-flow annotations, and structural signals in the architecture. Confidence is Medium for logging/audit (explicit architectural data flows described) and Low for input validation (implied by the Guardrails component role). The four F-5 Wave 2 findings (D-10, D-11, LLM-15, LLM-16) targeting the LLM Agent Orchestrator were freshly analyzed and inherit the same architectural control signals as baseline findings for that component.

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
| R-9 | Clinical Advisory Sub-Agent | ClinAdvisor denies generating a clinical recommendation | 5.2 | 0.25 | 3.9 |
| R-8 | External API | External API denies returning a specific response | 5.0 | 0.25 | 3.8 |
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

**Effectiveness Assessment**: *Detailed effectiveness assessment available in P1 (User Story 6).*

**Threats Mitigated by This Control** (LLM Threats findings where audit logging provides partial control):

| Threat ID | Component | Threat (brief) | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|----------------|----------------|------------------|----------------|
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection via User→Guardrails | 7.2 | 0.25 | 5.4 |
| LLM-4 | LLM Agent Orchestrator | Training data poisoning via Learning Loop | 7.1 | 0.25 | 5.3 |
| LLM-15 | LLM Agent Orchestrator | Cost Amplification via Recursive Prompting | 7.2 | 0.25 | 5.4 |
| LLM-16 | LLM Agent Orchestrator | Denial-of-Wallet via Context-Window Cost Amplification | 7.2 | 0.25 | 5.4 |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via KB retrieval | 6.8 | 0.25 | 5.1 |
| LLM-7 | LLM Agent Orchestrator | SSRF via LLM-synthesized URL | 6.6 | 0.25 | 5.0 |
| LLM-10 | Specialist Agent | Server-side injection via Specialist tool call | 6.5 | 0.25 | 4.9 |
| OI-3 | LLM Agent Orchestrator | SSRF via LLM-synthesized URL (OI category) | 6.5 | 0.25 | 4.9 |
| LLM-3 | LLM Agent Orchestrator | Model theft via systematic API probing | 5.3 | 0.25 | 4.0 |

*Note: D-10 and D-11 (Denial of Service category) map to Rate Limiting, not Logging/Audit. Logging provides no reduction for inference-layer denial-of-service findings absent rate-limiting implementation. Both classified as No Control Found.*

---

#### ARCH-LOG-03 — Clinical Advisory Sub-Agent clinical decision logging

**Category**: Logging/Audit | **Status**: Partial | **Effectiveness**: Moderate

**Detected in**: `architecture.md:58`

```
ClinAdvisor -->|"Clinical Decision Log Entry"| AuditLog
```

**Effectiveness Assessment**: *Detailed effectiveness assessment available in P1 (User Story 6).*

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

*Note: D-10 and D-11 target Denial-of-Service via resource exhaustion at the LLM inference layer. The Guardrails Service filters prompt content but does not enforce per-tenant QPS limits or max-context-window policies at the inference tier. These are categorically distinct from input content validation and are classified as No Control Found against the Rate Limiting category.*

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

**What to Implement**: Implement least-privilege access control for the Orchestrator: (a) scope KB access to query-relevant documents only (not full-corpus access), (b) restrict tool invocation to a pre-approved allowlist per request context, and (c) implement delegation authority limits so the Orchestrator can only delegate tasks within the scope of the original user request. Use ABAC policy evaluation before each privileged operation.

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

#### 5. D-10 — LLM Agent Orchestrator (Composite: 7.2, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement per-tenant QPS (queries-per-second) rate limiting at the API gateway layer for the LLM inference endpoint. Enforce max-token-per-request limits to prevent individual requests from consuming the full inference compute budget. Add fan-out budget enforcement that caps the total number of concurrent downstream inference calls (Orchestrator + Specialist + ClinAdvisor) triggered by a single user request. Set automated circuit-breaker thresholds that reject incoming inference requests when the inference queue depth exceeds a configured ceiling.

**Where to Implement**: `api-gateway/middleware/inference-rate-limiter.{ts|py}` for per-tenant QPS enforcement; `orchestrator/policy/token-budget.{ts|py}` for max-token-per-request policy; `orchestrator/policy/fan-out-budget.{ts|py}` for concurrent downstream inference cap.

**Reference Patterns**: `express-rate-limit` or `rate-limiter-flexible` for API-gateway rate limiting; `tiktoken` for server-side token counting before submission; `opossum` for circuit breaker on inference queue depth; LLM API provider-level per-key rate limit configuration (OpenAI, Anthropic, Azure APIM policies).

**Effort Estimate**: Medium — API-gateway rate limiting and token-counting middleware are standard configuration additions; fan-out budget enforcement requires a lightweight orchestration policy layer.

---

#### 6. D-11 — LLM Agent Orchestrator (Composite: 7.2, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement max-context-window enforcement at the API gateway before inference requests are dispatched. Reject or truncate conversation history payloads that exceed the declared context limit for the deployed model tier. Add recursive-prompt detection that identifies adversarially constructed long prompts (repeated patterns, padding sequences) and short-circuits them before they enter the inference queue. Apply the same fan-out slot protection as D-10 to prevent a single max-context request from blocking all three inference endpoints simultaneously.

**Where to Implement**: `api-gateway/middleware/context-window-enforcer.{ts|py}` — token-count enforcement rejecting payloads exceeding the configured maximum; `orchestrator/policy/recursive-prompt-guard.{ts|py}` — repetition and expansion pattern detection.

**Reference Patterns**: `tiktoken` for server-side token counting; sliding-window context truncation utilities; `opossum` for circuit breaker on inference slot exhaustion; LLM proxy layers (LiteLLM, Portkey) with built-in context-limit enforcement.

**Effort Estimate**: Medium — context-window enforcement is a token-counting middleware addition; recursive prompt detection requires a lightweight heuristic pattern matcher.

---

#### 7. I-2 — LLM Agent Orchestrator (Composite: 7.2, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement context isolation controls to prevent context window leakage: (a) enforce strict system-prompt confidentiality (system prompt never echoed in responses), (b) implement output filtering to detect and redact context-referencing disclosures before sending responses to users, and (c) segment the context window so KB documents and tool results are in separate memory regions not directly accessible to response generation without explicit retrieval.

**Where to Implement**: `orchestrator/output-filter/context-leak-guard.{ts|py}` — output scanning for system-prompt disclosure patterns; `orchestrator/memory/context-segmentation.{ts|py}` — context isolation architecture.

**Reference Patterns**: Prompt isolation patterns; output filtering with `rebuff`; structured context management with LangChain memory classes.

**Effort Estimate**: High — context isolation requires rearchitecting how the Orchestrator assembles and exposes its context window.

---

#### 8. T-2 — LLM Agent Orchestrator (Composite: 7.1, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement context window integrity controls: (a) sign all system-prompt segments with HMAC before inserting them into the context window, (b) validate HMAC signatures at context assembly time to detect tampering, and (c) implement content-hash verification on Knowledge Base documents retrieved into context to detect upstream poisoning.

**Where to Implement**: `orchestrator/context-assembly/hmac-validator.{ts|py}` — context integrity verification; `orchestrator/kb-client/document-hash-check.{ts|py}` — retrieved document integrity verification.

**Reference Patterns**: HMAC-SHA256 for segment integrity; Merkle-chained context assembly; content-addressed document storage.

**Effort Estimate**: High — comprehensive context integrity requires changes to the context assembly pipeline and KB retrieval path.

---

#### 9. E-5 — MCP Tool Server (Composite: 7.0, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement zero-trust authorization at the MCP Tool Server: each tool call request must carry a signed capability token scoped to the specific tool and parameters; the Tool Server validates the token and rejects calls exceeding the granted scope. Implement tool-call audit logging for all executions, and enforce credential least-privilege so each tool uses its own minimum-privilege service account rather than shared credentials.

**Where to Implement**: `tool-server/middleware/capability-validator.{ts|py}` — capability token validation; `tool-server/auth/service-account-router.{ts|py}` — per-tool credential scoping.

**Reference Patterns**: Capability-based security with JWT scope claims; `casbin` for tool-level authorization policy; MCP server authorization middleware patterns.

**Effort Estimate**: High — zero-trust tool authorization requires changes to the agent-to-tool-server protocol and credential management infrastructure.

---

#### 10. T-5 — MCP Tool Server (Composite: 7.0, High) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement strict tool call parameter validation at the MCP Tool Server: define a JSON Schema for each registered tool's `params` object and validate all incoming parameters against it before dispatch. Reject calls where parameters fail schema validation. Implement parameter sanitization stripping SQL injection, shell metacharacters, and path traversal sequences from string parameters.

**Where to Implement**: `tool-server/middleware/param-schema-validator.{ts|py}` — JSON Schema validation per tool; `tool-server/middleware/param-sanitizer.{ts|py}` — injection metacharacter stripping.

**Reference Patterns**: JSON Schema validation with `ajv`; `zod` for TypeScript tool parameter schemas; `validator.js` for input sanitization.

**Effort Estimate**: Medium — schema-based parameter validation per registered tool is a configuration addition to the MCP Tool Server dispatcher.

---

#### 11. LLM-6 — LLM Agent Orchestrator (Composite: 7.7, High) — Partial Control

**Current Status**: Partial Control (Guardrails filters user input but not LLM-generated tool parameters)

**What to Implement**: Extend the existing Guardrails input validation to cover LLM-synthesized JSON-RPC parameters flowing to the MCP Tool Server. Implement a tool parameter sanitization layer at the Tool Server ingress that validates each parameter against the tool's declared JSON Schema and strips injection payloads (SQL fragments, shell metacharacters, template expressions) before dispatch.

**Where to Implement**: `tool-server/middleware/param-sanitizer.{ts|py}` — server-side validation at MCP Tool Server ingress on all JSON-RPC `params`; extend `orchestrator/output-validator.{ts|py}` to cover Orchestrator-generated tool invocations.

**Reference Patterns**: JSON Schema validation with `ajv`; `zod` for strict TypeScript parameter schemas; parameterized query enforcement for database-backed tools.

**Effort Estimate**: Medium — extending existing validation infrastructure to the tool parameter path requires schema definitions for each registered tool.

---

#### 12. OI-2 — LLM Agent Orchestrator (Composite: 7.7, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Implement a dedicated output sanitization layer treating all LLM-generated content destined for server-side execution sinks as untrusted input. Validate parameter schemas, strip injection metacharacters, and require parameterized invocations for all database and shell tool calls. This is the OI-category complement to LLM-6 and should be implemented together.

**Where to Implement**: `orchestrator/output-sanitizer/tool-params.{ts|py}` — intercept all `Tool Call Request (JSON-RPC)` messages before emission to the Tool Server.

**Reference Patterns**: `instructor` for structured LLM outputs; JSON Schema enforcement; parameterized tool invocations with strict type validation.

**Effort Estimate**: Medium — output sanitization interceptor in the Orchestrator's tool dispatch path; implement together with LLM-6 remediation.

---

#### 13. LLM-5 — LLM Agent Orchestrator (Composite: 7.5, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Implement client-side XSS prevention: (a) apply HTML output encoding to all LLM-generated content before client rendering, (b) deploy a Content Security Policy (CSP) header restricting script execution to approved sources, and (c) use a DOM sanitization library to strip executable markup from LLM responses. The architecture passes LLM output directly to the User without client-side sanitization.

**Where to Implement**: `api-gateway/middleware/response-sanitizer.{ts|py}` for server-side output encoding; HTTP response CSP header configuration; `frontend/utils/sanitize.ts` for DOM-level sanitization.

**Reference Patterns**: `DOMPurify` for DOM sanitization; `helmet` with `contentSecurityPolicy` for CSP enforcement; `sanitize-html` for HTML stripping.

**Effort Estimate**: Medium — CSP and output encoding require coordination between backend response headers and frontend rendering pipeline.

---

#### 14. OI-1 — LLM Agent Orchestrator (Composite: 7.5, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: OI-1 covers the same XSS attack vector as LLM-5 from the Output Integrity taxonomy perspective. Implementing the LLM-5 remediation (output encoding + CSP + DOM sanitization) fully addresses OI-1 with no additional changes required.

**Where to Implement**: Same as LLM-5 remediation — `api-gateway/middleware/response-sanitizer.{ts|py}` and CSP header configuration.

**Reference Patterns**: `DOMPurify`; `helmet` CSP; `sanitize-html`.

**Effort Estimate**: Low — OI-1 is resolved by the LLM-5 remediation; no standalone implementation required.

---

#### 15. LLM-13 — Clinical Advisory Sub-Agent (Composite: 7.4, High) — Partial Control

**Current Status**: Partial Control (logging present; input validation for clinical context missing)

**What to Implement**: Extend the logging-based partial control to include clinical query input validation: (a) implement a clinical context schema validator enforcing structured clinical query formats and rejecting free-form injection attempts, (b) add a prompt integrity check detecting instruction-override patterns in clinical context messages, and (c) require HMAC-signed clinical context objects from the Orchestrator to the Sub-Agent to prevent in-transit tampering.

**Where to Implement**: `clinical-advisor/middleware/context-validator.{ts|py}` — schema and injection-pattern validation; `orchestrator/clinical-client/hmac-signer.{ts|py}` — HMAC signing of clinical context before dispatch.

**Reference Patterns**: Structured clinical query schemas with `zod` / `pydantic`; prompt injection pattern detection; HMAC-SHA256 for message integrity.

**Effort Estimate**: Medium — schema validation and HMAC signing are standard middleware additions.

---

#### 16. LLM-8 — Specialist Agent (Composite: 7.3, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend the existing Guardrails input validation to cover the delegation message path: implement a delegation message schema validator that enforces structured task specifications and rejects free-form prompt-injection patterns in task descriptions. Add HMAC signing of delegation messages from the Orchestrator and verify signatures at the Specialist Agent ingress before task execution.

**Where to Implement**: `specialist-agent/middleware/delegation-validator.{ts|py}` — schema and injection-pattern validation on incoming delegation messages; `orchestrator/channel/hmac-signer.{ts|py}` — HMAC signing of delegation messages.

**Reference Patterns**: Structured delegation schemas; HMAC-SHA256 for message integrity; `zod` for delegation schema validation.

**Effort Estimate**: Medium — delegation schema enforcement is an extension to the Channel's message routing; HMAC signing is a standard addition.

---

### Medium Risk Gaps

#### 17. LLM-1 — LLM Agent Orchestrator (Composite: 7.2, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Harden the existing Guardrails input validation to improve direct prompt injection resistance: (a) implement adversarial prompt detection using a secondary classifier, (b) enforce structured prompt templates that constrain user-controllable text regions, and (c) add jailbreak pattern matching against a curated injection pattern library.

**Where to Implement**: `guardrails/filters/injection-classifier.{ts|py}` — secondary classifier for adversarial prompts; `guardrails/templates/prompt-template.{ts|py}` — structured prompt template enforcement.

**Reference Patterns**: `rebuff` for prompt injection detection; `llm-guard` for adversarial prompt classification; NeMo Guardrails input rails.

**Effort Estimate**: Medium — secondary classifier and template enforcement are additions to the existing Guardrails filter pipeline.

---

#### 18. LLM-15 — LLM Agent Orchestrator (Composite: 7.2, High) — Partial Control

**Current Status**: Partial Control (logging present via Audit Logger; no output-token cap or recursive-depth limit detected)

**What to Implement**: Implement output-amplification monitoring and cost-per-query alerting: (a) enforce per-request output-token caps at the LLM API client level before dispatching to the model provider, (b) track cumulative token consumption per session across all fan-out legs (Orchestrator + Specialist + ClinAdvisor), (c) emit cost-per-query metrics to the monitoring stack with threshold-based alerts when a single request exceeds a cost ceiling, and (d) implement recursive prompt depth tracking that aborts multi-hop chains exceeding a configured depth limit.

**Where to Implement**: `orchestrator/policy/output-token-cap.{ts|py}` — per-request output limit enforcement; `orchestrator/telemetry/cost-tracker.{ts|py}` — cumulative cost tracking and alerting; `orchestrator/policy/recursion-depth-guard.{ts|py}` — multi-hop chain depth limiter.

**Reference Patterns**: LLM API provider `max_tokens` parameter enforcement; `tiktoken` for output token counting; OpenTelemetry metrics for cost-per-query tracking; LiteLLM or Portkey cost tracking middleware.

**Effort Estimate**: Medium — output-token caps and cost tracking are standard LLM client configuration additions; recursion depth tracking requires lightweight state management in the Orchestrator's chain execution.

---

#### 19. LLM-16 — LLM Agent Orchestrator (Composite: 7.2, High) — Partial Control

**Current Status**: Partial Control (logging present; no per-tenant token budget hard-cap or denial-of-wallet anomaly detection detected)

**What to Implement**: Implement per-tenant token budget hard-caps with automated tenant suspension on budget exhaustion: (a) enforce daily/monthly token budgets per tenant at the API gateway, rejecting requests that would exceed the tenant's remaining budget, (b) implement denial-of-wallet anomaly detection comparing current spend rate to tenant baseline and triggering alerts on anomalous acceleration, (c) add automated tenant suspension that pauses a tenant's access when spend exceeds a 2x daily baseline within any rolling 1-hour window.

**Where to Implement**: `api-gateway/middleware/tenant-budget-enforcer.{ts|py}` — per-tenant token budget hard-cap with request rejection on exhaustion; `api-gateway/telemetry/spend-anomaly-detector.{ts|py}` — baseline spend comparison and anomaly alerting; `api-gateway/policy/tenant-suspension.{ts|py}` — automated suspension logic.

**Reference Patterns**: Per-tenant quota management with Redis-backed counters; time-series spend anomaly detection; API gateway tenant lifecycle management; cost management APIs from LLM providers (OpenAI usage limits, AWS Bedrock quotas).

**Effort Estimate**: High — per-tenant budget enforcement with anomaly detection and automated suspension requires a tenant billing/quota management subsystem that spans the API gateway and monitoring stack.

---

#### 20. LLM-4 — LLM Agent Orchestrator (Composite: 7.1, High) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend the existing audit logging to include training data provenance tracking: log the content hash of each audit entry contributing to the training signal stream, and implement a validation step in the Learning Loop that verifies audit entry hashes before incorporating them into training. This makes poisoned audit entries detectable through hash chain breaks.

**Where to Implement**: `audit-logger/export/signed-training-batch.{ts|py}` — hash-chained training export; `learning-loop/intake/provenance-verifier.{ts|py}` — hash verification before training.

**Reference Patterns**: Merkle-chained audit exports; content-addressed training batches; signed dataset provenance.

**Effort Estimate**: Medium — hash-chaining the training export and verification step is a targeted addition to the audit pipeline.

---

#### 21. E-7 — Clinical Advisory Sub-Agent (Composite: 6.9, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement least-privilege access control for the Clinical Advisory Sub-Agent: restrict its KB retrieval to clinical document namespaces only, enforce read-only access to the KB, and implement capability tokens limiting the Sub-Agent to clinical summary operations. Apply ABAC policy evaluation at each KB retrieval call.

**Where to Implement**: `clinical-advisor/access-control/capability-policy.{ts|py}` — ABAC capability enforcement; `knowledge-base/access-control/clinical-namespace-policy.{ts|py}` — namespace-scoped retrieval access.

**Reference Patterns**: `casbin` for ABAC; vector store namespace isolation; capability-scoped JWT tokens.

**Effort Estimate**: Medium — namespace-scoped access control is configurable at the vector store level with per-caller metadata filters.

---

#### 22. I-9 — Clinical Advisory Sub-Agent (Composite: 6.8, Medium) — No Control Found

**Current Status**: No Control Found

**What to Implement**: Implement encryption and minimization for clinical data processed by the Clinical Advisory Sub-Agent: (a) encrypt clinical query payloads in transit between the Orchestrator and the Sub-Agent using TLS 1.3 mutual authentication, (b) implement field-level data minimization so the Sub-Agent receives only the clinical fields required for each query, and (c) enforce PII masking on clinical data before logging to the Audit Logger.

**Where to Implement**: `orchestrator/clinical-client/tls-client.{ts|py}` — mTLS configuration; `clinical-advisor/middleware/field-minimizer.{ts|py}` — field minimization; `audit-logger/masking/clinical-pii-masker.{ts|py}` — PII masking before logging.

**Reference Patterns**: TLS 1.3 mTLS; `presidio` for PII masking; field-level data minimization schemas.

**Effort Estimate**: High — mTLS between components and PII masking in the audit path require changes to both the transport layer and logging pipeline.

---

#### 23. LLM-2 — LLM Agent Orchestrator (Composite: 6.8, Medium) — Partial Control

**Current Status**: Partial Control

**What to Implement**: Extend the existing Guardrails input validation to the Knowledge Base retrieval path: implement document content scanning at KB retrieval time that detects adversarially injected prompt override patterns in retrieved documents before they enter the Orchestrator's context window. Add retrieval-time content hash verification against a trusted document registry.

**Where to Implement**: `orchestrator/kb-client/retrieval-content-scanner.{ts|py}` — content scanning for injection patterns in retrieved documents.

**Reference Patterns**: Indirect prompt injection detection in RAG pipelines; content hash verification; document content sandboxing.

**Effort Estimate**: Medium — retrieval-time content scanning is an interceptor addition to the KB retrieval client.

---

#### 24–88. Additional Medium/Low Gap Recommendations

Remaining findings follow the same architectural control patterns established above. Key additional remediation themes:

- **D-1 (Guardrails DoS)**: Extend Guardrails to enforce per-IP request rate limits and implement circuit breaker logic to prevent resource exhaustion. Effort: Medium.
- **LLM-7 / OI-3 (SSRF via LLM output)**: Implement URL allowlist validation at the Tool Server ingress; reject any URL not in the pre-approved External API domain list before dispatching HTTP requests. Effort: Medium.
- **LLM-14 / T-9 (Clinical Advisory poisoning/tampering)**: Extend audit-log-based provenance tracking to the Clinical Advisory Sub-Agent's training inputs; implement content hash verification on clinical context payloads. Effort: Medium.
- **MI-1 / MI-2 / MI-3 (Misinformation)**: Implement source attribution tracking for all clinical claims; add HITL review gate before clinical recommendations reach the user; deploy a retrieval-grounding validator. Effort: High.
- **E-3 / E-4 / S-5 / T-4 (Channel security)**: Implement comprehensive inter-agent channel security: mTLS mutual authentication, HMAC message integrity, replay-prevention nonces. Effort: High.
- **S-7 / AG-7 / T-8 (Learning Loop temporal attacks)**: Implement signed model update manifests and hash-chained training data provenance. Effort: High.
- **D-2 (Orchestrator token flooding)**: Implement per-session token budgets and inference queue depth limits at the Orchestrator. This complements D-10/D-11 rate limiting. Effort: Medium.
- **D-6 / D-7 / D-8 (KB/Logger/Loop DoS)**: Implement per-caller rate limiting and backpressure at each data store interface. Effort: Medium per component.
- **AG-8 (Inter-Agent insecure communication)**: Implement OWASP ASI07:2026 comprehensive controls: mutual authentication between all agent pairs, HMAC message integrity, replay-prevention nonces, message content validation against declared schemas. Effort: High.
- **AGP-01 (Emergent behavior)**: Deploy multi-agent behavioral monitoring with delegation depth circuit breakers and anomaly correlation. Effort: High.
- **I-3 / I-4 (Sensitive data in channel)**: Enforce TLS encryption for all inter-agent channel messages; encrypt delegation message payloads containing sensitive data fields. Effort: Medium.
- **R-5 (Channel repudiation)**: Implement signed delivery receipts with non-repudiation evidence on the Channel substrate. Effort: High.
- **LLM-3 / LLM-12 (Model theft)**: Implement output rate limiting and differential privacy on API responses to prevent systematic model behavior extraction. Effort: Medium / High.
- **S-2 / S-3 (Component spoofing)**: Implement mTLS for all Application Zone component-to-component communication. Effort: High.
- **T-6 / T-7 (KB/Logger tampering)**: Implement write-access control (only authorized indexers may write to KB; components have write-only access to Audit Logger, not read or delete). Effort: Medium.
- **R-2 / R-4 / R-6 (Low-severity repudiation)**: Hardening the existing Audit Logger to include per-action content hash signatures would upgrade these from partial to found. Effort: Medium.

---

## 5. Residual Risk Summary

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total inherent risk (sum of composite scores) | 537.6 |
| Total residual risk (sum of residual scores) | 505.1 |
| Risk delta | 32.5 |
| Overall reduction percentage | 6.0% |

### Per-Severity-Band Shift

| Shift | Count |
|-------|-------|
| High → Medium | 11 |
| High → Low | 0 |
| Medium → Low | 5 |
| Medium → Medium (no band change) | 62 |
| High → High (no band change — missing control) | 10 |
| **Total severity shifts (band changes only)** | **16** |

*New shifts vs. baseline: LLM-15 (High → Medium, partial logging control) and LLM-16 (High → Medium, partial logging control) added 2 new High→Medium shifts. D-10 and D-11 remain High → High (no control found).*

### Severity Distribution Comparison

| Severity Band | Inherent Count | Residual Count | Delta |
|---------------|---------------|----------------|-------|
| Critical | 0 | 0 | 0 |
| High | 21 | 10 | −11 |
| Medium | 67 | 73 | +6 |
| Low | 0 | 5 | +5 |
| **Total** | **88** | **88** | — |

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

1. **Input parsing**: 88 scored findings extracted from `risk-scores.md`. Composite scores range from 4.3 (R-5) to 8.2 (S-1). Severity distribution: 21 High, 67 Medium, 0 Critical, 0 Low.

2. **Codebase discovery**: No source codebase provided. Analysis target is `architecture.md`, which describes component roles, data flows, and trust boundaries for a multi-agent AI application with 11 components across 3 trust zones (User Zone, Application Zone, External Services).

3. **Incremental scan scope**: 84 findings carried forward from baseline (2026-04-26T03-39-12) with control results unchanged. 4 NEW findings freshly analyzed: D-10, D-11 (Denial of Service → Rate Limiting category per FR-021 denial-of-service code path), LLM-15, LLM-16 (LLM Threats → Input Validation + Logging/Audit categories per FR-021 llm code path).

4. **Control detection for F-5 findings**: Architecture signals analyzed for D-10, D-11, LLM-15, LLM-16.
   - **D-10 / D-11 (Rate Limiting)**: No rate limiting, QPS throttling, token-count enforcement, or circuit breaker described in architecture for the LLM inference path. Classified as No Control Found. The Guardrails Service provides prompt content filtering (input validation), not inference-layer rate limiting — these are categorically distinct controls.
   - **LLM-15 / LLM-16 (LLM Threats → Logging/Audit)**: The Orchestrator emits Decision Log Entries to the Audit Logger (`architecture.md:47`). This architectural logging signal is the same evidence applying to other LLM-category findings on the Orchestrator component. Classified as Partial Control (same as LLM-1, LLM-4, LLM-2, LLM-7). No output-token cap, cost-per-query alerting, or per-tenant budget hard-cap is described in the architecture.

5. **Classification**: STRIDE-to-control-category mapping applied per the control-categories reference. 33 findings receive Partial Control; 55 receive No Control Found; 0 receive Control Found.

6. **Residual risk calculation**: `residual_score = composite_score × (1 − reduction_factor)`. D-10: 7.2 × 1.00 = 7.2 (High). D-11: 7.2 × 1.00 = 7.2 (High). LLM-15: 7.2 × 0.75 = 5.4 (Medium). LLM-16: 7.2 × 0.75 = 5.4 (Medium). All residual scores clamped to [0.0, 10.0] and rounded to 1 decimal place.

7. **Recommendations**: Generated for all 55 missing and 33 partial findings, sorted by composite score descending.

### Control Categories Assessed

| Category | Detection Result | Architectural Signal |
|----------|-----------------|---------------------|
| Authentication | No detection | No auth middleware, JWT, or session management described |
| Input Validation | Partial (Guardrails only) | Guardrails described as filtering/validating user prompts |
| Rate Limiting | No detection | No rate limiting, QPS throttle, or token-count enforcement described — D-10 and D-11 classified missing |
| Encryption | No detection | HTTPS transport described but no at-rest encryption or TLS config detail |
| Logging/Audit | Partial (5 components) | Explicit data flows to Audit Logger from 5 components; applied to LLM-15 and LLM-16 as partial |
| CSRF Protection | No detection | No CSRF mechanism described |
| CSP/Security Headers | No detection | No HTTP security headers described |
| Access Control | No detection | No RBAC, ABAC, or permission model described |

### Limitations

- **No source code available**: All control classifications are architectural inferences. Production analysis requires scanning implementation files. All partial detections should be treated as unverified assumptions pending code-level review.
- **Architecture signals are high-level**: The architecture describes intended behavior, not implemented behavior. A "Guardrails Service" may have stronger or weaker actual filtering than the architecture implies.
- **F-5 LLM10 findings require implementation-level review**: D-10, D-11, LLM-15, and LLM-16 represent unbounded-consumption vectors that require actual API gateway configuration review (rate limit policies, QPS thresholds, per-tenant budget settings) to confirm presence or absence of controls — architecture-level signals are insufficient to confirm these controls exist.
