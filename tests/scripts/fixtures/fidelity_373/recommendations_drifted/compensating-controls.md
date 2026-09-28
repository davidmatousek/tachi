---
schema_version: "1.0"
date: "2026-01-06"
source_file: "tests/scripts/fixtures/fidelity_373/recommendations_drifted/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K13.1 drift)

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic DoS threat; controls Section 4 has content but does not cover this ID | 7.5 | High | No Control Found | 7.5 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-2 | — | Backend Service | Synthetic privilege threat; controls Section 4 has content but does not cover this ID, no Section 7 mitigation either | 6.0 | Medium | No Control Found | 6.0 | Medium |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 50% |
| Medium | 1 | 50% |
| Low | 0 | 0% |
| **Total** | **2** | **100%** |

---

## 4. Recommendations

### Medium Risk Gaps

#### 1. Z-9 — Unrelated Component (Composite: 6.0, Medium)

**Current Status**: No Control Found

**What to Implement**: This recommendation belongs to a finding ID that does not appear among the Section 2 rows above, so it must not join to T-1 or T-2 and must not suppress the Section 4 drift warning.

**Where to Implement**: `unrelated/module.py`

**Reference Patterns**: N/A.

**Effort Estimate**: Low.
