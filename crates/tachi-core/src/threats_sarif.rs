use std::collections::hash_map::DefaultHasher;
use std::collections::BTreeMap;
use std::hash::{Hash, Hasher};

use serde_json::{json, Value};

use crate::sarif_common::{
    baseline_run_id, build_sarif_envelope, logical_location_kind_for_dfd_type, ComponentMetadata,
};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ThreatSarifFinding {
    pub id: String,
    pub prefix: String,
    pub status: String,
    pub component: String,
    pub maestro: String,
    pub agentic_pattern: String,
    pub threat: String,
    pub owasp_ref: String,
    pub likelihood: String,
    pub impact: String,
    pub risk_level: String,
    pub mitigation: String,
}

pub fn build_threats_sarif(
    findings: &[ThreatSarifFinding],
    component_meta: &BTreeMap<String, ComponentMetadata>,
    source_threats_uri: &str,
) -> Value {
    let results = findings
        .iter()
        .map(|finding| build_result(finding, component_meta, source_threats_uri))
        .collect::<Vec<_>>();

    let driver = json!({
        "name": "Tachi",
        "semanticVersion": "1.7",
        "informationUri": "https://github.com/pratik-saptarshi/tachi-rust",
        "supportedTaxonomies": [
            {"name": "OWASP", "index": 0},
            {"name": "CWE", "index": 1},
        ],
        "rules": [],
    });

    build_sarif_envelope(driver, taxonomies(), results, true)
}

fn build_result(
    finding: &ThreatSarifFinding,
    component_meta: &BTreeMap<String, ComponentMetadata>,
    source_threats_uri: &str,
) -> Value {
    let rule_id = rule_for_prefix(&finding.prefix);
    let level = level_for_risk(&finding.risk_level);

    let meta = component_meta
        .get(&finding.component)
        .cloned()
        .unwrap_or_else(default_component_meta);
    let kind = logical_location_kind_for_dfd_type(&meta.dfd_type);
    let fq = format!("{}/{}", meta.zone, finding.component);
    let owasp_id = normalize_owasp_id(&finding.owasp_ref, &finding.prefix);

    let mut tags = tags_for_prefix(&finding.prefix);
    if !finding.maestro.is_empty() && finding.maestro != "—" {
        let layer_short = finding
            .maestro
            .split_whitespace()
            .next()
            .filter(|token| token.starts_with('L'))
            .unwrap_or("Unclassified");
        tags.push(format!("maestro-layer:{layer_short}"));
    }
    if !finding.agentic_pattern.is_empty() {
        tags.push(format!("maestro-pattern:{}", finding.agentic_pattern));
    }

    let mut properties = json!({
        "baselineState": if finding.status == "[NEW]" { "new" } else { "unchanged" },
        "tags": tags,
        "maestro-layer": if finding.maestro.is_empty() { "Unclassified" } else { finding.maestro.as_str() },
        "severity": finding.risk_level,
        "likelihood": finding.likelihood,
        "impact": finding.impact,
    });

    if !finding.agentic_pattern.is_empty() {
        properties["maestro-pattern"] = json!(finding.agentic_pattern);
    }
    if !owasp_id.is_empty() {
        properties["owasp_id"] = json!(owasp_id);
    }
    if finding.id == "AG-8" {
        properties["asi07_emission"] = json!(true);
        properties["feature"] = json!("219-asi07-tool-abuse-enrichment");
        properties["pattern_category"] = json!(9);
    }

    json!({
        "ruleId": rule_id,
        "message": {
            "text": finding.threat,
            "markdown": finding.mitigation,
        },
        "level": level,
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": source_threats_uri,
                    },
                    "region": {"startLine": 1},
                },
                "logicalLocations": [
                    {
                        "name": finding.component,
                        "fullyQualifiedName": fq,
                        "kind": kind,
                    }
                ],
            }
        ],
        "partialFingerprints": {
            "primaryLocationLineHash": line_hash_for(&finding.id),
            "findingId/v1": finding.id,
            "baselineRunId": if finding.status == "[NEW]" { "" } else { baseline_run_id() },
        },
        "properties": properties,
    })
}

