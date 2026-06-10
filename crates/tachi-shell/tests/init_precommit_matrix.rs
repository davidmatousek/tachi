use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

const PROMPT_MARKER: &str = "Install pre-commit secret-scanning hook";
const WARN_MARKER: &str = "WARN: pre-commit";

#[derive(Debug)]
struct InitRun {
    status: i32,
    stdout: String,
    stderr: String,
}

#[test]
fn init_precommit_matrix_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_init_precommit_matrix.py")
            .exists(),
        "precommit matrix coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn non_tty_no_flag_skips_prompt_and_install() {
    let temp_dir = unique_temp_dir("non-tty-no-flag");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let run = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root), &[]);

    assert_eq!(
        run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        run.status,
        stderr_tail(&run.stderr, 1500)
    );
    assert!(
        !prompt_emitted(&run),
        "non-TTY no-flag must not emit prompt"
    );
    assert!(
        !install_attempted(&run),
        "non-TTY no-flag must not attempt install"
    );

    cleanup_dir(&temp_dir);
}

#[test]
fn non_tty_no_precommit_flag_skips_install() {
    let temp_dir = unique_temp_dir("non-tty-no-precommit");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let run = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--no-precommit"],
    );

    assert_eq!(
        run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        run.status,
        stderr_tail(&run.stderr, 1500)
    );
    assert!(!prompt_emitted(&run), "--no-precommit must not emit prompt");
    assert!(
        !install_attempted(&run),
        "--no-precommit must not attempt install"
    );

    cleanup_dir(&temp_dir);
}

#[test]
fn non_tty_precommit_flag_attempts_install() {
    let temp_dir = unique_temp_dir("non-tty-precommit");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let run = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--precommit"],
    );

    assert_eq!(
        run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        run.status,
        stderr_tail(&run.stderr, 1500)
    );
    assert!(!prompt_emitted(&run), "--precommit must not emit prompt");
    assert!(
        install_attempted(&run),
        "--precommit must attempt install or warn"
    );

    cleanup_dir(&temp_dir);
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn unique_temp_dir(label: &str) -> PathBuf {
    let suffix = TEMP_DIR_COUNTER.fetch_add(1, Ordering::Relaxed);
    std::env::temp_dir().join(format!(
        "tachi-rust-init-precommit-matrix-{label}-{suffix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}

fn clone_into_tmpdir(temp_dir: &Path) -> PathBuf {
    let repo_root = workspace_root();
    let head_sha = git_stdout(&repo_root, &["rev-parse", "HEAD"]);
    let clone_root = temp_dir.join("tachi");

    let clone = Command::new("git")
        .args(["clone", "--quiet"])
        .arg(format!("file://{}", repo_root.display()))
        .arg(&clone_root)
        .output()
        .expect("clone repo into temp dir");
    assert!(
        clone.status.success(),
        "git clone failed: {}",
        String::from_utf8_lossy(&clone.stderr)
    );

    let checkout = Command::new("git")
        .args(["checkout", "--quiet", head_sha.trim()])
        .current_dir(&clone_root)
        .output()
        .expect("checkout cloned head");
    assert!(
        checkout.status.success(),
        "git checkout failed: {}",
        String::from_utf8_lossy(&checkout.stderr)
    );

    clone_root
}

fn git_stdout(repo_root: &Path, args: &[&str]) -> String {
    let output = Command::new("git")
        .args(args)
        .current_dir(repo_root)
        .output()
        .expect("run git command");
    assert!(
        output.status.success(),
        "git {} failed: {}",
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .expect("git stdout should be utf-8")
        .trim()
        .to_string()
}

fn build_canonical_stdin(clone_root: &Path) -> String {
    let other_index = discover_pack_count(clone_root) + 1;
    [
        "tachi",
        "threat modeling sidecar",
        "benchmark-test-org",
        "",
        "1",
        &other_index.to_string(),
        "Python + FastAPI",
        "PostgreSQL",
        "",
        "Y",
    ]
    .join("\n")
        + "\n"
}

fn discover_pack_count(clone_root: &Path) -> usize {
    let stacks_dir = clone_root.join("stacks");
    if !stacks_dir.is_dir() {
        return 0;
    }

    fs::read_dir(stacks_dir)
        .expect("read stacks dir")
        .filter_map(Result::ok)
        .filter(|entry| entry.path().join("STACK.md").is_file())
        .count()
}

fn run_init_in_clone(clone_root: &Path, stdin_payload: &str, flags: &[&str]) -> InitRun {
    let fake_home = clone_root
        .parent()
        .expect("clone root parent")
        .join("fake_home");
    fs::create_dir_all(&fake_home).expect("create fake home");

    let mut command =
        Command::new(std::env::var("BASH").unwrap_or_else(|_| "/bin/bash".to_string()));
    command
        .arg("./scripts/init.sh")
        .args(flags)
        .current_dir(clone_root)
        .env("LC_ALL", "C")
        .env("HOME", &fake_home)
        .env("PATH", safe_path())
        .env("AOD_RATIFICATION_DATE_OVERRIDE", "2026-05-04")
        .env("AOD_CURRENT_DATE_OVERRIDE", "2026-05-04")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let output = command
        .spawn()
        .and_then(|mut child| {
            child
                .stdin
                .as_mut()
                .expect("child stdin")
                .write_all(stdin_payload.as_bytes())?;
            child.wait_with_output()
        })
        .expect("run bash ./scripts/init.sh");

    InitRun {
        status: output.status.code().unwrap_or(1),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
    }
}

fn safe_path() -> String {
    let blocked = ["/opt/homebrew/bin", "/usr/local/bin", "/opt/homebrew/sbin"];
    let current = std::env::var("PATH").unwrap_or_default();
    let kept = current
        .split(':')
        .filter(|part| !blocked.contains(part))
        .collect::<Vec<_>>();

    let has_node = kept
        .iter()
        .any(|part| Path::new(part).join("node").exists());
    if has_node {
        kept.join(":")
    } else {
        current
    }
}

fn prompt_emitted(run: &InitRun) -> bool {
    run.stdout.contains(PROMPT_MARKER) || run.stderr.contains(PROMPT_MARKER)
}

fn install_attempted(run: &InitRun) -> bool {
    run.stdout.contains("pre-commit installed at")
        || run.stderr.contains("pre-commit installed at")
        || run.stdout.contains(WARN_MARKER)
        || run.stderr.contains(WARN_MARKER)
}

fn stderr_tail(text: &str, max_chars: usize) -> &str {
    tail_chars(text, max_chars)
}

fn tail_chars(text: &str, max_chars: usize) -> &str {
    if text.len() <= max_chars {
        return text;
    }

    let start = text
        .char_indices()
        .rev()
        .nth(max_chars.saturating_sub(1))
        .map(|(idx, _)| idx)
        .unwrap_or(0);
    &text[start..]
}

fn cleanup_dir(path: &Path) {
    if let Err(err) = fs::remove_dir_all(path) {
        if path.exists() {
            panic!("failed to remove {}: {err}", path.display());
        }
    }
}
