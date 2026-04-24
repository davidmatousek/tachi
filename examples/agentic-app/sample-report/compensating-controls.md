---
schema_version: "1.0"
date: "2026-04-23"
source_file: "examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/risk-scores.md"
target_path: "examples/agentic-app"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Agentic AI Application (F-2 Wave 4)

## 1. Executive Summary

**83** threats analyzed | **0** Control Found | **3** Partial Control | **80** No Control Found

**Coverage**: 0% Found | 4% Partial | 96% Missing

**Risk Reduction**: 469.4 inherent -> 467.2 residual (**0.5%** reduction)

**Highest-Risk Unmitigated Finding**: S-1 — User — Composite 8.2 (High)

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-23 |
| Source file | `examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/risk-scores.md` |
| Target codebase | `examples/agentic-app` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0% |
| Partial Control | 3 | 4% |
| No Control Found | 80 | 96% |
| **Total** | **83** | **100%** |

> **Analysis Warning**: No target codebase files exist for this architecture-only sample. All control detection was performed at the architecture/DFD level using threat descriptions and component narrative. Three partial controls were inferred from architectural intent: (1) the Guardrails Service implies input validation/filtering for LLM threats on the Guardrails Service component; (2) the Audit Logger implies a logging/audit control for repudiation findings on the Audit Logger component; (3) TLS is referenced in threat S-8 as an existing baseline for the External API component. All other 80 findings receive "No Control Found" status because no implementation evidence can be sourced from a codebase. Evidence citations below reference DFD/architecture descriptions, not code files. The reduction is minimal (0.5%) because only 3 of 83 findings receive the partial reduction factor (0.25). This portfolio carries near-maximum inherent residual risk and requires urgent remediation.

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | false | User | An attacker impersonates a legitimate user by replaying stolen session tokens | 8.2 | High | No Control Found | 8.2 | High |
| AG-1 | false | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized actions | 7.8 | High | No Control Found | 7.8 | High |
| E-2 | false | LLM Agent Orchestrator | The Orchestrator has privileged access and can self-authorize elevated operations | 7.8 | High | No Control Found | 7.8 | High |
| R-3 | false | LLM Agent Orchestrator | The Orchestrator denies having issued a specific delegation message or tool call | 7.8 | High | No Control Found | 7.8 | High |
| E-1 | false | Guardrails Service | Prompt injection bypasses the Guardrails Service and elevates attacker privilege | 7.7 | High | No Control Found | 7.7 | High |
| LLM-6 | false | LLM Agent Orchestrator | Improper output handling — server-side execution via Tool Call Request | 7.7 | High | No Control Found | 7.7 | High |
| OI-2 | false | LLM Agent Orchestrator | Improper output handling — server-side execution via Tool Call Request (OI signal) | 7.7 | High | No Control Found | 7.7 | High |
| LLM-5 | false | LLM Agent Orchestrator | Improper output handling — client-side XSS via Orchestrator HTTPS response | 7.5 | High | No Control Found | 7.5 | High |
| OI-1 | false | LLM Agent Orchestrator | Improper output handling — client-side XSS via LLM response rendered in browser | 7.5 | High | No Control Found | 7.5 | High |
| LLM-13 | false | Clinical Advisory Sub-Agent | Prompt injection via clinical query context overrides sub-agent system prompt | 7.4 | High | No Control Found | 7.4 | High |
| LLM-8 | false | Specialist Agent | Prompt injection via delegation messages hijacks Specialist task execution | 7.3 | High | No Control Found | 7.3 | High |
| I-2 | false | LLM Agent Orchestrator | The Orchestrator's context window leaks sensitive data in HTTPS response to User | 7.2 | High | No Control Found | 7.2 | High |
| LLM-1 | false | LLM Agent Orchestrator | Direct prompt injection via User→Guardrails→Orchestrator chain causes Orchestrator override | 7.2 | High | No Control Found | 7.2 | High |
| LLM-4 | false | LLM Agent Orchestrator | Training data poisoning via Long-Running Learning Loop corrupts future Orchestrator behavior | 7.1 | High | No Control Found | 7.1 | High |
| T-2 | false | LLM Agent Orchestrator | The Orchestrator's context window tampered by upstream data source control | 7.1 | High | No Control Found | 7.1 | High |
| E-5 | false | MCP Tool Server | The MCP Tool Server executes tools with credentials accessible to unauthorized callers | 7.0 | High | No Control Found | 7.0 | High |
| T-5 | false | MCP Tool Server | Tool call request parameters tampered to invoke unintended tools | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| AG-5 | false | MCP Tool Server | MCP Tool Server vulnerable to tool call injection from compromised agent LLM output | 6.9 | Medium | No Control Found | 6.9 | Medium |
| E-7 | false | Clinical Advisory Sub-Agent | Clinical Advisory Sub-Agent prompt injection enables self-authorization of elevated access | 6.9 | Medium | No Control Found | 6.9 | Medium |
| I-9 | false | Clinical Advisory Sub-Agent | Clinical Advisory Sub-Agent clinical output leaks to unauthorized parties | 6.8 | Medium | No Control Found | 6.8 | Medium |
| LLM-2 | false | LLM Agent Orchestrator | Indirect prompt injection via Knowledge Base adversarial documents into Orchestrator context | 6.8 | Medium | No Control Found | 6.8 | Medium |
| D-1 | false | Guardrails Service | Guardrails Service vulnerable to resource exhaustion via high-volume prompt submission | 6.7 | Medium | No Control Found | 6.7 | Medium |
| LLM-7 | false | LLM Agent Orchestrator | Improper output handling — SSRF via LLM-synthesized URL to internal metadata endpoints | 6.6 | Medium | No Control Found | 6.6 | Medium |
| LLM-14 | false | Clinical Advisory Sub-Agent | Training data poisoning of Clinical Advisory Sub-Agent via Learning Loop | 6.6 | Medium | No Control Found | 6.6 | Medium |
| MI-2 | false | Clinical Advisory Sub-Agent | Overreliance / Missing HITL on decision-critical clinical output without physician sign-off | 6.6 | Medium | No Control Found | 6.6 | Medium |
| T-9 | false | Clinical Advisory Sub-Agent | Clinical Advisory Sub-Agent context window tampered via KB documents or query payload | 6.6 | Medium | No Control Found | 6.6 | Medium |
| LLM-10 | false | Specialist Agent | Improper output handling — server-side injection via tool call results chained to next call | 6.5 | Medium | No Control Found | 6.5 | Medium |
| MI-1 | false | Clinical Advisory Sub-Agent | Ungrounded factual emission — clinical summaries without mandatory RAG grounding | 6.5 | Medium | No Control Found | 6.5 | Medium |
| MI-3 | false | Clinical Advisory Sub-Agent | Retrieval-grounding gap — no mechanism to detect retrieval failures in Knowledge Base | 6.5 | Medium | No Control Found | 6.5 | Medium |
| OI-3 | false | LLM Agent Orchestrator | Improper output handling — SSRF via LLM-synthesized URL in Tool Call Request (OI signal) | 6.5 | Medium | No Control Found | 6.5 | Medium |
| E-3 | false | Specialist Agent | Specialist Agent receives forged delegation message granting elevated permissions | 6.4 | Medium | No Control Found | 6.4 | Medium |
| E-4 | false | Inter-Agent Communication Channel | Channel lacks sender authentication enabling privilege escalation via forged identity headers | 6.4 | Medium | No Control Found | 6.4 | Medium |
| S-5 | false | Inter-Agent Communication Channel | Channel shared message substrate enables impersonation of Orchestrator or Specialist | 6.4 | Medium | No Control Found | 6.4 | Medium |
| S-7 | false | Long-Running Learning Loop | Learning Loop accepts Training Signal Stream without integrity or authenticity verification | 6.4 | Medium | No Control Found | 6.4 | Medium |
| AG-3 | false | Specialist Agent | Specialist Agent executes holistically prohibited multi-step tool sequence autonomously | 6.2 | Medium | No Control Found | 6.2 | Medium |
| AG-6 | false | MCP Tool Server | Runaway agents cause MCP Tool Server to flood External API exhausting rate limits | 6.2 | Medium | No Control Found | 6.2 | Medium |
| D-2 | false | LLM Agent Orchestrator | Orchestrator inference pipeline exhausted by high-token prompts or recursive tool chains | 6.2 | Medium | No Control Found | 6.2 | Medium |
| D-5 | false | MCP Tool Server | Tool Server connection pool exhausted by high-volume tool call requests from compromised agent | 6.2 | Medium | No Control Found | 6.2 | Medium |
| OI-4 | false | Clinical Advisory Sub-Agent | Improper output handling — server-side execution via clinical output injected into Tool Call | 6.2 | Medium | No Control Found | 6.2 | Medium |
| R-1 | false | User | User denies having submitted a particular prompt — no request signing at User→Guardrails boundary | 6.2 | Medium | No Control Found | 6.2 | Medium |
| S-6 | false | MCP Tool Server | Application Zone attacker spoofs valid agent to submit unauthorized tool call requests | 6.2 | Medium | No Control Found | 6.2 | Medium |
| AG-2 | false | LLM Agent Orchestrator | Orchestrator and Specialist jointly coordinate to circumvent per-agent policies | 6.1 | Medium | No Control Found | 6.1 | Medium |
| AG-4 | false | Inter-Agent Communication Channel | Agent-in-the-middle intercepts and modifies delegation messages in channel | 6.0 | Medium | No Control Found | 6.0 | Medium |
| E-6 | false | Long-Running Learning Loop | Learning Loop model update mechanism compromised elevates to model-parameter control | 6.0 | Medium | No Control Found | 6.0 | Medium |
| I-1 | false | Guardrails Service | Guardrails Service leaks rejected prompt content in error responses enabling adaptive bypass | 5.6 | Medium | No Control Found | 5.6 | Medium |
| S-3 | false | LLM Agent Orchestrator | Orchestrator identity not cryptographically attested to Specialist via Inter-Agent Channel | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-3 | false | Specialist Agent | Specialist Agent operational context tampered via adversarial delegation message content | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-4 | false | Inter-Agent Communication Channel | Messages transiting Inter-Agent Channel modified in transit by process with queue access | 5.9 | Medium | No Control Found | 5.9 | Medium |
| S-8 | false | External API | External API provider identity not verified beyond TLS certificate validation | 5.8 | Medium | Partial Control | 4.4 | Medium |
| S-9 | false | Clinical Advisory Sub-Agent | Clinical Advisory Sub-Agent receives clinical queries without per-message sender attestation | 5.8 | Medium | No Control Found | 5.8 | Medium |
| T-7 | false | Audit Logger | Audit Logger entries tampered by process with write access to log store | 5.8 | Medium | No Control Found | 5.8 | Medium |
| AG-7 | false | Long-Running Learning Loop | Learning Loop fed adversarial training signals enabling gradual autonomy expansion | 5.6 | Medium | No Control Found | 5.6 | Medium |
| D-9 | false | Clinical Advisory Sub-Agent | High-volume clinical queries exhaust sub-agent inference and Knowledge Base query capacity | 5.6 | Medium | No Control Found | 5.6 | Medium |
| LLM-9 | false | Specialist Agent | Training data poisoning of Specialist Agent via self-poisoning audit log entries | 5.6 | Medium | No Control Found | 5.6 | Medium |
| D-6 | false | Knowledge Base | Knowledge Base unavailable via high-volume complex vector search queries | 5.7 | Medium | No Control Found | 5.7 | Medium |
| LLM-11 | false | Long-Running Learning Loop | Data poisoning of Learning Loop training signal via adversarial audit log entries | 5.7 | Medium | No Control Found | 5.7 | Medium |
| T-8 | false | Long-Running Learning Loop | Training signal stream from Audit Logger poisoned with sleeper-agent trigger injection | 5.7 | Medium | No Control Found | 5.7 | Medium |
| D-3 | false | Specialist Agent | Specialist Agent exhausted by computationally expensive adversarially crafted tasks | 5.5 | Medium | No Control Found | 5.5 | Medium |
| D-4 | false | Inter-Agent Communication Channel | Channel message queue flooded causing legitimate message drop and coordination disruption | 5.5 | Medium | No Control Found | 5.5 | Medium |
| D-7 | false | Audit Logger | Audit Logger overwhelmed by log-flooding attack from compromised Application Zone process | 5.5 | Medium | Partial Control | 4.1 | Medium |
| I-6 | false | Knowledge Base | Knowledge Base exposes full corpus to any process issuing vector search queries | 5.4 | Medium | No Control Found | 5.4 | Medium |
| I-7 | false | Audit Logger | Audit Logger aggregates sensitive data with unauthorized read access exposing full history | 5.4 | Medium | No Control Found | 5.4 | Medium |
| D-8 | false | Long-Running Learning Loop | Learning Loop enters runaway processing from high-volume training signal injection | 5.3 | Medium | No Control Found | 5.3 | Medium |
| I-5 | false | MCP Tool Server | Tool results containing PII logged verbatim to Audit Logger without redaction | 5.3 | Medium | No Control Found | 5.3 | Medium |
| LLM-3 | false | LLM Agent Orchestrator | Model theft via systematic API probing extracting model behavior and system prompt contents | 5.3 | Medium | No Control Found | 5.3 | Medium |
| LLM-12 | false | Long-Running Learning Loop | Model theft via Learning Loop output monitoring reconstructing model parameters | 5.3 | Medium | No Control Found | 5.3 | Medium |
| T-6 | false | Knowledge Base | Knowledge Base corpus tampered by attacker with write access injecting adversarial documents | 5.3 | Medium | No Control Found | 5.3 | Medium |
| R-9 | false | Clinical Advisory Sub-Agent | Clinical Advisory Sub-Agent denies having generated specific clinical summary | 5.2 | Medium | No Control Found | 5.2 | Medium |
| S-2 | false | Guardrails Service | Attacker spoofs Guardrails Service sending crafted requests to Orchestrator internal endpoint | 5.2 | Medium | No Control Found | 5.2 | Medium |
| I-4 | false | Inter-Agent Communication Channel | Inter-Agent Channel messages observable by any Application Zone process with bus access | 5.1 | Medium | No Control Found | 5.1 | Medium |
| R-8 | false | External API | External API provider denies having returned a specific response to MCP Tool Server | 5.0 | Medium | Partial Control | 3.8 | Low |
| T-1 | false | Guardrails Service | Attacker modifies Guardrails Service filtering rules via misconfigured admin endpoint | 5.0 | Medium | No Control Found | 5.0 | Medium |
| I-8 | false | Long-Running Learning Loop | Learning Loop memorizes sensitive training data reproducing PII in responses | 4.9 | Medium | No Control Found | 4.9 | Medium |
| R-7 | false | Long-Running Learning Loop | Learning Loop denies having applied specific model update or attributes update to different data | 4.9 | Medium | No Control Found | 4.9 | Medium |
| S-4 | false | Specialist Agent | Specialist Agent impersonates Orchestrator returning fabricated aggregated results | 4.9 | Medium | No Control Found | 4.9 | Medium |
| I-3 | false | Specialist Agent | Specialist Agent includes sensitive data verbatim in results returned via Inter-Agent Channel | 4.8 | Medium | No Control Found | 4.8 | Medium |
| R-2 | false | Guardrails Service | Guardrails Service denies having logged a filtering event without tamper-evident logs | 4.4 | Medium | No Control Found | 4.4 | Medium |
| R-4 | false | Specialist Agent | Specialist Agent denies having executed a tool call or produced specific result | 4.4 | Medium | No Control Found | 4.4 | Medium |
| R-6 | false | MCP Tool Server | MCP Tool Server denies having executed specific tool invocation without signed logs | 4.4 | Medium | No Control Found | 4.4 | Medium |
| R-5 | false | Inter-Agent Communication Channel | Channel denies having delivered or modified a specific message | 4.3 | Medium | No Control Found | 4.3 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| R-8 | false | External API | External API provider denies having returned a specific response to MCP Tool Server | 5.0 | Medium | Partial Control | 3.8 | Low |

