---
schema_version: "1.0"
date: "2026-01-14"
source_file: "tests/scripts/fixtures/fidelity_373/posture_mmdc_free/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 posture, mmdc-free)

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic threat T-1 | 8.5 | High | Partial Control | 8.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-2 | — | Backend Service | Synthetic threat T-2 | 6.0 | Medium | Control Found | 5.0 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-3 | — | Batch Worker | Synthetic threat T-3 | 2.5 | Low | No Control Found | 2.5 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 33% |
| Medium | 1 | 33% |
| Low | 1 | 33% |
| **Total** | **3** | **100%** |
