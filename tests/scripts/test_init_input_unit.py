"""Unit-level tests for `aod_init_read_validated` (FR-002).

This module replaces 4 of the prompt-rejection adversarial cases that
historically lived in the soon-to-be-deleted `ADVERSARIAL_CASES` block of
`tests/scripts/test_init_sh_adversarial.py:41-162` (cases 9-12), plus a
positive-path canary that exercises the accept branch. By exercising the
helper directly (sub-second `bash -c source` per case) instead of forking
`init.sh` end-to-end (~30s per case on macos-latest cold cache), this
module eliminates the 300s subprocess timeout class on the macos-latest
CI leg (FR-016 / SC-002).

R-1 — pipe-subshell trap (HIGH severity, FR-006):
    The helper writes its validated value to caller scope via
    `printf -v "$var_name" '%s' "$validated"`. `printf -v` only mutates
    the caller's scope when the function runs in the parent shell. If the
    helper is invoked through a shell pipe (producer-stdout piped into
    helper-stdin), bash runs the rightmost pipeline element in a
    subshell. The `printf -v` assignment "succeeds" inside the subshell,
    but the subshell exits before any caller can observe the assignment
    — the caller sees `result=""` and exit code 0. THIS IS A SILENT
    FALSE PASS for any test asserting accept-path behaviour.

    The ONLY sanctioned invocation pattern in this module is process
    substitution: feed stdin via `< <(printf ...)`. Process substitution
    feeds the producer's stdout to the consumer's stdin without a pipe,
    keeping the consumer in the parent shell so `printf -v` writes to
    the caller's variable. ANY pipe-style invocation here is a
    critical-severity bug and a Wave 4 review failure.

FR-007 — module-load canary contract:
    The FIRST entry in `INPUT_CASES` MUST be `case_0_canary_positive`.
    Pytest collects parametrize entries in declaration order, so the
    canary runs first. If a future regression breaks the
    process-substitution invocation pattern (a developer accidentally
    re-pipes the input, or refactors the bash script to use a pipe), the
    canary fails fast with a stderr message that names "pipe-subshell"
    as the suspected diagnosis. This is the early-warning system that
    converts R-1 from a silent false pass into a detected regression.

R-4 — locale pinning rationale (FR-008):
    Every `subprocess.run(["bash", "-c", ...])` invocation pins
    `LC_ALL=C` in a freshly constructed `env=` mapping. The parent
    shell's locale is NOT inherited — locale-dependent control-character
    classifications (`[[:cntrl:]]` under different `LC_ALL` values) would
    otherwise cause the rejection ladder to behave differently between
    dev and CI. PATH is forwarded so `bash` itself remains resolvable.

FR-003 — zero-import constraint:
    This module deliberately does NOT import any integration-test
    helper. No clone-tree fixture, no end-to-end driver. The whole
    point of the FR-002 extraction is to eliminate the
    integration-helper dependency for these helper-scoped cases. The
    only imports below are stdlib (`os`, `subprocess`) and `pytest`.

NO filesystem touch:
    The helper's contract is purely env-in / stdout-out / stderr-out.
    There is no temporary directory or fixture file used anywhere in
    this module. The helper validates a string supplied via stdin
    (process substitution) and writes the result to a caller-scope
    bash variable observed via `declare -p`.

Reason-class authority:
    The exact stderr substring emitted by `aod_init_read_validated` for
    each rejection path is the contract source. The helper at
    `.aod/scripts/bash/init-input.sh` rejects on three conditions:
      1. NUL byte         → "NUL byte not allowed"
      2. Control character → "control character not allowed"
      3. Over-length       → "over-length (max N chars)"
    See contracts/aod_init_read_validated.md and the helper source for
    the authoritative substring list. Cases 9-12 below carry the
    historical inputs from `test_init_sh_adversarial.py:73-86`, which
    map deterministically to these three rejection classes.
"""

from __future__ import annotations

import os
import subprocess

import pytest


