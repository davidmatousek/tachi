---
schema_version: "1.0"
date: "2026-10-21"
source_file: "baseline/risk-scores.md"
target_path: "stub-codebase"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report

## 1. Executive Summary

**42** threats analyzed | **17** Control Found | **15** Partial Control | **10** No Control Found

**Coverage**: 40.5% Found | 35.7% Partial | 23.8% Missing

**Risk Reduction**: 249.9 inherent -> 178.3 residual (**28.7%** reduction)

**Highest-Risk Unmitigated Finding**: E-1 — edge-gateway — Composite 8.0 (High)

| Metric | Value |
|--------|-------|
| Analysis date | 2026-10-21 |
| Source file | `baseline/risk-scores.md` |
| Target codebase | `stub-codebase` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 17 | 40.5% |
| Partial Control | 15 | 35.7% |
| No Control Found | 10 | 23.8% |
| **Total** | **42** | **100%** |

> Analysis completed within the file-read budget; no directories were skipped.

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| E-1 | — | edge-gateway | Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others. | 8.0 | High | No Control Found | 8.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| T-4 | — | auth-broker | Unsanitised credential assertions and session grants reach auth-broker and are processed as trusted structure, so crafted input changes how later steps interpret the record. | 6.7 | Medium | No Control Found | 6.7 | Medium |
| OI-3 | — | worker-2 | Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it. | 6.3 | Medium | No Control Found | 6.3 | Medium |
| D-2 | — | intake-agent | A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests. | 6.1 | Medium | No Control Found | 6.1 | Medium |
| T-1 | — | auth-broker | Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores. | 6.0 | Medium | No Control Found | 6.0 | Medium |
| S-3 | — | auth-broker | A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. | 7.9 | High | Partial Control | 5.9 | Medium |
| I-5 | — | vector-store-a | embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position. | 5.7 | Medium | No Control Found | 5.7 | Medium |
| D-1 | — | edge-gateway | A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request. | 7.3 | High | Partial Control | 5.5 | Medium |
| D-3 | — | vector-store-a | Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage. | 5.3 | Medium | No Control Found | 5.3 | Medium |
| OI-1 | — | intake-agent | intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests. | 7.1 | High | Partial Control | 5.3 | Medium |
| OI-2 | — | intake-agent | Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field flows straight into business logic. | 7.1 | High | Partial Control | 5.3 | Medium |
| I-1 | — | edge-gateway | Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures. | 6.9 | Medium | Partial Control | 5.2 | Medium |
| LLM-1 | — | edge-gateway | edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns. | 6.9 | Medium | Partial Control | 5.2 | Medium |
| LLM-2 | — | edge-gateway | Prompt content logged by auth-broker is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context. | 6.9 | Medium | Partial Control | 5.2 | Medium |
| LLM-3 | — | intake-agent | Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text. | 6.9 | Medium | Partial Control | 5.2 | Medium |
| I-3 | — | worker-2 | Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to the logging pipeline can read content meant for one tenant. | 4.8 | Medium | No Control Found | 4.8 | Medium |
| LLM-7 | — | worker-2 | worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content. | 4.8 | Medium | No Control Found | 4.8 | Medium |
| AG-4 | — | tool-server-1 | tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded. | 6.3 | Medium | Partial Control | 4.7 | Medium |
| AG-6 | — | planner-agent | planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives. | 6.3 | Medium | Partial Control | 4.7 | Medium |
| E-2 | — | intake-agent | Role claims carried in the service token presented to intake-agent are honoured without confirmation against the authoritative directory. | 4.6 | Medium | No Control Found | 4.6 | Medium |
| AGP-01 | — | worker-2 | Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them... | 6.0 | Medium | Partial Control | 4.5 | Medium |
| S-4 | — | tool-server-1 | A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. | 5.9 | Medium | Partial Control | 4.4 | Medium |
| E-3 | — | planner-agent | planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources. | 5.7 | Medium | Partial Control | 4.3 | Medium |
| AG-2 | — | planner-agent | planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful. | 5.7 | Medium | Partial Control | 4.3 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | — | edge-gateway | A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. | 7.6 | High | Control Found | 3.8 | Low |
| MI-2 | — | intake-agent | Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes. | 6.8 | Medium | Control Found | 3.4 | Low |
| S-5 | — | tool-server-1 | An unauthenticated callback or health route on tool-server-1 accepts requests that downstream code treats as if they had come from audit-ledger. | 6.6 | Medium | Control Found | 3.3 | Low |
| LLM-4 | — | tool-server-1 | Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks plain English text. | 6.6 | Medium | Control Found | 3.3 | Low |
| MI-1 | — | intake-agent | intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents. | 6.6 | Medium | Control Found | 3.3 | Low |
| TE-2 | — | intake-agent | Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review. | 6.2 | Medium | Control Found | 3.1 | Low |
| AG-5 | — | tool-server-1 | tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed. | 6.0 | Medium | Control Found | 3.0 | Low |
| R-4 | — | tool-server-1 | Actions taken through tool-server-1 are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to tool call arguments and results. | 3.7 | Low | Partial Control | 2.8 | Low |
| I-4 | — | model-gateway | Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes another tenant's prompts and completions. | 5.4 | Medium | Control Found | 2.7 | Low |
| LLM-5 | — | model-gateway | Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system. | 5.4 | Medium | Control Found | 2.7 | Low |
| T-2 | — | vector-store-a | Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour. | 5.0 | Medium | Control Found | 2.5 | Low |
| R-3 | — | tool-server-1 | Operators approve changes to tool call arguments and results through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed. | 5.0 | Medium | Control Found | 2.5 | Low |
| AG-3 | — | tool-server-1 | Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task. | 5.0 | Medium | Control Found | 2.5 | Low |
| LLM-6 | — | vector-store-a | Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict authoritative sources. | 5.0 | Medium | Control Found | 2.5 | Low |
| R-1 | — | intake-agent | Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of actions on free-text shipment requests cannot be reconstructed reliably. | 4.6 | Medium | Control Found | 2.3 | Low |
| AG-1 | — | intake-agent | Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task. | 4.6 | Medium | Control Found | 2.3 | Low |
| TE-1 | — | intake-agent | intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants. | 4.4 | Medium | Control Found | 2.2 | Low |
| T-3 | — | audit-ledger | An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their... | 4.2 | Medium | Control Found | 2.1 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0.0% |
| High | 1 | 2.4% |
| Medium | 23 | 54.8% |
| Low | 18 | 42.8% |
| **Total** | **42** | **100%** |

