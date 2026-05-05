"""Unit-level tests for `aod_template_load_kv_file` (FR-001, F-2 BLP-02 Wave 2).

This module validates the canonical config-file load primitive in
`.aod/scripts/bash/template-config-load.sh` against the 27-case test surface
documented in `contracts/config-load-helper-contract.md` §Test Surface and in
spec.md FR-009 AC-9.2.

The function under test is:
    aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]

Behavior:
- Reads <path> once into a buffer (TOCTOU mitigation per H-2).
- Iterates lines via `while IFS= read -r line` on a here-string.
- Validates each line against a strict KV regex (mode-dependent).
- Optionally enforces a whitelist of allowed keys (per pre-pass + completeness
  check after parse).
- Defensive identifier check on `${var_prefix}${KEY}` per H-1.
- Assigns via `printf -v` (NOT eval) — caller-scope variables populated.

Exit codes (canonicalized):
    0 — success
    1 — argument error (empty path, invalid var_prefix, invalid <key_case>)
    3 — file absent
    8 — validation failure (malformed line, disallowed key, missing whitelist key)

R-1 — pipe-subshell trap (HIGH severity, F-1 lesson):
    `printf -v` only mutates caller scope when the function runs in the parent
    shell. A pipe puts the rightmost element in a subshell and the assignment
    is invisible to the caller — silent false pass. The ONLY sanctioned
    invocation pattern is the temp-file approach (write the fixture file via
    `tmp_path`, source the library, invoke the function, observe `declare -p`
    output) — no pipes anywhere.

FR-007 — module-load canary contract:
    The FIRST entry in `KV_CASES` MUST be `case_0_canary_positive`. Pytest
    collects parametrize entries in declaration order; the canary runs first
    and fails fast with a stderr message naming "pipe-subshell" if a future
    refactor breaks the temp-file invocation pattern.

R-4 — locale pinning rationale:
    Every `subprocess.run(["bash", "-c", ...])` invocation pins LC_ALL=C in a
    freshly constructed env= mapping. Locale-dependent regex behavior would
    otherwise cause the strict-KV regex to behave differently between dev and
    CI legs of the matrix.

Bash binary pin:
    The BASH env var defaults to `/bin/bash` (system bash 3.2.57 on macOS) so
    the matrix-canonical bash 3.2 path is exercised locally. Override via
    BASH=/path/to/bash in the test environment if a different bash is desired
    (Linux CI's bash 5.x exercises the same library through the same code
    path; identical regex semantics on both).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = REPO_ROOT / ".aod" / "scripts" / "bash" / "template-config-load.sh"
BASH_BIN = os.environ.get("BASH", "/bin/bash")


# Each case is invoked with a fixture file written to tmp_path. The fixture
# content is bytes (so embedded NUL / CR / LF can be expressed exactly), the
# var_prefix and optional whitelist + key_case match the function signature.
#
# expected_rc is the bash exit code; expected_assignments is a dict mapping
# bash-variable-name → expected-value-string. The test uses `declare -p` on
# each expected name to assert assignment after the function returns. None on
# expected_assignments means "do not assert any specific assignment" (rejection
# cases — the function returned non-zero and partial assignment is forbidden
# per the contract post-condition).
#
# expected_stderr_substr is an optional case-specific stderr substring used
# for diagnostic assertions on rejection paths.
#
# FR-007: case_0_canary_positive MUST be the first entry. A regression in the
# temp-file invocation pattern is named explicitly as the suspected diagnosis.
KV_CASES: list[dict] = [
    # -----------------------------------------------------------------
    # case_0 — module-load canary (FR-007). Asserts that the temp-file
    # invocation pattern correctly writes to caller scope. A regression
    # here is the canonical R-1 pipe-subshell trap.
    # -----------------------------------------------------------------
    {
        "id": "case_0_canary_positive",
        "fixture": b"KEY=value\n",
        "var_prefix": "STACK_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"STACK_KEY": "value"},
        "expected_stderr_substr": None,
        "marker": "positive-path canary — guards against pipe-subshell regression (R-1)",
    },
    # -----------------------------------------------------------------
    # Cases 1-5: valid KV (no whitelist) — five value shapes.
    # -----------------------------------------------------------------
    {
        "id": "case_1_unquoted_simple",
        "fixture": b"KEY=value\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": "value"},
        "expected_stderr_substr": None,
        "marker": "valid unquoted simple value",
    },
    {
        "id": "case_2_double_quoted",
        "fixture": b'KEY="quoted"\n',
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": "quoted"},
        "expected_stderr_substr": None,
        "marker": "valid double-quoted value",
    },
    {
        "id": "case_3_single_quoted",
        "fixture": b"KEY='single-quoted'\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": "single-quoted"},
        "expected_stderr_substr": None,
        "marker": "valid single-quoted value",
    },
    {
        "id": "case_4_unquoted_path",
        "fixture": b"KEY=path/with/slashes\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": "path/with/slashes"},
        "expected_stderr_substr": None,
        "marker": "valid unquoted path (slashes in allowlist class)",
    },
    {
        "id": "case_5_unquoted_email",
        "fixture": b"KEY=email@example.com\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": "email@example.com"},
        "expected_stderr_substr": None,
        "marker": "valid unquoted email (@ + . in allowlist class)",
    },
    # -----------------------------------------------------------------
    # Case 6: valid KV with whitelist — all keys present.
    # -----------------------------------------------------------------
    {
        "id": "case_6_whitelist_all_present",
        "fixture": (
            b'TECH_STACK="nextjs"\n'
            b'TECH_STACK_DATABASE="supabase"\n'
            b'TECH_STACK_VECTOR="pgvector"\n'
            b'TECH_STACK_AUTH="supabase"\n'
            b'CLOUD_PROVIDER="vercel"\n'
        ),
        "var_prefix": "STACK_",
        "allowed_keys": [
            "TECH_STACK",
            "TECH_STACK_DATABASE",
            "TECH_STACK_VECTOR",
            "TECH_STACK_AUTH",
            "CLOUD_PROVIDER",
        ],
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {
            "STACK_TECH_STACK": "nextjs",
            "STACK_TECH_STACK_DATABASE": "supabase",
            "STACK_TECH_STACK_VECTOR": "pgvector",
            "STACK_TECH_STACK_AUTH": "supabase",
            "STACK_CLOUD_PROVIDER": "vercel",
        },
        "expected_stderr_substr": None,
        "marker": "valid 5-key file with whitelist all present",
    },
    # -----------------------------------------------------------------
    # Cases 7-15: invalid lines.
    # -----------------------------------------------------------------
    {
        "id": "case_7_command_substitution",
        "fixture": b'KEY="$(rm -rf /)"\n',
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "command-substitution rejection ($(...) inside double-quotes)",
    },
    {
        "id": "case_8_unbalanced_quote",
        "fixture": b'KEY="unbalanced\n',
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "unbalanced double-quote rejection",
    },
    {
        "id": "case_9_backtick",
        "fixture": b"KEY=`whoami`\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "backtick command-substitution rejection",
    },
    {
        "id": "case_10_dollar_inside_double_quotes",
        "fixture": b'KEY="$VAR"\n',
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "parameter-expansion rejection ($ inside double-quotes)",
    },
    {
        "id": "case_11_lowercase_in_upper_mode",
        "fixture": b"key=value\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "lowercase KEY rejected in upper mode",
    },
    {
        "id": "case_12_missing_whitelisted_key",
        "fixture": (
            b'TECH_STACK="nextjs"\n'
            b'TECH_STACK_DATABASE="supabase"\n'
            b'TECH_STACK_VECTOR="pgvector"\n'
            b'TECH_STACK_AUTH="supabase"\n'
        ),  # CLOUD_PROVIDER deliberately omitted
        "var_prefix": "STACK_",
        "allowed_keys": [
            "TECH_STACK",
            "TECH_STACK_DATABASE",
            "TECH_STACK_VECTOR",
            "TECH_STACK_AUTH",
            "CLOUD_PROVIDER",
        ],
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "CLOUD_PROVIDER",
        "marker": "missing whitelisted key (CLOUD_PROVIDER) rejected",
    },
    {
        "id": "case_13_disallowed_key",
        "fixture": (
            b'TECH_STACK="nextjs"\n'
            b'TECH_STACK_DATABASE="supabase"\n'
            b'TECH_STACK_VECTOR="pgvector"\n'
            b'TECH_STACK_AUTH="supabase"\n'
            b'CLOUD_PROVIDER="vercel"\n'
            b'MALICIOUS_KEY="oops"\n'
        ),
        "var_prefix": "STACK_",
        "allowed_keys": [
            "TECH_STACK",
            "TECH_STACK_DATABASE",
            "TECH_STACK_VECTOR",
            "TECH_STACK_AUTH",
            "CLOUD_PROVIDER",
        ],
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "MALICIOUS_KEY",
        "marker": "disallowed extra key rejected",
    },
    {
        "id": "case_14_only_key_no_equals",
        "fixture": b"KEY\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "line with only KEY and no = rejected",
    },
    {
        "id": "case_15_embedded_nul",
        # Embedded NUL inside an otherwise valid line. Bash variables are
        # NUL-terminated, so `cat $path` would silently truncate the
        # content at the NUL — bypassing the regex's value-class
        # rejection promise (FR-005 AC-5.4). The library MUST run an
        # explicit NUL pre-check (Step 2b) before the cat-into-buffer
        # step. The pre-check rejects with exit 8 + "NUL byte" stderr
        # substring.
        "fixture": b"KEY=foo\x00bar\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "NUL byte",
        "marker": "embedded-NUL pre-check rejection (Step 2b)",
    },
    # -----------------------------------------------------------------
    # Case 16: bare KEY= empty unquoted (B-1) → PASS exit 0.
    # The unquoted-value class uses `*` quantifier (not `+`) so the bare
    # form passes. Required by version-file contract for non-tagged
    # commits where line 1 is literally `version=`.
    # -----------------------------------------------------------------
    {
        "id": "case_16_bare_empty_unquoted",
        "fixture": b"KEY=\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": ""},
        "expected_stderr_substr": None,
        "marker": "bare KEY= empty unquoted PASS (B-1)",
    },
    # -----------------------------------------------------------------
    # Case 17: defensive identifier check (H-1) — invalid <var_prefix>.
    # Step 1 rejects var_prefix values that don't match the bash
    # identifier regex; the function exits 1 (argument error) per the
    # contract Step 1 / pre-condition 2.
    # -----------------------------------------------------------------
    {
        "id": "case_17_invalid_var_prefix",
        "fixture": b"KEY=value\n",
        "var_prefix": "1bad-prefix",  # leading digit + dash — both invalid
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 1,
        "expected_assignments": None,
        "expected_stderr_substr": None,  # exit 1 message varies; rc check is sufficient
        "marker": "invalid var_prefix rejected exit 1 (H-1 defensive check)",
    },
    # -----------------------------------------------------------------
    # Case 18: empty-value PASS via double-quotes (B-1).
    # KEY="" — explicit empty double-quoted value. Should pass.
    # -----------------------------------------------------------------
    {
        "id": "case_18_empty_quoted_value",
        "fixture": b'KEY=""\n',
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_KEY": ""},
        "expected_stderr_substr": None,
        "marker": "empty double-quoted value PASS (B-1 reinforcement)",
    },
    # -----------------------------------------------------------------
    # Cases 19-23 (B-3): line-iteration edge cases.
    # -----------------------------------------------------------------
    {
        "id": "case_19_trailing_newline",
        # File ends WITH a trailing newline. The here-string mechanism
        # parses both lines correctly.
        "fixture": b"A=1\nB=2\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_A": "1", "T_B": "2"},
        "expected_stderr_substr": None,
        "marker": "trailing-newline file (B-3) parses both lines",
    },
    {
        "id": "case_20_no_trailing_newline",
        # File ends WITHOUT a trailing newline (printf 'A=1' > fixture).
        # The `<<< "$content"` here-string adds a trailing newline back so
        # while-read iterates the last line regardless.
        "fixture": b"A=1\nB=2",  # no \n at end
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_A": "1", "T_B": "2"},
        "expected_stderr_substr": None,
        "marker": "no-trailing-newline file (B-3) — last line still parsed",
    },
    {
        "id": "case_21_crlf",
        # CRLF line endings (Windows-edited config). Per-line CRLF strip
        # `line="${line%$'\r'}"` tolerates them.
        "fixture": b"A=1\r\nB=2\r\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_A": "1", "T_B": "2"},
        "expected_stderr_substr": None,
        "marker": "CRLF line endings (B-3) tolerated via per-line CR strip",
    },
    {
        "id": "case_22_leading_whitespace",
        # Leading whitespace on each line. Per B-3 path-a, the leading-
        # whitespace strip mirrors init.sh:217 behavior.
        "fixture": b"  A=1\n\tB=2\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_A": "1", "T_B": "2"},
        "expected_stderr_substr": None,
        "marker": "leading-whitespace (B-3) tolerated via path-a strip",
    },
    {
        "id": "case_23_blank_then_content",
        # Blank line followed by content. Blank lines are skipped; the
        # following content lines are validated normally.
        "fixture": b"\n\nA=1\n\n# comment\nB=2\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 0,
        "expected_assignments": {"T_A": "1", "T_B": "2"},
        "expected_stderr_substr": None,
        "marker": "blank-then-content + comment lines skipped (B-3)",
    },
    # -----------------------------------------------------------------
    # Case 24: missing-arg behavior — empty <path>.
    # -----------------------------------------------------------------
    {
        "id": "case_24_missing_path_arg",
        "fixture": None,  # special: do NOT write a fixture; pass empty path
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 1,
        "expected_assignments": None,
        "expected_stderr_substr": "<path>",
        "marker": "missing <path> argument exit 1",
    },
    # -----------------------------------------------------------------
    # Case 25: file-absent — non-existent <path>.
    # -----------------------------------------------------------------
    {
        "id": "case_25_file_absent",
        "fixture": "__USE_NONEXISTENT_PATH__",  # special sentinel
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 3,
        "expected_assignments": None,
        "expected_stderr_substr": "does not exist",
        "marker": "file-absent <path> exit 3",
    },
    # -----------------------------------------------------------------
    # Case 26: <key_case>=lower mode — accepts lowercase, rejects upper.
    # -----------------------------------------------------------------
    {
        "id": "case_26a_lower_mode_accepts_lowercase",
        "fixture": b"version=4.28.0\n",
        "var_prefix": "",
        "allowed_keys": None,
        "key_case": "lower",
        "expected_rc": 0,
        "expected_assignments": {"version": "4.28.0"},
        "expected_stderr_substr": None,
        "marker": "<key_case>=lower accepts lowercase keys",
    },
    {
        "id": "case_26b_lower_mode_rejects_uppercase",
        "fixture": b"VERSION=4.28.0\n",
        "var_prefix": "",
        "allowed_keys": None,
        "key_case": "lower",
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "malformed line",
        "marker": "<key_case>=lower rejects uppercase keys exit 8",
    },
    # -----------------------------------------------------------------
    # Case 27: <key_case>=mixed → exit 1 (Q-2.5 ruling — only upper/lower).
    # -----------------------------------------------------------------
    {
        "id": "case_27_mixed_mode_rejected",
        "fixture": b"KEY=value\n",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": "mixed",
        "expected_rc": 1,
        "expected_assignments": None,
        "expected_stderr_substr": "key_case",
        "marker": "<key_case>=mixed rejected exit 1 (Q-2.5)",
    },
    # -----------------------------------------------------------------
    # Case 28: file-size cap — fixture exceeds AOD_KV_MAX_BYTES default
    # 65536. DoS hardening: caps the Step 3 cat buffer to a reasonable
    # ceiling for the typical knip.jsonc / personalization.env workloads.
    # 9000 lines of "K####=v\n" (~72 KB) trips the default cap.
    # -----------------------------------------------------------------
    {
        "id": "case_28_size_cap_returns_8",
        "fixture": b"".join(
            f"K{i:04d}=v\n".encode() for i in range(9000)
        ),
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 8,
        "expected_assignments": None,
        "expected_stderr_substr": "AOD_KV_MAX_BYTES",
        "marker": "fixture > AOD_KV_MAX_BYTES default 65536 → exit 8",
    },
    # -----------------------------------------------------------------
    # Case 29: directory at <path> — the tmp_path itself is passed (it's
    # a directory, not a regular file). [ ! -f ] catches it and emits a
    # distinct "not a regular file" diagnostic separate from "does not
    # exist" so the caller can distinguish the two failure modes.
    # -----------------------------------------------------------------
    {
        "id": "case_29_directory_path_returns_3",
        "fixture": "__USE_DIRECTORY_PATH__",
        "var_prefix": "T_",
        "allowed_keys": None,
        "key_case": None,
        "expected_rc": 3,
        "expected_assignments": None,
        "expected_stderr_substr": "not a regular file",
        "marker": "directory <path> → exit 3 with regular-file diagnostic",
    },
]


def _build_bash_script(
    fixture_path: str,
    var_prefix: str,
    allowed_keys: list[str] | None,
    key_case: str | None,
    expected_assignments: dict[str, str] | None,
) -> str:
    """Build the bash -c script for a single case.

    The script:
      1. Sources `.aod/scripts/bash/template-config-load.sh`.
      2. Optionally declares the whitelist array.
      3. Invokes `aod_template_load_kv_file` with the case args.
      4. Captures the exit code into RC.
      5. Emits `RC=<code>` on stdout for assertion.
      6. Emits `declare -p` of each expected variable on stdout (positive cases)
         so the test can inspect the actual caller-scope values.

    No pipes anywhere — the function runs in the parent shell so `printf -v`
    writes to caller scope visibly.
    """
    parts: list[str] = []
    parts.append("set +e")  # we want to capture rc, not let set -e short-circuit
    parts.append(f"source {LIB_PATH}")

    if allowed_keys is not None:
        keys_literal = " ".join(f'"{k}"' for k in allowed_keys)
        parts.append(f"ALLOWED=({keys_literal})")
        whitelist_arg = " ALLOWED"
    else:
        whitelist_arg = ""

    if key_case is not None:
        # When key_case is provided but no whitelist, an empty 3rd arg is
        # required so the 4th positional aligns. Quote both args explicitly.
        if allowed_keys is None:
            invocation = (
                f'aod_template_load_kv_file "{fixture_path}" "{var_prefix}" '
                f'"" "{key_case}"'
            )
        else:
            invocation = (
                f'aod_template_load_kv_file "{fixture_path}" "{var_prefix}" '
                f'ALLOWED "{key_case}"'
            )
    else:
        # No 4th arg supplied — default key_case=upper.
        if allowed_keys is None:
            invocation = (
                f'aod_template_load_kv_file "{fixture_path}" "{var_prefix}"'
            )
        else:
            invocation = (
                f'aod_template_load_kv_file "{fixture_path}" "{var_prefix}" '
                f'ALLOWED'
            )

    parts.append(invocation)
    parts.append("RC=$?")
    parts.append("echo RC=$RC")

    # Emit declare -p for each expected assignment so the test sees actual
    # caller-scope state. On rejection paths (expected_assignments is None) we
    # still emit declare -p for any STACK_/T_/etc. variables a buggy
    # implementation might have set, so a partial-assignment regression is
    # caught (post-condition: no partial assignment on failure).
    if expected_assignments:
        for var_name in expected_assignments:
            # `declare -p` errors if the variable is unset; route stderr to
            # /dev/null so the test only sees the success-path declarations.
            parts.append(f"declare -p {var_name} 2>/dev/null || echo UNSET={var_name}")

    return "; ".join(parts)


def _write_fixture(tmp_path: Path, content: bytes) -> str:
    """Write a fixture file to tmp_path and return its absolute path."""
    fixture_file = tmp_path / "fixture.env"
    fixture_file.write_bytes(content)
    return str(fixture_file)


@pytest.mark.parametrize("case", KV_CASES, ids=lambda c: c["id"])
def test_template_config_load(case: dict, tmp_path: Path) -> None:
    """Per-case unit assertion against `aod_template_load_kv_file`.

    Temp-file invocation only — no pipes (R-1). Each case writes the fixture
    to tmp_path, sources the library, invokes the function, captures the exit
    code via $? echo, asserts the rc matches expected_rc, and on positive
    cases asserts the caller-scope variables have the expected values via
    `declare -p`.

    case_0_canary_positive runs first per FR-007. Its failure message names
    "pipe-subshell" or "library-not-loaded" as suspected diagnoses so a
    future regression is detected immediately.
    """
    # Resolve fixture path. Three special modes:
    #   - case["fixture"] is None      → pass empty path argument (case 24)
    #   - case["fixture"] is "__USE_NONEXISTENT_PATH__" → pass non-existent path (case 25)
    #   - case["fixture"] is bytes     → write a real file with the given bytes
    if case["fixture"] is None:
        fixture_path = ""
    elif case["fixture"] == "__USE_NONEXISTENT_PATH__":
        fixture_path = str(tmp_path / "does_not_exist.env")
    elif case["fixture"] == "__USE_DIRECTORY_PATH__":
        fixture_path = str(tmp_path)
    else:
        fixture_path = _write_fixture(tmp_path, case["fixture"])

    bash_script = _build_bash_script(
        fixture_path,
        case["var_prefix"],
        case["allowed_keys"],
        case["key_case"],
        case["expected_assignments"],
    )

    env = {
        "LC_ALL": "C",
        "PATH": os.environ["PATH"],
    }

    # Invoke against the canonical /bin/bash 3.2.57 path on macOS by default.
    # The BASH env var override allows CI matrix to point at /usr/bin/bash on
    # Linux without modifying the test code.
    result = subprocess.run(
        [BASH_BIN, "-c", bash_script],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    # Parse out the RC=<n> line emitted by the script. The function-under-test
    # exit code is what we assert; the bash -c overall returncode would
    # otherwise reflect the LAST command (the declare -p emission).
    rc_line = next(
        (line for line in result.stdout.splitlines() if line.startswith("RC=")),
        None,
    )

    assert rc_line is not None, (
        f"PIPE-SUBSHELL OR LIBRARY-NOT-LOADED REGRESSION SUSPECTED for {case['id']}. "
        f"The bash script did not emit any RC=<n> line, indicating either the "
        f"library failed to source, the function crashed before $?-capture, "
        f"or the temp-file invocation pattern is broken. Check that "
        f"{LIB_PATH} exists and that the bash script does not pipe output. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )

    actual_rc = int(rc_line.split("=", 1)[1])

    assert actual_rc == case["expected_rc"], (
        f"unexpected rc {actual_rc} for {case['id']} ({case['marker']}). "
        f"expected {case['expected_rc']}. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )

    # On expected-stderr-substring cases, assert the substring appears.
    if case.get("expected_stderr_substr"):
        assert case["expected_stderr_substr"] in result.stderr, (
            f"stderr substring {case['expected_stderr_substr']!r} not found "
            f"for {case['id']} ({case['marker']}). "
            f"stderr: {result.stderr!r}"
        )

    # On positive cases (rc=0), assert each expected caller-scope assignment
    # is present in the declare -p output. This is the canonical canary check
    # — a pipe-subshell regression would set the variable in the subshell but
    # the parent shell's declare -p would print UNSET=<name> instead.
    if case["expected_rc"] == 0 and case["expected_assignments"]:
        for var_name, expected_value in case["expected_assignments"].items():
            expected_decl = f'declare -- {var_name}="{expected_value}"'
            unset_marker = f"UNSET={var_name}"
            if unset_marker in result.stdout:
                pytest.fail(
                    f"PIPE-SUBSHELL REGRESSION SUSPECTED for {case['id']}. "
                    f"Variable {var_name} was UNSET after the function returned, "
                    f"indicating `printf -v` did not propagate to caller scope. "
                    f"This is the canonical R-1 trap — check that the bash "
                    f"script does not use a pipe and that the library file "
                    f"correctly uses `printf -v` (NOT eval) for assignment. "
                    f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
                )
            assert expected_decl in result.stdout, (
                f"caller-scope assignment mismatch for {case['id']} "
                f"({case['marker']}). expected stdout to contain "
                f"{expected_decl!r}, got stdout: {result.stdout!r}, "
                f"stderr: {result.stderr!r}"
            )

    # On rejection paths (rc != 0) where the case explicitly listed expected
    # assignments as None, assert NO partial assignment was applied. The
    # contract post-condition 1 forbids partial assignment on failure. We
    # emit declare -p for known-prefix variables in `_build_bash_script`
    # only on positive cases — for rejection paths the caller-scope state is
    # implicit (no UNSET= markers expected because we did not declare -p).
    # This is the contract check; a stronger version would scan all variables
    # under the prefix, but that is bash 3.2-incompatible without `compgen`.
    # The Test-2 integration suite (T020/T028 et al.) provides the Site-A/B
    # cross-cutting partial-assignment checks.
