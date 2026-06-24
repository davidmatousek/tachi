use pretty_assertions::assert_eq;
use std::str::FromStr;

use tachi_core::{aisvs_control_registry, AisvsControlId, AisvsError, AisvsRegistry};

fn assert_send_sync<T: Send + Sync>() {}

#[test]
fn aisvs_registry_lists_all_controls_in_order() {
    let registry = aisvs_control_registry();
    let ids: Vec<_> = registry
        .controls()
        .iter()
        .map(|control| control.id().as_str())
        .collect();

    assert_eq!(
        ids,
        vec!["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12",]
    );
    assert_eq!(registry.framework_name(), "AISVS 1.0");
    assert_eq!(
        registry.controls()[0].capability(),
        "Training-data integrity and traceability"
    );
    assert_eq!(registry.controls()[11].function(), "Monitoring and logging");
    assert_eq!(
        registry.controls()[4].validation_command(),
        "cargo test -p tachi-core --test aisvs_controls c05_access_context_requires_explicit_mode_and_role"
    );
}

#[test]
fn aisvs_registry_exposes_validation_commands_for_each_control() {
    let registry = aisvs_control_registry();
    let commands = registry.validation_commands();

    assert_eq!(
        commands,
        vec![
            "cargo test -p tachi-core --test aisvs_controls c01_training_data_asset_requires_provenance_and_integrity",
            "cargo test -p tachi-core --test aisvs_controls c02_prompt_input_rejects_blank_ambiguous_and_control_bytes",
            "cargo test -p tachi-core --test aisvs_controls c03_lifecycle_gate_forbids_skipping_validation_states",
            "cargo test -p tachi-core --test aisvs_controls c04_infrastructure_policy_defaults_to_least_privilege",
            "cargo test -p tachi-core --test aisvs_controls c05_access_context_requires_explicit_mode_and_role",
            "cargo test -p tachi-core --test aisvs_controls c06_supply_chain_evidence_requires_attestation_and_audit_tag",
            "cargo test -p tachi-core --test aisvs_controls c07_model_behavior_policy_rejects_unbounded_free_form_output",
            "cargo test -p tachi-core --test aisvs_controls c08_memory_scope_rejects_unbounded_retention_and_cross_scope_use",
            "cargo test -p tachi-core --test aisvs_controls c09_orchestration_policy_requires_approval_before_escalation",
            "cargo test -p tachi-core --test aisvs_controls c10_mcp_policy_requires_schema_and_tool_allowlist",
            "cargo test -p tachi-core --test aisvs_controls c11_adversarial_case_is_explicit_and_fail_closed",
            "cargo test -p tachi-core --test aisvs_controls c12_monitoring_policy_redacts_secrets_and_rejects_empty_events",
        ]
    );
}

#[test]
fn aisvs_control_id_parses_known_values_and_rejects_invalid_inputs() {
    assert_eq!(
        AisvsControlId::from_str("C01").unwrap(),
        AisvsControlId::C01
    );
    assert_eq!(
        AisvsControlId::from_str(" C12 ").unwrap(),
        AisvsControlId::C12
    );
    assert_eq!(
        AisvsControlId::from_str("c07").unwrap(),
        AisvsControlId::C07
    );

    let err = AisvsControlId::from_str("C99").unwrap_err();
    assert_eq!(err, AisvsError::InvalidControlId);
    assert_eq!(err.code(), "AISVS_INVALID_CONTROL_ID");
    assert_eq!(err.to_string(), "invalid AISVS control id");
}

#[test]
fn aisvs_lookup_returns_sanitized_error() {
    let registry = AisvsRegistry::new(
        "AISVS 1.0",
        "1.0",
        vec![tachi_core::AisvsControl::new(
            AisvsControlId::C01,
            "Training-data integrity and traceability",
            "Immutable training lineage",
            "Capture provenance for AI input sets",
            "Training-data integrity and traceability",
            "cargo test -p tachi-core --test aisvs_controls c01_training_data_asset_requires_provenance_and_integrity",
            "Tests prove invalid lineage is unrepresentable and provenance is preserved.",
        )],
    )
    .unwrap();

    let err = registry.control(AisvsControlId::C02).unwrap_err();
    assert_eq!(err, AisvsError::UnknownControl);
    assert_eq!(err.code(), "AISVS_UNKNOWN_CONTROL");
    assert_eq!(err.to_string(), "unknown AISVS control");
}

#[test]
fn aisvs_registry_rejects_duplicate_controls() {
    let duplicate = tachi_core::AisvsControl::new(
        AisvsControlId::C01,
        "Training-data integrity and traceability",
        "Immutable training lineage",
        "Capture provenance for AI input sets",
        "Training-data integrity and traceability",
        "cargo test -p tachi-core --test aisvs_controls c01_training_data_asset_requires_provenance_and_integrity",
        "Tests prove invalid lineage is unrepresentable and provenance is preserved.",
    );

    let err =
        AisvsRegistry::new("AISVS 1.0", "1.0", vec![duplicate.clone(), duplicate]).unwrap_err();

    assert_eq!(err, AisvsError::DuplicateControlId);
    assert_eq!(err.code(), "AISVS_DUPLICATE_CONTROL_ID");
    assert_eq!(err.to_string(), "duplicate AISVS control");
}

#[test]
fn aisvs_registry_is_send_sync() {
    assert_send_sync::<AisvsRegistry>();
}
