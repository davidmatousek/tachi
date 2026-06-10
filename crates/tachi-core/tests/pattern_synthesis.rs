use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};

use regex::Regex;
use serde_yaml::Value;
use tachi_core::parsers::{parse_threats_findings, VALID_AGENTIC_PATTERNS};

#[derive(Debug, Clone, PartialEq, Eq)]
struct GateMetadata {
    agentic_llm_count: usize,
    matched_components: Vec<String>,
    matched_flow: Option<(String, String)>,
    matched_keywords: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct GateRecord {
    result: bool,
    condition_a: bool,
    condition_b: bool,
    condition_c: bool,
    evaluation_metadata: GateMetadata,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct SynthesisResult {
    gate: GateRecord,
    classified: Vec<Value>,
    net_new: Vec<Value>,
    has_agentic_patterns: bool,
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn fixtures_dir() -> PathBuf {
    workspace_root().join("tests/scripts/fixtures/pattern_synthesis")
}

fn read_text(path: &Path) -> String {
    fs::read_to_string(path)
        .unwrap_or_else(|err| panic!("failed to read {}: {err}", path.display()))
}

fn read_yaml(path: &Path) -> Value {
    serde_yaml::from_str(&read_text(path))
        .unwrap_or_else(|err| panic!("failed to parse {}: {err}", path.display()))
}

fn yaml_mapping<'a>(value: &'a Value, key: &str) -> Option<&'a serde_yaml::Mapping> {
    value
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from(key)))
        .and_then(Value::as_mapping)
}

fn yaml_string(value: &Value, key: &str) -> String {
    value
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from(key)))
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_string()
}

fn yaml_sequence<'a>(value: &'a Value, key: &str) -> Option<&'a Vec<Value>> {
    value
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from(key)))
        .and_then(Value::as_sequence)
}

fn yaml_i64(value: &Value, key: &str) -> i64 {
    value
        .as_mapping()
        .and_then(|mapping| mapping.get(Value::from(key)))
        .and_then(Value::as_i64)
        .unwrap_or(10_000)
}

fn load_rules() -> Vec<Value> {
    let data = read_yaml(&fixtures_dir().join("rules.yaml"));
    yaml_sequence(&data, "rules").expect("rules table").clone()
}

fn load_architecture(name: &str) -> Value {
    read_yaml(&fixtures_dir().join(format!("arch_{name}.yaml")))
}

fn load_architectures() -> BTreeMap<String, Value> {
    [
        "web_app",
        "microservices",
        "ascii_web_api",
        "mermaid_agentic_app",
        "free_text_microservice",
        "agentic_app_extended",
        "single_agent_with_fine_tuning",
    ]
    .into_iter()
    .map(|name| (name.to_string(), load_architecture(name)))
    .collect()
}

fn multi_agent_keywords() -> [&'static str; 5] {
    [
        "multi-agent",
        "swarm",
        "supervisor",
        "delegation",
        "agent mesh",
    ]
}

fn persistent_state_tokens() -> [(&'static str, [&'static str; 6]); 3] {
    [
        (
            "fine_tuning_pipeline",
            [
                "fine-tuning pipeline",
                "fine tuning pipeline",
                "training pipeline",
                "fine-tune pipeline",
                "",
                "",
            ],
        ),
        (
            "persistent_agent_memory",
            [
                "agent memory",
                "persistent memory",
                "memory store",
                "long-term memory",
                "agent state store",
                "",
            ],
        ),
        (
            "long_running_learning_loop",
            [
                "learning loop",
                "feedback loop",
                "continual learning",
                "rlhf loop",
                "reward model loop",
                "self-improvement loop",
            ],
        ),
    ]
}

fn inter_agent_channel_keywords() -> [&'static str; 5] {
    [
        "inter-agent channel",
        "message bus",
        "agent communication channel",
        "shared queue",
        "shared memory",
    ]
}

