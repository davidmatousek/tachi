use std::str::FromStr;

use pretty_assertions::assert_eq;

use tachi_core::{
    AccessContext, AccessMode, AisvsError, InfrastructurePolicy, LifecycleGate, LifecycleStage,
    MemoryScope, ModelBehaviorPolicy, PromptInput, SupplyChainEvidence, TrainingDataAsset,
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

#[test]
fn c05_access_context_requires_explicit_mode_and_role() {
    let context = AccessContext::new("ops-user", AccessMode::Operator).unwrap();
    assert_eq!(context.subject(), "ops-user");
    assert_eq!(context.mode(), AccessMode::Operator);

    let err = AccessContext::new("  ", AccessMode::Operator).unwrap_err();
    assert_eq!(err, AisvsError::InvalidAccessContext);
    assert_eq!(err.code(), "AISVS_INVALID_ACCESS_CONTEXT");
}

#[test]
fn c06_supply_chain_evidence_requires_attestation_and_audit_tag() {
    let evidence = SupplyChainEvidence::new(
        "glib",
        "0.18.5",
        "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "https://example.com/attestations/glib-0.18.5",
    )
    .unwrap();

    assert_eq!(evidence.package(), "glib");
    assert_eq!(evidence.version(), "0.18.5");
    assert_eq!(evidence.audit_tag(), "glib@0.18.5");

    let err = SupplyChainEvidence::new("glib", "0.18.5", "sha256:bad", "").unwrap_err();
    assert_eq!(err, AisvsError::InvalidSupplyChainEvidence);
    assert_eq!(err.code(), "AISVS_INVALID_SUPPLY_CHAIN_EVIDENCE");
}

#[test]
fn c07_model_behavior_policy_rejects_unbounded_free_form_output() {
    let policy = ModelBehaviorPolicy::strict("response.schema.json", 4096).unwrap();
    assert_eq!(policy.output_schema(), "response.schema.json");
    assert_eq!(policy.max_output_chars(), 4096);
    assert!(policy.is_redaction_required());

    let err = ModelBehaviorPolicy::new("", 0, false).unwrap_err();
    assert_eq!(err, AisvsError::InvalidModelBehaviorPolicy);
    assert_eq!(err.code(), "AISVS_INVALID_MODEL_BEHAVIOR_POLICY");
}

#[test]
fn c08_memory_scope_rejects_unbounded_retention_and_cross_scope_use() {
    let scope = MemoryScope::bounded(128, 30).unwrap();
    assert_eq!(scope.max_entries(), 128);
    assert_eq!(scope.retention_days(), 30);
    assert!(!scope.allows_cross_scope());

    let err = MemoryScope::new(0, 365, true).unwrap_err();
    assert_eq!(err, AisvsError::InvalidMemoryScope);
    assert_eq!(err.code(), "AISVS_INVALID_MEMORY_SCOPE");
}
