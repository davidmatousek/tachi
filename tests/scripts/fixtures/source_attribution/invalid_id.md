---
schema_version: "1.5"
date: "2026-04-21"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-21T14-30-00"
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

# Source Attribution Invalid-ID Fixture — F-A2 T020

One finding (E-2) carries an attribution record whose ``id`` is syntactically
valid (non-empty string, closed enums pass) but does NOT resolve in the target
catalog. Exercises V4 (validator-tier referential integrity) — parse_threats_findings
MUST succeed; validate_source_attribution MUST return a ValidationError naming
the finding ID, the unresolved ID, and the target YAML path.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| E-2 | privilege-escalation | — | Identity Service | Attacker leverages broken role-inheritance to gain admin scope | High | Explicit role grant audit + least-privilege review |

## 9. Source Attribution

```yaml
E-2:
  - {taxonomy: owasp, id: NOT-A-REAL-OWASP-ID, relationship: primary}
```
