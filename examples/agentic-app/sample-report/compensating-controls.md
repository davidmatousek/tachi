---
schema_version: "1.0"
date: "2026-04-18"
source_file: "risk-scores.md"
target_path: "/Users/david/Projects/tachi/examples/agentic-app/"
classification: "security"
---

# Compensating Controls Analysis — Agentic AI Application

## 1. Executive Summary

**Coverage**: 0 of 70 findings have controls detected (implemented=0, partial=0, missing=70 -- 0.0% / 0.0% / 100.0%).

**Risk reduction**: Total inherent risk 395.6 -> Total residual risk 395.6 (delta 0.0, reduction 0.0%).

The target codebase is a fictional reference architecture (`examples/agentic-app/`) consisting solely of a Mermaid flowchart description plus Component Summary tables. No implementation files exist (no `.js`, `.ts`, `.py`, or configuration files representing middleware, validators, guards, encryption helpers, or logging integrations). Every scanned component maps to zero production code, so every finding is classified `No Control Found`. This is the expected and correct outcome for reference-architecture inputs: the threat model identifies the defensive postures that an implementor MUST build; this analysis confirms none are yet in place.

> **Highest-risk unmitigated finding (residual 7.9, High)**: **S-1 -- Attacker impersonates legitimate user via replayed session tokens** (User, at the User->Guardrails boundary). Target mitigation: short-lived JWT/session tokens with client IP / device fingerprint binding, MFA, and token revocation lists.

### Metadata

| Field | Value |
|-------|-------|
| Findings analyzed | 70 |
| Components scanned | 10 |
| Files read | 1 (architecture.md; no implementation files present) |
| Analysis date | 2026-04-18 |
| Scoring weights | CVSS 0.35 / Exploit 0.30 / Scale 0.15 / Reach 0.20 |
| Reduction model | P0 binary (found=0.50, partial=0.25, missing=0.00) |

### Coverage Distribution

| Control Status | Count | Percent |
|---------------|-------|---------|
| Control Found (implemented) | 0 | 0.0% |
| Partial Control | 0 | 0.0% |
| No Control Found | 70 | 100.0% |
| **Total** | **70** | **100.0%** |

### Analysis Warnings

- Target codebase is a reference architecture, not an implementation. No middleware, routes, handlers, validators, configuration files, or service scaffolding are present. All 8 control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) evaluate to `detected: false` for every component.
- 3 Feature-201 output-integrity findings (OI-1, OI-2, OI-3) are covered in this analysis. Per F-1 scope, these findings map to two additional implementor-facing control patterns beyond the 8-category taxonomy: **Output Sanitization and Encoding** (OI-1 client-side XSS), **Allowlist Validation** (OI-2 server-side execution), and **Egress Control** (OI-3 SSRF). Recommendations for OI findings are populated in Section 4 using those patterns.

---

## 2. Coverage Matrix

All findings, sorted by residual severity band (Critical first), then by residual score descending, then by Threat ID ascending.

### Critical (residual >= 9.0)

_No findings in this band. Inherent scores are clamped by Application-Zone Trusted Reachability floor (1.0) for the vast majority of findings, keeping the highest composite below 9.0._

### High (residual 7.0 - 8.9)

| ID | Component | MAESTRO Layer | Threat | Inherent | Inherent Sev | Control Status | Control Category | Residual | Residual Sev |
|----|-----------|---------------|--------|----------|--------------|----------------|-----------------|----------|--------------|
| S-1 | User | L7 | Attacker impersonates legitimate user via replayed session tokens | 7.9 | High | No Control Found | Authentication | 7.9 | High |
| E-1 | Guardrails Service | L6 | Prompt injection bypass elevates attacker to trusted Orchestrator caller | 7.3 | High | No Control Found | Access Control | 7.3 | High |
| E-2 | LLM Agent Orchestrator | L1 | Orchestrator prompt injection self-authorizes elevated operations | 7.2 | High | No Control Found | Access Control | 7.2 | High |
| LLM-1 | LLM Agent Orchestrator | L1 | Direct prompt injection overrides system prompt or reveals context | 7.2 | High | No Control Found | Input Validation | 7.2 | High |
| LLM-5 | LLM Agent Orchestrator | L1 | Client-side XSS via LLM response rendered in browser | 7.2 | High | No Control Found | Input Validation | 7.2 | High |
| OI-1 | LLM Agent Orchestrator | L1 | Client-side XSS via LLM response to User browser | 7.2 | High | No Control Found | Output Sanitization and Encoding | 7.2 | High |

### Medium (residual 4.0 - 6.9)

