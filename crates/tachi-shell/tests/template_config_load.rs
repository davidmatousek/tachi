use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
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

#[test]
fn template_config_load_integration_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_template_config_load_integration.py")
            .exists(),
        "template-config-load integration coverage should live in Rust tests, not pytest"
    );

    for case in site_b_cases(&root) {
        let temp_dir = unique_temp_dir(case.id);
        fs::create_dir_all(&temp_dir).expect("create temp test directory");
        let fixture_path = materialize_site_fixture(&temp_dir, &case.fixture);
        let pwned_marker = Path::new("/tmp/F-256-pwned");
        let _ = fs::remove_file(pwned_marker);

        let script = build_site_b_script(&root, &fixture_path, case.expected_rc == 0);
        let output = run_bash(&script);
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let actual_rc = parse_rc(&stdout, "RC", case.id, case.marker, &stderr);

        assert_eq!(
            actual_rc, case.expected_rc,
            "unexpected rc for {} ({}). stdout={stdout:?} stderr={stderr:?}",
            case.id, case.marker
        );
        assert!(
            !pwned_marker.exists(),
            "command-injection marker was created for {} ({}). stderr={stderr:?}",
            case.id,
            case.marker
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
            for field in [
                "version",
                "sha",
                "updated_at",
                "upstream_url",
                "manifest_sha256",
            ] {
                let unset_marker = format!("UNSET={field}");
                assert!(
                    !stdout.contains(&unset_marker),
                    "caller-scope variable {field} was unset for {} ({}). stdout={stdout:?} stderr={stderr:?}",
                    case.id,
                    case.marker
                );
            }
        }

        let _ = fs::remove_file(pwned_marker);
        fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
    }

    assert_site_b_writer_roundtrip(&root);

    for case in site_d_cases(&root) {
        let temp_dir = unique_temp_dir(case.id);
        fs::create_dir_all(&temp_dir).expect("create temp test directory");
        let fixture_path = materialize_site_fixture(&temp_dir, &case.fixture);

        let script = build_site_d_script(&root, &fixture_path, &case.expected_assignments);
        let output = run_bash(&script);
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let actual_rc = parse_rc(&stdout, "RC", case.id, case.marker, &stderr);

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
            for var_name in &case.expected_assignments {
                let unset_marker = format!("UNSET={var_name}");
                assert!(
                    !stdout.contains(&unset_marker),
                    "caller-scope variable {var_name} was unset for {} ({}). stdout={stdout:?} stderr={stderr:?}",
                    case.id,
                    case.marker
                );
            }
        }

        fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
    }

    assert_site_d_toctou_residual_race(&root);
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

struct SiteCase {
    id: &'static str,
    fixture: SiteFixture,
    expected_rc: i32,
    expected_assignments: Vec<&'static str>,
    expected_stderr: Option<&'static str>,
    marker: &'static str,
}

enum Fixture {
    Bytes(Vec<u8>),
    MissingPathArgument,
    NonexistentPath,
    DirectoryPath,
}

