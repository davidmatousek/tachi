use tachi_core::sarif_common::{
    build_sarif_envelope, level_for_band, parse_component_metadata, prefix_for, SARIF_SCHEMA_URI,
};

#[test]
fn prefix_for_splits_on_the_last_hyphen_only() {
    assert_eq!(prefix_for("AG-12"), "AG");
    assert_eq!(prefix_for("AGP-12"), "AGP");
    assert_eq!(prefix_for("LLM-10"), "LLM");
    assert_eq!(prefix_for("no-hyphen"), "no");
}

#[test]
fn level_for_band_defaults_to_warning_for_unknown_bands() {
    assert_eq!(level_for_band("Critical"), "error");
    assert_eq!(level_for_band("Low"), "note");
    assert_eq!(level_for_band("unexpected"), "warning");
}

#[test]
fn parse_component_metadata_maps_components_to_zones() {
    let threats_md = r#"
# Threat Model

### Components

| Component | Type |
| --- | --- |
| API Gateway | Process |
| Database | Data Store |

### Trust Zones

| Zone | Components |
| --- | --- |
| Edge | API Gateway |
| Core | Database |
"#;

    let metadata = parse_component_metadata(threats_md);

    assert_eq!(metadata.get("API Gateway").unwrap().zone, "Edge");
    assert_eq!(metadata.get("API Gateway").unwrap().dfd_type, "Process");
    assert_eq!(metadata.get("Database").unwrap().zone, "Core");
}

#[test]
fn build_sarif_envelope_places_schema_before_version_when_requested() {
    let driver = serde_json::json!({"name": "tachi"});
    let taxonomies = vec![serde_json::json!({"name": "OWASP"})];
    let results = vec![serde_json::json!({"ruleId": "tachi/stride/spoofing"})];

    let envelope = build_sarif_envelope(driver, taxonomies, results, true);
    let serialized = serde_json::to_string(&envelope).expect("serialize sarif envelope");

    assert!(serialized.contains(SARIF_SCHEMA_URI));
    assert!(serialized.contains("\"version\":\"2.1.0\""));
}
