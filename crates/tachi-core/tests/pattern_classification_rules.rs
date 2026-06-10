use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};

use serde_yaml::{Mapping, Value};

use tachi_core::parsers::VALID_AGENTIC_PATTERNS;

const CANONICAL_PATTERNS: &[&str] = &[
    "agent_collusion",
    "emergent_behavior",
    "temporal_attack",
    "trust_exploitation",
    "communication_vulnerability",
    "resource_competition",
];

const DOCUMENTED_COMPONENT_TYPES: &[&str] = &[
    "fine_tuning_pipeline",
    "persistent_agent_memory",
    "long_running_learning_loop",
    "inter_agent_channel",
];

const DOCUMENTED_TOPOLOGY_INDICATORS: &[&str] = &[
    "multi_agent",
    "inter_agent_data_flow",
    "persistent_state",
    "inter_agent_channel",
];

const EXPECTED_NET_NEW_RULE_IDS: &[&str] = &["R-01", "R-02", "R-03"];

const EXPECTED_RULE_PRIORITIES: &[(&str, i64)] = &[
    ("R-01", 10),
    ("R-02", 20),
    ("R-03", 30),
    ("R-04", 40),
    ("R-05", 50),
    ("R-06", 60),
];

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn shared_reference_path() -> PathBuf {
    workspace_root()
        .join(".claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md")
}

fn finding_schema_path() -> PathBuf {
    workspace_root().join("schemas/finding.yaml")
}

fn rule_table() -> Vec<Mapping> {
    let shared_ref_text =
        fs::read_to_string(shared_reference_path()).expect("read shared reference");
    let section = shared_ref_text
        .split_once("## Section 3: Classification Rule Table")
        .map(|(_, rest)| rest)
        .expect("Section 3 heading");
    let section = section
        .split_once("\n## ")
        .map(|(body, _)| body)
        .unwrap_or(section);
    let yaml_block = section
        .split_once("```yaml")
        .map(|(_, rest)| rest)
        .and_then(|rest| rest.split_once("```").map(|(yaml, _)| yaml))
        .expect("fenced yaml rule table");
    let parsed: Value = serde_yaml::from_str(yaml_block).expect("parse rule table yaml");
    let rules = parsed
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from("rules")))
        .and_then(Value::as_sequence)
        .expect("top-level rules list");

    rules
        .iter()
        .map(|rule| rule.as_mapping().cloned().expect("rule mapping"))
        .collect()
}

fn finding_schema_enums() -> BTreeMap<String, BTreeSet<String>> {
    let schema_text = fs::read_to_string(finding_schema_path()).expect("read finding schema");
    let schema: Value = serde_yaml::from_str(&schema_text).expect("parse finding schema");
    let finding = schema
        .get("finding")
        .and_then(Value::as_mapping)
        .expect("finding schema mapping");

    let mut enums = BTreeMap::new();
    for key in ["category", "maestro_layer", "agentic_pattern"] {
        let values = finding
            .get(Value::from(key))
            .and_then(Value::as_mapping)
            .and_then(|mapping| mapping.get(Value::from("enum")))
            .and_then(Value::as_sequence)
            .expect("enum array");
        enums.insert(
            key.to_string(),
            values
                .iter()
                .map(|value| value.as_str().expect("enum string").to_string())
                .collect(),
        );
    }
    enums
}

fn rule_string(rule: &Mapping, key: &str) -> Option<String> {
    rule.get(Value::from(key))
        .and_then(Value::as_str)
        .map(ToOwned::to_owned)
}

fn rule_int(rule: &Mapping, key: &str) -> Option<i64> {
    rule.get(Value::from(key)).and_then(Value::as_i64)
}

fn rule_bool(rule: &Mapping, key: &str) -> Option<bool> {
    rule.get(Value::from(key)).and_then(Value::as_bool)
}

fn rule_mapping<'a>(rule: &'a Mapping, key: &str) -> Option<&'a Mapping> {
    rule.get(Value::from(key)).and_then(Value::as_mapping)
}

