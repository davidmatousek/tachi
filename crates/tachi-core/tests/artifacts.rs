use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::facade::{detect_artifacts, determine_tier};

fn temp_repo_dir() -> PathBuf {
    let mut root = std::env::temp_dir();
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system time before UNIX_EPOCH")
        .as_nanos();
    root.push(format!("tachi-core-artifacts-{stamp}"));
    fs::create_dir_all(&root).expect("create temp root");
    root
}

fn write_file(path: &Path, contents: &str) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent");
    }
    fs::write(path, contents).expect("write file");
}

#[test]
fn detect_artifacts_reports_present_files_and_directories() {
    let root = temp_repo_dir();
    write_file(&root.join("threats.md"), "# threats");
    write_file(&root.join("risk-scores.md"), "# risk");
    write_file(&root.join("compensating-controls.md"), "# controls");
    write_file(&root.join("threat-report.md"), "# report");
    write_file(&root.join("attack-trees").join("S-1.md"), "tree");

    let artifacts = detect_artifacts(&root);

    assert!(artifacts.has_threats_md);
    assert!(artifacts.has_risk_scores_md);
    assert!(artifacts.has_compensating_controls_md);
    assert!(artifacts.has_threat_report_md);
    assert!(artifacts.has_attack_trees);

    fs::remove_dir_all(root).ok();
}

#[test]
fn determine_tier_prefers_compensating_controls_then_risk_scores_then_threats() {
    let tier1 = detect_artifacts(&temp_with("compensating-controls.md"));
    let tier2 = detect_artifacts(&temp_with("risk-scores.md"));
    let tier3 = detect_artifacts(&temp_with("threats.md"));

    assert_eq!(determine_tier(&tier1), 1);
    assert_eq!(determine_tier(&tier2), 2);
    assert_eq!(determine_tier(&tier3), 3);
}

fn temp_with(filename: &str) -> PathBuf {
    let root = temp_repo_dir();
    write_file(&root.join(filename), "# artifact");
    root
}