fn default_component_meta() -> ComponentMetadata {
    ComponentMetadata {
        zone: String::from("Application Zone"),
        dfd_type: String::from("Process"),
    }
}

fn level_for_risk(risk_level: &str) -> &'static str {
    match risk_level {
        "Critical" | "High" => "error",
        "Medium" => "warning",
        "Low" | "Note" => "note",
        _ => "note",
    }
}

fn tags_for_prefix(prefix: &str) -> Vec<String> {
    match prefix {
        "S" => vec![
            String::from("security"),
            String::from("stride"),
            String::from("spoofing"),
        ],
        "T" => vec![
            String::from("security"),
            String::from("stride"),
            String::from("tampering"),
        ],
        "R" => vec![
            String::from("security"),
            String::from("stride"),
            String::from("repudiation"),
        ],
        "I" => vec![
            String::from("security"),
            String::from("stride"),
            String::from("information-disclosure"),
        ],
        "D" => vec![
            String::from("security"),
            String::from("stride"),
            String::from("denial-of-service"),
        ],
        "E" => vec![
            String::from("security"),
            String::from("stride"),
            String::from("elevation-of-privilege"),
        ],
        "AG" => vec![
            String::from("security"),
            String::from("ai"),
            String::from("agentic"),
        ],
        "AGP" => vec![
            String::from("security"),
            String::from("ai"),
            String::from("agentic"),
            String::from("agentic-pattern"),
        ],
        "LLM" => vec![
            String::from("security"),
            String::from("ai"),
            String::from("llm"),
        ],
        "OI" => vec![
            String::from("security"),
            String::from("ai"),
            String::from("llm"),
            String::from("output-integrity"),
        ],
        "MI" => vec![
            String::from("security"),
            String::from("ai"),
            String::from("llm"),
            String::from("misinformation"),
        ],
        _ => vec![String::from("security")],
    }
}

fn rule_for_prefix(prefix: &str) -> &'static str {
    match prefix {
        "S" => "tachi/stride/spoofing",
        "T" => "tachi/stride/tampering",
        "R" => "tachi/stride/repudiation",
        "I" => "tachi/stride/information-disclosure",
        "D" => "tachi/stride/denial-of-service",
        "E" => "tachi/stride/elevation-of-privilege",
        "AG" | "AGP" => "tachi/ai/agentic",
        "LLM" | "OI" | "MI" => "tachi/ai/llm",
        _ => "tachi/ai/agentic",
    }
}

fn normalize_owasp_id(owasp_ref: &str, prefix: &str) -> String {
    let trimmed = owasp_ref.trim();
    if !trimmed.is_empty() {
        if let Some(rest) = trimmed.strip_prefix("OWASP LLM") {
            if let Some((num, _)) = rest.split_once(':') {
                if let Ok(value) = num.parse::<usize>() {
                    return format!("LLM-{value:02}");
                }
            }
        }
        if let Some(rest) = trimmed.strip_prefix("ASI") {
            let rest = rest.strip_prefix('-').unwrap_or(rest);
            if let Ok(value) = rest.parse::<usize>() {
                return format!("ASI-{value:02}");
            }
        }
        if let Some(rest) = trimmed.strip_prefix("MCP") {
            let rest = rest.strip_prefix('-').unwrap_or(rest);
            if let Ok(value) = rest.parse::<usize>() {
                return format!("MCP-{value:02}");
            }
        }
        return trimmed.to_string();
    }

    match prefix {
        "S" => String::from("A07"),
        "T" => String::from("A08"),
        "R" => String::from("A09"),
        "I" => String::from("A01"),
        "D" => String::from("A05"),
        "E" => String::from("A01"),
        _ => String::new(),
    }
}

