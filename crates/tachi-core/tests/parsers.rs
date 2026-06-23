use serde_json::json;
use std::path::Path;
use tachi_core::normalization::{normalize_optional_text, normalize_value, stable_trim_text};
use tachi_core::parsers::{
    compute_delta_counts, compute_has_source_attribution, escape_typst_string,
    parse_component_asset_map, parse_finding_pattern, parse_markdown_table, parse_project_name,
    parse_threats_findings, strip_bold, validate_source_attribution, ResolvedFinding,
    ThreatFinding, VALID_AGENTIC_PATTERNS, VALID_ASSET_TAGS,
};

static PARSER_TEMP_DIR_COUNTER: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

#[test]
fn escape_typst_string_escapes_backslashes_quotes_and_newlines() {
    let input = "one\\two\"three\nfour";

    let output = escape_typst_string(input);

    assert_eq!(output, "one\\\\two\\\"three\\nfour");
}

#[test]
fn strip_bold_removes_wrapping_double_asterisks() {
    assert_eq!(strip_bold("**Threat Model**"), "Threat Model");
    assert_eq!(strip_bold("no-bold"), "no-bold");
}

#[test]
fn parse_markdown_table_reads_rows_after_header() {
    let markdown = r#"
## 2. Scored Threat Table

| ID | Component | Threat |
| --- | --- | --- |
| S-1 | API | Broken auth |
| S-2 | UI | XSS |
"#;

    let rows = parse_markdown_table(markdown, "## 2. Scored Threat Table");

    assert_eq!(rows.len(), 2);
    assert_eq!(rows[0].get("ID").map(String::as_str), Some("S-1"));
    assert_eq!(rows[0].get("Component").map(String::as_str), Some("API"));
    assert_eq!(
        rows[0].get("Threat").map(String::as_str),
        Some("Broken auth")
    );
    assert_eq!(rows[1].get("ID").map(String::as_str), Some("S-2"));
}

#[test]
fn parse_project_name_prefers_title_override_then_threats_then_architecture_then_unknown() {
    let root = temp_dir();
    write_text(
        &root.join("architecture.md"),
        "# Web Application — Architecture\n",
    );

    assert_eq!(
        parse_project_name("# Beta Threat Model\n", Some("Gamma"), Some(&root)),
        "Gamma"
    );
    assert_eq!(
        parse_project_name("# Alpha Threat Model\n", None, Some(&root)),
        "Alpha"
    );
    assert_eq!(
        parse_project_name("# Threat Model: second-brain-mcp\n", None, Some(&root)),
        "second-brain-mcp"
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "Web Application"
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, None),
        "Unknown Project"
    );

    std::fs::remove_dir_all(root).ok();
}

#[test]
fn parse_project_name_matches_retired_pytest_contract() {
    let root = temp_dir();

    assert!(
        !workspace_root()
            .join("tests/scripts/test_project_name_parser.py")
            .exists(),
        "project-name parser coverage should live in Rust tests, not pytest"
    );

    assert_eq!(
        parse_project_name("# Alpha Threat Model\n", Some(""), None),
        "Alpha"
    );
    assert_eq!(
        parse_project_name("# Web Application Threat Model\n", None, None),
        "Web Application"
    );
    assert_eq!(
        parse_project_name("# Threat Model: second-brain-mcp\n", None, None),
        "second-brain-mcp"
    );

    write_text(
        &root.join("architecture.md"),
        "# Security Architecture — second-brain-mcp\n",
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "second-brain-mcp"
    );

    write_text(
        &root.join("architecture.md"),
        "# Architecture — my-service\n",
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "my-service"
    );

    write_text(&root.join("architecture.md"), "# Plain Heading\n");
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "Unknown Project"
    );

    write_text(
        &root.join("architecture.md"),
        "# Web Application - Architecture\n",
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "Unknown Project"
    );

    write_text(
        &root.join("architecture.md"),
        "#   Web Application   —   Architecture   \n",
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "Web Application"
    );

    write_text(
        &root.join("architecture.md"),
        "# Web Application — Architecture\n\n# Another Heading\n",
    );
    assert_eq!(
        parse_project_name("# Threat Model Report\n", None, Some(&root)),
        "Web Application"
    );
    assert_eq!(
        parse_project_name("# Beta Threat Model\n", None, Some(&root)),
        "Beta"
    );

    std::fs::remove_dir_all(root).ok();
}

