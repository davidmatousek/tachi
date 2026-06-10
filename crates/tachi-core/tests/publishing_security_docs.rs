use std::fs;
use std::path::{Path, PathBuf};

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

#[test]
fn publishing_security_docs_are_repo_specific_and_privacy_aware() {
    let root = workspace_root();
    let security = fs::read_to_string(root.join("SECURITY.md")).expect("SECURITY.md exists");
    let checklist = fs::read_to_string(root.join("docs/standards/PUBLISHING_SECURITY.md"))
        .expect("publishing security checklist exists");
    let standards =
        fs::read_to_string(root.join("docs/standards/README.md")).expect("standards index exists");

    assert!(
        security.contains("pratik-saptarshi/tachi-rust"),
        "SECURITY.md should point at the public tachi-rust repository"
    );
    assert!(
        !security.contains("pratik-saptarshi/tachi-rust"),
        "SECURITY.md should not point at the legacy Python repository"
    );
    assert!(
        security.contains("Privacy and data handling"),
        "SECURITY.md should document privacy expectations"
    );

    for required in [
        "cargo test -q",
        "cargo clippy --all-targets -- -D warnings",
        "make llvm-cov",
        "85%",
        "No secrets, credentials, tokens, or private keys",
        "No personal data, customer data, or private assessment output",
        "GitHub private vulnerability reporting",
    ] {
        assert!(
            checklist.contains(required),
            "publishing checklist should mention {required}"
        );
    }

    assert!(
        standards.contains("PUBLISHING_SECURITY.md"),
        "standards index should link the publishing security checklist"
    );
}
