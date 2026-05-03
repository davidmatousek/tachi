---
schema_version: "1.5"
date: "2026-04-21"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-21T14-15-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
has-source-attribution: true
---

# Source Attribution Invalid-Relationship Fixture — F-A2 T019

One finding (I-7) carries an attribution record whose ``relationship`` value is
outside the closed 3-value enum. Exercises V2 (parser-tier relationship enum
validation) — parser MUST raise ``ValueError`` naming the finding ID, the bad
value, and the closed domain.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| I-7 | info-disclosure | — | Metrics Exporter | Exporter leaks API keys via stack trace in debug endpoint | High | Disable debug endpoints in production builds |

## 9. Source Attribution

```yaml
I-7:
  - {taxonomy: owasp, id: LLM05, relationship: fabricated_value}
```
