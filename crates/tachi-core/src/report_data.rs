use std::fs;
use std::path::Path;

use crate::assets::detect_images;
use crate::coverage_attestation::{
    build_per_finding_rows, build_per_framework_aggregates, CoverageFindingRow,
    CoverageFrameworkAggregate, CoverageReference,
};
use crate::parsers::{compute_has_source_attribution, parse_project_name, parse_threats_findings};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReportImageBinding {
    pub has_name: &'static str,
    pub path_name: &'static str,
    pub path: Option<String>,
}

pub fn build_report_data_typst(target_dir: &Path, template_dir: &Path) -> String {
    let images = detect_images(target_dir, template_dir);
    let project_name = parse_report_project_name(target_dir);
    let threats_content = fs::read_to_string(target_dir.join("threats.md")).unwrap_or_default();
    let findings = parse_threats_findings(&threats_content).unwrap_or_default();
    let has_source_attribution = compute_has_source_attribution(&findings);
    let per_finding_rows = build_per_finding_rows(&findings);
    let per_framework_aggregates = build_per_framework_aggregates(&findings);

    let mut output = render_report_data_typst(
        &project_name,
        &[
            ReportImageBinding {
                has_name: "has-funnel-image",
                path_name: "funnel-image-path",
                path: images.funnel_image_path,
            },
            ReportImageBinding {
                has_name: "has-baseball-image",
                path_name: "baseball-image-path",
                path: images.baseball_image_path,
            },
            ReportImageBinding {
                has_name: "has-architecture-image",
                path_name: "architecture-image-path",
                path: images.architecture_image_path,
            },
            ReportImageBinding {
                has_name: "has-maestro-stack-image",
                path_name: "maestro-stack-image-path",
                path: images.maestro_stack_image_path,
            },
            ReportImageBinding {
                has_name: "has-maestro-heatmap-image",
                path_name: "maestro-heatmap-image-path",
                path: images.maestro_heatmap_image_path,
            },
            ReportImageBinding {
                has_name: "has-executive-architecture",
                path_name: "executive-architecture-image-path",
                path: images.executive_architecture_image_path,
            },
        ],
    );
    output.push_str(&render_coverage_attestation_typst(
        has_source_attribution,
        &per_finding_rows,
        &per_framework_aggregates,
    ));
    output
}

fn render_report_data_typst(project_name: &str, bindings: &[ReportImageBinding]) -> String {
    let mut lines = Vec::with_capacity(bindings.len() * 2 + 1);
    lines.push(format!(
        "#let project-name = {}",
        typst_string(project_name)
    ));

    for binding in bindings {
        let has_image = binding.path.is_some();
        lines.push(format!("#let {} = {}", binding.has_name, has_image));
        lines.push(format!(
            "#let {} = {}",
            binding.path_name,
            typst_string(binding.path.as_deref().unwrap_or(""))
        ));
    }

    lines.join("\n") + "\n"
}

fn render_coverage_attestation_typst(
    has_source_attribution: bool,
    per_finding_rows: &[CoverageFindingRow],
    per_framework_aggregates: &[CoverageFrameworkAggregate],
) -> String {
    let mut lines = Vec::new();
    lines.push(String::from(
        "// --- Coverage Attestation Data ----------------------------------------------",
    ));
    lines.push(format!(
        "#let has-source-attribution = {}",
        has_source_attribution
    ));

    if per_finding_rows.is_empty() {
        lines.push(String::from("#let per-finding-rows = ()"));
    } else {
        lines.push(String::from("#let per-finding-rows = ("));
        for row in per_finding_rows {
            lines.push(format!(
                "  (id: {}, title: {}, severity: {}, owasp-refs: {}, mitre-refs: {}, nist-refs: {}, cwe-refs: {}),",
                typst_string(&row.id),
                typst_string(&row.title),
                typst_string(&row.severity),
                render_reference_group(&row.owasp_refs),
                render_reference_group(&row.mitre_refs),
                render_reference_group(&row.nist_refs),
                render_reference_group(&row.cwe_refs),
            ));
        }
        lines.push(String::from(")"));
    }

    if per_framework_aggregates.is_empty() {
        lines.push(String::from("#let per-framework-aggregates = ()"));
    } else {
        lines.push(String::from("#let per-framework-aggregates = ("));
        for aggregate in per_framework_aggregates {
            let items = render_framework_items(&aggregate.items);
            lines.push(format!(
                "  (framework: {}, yaml-record-count: {}, in-scope-record-count: {}, covered-count: {}, partial-count: {}, gap-count: {}, coverage-percentage: {}, items: {}),",
                typst_string(&aggregate.framework),
                aggregate.yaml_record_count,
                aggregate.in_scope_yaml_record_count,
                aggregate.covered_count,
                aggregate.partial_count,
                aggregate.gap_count,
                typst_string(&aggregate.coverage_percentage),
                items,
            ));
        }
        lines.push(String::from(")"));
    }

    lines.push(String::new());
    lines.join("\n") + "\n"
}

fn render_reference_group(items: &[CoverageReference]) -> String {
    if items.is_empty() {
        return String::from("()");
    }

    let inner = items
        .iter()
        .map(|item| {
            format!(
                "(id: {}, relationship: {})",
                typst_string(&item.id),
                typst_string(&item.relationship)
            )
        })
        .collect::<Vec<_>>()
        .join(", ");
    format!("({inner},)")
}

fn render_framework_items(items: &[crate::coverage_attestation::CoverageFrameworkItem]) -> String {
    if items.is_empty() {
        return String::from("()");
    }

    let inner = items
        .iter()
        .map(|item| {
            format!(
                "(id: {}, classification: {})",
                typst_string(&item.id),
                typst_string(&item.classification)
            )
        })
        .collect::<Vec<_>>()
        .join(", ");
    format!("({inner},)")
}

fn parse_report_project_name(target_dir: &Path) -> String {
    let threats_content = fs::read_to_string(target_dir.join("threats.md")).unwrap_or_default();
    parse_project_name(&threats_content, None, Some(target_dir))
}

fn typst_string(value: &str) -> String {
    let escaped = value.replace('\\', "\\\\").replace('"', "\\\"");
    format!("\"{escaped}\"")
}