#[test]
fn parse_finding_pattern_normalizes_case_and_sentinels() {
    assert_eq!(VALID_AGENTIC_PATTERNS.len(), 8);
    assert_eq!(
        VALID_AGENTIC_PATTERNS.to_vec(),
        vec![
            "agent_collusion",
            "emergent_behavior",
            "temporal_attack",
            "trust_exploitation",
            "communication_vulnerability",
            "resource_competition",
            "none",
            "multiple",
        ]
    );
    assert_eq!(
        parse_finding_pattern(Some("AGENT_COLLUSION")),
        "agent_collusion"
    );
    assert_eq!(parse_finding_pattern(Some("Multiple")), "multiple");
    assert_eq!(parse_finding_pattern(Some("—")), "none");
    assert_eq!(parse_finding_pattern(Some("-")), "none");
    assert_eq!(parse_finding_pattern(None), "none");
    assert_eq!(parse_finding_pattern(Some("xyz")), "none");
}

#[test]
fn finding_pattern_parser_contract_is_rust_native() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/scripts/test_finding_pattern_parser.py")
            .exists(),
        "finding-pattern parser coverage should live in Rust tests, not pytest"
    );

    let with_patterns = parse_threats_findings(include_str!(
        "../../../tests/scripts/fixtures/finding_pattern_parser/threats_with_patterns.md"
    ))
    .expect("parse pattern fixture");
    assert_eq!(with_patterns.len(), 10);
    assert_eq!(with_patterns[0].agentic_pattern, "trust_exploitation");
    assert_eq!(with_patterns[1].agentic_pattern, "agent_collusion");
    assert_eq!(with_patterns[2].agentic_pattern, "agent_collusion");
    assert_eq!(with_patterns[3].agentic_pattern, "none");
    assert_eq!(with_patterns[4].agentic_pattern, "emergent_behavior");
    assert_eq!(with_patterns[5].agentic_pattern, "temporal_attack");
    assert_eq!(
        with_patterns[6].agentic_pattern,
        "communication_vulnerability"
    );
    assert_eq!(with_patterns[7].agentic_pattern, "resource_competition");
    assert_eq!(with_patterns[8].agentic_pattern, "multiple");
    assert_eq!(with_patterns[9].agentic_pattern, "none");

    let pre_feature = parse_threats_findings(include_str!(
        "../../../tests/scripts/fixtures/finding_pattern_parser/threats_pre_feature_142.md"
    ))
    .expect("parse pre-feature fixture");
    assert_eq!(pre_feature.len(), 5);
    assert!(pre_feature
        .iter()
        .all(|finding| finding.agentic_pattern == "none"));

    let all_em_dash = parse_threats_findings(include_str!(
        "../../../tests/scripts/fixtures/finding_pattern_parser/threats_all_em_dash.md"
    ))
    .expect("parse em-dash fixture");
    assert_eq!(all_em_dash.len(), 4);
    assert!(all_em_dash
        .iter()
        .all(|finding| finding.agentic_pattern == "none"));

    let mixed_case = parse_threats_findings(include_str!(
        "../../../tests/scripts/fixtures/finding_pattern_parser/threats_mixed_case_headers.md"
    ))
    .expect("parse mixed-case fixture");
    assert_eq!(
        mixed_case
            .iter()
            .map(|finding| finding.agentic_pattern.as_str())
            .collect::<Vec<_>>(),
        vec![
            "trust_exploitation",
            "agent_collusion",
            "emergent_behavior",
            "multiple",
            "none",
        ]
    );

    let shifted = parse_threats_findings(include_str!(
        "../../../tests/scripts/fixtures/finding_pattern_parser/threats_pattern_column_shifted.md"
    ))
    .expect("parse shifted-column fixture");
    assert_eq!(
        shifted
            .iter()
            .map(|finding| finding.agentic_pattern.as_str())
            .collect::<Vec<_>>(),
        vec!["trust_exploitation", "agent_collusion", "none"]
    );
}

