use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[derive(Debug)]
struct InitRun {
    status: i32,
    stdout: String,
    stderr: String,
}

#[test]
fn init_constitution_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_init_sh_constitution.py")
            .exists(),
        "init constitution coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn constitution_byte_equals_clean_template() {
    let temp_dir = unique_temp_dir("constitution");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let init_run = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root));
    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
        init_run.status,
        stdout_tail(&init_run.stdout, 1500),
        stderr_tail(&init_run.stderr, 1500)
    );

    let constitution = clone_root
        .join(".aod")
        .join("memory")
        .join("constitution.md");
    let template_clean = clone_root
        .join(".aod")
        .join("templates")
        .join("constitution-clean.md");

    assert!(
        constitution.is_file(),
        "post-init constitution missing: {}",
        constitution.display()
    );
    assert!(
        template_clean.is_file(),
        "clean template missing: {}",
        template_clean.display()
    );

    let constitution_bytes = fs::read(&constitution).expect("read constitution");
    let template_bytes = fs::read(&template_clean).expect("read clean template");
    assert_eq!(
        constitution_bytes, template_bytes,
        "byte-comparison failed:\n  constitution length: {}\n  template length: {}\n  first divergence (truncated): {}",
        constitution_bytes.len(),
        template_bytes.len(),
        first_divergence(&constitution_bytes, &template_bytes)
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
        "tachi-rust-init-constitution-{label}-{suffix}-{}",
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

fn run_init_in_clone(clone_root: &Path, stdin_payload: &str) -> InitRun {
    let fake_home = clone_root
        .parent()
        .expect("clone root parent")
        .join("fake_home");
    fs::create_dir_all(&fake_home).expect("create fake home");

    let output = Command::new(std::env::var("BASH").unwrap_or_else(|_| "/bin/bash".to_string()))
        .arg("./scripts/init.sh")
        .current_dir(clone_root)
        .env("LC_ALL", "C")
        .env("HOME", &fake_home)
        .env("PATH", safe_path())
        .env("AOD_RATIFICATION_DATE_OVERRIDE", "2026-05-04")
        .env("AOD_CURRENT_DATE_OVERRIDE", "2026-05-04")
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .and_then(|mut child| {
            use std::io::Write;

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

fn stderr_tail(stderr: &str, max_chars: usize) -> String {
    stderr
        .chars()
        .rev()
        .take(max_chars)
        .collect::<String>()
        .chars()
        .rev()
        .collect()
}

fn stdout_tail(stdout: &str, max_chars: usize) -> String {
    stdout_tail_impl(stdout, max_chars)
}

fn stdout_tail_impl(text: &str, max_chars: usize) -> String {
    text.chars()
        .rev()
        .take(max_chars)
        .collect::<String>()
        .chars()
        .rev()
        .collect()
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

fn first_divergence(a: &[u8], b: &[u8]) -> String {
    let n = a.len().min(b.len());
    for i in 0..n {
        if a[i] != b[i] {
            let lo = i.saturating_sub(60);
            let hi = (i + 60).min(n);
            return format!(
                "@offset {i}: actual={:?} | template={:?}",
                &a[lo..hi],
                &b[lo..hi]
            );
        }
    }
    if a.len() != b.len() {
        return format!("length differs: actual={} template={}", a.len(), b.len());
    }
    String::from("no divergence detected (this is unexpected)")
}

fn cleanup_dir(path: &Path) {
    let _ = fs::remove_dir_all(path);
}