> Note: R-8 appears in the Low band because its residual score (3.8) falls below the Medium threshold (4.0) after the 0.25 partial reduction factor is applied.

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 17 | 20% |
| Medium | 65 | 78% |
| Low | 1 | 1% |
| **Total** | **83** | **100%** |

---

## 3. Control Details

Per-control evidence showing detected security controls at the architecture level. Controls are inferred from the DFD component descriptions and threat narratives. No codebase implementation evidence is available.

### Encryption

#### CTRL-ENC-01 — TLS Certificate Validation on External API Outbound Channel

**Category**: Encryption | **Status**: partial | **Effectiveness**: moderate

**Detected in**: `examples/agentic-app/architecture.md` (DFD — S-8 threat narrative: "The External API provider's identity is not verified *beyond* TLS certificate validation")

```
Architecture-level inference: The threat description for S-8 states that
TLS certificate validation is performed on the External API outbound channel.
This implies TLS is present but certificate pinning and API response signing
are absent, making this a partial encryption control.
```

> Architecture-level evidence only — no codebase snippet available.

**Effectiveness Assessment**: Detailed effectiveness assessment available in P1 (User Story 6).

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| S-8 | External API | External API provider identity not verified beyond TLS cert validation | 5.8 | 0.25 | 4.4 |
| R-8 | External API | External API provider denies having returned a specific response | 5.0 | 0.25 | 3.8 |

---

### Logging/Audit

#### CTRL-LOG-01 — Audit Logger Component (Architecture-Level)

**Category**: Logging/Audit | **Status**: partial | **Effectiveness**: moderate

**Detected in**: `examples/agentic-app/architecture.md` (DFD — Audit Logger component processes log entries from all Application Zone components)

```
Architecture-level inference: The Audit Logger is a named architectural
component that aggregates security-relevant events from all Application
Zone components. However, it lacks tamper-evidence (Merkle/hash chain),
per-entry content hashing, and signed records — making it a partial
logging/audit control vulnerable to its own repudiation threats.
```

> Architecture-level evidence only — no codebase snippet available.

**Effectiveness Assessment**: Detailed effectiveness assessment available in P1 (User Story 6).

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| D-7 | Audit Logger | Audit Logger overwhelmed by log-flooding attack | 5.5 | 0.25 | 4.1 |

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control," sorted by composite risk score descending.

### Critical / High Risk Gaps

#### 1. S-1 — User (Composite: 8.2, High)

**Current Status**: No Control Found

**What to Implement**: Implement session token binding and short-lived JWT-based authentication at the User→Guardrails boundary. Bind tokens to client fingerprints (IP, device), enforce short expiry (15 min), implement server-side token revocation lists, and add replay detection via nonce or jti claim tracking. Add multi-factor authentication for high-privilege actions.

**Where to Implement**: `src/middleware/auth.ts` (authentication middleware at API gateway or Guardrails ingress) — add JWT verification with jti tracking and token binding headers.

**Reference Patterns**: `jsonwebtoken` + Redis nonce store for replay prevention; `express-jwt` with revocation middleware; OAuth 2.0 PKCE flow with short-lived access tokens; WebAuthn for MFA.

**Effort Estimate**: High — redesigning the authentication boundary from session-based to cryptographically bound tokens requires architectural changes to the User→Guardrails→Orchestrator entry path.

---

#### 2. AG-1 — LLM Agent Orchestrator (Composite: 7.8, High)

**Current Status**: No Control Found

**What to Implement**: Implement a human-in-the-loop (HITL) confirmation gate for high-impact autonomous actions (mass data access, bulk tool invocations, delegation beyond defined scope). Add a structured action authorization layer that intercepts Orchestrator-originated actions before execution and requires explicit approval for actions exceeding a defined risk threshold. Combine with prompt injection defenses (instruction hierarchy, delimited context blocks, output structured parsing rather than free-form tool dispatch).

**Where to Implement**: `src/orchestrator/action-gate.ts` — insert between Orchestrator reasoning output and tool/delegation dispatch. Define a risk-scored action catalog with per-action authorization requirements.

**Reference Patterns**: OWASP LLM04 mitigations; structured output parsing with JSON schema enforcement on tool call parameters; action allowlisting with RBAC; LangChain `tools` with `human_as_tool` confirmation step.

**Effort Estimate**: High — requires architecting an authorization layer across all Orchestrator action paths; must not introduce latency for low-risk actions while blocking high-risk ones.

---

#### 3. E-2 — LLM Agent Orchestrator (Composite: 7.8, High)

**Current Status**: No Control Found

**What to Implement**: Implement least-privilege access control for the Orchestrator by scoping its permissions to the minimum required for each user session. The Orchestrator should not hold blanket access to the full Knowledge Base corpus, all MCP tools, and unlimited delegation authority simultaneously. Implement per-session permission scoping, tool-call allowlists derived from the authenticated user's role, and delegated permission certificates that expire with the session.

**Where to Implement**: `src/orchestrator/permission-scope.ts` — add a permission scope resolver that derives the Orchestrator's allowable actions from the authenticated user's session context. Tool call dispatch should validate against session-scoped allowlists.

**Reference Patterns**: Principle of least privilege via RBAC session scoping; OAuth 2.0 scoped access tokens for tool authorization; `casl` or `casbin` for dynamic permission evaluation per request context.

**Effort Estimate**: High — requires re-architecting the Orchestrator's access model from ambient authority to request-scoped minimal authority.

---

#### 4. R-3 — LLM Agent Orchestrator (Composite: 7.8, High)

**Current Status**: No Control Found

**What to Implement**: Implement per-action structured logging with content hashes for all Orchestrator-originated actions: delegation messages, tool call requests, KB retrieval queries, and user responses. Each log entry must include the action type, parameters, a SHA-256 hash of the message content, and a chain pointer to the previous log entry (Merkle/hash chain) to achieve tamper-evident non-repudiation. Store logs in an append-only, write-once store.

**Where to Implement**: `src/audit/action-logger.ts` — add Orchestrator action event emission with content hashing before dispatch to the Audit Logger. Use a structured event schema: `{action_id, type, params_hash, timestamp, session_id, chain_hash}`.

**Reference Patterns**: `winston` with custom transport writing to an append-only store; AWS CloudWatch Logs with log integrity validation; WORM (write-once read-many) log storage; Merkle tree log integrity as used in Certificate Transparency.

**Effort Estimate**: High — content hashing and Merkle-chain logging requires coordination across all Orchestrator action emission points and a new append-only log infrastructure.

---

#### 5. E-1 — Guardrails Service (Composite: 7.7, High)

**Current Status**: No Control Found

**What to Implement**: Harden the Guardrails Service against prompt injection bypass by implementing multi-layer detection: (1) lexical pattern matching for known injection signatures, (2) a secondary classifier that evaluates the semantic intent of the prompt against allowable task types, (3) structured output enforcement that validates the Orchestrator's response schema before returning to the user. The Guardrails Service should treat any ambiguous classification as a rejection rather than a pass-through.

**Where to Implement**: `src/guardrails/classifier.ts` — add a two-stage pipeline: lexical filter → semantic intent classifier → schema validator. Implement fail-closed logic (reject on ambiguity).

**Reference Patterns**: Meta's Llama Guard for intent classification; Rebuff prompt injection detector; output schema enforcement via Zod/JSON Schema; Microsoft's PyRIT adversarial prompt testing framework for regression testing.

**Effort Estimate**: High — building a robust multi-layer Guardrails pipeline with semantic classification requires significant ML infrastructure and ongoing red-team testing.

---

#### 6. LLM-6 — LLM Agent Orchestrator (Composite: 7.7, High)

**Current Status**: No Control Found

