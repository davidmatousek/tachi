use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::coverage_attestation::{build_per_finding_rows, build_per_framework_aggregates};
use tachi_core::parsers::{SourceAttributionRecord, ThreatFinding};
use tachi_core::build_report_data_typst;

const OWASP_IDS: &[&str] = &[
    "LLM01", "LLM02", "LLM03", "LLM04", "LLM05", "LLM06", "LLM07", "LLM08", "LLM09", "LLM10",
    "A01", "A02", "A03", "A04", "A05",
];
const MITRE_ATTACK_IDS: &[&str] = &[
    "T1070.001",
    "T1078",
    "T1059",
    "T1082",
    "T1083",
    "T1021",
    "T1005",
    "T1110",
    "T1486",
    "T1566",
];
const MITRE_ATLAS_IDS: &[&str] = &[
    "AML.T0051",
    "AML.T0018",
    "AML.T0010",
    "AML.T0024",
    "AML.T0048",
];
const NIST_IDS: &[&str] = &[
    "MAP 4.2",
    "MEASURE 2.7",
    "MEASURE 2.10",
    "MANAGE 1.3",
    "GOVERN 1.4",
];
const CWE_IDS: &[&str] = &[
    "CWE-200", "CWE-1333", "CWE-79", "CWE-287", "CWE-306", "CWE-352", "CWE-862", "CWE-89",
    "CWE-78", "CWE-611",
];

const TAXONOMY_POOLS: &[(&str, &[&str])] = &[
    ("owasp", OWASP_IDS),
    ("mitre-attack", MITRE_ATTACK_IDS),
    ("mitre-atlas", MITRE_ATLAS_IDS),
    ("nist-ai-rmf", NIST_IDS),
    ("cwe", CWE_IDS),
];

const RELATIONSHIPS: &[&str] = &["primary", "related", "derived"];
const SEVERITIES: &[&str] = &["Critical", "High", "Medium", "Low"];

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn unique_temp_dir(prefix: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock should be monotonic")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{nanos}"))
}

fn write_text(path: &Path, content: &str) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent directories");
    }
    fs::write(path, content).expect("write test file");
}

fn generate_findings(count: usize) -> Vec<ThreatFinding> {
    let mut findings = Vec::with_capacity(count);

    for idx in 0..count {
        let prefix = ["S", "T", "R", "I", "D", "E", "LLM", "AG"][idx % 8];
        let severity = SEVERITIES[idx % SEVERITIES.len()];
        let citation_count = (idx % 4) + 1;
        let mut source_attribution = Vec::with_capacity(citation_count);

        for offset in 0..citation_count {
            let (taxonomy, ids) = TAXONOMY_POOLS[(idx + offset) % TAXONOMY_POOLS.len()];
            source_attribution.push(SourceAttributionRecord {
                taxonomy: taxonomy.to_string(),
                id: ids[(idx + offset) % ids.len()].to_string(),
                relationship: RELATIONSHIPS[(idx + offset) % RELATIONSHIPS.len()].to_string(),
            });
        }

        findings.push(ThreatFinding {
            id: format!("{prefix}-{:03}", idx + 1),
            component: format!("Component-{}", idx % 20 + 1),
            threat: format!("Synthetic threat {} for pagination smoke test", idx + 1),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: severity.to_string(),
            mitigation: format!("Synthetic mitigation {}", idx + 1),
            agentic_pattern: String::from("none"),
            delta_status: None,
            source_attribution: Some(source_attribution),
        });
    }

    findings
}

fn build_threats_markdown(findings: &[ThreatFinding], include_source_attribution: bool) -> String {
    let mut rendered = String::from(
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n",
    );

    for finding in findings {
        rendered.push_str(&format!(
            "| {} | {} | {} | {} | {} | [NEW] |\n",
            finding.id, finding.component, finding.threat, finding.risk_level, finding.mitigation
        ));
    }

    if include_source_attribution {
        rendered.push_str("\n## 9. Source Attribution\n\n```yaml\n");
        for finding in findings {
            rendered.push_str(&format!("{}:\n", finding.id));
            for citation in finding.source_attribution.as_deref().unwrap_or(&[]) {
                rendered.push_str(&format!(
                    "  - {{taxonomy: \"{}\", id: \"{}\", relationship: \"{}\"}}\n",
                    citation.taxonomy, citation.id, citation.relationship
                ));
            }
        }
        rendered.push_str("```\n");
    }

    rendered
}

