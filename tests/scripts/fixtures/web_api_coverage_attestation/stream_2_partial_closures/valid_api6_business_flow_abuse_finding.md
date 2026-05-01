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

# Stream 2 Wave 2 Fixture — API6:2023 Unrestricted Access to Sensitive Business Flows Closure on tachi-tool-abuse Pattern Category 11

Validates that the F-241 Stream 2 closure of OWASP API6:2023 (Unrestricted
Access to Sensitive Business Flows) — added as a new Pattern Category 11
(Business Flow Abuse via Automated Tool Composition) on
`tachi-tool-abuse` per ADR-037 D-1 host placement — is operational by surfacing
a representative finding citing OWASP API6:2023 as `relationship: primary` plus
≥1 `relationship: related` CWE entry per BLP-01 §8 Quality Bar. The finding
exercises the multi-step tool-composition architectural-tell (search → reserve
→ purchase chain at sustained concurrency without per-actor flow-completion
throttling, behavioral biometrics, or step-up authentication) which
disambiguates Cat 11 from per-call rate-limiting (API4:2023 / `denial-of-service`
Cat 9 raw resource flooding) and from per-request intent hijack (Cat 7).

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| AG-9 | tool-abuse | API6 Unrestricted Access to Sensitive Business Flows | LLM Concierge Agent (ConciergeMCP ticket-booking platform) | LLM-agent-backed ticket-booking concierge invokes the searchInventory + reserveSeat + purchase MCP tool chain at 100 concurrent sessions to corner inventory ahead of public on-sale; per-call rate limits pass (each individual tool call is below the per-IP and per-token rate threshold) but the aggregate flow-completion rate goes uncapped, with no per-actor flow-completion throttle, no CAPTCHA on flow entry, and no behavioral biometrics on the reservation step | High | Enforce per-actor flow-completion rate limits (not just per-call) with separate budgets for searchInventory, reserveSeat, and purchase; require CAPTCHA / device-attestation on reserveSeat entry; deploy behavioral biometrics (mouse-movement, timing distribution, session-duration anomaly) on the purchase step; implement agentic-budget enforcement at the API gateway with per-tenant flow-completion ceilings and step-up authentication on reservation count above a baseline threshold |

## 9. Source Attribution

```yaml
AG-9:
  - {taxonomy: owasp, id: "API6:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-799", relationship: related}
  - {taxonomy: cwe, id: "CWE-841", relationship: related}
```

## Closure Evidence

- **Pattern Category Citation**: `tachi-tool-abuse` Pattern Category 11 — Business Flow Abuse via Automated Tool Composition (OWASP API6:2023) at `.claude/skills/tachi-tool-abuse/references/detection-patterns.md:216`
- **Primary Source Block**: OWASP API6:2023 link added to Pattern Category 11 Primary source list and to file-end Primary Sources block (extended from 11 to 14 entries)
- **Indicator Extension**: 7 indicators authored covering atomic capability suppression on aggregate flows, per-call-throttle-only architectures, missing CAPTCHA / step-up on flow entry, absent behavioral biometrics, missing per-actor velocity caps, missing audit-binding on multi-step flows, and absent agentic-budget enforcement
- **BLP-01 §8 Quality Bar**: ≥1 host agent (`tachi-tool-abuse`) + ≥1 detection-pattern category (Pattern Category 11) + 1 narrative paragraph + 7 indicators (≥4) + 4 Primary source URLs (≥3) + 1 worked example with 2 variants (ticketing + comment-spam) + 6 named mitigation bullets (≥3)
