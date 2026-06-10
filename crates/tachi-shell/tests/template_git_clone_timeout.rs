use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[test]
fn template_git_clone_timeout_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_template_git_clone_timeout.py")
            .exists(),
        "template git clone timeout coverage should live in Rust tests, not pytest"
    );

    assert_template_git_declares_timeout_contract(&root);
    assert_hanging_clone_times_out_and_cleans_destdir(&root, 3, 5.0);
    assert_invalid_timeouts_are_rejected_before_clone(&root);
    assert_fast_clone_succeeds_with_default_timeout(&root);
}

fn assert_template_git_declares_timeout_contract(root: &Path) {
    let template_git = fs::read_to_string(root.join(".aod/scripts/bash/template-git.sh"))
        .expect("read template-git.sh");

    assert!(
        template_git.contains("local fetch_timeout=\"${AOD_FETCH_TIMEOUT:-60}\""),
        "template-git.sh must default AOD_FETCH_TIMEOUT to 60 seconds"
    );
    assert!(
        template_git.contains("^\\[1-9\\]\\[0-9\\]*$") || template_git.contains("^[1-9][0-9]*$"),
        "template-git.sh must validate AOD_FETCH_TIMEOUT as a positive integer"
    );
}

fn assert_hanging_clone_times_out_and_cleans_destdir(
    root: &Path,
    timeout_seconds: u64,
    upper_bound_seconds: f64,
) {
    let temp_dir = unique_temp_dir("template-git-timeout");
    fs::create_dir_all(&temp_dir).expect("create temp directory");
    let destdir = temp_dir.join("fetched");
    let git_bin_dir = install_hanging_git_wrapper(&temp_dir);

    let start = Instant::now();
    let output = run_fetch(
        root,
        "https://example.invalid/test.git",
        "main",
        &destdir,
        Some(timeout_seconds.to_string().as_str()),
        Duration::from_secs((upper_bound_seconds as u64) + 5),
        Some(&git_bin_dir),
    );
    let elapsed = start.elapsed().as_secs_f64();

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let rc = parse_rc(&stdout, "hanging clone", &stderr);

    assert_eq!(
        rc, 9,
        "watchdog returned rc {rc} for hanging clone. stdout={stdout:?} stderr={stderr:?}"
    );
    let lower_bound_seconds = (timeout_seconds as f64 - 1.0).max(0.5);
    assert!(
        elapsed >= lower_bound_seconds && elapsed <= upper_bound_seconds,
        "elapsed {elapsed:.2}s outside expected window [{lower_bound_seconds:.2}, {upper_bound_seconds:.2}]"
    );
    assert!(
        !destdir.exists(),
        "destdir should be removed after timeout. stderr={stderr:?}"
    );
    assert!(
        stderr.contains("timed out after 3s"),
        "stderr should mention the configured timeout. stderr={stderr:?}"
    );

    fs::remove_dir_all(&temp_dir).expect("remove temp directory");
}

fn assert_invalid_timeouts_are_rejected_before_clone(root: &Path) {
    for timeout_value in ["0", "abc", "01"] {
        let temp_dir = unique_temp_dir("template-git-invalid-timeout");
        fs::create_dir_all(&temp_dir).expect("create temp directory");
        let destdir = temp_dir.join("fetched");
        let fake_url = "file:///nonexistent/path/that/should/never/be/reached.git";

        let output = run_fetch(
            root,
            fake_url,
            "main",
            &destdir,
            Some(timeout_value),
            Duration::from_secs(10),
            None,
        );

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let rc = parse_rc(&stdout, "invalid timeout", &stderr);

        assert_eq!(
            rc, 1,
            "AOD_FETCH_TIMEOUT={timeout_value:?} should fail validation before clone. stdout={stdout:?} stderr={stderr:?}"
        );
        assert!(
            stderr.contains("AOD_FETCH_TIMEOUT"),
            "stderr should name AOD_FETCH_TIMEOUT for value {timeout_value:?}. stderr={stderr:?}"
        );
        assert!(
            !destdir.exists(),
            "destdir should not exist when validation fails before clone"
        );

        fs::remove_dir_all(&temp_dir).expect("remove temp directory");
    }
}

fn assert_fast_clone_succeeds_with_default_timeout(root: &Path) {
    let temp_dir = unique_temp_dir("template-git-fast-clone");
    fs::create_dir_all(&temp_dir).expect("create temp directory");
    let upstream = temp_dir.join("tiny-upstream");
    let destdir = temp_dir.join("fetched");

    init_tiny_upstream(&upstream);

    let start = Instant::now();
    let output = run_fetch(
        root,
        &format!("file://{}", upstream.display()),
        "main",
        &destdir,
        None,
        Duration::from_secs(15),
        None,
    );
    let elapsed = start.elapsed().as_secs_f64();

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let rc = parse_rc(&stdout, "fast clone", &stderr);

    assert_eq!(
        rc, 0,
        "fast clone should succeed with default timeout. stdout={stdout:?} stderr={stderr:?}"
    );
    assert!(destdir.is_dir(), "destdir should exist after fast clone");
    assert!(
        elapsed < 10.0,
        "fast clone took {elapsed:.2}s, suggesting watchdog leakage"
    );

    fs::remove_dir_all(&temp_dir).expect("remove temp directory");
}

