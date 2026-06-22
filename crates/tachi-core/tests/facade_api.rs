use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, collect_audit, crate_name,
    detect_artifacts, detect_brand_assets, detect_images, ensure_attack_path_renderer_available,
    format_attack_path_render_failure_summary, generate_chain_mermaid, parse_attack_chains,
    parse_compensating_controls_md, parse_component_metadata, parse_risk_md_section2,
    parse_risk_md_section3, parse_risk_md_section4, parse_threats_findings, prefix_for, render,
    AttackChain, AttackChainFinding, MermaidRenderFailure, ThreatSarifFinding, MMDC_INSTALL_HINT,
};

#[test]
fn facade_exports_stable_core_surface() {
    let threats = "# Threat Model: Facade Test\n";
    let findings = parse_threats_findings(threats).expect("parse threats");
    assert!(findings.is_empty());
    assert_eq!(prefix_for("AG-1"), "AG");
    assert_eq!(crate_name(), "tachi-core");

    let _ = collect_audit(std::path::Path::new("."));
    let _ = render(&tachi_core::coverage_audit::collect_audit(std::path::Path::new(".")), std::path::Path::new("."));
    let _ = detect_artifacts(std::path::Path::new("."));
    let _ = detect_brand_assets(std::path::Path::new("."), None);
    let _ = detect_images(std::path::Path::new("."), std::path::Path::new("."));
    let _ = ensure_attack_path_renderer_available(0, false);
    let _ = format_attack_path_render_failure_summary(&[]);
    let _ = generate_chain_mermaid(&AttackChain::default());
    let _ = parse_attack_chains(None);
    let _ = build_report_data_typst(std::path::Path::new("."), std::path::Path::new("."));
    let _ = build_infographic_payload(std::path::Path::new("."), "maestro-stack");
    let _ = parse_component_metadata(threats);
    let _ = parse_compensating_controls_md("---\nschema_version: \"1.0\"\n---\n");
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
    let _ = AttackChain::default();
    let _ = AttackChainFinding::default();
    let _ = MermaidRenderFailure {
        id: String::new(),
        file_path: String::new(),
        failure_class: String::new(),
        stderr_excerpt: String::new(),
    };
    let _ = MMDC_INSTALL_HINT;
}
