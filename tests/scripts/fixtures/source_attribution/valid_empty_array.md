---
schema_version: "1.5"
date: "2026-04-21"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-21T09-30-00"
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

# Source Attribution Present-but-Empty Fixture — F-A2 T013

One finding (D-4) explicitly declares ``source_attribution: []`` in the Section 9
block. Exercises the V6 present-but-empty semantic: the parser MUST inject the
``source_attribution`` key with value ``[]`` on the returned finding dict,
distinct from the absent-key case (US-189-2 AC-2).

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| D-4 | denial-of-service | — | Rate Limiter | Unthrottled inbound traffic exhausts downstream capacity | High | Token-bucket rate limit per caller |

## 9. Source Attribution

```yaml
D-4: []
```