---

## 3. Control Details

Per-control evidence showing detected security controls with their location, code evidence and threat coverage, grouped by control category.

### Authentication

#### CTRL-01 — Signed token verification at the gateway

**Category**: Authentication | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/gateway/token_verify.py:7`

```python
def verify_token(raw, keys, audience):
    claims = decode_signed(raw, keys, algorithms=["ES256"])
    if claims["aud"] != audience or claims["exp"] < now():
        raise Rejected("token not valid for this service")
    return claims
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| S-1 | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 7.6 | 0.50 | 3.8 |
| S-3 | auth-broker | A shared or long-lived refresh token on auth-broker lets... | 7.9 | 0.25 | 5.9 |
| AG-1 | intake-agent | Memory written by intake-agent is trusted on later runs... | 4.6 | 0.50 | 2.3 |
| TE-1 | intake-agent | intake-agent adopts a persona that presents itself as a... | 4.4 | 0.50 | 2.2 |
| TE-2 | intake-agent | Persuasive phrasing from intake-agent pushes operators... | 6.2 | 0.50 | 3.1 |

---

### Authentication

#### CTRL-02 — Mutual TLS between internal services

**Category**: Authentication | **Status**: Partial Control | **Effectiveness**: Weak

**Detected in**: `src/gateway/mtls_config.py:8`

