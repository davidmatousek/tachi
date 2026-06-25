use pretty_assertions::assert_eq;
use std::collections::BTreeMap;
use tachi_core::parsers::SourceAttributionRecord;
use tachi_core::sarif_common::ComponentMetadata;
use tachi_core::{
    build_risk_scores_sarif, parse_risk_md_section2, parse_risk_md_section3,
    parse_risk_md_section4, RiskScoreBreakdown, RiskScoreFinding, RiskScoreGovernance,
};

#[test]
fn parse_risk_scores_sections_extracts_scored_table_metadata_and_governance() {
    let md = r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------------|--------------|--------------|-----------|----------|-----|-------------|
| AG-8 | Agent | Prompt injection | 9.1 | 9.0 | 8.5 | 8.0 | 8.8 | High | 7 | Monitor |

## 3. Dimensional Breakdown

### AG-8: Prompt injection

**Component**: Agent
**Category**: Agentic Threats
**MAESTRO Layer**: L3 Triage
**CVSS Vector**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`
**Correlation Group**: Scores inherited from primary finding AG-3
*Score source: correlation primary*

## 4. Governance Fields

| ID | Owner | SLA | Disposition | Review Date |
|----|-------|-----|-------------|-------------|
| AG-8 | Alice | 7 | Monitor | 2026-06-06 |
"#;

    let section2 = parse_risk_md_section2(md).expect("section 2 parse");
    let section3 = parse_risk_md_section3(md);
    let section4 = parse_risk_md_section4(md);

    assert_eq!(section2.len(), 1);
    assert_eq!(section2[0].id, "AG-8");
    assert_eq!(section2[0].component, "Agent");
    assert_eq!(section2[0].severity_band, "High");
    assert_eq!(section2[0].composite, 8.8);

    let s3 = section3.get("AG-8").expect("section 3 entry");
    assert_eq!(s3.threat_full, "Prompt injection");
    assert_eq!(s3.component, "Agent");
    assert_eq!(s3.category, "Agentic Threats");
    assert_eq!(s3.maestro_layer, "L3 Triage");
    assert_eq!(s3.correlation_primary.as_deref(), Some("AG-3"));
    assert_eq!(s3.score_source_raw, "correlation primary");

    let s4 = section4.get("AG-8").expect("section 4 entry");
    assert_eq!(s4.owner, "Alice");
    assert_eq!(s4.sla_days, "7");
    assert_eq!(s4.disposition, "Monitor");
    assert_eq!(s4.review_date, "2026-06-06");
}

#[test]
fn build_risk_scores_sarif_marks_inherited_agentic_finding() {
    let mut component_meta = BTreeMap::new();
    component_meta.insert(
        String::from("Agent"),
        ComponentMetadata {
            zone: String::from("Core"),
            dfd_type: String::from("Data Store"),
        },
    );

    let findings = vec![RiskScoreFinding {
        id: String::from("AG-8"),
        component: String::from("Agent"),
        threat_summary: String::from("Prompt injection"),
        cvss_base: 9.1,
        exploitability: 9.0,
        scalability: 8.5,
        reachability: 8.0,
        composite: 8.8,
        severity_band: String::from("High"),
        sla_days: String::from("7"),
        disposition: String::from("Monitor"),
    }];

    let mut section3 = BTreeMap::new();
    section3.insert(
        String::from("AG-8"),
        RiskScoreBreakdown {
            threat_full: String::from("Prompt injection"),
            component: String::from("Agent"),
            category: String::from("Agentic Threats"),
            maestro_layer: String::from("L3 Triage"),
            cvss_vector: String::from("AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L"),
            correlation_primary: Some(String::from("AG-3")),
            score_source_raw: String::from("correlation primary"),
        },
    );

    let mut section4 = BTreeMap::new();
    section4.insert(
        String::from("AG-8"),
        RiskScoreGovernance {
            owner: String::from("Alice"),
            sla_days: String::from("7"),
            disposition: String::from("Monitor"),
            review_date: String::from("2026-06-06"),
        },
    );

    let mut threats_status = BTreeMap::new();
    threats_status.insert(String::from("AG-8"), String::from("NEW"));

    let mut threats_full = BTreeMap::new();
    threats_full.insert(
        String::from("AG-8"),
        (
            String::from("Prompt injection"),
            String::from("Harden prompts"),
        ),
    );

    let mut source_attribution = BTreeMap::new();
    source_attribution.insert(
        String::from("AG-8"),
        vec![SourceAttributionRecord {
            taxonomy: String::from("OWASP"),
            id: String::from("LLM05:2025"),
            relationship: String::from("relevant"),
        }],
    );

    let sarif = build_risk_scores_sarif(
        &findings,
        &section3,
        &section4,
        &threats_status,
        &threats_full,
        &source_attribution,
        &component_meta,
    );

    let result = &sarif["runs"][0]["results"][0];

    assert_eq!(result["ruleId"], "tachi/ai/agentic");
    assert_eq!(result["level"], "error");
    assert_eq!(result["message"]["text"], "Prompt injection");
    assert_eq!(result["message"]["markdown"], "Harden prompts");
    assert_eq!(
        result["locations"][0]["logicalLocation"]["kind"],
        "data-store"
    );
    assert_eq!(result["properties"]["score-source"], "inherited");
    assert_eq!(
        result["properties"]["score-source-detail"],
        "correlation primary"
    );
    assert_eq!(result["properties"]["correlation-primary"], "AG-3");
    assert_eq!(
        result["properties"]["owasp-reference"],
        serde_json::Value::Null
    );
    assert_eq!(
        result["properties"]["source-attribution"][0]["id"],
        "LLM05:2025"
    );
    assert_eq!(result["properties"]["new-finding"], true);
    assert_eq!(result["properties"]["asi07_emission"], true);
    assert_eq!(
        result["properties"]["feature"],
        "219-asi07-tool-abuse-enrichment"
    );
}

#[test]
fn test_parse_risk_md_section2_returns_err_on_malformed_scores() {
    let md = r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------------|--------------|--------------|-----------|----------|-----|-------------|
| AG-8 | Agent | Prompt injection | malformed_score | 9.0 | 8.5 | 8.0 | 8.8 | High | 7 | Monitor |
"#;
    let res = parse_risk_md_section2(md);
    assert!(
        res.is_err(),
        "Expected error for malformed score, got {:?}",
        res
    );
    let err = res.expect_err("malformed score should be rejected");
    assert!(
        err.contains("failed to parse CVSS score for AG-8"),
        "unexpected error: {err}"
    );
}
