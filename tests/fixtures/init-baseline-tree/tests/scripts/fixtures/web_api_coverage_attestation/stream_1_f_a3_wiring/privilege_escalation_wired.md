---
schema_version: "1.8"
date: "2026-05-01"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-05-01T09-15-00"
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

# F-A3 Wave 1 Fixture — Privilege-Escalation Host Populator Wiring

Validates that `tachi-privilege-escalation` agent emits `source_attribution` arrays per ADR-037 D-3.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| E-1 | privilege-escalation | IDOR | Document API | Resource access without ownership validation | Critical | Per-request ownership check; UUIDs; tenant-scoped queries |

## 9. Source Attribution

```yaml
E-1:
  - {taxonomy: owasp, id: "A01:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-639", relationship: related}
  - {taxonomy: cwe, id: "CWE-285", relationship: related}
```
