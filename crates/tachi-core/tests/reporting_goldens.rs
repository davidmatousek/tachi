use std::collections::hash_map::DefaultHasher;
use std::collections::BTreeMap;
use std::fs;
use std::hash::{Hash, Hasher};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use pretty_assertions::assert_eq;
use serde_json::json;

use tachi_core::coverage_audit::render;
use tachi_core::infographic::build_infographic_payload_from_content;
use tachi_core::report_data::build_report_data_typst;
use tachi_core::sarif_common::{build_sarif_envelope, ComponentMetadata, SARIF_SCHEMA_URI};
use tachi_core::threats_sarif::{build_threats_sarif, ThreatSarifFinding};
use tachi_core::{
    coverage_audit::collect_audit,
    parsers::SourceAttributionRecord,
    risk_scores::{
        build_risk_scores_sarif, RiskScoreBreakdown, RiskScoreFinding, RiskScoreGovernance,
    },
};

const INFOGRAPHIC_THREATS_MD: &str = r#"
# Agentic AI Application

### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| LLM Agent Orchestrator | Service | L2 — Foundation Model |
| MCP Tool Server | Service | L2 — Foundation Model |
| Guardrails Service | Service | L5 — Infrastructure Controls |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
| --- | --- | --- |
| L2 — Foundation Model | 2 | High |
| L5 — Infrastructure Controls | 1 | Critical |

## 7. Recommended Actions

| Finding ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L2 — Foundation Model | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L2 — Foundation Model | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L5 — Infrastructure Controls | Critical | Model output exfiltration | Enforce egress controls |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 1 |
| High | 1 |
| Medium | 1 |
| Low | 0 |
| Note | 0 |
| Total | 3 |
"#;

fn temp_dir(prefix: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("monotonic clock")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{nanos}"))
}

fn write_text(path: &Path, content: &str) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent directories");
    }
    fs::write(path, content).expect("write test file");
}

