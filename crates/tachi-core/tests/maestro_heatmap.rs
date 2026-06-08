use std::collections::BTreeMap;

use pretty_assertions::assert_eq;

use tachi_core::infographic::{compute_maestro_heatmap, MaestroFinding, MaestroHeatmapRow};

#[test]
fn compute_maestro_heatmap_keeps_highest_severity_per_cell_and_sorts_components() {
    let findings = vec![
        MaestroFinding {
            id: String::from("A-1"),
            component: String::from("API"),
            maestro_layer: String::from("L1 — Foundation Model"),
            risk_level: String::from("Low"),
            threat: String::from("Prompt injection"),
        },
        MaestroFinding {
            id: String::from("A-2"),
            component: String::from("API"),
            maestro_layer: String::from("L1 — Foundation Model"),
            risk_level: String::from("High"),
            threat: String::from("Prompt injection"),
        },
        MaestroFinding {
            id: String::from("B-1"),
            component: String::from("Auth"),
            maestro_layer: String::from("L6 — Security and Compliance"),
            risk_level: String::from("Medium"),
            threat: String::from("Jailbreak"),
        },
    ];

    let actual = compute_maestro_heatmap(&findings);
    let expected = vec![
        MaestroHeatmapRow {
            component: String::from("API"),
            layers: layers(&[("L1", Some("High"))]),
        },
        MaestroHeatmapRow {
            component: String::from("Auth"),
            layers: layers(&[("L6", Some("Medium"))]),
        },
    ];

    assert_eq!(actual, expected);
}

fn layers(entries: &[(&str, Option<&str>)]) -> BTreeMap<String, Option<String>> {
    let mut layers = BTreeMap::new();
    for lid in ["L1", "L2", "L3", "L4", "L5", "L6", "L7"] {
        layers.insert(lid.to_string(), None);
    }

    for (layer_id, severity) in entries {
        layers.insert(
            (*layer_id).to_string(),
            severity.map(|value| value.to_string()),
        );
    }

    layers
}
