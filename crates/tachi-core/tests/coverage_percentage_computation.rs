use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

use tachi_core::coverage_attestation::{
    build_per_framework_aggregates_in_dir, CoverageFrameworkAggregate,
};
use tachi_core::facade::parse_compensating_controls_md;
use tachi_core::parsers::{parse_threats_findings, SourceAttributionRecord, ThreatFinding};

const FRAMEWORKS: [&str; 5] = ["owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"];

#[derive(Clone, Copy)]
struct Baseline {
    threats_path: &'static str,
    compensating_controls_path: Option<&'static str>,
}

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn stream_4_dir() -> PathBuf {
    repo_root().join("tests/scripts/fixtures/stream_4_coverage_percentage")
}

fn write_taxonomy_file(dir: &Path, framework: &str, content: &str) {
    fs::create_dir_all(dir).expect("create taxonomy dir");
    fs::write(dir.join(format!("{framework}.yaml")), content).expect("write taxonomy file");
}

fn temp_root(prefix: &str) -> PathBuf {
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("clock")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{nanos}"))
}

fn load_baseline_findings(baseline: &Baseline, root: &Path) -> Vec<ThreatFinding> {
    let threats_path = root.join(baseline.threats_path);
    let threats_content = fs::read_to_string(&threats_path).expect("read baseline threats.md");
    let threats_findings = parse_threats_findings(&threats_content).unwrap_or_default();

    let Some(compensating_controls_path) = baseline.compensating_controls_path else {
        return threats_findings;
    };

    let cc_content = fs::read_to_string(root.join(compensating_controls_path))
        .expect("read compensating-controls.md");
    let cc_data = parse_compensating_controls_md(&cc_content);

    let source_by_id: BTreeMap<String, Vec<SourceAttributionRecord>> = threats_findings
        .iter()
        .filter_map(|finding| {
            finding
                .source_attribution
                .as_ref()
                .map(|attrs| (finding.id.clone(), attrs.clone()))
        })
        .collect();

    cc_data
        .findings
        .into_iter()
        .map(|finding| ThreatFinding {
            id: finding.id.clone(),
            component: finding.component,
            threat: finding.threat,
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: finding.residual_severity,
            mitigation: finding.recommendation,
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: source_by_id.get(&finding.id).cloned(),
        })
        .collect()
}

fn independent_load_in_scope_record_ids(taxonomy_dir: &Path, framework_name: &str) -> Vec<String> {
    let path = taxonomy_dir.join(format!("{framework_name}.yaml"));
    let text = fs::read_to_string(path).unwrap_or_default();

    let mut records = Vec::new();
    let mut current: Option<(String, bool)> = None;

    for line in text.lines() {
        let trimmed_start = line.trim_start();
        if let Some(id) = trimmed_start.strip_prefix("- id: ") {
            if let Some((previous_id, out_of_scope)) = current.take() {
                if !out_of_scope {
                    records.push(previous_id);
                }
            }
            current = Some((id.trim().to_string(), false));
            continue;
        }

        let Some((_, out_of_scope)) = current.as_mut() else {
            continue;
        };

        if let Some(value) = line.trim().strip_prefix("out_of_scope:") {
            *out_of_scope = value.trim().eq_ignore_ascii_case("true");
        }
    }

    if let Some((previous_id, out_of_scope)) = current.take() {
        if !out_of_scope {
            records.push(previous_id);
        }
    }

    records
}

fn independent_count_covered(
    findings: &[ThreatFinding],
    framework_name: &str,
    in_scope_record_ids: &[String],
) -> usize {
    let mut covered = 0usize;

    for record_id in in_scope_record_ids {
        let mut record_is_covered = false;

        for finding in findings {
            let Some(source_attribution) = finding.source_attribution.as_deref() else {
                continue;
            };

            if source_attribution.iter().any(|reference| {
                reference.taxonomy == framework_name
                    && reference.id == *record_id
                    && reference.relationship == "primary"
            }) {
                record_is_covered = true;
                break;
            }
        }

        if record_is_covered {
            covered += 1;
        }
    }

    covered
}

fn independent_format_pct(covered: usize, in_scope: usize) -> String {
    if in_scope == 0 {
        return String::from("N/A");
    }

    format!("{:.2}%", (covered as f64 / in_scope as f64) * 100.0)
}

fn assert_aggregate_matches_independent(
    aggregate: &CoverageFrameworkAggregate,
    independent_in_scope: usize,
    independent_covered: usize,
) {
    assert_eq!(aggregate.in_scope_yaml_record_count, independent_in_scope);
    assert_eq!(aggregate.covered_count, independent_covered);
    assert_eq!(
        aggregate.coverage_percentage,
        independent_format_pct(independent_covered, independent_in_scope)
    );
}

