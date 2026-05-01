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

# Stream 2 Wave 2 Fixture — API9:2023 Improper Inventory Management Closure on tachi-info-disclosure Pattern Category 10

Validates that the F-241 Stream 2 closure of OWASP API9:2023 (Improper Inventory
Management) — added as a new Pattern Category 10 (API Surface Inventory and
Documentation Exposure) on `tachi-info-disclosure` per ADR-037 D-2 host
placement (Q-Plan-2 RESOLVED to info-disclosure) — is operational by surfacing a
representative finding citing OWASP API9:2023 as `relationship: primary` plus
≥1 `relationship: related` CWE entry per BLP-01 §8 Quality Bar. The finding
exercises the architectural-tell (retained swagger-ui / OpenAPI documentation
on production combined with deprecated-version co-residence and missing
inventory governance) which disambiguates Cat 10 from Cat 7 SSRF (runtime
metadata exfiltration) and Cat 8 (server-side debug-output) per the Pattern
Category Disambiguation update authored at the same closure.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| I-10 | info-disclosure | API9 Improper Inventory Management | Production API Gateway (FinTransfer fintech platform) | Production fintech API exposes unauthenticated `/swagger-ui` revealing the deprecated `/api/v1/transfer` endpoint alongside the current `/api/v3/transfer`; the v1 endpoint enforces neither device-attestation nor step-up authentication (controls introduced in v2 and tightened in v3) but remains routable on the production hostname because no inventory artifact tracked the deprecation; attacker discovers v1 from swagger, observes its weaker rate-limit threshold via `Retry-After` headers, and uses v1 for transfer-fraud automation while v3 enforces the modern controls; staging-tier `api-staging.fintransfer.example.com` is publicly resolvable and exposes a `/api/v4-beta` endpoint with reused production OAuth issuer keys, enabling cross-tier credential reuse | High | Maintain a versioned API inventory artifact (OpenAPI 3.x specification + declared deprecation cycle with `Sunset:` and `Deprecation:` HTTP headers); enforce environment-tier hostname separation (no production OAuth issuer keys reused across staging / dev / beta tiers); gate swagger-ui / graphiql / OpenAPI exposure behind authentication on production (or strip from production builds entirely); declare and enforce deprecation cycles with automated route-removal at sunset date; integrate automated route-discovery tooling (kiterunner, feroxbuster, gobuster, OWASP ZAP, Burp Suite Enterprise) into CI to detect undeclared / orphaned routes; document third-party API integrations and environment-tier boundaries in the architecture-of-record |

## 9. Source Attribution

```yaml
I-10:
  - {taxonomy: owasp, id: "API9:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-1059", relationship: related}
  - {taxonomy: cwe, id: "CWE-200", relationship: related}
```

## Closure Evidence

- **Pattern Category Citation**: `tachi-info-disclosure` Pattern Category 10 — API Surface Inventory and Documentation Exposure (OWASP API9:2023) at `.claude/skills/tachi-info-disclosure/references/detection-patterns.md:166`
- **Primary Source Block**: OWASP API9:2023 link added to Pattern Category 10 Primary source list (6 URLs total: API9:2023 + API Security project home + CWE-1059 + CWE-1295 + CWE-200 + NIST SP 800-204) and to file-end Primary Sources block (5 URLs added)
- **Indicator Extension**: 9 indicators authored covering swagger-ui retention on production, GraphQL `__schema` introspection probe, multi-version co-residence with deprecation gap, public dev/staging DNS, no inventory artifact, header-leak banners (`Server:` / `X-Powered-By:` / `X-API-Version:` / `X-Environment:`), beta gating gap, k8s-annotation leaks, and OAuth-issuer cross-tier reuse
- **BLP-01 §8 Quality Bar**: ≥1 host agent (`tachi-info-disclosure`) + ≥1 detection-pattern category (Pattern Category 10) + 1 narrative paragraph (6 sentences) + 9 indicators (≥4) + 6 Primary source URLs (≥3) + 1 worked example (two-stage fintech scenario) + 8 named mitigation bullets (≥3)
