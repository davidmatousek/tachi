# Compensating Controls Report

---

```yaml
---
schema_version: "1.0"
date: "2026-03-28"
source_file: "risk-scores.md"
target_path: "examples/agentic-app"
classification: "security"
---
```

---

## 1. Executive Summary

**34** threats analyzed | **8** Control Found | **13** Partial Control | **13** No Control Found

**Coverage**: 23.5% Found | 38.2% Partial | 38.2% Missing

**Risk Reduction**: 214.5 inherent -> 156.8 residual (**26.9%** reduction)

**Highest-Risk Unmitigated Finding**: LLM-1 — LLM Agent Orchestrator — Composite 8.3 (High)

| Metric | Value |
|--------|-------|
| Analysis date | 2026-03-28 |
| Source file | `risk-scores.md` |
| Target codebase | `examples/agentic-app` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 8 | 23.5% |
| Partial Control | 13 | 38.2% |
| No Control Found | 13 | 38.2% |
| **Total** | **34** | **100%** |

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### Critical Residual Severity

| Threat ID | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| LLM-1 | LLM Agent Orchestrator | Adversarial prompts override system prompt | 8.3 | High | No Control Found | 8.3 | Critical |

### High Residual Severity

| Threat ID | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | User | Attacker impersonates legitimate user by replaying tokens | 7.9 | High | Partial Control | 5.9 | High |
| E-2 | LLM Agent Orchestrator | Attacker escalates to admin tool access through prompt injection | 7.6 | High | No Control Found | 7.6 | High |
| AG-1 | LLM Agent Orchestrator | Orchestrator executes consequential actions without human approval | 7.6 | High | No Control Found | 7.6 | High |
| E-3 | MCP Tool Server | User invokes admin tool endpoints by manipulating tool_name | 7.5 | High | No Control Found | 7.5 | High |
| D-1 | Guardrails Service | Attacker floods Guardrails Service to exhaust CPU | 7.4 | High | Partial Control | 5.6 | High |
| D-2 | LLM Agent Orchestrator | Attacker sends concurrent max-length prompts | 7.3 | High | No Control Found | 7.3 | High |
| S-3 | LLM Agent Orchestrator | Attacker forges tool call requests to MCP Tool Server | 7.2 | High | Partial Control | 5.4 | High |
| T-3 | MCP Tool Server | Attacker manipulates JSON-RPC parameters in transit | 7.1 | High | No Control Found | 7.1 | High |
| AG-3 | MCP Tool Server | MCP Tool Server exposes all tools without per-agent scoping | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-2 | Guardrails Service | Attacker bypasses Guardrails by directly accessing Orchestrator | 6.7 | Medium | Partial Control | 5.0 | Medium |
| E-1 | Guardrails Service | Attacker bypasses Guardrails via alternate route | 6.6 | Medium | Partial Control | 5.0 | Medium |
| D-3 | MCP Tool Server | Resource exhaustion through concurrent tool calls | 6.4 | Medium | Partial Control | 4.8 | Medium |
| AG-4 | MCP Tool Server | Tool call chaining enables capability escalation | 6.4 | Medium | No Control Found | 6.4 | Medium |
| T-4 | Knowledge Base | Attacker injects malicious content into Knowledge Base | 6.3 | Medium | Partial Control | 4.7 | Medium |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via adversarial content in Knowledge Base | 6.3 | Medium | No Control Found | 6.3 | Medium |
| I-1 | Guardrails Service | Rejection reasons reveal internal filtering rules | 6.2 | Medium | Control Found | 3.1 | Medium |
| T-2 | LLM Agent Orchestrator | Attacker injects malicious content by tampering with data flow | 6.1 | Medium | Partial Control | 4.6 | Medium |
| D-4 | Knowledge Base | Unbounded vector search queries exhaust resources | 6.0 | Medium | Partial Control | 4.5 | Medium |
| I-4 | Knowledge Base | Query responses include internal metadata | 5.9 | Medium | Control Found | 3.0 | Medium |
| T-1 | Guardrails Service | Attacker modifies validation rules at runtime | 5.8 | Medium | Control Found | 2.9 | Medium |
| S-4 | MCP Tool Server | Attacker redirects outbound API requests via DNS spoofing | 5.7 | Medium | Control Found | 2.9 | Medium |
| I-3 | MCP Tool Server | Raw API error responses forwarded without sanitization | 5.6 | Medium | Partial Control | 4.2 | Medium |
| I-2 | LLM Agent Orchestrator | Verbose error messages leak internal service topology | 5.5 | Medium | Control Found | 2.8 | Medium |

### Low Residual Severity

