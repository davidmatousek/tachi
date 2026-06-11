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

fn extract_first_yaml_block(content: &str) -> Value {
    let lines = content.lines();
    let mut in_block = false;
    let mut yaml = String::new();
    for line in lines {
        if !in_block {
            if line.trim() == "```yaml" {
                in_block = true;
            }
            continue;
        }
        if line.trim() == "```" {
            break;
        }
        yaml.push_str(line);
        yaml.push('\n');
    }
    serde_yaml::from_str(&yaml).expect("parse yaml block")
}

fn joined_refs(path: &Path) -> String {
    let yaml = read_yaml(path);
    let refs = yaml
        .get("references")
        .and_then(Value::as_sequence)
        .expect("references array");
    refs.iter()
        .map(|item| item.as_str().expect("reference string"))
        .collect::<Vec<_>>()
        .join(" | ")
}

fn slice_section(content: &str, start_header: &str, terminators: &[&str]) -> String {
    let start_idx = content
        .find(start_header)
        .unwrap_or_else(|| panic!("missing section header {start_header:?}"));
    let mut end_idx = content.len();
    for term in terminators {
        if let Some(candidate) =
            content[start_idx + start_header.len()..].find(&format!("\n{term}"))
        {
            let candidate = start_idx + start_header.len() + candidate;
            if candidate < end_idx {
                end_idx = candidate;
            }
        }
    }
    content[start_idx..end_idx].to_string()
}

const DOS_AGENT: &str = ".claude/agents/tachi/denial-of-service.md";
const MODEL_THEFT_AGENT: &str = ".claude/agents/tachi/model-theft.md";
const DOS_COMPANION: &str =
    ".claude/skills/tachi-denial-of-service/references/detection-patterns.md";
const MODEL_THEFT_COMPANION: &str =
    ".claude/skills/tachi-model-theft/references/detection-patterns.md";
const CAT_12_FIXTURE: &str = "tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_12_inference_flooding_finding.yaml";
const CAT_13_FIXTURE: &str = "tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_13_context_window_latency_finding.yaml";
const CAT_10_FIXTURE: &str = "tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_10_cost_amplification_finding.yaml";
const CAT_11_FIXTURE: &str = "tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_11_denial_of_wallet_finding.yaml";
const CAT_11_FREEMIUM_FIXTURE: &str = "tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_11_critical_floor_freemium_finding.yaml";

#[test]
fn llm10_unbounded_consumption_contract_is_rust_native() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_llm10_unbounded_consumption_enrichment.py")
            .exists(),
        "LLM10 bundle coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn line_caps_are_preserved_across_all_f5_artifacts() {
    let root = workspace_root();
    assert!(read_text(&root.join(DOS_AGENT)).lines().count() <= 120);
    assert!(read_text(&root.join(MODEL_THEFT_AGENT)).lines().count() <= 150);
}

#[test]
fn enriched_files_do_not_reference_maestro() {
    let root = workspace_root();
    for relative in [
        DOS_AGENT,
        MODEL_THEFT_AGENT,
        DOS_COMPANION,
        MODEL_THEFT_COMPANION,
    ] {
        assert!(
            !read_text(&root.join(relative))
                .to_lowercase()
                .contains("maestro"),
            "{relative} must be MAESTRO-free"
        );
    }
}

#[test]
fn mandatory_read_directives_are_preserved() {
    let root = workspace_root();
    for relative in [DOS_AGENT, MODEL_THEFT_AGENT] {
        assert_eq!(
            read_text(&root.join(relative))
                .matches("**MANDATORY**: Read")
                .count(),
            1
        );
    }
}

#[test]
fn companion_pattern_categories_are_present() {
    let root = workspace_root();
    let dos = read_text(&root.join(DOS_COMPANION));
    assert!(dos.contains("## Pattern Category 12: LLM Inference-Request Flooding"));
    assert!(dos.contains("## Pattern Category 13: Context-Window Exhaustion"));

    let model_theft = read_text(&root.join(MODEL_THEFT_COMPANION));
    assert!(model_theft.contains("## Pattern Category 10: Cost Amplification"));
    assert!(model_theft.contains("## Pattern Category 11: Denial-of-Wallet"));
}

#[test]
fn pattern_category_disambiguation_sections_are_present() {
    let root = workspace_root();
    let dos = read_text(&root.join(DOS_COMPANION));
    let dos_section = slice_section(&dos, "## Pattern Category Disambiguation", &["## "]);
    assert!(dos_section.contains("Pattern Category 9"));
    assert!(
        dos_section.contains("Pattern Category 12")
            || dos_section.contains("Pattern Categories 12 + 13")
    );

    let model_theft = read_text(&root.join(MODEL_THEFT_COMPANION));
    let model_theft_section =
        slice_section(&model_theft, "## Pattern Category Disambiguation", &["## "]);
    assert!(model_theft_section.contains("Pattern Category 6"));
    assert!(
        model_theft_section.contains("Pattern Category 10")
            || model_theft_section.contains("Pattern Categories 10 + 11")
    );
}

#[test]
fn t1496_is_prose_only_in_model_theft() {
    let content = read_text(&workspace_root().join(MODEL_THEFT_COMPANION));
    assert!(content.contains("T1496"));
    let primary_sources = slice_section(&content, "## Primary Sources", &["## ", "# "]);
    assert!(!primary_sources.contains("T1496"));
}

#[test]
fn fixture_references_arrays_are_catalog_resolvable() {
    let root = workspace_root();
    assert!(joined_refs(&root.join(CAT_12_FIXTURE)).contains("OWASP LLM10:2025"));
    assert!(joined_refs(&root.join(CAT_13_FIXTURE)).contains("OWASP LLM10:2025"));
    assert!(joined_refs(&root.join(CAT_10_FIXTURE)).contains("OWASP LLM10:2025"));
    assert!(joined_refs(&root.join(CAT_11_FIXTURE)).contains("OWASP LLM10:2025"));
    assert!(joined_refs(&root.join(CAT_11_FREEMIUM_FIXTURE)).contains("OWASP LLM10:2025"));
}

#[test]
fn llm10_references_do_not_include_t1496() {
    let root = workspace_root();
    for relative in [CAT_10_FIXTURE, CAT_11_FIXTURE, CAT_11_FREEMIUM_FIXTURE] {
        assert!(!joined_refs(&root.join(relative)).contains("T1496"));
    }
}

#[test]
fn agent_metadata_includes_llm10() {
    let root = workspace_root();
    for relative in [DOS_AGENT, MODEL_THEFT_AGENT] {
        let yaml = extract_first_yaml_block(&read_text(&root.join(relative)));
        let metadata = yaml
            .get("owasp_references")
            .and_then(Value::as_sequence)
            .expect("owasp_references");
        let joined = metadata
            .iter()
            .map(|item| item.as_str().expect("reference string"))
            .collect::<Vec<_>>()
            .join(" | ");
        assert!(joined.contains("LLM10:2025"));
    }
}

#[test]
fn detection_workflow_step_5_references_llm10() {
    let root = workspace_root();
    for relative in [DOS_AGENT, MODEL_THEFT_AGENT] {
        let content = read_text(&root.join(relative));
        let step5 = content
            .lines()
            .find(|line| line.starts_with("5. ") && line.contains("references"))
            .expect("step 5 line");
        assert!(step5.contains("LLM10"));
    }
}