| ID | Component | MAESTRO Layer | Threat | Inherent | Inherent Sev | Control Status | Control Category | Residual | Residual Sev |
|----|-----------|---------------|--------|----------|--------------|----------------|-----------------|----------|--------------|
| AG-1 | LLM Agent Orchestrator | L1 | Autonomous unauthorized high-impact actions via prompt injection | 6.9 | Medium | No Control Found | Access Control (Agentic) | 6.9 | Medium |
| LLM-8 | Specialist Agent | Unclassified | Prompt injection via delegation message hijacks Specialist | 6.8 | Medium | No Control Found | Input Validation | 6.8 | Medium |
| LLM-6 | LLM Agent Orchestrator | L1 | Server-side execution via LLM-emitted Tool Call Request params | 6.7 | Medium | No Control Found | Input Validation | 6.7 | Medium |
| OI-2 | LLM Agent Orchestrator | L1 | Server-side code/command execution via LLM-synthesized Tool Call parameters | 6.7 | Medium | No Control Found | Allowlist Validation | 6.7 | Medium |
| D-1 | Guardrails Service | L6 | Resource exhaustion via high-volume expensive prompts | 6.6 | Medium | No Control Found | Rate Limiting | 6.6 | Medium |
| E-5 | MCP Tool Server | L3 | Unauthorized tool calls gain Tool Server execution privileges | 6.6 | Medium | No Control Found | Access Control | 6.6 | Medium |
| AG-5 | MCP Tool Server | L3 | Tool call injection via LLM-influenced JSON-RPC parameters | 6.5 | Medium | No Control Found | Input Validation (Agentic) | 6.5 | Medium |
| AG-6 | MCP Tool Server | L3 | Runaway tool calls exhaust External API rate limits | 6.5 | Medium | No Control Found | Rate Limiting (Agentic) | 6.5 | Medium |
| LLM-2 | LLM Agent Orchestrator | L1 | Indirect prompt injection via adversarial Knowledge Base documents | 6.4 | Medium | No Control Found | Input Validation | 6.4 | Medium |
| E-4 | Inter-Agent Communication Channel | Unclassified | Channel forged elevated sender identity | 6.4 | Medium | No Control Found | Access Control | 6.4 | Medium |
| D-5 | MCP Tool Server | L3 | Connection pool exhaustion via high-volume tool calls | 6.3 | Medium | No Control Found | Rate Limiting | 6.3 | Medium |
| AG-2 | LLM Agent Orchestrator | L1 | Orchestrator-Specialist collusion for policy circumvention | 6.2 | Medium | No Control Found | Access Control (Agentic) | 6.2 | Medium |
| AG-4 | Inter-Agent Communication Channel | Unclassified | Agent-in-the-middle modifies delegation messages | 6.2 | Medium | No Control Found | Encryption / Access Control (Agentic) | 6.2 | Medium |
| E-3 | Specialist Agent | Unclassified | Forged delegation grants Specialist elevated permissions | 6.2 | Medium | No Control Found | Access Control | 6.2 | Medium |
| LLM-7 | LLM Agent Orchestrator | L1 | SSRF via LLM-synthesized URL in Tool Call Request | 6.1 | Medium | No Control Found | Input Validation | 6.1 | Medium |
| OI-3 | LLM Agent Orchestrator | L1 | SSRF via LLM-synthesized URL in Tool Call Request | 6.1 | Medium | No Control Found | Egress Control | 6.1 | Medium |
| AG-3 | Specialist Agent | Unclassified | Specialist cumulative prohibited tool call sequence | 6.0 | Medium | No Control Found | Access Control (Agentic) | 6.0 | Medium |
| LLM-3 | LLM Agent Orchestrator | L1 | Model theft via systematic API probing | 6.0 | Medium | No Control Found | Logging/Audit | 6.0 | Medium |
| D-2 | LLM Agent Orchestrator | L1 | Orchestrator inference pipeline exhaustion | 5.9 | Medium | No Control Found | Rate Limiting | 5.9 | Medium |
| D-3 | Specialist Agent | Unclassified | Specialist Agent resource exhaustion | 5.9 | Medium | No Control Found | Rate Limiting | 5.9 | Medium |
| D-4 | Inter-Agent Communication Channel | Unclassified | Message queue flooding drops coordination messages | 5.9 | Medium | No Control Found | Rate Limiting | 5.9 | Medium |
| LLM-10 | Specialist Agent | Unclassified | Server-side injection via tool result incorporation | 5.9 | Medium | No Control Found | Input Validation | 5.9 | Medium |
| T-2 | LLM Agent Orchestrator | L1 | Context window tampering via upstream data source | 5.8 | Medium | No Control Found | Input Validation | 5.8 | Medium |
| T-5 | MCP Tool Server | L3 | LLM-generated tool parameter allowlist bypass | 5.8 | Medium | No Control Found | Input Validation | 5.8 | Medium |
| R-1 | User | L7 | User denies submitting prompt; no non-repudiation control | 5.7 | Medium | No Control Found | Logging/Audit | 5.7 | Medium |
| S-3 | LLM Agent Orchestrator | L1 | Orchestrator identity not attested to Specialist | 5.6 | Medium | No Control Found | Authentication | 5.6 | Medium |
| S-5 | Inter-Agent Communication Channel | Unclassified | Channel no sender authentication | 5.6 | Medium | No Control Found | Authentication | 5.6 | Medium |
| S-6 | MCP Tool Server | L3 | Tool Server caller authentication bypass | 5.6 | Medium | No Control Found | Authentication | 5.6 | Medium |
| D-7 | Audit Logger | L5 | Audit Logger flooding attack | 5.5 | Medium | No Control Found | Rate Limiting | 5.5 | Medium |
| E-6 | Long-Running Learning Loop | Unclassified | Poisoned update escalates to model parameter control | 5.5 | Medium | No Control Found | Access Control | 5.5 | Medium |
| T-3 | Specialist Agent | Unclassified | Specialist delegation message tampering | 5.5 | Medium | No Control Found | Input Validation | 5.5 | Medium |
| T-4 | Inter-Agent Communication Channel | Unclassified | Messages modified in transit (AITM) | 5.5 | Medium | No Control Found | Input Validation | 5.5 | Medium |
| I-2 | LLM Agent Orchestrator | L1 | Context window leaked via injection/hallucination | 5.5 | Medium | No Control Found | Encryption / Input Validation | 5.5 | Medium |
| S-2 | Guardrails Service | L6 | Direct bypass to Orchestrator internal endpoint | 5.4 | Medium | No Control Found | Authentication | 5.4 | Medium |
| S-4 | Specialist Agent | Unclassified | Specialist impersonates Orchestrator | 5.4 | Medium | No Control Found | Authentication | 5.4 | Medium |
| S-8 | External API | Unclassified | DNS hijacking / BGP attack on External API | 5.4 | Medium | No Control Found | Authentication | 5.4 | Medium |
| LLM-4 | LLM Agent Orchestrator | L1 | Training data poisoning via Learning Loop | 5.3 | Medium | No Control Found | Input Validation / Logging/Audit | 5.3 | Medium |
| LLM-9 | Specialist Agent | Unclassified | Specialist self-poisoning via audit log loop | 5.3 | Medium | No Control Found | Input Validation / Logging/Audit | 5.3 | Medium |
| LLM-11 | Long-Running Learning Loop | Unclassified | Systematic audit log poisoning temporal attack | 5.3 | Medium | No Control Found | Input Validation / Logging/Audit | 5.3 | Medium |
| LLM-12 | Long-Running Learning Loop | Unclassified | Model theft via update artifact monitoring | 5.3 | Medium | No Control Found | Logging/Audit | 5.3 | Medium |
| I-6 | Knowledge Base | L2 | Knowledge Base corpus exfiltration | 5.3 | Medium | No Control Found | Encryption / Rate Limiting | 5.3 | Medium |
| D-6 | Knowledge Base | L2 | Vector search DoS | 5.3 | Medium | No Control Found | Rate Limiting | 5.3 | Medium |
| AG-7 | Long-Running Learning Loop | Unclassified | Temporal autonomy expansion via training data | 5.1 | Medium | No Control Found | Access Control (Agentic) | 5.1 | Medium |
| S-7 | Long-Running Learning Loop | Unclassified | Training signal source integrity not verified | 5.1 | Medium | No Control Found | Authentication | 5.1 | Medium |
| I-4 | Inter-Agent Communication Channel | Unclassified | Inter-agent messages observable | 5.1 | Medium | No Control Found | Encryption | 5.1 | Medium |
| I-7 | Audit Logger | L5 | Audit Logger unauthorized read exposure | 4.9 | Medium | No Control Found | Encryption / Access Control | 4.9 | Medium |
| I-3 | Specialist Agent | Unclassified | Specialist result sensitive context leakage | 4.8 | Medium | No Control Found | Encryption | 4.8 | Medium |
| I-5 | MCP Tool Server | L3 | Tool results PII logging | 4.8 | Medium | No Control Found | Encryption | 4.8 | Medium |
| T-1 | Guardrails Service | L6 | Guardrails filtering rule modification | 4.8 | Medium | No Control Found | Input Validation / Access Control | 4.8 | Medium |
| T-7 | Audit Logger | L5 | Audit log tampering | 4.8 | Medium | No Control Found | Input Validation / Access Control | 4.8 | Medium |
| I-1 | Guardrails Service | L6 | Guardrails rejection reason leakage | 4.7 | Medium | No Control Found | Encryption | 4.7 | Medium |
| T-6 | Knowledge Base | L2 | KB corpus poisoning via unauthorized write | 4.7 | Medium | No Control Found | Access Control | 4.7 | Medium |
| AGP-01 | LLM Agent Orchestrator | L1 | Multi-agent emergent behavior | 4.6 | Medium | No Control Found | Logging/Audit (Agentic) | 4.6 | Medium |
| D-8 | Long-Running Learning Loop | Unclassified | Learning Loop training signal flooding | 4.6 | Medium | No Control Found | Rate Limiting | 4.6 | Medium |
| T-8 | Long-Running Learning Loop | Unclassified | Training signal temporal poisoning | 4.3 | Medium | No Control Found | Input Validation | 4.3 | Medium |
| I-8 | Long-Running Learning Loop | Unclassified | Training data extraction via model memorization | 4.3 | Medium | No Control Found | Encryption | 4.3 | Medium |
| R-8 | External API | Unclassified | External API provider denies response | 4.1 | Medium | No Control Found | Logging/Audit | 4.1 | Medium |

