use std::str::FromStr;

use pretty_assertions::assert_eq;

use tachi_core::{
    AisvsError, InfrastructurePolicy, LifecycleGate, LifecycleStage, PromptInput, TrainingDataAsset,
};

#[test]
fn c01_training_data_asset_requires_provenance_and_integrity() {
    let asset = TrainingDataAsset::parse(
        "https://example.com/datasets/train.jsonl",
        "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "example corp",
    )
    .unwrap();

    assert_eq!(asset.source(), "https://example.com/datasets/train.jsonl");
    assert_eq!(asset.provenance(), "example corp");

    let err = TrainingDataAsset::parse("", "sha256:bad", "example corp").unwrap_err();
    assert_eq!(err, AisvsError::InvalidTrainingDataAsset);
    assert_eq!(err.code(), "AISVS_INVALID_TRAINING_DATA_ASSET");
}

#[test]
fn c02_prompt_input_rejects_blank_ambiguous_and_control_bytes() {
    let prompt = PromptInput::from_str("  normalize this prompt  ").unwrap();
    assert_eq!(prompt.as_str(), "normalize this prompt");

    let err = PromptInput::from_str("   ").unwrap_err();
    assert_eq!(err, AisvsError::InvalidPromptInput);
    assert_eq!(err.code(), "AISVS_INVALID_PROMPT_INPUT");
}

#[test]
fn c03_lifecycle_gate_forbids_skipping_validation_states() {
    let validated = LifecycleGate::new(LifecycleStage::Draft)
        .advance_to(LifecycleStage::Validated)
        .unwrap();
    let approved = validated.advance_to(LifecycleStage::Approved).unwrap();
    let deployed = approved.advance_to(LifecycleStage::Deployed).unwrap();

    assert_eq!(deployed.stage(), LifecycleStage::Deployed);

    let err = LifecycleGate::new(LifecycleStage::Draft)
        .advance_to(LifecycleStage::Approved)
        .unwrap_err();
    assert_eq!(err, AisvsError::InvalidLifecycleTransition);
    assert_eq!(err.code(), "AISVS_INVALID_LIFECYCLE_TRANSITION");
}

#[test]
fn c04_infrastructure_policy_defaults_to_least_privilege() {
    let policy = InfrastructurePolicy::least_privilege();
    assert!(policy.is_least_privilege());
    assert!(!policy.allows_network());
    assert!(!policy.allows_secret_access());

    let err = InfrastructurePolicy::new(true, true, true).unwrap_err();
    assert_eq!(err, AisvsError::OverbroadInfrastructurePolicy);
    assert_eq!(err.code(), "AISVS_OVERBROAD_INFRASTRUCTURE_POLICY");
}
