use std::fs;
use std::path::{Path, PathBuf};

use serde_yaml::Value;

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read_text(path: &Path) -> String {
    fs::read_to_string(path).expect("read text")
}

fn line_count(path: &Path) -> usize {
    read_text(path).lines().count()
}

fn joined_refs(path: &Path) -> String {
    let value: Value = serde_yaml::from_str(&read_text(path)).expect("parse yaml fixture");
    let refs = value
        .get("references")
        .and_then(Value::as_sequence)
        .expect("fixture references array");

    refs.iter()
        .map(|item| item.as_str().expect("reference string"))
        .collect::<Vec<_>>()
        .join(" | ")
}

fn all_fixture_refs_joined() -> String {
    [
        T_10_FIXTURE,
        D_8_FIXTURE,
        D_9_FIXTURE,
        D_10_FIXTURE,
        LLM_12_FIXTURE,
        LLM_13_FIXTURE,
        LLM_14_FIXTURE,
    ]
    .into_iter()
    .map(|relative| joined_refs(&workspace_root().join(relative)))
    .collect::<Vec<_>>()
    .join(" | ")
}

const TAMPERING_AGENT: &str = ".claude/agents/tachi/tampering.md";
const DATA_POISONING_AGENT: &str = ".claude/agents/tachi/data-poisoning.md";
const MODEL_THEFT_AGENT: &str = ".claude/agents/tachi/model-theft.md";

const TAMPERING_COMPANION: &str = ".claude/skills/tachi-tampering/references/detection-patterns.md";
const DATA_POISONING_COMPANION: &str =
    ".claude/skills/tachi-data-poisoning/references/detection-patterns.md";
const MODEL_THEFT_COMPANION: &str =
    ".claude/skills/tachi-model-theft/references/detection-patterns.md";

const T_10_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_10_tampering_adversarial_input_finding.yaml",
);
const D_8_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_8_data_poisoning_transfer_learning_finding.yaml",
);
const D_9_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_9_data_poisoning_feedback_loop_finding.yaml",
);
const D_10_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_10_data_poisoning_corpus_supply_chain_finding.yaml",
);
const LLM_12_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_12_model_theft_inversion_finding.yaml",
);
const LLM_13_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_13_model_theft_membership_inference_finding.yaml",
);
const LLM_14_FIXTURE: &str = concat!(
    "tests/scripts/fixtures/ml_top_10_coverage_bundle/",
    "valid_category_14_model_theft_artifact_supply_chain_finding.yaml",
);

const ALL_ENRICHED_FILES: &[&str] = &[
    TAMPERING_AGENT,
    DATA_POISONING_AGENT,
    MODEL_THEFT_AGENT,
    TAMPERING_COMPANION,
    DATA_POISONING_COMPANION,
    MODEL_THEFT_COMPANION,
];

const ALL_F6_COMPANIONS: &[&str] = &[
    TAMPERING_COMPANION,
    DATA_POISONING_COMPANION,
    MODEL_THEFT_COMPANION,
];

#[test]
fn ml_top_10_coverage_bundle_contract_is_rust_native() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py")
            .exists(),
        "ML Top 10 bundle coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn line_caps_are_preserved_across_all_f6_agents() {
    let root = workspace_root();
    assert!(line_count(&root.join(TAMPERING_AGENT)) <= 120);
    assert!(line_count(&root.join(DATA_POISONING_AGENT)) <= 150);
    assert!(line_count(&root.join(MODEL_THEFT_AGENT)) <= 150);
}

#[test]
fn enriched_files_do_not_reference_maestro() {
    let root = workspace_root();
    for relative in ALL_ENRICHED_FILES {
        let content = read_text(&root.join(relative)).to_lowercase();
        assert!(
            !content.contains("maestro"),
            "{relative} must be MAESTRO-free"
        );
    }
}

#[test]
fn pattern_category_disambiguation_sections_are_present() {
    let root = workspace_root();
    for relative in ALL_F6_COMPANIONS {
        let content = read_text(&root.join(relative));
        let matches = content
            .match_indices("## Pattern Category Disambiguation")
            .count();
        assert_eq!(
            matches, 1,
            "{relative} must contain exactly one disambiguation section"
        );
    }
}

#[test]
fn companion_pattern_categories_are_present() {
    let root = workspace_root();
    let tampering = read_text(&root.join(TAMPERING_COMPANION));
    assert!(tampering.contains("## Pattern Category 10: Adversarial Input Manipulation"));

    let data_poisoning = read_text(&root.join(DATA_POISONING_COMPANION));
    assert!(data_poisoning.contains("## Pattern Category 8: Transfer Learning Supply Chain"));
    assert!(data_poisoning.contains("## Pattern Category 9: Feedback-Loop Model Skewing"));
    assert!(
        data_poisoning.contains("## Pattern Category 10: Predictive-ML Supply Chain Completeness")
    );

    let model_theft = read_text(&root.join(MODEL_THEFT_COMPANION));
    assert!(model_theft.contains("## Pattern Category 12: Model Inversion"));
    assert!(model_theft.contains("## Pattern Category 13: Membership Inference"));
    assert!(model_theft.contains("## Pattern Category 14: Artifact Supply Chain"));
}

#[test]
fn fixture_references_arrays_are_catalog_resolvable() {
    assert!(joined_refs(&workspace_root().join(T_10_FIXTURE)).contains("OWASP ML01:2023"));
    assert!(joined_refs(&workspace_root().join(D_8_FIXTURE)).contains("OWASP ML07:2023"));
    assert!(joined_refs(&workspace_root().join(D_9_FIXTURE)).contains("OWASP ML08:2023"));

    let d_10 = joined_refs(&workspace_root().join(D_10_FIXTURE));
    assert!(d_10.contains("OWASP ML06:2023"));
    assert!(d_10.contains("T1195"));

    let llm_12 = joined_refs(&workspace_root().join(LLM_12_FIXTURE));
    assert!(llm_12.contains("OWASP ML03:2023"));
    assert!(llm_12.contains("AML.T0024"));

    let llm_13 = joined_refs(&workspace_root().join(LLM_13_FIXTURE));
    assert!(llm_13.contains("OWASP ML04:2023"));
    assert!(llm_13.contains("AML.T0024"));

    let llm_14 = joined_refs(&workspace_root().join(LLM_14_FIXTURE));
    assert!(llm_14.contains("OWASP ML06:2023"));
    assert!(llm_14.contains("T1195"));
    assert!(llm_14.contains("T1195.001"));
    assert!(llm_14.contains("T1195.002"));
}

#[test]
fn atlas_techniques_are_only_referenced_when_catalog_resolvable() {
    let all_refs = all_fixture_refs_joined();

    for atlas_id in ["T0015", "T0019", "T0031"] {
        assert!(
            !all_refs.contains(atlas_id),
            "AML.{atlas_id} must remain prose-only in the ML bundle"
        );
    }

    assert!(all_refs.contains("T0018"));
    assert!(all_refs.contains("T0020"));
    assert!(all_refs.contains("T0024"));
    assert!(all_refs.contains("T1195"));
    assert!(all_refs.contains("T1195.001"));
    assert!(all_refs.contains("T1195.002"));
}

#[test]
fn mandatory_read_directives_are_preserved() {
    let root = workspace_root();
    for relative in [TAMPERING_AGENT, DATA_POISONING_AGENT, MODEL_THEFT_AGENT] {
        let content = read_text(&root.join(relative));
        assert!(content.contains("**MANDATORY**: Read"));
    }
}
