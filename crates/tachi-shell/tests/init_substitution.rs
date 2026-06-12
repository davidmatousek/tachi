use std::collections::BTreeSet;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};

#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[test]
fn init_substitution_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_init_sh_substitution.py")
            .exists(),
        "init substitution coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn init_substitution_leaves_unmanifested_files_unchanged() {
    let temp_dir = unique_temp_dir("substitution-scope");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let stray_path = clone_root.join("sandbox/rogue-note.md");
    fs::create_dir_all(stray_path.parent().expect("rogue parent")).expect("create stray dir");
    let original = "This file should stay literal: {{PROJECT_NAME}} and {{CURRENT_DATE}}.\n";
    fs::write(&stray_path, original).expect("write stray file");

    let init_run = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root));
    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        init_run.status,
        stderr_tail(&init_run.stderr, 1500)
    );

    let after = fs::read_to_string(&stray_path).expect("read stray file after init");
    assert_eq!(
        after, original,
        "init.sh should only substitute files tracked in .aod/template-manifest.txt"
    );
}

#[test]
fn init_substitution_leaves_tracked_unmanifested_files_unchanged() {
    let temp_dir = unique_temp_dir("substitution-tracked-scope");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let stray_path = clone_root.join("sandbox/rogue-tracked-note.md");
    fs::create_dir_all(stray_path.parent().expect("rogue tracked parent"))
        .expect("create stray tracked dir");
    let original = "This tracked file should stay literal: {{PROJECT_NAME}} and {{CURRENT_DATE}}.\n";
    fs::write(&stray_path, original).expect("write tracked stray file");
    git(&clone_root, &["add", "sandbox/rogue-tracked-note.md"]);

    let init_run = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root));
    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        init_run.status,
        stderr_tail(&init_run.stderr, 1500)
    );

    let after = fs::read_to_string(&stray_path).expect("read tracked stray file after init");
    assert_eq!(
        after, original,
        "init.sh should only substitute files listed in .aod/template-manifest.txt, not every tracked file"
    );
}

#[test]
fn personalized_tree_bytes_match_baseline() {
    let temp_dir = unique_temp_dir("substitution-bytes");
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

    let baseline_dir = workspace_root().join("tests/fixtures/init-baseline-tree");
    let baseline_has_files = baseline_dir
        .read_dir()
        .ok()
        .and_then(|mut entries| entries.next())
        .is_some();
    assert!(
        baseline_dir.is_dir() && baseline_has_files,
        "init baseline tree should already be committed"
    );

    let contract_paths = personalized_contract_paths();
    let baseline_paths = files_in_tree(&baseline_dir, false);
    let compare_paths = contract_paths
        .intersection(&baseline_paths)
        .cloned()
        .collect::<Vec<_>>();

    let missing_from_actual = compare_paths
        .iter()
        .filter(|rel| !clone_root.join(rel).is_file())
        .cloned()
        .collect::<Vec<_>>();
    assert!(
        missing_from_actual.is_empty(),
        "init.sh dropped {} file(s) from the personalized contract/fixture intersection. First 10:\n  {}",
        missing_from_actual.len(),
        missing_from_actual
            .iter()
            .take(10)
            .map(|path| path.display().to_string())
            .collect::<Vec<_>>()
            .join("\n  ")
    );

    let mut mismatches = Vec::new();
    for rel in compare_paths {
        let actual_bytes = fs::read(clone_root.join(&rel))
            .unwrap_or_else(|err| panic!("read actual {}: {err}", rel.display()));
        let baseline_bytes = fs::read(baseline_dir.join(&rel))
            .unwrap_or_else(|err| panic!("read baseline {}: {err}", rel.display()));
        if actual_bytes != baseline_bytes {
            mismatches.push(rel.display().to_string());
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} file(s) drifted from personalized baseline. First 10: {:?}",
        mismatches.len(),
        mismatches.iter().take(10).collect::<Vec<_>>()
    );
}

