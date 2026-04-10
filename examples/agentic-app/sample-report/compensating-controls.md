# Compensating Controls Report


---

```yaml
---
schema_version: "1.0"
date: "2026-04-10"
source_file: "risk-scores.md"
target_path: "."
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---
```

---

## 1. Executive Summary

**22** threats analyzed | **0** Control Found | **0** Partial Control | **22** No Control Found

**Coverage**: 0.0% Found | 0.0% Partial | 100.0% Missing

**Risk Reduction**: 148.1 inherent → 148.1 residual (**0.0%** reduction)

**Highest-Risk Unmitigated Finding**: LLM-1 — LLM Agent Orchestrator — Composite 8.1 (High)

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-10 |
| Source file | `risk-scores.md` |
| Target codebase | `.` |
| Schema version | 1.0 |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0.0% |
| Partial Control | 0 | 0.0% |
| No Control Found | 22 | 100.0% |
| **Total** | **22** | **100%** |

> Target codebase is the tachi methodology template repository. Tachi provides threat modeling artifacts and pipeline orchestration — it is not a production application with enforcement code. As expected, the control scan found no application-layer security controls in the target, so every finding reports No Control Found with residual risk equal to inherent risk. Downstream consumers integrating tachi into a production codebase should re-run this analysis against their application source to derive meaningful residual risk reductions.

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### Critical Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|---------------|--------|----------------|-------------------|----------------|----------------|-------------------|

### High Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|---------------|--------|----------------|-------------------|----------------|----------------|-------------------|
| LLM-1 | N | LLM Agent Orchestrator | L1 — Foundation Model | Indirect prompt injection via documents retrieved from the … | 8.1 | High | No Control Found | 8.1 | High |
| AG-4 | N | MCP Tool Server | L3 — Agent Framework | Compromised or manipulated agent triggers excessive tool in… | 8.0 | High | No Control Found | 8.0 | High |
| E-2 | N | Guardrails Service | L6 — Security and Compliance | Attacker bypasses guardrails validation through prompt obfu… | 7.7 | High | No Control Found | 7.7 | High |
| E-1 | N | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator escalates its own tool permissions beyond the … | 7.5 | High | No Control Found | 7.5 | High |
| LLM-3 | N | LLM Agent Orchestrator | L1 — Foundation Model | Attacker crafts prompts that cause the LLM to generate tool… | 7.5 | High | No Control Found | 7.5 | High |
| AG-2 | N | MCP Tool Server | L3 — Agent Framework | Attacker manipulates prompt context to cause the tool serve… | 7.4 | High | No Control Found | 7.4 | High |
| D-1 | N | Guardrails Service | L6 — Security and Compliance | Attacker floods the guardrails service with complex prompts… | 7.4 | High | No Control Found | 7.4 | High |
| S-1 | N | User | L7 — Agent Ecosystem | Attacker spoofs a legitimate user identity by stealing or r… | 7.4 | High | No Control Found | 7.4 | High |
| S-3 | N | External API | L3 — Agent Framework | Compromised or spoofed external API returns malicious paylo… | 7.4 | High | No Control Found | 7.4 | High |
| AG-1 | N | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator autonomously escalates its own action scope by… | 7.3 | High | No Control Found | 7.3 | High |

