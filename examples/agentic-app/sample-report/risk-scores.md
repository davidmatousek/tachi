---
schema_version: "1.0"
date: "2026-04-18"
source_file: "threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Agentic AI Application

## 1. Executive Summary

**Total findings scored**: 70

### Severity Distribution

| Severity | Count |
|---|---|
| Critical | 37 |
| High | 26 |
| Medium | 7 |
| Low | 0 |

**Highest-risk component**: LLM Agent Orchestrator (composite score 7.9, 19 findings scored).

The threat surface is dominated by Critical-band findings on the LLM Agent Orchestrator and its multi-agent communication surface, driven by LLM-category composite scores with S:C scope change and high exploitability. Output-integrity (OI) findings OI-1, OI-2, and OI-3 score as Critical, Critical, and High respectively, consistent with their LLM-category treatment under FR-014. Correlation group primaries (CG-1 through CG-5) propagate their composite scores to peer findings.

---

## 2. Scored Threat Table

Sorted by composite score descending (secondary sort by ID).

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|---|---|---|---|---|---|---|---|---|---|---|
| E-2 | LLM Agent Orchestrator | Orchestrator prompt injection self-authorizes elevated operations... | 9.9 | 8.0 | 7.5 | 1.0 | 7.2 | High | 7d | Mitigate |
| AG-1 | LLM Agent Orchestrator | Prompt injection causes autonomous unauthorized high-impact act... | 9.1 | 8.0 | 7.3 | 1.0 | 6.9 | Medium | 30d | Review |
| AG-2 | LLM Agent Orchestrator | Orchestrator+Specialist jointly coordinate to circumvent policy... | 9.1 | 6.5 | 5.8 | 1.0 | 6.2 | Medium | 30d | Review |
| AG-3 | Specialist Agent | Specialist delegated task causes cumulative prohibited tool ca... | 9.1 | 6.0 | 5.8 | 1.0 | 6.0 | Medium | 30d | Review |
| AG-4 | Inter-Agent Communication Channel | Agent-in-the-middle intercepts and modifies delegation message... | 9.1 | 6.5 | 5.8 | 1.0 | 6.2 | Medium | 30d | Review |
| AG-5 | MCP Tool Server | Tool call injection via LLM-influenced JSON-RPC parameters | 9.1 | 7.0 | 6.0 | 1.0 | 6.5 | Medium | 30d | Review |
| AG-6 | MCP Tool Server | Runaway agent-driven tool calls exhaust External API rate limi... | 9.1 | 7.0 | 6.5 | 1.0 | 6.5 | Medium | 30d | Review |
| AG-7 | Long-Running Learning Loop | Training data temporal autonomy expansion on next update | 9.1 | 3.0 | 4.5 | 1.0 | 5.1 | Medium | 30d | Review |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection overrides system prompt or reveals con... | 9.3 | 8.8 | 7.3 | 1.0 | 7.2 | High | 7d | Mitigate |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via adversarial Knowledge Base docum... | 9.3 | 6.0 | 7.3 | 1.0 | 6.4 | Medium | 30d | Review |
| LLM-4 | LLM Agent Orchestrator | Training data poisoning via Audit Logger-fed Learning Loop upd... | 9.3 | 3.0 | 6.5 | 1.0 | 5.3 | Medium | 30d | Review |
| LLM-5 | LLM Agent Orchestrator | Client-side XSS via LLM response rendered in browser | 9.3 | 8.8 | 7.3 | 1.0 | 7.2 | High | 7d | Mitigate |
| LLM-6 | LLM Agent Orchestrator | Server-side execution via LLM-emitted Tool Call Request params | 9.3 | 7.5 | 7.0 | 1.0 | 6.7 | Medium | 30d | Review |
| LLM-8 | Specialist Agent | Prompt injection via delegation message hijacks task execution | 9.3 | 7.5 | 7.3 | 1.0 | 6.8 | Medium | 30d | Review |
| LLM-9 | Specialist Agent | Training data poisoning via Specialist self-poisoning audit lo... | 9.3 | 3.0 | 6.5 | 1.0 | 5.3 | Medium | 30d | Review |
| LLM-11 | Long-Running Learning Loop | Systematic audit log poisoning for delayed temporal model beha... | 9.3 | 3.0 | 6.5 | 1.0 | 5.3 | Medium | 30d | Review |
| OI-1 | LLM Agent Orchestrator | Client-side XSS via LLM response to User browser | 9.3 | 8.8 | 7.3 | 1.0 | 7.2 | High | 7d | Mitigate |
| OI-2 | LLM Agent Orchestrator | Server-side code/command execution via LLM-synthesized Tool Ca... | 9.3 | 7.5 | 7.0 | 1.0 | 6.7 | Medium | 30d | Review |
| S-1 | User | Attacker impersonates legitimate user via replayed session tok... | 8.2 | 7.5 | 6.8 | 9.5 | 7.9 | High | 7d | Mitigate |
| S-3 | LLM Agent Orchestrator | Orchestrator identity not attested to Specialist; rogue proces... | 8.2 | 5.5 | 6.5 | 1.0 | 5.6 | Medium | 30d | Review |
| S-5 | Inter-Agent Communication Channel | Shared channel with no sender authentication; malicious proces... | 8.2 | 5.5 | 6.5 | 1.0 | 5.6 | Medium | 30d | Review |
| S-6 | MCP Tool Server | Application Zone process spoofs agent identity to submit unaut... | 8.2 | 5.5 | 6.5 | 1.0 | 5.6 | Medium | 30d | Review |
| S-7 | Long-Running Learning Loop | Training signal accepted without source integrity verification | 8.2 | 4.0 | 5.5 | 1.0 | 5.1 | Medium | 30d | Review |
| T-2 | LLM Agent Orchestrator | Orchestrator context window tampered via upstream data source... | 7.1 | 7.0 | 6.5 | 1.0 | 5.8 | Medium | 30d | Review |
| T-3 | Specialist Agent | Delegation message context tampered via Inter-Agent Channel i... | 7.1 | 6.5 | 6.0 | 1.0 | 5.5 | Medium | 30d | Review |
| T-4 | Inter-Agent Communication Channel | Messages modified in transit by agent-in-the-middle | 7.1 | 6.5 | 6.0 | 1.0 | 5.5 | Medium | 30d | Review |
| T-5 | MCP Tool Server | LLM-generated tool parameters bypass allowlist; shell/SQL inje... | 7.1 | 7.0 | 6.5 | 1.0 | 5.8 | Medium | 30d | Review |
| T-8 | Long-Running Learning Loop | Training signal poisoning with temporal/sleeper-agent injection | 7.1 | 3.0 | 5.0 | 1.0 | 4.3 | Medium | 30d | Review |
| R-3 | LLM Agent Orchestrator | Orchestrator denies issued delegation/tool actions without con... | 4.3 | 4.5 | 5.3 | 1.0 | 3.9 | Low | 90d | Review |
| I-2 | LLM Agent Orchestrator | Context window leaked in response via hallucination/injection | 6.5 | 7.0 | 6.3 | 1.0 | 5.5 | Medium | 30d | Review |
| I-4 | Inter-Agent Communication Channel | Inter-agent messages observable to unauthorized Application Zo... | 6.5 | 6.0 | 5.5 | 1.0 | 5.1 | Medium | 30d | Review |
| I-7 | Audit Logger | Unauthorized read access exposes full operational history of ... | 6.5 | 5.5 | 6.0 | 1.0 | 4.9 | Medium | 30d | Review |
| D-1 | Guardrails Service | Resource exhaustion via high-volume computationally expensive... | 7.5 | 8.5 | 8.0 | 1.0 | 6.6 | Medium | 30d | Review |
| D-2 | LLM Agent Orchestrator | Inference pipeline exhaustion via high-token prompts or recur... | 7.5 | 7.5 | 6.5 | 1.0 | 5.9 | Medium | 30d | Review |
| D-5 | MCP Tool Server | Connection pool exhaustion via high-volume tool call requests | 7.5 | 8.0 | 7.0 | 1.0 | 6.3 | Medium | 30d | Review |
| E-1 | Guardrails Service | Prompt injection bypass elevates attacker to trusted Orchestr... | 9.9 | 8.5 | 7.3 | 1.0 | 7.3 | High | 7d | Mitigate |
| E-4 | Inter-Agent Communication Channel | Application Zone process injects messages with forged elevate... | 9.9 | 6.0 | 6.0 | 1.0 | 6.4 | Medium | 30d | Review |
| E-5 | MCP Tool Server | Unauthorized tool calls gain Tool Server execution privileges... | 9.9 | 6.5 | 6.5 | 1.0 | 6.6 | Medium | 30d | Review |
| E-6 | Long-Running Learning Loop | Poisoned update escalates attacker from data access to model ... | 9.9 | 3.5 | 5.0 | 1.0 | 5.5 | Medium | 30d | Review |
| S-2 | Guardrails Service | Direct bypass to Orchestrator internal endpoint without Guard... | 8.2 | 5.0 | 5.5 | 1.0 | 5.4 | Medium | 30d | Review |
| S-4 | Specialist Agent | Specialist impersonates Orchestrator to inject fabricated agg... | 8.2 | 5.0 | 5.5 | 1.0 | 5.4 | Medium | 30d | Review |
| S-8 | External API | DNS hijacking/BGP attack redirects External API calls to atta... | 8.2 | 3.0 | 4.5 | 4.5 | 5.4 | Medium | 30d | Review |
| T-1 | Guardrails Service | Filtering rule modification to allow blocked prompt patterns | 7.1 | 4.5 | 5.0 | 1.0 | 4.8 | Medium | 30d | Review |
| T-6 | Knowledge Base | KB corpus poisoning via unauthorized write access | 7.1 | 4.0 | 5.3 | 1.0 | 4.7 | Medium | 30d | Review |
| T-7 | Audit Logger | Audit log tampering destroys training signal integrity and fo... | 7.1 | 4.5 | 5.3 | 1.0 | 4.8 | Medium | 30d | Review |
| R-4 | Specialist Agent | Specialist denies executed tool calls or produced specific re... | 4.3 | 3.5 | 5.0 | 1.0 | 3.5 | Low | 90d | Review |
| R-6 | MCP Tool Server | Tool Server denies having executed specific tool invocation | 4.3 | 3.5 | 5.0 | 1.0 | 3.5 | Low | 90d | Review |
| R-7 | Long-Running Learning Loop | Learning Loop denies having applied specific model update | 4.3 | 3.0 | 4.5 | 1.0 | 3.3 | Low | 90d | Review |
| I-3 | Specialist Agent | Sensitive delegation context leaked in Specialist results via... | 6.5 | 5.0 | 5.5 | 1.0 | 4.8 | Medium | 30d | Review |
| I-5 | MCP Tool Server | Tool results containing PII logged verbatim to Audit Logger | 6.5 | 5.0 | 5.5 | 1.0 | 4.8 | Medium | 30d | Review |
| I-6 | Knowledge Base | Full corpus exfiltration via unrestricted vector search queries | 6.5 | 6.5 | 6.3 | 1.0 | 5.3 | Medium | 30d | Review |
| I-8 | Long-Running Learning Loop | Model memorizes training data PII; training data extraction a... | 6.5 | 3.5 | 5.0 | 1.0 | 4.3 | Medium | 30d | Review |
| D-3 | Specialist Agent | Computationally expensive delegated tasks exhaust Specialist ... | 7.5 | 7.0 | 6.3 | 1.0 | 5.9 | Medium | 30d | Review |
| D-4 | Inter-Agent Communication Channel | Message queue flooding drops legitimate coordination messages | 7.5 | 7.0 | 6.3 | 1.0 | 5.9 | Medium | 30d | Review |
| D-7 | Audit Logger | Log-flooding attack creates audit gaps and blocks pipeline op... | 7.5 | 6.0 | 5.8 | 1.0 | 5.5 | Medium | 30d | Review |
| E-3 | Specialist Agent | Forged delegation grants Specialist elevated permissions beyo... | 9.9 | 5.5 | 6.0 | 1.0 | 6.2 | Medium | 30d | Review |
| LLM-3 | LLM Agent Orchestrator | Model theft via systematic API probing and behavior extraction | 8.5 | 6.3 | 6.0 | 1.0 | 6.0 | Medium | 30d | Review |
| LLM-7 | LLM Agent Orchestrator | SSRF via LLM-synthesized URL in Tool Call Request | 8.5 | 6.5 | 6.3 | 1.0 | 6.1 | Medium | 30d | Review |
| LLM-10 | Specialist Agent | Server-side injection via tool result incorporation | 8.5 | 6.0 | 6.0 | 1.0 | 5.9 | Medium | 30d | Review |
| LLM-12 | Long-Running Learning Loop | Model theft via Learning Loop output artifact monitoring | 8.5 | 4.5 | 5.5 | 1.0 | 5.3 | Medium | 30d | Review |
| OI-3 | LLM Agent Orchestrator | SSRF via LLM-synthesized URL in Tool Call Request | 8.5 | 6.5 | 6.3 | 1.0 | 6.1 | Medium | 30d | Review |
| AGP-01 | LLM Agent Orchestrator | Multi-agent emergent behavior — cascading failures or feedba... | 7.0 | 4.0 | 5.0 | 1.0 | 4.6 | Medium | 30d | Review |
| R-1 | User | User denies submitting specific prompt; no non-repudiation co... | 4.3 | 5.0 | 5.3 | 9.5 | 5.7 | Medium | 30d | Review |
| R-2 | Guardrails Service | Guardrails denies filtering decisions without tamper-evident ... | 4.3 | 3.5 | 5.0 | 1.0 | 3.5 | Low | 90d | Review |
| I-1 | Guardrails Service | Rejection reasons reveal filtering rules to iterative probers | 5.3 | 6.0 | 6.0 | 1.0 | 4.7 | Medium | 30d | Review |
| D-6 | Knowledge Base | High-volume complex vector search queries degrade retrieval p... | 6.5 | 6.5 | 6.3 | 1.0 | 5.3 | Medium | 30d | Review |
| D-8 | Long-Running Learning Loop | Training signal flooding causes runaway Learning Loop process... | 6.5 | 4.5 | 5.0 | 1.0 | 4.6 | Medium | 30d | Review |
| R-5 | Inter-Agent Communication Channel | Channel denies delivery/modification of specific message with... | 4.3 | 3.0 | 4.5 | 1.0 | 3.3 | Low | 90d | Review |
| R-8 | External API | External API provider denies returned specific response | 4.3 | 3.5 | 4.5 | 4.5 | 4.1 | Medium | 30d | Review |