**What to Implement**: Implement strict parameterized tool call dispatch at the MCP Tool Server — all JSON-RPC parameters synthesized from LLM output must be validated against a per-tool schema before execution. SQL queries must use parameterized queries exclusively. Shell invocations must use allowlisted command patterns with no string interpolation. Template expressions must be evaluated in a sandboxed context with no access to system variables.

**Where to Implement**: `src/mcp/tool-dispatcher.ts` — add schema-validated parameter ingestion for each registered tool. Define a tool manifest with JSON Schema parameter definitions; reject calls with parameters failing schema validation.

**Reference Patterns**: JSON-RPC parameter schema validation with Ajv; parameterized DB queries via Prisma ORM; command allowlisting via shell escaping + `child_process.execFile` (not `exec`); OWASP LLM05 output handling controls.

**Effort Estimate**: High — requires defining per-tool parameter schemas for all MCP tools and retrofitting the tool dispatcher to enforce them before execution.

---

#### 7. OI-2 — LLM Agent Orchestrator (Composite: 7.7, High)

**Current Status**: No Control Found

**What to Implement**: Implement the same parameterized tool call dispatch as LLM-6 (these findings share the same attack class). Additionally, add output sanitization at the Orchestrator→MCP boundary: before any LLM-synthesized content is forwarded as a tool parameter, strip SQL metacharacters, shell metacharacters, template expression delimiters, and path traversal sequences. Use an allowlist of permitted parameter value patterns per tool type.

**Where to Implement**: `src/orchestrator/output-sanitizer.ts` — apply output sanitization middleware between the Orchestrator's reasoning output and tool call dispatch. Chain with the schema validator from LLM-6 remediation.

**Reference Patterns**: `sanitize-html` for content sanitization; SQL parameterization via ORM; OWASP LLM05 parameterized output controls; structured output parsing with JSON Schema `additionalProperties: false`.

**Effort Estimate**: Medium — if LLM-6 schema enforcement is implemented, this hardening adds an incremental sanitization layer on top of existing schema validation.

---

#### 8. LLM-5 — LLM Agent Orchestrator (Composite: 7.5, High)

**Current Status**: No Control Found

**What to Implement**: Implement Content Security Policy (CSP) headers on all Orchestrator HTTPS responses to the User, and enforce contextual HTML encoding of LLM-generated content before DOM injection. The frontend rendering layer must never use `innerHTML` or equivalent with raw LLM output — use `textContent` or a sanitization library. Add a CSP header that blocks inline script execution and restricts script sources to trusted CDNs.

**Where to Implement**: `src/middleware/csp.ts` — add security headers middleware with a restrictive CSP. Frontend rendering: replace all `innerHTML` assignments with `DOMPurify.sanitize()` or `textContent`.

**Reference Patterns**: `helmet` with `contentSecurityPolicy` directive; `DOMPurify` for client-side HTML sanitization; `sanitize-html` for server-side output scrubbing; OWASP XSS Prevention Cheat Sheet.

**Effort Estimate**: Medium — CSP headers require middleware configuration; DOM injection fixes require auditing all frontend rendering paths that display LLM output.

---

#### 9. OI-1 — LLM Agent Orchestrator (Composite: 7.5, High)

**Current Status**: No Control Found

**What to Implement**: Same XSS mitigation as LLM-5: enforce contextual output encoding and CSP headers. Additionally, add server-side output scrubbing in the Orchestrator's response path — strip HTML tags and script content from LLM output before including it in the HTTPS response body. This defense-in-depth approach protects against XSS even if the client-side rendering layer fails to properly encode content.

**Where to Implement**: `src/orchestrator/response-sanitizer.ts` — add server-side output scrubbing before writing the LLM response to the HTTPS response body. Chain with the CSP middleware from LLM-5 remediation.

**Reference Patterns**: `sanitize-html` with whitelist of permitted tags; `DOMPurify` with `FORCE_BODY`; OWASP LLM05 output handling; Content-Type enforcement (`text/plain` for non-HTML LLM responses).

**Effort Estimate**: Medium — server-side scrubbing is an incremental addition if LLM-5 CSP middleware is already implemented; the main work is auditing all Orchestrator response paths.

---

#### 10. LLM-13 — Clinical Advisory Sub-Agent (Composite: 7.4, High)

**Current Status**: No Control Found

**What to Implement**: Implement input validation and content inspection on all Clinical Query / Context payloads entering the Clinical Advisory Sub-Agent. Apply a secondary Guardrails classifier specifically tuned for clinical injection patterns. Enforce a structured clinical query schema (patient ID, query type, context boundaries) that prevents free-form adversarial text from reaching the sub-agent's system prompt context. Implement context isolation between the system prompt and user-provided clinical context.

**Where to Implement**: `src/clinical-advisor/input-validator.ts` — add a clinical-specific input validation layer before the sub-agent receives the Clinical Query / Context payload. Define a JSON Schema for permissible clinical query structure.

**Reference Patterns**: Llama Guard for clinical intent classification; JSON Schema validation with Ajv; prompt structuring with XML/YAML delimiters for context isolation; OWASP LLM01 prompt injection mitigations.

**Effort Estimate**: High — clinical-specific injection defense requires domain expertise to define valid query schemas and classifier training data.

---

#### 11. LLM-8 — Specialist Agent (Composite: 7.3, High)

**Current Status**: No Control Found

**What to Implement**: Implement cryptographic message authentication on delegation messages transiting the Inter-Agent Communication Channel to the Specialist Agent. The Orchestrator must sign each delegation message with an HMAC or asymmetric signature using a per-session key. The Specialist Agent must verify the signature before processing the delegation. Reject delegation messages with invalid signatures.

**Where to Implement**: `src/inter-agent/message-auth.ts` — add HMAC-SHA256 signing at delegation message emission (Orchestrator side) and signature verification at delegation message receipt (Specialist side). Use a per-session ephemeral key derived from the authenticated user session.

**Reference Patterns**: HMAC-SHA256 with `crypto.createHmac`; asymmetric signing via `tweetnacl` or `libsodium`; JWT for delegation message envelopes with short expiry; OWASP API9:2023 Improper Inventory Management mitigations.

**Effort Estimate**: High — requires introducing a cryptographic signing infrastructure to the Inter-Agent Communication Channel affecting all delegation message flows.

---

#### 12. I-2 — LLM Agent Orchestrator (Composite: 7.2, High)

**Current Status**: No Control Found

**What to Implement**: Implement context window scrubbing before the Orchestrator's response is returned to the User. Before emitting the HTTPS response, strip all system prompt content, KB document excerpts, tool results, and internal metadata from the LLM output. Use a structured output format for the Orchestrator's user-facing responses that has a defined schema of permissible fields, rejecting any response content outside that schema.

**Where to Implement**: `src/orchestrator/context-scrubber.ts` — add a post-processing step that applies a content allowlist to the Orchestrator's final response before writing to the HTTPS response body. Define sentinel tokens or response envelope schemas that prevent context leakage.

**Reference Patterns**: Structured output mode (OpenAI `response_format: json_schema`); output schema validation with Zod; content classification to detect system context in outputs; OWASP LLM06 sensitive information disclosure mitigations.

**Effort Estimate**: High — context scrubbing requires understanding the full range of Orchestrator output patterns and may require model-level structured output enforcement to be reliable.

---

#### 13. LLM-1 — LLM Agent Orchestrator (Composite: 7.2, High)

**Current Status**: No Control Found

**What to Implement**: Strengthen the Guardrails Service against direct prompt injection by implementing an adversarial prompt detection pipeline that evaluates the User's prompt before forwarding it to the Orchestrator. Use a combination of lexical filtering, semantic classification, and structural analysis to detect instruction-override patterns. Apply fail-closed logic. Correlate with LLM-5/OI-1 and E-1 remediations as this finding shares the same injection attack surface.

**Where to Implement**: `src/guardrails/prompt-detector.ts` — add adversarial injection detection to the Guardrails pipeline. This extends the E-1 multi-layer classifier recommendation with a specific focus on instruction-override patterns targeting the Orchestrator.

**Reference Patterns**: Same as E-1: Llama Guard, Rebuff, PyRIT; additionally consider Anthropic's constitutional AI approach for instruction hierarchy enforcement at the Orchestrator system prompt level.

**Effort Estimate**: Medium — if E-1 Guardrails hardening is implemented, this finding is addressed by the same remediation with additional Orchestrator-specific instruction hierarchy tuning.

---

#### 14. LLM-4 — LLM Agent Orchestrator (Composite: 7.1, High)

**Current Status**: No Control Found

**What to Implement**: Implement training data validation and provenance tracking for the Learning Loop's training signal stream. Before incorporating audit log entries into the training dataset, apply adversarial training sample detection (statistical anomaly detection, out-of-distribution detection, data validation against expected interaction schemas). Require cryptographic provenance for all training samples (each audit log entry signed by the emitting component).

**Where to Implement**: `src/learning-loop/training-validator.ts` — add a validation gate that applies anomaly detection and schema validation to each audit log entry before inclusion in the training dataset. Integrate with the content-hashed audit logging recommended in R-3.

**Reference Patterns**: PyTorch data validation hooks; `cleanlab` for noisy label detection; MITRE ATLAS AML.M0007 training data filtering; differential privacy via `opacus`; data provenance with SLSA framework concepts.

**Effort Estimate**: High — training data validation requires ML-specific tooling and integration with the Learning Loop's data ingestion pipeline.

---

#### 15. T-2 — LLM Agent Orchestrator (Composite: 7.1, High)

**Current Status**: No Control Found

**What to Implement**: Implement integrity verification for all data sources that populate the Orchestrator's context window. Knowledge Base documents must carry cryptographic signatures from the document ingestion system. Tool call results must be schema-validated against expected result shapes. The Orchestrator must reject context contributions from sources that fail signature or schema verification. Treat context window integrity as a security boundary.

**Where to Implement**: `src/orchestrator/context-verifier.ts` — add a context assembly validation step that verifies document signatures and result schemas before populating the context window. Add KB document signing at ingestion time.

**Reference Patterns**: Content-addressable document storage with IPFS-style hashing; JSON Schema validation for tool results; digital signatures on KB documents using `tweetnacl` or AWS KMS signing; OWASP LLM02 insecure output handling controls.

**Effort Estimate**: High — requires implementing a document signing infrastructure at the Knowledge Base ingestion layer and adding signature verification to the Orchestrator's context assembly pipeline.

---

#### 16. E-5 — MCP Tool Server (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement caller authentication on the MCP Tool Server so that only the authorized Orchestrator and Specialist Agent can invoke tools. Use mutual TLS (mTLS) between agents and the Tool Server, with per-agent client certificates. Additionally, implement per-session credential scoping — the Tool Server must derive the External API credentials to use from the authenticated caller's session scope, not from a shared ambient credential store.

**Where to Implement**: `src/mcp/caller-authenticator.ts` — add mTLS client certificate validation at the Tool Server's JSON-RPC ingress. Implement a credential resolver that maps authenticated caller identity to a minimal set of permitted external API scopes.

**Reference Patterns**: mTLS with `node:tls` and client certificate validation; SPIFFE/SPIRE for workload identity in agent meshes; OAuth 2.0 token exchange for per-session credential derivation; HashiCorp Vault dynamic secrets for external API credential scoping.

**Effort Estimate**: High — implementing mTLS and per-session credential scoping requires infrastructure changes to the agent communication layer and credential management system.

---

#### 17. T-5 — MCP Tool Server (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement strict JSON-RPC parameter allowlisting at the MCP Tool Server. Define a per-tool manifest that specifies: (1) permitted tool names (reject any call to a tool not in the manifest), (2) JSON Schema for each tool's parameters with `additionalProperties: false`, (3) per-parameter value constraints (regex patterns, enum lists, numeric ranges). Validate every incoming tool call against this manifest before dispatch.

**Where to Implement**: `src/mcp/parameter-validator.ts` — add a pre-dispatch validation middleware that loads the tool manifest and validates each JSON-RPC call against per-tool schemas. Return a structured error for any validation failure.

