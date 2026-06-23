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