fn compile_report_data(
    workspace_root: &Path,
    report_data: &str,
    output_pdf: &Path,
) -> std::process::Output {
    let template_dir = workspace_root.join("templates/tachi/security-report");
    let report_data_path = template_dir.join("report-data.typ");
    let backup = report_data_path
        .exists()
        .then(|| fs::read(&report_data_path).expect("backup report-data.typ"));

    write_text(&report_data_path, report_data);
    let output = Command::new("typst")
        .arg("compile")
        .arg(template_dir.join("main.typ"))
        .arg(output_pdf)
        .arg("--root")
        .arg(workspace_root)
        .current_dir(workspace_root)
        .output()
        .expect("run typst compile");

    if let Some(previous) = backup {
        fs::write(&report_data_path, previous).expect("restore report-data.typ");
    } else if report_data_path.exists() {
        fs::remove_file(&report_data_path).expect("remove temporary report-data.typ");
    }

    output
}

fn count_pdf_pages(pdf_path: &Path) -> usize {
    if let Ok(output) = Command::new("pdfinfo").arg(pdf_path).output() {
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            if let Some(line) = stdout.lines().find(|line| line.starts_with("Pages:")) {
                return line
                    .split_once(':')
                    .and_then(|(_, value)| value.trim().parse::<usize>().ok())
                    .unwrap_or(0);
            }
        }
    }

    let data = fs::read(pdf_path).expect("read generated pdf");
    data.windows(10)
        .filter(|window| *window == b"/Type /Page")
        .count()
}

#[test]
fn coverage_attestation_pagination_smoke_compiles_at_scale() {
    if !Command::new("typst")
        .arg("--version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
    {
        return;
    }

    let workspace = workspace_root();
    let template_dir = workspace.join("templates/tachi/security-report");
    let baseline_target = unique_temp_dir("tachi-pagination-baseline");
    let scale_target = unique_temp_dir("tachi-pagination-scale");

    let baseline_findings = generate_findings(1);
    let scale_findings = generate_findings(100);

    let frameworks = scale_findings
        .iter()
        .flat_map(|finding| finding.source_attribution.as_deref().unwrap_or(&[]))
        .map(|citation| citation.taxonomy.as_str())
        .collect::<BTreeSet<_>>();

    assert_eq!(
        frameworks,
        BTreeSet::from(["owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe",])
    );

    assert_eq!(build_per_finding_rows(&scale_findings).len(), 100);
    assert_eq!(build_per_framework_aggregates(&scale_findings).len(), 5);

    write_text(
        &baseline_target.join("examples/agentic-app/sample-report/threats.md"),
        &build_threats_markdown(&baseline_findings, false),
    );
    write_text(
        &scale_target.join("examples/agentic-app/sample-report/threats.md"),
        &build_threats_markdown(&scale_findings, true),
    );

    let baseline_report_data = build_report_data_typst(
        &baseline_target.join("examples/agentic-app/sample-report"),
        &template_dir,
    );
    let scale_report_data = build_report_data_typst(
        &scale_target.join("examples/agentic-app/sample-report"),
        &template_dir,
    );

    let baseline_pdf = baseline_target.join("baseline.pdf");
    let baseline_output = compile_report_data(&workspace, &baseline_report_data, &baseline_pdf);
    assert!(
        baseline_output.status.success(),
        "typst compile should succeed for the pagination baseline. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&baseline_output.stdout),
        String::from_utf8_lossy(&baseline_output.stderr)
    );

    let scale_pdf = scale_target.join("scale.pdf");
    let scale_output = compile_report_data(&workspace, &scale_report_data, &scale_pdf);
    assert!(
        scale_output.status.success(),
        "typst compile should succeed for the pagination smoke scale. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&scale_output.stdout),
        String::from_utf8_lossy(&scale_output.stderr)
    );

    let baseline_pages = count_pdf_pages(&baseline_pdf);
    let scale_pages = count_pdf_pages(&scale_pdf);

    assert!(
        scale_pages >= baseline_pages + 6,
        "expected pagination smoke compile to add at least 6 pages at 100-finding scale; baseline={baseline_pages}, scale={scale_pages}"
    );
}
