---
schema_version: "1.0"
date: "2026-01-09"
source_file: "tests/scripts/fixtures/fidelity_373/funnel_3tier/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Synthetic Fixture (F-373 K11 3-tier)

## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploit. | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|-----:|---------:|-------------:|-------------:|----------:|----------|-----|-------------|
| T-1 | API Gateway | Synthetic threat T-1 | 8.5 | 8.0 | 6.0 | 8.0 | 8.0 | High | 7d | Mitigate |
| T-2 | Backend Service | Synthetic threat T-2 | 6.5 | 6.0 | 5.0 | 5.0 | 6.0 | Medium | 30d | Review |