### Low (residual < 4.0)

| ID | Component | MAESTRO Layer | Threat | Inherent | Inherent Sev | Control Status | Control Category | Residual | Residual Sev |
|----|-----------|---------------|--------|----------|--------------|----------------|-----------------|----------|--------------|
| R-3 | LLM Agent Orchestrator | L1 | Orchestrator action repudiation | 3.9 | Low | No Control Found | Logging/Audit | 3.9 | Low |
| R-2 | Guardrails Service | L6 | Guardrails filtering decision repudiation | 3.5 | Low | No Control Found | Logging/Audit | 3.5 | Low |
| R-4 | Specialist Agent | Unclassified | Specialist action repudiation | 3.5 | Low | No Control Found | Logging/Audit | 3.5 | Low |
| R-6 | MCP Tool Server | L3 | Tool Server invocation repudiation | 3.5 | Low | No Control Found | Logging/Audit | 3.5 | Low |
| R-7 | Long-Running Learning Loop | Unclassified | Learning Loop model update repudiation | 3.3 | Low | No Control Found | Logging/Audit | 3.3 | Low |
| R-5 | Inter-Agent Communication Channel | Unclassified | Channel message delivery repudiation | 3.3 | Low | No Control Found | Logging/Audit | 3.3 | Low |

---

## 3. Control Details

_No compensating controls detected in the target codebase. The target is a fictional reference architecture (`examples/agentic-app/`) consisting solely of `architecture.md` (Mermaid flowchart + Component Summary tables). No implementation files were found under any of the 10 architectural components:_

- User (external entity -- no server-side code expected)
- Guardrails Service
- LLM Agent Orchestrator
- Specialist Agent
- Inter-Agent Communication Channel
- MCP Tool Server
- Knowledge Base
- Audit Logger
- Long-Running Learning Loop
- External API (external entity -- no server-side code expected)

_No source files matched the pattern indicators for any of the 8 standard control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) or the 3 Feature-201 patterns (output sanitization, allowlist validation, egress control). The threat model's per-finding Mitigation column and Section 4 remediations describe the controls that an implementor would build; this analysis confirms none are currently present._

---

## 4. Recommendations

70 recommendations, grouped by inherent severity band. Processed in descending composite-score order within each band.

### High-severity recommendations (composite 7.0 - 8.9)

