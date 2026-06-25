use std::collections::BTreeMap;

use pretty_assertions::assert_eq;
use tachi_core::sarif_common::{ComponentMetadata, SARIF_SCHEMA_URI};

#[test]
fn build_threats_sarif_marks_agentic_finding_with_asi07_metadata() {
    let mut component_meta = BTreeMap::new();
    component_meta.insert(
        String::from("Agent"),
        ComponentMetadata {
            zone: String::from("Core"),
            dfd_type: String::from("Data Store"),
        },
    );

    let finding = tachi_core::threats_sarif::ThreatSarifFinding {
        id: String::from("AG-8"),
        prefix: String::from("AG"),
        status: String::from("[NEW]"),
        component: String::from("Agent"),
        maestro: String::from("L3 Triage"),
        agentic_pattern: String::from("trust_exploitation"),
        threat: String::from("Prompt injection"),
        owasp_ref: String::new(),
        likelihood: String::from("High"),
        impact: String::from("High"),
        risk_level: String::from("High"),
        mitigation: String::from("Harden prompts"),
    };

    let source_threats_uri = "reports/custom/threats.md";
    let sarif = tachi_core::threats_sarif::build_threats_sarif(
        &[finding],
        &component_meta,
        source_threats_uri,
    );
    let run = &sarif["runs"][0];
    let result = &run["results"][0];

    assert_eq!(sarif["$schema"], SARIF_SCHEMA_URI);
    assert_eq!(sarif["version"], "2.1.0");
    assert_eq!(result["ruleId"], "tachi/ai/agentic");
    assert_eq!(result["level"], "error");
    assert_eq!(result["message"]["text"], "Prompt injection");
    assert_eq!(result["message"]["markdown"], "Harden prompts");
    assert_eq!(
        result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
        source_threats_uri
    );
    assert_eq!(
        result["locations"][0]["logicalLocations"][0]["fullyQualifiedName"],
        "Core/Agent"
    );
    assert_eq!(
        result["locations"][0]["logicalLocations"][0]["kind"],
        "data-store"
    );
    assert_eq!(result["partialFingerprints"]["findingId/v1"], "AG-8");
    assert_eq!(
        result["partialFingerprints"]["primaryLocationLineHash"]
            .as_str()
            .unwrap()
            .len(),
        16
    );
    assert_eq!(result["partialFingerprints"]["baselineRunId"], "");
    assert_eq!(result["properties"]["baselineState"], "new");
    assert_eq!(result["properties"]["maestro-layer"], "L3 Triage");
    assert_eq!(result["properties"]["asi07_emission"], true);
    assert_eq!(
        result["properties"]["feature"],
        "219-asi07-tool-abuse-enrichment"
    );
    assert_eq!(result["properties"]["pattern_category"], 9);
    assert_eq!(result["properties"]["tags"][0], "security");
    assert_eq!(result["properties"]["tags"][1], "ai");
}
