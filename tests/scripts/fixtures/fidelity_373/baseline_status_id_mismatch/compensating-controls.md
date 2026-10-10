---
schema_version: "1.0"
date: "2026-01-03"
source_file: "tests/scripts/fixtures/fidelity_373/baseline_status_id_mismatch/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "incremental"
carry_forward_count: 2
---

# Compensating Controls Report — Synthetic Fixture (F-373 F1/NM-1)

Tier-1 finding-ID set (A-1, A-2, A-4) does not match the sibling `threats.md`
Section 7 Status map (A-1, A-2, A-3) in this same directory: A-4 is only in
this tier, A-3 is only in the map.

## 2. Coverage Matrix

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| A-2 | — | Backend Service | Synthetic tampering threat A-2 | 5.0 | Medium | No Control Found | 5.0 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| A-1 | — | API Gateway | Synthetic spoofing threat A-1 | 6.0 | Medium | Control Found | 3.0 | Low |
| A-4 | — | API Gateway | Synthetic threat A-4, absent from Section 7 | 4.5 | Medium | Partial Control | 3.5 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 0 | 0% |
| Medium | 1 | 33% |
| Low | 2 | 67% |
| **Total** | **3** | **100%** |