**Reference Patterns**: Ajv for JSON Schema validation; `zod` for TypeScript-native parameter schema definition; JSON-RPC 2.0 `params` validation; OWASP LLM05 output handling with tool call parameterization.

**Effort Estimate**: Medium — defining tool manifests requires documenting all permitted tool signatures; the validation middleware itself is a straightforward schema enforcement layer.

---

### Medium Risk Gaps

#### 18. AG-5 — MCP Tool Server (Composite: 6.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement tool name allowlisting (separate from T-5 parameter allowlisting) to prevent tool name injection. The Tool Server must maintain a static, configuration-managed manifest of permitted tool names. Any JSON-RPC call requesting a tool not in the manifest is rejected before parameter parsing. Combine with E-5 caller authentication to ensure only authenticated agents can invoke any tool.

**Where to Implement**: `src/mcp/tool-manifest.ts` — define and enforce a static tool registry; validate `method` field against registry before processing `params`.

**Reference Patterns**: Same as T-5 (tool manifest validation); MCP protocol tool registration spec; server-side function dispatch tables with strict allowlisting.

**Effort Estimate**: Low — if the T-5 tool manifest infrastructure is implemented, tool name allowlisting is an incremental addition to the same registry enforcement.

---

#### 19. E-7 — Clinical Advisory Sub-Agent (Composite: 6.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement least-privilege access control for the Clinical Advisory Sub-Agent. The sub-agent must not have ambient access to the full Knowledge Base — restrict it to clinical-specific KB namespaces. Its outputs must be treated as untrusted by the Orchestrator — the Orchestrator must not execute tool calls whose parameters are derived directly from clinical sub-agent output without sanitization. Implement a clinical output validator that strips injection-capable content from clinical summaries before they reach the Orchestrator's tool dispatch layer.

**Where to Implement**: `src/clinical-advisor/output-validator.ts` — add output validation/sanitization before clinical summaries are returned to the Orchestrator. `src/orchestrator/clinical-output-handler.ts` — treat clinical sub-agent output as untrusted input requiring sanitization before tool parameter use.

**Reference Patterns**: Data minimization via KB namespace scoping; output sanitization with `sanitize-html`; sandboxed sub-agent output processing; OWASP LLM08 excessive agency mitigations.

**Effort Estimate**: Medium — KB namespace scoping requires configuration changes; output sanitization is a new middleware component in the Orchestrator's clinical response handling path.

---

#### 20. I-9 — Clinical Advisory Sub-Agent (Composite: 6.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement output scrubbing on Clinical Advisory Sub-Agent outputs before inclusion in the Orchestrator's HTTPS response to the User. Apply field-level classification to the Clinical Summary + Recommendations output — identify and strip or redact clinical PII fields (patient identifiers, specific medical record references) before the output reaches the user-facing response path. Implement separate data classification for Clinical Decision Log Entries before they are written to the Audit Logger.

**Where to Implement**: `src/clinical-advisor/output-scrubber.ts` — add PII field classification and redaction to clinical output before return to Orchestrator. `src/audit/clinical-log-classifier.ts` — classify and redact sensitive clinical fields before writing to the Audit Logger.

**Reference Patterns**: Microsoft Presidio for PII detection and redaction; AWS Comprehend Medical for clinical PII identification; data classification schemas following HIPAA minimum necessary standard.

**Effort Estimate**: High — clinical PII detection and redaction requires domain-specific configuration of PII detectors and healthcare data classification policies.

---

#### 21. LLM-2 — LLM Agent Orchestrator (Composite: 6.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement document integrity verification and adversarial content detection in the Knowledge Base ingestion pipeline. Before a document is added to the KB, scan it for prompt injection markers, instruction-override patterns, and adversarial ML content. Sign each approved document at ingestion time. At retrieval time, the Orchestrator must verify document signatures before incorporating retrieved content into its context window.

**Where to Implement**: `src/knowledge-base/ingestion-validator.ts` — add injection pattern detection and signing at document ingestion. Extend with context assembly signature verification per the T-2 remediation.

**Reference Patterns**: Rebuff indirect injection detection; semantic similarity checks against known adversarial prompts; IPFS-style content addressing for document integrity; OWASP LLM02 indirect prompt injection mitigations.

**Effort Estimate**: High — requires building a KB ingestion validation pipeline with adversarial content detection and a document signing infrastructure.

---

#### 22. D-1 — Guardrails Service (Composite: 6.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting at the Guardrails Service ingress to prevent resource exhaustion from high-volume prompt submission. Configure per-user and per-IP rate limits with an exponential backoff penalty for burst traffic. Add circuit breaker logic that fails fast when the Guardrails Service is under excessive load, returning a 429 response rather than processing expensive prompts under pressure.

**Where to Implement**: `src/guardrails/rate-limiter.ts` — add rate limiting middleware at the Guardrails Service entry point before prompt processing. Configure: `windowMs: 60000, max: 20` requests per minute per authenticated user; `max: 5` for unauthenticated requests.

**Reference Patterns**: `express-rate-limit` with Redis store for distributed rate limiting; `rate-limiter-flexible` for fine-grained control; `opossum` circuit breaker for the Guardrails processing pipeline; token-bucket algorithm for burst tolerance.

**Effort Estimate**: Medium — rate limiting middleware is a well-understood pattern; the main design decision is configuring appropriate thresholds for legitimate clinical and general query use.

---

#### 23. LLM-7 — LLM Agent Orchestrator (Composite: 6.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement URL allowlisting for all URLs synthesized by the Orchestrator's LLM output and forwarded to the MCP Tool Server as fetch parameters. Maintain a static allowlist of permitted external domains and URL prefixes. Reject any Tool Call Request containing a URL that does not match the allowlist. Additionally, block all internal network ranges (RFC 1918, 169.254.0.0/16 link-local, loopback) from the Tool Server's outbound HTTP client configuration.

**Where to Implement**: `src/mcp/url-validator.ts` — add URL allowlist validation in the tool dispatcher before executing any URL-fetching tool call. `src/mcp/http-client.ts` — configure the outbound HTTP client to block private/internal IP ranges.

**Reference Patterns**: URL allowlist with `URL` API + domain pattern matching; `ssrf-req-filter` npm package for blocking internal IPs; OWASP SSRF prevention cheat sheet; AWS metadata service IMDSv2 requirement.

**Effort Estimate**: Medium — URL allowlisting is straightforward configuration; blocking internal IP ranges requires modifying the Tool Server's outbound HTTP client configuration.

---

#### 24. LLM-14 — Clinical Advisory Sub-Agent (Composite: 6.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement training data isolation for the Clinical Advisory Sub-Agent's contribution to the Learning Loop's training signal. Clinical Decision Log Entries must be segregated from the main training stream and subject to additional validation (clinical domain expert review, anomaly detection against expected clinical decision patterns) before being incorporated into training data. Implement differential privacy noise injection for clinical training samples.

**Where to Implement**: `src/learning-loop/clinical-data-pipeline.ts` — add a separate validation stage for Clinical Decision Log Entries before inclusion in the training dataset. Apply the same training validator as recommended in LLM-4, with additional clinical-specific anomaly detection.

**Reference Patterns**: Differential privacy via `opacus` (PyTorch); domain expert review workflow integration; clinical training data schemas with mandatory field validation; MITRE ATLAS AML.M0007 data sanitization.

**Effort Estimate**: High — requires clinical domain expertise for anomaly detection configuration and differential privacy calibration for clinical training data.

---

#### 25. MI-2 — Clinical Advisory Sub-Agent (Composite: 6.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement a mandatory human-in-the-loop (HITL) review gate for all Clinical Advisory Sub-Agent outputs before they are included in the Orchestrator's user-facing response. Clinical recommendations must be routed to a physician or qualified clinical reviewer before delivery to the end consumer. Implement a workflow where the Orchestrator holds the clinical output pending HITL approval, surfacing an interim response to the user ("Clinical recommendations are under physician review") while the approval is pending.

**Where to Implement**: `src/orchestrator/hitl-gate.ts` — add a HITL workflow intercept in the Orchestrator's response path that detects clinical recommendation content and routes it to a physician review queue before releasing to the user.

**Reference Patterns**: Task queue (BullMQ, Celery) for async HITL review workflows; physician notification via webhook + approval token; EU AI Act Article 14 HITL requirements for high-risk AI; FDA Software as Medical Device (SaMD) oversight requirements.

**Effort Estimate**: High — HITL gate requires building an asynchronous review workflow system with physician notification, approval, and response release infrastructure — a significant architectural addition.

---

#### 26. T-9 — Clinical Advisory Sub-Agent (Composite: 6.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement integrity verification for Clinical Query / Context payloads from the Orchestrator: the Orchestrator must sign each clinical query before dispatching it to the sub-agent (HMAC or asymmetric signature), and the sub-agent must verify the signature before processing. Additionally, implement document integrity verification for KB retrievals per the LLM-2 remediation — the sub-agent must only incorporate documents with valid KB ingestion signatures into its context.

**Where to Implement**: `src/clinical-advisor/query-authenticator.ts` — add signature verification for incoming Clinical Query / Context messages. Extend with KB document signature verification per LLM-2 remediation.

**Reference Patterns**: Same as LLM-8 inter-agent message authentication; HMAC-SHA256 per-message signing; JSON Web Signatures (JWS) for clinical query envelopes.

**Effort Estimate**: Medium — if inter-agent message authentication (LLM-8 remediation) is implemented, this finding is addressed by extending the same signing infrastructure to the Orchestrator→ClinicalAdvisor channel.

---

#### 27. LLM-10 — Specialist Agent (Composite: 6.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement tool result validation and sanitization before the Specialist Agent incorporates tool results into its context for subsequent tool calls. Tool results from the MCP Tool Server must be validated against the expected result schema for that tool (defined in the tool manifest from T-5 remediation) before being used as input to the next tool call. Strip injection-capable content from tool results before incorporating them into the agent context.

**Where to Implement**: `src/specialist/tool-result-validator.ts` — add tool result schema validation and sanitization between tool call response receipt and context incorporation.

**Reference Patterns**: Same tool manifest schema validation as T-5; `sanitize-html` for stripping injection content from tool results; JSON Schema `additionalProperties: false` for tool result schema enforcement.

**Effort Estimate**: Medium — if the tool manifest infrastructure from T-5 is implemented, this requires adding a parallel result validation step using the same schemas.

---

#### 28. MI-1 — Clinical Advisory Sub-Agent (Composite: 6.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement mandatory RAG grounding verification before the Clinical Advisory Sub-Agent emits clinical summaries. For every factual claim in the clinical output, require a minimum retrieval strength score (e.g., cosine similarity >= 0.75) from at least one retrieved KB document. Claims without sufficient retrieval support must be flagged as ungrounded and either suppressed or explicitly marked as requiring physician review. Implement per-claim source anchoring in the output metadata.

**Where to Implement**: `src/clinical-advisor/grounding-verifier.ts` — add a post-generation verification step that maps each factual claim to retrieved documents via citation linking, calculates retrieval strength scores, and flags ungrounded claims.

**Reference Patterns**: RAG attribution scoring with sentence transformers; RAGAS evaluation framework for retrieval grounding assessment; per-claim citation metadata in structured clinical output; MITRE ATLAS AML.T0042 mitigations.

**Effort Estimate**: High — per-claim grounding verification requires NLP claim extraction, citation linking, and retrieval strength assessment — significant ML engineering work.

---

#### 29. MI-3 — Clinical Advisory Sub-Agent (Composite: 6.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement retrieval failure detection in the Clinical Advisory Sub-Agent's KB retrieval pipeline. When a vector search returns fewer than a minimum number of results above a relevance threshold, the sub-agent must not proceed to generate a clinical summary — instead, it must return a structured "insufficient knowledge base coverage" response that is escalated to a physician reviewer. Implement KB coverage monitoring to detect systematic staleness.