fn line_hash_for(fid: &str) -> String {
    let mut hasher = DefaultHasher::new();
    fid.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

#[test]
fn coverage_audit_render_matches_canonical_inventory_golden() {
    let root = temp_dir("tachi-coverage-golden");
    write_text(&root.join("tests/scripts/test_smoke.py"), "print('smoke')");
    write_text(
        &root.join("tests/scripts/test_example_unit.py"),
        "print('unit')",
    );
    write_text(
        &root.join("tests/scripts/test_example_integration.py"),
        "print('integration')",
    );
    write_text(
        &root.join("crates/tachi-core/src/report_data.rs"),
        "pub fn placeholder() {}",
    );
    write_text(
        &root.join("crates/tachi-shell/tests/init_substitution.rs"),
        "#[test]\nfn placeholder() {}",
    );

    let audit = collect_audit(&root);
    let rendered = render(&audit, &root);
    let expected_lines = vec![
        format!("Coverage audit for {}", root.display()),
        String::from("Active test modules: 4"),
        String::from("Fixture-copy modules (excluded from active suite): 0"),
        String::new(),
        String::from("Unit: 1"),
        String::from("  - tests/scripts/test_example_unit.py"),
        String::new(),
        String::from("Integration: 1"),
        String::from("  - tests/scripts/test_example_integration.py"),
        String::new(),
        String::from("Smoke: 1"),
        String::from("  - tests/scripts/test_smoke.py"),
        String::new(),
        String::from("True end-to-end: 1"),
        String::from("  - crates/tachi-shell/tests/init_substitution.rs"),
        String::new(),
        String::from("Support / regression: 0"),
    ];
    let rendered_lines = rendered
        .lines()
        .take(expected_lines.len())
        .collect::<Vec<_>>();

    assert_eq!(rendered_lines, expected_lines);
}

#[test]
fn coverage_audit_render_preserves_semantic_section_invariants() {
    let root = temp_dir("tachi-coverage-semantic");
    write_text(&root.join("tests/scripts/test_smoke.py"), "print('smoke')");
    write_text(
        &root.join("tests/scripts/test_example_unit.py"),
        "print('unit')",
    );
    write_text(
        &root.join("tests/scripts/test_example_integration.py"),
        "print('integration')",
    );
    write_text(
        &root.join("crates/tachi-core/src/report_data.rs"),
        "pub fn placeholder() {}",
    );
    write_text(
        &root.join("crates/tachi-shell/tests/init_substitution.rs"),
        "#[test]\nfn placeholder() {}",
    );

    let audit = collect_audit(&root);
    let rendered = render(&audit, &root);

    assert!(rendered.contains(&format!("Coverage audit for {}", root.display())));
    assert!(rendered.contains("Active test modules: 4"));
    assert!(rendered.contains("Unit: 1"));
    assert!(rendered.contains("Integration: 1"));
    assert!(rendered.contains("Smoke: 1"));
    assert!(rendered.contains("True end-to-end: 1"));
    assert!(rendered.contains("Support / regression: 0"));
}

#[test]
fn build_report_data_typst_matches_canonical_golden() {
    let root = temp_dir("tachi-report-golden");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_text(
        &target_dir.join("threats.md"),
        "# Threat Model: Golden Report\n",
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);
    let expected_prefix = vec![
        "#let project-name = \"Golden Report\"",
        "#let has-funnel-image = false",
        "#let funnel-image-path = \"\"",
        "#let has-baseball-image = false",
        "#let baseball-image-path = \"\"",
        "#let has-architecture-image = false",
        "#let architecture-image-path = \"\"",
        "#let has-maestro-stack-image = false",
        "#let maestro-stack-image-path = \"\"",
        "#let has-maestro-heatmap-image = false",
        "#let maestro-heatmap-image-path = \"\"",
        "#let has-executive-architecture = false",
        "#let executive-architecture-image-path = \"\"",
        "// --- Coverage Attestation Data ----------------------------------------------",
        "#let has-source-attribution = false",
        "#let per-finding-rows = ()",
        "#let per-framework-aggregates = (",
    ];
    let rendered_prefix = rendered
        .lines()
        .take(expected_prefix.len())
        .collect::<Vec<_>>();

    assert_eq!(rendered_prefix, expected_prefix);
    assert!(rendered.contains("coverage-percentage: \"0.00%\""));
}

#[test]
fn threats_sarif_matches_canonical_golden() {
    let mut component_meta = BTreeMap::new();
    component_meta.insert(
        String::from("Agent"),
        ComponentMetadata {
            zone: String::from("Core"),
            dfd_type: String::from("Data Store"),
        },
    );

    let finding = ThreatSarifFinding {
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

    let actual = build_threats_sarif(std::slice::from_ref(&finding), &component_meta);
    let expected_result = json!({
        "ruleId": "tachi/ai/agentic",
        "message": {
            "text": finding.threat,
            "markdown": finding.mitigation,
        },
        "level": "error",
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "examples/agentic-app/sample-report/threats.md",
                    },
                    "region": {"startLine": 1},
                },
                "logicalLocations": [
                    {
                        "name": "Agent",
                        "fullyQualifiedName": "Core/Agent",
                        "kind": "data",
                    }
                ],
            }
        ],
        "partialFingerprints": {
            "primaryLocationLineHash": line_hash_for("AG-8"),
            "findingId/v1": "AG-8",
            "baselineRunId": "",
        },
        "properties": {
            "baselineState": "new",
            "tags": [
                "security",
                "ai",
                "agentic",
                "maestro-layer:L3",
                "maestro-pattern:trust_exploitation",
            ],
            "maestro-layer": "L3 Triage",
            "severity": "High",
            "likelihood": "High",
            "impact": "High",
            "maestro-pattern": "trust_exploitation",
            "asi07_emission": true,
            "feature": "219-asi07-tool-abuse-enrichment",
            "pattern_category": 9,
        },
    });
    let expected = build_sarif_envelope(
        json!({
            "name": "Tachi",
            "semanticVersion": "1.7",
            "informationUri": "https://github.com/pratik-saptarshi/tachi-rust",
            "supportedTaxonomies": [
                {"name": "OWASP", "index": 0},
                {"name": "CWE", "index": 1},
            ],
            "rules": [],
        }),
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
        ],
        vec![expected_result],
        true,
    );

    assert_eq!(actual, expected);
    assert_eq!(actual["$schema"], SARIF_SCHEMA_URI);
}

