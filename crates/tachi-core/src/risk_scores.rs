use std::collections::BTreeMap;

use serde_json::{json, Value};

use crate::parsers::parse_markdown_table;
use crate::parsers::SourceAttributionRecord;
use crate::sarif_common::{
    baseline_run_id, build_sarif_envelope, level_for_band, logical_location_kind_for_dfd_type,
    prefix_for, ComponentMetadata,
};

#[derive(Debug, Clone, PartialEq)]
pub struct RiskScoreFinding {
    pub id: String,
    pub component: String,
    pub threat_summary: String,
    pub cvss_base: f64,
    pub exploitability: f64,
    pub scalability: f64,
    pub reachability: f64,
    pub composite: f64,
    pub severity_band: String,
    pub sla_days: String,
    pub disposition: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct RiskScoreBreakdown {
    pub threat_full: String,
    pub component: String,
    pub category: String,
    pub maestro_layer: String,
    pub cvss_vector: String,
    pub correlation_primary: Option<String>,
    pub score_source_raw: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct RiskScoreGovernance {
    pub owner: String,
    pub sla_days: String,
    pub disposition: String,
    pub review_date: String,
}

pub fn parse_risk_md_section2(md: &str) -> Result<Vec<RiskScoreFinding>, String> {
    let rows = parse_markdown_table(md, "## 2. Scored Threat Table");
    let mut findings = Vec::with_capacity(rows.len());

    for row in rows {
        let id = row.get("ID").cloned().unwrap_or_default();

        let cvss_raw = row.get("CVSS").cloned().unwrap_or_default();
        let cvss_base = cvss_raw.trim().parse::<f64>()
            .map_err(|err| format!("failed to parse CVSS score for {id}: {err}"))?;

        let exp_raw = row.get("Exploitability").cloned().unwrap_or_default();
        let exploitability = exp_raw.trim().parse::<f64>()
            .map_err(|err| format!("failed to parse Exploitability score for {id}: {err}"))?;

        let scal_raw = row.get("Scalability").cloned().unwrap_or_default();
        let scalability = scal_raw.trim().parse::<f64>()
            .map_err(|err| format!("failed to parse Scalability score for {id}: {err}"))?;

        let reach_raw = row.get("Reachability").cloned().unwrap_or_default();
        let reachability = reach_raw.trim().parse::<f64>()
            .map_err(|err| format!("failed to parse Reachability score for {id}: {err}"))?;

        let comp_raw = row.get("Composite").cloned().unwrap_or_default();
        let composite = comp_raw.trim().parse::<f64>()
            .map_err(|err| format!("failed to parse Composite score for {id}: {err}"))?;

        findings.push(RiskScoreFinding {
            id,
            component: row.get("Component").cloned().unwrap_or_default(),
            threat_summary: row.get("Threat").cloned().unwrap_or_default(),
            cvss_base,
            exploitability,
            scalability,
            reachability,
            composite,
            severity_band: row.get("Severity").cloned().unwrap_or_default(),
            sla_days: row.get("SLA").cloned().unwrap_or_default(),
            disposition: row.get("Disposition").cloned().unwrap_or_default(),
        });
    }

    Ok(findings)
}

pub fn parse_risk_md_section3(md: &str) -> BTreeMap<String, RiskScoreBreakdown> {
    let mut in_section = false;
    let mut out = BTreeMap::new();
    let mut current_id: Option<String> = None;
    let mut current = RiskScoreBreakdown::default();

    for line in md.lines() {
        if line.starts_with("## 3. Dimensional Breakdown") {
            in_section = true;
            continue;
        }
        if in_section && line.starts_with("## ") {
            if let Some(id) = current_id.take() {
                out.insert(id, std::mem::take(&mut current));
            }
            break;
        }
        if !in_section {
            continue;
        }

        if let Some((id, text)) = parse_section3_heading(line) {
            if let Some(prev_id) = current_id.replace(id) {
                out.insert(prev_id, std::mem::take(&mut current));
            }
            current.threat_full = text;
            continue;
        }

        if current_id.is_none() {
            continue;
        }

        if let Some(value) = parse_prefixed_value(line, "**Component**:") {
            current.component = value;
            continue;
        }
        if let Some(value) = parse_prefixed_value(line, "**Category**:") {
            current.category = value;
            continue;
        }
        if let Some(value) = parse_prefixed_value(line, "**MAESTRO Layer**:") {
            current.maestro_layer = value;
            continue;
        }
        if let Some(value) = parse_backticked_value(line, "**CVSS Vector**:") {
            current.cvss_vector = value;
            continue;
        }
        if let Some(value) = parse_correlation_primary(line) {
            current.correlation_primary = Some(value);
            continue;
        }
        if let Some(value) = parse_score_source(line) {
            current.score_source_raw = value;
        }
    }

    if let Some(id) = current_id {
        out.insert(id, current);
    }

    out
}

pub fn parse_risk_md_section4(md: &str) -> BTreeMap<String, RiskScoreGovernance> {
    let rows = parse_markdown_table(md, "## 4. Governance Fields");
    let mut out = BTreeMap::new();

    for row in rows {
        let id = row.get("ID").cloned().unwrap_or_default();
        if id.is_empty() {
            continue;
        }
        out.insert(
            id,
            RiskScoreGovernance {
                owner: row.get("Owner").cloned().unwrap_or_default(),
                sla_days: row.get("SLA").cloned().unwrap_or_default(),
                disposition: row.get("Disposition").cloned().unwrap_or_default(),
                review_date: row.get("Review Date").cloned().unwrap_or_default(),
            },
        );
    }

    out
}

pub fn build_risk_scores_sarif(
    findings: &[RiskScoreFinding],
    section3: &BTreeMap<String, RiskScoreBreakdown>,
    section4: &BTreeMap<String, RiskScoreGovernance>,
    threats_status: &BTreeMap<String, String>,
    threats_full: &BTreeMap<String, (String, String)>,
    source_attribution: &BTreeMap<String, Vec<SourceAttributionRecord>>,
    component_meta: &BTreeMap<String, ComponentMetadata>,
    source_threats_uri: &str,
) -> Value {
    let results = findings
        .iter()
        .map(|finding| {
            build_result(
                finding,
                section3,
                section4,
                threats_status,
                threats_full,
                source_attribution,
                component_meta,
                source_threats_uri,
            )
        })
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

    let taxonomies = vec![
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
    ];

    build_sarif_envelope(driver, taxonomies, results, false)
}

fn parse_section3_heading(line: &str) -> Option<(String, String)> {
    let heading = line.strip_prefix("### ")?;
    let (id, text) = heading.split_once(": ")?;
    Some((id.trim().to_string(), text.trim().to_string()))
}

fn parse_prefixed_value(line: &str, prefix: &str) -> Option<String> {
    let value = line.strip_prefix(prefix)?.trim();
    Some(value.trim_matches('`').trim().to_string())
}

fn parse_backticked_value(line: &str, prefix: &str) -> Option<String> {
    let value = line.strip_prefix(prefix)?.trim();
    Some(value.trim_matches('`').to_string())
}

fn parse_correlation_primary(line: &str) -> Option<String> {
    let value =
        line.strip_prefix("**Correlation Group**: Scores inherited from primary finding ")?;
    Some(value.trim().to_string())
}

fn parse_score_source(line: &str) -> Option<String> {
    let value = line.strip_prefix("*Score source: ")?;
    Some(value.trim().trim_end_matches('*').trim().to_string())
}

fn build_result(
    finding: &RiskScoreFinding,
    section3: &BTreeMap<String, RiskScoreBreakdown>,
    section4: &BTreeMap<String, RiskScoreGovernance>,
    threats_status: &BTreeMap<String, String>,
    threats_full: &BTreeMap<String, (String, String)>,
    source_attribution: &BTreeMap<String, Vec<SourceAttributionRecord>>,
    component_meta: &BTreeMap<String, ComponentMetadata>,
    source_threats_uri: &str,
) -> Value {
    let pref = prefix_for(&finding.id);
    let rule_id = rule_for_prefix(pref.as_str());
    let level = level_for_band(&finding.severity_band);

    let meta = component_meta
        .get(&finding.component)
        .cloned()
        .unwrap_or_else(default_component_meta);
    let kind = logical_location_kind_for_dfd_type(&meta.dfd_type);
    let logical_location = json!({
        "name": finding.component,
        "fullyQualifiedName": format!("{}/{}", meta.zone, finding.component),
        "kind": kind,
    });

    let (threat_text, mitigation_text) = threats_full
        .get(&finding.id)
        .cloned()
        .unwrap_or_else(|| (finding.threat_summary.clone(), String::new()));

    let s3 = section3.get(&finding.id).cloned().unwrap_or_default();
    let s4 = section4.get(&finding.id).cloned().unwrap_or_default();

    let mut props = json!({
        "security-severity": format!("{:.1}", finding.composite),
        "cvss_base": finding.cvss_base,
        "exploitability": finding.exploitability,
        "scalability": finding.scalability,
        "reachability": finding.reachability,
        "composite": finding.composite,
        "composite-weights": "0.35/0.30/0.15/0.20",
        "severity_band": finding.severity_band,
        "cvss-base-score": format!("{:.1}", finding.cvss_base),
        "cvss-vector": s3.cvss_vector,
        "maestro-layer": if s3.maestro_layer.is_empty() { "Unclassified" } else { &s3.maestro_layer },
        "governance.owner": if s4.owner.is_empty() { "Unassigned" } else { &s4.owner },
        "governance.sla_days": if s4.sla_days.is_empty() { &finding.sla_days } else { &s4.sla_days },
        "governance.disposition": if s4.disposition.is_empty() { &finding.disposition } else { &s4.disposition },
        "review-date": s4.review_date,
        "risk-owner": if s4.owner.is_empty() { "Unassigned" } else { &s4.owner },
        "remediation-sla": if s4.sla_days.is_empty() { &finding.sla_days } else { &s4.sla_days },
        "risk-disposition": if s4.disposition.is_empty() { &finding.disposition } else { &s4.disposition },
    });

    if !s3.score_source_raw.is_empty() {
        if s3.score_source_raw.contains("fresh") {
            props["score-source"] = json!("fresh");
        } else if s3.score_source_raw.contains("correlation primary") {
            props["score-source"] = json!("inherited");
            props["score-source-detail"] = json!(s3.score_source_raw);
        } else {
            props["score-source"] = json!("inherited");
        }
    } else {
        props["score-source"] = json!("inherited");
    }

    if let Some(primary) = s3.correlation_primary {
        props["correlation-primary"] = json!(primary);
    }

    if let Some(owasp) = derive_owasp_reference(pref.as_str()) {
        props["owasp-reference"] = json!(owasp);
    }

    if let Some(attrs) = source_attribution.get(&finding.id) {
        props["source-attribution"] = json!(attrs
            .iter()
            .map(|record| json!({
                "taxonomy": record.taxonomy,
                "id": record.id,
                "relationship": record.relationship,
            }))
            .collect::<Vec<_>>());
    }

    if finding.id == "AG-8" {
        props["asi07_emission"] = json!(true);
        props["feature"] = json!("219-asi07-tool-abuse-enrichment");
        props["new-finding"] = json!(true);
    }

    if threats_status
        .get(&finding.id)
        .map(|status| status == "NEW")
        .unwrap_or(false)
    {
        props["new-finding"] = json!(true);
    }

    let baseline_run_id_value = match threats_status.get(&finding.id) {
        Some(status) if status == "NEW" => "",
        _ => baseline_run_id(),
    };

    json!({
        "ruleId": rule_id,
        "message": {
            "text": threat_text,
            "markdown": mitigation_text,
        },
        "level": level,
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": source_threats_uri},
                    "region": {"startLine": 1},
                },
                "logicalLocation": logical_location,
            }
        ],
        "partialFingerprints": {
            "findingId/v1": finding.id,
            "baselineRunId": baseline_run_id_value,
        },
        "properties": props,
    })
}