**Where to Implement**: `src/clinical-advisor/retrieval-guard.ts` — add a retrieval quality gate that checks result count and minimum similarity score before passing retrieved documents to the sub-agent. Define: `min_results: 3, min_similarity: 0.70`.

**Reference Patterns**: Vector similarity threshold enforcement in retrieval pipeline; LlamaIndex retrieval quality callbacks; out-of-distribution detection for clinical queries; KB staleness monitoring via document age metrics.

**Effort Estimate**: Medium — retrieval quality gating is a configuration-level addition to the existing KB retrieval pipeline; the main work is defining appropriate thresholds for the clinical domain.

---

#### 30. OI-3 — LLM Agent Orchestrator (Composite: 6.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Same as LLM-7 (URL allowlisting and internal IP blocking). OI-3 is the output-integrity signal-class finding for the same SSRF via LLM-synthesized URL threat. Implement the URL allowlist validator and internal IP range blocking per the LLM-7 remediation. Both findings are addressed by the same `src/mcp/url-validator.ts` implementation.

**Where to Implement**: `src/mcp/url-validator.ts` — same implementation as LLM-7 remediation. No additional work required beyond LLM-7 remediation.

**Reference Patterns**: Same as LLM-7.

**Effort Estimate**: Low — if LLM-7 remediation is implemented, OI-3 is addressed by the same change with no additional effort.

---

#### 31. E-3 — Specialist Agent (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement delegation message authentication and scope validation on the Specialist Agent side. The Specialist must verify that each delegation message carries a valid Orchestrator signature (per LLM-8 remediation) and that the delegated permissions in the message are within the bounds of the authenticated user's session scope. Reject delegation messages that attempt to grant permissions exceeding the user's authorized scope.

**Where to Implement**: `src/specialist/delegation-validator.ts` — add signature verification and scope boundary checking for all received delegation messages. Define a permission scope model that bounds permissible delegations.

**Reference Patterns**: Same inter-agent message authentication as LLM-8; permission scope validation via `casbin`; OAuth 2.0 Token Exchange (RFC 8693) for delegation scope validation.

**Effort Estimate**: Medium — extends the LLM-8 message authentication remediation with scope boundary validation logic on the Specialist side.

---

#### 32. E-4 — Inter-Agent Communication Channel (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement sender authentication on the Inter-Agent Communication Channel. All messages entering the channel must carry a cryptographic sender identity attestation (HMAC or asymmetric signature with a per-component identity key). The channel infrastructure must validate sender attestations before routing messages. Reject messages with missing or invalid sender attestations.

**Where to Implement**: `src/inter-agent/sender-authenticator.ts` — add sender attestation validation at the channel ingress. Assign per-component signing keys (Orchestrator, Specialist, ClinicalAdvisor) managed via a key management service.

**Reference Patterns**: SPIFFE/SPIRE for workload identity and mTLS; per-component HMAC signing with shared key per authorized sender; message signing with `node:crypto` using ECDSA per-component identity keys.

**Effort Estimate**: High — requires introducing a workload identity infrastructure for all Application Zone components and updating all message emission points to include attestations.

---

#### 33. S-5 — Inter-Agent Communication Channel (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement sender authentication on the Inter-Agent Communication Channel (same root cause as E-4). The absence of sender authentication enables S-5 impersonation. Implementing the E-4 remediation (channel sender authentication with per-component signing keys) directly addresses S-5. Additionally, implement message sequence numbers and delivery receipts to detect message injection that disrupts expected communication sequences.

**Where to Implement**: Same as E-4 — `src/inter-agent/sender-authenticator.ts`. Add sequence number tracking in `src/inter-agent/message-sequencer.ts`.

**Reference Patterns**: Same as E-4; additionally: ordered message delivery with sequence numbers; Redis-backed message sequence tracking for detection of injection gaps.

**Effort Estimate**: Low — if E-4 sender authentication is implemented, S-5 is addressed by the same change. Sequence number tracking is an incremental addition.

---

#### 34. S-7 — Long-Running Learning Loop (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement Training Signal Stream authentication on the Learning Loop's data ingestion interface. The Learning Loop must verify that the Training Signal Stream originates from the authenticated Audit Logger component (using the Audit Logger's component signing key) and that each training sample carries a valid content hash signed by the emitting component. Reject training data from unauthenticated sources.

**Where to Implement**: `src/learning-loop/stream-authenticator.ts` — add source authentication and per-sample signature verification at the Learning Loop's training data ingestion. Extend with the content-hashed audit logging from R-3 remediation.

**Reference Patterns**: Same inter-component authentication as E-4; SLSA supply chain integrity framework for training data provenance; content-addressed training sample storage.

**Effort Estimate**: High — requires implementing source authentication for the training data pipeline, coordinating with Audit Logger signing infrastructure from R-3 remediation.

---

#### 35. AG-3 — Specialist Agent (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement a step-by-step action authorization gate for the Specialist Agent's autonomous tool call sequences. The Specialist must pause at configurable checkpoints during multi-step tool sequences and verify that the accumulated action history remains within the bounds of the original delegation scope. Implement holistic action sequence evaluation — detect when a sequence of individually-permitted actions produces a prohibited composite outcome.

**Where to Implement**: `src/specialist/action-sequence-auditor.ts` — add an action sequence monitoring component that tracks cumulative tool invocations against delegation scope bounds and triggers HITL review when sequences approach policy boundaries.

**Reference Patterns**: Finite state machine for permitted action sequences; OWASP LLM08 excessive agency mitigations; reinforcement learning from human feedback (RLHF) to train scope-aware agent behavior; step-level authorization callbacks in LangGraph.

**Effort Estimate**: High — holistic multi-step action sequence authorization requires significant agentic framework changes and policy definition for the permitted action space.

---

#### 36. AG-6 — MCP Tool Server (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement per-agent rate limiting on the MCP Tool Server to prevent runaway agents from flooding External API endpoints. Configure per-authenticated-caller rate limits on tool invocations (e.g., 100 tool calls/minute per agent session). Add circuit breakers on External API outbound connections that open after 5 consecutive failures or 80% error rate. Implement a per-tool concurrency limit to bound concurrent External API calls.

**Where to Implement**: `src/mcp/rate-limiter.ts` — add per-caller rate limiting middleware at the Tool Server's JSON-RPC ingress. `src/mcp/external-api-circuit-breaker.ts` — wrap all External API outbound calls in circuit breaker logic.

**Reference Patterns**: `rate-limiter-flexible` with per-caller key generation; `opossum` circuit breaker for External API calls; connection pool configuration with `max: N` concurrent connections; exponential backoff with jitter for retry logic.

**Effort Estimate**: Medium — rate limiting and circuit breakers are well-understood patterns; the main design work is calibrating thresholds for legitimate agent behavior versus runaway execution.

---

#### 37. D-2 — LLM Agent Orchestrator (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement token budget enforcement and recursive tool invocation depth limiting at the Orchestrator. Set a maximum context window budget per user request (e.g., 32,000 tokens) and reject or truncate requests exceeding the budget. Limit recursive tool invocation chains to a maximum depth (e.g., 5 levels) to prevent context-filling recursive attacks. Implement per-user Orchestrator capacity quotas.

**Where to Implement**: `src/orchestrator/resource-governor.ts` — add token budget tracking and tool invocation depth counting. Return a structured error when budgets are exceeded rather than processing expensive requests.

**Reference Patterns**: Token counting with `tiktoken`; recursive depth tracking in tool call dispatch; per-user request quotas with Redis-backed counters; inference timeout enforcement with `AbortController`.

**Effort Estimate**: Medium — token budget enforcement and depth limiting are configuration-level additions to the Orchestrator's invocation logic; per-user quota tracking requires a Redis-backed counter store.

---

#### 38. D-5 — MCP Tool Server (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement connection pool limits and per-caller concurrency limits on the MCP Tool Server's External API outbound connections. Configure a maximum concurrent connection count per External API provider and a maximum concurrent tool calls per authenticated agent session. Add backpressure signaling to calling agents when the pool is near capacity.

**Where to Implement**: `src/mcp/connection-pool.ts` — configure bounded connection pool with `max: 50` concurrent outbound connections, `maxWaitingClients: 20` queue depth. Add per-caller semaphore limits.

**Reference Patterns**: `generic-pool` for connection pool management; `p-limit` for per-caller concurrency limiting; HTTP/2 multiplexing for efficient External API connection reuse; backpressure signaling via 503 responses with `Retry-After` headers.

**Effort Estimate**: Medium — connection pool configuration and per-caller limits are infrastructure configuration with moderate development effort for the backpressure signaling mechanism.

---

#### 39. OI-4 — Clinical Advisory Sub-Agent (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement output sanitization for Clinical Advisory Sub-Agent outputs before the Orchestrator incorporates them into Tool Call Request parameters. Clinical summaries must be treated as untrusted input at the Orchestrator boundary — apply the same parameterized tool call dispatch from LLM-6/OI-2 remediations before any clinical output-derived parameters reach the Tool Server. This is an extension of the E-7 clinical output handler recommendation.

**Where to Implement**: `src/orchestrator/clinical-output-handler.ts` — treat clinical sub-agent output as untrusted and apply full output sanitization before tool parameter use. Reference the OI-2 sanitizer implementation.

**Reference Patterns**: Same as OI-2 output sanitization; clinical output schema validation to strip injection-capable content; structured output parsing that prevents free-form clinical text from reaching tool parameters.

**Effort Estimate**: Low — if OI-2 output sanitization is implemented, extending it to cover clinical output in tool parameters is an incremental addition to the existing sanitizer.

---

#### 40. R-1 — User (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement request signing at the User→Guardrails boundary to enable non-repudiation of user-submitted prompts. Include a signed timestamp and request nonce in each request, stored with the audit log entry. Use client-side signing via a session key derived at authentication time. The audit log entry must include the signed request payload so that repudiation claims can be disproved cryptographically.

**Where to Implement**: `src/guardrails/request-signer.ts` — add request receipt and signature verification at the Guardrails ingress. `src/audit/signed-request-logger.ts` — store signed request payloads with audit log entries.

**Reference Patterns**: JWT with `iat` claim and nonce for request binding; HTTP Message Signatures (RFC 9421) for signed request non-repudiation; HMAC request signing similar to AWS Signature Version 4.

**Effort Estimate**: Medium — request signing infrastructure requires changes to both the client-side session management and server-side Guardrails ingress; storing signed payloads with audit entries extends the audit logging schema.

---

#### 41. S-6 — MCP Tool Server (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement caller authentication on the MCP Tool Server (same root cause as E-5). S-6 is the spoofing perspective on the same missing authentication control. Implementing the E-5 remediation (mTLS caller authentication with per-agent client certificates) directly addresses S-6. Require all tool call requestors to present a valid client certificate before any tool invocation is processed.

**Where to Implement**: Same as E-5 — `src/mcp/caller-authenticator.ts`. No additional work beyond E-5 remediation.

**Reference Patterns**: Same as E-5 (mTLS, SPIFFE/SPIRE).

**Effort Estimate**: Low — if E-5 is implemented, S-6 is addressed by the same change with no additional effort.

---

#### 42. AG-2 — LLM Agent Orchestrator (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement cross-agent coordination monitoring to detect when the Orchestrator and Specialist are jointly executing a pattern that would exceed per-agent rate limits or violate policy individually. Implement a policy engine that evaluates combined action sequences from both agents against system-wide policy limits (e.g., maximum data accessed per session across all agents, maximum External API calls per session across all agents).

**Where to Implement**: `src/orchestrator/cross-agent-monitor.ts` — add a session-scoped aggregated action tracker that accumulates action counts from both the Orchestrator and Specialist and triggers rate limiting or HITL when combined limits are approached.

