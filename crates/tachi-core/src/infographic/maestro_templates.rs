use serde_json::{json, Map, Value};

use crate::coverage_taxonomy::normalize_maestro_layer_label;

use super::{
    severity_rank, MaestroData, MaestroHeatmapRow, MaestroLayerDistribution, PerLayerTopFinding,
};

pub(crate) fn build_maestro_stack_template_data(maestro_data: &MaestroData) -> Value {
    let per_layer_summaries = maestro_data
        .maestro_layer_distribution
        .iter()
        .map(|layer| {
            let mut layer_findings = maestro_data
                .per_finding_maestro
                .iter()
                .filter(|f| {
                    normalize_maestro_layer_label(&f.maestro_layer).starts_with(&layer.layer_id)
                })
                .collect::<Vec<_>>();

            layer_findings.sort_by(|left, right| {
                severity_rank(&right.risk_level)
                    .cmp(&severity_rank(&left.risk_level))
                    .then_with(|| left.id.cmp(&right.id))
            });

            let top = layer_findings
                .iter()
                .take(2)
                .map(|finding| PerLayerTopFinding {
                    id: finding.id.clone(),
                    threat: finding.threat.chars().take(120).collect(),
                });

            json!({
                "layer_id": layer.layer_id,
                "layer_name": layer.layer_name,
                "finding_count": layer.finding_count,
                "highest_severity": layer.highest_severity,
                "top_findings": top.collect::<Vec<_>>(),
            })
        })
        .collect::<Vec<_>>();

    json!({
        "maestro_layer_distribution": to_value_layer_distribution(&maestro_data.maestro_layer_distribution),
        "most_exposed_layer": maestro_data.most_exposed_layer,
        "per_layer_summaries": per_layer_summaries,
        "has_maestro_data": maestro_data.has_maestro_data,
    })
}

pub(crate) fn build_maestro_heatmap_template_data(maestro_data: &MaestroData) -> Value {
    json!({
        "maestro_heatmap": to_value_heatmap(&maestro_data.maestro_heatmap),
        "maestro_layer_distribution": to_value_layer_distribution(&maestro_data.maestro_layer_distribution),
        "has_maestro_data": maestro_data.has_maestro_data,
    })
}

fn to_value_layer_distribution(layers: &[MaestroLayerDistribution]) -> Vec<Value> {
    layers
        .iter()
        .map(|layer| {
            json!({
                "layer_id": layer.layer_id,
                "layer_name": layer.layer_name,
                "finding_count": layer.finding_count,
                "highest_severity": layer.highest_severity,
            })
        })
        .collect()
}

fn to_value_heatmap(heatmap: &[MaestroHeatmapRow]) -> Vec<Value> {
    let mut rows = Vec::new();

    for row in heatmap {
        let mut value_map: Map<String, Value> = Map::new();
        value_map.insert(
            String::from("component"),
            Value::String(row.component.clone()),
        );

        for layer in crate::coverage_taxonomy::MAESTRO_LAYERS {
            value_map.insert(
                layer.to_string(),
                match row.layers.get(layer) {
                    Some(Some(score)) => Value::String(score.clone()),
                    _ => Value::Null,
                },
            );
        }

        rows.push(Value::Object(value_map));
    }

    rows
}

#[cfg(test)]
mod tests {
    use super::build_maestro_stack_template_data;
    use crate::infographic::{
        MaestroData, MaestroFinding, MaestroHeatmapRow, MaestroLayerDistribution,
    };
    use std::collections::BTreeMap;

    #[test]
    fn build_maestro_stack_template_data_exposes_layer_summaries() {
        let data = MaestroData {
            maestro_layer_distribution: vec![MaestroLayerDistribution {
                layer_id: String::from("L2"),
                layer_name: String::from("Data Operations"),
                finding_count: 1,
                highest_severity: String::from("High"),
            }],
            most_exposed_layer: String::from("L2 — Data Operations"),
            component_layer_map: BTreeMap::new(),
            per_finding_maestro: vec![MaestroFinding {
                id: String::from("S-1"),
                component: String::from("Agent"),
                maestro_layer: String::from("L2 — Data Operations"),
                risk_level: String::from("High"),
                threat: String::from("Prompt override"),
            }],
            maestro_heatmap: vec![MaestroHeatmapRow {
                component: String::from("Agent"),
                layers: BTreeMap::new(),
            }],
            has_maestro_data: true,
        };

        let actual = build_maestro_stack_template_data(&data);
        assert_eq!(actual["has_maestro_data"], true);
        assert_eq!(actual["per_layer_summaries"][0]["layer_id"], "L2");
    }
}
