# Contract: Finding Intermediate Representation

**Schema File**: `schemas/finding.yaml`
**Producers**: All threat agents (6 STRIDE + 5 AI)
**Consumers**: Output templates, SARIF export (F-006), narrative report (F-007), infographic (F-008)

## Purpose

The IR schema is the single contract point between agents and all output formats. Every agent produces findings conforming to this schema. Every output template and export format consumes findings from this schema. This separation allows new output formats to be added without changing any agent.

## Schema Version

`1.0` — established from day one. Breaking changes require a new major version with migration guidance.

## Fields

```yaml
finding:
  id:
    type: string
    pattern: "^(S|T|R|I|D|E|AG|LLM)-\\d+$"
    description: "Unique finding identifier. Prefix = category, suffix = sequential number."
    examples: ["S-1", "T-3", "AG-2", "LLM-1"]

  category:
    type: string
    enum: [spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm]
    description: "Threat category. Maps 1:1 to agent type."

  component:
    type: string
    description: "Target component name from architecture input."
    examples: ["API Gateway", "User Database", "LLM Agent"]

  threat:
    type: string
    description: "Description of the identified threat."
    examples: ["Attacker could spoof authentication tokens to impersonate legitimate users"]

  likelihood:
    type: string
    enum: [LOW, MEDIUM, HIGH]
    description: "Assessed probability of exploitation using OWASP likelihood factors."

  impact:
    type: string
    enum: [LOW, MEDIUM, HIGH]
    description: "Assessed severity of exploitation using OWASP impact factors."

  risk_level:
    type: string
    enum: [Critical, High, Medium, Low, Note]
    description: "Computed from OWASP 3x3 matrix (likelihood x impact)."

  mitigation:
    type: string
    description: "Recommended countermeasure."
    examples: ["Implement JWT token validation with RS256 signing"]

  references:
    type: list[string]
    description: "OWASP IDs, CVE IDs, or framework citations."
    examples: ["OWASP LLM01:2025", "ASI-01", "MCP-03", "CWE-287"]

  dfd_element_type:
    type: string
    enum: [External Entity, Process, Data Store, Data Flow]
    description: "DFD classification of the target component."
```

## Validation Rules

- `id` prefix must match `category` (e.g., S-* for spoofing, AG-* for agentic)
- `risk_level` must match OWASP 3x3 computation from `likelihood` and `impact`
- `references` must contain at least one entry for AI categories (agentic, llm)