**Reference Patterns**: Distributed rate limiting with Redis sorted sets for per-session aggregate action tracking; policy evaluation engine with `casbin`; OWASP LLM08 excessive agency pattern monitoring.

**Effort Estimate**: High — cross-agent policy enforcement requires a shared session state infrastructure visible to both the Orchestrator and Specialist, plus policy definition for permitted combined action spaces.

---

#### 43. AG-4 — Inter-Agent Communication Channel (Composite: 6.0, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement message integrity protection on the Inter-Agent Communication Channel using HMAC or cryptographic signing per message (per E-4 remediation). Additionally, implement message replay prevention via nonce tracking — each message carries a unique nonce that is verified against a short-lived nonce store before routing. This prevents agent-in-the-middle attacks that replay or delay messages.

**Where to Implement**: Same as E-4 sender authentication infrastructure. Add nonce tracking in `src/inter-agent/nonce-tracker.ts` with a Redis-backed nonce expiry store.

**Reference Patterns**: Same as E-4; additionally Redis-backed nonce verification with TTL; message integrity with HMAC-SHA256; replay window detection.

**Effort Estimate**: Low — if E-4 is implemented, replay prevention is an incremental addition to the same message authentication middleware.

---

#### 44. E-6 — Long-Running Learning Loop (Composite: 6.0, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement model update verification before the Learning Loop applies updates to Orchestrator, Specialist, and Clinical Advisory Sub-Agent models. Require cryptographic provenance for all model update artifacts (sign update packages with the Learning Loop's identity key). Implement a model update review gate where a human operator must approve each update before deployment. Add behavioral regression testing before applying updates.

**Where to Implement**: `src/learning-loop/update-verifier.ts` — add update package signature verification and human approval workflow before model deployment. `src/learning-loop/behavioral-tester.ts` — add automated behavioral regression tests against a safety test suite before update approval.

**Reference Patterns**: SLSA framework for model artifact provenance; model signing with `sigstore`; human approval workflow via task queue (BullMQ); automated behavioral testing with HELM or MMLU-style safety benchmarks.

**Effort Estimate**: High — model update provenance, human approval workflows, and behavioral testing infrastructure are significant additions to the Learning Loop's deployment pipeline.

---

#### 45. I-1 — Guardrails Service (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement generic error responses for the Guardrails Service — replace rejection reasons that reveal filter rule details with a uniform "Request not permitted" message. Implement a probe detection mechanism that tracks repeated rejection patterns from the same user/IP and applies progressive rate limiting or blocks further probing attempts. Ensure error responses never include the matched filter rule, the rejection category, or the content that triggered the rejection.

**Where to Implement**: `src/guardrails/error-handler.ts` — replace specific rejection messages with generic 400 responses. `src/guardrails/probe-detector.ts` — add pattern-based probe detection with progressive rate limiting.

**Reference Patterns**: Uniform error response design; Redis-backed rejection counter per user/IP; `express-rate-limit` with custom key generator for probe detection; OWASP Error Handling Cheat Sheet.

**Effort Estimate**: Low — replacing specific rejection messages with generic ones is a configuration change; probe detection is a new rate-limiting middleware component.

---

#### 46. S-3 — LLM Agent Orchestrator (Composite: 5.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement cryptographic identity attestation for the Orchestrator on the Inter-Agent Communication Channel. The Orchestrator must sign all delegation messages and channel communications with its per-component identity key (per E-4 remediation). The Specialist and Clinical Advisory Sub-Agent must verify Orchestrator attestations before processing any delegation or instruction. Deploying the E-4 inter-agent sender authentication infrastructure addresses this finding.

**Where to Implement**: Same as E-4 — extend `src/inter-agent/sender-authenticator.ts` to include Orchestrator identity attestation in all outbound channel messages.

**Reference Patterns**: Same as E-4 (SPIFFE/SPIRE, per-component ECDSA keys).

**Effort Estimate**: Low — addressed by E-4 sender authentication remediation with no additional effort.

---

#### 47. T-3 — Specialist Agent (Composite: 5.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement message integrity verification on all delegation messages received by the Specialist Agent (per LLM-8 remediation). Verify HMAC signatures on incoming delegation messages before processing. Reject delegation messages with invalid signatures. This is the tampering perspective on the same missing message authentication addressed by LLM-8 and E-4.

**Where to Implement**: `src/specialist/delegation-validator.ts` — same signature verification as LLM-8/E-3 remediations. No additional work beyond LLM-8 implementation.

**Reference Patterns**: Same as LLM-8.

**Effort Estimate**: Low — addressed by LLM-8 delegation message authentication remediation.

---

#### 48. T-4 — Inter-Agent Communication Channel (Composite: 5.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement message integrity protection on the Inter-Agent Communication Channel (per E-4 remediation). Per-message HMAC or asymmetric signatures prevent in-transit message modification. T-4 (tampering via message queue access) and E-4 (privilege escalation via forged sender) are addressed by the same channel sender authentication infrastructure.

**Where to Implement**: Same as E-4 — `src/inter-agent/sender-authenticator.ts`.

**Reference Patterns**: Same as E-4.

**Effort Estimate**: Low — addressed by E-4 channel authentication remediation.

---

#### 49. S-9 — Clinical Advisory Sub-Agent (Composite: 5.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement per-message sender attestation on clinical queries from the Orchestrator to the Clinical Advisory Sub-Agent (per T-9 remediation). The Orchestrator must sign each Clinical Query / Context message with its identity key; the sub-agent must verify the signature before processing. This addresses S-9's JSON-RPC spoofing vector via the same message authentication infrastructure.

**Where to Implement**: `src/clinical-advisor/query-authenticator.ts` — same implementation as T-9 remediation.

**Reference Patterns**: Same as T-9 (HMAC, JWS).

**Effort Estimate**: Low — addressed by T-9 query authentication remediation.

---

#### 50. T-7 — Audit Logger (Composite: 5.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement tamper-evident audit log storage using a Merkle hash chain or cryptographic log chaining. Each log entry must include a hash of the previous entry (chain pointer) and be signed by the logging component. Store logs in a write-once, append-only storage backend. Implement log integrity verification as a periodic background job that validates the chain continuity.

**Where to Implement**: `src/audit/tamper-evident-logger.ts` — replace the current append mechanism with Merkle-chain logging. Each entry: `{entry_id, content, content_hash, prev_hash, timestamp, signature}`.

**Reference Patterns**: Certificate Transparency log structure; AWS CloudTrail with log file integrity validation; `merkle-lib` for Merkle tree construction; append-only storage with S3 Object Lock or Worm-enabled database.

**Effort Estimate**: High — Merkle-chain tamper-evident logging requires redesigning the Audit Logger's storage model and adding chain verification infrastructure; existing log entries cannot be retroactively chained.

---

#### 51. AG-7 — Long-Running Learning Loop (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement training data content analysis for autonomy-expansion patterns. Before incorporating training samples into the Learning Loop, apply a behavioral intent classifier that detects samples that would expand the updated model's autonomous action scope. Flag samples that instruct the model to take more autonomous actions, bypass confirmation gates, or act outside its defined role. Require human review for flagged training samples.

**Where to Implement**: `src/learning-loop/autonomy-guard.ts` — add an intent classifier in the training data pipeline that detects capability-expansion patterns and routes flagged samples to human review.

**Reference Patterns**: Constitutional AI alignment techniques; RLHF preference modeling for scope-constrained behavior; MITRE ATLAS AML.T0041 mitigations; training data safety classifiers.

**Effort Estimate**: High — autonomy-expansion pattern detection requires ML expertise and a behavioral intent classification model that understands the system's defined scope boundaries.

---

#### 52. D-9 — Clinical Advisory Sub-Agent (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting on Clinical Advisory Sub-Agent invocations (per-session and per-IP) to prevent clinical query flooding. Set a maximum clinical queries per minute per authenticated user (e.g., 10/min). Implement timeout enforcement on KB vector searches to prevent computationally expensive queries from starving shared KB capacity. Implement admission control that sheds clinical queries during high load rather than queuing them indefinitely.

**Where to Implement**: `src/clinical-advisor/rate-limiter.ts` — add per-caller rate limiting on clinical query invocations. `src/knowledge-base/query-governor.ts` — add query timeout enforcement and admission control.

**Reference Patterns**: `rate-limiter-flexible` for per-caller limits; vector search timeout via HNSW `ef_search` limit; admission control with load shedding; circuit breaker for KB unavailability scenarios.

**Effort Estimate**: Medium — rate limiting is a well-understood pattern; the main design work is calibrating thresholds appropriate for clinical query latency characteristics.

---

#### 53. LLM-9 — Specialist Agent (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement field-level classification and anomaly detection on Specialist Agent audit log entries before they enter the Learning Loop's training signal. Self-poisoning via the Specialist's own interaction logs requires that the training pipeline validate Specialist decision logs against expected behavior patterns before inclusion. Extend the training data validation from LLM-4 remediation to cover Specialist-sourced training samples.

**Where to Implement**: `src/learning-loop/specialist-data-validator.ts` — add Specialist-specific behavioral anomaly detection in the training data pipeline. Extend the LLM-4 training validator with Specialist-domain behavioral pattern baseline.

**Reference Patterns**: Same as LLM-4 training data validation; behavioral baseline for Specialist decision logs; anomaly detection against expected tool call frequency and type distributions.

**Effort Estimate**: Medium — extends the LLM-4 training data validation framework with Specialist-specific behavioral baseline validation.

---

#### 54. D-6 — Knowledge Base (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement query cost estimation and admission control on the Knowledge Base's vector search interface. Limit maximum query complexity (number of results requested, dimensionality of search vectors, search index parameters) to bound computational cost per query. Implement per-caller rate limits on KB queries and circuit breaker logic that sheds queries during high load.

**Where to Implement**: `src/knowledge-base/query-governor.ts` — add query complexity scoring and per-caller rate limiting. Configure: max `top_k: 20` results per query, `ef_search: 64` HNSW complexity bound, `5 queries/sec` per caller.

**Reference Patterns**: `rate-limiter-flexible` for KB query rate limiting; HNSW parameter tuning for complexity bounding; vector database admission control; circuit breaker for KB degradation scenarios.

**Effort Estimate**: Medium — query complexity bounds are configuration-level changes to the vector database; per-caller rate limiting is a standard middleware addition.

---

#### 55. LLM-11 — Long-Running Learning Loop (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement audit log entry validation in the Learning Loop's training signal ingestion (same as T-8 remediation). The training validator from LLM-4 must include Audit Logger entry schema validation that rejects entries with anomalous structure, out-of-distribution content, or statistical patterns inconsistent with normal operational data. Apply the T-8 tamper-evident logging recommendation at the source.

**Where to Implement**: Extend `src/learning-loop/training-validator.ts` from LLM-4 with Audit Logger entry schema validation. Cross-reference with T-8 and S-7 remediations.

**Reference Patterns**: Same as LLM-4 training data validation; Audit Logger schema validation; statistical anomaly detection for training signal quality.

**Effort Estimate**: Low — if LLM-4 training data validation is implemented, this is an incremental extension with Audit Logger-specific schema validation rules.

---

#### 56. T-8 — Long-Running Learning Loop (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement tamper-evident audit logging (per T-7 remediation) as the primary defense — if audit log entries are signed and chained, injection of adversarial entries is detectable before they enter the training pipeline. Additionally, implement training data provenance verification per S-7 remediation — the Learning Loop must verify that each training sample carries a valid Audit Logger signature before incorporation.

**Where to Implement**: `src/learning-loop/stream-authenticator.ts` — extend with per-sample provenance verification. Cross-references T-7 (tamper-evident logging) and S-7 (stream authentication) remediations.

**Reference Patterns**: Same as T-7 (Merkle-chain logging) and S-7 (stream source authentication).

**Effort Estimate**: Low — if T-7 and S-7 remediations are implemented, T-8 is addressed by the combined tamper-evidence and source authentication infrastructure.