enum SiteFixture {
    Existing(PathBuf),
    Bytes(Vec<u8>),
    EmptyPath,
    NonexistentPath,
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

fn site_b_cases(root: &Path) -> Vec<SiteCase> {
    let fixtures = root.join("tests/fixtures/config-load");
    vec![
        SiteCase {
            id: "site_b_malformed_command_injection",
            fixture: SiteFixture::Existing(
                fixtures
                    .join("adversarial")
                    .join("aod-kit-version-malformed"),
            ),
            expected_rc: 8,
            expected_assignments: Vec::new(),
            expected_stderr: Some("malformed line"),
            marker: "command-injection rejected by lowercase version loader",
        },
        SiteCase {
            id: "site_b_valid_lowercase",
            fixture: SiteFixture::Existing(fixtures.join("valid").join("aod-kit-version-valid")),
            expected_rc: 0,
            expected_assignments: Vec::new(),
            expected_stderr: None,
            marker: "valid lowercase five-field aod-kit-version loads cleanly",
        },
        SiteCase {
            id: "site_b_bare_version_empty",
            fixture: SiteFixture::Bytes(
                b"version=\nsha=abc123def456abc123def456abc123def456abcd\nupdated_at=2026-05-04T12:00:00Z\nupstream_url=https://github.com/example/upstream\nmanifest_sha256=abc123def456abc123def456abc123def456abc123def456abc123def456abcd\n"
                    .to_vec(),
            ),
            expected_rc: 0,
            expected_assignments: Vec::new(),
            expected_stderr: None,
            marker: "bare version= empty value stays accepted",
        },
        SiteCase {
            id: "site_b_uppercase_rejected",
            fixture: SiteFixture::Bytes(b"VERSION=4.28.0\n".to_vec()),
            expected_rc: 8,
            expected_assignments: Vec::new(),
            expected_stderr: Some("malformed line"),
            marker: "uppercase keys are rejected in lowercase mode",
        },
    ]
}

fn site_d_cases(root: &Path) -> Vec<SiteCase> {
    let fixtures = root.join("tests/fixtures/config-load");
    vec![
        SiteCase {
            id: "site_d_collapsed_body_valid",
            fixture: SiteFixture::Existing(
                fixtures.join("valid").join("personalization-env-valid"),
            ),
            expected_rc: 0,
            expected_assignments: vec![
                "AOD_PERSONALIZATION_PROJECT_NAME",
                "AOD_PERSONALIZATION_GITHUB_ORG",
                "AOD_PERSONALIZATION_TECH_STACK",
                "AOD_PERSONALIZATION_CLOUD_PROVIDER",
            ],
            expected_stderr: None,
            marker: "collapsed wrapper delegates to library and populates caller scope",
        },
        SiteCase {
            id: "site_d_missing_path",
            fixture: SiteFixture::EmptyPath,
            expected_rc: 1,
            expected_assignments: Vec::new(),
            expected_stderr: Some("<path>"),
            marker: "empty path argument is rejected",
        },
        SiteCase {
            id: "site_d_file_absent",
            fixture: SiteFixture::NonexistentPath,
            expected_rc: 3,
            expected_assignments: Vec::new(),
            expected_stderr: Some("does not exist"),
            marker: "absent path is rejected",
        },
        SiteCase {
            id: "site_d_embedded_nul",
            fixture: SiteFixture::Bytes(
                b"PROJECT_NAME=\"tachi\"\nPROJECT_DESCRIPTION=\"test\"\nGITHUB_ORG=\"test\"\nGITHUB_REPO=\"test\"\nAI_AGENT=\"claude\"\nTECH_STACK=\"nextjs\"\nTECH_STACK_DATABASE=\"pg\"\nTECH_STACK_VECTOR=\"N/A\"\nTECH_STACK_AUTH=\"jwt\"\nRATIFICATION_DATE=\"2026-05-04\"\nCURRENT_DATE=\"2026-05-04\"\nCLOUD_PROVIDER=\"vercel\0pwned\"\n"
                    .to_vec(),
            ),
            expected_rc: 8,
            expected_assignments: Vec::new(),
            expected_stderr: Some("NUL byte"),
            marker: "embedded NUL is rejected by library pre-check",
        },
        SiteCase {
            id: "site_d_missing_canonical_key",
            fixture: SiteFixture::Bytes(
                b"PROJECT_NAME=\"tachi\"\nPROJECT_DESCRIPTION=\"test\"\nGITHUB_ORG=\"test\"\nGITHUB_REPO=\"test\"\nAI_AGENT=\"claude\"\nTECH_STACK=\"nextjs\"\nTECH_STACK_DATABASE=\"pg\"\nTECH_STACK_VECTOR=\"N/A\"\nTECH_STACK_AUTH=\"jwt\"\nRATIFICATION_DATE=\"2026-05-04\"\nCURRENT_DATE=\"2026-05-04\"\n"
                    .to_vec(),
            ),
            expected_rc: 8,
            expected_assignments: Vec::new(),
            expected_stderr: Some("CLOUD_PROVIDER"),
            marker: "missing canonical key is rejected by whitelist post-pass",
        },
    ]
}

fn materialize_site_fixture(temp_dir: &Path, fixture: &SiteFixture) -> String {
    match fixture {
        SiteFixture::Existing(path) => path.display().to_string(),
        SiteFixture::Bytes(bytes) => {
            let fixture_file = temp_dir.join("fixture.env");
            fs::write(&fixture_file, bytes).expect("write site fixture file");
            fixture_file.display().to_string()
        }
        SiteFixture::EmptyPath => String::new(),
        SiteFixture::NonexistentPath => temp_dir.join("does_not_exist.env").display().to_string(),
    }
}

fn build_site_b_script(root: &Path, fixture_path: &str, dump_fields: bool) -> String {
    let mut parts = vec![
        "set +e".to_string(),
        format!(
            "source '{}'",
            root.join(".aod/scripts/bash/template-config-load.sh")
                .display()
        ),
        format!("aod_template_load_kv_file \"{fixture_path}\" \"\" \"\" \"lower\""),
        "RC=$?".to_string(),
        "echo RC=$RC".to_string(),
    ];

    if dump_fields {
        for field in [
            "version",
            "sha",
            "updated_at",
            "upstream_url",
            "manifest_sha256",
        ] {
            parts.push(format!(
                "declare -p {field} 2>/dev/null || echo UNSET={field}"
            ));
        }
    }

    parts.join("; ")
}

fn assert_site_b_writer_roundtrip(root: &Path) {
    let temp_dir = unique_temp_dir("site_b_writer_roundtrip");
    fs::create_dir_all(&temp_dir).expect("create temp test directory");
    let dest_path = temp_dir.join("aod-kit-version");
    let script = format!(
        "set +e; \
         source '{}'; \
         source '{}'; \
         aod_template_write_version_file '{}' \
           'v1.0.0' \
           'abc123def456abc123def456abc123def456abcd' \
           '2026-05-04T12:00:00Z' \
           'https://github.com/example/upstream' \
           'abc123def456abc123def456abc123def456abc123def456abc123def456abcd'; \
         WR_RC=$?; echo WR_RC=$WR_RC; \
         aod_template_load_kv_file '{}' '' '' 'lower'; \
         RD_RC=$?; echo RD_RC=$RD_RC; \
         declare -p version 2>/dev/null || echo UNSET=version; \
         declare -p sha 2>/dev/null || echo UNSET=sha",
        root.join(".aod/scripts/bash/template-config-load.sh")
            .display(),
        root.join(".aod/scripts/bash/template-git.sh").display(),
        dest_path.display(),
        dest_path.display()
    );

    let output = run_bash(&script);
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(
        parse_rc(
            &stdout,
            "WR_RC",
            "site_b_writer_roundtrip",
            "writer produces version file",
            &stderr
        ),
        0,
        "writer failed. stdout={stdout:?} stderr={stderr:?}"
    );
    assert!(dest_path.is_file(), "writer did not create version file");
    assert_eq!(
        parse_rc(
            &stdout,
            "RD_RC",
            "site_b_writer_roundtrip",
            "reader loads written version file",
            &stderr
        ),
        0,
        "round-trip read failed. stdout={stdout:?} stderr={stderr:?}"
    );
    assert!(
        stdout.contains("declare -- version=\"v1.0.0\""),
        "caller-scope version missing after roundtrip. stdout={stdout:?}"
    );
    assert!(
        !stdout.contains("UNSET=sha"),
        "caller-scope sha missing after roundtrip. stdout={stdout:?}"
    );

    fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
}

fn build_site_d_script(root: &Path, fixture_path: &str, dump_fields: &[&str]) -> String {
    let mut parts = vec![
        "set +e".to_string(),
        format!(
            "source '{}'",
            root.join(".aod/scripts/bash/template-config-load.sh")
                .display()
        ),
        format!(
            "source '{}'",
            root.join(".aod/scripts/bash/template-substitute.sh")
                .display()
        ),
        format!("aod_template_load_personalization_env \"{fixture_path}\""),
        "RC=$?".to_string(),
        "echo RC=$RC".to_string(),
    ];

    for var_name in dump_fields {
        parts.push(format!(
            "declare -p {var_name} 2>/dev/null || echo UNSET={var_name}"
        ));
    }

    parts.join("; ")
}

fn assert_site_d_toctou_residual_race(root: &Path) {
    let temp_dir = unique_temp_dir("site_d_toctou_residual_race");
    fs::create_dir_all(&temp_dir).expect("create temp test directory");
    let fixture_file = temp_dir.join("personalization.env");
    let initial_content = b"PROJECT_NAME=\"initial\"\nPROJECT_DESCRIPTION=\"initial\"\nGITHUB_ORG=\"initial\"\nGITHUB_REPO=\"initial\"\nAI_AGENT=\"initial\"\nTECH_STACK=\"initial\"\nTECH_STACK_DATABASE=\"initial\"\nTECH_STACK_VECTOR=\"initial\"\nTECH_STACK_AUTH=\"initial\"\nRATIFICATION_DATE=\"2026-05-04\"\nCURRENT_DATE=\"2026-05-04\"\nCLOUD_PROVIDER=\"initial\"\n";
    fs::write(&fixture_file, initial_content).expect("write initial fixture");
    let swapped_path = temp_dir.join("personalization-swapped.env");
    fs::write(
        &swapped_path,
        String::from_utf8_lossy(initial_content).replace("initial", "swapped"),
    )
    .expect("write swapped fixture");

    let script = format!(
        "set +e; \
         source '{}'; \
         source '{}'; \
         ( sleep 0.005; mv -f '{}' '{}' ) & \
         swap_pid=$!; \
         aod_template_load_personalization_env '{}'; \
         RC=$?; \
         wait $swap_pid 2>/dev/null; \
         echo RC=$RC; \
         declare -p AOD_PERSONALIZATION_PROJECT_NAME 2>/dev/null || echo UNSET=AOD_PERSONALIZATION_PROJECT_NAME",
        root.join(".aod/scripts/bash/template-config-load.sh")
            .display(),
        root.join(".aod/scripts/bash/template-substitute.sh")
            .display(),
        swapped_path.display(),
        fixture_file.display(),
        fixture_file.display()
    );

    let output = run_bash(&script);
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let rc = parse_rc(
        &stdout,
        "RC",
        "site_d_toctou_residual_race",
        "bounded single-snapshot race",
        &stderr,
    );
    assert!(
        rc == 0 || rc == 8,
        "unexpected TOCTOU rc {rc}. stdout={stdout:?} stderr={stderr:?}"
    );
    if rc == 0 {
        assert!(
            stdout.contains("declare -- AOD_PERSONALIZATION_PROJECT_NAME=\"initial\"")
                || stdout.contains("declare -- AOD_PERSONALIZATION_PROJECT_NAME=\"swapped\""),
            "TOCTOU success produced neither complete candidate value. stdout={stdout:?}"
        );
    }

    fs::remove_dir_all(&temp_dir).expect("remove temp test directory");
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

fn parse_rc(stdout: &str, label: &str, id: &str, marker: &str, stderr: &str) -> i32 {
    let prefix = format!("{label}=");
    stdout
        .lines()
        .find_map(|line| line.strip_prefix(&prefix))
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or_else(|| {
            panic!("missing {label} line for {id} ({marker}). stdout={stdout:?} stderr={stderr:?}")
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
        "tachi-rust-template-config-{label}-{suffix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}
