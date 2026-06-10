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
| LLM Agent Orchestrator | Service | L5 — Infrastructure Controls |
| MCP Tool Server | Service | L5 — Security |
| Guardrails Service | Service | L6 — Agent Ecosystem |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
| --- | --- | --- |
| L5 — Security | 2 | High |
| L6 — Agent Ecosystem | 1 | Critical |

### 3. AI Agents

| ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L5 — Infrastructure Controls | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L5 — Security | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L6 — Agent Ecosystem | Critical | Model output exfiltration | Enforce egress controls |

## 7. Recommended Actions

| Finding ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L5 — Infrastructure Controls | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L5 — Security | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L6 — Agent Ecosystem | Critical | Model output exfiltration | Enforce egress controls |

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

const EXECUTIVE_ARCHITECTURE_THREATS_MD: &str = r#"
# Agentic AI Application

### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| Web UI | Interface | L1 — Presentation |
| API Gateway | Service | L2 — Foundation Model |
| Edge Router | Service | L2 — Foundation Model |
| Core Service | Service | L3 — Control Plane |
| Guardrails Service | Service | L5 — Security |

### Data Flows

| Source | Destination | Data | Protocol |
| --- | --- | --- | --- |
| API Gateway | Core Service | Primary Request | HTTPS |
| Web UI | API Gateway | Login Request | HTTPS |
| Edge Router | API Gateway | Forwarded Request | HTTPS |

### Trust Zones

| Zone | Trust Level | Components |
| --- | --- | --- |
| Edge Layer | untrusted | Web UI, API Gateway, Edge Router |
| Core Layer | semi-trusted | Core Service |
| Security Layer | trusted | Guardrails Service |

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| S-1 | Web UI | Prompt override risk | Critical | Harden instruction guards | [NEW] |
| S-2 | API Gateway | Prompt override risk | Critical | Harden instruction guards | [NEW] |
| S-3 | Edge Router | Prompt override risk | Critical | Harden instruction guards | [NEW] |
| S-4 | API Gateway | Prompt override risk | Critical | Harden instruction guards | [NEW] |
| S-5 | Edge Router | Model output exfiltration | High | Enforce egress controls | [NEW] |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 4 |
| High | 1 |
| Medium | 0 |
| Low | 0 |
| Note | 0 |
| Total | 5 |
"#;

const EXECUTIVE_ARCHITECTURE_NO_SCOPE_MD: &str = r#"
# Agentic AI Application

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| S-1 | Web UI | Prompt override risk | Critical | Harden instruction guards | [NEW] |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 1 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Note | 0 |
| Total | 1 |
"#;

fn layer_distribution_fixture() -> Vec<MaestroLayerDistribution> {
    vec![
        MaestroLayerDistribution {
            layer_id: String::from("L5"),
            layer_name: String::from("Evaluation and Observability"),
            finding_count: 2,
            highest_severity: String::from("High"),
        },
        MaestroLayerDistribution {
            layer_id: String::from("L6"),
            layer_name: String::from("Security and Compliance"),
            finding_count: 1,
            highest_severity: String::from("Critical"),
        },
    ]
}

fn expected_stack_payload() -> Value {
    let per_layer = vec![
        PerLayerSummary {
            layer_id: String::from("L5"),
            layer_name: String::from("Evaluation and Observability"),
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
            layer_id: String::from("L6"),
            layer_name: String::from("Security and Compliance"),
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
        "most_exposed_layer": "L5 — Evaluation and Observability",
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
    assert_eq!(l2_row["L5"], Value::String("High".to_string()));
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

fn temp_dir_with_executive_architecture_threats(content: &str) -> std::path::PathBuf {
    let mut path = std::env::temp_dir();
    let unique_suffix = TEMP_DIR_COUNTER.fetch_add(1, Ordering::Relaxed);
    path.push(format!(
        "tachi-rust-exec-arch-payload-{}-{}-{}",
        std::process::id(),
        unique_suffix,
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));
    std::fs::create_dir_all(&path).expect("create temp dir");
    std::fs::write(path.join("threats.md"), content).expect("write threats");
    path
}

#[test]
fn build_infographic_payload_executive_architecture_includes_layers_callouts_and_overlay() {
    let root = temp_dir_with_executive_architecture_threats(EXECUTIVE_ARCHITECTURE_THREATS_MD);
    let payload = build_infographic_payload(&root, "executive-architecture").expect("payload");

    assert_eq!(payload["template"], "executive-architecture");
    assert_eq!(
        payload["template_data"]["metadata"]["template_name"],
        "executive-architecture"
    );
    assert_eq!(payload["template_data"]["metadata"]["skip_image"], false);
    assert_eq!(payload["template_data"]["metadata"]["fallback_used"], false);

    let layers = payload["template_data"]["layers"]
        .as_array()
        .expect("layers array");
    assert_eq!(layers.len(), 3);
    assert_eq!(layers[0]["name"], "Edge Layer");
    assert_eq!(layers[0]["layer_overflow"], "+ 1 more in this layer");

    let callouts = payload["template_data"]["callouts"]
        .as_array()
        .expect("callouts array");
    let edge_callouts: Vec<_> = callouts
        .iter()
        .filter(|callout| callout["layer_name"] == "Edge Layer")
        .collect();
    assert_eq!(edge_callouts.len(), 4);
    assert_eq!(edge_callouts[0]["finding_id"], "S-1");
    assert_eq!(edge_callouts[1]["finding_id"], "S-2");
    assert_eq!(edge_callouts[2]["finding_id"], "S-3");
    assert_eq!(edge_callouts[3]["finding_id"], "S-4");

    let flow_edges = payload["template_data"]["flow_edges"]
        .as_array()
        .expect("flow_edges array");
    assert_eq!(flow_edges.len(), 3);
    assert_eq!(flow_edges[0]["source"], "API Gateway");
    assert_eq!(flow_edges[0]["destination"], "Core Service");

    let clusters = payload["template_data"]["clusters"]
        .as_array()
        .expect("clusters array");
    assert_eq!(clusters.len(), 3);
    assert_eq!(clusters[0]["name"], "Security Layer");
    assert_eq!(clusters[0]["trust_level"], "trusted");
}

#[test]
fn build_infographic_payload_executive_architecture_requires_scope_data() {
    let root = temp_dir_with_executive_architecture_threats(EXECUTIVE_ARCHITECTURE_NO_SCOPE_MD);
    let err = build_infographic_payload(&root, "executive-architecture").expect_err("error");

    assert!(
        err.contains("no_scope_data"),
        "expected no_scope_data error, got {err}"
    );
}
