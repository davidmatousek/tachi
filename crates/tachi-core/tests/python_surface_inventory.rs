use std::fs;
use std::path::{Path, PathBuf};

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn collect_active_python_files(root: &Path) -> Vec<String> {
    let mut files = Vec::new();
    collect_python_files(root, root, &mut files);
    files.sort();
    files
}

fn collect_python_files(root: &Path, current: &Path, files: &mut Vec<String>) {
    let entries = match fs::read_dir(current) {
        Ok(entries) => entries,
        Err(_) => return,
    };

    for entry in entries.flatten() {
        let path = entry.path();
        let relative = match path.strip_prefix(root) {
            Ok(relative) => relative.to_string_lossy().replace('\\', "/"),
            Err(_) => continue,
        };

        if relative.contains("/fixtures/")
            || relative.starts_with("specs/")
            || relative.starts_with(".worktrees/")
            || relative.starts_with(".git/")
        {
            continue;
        }

        if path.is_dir() {
            collect_python_files(root, &path, files);
        } else if path.extension().and_then(|value| value.to_str()) == Some("py") {
            files.push(relative);
        }
    }
}

#[test]
fn python_surface_inventory_lists_every_active_python_file() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let expected_files = collect_active_python_files(&root);
    assert!(
        !expected_files.is_empty(),
        "expected to discover active python files in the workspace"
    );

    let missing: Vec<String> = expected_files
        .into_iter()
        .filter(|path| !inventory.contains(path))
        .collect();

    assert!(
        missing.is_empty(),
        "inventory is missing {} active python paths: {}",
        missing.len(),
        missing.join(", ")
    );

    for required in [
        "pyproject.toml",
        "requirements-dev.txt",
        "scripts/extract-infographic-data.py",
        "scripts/generate-threats-sarif.py",
        "scripts/generate-risk-scores-sarif.py",
        "scripts/tachi_parsers.py",
        "scripts/sarif_common.py",
    ] {
        assert!(
            inventory.contains(required),
            "inventory should mention {required}"
        );
    }
}

#[test]
fn python_surface_inventory_retired_sarif_scripts_are_no_longer_active() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    for retired in [
        "scripts/generate-threats-sarif.py",
        "scripts/generate-risk-scores-sarif.py",
        "scripts/sarif_common.py",
    ] {
        assert!(
            !active_section.contains(retired),
            "active inventory should no longer list retired SARIF script {retired}"
        );
    }
}

#[test]
fn python_surface_inventory_retires_pagination_smoke_python_modules() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    for retired in [
        "tests/scripts/generate_pagination_fixture.py",
        "tests/scripts/test_coverage_attestation_pagination.py",
        "tests/scripts/test_smoke.py",
    ] {
        assert!(
            !active_lines.contains(&retired),
            "active inventory should no longer list pagination smoke python module {retired}"
        );
    }
}

#[test]
fn python_surface_inventory_retires_attack_chain_extraction_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_attack_chain_extraction.py"),
        "active inventory should no longer list attack-chain extraction pytest coverage"
    );
}

#[test]
fn python_surface_inventory_retires_pattern_classification_rules_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_pattern_classification_rules.py"),
        "active inventory should no longer list pattern classification rules pytest coverage"
    );
}

#[test]
fn python_surface_inventory_retires_pattern_synthesis_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_pattern_synthesis.py"),
        "active inventory should no longer list pattern synthesis pytest coverage"
    );
}

#[test]
fn python_surface_inventory_retires_init_substitution_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_init_sh_substitution.py"),
        "active inventory should no longer list the init substitution pytest module"
    );
}

#[test]
fn python_surface_inventory_retires_init_constitution_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_init_sh_constitution.py"),
        "active inventory should no longer list the init constitution pytest module"
    );
}

#[test]
fn python_surface_inventory_retires_extract_report_data_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"scripts/extract-report-data.py"),
        "active inventory should no longer list the report-data Python runtime script"
    );
}

#[test]
fn python_surface_inventory_retires_mmdc_preflight_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_mmdc_preflight.py"),
        "active inventory should no longer list the mmdc preflight pytest module"
    );
}

#[test]
fn python_surface_inventory_retires_tool_abuse_enrichment_python_module() {
    let root = workspace_root();
    let inventory_path = root.join("docs/roadmap/2026-06-08-python-surface-inventory.md");
    let inventory = fs::read_to_string(&inventory_path)
        .expect("expected the python surface inventory doc to exist");

    let active_section = inventory
        .split("## Active Python Files")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active python files section");

    let active_lines = active_section.lines().map(str::trim).collect::<Vec<_>>();

    assert!(
        !active_lines.contains(&"tests/scripts/test_tool_abuse_enrichment.py"),
        "active inventory should no longer list tool abuse enrichment pytest coverage"
    );
}
