---
schema_version: "1.5"
date: "2026-04-20"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-20T09-00-00"
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

# Source Attribution Multi-Record Fixture — F-A2 T006

One finding (LLM-5) carries three attribution records spanning 3 distinct external taxonomies.
Exercises FR-007 round-trip with input-order preservation (US-189-1 AC-3).

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| LLM-5 | llm | — | LLM Response Handler | Unsanitized LLM output renders into downstream HTML surface | High | Strict output encoding + CSP |

## 9. Source Attribution

```yaml
LLM-5:
  - {taxonomy: owasp, id: LLM05, relationship: primary}
  - {taxonomy: cwe, id: CWE-116, relationship: primary}
  - {taxonomy: mitre-atlas, id: AML.T0051, relationship: primary}
```