#[test]
fn personalized_tree_modes_match_baseline() {
    let temp_dir = unique_temp_dir("substitution-modes");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);
    let init_run = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root));
    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        init_run.status,
        stderr_tail(&init_run.stderr, 1500)
    );

    let baseline_dir = workspace_root().join("tests/fixtures/init-baseline-tree");
    let mut drifts = Vec::new();
    let contract_paths = personalized_contract_paths();
    let baseline_paths = files_in_tree(&baseline_dir, false);
    for rel in contract_paths.intersection(&baseline_paths) {
        let baseline_path = baseline_dir.join(&rel);
        if !baseline_path.is_file() {
            continue;
        }
        let actual_mode = fs::metadata(clone_root.join(&rel))
            .expect("read actual metadata")
            .permissions()
            .mode()
            & 0o777;
        let baseline_mode = fs::metadata(&baseline_path)
            .expect("read baseline metadata")
            .permissions()
            .mode()
            & 0o777;
        if actual_mode != baseline_mode {
            drifts.push(format!(
                "{}: {} vs baseline {}",
                rel.display(),
                format_args!("0o{actual_mode:o}"),
                format_args!("0o{baseline_mode:o}")
            ));
        }
    }

    assert!(
        drifts.is_empty(),
        "mode drift on {} file(s): {:?}",
        drifts.len(),
        drifts.iter().take(5).collect::<Vec<_>>()
    );
}

fn personalized_contract_paths() -> BTreeSet<PathBuf> {
    let root = workspace_root();
    let manifest = root.join(".aod/template-manifest.txt");
    let manifest_text = fs::read_to_string(&manifest).expect("read manifest");
    let mut out = BTreeSet::new();

    for line in manifest_text.lines() {
        let line = line.trim();
        if !line.starts_with("personalized|") {
            continue;
        }
        let rel = line.trim_start_matches("personalized|");
        if rel.is_empty() {
            continue;
        }
        out.insert(PathBuf::from(rel));
    }

    out.insert(PathBuf::from(".aod/templates/constitution-clean.md"));
    out
}

fn files_in_tree(root: &Path, exclude_baseline_tree: bool) -> BTreeSet<PathBuf> {
    let excluded_dirs = [".git", "node_modules"];
    let excluded_suffixes = [".png", ".jpg", ".ico"];
    let excluded_path_prefix = Path::new("tests")
        .join("fixtures")
        .join("init-baseline-tree");
    let mut out = BTreeSet::new();

    for path in walk_files(root) {
        let rel = match path.strip_prefix(root) {
            Ok(rel) => rel.to_path_buf(),
            Err(_) => continue,
        };
        if rel
            .components()
            .any(|component| excluded_dirs.contains(&component.as_os_str().to_str().unwrap_or("")))
        {
            continue;
        }
        if excluded_suffixes
            .iter()
            .any(|suffix| rel.to_string_lossy().ends_with(suffix))
        {
            continue;
        }
        if exclude_baseline_tree && rel.starts_with(&excluded_path_prefix) {
            continue;
        }
        out.insert(rel);
    }

    out
}

fn walk_files(root: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut stack = vec![root.to_path_buf()];

    while let Some(dir) = stack.pop() {
        let entries = match fs::read_dir(&dir) {
            Ok(entries) => entries,
            Err(_) => continue,
        };
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                stack.push(path);
            } else if path.is_file() {
                out.push(path);
            }
        }
    }

    out
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
        "tachi-rust-init-substitution-{label}-{suffix}-{}",
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

fn git(repo_root: &Path, args: &[&str]) {
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
    stdout
        .chars()
        .rev()
        .take(max_chars)
        .collect::<String>()
        .chars()
        .rev()
        .collect()
}

#[derive(Debug)]
struct InitRun {
    status: i32,
    stdout: String,
    stderr: String,
}
