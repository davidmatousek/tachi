use std::fs;
use std::os::unix::fs::symlink;
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::Command;
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
static EXEC_POLICY_LOCK: Mutex<()> = Mutex::new(());

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

fn wait_for_file(path: &Path) {
    for _ in 0..100 {
        if path.exists() {
            return;
        }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("timed out waiting for {}", path.display());
}

#[test]
fn dispatch_command_routes_bootstrap_to_update_with_prefix() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
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
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
    let root = fixture_repo();

    let output = dispatch_command("unknown", &root, &[]);

    assert_ne!(output.status, 0);
    assert!(output.stderr.contains("unsupported command"));
}

#[test]
fn dispatch_command_with_progress_can_cancel_running_install_script() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\ntrap 'exit 130' TERM\nsleep 60 &\nchild=$!\nprintf '%s\\n' \"$child\" > child.pid\nprintf 'begin\\n'\nwait\n",
    );

    let token = CancellationToken::new();
    let worker_token = token.clone();
    let events = Arc::new(Mutex::new(Vec::new()));
    let reporter = RecordingReporter(events.clone());
    let child_root = root.clone();

    let handle = thread::spawn(move || {
        let mut reporter = reporter;
        dispatch_command_with_progress("install", &child_root, &[], &worker_token, &mut reporter)
    });

    wait_for_file(&root.join("child.pid"));
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
    let child_pid = fs::read_to_string(root.join("child.pid"))
        .expect("read child pid")
        .trim()
        .to_string();
    let kill_status = Command::new("kill")
        .arg("-0")
        .arg(&child_pid)
        .status()
        .expect("probe child pid");
    assert!(
        !kill_status.success(),
        "background child should not survive cancel"
    );
}

#[test]
fn dispatch_command_times_out_long_running_install_script_and_cleans_children() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
    let previous_timeout = std::env::var("TACHI_EXECUTION_TIMEOUT_MS").ok();
    std::env::set_var("TACHI_EXECUTION_TIMEOUT_MS", "1000");

    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\nsleep 60 &\nchild=$!\nprintf '%s\\n' \"$child\" > child.pid\nwait\n",
    );

    let output = dispatch_command("install", &root, &[]);

    if let Some(value) = previous_timeout {
        std::env::set_var("TACHI_EXECUTION_TIMEOUT_MS", value);
    } else {
        std::env::remove_var("TACHI_EXECUTION_TIMEOUT_MS");
    }

    assert_eq!(output.status, 124);
    assert!(output.stderr.is_empty() || output.stderr.contains("timed out"));
    let child_pid = fs::read_to_string(root.join("child.pid"))
        .expect("read child pid")
        .trim()
        .to_string();
    let kill_status = Command::new("kill")
        .arg("-0")
        .arg(&child_pid)
        .status()
        .expect("probe child pid");
    assert!(
        !kill_status.success(),
        "background child should not survive timeout"
    );
}

#[test]
fn dispatch_command_caps_large_stdout_and_stderr_output() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\nfor i in $(seq 1 10000); do printf '0123456789'; done\nfor i in $(seq 1 10000); do printf 'abcdefghij' >&2; done\n",
    );

    let output = dispatch_command("install", &root, &[]);

    assert_eq!(output.status, 0);
    assert!(output.stdout.len() <= 64 * 1024);
    assert!(output.stderr.len() <= 64 * 1024);
    assert!(output.stdout.starts_with("0123456789"));
    assert!(output.stderr.starts_with("abcdefghij"));
}

#[test]
fn dispatch_command_propagates_nonzero_exit_status() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\nprintf 'bad exit\\n' >&2\nexit 7\n",
    );

    let output = dispatch_command("install", &root, &[]);

    assert_eq!(output.status, 7);
    assert!(output.stderr.contains("bad exit"));
}

#[test]
fn dispatch_command_rejects_output_path_escape_and_parent_traversal() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
    let root = fixture_repo();
    let target_dir = root.join("target");
    let template_dir = root.join("templates/tachi/security-report");
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::create_dir_all(&target_dir).expect("create target dir");
    fs::write(
        target_dir.join("threats.md"),
        "# Threat Model: Escape Test\n",
    )
    .expect("write threats");
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
    assert!(output
        .stderr
        .contains("path policy failed for report-data output"));

    let traversal = dispatch_command(
        "infographic-data",
        &root,
        &[
            "--root",
            root.join("..").to_string_lossy().as_ref(),
            "--template",
            "maestro-stack",
        ],
    );
    assert_eq!(traversal.status, 2);
    assert!(traversal.stderr.contains("contains parent traversal"));
}

#[test]
fn dispatch_command_rejects_symlink_escape_in_input_path() {
    let _guard = EXEC_POLICY_LOCK.lock().expect("policy lock");
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
    assert!(output
        .stderr
        .contains("path policy failed for threats input"));
}
