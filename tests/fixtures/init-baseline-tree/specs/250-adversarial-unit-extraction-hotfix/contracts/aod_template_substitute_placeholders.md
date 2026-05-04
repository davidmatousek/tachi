# Contract: `aod_template_substitute_placeholders`

**Helper location**: `.aod/scripts/bash/template-substitute.sh`
**Authority**: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` (Accepted 2026-05-04)
**Test module**: `tests/scripts/test_template_substitute_unit.py` (new — FR-001)
**Untouched by this hot-fix**: yes — FR-005, FR-019, TC-4

This document captures the contract surface the new unit module exercises. It is descriptive, not authoring — the helper's behaviour is owned by ADR-038.

---

## Signature

```bash
aod_template_substitute_placeholders <src_path> <dest_path>
```

- `<src_path>`: path to a file containing zero or more `{{PLACEHOLDER}}` tokens
- `<dest_path>`: path the substituted output is written to (caller responsible for parent directory)

## Environment contract

Caller MUST set the following env vars before invocation; values become the substitutions:

```
AOD_PERSONALIZATION_PROJECT_NAME
AOD_PERSONALIZATION_PROJECT_DESCRIPTION
AOD_PERSONALIZATION_GITHUB_USER
AOD_PERSONALIZATION_GITHUB_REPO
AOD_PERSONALIZATION_AUTHOR_NAME
AOD_PERSONALIZATION_AUTHOR_EMAIL
AOD_PERSONALIZATION_LICENSE
AOD_PERSONALIZATION_RATIFICATION_DATE
AOD_PERSONALIZATION_TIMESTAMP
AOD_PERSONALIZATION_PROJECT_TYPE
AOD_PERSONALIZATION_VERSION
AOD_PERSONALIZATION_HOMEPAGE
```

Each `tachi` (etc.) token in the source is literally replaced with the value of `AOD_PERSONALIZATION_PROJECT_NAME` (etc.). Replacement is byte-literal — no regex interpretation, no escape processing.

## Behaviour under shim

The helper sources `shopt -u patsub_replacement 2>/dev/null || true` at the top of the function body (line 64 of the helper). This disables bash 5.2+'s `patsub_replacement` option, which would otherwise treat `&` in the replacement as a "match-text" backref. On bash 3.2 (macOS) the `shopt` is unknown and silently no-ops via `2>/dev/null || true`.

**Removing the shim** on a bash 5.x runtime causes:
- Case 1 (`AT&T`) to corrupt to `ATtachiT` (the F-248 closure)
- Case 3 (`\1\2`) to mishandle backref-style replacement
- Case 6 (multibyte `Ⅷ-Ⅸ`) to mishandle byte boundaries in the replacement
- Cases 2, 4, 5 to remain correct (they exercise pure parameter expansion independent of `patsub_replacement`)

This split is the load-bearing invariant tested by FR-010 / SC-006.

## Exit codes

- `0` — substitution complete, dest written
- non-zero — pre-existing helper failure modes (missing src, unwritable dest, etc.) not exercised by this hot-fix

## Test invocation pattern (FR-006, FR-008)

```python
result = subprocess.run(
    ["bash", "-c", (
        "shopt -u patsub_replacement 2>/dev/null||true; "
        "source .aod/scripts/bash/template-substitute.sh; "
        f"aod_template_substitute_placeholders '{src}' '{dest}'"
    )],
    env={
        "LC_ALL": "C",
        "PATH": os.environ["PATH"],
        "AOD_PERSONALIZATION_PROJECT_NAME": case["project_name"],
        # ... 11 other AOD_PERSONALIZATION_* vars set to non-empty stubs
    },
    capture_output=True,
    text=True,
    timeout=15,
    check=False,
)
assert result.returncode == 0, result.stderr
assert dest.read_text() == case["expected_dest"]
```

**No imports from `init_sh_helpers.py`**. **No `clone_into_tmpdir` use**. Function-scoped `tmp_path` only.
