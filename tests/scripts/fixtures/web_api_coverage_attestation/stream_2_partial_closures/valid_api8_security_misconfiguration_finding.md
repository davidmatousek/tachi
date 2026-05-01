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

# Stream 2 Wave 2 Fixture — API8:2023 Security Misconfiguration Closure on tachi-privilege-escalation Pattern Category 11

Validates that the F-241 Stream 2 closure of OWASP API8:2023 (Security
Misconfiguration) — extended as the API-specific sub-variant of
`tachi-privilege-escalation` Pattern Category 11 (Security Misconfiguration
Privilege-Gain Variant — Mobile + Server-Side + API-Specific), with API-specific
indicators authored alongside the prior A05:2021 server-side indicators per
ADR-037 D-2 — is operational by surfacing a representative finding citing OWASP
API8:2023 as `relationship: primary` plus ≥1 `relationship: related` CWE entry
per BLP-01 §8 Quality Bar. The finding exercises the API-tier misconfiguration
architectural-tell (production GraphQL introspection enabled, retained
`/swagger-ui` exposure, permissive CORS allowlist with credentials) which
disambiguates the API8:2023 sub-variant from the A05:2021 server-side variant
(actuator endpoints, default credentials) and the Mobile M8:2024 variant
(debug-mode privilege gain on Android/iOS targets).

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| E-8 | privilege-escalation | API8 Security Misconfiguration (API-Specific Variant) | GraphQL Gateway (apollo-server) | Production GraphQL endpoint at `/graphql` has introspection enabled (`apollo-server` configured with `introspection: true` and no `NODE_ENV=production` gate); attacker enumerates the internal schema via `__type(name:"Mutation")` introspection probe and discovers undocumented `internalAccountTransfer` and `impersonateUser` mutations enabling unauthorized account-takeover; CORS allowlist contains wildcard `*` paired with `Access-Control-Allow-Credentials: true` enabling cross-site credential theft; auto-generated `/swagger-ui` retained on the production deployment without authentication, exposing additional REST surface tagged with `@Internal` annotations | High | Disable GraphQL introspection in production (`introspection: NODE_ENV !== 'production'`); enforce strict CORS allowlist per origin (no wildcard with credentials, no wildcard origin when `Allow-Credentials: true`); strip auto-generated API documentation (`/swagger-ui`, `/api-docs`, `/graphiql`, `/playground`) from production builds via build-time exclusion or environment-gated deployment; disable verbose error responses including stack traces and ORM diagnostic output |

## 9. Source Attribution

```yaml
E-8:
  - {taxonomy: owasp, id: "API8:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-1188", relationship: related}
  - {taxonomy: cwe, id: "CWE-942", relationship: related}
```

## Closure Evidence

- **Pattern Category Citation**: `tachi-privilege-escalation` Pattern Category 11 — Security Misconfiguration Privilege-Gain Variant — Mobile (OWASP M8:2024), Server-Side (OWASP A05:2021), and API-Specific (OWASP API8:2023), `Indicators (API-specific / OWASP API8:2023)` subsection extension at `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md:211+`
- **Primary Source Block**: OWASP API8:2023 link added to Pattern Category 11 Primary source list alongside the existing M8:2024 + A05:2021 entries; CWE-1188 + CWE-942 already present from prior A05:2021 closure
- **Indicator Extension**: API-specific indicators authored covering GraphQL introspection enabled in production, retained swagger-ui / graphiql / playground in production, permissive CORS allowlist with credentials (wildcard origin + `Allow-Credentials: true`), auto-generated API documentation exposure, missing `NODE_ENV=production` gates on dev tooling, and verbose error / stack-trace responses on the API tier
- **BLP-01 §8 Quality Bar**: ≥1 host agent (`tachi-privilege-escalation`) + ≥1 detection-pattern category (Pattern Category 11 API8:2023 sub-variant)
