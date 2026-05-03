---
schema_version: "1.5"
date: "2026-04-21"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-21T09-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
has-source-attribution: false
---

# Source Attribution Absent Fixture — F-A2 T012

Three findings in the Section 7 table, NONE carrying attribution data. NO Section 9
block is rendered. Exercises the V6 absent-key round-trip (US-189-2 AC-1): the
parser MUST omit the ``source_attribution`` key from every returned finding dict.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| S-1 | spoofing | — | API Gateway | Attacker forges JWT to impersonate legitimate users | High | JWT RS256 validation with short-lived tokens |
| T-2 | tampering | — | Order Service | Attacker modifies cart totals via API replay | Medium | Request signing with HMAC |
| I-3 | info-disclosure | — | Logs Collector | Sensitive PII logged in plaintext traces | Medium | Redact PII fields before log emission |