fn run_fetch(
    root: &Path,
    url: &str,
    ref_name: &str,
    destdir: &Path,
    fetch_timeout: Option<&str>,
    command_timeout: Duration,
    path_prefix: Option<&Path>,
) -> Output {
    let mut script = vec![
        "set +e".to_string(),
        format!(
            "source '{}'",
            root.join(".aod/scripts/bash/template-config-load.sh")
                .display()
        ),
        format!(
            "source '{}'",
            root.join(".aod/scripts/bash/template-git.sh").display()
        ),
        format!(
            "aod_template_fetch_upstream \"{url}\" \"{ref_name}\" \"{}\"",
            destdir.display()
        ),
        "RC=$?".to_string(),
        "echo RC=$RC".to_string(),
    ];

    if fetch_timeout.is_none() {
        script.insert(1, "unset AOD_FETCH_TIMEOUT".to_string());
    }

    let mut command =
        Command::new(std::env::var("BASH").unwrap_or_else(|_| "/bin/bash".to_string()));
    command.arg("-c").arg(script.join("; ")).env_clear();
    command
        .env("LC_ALL", "C")
        .env("PATH", build_path(path_prefix))
        .env("GIT_TERMINAL_PROMPT", "0")
        .env(
            "HOME",
            std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string()),
        );

    if let Some(fetch_timeout) = fetch_timeout {
        command.env("AOD_FETCH_TIMEOUT", fetch_timeout);
    }

    command
        .output_timeout(command_timeout)
        .expect("run bash helper with timeout")
}

fn install_hanging_git_wrapper(temp_dir: &Path) -> PathBuf {
    let bin_dir = temp_dir.join("bin");
    fs::create_dir_all(&bin_dir).expect("create wrapper bin directory");
    let wrapper_path = bin_dir.join("git");
    let real_git = find_git_binary();
    let wrapper = format!(
        "#!/bin/bash\nif [ \"$1\" = \"clone\" ]; then\n  destdir=\"${{@: -1}}\"\n  mkdir -p \"$destdir\"\n  while true; do sleep 1; done\nfi\nexec \"{}\" \"$@\"\n",
        real_git.display()
    );
    fs::write(&wrapper_path, wrapper).expect("write git wrapper");

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&wrapper_path)
            .expect("wrapper metadata")
            .permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&wrapper_path, perms).expect("chmod git wrapper");
    }

    bin_dir
}

fn init_tiny_upstream(upstream: &Path) {
    fs::create_dir_all(upstream).expect("create tiny upstream directory");
    run_git(
        [
            "init",
            "--quiet",
            "--initial-branch=main",
            upstream.to_str().expect("utf-8 path"),
        ],
        None,
    );
    fs::write(upstream.join("README.md"), "tiny test upstream\n").expect("write README");
    run_git(
        [
            "-C",
            upstream.to_str().expect("utf-8 path"),
            "add",
            "README.md",
        ],
        None,
    );
    run_git(
        [
            "-C",
            upstream.to_str().expect("utf-8 path"),
            "commit",
            "--quiet",
            "-m",
            "init",
        ],
        Some(&[
            ("GIT_AUTHOR_NAME", "Test"),
            ("GIT_AUTHOR_EMAIL", "test@example.com"),
            ("GIT_COMMITTER_NAME", "Test"),
            ("GIT_COMMITTER_EMAIL", "test@example.com"),
        ]),
    );
}

fn run_git<const N: usize>(args: [&str; N], extra_env: Option<&[(&str, &str)]>) {
    let mut command = Command::new(find_git_binary());
    command.args(args).env_clear();
    command
        .env("LC_ALL", "C")
        .env("PATH", std::env::var("PATH").expect("PATH available"))
        .env(
            "HOME",
            std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string()),
        );

    if let Some(extra_env) = extra_env {
        for (key, value) in extra_env {
            command.env(key, value);
        }
    }

    let output = command.output().expect("run git");
    assert!(
        output.status.success(),
        "git command failed: args={args:?} stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
}

fn find_git_binary() -> PathBuf {
    let path = std::env::var_os("PATH").expect("PATH available");
    for dir in std::env::split_paths(&path) {
        let candidate = dir.join("git");
        if candidate.is_file() {
            return candidate;
        }
    }
    panic!("git binary not found on PATH");
}

fn build_path(path_prefix: Option<&Path>) -> String {
    let path = std::env::var("PATH").expect("PATH available");
    match path_prefix {
        Some(prefix) => format!("{}:{path}", prefix.display()),
        None => path,
    }
}

fn parse_rc(stdout: &str, context: &str, stderr: &str) -> i32 {
    stdout
        .lines()
        .find_map(|line| line.strip_prefix("RC="))
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or_else(|| {
            panic!("missing RC line for {context}. stdout={stdout:?} stderr={stderr:?}")
        })
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
        "tachi-rust-{label}-{suffix}-{}",
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}

trait OutputTimeout {
    fn output_timeout(&mut self, timeout: Duration) -> io::Result<Output>;
}

impl OutputTimeout for Command {
    fn output_timeout(&mut self, timeout: Duration) -> io::Result<Output> {
        self.stdout(Stdio::piped());
        self.stderr(Stdio::piped());
        let mut child = self.spawn()?;
        let start = Instant::now();

        loop {
            if let Some(_status) = child.try_wait()? {
                return child.wait_with_output();
            }
            if start.elapsed() > timeout {
                child.kill()?;
                let _ = child.wait();
                return Err(io::Error::new(
                    io::ErrorKind::TimedOut,
                    format!("command exceeded {:?}", timeout),
                ));
            }
            thread::sleep(Duration::from_millis(50));
        }
    }
}
