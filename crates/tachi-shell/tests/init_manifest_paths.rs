use std::path::{Path, PathBuf};
use std::process::Command;

#[test]
fn template_manifest_personalized_paths_helper_matches_manifest_entries() {
    let root = workspace_root();
    let manifest = root.join(".aod/template-manifest.txt");
    let helper = root.join(".aod/scripts/bash/template-substitute.sh");

    let helper_output = Command::new("bash")
        .current_dir(&root)
        .arg("-lc")
        .arg(format!(
            "source '{}' >/dev/null; aod_template_manifest_personalized_paths '{}'",
            helper.display(),
            manifest.display()
        ))
        .output()
        .expect("run manifest path helper");

    assert!(
        helper_output.status.success(),
        "helper should list personalized manifest paths. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&helper_output.stdout),
        String::from_utf8_lossy(&helper_output.stderr)
    );

    let manifest_output = Command::new("bash")
        .current_dir(&root)
        .arg("-lc")
        .arg(format!(
            "sed -n 's/^personalized|//p' '{}' | tr -d '\\r'",
            manifest.display()
        ))
        .output()
        .expect("run manifest parser");

    assert!(
        manifest_output.status.success(),
        "manifest parser should succeed. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&manifest_output.stdout),
        String::from_utf8_lossy(&manifest_output.stderr)
    );

    assert_eq!(
        String::from_utf8_lossy(&helper_output.stdout),
        String::from_utf8_lossy(&manifest_output.stdout),
        "helper output should match the manifest-backed personalized path list"
    );
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}
