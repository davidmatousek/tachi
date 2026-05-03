---
schema_version: "1.8"
date: "2026-05-01"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-05-01T09-05-00"
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

# F-A3 Wave 1 Fixture — Tampering Host Populator Wiring

Validates that `tachi-tampering` agent emits `source_attribution` arrays per ADR-037 D-3.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| T-1 | tampering | SQL Injection | User Search Service | Concatenated query parameter into SQL WHERE clause | Critical | Use parameterized queries; least-privilege DB role |

## 9. Source Attribution

```yaml
T-1:
  - {taxonomy: owasp, id: "A03:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-89", relationship: related}
```
