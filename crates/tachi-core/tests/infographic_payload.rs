use pretty_assertions::assert_eq;
use serde_json::Value;
use std::sync::atomic::{AtomicU64, Ordering};

use tachi_core::infographic::{
    build_infographic_payload, MaestroLayerDistribution, PerLayerSummary,
};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

const MAESTRO_THREATS_MD: &str = r#"
# Agentic AI Application

### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| LLM Agent Orchestrator | Service | L2 — Foundation Model |
| MCP Tool Server | Service | L2 — Foundation Model |
| Guardrails Service | Service | L5 — Infrastructure Controls |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
| --- | --- | --- |
| L2 — Foundation Model | 2 | High |
| L5 — Infrastructure Controls | 1 | Critical |

### 3. AI Agents

| ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L2 — Foundation Model | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L2 — Foundation Model | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L5 — Infrastructure Controls | Critical | Model output exfiltration | Enforce egress controls |

## 7. Recommended Actions

| Finding ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L2 — Foundation Model | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L2 — Foundation Model | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L5 — Infrastructure Controls | Critical | Model output exfiltration | Enforce egress controls |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 1 |
| High | 1 |
| Medium | 1 |
| Low | 0 |
| Note | 0 |
| Total | 3 |
"#;

fn layer_distribution_fixture() -> Vec<MaestroLayerDistribution> {
    vec![
        MaestroLayerDistribution {
            layer_id: String::from("L2"),
            layer_name: String::from("Foundation Model"),
            finding_count: 2,
            highest_severity: String::from("High"),
        },
        MaestroLayerDistribution {
            layer_id: String::from("L5"),
            layer_name: String::from("Infrastructure Controls"),
            finding_count: 1,
            highest_severity: String::from("Critical"),
        },
    ]
}

fn expected_stack_payload() -> Value {
    let per_layer = vec![
        PerLayerSummary {
            layer_id: String::from("L2"),
            layer_name: String::from("Foundation Model"),
            finding_count: 2,
            highest_severity: String::from("High"),
            top_findings: vec![
                tachi_core::infographic::PerLayerTopFinding {
                    id: String::from("S-1"),
                    threat: String::from("Prompt override risk"),
                },
                tachi_core::infographic::PerLayerTopFinding {
                    id: String::from("A-1"),
                    threat: String::from("Tool abuse injection"),
                },
            ],
        },
        PerLayerSummary {
            layer_id: String::from("L5"),
            layer_name: String::from("Infrastructure Controls"),
            finding_count: 1,
            highest_severity: String::from("Critical"),
            top_findings: vec![tachi_core::infographic::PerLayerTopFinding {
                id: String::from("I-1"),
                threat: String::from("Model output exfiltration"),
            }],
        },
    ];

    let expected_template_data = serde_json::json!({
        "maestro_layer_distribution": layer_distribution_fixture(),
        "most_exposed_layer": "L2 — Foundation Model",
        "per_layer_summaries": per_layer,
        "has_maestro_data": true,
    });

    serde_json::json!({
        "template_data": expected_template_data,
    })
}

#[test]
fn build_infographic_payload_maestro_stack_includes_layer_summaries() {
    let root = temp_dir_with_threats();
    let payload = build_infographic_payload(&root, "maestro-stack").expect("payload");
    let expected = expected_stack_payload();

    assert_eq!(payload["template"], "maestro-stack");
    assert_eq!(payload["metadata"]["data_source_type"], "threats-only");
    assert_eq!(payload["has_maestro_data"], true);
    assert_eq!(payload["template_data"], expected["template_data"]);
}

#[test]
fn build_infographic_payload_maestro_heatmap_includes_distribution_and_flags() {
    let root = temp_dir_with_threats();
    let payload = build_infographic_payload(&root, "maestro-heatmap").expect("payload");

    assert_eq!(payload["template"], "maestro-heatmap");
    assert_eq!(payload["has_maestro_data"], true);

    let heat_map = payload["template_data"]["maestro_heatmap"]
        .as_array()
        .expect("heat_map array");
    assert_eq!(heat_map.len(), 3);
    let l2_row = heat_map
        .iter()
        .find(|row| row["component"] == "LLM Agent Orchestrator")
        .expect("LLM row exists");
    assert_eq!(l2_row["L2"], Value::String("High".to_string()));
}

fn temp_dir_with_threats() -> std::path::PathBuf {
    let mut path = std::env::temp_dir();
    let unique_suffix = TEMP_DIR_COUNTER.fetch_add(1, Ordering::Relaxed);
    path.push(format!(
        "tachi-rust-infographic-payload-{}-{}-{}",
        std::process::id(),
        unique_suffix,
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));
    std::fs::create_dir_all(&path).expect("create temp dir");
    std::fs::write(path.join("threats.md"), MAESTRO_THREATS_MD).expect("write threats");
    path
}
