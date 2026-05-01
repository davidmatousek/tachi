---
schema_version: "1.8"
date: "2026-05-01"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-05-01T09-20-00"
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

# F-A3 Wave 1 Fixture — Repudiation Host Populator Wiring

Validates that `tachi-repudiation` agent emits `source_attribution` arrays per ADR-037 D-3.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| R-1 | repudiation | Missing Audit Trail | Authentication Service | Failed logins / MFA bypasses not logged | High | Structured audit events; immutable log storage; retention per regulation |

## 9. Source Attribution

```yaml
R-1:
  - {taxonomy: owasp, id: "A09:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-778", relationship: related}
  - {taxonomy: cwe, id: "CWE-223", relationship: related}
```