---

#### 57. D-3 — Specialist Agent (Composite: 5.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement task complexity budgeting on the Specialist Agent. Each delegation message must include a computational budget (maximum tool calls, maximum execution time, maximum token budget) derived from the delegation scope. The Specialist must enforce the budget and terminate execution when limits are exceeded. Implement per-delegation rate limiting to prevent task queue flooding.

**Where to Implement**: `src/specialist/budget-enforcer.ts` — add task budget tracking and enforcement. `src/inter-agent/delegation-rate-limiter.ts` — add per-session delegation rate limiting at the channel ingress.

**Reference Patterns**: `AbortController` for timeout enforcement; per-delegation budget tracking with Redis counters; delegation queue depth limits; OWASP LLM08 excessive agency mitigations.

**Effort Estimate**: Medium — budget enforcement requires integrating budget parameters into the delegation message schema and adding enforcement logic to the Specialist's execution loop.

---

#### 58. D-4 — Inter-Agent Communication Channel (Composite: 5.5, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement per-sender rate limiting on the Inter-Agent Communication Channel message queue to prevent queue flooding. Each Application Zone process must be subject to a maximum message submission rate. Implement dead letter queue handling for overflowed messages. Add queue depth monitoring with alerts when the queue depth exceeds safe operating thresholds.

**Where to Implement**: `src/inter-agent/queue-rate-limiter.ts` — add per-sender rate limiting on message queue writes. Configure: max `100 messages/minute` per authenticated sender; dead letter queue for overflow.

**Reference Patterns**: RabbitMQ per-queue rate limits; Redis-backed per-sender rate limiting; queue depth monitoring with CloudWatch or Prometheus; OWASP LLM08 rate limiting patterns.

**Effort Estimate**: Medium — queue rate limiting is a configuration-level addition to the message queue infrastructure with a modest development effort for the enforcement middleware.

---

#### 59. D-7 — Audit Logger (Composite: 5.5, Partial)

**Current Status**: Partial Control

**What to Implement**: Harden the existing Audit Logger component against log flooding by implementing write rate limiting and log entry validation. The Audit Logger component exists architecturally but lacks rate limits on write operations. Add: (1) per-caller write rate limits to bound log entry injection rate, (2) maximum log entry size enforcement, (3) structured log entry schema validation to reject malformed entries, (4) backpressure signaling when the logger is under load.

**Where to Implement**: Extend the existing Audit Logger component with write rate limiting middleware. `src/audit/write-rate-limiter.ts` — add per-caller write limits. `src/audit/entry-validator.ts` — add schema validation for incoming log entries.

**Reference Patterns**: `rate-limiter-flexible` for per-caller write rate limiting; structured log entry schemas with Zod; log entry size limits; write backpressure with 429 responses to high-rate log writers.

**Effort Estimate**: Low — rate limiting and schema validation are incremental hardening of the existing Audit Logger component; no architectural changes required.

---

#### 60. I-6 — Knowledge Base (Composite: 5.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement access control and result limiting on the Knowledge Base's vector search interface. Add query-result access controls that restrict the documents a caller can retrieve based on their authenticated role and namespace permissions. Implement result count limiting (max `top_k` per query) and result rate limiting (max corpus volume retrievable per session) to prevent exhaustive corpus extraction.

**Where to Implement**: `src/knowledge-base/access-controller.ts` — add RBAC-based query result filtering. `src/knowledge-base/result-limiter.ts` — add per-session corpus volume limits.

**Reference Patterns**: Vector database namespace isolation; RBAC query filtering with per-document access tags; result count limits (`top_k` enforcement); per-session cumulative result volume tracking.

**Effort Estimate**: High — implementing RBAC-based query result filtering requires per-document access control metadata in the KB and a policy evaluation layer at query time.

---

#### 61. I-7 — Audit Logger (Composite: 5.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement access control on the Audit Logger read interface. Restrict read access to authorized security and compliance roles only — no agent component should have read access to the full audit trail during normal operations. Implement field-level access control that allows the Learning Loop to access only the training-relevant fields of audit entries, not the full sensitive operational data.

**Where to Implement**: `src/audit/access-controller.ts` — add RBAC-based read access control on the Audit Logger's query interface. Define roles: `security-reviewer` (full read), `learning-loop` (training fields only), no agent (no direct audit read access).

**Reference Patterns**: RBAC access control with `casl`; field-level access control via query projection; audit log read API with role-based response shaping; separation of duties between operational and audit access.

**Effort Estimate**: High — implementing field-level RBAC on the audit trail requires redesigning the Audit Logger's read interface to support role-based response shaping.

---

#### 62. D-8 — Long-Running Learning Loop (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement training data volume limits and processing resource quotas on the Learning Loop. Set a maximum training batch size derived from the expected operational data volume. Implement CPU/memory quotas for the Learning Loop's batch processing job. Add circuit breakers that abort a training run when resource consumption exceeds safe thresholds.

**Where to Implement**: `src/learning-loop/resource-governor.ts` — add training batch size limits and resource quota enforcement. Configure container CPU/memory limits for the Learning Loop process.

**Reference Patterns**: Kubernetes resource limits and requests for the Learning Loop container; PyTorch DataLoader batch size limits; compute budget enforcement with process-level CPU quotas; circuit breaker for training runaway detection.

**Effort Estimate**: Medium — resource quota enforcement is primarily infrastructure configuration (container limits, batch size settings) with moderate code changes for programmatic circuit breaker logic.

---

#### 63. I-5 — MCP Tool Server (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement PII detection and redaction on tool results before the MCP Tool Server logs them to the Audit Logger. Apply a PII detector (regex + ML-based) to all tool result content. Redact detected PII fields before writing to the audit trail. Additionally, implement result data minimization — log only the fields required for audit purposes, not the full tool result payload.

**Where to Implement**: `src/mcp/result-redactor.ts` — add PII detection and redaction to tool results before Audit Logger writes. Define a per-tool result audit schema that specifies which fields to include in audit logs.

**Reference Patterns**: Microsoft Presidio for PII detection; regex-based PII patterns for common identifiers; per-tool result audit schemas defined in the tool manifest; GDPR data minimization principle.

**Effort Estimate**: Medium — PII detection integration requires configuring a PII detector for the data types handled by each tool; result audit schemas require per-tool configuration work.

---

#### 64. LLM-3 — LLM Agent Orchestrator (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting and behavioral anomaly detection to counter systematic model probing. Limit query rate per authenticated user (e.g., 60 queries/minute). Detect systematic probing patterns (queries designed to extract model behavior via delta analysis) using a probe signature classifier. Apply progressive rate limiting or session suspension for detected probing patterns.

**Where to Implement**: `src/guardrails/probe-detector.ts` — extend the I-1 probe detector to cover model behavior probing patterns. Add `src/orchestrator/query-rate-limiter.ts` for per-user query rate limits.

**Reference Patterns**: Same probe detection as I-1; behavioral fingerprinting of model extraction queries; `rate-limiter-flexible` for per-user query limits; differential privacy in model responses to increase extraction cost.

**Effort Estimate**: Medium — extends the I-1 probe detection infrastructure with model extraction-specific patterns; per-user rate limiting is straightforward.

---

#### 65. LLM-12 — Long-Running Learning Loop (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement access control on the Learning Loop's model update artifacts. Restrict access to model parameter diffs, update packages, and training artifacts to authorized deployment personnel only. Encrypt model update artifacts at rest using envelope encryption. Implement signed artifact distribution so that only signed updates can be applied to production agents.

**Where to Implement**: `src/learning-loop/artifact-access-control.ts` — add RBAC-based access control on model update artifacts. `src/learning-loop/artifact-encryptor.ts` — add at-rest encryption for model update packages.

**Reference Patterns**: AWS KMS envelope encryption for model artifacts; RBAC artifact access with IAM policies; model signing with Sigstore; artifact version registry with access-controlled distribution.

**Effort Estimate**: Medium — artifact encryption and access control are infrastructure-level configurations with moderate development effort for the signing and distribution workflow.

---

#### 66. T-6 — Knowledge Base (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement access control and integrity verification on the Knowledge Base write interface. Restrict document ingestion to authorized service accounts only (no agent component should have write access to the KB). Implement document signing at ingestion time (per LLM-2 remediation). Add document validation that rejects adversarial content patterns detected by the ingestion validator.

**Where to Implement**: `src/knowledge-base/write-access-controller.ts` — add RBAC-based write access control. Limit KB write permissions to the document ingestion service account only.

**Reference Patterns**: IAM policy restricting KB write access; per-document signing per LLM-2 remediation; content-addressable document storage; OWASP Stored XSS and data integrity controls adapted for KB document ingestion.

**Effort Estimate**: Medium — write access control is an infrastructure configuration change (IAM policy); document signing extends the LLM-2 remediation with no new infrastructure.

---

#### 67. R-9 — Clinical Advisory Sub-Agent (Composite: 5.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement non-repudiable clinical output logging. Each Clinical Summary + Recommendations output must be logged with: the full output content, a SHA-256 content hash, the KB documents retrieved (document IDs + content hashes), and a cryptographic signature from the Clinical Advisory Sub-Agent's component identity key. Store logs in the tamper-evident Audit Logger per T-7 remediation.

**Where to Implement**: `src/clinical-advisor/output-logger.ts` — add structured non-repudiable clinical output logging with content hashing and component signing.

**Reference Patterns**: SHA-256 content hashing per R-3 remediation; component signing with ECDSA per E-4 signing infrastructure; structured clinical output log schema; append-only log storage per T-7 remediation.

**Effort Estimate**: Medium — clinical output logging with content hashing extends the R-3 action logging infrastructure with clinical-specific fields.

---

#### 68. S-2 — Guardrails Service (Composite: 5.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement mutual TLS (mTLS) authentication between the Guardrails Service and the LLM Agent Orchestrator. The Orchestrator must only accept validated inputs from the authenticated Guardrails Service component. All internal service endpoints must require client certificate authentication — no unauthenticated access from Application Zone processes.

**Where to Implement**: `src/orchestrator/ingress-authenticator.ts` — add mTLS client certificate validation on the Orchestrator's internal API endpoint. Generate per-component certificates for the Guardrails Service.

**Reference Patterns**: mTLS with `node:tls` and client certificate validation; SPIFFE/SPIRE for workload identity; service mesh (Istio, Linkerd) for automatic mTLS in containerized deployments.

**Effort Estimate**: High — mTLS across all internal service endpoints requires a certificate management infrastructure and configuration changes across all Application Zone components.

---

#### 69. I-4 — Inter-Agent Communication Channel (Composite: 5.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement message-level encryption on the Inter-Agent Communication Channel to prevent passive observation by Application Zone processes. Encrypt inter-agent messages at the application layer using per-session symmetric keys derived from a key agreement protocol between communicating agents. Application-layer encryption complements transport-layer TLS and ensures message confidentiality even if the message bus infrastructure is compromised.

**Where to Implement**: `src/inter-agent/message-encryptor.ts` — add application-layer message encryption using AES-256-GCM with per-session ephemeral keys derived via ECDH key agreement.

**Reference Patterns**: `tweetnacl` for ECDH key agreement + XSalsa20 message encryption; `libsodium.js` sealed box encryption; per-session symmetric key derivation using HKDF; channel encryption independent of transport security.

**Effort Estimate**: High — per-session key agreement between agents requires a key exchange protocol and session key lifecycle management across all agent pairs.

---

#### 70. T-1 — Guardrails Service (Composite: 5.0, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement dual-approval enforcement and change auditing for Guardrails Service configuration modifications. Any change to filtering rules must require approval from two independent authorized administrators before taking effect. Implement configuration change logging with full diff recording and revert capability. Apply integrity verification to the deployed configuration.

