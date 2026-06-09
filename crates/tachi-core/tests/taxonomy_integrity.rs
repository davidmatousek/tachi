use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};

const CATALOG_FILENAMES: &[&str] = &[
    "owasp.yaml",
    "mitre-attack.yaml",
    "mitre-atlas.yaml",
    "nist-ai-rmf.yaml",
    "cwe.yaml",
    "tachi-control-category.yaml",
    "tachi-stride-ai-category.yaml",
];

const TAXONOMIES: &[&str] = &[
    "owasp",
    "mitre-attack",
    "mitre-atlas",
    "nist-ai-rmf",
    "cwe",
    "tachi-control-category",
    "tachi-stride-ai-category",
];

const EDGE_TYPES: &[&str] = &["primary", "related", "superseded"];
const CONFIDENCE_VALUES: &[&str] = &["high", "medium", "low"];
const PRIMARY_EDGE_FLOOR: usize = 500;

#[derive(Debug)]
struct CatalogRecord {
    id: String,
    body: Vec<String>,
}

#[derive(Debug)]
struct CrosswalkEdge {
    source_taxonomy: String,
    source_id: String,
    target_taxonomy: String,
    target_id: String,
    edge_type: String,
    confidence: String,
    citation: String,
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn taxonomy_dir(root: &Path) -> PathBuf {
    root.join("schemas/taxonomy")
}

fn parse_catalog_records(text: &str) -> Vec<CatalogRecord> {
    let mut records = Vec::new();
    let mut current_id: Option<String> = None;
    let mut current_body = Vec::new();

    for line in text.lines() {
        if let Some(rest) = line.trim().strip_prefix("- id: ") {
            if let Some(id) = current_id.replace(rest.trim().to_string()) {
                records.push(CatalogRecord {
                    id,
                    body: std::mem::take(&mut current_body),
                });
            }
        } else if current_id.is_some() {
            current_body.push(line.to_string());
        }
    }

    if let Some(id) = current_id {
        records.push(CatalogRecord {
            id,
            body: current_body,
        });
    }

    records
}

fn scalar_value(line: &str, key: &str) -> Option<String> {
    line.trim()
        .strip_prefix(key)
        .map(|value| value.trim().trim_matches('"').to_string())
}

fn contains_key(record: &CatalogRecord, key: &str) -> bool {
    record
        .body
        .iter()
        .any(|line| line.trim_start().starts_with(key))
}

fn record_url(record: &CatalogRecord) -> Option<String> {
    record
        .body
        .iter()
        .find_map(|line| scalar_value(line, "url:"))
}

fn is_url_or_existing_file(root: &Path, value: &str) -> bool {
    value.starts_with("http://") || value.starts_with("https://") || root.join(value).is_file()
}

fn nist_sort_key(id: &str) -> (String, u32, u32, String) {
    let (function, number) = id.split_once(' ').unwrap_or((id, ""));
    let (major, minor) = number.split_once('.').unwrap_or((number, "0"));
    (
        function.to_string(),
        major.parse().unwrap_or(0),
        minor.parse().unwrap_or(0),
        id.to_string(),
    )
}

fn parse_crosswalk_edges(text: &str) -> Vec<CrosswalkEdge> {
    let mut edges = Vec::new();
    let mut source_taxonomy = String::new();
    let mut source_id = String::new();
    let mut target_taxonomy = String::new();
    let mut target_id = String::new();
    let mut edge_type = String::new();
    let mut confidence = String::new();
    let mut citation = String::new();
    let mut endpoint: Option<&str> = None;

    for line in text.lines() {
        let trimmed = line.trim();
        match trimmed {
            "- source:" => {
                if !source_taxonomy.is_empty() {
                    edges.push(CrosswalkEdge {
                        source_taxonomy: std::mem::take(&mut source_taxonomy),
                        source_id: std::mem::take(&mut source_id),
                        target_taxonomy: std::mem::take(&mut target_taxonomy),
                        target_id: std::mem::take(&mut target_id),
                        edge_type: std::mem::take(&mut edge_type),
                        confidence: std::mem::take(&mut confidence),
                        citation: std::mem::take(&mut citation),
                    });
                }
                endpoint = Some("source");
            }
            "target:" => endpoint = Some("target"),
            _ => {
                if let Some(value) = scalar_value(trimmed, "taxonomy:") {
                    match endpoint {
                        Some("source") => source_taxonomy = value,
                        Some("target") => target_taxonomy = value,
                        _ => {}
                    }
                } else if let Some(value) = scalar_value(trimmed, "id:") {
                    match endpoint {
                        Some("source") => source_id = value,
                        Some("target") => target_id = value,
                        _ => {}
                    }
                } else if let Some(value) = scalar_value(trimmed, "edge_type:") {
                    edge_type = value;
                    endpoint = None;
                } else if let Some(value) = scalar_value(trimmed, "confidence:") {
                    confidence = value;
                } else if let Some(value) = scalar_value(trimmed, "citation:") {
                    citation = value;
                }
            }
        }
    }

    if !source_taxonomy.is_empty() {
        edges.push(CrosswalkEdge {
            source_taxonomy,
            source_id,
            target_taxonomy,
            target_id,
            edge_type,
            confidence,
            citation,
        });
    }

    edges
}

#[test]
fn taxonomy_integrity_contract_is_rust_native() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/schemas/test_taxonomy_integrity.py")
            .exists(),
        "taxonomy integrity coverage should live in Rust tests, not pytest"
    );

    let mut catalog_ids: BTreeMap<&str, BTreeSet<String>> = BTreeMap::new();

    for filename in CATALOG_FILENAMES {
        let path = taxonomy_dir(&root).join(filename);
        let text = fs::read_to_string(&path).unwrap_or_else(|err| {
            panic!(
                "expected taxonomy catalog {} to load: {err}",
                path.display()
            )
        });
        let records = parse_catalog_records(&text);
        assert!(
            !records.is_empty(),
            "{filename}: expected non-empty records"
        );

        let mut seen_ids = BTreeSet::new();
        let mut ids = Vec::new();
        for record in &records {
            assert!(
                seen_ids.insert(record.id.clone()),
                "{filename}: duplicate id {:?}",
                record.id
            );
            ids.push(record.id.clone());

            for key in ["full_id:", "name:", "url:"] {
                assert!(
                    contains_key(record, key),
                    "{filename}: {} missing {key}",
                    record.id
                );
            }

            if *filename == "cwe.yaml" {
                assert!(
                    !contains_key(record, "cwe_refs:"),
                    "{filename}: {} must not carry cwe_refs",
                    record.id
                );
            } else {
                assert!(
                    contains_key(record, "cwe_refs:"),
                    "{filename}: {} missing cwe_refs",
                    record.id
                );
            }

            let url = record_url(record).expect("url checked above");
            assert!(
                is_url_or_existing_file(&root, &url),
                "{filename}: {} url {url:?} is not URL-shaped or an existing file",
                record.id
            );
        }

        let mut expected = ids.clone();
        if *filename == "nist-ai-rmf.yaml" {
            expected.sort_by_key(|id| nist_sort_key(id));
        } else {
            expected.sort();
        }
        assert_eq!(ids, expected, "{filename}: records should be sorted by id");

        catalog_ids.insert(filename.trim_end_matches(".yaml"), seen_ids);
    }

    let crosswalk_path = taxonomy_dir(&root).join("crosswalk.yaml");
    let crosswalk = fs::read_to_string(&crosswalk_path).unwrap_or_else(|err| {
        panic!(
            "expected taxonomy crosswalk {} to load: {err}",
            crosswalk_path.display()
        )
    });
    let edges = parse_crosswalk_edges(&crosswalk);
    assert!(
        !edges.is_empty(),
        "crosswalk.yaml: expected non-empty edges"
    );

    let mut seen_edges = BTreeSet::new();
    let mut primary_count = 0;
    for edge in &edges {
        assert!(TAXONOMIES.contains(&edge.source_taxonomy.as_str()));
        assert!(TAXONOMIES.contains(&edge.target_taxonomy.as_str()));
        assert!(EDGE_TYPES.contains(&edge.edge_type.as_str()));
        assert!(CONFIDENCE_VALUES.contains(&edge.confidence.as_str()));
        assert!(
            !edge.citation.is_empty() && is_url_or_existing_file(&root, edge.citation.as_str()),
            "crosswalk.yaml: citation {:?} is not URL-shaped or an existing file",
            edge.citation
        );

        assert!(
            catalog_ids
                .get(edge.source_taxonomy.as_str())
                .is_some_and(|ids| ids.contains(&edge.source_id)),
            "crosswalk.yaml: source {:?}:{:?} not found",
            edge.source_taxonomy,
            edge.source_id
        );
        assert!(
            catalog_ids
                .get(edge.target_taxonomy.as_str())
                .is_some_and(|ids| ids.contains(&edge.target_id)),
            "crosswalk.yaml: target {:?}:{:?} not found",
            edge.target_taxonomy,
            edge.target_id
        );

        assert!(
            seen_edges.insert((
                edge.source_taxonomy.as_str(),
                edge.source_id.as_str(),
                edge.target_taxonomy.as_str(),
                edge.target_id.as_str(),
                edge.edge_type.as_str(),
            )),
            "crosswalk.yaml: duplicate edge {edge:?}"
        );

        if edge.edge_type == "primary" {
            primary_count += 1;
        }
    }

    assert!(
        primary_count >= PRIMARY_EDGE_FLOOR,
        "crosswalk.yaml: {primary_count} primary edges below floor of {PRIMARY_EDGE_FLOOR}"
    );
}
