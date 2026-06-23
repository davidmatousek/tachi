use std::fs;
use std::path::Path;

use tachi_core::coverage_attestation::{
    build_per_framework_aggregates_from_store, build_per_framework_aggregates_in_dir,
    load_framework_yaml_in_scope_record_counts_from_dir, load_framework_yaml_records_from_dir,
};
use tachi_core::parsers::{SourceAttributionRecord, ThreatFinding};

struct FakeTaxonomyStore {
    records: std::collections::BTreeMap<(String, bool), Vec<tachi_core::coverage_attestation::FrameworkRecord>>,
}

impl tachi_core::coverage_attestation::TaxonomyStore for FakeTaxonomyStore {
    fn load_framework_records(
        &self,
        framework_name: &str,
        in_scope_only: bool,
    ) -> Vec<tachi_core::coverage_attestation::FrameworkRecord> {
        self.records
            .get(&(framework_name.to_string(), in_scope_only))
            .cloned()
            .unwrap_or_default()
    }
}

struct DirTaxonomyStore {
    taxonomy_dir: std::path::PathBuf,
}

impl tachi_core::coverage_attestation::TaxonomyStore for DirTaxonomyStore {
    fn load_framework_records(
        &self,
        framework_name: &str,
        in_scope_only: bool,
    ) -> Vec<tachi_core::coverage_attestation::FrameworkRecord> {
        load_framework_yaml_records_from_dir(&self.taxonomy_dir, framework_name, in_scope_only)
    }
}

fn temp_root(prefix: &str) -> std::path::PathBuf {
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("clock")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{nanos}"))
}

fn write_taxonomy_file(dir: &Path, name: &str, content: &str) {
    fs::create_dir_all(dir).expect("create taxonomy dir");
    fs::write(dir.join(format!("{name}.yaml")), content).expect("write taxonomy file");
}

fn finding(id: &str, taxonomy: &str, ref_id: &str, relationship: &str) -> ThreatFinding {
    ThreatFinding {
        id: id.to_string(),
        component: String::from("Component"),
        threat: String::from("Threat"),
        likelihood: String::from("—"),
        impact: String::from("—"),
        risk_level: String::from("High"),
        mitigation: String::from("Mitigation"),
        agentic_pattern: String::from("none"),
        delta_status: None,
        source_attribution: Some(vec![SourceAttributionRecord {
            taxonomy: taxonomy.to_string(),
            id: ref_id.to_string(),
            relationship: relationship.to_string(),
        }]),
    }
}

#[test]
fn load_framework_yaml_records_from_dir_filters_oos_and_treats_missing_field_as_in_scope() {
    let root = temp_root("tachi-coverage-attestation-in-scope");
    let taxonomy_dir = root.join("schemas/taxonomy");
    write_taxonomy_file(
        &taxonomy_dir,
        "owasp",
        r#"- id: A01
  out_of_scope: false
- id: A02
  out_of_scope: true
- id: A03
"#,
    );

    let raw = load_framework_yaml_records_from_dir(&taxonomy_dir, "owasp", false);
    let in_scope = load_framework_yaml_records_from_dir(&taxonomy_dir, "owasp", true);
    let in_scope_counts = load_framework_yaml_in_scope_record_counts_from_dir(&taxonomy_dir);

    assert_eq!(raw.len(), 3);
    assert_eq!(in_scope.len(), 2);
    assert_eq!(in_scope_counts.get("owasp").copied(), Some(2));

    let _ = fs::remove_dir_all(root);
}

#[test]
fn build_per_framework_aggregates_in_dir_uses_in_scope_denominator() {
    let root = temp_root("tachi-coverage-attestation-aggregate");
    let taxonomy_dir = root.join("schemas/taxonomy");
    for framework in ["owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"] {
        write_taxonomy_file(
            &taxonomy_dir,
            framework,
            r#"- id: X01
  out_of_scope: false
- id: X02
  out_of_scope: true
"#,
        );
    }

    let findings = vec![
        finding("F-1", "owasp", "X01", "primary"),
        finding("F-2", "owasp", "X02", "related"),
    ];

    let aggregates = build_per_framework_aggregates_in_dir(&taxonomy_dir, &findings);

    assert_eq!(aggregates.len(), 5);
    let owasp = aggregates
        .iter()
        .find(|aggregate| aggregate.framework == "owasp")
        .expect("owasp aggregate");
    assert_eq!(owasp.yaml_record_count, 2);
    assert_eq!(owasp.in_scope_yaml_record_count, 1);
    assert_eq!(owasp.covered_count, 1);
    assert_eq!(owasp.partial_count, 0);
    assert_eq!(owasp.gap_count, 0);
    assert_eq!(owasp.coverage_percentage, "100.00%");

    let _ = fs::remove_dir_all(root);
}

#[test]
fn build_per_framework_aggregates_from_store_uses_fake_taxonomy_provider() {
    let mut records = std::collections::BTreeMap::new();
    records.insert(
        (String::from("owasp"), false),
        vec![
            tachi_core::coverage_attestation::FrameworkRecord::new("A01", false),
            tachi_core::coverage_attestation::FrameworkRecord::new("A02", true),
        ],
    );
    records.insert(
        (String::from("owasp"), true),
        vec![tachi_core::coverage_attestation::FrameworkRecord::new("A01", false)],
    );
    let store = FakeTaxonomyStore { records };
    let findings = vec![finding("F-1", "owasp", "A01", "primary")];

    let aggregates =
        tachi_core::coverage_attestation::build_per_framework_aggregates_from_store(
            &store, &findings,
        );

    let owasp = aggregates
        .iter()
        .find(|aggregate| aggregate.framework == "owasp")
        .expect("owasp aggregate");
    assert_eq!(owasp.yaml_record_count, 2);
    assert_eq!(owasp.in_scope_yaml_record_count, 1);
    assert_eq!(owasp.covered_count, 1);
    assert_eq!(owasp.gap_count, 0);
}

#[test]
fn build_per_framework_aggregates_from_store_matches_dir_backed_adapter() {
    let root = temp_root("tachi-coverage-attestation-dir-adapter");
    let taxonomy_dir = root.join("schemas/taxonomy");
    write_taxonomy_file(
        &taxonomy_dir,
        "owasp",
        r#"- id: A01
  out_of_scope: false
- id: A02
  out_of_scope: true
"#,
    );

    let dir_store = DirTaxonomyStore {
        taxonomy_dir: taxonomy_dir.clone(),
    };
    let findings = vec![finding("F-1", "owasp", "A01", "primary")];

    let from_dir = build_per_framework_aggregates_in_dir(&taxonomy_dir, &findings);
    let from_store = build_per_framework_aggregates_from_store(&dir_store, &findings);

    assert_eq!(from_store, from_dir);

    let _ = fs::remove_dir_all(root);
}
