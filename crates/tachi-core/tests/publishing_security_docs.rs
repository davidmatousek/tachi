use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
    .to_path_buf()
}

fn unique_temp_root(prefix: &str) -> PathBuf {
    let suffix = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("clock")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{suffix}"))
}

fn write_file(root: &Path, rel: &str, contents: &str) {
    let path = root.join(rel);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent directories");
    }
    fs::write(path, contents).expect("write test file");
}

fn docs_archive_gate_script() -> PathBuf {
    workspace_root().join("scripts/docs-archive-version-gate.sh")
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
        !security.contains("https://github.com/pratik-saptarshi/tachi.git"),
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

#[test]
fn fuzz_mutation_docs_and_baseline_artifact_are_repo_specific_and_offline_safe() {
    let root = workspace_root();
    let audit = fs::read_to_string(root.join("docs/testing/fuzz-mutation-audit.md"))
        .expect("fuzz mutation audit exists");
    let baseline = fs::read_to_string(root.join("docs/reports/fuzz-mutation-baseline.md"))
        .expect("fuzz mutation baseline exists");

    for required in [
        "cargo fuzz run parser_roundtrip",
        "cargo fuzz run reporting_roundtrip",
        "cargo-mutants run --workspace --test",
        "Follow-up Beads tasks",
        "advisory and starts observationally",
    ] {
        assert!(
            audit.contains(required) || baseline.contains(required),
            "fuzz/mutation docs should mention {required}"
        );
    }

    assert!(
        baseline.contains("not executed in this environment"),
        "baseline should remain offline-safe"
    );
    for forbidden in ["BEGIN PRIVATE KEY", "github_pat_", "ghp_", "sk-"] {
        assert!(
            !baseline.contains(forbidden),
            "baseline should not contain {forbidden}"
        );
    }
}

#[test]
fn docs_archive_version_gate_allows_archival_references_and_rejects_maintained_drift() {
    let allowlisted_root = unique_temp_root("tachi-rust-docs-archive-allowlisted");
    write_file(
        &allowlisted_root,
        "docs/guides/CONSUMER_GUIDE_TACHI.md",
        "Upload via `codeql/upload-sarif@v3` GitHub Action. Historical reference: this reflects the original tachi adapter docs, not the current `tachi-rust` CI surface.\n",
    );

    let allowlisted_output = Command::new(docs_archive_gate_script())
        .arg(&allowlisted_root)
        .output()
        .expect("run docs archive gate on allowlisted tree");
    assert!(
        allowlisted_output.status.success(),
        "archival references should be allowed in docs archive gate. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&allowlisted_output.stdout),
        String::from_utf8_lossy(&allowlisted_output.stderr)
    );

    let maintained_root = unique_temp_root("tachi-rust-docs-archive-maintained");
    write_file(
        &maintained_root,
        "docs/roadmap/archival-note.md",
        "Legacy guidance mentions `codeql/upload-sarif@v3` without an archival marker.\n",
    );

    let maintained_output = Command::new(docs_archive_gate_script())
        .arg(&maintained_root)
        .output()
        .expect("run docs archive gate on maintained-doc drift");
    assert!(
        !maintained_output.status.success(),
        "maintained docs drift should fail the archive gate"
    );
    let stderr = String::from_utf8_lossy(&maintained_output.stderr);
    assert!(
        stderr.contains("docs/roadmap/archival-note.md"),
        "failure should name the stale file: {stderr}"
    );
    assert!(
        stderr.contains("stale workflow-version references"),
        "failure should explain the gate condition: {stderr}"
    );
}