**S-1 (User; composite 7.9)** -- Implement session authentication with replay protection for the User->Guardrails boundary. Build short-lived JWT or opaque session tokens (5-15 minute access token lifetime, refresh-token rotation) bound to client IP and device fingerprint; require MFA enrollment for all users; maintain a token revocation list checked on every request. Suggested location: new `auth/` directory (e.g., `auth/session-middleware.{ts,py}`, `auth/mfa-verifier.{ts,py}`, `auth/token-revocation-store.{ts,py}`). Reference implementations: `jsonwebtoken` + `express-session` + `redis` for Node.js; `authlib` + `flask-login` + `redis` for Python; `Spring Security` for JVM; `django.contrib.auth` for Django. This control addresses the threat that a replayed token grants full user-session access at the untrusted-zone boundary. Effort: **High** (new auth subsystem).

**E-1 (Guardrails Service; composite 7.3)** -- Implement defense-in-depth prompt injection detection at the Orchestrator layer, independent of Guardrails. Do NOT treat Guardrails-passed input as implicitly trusted -- enforce a separate input-classification step on the Orchestrator (policy engine, second-stage classifier, or LLM-based guard with adversarial training set). Apply least-privilege on Guardrails->Orchestrator data flows. Suggested location: new `orchestrator/prompt-guard.{ts,py}` module invoked before every Orchestrator LLM call. Reference implementations: open-source prompt-guard models (Meta Prompt-Guard, NVIDIA NeMo Guardrails), `semantic-router`, custom classifier hooks. Effort: **High** (new subsystem and policy engine).

**E-2 (LLM Agent Orchestrator; composite 7.2)** -- Implement per-session scoped permissions for the Orchestrator enforced by the Tool Server and KB independently. Determine the session's permitted tool set and KB scope at authentication time; the Orchestrator MUST NOT grant itself elevated capabilities at runtime. Apply step-up authentication for high-privilege operations (bulk export, external writes, admin tools). Suggested location: new `authz/session-scope.{ts,py}` capturing scope at auth; enforce in `tool-server/authorize-invocation.{ts,py}` and `kb/authorize-query.{ts,py}`. Reference implementations: `casbin`, `casl`, `oso`, `@nestjs/passport` guards, `Spring Security` method-level security. Effort: **High** (cross-cutting authorization architecture).

**LLM-1 (LLM Agent Orchestrator; composite 7.2)** -- Implement input validation to detect direct prompt injection patterns. Combine structural checks (reject known injection markers like "ignore previous instructions", role-override syntax, encoded payloads) with model-based classification (Prompt-Guard, adversarial-trained classifier). Apply BEFORE the prompt reaches the Orchestrator LLM. Suggested location: `orchestrator/prompt-sanitizer.{ts,py}` alongside the injection-detection module built for E-1. Reference implementations: `Meta Prompt-Guard`, `NeMo Guardrails`, `Rebuff`, regex+classifier composite. Effort: **Medium**.

**LLM-5 / OI-1 (LLM Agent Orchestrator; composite 7.2)** -- Implement output sanitization and context-aware encoding on all Orchestrator LLM responses flowing to the User browser. Two controls are required in series: (1) server-side output sanitization stripping dangerous HTML tags/attributes/JavaScript from the LLM-generated text; (2) a strict Content-Security-Policy response header (`default-src 'self'; script-src 'self' 'nonce-<nonce>'; object-src 'none'; base-uri 'self'`) preventing any unsanitized DOM sinks from executing. On the client render path, use `textContent` (not `innerHTML`) by default; if a Markdown/HTML surface is required, pass the output through `DOMPurify` first. React surfaces MUST render as `{value}` JSX expressions (never `dangerouslySetInnerHTML`). Suggested location: `orchestrator/response-sanitizer.{ts,py}` on the server; `render/safe-html.tsx` on the client; `http/security-headers.{ts,py}` for CSP. Reference implementations: `DOMPurify`, `sanitize-html`, `bleach`, `helmet` with `contentSecurityPolicy` directive. Effort: **Medium** (server-side sanitizer + CSP middleware).

### Medium-severity recommendations (composite 4.0 - 6.9)

**AG-1 (LLM Agent Orchestrator; composite 6.9)** -- Implement a scope-enforcement layer validating every proposed Orchestrator action against the user session's permitted scope before execution. Add human-in-the-loop confirmation for high-impact operations. Apply a supervised-autonomy model (Orchestrator proposes action plan; policy engine approves/rejects). Suggested location: `orchestrator/action-scope-validator.{ts,py}` + `policy-engine/`. Effort: **High**.

**LLM-8 (Specialist Agent; composite 6.8)** -- Validate and sanitize all delegation task payloads received by the Specialist. Apply HMAC or digital signature verification on every received delegation message (see S-5 / T-3 / T-4 for the complementary channel-layer controls). Reject tasks with unexpected structural patterns (new tool targets, exfiltration URLs). Suggested location: `specialist/delegation-validator.{ts,py}`. Effort: **Medium**.

**LLM-6 / OI-2 (LLM Agent Orchestrator; composite 6.7)** -- Implement allowlist validation for every Tool Call Request parameter emitted by the Orchestrator LLM. Reject unknown tool names; for allowlisted tools, enforce per-parameter JSON Schema against a signed-off schema catalog (tool name enumeration, type, length, regex, enumerable values for enum parameters). For SQL contexts, use parameterized queries (`SQLAlchemy text().bindparams()`, `psycopg2 cursor.execute(sql, params)`, Prisma template literals). For shell contexts, use `subprocess.run([cmd, arg1, arg2], shell=False)`. NEVER interpolate LLM-emitted text into shell or SQL. Suggested location: `tool-server/parameter-validator.{ts,py}` + `tool-server/tool-schema-catalog.yaml`. Reference implementations: `zod`, `joi`, `pydantic`, `ajv`. Effort: **Medium**.

**D-1 (Guardrails Service; composite 6.6)** -- Implement per-IP and per-session rate limiting at network ingress BEFORE Guardrails. Apply a computational complexity budget per prompt; reject over-budget prompts. Use async processing queues with backpressure. Suggested location: reverse-proxy / ingress controller + `guardrails/rate-limiter.{ts,py}`. Reference implementations: `express-rate-limit`, `rate-limiter-flexible`, `slowapi`, `flask-limiter`, NGINX `limit_req`. Effort: **Medium**.

