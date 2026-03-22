# Data Model: STRIDE Threat Agents

## Agent Inventory

| # | Agent File | Category | Threat Class | DFD Targets | Lines | Status |
|---|-----------|----------|-------------|-------------|-------|--------|
| 1 | `agents/stride/spoofing.md` | spoofing | S | External Entity, Process | ~101 | Content-complete |
| 2 | `agents/stride/tampering.md` | tampering | T | Process, Data Store, Data Flow | ~107 | Content-complete |
| 3 | `agents/stride/repudiation.md` | repudiation | R | External Entity, Process | ~105 | Content-complete |
| 4 | `agents/stride/info-disclosure.md` | info-disclosure | I | Process, Data Store, Data Flow | ~116 | Content-complete |
| 5 | `agents/stride/denial-of-service.md` | denial-of-service | D | Process, Data Store, Data Flow | ~115 | Content-complete |
| 6 | `agents/stride/privilege-escalation.md` | privilege-escalation | E | Process | ~115 | Content-complete |

## STRIDE-per-Element Validation Matrix

Reference matrix for DFD element targeting validation:

| DFD Element | S | T | R | I | D | E |
|-------------|---|---|---|---|---|---|
| **Processes** | X | X | X | X | X | X |
| **Data Flows** | | X | | X | X | |
| **Data Stores** | | X | | X | X | |
| **External Entities** | X | | X | | | |

## OWASP API Security Top 10 2023 Cross-Reference Map

P1 deliverable — OWASP API Security references to add per agent:

| Agent | Primary API Security Reference | Rationale |
|-------|-------------------------------|-----------|
| spoofing.md | API2:2023 Broken Authentication | Authentication failures = identity spoofing |
| tampering.md | API3:2023 Broken Object Property Level Authorization | Mass assignment = unauthorized data modification |
| repudiation.md | API9:2023 Improper Inventory Management | Undocumented endpoints lack audit coverage |
| info-disclosure.md | API3:2023 Broken Object Property Level Authorization | Excessive data exposure in responses |
| denial-of-service.md | API4:2023 Unrestricted Resource Consumption | Rate limiting and resource quota gaps |
| privilege-escalation.md | API1:2023 Broken Object Level Authorization, API5:2023 Broken Function Level Authorization | Authorization bypass = privilege escalation |

## Finding IR Field Inventory

All agents must produce findings with these 10 fields (from `schemas/finding.yaml` v1.0):

| # | Field | Type | Validation Rule |
|---|-------|------|----------------|
| 1 | id | string | Pattern: `^(S|T|R|I|D|E)-\d+$` |
| 2 | category | string | Enum: spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation |
| 3 | component | string | Must match named component from architecture input |
| 4 | threat | string | Must describe attacker action + violated trust assumption |
| 5 | likelihood | string | Enum: LOW, MEDIUM, HIGH |
| 6 | impact | string | Enum: LOW, MEDIUM, HIGH |
| 7 | risk_level | string | Enum: Critical, High, Medium, Low, Note — computed from OWASP 3x3 |
| 8 | mitigation | string | Must be actionable with specific technology/configuration |
| 9 | references | list[string] | At least one OWASP, CWE, or ATT&CK identifier |
| 10 | dfd_element_type | string | Enum: External Entity, Process, Data Store, Data Flow |

## Agent Structural Schema

All 6 agents must follow this canonical section order:

```
1. YAML frontmatter (agent_name, category, threat_class, dfd_targets, owasp_references, output_schema)
2. # {Category} Threat Agent
3. ## Purpose
4. ## Detection Scope
   ### Targeted DFD Element Types
   ### Patterns and Indicators
     **{Pattern Category 1}**
     **{Pattern Category 2}**
     ...
5. ## Finding Template
   ### Risk Level Computation
6. ## References
```