```python
def internal_context(ca_bundle, cert, key):
    ctx = new_tls_context(purpose="server")
    ctx.load_chain(cert, key)
    ctx.require_client_certificate(ca_bundle)
    return ctx
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Limited | Applied on part of the request path only |
| Configuration | Basic | Defaults are mostly unchanged |
| Currency | Current | Built on maintained primitives |
| Completeness | Low | Several paths and components are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| S-4 | tool-server-1 | A shared or long-lived tool API key on tool-server-1... | 5.9 | 0.25 | 4.4 |
| S-5 | tool-server-1 | An unauthenticated callback or health route on... | 6.6 | 0.50 | 3.3 |
| AGP-01 | worker-2 | Worker agents coordinate through the shared message bus... | 6.0 | 0.25 | 4.5 |

---

### Access Control

#### CTRL-03 — Role check on every request

**Category**: Access Control | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/policy/rbac.py:9`

```python
def require_role(role):
    def guard(request):
        if role not in directory.roles_for(request.principal):
            raise Forbidden(request.principal, role)
    return guard
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| E-3 | planner-agent | planner-agent runs with broader permissions than its... | 5.7 | 0.25 | 4.3 |
| AG-2 | planner-agent | planner-agent runs without a budget on steps or spend... | 5.7 | 0.25 | 4.3 |
| AG-6 | planner-agent | planner-agent does not limit the rate or total number of... | 6.3 | 0.25 | 4.7 |

---

### Input Validation

#### CTRL-05 — Schema validation of structured requests

**Category**: Input Validation | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/intake/schema.py:7`

```python
def parse_request(payload):
    data = REQUEST_SCHEMA.validate(payload, extra="forbid")
    if len(data["text"]) > MAX_TEXT:
        raise Rejected("request too large")
    return data
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| AG-3 | tool-server-1 | Memory written by tool-server-1 is trusted on later... | 5.0 | 0.50 | 2.5 |
| AG-4 | tool-server-1 | tool-server-1 retries failed actions on its own... | 6.3 | 0.25 | 4.7 |
| AG-5 | tool-server-1 | tool-server-1 invokes tools with arguments assembled... | 6.0 | 0.50 | 3.0 |
| LLM-1 | edge-gateway | edge-gateway passes conversation history from earlier... | 6.9 | 0.25 | 5.2 |
| LLM-2 | edge-gateway | Prompt content logged by auth-broker is later replayed... | 6.9 | 0.25 | 5.2 |
| LLM-3 | intake-agent | Encoded or multilingual payloads bypass the keyword... | 6.9 | 0.25 | 5.2 |
| LLM-4 | tool-server-1 | Encoded or multilingual payloads bypass the keyword... | 6.6 | 0.50 | 3.3 |
| OI-1 | intake-agent | intake-agent emits URLs that downstream services fetch... | 7.1 | 0.25 | 5.3 |
| OI-2 | intake-agent | Structured output from intake-agent is trusted by... | 7.1 | 0.25 | 5.3 |
| MI-1 | intake-agent | intake-agent fabricates reference numbers and clause... | 6.6 | 0.50 | 3.3 |
| MI-2 | intake-agent | Stale data in the knowledge base lets intake-agent... | 6.8 | 0.50 | 3.4 |

---

### Input Validation

#### CTRL-06 — Parameterised database queries

**Category**: Input Validation | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/store/queries.py:8`

```python
def load_task(conn, task_id):
    cur = conn.cursor()
    cur.execute("select body from tasks where id = %s", (task_id,))
    row = cur.fetchone()
    return row[0] if row else None
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| T-2 | vector-store-a | Serialised objects arriving from worker-2 are... | 5.0 | 0.50 | 2.5 |
| T-3 | audit-ledger | An attacker who can write to the channel between... | 4.2 | 0.50 | 2.1 |
| LLM-6 | vector-store-a | Anyone who can write to the ingestion path of... | 5.0 | 0.50 | 2.5 |

---

### Encryption

#### CTRL-07 — TLS 1.3 for outbound and inbound links

**Category**: Encryption | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/common/tls.py:9`