**E-5 (MCP Tool Server; composite 6.6)** -- Implement zero-trust authorization at the Tool Server: every tool invocation authorized against the originating session scope, independent of caller identity. Use tool-specific service accounts with least-privilege external permissions. Rotate API credentials regularly (KMS-managed). Suggested location: `tool-server/invocation-authorizer.{ts,py}`. Effort: **High**.

**AG-5 (MCP Tool Server; composite 6.5)** -- Apply strict parameter validation + allowlist enforcement on all JSON-RPC tool invocations (see LLM-6/OI-2 for the complementary control at the Orchestrator side). Reject metacharacters and unexpected structural elements before tool dispatch. Suggested location: `tool-server/parameter-validator.{ts,py}`. Effort: **Medium**.

**AG-6 (MCP Tool Server; composite 6.5)** -- Implement per-caller and per-tool rate limiting at the Tool Server with connection-pool overflow rejection (not queuing). Apply per-session tool-call budgets and circuit breakers. Suggested location: `tool-server/rate-limiter.{ts,py}` + `tool-server/circuit-breaker.{ts,py}`. Reference implementations: `opossum`, `cockatiel`, `resilience4j`. Effort: **Medium**.

**LLM-2 (LLM Agent Orchestrator; composite 6.4)** -- Apply document-level integrity checks (hash + signature at KB write time; verify at retrieval time) on all retrieved KB documents. Regularly scan the corpus for adversarial content patterns. Treat retrieved documents as untrusted input at context-injection time. Suggested location: `kb/document-integrity.{ts,py}` + `orchestrator/context-sanitizer.{ts,py}`. Effort: **Medium**.

**E-4 (Inter-Agent Communication Channel; composite 6.4)** -- Enforce sender identity authentication at the Channel layer: every message carries a verifiable signed token or mTLS certificate; Channel rejects unverifiable messages before routing. Suggested location: `channel/sender-authenticator.{ts,py}`. Reference implementations: `SPIFFE/SPIRE`, mTLS with SPIFFE IDs, per-message ED25519 signatures. Effort: **Medium**.

**D-5 (MCP Tool Server; composite 6.3)** -- Implement per-caller and per-tool rate limits; enforce connection-pool limit with overflow rejection. See AG-6 above. Effort: **Medium**.

**AG-2 (LLM Agent Orchestrator; composite 6.2)** -- Implement cross-agent rate limits and coordination throttles at the Channel. Log all inter-agent coordination patterns to the Audit Logger. Apply a policy engine that evaluates the combined effect of multi-agent action sequences. Enforce per-agent AND per-session action budgets independently. Suggested location: `channel/coordination-throttle.{ts,py}` + policy engine built for AG-1. Effort: **High**.

**AG-4 (Inter-Agent Communication Channel; composite 6.2)** -- Apply end-to-end message integrity protection with digital signatures at the channel layer, complemented by per-message sequence numbers and monotonic counters to detect dropped/reordered messages. Suggested location: `channel/message-signer.{ts,py}`. Effort: **Medium**.

**E-3 (Specialist Agent; composite 6.2)** -- The Tool Server MUST verify the Specialist's claimed permission scope against the originating user session's authorization at every invocation. Delegation messages MUST be validated against a central session-authorization record -- not self-signed by the Orchestrator alone. Suggested location: `tool-server/specialist-scope-checker.{ts,py}` + `authz/session-authorization-store.{ts,py}`. Effort: **High**.

**LLM-7 / OI-3 (LLM Agent Orchestrator; composite 6.1)** -- Implement egress control with a URL allowlist + egress firewall blocking internal addresses (including the cloud metadata endpoint `169.254.169.254`, RFC1918 private ranges, `127.0.0.0/8`, `::1`, link-local addresses). For any LLM-synthesized URL, parse and verify scheme is `https`, host is in the allowlist, and port is expected (443). Apply at the Tool Server BEFORE any `fetch()` or HTTP-client invocation. Suggested location: `tool-server/url-allowlist.{ts,py}` + network-layer egress firewall (VPC egress rules, eBPF filter, Istio egress). Reference implementations: explicit URL parse + `ipaddress.ip_address(host).is_private` check, `aws:SourceVpc` IAM conditions, Cilium/Calico egress policies. Effort: **Medium** (url validator) + **High** (network egress rules).

**AG-3 (Specialist Agent; composite 6.0)** -- Enforce per-session cumulative action budgets at the Tool Server (see E-3, AG-2). Policy engine evaluates sequences of tool calls against prohibited-sequence patterns. Suggested location: `policy-engine/sequence-evaluator.{ts,py}`. Effort: **High**.

**LLM-3 (LLM Agent Orchestrator; composite 6.0)** -- Implement anomaly detection on query patterns (volume, entropy, semantic novelty) consistent with model-extraction probing. Rate-limit by session and apply step-up authentication on high-volume queriers. Log all queries with classification scores to the Audit Logger. Suggested location: `orchestrator/anomaly-detector.{ts,py}` + `observability/query-log-analyzer.{ts,py}`. Effort: **Medium**.

**D-2 (LLM Agent Orchestrator; composite 5.9)** -- Apply per-session token budgets, hard context-window limits, circuit breakers on tool invocation chains (maximum recursion depth), request queuing with priority tiers, and capacity-based load shedding. Suggested location: `orchestrator/resource-budgeter.{ts,py}`. Effort: **Medium**.

**D-3 (Specialist Agent; composite 5.9)** -- Apply per-task execution-time limits and resource budgets on Specialist invocations. Implement task-queue depth limits with backpressure. Orchestrator health-check probes to detect overload. Suggested location: `specialist/task-budgeter.{ts,py}`. Effort: **Medium**.

**D-4 (Inter-Agent Communication Channel; composite 5.9)** -- Message-queue depth limits + per-sender rate limits at the Channel. Backpressure responses when queue approaches capacity. Queue-depth metrics with alerts. Suggested location: `channel/queue-limiter.{ts,py}`. Effort: **Medium**.

