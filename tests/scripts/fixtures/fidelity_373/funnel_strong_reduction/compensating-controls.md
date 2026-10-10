---
schema_version: "1.0"
date: "2026-01-08"
source_file: "tests/scripts/fixtures/fidelity_373/funnel_strong_reduction/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K11 strong-reduction, FLOOR-bound)

## 2. Coverage Matrix

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic threat T-1 | 5.0 | Medium | Control Found | 1.0 | Low |
| T-2 | — | Backend Service | Synthetic threat T-2 | 5.0 | Medium | Partial Control | 2.0 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 0 | 0% |
| Medium | 0 | 0% |
| Low | 2 | 100% |
| **Total** | **2** | **100%** |
