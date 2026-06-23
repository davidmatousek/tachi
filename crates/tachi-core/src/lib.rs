pub(crate) mod artifacts;
pub(crate) mod assets;
pub(crate) mod attack_chains;
pub mod attack_trees;
pub(crate) mod compensating_controls;
pub mod coverage_attestation;
pub mod coverage_audit;
pub(crate) mod coverage_taxonomy;
pub mod fixtures;
pub mod infographic;
pub(crate) mod metadata;
pub(crate) mod mmdc;
pub mod normalization;
pub(crate) mod parity;
pub mod parsers;
pub mod report_data;
pub(crate) mod report_extraction;
pub mod risk_scores;
pub mod sarif_common;
pub mod threats_sarif;

pub mod facade;

pub use facade::{
    build_infographic_payload, build_remediation_actions, build_report_data_typst,
    build_threats_sarif, canonical_maestro_layer_label, collect_audit, crate_name,
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
