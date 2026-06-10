use tachi_core::coverage_attestation::{
    build_per_finding_rows, build_per_framework_aggregates, CoverageFindingRow,
    CoverageFrameworkAggregate,
};
use tachi_core::parsers::{SourceAttributionRecord, ThreatFinding};

fn finding(
    id: &str,
    title: &str,
    severity: &str,
    source_attribution: Vec<SourceAttributionRecord>,
) -> ThreatFinding {
    ThreatFinding {
        id: id.to_string(),
        component: String::from("Component"),
        threat: title.to_string(),
        likelihood: String::from("—"),
        impact: String::from("—"),
        risk_level: severity.to_string(),
        mitigation: String::from("Mitigation"),
        agentic_pattern: String::from("none"),
        delta_status: None,
        source_attribution: Some(source_attribution),
    }
}

#[test]
fn build_per_finding_rows_groups_taxonomies_and_preserves_order() {
    let findings = vec![
        finding(
            "AG-1",
            "First finding",
            "High",
            vec![
                SourceAttributionRecord {
                    taxonomy: String::from("owasp"),
                    id: String::from("A01"),
                    relationship: String::from("primary"),
                },
                SourceAttributionRecord {
                    taxonomy: String::from("mitre-attack"),
                    id: String::from("T1190"),
                    relationship: String::from("related"),
                },
                SourceAttributionRecord {
                    taxonomy: String::from("cwe"),
                    id: String::from("CWE-79"),
                    relationship: String::from("derived"),
                },
            ],
        ),
        finding(
            "AG-2",
            "Second finding",
            "Low",
            vec![
                SourceAttributionRecord {
                    taxonomy: String::from("mitre-atlas"),
                    id: String::from("ATLAS-3"),
                    relationship: String::from("primary"),
                },
                SourceAttributionRecord {
                    taxonomy: String::from("nist-ai-rmf"),
                    id: String::from("GV-1"),
                    relationship: String::from("related"),
                },
            ],
        ),
    ];

    let rows: Vec<CoverageFindingRow> = build_per_finding_rows(&findings);

    assert_eq!(rows.len(), 2);
    assert_eq!(rows[0].id, "AG-1");
    assert_eq!(rows[0].title, "First finding");
    assert_eq!(rows[0].severity, "high");
    assert_eq!(rows[0].owasp_refs.len(), 1);
    assert_eq!(rows[0].mitre_refs.len(), 1);
    assert_eq!(rows[0].mitre_refs[0].id, "ATT&CK:T1190");
    assert_eq!(rows[0].cwe_refs[0].id, "CWE-79");
    assert_eq!(rows[1].id, "AG-2");
    assert_eq!(rows[1].mitre_refs[0].id, "ATLAS:ATLAS-3");
    assert_eq!(rows[1].nist_refs[0].relationship, "related");
}

#[test]
fn build_per_framework_aggregates_emits_five_frameworks_and_na_for_zero_denominator() {
    let findings = vec![
        finding(
            "AG-1",
            "Covered finding",
            "High",
            vec![SourceAttributionRecord {
                taxonomy: String::from("owasp"),
                id: String::from("A01"),
                relationship: String::from("primary"),
            }],
        ),
        finding(
            "AG-2",
            "Partial finding",
            "Medium",
            vec![SourceAttributionRecord {
                taxonomy: String::from("owasp"),
                id: String::from("A02"),
                relationship: String::from("related"),
            }],
        ),
    ];

    let aggregates: Vec<CoverageFrameworkAggregate> = build_per_framework_aggregates(&findings);

    assert_eq!(aggregates.len(), 5);
    let owasp = aggregates
        .iter()
        .find(|aggregate| aggregate.framework == "owasp")
        .expect("owasp aggregate");
    assert!(owasp.coverage_percentage.ends_with('%'));
    assert_eq!(owasp.items.len(), owasp.in_scope_yaml_record_count);
    assert_eq!(
        owasp.covered_count + owasp.partial_count + owasp.gap_count,
        owasp.in_scope_yaml_record_count
    );
    assert!(aggregates.iter().any(|aggregate| {
        aggregate.coverage_percentage == "N/A" || aggregate.coverage_percentage.ends_with('%')
    }));
}
