use std::fs;
use std::path::{Path, PathBuf};

use serde_yaml::Value;
use tachi_core::parsers::{validate_source_attribution, SourceAttributionRecord, ThreatFinding};

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read_text(path: &Path) -> String {
    fs::read_to_string(path)
        .unwrap_or_else(|err| panic!("failed to read {}: {err}", path.display()))
}

fn read_yaml(path: &Path) -> Value {
    let content = read_text(path);
    serde_yaml::from_str(&content)
        .unwrap_or_else(|err| panic!("failed to parse {}: {err}", path.display()))
}

fn yaml_string(value: &Value, key: &str) -> String {
    value
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from(key)))
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_string()
}

fn yaml_to_threat_finding(value: Value) -> ThreatFinding {
    let source_attribution = value
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from("source_attribution")))
        .and_then(Value::as_sequence)
        .map(|records| {
            records
                .iter()
                .map(|record| SourceAttributionRecord {
                    taxonomy: yaml_string(record, "taxonomy"),
                    id: yaml_string(record, "id"),
                    relationship: yaml_string(record, "relationship"),
                })
                .collect::<Vec<_>>()
        });

    ThreatFinding {
        id: yaml_string(&value, "id"),
        component: yaml_string(&value, "component"),
        threat: yaml_string(&value, "threat"),
        likelihood: yaml_string(&value, "likelihood"),
        impact: yaml_string(&value, "impact"),
        risk_level: yaml_string(&value, "risk_level"),
        mitigation: yaml_string(&value, "mitigation"),
        agentic_pattern: yaml_string(&value, "agentic_pattern"),
        delta_status: value
            .as_mapping()
            .and_then(|mapping| mapping.get(Value::from("delta_status")))
            .and_then(Value::as_str)
            .map(ToOwned::to_owned),
        source_attribution,
    }
}

fn tool_abuse_agent_path() -> PathBuf {
    workspace_root().join(".claude/agents/tachi/tool-abuse.md")
}

fn detection_patterns_path() -> PathBuf {
    workspace_root().join(".claude/skills/tachi-tool-abuse/references/detection-patterns.md")
}

fn tool_abuse_fixture_dir() -> PathBuf {
    workspace_root().join("tests/scripts/fixtures/tool_abuse_enrichment")
}

fn taxonomy_dir() -> PathBuf {
    workspace_root().join("schemas/taxonomy")
}

#[test]
fn tool_abuse_enrichment_contract_is_rust_native() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_tool_abuse_enrichment.py")
            .exists(),
        "tool-abuse enrichment coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn tool_abuse_line_count_within_cap() {
    let line_count = fs::read_to_string(tool_abuse_agent_path())
        .expect("read tool-abuse.md")
        .lines()
        .count();
    assert!(
        line_count <= 150,
        "tool-abuse.md line count {line_count} exceeds AI-tier cap of 150"
    );
}

#[test]
fn tool_abuse_single_mandatory_read() {
    let content = read_text(&tool_abuse_agent_path());
    assert_eq!(
        content.matches("**MANDATORY**: Read").count(),
        1,
        "tool-abuse.md must contain exactly one mandatory read directive"
    );
}

#[test]
fn tool_abuse_zero_maestro_references() {
    let content = read_text(&tool_abuse_agent_path()).to_lowercase();
    assert!(
        !content.contains("maestro"),
        "tool-abuse.md must contain zero MAESTRO references"
    );
}

#[test]
fn tool_abuse_metadata_includes_asi07() {
    let content = read_text(&tool_abuse_agent_path());
    let metadata_line = content
        .lines()
        .find(|line| line.starts_with("owasp_references: ["))
        .expect("owasp_references metadata key");
    assert!(metadata_line.contains("ASI-07"));
    for required in ["ASI-02", "ASI-04", "MCP-03", "MCP-05", "LLM06:2025"] {
        assert!(
            metadata_line.contains(required),
            "tool-abuse.md should preserve {required}"
        );
    }
}

#[test]
fn tool_abuse_workflow_step5_extended() {
    let content = read_text(&tool_abuse_agent_path());
    for required in ["ASI-07", "AML.T0060", "CWE-287", "CWE-345"] {
        assert!(
            content.contains(required),
            "tool-abuse.md should include {required}"
        );
    }
}

#[test]
fn detection_patterns_categories_9_and_10_present() {
    let content = read_text(&detection_patterns_path());
    assert!(
        content.contains("## Pattern Category 9: Insecure Inter-Agent Communication"),
        "Pattern Category 9 header missing"
    );
    assert!(
        content.contains("## Pattern Category 10: MCP-to-MCP Trust Propagation"),
        "Pattern Category 10 header missing"
    );
    assert!(
        content.contains("## Pattern Category Disambiguation"),
        "Pattern category disambiguation subsection missing"
    );
}

#[test]
fn detection_patterns_categories_have_required_subsections() {
    let content = read_text(&detection_patterns_path());
    let cat9_start = content
        .find("## Pattern Category 9: Insecure Inter-Agent Communication")
        .expect("category 9 heading");
    let cat10_start = content
        .find("## Pattern Category 10: MCP-to-MCP Trust Propagation")
        .expect("category 10 heading");
    let disambiguation_start = content
        .find("## Pattern Category Disambiguation")
        .expect("disambiguation heading");
    let cat9_section = &content[cat9_start..cat10_start];
    let cat10_section = &content[cat10_start..disambiguation_start];

    for (section_name, section_content) in
        [("Category 9", cat9_section), ("Category 10", cat10_section)]
    {
        for required in [
            "**Indicators**",
            "**Anti-Indicators**",
            "**Worked Example**",
            "**Primary source**",
            "**Related sources**",
            "**Mitigations**",
        ] {
            assert!(
                section_content.contains(required),
                "{section_name} missing {required}"
            );
        }
    }
}

