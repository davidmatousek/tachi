---
schema_version: "1.8"
date: "2026-05-01"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-05-01T09-10-00"
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

# F-A3 Wave 1 Fixture — Info-Disclosure Host Populator Wiring

Validates that `tachi-info-disclosure` agent emits `source_attribution` arrays per ADR-037 D-3.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| I-1 | info-disclosure | Verbose Error Messages | API Error Handler | Stack traces exposed in error responses | High | Generic error messages + correlation IDs; log full trace server-side |

## 9. Source Attribution

```yaml
I-1:
  - {taxonomy: owasp, id: "A02:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-209", relationship: related}
  - {taxonomy: cwe, id: "CWE-200", relationship: related}
```