---

## 3. Dimensional Breakdown

One subsection per finding, ordered by composite score descending.

### S-1: Attacker impersonates legitimate user via replayed session tokens

**Component**: User
**Category**: Spoofing
**Composite Score**: 7.9 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **7.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Default spoofing vector; unauthenticated remote attack with high confidentiality impact via account takeover.
- **Exploitability**: Session token replay is well-documented with tooling (Burp Suite, tamper proxies); low skill required.
- **Scalability**: Scriptable credential replay applicable to all users with weak session binding; moderate detection risk.
- **Reachability**: User zone Untrusted (9.0) plus keyword "user" (+0.5) = 9.5; directly exposed to attacker-controlled input.

### E-1: Prompt injection bypass elevates attacker to trusted Orchestrator caller

**Component**: Guardrails Service
**Category**: Privilege Escalation
**Composite Score**: 7.3 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **7.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege-escalation default vector with S:C and full CIA.
- **Exploitability**: Prompt injection techniques are extensively documented and trivial to author.
- **Scalability**: Highly repeatable via crafted prompt payloads; moderate detection difficulty.
- **Reachability**: Application Zone Trusted with auth barrier + 2 network boundaries; clamped to Trusted floor 1.0.

### E-2: Orchestrator prompt injection self-authorizes elevated operations

