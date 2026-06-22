use tachi_core::facade::{
    build_remediation_actions, RemediationFinding, RemediationTimelineEntry, ThreatReportData,
};

#[test]
fn build_remediation_actions_uses_compensating_controls_for_tier1() {
    let findings = vec![
        RemediationFinding {
            id: String::from("S-1"),
            threat: String::from("Auth bypass"),
            recommendation: String::from("Rotate keys"),
            control_status: String::from("Partial"),
            residual_severity: String::from("High"),
            severity: String::new(),
            risk_level: String::new(),
            mitigation: String::new(),
        },
        RemediationFinding {
            id: String::from("S-2"),
            threat: String::from("Data exfil"),
            recommendation: String::new(),
            control_status: String::new(),
            residual_severity: String::from("Unknown"),
            severity: String::new(),
            risk_level: String::new(),
            mitigation: String::new(),
        },
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
    let findings = vec![RemediationFinding {
        id: String::from("S-3"),
        threat: String::from("Admin misuse"),
        recommendation: String::from("Not used"),
        control_status: String::from("Not used"),
        residual_severity: String::new(),
        severity: String::new(),
        risk_level: String::from("Critical"),
        mitigation: String::from("Enforce MFA"),
    }];
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
