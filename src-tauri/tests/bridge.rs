use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;

use pretty_assertions::assert_eq;
use tachi_tauri::{dispatch_desktop_command, registered_commands};

fn fixture_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-tauri-shell-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(root.join("scripts")).expect("create fixture scripts");
    root
}

fn write_executable_file(path: &PathBuf, content: &str) {
    fs::write(path, content).expect("write temporary script");
    let mut perms = fs::metadata(path).expect("read metadata").permissions();
    perms.set_mode(0o755);
    fs::set_permissions(path, perms).expect("set executable mode");
}

#[test]
fn registered_commands_expose_shared_shell_surface() {
    assert_eq!(
        registered_commands(),
        &["install", "init", "update", "bootstrap", "infographic-data"]
    );
}

#[test]
fn dispatch_desktop_command_reuses_shared_bridge_for_bootstrap() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let output = dispatch_desktop_command("bootstrap", &root, &["--yes"]);

    assert_eq!(output.status, 0);
    let lines: Vec<_> = output.stdout.lines().collect();
    assert_eq!(lines, vec!["--bootstrap", "--yes"]);
}
