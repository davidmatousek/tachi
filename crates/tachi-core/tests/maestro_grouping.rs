use tachi_core::infographic::{
    group_maestro_findings_by_layer, MaestroData, MaestroFinding, MaestroLayerDistribution,
};

#[test]
fn group_maestro_findings_by_layer_orders_canonical_layers_before_unclassified() {
    let data = MaestroData {
        maestro_layer_distribution: vec![
            MaestroLayerDistribution {
                layer_id: String::from("L2"),
                layer_name: String::from("Foundation Model"),
                finding_count: 2,
                highest_severity: String::from("High"),
            },
            MaestroLayerDistribution {
                layer_id: String::from("L5"),
                layer_name: String::from("Evaluation and Observability"),
                finding_count: 1,
                highest_severity: String::from("Critical"),
            },
            MaestroLayerDistribution {
                layer_id: String::from("L6"),
                layer_name: String::from("Security and Compliance"),
                finding_count: 1,
                highest_severity: String::from("High"),
            },
        ],
        per_finding_maestro: vec![
            MaestroFinding {
                id: String::from("S-1"),
                component: String::from("LLM Agent Orchestrator"),
                maestro_layer: String::from("L2 — Foundation Model"),
                risk_level: String::from("High"),
                threat: String::from("Prompt override risk"),
            },
            MaestroFinding {
                id: String::from("A-1"),
                component: String::from("MCP Tool Server"),
                maestro_layer: String::from("L5 — Infrastructure Controls"),
                risk_level: String::from("Medium"),
                threat: String::from("Tool abuse injection"),
            },
            MaestroFinding {
                id: String::from("I-1"),
                component: String::from("Guardrails Service"),
                maestro_layer: String::from("Guardrails"),
                risk_level: String::from("Critical"),
                threat: String::from("Model output exfiltration"),
            },
        ],
        ..Default::default()
    };

    let groups = group_maestro_findings_by_layer(&data);

    assert_eq!(groups.len(), 3);
    assert_eq!(groups[0].layer_id, "L2");
    assert_eq!(groups[0].layer_name, "Foundation Model");
    assert_eq!(
        groups[0]
            .findings
            .iter()
            .map(|finding| finding.id.as_str())
            .collect::<Vec<_>>(),
        vec!["S-1"]
    );

    assert_eq!(groups[1].layer_id, "L5");
    assert_eq!(groups[1].layer_name, "Evaluation and Observability");
    assert_eq!(
        groups[1]
            .findings
            .iter()
            .map(|finding| finding.id.as_str())
            .collect::<Vec<_>>(),
        vec!["A-1"]
    );

    assert_eq!(groups[2].layer_id, "L6");
    assert_eq!(groups[2].layer_name, "Security and Compliance");
    assert_eq!(
        groups[2]
            .findings
            .iter()
            .map(|finding| finding.id.as_str())
            .collect::<Vec<_>>(),
        vec!["I-1"]
    );
}