**Component**: LLM Agent Orchestrator
**Category**: Privilege Escalation
**Composite Score**: 7.2 (High)
**Correlation Group**: Primary of CG-3 (peers R-3, AG-1)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege-escalation default with scope change and full CIA.
- **Exploitability**: Prompt injection leveraged for self-authorization is documented technique requiring moderate prompt engineering.
- **Scalability**: Scales across user sessions with Orchestrator broad access; moderate detection due to normal-appearing queries.
- **Reachability**: Orchestrator in Trusted Application Zone behind Guardrails auth and multiple network boundaries; clamped to floor 1.0.

### LLM-1: Direct prompt injection overrides system prompt

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 7.2 (High)
**Correlation Group**: Part of CG-4 (peer I-2)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM default vector — remote, unauthenticated, scope-changed, high C/I impact.
- **Exploitability**: Direct prompt injection is the benchmark AI-exploitability case (extensively documented, trivial tooling, no skill).
- **Scalability**: Fully scriptable, universal to all model-facing endpoints; moderate detection difficulty.
- **Reachability**: Application Zone Trusted; clamped to floor 1.0 after auth + network segmentation adjustments.

### LLM-5: Client-side XSS via LLM response rendered in browser

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 7.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM default vector applied to XSS with scope change to user browser session cookies.
- **Exploitability**: XSS payloads via prompt injection are highly documented; off-the-shelf payloads exist.
- **Scalability**: Universal across all browser-rendered LLM outputs; highly scriptable; moderate detection.
- **Reachability**: Orchestrator in Trusted Application Zone; clamped to floor 1.0.

