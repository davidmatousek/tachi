pub(crate) mod artifacts;
pub(crate) mod assets;
pub(crate) mod attack_chains;
pub mod attack_trees;
pub(crate) mod compensating_controls;
pub mod fixtures;
pub mod coverage_attestation;
pub mod coverage_audit;
pub mod coverage_taxonomy;
pub mod normalization;
pub mod infographic;
pub(crate) mod mmdc;
pub(crate) mod parity;
pub mod parsers;
pub mod report_data;
pub mod report_extraction;
pub mod risk_scores;
pub mod sarif_common;
pub mod threats_sarif;

pub mod facade;

pub use facade::{
    build_infographic_payload, build_report_data_typst, build_threats_sarif, collect_audit,
    crate_name, detect_artifacts, detect_brand_assets, detect_images,
    ensure_attack_path_renderer_available, format_attack_path_render_failure_summary,
    generate_chain_mermaid, parse_attack_chains, parse_compensating_controls_md,
    parse_component_metadata, parse_risk_md_section2, parse_risk_md_section3,
    parse_risk_md_section4, parse_threats_findings, prefix_for, render, AttackChain,
    AttackChainFinding, MermaidRenderFailure, ThreatSarifFinding, MMDC_INSTALL_HINT,
};