fn architecture_text_pool(architecture: &Value) -> String {
    let mut parts = vec![yaml_string(architecture, "description")];
    if let Some(components) = yaml_sequence(architecture, "components") {
        for component in components {
            parts.push(yaml_string(component, "name"));
        }
    }
    parts.join(" ").to_lowercase()
}

fn architecture_has_topology(architecture: &Value, indicator: &str) -> bool {
    let gate = evaluate_multi_agent_gate(architecture);
    match indicator {
        "multi_agent" => gate.condition_a,
        "inter_agent_data_flow" => gate.condition_b,
        "persistent_state" => {
            let text_pool = architecture_text_pool(architecture);
            persistent_state_tokens().iter().any(|(_, keywords)| {
                keywords
                    .iter()
                    .filter(|kw| !kw.is_empty())
                    .any(|kw| text_pool.contains(kw))
            })
        }
        "inter_agent_channel" => {
            if !gate.condition_a {
                return false;
            }
            let text_pool = architecture_text_pool(architecture);
            inter_agent_channel_keywords()
                .iter()
                .any(|kw| text_pool.contains(kw))
        }
        _ => false,
    }
}

fn evaluate_multi_agent_gate(architecture: &Value) -> GateRecord {
    let components = yaml_sequence(architecture, "components")
        .cloned()
        .unwrap_or_default();
    let flows = yaml_sequence(architecture, "data_flows")
        .cloned()
        .unwrap_or_default();
    let description = yaml_string(architecture, "description");

    let agentic_components: Vec<&Value> = components
        .iter()
        .filter(|component| {
            matches!(
                yaml_string(component, "category").to_lowercase().as_str(),
                "agentic" | "llm"
            )
        })
        .collect();
    let condition_a = agentic_components.len() >= 2;

    let category_by_name: BTreeMap<String, String> = components
        .iter()
        .map(|component| {
            (
                yaml_string(component, "name"),
                yaml_string(component, "category").to_lowercase(),
            )
        })
        .collect();

    let mut condition_b = false;
    let mut matched_flow = None;
    for flow in &flows {
        let source = yaml_string(flow, "source");
        let target = yaml_string(flow, "target");
        let src_cat = category_by_name.get(&source).cloned().unwrap_or_default();
        let tgt_cat = category_by_name.get(&target).cloned().unwrap_or_default();
        if matches!(src_cat.as_str(), "agentic" | "llm")
            && matches!(tgt_cat.as_str(), "agentic" | "llm")
        {
            condition_b = true;
            matched_flow = Some((source, target));
            break;
        }
    }

    let desc_lower = description.to_lowercase();
    let matched_keywords: Vec<String> = multi_agent_keywords()
        .iter()
        .filter(|keyword| desc_lower.contains(**keyword))
        .map(|keyword| (*keyword).to_string())
        .collect();
    let condition_c = !matched_keywords.is_empty();

    let result = condition_a || condition_b || condition_c;
    GateRecord {
        result,
        condition_a,
        condition_b,
        condition_c,
        evaluation_metadata: GateMetadata {
            agentic_llm_count: agentic_components.len(),
            matched_components: agentic_components
                .iter()
                .map(|component| yaml_string(component, "name"))
                .collect(),
            matched_flow,
            matched_keywords,
        },
    }
}

