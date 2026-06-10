use std::fs;
use std::path::{Path, PathBuf};

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
