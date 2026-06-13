use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[test]
fn init_trace_summary_reports_phases_and_total_elapsed_time() {
    let temp_dir = unique_temp_dir("trace-summary");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let init_run = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--no-precommit"],
    );

    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
        init_run.status,
        stdout_tail(&init_run.stdout, 1500),
        stderr_tail(&init_run.stderr, 1500)
    );

    let phase_markers = [
        "INIT TRACE phase=prerequisites",
        "INIT TRACE phase=stack-discovery",
        "INIT TRACE phase=precommit",
        "INIT TRACE phase=personalization",
        "INIT TRACE phase=substitution",
        "INIT TRACE phase=version-pin",
        "INIT TRACE phase=cleanup",
    ];

    let phase_offsets = phase_markers
        .iter()
        .map(|marker| {
            init_run
                .stderr
                .find(marker)
                .unwrap_or_else(|| panic!("missing trace marker: {marker}"))
        })
        .collect::<Vec<_>>();
    assert_eq!(
        phase_offsets,
        {
            let mut ordered = phase_offsets.clone();
            ordered.sort_unstable();
            ordered
        },
        "init.sh should trace each startup phase in order"
    );

    assert!(
        init_run
            .stderr
            .lines()
            .any(|line| line.starts_with("INIT TRACE summary total=") && line.contains("phases=7")),
        "init.sh should print a final timing summary line with the phase count"
    );
}

#[test]
fn init_trace_summary_reports_slowest_phase() {
    let temp_dir = unique_temp_dir("trace-summary-slowest");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let init_run = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--no-precommit"],
    );

    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
        init_run.status,
        stdout_tail(&init_run.stdout, 1500),
        stderr_tail(&init_run.stderr, 1500)
    );

    assert!(
        init_run
            .stderr
            .lines()
            .any(|line| line.starts_with("INIT TRACE summary total=")
                && line.contains("slowest-phase=")
                && line.contains("slowest-duration=")),
        "init.sh should report the slowest phase in the final timing summary"
    );
}

#[test]
fn init_trace_summary_exposes_millisecond_fields_for_benchmarking() {
    let temp_dir = unique_temp_dir("trace-summary-ms");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let init_run = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--no-precommit"],
    );

    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
        init_run.status,
        stdout_tail(&init_run.stdout, 1500),
        stderr_tail(&init_run.stderr, 1500)
    );

    for marker in [
        "INIT TRACE phase=prerequisites",
        "INIT TRACE phase=stack-discovery",
        "INIT TRACE phase=precommit",
    ] {
        assert!(
            init_run
                .stderr
                .lines()
                .any(|line| line.contains(marker) && line.contains("elapsed_ms=")),
            "init.sh should emit millisecond timing fields for benchmark comparison: {marker}\nstderr tail:\n{}",
            stderr_tail(&init_run.stderr, 2000)
        );
    }

    assert!(
        init_run
            .stderr
            .lines()
            .any(|line| {
                line.starts_with("INIT TRACE summary total=")
                    && line.contains("total_ms=")
                    && line.contains("slowest-duration_ms=")
            }),
        "init.sh should include millisecond totals and slowest-phase duration in the final summary\nstderr tail:\n{}",
        stderr_tail(&init_run.stderr, 2000)
    );
}

#[test]
fn init_trace_summary_can_collect_cold_and_warm_samples_in_one_clone() {
    let temp_dir = unique_temp_dir("trace-summary-cold-warm");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let cold = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--no-precommit"],
    );
    assert_eq!(
        cold.status,
        0,
        "cold init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
        cold.status,
        stdout_tail(&cold.stdout, 1500),
        stderr_tail(&cold.stderr, 1500)
    );

    restore_init_script(&clone_root);
    let personalization_env = clone_root.join(".aod/personalization.env");
    if personalization_env.exists() {
        fs::remove_file(&personalization_env).expect("remove personalization env");
    }

    let warm = run_init_in_clone(
        &clone_root,
        &build_canonical_stdin(&clone_root),
        &["--no-precommit"],
    );
    assert_eq!(
        warm.status,
        0,
        "warm init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
        warm.status,
        stdout_tail(&warm.stdout, 1500),
        stderr_tail(&warm.stderr, 1500)
    );

    for (label, run) in [("cold", &cold), ("warm", &warm)] {
        assert!(
            run.stderr.contains("total_ms=") && run.stderr.contains("slowest-duration_ms="),
            "{label} init trace summary should expose millisecond totals\nstderr tail:\n{}",
            stderr_tail(&run.stderr, 2000)
        );
    }
}

#[test]
fn init_trace_summary_can_collect_cold_and_warm_samples_with_and_without_precommit_in_one_clone() {
    let temp_dir = unique_temp_dir("trace-summary-cold-warm-precommit");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    for (label, args) in [
        ("no-precommit", &["--no-precommit"][..]),
        ("precommit", &["--precommit"][..]),
    ] {
        restore_init_script(&clone_root);
        let personalization_env = clone_root.join(".aod/personalization.env");
        if personalization_env.exists() {
            fs::remove_file(&personalization_env).expect("remove personalization env");
        }

        let cold = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root), args);
        assert_eq!(
            cold.status,
            0,
            "cold {label} init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
            cold.status,
            stdout_tail(&cold.stdout, 1500),
            stderr_tail(&cold.stderr, 1500)
        );

        restore_init_script(&clone_root);
        if personalization_env.exists() {
            fs::remove_file(&personalization_env).expect("remove personalization env");
        }

        let warm = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root), args);
        assert_eq!(
            warm.status,
            0,
            "warm {label} init.sh exit {}; stdout tail:\n{}\nstderr tail:\n{}",
            warm.status,
            stdout_tail(&warm.stdout, 1500),
            stderr_tail(&warm.stderr, 1500)
        );

        for (sample, run) in [("cold", &cold), ("warm", &warm)] {
            assert!(
                run.stderr.contains("slowest-phase=") && run.stderr.contains("slowest-duration_ms="),
                "{label} {sample} init trace summary should expose the slowest-phase timing fields\nstderr tail:\n{}",
                stderr_tail(&run.stderr, 2000)
            );
        }
    }
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
        "tachi-rust-init-trace-summary-{label}-{suffix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}