#[test]
fn baseline_cross_check_matches_independent_percentage_formula() {
    let root = repo_root();
    let baselines = [
        Baseline {
            threats_path: "examples/web-app/threats.md",
            compensating_controls_path: None,
        },
        Baseline {
            threats_path: "examples/microservices/threats.md",
            compensating_controls_path: None,
        },
        Baseline {
            threats_path: "examples/ascii-web-api/threats.md",
            compensating_controls_path: None,
        },
        Baseline {
            threats_path: "examples/mermaid-agentic-app/threats.md",
            compensating_controls_path: None,
        },
        Baseline {
            threats_path: "examples/free-text-microservice/threats.md",
            compensating_controls_path: None,
        },
        Baseline {
            threats_path: "examples/maestro-reference/threats.md",
            compensating_controls_path: Some("examples/maestro-reference/compensating-controls.md"),
        },
        Baseline {
            threats_path: "examples/predictive-ml-app/sample-report/threats.md",
            compensating_controls_path: Some(
                "examples/predictive-ml-app/sample-report/compensating-controls.md",
            ),
        },
        Baseline {
            threats_path: "examples/mobile-banking-app/sample-report/threats.md",
            compensating_controls_path: Some(
                "examples/mobile-banking-app/sample-report/compensating-controls.md",
            ),
        },
    ];

    for baseline in baselines {
        let findings = load_baseline_findings(&baseline, &root);
        let aggregates =
            build_per_framework_aggregates_in_dir(&root.join("schemas/taxonomy"), &findings);

        for aggregate in aggregates {
            let in_scope_record_ids = independent_load_in_scope_record_ids(
                &root.join("schemas/taxonomy"),
                &aggregate.framework,
            );
            let independent_in_scope = in_scope_record_ids.len();
            let independent_covered =
                independent_count_covered(&findings, &aggregate.framework, &in_scope_record_ids);

            assert_aggregate_matches_independent(
                &aggregate,
                independent_in_scope,
                independent_covered,
            );
        }
    }
}

#[test]
fn mixed_and_oos_fixtures_match_expected_percentage_shape() {
    let root = repo_root();
    let fixture_dir = stream_4_dir();
    let mixed_findings = parse_threats_findings(
        &fs::read_to_string(fixture_dir.join("findings_mixed.yaml")).expect("read mixed fixture"),
    )
    .expect("parse mixed fixture");
    let oos_only_findings = parse_threats_findings(
        &fs::read_to_string(fixture_dir.join("findings_oos_only.yaml"))
            .expect("read oos-only fixture"),
    )
    .expect("parse oos-only fixture");

    let mixed_aggregates =
        build_per_framework_aggregates_in_dir(&root.join("schemas/taxonomy"), &mixed_findings);
    let oos_only_aggregates =
        build_per_framework_aggregates_in_dir(&root.join("schemas/taxonomy"), &oos_only_findings);

    for aggregate in mixed_aggregates {
        let in_scope_record_ids = independent_load_in_scope_record_ids(
            &root.join("schemas/taxonomy"),
            &aggregate.framework,
        );
        let independent_in_scope = in_scope_record_ids.len();
        let independent_covered =
            independent_count_covered(&mixed_findings, &aggregate.framework, &in_scope_record_ids);
        assert_aggregate_matches_independent(&aggregate, independent_in_scope, independent_covered);
    }

    for aggregate in oos_only_aggregates {
        let in_scope_record_ids = independent_load_in_scope_record_ids(
            &root.join("schemas/taxonomy"),
            &aggregate.framework,
        );
        let independent_in_scope = in_scope_record_ids.len();
        let independent_covered = independent_count_covered(
            &oos_only_findings,
            &aggregate.framework,
            &in_scope_record_ids,
        );
        assert_aggregate_matches_independent(&aggregate, independent_in_scope, independent_covered);
    }
}

#[test]
fn zero_denominator_and_missing_out_of_scope_default_behaviors_match() {
    let root = temp_root("tachi-coverage-percentage");
    let taxonomy_dir = root.join("schemas/taxonomy");

    for framework in FRAMEWORKS {
        write_taxonomy_file(
            &taxonomy_dir,
            framework,
            r#"- id: X01
  out_of_scope: false
- id: X02
  out_of_scope: true
"#,
        );
    }

    let findings = vec![ThreatFinding {
        id: String::from("F-1"),
        component: String::from("Component"),
        threat: String::from("Threat"),
        likelihood: String::from("—"),
        impact: String::from("—"),
        risk_level: String::from("High"),
        mitigation: String::from("Mitigation"),
        agentic_pattern: String::from("none"),
        delta_status: None,
        source_attribution: Some(vec![SourceAttributionRecord {
            taxonomy: String::from("owasp"),
            id: String::from("X02"),
            relationship: String::from("related"),
        }]),
    }];

    let aggregates = build_per_framework_aggregates_in_dir(&taxonomy_dir, &findings);
    let owasp = aggregates
        .iter()
        .find(|aggregate| aggregate.framework == "owasp")
        .expect("owasp aggregate");

    assert_eq!(owasp.yaml_record_count, 2);
    assert_eq!(owasp.in_scope_yaml_record_count, 1);
    assert_eq!(owasp.covered_count, 0);
    assert_eq!(owasp.coverage_percentage, "0.00%");
    assert_eq!(independent_format_pct(0, 1), "0.00%");

    let zero_root = temp_root("tachi-coverage-percentage-zero");
    let zero_taxonomy_dir = zero_root.join("schemas/taxonomy");
    for framework in FRAMEWORKS {
        write_taxonomy_file(
            &zero_taxonomy_dir,
            framework,
            r#"- id: Z01
  out_of_scope: true
"#,
        );
    }

    let zero_aggregates = build_per_framework_aggregates_in_dir(&zero_taxonomy_dir, &[]);
    let owasp_zero = zero_aggregates
        .iter()
        .find(|aggregate| aggregate.framework == "owasp")
        .expect("owasp zero aggregate");
    assert_eq!(owasp_zero.yaml_record_count, 1);
    assert_eq!(owasp_zero.in_scope_yaml_record_count, 0);
    assert_eq!(owasp_zero.coverage_percentage, "N/A");
    assert_eq!(independent_format_pct(0, 0), "N/A");
}
