---
schema_version: "1.0"
date: "2026-01-11"
source_file: "tests/scripts/fixtures/fidelity_373/funnel_volumes_unavailable/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K11 volumes-unavailable)

This table has no "Inherent Score" / "Inherent" column at all, and no
`risk-scores.md` sits alongside it in this directory, so no join is possible.
No row in the one row set carries an inherent score: `V2` has no terms, and
funnel volumes / `risk_reduction` are unavailable (data-model §4.3, condition 1).

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic threat T-1 | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|-----------------|----------------|--------------------|
| T-2 | — | Backend Service | Synthetic threat T-2 | Partial Control | 4.0 | Medium |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 50% |
| Medium | 1 | 50% |
| Low | 0 | 0% |
| **Total** | **2** | **100%** |