fn rule_strings(rule: &Mapping, key: &str) -> Vec<String> {
    rule.get(Value::from(key))
        .and_then(Value::as_sequence)
        .map(|values| {
            values
                .iter()
                .map(|value| value.as_str().expect("string item").to_string())
                .collect()
        })
        .unwrap_or_default()
}

fn architecture_has_strings(rule: &Mapping, key: &str) -> Vec<String> {
    let arch_has = match rule_mapping(rule, "match_conditions") {
        Some(mapping) => rule_mapping(mapping, "architecture_has"),
        None => None,
    };

    arch_has
        .and_then(|mapping| mapping.get(Value::from(key)))
        .and_then(Value::as_sequence)
        .map(|values| {
            values
                .iter()
                .map(|value| value.as_str().expect("string item").to_string())
                .collect()
        })
        .unwrap_or_default()
}

fn rule_id_order(rule: &Mapping) -> String {
    rule_string(rule, "rule_id").expect("rule_id")
}

#[test]
fn all_six_patterns_are_covered_by_at_least_one_rule() {
    let patterns_in_rules = rule_table()
        .iter()
        .filter_map(|rule| rule_string(rule, "pattern"))
        .collect::<BTreeSet<_>>();
    let expected = CANONICAL_PATTERNS
        .iter()
        .copied()
        .map(String::from)
        .collect::<BTreeSet<_>>();
    let missing = expected
        .difference(&patterns_in_rules)
        .cloned()
        .collect::<Vec<_>>();

    assert!(
        missing.is_empty(),
        "patterns missing from rule table: {missing:?}"
    );
}

#[test]
fn every_rule_has_match_conditions() {
    for rule in rule_table() {
        let rule_id = rule_string(&rule, "rule_id").unwrap_or_else(|| String::from("<missing>"));
        let match_conditions = rule_mapping(&rule, "match_conditions");
        assert!(
            match_conditions.is_some(),
            "rule {rule_id} missing match_conditions"
        );
    }
}

#[test]
fn rule_patterns_are_within_schema_enum() {
    let valid_patterns = VALID_AGENTIC_PATTERNS
        .iter()
        .copied()
        .filter(|value| *value != "none" && *value != "multiple")
        .collect::<BTreeSet<_>>();

    for rule in rule_table() {
        let rule_id = rule_string(&rule, "rule_id").unwrap_or_else(|| String::from("<missing>"));
        let pattern = rule_string(&rule, "pattern").expect("pattern");
        assert!(
            valid_patterns.contains(pattern.as_str()),
            "rule {rule_id} pattern {pattern:?} is not in the canonical enum"
        );
    }
}

#[test]
fn rule_match_conditions_use_documented_tokens_only() {
    let schema_enums = finding_schema_enums();
    let valid_categories = schema_enums.get("category").expect("category enum");
    let valid_layers = schema_enums
        .get("maestro_layer")
        .expect("maestro_layer enum");

    for rule in rule_table() {
        let rule_id = rule_string(&rule, "rule_id").unwrap_or_else(|| String::from("<missing>"));
        let match_conditions = rule_mapping(&rule, "match_conditions").expect("match_conditions");
        for value in rule_strings(match_conditions, "category_in") {
            assert!(
                valid_categories.contains(value.as_str()),
                "rule {rule_id} category_in token {value:?} is not in schemas/finding.yaml"
            );
        }
        for value in rule_strings(match_conditions, "maestro_layer_in") {
            assert!(
                valid_layers.contains(value.as_str()),
                "rule {rule_id} maestro_layer_in token {value:?} is not in schemas/finding.yaml"
            );
        }
        for value in architecture_has_strings(&rule, "component_type") {
            assert!(
                DOCUMENTED_COMPONENT_TYPES.contains(&value.as_str()),
                "rule {rule_id} undocumented component_type token {value:?}"
            );
        }
        for value in architecture_has_strings(&rule, "topology") {
            assert!(
                DOCUMENTED_TOPOLOGY_INDICATORS.contains(&value.as_str()),
                "rule {rule_id} undocumented topology token {value:?}"
            );
        }
    }
}

