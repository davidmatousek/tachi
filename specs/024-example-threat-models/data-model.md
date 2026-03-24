# Data Model: Example Threat Models

## Entities

### Example
A self-contained directory under `examples/` targeting a specific architecture type.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Directory name (kebab-case: `web-app`, `agentic-app`, `microservices`) |
| architecture | file | `architecture.md` — Mermaid flowchart input |
| threats | file | `threats.md` — schema v1.1 output with OWASP appendix |

### Architecture Diagram
Mermaid flowchart describing system components, trust boundaries, and data flows.

| Attribute | Type | Constraints |
|-----------|------|-------------|
| format | enum | `flowchart TD` (Mermaid) |
| components | list | Minimum 4 labeled nodes |
| trust_zones | list | Subgraph blocks, minimum 2 zones |
| data_flows | list | Labeled arrows between components |

### Threat Model Output
Structured document conforming to output schema v1.1.

| Section | Required | Content |
|---------|----------|---------|
| Frontmatter | Yes | `schema_version: "1.1"`, `date`, `input_format: "mermaid"`, `classification` |
| 1. System Overview | Yes | Components, data flows, technologies |
| 2. Trust Boundaries | Yes | Trust zones, boundary crossings |
| 3. STRIDE Tables | Yes | 6 tables (S, T, R, I, D, E) |
| 4. AI Threat Tables | Yes | 2 tables (AG, LLM) — may be empty |
| 4a. Correlated Findings | Yes | Cross-agent groups — may be empty |
| 5. Coverage Matrix | Yes | Components x categories, three-state cells |
| 6. Risk Summary | Yes | OWASP 3x3 risk counts |
| 7. Recommended Actions | Yes | All findings sorted by risk desc |

### OWASP Cross-Reference Appendix
Mapping table appended to `threats.md` linking findings to framework categories.

| Attribute | Type | Description |
|-----------|------|-------------|
| finding_id | string | Reference to a finding in Sections 3/4 |
| owasp_category | string | Framework category ID (A01, ASI01, MCP01, etc.) |
| category_name | string | Human-readable category name |
| notes | string | Optional context for the mapping |

## Relationships

```
Example 1──1 Architecture Diagram
Example 1──1 Threat Model Output
Threat Model Output 1──1 OWASP Appendix
Threat Model Output 1──* Finding (in STRIDE/AI tables)
Finding *──0..1 Correlation Group (in Section 4a)
Finding *──0..* OWASP Mapping (in appendix)
```

## STRIDE-per-Element Rules

| DFD Element Type | S | T | R | I | D | E |
|------------------|---|---|---|---|---|---|
| External Entity | Yes | — | Yes | — | — | — |
| Process | Yes | Yes | Yes | Yes | Yes | Yes |
| Data Store | — | Yes | — | Yes | Yes | — |
| Data Flow | — | Yes | — | Yes | Yes | — |

## Correlation Rules

| Rule | STRIDE | AI | Basis |
|------|--------|----|-------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |
