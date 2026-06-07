use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use std::os::unix::fs::PermissionsExt;

use tachi_shell::commands::{bootstrap_output, init_output, install_output, update_output};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[cfg(unix)]
fn write_executable_file(path: &Path, content: &str) {
    fs::write(path, content).expect("write temporary script");
    let mut perms = fs::metadata(path).expect("read metadata").permissions();
    perms.set_mode(0o755);
    fs::set_permissions(path, perms).expect("set executable mode");
}

#[cfg(not(unix))]
fn write_executable_file(path: &Path, content: &str) {
    fs::write(path, content).expect("write temporary script");
}

fn fixture_repo() -> PathBuf {
    let unique_suffix = TEMP_DIR_COUNTER.fetch_add(1, Ordering::Relaxed);
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-control-plane-{}-{}",
        unique_suffix,
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    let scripts_dir = root.join("scripts");
    fs::create_dir_all(&scripts_dir).expect("create fixture scripts directory");
    root
}

fn fixture_repo_with_nested_path() -> (PathBuf, PathBuf) {
    let root = fixture_repo();
    let nested = root.join("nested").join("deep");
    fs::create_dir_all(&nested).expect("create nested repo path");
    (root, nested)
}

#[test]
fn install_output_runs_install_script_with_provided_flags() {
    let root = fixture_repo();
    let script = root.join("scripts/install.sh");
    write_executable_file(
        &script,
        "#!/usr/bin/env bash\nprintf 'args:'\nfor arg in \"$@\"; do printf ' %s' \"$arg\"; done\nprintf '\\n'\nexit 0\n",
    );

    let output = install_output(&root, &["--source", "/tmp/source", "--version", "v1.2.3"]);
    assert_eq!(output.status, 0);
    assert_eq!(
        output.stdout.trim(),
        "args: --source /tmp/source --version v1.2.3"
    );
}

#[test]
fn init_output_forwards_args_to_init_script() {
    let root = fixture_repo();
    let script = root.join("scripts/init.sh");
    write_executable_file(
        &script,
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\"\nprintf '%s\\n' \"$2\"\nexit 0\n",
    );

    let output = init_output(&root, &["--precommit", "--help"]);
    assert_eq!(output.status, 0);
    assert_eq!(output.stdout.lines().next(), Some("--precommit"));
    assert_eq!(output.stdout.lines().nth(1), Some("--help"));
}

#[test]
fn update_output_forwards_update_flags() {
    let root = fixture_repo();
    let script = root.join("scripts/update.sh");
    write_executable_file(
        &script,
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\"\nprintf '%s\\n' \"$2\"\nprintf '%s\\n' \"$3\"\nexit 0\n",
    );

    let output = update_output(&root, &["--dry-run", "--yes", "--json"]);
    assert_eq!(output.status, 0);
    let lines: Vec<_> = output.stdout.lines().collect();
    assert_eq!(lines, vec!["--dry-run", "--yes", "--json"]);
}

#[test]
fn bootstrap_output_prepends_bootstrap_flag() {
    let root = fixture_repo();
    let script = root.join("scripts/update.sh");
    write_executable_file(
        &script,
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let output = bootstrap_output(&root, &["--upstream-url=https://example.com/upstream.git"]);
    assert_eq!(output.status, 0);
    let lines: Vec<_> = output.stdout.lines().collect();
    assert_eq!(
        lines,
        vec![
            "--bootstrap",
            "--upstream-url=https://example.com/upstream.git"
        ]
    );
}

#[test]
fn init_output_uses_ancestor_scripts_dir_when_invoked_from_nested_path() {
    let (root, nested) = fixture_repo_with_nested_path();
    let script = root.join("scripts/init.sh");
    write_executable_file(
        &script,
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$PWD\"\nprintf '%s\\n' \"$1\"",
    );

    let output = init_output(&nested, &["--help"]);
    assert_eq!(output.status, 0);
    assert!(output
        .stdout
        .lines()
        .next()
        .expect("expected cwd on first output line")
        .contains(
            root.file_name()
                .and_then(|name| name.to_str())
                .expect("root path has non-UTF8 component"),
        ));
    assert_eq!(output.stdout.lines().nth(1), Some("--help"));
}