#[test]
fn parse_threats_findings_roundtrips_a_canonical_seed_row_without_loss() {
    let seed = r#"
## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Agentic Pattern | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-1 | Parser | Preserve exact field tokens | Medium | Keep identifiers stable | trust_exploitation | open |
"#;

    let findings = parse_threats_findings(seed).expect("parse canonical seed row");
    assert_eq!(findings.len(), 1);

    let first = &findings[0];
    assert_eq!(first.id, "R-1");
    assert_eq!(first.component, "Parser");
    assert_eq!(first.threat, "Preserve exact field tokens");
    assert_eq!(first.risk_level, "Medium");
    assert_eq!(first.mitigation, "Keep identifiers stable");
    assert_eq!(first.agentic_pattern, "trust_exploitation");
    assert_eq!(first.delta_status.as_deref(), Some("open"));
    assert!(first.source_attribution.is_none());

    let roundtripped = format!(
        r#"
## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Agentic Pattern | Status |
| --- | --- | --- | --- | --- | --- | --- |
| {id} | {component} | {threat} | {risk_level} | {mitigation} | {pattern} | {status} |
"#,
        id = first.id,
        component = first.component,
        threat = first.threat,
        risk_level = first.risk_level,
        mitigation = first.mitigation,
        pattern = first.agentic_pattern,
        status = first.delta_status.as_deref().unwrap_or("—"),
    );

    let reparsed = parse_threats_findings(&roundtripped).expect("reparse roundtripped seed");
    assert_eq!(reparsed.len(), 1);
    assert_eq!(reparsed[0].id, first.id);
    assert_eq!(reparsed[0].component, first.component);
    assert_eq!(reparsed[0].threat, first.threat);
    assert_eq!(reparsed[0].risk_level, first.risk_level);
    assert_eq!(reparsed[0].mitigation, first.mitigation);
    assert_eq!(reparsed[0].agentic_pattern, first.agentic_pattern);
    assert_eq!(reparsed[0].delta_status, first.delta_status);
    assert_eq!(reparsed[0].source_attribution, first.source_attribution);
}

#[test]
fn normalize_value_trims_strings_and_stably_orders_nested_objects() {
    assert_eq!(stable_trim_text("  padded  "), "padded");
    assert_eq!(
        normalize_optional_text(Some("  ready  ")),
        Some(String::from("ready"))
    );
    assert_eq!(normalize_optional_text(Some("   ")), None);
    assert_eq!(normalize_optional_text(None), None);

    let payload = json!({
        "z": "  tail  ",
        "nested": {
            "b": "  bravo ",
            "a": null,
            "c": [" first ", {"d": " second "}],
        },
        "keep": 3,
    });

    let normalized = normalize_value(&payload);

    assert_eq!(
        normalized,
        json!({
            "keep": 3,
            "nested": {
                "a": null,
                "b": "bravo",
                "c": ["first", {"d": "second"}],
            },
            "z": "tail",
        })
    );
}

#[test]
fn parse_threats_findings_extracts_source_attribution_and_pattern() {
    let markdown =
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_multi_record.md");
    let findings = parse_threats_findings(markdown).expect("parse threats findings");

    assert_eq!(findings.len(), 1);
    let finding = &findings[0];
    assert_eq!(finding.id, "LLM-5");
    assert_eq!(finding.agentic_pattern, "none");
    let records = finding
        .source_attribution
        .as_ref()
        .expect("source attribution");
    assert_eq!(records.len(), 3);
    assert_eq!(records[0].taxonomy, "owasp");
    assert_eq!(records[0].id, "LLM05");
    assert_eq!(records[0].relationship, "primary");
}

