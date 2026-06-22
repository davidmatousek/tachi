use std::fs;
use std::path::{Path, PathBuf};

use tachi_core::facade::detect_images;
use tachi_core::facade::parse_compensating_controls_md;
use tachi_core::facade::{merge_delta_status, parse_threat_report_md};
use tachi_core::{attack_trees::parse_attack_trees, parsers::ThreatFinding};

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

#[test]
fn extractor_contract_fixes_contract_is_rust_native() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/scripts/test_extractor_contract_fixes.py")
            .exists(),
        "extractor contract fixes coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn parse_attack_trees_accepts_agent_emitted_slugged_filenames() {
    let root = workspace_root();
    let target_dir = root.join("target/test-extractor-contract-fixes");
    let attack_trees_dir = target_dir.join("attack-trees");
    fs::create_dir_all(&attack_trees_dir).expect("create attack-trees dir");
    fs::write(
        attack_trees_dir.join("S-1-api-auth-bypass.md"),
        "# Attack Tree: S-1 -- API auth bypass\n\n| Field | Value |\n|-------|-------|\n| Finding ID | S-1 |\n| Component | API |\n| Risk Level | Critical |\n| Threat | Attacker bypasses API auth |\n\n```mermaid\ngraph TD\n    A[Attacker] --> B[API]\n```\n",
    )
    .expect("write attack tree");

    let findings = vec![ThreatFinding {
        id: String::from("S-1"),
        component: String::from("API"),
        risk_level: String::from("Critical"),
        threat: String::from("Attacker bypasses API auth"),
        ..ThreatFinding::default()
    }];

    let entries = parse_attack_trees(&target_dir, &findings, None);

    assert_eq!(entries.len(), 1);
    assert_eq!(entries[0].id, "S-1");
}

#[test]
fn parse_threat_report_md_falls_back_to_full_section1_prose() {
    let result = parse_threat_report_md(
        "# Threat Report\n\n## 1. Executive Summary\n\nThe system under review is a SaaS application with 42 active findings.\n\n**Risk profile by count**: 5 Critical, 12 High, 20 Medium, 5 Low.\n\n**Most critical unresolved exposure**: The auth service allows unauthenticated admin access via a legacy flag that was never removed.\n\n## 2. Architecture Overview\n\nComponents and trust boundaries follow below.\n",
    );

    let narrative = result.executive_narrative.expect("narrative should exist");
    assert!(narrative.contains("42 active findings"));
    assert!(narrative.contains("Risk profile by count"));
    assert!(!narrative.contains("## 2."));
}

#[test]
fn detect_images_accepts_matching_png_and_jpeg_bytes() {
    let root = workspace_root().join("target/test-extractor-contract-fixes-images");
    let target_dir = root.join("target");
    let template_dir = root.join("template");
    fs::create_dir_all(&target_dir).expect("create target dir");
    fs::create_dir_all(&template_dir).expect("create template dir");
    let png_bytes = [b"\x89PNG\r\n\x1a\n".as_slice(), b"payload".as_slice()].concat();
    fs::write(target_dir.join("threat-risk-funnel.jpg"), &png_bytes).expect("write mislabeled png");
    fs::write(target_dir.join("threat-baseball-card.png"), &png_bytes).expect("write png");

    let images = detect_images(&target_dir, &template_dir);
    assert!(images
        .funnel_image_path
        .as_deref()
        .expect("funnel image path")
        .ends_with("threat-risk-funnel.png"));
    assert!(images
        .baseball_image_path
        .as_deref()
        .expect("baseball image path")
        .ends_with("threat-baseball-card.png"));
}

#[test]
fn parse_compensating_controls_dedupes_cross_listed_findings() {
    let data = parse_compensating_controls_md(
        "---\nschema_version: \"1.0\"\n---\n\n## 1. Executive Summary\n\n**Risk Reduction**: 100.0 inherent -> 60.0 residual (**40.0%** reduction)\n**Coverage**: 30% Found | 30% Partial | 40% Missing\n\n## 2. Coverage Matrix\n\n### High Residual Severity\n\n| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |\n|-----------|-----------|--------|----------------|-------------------|----------------|\n| S-1 | API | Auth bypass | 8.0 | High | Partial |\n| S-2 | DB | Data exfil | 5.5 | High | Missing |\n\n### Medium Residual Severity\n\n| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |\n|-----------|-----------|--------|----------------|-------------------|----------------|\n| S-2 | DB | Data exfil | 5.5 | Medium | Missing |\n| S-3 | Net | Flood | 4.5 | Medium | Found |\n",
    );

    assert_eq!(data.findings.len(), 3);
    assert_eq!(data.severity.total, 3);
}

#[test]
fn merge_delta_status_populates_tier1_findings() {
    let mut findings = vec![
        ThreatFinding {
            id: String::from("S-1"),
            component: String::from("API"),
            threat: String::from("Auth bypass"),
            ..ThreatFinding::default()
        },
        ThreatFinding {
            id: String::from("S-2"),
            component: String::from("DB"),
            threat: String::from("Data exfil"),
            ..ThreatFinding::default()
        },
        ThreatFinding {
            id: String::from("S-3"),
            component: String::from("Net"),
            threat: String::from("Unknown"),
            ..ThreatFinding::default()
        },
    ];

    merge_delta_status(
        &mut findings,
        "# Threat Model\n\n## 7. Recommended Actions\n\n| Finding ID | Status | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |\n|------------|--------|-----------|---------------|--------|------------|------------|\n| S-1 | UNCHANGED | API | L3 | Auth bypass | Critical | Rotate keys |\n| S-2 | NEW | DB | L2 | Data exfil | High | Encrypt |\n",
    );

    assert_eq!(findings[0].delta_status.as_deref(), Some("UNCHANGED"));
    assert_eq!(findings[1].delta_status.as_deref(), Some("NEW"));
    assert!(findings[2].delta_status.is_none());
}