# Each entry: InputCase per data-model.md §Schema 2.
#   id                     — kebab-case label, used as pytest -k filter and failure ID
#   input                  — raw input fed via process substitution (single line for canary;
#                            same line repeated 3x for 3-strike rejection cases)
#   expected_rc            — 0 for accepted, 1 for rejected after 3 strikes
#   expected_result        — exact value expected in `result` shell variable on accept;
#                            None for reject
#   expected_reason_class  — substring expected on stderr for reject; None for accept
#   marker                 — short rationale used in failure messages and audit
#
# FR-007: case_0_canary_positive MUST be the first entry — pytest collects
# parametrize entries in declaration order, so this case runs first and
# fails fast on a pipe-subshell regression (R-1).
INPUT_CASES: list[dict] = [
    # FIRST entry — module-load canary (FR-007). Asserts that the
    # process-substitution invocation pattern correctly writes to caller
    # scope. A regression here is the canonical R-1 pipe-subshell trap.
    {
        "id": "case_0_canary_positive",
        "input": "MyValidProject",
        "expected_rc": 0,
        "expected_result": "MyValidProject",
        "expected_reason_class": None,
        "marker": "positive-path canary — guards against pipe-subshell regression (R-1)",
    },
    # case_9 — control character (0x07 BEL). Historical input from
    # test_init_sh_adversarial.py:76. Helper's [[:cntrl:]] ladder catches
    # this and rejects with "control character not allowed".
    {
        "id": "case_9_control_char_bel",
        "input": "foo\x07bar",
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "control character",
        "marker": "control-character rejection after 3 strikes (BEL 0x07)",
    },
    # case_10 — NUL byte. Historical input from the original adversarial
    # block. Helper's byte-by-byte read loop detects NUL via
    # empty-byte-after-success and rejects with "NUL byte not allowed".
    # The `input` field carries the literal backslash-escape sequence
    # `foo\x00bar` (9 chars: f, o, o, \, x, 0, 0, b, a, r). Python's
    # `subprocess.run` refuses env values containing real NUL bytes
    # (raises `ValueError: embedded null byte`), so we use the bash
    # `printf '%b'` decoder downstream to materialize the NUL inside
    # the bash subprocess where Python's env-validation can no longer
    # interfere.
    {
        "id": "case_10_nul_byte",
        "input": "foo\\x00bar",
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "NUL byte",
        "marker": "NUL-byte rejection after 3 strikes",
    },
    # case_11 — over-length (101 chars; cap is 100). Historical input
    # from test_init_sh_adversarial.py:82. Helper's length check rejects
    # with "over-length (max 100 chars)".
    {
        "id": "case_11_over_length",
        "input": "x" * 101,
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "over-length",
        "marker": "over-length rejection after 3 strikes (101 chars > 100 cap)",
    },
    # case_12 — control character (0x01 SOH). Historical input from
    # test_init_sh_adversarial.py:85. Distinct rejection-ladder class
    # from case_9 (different control byte) to confirm the [[:cntrl:]]
    # check covers the full 0x01-0x1F range, not just 0x07.
    {
        "id": "case_12_control_char_soh",
        "input": "foo\x01bar",
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "control character",
        "marker": "control-character rejection after 3 strikes (SOH 0x01)",
    },
    # F-2 BLP-02 Wave 2 amendment per B-2 Path R-2 (T026 + T032):
    # extend the rejection ladder to additionally reject `$`, `\`, backtick
    # at the prompt boundary. This complements the existing newline / NUL /
    # control / over-length rejections and forms the upstream defense for
    # the writer escape pass removal at template-substitute.sh:566-571
    # (T031). CHANGELOG migration guidance lands at T053.
    {
        "id": "case_13_metachar_dollar",
        "input": "my$project",
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "metachar",
        "marker": "F-2 amendment — reject `$` at prompt boundary",
    },
    {
        "id": "case_14_metachar_backslash",
        # Use a single backslash followed by name; bash printf %b will
        # interpret backslash escapes, so we deliberately use a raw
        # backslash that is NOT a recognized escape sequence. `\\n` would
        # become a newline; `\\m` is left as-is by `printf '%b'`. To pass
        # a literal backslash through, send `\\\\` (printf %b → `\\`).
        "input": "proj\\\\name",
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "metachar",
        "marker": "F-2 amendment — reject `\\` at prompt boundary",
    },
    {
        "id": "case_15_metachar_backtick",
        "input": "proj`name`",
        "expected_rc": 1,
        "expected_result": None,
        "expected_reason_class": "metachar",
        "marker": "F-2 amendment — reject backtick at prompt boundary",
    },
]