#[test]
fn risk_scores_sarif_matches_canonical_golden() {
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

    let mut component_meta = BTreeMap::new();
    component_meta.insert(
        String::from("Agent"),
        ComponentMetadata {
            zone: String::from("Core"),
            dfd_type: String::from("Data Store"),
        },
    );

    let actual = build_risk_scores_sarif(
        &findings,
        &section3,
        &section4,
        &threats_status,
        &threats_full,
        &source_attribution,
        &component_meta,
    );
    let expected_result = json!({
        "ruleId": "tachi/ai/agentic",
        "message": {
            "text": "Prompt injection",
            "markdown": "Harden prompts",
        },
        "level": "error",
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/threats.md",
                    },
                    "region": {"startLine": 1},
                },
                "logicalLocation": {
                    "name": "Agent",
                    "fullyQualifiedName": "Core/Agent",
                    "kind": "data-store",
                },
            }
        ],
        "partialFingerprints": {
            "findingId/v1": "AG-8",
        },
        "properties": {
            "security-severity": "8.8",
            "cvss_base": 9.1,
            "exploitability": 9.0,
            "scalability": 8.5,
            "reachability": 8.0,
            "composite": 8.8,
            "composite-weights": "0.35/0.30/0.15/0.20",
            "severity_band": "High",
            "cvss-base-score": "9.1",
            "cvss-vector": "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L",
            "maestro-layer": "L3 Triage",
            "governance.owner": "Alice",
            "governance.sla_days": "7",
            "governance.disposition": "Monitor",
            "review-date": "2026-06-06",
            "risk-owner": "Alice",
            "remediation-sla": "7",
            "risk-disposition": "Monitor",
            "score-source": "inherited",
            "score-source-detail": "correlation primary",
            "correlation-primary": "AG-3",
            "source-attribution": [
                {
                    "taxonomy": "OWASP",
                    "id": "LLM05:2025",
                    "relationship": "relevant",
                }
            ],
            "asi07_emission": true,
            "feature": "219-asi07-tool-abuse-enrichment",
            "new-finding": true,
        },
    });
    let expected = build_sarif_envelope(
        json!({
            "name": "Tachi",
            "semanticVersion": "1.7",
            "informationUri": "https://github.com/pratik-saptarshi/tachi-rust",
            "supportedTaxonomies": [
                {"name": "OWASP", "index": 0},
                {"name": "CWE", "index": 1},
            ],
            "rules": [],
        }),
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
        ],
        vec![expected_result],
        false,
    );

    assert_eq!(actual, expected);
}

#[test]
fn infographic_payload_matches_canonical_maestro_stack_golden() {
    let actual = build_infographic_payload_from_content(
        INFOGRAPHIC_THREATS_MD,
        2,
        String::from("Agentic AI Application"),
        None,
        None,
        "maestro-stack",
    )
    .expect("build infographic payload");

    let expected = json!({
        "template": "maestro-stack",
        "metadata": {
            "agent_count": 3,
            "data_source_type": "risk-scores",
            "note_count": 0,
            "project_name": "Agentic AI Application",
            "risk_posture": "Inherent risk — 1 Critical and 1 High findings across 3 components",
            "scan_date": "unknown",
            "schema_version": "1.1",
            "template": "maestro-stack",
            "tier": 2,
            "total_findings": 3,
        },
        "severity_distribution": [
            {"label": "Critical", "count": 1, "percentage": 34, "color": "#DC2626"},
            {"label": "High", "count": 1, "percentage": 33, "color": "#EA580C"},
            {"label": "Medium", "count": 1, "percentage": 33, "color": "#CA8A04"},
            {"label": "Low", "count": 0, "percentage": 0, "color": "#2563EB"},
        ],
        "heat_map": [
            {
                "component": "Guardrails Service",
                "critical": 1,
                "high": 0,
                "medium": 0,
                "low": 0,
                "total": 1,
            },
            {
                "component": "LLM Agent Orchestrator",
                "critical": 0,
                "high": 1,
                "medium": 0,
                "low": 0,
                "total": 1,
            },
            {
                "component": "MCP Tool Server",
                "critical": 0,
                "high": 0,
                "medium": 1,
                "low": 0,
                "total": 1,
            },
        ],
        "top_findings": [
            {
                "id": "I-1",
                "component": "Guardrails Service",
                "risk_level": "Critical",
                "score": 0.0,
                "threat": "Model output exfiltration",
            },
            {
                "id": "S-1",
                "component": "LLM Agent Orchestrator",
                "risk_level": "High",
                "score": 0.0,
                "threat": "Prompt override risk",
            },
            {
                "id": "A-1",
                "component": "MCP Tool Server",
                "risk_level": "Medium",
                "score": 0.0,
                "threat": "Tool abuse injection",
            },
        ],
        "findings_ids": ["I-1", "S-1", "A-1"],
        "template_data": {
            "maestro_layer_distribution": [
                {
                    "layer_id": "L2",
                    "layer_name": "Data Operations",
                    "finding_count": 2,
                    "highest_severity": "High",
                },
                {
                    "layer_id": "L5",
                    "layer_name": "Evaluation and Observability",
                    "finding_count": 1,
                    "highest_severity": "Critical",
                },
            ],
            "most_exposed_layer": "L2 — Data Operations",
            "per_layer_summaries": [
                {
                    "layer_id": "L2",
                    "layer_name": "Data Operations",
                    "finding_count": 2,
                    "highest_severity": "High",
                    "top_findings": [],
                },
                {
                    "layer_id": "L5",
                    "layer_name": "Evaluation and Observability",
                    "finding_count": 1,
                    "highest_severity": "Critical",
                    "top_findings": [],
                },
            ],
            "has_maestro_data": true,
        },
        "has_maestro_data": true,
        "prompt_scaffold": null,
    });

    assert_eq!(actual, expected);
}