### OI-1: Client-side XSS via LLM response to User browser

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 7.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM default; DOM sink exposure to session cookies and CSRF tokens qualifies as C:H/I:H under scope change.
- **Exploitability**: Output-integrity XSS via prompt priming is a documented OWASP LLM05 technique with ready payloads.
- **Scalability**: Highly scriptable; affects all browser-rendered response paths; moderate detection.
- **Reachability**: Application Zone Trusted; clamped to floor 1.0 after auth + network boundary adjustments.

### AG-1: Prompt injection causes autonomous unauthorized high-impact actions

**Component**: LLM Agent Orchestrator
**Category**: Agentic Threats
**Composite Score**: 6.9 (Medium)
**Correlation Group**: Part of CG-3 (primary E-2)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default vector; authenticated access, scope change, high C/I.
- **Exploitability**: Emerging but well-documented agent autonomy abuse.
- **Scalability**: Prompt-injection-scalable across all Orchestrator sessions; hard to distinguish from normal use.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### LLM-8: Prompt injection via delegation messages hijacks Specialist

**Component**: Specialist Agent
**Category**: LLM Threats
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM default, PR:L (requires Orchestrator-delegated context), scope change.
- **Exploitability**: Indirect prompt injection via inter-agent messages; documented research.
- **Scalability**: Fully repeatable through channel injection; moderate detection.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### LLM-6: Server-side execution via LLM Tool Call Request parameters

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 6.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: LLM default plus A:H (server-side code execution).
- **Exploitability**: Well-documented injection via LLM-emitted tool args; moderate complexity (depends on tool schema).
- **Scalability**: Scales across all tool invocations; moderate detection.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### OI-2: Server-side execution via LLM-synthesized Tool Call Request parameters

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 6.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: LLM default; server-side exec elevates availability impact to High.
- **Exploitability**: Well-documented prompt-engineering to control tool parameter structure; moderate tooling.
- **Scalability**: Universal to tool server integrations lacking parameterization.
- **Reachability**: Application Zone Trusted; clamped to floor 1.0.

### D-1: Resource exhaustion via high-volume expensive prompts

**Component**: Guardrails Service
**Category**: Denial of Service
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS default vector — unauthenticated remote, high availability.
- **Exploitability**: Trivial prompt-flooding with off-the-shelf tooling.
- **Scalability**: Highly scriptable; all service consumers affected; moderate bandwidth.
- **Reachability**: Guardrails in Trusted zone behind HTTPS/ingress; clamped to floor 1.0.

### E-5: Unauthorized tool calls gain Tool Server execution privileges

**Component**: MCP Tool Server
**Category**: Privilege Escalation
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege-escalation default; full CIA with scope change to external API.
- **Exploitability**: Requires forged caller token or compromised agent; moderate complexity.
- **Scalability**: Scales per tool server deployment; moderate detection.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### AG-5: Tool call injection via LLM-influenced JSON-RPC parameters

**Component**: MCP Tool Server
**Category**: Agentic Threats
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default with scope change to executed external systems.
- **Exploitability**: LLM output control documented; moderate crafting complexity.
- **Scalability**: Tool allowlists often incomplete; moderate detection.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### AG-6: Runaway tool calls exhaust External API rate limits