**LLM-10 (Specialist Agent; composite 5.9)** -- Treat tool results as untrusted input; apply output encoding and schema validation before incorporation into the Specialist's context or emitted downstream. Suggested location: `specialist/tool-result-sanitizer.{ts,py}`. Effort: **Medium**.

**T-2 (LLM Agent Orchestrator; composite 5.8)** -- Validate integrity of all context sources before injection into the Orchestrator's context window: hash retrieved KB documents at write/read; HMAC-verify aggregated results from Channel; treat tool results as untrusted and apply output encoding. Suggested location: `orchestrator/context-integrity-validator.{ts,py}`. Effort: **Medium**.

**T-5 (MCP Tool Server; composite 5.8)** -- Per-tool JSON Schema enforcement + allowlisted parameter values + metacharacter rejection. See LLM-6/OI-2. Effort: **Medium**.

**R-1 (User; composite 5.7)** -- Implement client-side request signing (user-held private key or WebCrypto-derived session key). Log signed request hash in the Audit Logger alongside session identity. Timestamped immutable audit entries establish proof of submission. Suggested location: client SDK `sdk/request-signer.ts` + server `audit/request-hash-logger.{ts,py}`. Effort: **High** (client SDK change).

**S-3 (LLM Agent Orchestrator; composite 5.6)** -- Authenticate all Orchestrator->Channel messages via HMAC or asymmetric signing with per-session keys. Specialist verifies signature before acting. Nonce/replay-prevention field in every message. Suggested location: `orchestrator/channel-signer.{ts,py}` + `specialist/channel-verifier.{ts,py}`. Effort: **Medium**.

**S-5 (Inter-Agent Communication Channel; composite 5.6)** -- ED25519 or HMAC-SHA256 per-message digital signatures on all channel messages. Bind sender identity to envelope. Reject unsigned/unverifiable messages. Suggested location: `channel/envelope-signer.{ts,py}`. Effort: **Medium**.

**S-6 (MCP Tool Server; composite 5.6)** -- Caller authentication on all JSON-RPC endpoints via signed caller token or mTLS certificate. Tool Server verifies caller identity before executing any tool invocation. Suggested location: `tool-server/caller-authenticator.{ts,py}`. Reference implementations: `SPIFFE/SPIRE`, `Istio` mTLS. Effort: **Medium**.

**D-7 (Audit Logger; composite 5.5)** -- Decouple Audit Logger writes from critical path via async write queues; per-source write rate limits; log rotation and capacity management; alerts on abnormal write rates. Suggested location: `audit/async-writer.{ts,py}` + `audit/rate-limiter.{ts,py}`. Effort: **Medium**.

**E-6 (Long-Running Learning Loop; composite 5.5)** -- HSM-backed signing of every model update package; Orchestrator and Specialist verify update signature before applying; staged rollout with A/B testing and behavioral regression checks. Suggested location: `learning-loop/update-signer.{ts,py}` + `orchestrator/update-verifier.{ts,py}` + `observability/regression-checker.{ts,py}`. Effort: **High**.

**T-3 (Specialist Agent; composite 5.5)** -- HMAC or digital signature verification on every delegation message payload; reject tasks with unexpected structural patterns. See LLM-8. Effort: **Medium**.

**T-4 (Inter-Agent Communication Channel; composite 5.5)** -- End-to-end digital signatures, sequence numbers, monotonic counters. See AG-4. Effort: **Medium**.

**I-2 (LLM Agent Orchestrator; composite 5.5)** -- Output scrubbing on Orchestrator responses before HTTPS transmission: detect and redact sensitive-data markers (system prompt preambles, KB doc IDs, tool-response metadata). Separate response-auditor step reviews output before sending. Suggested location: `orchestrator/response-scrubber.{ts,py}` + `orchestrator/response-auditor.{ts,py}`. Effort: **Medium**.

**S-2 (Guardrails Service; composite 5.4)** -- Enforce mutual TLS between Guardrails and Orchestrator. Service-mesh identity (SPIFFE/SPIRE). Orchestrator endpoint never exposed to unauthenticated internal callers. Suggested location: service-mesh config + `mtls/client-cert-verifier.{ts,py}`. Effort: **Medium**.

**S-4 (Specialist Agent; composite 5.4)** -- Sign all Specialist->Channel messages with Specialist identity key; Orchestrator verifies origin before incorporating into context. Suggested location: `specialist/result-signer.{ts,py}` + `orchestrator/result-verifier.{ts,py}`. Effort: **Medium**.

**S-8 (External API; composite 5.4)** -- Certificate pinning on outbound HTTPS from Tool Server to External API. Verify leaf certificate CN/SAN against expected provider identity. HSTS preloading where available. Suggested location: `tool-server/external-api-client.{ts,py}` with pinning config. Effort: **Low**.

**LLM-4 (LLM Agent Orchestrator; composite 5.3)** -- Training data provenance attestation (per-log-entry origin signature), anomaly detection on training-signal distributions, per-source influence limits, gradient clipping, differential privacy during training. Suggested location: `learning-loop/provenance-verifier.{ts,py}` + `learning-loop/anomaly-detector.{ts,py}`. Effort: **High**.