### Medium Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|---------------|--------|----------------|-------------------|----------------|----------------|-------------------|
| LLM-2 | N | LLM Agent Orchestrator | L1 — Foundation Model | Attacker poisons knowledge base documents with adversarial … | 6.9 | Medium | No Control Found | 6.9 | Medium |
| AG-3 | N | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator generates and executes multi-step plans withou… | 6.7 | Medium | No Control Found | 6.7 | Medium |
| D-2 | N | MCP Tool Server | L3 — Agent Framework | Attacker triggers recursive or excessively long tool call c… | 6.7 | Medium | No Control Found | 6.7 | Medium |
| I-1 | N | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator leaks sensitive context from the knowledge bas… | 6.7 | Medium | No Control Found | 6.7 | Medium |
| I-3 | N | MCP Tool Server | L3 — Agent Framework | Tool server includes API credentials, internal endpoint URL… | 6.2 | Medium | No Control Found | 6.2 | Medium |
| T-1 | N | Knowledge Base | L2 — Data Operations | Attacker with write access to the vector store injects or m… | 6.1 | Medium | No Control Found | 6.1 | Medium |
| S-2 | N | LLM Agent Orchestrator | L1 — Foundation Model | Attacker crafts spoofed tool call responses that mimic the … | 6.0 | Medium | No Control Found | 6.0 | Medium |
| R-1 | N | User | L7 — Agent Ecosystem | User denies submitting a harmful or policy-violating prompt… | 5.8 | Medium | No Control Found | 5.8 | Medium |
| T-2 | N | LLM Agent Orchestrator | L1 — Foundation Model | Attacker tampers with orchestration configuration or interm… | 5.7 | Medium | No Control Found | 5.7 | Medium |
| I-2 | N | Knowledge Base | L2 — Data Operations | Unauthorized access to vector store contents exposes confid… | 5.3 | Medium | No Control Found | 5.3 | Medium |
| T-3 | N | Audit Logger | L5 — Evaluation and Observability | Attacker with elevated access modifies or truncates audit l… | 5.3 | Medium | No Control Found | 5.3 | Medium |
| R-2 | N | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator makes autonomous multi-step decisions that can… | 5.0 | Medium | No Control Found | 5.0 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|---------------|--------|----------------|-------------------|----------------|----------------|-------------------|

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0.0% |
| High | 10 | 45.5% |
| Medium | 12 | 54.5% |
| Low | 0 | 0.0% |
| **Total** | **22** | **100%** |

---

## 3. Control Details

No application-layer security controls were detected in the target codebase. The tachi methodology template provides threat modeling orchestration and does not include production enforcement code (authentication services, rate limiters, input validators, access control middleware, etc.) that would be expected to mitigate the findings in `risk-scores.md`.

Downstream consumers should re-run `/tachi.compensating-controls risk-scores.md <target-path>` against their application source to populate this section with detected controls, evidence snippets, effectiveness assessments, and per-threat reduction factors.

---

## 4. Risk Reduction Analysis

Per-finding inherent-vs-residual risk comparison. Because no controls were detected in the target, residual equals inherent for every finding.

| Finding ID | Component | Inherent Score | Residual Score | Reduction |
|------------|-----------|----------------|----------------|-----------|
| LLM-1 | LLM Agent Orchestrator | 8.1 | 8.1 | 0.0 |
| AG-4 | MCP Tool Server | 8.0 | 8.0 | 0.0 |
| E-2 | Guardrails Service | 7.7 | 7.7 | 0.0 |
| E-1 | LLM Agent Orchestrator | 7.5 | 7.5 | 0.0 |
| LLM-3 | LLM Agent Orchestrator | 7.5 | 7.5 | 0.0 |
| AG-2 | MCP Tool Server | 7.4 | 7.4 | 0.0 |
| D-1 | Guardrails Service | 7.4 | 7.4 | 0.0 |
| S-1 | User | 7.4 | 7.4 | 0.0 |
| S-3 | External API | 7.4 | 7.4 | 0.0 |
| AG-1 | LLM Agent Orchestrator | 7.3 | 7.3 | 0.0 |
| LLM-2 | LLM Agent Orchestrator | 6.9 | 6.9 | 0.0 |
| AG-3 | LLM Agent Orchestrator | 6.7 | 6.7 | 0.0 |
| D-2 | MCP Tool Server | 6.7 | 6.7 | 0.0 |
| I-1 | LLM Agent Orchestrator | 6.7 | 6.7 | 0.0 |
| I-3 | MCP Tool Server | 6.2 | 6.2 | 0.0 |
| T-1 | Knowledge Base | 6.1 | 6.1 | 0.0 |
| S-2 | LLM Agent Orchestrator | 6.0 | 6.0 | 0.0 |
| R-1 | User | 5.8 | 5.8 | 0.0 |
| T-2 | LLM Agent Orchestrator | 5.7 | 5.7 | 0.0 |
| I-2 | Knowledge Base | 5.3 | 5.3 | 0.0 |
| T-3 | Audit Logger | 5.3 | 5.3 | 0.0 |
| R-2 | LLM Agent Orchestrator | 5.0 | 5.0 | 0.0 |

