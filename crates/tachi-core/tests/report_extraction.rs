use tachi_core::report_extraction::parse_threat_report_md;

const THREAT_REPORT_PROSE_ONLY: &str = "# Threat Report\n\n## 1. Executive Summary\n\nThe system under review is a SaaS application with 42 active findings.\n\n**Risk profile by count**: 5 Critical, 12 High, 20 Medium, 5 Low.\n\n**Most critical unresolved exposure**: The auth service allows unauthenticated\nadmin access via a legacy flag that was never removed.\n\n## 2. Architecture Overview\n\nComponents and trust boundaries follow below.\n";

const THREAT_REPORT_WITH_TIMELINE: &str = "# Threat Report\n\n## 1. Executive Summary\n\n### Risk Posture\nHigh residual exposure remains in the authentication and reporting paths.\n\n### Remediation Timeline\n- **Short-term** (3 Critical findings)\n- **Mid-term** (12 High findings)\n\n## 2. Architecture Overview\n\nComponents and trust boundaries follow below.\n";

#[test]
fn parse_threat_report_falls_back_to_full_section1_prose() {
    let result = parse_threat_report_md(THREAT_REPORT_PROSE_ONLY);

    let narrative = result
        .executive_narrative
        .as_deref()
        .expect("narrative should be populated");

    assert!(narrative.contains("42 active findings"));
    assert!(narrative.contains("Risk profile by count"));
    assert!(!narrative.contains("## 2."));
}

#[test]
fn parse_threat_report_extracts_remediation_timeline_entries() {
    let result = parse_threat_report_md(THREAT_REPORT_WITH_TIMELINE);

    let narrative = result
        .executive_narrative
        .as_deref()
        .expect("narrative should be populated");

    assert!(narrative.contains("High residual exposure remains"));
    assert!(!narrative.contains("Architecture Overview"));

    assert_eq!(result.remediation_timeline.len(), 2);
    assert_eq!(result.remediation_timeline[0].timeline, "Short-term");
    assert_eq!(result.remediation_timeline[0].count, 3);
    assert_eq!(result.remediation_timeline[0].severity, "Critical");
    assert_eq!(result.remediation_timeline[1].timeline, "Mid-term");
    assert_eq!(result.remediation_timeline[1].count, 12);
    assert_eq!(result.remediation_timeline[1].severity, "High");
}
