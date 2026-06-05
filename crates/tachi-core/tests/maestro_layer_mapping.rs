use std::collections::BTreeMap;

use pretty_assertions::assert_eq;

use tachi_core::infographic::{
    extract_maestro_data, parse_component_layer_mapping, MaestroData, MaestroFinding,
    MaestroHeatmapRow, MaestroLayerDistribution,
};

#[test]
fn parse_component_layer_mapping_reads_layer_table() {
    let threats_markdown = r#"
### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| API Gateway | API | L2 — Guardrails |
| Policy Engine | Service | L5 — Infrastructure Controls |
"#;

    let mapping = parse_component_layer_mapping(threats_markdown);
    let expected: BTreeMap<String, String> = [
        (String::from("API Gateway"), String::from("L2 — Guardrails")),
        (
            String::from("Policy Engine"),
            String::from("L5 — Infrastructure Controls"),
        ),
    ]
    .into_iter()
    .collect();

    assert_eq!(mapping, expected);
}

#[test]
fn extract_maestro_data_aggregates_sections_and_flags_presence() {
    let threats_markdown = r#"
### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| API Gateway | API | L2 — Guardrails |
| Policy Engine | Service | L5 — Infrastructure Controls |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
| --- | --- | --- |
| L2 — Guardrails | 2 | High |
| L5 — Infrastructure Controls | 1 | Critical |

### 3. AI

| ID | Component | MAESTRO Layer | Risk Level |
| --- | --- | --- | --- |
| S-1 | API Gateway | L2 — Guardrails | High |
"#;

    let actual = extract_maestro_data(threats_markdown);

    let expected = MaestroData {
        maestro_layer_distribution: vec![
            MaestroLayerDistribution {
                layer_id: String::from("L2"),
                layer_name: String::from("Guardrails"),
                finding_count: 2,
                highest_severity: String::from("High"),
            },
            MaestroLayerDistribution {
                layer_id: String::from("L5"),
                layer_name: String::from("Infrastructure Controls"),
                finding_count: 1,
                highest_severity: String::from("Critical"),
            },
        ],
        most_exposed_layer: String::from("L2 — Guardrails"),
        component_layer_map: [
            (String::from("API Gateway"), String::from("L2 — Guardrails")),
            (
                String::from("Policy Engine"),
                String::from("L5 — Infrastructure Controls"),
            ),
        ]
        .into_iter()
        .collect(),
        per_finding_maestro: vec![MaestroFinding {
            id: String::from("S-1"),
            component: String::from("API Gateway"),
            maestro_layer: String::from("L2 — Guardrails"),
            risk_level: String::from("High"),
            threat: String::new(),
        }],
        maestro_heatmap: vec![MaestroHeatmapRow {
            component: String::from("API Gateway"),
            layers: [
                (String::from("L1"), None),
                (String::from("L2"), Some(String::from("High"))),
                (String::from("L3"), None),
                (String::from("L4"), None),
                (String::from("L5"), None),
                (String::from("L6"), None),
                (String::from("L7"), None),
            ]
            .into_iter()
            .collect(),
        }],
        has_maestro_data: true,
    };

    assert_eq!(actual, expected);
}
