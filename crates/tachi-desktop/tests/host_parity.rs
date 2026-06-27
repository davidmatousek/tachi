use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

use pretty_assertions::assert_eq;
use tachi_desktop::dispatch_desktop_command;
use tachi_desktop::dispatch_desktop_command_owned;
use tachi_desktop::dispatch_desktop_command_with_noop_progress;
use tachi_desktop::dispatch_desktop_command_with_progress;
use tachi_desktop::registered_commands;
use tachi_desktop::DesktopHost;
use tachi_shell::commands::command_registry;
use tachi_shell::progress::CancellationToken;
use tachi_shell::progress::ProgressEvent;
use tachi_shell::progress::ProgressReporter;

#[derive(Clone)]
struct RecordingReporter(Arc<Mutex<Vec<ProgressEvent>>>);

static FIXTURE_COUNTER: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

impl ProgressReporter for RecordingReporter {
    fn emit(&mut self, event: ProgressEvent) {
        self.0.lock().expect("reporter mutex").push(event);
    }
}

fn fixture_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-desktop-shell-{}-{}",
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos(),
        FIXTURE_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
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
fn registered_commands_match_shared_shell_registry() {
    let expected = command_registry().names();
    assert_eq!(registered_commands(), expected.as_slice());
}

#[test]
fn desktop_host_methods_match_free_function_surface() {
    let host = DesktopHost::new();
    assert_eq!(host.registered_commands(), registered_commands());

    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let host_output = host.dispatch_command("bootstrap", &root, &["--yes"]);
    let free_output = dispatch_desktop_command("bootstrap", &root, &["--yes"]);

    assert_eq!(host_output.status, free_output.status);
    assert_eq!(host_output.stdout, free_output.stdout);
    assert_eq!(host_output.stderr, free_output.stderr);
}

#[test]
fn owned_and_noop_dispatch_helpers_route_to_shared_surface() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let owned = dispatch_desktop_command_owned(
        "bootstrap",
        root.clone(),
        vec![String::from("--yes"), String::from("--dry-run")],
    );
    let noop =
        dispatch_desktop_command_with_noop_progress("bootstrap", &root, &["--yes", "--dry-run"]);

    assert_eq!(owned.status, 0);
    assert_eq!(owned.stdout, "--bootstrap\n--yes\n--dry-run\n");
    assert_eq!(noop.status, owned.status);
    assert_eq!(noop.stdout, owned.stdout);
    assert_eq!(noop.stderr, owned.stderr);
}

#[test]
fn desktop_host_progress_method_uses_supplied_reporter() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nprintf 'progress-ok\\n'\n",
    );
    let token = CancellationToken::new();
    let events = Arc::new(Mutex::new(Vec::new()));
    let mut reporter = RecordingReporter(events.clone());

    let output = DesktopHost::new().dispatch_command_with_progress(
        "bootstrap",
        &root,
        &["--yes"],
        &token,
        &mut reporter,
    );

    assert_eq!(output.status, 0);
    assert!(events
        .lock()
        .expect("events")
        .iter()
        .any(|event| { event.command == "bootstrap" && event.message == "completed" }));
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

#[test]
fn dispatch_desktop_command_routes_infographic_data_through_shared_shell_surface() {
    let root = fixture_repo();
    fs::write(
        root.join("threats.md"),
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n| AG-8 | Agent | Prompt injection | High | Harden prompts | [NEW] |\n",
    )
    .expect("write threats");

    let output = dispatch_desktop_command(
        "infographic-data",
        &root,
        &[
            "--root",
            root.to_string_lossy().as_ref(),
            "--template",
            "maestro-stack",
        ],
    );

    assert_eq!(output.status, 0);
    assert!(output.stderr.is_empty());
    let payload: serde_json::Value =
        serde_json::from_str(&output.stdout).expect("valid infographic JSON");
    assert_eq!(payload["template"], "maestro-stack");
    assert!(payload["template_data"].is_object());
}

#[test]
fn dispatch_desktop_command_with_progress_can_cancel_running_install_script() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\ntrap 'exit 130' TERM\nprintf 'begin\\n'\nsleep 5\nprintf 'done\\n'\n",
    );

    let token = CancellationToken::new();
    let worker_token = token.clone();
    let events = Arc::new(Mutex::new(Vec::new()));
    let reporter = RecordingReporter(events.clone());

    let handle = std::thread::spawn(move || {
        let mut reporter = reporter;
        dispatch_desktop_command_with_progress(
            "install",
            &root,
            &["--root", root.to_string_lossy().as_ref()],
            &worker_token,
            &mut reporter,
        )
    });

    std::thread::sleep(std::time::Duration::from_millis(100));
    token.cancel();

    let output = handle.join().expect("join worker");
    assert_eq!(output.status, 130);
    assert!(events.lock().expect("events").iter().any(|event| {
        let ProgressEvent { command, message } = event;
        command == "install" && message == "cancelled"
    }));
}