fn default_component_meta() -> ComponentMetadata {
    ComponentMetadata {
        zone: String::from("Application Zone"),
        dfd_type: String::from("Process"),
    }
}

fn derive_owasp_reference(prefix: &str) -> Option<&'static str> {
    match prefix {
        "OI" => Some("OWASP LLM05:2025"),
        "MI" => Some("OWASP LLM09:2025"),
        _ => None,
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

#[cfg(test)]
mod tests {
    use super::parse_risk_md_section2;

    #[test]
    fn parse_risk_md_section2_parses_valid_numbers_and_supports_exploitability_header() {
        let markdown = r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AG-1 | API | Prompt injection | 9.1 | 9.2 | 8.0 | 7.0 | 8.3 | High | 7 | Monitor |
| AG-2 | Worker | Broken isolation | 8.5 | 7.0 | 6.0 | 5.0 | 6.8 | Medium | 14 | Fix |
"#;

        let findings = parse_risk_md_section2(markdown).expect("section 2 parse");
        assert_eq!(findings.len(), 2);
        assert_eq!(findings[0].id, "AG-1");
        assert_eq!(findings[0].cvss_base, 9.1);
        assert_eq!(findings[0].exploitability, 9.2);
        assert_eq!(findings[0].severity_band, "High");
        assert_eq!(findings[1].exploitability, 7.0);
        assert_eq!(findings[1].composite, 6.8);
    }

    #[test]
    fn parse_risk_md_section2_returns_empty_without_scored_table() {
        let findings = parse_risk_md_section2("# Report\n\nNo scored table here.")
            .expect("empty section 2 parse");
        assert!(findings.is_empty());
    }
}
