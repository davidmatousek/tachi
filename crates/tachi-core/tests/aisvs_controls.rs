use std::str::FromStr;

use pretty_assertions::assert_eq;

use tachi_core::{
    AccessContext, AccessMode, AdversarialCase, AisvsError, InfrastructurePolicy, LifecycleGate,
    LifecycleStage, McpInvocation, McpPolicy, MemoryScope, ModelBehaviorPolicy, MonitoringEvent,
    MonitoringPolicy, OrchestrationAction, OrchestrationPolicy, PromptInput, SupplyChainEvidence,
    TrainingDataAsset,
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

#[test]
fn c09_orchestration_policy_requires_approval_before_escalation() {
    let policy = OrchestrationPolicy::new(true, false).unwrap();
    assert!(policy.requires_approval());
    assert!(!policy.allows_escalation());

    let action = OrchestrationAction::new("render-report", false).unwrap();
    assert_eq!(action.name(), "render-report");
    assert!(!action.is_escalation());

    let err = OrchestrationPolicy::new(false, true).unwrap_err();
    assert_eq!(err, AisvsError::InvalidOrchestrationPolicy);
    assert_eq!(err.code(), "AISVS_INVALID_ORCHESTRATION_POLICY");
}

#[test]
fn c10_mcp_policy_requires_schema_and_tool_allowlist() {
    let policy = McpPolicy::new("invoke.schema.json", &["search", "status"]).unwrap();
    assert_eq!(policy.schema_name(), "invoke.schema.json");
    assert!(policy.allows_tool("search"));
    assert!(!policy.allows_tool("delete"));

    let invocation = McpInvocation::new("search", "query=telemetry").unwrap();
    assert_eq!(invocation.tool_name(), "search");
    assert_eq!(invocation.payload(), "query=telemetry");

    let err = McpPolicy::new("", &["search"]).unwrap_err();
    assert_eq!(err, AisvsError::InvalidMcpPolicy);
    assert_eq!(err.code(), "AISVS_INVALID_MCP_POLICY");
}

#[test]
fn c11_adversarial_case_is_explicit_and_fail_closed() {
    let case = AdversarialCase::new("prompt-injection", "drop system prompt").unwrap();
    assert_eq!(case.family(), "prompt-injection");
    assert_eq!(case.payload(), "drop system prompt");

    let err = AdversarialCase::new(" ", "").unwrap_err();
    assert_eq!(err, AisvsError::InvalidAdversarialCase);
    assert_eq!(err.code(), "AISVS_INVALID_ADVERSARIAL_CASE");
}

#[test]
fn c12_monitoring_policy_redacts_secrets_and_rejects_empty_events() {
    let policy = MonitoringPolicy::strict_redaction();
    let event = MonitoringEvent::new("aisvs", "policy updated").unwrap();
    assert_eq!(event.component(), "aisvs");
    assert_eq!(event.message(), "policy updated");
    assert!(policy.redacts_secrets());

    let err = MonitoringEvent::new("", " ").unwrap_err();
    assert_eq!(err, AisvsError::InvalidMonitoringEvent);
    assert_eq!(err.code(), "AISVS_INVALID_MONITORING_EVENT");
}
