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

# Stream 2 Wave 2 Fixture — API10:2023 Unsafe Consumption of APIs Closure on tachi-tampering Pattern Category 9

Validates that the F-241 Stream 2 closure of OWASP API10:2023 (Unsafe
Consumption of APIs) — extended as the consumed-API-response trust variant of
`tachi-tampering` Pattern Category 9 (Injection Attacks Beyond SQL) per
ADR-037 D-1 dual-host placement (primary on tampering Cat 9; cross-reference
on `tachi-info-disclosure` Cat 7 SSRF) — is operational by surfacing a
representative finding citing OWASP API10:2023 as `relationship: primary` plus
≥1 `relationship: related` CWE entry per BLP-01 §8 Quality Bar. The finding
exercises the trust-provenance architectural-tell (consumer-to-upstream
outbound call coupled with use of the upstream response in injection-prone
sinks without re-validation at the trust boundary) which disambiguates the
API10:2023 consumed-response variant from generic Cat 9 injection by the
provenance of the payload (a "trusted" upstream API response) rather than by
the architectural-tell of the sink itself.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| T-11 | tampering | API10 Unsafe Consumption of APIs | Order Management Service (OrdersAPI) | OrderManagementService queries the partner-supplier API (`https://supplier-api.example.com/v1/shipping/rates`) for shipping rates and stores the returned `description` field in a quoted SQL `INSERT INTO order_summaries(...)` for customer order summaries; supplier-side compromise (or a malicious supplier whose authentication was never treated as a trust boundary) returns a `description` field with a SQL injection payload (`'); DROP TABLE customer_pii; --`); the order service trusts the upstream response, performs no schema validation or content escaping, and executes the attacker SQL in the order-service-database role context, exposing both data integrity (DROP TABLE) and confidentiality (SELECT credit_card) attack vectors; outbound HTTP redirects from the supplier endpoint are followed without re-applying the egress allowlist, opening a secondary SSRF surface to internal services | High | Maintain an egress allowlist with per-route response schema validation (OpenAPI 3.x spec + JSON Schema enforcement at the API client boundary); treat consumed API responses as untrusted by default and parameterize all SQL / template / shell / eval sinks that incorporate consumed-response data; disable redirect-following on outbound third-party API clients (or re-apply the egress allowlist on every redirect hop with DNS-resolved-IP denylist for RFC1918 + link-local ranges); declare third-party API integrations as explicit trust boundaries in the architecture-of-record and fail-closed on auth violations or contract-shape mismatches (no fail-open with null/empty defaults on 401/5xx upstream responses) |

## 9. Source Attribution

```yaml
T-11:
  - {taxonomy: owasp, id: "API10:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-20", relationship: related}
  - {taxonomy: cwe, id: "CWE-602", relationship: related}
```

## Closure Evidence

- **Pattern Category Citation**: `tachi-tampering` Pattern Category 9 (Injection Attacks Beyond SQL) extended with the **Indicators (consumed-API-response trust / OWASP API10:2023)** subsection at `.claude/skills/tachi-tampering/references/detection-patterns.md:138+`. Cross-reference at `tachi-info-disclosure` Pattern Category 7 (SSRF) under the **Cross-reference to OWASP API10:2023 (Unsafe Consumption of APIs)** subsection covers the redirect-target architectural-tell variant
- **Primary Source Block**: OWASP API10:2023 link added to Pattern Category 9 Primary source extension (1 dedicated subsection block) and as a cross-link bullet on info-disclosure Cat 7
- **Indicator Extension**: 5 API10:2023-specific indicators authored covering outbound HTTP → response in injection sink (textbook flow), redirect-following without egress re-application (SSRF intersection), no declared schema validation (controls-absence indicator), fail-open upstream auth (proceeds with null/empty on 401/5xx), and undeclared trust boundary (architecture-document indicator). Indicator 2 deliberately overlaps with the cross-reference subsection on info-disclosure Cat 7
- **BLP-01 §8 Quality Bar**: ≥1 host agent (`tachi-tampering` primary + `tachi-info-disclosure` cross-reference) + ≥1 detection-pattern category (Pattern Category 9 extended; Pattern Category 7 cross-referenced) + 5 indicators (≥3 required) + 1 dedicated Primary Source URL + 1 worked example (order-management → supplier-API → SQL injection) + 4 named mitigation bullets (≥2 required)