```python
def client_context():
    ctx = new_tls_context(purpose="client")
    ctx.minimum_version = TLS_1_3
    ctx.verify_hostname = True
    return ctx
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| I-1 | edge-gateway | Secrets such as the bearer token for edge-gateway appear... | 6.9 | 0.25 | 5.2 |
| I-4 | model-gateway | Cross-tenant filters on model-gateway are applied in... | 5.4 | 0.50 | 2.7 |

---

### Rate Limiting

#### CTRL-09 — Token bucket per caller at the edge

**Category**: Rate Limiting | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/gateway/ratelimit.py:7`

```python
def allow(caller, now):
    bucket = buckets.setdefault(caller, Bucket(rate=RATE, burst=BURST))
    bucket.refill(now)
    return bucket.take(1)
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| D-1 | edge-gateway | A dependency of edge-gateway becomes unavailable and the... | 7.3 | 0.25 | 5.5 |

---

### Logging/Audit

#### CTRL-11 — Append-only audit writer

**Category**: Logging/Audit | **Status**: Control Found | **Effectiveness**: Moderate

**Detected in**: `src/audit/ledger_writer.py:9`

```python
def record(event):
    entry = {"at": utc_now(), "who": event.principal, "what": event.action}
    entry["prev"] = ledger.tail_hash()
    ledger.append(entry)
    return entry["prev"]
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Moderate | Applied on the main request path of the protected components |
| Configuration | Adequate | Defaults have been reviewed and tightened |
| Currency | Current | Built on maintained primitives |
| Completeness | Partial | Some secondary paths are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| R-3 | tool-server-1 | Operators approve changes to tool call arguments and... | 5.0 | 0.50 | 2.5 |
| R-4 | tool-server-1 | Actions taken through tool-server-1 are logged without... | 3.7 | 0.25 | 2.8 |

---

### Logging/Audit

#### CTRL-12 — Trace redaction before storage

**Category**: Logging/Audit | **Status**: Partial Control | **Effectiveness**: Weak

**Detected in**: `src/obs/trace_redact.py:6`

