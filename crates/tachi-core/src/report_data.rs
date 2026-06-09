use std::fs;
use std::path::Path;

use crate::assets::detect_images;
use crate::parsers::parse_project_name;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReportImageBinding {
    pub has_name: &'static str,
    pub path_name: &'static str,
    pub path: Option<String>,
}

pub fn build_report_data_typst(target_dir: &Path, template_dir: &Path) -> String {
    let images = detect_images(target_dir, template_dir);
    let project_name = parse_report_project_name(target_dir);

    render_report_data_typst(
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
    )
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

fn parse_report_project_name(target_dir: &Path) -> String {
    let threats_content = fs::read_to_string(target_dir.join("threats.md")).unwrap_or_default();
    parse_project_name(&threats_content, None, Some(target_dir))
}

fn typst_string(value: &str) -> String {
    let escaped = value.replace('\\', "\\\\").replace('"', "\\\"");
    format!("\"{escaped}\"")
}
