# Compensating Controls Report

<!--
  Canonical output template for tachi compensating controls reports.

  Schema version : 1.0
  Schema file    : schemas/compensating-controls.yaml
  Finding schema : schemas/finding.yaml

  Producers      : agents/tachi/control-analyzer.md
  Consumers      : Security engineers, security managers, developers, GRC tools

  Every generated compensating controls output MUST conform to this structure.
  All sections are required. Sections must appear in the order listed.
-->

---

```yaml
---
schema_version: "1.0"
date: "YYYY-MM-DD"
source_file: "{path to input risk-scores.md or risk-scores.sarif}"
target_path: "{--target codebase path}"
classification: "security"
rescan_scope: "{full or incremental}"
carry_forward_count: "{number of carried-forward control results or null}"
---
```

**Frontmatter fields:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Compensating controls schema version. Always `"1.0"` for this release. |
| `date` | string | ISO 8601 date when the analysis was performed. Format: `YYYY-MM-DD`. |
| `source_file` | string | Path to the input risk score file that was analyzed. |
| `target_path` | string | Path to the target codebase scanned for controls (`--target` flag value). |
| `classification` | string | Data classification label. Always `"security"` for compensating controls reports. |
| `rescan_scope` | string | `full` (first run or all findings changed) or `incremental` (only NEW/UPDATED findings re-scanned, UNCHANGED carried forward). |
| `carry_forward_count` | integer, nullable | Number of findings with carried-forward control results from baseline. Null when no baseline. |

---

## 1. Executive Summary

**{total_threats}** threats analyzed | **{coverage_found_count}** Control Found | **{coverage_partial_count}** Partial Control | **{coverage_missing_count}** No Control Found

**Coverage**: {coverage_found_pct}% Found | {coverage_partial_pct}% Partial | {coverage_missing_pct}% Missing

**Risk Reduction**: {total_inherent_risk} inherent -> {total_residual_risk} residual (**{risk_reduction_pct}%** reduction)

**Highest-Risk Unmitigated Finding**: {highest_risk_unmitigated_id} — {highest_risk_unmitigated_component} — Composite {highest_risk_unmitigated_score} ({highest_risk_unmitigated_severity})

| Metric | Value |
|--------|-------|
| Analysis date | {date} |
| Source file | `{source_file}` |
| Target codebase | `{target_path}` |
| Schema version | {schema_version} |

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | {coverage_found_count} | {coverage_found_pct}% |
| Partial Control | {coverage_partial_count} | {coverage_partial_pct}% |
| No Control Found | {coverage_missing_count} | {coverage_missing_pct}% |
| **Total** | **{total_threats}** | **100%** |

> {analysis_warnings}

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### Critical Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| {id} | {cf} | {component} | {threat} | {inherent_score} | {inherent_severity} | {control_status} | {residual_score} | Critical |

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| {id} | {cf} | {component} | {threat} | {inherent_score} | {inherent_severity} | {control_status} | {residual_score} | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| {id} | {cf} | {component} | {threat} | {inherent_score} | {inherent_severity} | {control_status} | {residual_score} | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| {id} | {cf} | {component} | {threat} | {inherent_score} | {inherent_severity} | {control_status} | {residual_score} | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | {residual_critical_count} | {residual_critical_pct}% |
| High | {residual_high_count} | {residual_high_pct}% |
| Medium | {residual_medium_count} | {residual_medium_pct}% |
| Low | {residual_low_count} | {residual_low_pct}% |
| **Total** | **{total_threats}** | **100%** |

---

## 3. Control Details

Per-control evidence showing detected security controls with their location, code evidence, and threat coverage. One subsection per detected control, grouped by control category.

### {control_category}

#### {control_id} — {control_summary}

**Category**: {control_category} | **Status**: {control_status} | **Effectiveness**: {control_effectiveness}

**Detected in**: `{evidence_file}:{evidence_line}`

```{evidence_language}
{evidence_snippet}
```

> Code snippet limited to 5 lines centered on the control implementation.

**Effectiveness Assessment**:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Coverage | {eff_coverage_rating} | {eff_coverage_rationale} |
| Configuration | {eff_configuration_rating} | {eff_configuration_rationale} |
| Currency | {eff_currency_rating} | {eff_currency_rationale} |
| Completeness | {eff_completeness_rating} | {eff_completeness_rationale} |

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| {threat_id} | {threat_component} | {threat_description} | {inherent_score} | {reduction_factor} | {residual_score} |

---

*Repeat the above block for each detected control, grouped by control category in this order: Authentication, Access Control, Input Validation, Encryption, Rate Limiting, Logging/Audit, CSRF Protection, CSP/Security Headers.*

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control," sorted by composite risk score descending (highest risk gaps first).

### Critical / High Risk Gaps

#### {rec_id}. {rec_threat_id} — {rec_component} (Composite: {rec_inherent_score}, {rec_inherent_severity})

**Current Status**: {rec_control_status}

**What to Implement**: {rec_what}

**Where to Implement**: `{rec_where_path}` — {rec_where_rationale}

**Reference Patterns**: {rec_reference_patterns}

**Effort Estimate**: {rec_effort_estimate} — {rec_effort_rationale}

---

### Medium Risk Gaps

