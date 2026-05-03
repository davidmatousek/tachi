# Contract: `aod_init_read_validated` Input Validation Helper

**Helper file**: `.aod/scripts/bash/init-input.sh` (NEW; sibling to existing `template-*.sh` library files per Q-2 Option b adjudication)
**Function**: `aod_init_read_validated`
**Purpose**: Wrap each interactive `read -p` prompt in `init.sh:24-28` with prompt-time input validation that rejects newlines, NUL bytes, control characters (0x00–0x1F except space), and over-length input. Re-prompts up to 3 times; exits non-zero on the 3rd consecutive rejection.

This contract is consumed by `init.sh` post-F-1. F-2 (BLP-02 Wave 2) reuses the **validation triplet pattern** documented in ADR-038 (regex-validate → reject-on-mismatch → `printf -v` assignment), NOT this function (which is interactive `read -p`-only).

## Function Signature

```bash
aod_init_read_validated <prompt> <var_name> <max_len>
```

### Parameters

| Position | Name | Type | Required | Constraints |
|----------|------|------|----------|-------------|
| `$1` | `prompt` | string | YES | non-empty; written verbatim to stdout |
| `$2` | `var_name` | string | YES | valid bash identifier (`[A-Za-z_][A-Za-z0-9_]*`); names the bash variable in caller scope to populate on success |
| `$3` | `max_len` | integer | YES | positive integer; max accepted character length (per `${#answer}`) |

### Pre-conditions

- Caller is interactive bash 3.2+ (terminal attached to stdin).
- `$var_name` does not collide with internal helper variables (`prompt`, `var_name`, `max_len`, `answer`, `attempt`, `reason`).
- The function is sourced (not exec'd in subshell) so `printf -v` writes to caller scope.

## Behavior Contract

### Success path

1. Print `prompt` to stdout via `read -r -p "$prompt"`.
2. Read input into local `answer` (with `read -r` to disable backslash continuation).
3. Validate against the rejection ladder (in this order):
   - Embedded literal newline character: rejected with `[init] Input rejected: newline not allowed; please re-enter.`
   - NUL byte (0x00): rejected with `[init] Input rejected: NUL byte not allowed; please re-enter.`
   - Any 0x00–0x1F control character: rejected with `[init] Input rejected: control character not allowed; please re-enter.`
   - Length > `max_len`: rejected with `[init] Input rejected: over-length (max <max_len> chars); please re-enter.`
4. On all-passes (no rejection class fires): set the variable named by `$var_name` via `printf -v "$var_name" '%s' "$answer"` and return 0.

### Rejection path

1. Print rejection message to stderr: `[init] Input rejected: <class>; please re-enter.`
2. Increment internal `attempt` counter.
3. If `attempt < 3`: re-prompt (return to step 1 of success path).
4. If `attempt == 3`: print `[init] FATAL: 3 consecutive invalid inputs for $var_name; aborting.` to stderr; exit 1.

### Output streams

- **stdout**: prompt text only (`read -r -p` writes prompt to stdout/stderr per bash semantics — actual stream depends on interactive vs piped; treat as user-visible).
- **stderr**: rejection messages and FATAL message.
- **No log files** written; no global env vars set; no side effects beyond setting `$var_name`.

### Exit codes

| Exit code | Condition |
|-----------|-----------|
| 0 | Input accepted on attempt 1, 2, or 3; variable set successfully |
| 1 | 3 consecutive rejections; FATAL message printed; exits the calling script |

### Empty-input semantics

- Empty input (`answer=""`) is **accepted** (length 0 ≤ max_len; no character classes match). The caller is responsible for downstream validation of empty values where domain rules forbid them (e.g., the existing `init.sh` logic for `GITHUB_REPO` defaults empty input to `$PROJECT_NAME`).

## Bash Compatibility Contract

### bash 3.2 (macOS-default 3.2.57)

- **MUST work**: parameter expansion `${var}`, regex match `[[ ... =~ ... ]]`, POSIX character classes `[[:cntrl:]]`, length expansion `${#var}`, `printf -v`, `read -r -p`, `(( ... ))` arithmetic.
- **MUST NOT use**: associative arrays (`declare -A`), `mapfile`/`readarray`, lowercase parameter expansion (`${var,,}`), `&>` redirection.

### bash 4+ (Linux 5.x in CI)

- All bash 3.2 features available; no version-specific behavior used.

### `set -euo pipefail` interaction

- Compatible. Per Feature 132 lesson (devops/CI_CD_GUIDE.md:372): if the helper internally uses command substitution under `set -euo pipefail`, bracket with `set +e`/`set -e` if `local rc=$?` capture is needed (bash 3.2 errexit foot-gun). The current implementation does not use command substitution within the rejection-class check, so no bracketing is needed.

## Test Contract

The helper is exercised by these tests (cross-reference Regression Protection Plan):

| Test | Coverage |
|------|----------|
| `test_init_sh_adversarial.py` Case 9 | Multi-line paste rejection |
| `test_init_sh_adversarial.py` Case 10 | NUL paste rejection |
| `test_init_sh_adversarial.py` Case 11 | Over-length rejection |
| `test_init_sh_adversarial.py` Case 12 | Control character (0x07 BEL) rejection |
| `test_init_sh_adversarial.py` (3-strikes) | 3 consecutive rejections → exit 1 with FATAL |
| `test_init_sh_substitution.py` | Helper integrates cleanly with init.sh prompt flow |

## Reference Implementation Sketch

```bash
# .aod/scripts/bash/init-input.sh — F-1 BLP-02 Wave 1
# Copyright contract per AOD-Kit licensing.

aod_init_read_validated() {
    local prompt="$1"
    local var_name="$2"
    local max_len="$3"
    local answer
    local attempt=0
    local reason

    while (( attempt < 3 )); do
        # shellcheck disable=SC2162  # -r is set
        read -r -p "$prompt" answer

        reason=""
        if [[ "$answer" =~ $'\n' ]]; then
            reason="newline not allowed"
        elif [[ "$answer" =~ $'\0' ]]; then
            reason="NUL byte not allowed"
        elif [[ "$answer" =~ [[:cntrl:]] ]]; then
            reason="control character not allowed"
        elif (( ${#answer} > max_len )); then
            reason="over-length (max $max_len chars)"
        fi

        if [[ -z "$reason" ]]; then
            printf -v "$var_name" '%s' "$answer"
            return 0
        fi

        echo "[init] Input rejected: $reason; please re-enter." >&2
        ((attempt++))
    done

    echo "[init] FATAL: 3 consecutive invalid inputs for $var_name; aborting." >&2
    exit 1
}
```

(Final implementation may differ in shellcheck disable comments and edge-case handling per build review.)

## Stability Contract

- **Public surface**: function name, parameter order, parameter semantics, exit codes, output stream conventions. Changes to these require ADR.
- **Internal**: rejection-class names in error messages, `attempt` counter implementation, regex character class details — may change without ADR.
- **Reuse expectation**: F-2 Wave 2 reuses the *pattern* (regex-validate → reject-on-mismatch → `printf -v`) documented in ADR-038, NOT this function directly. New file-parse helpers (e.g., `aod_defaults_parse_validated` for `defaults.env`) will follow the same pattern but operate on file content rather than interactive prompts.
