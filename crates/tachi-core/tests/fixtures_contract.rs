use pretty_assertions::assert_eq;
use serde_json::json;
use tachi_core::fixtures::{
    hash_fixture_payload, serialize_fixture, validate_fixture_schema, CommandFixture,
};

#[test]
fn serialize_fixture_emits_versioned_command_contract() {
    let input = json!({
        "template": "maestro-stack",
        "root": "/tmp/workspace"
    });
    let output = json!({
        "template": "maestro-stack",
        "template_data": {
            "layers": ["l1", "l2"]
        }
    });

    let rendered = serialize_fixture("infographic-data", &input, &output)
        .expect("serialize command fixture");
    let parsed = validate_fixture_schema(&rendered).expect("validate serialized fixture");

    assert_eq!(parsed.command, "infographic-data");
    assert_eq!(parsed.schema_version, 1);
    assert_eq!(parsed.input, input);
    assert_eq!(parsed.output, output);
    assert_eq!(parsed.input_hash, hash_fixture_payload(&parsed.input).unwrap());
    assert_eq!(parsed.output_hash, hash_fixture_payload(&parsed.output).unwrap());
}

#[test]
fn hash_fixture_payload_is_order_independent_for_objects() {
    let left = json!({"b": 2, "a": 1});
    let right = json!({"a": 1, "b": 2});

    assert_eq!(
        hash_fixture_payload(&left).expect("hash left"),
        hash_fixture_payload(&right).expect("hash right")
    );
}

#[test]
fn validate_fixture_schema_rejects_version_skew_and_hash_mismatch() {
    let fixture = CommandFixture {
        schema_version: 9,
        command: String::from("report-data"),
        input: json!({"root": "/tmp"}),
        input_hash: String::from("bad"),
        output: json!({"status": "ok"}),
        output_hash: String::from("also-bad"),
    };

    let rendered = serde_json::to_string_pretty(&fixture).expect("serialize malformed fixture");
    let err = validate_fixture_schema(&rendered).expect_err("reject version skew");
    assert!(
        err.contains("schema version"),
        "unexpected validation error: {err}"
    );
}