**Component**: MCP Tool Server
**Category**: Agentic Threats
**Composite Score**: 6.5 (Medium)
**Correlation Group**: Part of CG-5 (peer D-5)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Agentic default plus A:H for sustained resource exhaustion.
- **Exploitability**: Agent runaway patterns documented; moderate complexity.
- **Scalability**: Scriptable, universal to all tool consumers.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### LLM-2: Indirect prompt injection via adversarial KB documents

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM default with PR:L (KB write), UI:N (attacker content already resident).
- **Exploitability**: Requires KB write access; moderate skill.
- **Scalability**: Universal to all retrievals matching poisoned docs; hard to detect.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### E-4: Channel forged elevated sender identity

**Component**: Inter-Agent Communication Channel
**Category**: Privilege Escalation
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege-escalation default vector.
- **Exploitability**: Requires Application Zone foothold; moderate.
- **Scalability**: Scales per channel deployment.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### D-5: Connection pool exhaustion via high-volume tool call requests

**Component**: MCP Tool Server
**Category**: Denial of Service
**Composite Score**: 6.3 (Medium)
**Correlation Group**: Primary of CG-5 (peer AG-6)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS default vector.
- **Exploitability**: Trivial flooding if callers unauthenticated; requires path to Tool Server.
- **Scalability**: Scriptable; affects all tool consumers.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### AG-2: Orchestrator-Specialist collusion for policy circumvention

**Component**: LLM Agent Orchestrator
**Category**: Agentic Threats
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default; scope change via joint action.
- **Exploitability**: Requires coordinated injection across two agents; moderate complexity.
- **Scalability**: Limited to multi-agent deployments; hard to detect.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### AG-4: Agent-in-the-middle modifies delegation messages

**Component**: Inter-Agent Communication Channel
**Category**: Agentic Threats
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default; AITM scope change.
- **Exploitability**: Requires channel read-write; moderate.
- **Scalability**: Limited to channels without signed messages.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### E-3: Forged delegation grants Specialist elevated permissions

**Component**: Specialist Agent
**Category**: Privilege Escalation
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege-escalation with AC:H (requires forging signed delegation).
- **Exploitability**: Requires Orchestrator compromise or signing key access; moderate.
- **Scalability**: Limited to unsigned delegation protocols.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### LLM-7: SSRF via LLM-synthesized URL in Tool Call Request

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined — cloud metadata exposure (C:H), limited integrity (I:L).
- **Exploitability**: Prompt-engineered URL emission; moderate complexity.
- **Scalability**: Universal to outbound HTTP tools; moderate detection.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### OI-3: SSRF via LLM-synthesized URL in Tool Call Request

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined; IAM credential exfiltration via metadata endpoint.
- **Exploitability**: Documented SSRF via LLM-synthesized URL; moderate.
- **Scalability**: Universal to outbound fetch tools without allowlists.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### AG-3: Specialist cumulative prohibited tool call sequence

**Component**: Specialist Agent
**Category**: Agentic Threats
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default; agent-autonomy-driven policy circumvention.
- **Exploitability**: Emerging research; requires task sequence engineering.
- **Scalability**: Limited to multi-step tool workflows; hard to detect.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### LLM-3: Model theft via systematic API probing

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined — high complexity probing, high confidentiality loss.
- **Exploitability**: Academic technique with custom scripting.
- **Scalability**: Requires sustained query budget; detectable via anomaly monitoring.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### D-2: Orchestrator inference pipeline exhaustion

**Component**: LLM Agent Orchestrator
**Category**: Denial of Service
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS refined — PR:L (authenticated user session).
- **Exploitability**: Token flooding straightforward; moderate tooling.
- **Scalability**: Scales per session; moderate bandwidth.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### D-3: Specialist Agent resource exhaustion

**Component**: Specialist Agent
**Category**: Denial of Service
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS default.
- **Exploitability**: Task flooding via Orchestrator; moderate.
- **Scalability**: Scriptable; scales per Specialist deployment.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### D-4: Message queue flooding drops coordination messages

**Component**: Inter-Agent Communication Channel
**Category**: Denial of Service
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS default.
- **Exploitability**: Queue flooding trivial once authenticated.
- **Scalability**: Scriptable; universal to unbounded queues.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### LLM-10: Server-side injection via tool result incorporation

**Component**: Specialist Agent
**Category**: LLM Threats
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: LLM refined — AC:H (requires Tool Server-influenced content).
- **Exploitability**: Indirect; requires sink-to-source chain.
- **Scalability**: Limited to multi-step tool workflows.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### T-2: Orchestrator context window tampering

**Component**: LLM Agent Orchestrator
**Category**: Tampering
**Composite Score**: 5.8 (Medium)
**Correlation Group**: Primary of CG-1 (peer LLM-4)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering refined with scope change to downstream context.
- **Exploitability**: Requires upstream write; moderate.
- **Scalability**: Scales via KB/channel poisoning.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### T-5: Tool Server LLM-generated parameter allowlist bypass

**Component**: MCP Tool Server
**Category**: Tampering
**Composite Score**: 5.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering with scope change to executed tools.
- **Exploitability**: Requires LLM output influence; moderate.
- **Scalability**: Universal to Tool Server deployments without parameter validation.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### R-1: User denies submitting prompt

