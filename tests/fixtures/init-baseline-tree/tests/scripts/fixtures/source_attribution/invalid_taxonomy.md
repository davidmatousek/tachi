---
schema_version: "1.5"
date: "2026-04-21"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-21T14-00-00"
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

# Source Attribution Invalid-Taxonomy Fixture — F-A2 T018

One finding (T-9) carries an attribution record whose ``taxonomy`` value is
outside the closed 5-value enum. Exercises V1 (parser-tier taxonomy enum
validation) — parser MUST raise ``ValueError`` naming the finding ID, the bad
value, and the closed domain.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| T-9 | tampering | — | Config Service | Attacker mutates a deployment manifest to inject privileged container | High | Signed manifest verification |

## 9. Source Attribution

```yaml
T-9:
  - {taxonomy: not-a-real-taxonomy, id: X, relationship: primary}
```
