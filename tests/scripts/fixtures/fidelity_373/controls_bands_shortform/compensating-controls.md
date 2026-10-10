---
schema_version: "1.0"
date: "2026-01-01"
source_file: "tests/scripts/fixtures/fidelity_373/controls_bands_shortform/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K9)

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### Critical Residual Severity

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent | Inherent Severity | Status | Residual | Residual Sev. |
|-----------|-----|-----------|--------|----------|--------------------|--------|----------|---------------|
| T-1 | — | API Gateway | Synthetic threat description A | 8.0 | High | No Control Found | 8.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent | Inherent Severity | Status | Residual | Residual Sev. |
|-----------|-----|-----------|--------|----------|--------------------|--------|----------|---------------|
| T-2 | — | Backend Service | Synthetic threat description B | 6.5 | Medium | Control Found | 4.5 | Medium |

### Low Residual Severity

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 50% |
| Medium | 1 | 50% |
| Low | 0 | 0% |
| **Total** | **2** | **100%** |
