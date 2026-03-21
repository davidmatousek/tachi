# Data Model: Project Skeleton & Interface Contract

## Overview

F-001 is a knowledge system feature — all entities are content artifacts (markdown + YAML files), not database tables. The "data model" defines the structure of the Intermediate Representation (IR) that serves as the contract between threat agents and output templates.

## Entity: Finding (IR Schema)

The atomic unit of threat analysis. Produced by agents, consumed by templates and downstream features.

| Field | Type | Allowed Values | Description |
|-------|------|---------------|-------------|
| `id` | string | Pattern: `{CATEGORY_PREFIX}-{N}` (e.g., S-1, AG-3, LLM-2) | Unique finding identifier within a threat model |
| `category` | string | `spoofing`, `tampering`, `repudiation`, `info-disclosure`, `denial-of-service`, `privilege-escalation`, `agentic`, `llm` | Threat category — maps to agent type |
| `component` | string | Free-text | Target component name from architecture input |
| `threat` | string | Free-text | Description of the identified threat |
| `likelihood` | string | `LOW`, `MEDIUM`, `HIGH` | Assessed probability of exploitation |
| `impact` | string | `LOW`, `MEDIUM`, `HIGH` | Assessed severity of exploitation |
| `risk_level` | string | `Critical`, `High`, `Medium`, `Low`, `Note` | Computed from OWASP 3x3 matrix (likelihood x impact) |
| `mitigation` | string | Free-text | Recommended countermeasure |
| `references` | list[string] | OWASP IDs, CVE IDs, framework citations | Supporting references |
| `dfd_element_type` | string | `External Entity`, `Process`, `Data Store`, `Data Flow` | DFD classification of the target component |

### ID Prefix Convention

| Prefix | Category | Agent Source |
|--------|----------|-------------|
| S | Spoofing | agents/stride/spoofing.md |
| T | Tampering | agents/stride/tampering.md |
| R | Repudiation | agents/stride/repudiation.md |
| I | Information Disclosure | agents/stride/info-disclosure.md |
| D | Denial of Service | agents/stride/denial-of-service.md |
| E | Elevation of Privilege | agents/stride/privilege-escalation.md |
| AG | Agentic Threats | agents/ai/agent-autonomy.md, agents/ai/tool-abuse.md |
| LLM | LLM Threats | agents/ai/prompt-injection.md, agents/ai/data-poisoning.md, agents/ai/model-theft.md |

### Risk Level Computation (OWASP 3x3)

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## Entity: DFD Element

A component in the architecture input classified by Data Flow Diagram type.

| Field | Type | Allowed Values | Description |
|-------|------|---------------|-------------|
| `name` | string | Free-text | Component name from architecture input |
| `type` | string | `External Entity`, `Process`, `Data Store`, `Data Flow` | DFD classification |
| `stride_categories` | list[string] | Per normalization table | Applicable STRIDE categories |
| `ai_dispatch` | list[string] | `agentic`, `llm`, or empty | AI agent categories to dispatch |

### STRIDE-per-Element Normalization

| DFD Element Type | Applicable STRIDE Categories |
|------------------|------------------------------|
| External Entity | S, R |
| Process | S, T, R, I, D, E |
| Data Store | T, I, D |
| Data Flow | T, I, D |

### AI Extension Dispatch Rules

| Keyword Pattern | Dispatches |
|----------------|------------|
| "LLM", "model", "GPT", "Claude" | LLM Threat Agents |
| "agent", "autonomous", "orchestrator" | Agentic Threat Agents |
| "MCP server", "tool server", "plugin" | Agentic Threat Agents |

Elements matching both patterns dispatch both agent categories. Deduplication occurs at the coverage matrix level.

## Entity: Threat Model Output

The structured document produced by applying the template to IR findings.

| Section | Required | Content |
|---------|----------|---------|
| Frontmatter | Yes | `schema_version`, `date`, `input_format`, `classification` |
| System Overview | Yes | Parsed architecture summary (components, flows, technologies) |
| Trust Boundaries | Yes | Zone names and boundary crossings |
| STRIDE Tables (6) | Yes | One table per STRIDE category with finding rows |
| AI Threat Tables (2) | Yes | AG and LLM tables with finding rows |
| Coverage Matrix | Yes | Components × categories matrix with finding counts |
| Risk Summary | Yes | Counts per risk level (Critical/High/Medium/Low/Note) |
| Recommended Actions | Yes | Findings sorted by risk level descending |

## Relationships

```
Architecture Input
       │
       ▼
  DFD Elements ──── dispatch ──→ Threat Agents
       │                              │
       │                              ▼
       │                         Findings (IR)
       │                              │
       ▼                              ▼
  Trust Boundaries ──→ Threat Model Output ←── Output Template
```
