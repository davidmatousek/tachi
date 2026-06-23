use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, collect_audit, crate_name,
    detect_artifacts, detect_brand_assets, detect_images, ensure_attack_path_renderer_available,
    format_attack_path_render_failure_summary, generate_chain_mermaid, maestro_layer_catalog,
    merge_delta_status, merge_source_attribution, normalize_maestro_layer_label,
    owasp_coverage_family_catalog, parse_attack_chains, parse_compensating_controls_md,
    parse_component_metadata, parse_risk_md_section2, parse_risk_md_section3,
    parse_risk_md_section4, parse_threat_report_md, parse_threats_findings, prefix_for, render,
    render_owasp_coverage_matrix, AttackChain, AttackChainFinding, MaestroLayer,
    MermaidRenderFailure, OwaspCoverageFamily, RemediationAction, RemediationFinding,
    RemediationTimelineEntry, ThreatReportData, ThreatSarifFinding, MMDC_INSTALL_HINT,
};
use tachi_core::parsers::ThreatFinding;

#[test]
fn facade_exports_stable_core_surface() {
    let threats = "# Threat Model: Facade Test\n";
    let findings = parse_threats_findings(threats).expect("parse threats");
    assert!(findings.is_empty());
    assert_eq!(prefix_for("AG-1"), "AG");
    assert_eq!(crate_name(), "tachi-core");

    let _ = collect_audit(std::path::Path::new("."));
    let _ = render(
        &tachi_core::collect_audit(std::path::Path::new(".")),
        std::path::Path::new("."),
    );
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
    let catalog = maestro_layer_catalog();
    assert_eq!(catalog.len(), 7);
    assert_eq!(catalog[0].layer_id, "L1");
    assert_eq!(
        normalize_maestro_layer_label("foundation models"),
        "L1 — Foundation Model"
    );
    assert_eq!(
        normalize_maestro_layer_label("unclassified"),
        "Unclassified"
    );
    let owasp_catalog = owasp_coverage_family_catalog();
    assert_eq!(owasp_catalog.len(), 6);
    assert_eq!(owasp_catalog[3].framework, "Mobile 2024");
    let matrix = render_owasp_coverage_matrix();
    assert!(matrix.contains("| Mobile 2024 | OWASP-MOBILE-2024 | M1-M10 | 10/10 |"));
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
    let _ = MaestroLayer {
        layer_id: "L1",
        layer_name: "Foundation Model",
        description: "",
        aliases: &[],
    };
    let _ = OwaspCoverageFamily {
        framework: "",
        bucket: "",
        items: "",
        status: "",
        anchor: "",
        detection_adrs: &[],
    };
    let _ = MermaidRenderFailure {
        id: String::new(),
        file_path: String::new(),
        failure_class: String::new(),
        stderr_excerpt: String::new(),
    };
    let report = parse_threat_report_md(
        "# Threat Report\n\n## 1. Executive Summary\n\n### Risk Posture\nStable posture.\n\n### Remediation Timeline\n- **Immediate** (1 Critical finding)\n- **Short-term** (2 High findings)\n\n## 2. Architecture Overview\n",
    );
    assert_eq!(
        report.executive_narrative.as_deref(),
        Some("Stable posture.")
    );
    assert_eq!(report.remediation_timeline.len(), 2);
    assert_eq!(report.remediation_timeline[0].timeline, "Immediate");
    assert_eq!(report.remediation_timeline[0].count, 1);
    assert_eq!(report.remediation_timeline[0].severity, "Critical");
    let mut findings = vec![ThreatFinding {
        id: String::from("S-1"),
        component: String::from("Component"),
        threat: String::from("Threat"),
        likelihood: String::from("—"),
        impact: String::from("—"),
        risk_level: String::from("High"),
        mitigation: String::from("Mitigation"),
        agentic_pattern: String::from("none"),
        delta_status: None,
        source_attribution: None,
    }];
    merge_delta_status(
        &mut findings,
        "## 7. Recommended Actions\n\n| Finding ID | Status |\n| --- | --- |\n| S-1 | UPDATED |\n",
    );
    assert_eq!(findings[0].delta_status.as_deref(), Some("UPDATED"));
    merge_source_attribution(
        &mut findings,
        "## 9. Source Attribution\n\n```yaml\nS-1:\n  - {taxonomy: owasp, id: A07, relationship: primary}\n```\n",
    );
    assert_eq!(
        findings[0].source_attribution.as_ref().map(Vec::len),
        Some(1)
    );
    let _ = ThreatReportData::default();
    let _ = RemediationTimelineEntry {
        timeline: String::new(),
        count: 0,
        severity: String::new(),
    };
    let _ = RemediationFinding::default();
    let _ = RemediationAction {
        severity: String::new(),
        finding_id: String::new(),
        finding_name: String::new(),
        recommendation: String::new(),
        sla: String::new(),
        status: String::new(),
    };
    let _ = MMDC_INSTALL_HINT;
}
