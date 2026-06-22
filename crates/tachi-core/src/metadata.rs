use std::fs;
use std::path::Path;

use crate::parsers::parse_threats_h1;

pub(crate) fn resolve_report_project_name(
    content: &str,
    title_override: Option<&str>,
    target_dir: Option<&Path>,
) -> String {
    if let Some(override_name) = title_override
        .map(str::trim)
        .filter(|name| !name.is_empty())
    {
        return override_name.to_string();
    }

    if let Some(name) = parse_threats_h1(content) {
        return name;
    }

    if let Some(dir) = target_dir {
        let architecture_path = dir.join("architecture.md");
        if let Ok(architecture) = fs::read_to_string(architecture_path) {
            if let Some(name) = parse_architecture_heading(&architecture) {
                return name;
            }
        }
    }

    String::from("Unknown Project")
}

fn parse_architecture_heading(content: &str) -> Option<String> {
    let first_h1 = content.lines().find_map(|line| {
        let trimmed = line.trim();
        trimmed.strip_prefix('#').map(|rest| rest.trim())
    })?;

    for separator in ['—', '–', '-'] {
        if let Some((left, right)) = first_h1.split_once(separator) {
            let left = left.trim();
            let right = right.trim();
            if right.eq_ignore_ascii_case("Architecture") {
                return normalize_project_name(left);
            }
            if left.eq_ignore_ascii_case("Architecture")
                || left.eq_ignore_ascii_case("Security Architecture")
            {
                return normalize_project_name(right);
            }
        }
    }

    None
}

fn normalize_project_name(value: &str) -> Option<String> {
    let normalized = value.trim();
    if normalized.is_empty() {
        None
    } else {
        Some(normalized.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::resolve_report_project_name;
    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn temp_test_dir() -> std::path::PathBuf {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos();
        let dir = std::env::temp_dir().join(format!("tachi-core-metadata-{stamp}-{}", std::process::id()));
        fs::create_dir_all(&dir).expect("create temp dir");
        dir
    }

    #[test]
    fn resolves_project_name_from_override_and_h1() {
        let temp_dir = temp_test_dir();
        fs::write(temp_dir.join("architecture.md"), "# Fallback — Architecture\n")
            .expect("architecture");

        assert_eq!(
            resolve_report_project_name(
                "# Alpha Threat Model\n",
                Some("Gamma"),
                Some(temp_dir.as_path()),
            ),
            "Gamma"
        );
        assert_eq!(
            resolve_report_project_name("# Alpha Threat Model\n", None, Some(temp_dir.as_path())),
            "Alpha"
        );
    }

    #[test]
    fn resolves_project_name_from_architecture_md_when_report_h1_missing() {
        let temp_dir = temp_test_dir();
        fs::write(temp_dir.join("architecture.md"), "# Beta — Architecture\n")
            .expect("architecture");

        assert_eq!(
            resolve_report_project_name("# Threat Model Report\n", None, Some(temp_dir.as_path())),
            "Beta"
        );
    }

    #[test]
    fn falls_back_to_unknown_when_no_signal_exists() {
        assert_eq!(resolve_report_project_name("", None, None), "Unknown Project");
    }
}