fn finding_matches_rule(finding: &Value, rule: &Value, architecture: &Value) -> bool {
    let mc = yaml_mapping(rule, "match_conditions")
        .cloned()
        .unwrap_or_default();
    let mc_value = Value::Mapping(mc.clone());

    if let Some(categories) = yaml_sequence(&mc_value, "category_in") {
        let category = yaml_string(finding, "category");
        if !categories
            .iter()
            .any(|value| value.as_str() == Some(category.as_str()))
        {
            return false;
        }
    }

    if let Some(layers) = yaml_sequence(&mc_value, "maestro_layer_in") {
        let layer = yaml_string(finding, "maestro_layer");
        if !layers
            .iter()
            .any(|value| value.as_str() == Some(layer.as_str()))
        {
            return false;
        }
    }

    if let Some(target_component_matches) = mc
        .get(Value::from("target_component_matches"))
        .and_then(Value::as_mapping)
    {
        if let Some(regex_pattern) = target_component_matches
            .get(Value::from("type_or_name_regex"))
            .and_then(Value::as_str)
        {
            let regex = Regex::new(regex_pattern).expect("compile component regex");
            let component = yaml_string(finding, "component");
            if !regex.is_match(&component) {
                return false;
            }
        }
    }

    if let Some(architecture_has) = mc
        .get(Value::from("architecture_has"))
        .and_then(Value::as_mapping)
    {
        if let Some(topologies) = architecture_has
            .get(Value::from("topology"))
            .and_then(Value::as_sequence)
        {
            if !topologies
                .iter()
                .filter_map(Value::as_str)
                .any(|topology| architecture_has_topology(architecture, topology))
            {
                return false;
            }
        }
    }

    if let Some(tokens) = yaml_sequence(&mc_value, "description_contains") {
        let fdesc = yaml_string(finding, "description").to_lowercase();
        if !tokens
            .iter()
            .filter_map(Value::as_str)
            .any(|tok| fdesc.contains(&tok.to_lowercase()))
        {
            return false;
        }
    }

    true
}

fn classify_finding(finding: &Value, rules: &[Value], architecture: &Value) -> String {
    let mut matching: Vec<&Value> = rules
        .iter()
        .filter(|rule| finding_matches_rule(finding, rule, architecture))
        .collect();
    if matching.is_empty() {
        return "none".to_string();
    }
    matching.sort_by_key(|rule| yaml_i64(rule, "priority"));
    let best_priority = yaml_i64(matching[0], "priority");
    let tied = matching
        .iter()
        .filter(|rule| yaml_i64(rule, "priority") == best_priority)
        .count();
    if tied > 1 {
        return "multiple".to_string();
    }
    yaml_string(matching[0], "pattern")
}

fn classifiy_all_findings(
    findings: &[Value],
    rules: &[Value],
    architecture: &Value,
    gate_result: bool,
) -> Vec<Value> {
    let mut out = Vec::new();
    for finding in findings {
        let mut enriched = finding.clone();
        if !gate_result {
            set_yaml_string(&mut enriched, "agentic_pattern", "none");
        } else {
            let existing = yaml_string(&enriched, "agentic_pattern");
            if existing.is_empty() || existing == "none" {
                let assigned = classify_finding(&enriched, rules, architecture);
                set_yaml_string(&mut enriched, "agentic_pattern", &assigned);
            }
        }
        out.push(enriched);
    }
    out
}

fn set_yaml_string(value: &mut Value, key: &str, new_value: &str) {
    if let Value::Mapping(mapping) = value {
        mapping.insert(Value::from(key), Value::from(new_value));
    }
}

fn jaccard_overlap(a: &str, b: &str) -> f64 {
    fn tokens(s: &str) -> BTreeSet<String> {
        s.to_lowercase()
            .split_whitespace()
            .filter_map(|raw| {
                let t = raw.trim_matches(|ch: char| ".,;:!?()[]{}\"'`—–-".contains(ch));
                (!t.is_empty()).then(|| t.to_string())
            })
            .collect()
    }

    let ta = tokens(a);
    let tb = tokens(b);
    if ta.is_empty() && tb.is_empty() {
        return 0.0;
    }
    ta.intersection(&tb).count() as f64 / ta.union(&tb).count() as f64
}

fn pick_target_component(architecture: &Value) -> Option<String> {
    let components = yaml_sequence(architecture, "components")?;
    for component in components {
        let category = yaml_string(component, "category").to_lowercase();
        if matches!(category.as_str(), "agentic" | "llm") {
            return Some(yaml_string(component, "name"));
        }
    }
    components
        .first()
        .map(|component| yaml_string(component, "name"))
}

