use std::collections::BTreeMap;
use std::path::Path;

use crate::parsers::ThreatFinding;
use serde::Serialize;
use serde_json::{json, Value};

use super::{
    allocate_executive_architecture_callouts, build_executive_architecture_callouts,
    build_executive_architecture_clusters, build_executive_architecture_flow_edges,
    build_executive_architecture_layers, parse_scope_data,
    qualifying_executive_architecture_findings,
};

#[derive(Debug, Clone, Serialize)]
pub(crate) struct ExecutiveArchitectureLayer {
    pub(crate) name: String,
    pub(crate) position: usize,
    pub(crate) components: Vec<String>,
    pub(crate) component_count: usize,
    pub(crate) source_kind: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub(crate) layer_overflow: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub(crate) struct ExecutiveArchitectureCallout {
    pub(crate) layer_name: String,
    pub(crate) finding_id: String,
    pub(crate) severity: String,
    pub(crate) raw_description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub(crate) composite_score: Option<f64>,
    pub(crate) affected_component: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub(crate) struct ExecutiveArchitectureFlowEdge {
    pub(crate) source: String,
    pub(crate) destination: String,
    pub(crate) data: String,
    pub(crate) protocol: String,
}

#[derive(Debug, Clone, Serialize)]
pub(crate) struct ExecutiveArchitectureCluster {
    pub(crate) name: String,
    pub(crate) members: Vec<String>,
    pub(crate) trust_level: String,
}

pub(crate) fn build_executive_architecture_template_data(
    threats_content: &str,
    tier: u8,
    source_file: Option<&Path>,
    findings: &[ThreatFinding],
) -> Result<Value, String> {
    let scope_data = parse_scope_data(threats_content);
    let (mut layers, fallback_used) = build_executive_architecture_layers(&scope_data)?;
    let flow_edges = build_executive_architecture_flow_edges(&scope_data);
    let clusters = build_executive_architecture_clusters(&scope_data);
    let per_layer_qualifying = qualifying_executive_architecture_findings(findings, &layers);
    let allocation = allocate_executive_architecture_callouts(&per_layer_qualifying);
    let callouts =
        build_executive_architecture_callouts(&layers, &per_layer_qualifying, &allocation);
    let callouts_per_layer = callouts.iter().fold(BTreeMap::new(), |mut acc, callout| {
        *acc.entry(callout.layer_name.clone()).or_insert(0) += 1;
        acc
    });

    for layer in &mut layers {
        let qualifying_count = per_layer_qualifying
            .get(&layer.name)
            .map(|items| items.len())
            .unwrap_or(0);
        let allocated = callouts_per_layer.get(&layer.name).copied().unwrap_or(0);
        if qualifying_count > allocated {
            layer.layer_overflow = Some(format!(
                "+ {} more in this layer",
                qualifying_count - allocated
            ));
        }
    }

    let critical_count = findings
        .iter()
        .filter(|finding| finding.risk_level.eq_ignore_ascii_case("Critical"))
        .count();
    let high_count = findings
        .iter()
        .filter(|finding| finding.risk_level.eq_ignore_ascii_case("High"))
        .count();
    let total_qualifying = critical_count + high_count;
    let skip_image = total_qualifying == 0;
    let source_file = source_file
        .map(|path| path.display().to_string())
        .unwrap_or_default();

    Ok(json!({
        "metadata": {
            "template_name": "executive-architecture",
            "tier_source": tier,
            "source_file": source_file,
            "generation_timestamp": "unknown",
            "qualifying_layer_count": layers.len(),
            "total_filtered_count": total_qualifying,
            "skip_image": skip_image,
            "fallback_used": fallback_used,
        },
        "layers": layers,
        "callouts": callouts,
        "severity_distribution": {
            "critical_count": critical_count,
            "high_count": high_count,
            "total_qualifying": total_qualifying,
            "total_after_layer_dedup": callouts.len(),
        },
        "flow_edges": flow_edges,
        "clusters": clusters,
    }))
}

#[cfg(test)]
mod tests {
    use super::build_executive_architecture_template_data;

    #[test]
    fn executive_architecture_template_data_rejects_missing_scope_data() {
        let err = build_executive_architecture_template_data("", 2, None, &[])
            .expect_err("empty scope should fail");
        assert_eq!(err, "no_scope_data");
    }
}
