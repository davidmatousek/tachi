use tachi_core::facade::parse_compensating_controls_md;

const CC_MD_WITH_CROSS_LISTED: &str = r#"---
schema_version: "1.0"
---

## 1. Executive Summary

**Risk Reduction**: 100.0 inherent -> 60.0 residual (**40.0%** reduction)
**Coverage**: 30% Found | 30% Partial | 40% Missing

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|
| S-1 | API | Auth bypass | 8.0 | High | Partial |
| S-2 | DB | Data exfil | 5.5 | High | Missing |

### Medium Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|
| S-2 | DB | Data exfil | 5.5 | Medium | Missing |
| S-3 | Net | Flood | 4.5 | Medium | Found |

### Low Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|

### Critical Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|

## 3. Control Details
## 4. Recommendations
"#;

#[test]
fn parse_compensating_controls_dedupes_cross_listed_findings() {
    let data = parse_compensating_controls_md(CC_MD_WITH_CROSS_LISTED);

    let ids = data
        .findings
        .iter()
        .map(|finding| finding.id.as_str())
        .collect::<Vec<_>>();

    assert_eq!(data.findings.len(), 3);
    assert_eq!(ids.iter().filter(|id| **id == "S-2").count(), 1);
    assert_eq!(data.severity.total, 3);
    assert_eq!(
        data.severity.critical + data.severity.high + data.severity.medium + data.severity.low,
        data.severity.total
    );
}