**LLM-9 (Specialist Agent; composite 5.3)** -- Same provenance-attestation controls as LLM-4; additionally apply feedback-loop detection (flag training signals whose source is the Specialist's own output). Effort: **High**.

**LLM-11 (Long-Running Learning Loop; composite 5.3)** -- Same as LLM-4 applied at the Learning Loop ingestion boundary. Effort: **High**.

**LLM-12 (Long-Running Learning Loop; composite 5.3)** -- Restrict observability access to the Learning Loop's output artifacts to a narrow set of privileged accounts. Log all read accesses. Monitor for enumeration patterns. Suggested location: `learning-loop/artifact-access-control.{ts,py}`. Effort: **Medium**.

**I-6 (Knowledge Base; composite 5.3)** -- Per-query result limits + per-session query budgets. Context-aware authorization restricting retrieval to session-permitted scope. Monitor anomalous query patterns (high-volume, exhaustive retrievals). Suggested location: `kb/query-budgeter.{ts,py}` + `kb/scope-authorizer.{ts,py}`. Effort: **Medium**.

**D-6 (Knowledge Base; composite 5.3)** -- Per-session query rate limits + complexity bounds on vector search; result caching for frequent queries; reject queries exceeding complexity thresholds. Suggested location: `kb/complexity-limiter.{ts,py}`. Effort: **Medium**.

**AG-7 (Long-Running Learning Loop; composite 5.1)** -- Behavioral regression testing of post-update models against a fixed evaluation set that includes autonomy-boundary probes. Staged rollout. Reject updates exceeding autonomy drift threshold. Suggested location: `observability/autonomy-drift-evaluator.{ts,py}`. Effort: **High**.

**S-7 (Long-Running Learning Loop; composite 5.1)** -- Cryptographic signing of every training signal batch at Audit Logger emission; Learning Loop verifies signature before ingestion. Provenance attestation on all training data. Suggested location: `audit/batch-signer.{ts,py}` + `learning-loop/ingestion-verifier.{ts,py}`. Effort: **Medium**.

**I-4 (Inter-Agent Communication Channel; composite 5.1)** -- Per-message E2E encryption (keys derived from sender-receiver pair, not channel transport security alone). Strict ACLs on channel infrastructure preventing unauthorized reads. Suggested location: `channel/e2e-encryption.{ts,py}`. Effort: **Medium**.

**I-7 (Audit Logger; composite 4.9)** -- Strict read ACLs limiting to incident-response and analytics service accounts; envelope encryption at rest with per-batch keys in KMS; audit of all log-store read access. Suggested location: `audit/read-access-control.{ts,py}` + KMS integration. Effort: **Medium**.

**I-3 (Specialist Agent; composite 4.8)** -- Data minimization on delegation messages: Orchestrator MUST NOT include sensitive context unless strictly required. Output scrubbing on Specialist results before logging/forwarding. Classify and label sensitive fields in inter-agent messages. Suggested location: `orchestrator/delegation-minimizer.{ts,py}` + `specialist/result-scrubber.{ts,py}`. Effort: **Medium**.

**I-5 (MCP Tool Server; composite 4.8)** -- Structured logging with field-level classification; PII/sensitive fields hashed or tokenized before writing; log-before-hash policy. Suggested location: `tool-server/log-sanitizer.{ts,py}`. Effort: **Medium**.

**T-1 (Guardrails Service; composite 4.8)** -- Configuration-as-code with cryptographic commit signing for Guardrails rule updates; dual approval for rule changes; audit every rule modification; alert on rule relaxation. Suggested location: `guardrails/rule-change-gate.{ts,py}` + git-commit signing policy. Effort: **Medium**.

**T-7 (Audit Logger; composite 4.8)** -- Append-only store (no update/delete); Merkle-tree hash of log batches detecting post-write modification; external hash-chain store that cannot be altered without detection. Suggested location: `audit/append-only-store.{ts,py}` + `audit/merkle-tree.{ts,py}`. Effort: **High**.

**I-1 (Guardrails Service; composite 4.7)** -- Return generic rejection messages to the User that do not reveal the specific rule triggered. Log detailed rejection reason internally only. Suggested location: `guardrails/rejection-formatter.{ts,py}`. Effort: **Low**.

**T-6 (Knowledge Base; composite 4.7)** -- Write access controls with least-privilege service accounts; all writes logged with immutable audit trails; document-level hash + signature at write; verify at retrieval. Regular corpus scanning for adversarial patterns. Suggested location: `kb/write-gate.{ts,py}` + `kb/integrity-verifier.{ts,py}`. Effort: **Medium**.

**AGP-01 (LLM Agent Orchestrator; composite 4.6)** -- Emergent-behavior observability: log all cross-agent coordination events to the Audit Logger and apply a policy engine that evaluates combined effects of multi-agent action sequences. See AG-2. Effort: **High**.

**D-8 (Long-Running Learning Loop; composite 4.6)** -- Training-run scheduling with resource quotas (CPU, memory, time-to-completion); training-data volume cap per scheduled run; separate compute pools for Learning Loop vs. inference. Suggested location: `learning-loop/scheduler-quotas.{ts,py}`. Effort: **Medium**.

**T-8 (Long-Running Learning Loop; composite 4.3)** -- Same provenance + anomaly detection + gradient clipping + differential privacy controls as LLM-4/LLM-11. Effort: **High**.

**I-8 (Long-Running Learning Loop; composite 4.3)** -- Differential privacy during training to limit per-example memorization; PII de-identification on training signals before ingestion; canary injection to detect memorization in post-training evaluation. Suggested location: `learning-loop/dp-trainer.{ts,py}` + `learning-loop/deid-preprocessor.{ts,py}`. Effort: **High**.

**R-8 (External API; composite 4.1)** -- Log all External API responses with content hash and timestamp upon receipt. Request/response signing protocols where supported. Suggested location: `tool-server/external-api-logger.{ts,py}`. Effort: **Low**.

### Low-severity recommendations (composite < 4.0)

**R-3 (LLM Agent Orchestrator; composite 3.9)** -- Log every Orchestrator action (delegation messages, tool call requests, response generation) with action type + content hash + session/request ID + monotonic sequence number + Orchestrator service key signature. Log BEFORE execution. Suggested location: `orchestrator/action-logger.{ts,py}`. Effort: **Medium**.

**R-2 (Guardrails Service; composite 3.5)** -- Log all Guardrails filtering decisions (pass AND reject) with prompt hash + rule applied + monotonic sequence number. Atomic write before returning filtering response. Suggested location: `guardrails/decision-logger.{ts,py}`. Effort: **Medium**.

**R-4 (Specialist Agent; composite 3.5)** -- Log every Specialist action with content hashes and Specialist service key signature, before execution. Suggested location: `specialist/action-logger.{ts,py}`. Effort: **Medium**.

**R-6 (MCP Tool Server; composite 3.5)** -- Log every JSON-RPC tool invocation with calling agent identity (verified from caller token), tool name, parameter hashes, and output hash. Atomic write before execution. Suggested location: `tool-server/invocation-logger.{ts,py}`. Effort: **Medium**.

**R-7 (Long-Running Learning Loop; composite 3.3)** -- Log every model update event: training dataset hash, parameter diff hash, update timestamp, approval signature. Model versioning with signed manifests. Store provenance records in immutable externally-verifiable store. Suggested location: `learning-loop/update-provenance-logger.{ts,py}`. Effort: **Medium**.

**R-5 (Inter-Agent Communication Channel; composite 3.3)** -- Message-delivery ACKs including content-hash of received message; store ACK records in Audit Logger; flag mismatched sender/receiver hashes for investigation. Suggested location: `channel/ack-logger.{ts,py}`. Effort: **Low**.

---

## 5. Residual Risk Summary

### Aggregate Risk

| Metric | Value |
|--------|-------|
| Total inherent risk | 395.6 |
| Total residual risk | 395.6 |
| Risk delta | 0.0 |
| Overall reduction percentage | 0.0% |

Because no controls are present in the fictional target codebase, residual risk equals inherent risk for every finding. A real implementation of the recommendations in Section 4 would produce the following per-control-status reductions at P0 binary effectiveness: `found` -> 0.50, `partial` -> 0.25, `missing` -> 0.00.

### Severity Distribution Comparison (Inherent vs Residual)

| Severity Band | Inherent Count | Residual Count | Shift |
|---------------|---------------|---------------|-------|
| Critical | 0 | 0 | 0 |
| High | 6 | 6 | 0 |
| Medium | 58 | 58 | 0 |
| Low | 6 | 6 | 0 |
| **Total** | **70** | **70** | **0** |

### Per-Severity-Band Shifts

No severity band shifts occurred -- every finding retained its inherent band because every `reduction_factor` is 0.00.

### Reduction Factor Reference (P0 Binary Model)

| Control Status | Reduction Factor | Residual = Inherent x |
|---------------|-----------------|----------------------|
| Control Found (implemented) | 0.50 | 0.50 |
| Partial Control | 0.25 | 0.75 |
| No Control Found | 0.00 | 1.00 |

**P1 note**: Future versions may refine the reduction model to weight controls by confidence level (High/Medium/Low) and by the number of control categories satisfied for multi-category threats (Spoofing, Agentic). The P0 binary model is the current baseline.

---

## 6. Methodology

### Analysis Pipeline

1. **Phase 1 -- Parse Input**: Parsed 70 scored findings from `risk-scores.md` canonical input. Every finding has required fields (id, component, category, composite_score, severity_band, dimensional scores, governance fields). No duplicates, no score-range violations, no severity-band mismatches. Correlation groups CG-1 through CG-5 preserved.
2. **Phase 2 -- Discover Codebase**: Target path `/Users/david/Projects/tachi/examples/agentic-app/`. Architecture document provided (`architecture.md`, Mermaid format). 10 components identified (User, Guardrails Service, LLM Agent Orchestrator, Specialist Agent, Inter-Agent Communication Channel, MCP Tool Server, Knowledge Base, Audit Logger, Long-Running Learning Loop, External API). Zero implementation files discovered under any component (the target is a reference architecture without source code). File read budget of 200 unused.
3. **Phase 3 -- Detect Controls**: Scanned zero source files. Every component recorded `detected: false` for all 8 standard control categories and the 3 Feature-201 patterns (output sanitization, allowlist validation, egress control).
4. **Phase 4 -- Map & Classify**: Every scored finding received `control_status: missing`, `reduction_factor: 0.00`, `confidence: null`. Classification is exhaustive -- all 70 findings classified, matching the Phase-1 count.
5. **Phase 5 -- Recommend & Calculate Residual Risk**: All 70 `missing` findings received a recommendation and effort estimate. Residual score for every finding equals its composite score (reduction_factor 0.00). Severity band preserved across all findings.
6. **Phase 6 -- Generate Output**: Produced `compensating-controls.md` (this file) and `compensating-controls.sarif` in the output directory. Cross-format consistency verified: 70 coverage matrix rows, 70 SARIF results, identical control statuses, identical residual scores.

### Control Categories Evaluated

Per the STRIDE-to-control-category mapping in `.claude/skills/tachi-control-analysis/references/control-categories.md`: Authentication, Input Validation, Rate Limiting, Encryption, Logging/Audit, CSRF Protection, CSP/Security Headers, Access Control. Plus Feature-201 extensions for OI findings: Output Sanitization and Encoding, Allowlist Validation, Egress Control.

### Reference Constants

- Scoring weights: CVSS 0.35 / Exploit 0.30 / Scale 0.15 / Reach 0.20 (from upstream `risk-scores.md`)
- Severity thresholds: Critical >= 9.0, High 7.0-8.9, Medium 4.0-6.9, Low < 4.0
- Reduction model: P0 binary (found=0.50, partial=0.25, missing=0.00)
- File read budget: 200 files (consumed: 1 -- architecture.md only)

### Known Limitations

- Target codebase is a reference architecture. Expected zero-implemented outcome; recommendations are authoritative design guidance but cannot be validated against running code.
- The OI-finding control categories (Output Sanitization and Encoding, Allowlist Validation, Egress Control) are Feature-201 extensions to the 8-category taxonomy. They are treated as first-class classifications in this report but do not yet have corresponding pattern indicators in the `control-categories.md` reference. An ADR or schema extension may be warranted if OI-control detection becomes a recurring requirement.
- Residual risk reduction for `found`/`partial` states would be computed against the P0 binary reduction model; the fictional target exercises only the `missing` arm of that model.