fn clone_into_tmpdir(temp_dir: &Path) -> PathBuf {
    let repo_root = workspace_root();
    let head_sha = git_stdout(&repo_root, &["rev-parse", "HEAD"]);
    let origin_url = git_stdout(&repo_root, &["remote", "get-url", "origin"]);
    let personalized_paths = personalized_manifest_paths(&repo_root);
    let clone_root = temp_dir.join("tachi");

    let clone = Command::new("git")
        .args(["clone", "--shared", "--sparse", "--quiet"])
        .arg(&repo_root)
        .arg(&clone_root)
        .output()
        .expect("clone repo into temp dir");
    assert!(
        clone.status.success(),
        "git clone failed: {}",
        String::from_utf8_lossy(&clone.stderr)
    );

    let origin_set = Command::new("git")
        .args(["remote", "set-url", "origin", origin_url.trim()])
        .current_dir(&clone_root)
        .output()
        .expect("set origin url");
    assert!(
        origin_set.status.success(),
        "git remote set-url failed: {}",
        String::from_utf8_lossy(&origin_set.stderr)
    );

    let sparse_init = Command::new("git")
        .args(["sparse-checkout", "init", "--no-cone"])
        .current_dir(&clone_root)
        .output()
        .expect("init sparse checkout");
    assert!(
        sparse_init.status.success(),
        "git sparse-checkout init failed: {}",
        String::from_utf8_lossy(&sparse_init.stderr)
    );

    let mut sparse_paths = vec![
        ".aod/template-manifest.txt".to_string(),
        ".aod/scripts/bash/template-substitute.sh".to_string(),
        ".aod/scripts/bash/init-input.sh".to_string(),
        ".aod/scripts/bash/template-config-load.sh".to_string(),
        ".aod/scripts/bash/template-git.sh".to_string(),
        ".aod/scripts/bash/github-lifecycle.sh".to_string(),
        ".aod/memory/constitution.md".to_string(),
        ".aod/templates/constitution-clean.md".to_string(),
        ".claude/rules/*.md".to_string(),
        "scripts/init.sh".to_string(),
        "docs/product/01_Product_Vision/product-vision.md".to_string(),
        "stacks/**/STACK.md".to_string(),
        "stacks/**/defaults.env".to_string(),
    ];
    sparse_paths.extend(
        personalized_paths
            .into_iter()
            .map(|path| path.display().to_string()),
    );

    let sparse_set = Command::new("git")
        .args(["sparse-checkout", "set", "--no-cone"])
        .args(&sparse_paths)
        .current_dir(&clone_root)
        .output()
        .expect("set sparse checkout patterns");
    assert!(
        sparse_set.status.success(),
        "git sparse-checkout set failed: {}",
        String::from_utf8_lossy(&sparse_set.stderr)
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

    sync_init_script(&clone_root);

    clone_root
}

fn personalized_manifest_paths(repo_root: &Path) -> Vec<PathBuf> {
    let manifest = repo_root.join(".aod/template-manifest.txt");
    let manifest_text = fs::read_to_string(&manifest).expect("read manifest");
    let mut out = Vec::new();

    for line in manifest_text.lines() {
        let line = line.trim();
        if !line.starts_with("personalized|") {
            continue;
        }
        let rel = line.trim_start_matches("personalized|");
        if rel.is_empty() {
            continue;
        }
        out.push(PathBuf::from(rel));
    }

    out
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

fn run_init_in_clone(clone_root: &Path, stdin_payload: &str, args: &[&str]) -> InitRun {
    let fake_home = clone_root
        .parent()
        .expect("clone root parent")
        .join("fake_home");
    fs::create_dir_all(&fake_home).expect("create fake home");

    let output = Command::new(std::env::var("BASH").unwrap_or_else(|_| "/bin/bash".to_string()))
        .arg("./scripts/init.sh")
        .args(args)
        .current_dir(clone_root)
        .env("LC_ALL", "C")
        .env("HOME", &fake_home)
        .env("PATH", safe_path())
        .env("AOD_RATIFICATION_DATE_OVERRIDE", "2026-05-04")
        .env("AOD_CURRENT_DATE_OVERRIDE", "2026-05-04")
        .env("AOD_INIT_TRACE", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
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

fn restore_init_script(clone_root: &Path) {
    sync_init_script(clone_root);
}

fn sync_init_script(clone_root: &Path) {
    let workspace_init = workspace_root().join("scripts/init.sh");
    let clone_init = clone_root.join("scripts/init.sh");
    fs::copy(&workspace_init, &clone_init).unwrap_or_else(|err| {
        panic!(
            "sync init script {} -> {}: {err}",
            workspace_init.display(),
            clone_init.display()
        )
    });
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

fn stderr_tail(text: &str, max_chars: usize) -> &str {
    tail_chars(text, max_chars)
}

fn stdout_tail(text: &str, max_chars: usize) -> &str {
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

#[derive(Debug)]
struct InitRun {
    status: i32,
    stdout: String,
    stderr: String,
}