fn line_hash_for(fid: &str) -> String {
    let mut hasher = DefaultHasher::new();
    fid.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

fn taxonomies() -> Vec<Value> {
    vec![
        json!({
            "name": "OWASP",
            "version": "2021",
            "informationUri": "https://owasp.org/Top10/",
            "organization": "OWASP Foundation",
            "shortDescription": {"text": "OWASP Top 10 Web Application Security Risks"},
        }),
        json!({
            "name": "CWE",
            "version": "4.13",
            "informationUri": "https://cwe.mitre.org/",
            "organization": "MITRE",
            "shortDescription": {"text": "Common Weakness Enumeration"},
        }),
    ]
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::{build_threats_sarif, ThreatSarifFinding};
    use crate::sarif_common::ComponentMetadata;

    #[test]
    fn build_threats_sarif_maps_prefix_classifier_precedence() {
        let mut component_meta = BTreeMap::new();
        component_meta.insert(
            String::from("Agent"),
            ComponentMetadata {
                zone: String::from("Core"),
                dfd_type: String::from("Process"),
            },
        );

        let findings = vec![
            ThreatSarifFinding {
                id: String::from("AG-1"),
                prefix: String::from("AG"),
                status: String::from("[NEW]"),
                component: String::from("Agent"),
                maestro: String::new(),
                agentic_pattern: String::new(),
                threat: String::from("Agentic threat"),
                owasp_ref: String::new(),
                likelihood: String::from("High"),
                impact: String::from("High"),
                risk_level: String::from("High"),
                mitigation: String::from("Mitigate"),
            },
            ThreatSarifFinding {
                id: String::from("AGP-1"),
                prefix: String::from("AGP"),
                status: String::from("[NEW]"),
                component: String::from("Agent"),
                maestro: String::new(),
                agentic_pattern: String::new(),
                threat: String::from("Agentic pattern threat"),
                owasp_ref: String::new(),
                likelihood: String::from("Medium"),
                impact: String::from("Medium"),
                risk_level: String::from("Medium"),
                mitigation: String::from("Mitigate"),
            },
            ThreatSarifFinding {
                id: String::from("LLM-1"),
                prefix: String::from("LLM"),
                status: String::from("[NEW]"),
                component: String::from("Agent"),
                maestro: String::new(),
                agentic_pattern: String::new(),
                threat: String::from("LLM threat"),
                owasp_ref: String::new(),
                likelihood: String::from("Low"),
                impact: String::from("Low"),
                risk_level: String::from("Low"),
                mitigation: String::from("Mitigate"),
            },
            ThreatSarifFinding {
                id: String::from("OI-1"),
                prefix: String::from("OI"),
                status: String::from("[NEW]"),
                component: String::from("Agent"),
                maestro: String::new(),
                agentic_pattern: String::new(),
                threat: String::from("Output integrity threat"),
                owasp_ref: String::new(),
                likelihood: String::from("Low"),
                impact: String::from("Low"),
                risk_level: String::from("Low"),
                mitigation: String::from("Mitigate"),
            },
            ThreatSarifFinding {
                id: String::from("MI-1"),
                prefix: String::from("MI"),
                status: String::from("[NEW]"),
                component: String::from("Agent"),
                maestro: String::new(),
                agentic_pattern: String::new(),
                threat: String::from("Misinformation threat"),
                owasp_ref: String::new(),
                likelihood: String::from("Low"),
                impact: String::from("Low"),
                risk_level: String::from("Low"),
                mitigation: String::from("Mitigate"),
            },
            ThreatSarifFinding {
                id: String::from("ZZ-1"),
                prefix: String::from("ZZ"),
                status: String::from("[NEW]"),
                component: String::from("Agent"),
                maestro: String::new(),
                agentic_pattern: String::new(),
                threat: String::from("Unknown threat"),
                owasp_ref: String::new(),
                likelihood: String::from("Note"),
                impact: String::from("Note"),
                risk_level: String::from("Note"),
                mitigation: String::from("Mitigate"),
            },
        ];

        let sarif = build_threats_sarif(&findings, &component_meta, "reports/internal/threats.md");
        let rule_ids = sarif["runs"][0]["results"]
            .as_array()
            .expect("results array")
            .iter()
            .map(|result| result["ruleId"].as_str().expect("rule id").to_owned())
            .collect::<Vec<_>>();

        assert_eq!(
            rule_ids,
            vec![
                String::from("tachi/ai/agentic"),
                String::from("tachi/ai/agentic"),
                String::from("tachi/ai/llm"),
                String::from("tachi/ai/llm"),
                String::from("tachi/ai/llm"),
                String::from("tachi/ai/agentic"),
            ]
        );
    }
}
