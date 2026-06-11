use std::fs;
use std::path::{Path, PathBuf};

use serde_yaml::Value;

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read_text(path: &Path) -> String {
    fs::read_to_string(path).expect("read text")
}

fn read_yaml(path: &Path) -> Value {
    serde_yaml::from_str(&read_text(path)).expect("parse yaml")
}

fn load_owasp_records() -> Vec<Value> {
    let path = workspace_root().join("schemas/taxonomy/owasp.yaml");
    read_yaml(&path)
        .as_sequence()
        .expect("owasp.yaml sequence")
        .clone()
}

fn owasp_citation_needles(id: &str) -> Vec<String> {
    if let Some(suffix) = id.strip_prefix("ASI") {
        vec![id.to_string(), format!("ASI-{suffix}")]
    } else {
        vec![id.to_string()]
    }
}

fn agent_cites_owasp(needle: &str) -> bool {
    let agents_dir = workspace_root().join(".claude/agents/tachi");
    if !agents_dir.exists() {
        return false;
    }

    let needles = owasp_citation_needles(needle);
    let entries = match fs::read_dir(&agents_dir) {
        Ok(entries) => entries,
        Err(_) => return false,
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|ext| ext.to_str()) != Some("md") {
            continue;
        }
        let contents = read_text(&path);
        if needles.iter().any(|candidate| contents.contains(candidate)) {
            return true;
        }
    }

    false
}

fn pattern_catalog_cites_owasp(needle: &str) -> bool {
    let skills_dir = workspace_root().join(".claude/skills");
    if !skills_dir.exists() {
        return false;
    }

    let needles = owasp_citation_needles(needle);
    let entries = match fs::read_dir(&skills_dir) {
        Ok(entries) => entries,
        Err(_) => return false,
    };

    for entry in entries.flatten() {
        let path = entry.path().join("references/detection-patterns.md");
        if path.exists() {
            let contents = read_text(&path);
            if needles.iter().any(|candidate| contents.contains(candidate)) {
                return true;
            }
        }
    }

    false
}

fn grep_pattern_file(skill_name: &str, needle: &str) -> bool {
    let path = workspace_root()
        .join(".claude/skills")
        .join(skill_name)
        .join("references/detection-patterns.md");
    if !path.exists() {
        return false;
    }

    let contents = read_text(&path);
    owasp_citation_needles(needle)
        .iter()
        .any(|candidate| contents.contains(candidate))
}

#[test]
fn coverage_attestation_audit_contract_is_rust_native() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_coverage_attestation_audit.py")
            .exists(),
        "coverage attestation audit coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn owasp_yaml_loads_sixty_records_with_required_audit_fields() {
    let records = load_owasp_records();
    assert_eq!(
        records.len(),
        60,
        "owasp.yaml must carry exactly 60 records"
    );

    for (index, record) in records.iter().enumerate() {
        let map = record.as_mapping().expect("owasp record map");
        for key in ["id", "full_id", "name", "url", "cwe_refs"] {
            assert!(
                map.contains_key(Value::String(key.to_string())),
                "OWASP record idx={index} missing required field {key}"
            );
        }

        let out_of_scope = map
            .get(Value::String("out_of_scope".to_string()))
            .expect("out_of_scope field");
        assert!(
            out_of_scope.is_bool(),
            "OWASP record idx={index} out_of_scope must be bool"
        );

        let rationale = map
            .get(Value::String("out_of_scope_rationale".to_string()))
            .expect("out_of_scope_rationale field");
        assert!(
            rationale.is_string(),
            "OWASP record idx={index} out_of_scope_rationale must be string"
        );
    }
}

#[test]
fn every_covered_owasp_has_agent_citation() {
    let records = load_owasp_records();

    for record in records {
        let map = record.as_mapping().expect("owasp record map");
        let out_of_scope = map
            .get(Value::String("out_of_scope".to_string()))
            .and_then(Value::as_bool)
            .unwrap_or(false);
        if out_of_scope {
            continue;
        }

        let id = map
            .get(Value::String("id".to_string()))
            .and_then(Value::as_str)
            .expect("owasp id");
        assert!(
            agent_cites_owasp(id),
            "covered OWASP record {id} must be cited by at least one agent"
        );
    }
}

#[test]
fn every_covered_owasp_has_pattern_category_citation() {
    let records = load_owasp_records();

    for record in records {
        let map = record.as_mapping().expect("owasp record map");
        let out_of_scope = map
            .get(Value::String("out_of_scope".to_string()))
            .and_then(Value::as_bool)
            .unwrap_or(false);
        if out_of_scope {
            continue;
        }

        let id = map
            .get(Value::String("id".to_string()))
            .and_then(Value::as_str)
            .expect("owasp id");
        assert!(
            pattern_catalog_cites_owasp(id),
            "covered OWASP record {id} must be cited by at least one pattern catalog"
        );
    }
}

#[test]
fn partial_owasp_items_either_covered_or_explicitly_deferred() {
    for owasp_id in [
        "A05:2021",
        "A06:2021",
        "API6:2023",
        "API8:2023",
        "API9:2023",
        "API10:2023",
    ] {
        assert!(
            pattern_catalog_cites_owasp(owasp_id),
            "partial item {owasp_id} must be cited by the relevant pattern catalog"
        );
    }
}

#[test]
fn known_partial_item_closures_are_still_catalogued() {
    assert!(grep_pattern_file("tachi-privilege-escalation", "A05:2021"));
    assert!(grep_pattern_file("tachi-tampering", "A06:2021"));
    assert!(grep_pattern_file("tachi-tool-abuse", "API6:2023"));
    assert!(grep_pattern_file("tachi-privilege-escalation", "API8:2023"));
    assert!(grep_pattern_file("tachi-info-disclosure", "API9:2023"));
    assert!(grep_pattern_file("tachi-tampering", "API10:2023"));
}