#[test]
fn parse_threats_findings_preserves_absent_and_empty_source_attribution_semantics() {
    let absent = include_str!("../../../tests/scripts/fixtures/source_attribution/valid_absent.md");
    let empty =
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_empty_array.md");

    let absent_findings = parse_threats_findings(absent).expect("absent parse");
    assert!(absent_findings
        .iter()
        .all(|finding| finding.source_attribution.is_none()));

    let empty_findings = parse_threats_findings(empty).expect("empty parse");
    assert_eq!(
        empty_findings[0].source_attribution.as_ref().unwrap().len(),
        0
    );
}

#[test]
fn parse_threats_findings_skips_rows_with_missing_ids() {
    let markdown = r#"
## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
| --- | --- | --- | --- | --- |
| | API | Missing identifier | High | Fix it |
| S-1 | UI | Valid finding | Low | Fix it |
"#;

    let findings = parse_threats_findings(markdown).expect("parse findings");

    assert_eq!(findings.len(), 1);
    assert_eq!(findings[0].id, "S-1");
    assert_eq!(findings[0].component, "UI");
}

#[test]
fn validate_source_attribution_rejects_invalid_taxonomy_and_relationship() {
    let invalid_taxonomy =
        include_str!("../../../tests/scripts/fixtures/source_attribution/invalid_taxonomy.md");
    let invalid_relationship =
        include_str!("../../../tests/scripts/fixtures/source_attribution/invalid_relationship.md");

    assert!(parse_threats_findings(invalid_taxonomy).is_err());

    assert!(parse_threats_findings(invalid_relationship).is_err());
}

#[test]
fn validate_source_attribution_reports_unknown_catalog_ids() {
    let invalid_id =
        include_str!("../../../tests/scripts/fixtures/source_attribution/invalid_id.md");
    let findings = parse_threats_findings(invalid_id).expect("parse invalid id fixture");
    let taxonomy_dir = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|p| p.parent())
        .expect("repo root")
        .join("schemas/taxonomy");

    let errors = validate_source_attribution(&findings, &taxonomy_dir);
    assert_eq!(errors.len(), 1);
    assert_eq!(errors[0].finding_id, "E-2");
    assert_eq!(errors[0].record.taxonomy, "owasp");
    assert!(errors[0].target_yaml_path.ends_with("owasp.yaml"));
}

#[test]
fn source_attribution_contract_is_rust_native() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/scripts/test_source_attribution.py")
            .exists(),
        "source-attribution coverage should live in Rust tests, not pytest"
    );

    let valid_single =
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_single_record.md");
    let single_findings = parse_threats_findings(valid_single).expect("parse single fixture");
    assert_eq!(single_findings.len(), 1);
    assert_eq!(single_findings[0].id, "S-1");
    assert_eq!(
        single_findings[0].source_attribution.as_ref().unwrap()[0].relationship,
        "primary"
    );

    let valid_multi =
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_multi_record.md");
    let multi_findings = parse_threats_findings(valid_multi).expect("parse multi fixture");
    let records = multi_findings[0].source_attribution.as_ref().unwrap();
    assert_eq!(records.len(), 3);
    assert_eq!(records[0].taxonomy, "owasp");
    assert_eq!(records[1].taxonomy, "cwe");
    assert_eq!(records[2].taxonomy, "mitre-atlas");

    let mut all_valid_findings = Vec::new();
    for fixture in [
        valid_single,
        valid_multi,
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_absent.md"),
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_empty_array.md"),
    ] {
        all_valid_findings.extend(parse_threats_findings(fixture).expect("parse valid fixture"));
    }

    let taxonomy_dir = root.join("schemas/taxonomy");
    assert!(validate_source_attribution(&all_valid_findings, &taxonomy_dir).is_empty());
}

