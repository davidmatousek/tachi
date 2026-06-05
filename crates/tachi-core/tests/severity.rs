use std::collections::BTreeMap;

use pretty_assertions::assert_eq;
use rstest::rstest;

use tachi_core::infographic::{compute_severity_percentages, largest_remainder};
use tachi_core::parsers::{
    compute_delta_counts, parse_resolved_findings, parse_risk_scores_findings,
    parse_risk_scores_severity, parse_threats_severity, SeverityCounts, ThreatFinding,
};

#[rstest]
#[case(
    vec![("Critical", 5), ("High", 14), ("Medium", 1)],
    100,
    vec![("Critical", 25), ("High", 70), ("Medium", 5)]
)]
#[case(
    vec![("A", 1), ("B", 1), ("C", 1)],
    100,
    vec![("A", 34), ("B", 33), ("C", 33)]
)]
#[case(
    vec![("A", 0), ("B", 0)],
    100,
    vec![("A", 0), ("B", 0)]
)]
fn largest_remainder_distributes_integer_percentages_deterministically(
    #[case] counts: Vec<(&str, usize)>,
    #[case] target: usize,
    #[case] expected: Vec<(&str, usize)>,
) {
    let counts = counts
        .into_iter()
        .map(|(label, count)| (label.to_string(), count))
        .collect::<BTreeMap<_, _>>();
    let expected = expected
        .into_iter()
        .map(|(label, percentage)| (label.to_string(), percentage))
        .collect::<BTreeMap<_, _>>();

    let actual = largest_remainder(&counts, target);

    assert_eq!(actual, expected);
}

#[test]
fn compute_severity_percentages_uses_canonical_order_and_colors() {
    let severity = SeverityCounts {
        critical: 1,
        high: 1,
        medium: 1,
        low: 1,
        note: 9,
        total: 13,
    };

    let percentages = compute_severity_percentages(&severity);

    assert_eq!(percentages.len(), 4);
    assert_eq!(percentages[0].label, "Critical");
    assert_eq!(percentages[1].label, "High");
    assert_eq!(percentages[2].label, "Medium");
    assert_eq!(percentages[3].label, "Low");
    assert_eq!(percentages[0].count, 1);
    assert_eq!(percentages[0].percentage, 25);
    assert_eq!(percentages[0].color, "#DC2626");
    assert_eq!(percentages[3].color, "#2563EB");
}

#[test]
fn parse_threats_and_risk_scores_severity_accumulate_counts() {
    let threats = r#"
## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 1 |
| High | 2 |
| Medium | 3 |
| Low | 4 |
| Note | 5 |
| Total | 15 |
"#;
    let risk_scores = r#"
Severity Distribution

| Severity | Count |
| --- | --- |
| Critical | 2 |
| High | 4 |
| Medium | 6 |
| Low | 8 |
| Note | 10 |
| Total | 30 |
"#;

    let threats_counts = parse_threats_severity(threats);
    let risk_counts = parse_risk_scores_severity(risk_scores);

    assert_eq!(threats_counts.critical, 1);
    assert_eq!(threats_counts.total, 15);
    assert_eq!(risk_counts.high, 4);
    assert_eq!(risk_counts.total, 30);
}

#[test]
fn parse_resolved_findings_and_delta_counts_work_together() {
    let resolved = r#"
## 4b. Resolved Findings

| ID | Component | Threat | Last Risk Level | Resolution Reason |
| --- | --- | --- | --- | --- |
| S-1 | API | Auth issue | High | fixed |
"#;

    let resolved_findings = parse_resolved_findings(resolved);
    assert_eq!(resolved_findings.len(), 1);
    assert_eq!(resolved_findings[0].delta_status, "RESOLVED");

    let findings = vec![
        finding("S-1", Some("NEW")),
        finding("S-2", Some("UNCHANGED")),
        finding("S-3", Some("UPDATED")),
        finding("S-4", None),
    ];
    let counts = compute_delta_counts(&findings, &resolved_findings);

    assert_eq!(counts.get("new"), Some(&1));
    assert_eq!(counts.get("unchanged"), Some(&1));
    assert_eq!(counts.get("updated"), Some(&1));
    assert_eq!(counts.get("resolved"), Some(&1));
}

#[test]
fn parse_risk_scores_findings_reads_the_scored_table() {
    let markdown = r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploit. | Scalability | Reachability | Composite | Severity | SLA | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S-1 | API | Auth issue | 9.1 | 8.0 | 7.0 | 6.0 | 8.5 | High | 14d | Open |
"#;

    let findings = parse_risk_scores_findings(markdown);

    assert_eq!(findings.len(), 1);
    assert_eq!(findings[0].id, "S-1");
    assert_eq!(findings[0].component, "API");
    assert_eq!(findings[0].severity, "High");
    assert_eq!(findings[0].composite_score, "8.5");
}

fn finding(id: &str, delta_status: Option<&str>) -> ThreatFinding {
    ThreatFinding {
        id: id.to_string(),
        delta_status: delta_status.map(|s| s.to_string()),
        ..ThreatFinding::default()
    }
}
