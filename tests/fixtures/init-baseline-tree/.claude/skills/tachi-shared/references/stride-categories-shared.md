---
type: shared-reference
name: stride-categories-shared
version: 1.0.0
source_schema: schemas/finding.yaml
source_reference: .claude/skills/tachi-orchestration/references/dispatch-rules.md
consumers:
  - orchestrator
  - spoofing
  - tampering
  - repudiation
  - info-disclosure
  - denial-of-service
  - privilege-escalation
  - prompt-injection
  - data-poisoning
  - model-theft
  - agent-autonomy
  - tool-abuse
---

# STRIDE+AI Categories — Shared Reference

Canonical definitions for all 11 threat categories used across the tachi pipeline: 6 STRIDE categories and 5 AI-specific categories. This is the single source of truth for category descriptions, ID prefixes, agent mappings, and the DFD element-to-category applicability matrix. All consuming agents should Read this file rather than maintaining inline definitions.

---

## STRIDE Categories (6)

| ID Prefix | Category | Internal Name | Agent | Description |
|-----------|----------|---------------|-------|-------------|
| S | Spoofing | spoofing | tachi-spoofing | Threats where an attacker assumes the identity of another entity -- user, service, or system component. Undermines authentication guarantees. |
| T | Tampering | tampering | tachi-tampering | Threats where an attacker modifies data or code without authorization. Undermines data integrity guarantees. |
| R | Repudiation | repudiation | tachi-repudiation | Threats where an attacker denies having performed an action. Undermines accountability and audit trail guarantees. |
| I | Information Disclosure | info-disclosure | tachi-info-disclosure | Threats where sensitive data is exposed to unauthorized parties. Undermines confidentiality guarantees. |
| D | Denial of Service | denial-of-service | tachi-denial-of-service | Threats where system availability is degraded or eliminated. Undermines availability guarantees. |
| E | Elevation of Privilege | privilege-escalation | tachi-privilege-escalation | Threats where an attacker gains higher access than authorized. Undermines authorization guarantees. |

---

## AI Categories (5)

| ID Prefix | Category | Internal Name | Agent | OWASP Reference | Output Table |
|-----------|----------|---------------|-------|-----------------|-------------|
| LLM | Prompt Injection | llm | tachi-prompt-injection | OWASP LLM01:2025 | LLM Threats |
| LLM | Data Poisoning | llm | tachi-data-poisoning | OWASP LLM03:2025 | LLM Threats |
| LLM | Model Theft | llm | tachi-model-theft | OWASP LLM10:2025 | LLM Threats |
| AG | Agent Autonomy | agentic | tachi-agent-autonomy | ASI-01 | Agentic Threats |
| AG | Tool Abuse | agentic | tachi-tool-abuse | MCP-03 | Agentic Threats |

### Agent-to-Table Mapping

AI findings are grouped into 2 output tables:

| Output Table | ID Prefix | Agents | Reference Standards |
|--------------|-----------|--------|---------------------|
| Agentic Threats (AG) | AG | agent-autonomy, tool-abuse | OWASP Agentic Top 10, MCP Top 10 |
| LLM Threats (LLM) | LLM | prompt-injection, data-poisoning, model-theft | OWASP LLM Top 10 v2025 |

---

## DFD Element-to-Category Applicability Matrix

Each component from the architecture input is mapped to its applicable threat categories based on its DFD element type. Agents are dispatched only for applicable categories.

| DFD Element Type | S | T | R | I | D | E | Applicable Categories |
|------------------|---|---|---|---|---|---|----------------------|
| External Entity | x | | x | | | | S, R |
| Process | x | x | x | x | x | x | S, T, R, I, D, E |
| Data Store | | x | | x | x | | T, I, D |
| Data Flow | | x | | x | x | | T, I, D |

**Category legend**: S = Spoofing, T = Tampering, R = Repudiation, I = Information Disclosure, D = Denial of Service, E = Elevation of Privilege

Every DFD element type maps to at least 2 STRIDE categories, so the normalization step never produces zero applicable categories for a valid component.

---

## AI Keyword Dispatch Rules

AI dispatch is additive to STRIDE dispatch -- it never replaces STRIDE categories. A component always receives its STRIDE agents first, and AI agents are added when keywords match.

### LLM Keywords

When any of these keywords are found in a component's name or description (case-insensitive), dispatch LLM threat agents (prompt-injection, data-poisoning, model-theft):

- `"LLM"`
- `"model"`
- `"GPT"`
- `"Claude"`

### AG Keywords

When any of these keywords are found in a component's name or description (case-insensitive), dispatch AG threat agents (agent-autonomy, tool-abuse):

- `"agent"`
- `"autonomous"`
- `"orchestrator"`
- `"MCP server"`
- `"tool server"`
- `"plugin"`

### Matching Rules

1. **Case-insensitive**: All keyword matching is case-insensitive.
2. **Scope**: Keywords are matched against both component name and description.
3. **Multi-word keywords**: Keywords containing spaces match as a complete phrase (adjacent, in order).
4. **Substring matching**: A keyword match anywhere within the name or description triggers dispatch.
5. **Dual-dispatch**: When a component matches keywords from both LLM and AG categories, both agent groups are dispatched.

### Ambiguity Note

The keyword `"model"` is ambiguous -- it could refer to a data model or an LLM. When matched, dispatch the LLM agents and include a note: `"Keyword 'model' matched -- may refer to data model rather than LLM. AI agents dispatched for coverage; review findings for relevance."`

---

## Coverage Checklist Category Mapping

Category strings from `schemas/coverage-checklists.yaml` map to finding ID prefixes for coverage evaluation:

| Checklist Category | Finding Prefix | Threat Agent(s) |
|-------------------|---------------|-----------------|
| `spoofing` | S | tachi-spoofing |
| `tampering` | T | tachi-tampering |
| `repudiation` | R | tachi-repudiation |
| `info-disclosure` | I | tachi-info-disclosure |
| `denial-of-service` | D | tachi-denial-of-service |
| `privilege-escalation` | E | tachi-privilege-escalation |
| `agentic` | AG | tachi-tool-abuse, tachi-agent-autonomy |
| `llm` | LLM | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft |

---

## Correlation Rules

Cross-category correlation rules for detecting related STRIDE and AI findings on the same component:

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

Correlation detection is deterministic and rule-based. When findings from a STRIDE and AI category match a rule for the same component, they form a correlation group (CG-N). One correlation group per component, regardless of how many rules triggered.