| Threat ID | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| T-5 | Audit Logger | Attacker modifies audit log entries to cover tracks | 5.4 | Medium | Control Found | 2.7 | Low |
| D-5 | Audit Logger | High-volume logging events cause storage exhaustion | 5.3 | Medium | Partial Control | 4.0 | Low |
| R-3 | LLM Agent Orchestrator | Orchestrator executes tool calls without logging decision chain | 5.2 | Medium | Partial Control | 3.9 | Low |
| AG-2 | LLM Agent Orchestrator | Orchestrator operates in unbounded reasoning loop | 5.2 | Medium | No Control Found | 5.2 | Low |
| I-5 | Audit Logger | Audit logs contain sensitive data accessible beyond security team | 5.1 | Medium | Control Found | 2.6 | Low |
| LLM-3 | LLM Agent Orchestrator | Systematic querying enables model extraction | 5.0 | Medium | No Control Found | 5.0 | Low |
| R-1 | User | User denies having submitted a specific prompt | 4.8 | Medium | Control Found | 2.4 | Low |
| R-5 | External API | External API interactions lack correlation identifiers | 4.6 | Medium | No Control Found | 4.6 | Low |
| R-2 | Guardrails Service | Insufficient detail in filtering event logs | 4.5 | Medium | Partial Control | 3.4 | Low |
| R-4 | MCP Tool Server | Tool executions lack requesting orchestrator context | 4.3 | Medium | No Control Found | 4.3 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 1 | 2.9% |
| High | 9 | 26.5% |
| Medium | 14 | 41.2% |
| Low | 10 | 29.4% |
| **Total** | **34** | **100%** |

---

## 3. Control Details

Per-control evidence showing detected security controls with their location, code evidence, and threat coverage. One subsection per detected control, grouped by control category.

### Authentication

#### AUTH-1 — Bearer Token Validation

**Category**: Authentication | **Status**: Partial Control | **Effectiveness**: Moderate

**Detected in**: `src/middleware/auth.js:15`

```javascript
const token = req.headers.authorization?.split('Bearer ')[1];
if (!token) return res.status(401).json({ error: 'Missing token' });
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Token validation exists but lacks client context binding |
| Configuration | Moderate | JWT secret from environment variable |
| Currency | Strong | Using current jwt library version |
| Completeness | Weak | No DPoP, no session fingerprinting, no MFA |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| S-1 | User | Attacker impersonates legitimate user | 7.9 | 0.25 | 5.9 |

### Rate Limiting

#### RATE-1 — Express Rate Limiter

**Category**: Rate Limiting | **Status**: Partial Control | **Effectiveness**: Moderate

**Detected in**: `src/middleware/rateLimiter.js:8`

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});
```

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Rate limiting exists at API gateway |
| Configuration | Weak | Static 100 req/15min may be too generous |
| Currency | Strong | Current library version |
| Completeness | Weak | No per-endpoint limits, no adaptive throttling |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| D-1 | Guardrails Service | Attacker floods Guardrails Service | 7.4 | 0.25 | 5.6 |

### Encryption

#### ENC-1 — TLS Configuration

**Category**: Encryption | **Status**: Control Found | **Effectiveness**: Strong

**Detected in**: `src/config/tls.js:3`

```javascript
const tlsOptions = {
  cert: fs.readFileSync(process.env.TLS_CERT),
  key: fs.readFileSync(process.env.TLS_KEY),
};
```

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Strong | TLS configured for all external endpoints |
| Configuration | Strong | Certificate from environment variable |
| Currency | Strong | TLS 1.3 supported |
| Completeness | Moderate | No certificate pinning on outbound calls |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| S-3 | LLM Agent Orchestrator | Attacker forges tool call requests | 7.2 | 0.25 | 5.4 |
| S-4 | MCP Tool Server | Attacker redirects outbound API requests | 5.7 | 0.50 | 2.9 |

### Logging/Audit

#### LOG-1 — Centralized Audit Logging

**Category**: Logging/Audit | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/services/auditLogger.js:12`

```javascript
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.File({ filename: 'audit.log' })],
});
```

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Logging exists for most operations |
| Configuration | Moderate | JSON format, file transport |
| Currency | Strong | Current winston version |
| Completeness | Weak | No log integrity verification, no tamper protection |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| T-5 | Audit Logger | Attacker modifies audit log entries | 5.4 | 0.50 | 2.7 |
| R-1 | User | User denies having submitted a prompt | 4.8 | 0.50 | 2.4 |

### Input Validation

#### VAL-1 — Guardrails Input Filtering

**Category**: Input Validation | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/services/guardrails.js:25`

