# Contract: `aod_init_read_validated`

**Helper location**: `.aod/scripts/bash/init-input.sh`
**Authority**: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` §D-5 — Validation triplet pattern
**Test module**: `tests/scripts/test_init_input_unit.py` (new — FR-002)
**Untouched by this hot-fix**: yes — FR-005, FR-019, TC-4

This document captures the contract surface the new unit module exercises. It is descriptive, not authoring — the helper's behaviour is owned by ADR-038.

---

## Signature

```bash
aod_init_read_validated <prompt> <var_name> <max_len>
```

- `<prompt>`: the prompt string displayed before each read attempt (typically `"P: "`)
- `<var_name>`: the name of the caller-scope variable the validated value is written to (NOT a value — a name)
- `<max_len>`: maximum byte length accepted for the input

## Caller-scope write semantics — load-bearing constraint (R-1)

The helper writes the validated value to caller scope via:

```bash
printf -v "$var_name" '%s' "$validated"
```

`printf -v` mutates a variable in the caller's scope **only when the function runs in the parent shell**. If the function is invoked through a shell pipe like:

```bash
printf '%s\n' "$INPUT" | aod_init_read_validated 'P: ' result 100
```

then bash runs the rightmost pipeline element (`aod_init_read_validated ...`) in a subshell. The `printf -v "$var_name"` succeeds inside the subshell, but the subshell exits before any caller can observe the assignment — the caller sees `result=""` and exit code 0. **This is a silent false-pass for any test asserting accept-path behaviour.**

The **only sanctioned invocation pattern** in tests is process substitution:

```bash
aod_init_read_validated 'P: ' result 100 < <(printf '%s\n' "$INPUT")
```

Process substitution feeds the producer's stdout to the consumer's stdin **without a pipe**, keeping the consumer in the parent shell so `printf -v` works.

This is **R-1 (HIGH severity)** in the PRD risk register and FR-006 in the spec.

## Validation behaviour

- Reads one line of input
- Validates against an internal allow-list (regex check)
- On accept: `printf -v "$var_name" '%s' "$validated"`, exit 0
- On reject: print rejection reason to stderr, prompt again
- After 3 rejections: print final reason to stderr, exit 1

## Exit codes

- `0` — input accepted on attempt 1, 2, or 3; `<var_name>` populated in caller scope
- `1` — 3 strikes rejected; stderr contains a reason class identifier; `<var_name>` is empty

## Test invocation pattern (FR-006, FR-007, FR-008)

```python
# Positive-path canary — MUST be the first test collected
def test_canary_positive_path():
    result = subprocess.run(
        ["bash", "-c", (
            "set -euo pipefail; "
            "source .aod/scripts/bash/init-input.sh; "
            "result=''; "
            "aod_init_read_validated 'P: ' result 100 < <(printf '%s\\n' \"$INPUT\"); "
            "declare -p result"
        )],
        env={"LC_ALL": "C", "PATH": os.environ["PATH"], "INPUT": "MyValidProject"},
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert 'declare -- result="MyValidProject"' in result.stdout, (
        "Pipe-subshell regression suspected — process-substitution pattern broken. "
        f"stdout: {result.stdout!r}"
    )
```

For 3-strike rejection cases, the input is fed via:

```bash
< <(printf '%s\n%s\n%s\n' "$INPUT" "$INPUT" "$INPUT")
```

so the helper sees the same bad input three times, exits 1 on the third, and emits a named reason class on stderr.

**No imports from `init_sh_helpers.py`**. **No filesystem touch**. **No pipe invocation under any circumstance**.
