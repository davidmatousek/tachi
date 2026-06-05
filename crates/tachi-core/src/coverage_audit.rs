use std::fs;
use std::path::{Path, PathBuf};

const SMOKE_MODULES: &[&str] = &[
    "tests/scripts/test_smoke.py",
    "tests/scripts/test_substitute_shim_canary.py",
    "tests/scripts/test_coverage_attestation_pagination.py",
    "tests/scripts/test_asset_sensitivity_tags.py",
];

const E2E_MODULES: &[&str] = &["tests/scripts/test_init_sh_substitution.py"];

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct CoverageAudit {
    pub active: Vec<PathBuf>,
    pub fixture_copies: Vec<PathBuf>,
    pub unit: Vec<PathBuf>,
    pub integration: Vec<PathBuf>,
    pub smoke: Vec<PathBuf>,
    pub e2e: Vec<PathBuf>,
    pub support: Vec<PathBuf>,
}

pub fn collect_audit(root: &Path) -> CoverageAudit {
    let tests_root = root.join("tests");
    let mut audit = CoverageAudit::default();

    if !tests_root.exists() {
        return audit;
    }

    let mut paths = Vec::new();
    collect_test_paths(&tests_root, &mut paths);
    paths.sort();

    for path in paths {
        let relpath = match path.strip_prefix(root) {
            Ok(relpath) => relpath.to_path_buf(),
            Err(_) => continue,
        };

        if relpath
            .components()
            .any(|component| component.as_os_str() == "fixtures")
        {
            audit.fixture_copies.push(relpath);
            continue;
        }

        audit.active.push(relpath.clone());
        match classify_test(&relpath) {
            TestCategory::Unit => audit.unit.push(relpath),
            TestCategory::Integration => audit.integration.push(relpath),
            TestCategory::Smoke => audit.smoke.push(relpath),
            TestCategory::E2E => audit.e2e.push(relpath),
            TestCategory::Support => audit.support.push(relpath),
        }
    }

    audit
}

pub fn render(audit: &CoverageAudit, root: &Path) -> String {
    let mut lines = Vec::new();
    lines.push(format!("Coverage audit for {}", root.display()));
    lines.push(format!("Active test modules: {}", audit.active.len()));
    lines.push(format!(
        "Fixture-copy modules (excluded from active suite): {}",
        audit.fixture_copies.len()
    ));
    lines.push(String::new());

    let sections = [
        ("Unit", &audit.unit),
        ("Integration", &audit.integration),
        ("Smoke", &audit.smoke),
        ("True end-to-end", &audit.e2e),
        ("Support / regression", &audit.support),
    ];

    for (label, files) in sections {
        lines.push(format!("{label}: {}", files.len()));
        for relpath in files {
            lines.push(format!("  - {}", relpath.display()));
        }
        lines.push(String::new());
    }

    if !audit.fixture_copies.is_empty() {
        lines.push("Fixture copies excluded from the active suite:".to_string());
        for relpath in &audit.fixture_copies {
            lines.push(format!("  - {}", relpath.display()));
        }
    }

    lines.join("\n").trim_end().to_string() + "\n"
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum TestCategory {
    Unit,
    Integration,
    Smoke,
    E2E,
    Support,
}

fn classify_test(relpath: &Path) -> TestCategory {
    let relpath_str = relpath.to_string_lossy();
    let name = relpath.file_name().and_then(|n| n.to_str()).unwrap_or("");

    if matches_explicit_module(relpath, SMOKE_MODULES) {
        return TestCategory::Smoke;
    }
    if matches_explicit_module(relpath, E2E_MODULES) {
        return TestCategory::E2E;
    }
    if name == "test_smoke.py" || name.contains("_smoke") {
        return TestCategory::Smoke;
    }
    if name.ends_with("_unit.py") {
        return TestCategory::Unit;
    }
    if name.ends_with("_integration.py") {
        return TestCategory::Integration;
    }
    if name.ends_with("_e2e.py") || relpath_str.contains("_e2e") {
        return TestCategory::E2E;
    }
    TestCategory::Support
}

fn matches_explicit_module(relpath: &Path, modules: &[&str]) -> bool {
    modules.iter().any(|module| relpath == Path::new(module))
}

fn collect_test_paths(dir: &Path, out: &mut Vec<PathBuf>) {
    let entries = match fs::read_dir(dir) {
        Ok(entries) => entries,
        Err(_) => return,
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            collect_test_paths(&path, out);
            continue;
        }

        let Some(name) = path.file_name().and_then(|n| n.to_str()) else {
            continue;
        };
        if name.starts_with("test_") && name.ends_with(".py") {
            out.push(path);
        }
    }
}
