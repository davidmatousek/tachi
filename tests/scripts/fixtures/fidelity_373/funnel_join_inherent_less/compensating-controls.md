---
schema_version: "1.0"
date: "2026-01-12"
source_file: "tests/scripts/fixtures/fidelity_373/funnel_join_inherent_less/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K11 inherent-less join path, F2)

This table has no "Inherent Score" / "Inherent" column. The sibling
`risk-scores.md` in this directory supplies the composite score for each
Threat ID, so `parse_compensating_controls_md(content, composites_by_id=...)`
must fill `inherent` by ID join: T-1 <- 8.0, T-2 <- 7.0.

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic threat T-1 | Control Found | 7.5 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|-----------------|----------------|--------------------|
| T-2 | — | Backend Service | Synthetic threat T-2 | Partial Control | 6.6 | Medium |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 50% |
| Medium | 1 | 50% |
| Low | 0 | 0% |
| **Total** | **2** | **100%** |
