use tachi_core::report_extraction::{
    build_remediation_actions, RemediationFinding, RemediationTimelineEntry, ThreatReportData,
};

fn finding(
    id: &str,
    threat: &str,
    recommendation: &str,
    control_status: &str,
    residual_severity: &str,
    severity: &str,
    risk_level: &str,
    mitigation: &str,
) -> RemediationFinding {
    RemediationFinding {
        id: id.to_string(),
        threat: threat.to_string(),
        recommendation: recommendation.to_string(),
        control_status: control_status.to_string(),
        residual_severity: residual_severity.to_string(),
        severity: severity.to_string(),
        risk_level: risk_level.to_string(),
        mitigation: mitigation.to_string(),
    }
}

#[test]
fn build_remediation_actions_uses_compensating_controls_for_tier1() {
    let findings = vec![
        finding(
            "S-1",
            "Auth bypass",
            "Rotate keys",
            "Partial",
            "High",
            "",
            "",
            "",
        ),
        finding("S-2", "Data exfil", "", "", "Unknown", "", "", ""),
    ];
    let report_data = ThreatReportData {
        executive_narrative: None,
        remediation_timeline: vec![RemediationTimelineEntry {
            timeline: "Short-term".to_string(),
            count: 1,
            severity: "High".to_string(),
        }],
    };

    let actions = build_remediation_actions(&findings, 1, true, Some(&report_data))
        .expect("tier1 should produce remediation actions");

    assert_eq!(actions.len(), 2);
    assert_eq!(actions[0].severity, "High");
    assert_eq!(actions[0].finding_id, "S-1");
    assert_eq!(actions[0].finding_name, "Auth bypass");
    assert_eq!(actions[0].recommendation, "Rotate keys");
    assert_eq!(actions[0].sla, "14d");
    assert_eq!(actions[0].status, "Partial");

    assert_eq!(actions[1].severity, "Unknown");
    assert_eq!(actions[1].sla, "90d");
    assert_eq!(actions[1].status, "pending");
}

#[test]
fn build_remediation_actions_uses_threat_report_for_tier3() {
    let findings = vec![finding(
        "S-3",
        "Admin misuse",
        "Not used",
        "Not used",
        "",
        "",
        "Critical",
        "Enforce MFA",
    )];
    let report_data = ThreatReportData {
        executive_narrative: None,
        remediation_timeline: vec![RemediationTimelineEntry {
            timeline: "Short-term".to_string(),
            count: 3,
            severity: "Critical".to_string(),
        }],
    };

    let actions = build_remediation_actions(&findings, 3, false, Some(&report_data))
        .expect("tier3 should produce remediation actions when timeline exists");

    assert_eq!(actions.len(), 1);
    assert_eq!(actions[0].severity, "Critical");
    assert_eq!(actions[0].finding_id, "S-3");
    assert_eq!(actions[0].finding_name, "Admin misuse");
    assert_eq!(actions[0].recommendation, "Enforce MFA");
    assert_eq!(actions[0].sla, "7d");
    assert_eq!(actions[0].status, "pending");
}