fn generate_net_new_findings(
    classified_findings: &[Value],
    rules: &[Value],
    architecture: &Value,
    gate_result: bool,
    overlap_threshold: f64,
) -> Vec<Value> {
    if !gate_result {
        return Vec::new();
    }

    let assigned_patterns: BTreeSet<String> = classified_findings
        .iter()
        .map(|finding| yaml_string(finding, "agentic_pattern"))
        .filter(|pattern| !pattern.is_empty() && pattern != "none")
        .collect();

    let mut new_findings = Vec::new();
    let mut sequence = 1usize;

    let mut gen_rules: Vec<&Value> = rules
        .iter()
        .filter(|rule| {
            rule.as_mapping()
                .and_then(|mapping| mapping.get(Value::from("generates_finding_when_no_match")))
                .and_then(Value::as_bool)
                .unwrap_or(false)
        })
        .collect();
    gen_rules.sort_by_key(|rule| {
        yaml_mapping(rule, "priority")
            .and_then(|mapping| mapping.get(Value::from("priority")))
            .and_then(Value::as_i64)
            .unwrap_or(10_000)
    });

    for rule in gen_rules {
        let pattern = yaml_string(rule, "pattern");
        if assigned_patterns.contains(&pattern) {
            continue;
        }

        let match_conditions = yaml_mapping(rule, "match_conditions")
            .cloned()
            .unwrap_or_default();
        if let Some(architecture_has) = match_conditions
            .get(Value::from("architecture_has"))
            .and_then(Value::as_mapping)
        {
            if let Some(topologies) = architecture_has
                .get(Value::from("topology"))
                .and_then(Value::as_sequence)
            {
                if !topologies
                    .iter()
                    .filter_map(Value::as_str)
                    .any(|topology| architecture_has_topology(architecture, topology))
                {
                    continue;
                }
            }
        }

        let template = yaml_string(rule, "generation_template");
        if !template.is_empty()
            && classified_findings.iter().any(|finding| {
                let desc = yaml_string(finding, "description");
                !desc.is_empty() && jaccard_overlap(&desc, &template) >= overlap_threshold
            })
        {
            continue;
        }

        let Some(target_component) = pick_target_component(architecture) else {
            continue;
        };

        let description = template.replace("{component}", &target_component);
        let mut finding = Value::Mapping(serde_yaml::Mapping::new());
        set_yaml_string(&mut finding, "id", &format!("AGP-{sequence:02}"));
        set_yaml_string(&mut finding, "category", "agentic");
        set_yaml_string(&mut finding, "agentic_pattern", &pattern);
        set_yaml_string(&mut finding, "component", &target_component);
        set_yaml_string(&mut finding, "description", description.trim());
        set_yaml_string(&mut finding, "likelihood", "Medium");
        set_yaml_string(&mut finding, "impact", "Medium");
        set_yaml_string(&mut finding, "risk_level", "Medium");
        set_yaml_string(&mut finding, "delta_status", "NEW");

        new_findings.push(finding);
        sequence += 1;
    }

    new_findings
}

fn run_synthesis(findings: &[Value], rules: &[Value], architecture: &Value) -> SynthesisResult {
    let gate = evaluate_multi_agent_gate(architecture);
    let classified = classifiy_all_findings(findings, rules, architecture, gate.result);
    let net_new = generate_net_new_findings(&classified, rules, architecture, gate.result, 0.80);
    let has_agentic_patterns = classified
        .iter()
        .chain(net_new.iter())
        .map(|finding| yaml_string(finding, "agentic_pattern"))
        .any(|pattern| !pattern.is_empty() && pattern != "none");
    SynthesisResult {
        gate,
        classified,
        net_new,
        has_agentic_patterns,
    }
}