@pytest.mark.parametrize("case", INPUT_CASES, ids=lambda c: c["id"])
def test_init_input(case: dict) -> None:
    """Per-case unit assertion against `aod_init_read_validated`.

    Process-substitution invocation only — pipe-style invocation is forbidden
    (R-1). Each case feeds the configured input via `< <(printf ...)`,
    asserts the exit code matches expected_rc, and on accept asserts the
    `result` shell variable contains expected_result; on reject asserts
    expected_reason_class is a stderr substring.

    case_0_canary_positive is the first entry (FR-007). Its failure message
    explicitly names pipe-subshell as the suspected diagnosis so a future
    refactor that accidentally re-introduces a pipe is caught immediately.
    """
    if case["expected_rc"] == 0:
        # Positive case — single line via `printf '%b\n' "$INPUT"`.
        # `%b` (rather than `%s`) lets cases carry backslash-escape
        # sequences for byte values that Python `subprocess.run` cannot
        # express in `env=` mappings (NUL byte at minimum: Python raises
        # `ValueError: embedded null byte` if NUL appears in any env
        # value). For plain-text inputs without backslashes (the canary
        # and the over-length case), `%b` is identity. Process
        # substitution feeds stdin without a pipe, keeping the helper
        # in the parent shell so `printf -v` writes to caller scope.
        # `declare -p result` then prints the bash declaration of the
        # result variable to stdout for assertion below.
        bash_script = (
            "set -euo pipefail; "
            "source .aod/scripts/bash/init-input.sh; "
            "result=''; "
            "aod_init_read_validated 'P: ' result 100 < <(printf '%b\\n' \"$INPUT\"); "
            "declare -p result"
        )
    else:
        # 3-strike reject — feed the same input three times via
        # `printf '%b\n%b\n%b\n' "$INPUT" "$INPUT" "$INPUT"`. The helper
        # rejects each attempt with a reason class on stderr, then
        # `exit 1`s on the third strike. We do NOT use `set -e` here
        # because the helper's `exit 1` would short-circuit before any
        # downstream command; we capture rc via subprocess.run() return
        # and assert the reason class via stderr substring match. `%b`
        # rationale: see canary branch above (NUL bytes cannot be
        # passed through Python env).
        bash_script = (
            "source .aod/scripts/bash/init-input.sh; "
            "result=''; "
            "aod_init_read_validated 'P: ' result 100 "
            "< <(printf '%b\\n%b\\n%b\\n' \"$INPUT\" \"$INPUT\" \"$INPUT\")"
        )

    env = {
        "LC_ALL": "C",
        "PATH": os.environ["PATH"],
        "INPUT": case["input"],
    }

    result = subprocess.run(
        ["bash", "-c", bash_script],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == case["expected_rc"], (
        f"unexpected rc {result.returncode} for {case['id']} ({case['marker']}). "
        f"expected {case['expected_rc']}. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )

    if case["expected_rc"] == 0:
        # Canary check: `result` variable populated via `printf -v` in
        # parent shell. Process substitution keeps the helper in the
        # parent shell; a pipe would put it in a subshell and the
        # assignment would be invisible to the caller (silent false
        # pass). The failure message MUST name pipe-subshell so a
        # future regression is diagnosed immediately.
        expected_decl = f'declare -- result="{case["expected_result"]}"'
        assert expected_decl in result.stdout, (
            f"PIPE-SUBSHELL REGRESSION SUSPECTED for {case['id']}. "
            f"The helper's `printf -v` assignment did not propagate to "
            f"the caller scope. This indicates the process-substitution "
            f"invocation pattern is broken — check that the bash -c "
            f"script uses `< <(printf ...)` and not a pipe. "
            f"expected stdout to contain: {expected_decl!r}, "
            f"got stdout: {result.stdout!r}, stderr: {result.stderr!r}"
        )
    else:
        # Reject case: stderr names the rejection class. The helper's
        # contract source is `.aod/scripts/bash/init-input.sh` — see the
        # rejection ladder at the function body for authoritative
        # substrings ("NUL byte", "control character", "over-length").
        assert case["expected_reason_class"] in result.stderr, (
            f"reason class mismatch for {case['id']} ({case['marker']}). "
            f"expected {case['expected_reason_class']!r} in stderr, "
            f"got stderr: {result.stderr!r}, stdout: {result.stdout!r}"
        )