#### {rec_id}. {rec_threat_id} — {rec_component} (Composite: {rec_inherent_score}, {rec_inherent_severity})

**Current Status**: {rec_control_status}

**What to Implement**: {rec_what}

**Where to Implement**: `{rec_where_path}` — {rec_where_rationale}

**Reference Patterns**: {rec_reference_patterns}

**Effort Estimate**: {rec_effort_estimate} — {rec_effort_rationale}

---

### Low Risk Gaps

#### {rec_id}. {rec_threat_id} — {rec_component} (Composite: {rec_inherent_score}, {rec_inherent_severity})

**Current Status**: {rec_control_status}

**What to Implement**: {rec_what}

**Where to Implement**: `{rec_where_path}` — {rec_where_rationale}

**Reference Patterns**: {rec_reference_patterns}

**Effort Estimate**: {rec_effort_estimate} — {rec_effort_rationale}

---

*Repeat the recommendation block for each gap within each severity group. "Partial Control" recommendations focus on hardening (what's missing, how to extend) rather than replacement.*

### Recommendation Field Definitions

| Field | Description |
|-------|-------------|
| **What to Implement** | Specific control to add or harden. For "No Control Found": full implementation guidance. For "Partial Control": targeted hardening of the existing control. |
| **Where to Implement** | Suggested file path or module in the target codebase. Based on architecture mapping or codebase heuristics. |
| **Reference Patterns** | Industry-standard patterns, libraries, or framework features to use as implementation reference. |
| **Effort Estimate** | **Low**: Configuration change or flag toggle. **Medium**: New middleware, function, or module. **High**: Architectural change affecting multiple components. |

---

## 5. Residual Risk Summary

Comparison of inherent risk (before controls) to residual risk (after controls), showing the risk reduction achieved by existing controls.

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | {total_inherent_risk} |
| Total Residual Risk Score | {total_residual_risk} |
| Delta | {risk_delta} |
| Overall Reduction | {risk_reduction_pct}% |

### Per-Severity-Band Shift

Breakdown of how threats shifted between severity bands after residual risk calculation. "Shifted" means a threat moved from a higher inherent severity band to a lower residual severity band due to detected controls.

| Shift | Count | Examples |
|-------|-------|---------|
| Critical -> High | {shift_critical_to_high_count} | {shift_critical_to_high_examples} |
| Critical -> Medium | {shift_critical_to_medium_count} | {shift_critical_to_medium_examples} |
| Critical -> Low | {shift_critical_to_low_count} | {shift_critical_to_low_examples} |
| High -> Medium | {shift_high_to_medium_count} | {shift_high_to_medium_examples} |
| High -> Low | {shift_high_to_low_count} | {shift_high_to_low_examples} |
| Medium -> Low | {shift_medium_to_low_count} | {shift_medium_to_low_examples} |
| No Shift | {shift_none_count} | {shift_none_examples} |
| **Total** | **{total_threats}** | |

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | {inherent_critical_count} | {residual_critical_count} | {critical_change} |
| High | {inherent_high_count} | {residual_high_count} | {high_change} |
| Medium | {inherent_medium_count} | {residual_medium_count} | {medium_change} |
| Low | {inherent_low_count} | {residual_low_count} | {low_change} |
| **Total** | **{total_threats}** | **{total_threats}** | |

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent * 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent * 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent * 1.00 | No matching control detected. Residual equals inherent. |

> P1 enhancement: When control effectiveness assessment (User Story 6) is active, reduction factors upgrade from the 3-level binary model above to a 7-level effectiveness-aware model. See spec FR-011 and User Story 6 for the extended factor table.

---

## 6. Methodology

This section documents the compensating controls analysis methodology used to produce this report.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware, RBAC/ABAC patterns | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing algorithms, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

Each scored threat receives exactly one classification based on detected controls:

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

Residual risk per threat is calculated as:

```
Residual Score = Inherent Score * (1 - Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0] and mapped to severity bands using the same thresholds as risk scoring:

| Severity | Residual Score Range |
|----------|---------------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 -- 8.9 |
| **Medium** | 4.0 -- 6.9 |
| **Low** | < 4.0 |

### 6.4 Data Sources

Analysis draws on the following inputs:

- **Scored threats**: Parsed from `risk-scores.md` (canonical) or `risk-scores.sarif` (fallback). All original threat metadata (ID, component, category, description, composite score, severity band) is preserved.
- **Target codebase**: Scanned via `--target` path. When `architecture.md` is available, component-to-directory mapping enables targeted file discovery. When absent, heuristic directories (`middleware/`, `auth/`, `security/`, `validators/`, `guards/`, `interceptors/`, `filters/`, `policies/`, `config/`) are prioritized.
- **STRIDE-to-control mapping**: Canonical mapping from threat categories to control categories drives which controls are searched for each threat.

### 6.5 Limitations

- Static analysis only — runtime control behavior is not evaluated
- 200-file read budget — large codebases may have directories skipped with warnings
- Files > 5,000 tokens are truncated to security-relevant sections
- Binary reduction factors (P0) approximate control impact; effectiveness-aware factors available in P1
- AI-specific control patterns (agentic, LLM) limited to general categories in P0; specialized patterns in P1
