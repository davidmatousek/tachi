use std::fs;
use std::path::{Path, PathBuf};

#[test]
fn yaml_import_invariant_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_pyyaml_deferred_import.py")
            .exists(),
        "YAML import coverage should live in Rust tests, not pytest"
    );

    let scripts = discover_yaml_referencing_scripts(&root);
    assert!(
        !scripts.is_empty(),
        "expected at least one yaml-referencing script under scripts/"
    );
    assert!(
        scripts
            .iter()
            .any(|path| path.ends_with("scripts/extract-report-data.py")),
        "extract-report-data.py should stay in the YAML import invariant scope"
    );

    let violations: Vec<String> = scripts
        .iter()
        .flat_map(|path| {
            let source = fs::read_to_string(path).expect("read script");
            yaml_import_violations(path, &source)
        })
        .collect();

    assert!(
        violations.is_empty(),
        "module-level yaml imports violate the stdlib-only module-load invariant:\n{}",
        violations.join("\n")
    );
}

#[test]
fn yaml_import_detector_handles_module_function_and_class_bodies() {
    let synthetic = Path::new("synthetic.py");

    assert_eq!(
        yaml_import_violations(synthetic, "import yaml\n"),
        vec![String::from("synthetic.py:1 - import yaml")]
    );
    assert!(yaml_import_violations(synthetic, "def load():\n    import yaml\n").is_empty());
    assert!(yaml_import_violations(
        synthetic,
        "def load(\n    name: str,\n) -> list:\n    import yaml\n"
    )
    .is_empty());
    assert_eq!(
        yaml_import_violations(synthetic, "class Loader:\n    import yaml\n"),
        vec![String::from("synthetic.py:2 - import yaml")]
    );
    assert_eq!(
        yaml_import_violations(synthetic, "from yaml import safe_load\n"),
        vec![String::from("synthetic.py:1 - from yaml import safe_load")]
    );
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn discover_yaml_referencing_scripts(root: &Path) -> Vec<PathBuf> {
    let scripts_dir = root.join("scripts");
    let mut scripts = Vec::new();

    for entry in fs::read_dir(scripts_dir).expect("read scripts directory") {
        let path = entry.expect("read script entry").path();
        if path.extension().and_then(|ext| ext.to_str()) != Some("py") {
            continue;
        }
        let source = fs::read_to_string(&path).expect("read script");
        if source.contains("yaml") {
            scripts.push(path);
        }
    }

    scripts.sort();
    scripts
}

fn yaml_import_violations(path: &Path, source: &str) -> Vec<String> {
    let mut violations = Vec::new();
    let mut function_indent_stack: Vec<usize> = Vec::new();
    let mut pending_function_indent: Option<usize> = None;

    for (index, line) in source.lines().enumerate() {
        let trimmed = line.trim_start();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let indent = line.len() - trimmed.len();
        while function_indent_stack
            .last()
            .is_some_and(|function_indent| indent <= *function_indent)
        {
            function_indent_stack.pop();
        }

        if is_yaml_import(trimmed) && function_indent_stack.is_empty() {
            violations.push(format!("{}:{} - {}", path.display(), index + 1, trimmed));
        }

        if is_function_start(trimmed) {
            pending_function_indent = Some(indent);
        }
        if let Some(function_indent) = pending_function_indent.filter(|_| trimmed.ends_with(':')) {
            function_indent_stack.push(function_indent);
            pending_function_indent = None;
        } else if is_single_line_function_definition(trimmed) {
            function_indent_stack.push(indent);
        }
    }

    violations
}

fn is_yaml_import(trimmed: &str) -> bool {
    trimmed == "import yaml"
        || trimmed.starts_with("import yaml ")
        || trimmed.starts_with("import yaml.")
        || trimmed.starts_with("from yaml import ")
        || trimmed.starts_with("from yaml.")
}

fn is_function_start(trimmed: &str) -> bool {
    trimmed.starts_with("def ") || trimmed.starts_with("async def ")
}

fn is_single_line_function_definition(trimmed: &str) -> bool {
    (trimmed.starts_with("def ") || trimmed.starts_with("async def ")) && trimmed.ends_with(':')
}
