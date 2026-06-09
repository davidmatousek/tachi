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

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}