**Component**: User
**Category**: Repudiation
**Composite Score**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Moderate; relies on absent controls.
- **Scalability**: Hard to detect by definition.
- **Reachability**: User Untrusted zone (+0.5 for "user" keyword) = 9.5.

### S-3: Orchestrator identity not attested to Specialist

**Component**: LLM Agent Orchestrator
**Category**: Spoofing
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing default.
- **Exploitability**: Requires Application Zone foothold.
- **Scalability**: Scales per channel.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### S-5: Channel no sender authentication

**Component**: Inter-Agent Communication Channel
**Category**: Spoofing
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing default.
- **Exploitability**: Requires Application Zone process.
- **Scalability**: Scales per channel.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### S-6: Tool Server caller authentication bypass

**Component**: MCP Tool Server
**Category**: Spoofing
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing default.
- **Exploitability**: Moderate; requires Zone foothold.
- **Scalability**: Scales per tool deployment.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### D-7: Audit Logger flooding attack

**Component**: Audit Logger
**Category**: Denial of Service
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS default with PR:L.
- **Exploitability**: Requires Application Zone write access.
- **Scalability**: Scales per log source.
- **Reachability**: Audit Logger Trusted zone; clamped to floor 1.0.

### E-6: Poisoned update escalates to model parameter control

**Component**: Long-Running Learning Loop
**Category**: Privilege Escalation
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege-escalation with AC:H (training-cycle temporal dependency).
- **Exploitability**: Requires sustained poisoning; ML expertise helpful.
- **Scalability**: Limited to next update cycle.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### T-3: Specialist delegation message tampering

**Component**: Specialist Agent
**Category**: Tampering
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering refined with scope change.
- **Exploitability**: Requires channel write access; moderate.
- **Scalability**: Scales via channel tampering.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### T-4: Messages modified in transit (AITM)

**Component**: Inter-Agent Communication Channel
**Category**: Tampering
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering with scope change.
- **Exploitability**: Requires channel-layer access.
- **Scalability**: Scales per channel deployment.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### I-2: Context window leaked via injection/hallucination

**Component**: LLM Agent Orchestrator
**Category**: Information Disclosure
**Composite Score**: 5.5 (Medium)
**Correlation Group**: Primary of CG-4 (peer LLM-1)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure default.
- **Exploitability**: Prompt injection-driven; documented.
- **Scalability**: Scales across all sessions; moderate detection.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### LLM-4: Training data poisoning via Learning Loop

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 5.3 (Medium)
**Correlation Group**: Part of CG-1 (primary T-2)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined with AC:H for temporal dependency.
- **Exploitability**: Data poisoning requires ML expertise and pipeline access.
- **Scalability**: Universal to next update cycle; hard to detect.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### LLM-9: Specialist self-poisoning via audit log loop

**Component**: Specialist Agent
**Category**: LLM Threats
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined (AC:H).
- **Exploitability**: Data poisoning through self-generated records; ML expertise.
- **Scalability**: Tied to update cycle.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### LLM-11: Systematic audit log poisoning temporal attack

**Component**: Long-Running Learning Loop
**Category**: LLM Threats
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined (AC:H).
- **Exploitability**: Data poisoning; ML expertise.
- **Scalability**: Universal to next update cycle.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### LLM-12: Model theft via update artifact monitoring

**Component**: Long-Running Learning Loop
**Category**: LLM Threats
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: LLM refined — PR:H (observability access), AC:H.
- **Exploitability**: Requires privileged observability access.
- **Scalability**: Limited to model update events.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### I-6: Knowledge Base corpus exfiltration

**Component**: Knowledge Base
**Category**: Information Disclosure
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure default.
- **Exploitability**: Query enumeration scriptable.
- **Scalability**: Universal to KBs without query limits.
- **Reachability**: KB Trusted zone; clamped to floor 1.0.

### D-6: Knowledge Base vector search DoS

**Component**: Knowledge Base
**Category**: Denial of Service
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

**Scoring Rationale**:
- **CVSS**: DoS refined — A:L (degraded performance).
- **Exploitability**: Query flooding scriptable.
- **Scalability**: Scales per KB deployment.
- **Reachability**: KB Trusted zone; clamped to floor 1.0.

### AG-7: Temporal autonomy expansion via training data

**Component**: Long-Running Learning Loop
**Category**: Agentic Threats
**Composite Score**: 5.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic refined — AC:H (temporal).
- **Exploitability**: Data-poisoning with ML expertise; rare targets.
- **Scalability**: Limited per update cycle.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### S-7: Training signal source integrity not verified

**Component**: Long-Running Learning Loop
**Category**: Spoofing
**Composite Score**: 5.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing refined with AC:H.
- **Exploitability**: Requires Audit Logger compromise.
- **Scalability**: Limited to update cycle.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### I-4: Inter-agent messages observable

**Component**: Inter-Agent Communication Channel
**Category**: Information Disclosure
**Composite Score**: 5.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure default.
- **Exploitability**: Requires channel read access.
- **Scalability**: Scales per channel deployment.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### I-7: Audit Logger unauthorized read exposure

**Component**: Audit Logger
**Category**: Information Disclosure
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure default.
- **Exploitability**: Requires misconfigured access or insider.
- **Scalability**: Single aggregation target.
- **Reachability**: Audit Logger Trusted zone; clamped to floor 1.0.

