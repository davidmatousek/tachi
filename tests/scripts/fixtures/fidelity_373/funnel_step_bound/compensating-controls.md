---
schema_version: "1.0"
date: "2026-01-07"
source_file: "tests/scripts/fixtures/fidelity_373/funnel_step_bound/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K11 STEP-bound)

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic threat T-1 | 8.0 | High | Control Found | 7.9 | High |
| T-2 | — | Backend Service | Synthetic threat T-2 | 8.0 | High | Partial Control | 7.8 | High |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 2 | 100% |
| Medium | 0 | 0% |
| Low | 0 | 0% |
| **Total** | **2** | **100%** |