#[test]
fn detection_patterns_primary_sources_extended() {
    let content = read_text(&detection_patterns_path());
    let primary_sources_start = content
        .find("## Primary Sources")
        .expect("primary sources heading");
    let primary_sources = &content[primary_sources_start..];
    assert!(primary_sources.contains("OWASP ASI07:2026"));
    assert!(primary_sources.contains("AML.T0060"));
}

#[test]
fn detection_patterns_zero_maestro_references() {
    let content = read_text(&detection_patterns_path()).to_lowercase();
    assert!(
        !content.contains("maestro"),
        "detection-patterns.md must contain zero MAESTRO references"
    );
}

#[test]
fn valid_cat_9_fixture_passes_referential_integrity() {
    let finding = yaml_to_threat_finding(read_yaml(
        &tool_abuse_fixture_dir().join("valid_category_9_a2a_finding.yaml"),
    ));
    let errors = validate_source_attribution(&[finding], &taxonomy_dir());
    assert!(
        errors.is_empty(),
        "valid category 9 fixture should pass referential integrity"
    );
}

#[test]
fn valid_cat_10_fixture_passes_referential_integrity() {
    let finding = yaml_to_threat_finding(read_yaml(
        &tool_abuse_fixture_dir().join("valid_category_10_mcp_to_mcp_finding.yaml"),
    ));
    let errors = validate_source_attribution(&[finding], &taxonomy_dir());
    assert!(
        errors.is_empty(),
        "valid category 10 fixture should pass referential integrity"
    );
}

#[test]
fn invalid_attribution_fixture_rejected() {
    let finding = yaml_to_threat_finding(read_yaml(
        &tool_abuse_fixture_dir().join("invalid_attribution_finding.yaml"),
    ));
    let errors = validate_source_attribution(&[finding], &taxonomy_dir());
    assert!(
        !errors.is_empty(),
        "invalid attribution fixture must be rejected"
    );
    assert!(
        errors
            .iter()
            .any(|error| error.reason.contains("CWE-99999")),
        "invalid attribution errors must mention CWE-99999"
    );
}

#[test]
fn cat_9_fixture_has_required_source_attribution_shape() {
    let finding = read_yaml(&tool_abuse_fixture_dir().join("valid_category_9_a2a_finding.yaml"));
    let sa = finding
        .get("source_attribution")
        .and_then(Value::as_sequence)
        .expect("source attribution sequence");
    assert!(sa.iter().any(|entry| {
        entry.get("taxonomy").and_then(Value::as_str) == Some("owasp")
            && entry.get("id").and_then(Value::as_str) == Some("ASI07")
            && entry.get("relationship").and_then(Value::as_str) == Some("primary")
    }));
    assert!(sa.iter().any(|entry| {
        entry.get("taxonomy").and_then(Value::as_str) == Some("cwe")
            && entry.get("id").and_then(Value::as_str) == Some("CWE-287")
            && entry.get("relationship").and_then(Value::as_str) == Some("related")
    }));
}

#[test]
fn cat_10_fixture_has_required_source_attribution_shape() {
    let finding =
        read_yaml(&tool_abuse_fixture_dir().join("valid_category_10_mcp_to_mcp_finding.yaml"));
    let sa = finding
        .get("source_attribution")
        .and_then(Value::as_sequence)
        .expect("source attribution sequence");
    assert!(sa.iter().any(|entry| {
        entry.get("taxonomy").and_then(Value::as_str) == Some("owasp")
            && entry.get("id").and_then(Value::as_str) == Some("ASI07")
            && entry.get("relationship").and_then(Value::as_str) == Some("primary")
    }));
    assert!(sa.iter().any(|entry| {
        entry.get("taxonomy").and_then(Value::as_str) == Some("cwe")
            && entry.get("id").and_then(Value::as_str) == Some("CWE-345")
            && entry.get("relationship").and_then(Value::as_str) == Some("related")
    }));
}

#[test]
fn fixture_ids_match_ag_prefix() {
    for fixture_name in [
        "valid_category_9_a2a_finding.yaml",
        "valid_category_10_mcp_to_mcp_finding.yaml",
    ] {
        let finding = read_yaml(&tool_abuse_fixture_dir().join(fixture_name));
        let finding_id = finding
            .get("id")
            .and_then(Value::as_str)
            .unwrap_or_default();
        assert!(
            finding_id.starts_with("AG-") && finding_id[3..].chars().all(|ch| ch.is_ascii_digit()),
            "fixture {fixture_name} id {finding_id:?} must match ^AG-\\d+$"
        );
    }
}

#[test]
fn validate_source_attribution_on_regen() {
    let threats_md = workspace_root().join("examples/agentic-app/sample-report/threats.md");
    let content = read_text(&threats_md);
    assert!(
        content.contains("| AG-"),
        "expected at least one AG finding in regenerated threats.md"
    );
    assert!(content.contains("ASI-07") || content.contains("ASI07"));
    assert!(
        content.contains("Inter-Agent Communication") || content.contains("A2A"),
        "expected A2A / inter-agent communication reference"
    );
    let mitigation_count = [
        "mTLS",
        "HMAC",
        "Ed25519",
        "message sign",
        "nonce",
        "replay",
        "taint",
    ]
    .iter()
    .filter(|pattern| content.contains(*pattern))
    .count();
    assert!(
        mitigation_count >= 2,
        "expected at least two named mitigation indicators"
    );
}
