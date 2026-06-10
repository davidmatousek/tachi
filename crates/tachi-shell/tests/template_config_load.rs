use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

static TEMP_DIR_COUNTER: AtomicU64 = AtomicU64::new(0);

#[test]
fn template_config_load_unit_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_template_config_load_unit.py")
            .exists(),
        "template-config-load unit coverage should live in Rust tests, not pytest"
    );

    for case in kv_cases() {
        let temp_dir = unique_temp_dir(case.id);
        fs::create_dir_all(&temp_dir).expect("create temp test directory");
        let fixture_path = materialize_fixture(&temp_dir, &case.fixture);

        let script = build_bash_script(
            &root,
            &fixture_path,
            case.var_prefix,
            case.allowed_keys.as_deref(),
            case.key_case,
            case.expected_assignments.as_deref(),
        );

        let output =
            Command::new(std::env::var("BASH").unwrap_or_else(|_| "/bin/bash".to_string()))
                .arg("-c")
                .arg(script)
                .env_clear()
                .env("LC_ALL", "C")
                .env("PATH", std::env::var("PATH").expect("PATH available"))
                .output()
                .expect("run template-config-load helper");

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let actual_rc = stdout
            .lines()
            .find_map(|line| line.strip_prefix("RC="))
            .and_then(|value| value.parse::<i32>().ok())
            .unwrap_or_else(|| {
                panic!(
                    "missing RC line for {} ({}). stdout={stdout:?} stderr={stderr:?}",
                    case.id, case.marker
                )
            });

        assert_eq!(
            actual_rc, case.expected_rc,
            "unexpected rc for {} ({}). stdout={stdout:?} stderr={stderr:?}",
            case.id, case.marker
        );

        if let Some(expected) = case.expected_stderr {
            assert!(
                stderr.contains(expected),
                "stderr substring {expected:?} missing for {} ({}). stderr={stderr:?}",
                case.id,
                case.marker
            );
        }

        if case.expected_rc == 0 {
            for (name, expected_value) in case.expected_assignments.unwrap_or_default() {
                let expected_decl = format!("declare -- {name}=\"{expected_value}\"");
                let unset_marker = format!("UNSET={name}");
                assert!(
                    !stdout.contains(&unset_marker),
                    "caller-scope variable {name} was unset for {} ({}). stdout={stdout:?} stderr={stderr:?}",
                    case.id,
                    case.marker
                );
                assert!(
                    stdout.contains(&expected_decl),
                    "caller-scope assignment {expected_decl:?} missing for {} ({}). stdout={stdout:?} stderr={stderr:?}",
                    case.id,
                    case.marker
                );
            }
        }

        fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
    }
}

struct KvCase {
    id: &'static str,
    fixture: Fixture,
    var_prefix: &'static str,
    allowed_keys: Option<Vec<&'static str>>,
    key_case: Option<&'static str>,
    expected_rc: i32,
    expected_assignments: Option<Vec<(&'static str, &'static str)>>,
    expected_stderr: Option<&'static str>,
    marker: &'static str,
}

enum Fixture {
    Bytes(Vec<u8>),
    MissingPathArgument,
    NonexistentPath,
    DirectoryPath,
}

