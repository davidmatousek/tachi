use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[test]
fn init_defaults_env_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_init_sh_defaults_env.py")
            .exists(),
        "init defaults.env coverage should live in Rust tests, not pytest"
    );

    assert_init_uses_safe_defaults_loader(&root);

    for fixture in [
        "tests/fixtures/config-load/valid/defaults-env-nextjs-supabase",
        "tests/fixtures/config-load/valid/defaults-env-fastapi-react",
    ] {
        let output = load_defaults_fixture(&root, &root.join(fixture), true);
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert_eq!(
            parse_rc(&stdout, "valid defaults fixture", &stderr),
            0,
            "valid defaults fixture {fixture} failed. stdout={stdout:?} stderr={stderr:?}"
        );
        for var_name in [
            "STACK_TECH_STACK",
            "STACK_TECH_STACK_DATABASE",
            "STACK_TECH_STACK_VECTOR",
            "STACK_TECH_STACK_AUTH",
            "STACK_CLOUD_PROVIDER",
        ] {
            assert!(
                !stdout.contains(&format!("UNSET={var_name}")),
                "{var_name} was not populated for {fixture}. stdout={stdout:?} stderr={stderr:?}"
            );
        }
    }

    assert_malicious_pack_rejected(&root);
    assert_missing_key_pack_rejected(&root);
}

fn assert_init_uses_safe_defaults_loader(root: &Path) {
    let init_sh = fs::read_to_string(root.join("scripts/init.sh")).expect("read scripts/init.sh");
    assert!(
        init_sh.contains("STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)"),
        "init.sh must define the Site A defaults.env whitelist"
    );
    assert!(
        init_sh.contains("aod_template_load_kv_file \"stacks/$SELECTED_PACK/defaults.env\" \"STACK_\" STACK_PACK_ALLOWED_KEYS"),
        "init.sh must load stack defaults through aod_template_load_kv_file"
    );
    assert!(
        !init_sh.contains("source \"stacks/$SELECTED_PACK/defaults.env\""),
        "init.sh must not source stack defaults.env directly"
    );
}

fn assert_malicious_pack_rejected(root: &Path) {
    let pwned_marker = Path::new("/tmp/F-256-pwned");
    let _ = fs::remove_file(pwned_marker);

    let output = load_defaults_fixture(
        root,
        &root.join("tests/fixtures/config-load/adversarial/malicious-pack-defaults.env"),
        false,
    );
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    assert_eq!(
        parse_rc(&stdout, "malicious defaults fixture", &stderr),
        8,
        "malicious defaults fixture should be rejected. stdout={stdout:?} stderr={stderr:?}"
    );
    assert!(
        !pwned_marker.exists(),
        "command substitution marker was created during malicious defaults.env load"
    );
    let stderr_lower = stderr.to_lowercase();
    assert!(
        stderr_lower.contains("malformed")
            || stderr_lower.contains("disallowed")
            || stderr_lower.contains("[aod] error"),
        "expected library rejection message on stderr; stderr={stderr:?}"
    );

    let _ = fs::remove_file(pwned_marker);
}

fn assert_missing_key_pack_rejected(root: &Path) {
    let output = load_defaults_fixture(
        root,
        &root.join("tests/fixtures/config-load/adversarial/missing-key-pack-defaults.env"),
        false,
    );
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    assert_eq!(
        parse_rc(&stdout, "missing-key defaults fixture", &stderr),
        8,
        "missing-key defaults fixture should be rejected. stdout={stdout:?} stderr={stderr:?}"
    );
    assert!(
        stderr.contains("CLOUD_PROVIDER"),
        "expected stderr to name CLOUD_PROVIDER; stderr={stderr:?}"
    );
}

fn load_defaults_fixture(root: &Path, fixture_path: &Path, dump_fields: bool) -> Output {
    let temp_dir = unique_temp_dir("defaults-env");
    fs::create_dir_all(&temp_dir).expect("create temp test directory");

    let mut script = vec![
        "set +e".to_string(),
        format!(
            "source '{}'",
            root.join(".aod/scripts/bash/template-config-load.sh")
                .display()
        ),
        "STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)".to_string(),
        format!(
            "aod_template_load_kv_file '{}' 'STACK_' STACK_PACK_ALLOWED_KEYS",
            fixture_path.display()
        ),
        "RC=$?".to_string(),
        "echo RC=$RC".to_string(),
    ];

    if dump_fields {
        for var_name in [
            "STACK_TECH_STACK",
            "STACK_TECH_STACK_DATABASE",
            "STACK_TECH_STACK_VECTOR",
            "STACK_TECH_STACK_AUTH",
            "STACK_CLOUD_PROVIDER",
        ] {
            script.push(format!(
                "declare -p {var_name} 2>/dev/null || echo UNSET={var_name}"
            ));
        }
    }

    let output = run_bash(&script.join("; "));
    fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
    output
}

fn run_bash(script: &str) -> Output {
    Command::new(std::env::var("BASH").unwrap_or_else(|_| "/bin/bash".to_string()))
        .arg("-c")
        .arg(script)
        .env_clear()
        .env("LC_ALL", "C")
        .env("PATH", std::env::var("PATH").expect("PATH available"))
        .output()
        .expect("run bash helper")
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
        "tachi-rust-init-defaults-{label}-{suffix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}