#[test]
fn generation_flags_and_templates_match_the_reference_contract() {
    let rules = rule_table();
    let generating = rules
        .iter()
        .filter(|rule| rule_bool(rule, "generates_finding_when_no_match").unwrap_or(false))
        .map(|rule| rule_string(rule, "rule_id").expect("rule_id"))
        .collect::<BTreeSet<_>>();

    let expected_generating = EXPECTED_NET_NEW_RULE_IDS
        .iter()
        .copied()
        .map(String::from)
        .collect::<BTreeSet<_>>();
    assert_eq!(generating, expected_generating, "unexpected net-new rules");

    for rule in rules {
        let rule_id = rule_string(&rule, "rule_id").unwrap_or_else(|| String::from("<missing>"));
        assert!(
            rule.get(Value::from("generates_finding_when_no_match"))
                .is_some(),
            "rule {rule_id} missing generates_finding_when_no_match"
        );
        if rule_bool(&rule, "generates_finding_when_no_match").unwrap_or(false) {
            let template = rule_string(&rule, "generation_template").expect("generation_template");
            assert!(
                !template.trim().is_empty(),
                "rule {rule_id} has empty template"
            );
            assert!(
                template.contains('{') && template.contains('}'),
                "rule {rule_id} template should contain at least one placeholder"
            );
        }
    }
}

#[test]
fn non_generating_rules_may_omit_templates() {
    let rules = rule_table();
    let non_generating = rules
        .iter()
        .filter(|rule| !rule_bool(rule, "generates_finding_when_no_match").unwrap_or(false))
        .collect::<Vec<_>>();
    assert!(
        !non_generating.is_empty(),
        "expected at least one non-generating rule"
    );
}

#[test]
fn every_rule_has_integer_priority() {
    for rule in rule_table() {
        let rule_id = rule_string(&rule, "rule_id").unwrap_or_else(|| String::from("<missing>"));
        let priority = rule_int(&rule, "priority");
        assert!(
            priority.is_some(),
            "rule {rule_id} missing integer priority"
        );
    }
}

#[test]
fn initial_rule_set_priorities_are_total_ordered() {
    let priorities = rule_table()
        .iter()
        .filter_map(|rule| rule_int(rule, "priority"))
        .collect::<Vec<_>>();
    let duplicates = priorities
        .iter()
        .copied()
        .collect::<BTreeSet<_>>()
        .into_iter()
        .filter(|priority| {
            priorities
                .iter()
                .filter(|value| **value == *priority)
                .count()
                > 1
        })
        .collect::<Vec<_>>();
    assert!(
        duplicates.is_empty(),
        "duplicate priorities: {duplicates:?}"
    );
}

#[test]
fn initial_rule_set_priorities_match_data_model() {
    let actual = rule_table()
        .iter()
        .filter_map(|rule| {
            let rule_id = rule_string(rule, "rule_id")?;
            let priority = rule_int(rule, "priority")?;
            Some((rule_id, priority))
        })
        .collect::<BTreeMap<_, _>>();
    let expected = EXPECTED_RULE_PRIORITIES
        .iter()
        .map(|(id, priority)| (String::from(*id), *priority))
        .collect::<BTreeMap<_, _>>();

    assert_eq!(
        actual, expected,
        "rule priorities drifted from the shared reference"
    );
}

#[test]
fn priority_order_matches_rule_id_order() {
    let mut initial_rules = rule_table()
        .into_iter()
        .filter(|rule| {
            EXPECTED_RULE_PRIORITIES
                .iter()
                .any(|(id, _)| rule_string(rule, "rule_id").as_deref() == Some(*id))
        })
        .collect::<Vec<_>>();
    initial_rules.sort_by_key(rule_id_order);
    let priorities = initial_rules
        .iter()
        .map(|rule| rule_int(rule, "priority").expect("priority"))
        .collect::<Vec<_>>();
    let sorted = {
        let mut sorted = priorities.clone();
        sorted.sort_unstable();
        sorted
    };
    assert_eq!(
        priorities, sorted,
        "priority order does not match rule_id order"
    );
}
