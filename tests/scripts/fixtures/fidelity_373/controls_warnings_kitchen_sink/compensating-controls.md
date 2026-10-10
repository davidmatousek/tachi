---
schema_version: "1.0"
date: "2026-01-13"
source_file: "tests/scripts/fixtures/fidelity_373/controls_warnings_kitchen_sink/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 warnings kitchen sink)

## 1. Executive Summary

**10** threats analyzed | **2** Control Found | **2** Partial Control | **6** No Control Found

**Coverage**: 20% Found | 20% Partial | 60% Missing

**Risk Reduction**: 60.0 inherent -> 52.7 residual (**26.9%** reduction)

> Synthetic fixture (F-373): the Risk Reduction line above is deliberately
> inconsistent with the row-derived totals (57.7 inherent -> 52.7 residual,
> 8.7% reduction; see the fixtures README) to exercise the Section 1
> comparand warning. The residual figure (52.7) is left matching the
> row-derived value on purpose, so only the inherent-total and the
> reduction-percentage fields warn — not every field.

## 2. Coverage Matrix

### Critical Residual Severity

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| W-6 | — | Audit Service | Synthetic threat W-6, unparseable residual (em dash) | 8.0 | High | Control Found | — | High |
| W-7 | — | Audit Service | Synthetic threat W-7, unparseable residual (trailing text) | 7.2 | High | No Control Found | 8.5 (High) | High |
| W-9 | — | Audit Service | Synthetic threat W-9, residual exceeds inherent | 8.0 | High | No Control Found | 9.5 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| W-1 | — | Audit Service | Synthetic threat W-1, status "Missing" | 6.0 | Medium | Missing | 6.0 | Medium |
| W-2 | — | Audit Service | Synthetic threat W-2, empty status | 5.5 | Medium |  | 5.5 | Medium |
| W-3 | — | Audit Service | Synthetic threat W-3, unrecognized status | 4.5 | Medium | Foobar | 4.5 | Medium |
| W-4 | — | Audit Service | Synthetic threat W-4, status "Partially Found" | 7.0 | High | Partially Found | 5.5 | Medium |
| W-5 | — | Audit Service | Synthetic threat W-5, status "None found" | 5.0 | Medium | None found | 5.0 | Medium |
| W-8 | — | Audit Service | Synthetic threat W-8, unparseable inherent (NaN) | NaN |  | Partial Control | 5.0 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| W-10 | — | Audit Service | Synthetic threat W-10, clean control (anchor row) | 6.5 | Medium | Control Found | 3.0 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 3 | 30% |
| Medium | 6 | 60% |
| Low | 1 | 10% |
| **Total** | **10** | **100%** |
