---
schema_version: "1.5"
date: "2026-04-20"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-20T09-15-00"
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

# Source Attribution Single-Record Fixture — F-A2 T007

One finding (S-1) carries one attribution record with the relationship field omitted,
exercising the V2 default-injection path (parser injects relationship: "primary" on emission).

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| S-1 | spoofing | — | API Gateway | Attacker forges JWT to impersonate legitimate users | High | Implement JWT RS256 validation with short-lived tokens |

## 9. Source Attribution

```yaml
S-1:
  - {taxonomy: owasp, id: A01}
```
