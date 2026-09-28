---
schema_version: "1.0"
date: "2026-01-13"
source_file: "tests/scripts/fixtures/fidelity_373/controls_warnings_kitchen_sink/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Synthetic Fixture (F-373 warnings kitchen sink; row-count mismatch)

Eleven rows here against ten in the sibling `compensating-controls.md`
(W-8 has no composite here, so its inherent-join lookup misses by design;
W-11 and W-12 are scored but not yet analyzed for controls) — an
11-vs-10 row-count mismatch.

## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploit. | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|-----:|---------:|-------------:|-------------:|----------:|----------|-----|-------------|
| W-1 | Audit Service | Synthetic threat W-1 | 6.5 | 6.0 | 5.5 | 5.5 | 6.0 | Medium | 30d | Review |
| W-2 | Audit Service | Synthetic threat W-2 | 6.0 | 5.5 | 5.0 | 5.0 | 5.5 | Medium | 30d | Review |
| W-3 | Audit Service | Synthetic threat W-3 | 5.0 | 4.5 | 4.0 | 4.0 | 4.5 | Medium | 30d | Review |
| W-4 | Audit Service | Synthetic threat W-4 | 7.5 | 7.0 | 6.5 | 6.0 | 7.0 | High | 7d | Mitigate |
| W-5 | Audit Service | Synthetic threat W-5 | 5.5 | 5.0 | 4.5 | 4.5 | 5.0 | Medium | 30d | Review |
| W-6 | Audit Service | Synthetic threat W-6 | 8.5 | 8.0 | 7.0 | 7.0 | 8.0 | High | 7d | Mitigate |
| W-7 | Audit Service | Synthetic threat W-7 | 7.7 | 7.2 | 6.5 | 6.5 | 7.2 | High | 7d | Mitigate |
| W-9 | Audit Service | Synthetic threat W-9 | 8.5 | 8.0 | 7.0 | 7.0 | 8.0 | High | 7d | Mitigate |
| W-10 | Audit Service | Synthetic threat W-10 | 7.0 | 6.5 | 6.0 | 6.0 | 6.5 | Medium | 30d | Review |
| W-11 | Audit Service | Synthetic threat W-11, scored but not yet analyzed for controls | 5.5 | 5.0 | 4.5 | 4.5 | 5.0 | Medium | 30d | Review |
| W-12 | Audit Service | Synthetic threat W-12, scored but not yet analyzed for controls | 4.5 | 4.0 | 3.5 | 3.5 | 4.0 | Medium | 30d | Review |
