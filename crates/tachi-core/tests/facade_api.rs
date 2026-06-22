use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, collect_audit, parse_component_metadata,
    parse_risk_md_section2, parse_risk_md_section3, parse_risk_md_section4,
    parse_threats_findings, prefix_for, render, ThreatSarifFinding,
};

#[test]
fn facade_exports_stable_core_surface() {
    let threats = "# Threat Model: Facade Test\n";
    let findings = parse_threats_findings(threats).expect("parse threats");
    assert!(findings.is_empty());
    assert_eq!(prefix_for("AG-1"), "AG");

    let _ = collect_audit(std::path::Path::new("."));
    let _ = render(&tachi_core::coverage_audit::collect_audit(std::path::Path::new(".")), std::path::Path::new("."));
    let _ = build_report_data_typst(std::path::Path::new("."), std::path::Path::new("."));
    let _ = build_infographic_payload(std::path::Path::new("."), "maestro-stack");
    let _ = parse_component_metadata(threats);
    let _ = parse_risk_md_section2("");
    let _ = parse_risk_md_section3("");
    let _ = parse_risk_md_section4("");
    let _ = ThreatSarifFinding {
        id: String::from("AG-1"),
        prefix: String::from("AG"),
        status: String::from("[NEW]"),
        component: String::from("Component"),
        maestro: String::new(),
        agentic_pattern: String::new(),
        threat: String::new(),
        owasp_ref: String::new(),
        likelihood: String::new(),
        impact: String::new(),
        risk_level: String::new(),
        mitigation: String::new(),
    };
}
