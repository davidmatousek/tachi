#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MermaidRenderFailure {
    pub id: String,
    pub file_path: String,
    pub failure_class: String,
    pub stderr_excerpt: String,
}

pub const MMDC_INSTALL_HINT: &str = "Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).\nInstall with: npm install -g @mermaid-js/mermaid-cli\nThen re-run /tachi.security-report.";

pub fn ensure_attack_path_renderer_available(
    attack_tree_count: usize,
    has_renderer: bool,
) -> Result<(), String> {
    if attack_tree_count == 0 || has_renderer {
        return Ok(());
    }

    Err(MMDC_INSTALL_HINT.to_string())
}

pub fn format_attack_path_render_failure_summary(failures: &[MermaidRenderFailure]) -> String {
    let mut lines = vec![format!(
        "Attack path rendering failed for {} findings:",
        failures.len()
    )];

    for failure in failures {
        lines.push(format!("  - {} ({})", failure.id, failure.file_path));
        lines.push(format!("    failure: {}", failure.failure_class));
        lines.push(format!("    stderr: {}", failure.stderr_excerpt));
    }

    lines.join("\n")
}