fn find_rule<'a>(rules: &'a [Value], rule_id: &str) -> &'a Value {
    rules
        .iter()
        .find(|rule| yaml_string(rule, "rule_id") == rule_id)
        .expect("rule")
}

fn canonical_rules(rules: &[Value]) -> Vec<Value> {
    rules
        .iter()
        .filter(|rule| yaml_string(rule, "rule_id").starts_with("R-0"))
        .cloned()
        .collect()
}

fn synthetic_tie_rules(rules: &[Value]) -> Vec<Value> {
    rules
        .iter()
        .filter(|rule| yaml_string(rule, "rule_id").starts_with("R-TIE"))
        .cloned()
        .collect()
}

#[test]
fn pattern_synthesis_contract_is_rust_native() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_pattern_synthesis.py")
            .exists(),
        "pattern synthesis coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn multi_agent_gate_across_baselines_matches_expected_matrix() {
    let architectures = load_architectures();
    let expectations = [
        ("web_app", false),
        ("microservices", false),
        ("ascii_web_api", false),
        ("free_text_microservice", false),
        ("single_agent_with_fine_tuning", false),
        ("mermaid_agentic_app", true),
        ("agentic_app_extended", true),
    ];

    for (name, expected) in expectations {
        let gate = evaluate_multi_agent_gate(architectures.get(name).expect("architecture"));
        assert_eq!(gate.result, expected, "unexpected gate result for {name}");
    }
}

#[test]
fn classification_rule_precedence_and_multiple_match_python_contracts_hold() {
    let rules = load_rules();
    let canonical = canonical_rules(&rules);
    let synthetic = synthetic_tie_rules(&rules);
    let architectures = load_architectures();
    let arch = architectures
        .get("agentic_app_extended")
        .expect("architecture");

    let finding = Value::Mapping(
        [
            ("id", "AG-9"),
            ("category", "agentic"),
            ("component", "LLM Agent Orchestrator"),
            (
                "description",
                "Coordinated peer-agent exploit with identity spoofing.",
            ),
        ]
        .into_iter()
        .map(|(k, v)| (Value::from(k), Value::from(v)))
        .collect(),
    );
    assert_eq!(
        classify_finding(&finding, &canonical, arch),
        "agent_collusion"
    );

    let finding = Value::Mapping(
        [
            ("id", "AG-77"),
            ("category", "agentic"),
            ("component", "LLM Agent Orchestrator"),
            (
                "description",
                "A synthetic_tie_marker threat exercising both tied rules.",
            ),
        ]
        .into_iter()
        .map(|(k, v)| (Value::from(k), Value::from(v)))
        .collect(),
    );
    assert_eq!(classify_finding(&finding, &synthetic, arch), "multiple");
}

