use tachi_core::facade::merge_source_attribution;
use tachi_core::parsers::{SourceAttributionRecord, ThreatFinding};

const SECTION_9_ON_TWO_FINDINGS: &str = r#"---
schema_version: "1.5"
---

# Threat Model

## 7. Findings

| ID | ... |

## 9. Source Attribution

```yaml
S-1:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-522, relationship: primary}
I-1:
  - {taxonomy: owasp, id: A02, relationship: primary}
```
"#;

const SECTION_9_PRESENT_BUT_EMPTY: &str = r#"---
schema_version: "1.5"
---

## 9. Source Attribution

```yaml
```
"#;

const NO_SECTION_9: &str = r#"---
schema_version: "1.5"
---

## 7. Findings

| ID | ... |

(no Section 9 here)
"#;

fn tier1_findings() -> Vec<ThreatFinding> {
    vec![
        ThreatFinding {
            id: String::from("S-1"),
            component: String::from("Component"),
            threat: String::from("API key spoofing"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Critical"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
        ThreatFinding {
            id: String::from("I-1"),
            component: String::from("Component"),
            threat: String::from("Credential disclosure"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Critical"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
        ThreatFinding {
            id: String::from("T-3"),
            component: String::from("Component"),
            threat: String::from("Config tampering"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Medium"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
    ]
}

fn tier2_findings() -> Vec<ThreatFinding> {
    vec![
        ThreatFinding {
            id: String::from("S-1"),
            component: String::from("Component"),
            threat: String::from("API key spoofing"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Critical"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
        ThreatFinding {
            id: String::from("I-1"),
            component: String::from("Component"),
            threat: String::from("Credential disclosure"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Medium"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
        ThreatFinding {
            id: String::from("T-3"),
            component: String::from("Component"),
            threat: String::from("Config tampering"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Low"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
    ]
}

#[test]
fn coverage_attestation_tiers_contract_is_rust_native() {
    let retired = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../tests/scripts/test_coverage_attestation_tiers.py");
    assert!(
        !retired.exists(),
        "pytest coverage_attestation_tiers should be retired once the Rust helper lands"
    );
}

#[test]
fn merge_attaches_attribution_on_matching_tier_1_findings() {
    let mut findings = tier1_findings();
    merge_source_attribution(&mut findings, SECTION_9_ON_TWO_FINDINGS);

    assert_eq!(
        findings[0].source_attribution,
        Some(vec![
            SourceAttributionRecord {
                taxonomy: String::from("owasp"),
                id: String::from("A07"),
                relationship: String::from("primary"),
            },
            SourceAttributionRecord {
                taxonomy: String::from("cwe"),
                id: String::from("CWE-522"),
                relationship: String::from("primary"),
            },
        ])
    );
    assert_eq!(
        findings[1].source_attribution,
        Some(vec![SourceAttributionRecord {
            taxonomy: String::from("owasp"),
            id: String::from("A02"),
            relationship: String::from("primary"),
        }])
    );
    assert!(findings[2].source_attribution.is_none());
}

#[test]
fn merge_attaches_attribution_on_matching_tier_2_findings() {
    let mut findings = tier2_findings();
    merge_source_attribution(&mut findings, SECTION_9_ON_TWO_FINDINGS);

    assert_eq!(
        findings[0].source_attribution,
        Some(vec![
            SourceAttributionRecord {
                taxonomy: String::from("owasp"),
                id: String::from("A07"),
                relationship: String::from("primary"),
            },
            SourceAttributionRecord {
                taxonomy: String::from("cwe"),
                id: String::from("CWE-522"),
                relationship: String::from("primary"),
            },
        ])
    );
    assert_eq!(
        findings[1].source_attribution,
        Some(vec![SourceAttributionRecord {
            taxonomy: String::from("owasp"),
            id: String::from("A02"),
            relationship: String::from("primary"),
        }])
    );
    assert!(findings[2].source_attribution.is_none());
}

#[test]
fn merge_is_noop_when_section_9_absent() {
    let mut findings = tier1_findings();
    merge_source_attribution(&mut findings, NO_SECTION_9);

    assert!(findings
        .iter()
        .all(|finding| finding.source_attribution.is_none()));
}

#[test]
fn merge_is_noop_when_section_9_header_present_but_block_empty() {
    let mut findings = tier1_findings();
    merge_source_attribution(&mut findings, SECTION_9_PRESENT_BUT_EMPTY);

    assert!(findings
        .iter()
        .all(|finding| finding.source_attribution.is_none()));
}

#[test]
fn merge_leaves_unmatched_findings_untouched() {
    let mut findings = vec![
        ThreatFinding {
            id: String::from("D-7"),
            component: String::from("Component"),
            threat: String::from("Only in findings, not in Section 9"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Low"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
        ThreatFinding {
            id: String::from("E-2"),
            component: String::from("Component"),
            threat: String::from("Also unmatched"),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: String::from("Low"),
            mitigation: String::from("Mitigation"),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: None,
        },
    ];

    merge_source_attribution(&mut findings, SECTION_9_ON_TWO_FINDINGS);

    assert!(findings
        .iter()
        .all(|finding| finding.source_attribution.is_none()));
}