### I-3: Specialist result sensitive context leakage

**Component**: Specialist Agent
**Category**: Information Disclosure
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure default.
- **Exploitability**: Moderate; requires channel observation.
- **Scalability**: Scales per Specialist deployment.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### I-5: Tool results PII logging

**Component**: MCP Tool Server
**Category**: Information Disclosure
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure default.
- **Exploitability**: Requires Audit Logger read access.
- **Scalability**: Scales per tool integration.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### T-1: Guardrails filtering rule modification

**Component**: Guardrails Service
**Category**: Tampering
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering refined with AC:H/PR:H (admin endpoint).
- **Exploitability**: Requires admin access.
- **Scalability**: Single target per deployment.
- **Reachability**: Guardrails Trusted zone; clamped to floor 1.0.

### T-7: Audit log tampering

**Component**: Audit Logger
**Category**: Tampering
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering refined with PR:H.
- **Exploitability**: Requires privileged log store access.
- **Scalability**: Limited to log stores.
- **Reachability**: Audit Logger Trusted zone; clamped to floor 1.0.

### I-1: Guardrails rejection reason leakage

**Component**: Guardrails Service
**Category**: Information Disclosure
**Composite Score**: 4.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure refined; low confidentiality (rule identifiers only).
- **Exploitability**: Iterative probing; documented.
- **Scalability**: Scriptable.
- **Reachability**: Guardrails Trusted zone; clamped to floor 1.0.

### T-6: KB corpus poisoning via unauthorized write

**Component**: Knowledge Base
**Category**: Tampering
**Composite Score**: 4.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Tampering refined with PR:H.
- **Exploitability**: Requires KB write access.
- **Scalability**: Single store per deployment.
- **Reachability**: KB Trusted zone; clamped to floor 1.0.

### AGP-01: Multi-agent emergent behavior

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**Composite Score**: 4.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.0 | 0.35 | 2.45 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Refined for emergent cross-agent behavior.
- **Exploitability**: Emerging research; hard to engineer.
- **Scalability**: Limited to multi-agent deployments.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### D-8: Learning Loop training signal flooding

**Component**: Long-Running Learning Loop
**Category**: Denial of Service
**Composite Score**: 4.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

**Scoring Rationale**:
- **CVSS**: DoS refined with A:L.
- **Exploitability**: Moderate; requires audit write volume.
- **Scalability**: Batch-scheduled.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### T-8: Training signal temporal poisoning

**Component**: Long-Running Learning Loop
**Category**: Tampering
**Composite Score**: 4.3 (Medium)
**Correlation Group**: Primary of CG-2 (peer LLM-11)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Tampering refined (AC:H, S:C).
- **Exploitability**: Data-poisoning with ML expertise.
- **Scalability**: Limited to update cycle.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### I-8: Training data extraction via model memorization

**Component**: Long-Running Learning Loop
**Category**: Information Disclosure
**Composite Score**: 4.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Info-disclosure refined with AC:H (memorization).
- **Exploitability**: ML-research technique.
- **Scalability**: Limited to memorized examples.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### R-8: External API provider denies response

**Component**: External API
**Category**: Repudiation
**Composite Score**: 4.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **4.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Low; disputes rare.
- **Scalability**: Hard to detect.
- **Reachability**: External API Semi-Trusted zone baseline 5.5 with 1 auth + 0 network = 4.5.

### S-2: Direct bypass to Orchestrator internal endpoint

**Component**: Guardrails Service
**Category**: Spoofing
**Composite Score**: 5.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.4** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing refined — AV:A (internal zone access).
- **Exploitability**: Requires Application Zone foothold.
- **Scalability**: Scales per deployment without mTLS.
- **Reachability**: Guardrails Trusted zone; clamped to floor 1.0.

### S-4: Specialist impersonates Orchestrator

**Component**: Specialist Agent
**Category**: Spoofing
**Composite Score**: 5.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.4** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing refined with I:H (result fabrication).
- **Exploitability**: Requires Specialist compromise.
- **Scalability**: Single-channel scope.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### S-8: DNS hijacking / BGP attack on External API

**Component**: External API
**Category**: Spoofing
**Composite Score**: 5.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **5.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Spoofing refined with AC:H (routing attacks).
- **Exploitability**: Significant infrastructure required.
- **Scalability**: Limited targets.
- **Reachability**: External API Semi-Trusted zone; 4.5.

### R-3: Orchestrator action repudiation

**Component**: LLM Agent Orchestrator
**Category**: Repudiation
**Composite Score**: 3.9 (Low)
**Correlation Group**: Part of CG-3 (primary E-2)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **3.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Relies on absent controls.
- **Scalability**: Hard to detect.
- **Reachability**: Orchestrator Trusted zone; clamped to floor 1.0.

### R-4: Specialist action repudiation

**Component**: Specialist Agent
**Category**: Repudiation
**Composite Score**: 3.5 (Low)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **3.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Moderate; absent controls.
- **Scalability**: Hard to detect.
- **Reachability**: Specialist Trusted zone; clamped to floor 1.0.

### R-6: Tool Server invocation repudiation

