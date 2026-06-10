use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[test]
fn template_substitute_shim_canary_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_substitute_shim_canary.py")
            .exists(),
        "template-substitute shim canary coverage should live in Rust tests, not pytest"
    );

    let helper_path = root.join(".aod/scripts/bash/template-substitute.sh");
    let helper_text = fs::read_to_string(&helper_path).expect("read template-substitute helper");

    assert!(
        helper_text.contains("shopt -u patsub_replacement"),
        "load-bearing bash 5.2 patsub_replacement shim removed from {}",
        helper_path.display()
    );
}

#[test]
fn template_substitute_no_eval_lint_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_template_substitute_lint_no_eval.py")
            .exists(),
        "template-substitute no-eval lint coverage should live in Rust tests, not pytest"
    );

    let helper_path = root.join(".aod/scripts/bash/template-substitute.sh");
    let helper_text = fs::read_to_string(&helper_path).expect("read template-substitute helper");

    let eval_matches = count_whole_word_eval(&helper_text);
    assert_eq!(
        eval_matches,
        0,
        "FR-007 violation: found {eval_matches} whole-word eval token(s) in {}",
        helper_path.display()
    );
}

#[test]
fn template_substitute_literal_project_names_are_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_template_substitute_unit.py")
            .exists(),
        "template-substitute literal substitution coverage should live in Rust tests, not pytest"
    );

    for case in substitution_cases() {
        let temp_dir = unique_temp_dir(case.id);
        fs::create_dir_all(&temp_dir).expect("create temp test directory");
        let source_path = temp_dir.join("src");
        let destination_path = temp_dir.join("dest");
        fs::write(&source_path, case.source).expect("write source template");

        let script = format!(
            "shopt -u patsub_replacement 2>/dev/null || true; \
             source '{}'; \
             aod_template_substitute_placeholders '{}' '{}'",
            root.join(".aod/scripts/bash/template-substitute.sh")
                .display(),
            source_path.display(),
            destination_path.display()
        );

        let output = Command::new("bash")
            .arg("-c")
            .arg(script)
            .current_dir(&root)
            .env_clear()
            .env("LC_ALL", "C")
            .env("PATH", std::env::var("PATH").expect("PATH available"))
            .env("AOD_PERSONALIZATION_PROJECT_NAME", case.project_name)
            .env(
                "AOD_PERSONALIZATION_PROJECT_DESCRIPTION",
                "stub-description",
            )
            .env("AOD_PERSONALIZATION_GITHUB_ORG", "stub-org")
            .env("AOD_PERSONALIZATION_GITHUB_REPO", "stub-repo")
            .env("AOD_PERSONALIZATION_AI_AGENT", "stub-agent")
            .env("AOD_PERSONALIZATION_TECH_STACK", "stub-stack")
            .env("AOD_PERSONALIZATION_TECH_STACK_DATABASE", "stub-database")
            .env("AOD_PERSONALIZATION_TECH_STACK_VECTOR", "stub-vector")
            .env("AOD_PERSONALIZATION_TECH_STACK_AUTH", "stub-auth")
            .env("AOD_PERSONALIZATION_RATIFICATION_DATE", "2026-05-04")
            .env("AOD_PERSONALIZATION_CURRENT_DATE", "2026-05-04")
            .env("AOD_PERSONALIZATION_CLOUD_PROVIDER", "stub-cloud")
            .output()
            .expect("run template-substitute helper");

        assert!(
            output.status.success(),
            "helper failed for {} ({}): stderr={}",
            case.id,
            case.marker,
            String::from_utf8_lossy(&output.stderr)
        );

        let destination = fs::read_to_string(&destination_path).expect("read destination output");
        assert_eq!(
            destination, case.expected,
            "substitution mismatch for {} ({})",
            case.id, case.marker
        );

        fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
    }
}

struct SubstitutionCase {
    id: &'static str,
    project_name: &'static str,
    source: &'static str,
    expected: &'static str,
    marker: &'static str,
}

fn substitution_cases() -> Vec<SubstitutionCase> {
    vec![
        SubstitutionCase {
            id: "case_1_ampersand",
            project_name: "AT&T",
            source: "{{PROJECT_NAME}}\n",
            expected: "AT&T\n",
            marker: "bash 5.2 patsub_replacement ampersand regression",
        },
        SubstitutionCase {
            id: "case_2_pipe",
            project_name: "foo|bar",
            source: "{{PROJECT_NAME}}\n",
            expected: "foo|bar\n",
            marker: "pipe byte remains literal",
        },
        SubstitutionCase {
            id: "case_3_backref",
            project_name: "\\1\\2",
            source: "{{PROJECT_NAME}}\n",
            expected: "\\1\\2\n",
            marker: "backref-looking value remains literal",
        },
        SubstitutionCase {
            id: "case_4_single_quoted",
            project_name: "'inside'",
            source: "{{PROJECT_NAME}}\n",
            expected: "'inside'\n",
            marker: "single quotes remain literal",
        },
        SubstitutionCase {
            id: "case_5_double_quoted",
            project_name: "\"inside\"",
            source: "{{PROJECT_NAME}}\n",
            expected: "\"inside\"\n",
            marker: "double quotes remain literal",
        },
        SubstitutionCase {
            id: "case_6_multibyte",
            project_name: "Ⅷ-Ⅸ",
            source: "{{PROJECT_NAME}}\n",
            expected: "Ⅷ-Ⅸ\n",
            marker: "multibyte project name remains intact",
        },
        SubstitutionCase {
            id: "case_7_newline_in_value",
            project_name: "line1\nline2",
            source: "{{PROJECT_NAME}}\n",
            expected: "line1\nline2\n",
            marker: "embedded newline is preserved",
        },
        SubstitutionCase {
            id: "case_8_empty_value",
            project_name: "",
            source: "{{PROJECT_NAME}}\n",
            expected: "\n",
            marker: "empty project name leaves only template newline",
        },
    ]
}

fn count_whole_word_eval(source: &str) -> usize {
    source
        .split(|ch: char| !(ch == '_' || ch.is_ascii_alphanumeric()))
        .filter(|token| *token == "eval")
        .count()
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn unique_temp_dir(label: &str) -> PathBuf {
    let suffix = TEMP_DIR_COUNTER.fetch_add(1, Ordering::Relaxed);
    std::env::temp_dir().join(format!(
        "tachi-rust-template-substitute-{label}-{suffix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}
