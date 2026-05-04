# Data Model: Adversarial Unit Extraction Hot-Fix

**Branch**: `250-adversarial-unit-extraction-hotfix`
**Date**: 2026-05-04
**Spec**: [spec.md](./spec.md) §Key Entities

This feature has no application data model. The "data" being designed is the **per-case parametrize table** that drives both new pytest modules. Below are the two table schemas.

---

## Schema 1: SubstituteCase (test_template_substitute_unit.py)

Each entry in the `SUBSTITUTE_CASES: list[dict]` table at the top of `test_template_substitute_unit.py` follows this shape:

```python
{
    "id": str,                              # short kebab-case label, used as pytest -k filter and failure ID
    "project_name": str,                    # value substituted into AOD_PERSONALIZATION_PROJECT_NAME
    "src_content": str,                     # exact bytes written to tmp_path/src (typically "tachi\n")
    "expected_dest": str,                   # exact bytes expected in tmp_path/dest after substitution
    "marker": str,                          # short rationale used in failure messages and test docstrings
}
```

### Validation rules

- `id` MUST be unique across all 8 cases and MUST match `^case_[0-9]+_[a-z0-9_]+$` so failure IDs are greppable.
- `project_name` MUST contain the metacharacter or value class the case is testing (no synthetic stand-ins).
- `src_content` MUST end with a newline (matches the F-248 baseline assumption that template files are LF-terminated).
- `expected_dest` MUST be the byte-literal post-substitution result; no f-strings, no concatenation. Reviewers eyeball this column to verify the test asserts what it claims.
- `marker` MUST name the regression class (e.g., "AT&T → ATtachiT corruption" for case 1).

### Case roster (cases 1-8)

| Case ID | project_name | Marker (regression class detected) |
|---------|--------------|------------------------------------|
| `case_1_ampersand` | `AT&T` | sed `&` backref expansion (the F-248 closure) |
| `case_2_pipe` | `foo\|bar` | sed `\|` alternation in s/// |
| `case_3_backref` | `\1\2` | sed `\1\2` capture-group backref |
| `case_4_single_quoted` | `'inside'` | shell quote-stripping pre-substitution |
| `case_5_double_quoted` | `"inside"` | shell expansion inside double-quotes |
| `case_6_multibyte` | `Ⅷ-Ⅸ` | bash 5.x `patsub_replacement` multibyte handling — load-bearing for shim |
| `case_7_newline_in_value` | `line1\nline2` | embedded LF byte handling |
| `case_8_empty_value` | `` (empty) | empty-value substitution edge |

### Load-bearing constraint (FR-010 / SC-006)

Cases 1, 3, and 6 MUST fail when the `shopt -u patsub_replacement 2>/dev/null || true` shim is removed from `.aod/scripts/bash/template-substitute.sh:64` on a bash 5.x runtime. Cases 2, 4, and 5 MUST pass under the same fault state.

This split is documented in the SubstituteCase table as an inline `# shim-sensitive: yes/no` comment on each row, so the deliberate-fault verification matrix can be derived mechanically.

---

## Schema 2: InputCase (test_init_input_unit.py)

Each entry in the `INPUT_CASES: list[dict]` table at the top of `test_init_input_unit.py` follows this shape:

```python
{
    "id": str,                              # short kebab-case label, used as pytest -k filter and failure ID
    "input": str,                           # raw input fed via process substitution (single line for positive cases; same line repeated 3x for 3-strike cases)
    "expected_rc": int,                     # 0 for accepted, 1 for rejected after 3 strikes
    "expected_result": str | None,          # exact value expected in `result` shell variable on accept; None for reject
    "expected_reason_class": str | None,    # substring expected on stderr for reject; None for accept
    "marker": str,                          # short rationale used in failure messages and test docstrings
}
```

### Validation rules

- `id` MUST be unique across all 5 cases (1 canary + 4 rejection) and MUST match `^case_[0-9]+_[a-z0-9_]+$`.
- The **canary case** (`case_0_canary_positive`) MUST be the first entry in the table — pytest collects in declaration order, so this guarantees it runs first and fails fast on a pipe-regression (R-1).
- `expected_rc` is `0` for the canary; `1` for cases 9-12.
- `expected_result` is the exact byte-literal expected on accept; `None` for reject (rejection paths produce empty `result`).
- `expected_reason_class` MUST match the stderr substring the helper emits for that rejection path — not a paraphrase. The contract source is `.aod/scripts/bash/init-input.sh`.
- `marker` MUST name the rejection class (e.g., "empty input", "multiline input", "disallowed character").

### Case roster (canary + cases 9-12)

| Case ID | Input | Expected | Marker |
|---------|-------|----------|--------|
| `case_0_canary_positive` | `MyValidProject` | rc=0, result="MyValidProject" | positive-path canary — guards against pipe-subshell regression (R-1) |
| `case_9_empty_input` | `` (3×) | rc=1, reason class "empty" | empty-string rejection after 3 strikes |
| `case_10_multiline_input` | `"line1\nline2"` (3×) | rc=1, reason class "multiline" or "newline" | embedded LF rejection after 3 strikes |
| `case_11_disallowed_char_class_a` | `bad/path` (3×) | rc=1, reason class "disallowed" or "invalid character" | disallowed-character class A rejection after 3 strikes |
| `case_12_disallowed_char_class_b` | `bad;cmd` (3×) | rc=1, reason class "disallowed" or "invalid character" | disallowed-character class B rejection after 3 strikes |

### Reason-class authority

The exact stderr string emitted by `aod_init_read_validated` for each rejection path is the contract source — the test asserts on a substring, not a regex. If the helper ever evolves to emit different stderr, the test fails fast and the contract document at `contracts/aod_init_read_validated.md` is the authoritative reference for the new substring.

---

## Cross-schema invariants

- Both schemas use a flat `list[dict]` (no nested classes, no dataclasses) — matches the existing `ADVERSARIAL_CASES` shape in the soon-to-be-deleted block of `test_init_sh_adversarial.py:48-87`. This keeps cognitive cost zero for reviewers familiar with the F-248 author intent.
- Neither schema imports any helper from `tests/scripts/init_sh_helpers.py` (FR-003).
- Both tables are module-level `list[dict]` constants; pytest parametrize uses `pytest.mark.parametrize("case", TABLE, ids=lambda c: c["id"])`.
- The `id` column is the single source of truth for grep / `pytest -k` / CI failure log identification — it MUST appear in the failure output verbatim.

---

## State transitions

Not applicable. Each case is a stateless input-output assertion against a pure helper invocation.

---

## Storage

Not applicable. No persistence beyond function-scoped `tmp_path` (substitute cases) or zero filesystem touch (input cases).