**Aggregate**: Total inherent risk = 148.1, total residual risk = 148.1, reduction = 0.0%.

---

## 5. Recommendations

Prioritized remediation guidance for findings with no detected controls. All recommendations derive from the upstream `risk-scores.md` mitigation fields, sorted by residual composite score descending.

| Priority | Finding ID | Component | Residual Severity | Recommended Action |
|----------|------------|-----------|-------------------|--------------------|
| 1 | LLM-1 | LLM Agent Orchestrator | High | Sanitize LLM inputs and outputs with instruction-data separation and egress filtering |
| 2 | AG-4 | MCP Tool Server | High | Constrain agent autonomy with HITL approval and chain-length limits |
| 3 | E-2 | Guardrails Service | High | Scope tool permissions per user and enforce least-privilege allowlists |
| 4 | E-1 | LLM Agent Orchestrator | High | Scope tool permissions per user and enforce least-privilege allowlists |
| 5 | LLM-3 | LLM Agent Orchestrator | High | Sanitize LLM inputs and outputs with instruction-data separation and egress filtering |
| 6 | AG-2 | MCP Tool Server | High | Constrain agent autonomy with HITL approval and chain-length limits |
| 7 | D-1 | Guardrails Service | High | Enforce rate limiting and request-complexity caps with circuit breakers |
| 8 | S-1 | User | High | Implement short-lived JWT tokens with fingerprint binding and MFA |
| 9 | S-3 | External API | High | Implement short-lived JWT tokens with fingerprint binding and MFA |
| 10 | AG-1 | LLM Agent Orchestrator | High | Constrain agent autonomy with HITL approval and chain-length limits |
| 11 | LLM-2 | LLM Agent Orchestrator | Medium | Sanitize LLM inputs and outputs with instruction-data separation and egress filtering |
| 12 | AG-3 | LLM Agent Orchestrator | Medium | Constrain agent autonomy with HITL approval and chain-length limits |
| 13 | D-2 | MCP Tool Server | Medium | Enforce rate limiting and request-complexity caps with circuit breakers |
| 14 | I-1 | LLM Agent Orchestrator | Medium | Apply per-user context isolation and output filtering for sensitive patterns |
| 15 | I-3 | MCP Tool Server | Medium | Apply per-user context isolation and output filtering for sensitive patterns |
| 16 | T-1 | Knowledge Base | Medium | Enforce cryptographic integrity checks on writes and signed configuration |
| 17 | S-2 | LLM Agent Orchestrator | Medium | Implement short-lived JWT tokens with fingerprint binding and MFA |
| 18 | R-1 | User | Medium | Log authenticated identity and session context for every request |
| 19 | T-2 | LLM Agent Orchestrator | Medium | Enforce cryptographic integrity checks on writes and signed configuration |
| 20 | I-2 | Knowledge Base | Medium | Apply per-user context isolation and output filtering for sensitive patterns |
| 21 | T-3 | Audit Logger | Medium | Enforce cryptographic integrity checks on writes and signed configuration |
| 22 | R-2 | LLM Agent Orchestrator | Medium | Log authenticated identity and session context for every request |

---

## 6. Appendix: Scan Metadata

| Field | Value |
|-------|-------|
| Source | `risk-scores.md` (22 scored findings) |
| Target | `.` (tachi repository root) |
| Scan strategy | Full scan (no baseline) |
| Detected controls | 0 |
| Analysis duration | N/A (static template analysis) |
