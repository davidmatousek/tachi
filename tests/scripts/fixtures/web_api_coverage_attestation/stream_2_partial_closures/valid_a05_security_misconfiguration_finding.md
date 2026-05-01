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

# Stream 2 Wave 1 Fixture — A05 Security Misconfiguration Closure on tachi-privilege-escalation Pattern Category 11

Validates that the F-241 Stream 2 closure of OWASP A05:2021 (Security
Misconfiguration) — added as a non-mobile Indicator extension on
`tachi-privilege-escalation` Pattern Category 11 — is operational by surfacing a
representative finding citing OWASP A05:2021 as `relationship: primary` plus
≥1 `relationship: related` CWE entry per BLP-01 §8 Quality Bar.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| E-1 | privilege-escalation | A05 Security Misconfiguration (Server-Side Variant) | Spring Boot Application | Spring Boot Actuator endpoints (/actuator/env, /actuator/heapdump) reachable without authentication on the production network, exposing environment variables including database connection strings and IAM credentials | Critical | Disable management endpoints on the production network via `management.endpoints.web.exposure.exclude=*` then explicitly include only `health,info`; rotate all credentials exposed via prior /env access; integrate Spring Security on remaining management endpoints |

## 9. Source Attribution

```yaml
E-1:
  - {taxonomy: owasp, id: "A05:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-1188", relationship: related}
  - {taxonomy: cwe, id: "CWE-732", relationship: related}
```

## Closure Evidence

- **Pattern Category Citation**: `tachi-privilege-escalation` Pattern Category 11 — Security Misconfiguration Privilege-Gain Variant — Mobile (OWASP M8:2024) and Server-Side (OWASP A05:2021), `Indicators (server-side / OWASP A05:2021)` subsection at `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md`
- **Primary Source Block**: OWASP A05:2021 link added to Pattern Category 11 Primary source list and to file-end Primary Sources section
- **Indicator Extension**: 6 server-side indicators authored covering admin-endpoint exposure, default credentials, unnecessary management features, default-permissive cloud IAM, weak management controls, and default-permissive feature flags
- **BLP-01 §8 Quality Bar**: ≥1 host agent (`tachi-privilege-escalation`) + ≥1 detection-pattern category (Pattern Category 11)