**Component**: MCP Tool Server
**Category**: Repudiation
**Composite Score**: 3.5 (Low)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **3.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Moderate.
- **Scalability**: Hard to detect.
- **Reachability**: Tool Server Trusted zone; clamped to floor 1.0.

### R-2: Guardrails filtering decision repudiation

**Component**: Guardrails Service
**Category**: Repudiation
**Composite Score**: 3.5 (Low)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **3.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Moderate.
- **Scalability**: Hard to detect.
- **Reachability**: Guardrails Trusted zone; clamped to floor 1.0.

### R-7: Learning Loop model update repudiation

**Component**: Long-Running Learning Loop
**Category**: Repudiation
**Composite Score**: 3.3 (Low)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **3.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Low; rare disputes.
- **Scalability**: Low.
- **Reachability**: Learning Loop Trusted zone; clamped to floor 1.0.

### R-5: Channel message delivery repudiation

**Component**: Inter-Agent Communication Channel
**Category**: Repudiation
**Composite Score**: 3.3 (Low)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **3.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default.
- **Exploitability**: Low.
- **Scalability**: Low.
- **Reachability**: Channel Trusted zone; clamped to floor 1.0.

### S-1 (Peer — see row above): Already scored.

---

## 4. Governance Fields

Sorted by composite score descending.

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|---|---|---|---|---|---|---|
| S-1 | User | High | Unassigned | 7d | Mitigate | 2026-04-25 |
| E-1 | Guardrails Service | High | Unassigned | 7d | Mitigate | 2026-04-25 |
| E-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-04-25 |
| LLM-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-04-25 |
| LLM-5 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-04-25 |
| OI-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-04-25 |
| AG-1 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-8 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-6 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| OI-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-18 |
| E-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AG-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AG-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| E-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AG-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AG-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-18 |
| E-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-7 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| OI-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AG-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-10 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| R-1 | User | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-5 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-18 |
| E-6 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-2 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-4 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-8 | External API | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-4 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-9 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-11 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| LLM-12 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AG-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| S-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-18 |
| AGP-01 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-18 |
| D-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| T-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| I-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-18 |
| R-8 | External API | Medium | Unassigned | 30d | Review | 2026-05-18 |
| R-3 | LLM Agent Orchestrator | Low | Unassigned | 90d | Review | 2026-07-17 |
| R-2 | Guardrails Service | Low | Unassigned | 90d | Review | 2026-07-17 |
| R-4 | Specialist Agent | Low | Unassigned | 90d | Review | 2026-07-17 |
| R-6 | MCP Tool Server | Low | Unassigned | 90d | Review | 2026-07-17 |
| R-7 | Long-Running Learning Loop | Low | Unassigned | 90d | Review | 2026-07-17 |
| R-5 | Inter-Agent Communication Channel | Low | Unassigned | 90d | Review | 2026-07-17 |

---

## 5. Scoring Methodology

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| CVSS 3.1 Base | 0.35 | Inherent vulnerability severity per CVSS 3.1 specification |
| Exploitability | 0.30 | Operational attack feasibility (known techniques, complexity, tooling, skill) |
| Scalability | 0.15 | Attack scalability (scriptability, target scope, resource requirements, detection difficulty) |
| Reachability | 0.20 | Trust-zone-derived architecture exposure (zone baseline, keyword refinement, architecture adjustments) |

### Default Weights and Rationale

- **CVSS Base (0.35)**: Inherent vulnerability severity carries the most weight because it captures industry-calibrated severity across confidentiality/integrity/availability impacts.
- **Exploitability (0.30)**: Practical attack feasibility is the second-strongest signal — a CVSS-Critical vulnerability with no known exploit and expert-only skill requirements poses lower operational risk.
- **Reachability (0.20)**: Architecture position matters — an Internet-facing vulnerability ranks higher than the same issue deep within trusted infrastructure.
- **Scalability (0.15)**: Blast radius and automation potential round out the composite.

### Composite Score Formula

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

### Severity Band Mapping

| Severity Band | Composite Score Range | SLA | Disposition |
|---------------|-----------------------|-----|-------------|
| Critical | >= 9.0 | 24h | Mitigate |
| High | 7.0 - 8.9 | 7d | Mitigate |
| Medium | 4.0 - 6.9 | 30d | Review |
| Low | < 4.0 | 90d | Review |

### Data Sources

- **Findings**: Parsed from `threats.md` (70 findings, all UNCHANGED from baseline `2026-04-19T02-53-49`)
- **Trust Zones**: Section 2 of `threats.md` (User Zone Untrusted, Application Zone Trusted, External Services Semi-Trusted)
- **Architecture**: `architecture.md` (supplementary context — HTTPS transport, content filtering at Guardrails, authenticated data flows)
- **Category Defaults**: `schemas/risk-scoring.yaml` CVSS baseline vectors

### Reproducibility

- Temperature 0 scoring with deterministic category default anchoring
- Per-dimension tolerance ±0.5 across repeat runs
- Correlation group primaries' scores propagated verbatim to peers (CG-1 through CG-5)
- OI findings (OI-1, OI-2, OI-3) scored through the same LLM category code paths as LLM-{N} findings per FR-014
- Baseline risk-scores.md not found at `test-output/2026-04-19T02-53-49/risk-scores.md`; all 70 findings scored fresh despite UNCHANGED delta_status