#[test]
fn synthesis_generation_and_suppression_rules_match_reference_behavior() {
    let rules = load_rules();
    let canonical = canonical_rules(&rules);
    let architectures = load_architectures();
    let arch = architectures
        .get("agentic_app_extended")
        .expect("architecture");

    let result = run_synthesis(&[], &canonical, arch);
    assert!(result.gate.result);
    let patterns: BTreeSet<String> = result
        .net_new
        .iter()
        .map(|finding| yaml_string(finding, "agentic_pattern"))
        .collect();
    assert!(patterns.contains("agent_collusion"));
    assert!(patterns.contains("temporal_attack"));
    assert!(patterns.contains("emergent_behavior"));
    assert_eq!(result.net_new.len(), 3);
    let ids: Vec<String> = result
        .net_new
        .iter()
        .map(|finding| yaml_string(finding, "id"))
        .collect();
    assert_eq!(ids, vec!["AGP-01", "AGP-02", "AGP-03"]);

    let existing = vec![Value::Mapping(
        [
            ("id", "AG-1"),
            ("category", "agentic"),
            ("component", "LLM Agent Orchestrator"),
            (
                "description",
                "Existing agent collusion finding from detection tier.",
            ),
            ("agentic_pattern", "agent_collusion"),
        ]
        .into_iter()
        .map(|(k, v)| (Value::from(k), Value::from(v)))
        .collect(),
    )];
    let result = run_synthesis(&existing, &canonical, arch);
    let patterns: BTreeSet<String> = result
        .net_new
        .iter()
        .map(|finding| yaml_string(finding, "agentic_pattern"))
        .collect();
    assert!(!patterns.contains("agent_collusion"));
    assert!(patterns.contains("temporal_attack"));
    assert!(patterns.contains("emergent_behavior"));
    assert_eq!(result.net_new.len(), 2);

    let r01_template = yaml_string(find_rule(&canonical, "R-01"), "generation_template");
    let existing = vec![Value::Mapping(
        [
            ("id", "AG-99"),
            ("category", "agentic"),
            ("component", "LLM Agent Orchestrator"),
            ("description", &r01_template),
            ("agentic_pattern", "none"),
        ]
        .into_iter()
        .map(|(k, v)| (Value::from(k), Value::from(v)))
        .collect(),
    )];
    let result = run_synthesis(&existing, &canonical, arch);
    let patterns: BTreeSet<String> = result
        .net_new
        .iter()
        .map(|finding| yaml_string(finding, "agentic_pattern"))
        .collect();
    assert!(!patterns.contains("agent_collusion"));
    assert!(patterns.contains("temporal_attack"));
    assert!(patterns.contains("emergent_behavior"));

    let arch = architectures
        .get("single_agent_with_fine_tuning")
        .expect("architecture");
    let result = run_synthesis(&[], &canonical, arch);
    assert!(!result.gate.result);
    assert!(result.net_new.is_empty());
    assert!(!result.has_agentic_patterns);
}

#[test]
fn synthesis_is_deterministic_and_order_independent() {
    let rules = load_rules();
    let canonical = canonical_rules(&rules);
    let architectures = load_architectures();
    let arch = architectures
        .get("agentic_app_extended")
        .expect("architecture");

    for architecture in architectures.values() {
        assert_eq!(
            evaluate_multi_agent_gate(architecture),
            evaluate_multi_agent_gate(architecture),
            "gate predicate should be deterministic"
        );
    }

    let findings = vec![
        Value::Mapping(
            [
                ("id", "AG-1"),
                ("category", "agentic"),
                ("component", "LLM Agent Orchestrator"),
                (
                    "description",
                    "Cascade of agent interactions amplifies failures.",
                ),
            ]
            .into_iter()
            .map(|(k, v)| (Value::from(k), Value::from(v)))
            .collect(),
        ),
        Value::Mapping(
            [
                ("id", "S-2"),
                ("category", "spoofing"),
                ("component", "Specialist Agent"),
                (
                    "description",
                    "Identity impersonation attack across peer agents.",
                ),
            ]
            .into_iter()
            .map(|(k, v)| (Value::from(k), Value::from(v)))
            .collect(),
        ),
        Value::Mapping(
            [
                ("id", "D-3"),
                ("category", "denial-of-service"),
                ("component", "Inter-Agent Channel"),
                (
                    "description",
                    "Resource monopolization by one peer agent starving others.",
                ),
            ]
            .into_iter()
            .map(|(k, v)| (Value::from(k), Value::from(v)))
            .collect(),
        ),
    ];
    let run1 = run_synthesis(&findings, &canonical, arch);
    let run2 = run_synthesis(&findings, &canonical, arch);
    assert_eq!(run1, run2);

    let forward = classifiy_all_findings(&findings, &canonical, arch, true);
    let backward = classifiy_all_findings(
        &findings.iter().rev().cloned().collect::<Vec<_>>(),
        &canonical,
        arch,
        true,
    );
    let forward_map: BTreeMap<String, String> = forward
        .iter()
        .map(|finding| {
            (
                yaml_string(finding, "id"),
                yaml_string(finding, "agentic_pattern"),
            )
        })
        .collect();
    let backward_map: BTreeMap<String, String> = backward
        .iter()
        .map(|finding| {
            (
                yaml_string(finding, "id"),
                yaml_string(finding, "agentic_pattern"),
            )
        })
        .collect();
    assert_eq!(forward_map, backward_map);
}

