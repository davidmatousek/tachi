# Contract: Output Schema

**Schema File**: `schemas/output.yaml`
**Producers**: Template engine (applying IR findings to output template)
**Consumers**: Integrators, SARIF export (F-006), downstream features

## Purpose

Defines the complete structure of a threat model output (`threats.md`). Validates that generated outputs contain all required sections with correct structure.

## Output Structure

```yaml
output:
  frontmatter:
    required: true
    fields:
      schema_version: {type: string, value: "1.0"}
      date: {type: string, format: "YYYY-MM-DD"}
      input_format: {type: string, enum: [ascii, free-text, mermaid, plantuml, c4]}
      classification: {type: string, default: "confidential"}

  sections:
    - name: System Overview
      required: true
      contains: [components_list, data_flows, technologies]

    - name: Trust Boundaries
      required: true
      contains: [zone_names, boundary_crossings]

    - name: STRIDE Tables
      required: true
      count: 6
      categories: [Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege]
      row_fields: [id, component, threat, likelihood, impact, risk_level, mitigation]

    - name: AI Threat Tables
      required: true
      count: 2
      categories: [Agentic (AG), LLM]
      row_fields: [id, component, threat, owasp_reference, likelihood, impact, risk_level, mitigation]

    - name: Coverage Matrix
      required: true
      structure: "rows=components, columns=S/T/R/I/D/E/AG/LLM, cells=finding_count"

    - name: Risk Summary
      required: true
      levels: [Critical, High, Medium, Low, Note]
      fields: [count, percentage]

    - name: Recommended Actions
      required: true
      sort_order: "risk_level descending"
      fields: [finding_id, component, threat, risk_level, mitigation]
```

## Naming Convention

Output files follow: `YYYY-MM-DD-{phase}/threats.md` with immutable retention.

## SARIF Severity Mapping

| Risk Level | SARIF Severity | CVSS Score Range |
|-----------|---------------|-----------------|
| Critical | error | 9.0-10.0 |
| High | error | 7.0-8.9 |
| Medium | warning | 4.0-6.9 |
| Low | note | 0.1-3.9 |
| Note | none | 0.0 |
