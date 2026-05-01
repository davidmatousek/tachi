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

# Stream 2 Wave 1 Fixture — A06 Vulnerable and Outdated Components Closure on tachi-tampering Pattern Category 8

Validates that the F-241 Stream 2 closure of OWASP A06:2021 (Vulnerable and
Outdated Components) — added as a Primary Source block + indicator extension on
`tachi-tampering` Pattern Category 8 (Software Supply Chain Integrity Failures)
— is operational by surfacing a representative finding citing OWASP A06:2021 as
`relationship: primary` plus ≥1 `relationship: related` CWE entry per BLP-01 §8
Quality Bar.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| T-1 | tampering | A06 Vulnerable and Outdated Components | Production Python Runtime | Application runtime carries `urllib3==1.25.0` (released 2019) pinned in lockfile but never bumped despite CVE-2020-26137 (authentication header smuggling) and CVE-2021-33503 (ReDoS); repository lacks Dependabot configuration and SCA pipeline | High | Enable Dependabot or Renovate with weekly cadence; integrate `pip-audit` / Snyk / OWASP Dependency-Check into CI as a build-failing gate on Critical/High CVEs; emit CycloneDX SBOM per build; bump urllib3 to current LTS version |

## 9. Source Attribution

```yaml
T-1:
  - {taxonomy: owasp, id: "A06:2021", relationship: primary}
  - {taxonomy: cwe, id: "CWE-1104", relationship: related}
  - {taxonomy: cwe, id: "CWE-937", relationship: related}
```

## Closure Evidence

- **Pattern Category Citation**: `tachi-tampering` Pattern Category 8 — Software Supply Chain Integrity Failures (OWASP A08:2021 + A06:2021), `Indicators` section extended at `.claude/skills/tachi-tampering/references/detection-patterns.md`
- **Primary Source Block**: OWASP A06:2021 link + CWE-1104 + CWE-937 added to Pattern Category 8 Primary source list
- **Indicator Extension**: 3 A06-specific indicators authored covering SCA tooling absence, EOL/unmaintained dependencies in production, and long-lived dependency versions without automated upgrade cadence
- **BLP-01 §8 Quality Bar**: ≥1 host agent (`tachi-tampering`) + ≥1 detection-pattern category (Pattern Category 8)