fn kv_cases() -> Vec<KvCase> {
    let stack_keys = vec![
        "TECH_STACK",
        "TECH_STACK_DATABASE",
        "TECH_STACK_VECTOR",
        "TECH_STACK_AUTH",
        "CLOUD_PROVIDER",
    ];

    vec![
        KvCase {
            id: "case_0_canary_positive",
            fixture: bytes(b"KEY=value\n"),
            var_prefix: "STACK_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("STACK_KEY", "value")]),
            expected_stderr: None,
            marker: "positive caller-scope assignment canary",
        },
        KvCase {
            id: "case_1_unquoted_simple",
            fixture: bytes(b"KEY=value\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "value")]),
            expected_stderr: None,
            marker: "valid unquoted value",
        },
        KvCase {
            id: "case_2_double_quoted",
            fixture: bytes(br#"KEY="quoted""#).with_newline(),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "quoted")]),
            expected_stderr: None,
            marker: "valid double-quoted value",
        },
        KvCase {
            id: "case_3_single_quoted",
            fixture: bytes(b"KEY='single-quoted'\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "single-quoted")]),
            expected_stderr: None,
            marker: "valid single-quoted value",
        },
        KvCase {
            id: "case_4_unquoted_path",
            fixture: bytes(b"KEY=path/with/slashes\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "path/with/slashes")]),
            expected_stderr: None,
            marker: "valid unquoted path",
        },
        KvCase {
            id: "case_5_unquoted_email",
            fixture: bytes(b"KEY=email@example.com\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "email@example.com")]),
            expected_stderr: None,
            marker: "valid unquoted email",
        },
        KvCase {
            id: "case_6_whitelist_all_present",
            fixture: bytes(
                b"TECH_STACK=\"nextjs\"\nTECH_STACK_DATABASE=\"supabase\"\nTECH_STACK_VECTOR=\"pgvector\"\nTECH_STACK_AUTH=\"supabase\"\nCLOUD_PROVIDER=\"vercel\"\n",
            ),
            var_prefix: "STACK_",
            allowed_keys: Some(stack_keys.clone()),
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![
                ("STACK_TECH_STACK", "nextjs"),
                ("STACK_TECH_STACK_DATABASE", "supabase"),
                ("STACK_TECH_STACK_VECTOR", "pgvector"),
                ("STACK_TECH_STACK_AUTH", "supabase"),
                ("STACK_CLOUD_PROVIDER", "vercel"),
            ]),
            expected_stderr: None,
            marker: "valid whitelisted stack defaults",
        },
        KvCase {
            id: "case_7_command_substitution",
            fixture: bytes(br#"KEY="$(rm -rf /)""#).with_newline(),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "command substitution is rejected",
        },
        KvCase {
            id: "case_8_unbalanced_quote",
            fixture: bytes(b"KEY=\"unbalanced\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "unbalanced quote is rejected",
        },
        KvCase {
            id: "case_9_backtick",
            fixture: bytes(b"KEY=`whoami`\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "backtick command substitution is rejected",
        },
        KvCase {
            id: "case_10_dollar_inside_double_quotes",
            fixture: bytes(br#"KEY="$VAR""#).with_newline(),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "parameter expansion is rejected",
        },
        KvCase {
            id: "case_11_lowercase_in_upper_mode",
            fixture: bytes(b"key=value\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "lowercase key rejected in upper mode",
        },
        KvCase {
            id: "case_12_missing_whitelisted_key",
            fixture: bytes(
                b"TECH_STACK=\"nextjs\"\nTECH_STACK_DATABASE=\"supabase\"\nTECH_STACK_VECTOR=\"pgvector\"\nTECH_STACK_AUTH=\"supabase\"\n",
            ),
            var_prefix: "STACK_",
            allowed_keys: Some(stack_keys.clone()),
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("CLOUD_PROVIDER"),
            marker: "missing required whitelist key is rejected",
        },
        KvCase {
            id: "case_13_disallowed_key",
            fixture: bytes(
                b"TECH_STACK=\"nextjs\"\nTECH_STACK_DATABASE=\"supabase\"\nTECH_STACK_VECTOR=\"pgvector\"\nTECH_STACK_AUTH=\"supabase\"\nCLOUD_PROVIDER=\"vercel\"\nMALICIOUS_KEY=\"oops\"\n",
            ),
            var_prefix: "STACK_",
            allowed_keys: Some(stack_keys),
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("MALICIOUS_KEY"),
            marker: "unknown whitelist key is rejected",
        },
        KvCase {
            id: "case_14_only_key_no_equals",
            fixture: bytes(b"KEY\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "missing equals is rejected",
        },
        KvCase {
            id: "case_15_embedded_nul",
            fixture: bytes(b"KEY=foo\0bar\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("NUL byte"),
            marker: "embedded NUL is rejected before cat",
        },
        KvCase {
            id: "case_16_bare_empty_unquoted",
            fixture: bytes(b"KEY=\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "")]),
            expected_stderr: None,
            marker: "bare empty value is accepted",
        },
        KvCase {
            id: "case_17_invalid_var_prefix",
            fixture: bytes(b"KEY=value\n"),
            var_prefix: "1bad-prefix",
            allowed_keys: None,
            key_case: None,
            expected_rc: 1,
            expected_assignments: None,
            expected_stderr: None,
            marker: "invalid variable prefix is rejected",
        },
        KvCase {
            id: "case_18_empty_quoted_value",
            fixture: bytes(br#"KEY="""#).with_newline(),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_KEY", "")]),
            expected_stderr: None,
            marker: "empty quoted value is accepted",
        },
        KvCase {
            id: "case_19_trailing_newline",
            fixture: bytes(b"A=1\nB=2\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_A", "1"), ("T_B", "2")]),
            expected_stderr: None,
            marker: "trailing newline file parses all lines",
        },
        KvCase {
            id: "case_20_no_trailing_newline",
            fixture: bytes(b"A=1\nB=2"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_A", "1"), ("T_B", "2")]),
            expected_stderr: None,
            marker: "no trailing newline file parses last line",
        },
        KvCase {
            id: "case_21_crlf",
            fixture: bytes(b"A=1\r\nB=2\r\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_A", "1"), ("T_B", "2")]),
            expected_stderr: None,
            marker: "CRLF line endings are tolerated",
        },
        KvCase {
            id: "case_22_leading_whitespace",
            fixture: bytes(b"  A=1\n\tB=2\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_A", "1"), ("T_B", "2")]),
            expected_stderr: None,
            marker: "leading whitespace is stripped",
        },
        KvCase {
            id: "case_23_blank_then_content",
            fixture: bytes(b"\n\nA=1\n\n# comment\nB=2\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 0,
            expected_assignments: Some(vec![("T_A", "1"), ("T_B", "2")]),
            expected_stderr: None,
            marker: "blank and comment lines are skipped",
        },
        KvCase {
            id: "case_24_missing_path_arg",
            fixture: Fixture::MissingPathArgument,
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 1,
            expected_assignments: None,
            expected_stderr: Some("<path>"),
            marker: "missing path argument is rejected",
        },
        KvCase {
            id: "case_25_file_absent",
            fixture: Fixture::NonexistentPath,
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 3,
            expected_assignments: None,
            expected_stderr: Some("does not exist"),
            marker: "absent file is rejected",
        },
        KvCase {
            id: "case_26a_lower_mode_accepts_lowercase",
            fixture: bytes(b"version=4.28.0\n"),
            var_prefix: "",
            allowed_keys: None,
            key_case: Some("lower"),
            expected_rc: 0,
            expected_assignments: Some(vec![("version", "4.28.0")]),
            expected_stderr: None,
            marker: "lower mode accepts lowercase keys",
        },
        KvCase {
            id: "case_26b_lower_mode_rejects_uppercase",
            fixture: bytes(b"VERSION=4.28.0\n"),
            var_prefix: "",
            allowed_keys: None,
            key_case: Some("lower"),
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("malformed line"),
            marker: "lower mode rejects uppercase keys",
        },
        KvCase {
            id: "case_27_mixed_mode_rejected",
            fixture: bytes(b"KEY=value\n"),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: Some("mixed"),
            expected_rc: 1,
            expected_assignments: None,
            expected_stderr: Some("key_case"),
            marker: "mixed mode is rejected",
        },
        KvCase {
            id: "case_28_size_cap_returns_8",
            fixture: Fixture::Bytes(size_cap_fixture()),
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 8,
            expected_assignments: None,
            expected_stderr: Some("AOD_KV_MAX_BYTES"),
            marker: "oversized fixture is rejected",
        },
        KvCase {
            id: "case_29_directory_path_returns_3",
            fixture: Fixture::DirectoryPath,
            var_prefix: "T_",
            allowed_keys: None,
            key_case: None,
            expected_rc: 3,
            expected_assignments: None,
            expected_stderr: Some("not a regular file"),
            marker: "directory path is rejected",
        },
    ]
}

trait WithNewline {
    fn with_newline(self) -> Self;
}

impl WithNewline for Fixture {
    fn with_newline(self) -> Self {
        match self {
            Fixture::Bytes(mut bytes) => {
                bytes.push(b'\n');
                Fixture::Bytes(bytes)
            }
            fixture => fixture,
        }
    }
}

fn bytes(input: &[u8]) -> Fixture {
    Fixture::Bytes(input.to_vec())
}

fn size_cap_fixture() -> Vec<u8> {
    let mut fixture = Vec::new();
    for i in 0..9000 {
        fixture.extend_from_slice(format!("K{i:04}=v\n").as_bytes());
    }
    fixture
}

fn materialize_fixture(temp_dir: &Path, fixture: &Fixture) -> String {
    match fixture {
        Fixture::Bytes(bytes) => {
            let fixture_file = temp_dir.join("fixture.env");
            fs::write(&fixture_file, bytes).expect("write fixture file");
            fixture_file.display().to_string()
        }
        Fixture::MissingPathArgument => String::new(),
        Fixture::NonexistentPath => temp_dir.join("does_not_exist.env").display().to_string(),
        Fixture::DirectoryPath => temp_dir.display().to_string(),
    }
}

fn build_bash_script(
    root: &Path,
    fixture_path: &str,
    var_prefix: &str,
    allowed_keys: Option<&[&str]>,
    key_case: Option<&str>,
    expected_assignments: Option<&[(&str, &str)]>,
) -> String {
    let mut parts = Vec::new();
    parts.push("set +e".to_string());
    parts.push(format!(
        "source '{}'",
        root.join(".aod/scripts/bash/template-config-load.sh")
            .display()
    ));

    let has_allowed_keys = if let Some(keys) = allowed_keys {
        let keys_literal = keys
            .iter()
            .map(|key| format!("\"{key}\""))
            .collect::<Vec<_>>()
            .join(" ");
        parts.push(format!("ALLOWED=({keys_literal})"));
        true
    } else {
        false
    };

    let invocation = match (has_allowed_keys, key_case) {
        (true, Some(case)) => {
            format!(
                "aod_template_load_kv_file \"{fixture_path}\" \"{var_prefix}\" ALLOWED \"{case}\""
            )
        }
        (true, None) => {
            format!("aod_template_load_kv_file \"{fixture_path}\" \"{var_prefix}\" ALLOWED")
        }
        (false, Some(case)) => {
            format!("aod_template_load_kv_file \"{fixture_path}\" \"{var_prefix}\" \"\" \"{case}\"")
        }
        (false, None) => {
            format!("aod_template_load_kv_file \"{fixture_path}\" \"{var_prefix}\"")
        }
    };
    parts.push(invocation);
    parts.push("RC=$?".to_string());
    parts.push("echo RC=$RC".to_string());

    if let Some(assignments) = expected_assignments {
        for (name, _) in assignments {
            parts.push(format!(
                "declare -p {name} 2>/dev/null || echo UNSET={name}"
            ));
        }
    }

    parts.join("; ")
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
        "tachi-rust-template-config-{label}-{suffix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}