```javascript
function validateInput(prompt) {
  if (prompt.length > MAX_PROMPT_LENGTH) throw new Error('Input too long');
  return sanitize(prompt);
}
```

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Input length check and basic sanitization |
| Configuration | Moderate | Max length configurable |
| Currency | Strong | Current sanitize library |
| Completeness | Weak | No structured prompt boundary enforcement |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| I-1 | Guardrails Service | Rejection reasons reveal filtering rules | 6.2 | 0.50 | 3.1 |
| I-2 | LLM Agent Orchestrator | Verbose error messages leak topology | 5.5 | 0.50 | 2.8 |
| I-4 | Knowledge Base | Query responses include internal metadata | 5.9 | 0.50 | 3.0 |
| T-1 | Guardrails Service | Attacker modifies validation rules | 5.8 | 0.50 | 2.9 |
| I-5 | Audit Logger | Audit logs contain sensitive data | 5.1 | 0.50 | 2.6 |

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control," sorted by composite risk score descending.

### Critical / High Risk Gaps

#### 1. LLM-1 — LLM Agent Orchestrator (Composite: 8.3, High)

**Current Status**: No Control Found

**What to Implement**: Deploy structured prompt templates with explicit boundary enforcement between system instructions and user input. Use delimiters, role markers, and instruction hierarchy to prevent adversarial prompt override.

**Where to Implement**: `src/services/orchestrator.js` — prompt construction module

**Reference Patterns**: OpenAI system prompt best practices, OWASP LLM01 mitigations

**Effort Estimate**: Medium — New prompt construction module with boundary enforcement

---

#### 2. E-2 — LLM Agent Orchestrator (Composite: 7.6, High)

**Current Status**: No Control Found

**What to Implement**: Implement role-based access control on tool dispatch. Map user roles to permitted tool sets and enforce at the orchestrator level before dispatching to MCP Tool Server.

**Where to Implement**: `src/services/orchestrator.js` — tool dispatch handler

**Reference Patterns**: OWASP access control guidelines, principle of least privilege

**Effort Estimate**: High — Requires RBAC framework integration across orchestrator and tool server

---

#### 3. AG-1 — LLM Agent Orchestrator (Composite: 7.6, High)

**Current Status**: No Control Found

**What to Implement**: Establish human-in-the-loop checkpoints for all irreversible or external actions. Classify operations by risk tier and require explicit user approval for consequential actions.

**Where to Implement**: `src/services/orchestrator.js` — action execution pipeline

**Reference Patterns**: OWASP ASI-01 mitigations, human approval gate patterns

**Effort Estimate**: High — Requires action classification system and approval workflow

---

#### 4. E-3 — MCP Tool Server (Composite: 7.5, High)

**Current Status**: No Control Found

**What to Implement**: Enforce per-agent capability scoping on the MCP Tool Server. Each connected client should only access tools permitted by its role and session context.

**Where to Implement**: `src/services/mcpServer.js` — tool registration and dispatch

**Reference Patterns**: MCP capability scoping, RBAC on tool endpoints

**Effort Estimate**: Medium — Tool permission matrix with per-session enforcement

---

#### 5. D-2 — LLM Agent Orchestrator (Composite: 7.3, High)

**Current Status**: No Control Found

**What to Implement**: Add input size caps and concurrent request limits at the orchestrator layer. Implement request queuing with timeout to prevent resource exhaustion from parallel maximum-length prompts.

**Where to Implement**: `src/middleware/rateLimiter.js` — extend to orchestrator endpoints

**Reference Patterns**: Express rate limiter per-endpoint configuration, request queuing patterns

**Effort Estimate**: Low — Extend existing rate limiter to orchestrator endpoints

---

### Medium Risk Gaps

#### 6. AG-4 — MCP Tool Server (Composite: 6.4, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement cross-tool policy evaluation that assesses composite effects of tool call chains. Add a policy engine that evaluates whether a sequence of tool calls exceeds individual permissions.

**Where to Implement**: `src/services/mcpServer.js` — tool chain policy evaluator

**Reference Patterns**: Capability-based security, tool composition policies

**Effort Estimate**: High — New policy engine for tool chain evaluation

---

#### 7. LLM-2 — LLM Agent Orchestrator (Composite: 6.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Add content sanitization and anomaly detection on Knowledge Base retrieval results before including them in the LLM context window. Filter or flag content that resembles instruction patterns.

**Where to Implement**: `src/services/knowledgeBase.js` — retrieval post-processing

**Reference Patterns**: RAG poisoning mitigations, content anomaly detection

**Effort Estimate**: Medium — Content filtering module for RAG pipeline

---

## 5. Residual Risk Summary

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | 214.5 |
| Total Residual Risk Score | 156.8 |
| Delta | 57.7 |
| Overall Reduction | 26.9% |

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | 0 | 1 | +1 |
| High | 10 | 9 | -1 |
| Medium | 24 | 14 | -10 |
| Low | 0 | 10 | +10 |
| **Total** | **34** | **34** | — |
