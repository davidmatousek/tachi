use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::os::unix::fs::symlink;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use tachi_shell::progress::{
    cancel_running_command, CancellationToken, ProgressEvent, ProgressReporter,
};
use tachi_shell::tauri_bridge::dispatch_command;
use tachi_shell::tauri_bridge::dispatch_command_with_progress;

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
        "tachi-rust-tauri-bridge-{}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
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
fn dispatch_command_routes_bootstrap_to_update_with_prefix() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let output = dispatch_command("bootstrap", &root, &["--yes"]);

    assert_eq!(output.status, 0);
    let lines: Vec<_> = output.stdout.lines().collect();
    assert_eq!(lines, vec!["--bootstrap", "--yes"]);
}

#[test]
fn dispatch_command_rejects_unknown_command() {
    let root = fixture_repo();

    let output = dispatch_command("unknown", &root, &[]);

    assert_ne!(output.status, 0);
    assert!(output.stderr.contains("unsupported command"));
}

#[test]
fn dispatch_command_with_progress_can_cancel_running_install_script() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\ntrap 'exit 130' TERM\nprintf 'begin\\n'\nsleep 5\nprintf 'done\\n'\n",
    );

    let token = CancellationToken::new();
    let worker_token = token.clone();
    let events = Arc::new(Mutex::new(Vec::new()));
    let reporter = RecordingReporter(events.clone());

    let handle = thread::spawn(move || {
        let mut reporter = reporter;
        dispatch_command_with_progress("install", &root, &[], &worker_token, &mut reporter)
    });

    thread::sleep(Duration::from_millis(100));
    cancel_running_command(&token);

    let output = handle.join().expect("join install command");

    assert_eq!(output.status, 130);
    let messages: Vec<_> = events
        .lock()
        .expect("report events")
        .iter()
        .map(|event| event.message.clone())
        .collect();
    assert!(messages.iter().any(|message| message == "starting"));
    assert!(messages.iter().any(|message| message == "running"));
    assert!(messages.iter().any(|message| message == "cancelled"));
}

#[test]
fn dispatch_command_rejects_output_path_escape_and_parent_traversal() {
    let root = fixture_repo();
    let target_dir = root.join("target");
    let template_dir = root.join("templates/tachi/security-report");
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::create_dir_all(&target_dir).expect("create target dir");
    fs::write(target_dir.join("threats.md"), "# Threat Model: Escape Test\n").expect("write threats");
    let output_path = std::env::temp_dir().join(format!(
        "tachi-rust-escape-{}",
        FIXTURE_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
    ));

    let output = dispatch_command(
        "report-data",
        &root,
        &[
            "--target-dir",
            target_dir.to_string_lossy().as_ref(),
            "--template-dir",
            template_dir.to_string_lossy().as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(output.status, 2);
    assert!(output.stderr.contains("path policy failed for report-data output"));

    let traversal = dispatch_command(
        "infographic-data",
        &root,
        &["--root", root.join("..").to_string_lossy().as_ref(), "--template", "maestro-stack"],
    );
    assert_eq!(traversal.status, 2);
    assert!(traversal.stderr.contains("contains parent traversal"));
}

#[test]
fn dispatch_command_rejects_symlink_escape_in_input_path() {
    let root = fixture_repo();
    let outside = std::env::temp_dir().join(format!(
        "tachi-rust-outside-{}",
        FIXTURE_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
    ));
    fs::create_dir_all(&outside).expect("create outside root");
    fs::write(outside.join("threats.md"), "outside").expect("write outside threats");
    symlink(outside.join("threats.md"), root.join("threats.md")).expect("create symlink");

    let output = dispatch_command(
        "threats-sarif",
        &root,
        &[
            "--input",
            root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            root.join("out/threats.sarif").to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(output.status, 2);
    assert!(output.stderr.contains("path policy failed for threats input"));
}
