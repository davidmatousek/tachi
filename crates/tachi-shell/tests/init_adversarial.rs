use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

const CANONICAL_PLACEHOLDERS: [&str; 12] = [
    "PROJECT_NAME",
    "PROJECT_DESCRIPTION",
    "GITHUB_ORG",
    "GITHUB_REPO",
    "AI_AGENT",
    "TECH_STACK",
    "TECH_STACK_DATABASE",
    "TECH_STACK_VECTOR",
    "TECH_STACK_AUTH",
    "RATIFICATION_DATE",
    "CURRENT_DATE",
    "CLOUD_PROVIDER",
];

#[derive(Debug)]
struct InitRun {
    status: i32,
    stdout: String,
    stderr: String,
}

#[test]
fn init_adversarial_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_init_sh_adversarial.py")
            .exists(),
        "init adversarial coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn init_preserves_case_13_file_bytes() {
    let temp_dir = unique_temp_dir("case13");
    fs::create_dir_all(&temp_dir).expect("create temp dir");

    let clone_root = clone_into_tmpdir(&temp_dir);

    let fixture_a = clone_root.join("test_fixture_case13a.txt");
    let bytes_a = b"a\\nb";
    fs::write(&fixture_a, bytes_a).expect("write case 13a fixture");
    assert_eq!(
        fs::read(&fixture_a).expect("read case 13a fixture"),
        bytes_a,
        "pre-condition: write integrity"
    );

    let fixture_b_no_lf = clone_root.join("test_fixture_case13b_no_lf.txt");
    let bytes_b_no_lf = b"hello world";
    fs::write(&fixture_b_no_lf, bytes_b_no_lf).expect("write case 13b no-lf fixture");

    let fixture_b_with_lf = clone_root.join("test_fixture_case13b_with_lf.txt");
    let bytes_b_with_lf = b"hello world\n";
    fs::write(&fixture_b_with_lf, bytes_b_with_lf).expect("write case 13b with-lf fixture");

    let init_run = run_init_in_clone(&clone_root, &build_canonical_stdin(&clone_root));
    assert_eq!(
        init_run.status,
        0,
        "init.sh exit {}; stderr tail:\n{}",
        init_run.status,
        stderr_tail(&init_run.stderr, 1500)
    );

    assert_eq!(
        fs::read(&fixture_a).expect("read case 13a fixture after init"),
        bytes_a,
        "case 13a: byte-identity broken"
    );
    assert_eq!(
        fs::read(&fixture_b_no_lf).expect("read case 13b no-lf fixture after init"),
        bytes_b_no_lf,
        "case 13b (no LF): trailing-newline drift"
    );
    assert_eq!(
        fs::read(&fixture_b_with_lf).expect("read case 13b with-lf fixture after init"),
        bytes_b_with_lf,
        "case 13b (with LF): trailing-newline dropped"
    );

    cleanup_dir(&temp_dir);
}

#[test]
fn init_leaves_no_residual_placeholders_in_personalized_files() {
    let temp_dir = unique_temp_dir("residuals");
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

    let personalized_paths = personalized_manifest_paths(&clone_root);
    assert!(
        !personalized_paths.is_empty(),
        "no personalized-category entries in manifest"
    );

    let residuals = personalized_paths
        .into_iter()
        .filter(|rel| {
            let path = clone_root.join(rel);
            path.is_file() && file_contains_canonical_placeholder(&path)
        })
        .map(|rel| rel.display().to_string())
        .collect::<Vec<_>>();

    assert!(
        residuals.is_empty(),
        "residual `{{KEY}}` placeholders survived init in {} file(s): {:?}\nstdout tail:\n{}",
        residuals.len(),
        residuals.iter().take(10).collect::<Vec<_>>(),
        stdout_tail(&init_run.stdout, 800)
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
        "tachi-rust-init-adversarial-{label}-{suffix}-{}",
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

fn personalized_manifest_paths(clone_root: &Path) -> Vec<PathBuf> {
    let manifest = clone_root.join(".aod/template-manifest.txt");
    assert!(
        manifest.is_file(),
        "template-manifest.txt missing in clone: {}",
        manifest.display()
    );

    fs::read_to_string(&manifest)
        .expect("read template-manifest.txt")
        .lines()
        .filter_map(|line| {
            let stripped = line.trim_start();
            if stripped.is_empty() || stripped.starts_with('#') {
                return None;
            }
            line.strip_prefix("personalized|")
                .map(|rel| PathBuf::from(rel.trim_end_matches('\r')))
        })
        .collect()
}

fn file_contains_canonical_placeholder(path: &Path) -> bool {
    let data = match fs::read(path) {
        Ok(data) => data,
        Err(_) => return false,
    };

    CANONICAL_PLACEHOLDERS.iter().any(|key| {
        let needle = format!("{{{{{key}}}}}");
        data.windows(needle.len())
            .any(|window| window == needle.as_bytes())
    })
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

fn cleanup_dir(path: &Path) {
    if let Err(err) = fs::remove_dir_all(path) {
        if path.exists() {
            panic!("failed to remove {}: {err}", path.display());
        }
    }
}
