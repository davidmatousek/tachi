---
schema_version: "1.0"
date: "2026-04-25"
source_file: "tests/scripts/fixtures/fidelity_373/comparand_exact_tenth/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 L-4)

## 1. Executive Summary

**1** threats analyzed | **1** Control Found | **0** Partial Control | **0** No Control Found

**Coverage**: 100% Found | 0% Partial | 0% Missing

**Risk Reduction**: 27.0 inherent -> 10.11 residual (**62.8%** reduction)

> Synthetic fixture (F-373 L-4): the stated inherent total (27.0) is
> deliberately exactly 0.1 above the row-derived total (26.9) -- must NOT
> warn after the Decimal-tolerance fix. The stated residual (10.11) is
> deliberately 0.11 above the row-derived total (10.0) -- must warn. The
> stated reduction percentage (62.8%) matches the row-derived value
> exactly, so it stays silent and does not add a third warning line.

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| W-1 | — | API | Synthetic threat W-1 | 26.9 | High | Control Found | 10.0 | High |

## 4. Recommendations

No recommendations.
