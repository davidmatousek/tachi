# Risk Scores Report


---

```yaml
---
schema_version: "1.0"
date: "2026-04-10"
source_file: "threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
baseline:
  source: null
  inherited_count: null
  fresh_count: null
---
```

---

## 1. Executive Summary

**22 findings** scored across 8 threat categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege, Agentic Threats, LLM Threats).

**Highest-Risk Component**: LLM Agent Orchestrator — 10 finding(s), max composite 8.1

| Metric | Value |
|--------|-------|
| Scoring date | 2026-04-10 |
| Source file | `threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 10 | 45.5% |
| Medium | 12 | 54.5% |
| Low | 0 | 0.0% |
| **Total** | **22** | **100%** |

The majority of findings cluster in the High (10) and Medium (12) bands. The LLM Agent Orchestrator is the highest-risk component, reflecting its central role in processing user prompts and dispatching tool calls across trust boundaries. Agentic and LLM-category threats dominate the top of the composite ranking due to broad scope (S:C) and scope-crossing impact on downstream tool servers and knowledge bases.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).

| ID | Source | Component | MAESTRO Layer | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|---------------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| LLM-1 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Indirect prompt injection via documents retrieved from the knowledge base cause… | 9.3 | 8.5 | 8.5 | 5.0 | 8.1 | High | 7d | Mitigate |
| AG-4 | fresh | MCP Tool Server | L3 — Agent Framework | Compromised or manipulated agent triggers excessive tool invocations in rapid s… | 9.1 | 8.5 | 8.0 | 5.5 | 8.0 | High | 7d | Mitigate |
| E-2 | fresh | Guardrails Service | L6 — Security and Compliance | Attacker bypasses guardrails validation through prompt obfuscation techniques (… | 9.9 | 6.5 | 7.5 | 6.0 | 7.7 | High | 7d | Mitigate |
| E-1 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator escalates its own tool permissions beyond the user's authorization… | 9.9 | 6.5 | 7.5 | 5.0 | 7.5 | High | 7d | Mitigate |
| LLM-3 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Attacker crafts prompts that cause the LLM to generate tool call parameters con… | 9.3 | 6.5 | 8.5 | 5.0 | 7.5 | High | 7d | Mitigate |
| AG-2 | fresh | MCP Tool Server | L3 — Agent Framework | Attacker manipulates prompt context to cause the tool server to invoke tools ou… | 9.1 | 6.5 | 8.0 | 5.5 | 7.4 | High | 7d | Mitigate |
| D-1 | fresh | Guardrails Service | L6 — Security and Compliance | Attacker floods the guardrails service with complex prompts designed to maximiz… | 7.5 | 8.5 | 7.0 | 6.0 | 7.4 | High | 7d | Mitigate |
| S-1 | fresh | User | L7 — Agent Ecosystem | Attacker spoofs a legitimate user identity by stealing or replaying session tok… | 8.2 | 6.5 | 5.5 | 9.0 | 7.4 | High | 7d | Mitigate |
| S-3 | fresh | External API | L3 — Agent Framework | Compromised or spoofed external API returns malicious payloads masquerading as … | 8.2 | 6.5 | 5.5 | 9.0 | 7.4 | High | 7d | Mitigate |
| AG-1 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator autonomously escalates its own action scope by chaining multiple t… | 9.1 | 6.5 | 8.0 | 5.0 | 7.3 | High | 7d | Mitigate |
| LLM-2 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Attacker poisons knowledge base documents with adversarial content designed to … | 9.3 | 4.5 | 8.5 | 5.0 | 6.9 | Medium | 30d | Review |
| AG-3 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator generates and executes multi-step plans without checkpoints, makin… | 9.1 | 4.5 | 8.0 | 5.0 | 6.7 | Medium | 30d | Review |
| D-2 | fresh | MCP Tool Server | L3 — Agent Framework | Attacker triggers recursive or excessively long tool call chains through crafte… | 7.5 | 6.5 | 7.0 | 5.5 | 6.7 | Medium | 30d | Review |
| I-1 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator leaks sensitive context from the knowledge base or prior conversat… | 6.5 | 8.5 | 6.0 | 5.0 | 6.7 | Medium | 30d | Review |
| I-3 | fresh | MCP Tool Server | L3 — Agent Framework | Tool server includes API credentials, internal endpoint URLs, or stack traces i… | 6.5 | 6.5 | 6.0 | 5.5 | 6.2 | Medium | 30d | Review |
| T-1 | fresh | Knowledge Base | L2 — Data Operations | Attacker with write access to the vector store injects or modifies document emb… | 7.1 | 6.5 | 5.5 | 4.0 | 6.1 | Medium | 30d | Review |
| S-2 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Attacker crafts spoofed tool call responses that mimic the MCP Tool Server, inj… | 8.2 | 4.5 | 5.5 | 5.0 | 6.0 | Medium | 30d | Review |
| R-1 | fresh | User | L7 — Agent Ecosystem | User denies submitting a harmful or policy-violating prompt because session log… | 4.3 | 6.5 | 3.5 | 9.0 | 5.8 | Medium | 30d | Review |
| T-2 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Attacker tampers with orchestration configuration or intermediate state to alte… | 7.1 | 4.5 | 5.5 | 5.0 | 5.7 | Medium | 30d | Review |
| I-2 | fresh | Knowledge Base | L2 — Data Operations | Unauthorized access to vector store contents exposes confidential document embe… | 6.5 | 4.5 | 6.0 | 4.0 | 5.3 | Medium | 30d | Review |
| T-3 | fresh | Audit Logger | L5 — Evaluation and Observability | Attacker with elevated access modifies or truncates audit log entries to concea… | 7.1 | 4.5 | 5.5 | 3.0 | 5.3 | Medium | 30d | Review |
| R-2 | fresh | LLM Agent Orchestrator | L1 — Foundation Model | Orchestrator makes autonomous multi-step decisions that cannot be attributed to… | 4.3 | 6.5 | 3.5 | 5.0 | 5.0 | Medium | 30d | Review |

---

## 3. Dimensional Breakdown

Per-finding dimensional scores with CVSS 3.1 vectors and rationale summaries. CVSS vectors follow category defaults with per-threat refinement; exploitability derives from likelihood; scalability reflects category blast radius; reachability derives from trust zone placement.

| ID | CVSS Vector | CVSS Base | Exploitability | Scalability | Reachability |
|----|-------------|-----------|----------------|-------------|--------------|
| LLM-1 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` | 9.3 | 8.5 | 8.5 | 5.0 |
| AG-4 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L` | 9.1 | 8.5 | 8.0 | 5.5 |
| E-2 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` | 9.9 | 6.5 | 7.5 | 6.0 |
| E-1 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` | 9.9 | 6.5 | 7.5 | 5.0 |
| LLM-3 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` | 9.3 | 6.5 | 8.5 | 5.0 |
| AG-2 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L` | 9.1 | 6.5 | 8.0 | 5.5 |
| D-1 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` | 7.5 | 8.5 | 7.0 | 6.0 |
| S-1 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N` | 8.2 | 6.5 | 5.5 | 9.0 |
| S-3 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N` | 8.2 | 6.5 | 5.5 | 9.0 |
| AG-1 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L` | 9.1 | 6.5 | 8.0 | 5.0 |
| LLM-2 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` | 9.3 | 4.5 | 8.5 | 5.0 |
| AG-3 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L` | 9.1 | 4.5 | 8.0 | 5.0 |
| D-2 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` | 7.5 | 6.5 | 7.0 | 5.5 |
| I-1 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` | 6.5 | 8.5 | 6.0 | 5.0 |
| I-3 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` | 6.5 | 6.5 | 6.0 | 5.5 |
| T-1 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L` | 7.1 | 6.5 | 5.5 | 4.0 |
| S-2 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N` | 8.2 | 4.5 | 5.5 | 5.0 |
| R-1 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N` | 4.3 | 6.5 | 3.5 | 9.0 |
| T-2 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L` | 7.1 | 4.5 | 5.5 | 5.0 |
| I-2 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` | 6.5 | 4.5 | 6.0 | 4.0 |
| T-3 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L` | 7.1 | 4.5 | 5.5 | 3.0 |
| R-2 | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N` | 4.3 | 6.5 | 3.5 | 5.0 |

---

## 4. Exploitability Analysis

Exploitability scores reflect the practical attack feasibility for each finding, considering known techniques, attack complexity, tooling availability, and required skill level. Scores are derived from the OWASP 3x3 likelihood field with mapping: HIGH→8.5, MEDIUM→6.5, LOW→4.5. Higher scores indicate easier exploitation.

**Exploitability distribution (averaged by category):**

| Category | Findings | Avg Exploitability |
|----------|----------|-------------------|
| agentic | 4 | 6.5 |
| denial-of-service | 2 | 7.5 |
| info-disclosure | 3 | 6.5 |
| llm | 3 | 6.5 |
| privilege-escalation | 2 | 6.5 |
| repudiation | 2 | 6.5 |
| spoofing | 3 | 5.8 |
| tampering | 3 | 5.2 |

---

## 5. Scalability Analysis

Scalability measures the blast radius and operational economics of an attack — how easily the attack scales from one target to many, and what resources the attacker requires. LLM and Agentic categories score highest because successful attacks propagate across tool-server boundaries (S:C in CVSS terms) and automate well. Single-target attacks like Repudiation score lowest.

**Scalability distribution (by category):**

| Category | Default Scalability | Rationale |
|----------|---------------------|-----------|
| llm | 8.5 | Prompt injection automates at scale; affects every tool-server tenant |
| agentic | 8.0 | Scope-crossing actions trigger downstream tool server impact |
| privilege-escalation | 7.5 | Privilege gain enables lateral movement |
| denial-of-service | 7.0 | Resource exhaustion scales linearly with attacker bandwidth |
| info-disclosure | 6.0 | Bulk retrieval enables mass data extraction |
| spoofing | 5.5 | Spoofed sessions scale with token theft volume |
| tampering | 5.5 | Integrity compromises require targeted access |
| repudiation | 3.5 | Single-user evasion, limited propagation |

---

## 6. Reachability Analysis

Reachability scores derive from component trust zone placement and architecture barrier analysis. Untrusted zones (User Zone, External Services) score 9.0; Trusted Application Zone components receive lower baselines (3.0-6.0) reflecting their position behind the first authentication/input-validation barrier at the Guardrails Service.

**Component reachability (by trust zone):**

| Component | Trust Zone | Reachability |
|-----------|-----------|--------------|
| User | Untrusted | 9.0 |
| External API | Untrusted | 9.0 |
| Guardrails Service | Semi-Trusted | 6.0 |
| MCP Tool Server | Semi-Trusted | 5.5 |
| LLM Agent Orchestrator | Semi-Trusted | 5.0 |
| Knowledge Base | Trusted | 4.0 |
| Audit Logger | Trusted | 3.0 |

No architecture barrier adjustments applied — barriers (TLS, input validation, egress filtering) are captured in per-component mitigation, not in reachability.

---

## 7. Composite Score & Severity Bands

Composite scores combine the four dimensions using the formula:

```
Composite = (0.35 × CVSS) + (0.30 × Exploit) + (0.15 × Scale) + (0.20 × Reach)
```

Severity bands map from the composite score:

| Band | Range | Findings | % |
|------|-------|----------|---|
| Critical | 9.0–10.0 | 0 | 0.0% |
| High | 7.0–8.9 | 10 | 45.5% |
| Medium | 4.0–6.9 | 12 | 54.5% |
| Low | 0.0–3.9 | 0 | 0.0% |

---

## 8. Governance Fields

Per-finding governance metadata including risk owner (unassigned on first run), remediation SLA (driven by severity band), disposition (Mitigate for Critical/High, Review for Medium/Low), and review date (today + SLA).

| ID | Severity | Risk Owner | SLA | Disposition | Review Date |
|----|----------|------------|-----|-------------|-------------|
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| AG-4 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| E-2 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| E-1 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| LLM-3 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| AG-2 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| S-1 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| S-3 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| AG-1 | High | Unassigned | 7d | Mitigate | 2026-04-17 |
| LLM-2 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| AG-3 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| D-2 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| I-1 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| I-3 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| T-1 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| S-2 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| I-2 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| T-3 | Medium | Unassigned | 30d | Review | 2026-05-10 |
| R-2 | Medium | Unassigned | 30d | Review | 2026-05-10 |

---

## 9. Methodology Notes

This risk scoring report applies the tachi four-dimensional model (CVSS 3.1 base + exploitability + scalability + reachability) to 22 findings from the upstream `threats.md` file. Category default CVSS vectors are used as baselines with per-threat refinement via the OWASP 3x3 likelihood/impact signals. Exploitability reflects attack feasibility derived from the `likelihood` field; scalability reflects category blast radius; reachability reflects trust zone position within the architecture.

**Scoring assumptions:**
- CVSS base: category default from `schemas/risk-scoring.yaml` category_defaults table
- Exploitability: mapped from `likelihood` (HIGH=8.5, MEDIUM=6.5, LOW=4.5)
- Scalability: category default (LLM/AG highest due to S:C scope-crossing)
- Reachability: component trust zone mapping from architecture.md

Composite scores are rounded to one decimal place. Severity bands apply inclusive lower bounds (e.g., 7.0 = High, 9.0 = Critical).

**Reproducibility**: All dimensional inputs and formulas are documented above. Re-running this report with the same `threats.md` and category defaults will produce byte-identical output (modulo the `date` field).