#[test]
fn backward_compatibility_defaults_to_none() {
    let rules = load_rules();
    let canonical = canonical_rules(&rules);
    let architectures = load_architectures();
    let arch = architectures.get("web_app").expect("architecture");

    let finding = Value::Mapping(
        [
            ("id", "S-1"),
            ("category", "spoofing"),
            ("component", "Auth Service"),
            ("description", "Token forgery via weak signature."),
        ]
        .into_iter()
        .map(|(k, v)| (Value::from(k), Value::from(v)))
        .collect(),
    );
    let result = run_synthesis(&[finding], &canonical, arch);
    assert_eq!(
        yaml_string(&result.classified[0], "agentic_pattern"),
        "none"
    );

    let pre_f142 = read_text(&fixtures_dir().join("threats_pre_f142.md"));
    let parsed = parse_threats_findings(&pre_f142).expect("parse pre-f142 threats");
    assert_eq!(parsed.len(), 3);
    for finding in parsed {
        let pattern = if finding.agentic_pattern.is_empty() {
            "none".to_string()
        } else {
            finding.agentic_pattern
        };
        assert_eq!(pattern, "none");
    }

    let post_f142 = read_text(&fixtures_dir().join("threats_post_f142.md"));
    let parsed = parse_threats_findings(&post_f142).expect("parse post-f142 threats");
    let ids: BTreeSet<String> = parsed.iter().map(|finding| finding.id.clone()).collect();
    assert!(ids.contains("AGP-01"));
    assert_eq!(parsed.len(), 5);

    assert_eq!(VALID_AGENTIC_PATTERNS.len(), 8);
    let canonical_patterns: BTreeSet<&str> = VALID_AGENTIC_PATTERNS
        .iter()
        .copied()
        .filter(|value| *value != "none" && *value != "multiple")
        .collect();
    assert_eq!(
        canonical_patterns,
        BTreeSet::from([
            "agent_collusion",
            "emergent_behavior",
            "temporal_attack",
            "trust_exploitation",
            "communication_vulnerability",
            "resource_competition",
        ])
    );
}

#[test]
fn reference_implementation_integrity_matches_rule_catalog() {
    let rules = load_rules();
    let canonical = canonical_rules(&rules);
    assert_eq!(
        canonical
            .iter()
            .map(|rule| yaml_string(rule, "rule_id"))
            .collect::<Vec<_>>(),
        vec!["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"]
    );
    let priorities: Vec<i64> = canonical
        .iter()
        .map(|rule| yaml_i64(rule, "priority"))
        .collect();
    let mut sorted = priorities.clone();
    sorted.sort_unstable();
    let deduped = {
        let mut values = sorted.clone();
        values.dedup();
        values
    };
    assert_eq!(sorted, deduped);
    assert_eq!(priorities.len(), 6);

    for rule in &canonical {
        if rule
            .as_mapping()
            .and_then(|mapping| mapping.get(Value::from("generates_finding_when_no_match")))
            .and_then(Value::as_bool)
            .unwrap_or(false)
        {
            assert!(
                !yaml_string(rule, "generation_template").is_empty(),
                "generator rule {} lacks a template",
                yaml_string(rule, "rule_id")
            );
        }
    }

    let valid_patterns: BTreeSet<&str> = VALID_AGENTIC_PATTERNS
        .iter()
        .copied()
        .filter(|value| *value != "none" && *value != "multiple")
        .collect();
    for rule in &canonical {
        let pattern = yaml_string(rule, "pattern");
        assert!(valid_patterns.contains(pattern.as_str()));
    }
}