**Where to Implement**: `src/guardrails/config-approval-workflow.ts` — add dual-approval workflow for configuration changes. `src/audit/config-change-logger.ts` — add configuration change audit logging with diff recording.

**Reference Patterns**: Two-person integrity (TPI) for configuration changes; GitOps-based configuration management with required PR approvals; configuration change events in the Audit Logger; configuration signing per the tamper-evident logging infrastructure.

**Effort Estimate**: Medium — dual-approval workflow requires building an administrative change management interface; configuration change logging is an extension of the Audit Logger infrastructure.

---

#### 71. I-8 — Long-Running Learning Loop (Composite: 4.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement differential privacy during the Learning Loop's training process to prevent the trained model from memorizing and reproducing sensitive training data. Apply Gaussian or Laplace noise to gradient updates during training with a privacy budget (epsilon) calibrated for the sensitivity of the training data. Additionally, implement training data anonymization before ingestion into the Learning Loop.

**Where to Implement**: `src/learning-loop/differential-privacy.ts` — integrate differential privacy training with `opacus` (PyTorch) or equivalent. `src/learning-loop/data-anonymizer.ts` — apply anonymization (k-anonymity, l-diversity) to training data before ingestion.

**Reference Patterns**: `opacus` for PyTorch differential privacy training; Google's DP-SGD implementation; k-anonymity via Presidio Anonymizer; NIST Privacy Framework; GDPR Article 89 anonymization standards.

**Effort Estimate**: High — differential privacy training requires significant ML engineering changes to the Learning Loop's training pipeline and careful privacy budget calibration.

---

#### 72. R-7 — Long-Running Learning Loop (Composite: 4.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement model update provenance using cryptographic attestations. Each model update package must include: training run ID, training data hash (Merkle root of training samples), training configuration hash, timestamp, and a cryptographic signature from the Learning Loop's component identity key. Store provenance records in the tamper-evident Audit Logger. This enables auditable attribution of any model behavior to a specific training run and data set.

**Where to Implement**: `src/learning-loop/provenance-recorder.ts` — generate and sign model update provenance records. Extend the E-6 model update verifier with provenance record generation at each training run.

**Reference Patterns**: SLSA provenance for ML artifacts; model cards with training provenance; SHA-256 Merkle root of training samples; artifact signing with Sigstore.

**Effort Estimate**: Medium — provenance recording extends the E-6 model update verification infrastructure with cryptographic training data commitments.

---

#### 73. S-4 — Specialist Agent (Composite: 4.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement result authentication on the Specialist Agent's result messages returned to the Orchestrator via the Inter-Agent Channel. The Specialist must sign aggregated results with its component identity key. The Orchestrator must verify the Specialist's result signatures before incorporating them into its reasoning. This prevents a compromised Specialist from injecting fabricated results without detection.

**Where to Implement**: `src/specialist/result-signer.ts` — add result message signing at Specialist result emission. `src/orchestrator/result-verifier.ts` — add result signature verification before incorporation into Orchestrator context.

**Reference Patterns**: Same component signing infrastructure as E-4; HMAC-SHA256 result signatures; result authentication as a required field in the aggregated result schema.

**Effort Estimate**: Medium — result signing extends the E-4 inter-component signing infrastructure to the Specialist's result emission path.

---

#### 74. I-3 — Specialist Agent (Composite: 4.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement data minimization on the Specialist Agent's result outputs. The Specialist must not include sensitive upstream context (user PII, system prompt content, KB document excerpts) verbatim in its results unless explicitly required by the delegation scope. Apply content filtering to result outputs that strips or redacts sensitive context fields before transmission via the Inter-Agent Channel.

**Where to Implement**: `src/specialist/result-scrubber.ts` — add content filtering to result outputs, stripping fields not explicitly authorized by the delegation scope. Define a result data minimization policy in the delegation schema.

**Reference Patterns**: Data minimization per GDPR Article 5(1)(c); content filtering with `sanitize-html`; per-delegation result schema that defines authorized output fields; result output classification before channel transmission.

**Effort Estimate**: Medium — result scrubbing requires defining per-delegation output schemas and implementing content filtering against sensitive context patterns.

---

#### 75. R-2 — Guardrails Service (Composite: 4.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement tamper-evident logging for all Guardrails Service filtering decisions. Each filtering event must be logged with the decision (pass/reject), the filter rule triggered, a content hash of the evaluated prompt (not the prompt itself, to prevent sensitive data in logs), and be chained in the Merkle-chain Audit Logger per T-7 remediation. This enables independent verification of filtering decisions without exposing the rejected content.

**Where to Implement**: `src/guardrails/decision-logger.ts` — add structured tamper-evident logging of filtering decisions to the Audit Logger. Include: `{decision, rule_id, prompt_hash, timestamp}`.

**Reference Patterns**: SHA-256 prompt content hashing (do not log raw prompts); structured decision events in the Merkle-chain Audit Logger per T-7; filtering decision schema separate from prompt content.

**Effort Estimate**: Low — filtering decision logging is a targeted extension of the existing Audit Logger with a Guardrails-specific event schema.

---

#### 76. R-4 — Specialist Agent (Composite: 4.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement signed decision logging for all Specialist Agent tool calls and result productions. Each tool invocation and result must be logged with content hashing and component signing (per R-3 remediation pattern). The Specialist's component identity key signs each log entry. Store in the tamper-evident Audit Logger per T-7.

**Where to Implement**: `src/specialist/decision-logger.ts` — add signed tool call and result logging. Extend the R-3 action logging pattern to the Specialist Agent.

**Reference Patterns**: Same as R-3 (content hashing, component signing, Merkle-chain logger).

**Effort Estimate**: Low — extends the R-3 action logging infrastructure to the Specialist Agent component.

---

#### 77. R-6 — MCP Tool Server (Composite: 4.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement signed execution logging for all MCP Tool Server tool invocations. Each JSON-RPC tool call must be logged with: caller identity (from authenticated session), tool name, parameter hash, response hash, timestamp, and a component signature from the Tool Server's identity key. Store in the tamper-evident Audit Logger per T-7.

**Where to Implement**: `src/mcp/execution-logger.ts` — add signed tool execution logging. Extend the R-3 action logging pattern to the Tool Server.

**Reference Patterns**: Same as R-3; additionally log External API response hashes for accountability of provider-level responses; coordinate with R-8 response signing for full end-to-end accountability.

**Effort Estimate**: Low — extends the R-3 action logging infrastructure to the Tool Server component.

---

#### 78. R-5 — Inter-Agent Communication Channel (Composite: 4.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement message delivery receipts and integrity records on the Inter-Agent Communication Channel. The channel must generate a signed delivery receipt for each message that records: message ID, sender, recipient, delivery timestamp, and a hash of the delivered message content. Receipts must be stored in the tamper-evident Audit Logger. This enables proof of delivery and content integrity for all inter-agent messages.

**Where to Implement**: `src/inter-agent/delivery-receipt-logger.ts` — add signed delivery receipt generation and logging for all channel messages.

**Reference Patterns**: Message delivery acknowledgments with signed receipts; AMQP publisher confirms adapted with content hashing; message provenance per the E-4/T-4 channel authentication infrastructure; storage in Merkle-chain Audit Logger per T-7.

**Effort Estimate**: Medium — delivery receipt generation requires coordination between the channel infrastructure and the Audit Logger, with per-message receipt signing extending the component identity infrastructure.

---

#### 79. S-8 — External API (Composite: 5.8, Partial — Hardening Required)

**Current Status**: Partial Control (TLS certificate validation exists)

**What to Implement**: Harden the existing TLS certificate validation by adding certificate pinning for trusted External API providers. Pin the expected certificate fingerprints or CA chain for each External API in the Tool Server's outbound HTTP client configuration. Additionally, implement API response signing verification — require External API providers to sign responses with a known public key, enabling the Tool Server to verify response authenticity before trusting the content.

**Where to Implement**: `src/mcp/tls-pinning.ts` — extend the outbound HTTP client with certificate fingerprint pinning per configured External API. `src/mcp/response-verifier.ts` — add API response signature verification where providers support it.

**Reference Patterns**: `tls.connect` with `checkServerIdentity` override for certificate pinning; HPKP-style cert fingerprint validation; HMAC response signing negotiated with API provider; Certificate Transparency monitoring for pinned certs.

**Effort Estimate**: Medium — certificate pinning requires per-provider certificate fingerprint configuration; response signing requires API provider cooperation or a service-level agreement change.

---

#### 80. R-8 — External API (Composite: 5.0, Partial — Hardening Required)

**Current Status**: Partial Control (TLS-based transport accountability exists)

**What to Implement**: Implement API response receipt logging with content hashing to enable non-repudiation of External API responses. The MCP Tool Server must log every External API response with: request ID, response content hash, response headers including any provider-signed fields, and timestamp. Correlate with R-6 (Tool Server execution logging) to create an end-to-end accountability chain from tool invocation to provider response. Request that External API providers implement response signing (HTTP Message Signatures).

**Where to Implement**: `src/mcp/response-logger.ts` — add response content hashing and structured receipt logging for all External API responses. Coordinate with `src/mcp/execution-logger.ts` from R-6.

**Reference Patterns**: HTTP Message Signatures (RFC 9421) for provider-signed responses; SHA-256 response body hashing; structured response receipt schema in the Audit Logger; request/response correlation via request ID.

**Effort Estimate**: Low — response content hashing and structured logging is an incremental addition to the Tool Server's existing request/response handling; provider-side signing requires external coordination.

---

## 5. Residual Risk Summary

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | 469.4 |
| Total Residual Risk Score | 467.2 |
| Delta | 2.2 |
| Overall Reduction | 0.5% |

### Per-Severity-Band Shift

| Shift | Count | Examples |
|-------|-------|---------|
| Critical -> High | 0 | N/A |
| Critical -> Medium | 0 | N/A |
| Critical -> Low | 0 | N/A |
| High -> Medium | 0 | None — all High findings remain High |
| High -> Low | 0 | None |
| Medium -> Low | 1 | R-8 (5.0 inherent → 3.8 residual) |
| No Shift | 82 | All remaining findings |
| **Total** | **83** | |

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | 0 | 0 | 0 |
| High | 17 | 17 | 0 |
| Medium | 66 | 65 | -1 |
| Low | 0 | 1 | +1 |
| **Total** | **83** | **83** | |

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent * 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent * 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent * 1.00 | No matching control detected. Residual equals inherent. |

> P1 enhancement: When control effectiveness assessment (User Story 6) is active, reduction factors upgrade from the 3-level binary model above to a 7-level effectiveness-aware model. See spec FR-011 and User Story 6 for the extended factor table.

---

## 6. Methodology

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

- **Scored threats**: Parsed from `risk-scores.md`. All original threat metadata (ID, component, category, description, composite score, severity band) is preserved.
- **Target codebase**: No codebase files exist for this architecture-only sample. Control detection was performed at the architecture/DFD level using threat descriptions and component narrative from the risk-scores.md dimensional breakdowns.
- **STRIDE-to-control mapping**: Canonical mapping from threat categories to control categories drives which controls are searched for each threat. MI-{N} findings are processed via the `llm` category code path per FR-014.

### 6.5 Limitations

- Architecture-only analysis — no codebase files were available for scanning. All control detections are architecture-level inferences from threat descriptions and DFD component narratives, not implementation evidence.
- Binary reduction factors (P0) approximate control impact; effectiveness-aware factors available in P1.
- AI-specific control patterns (agentic, LLM, misinformation) limited to general categories in P0; specialized patterns in P1.
- Three partial controls inferred from architecture: TLS on External API channel (S-8/R-8), Audit Logger component presence (D-7), and the Guardrails Service existence. No codebase evidence was collected.
- The MI-{N} misinformation findings (MI-1, MI-2, MI-3) are processed via the `llm` STRIDE category mapping (Input Validation, Logging/Audit) per FR-014. No MI-specific controls are architecturally attested; all three receive "No Control Found" status.
