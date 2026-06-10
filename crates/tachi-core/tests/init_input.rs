use std::path::{Path, PathBuf};
use std::process::Command;

#[test]
fn init_input_unit_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root.join("tests/scripts/test_init_input_unit.py").exists(),
        "init-input unit coverage should live in Rust tests, not pytest"
    );

    for case in input_cases() {
        let script = build_bash_script(&root, &case);
        let output = Command::new("bash")
            .arg("-c")
            .arg(script)
            .env_clear()
            .env("LC_ALL", "C")
            .env("PATH", std::env::var("PATH").expect("PATH available"))
            .env("INPUT", case.input)
            .output()
            .expect("run init-input helper");

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let actual_rc = output.status.code().unwrap_or(-1);

        assert_eq!(
            actual_rc, case.expected_rc,
            "unexpected rc for {} ({}). stdout={stdout:?} stderr={stderr:?}",
            case.id, case.marker
        );

        if case.expected_rc == 0 {
            let expected_decl = format!(
                "declare -- result=\"{}\"",
                case.expected_result.expect("accepted case has result")
            );
            assert!(
                stdout.contains(&expected_decl),
                "PIPE-SUBSHELL REGRESSION SUSPECTED for {}. Expected caller-scope declaration {expected_decl:?}. stdout={stdout:?} stderr={stderr:?}",
                case.id
            );
        } else {
            let expected_reason = case
                .expected_reason
                .expect("rejected case has stderr reason");
            assert!(
                stderr.contains(expected_reason),
                "reason class {expected_reason:?} missing for {} ({}). stdout={stdout:?} stderr={stderr:?}",
                case.id,
                case.marker
            );
        }
    }
}

struct InputCase {
    id: &'static str,
    input: &'static str,
    expected_rc: i32,
    expected_result: Option<&'static str>,
    expected_reason: Option<&'static str>,
    marker: &'static str,
}

fn input_cases() -> Vec<InputCase> {
    vec![
        InputCase {
            id: "case_0_canary_positive",
            input: "MyValidProject",
            expected_rc: 0,
            expected_result: Some("MyValidProject"),
            expected_reason: None,
            marker: "positive caller-scope assignment canary",
        },
        InputCase {
            id: "case_9_control_char_bel",
            input: "foo\x07bar",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("control character"),
            marker: "BEL control character rejected after 3 strikes",
        },
        InputCase {
            id: "case_10_nul_byte",
            input: "foo\\x00bar",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("NUL byte"),
            marker: "NUL byte rejected after 3 strikes",
        },
        InputCase {
            id: "case_11_over_length",
            input: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("over-length"),
            marker: "101-character value rejected by 100-character cap",
        },
        InputCase {
            id: "case_12_control_char_soh",
            input: "foo\x01bar",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("control character"),
            marker: "SOH control character rejected after 3 strikes",
        },
        InputCase {
            id: "case_13_metachar_dollar",
            input: "my$project",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("metachar"),
            marker: "dollar sign rejected at prompt boundary",
        },
        InputCase {
            id: "case_14_metachar_backslash",
            input: "proj\\\\name",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("metachar"),
            marker: "backslash rejected at prompt boundary",
        },
        InputCase {
            id: "case_15_metachar_backtick",
            input: "proj`name`",
            expected_rc: 1,
            expected_result: None,
            expected_reason: Some("metachar"),
            marker: "backtick rejected at prompt boundary",
        },
    ]
}

fn build_bash_script(root: &Path, case: &InputCase) -> String {
    let helper = root.join(".aod/scripts/bash/init-input.sh");
    if case.expected_rc == 0 {
        format!(
            "set -euo pipefail; source '{}'; result=''; \
             aod_init_read_validated 'P: ' result 100 < <(printf '%b\\n' \"$INPUT\"); \
             declare -p result",
            helper.display()
        )
    } else {
        format!(
            "source '{}'; result=''; \
             aod_init_read_validated 'P: ' result 100 \
             < <(printf '%b\\n%b\\n%b\\n' \"$INPUT\" \"$INPUT\" \"$INPUT\")",
            helper.display()
        )
    }
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}