#[test]
fn parse_component_asset_map_matches_retired_pytest_contract() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/scripts/test_asset_sensitivity_tags.py")
            .exists(),
        "asset-sensitivity tag parser coverage should live in Rust tests, not pytest"
    );

    assert_eq!(
        VALID_ASSET_TAGS,
        ["pii", "phi", "auth", "secrets", "financial", "safety"]
    );
    assert!(parse_component_asset_map("").is_empty());
    assert!(parse_component_asset_map("# Architecture\nNo mermaid here.").is_empty());
    assert!(parse_component_asset_map(
        "```mermaid\nflowchart TD\n    User[User]\n    DB[(Database)]\n```"
    )
    .is_empty());

    let bracket_shapes = parse_component_asset_map(
        r#"```mermaid
    Vault["Secrets Vault<br/>[asset:secrets]"]
    DB[("Postgres DB<br/>[asset:pii,auth]")]
    Svc[["Payment Service<br/>[asset:financial]"]]
```"#,
    );
    assert_eq!(
        tag_values(&bracket_shapes, "Secrets Vault"),
        Some(vec!["secrets"])
    );
    assert_eq!(
        tag_values(&bracket_shapes, "Postgres DB"),
        Some(vec!["auth", "pii"])
    );
    assert_eq!(
        tag_values(&bracket_shapes, "Payment Service"),
        Some(vec!["financial"])
    );

    assert_eq!(
        parse_component_asset_map(
            r#"```mermaid
    SecretsVault["[asset:secrets]"]
```"#
        )
        .get("SecretsVault")
        .map(|tags| tags.iter().map(String::as_str).collect::<Vec<_>>()),
        Some(vec!["secrets"])
    );
    assert_eq!(
        parse_component_asset_map(
            r#"```mermaid
    DB1["Store One<br>[asset:pii]"]
    DB2["Store Two<br />[asset:phi]"]
    DB3["Store Three<br/>[asset:auth]"]
```"#
        )
        .keys()
        .cloned()
        .collect::<Vec<_>>(),
        vec!["Store One", "Store Three", "Store Two"]
    );
    assert_eq!(
        parse_component_asset_map(
            r#"```mermaid
    DB["Database<br/>[asset: secrets,PII,auth,pii ]"]
```"#
        )
        .get("Database")
        .map(|tags| tags.iter().map(String::as_str).collect::<Vec<_>>()),
        Some(vec!["auth", "pii", "secrets"])
    );
    assert_eq!(
        parse_component_asset_map(
            r#"```mermaid
    A["A<br/>[asset:pii]"]
    B["B<br/>[asset:phi]"]
    C["C<br/>[asset:auth]"]
    D["D<br/>[asset:secrets]"]
    E["E<br/>[asset:financial]"]
    F["F<br/>[asset:safety]"]
```"#
        )
        .values()
        .flatten()
        .cloned()
        .collect::<std::collections::BTreeSet<_>>(),
        VALID_ASSET_TAGS
            .iter()
            .map(ToString::to_string)
            .collect::<std::collections::BTreeSet<_>>()
    );
    assert_eq!(
        parse_component_asset_map(
            r#"```mermaid
    DB["Database<br/>[asset:pii,unknown_tag,auth]"]
    Cache["Cache<br/>[asset:foo,bar,baz]"]
```"#
        )
        .get("Database")
        .map(|tags| tags.iter().map(String::as_str).collect::<Vec<_>>()),
        Some(vec!["auth", "pii"])
    );
    assert!(!parse_component_asset_map(
        r#"```mermaid
    Cache["Cache<br/>[asset:foo,bar,baz]"]
```"#
    )
    .contains_key("Cache"));

    let duplicates = parse_component_asset_map(
        r#"```mermaid
    DB["Database<br/>[asset:pii]"]
    DB["Database<br/>[asset:auth]"]
```"#,
    );
    assert_eq!(
        tag_values(&duplicates, "Database"),
        Some(vec!["auth", "pii"])
    );

    assert_eq!(
        parse_component_asset_map(
            r#"# Architecture
Our database carries [asset:pii] tags but this is prose.

```mermaid
    DB["Real DB<br/>[asset:auth]"]
```

Trailing prose with [asset:financial] also ignored.
"#
        )
        .get("Real DB")
        .map(|tags| tags.iter().map(String::as_str).collect::<Vec<_>>()),
        Some(vec!["auth"])
    );
    assert_eq!(
        parse_component_asset_map(
            r#"flowchart TD
    DB["Database<br/>[asset:pii]"]
    User --> DB
"#
        )
        .get("Database")
        .map(|tags| tags.iter().map(String::as_str).collect::<Vec<_>>()),
        Some(vec!["pii"])
    );

    let multi_fence = parse_component_asset_map(
        r#"```mermaid
    DB1["Store One<br/>[asset:pii]"]
```

Some prose between blocks.

```mermaid
    DB2["Store Two<br/>[asset:auth]"]
```"#,
    );
    assert_eq!(tag_values(&multi_fence, "Store One"), Some(vec!["pii"]));
    assert_eq!(tag_values(&multi_fence, "Store Two"), Some(vec!["auth"]));

    let worked_example = root.join("examples/agentic-app/architecture-with-asset-tags.md");
    if worked_example.is_file() {
        let parsed = parse_component_asset_map(
            &std::fs::read_to_string(worked_example).expect("read asset worked example"),
        );
        assert_eq!(
            tag_values(&parsed, "Knowledge Base"),
            Some(vec!["phi", "pii"])
        );
        assert_eq!(tag_values(&parsed, "Audit Logger"), Some(vec!["auth"]));
        assert_eq!(
            tag_values(&parsed, "Long-Running Learning Loop"),
            Some(vec!["safety"])
        );
        assert_eq!(
            tag_values(&parsed, "Clinical Advisory Sub-Agent"),
            Some(vec!["phi"])
        );
    }
}

#[test]
fn compute_has_source_attribution_is_true_only_for_non_empty_attribution() {
    let absent = include_str!("../../../tests/scripts/fixtures/source_attribution/valid_absent.md");
    let empty =
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_empty_array.md");
    let present =
        include_str!("../../../tests/scripts/fixtures/source_attribution/valid_single_record.md");

    let absent_findings = parse_threats_findings(absent).expect("absent parse");
    let empty_findings = parse_threats_findings(empty).expect("empty parse");
    let present_findings = parse_threats_findings(present).expect("present parse");

    assert!(!compute_has_source_attribution(&absent_findings));
    assert!(!compute_has_source_attribution(&empty_findings));
    assert!(compute_has_source_attribution(&present_findings));
}

#[test]
fn compute_delta_counts_trims_case_and_ignores_unknown_statuses() {
    let findings = vec![
        ThreatFinding {
            delta_status: Some("new".into()),
            ..Default::default()
        },
        ThreatFinding {
            delta_status: Some("NEW".into()),
            ..Default::default()
        },
        ThreatFinding {
            delta_status: Some("  updated ".into()),
            ..Default::default()
        },
        ThreatFinding {
            delta_status: Some("unchanged".into()),
            ..Default::default()
        },
        ThreatFinding {
            delta_status: Some("unknown".into()),
            ..Default::default()
        },
        ThreatFinding {
            delta_status: Some("".into()),
            ..Default::default()
        },
    ];

    let resolved = vec![ResolvedFinding {
        id: "R-1".into(),
        ..Default::default()
    }];

    let counts = compute_delta_counts(&findings, &resolved);

    assert_eq!(counts.get("new"), Some(&2));
    assert_eq!(counts.get("updated"), Some(&1));
    assert_eq!(counts.get("unchanged"), Some(&1));
    assert_eq!(counts.get("resolved"), Some(&1));
}

fn workspace_root() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn temp_dir() -> std::path::PathBuf {
    let mut root = std::env::temp_dir();
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("system time before UNIX_EPOCH")
        .as_nanos();
    let counter = PARSER_TEMP_DIR_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    root.push(format!("tachi-core-parsers-{stamp}-{counter}"));
    std::fs::create_dir_all(&root).expect("create temp dir");
    root
}

fn write_text(path: &std::path::Path, contents: &str) {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent).expect("create parent");
    }
    std::fs::write(path, contents).expect("write file");
}

fn tag_values<'a>(
    map: &'a std::collections::BTreeMap<String, Vec<String>>,
    key: &str,
) -> Option<Vec<&'a str>> {
    map.get(key)
        .map(|tags| tags.iter().map(String::as_str).collect::<Vec<_>>())
}
