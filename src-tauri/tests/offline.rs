use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;

use pretty_assertions::assert_eq;
use tachi_tauri::{
    bootstrap_from_cache, check_for_update, restore_offline_cache, BootstrapReport,
    OfflineRestoreReport, UpdateCheck,
};

fn fixture_root(prefix: &str) -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-{prefix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));
    fs::create_dir_all(&root).expect("create fixture root");
    root
}

fn write_executable_file(path: &PathBuf, content: &str) {
    fs::create_dir_all(path.parent().expect("parent")).expect("create parent");
    fs::write(path, content).expect("write temporary file");
    let mut perms = fs::metadata(path).expect("read metadata").permissions();
    perms.set_mode(0o755);
    fs::set_permissions(path, perms).expect("set executable mode");
}

#[test]
fn restore_offline_cache_restores_expected_files() {
    let repo_root = fixture_root("offline-repo");
    let cache_root = fixture_root("offline-cache");

    fs::create_dir_all(cache_root.join(".aod")).expect("create cache aod dir");
    write_executable_file(
        &cache_root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\necho offline update\n",
    );
    fs::write(
        cache_root.join(".aod/aod-kit-version"),
        "version=v1.2.3\nsha=abc123\n",
    )
    .expect("write version pin");

    let report = restore_offline_cache(&repo_root, &cache_root).expect("restore cache");

    assert_eq!(
        report,
        OfflineRestoreReport {
            restored_files: vec![
                repo_root.join(".aod/aod-kit-version"),
                repo_root.join("scripts/update.sh"),
            ],
            missing_cache_files: vec![
                repo_root.join("scripts/install.sh"),
                repo_root.join("scripts/init.sh"),
            ],
        }
    );
    assert!(repo_root.join("scripts/update.sh").is_file());
    assert!(repo_root.join(".aod/aod-kit-version").is_file());
}

#[test]
fn check_for_update_reports_cached_version_difference() {
    let repo_root = fixture_root("offline-current");
    let cache_root = fixture_root("offline-updated");

    fs::create_dir_all(repo_root.join(".aod")).expect("create repo aod dir");
    fs::create_dir_all(cache_root.join(".aod")).expect("create cache aod dir");
    fs::write(repo_root.join(".aod/aod-kit-version"), "version=v1.0.0\n").expect("write current");
    fs::write(cache_root.join(".aod/aod-kit-version"), "version=v1.1.0\n")
        .expect("write cached");

    let check = check_for_update(&repo_root, &cache_root).expect("check update");

    assert_eq!(
        check,
        UpdateCheck {
            current_version: Some(String::from("v1.0.0")),
            cached_version: Some(String::from("v1.1.0")),
            update_available: true,
        }
    );
}

#[test]
fn bootstrap_from_cache_restores_ready_offline_state() {
    let repo_root = fixture_root("offline-bootstrap-repo");
    let cache_root = fixture_root("offline-bootstrap-cache");

    fs::create_dir_all(cache_root.join(".aod")).expect("create cache aod dir");
    write_executable_file(
        &cache_root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\necho bootstrap\n",
    );
    fs::write(
        cache_root.join(".aod/aod-kit-version"),
        "version=v2.0.0\nsha=abc123\n",
    )
    .expect("write cached version");

    let report = bootstrap_from_cache(&repo_root, &cache_root).expect("bootstrap from cache");

    assert_eq!(
        report,
        BootstrapReport {
            restore: OfflineRestoreReport {
                restored_files: vec![
                    repo_root.join(".aod/aod-kit-version"),
                    repo_root.join("scripts/update.sh"),
                ],
                missing_cache_files: vec![
                    repo_root.join("scripts/install.sh"),
                    repo_root.join("scripts/init.sh"),
                ],
            },
            update_check: UpdateCheck {
                current_version: Some(String::from("v2.0.0")),
                cached_version: Some(String::from("v2.0.0")),
                update_available: false,
            },
            offline_ready: true,
        }
    );
}
