---
schema_version: "1.0"
date: "2026-01-05"
source_file: "tests/scripts/fixtures/fidelity_373/recommendations_partial_join/risk-scores.md"
target_path: "synthetic-fixture (architecture-only)"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# Compensating Controls Report — Synthetic Fixture (F-373 K13.1 partial join)

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-1 | — | API Gateway | Synthetic DoS threat, covered by controls Section 4 | 7.5 | High | No Control Found | 7.5 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|--------------------|-----------------|----------------|--------------------|
| T-2 | — | Backend Service | Synthetic privilege threat, not covered by controls Section 4 | 6.0 | Medium | Partial Control | 4.5 | Medium |
| T-3 | — | Batch Worker | Synthetic disclosure threat with no mitigation text on either side | 5.0 | Medium | No Control Found | 5.0 | Medium |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 33% |
| Medium | 2 | 67% |
| Low | 0 | 0% |
| **Total** | **3** | **100%** |

---

## 4. Recommendations

### High Risk Gaps

#### 1. T-1 — API Gateway (Composite: 7.5, High)

**Current Status**: No Control Found

**What to Implement**: Implement per-tenant rate limiting and a Web Application Firewall rule set at the API Gateway ingress to absorb volumetric requests before they reach backend services.

**Where to Implement**: `api-gateway/middleware/rate-limiter.{ts|py}`

**Reference Patterns**: `express-rate-limit`, WAF managed rule sets.

**Effort Estimate**: Medium — configuration addition to the existing gateway middleware chain.
