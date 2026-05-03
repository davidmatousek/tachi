---
schema_version: "1.8"
date: "2026-05-01"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-05-01T09-00-00"
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

# F-A3 Wave 1 Fixture — Spoofing Host Populator Wiring

Validates that `tachi-spoofing` agent emits `source_attribution` arrays with one
`relationship: primary` entry plus ≥1 `relationship: related` CWE entry, mirroring
the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| S-1 | spoofing | Authentication Bypass | API Gateway | Bearer token accepted without signing-key verification | Critical | Validate JWT signature against JWKS allowlist; reject alg=none |

## 9. Source Attribution

```yaml
S-1:
  - {taxonomy: owasp, id: "A07:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-287", relationship: related}
  - {taxonomy: cwe, id: "CWE-345", relationship: related}
```
