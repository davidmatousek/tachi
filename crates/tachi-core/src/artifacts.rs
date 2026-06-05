use std::fs;
use std::path::{Path, PathBuf};

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ArtifactDetection {
    pub has_threats_md: bool,
    pub threats_md: Option<PathBuf>,
    pub has_risk_scores_md: bool,
    pub risk_scores_md: Option<PathBuf>,
    pub has_compensating_controls_md: bool,
    pub compensating_controls_md: Option<PathBuf>,
    pub has_threat_report_md: bool,
    pub threat_report_md: Option<PathBuf>,
    pub has_attack_trees: bool,
    pub attack_trees_dir: Option<PathBuf>,
}

pub fn detect_artifacts(root: &Path) -> ArtifactDetection {
    let threats_md = root.join("threats.md");
    let risk_scores_md = root.join("risk-scores.md");
    let compensating_controls_md = root.join("compensating-controls.md");
    let threat_report_md = root.join("threat-report.md");
    let attack_trees_dir = root.join("attack-trees");

    let has_attack_trees = fs::read_dir(&attack_trees_dir)
        .map(|entries| {
            entries.flatten().any(|entry| {
                entry
                    .path()
                    .extension()
                    .and_then(|ext| ext.to_str())
                    .is_some_and(|ext| ext.eq_ignore_ascii_case("md"))
            })
        })
        .unwrap_or(false);

    ArtifactDetection {
        has_threats_md: threats_md.exists(),
        threats_md: threats_md.exists().then_some(threats_md),
        has_risk_scores_md: risk_scores_md.exists(),
        risk_scores_md: risk_scores_md.exists().then_some(risk_scores_md),
        has_compensating_controls_md: compensating_controls_md.exists(),
        compensating_controls_md: compensating_controls_md
            .exists()
            .then_some(compensating_controls_md),
        has_threat_report_md: threat_report_md.exists(),
        threat_report_md: threat_report_md.exists().then_some(threat_report_md),
        has_attack_trees,
        attack_trees_dir: has_attack_trees.then_some(attack_trees_dir),
    }
}

pub fn determine_tier(artifacts: &ArtifactDetection) -> u8 {
    if artifacts.has_compensating_controls_md {
        1
    } else if artifacts.has_risk_scores_md {
        2
    } else {
        3
    }
}