```python
def redact(span):
    for field in SENSITIVE_FIELDS:
        if field in span.attributes:
            span.attributes[field] = "[redacted]"
    return span
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | Limited | Applied on part of the request path only |
| Configuration | Basic | Defaults are mostly unchanged |
| Currency | Current | Built on maintained primitives |
| Completeness | Low | Several paths and components are not covered |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| R-1 | intake-agent | Clock drift between intake-agent and edge-gateway leaves... | 4.6 | 0.50 | 2.3 |
| LLM-5 | model-gateway | Indirect injection through documents retrieved for... | 5.4 | 0.50 | 2.7 |

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control", sorted by composite risk score descending.

### Critical / High Risk Gaps

#### 1. E-1 — edge-gateway (Composite: 8.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement access control for edge-gateway. Evaluate the original caller's entitlement for each object and action, and deny by default when the check cannot be made. Place the control where inbound API requests are first received, so that nothing downstream has to repeat the check. This addresses: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others. Acceptance check: a caller without the entitlement is denied for every object and action, including through indirect paths, and the denial is recorded. Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.

**Where to Implement**: `stub-codebase/src/edge_gateway/access_control.py` — a new module next to the code that handles inbound API requests, so the owners of that code review the control with it

**Reference Patterns**: Role and attribute checks at the service boundary, deny-by-default policy

**Effort Estimate**: High — a cross-cutting change that touches several components, including the tests that keep the control in place after later changes

---

#### 2. S-3 — auth-broker (Composite: 7.9, High)

**Current Status**: Partial Control

**What to Implement**: Harden the existing access control control: evaluate the original caller's entitlement for each object and action, and deny by default when the check cannot be made on the paths of auth-broker that it does not yet cover. The current implementation is recorded at src/gateway/token_verify.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. Acceptance check: a caller without the entitlement is denied for every object and action, including through indirect paths, and the denial is recorded. Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.

**Where to Implement**: `src/gateway/token_verify.py` — the existing control lives here and covers the main request path of auth-broker, and the owners of that module already review changes to it

**Reference Patterns**: Role and attribute checks at the service boundary, deny-by-default policy

**Effort Estimate**: Medium — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 3. D-1 — edge-gateway (Composite: 7.3, High)

**Current Status**: Partial Control

**What to Implement**: Harden the existing rate limiting control: bound concurrency, request rate and per-task spend for this component and shed load with a clear status on the paths of edge-gateway that it does not yet cover. The current implementation is recorded at src/gateway/ratelimit.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request. Acceptance check: a load test above the configured limits is shed with a clear status while normal traffic keeps its latency budget. Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.

**Where to Implement**: `src/gateway/ratelimit.py` — the existing control lives here and covers the main request path of edge-gateway, and the owners of that module already review changes to it

**Reference Patterns**: Token buckets, bulkheads, circuit breakers, task budgets

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 4. OI-1 — intake-agent (Composite: 7.1, High)

**Current Status**: Partial Control

**What to Implement**: Harden the existing logging/audit control: record who did what, to which object, with which outcome, in a store that operators cannot alter on the paths of intake-agent that it does not yet cover. The current implementation is recorded at src/intake/schema.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests. Acceptance check: every state change produces one complete record that an operator cannot edit, and a gap in the sequence raises an alert. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `src/intake/schema.py` — the existing control lives here and covers the main request path of intake-agent, and the owners of that module already review changes to it

**Reference Patterns**: Append-only ledger, hash chaining, structured events

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 5. OI-2 — intake-agent (Composite: 7.1, High)

**Current Status**: Partial Control

**What to Implement**: Harden the existing logging/audit control: record who did what, to which object, with which outcome, in a store that operators cannot alter on the paths of intake-agent that it does not yet cover. The current implementation is recorded at src/intake/schema.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field flows straight into business logic. Acceptance check: every state change produces one complete record that an operator cannot edit, and a gap in the sequence raises an alert. Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.

**Where to Implement**: `src/intake/schema.py` — the existing control lives here and covers the main request path of intake-agent, and the owners of that module already review changes to it

**Reference Patterns**: Append-only ledger, hash chaining, structured events

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

### Medium Risk Gaps

#### 6. I-1 — edge-gateway (Composite: 6.9, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing encryption control: protect this data in transit and at rest with current protocols and keys held outside the storage account on the paths of edge-gateway that it does not yet cover. The current implementation is recorded at src/common/tls.py:9 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures. Acceptance check: a scan of the link or store shows only current protocol versions and encrypted content, and keys rotate without downtime. Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.

**Where to Implement**: `src/common/tls.py` — the existing control lives here and covers the main request path of edge-gateway, and the owners of that module already review changes to it

**Reference Patterns**: TLS 1.3, envelope encryption, managed key service

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 7. LLM-1 — edge-gateway (Composite: 6.9, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing input validation control: validate each structured input against a closed schema before use, and reject unknown fields and oversized values on the paths of edge-gateway that it does not yet cover. The current implementation is recorded at src/intake/schema.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.

**Where to Implement**: `src/intake/schema.py` — the existing control lives here and covers the main request path of edge-gateway, and the owners of that module already review changes to it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 8. LLM-2 — edge-gateway (Composite: 6.9, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing input validation control: validate each structured input against a closed schema before use, and reject unknown fields and oversized values on the paths of edge-gateway that it does not yet cover. The current implementation is recorded at src/intake/schema.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: Prompt content logged by auth-broker is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `src/intake/schema.py` — the existing control lives here and covers the main request path of edge-gateway, and the owners of that module already review changes to it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 9. LLM-3 — intake-agent (Composite: 6.9, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing input validation control: validate each structured input against a closed schema before use, and reject unknown fields and oversized values on the paths of intake-agent that it does not yet cover. The current implementation is recorded at src/intake/schema.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.

**Where to Implement**: `src/intake/schema.py` — the existing control lives here and covers the main request path of intake-agent, and the owners of that module already review changes to it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 10. T-4 — auth-broker (Composite: 6.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement input validation for auth-broker. Validate each structured input against a closed schema before use, and reject unknown fields and oversized values. Place the control where credential assertions and session grants are first received, so that nothing downstream has to repeat the check. This addresses: Unsanitised credential assertions and session grants reach auth-broker and are processed as trusted structure, so crafted input changes how later steps interpret the record. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `stub-codebase/src/auth_broker/input_validation.py` — a new module next to the code that handles credential assertions and session grants, so the owners of that code review the control with it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 11. AG-4 — tool-server-1 (Composite: 6.3, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing authentication control: verify the caller's signed credential on every request to this component and bind it to the channel it arrived on on the paths of tool-server-1 that it does not yet cover. The current implementation is recorded at src/intake/schema.py:7 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded. Acceptance check: a request that carries a missing, expired or mismatched credential is rejected with a logged reason, and a valid request still succeeds. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `src/intake/schema.py` — the existing control lives here and covers the main request path of tool-server-1, and the owners of that module already review changes to it

**Reference Patterns**: Short-lived signed tokens, mutual TLS, workload identity

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 12. AG-6 — planner-agent (Composite: 6.3, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing input validation control: validate each structured input against a closed schema before use, and reject unknown fields and oversized values on the paths of planner-agent that it does not yet cover. The current implementation is recorded at src/policy/rbac.py:9 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.

**Where to Implement**: `src/policy/rbac.py` — the existing control lives here and covers the main request path of planner-agent, and the owners of that module already review changes to it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 13. OI-3 — worker-2 (Composite: 6.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement input validation for worker-2. Validate each structured input against a closed schema before use, and reject unknown fields and oversized values. Place the control where work orders and route candidates are first received, so that nothing downstream has to repeat the check. This addresses: Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.

**Where to Implement**: `stub-codebase/src/worker_2/input_validation.py` — a new module next to the code that handles work orders and route candidates, so the owners of that code review the control with it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 14. D-2 — intake-agent (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting for intake-agent. Bound concurrency, request rate and per-task spend for this component and shed load with a clear status. Place the control where free-text shipment requests are first received, so that nothing downstream has to repeat the check. This addresses: A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests. Acceptance check: a load test above the configured limits is shed with a clear status while normal traffic keeps its latency budget. Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.

**Where to Implement**: `stub-codebase/src/intake_agent/rate_limiting.py` — a new module next to the code that handles free-text shipment requests, so the owners of that code review the control with it

**Reference Patterns**: Token buckets, bulkheads, circuit breakers, task budgets

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 15. T-1 — auth-broker (Composite: 6.0, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement input validation for auth-broker. Validate each structured input against a closed schema before use, and reject unknown fields and oversized values. Place the control where credential assertions and session grants are first received, so that nothing downstream has to repeat the check. This addresses: Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.

**Where to Implement**: `stub-codebase/src/auth_broker/input_validation.py` — a new module next to the code that handles credential assertions and session grants, so the owners of that code review the control with it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 16. AGP-01 — worker-2 (Composite: 6.0, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing rate limiting control: bound concurrency, request rate and per-task spend for this component and shed load with a clear status on the paths of worker-2 that it does not yet cover. The current implementation is recorded at src/gateway/mtls_config.py:8 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour. Acceptance check: a load test above the configured limits is shed with a clear status while normal traffic keeps its latency budget. Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.

**Where to Implement**: `src/gateway/mtls_config.py` — the existing control lives here and covers the main request path of worker-2, and the owners of that module already review changes to it

**Reference Patterns**: Token buckets, bulkheads, circuit breakers, task budgets

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 17. S-4 — tool-server-1 (Composite: 5.9, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing authentication control: verify the caller's signed credential on every request to this component and bind it to the channel it arrived on on the paths of tool-server-1 that it does not yet cover. The current implementation is recorded at src/gateway/mtls_config.py:8 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile. Acceptance check: a request that carries a missing, expired or mismatched credential is rejected with a logged reason, and a valid request still succeeds. Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.

**Where to Implement**: `src/gateway/mtls_config.py` — the existing control lives here and covers the main request path of tool-server-1, and the owners of that module already review changes to it

**Reference Patterns**: Short-lived signed tokens, mutual TLS, workload identity

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 18. I-5 — vector-store-a (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement encryption for vector-store-a. Protect this data in transit and at rest with current protocols and keys held outside the storage account. Place the control where embedded documents and metadata are first received, so that nothing downstream has to repeat the check. This addresses: embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position. Acceptance check: a scan of the link or store shows only current protocol versions and encrypted content, and keys rotate without downtime. Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.

**Where to Implement**: `stub-codebase/src/vector_store_a/encryption.py` — a new module next to the code that handles embedded documents and metadata, so the owners of that code review the control with it

**Reference Patterns**: TLS 1.3, envelope encryption, managed key service

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 19. E-3 — planner-agent (Composite: 5.7, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing access control control: evaluate the original caller's entitlement for each object and action, and deny by default when the check cannot be made on the paths of planner-agent that it does not yet cover. The current implementation is recorded at src/policy/rbac.py:9 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources. Acceptance check: a caller without the entitlement is denied for every object and action, including through indirect paths, and the denial is recorded. Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.

**Where to Implement**: `src/policy/rbac.py` — the existing control lives here and covers the main request path of planner-agent, and the owners of that module already review changes to it

**Reference Patterns**: Role and attribute checks at the service boundary, deny-by-default policy

**Effort Estimate**: Medium — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 20. AG-2 — planner-agent (Composite: 5.7, Medium)

**Current Status**: Partial Control

**What to Implement**: Harden the existing logging/audit control: record who did what, to which object, with which outcome, in a store that operators cannot alter on the paths of planner-agent that it does not yet cover. The current implementation is recorded at src/policy/rbac.py:9 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful. Acceptance check: every state change produces one complete record that an operator cannot edit, and a gap in the sequence raises an alert. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `src/policy/rbac.py` — the existing control lives here and covers the main request path of planner-agent, and the owners of that module already review changes to it

**Reference Patterns**: Append-only ledger, hash chaining, structured events

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

#### 21. D-3 — vector-store-a (Composite: 5.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting for vector-store-a. Bound concurrency, request rate and per-task spend for this component and shed load with a clear status. Place the control where embedded documents and metadata are first received, so that nothing downstream has to repeat the check. This addresses: Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage. Acceptance check: a load test above the configured limits is shed with a clear status while normal traffic keeps its latency budget. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `stub-codebase/src/vector_store_a/rate_limiting.py` — a new module next to the code that handles embedded documents and metadata, so the owners of that code review the control with it

**Reference Patterns**: Token buckets, bulkheads, circuit breakers, task budgets

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 22. I-3 — worker-2 (Composite: 4.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement encryption for worker-2. Protect this data in transit and at rest with current protocols and keys held outside the storage account. Place the control where work orders and route candidates are first received, so that nothing downstream has to repeat the check. This addresses: Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to the logging pipeline can read content meant for one tenant. Acceptance check: a scan of the link or store shows only current protocol versions and encrypted content, and keys rotate without downtime. Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.

**Where to Implement**: `stub-codebase/src/worker_2/encryption.py` — a new module next to the code that handles work orders and route candidates, so the owners of that code review the control with it

**Reference Patterns**: TLS 1.3, envelope encryption, managed key service

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 23. LLM-7 — worker-2 (Composite: 4.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement input validation for worker-2. Validate each structured input against a closed schema before use, and reject unknown fields and oversized values. Place the control where work orders and route candidates are first received, so that nothing downstream has to repeat the check. This addresses: worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content. Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape. Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.

**Where to Implement**: `stub-codebase/src/worker_2/input_validation.py` — a new module next to the code that handles work orders and route candidates, so the owners of that code review the control with it

**Reference Patterns**: Schema validation, parameterised queries, output encoding

**Effort Estimate**: Medium — a new module and its tests, including the tests that keep the control in place after later changes

---

#### 24. E-2 — intake-agent (Composite: 4.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement access control for intake-agent. Evaluate the original caller's entitlement for each object and action, and deny by default when the check cannot be made. Place the control where free-text shipment requests are first received, so that nothing downstream has to repeat the check. This addresses: Role claims carried in the service token presented to intake-agent are honoured without confirmation against the authoritative directory. Acceptance check: a caller without the entitlement is denied for every object and action, including through indirect paths, and the denial is recorded. Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.

**Where to Implement**: `stub-codebase/src/intake_agent/access_control.py` — a new module next to the code that handles free-text shipment requests, so the owners of that code review the control with it

**Reference Patterns**: Role and attribute checks at the service boundary, deny-by-default policy

**Effort Estimate**: High — a cross-cutting change that touches several components, including the tests that keep the control in place after later changes

---

### Low Risk Gaps

#### 25. R-4 — tool-server-1 (Composite: 3.7, Low)

**Current Status**: Partial Control

**What to Implement**: Harden the existing logging/audit control: record who did what, to which object, with which outcome, in a store that operators cannot alter on the paths of tool-server-1 that it does not yet cover. The current implementation is recorded at src/audit/ledger_writer.py:9 and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. This addresses: Actions taken through tool-server-1 are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to tool call arguments and results. Acceptance check: every state change produces one complete record that an operator cannot edit, and a gap in the sequence raises an alert. Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.

**Where to Implement**: `src/audit/ledger_writer.py` — the existing control lives here and covers the main request path of tool-server-1, and the owners of that module already review changes to it

**Reference Patterns**: Append-only ledger, hash chaining, structured events

**Effort Estimate**: Low — the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way

---

## 5. Residual Risk Summary

Comparison of inherent risk (before controls) to residual risk (after controls).

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | 249.9 |
| Total Residual Risk Score | 178.3 |
| Delta | 71.6 |
| Overall Reduction | 28.7% |

### Per-Severity-Band Shift

| Shift | Count | Examples |
|-------|-------|----------|
| Critical -> High | 0 | — |
| Critical -> Medium | 0 | — |
| Critical -> Low | 0 | — |
| High -> Medium | 4 | S-3, D-1, OI-1 |
| High -> Low | 1 | S-1 |
| Medium -> Low | 16 | S-5, T-2, T-3 |
| No Shift | 21 | S-4, T-1, T-4 |
| **Total** | **42** |  |

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | 0 | 0 | +0 |
| High | 6 | 1 | -5 |
| Medium | 35 | 23 | -12 |
| Low | 1 | 18 | +17 |
| **Total** | **42** | **42** |  |

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent * 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent * 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent * 1.00 | No matching control detected. Residual equals inherent. |

---

## 6. Methodology

This section documents the compensating controls analysis methodology used to produce this report.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

```
Residual Score = Inherent Score * (1 - Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0], rounded half-up to one decimal place and mapped to severity bands with the thresholds used for risk scoring.

### 6.4 Data Sources

- **Scored threats**: parsed from `risk-scores.md` (canonical) or `risk-scores.sarif` (fallback).
- **Target codebase**: scanned through the `--target` path, with heuristic directories prioritized when no architecture mapping exists.
- **STRIDE-to-control mapping**: the canonical mapping from threat categories to control categories drives which controls are searched for.

### 6.5 Limitations

- Static analysis only: runtime control behavior is not evaluated.
- 200-file read budget: large codebases may have directories skipped with warnings.
- Files over 5,000 tokens are truncated to security-relevant sections.
- Binary reduction factors approximate control impact.
