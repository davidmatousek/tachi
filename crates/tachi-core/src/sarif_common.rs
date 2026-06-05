use std::collections::BTreeMap;

use serde_json::{Map, Value};

use crate::parsers::parse_scope_data;

pub const SARIF_SCHEMA_URI: &str = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ComponentMetadata {
    pub zone: String,
    pub dfd_type: String,
}

pub fn prefix_for(finding_id: &str) -> String {
    finding_id
        .rsplit_once('-')
        .map(|(prefix, _)| prefix.to_string())
        .unwrap_or_else(|| finding_id.to_string())
}

pub fn level_for_band(band: &str) -> &'static str {
    match band {
        "Critical" | "High" => "error",
        "Medium" => "warning",
        "Low" | "Note" => "note",
        _ => "warning",
    }
}

pub fn parse_component_metadata(threats_md: &str) -> BTreeMap<String, ComponentMetadata> {
    let scope = parse_scope_data(threats_md);
    let mut out = BTreeMap::new();

    for component in scope.components {
        if component.name.is_empty() {
            continue;
        }
        out.insert(
            component.name.clone(),
            ComponentMetadata {
                zone: String::from("Application Zone"),
                dfd_type: component.kind,
            },
        );
    }

    for boundary in scope.trust_boundaries {
        if boundary.zone.is_empty() {
            continue;
        }
        for member in boundary.components.split(',').map(str::trim) {
            if let Some(entry) = out.get_mut(member) {
                entry.zone = boundary.zone.clone();
            }
        }
    }

    out
}

pub fn build_sarif_envelope(
    driver: Value,
    taxonomies: Vec<Value>,
    results: Vec<Value>,
    schema_first: bool,
) -> Value {
    let mut envelope = Map::new();
    if schema_first {
        envelope.insert(
            "$schema".to_string(),
            Value::String(SARIF_SCHEMA_URI.to_string()),
        );
        envelope.insert("version".to_string(), Value::String(String::from("2.1.0")));
    } else {
        envelope.insert("version".to_string(), Value::String(String::from("2.1.0")));
        envelope.insert(
            "$schema".to_string(),
            Value::String(SARIF_SCHEMA_URI.to_string()),
        );
    }

    let mut run = Map::new();
    let mut tool = Map::new();
    tool.insert("driver".to_string(), driver);
    run.insert("tool".to_string(), Value::Object(tool));
    run.insert("taxonomies".to_string(), Value::Array(taxonomies));
    run.insert("results".to_string(), Value::Array(results));

    envelope.insert("runs".to_string(), Value::Array(vec![Value::Object(run)]));
    Value::Object(envelope)
}
