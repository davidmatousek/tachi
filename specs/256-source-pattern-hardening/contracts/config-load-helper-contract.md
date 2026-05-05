# Contract: `aod_template_load_kv_file` (config-load helper)

**Feature**: 256
**Status**: Specification (FR-001)
**Date**: 2026-05-04
**Implementation file**: `.aod/scripts/bash/template-config-load.sh` (Stream 1 deliverable)
**ADR reference**: [ADR-040 Decision Items 1-7](../../../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md) (post-Stream-3 commit)

---

## Function Signature

```bash
aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]
```

| Position | Argument | Required | Type | Default |
|---|---|---|---|---|
| 1 | `<path>` | Yes | string (file path) | — |
| 2 | `<var_prefix>` | Yes | string (bash identifier prefix or empty) | — |
| 3 | `<allowed_keys_array_name>` | No | string (name of bash indexed array) | empty (no whitelist) |
| 4 | `<key_case>` | No | enum: `upper` or `lower` | `upper` |

---

## Pre-Conditions (Caller Responsibilities)

1. **`<path>` is non-empty** — caller MUST pass a non-empty string (file existence is checked by the function).
2. **`<var_prefix>` matches `^[A-Z_][A-Z_0-9]*$` or is empty** — caller MUST pass a valid bash-identifier prefix or empty string.
3. **`<allowed_keys_array_name>` (if provided) names an existing bash indexed array** — caller MUST have declared the array before calling. Verified via `${!var+set}` indirection.
4. **`<key_case>` is `upper` or `lower`** — caller MUST NOT pass `mixed`, `Mixed`, `UPPER`, or any other variant (per Q-2.5 ruling).
5. **Bash 3.2.57+ runtime** — caller MUST run under bash 3.2 or later.

---

## Behavior

### Step 1: Argument validation
- `<path>` empty → exit **1** + `[aod] ERROR: aod_template_load_kv_file requires <path>`.
- `<var_prefix>` invalid (non-empty AND fails identifier regex) → exit **1**.
- `<allowed_keys_array_name>` non-empty AND no such bash array exists → behavior undefined (caller pre-condition 3 violated).
- `<key_case>` invalid → exit **1** + `[aod] ERROR: invalid <key_case>: <value> (allowed: upper, lower)`.

### Step 2: File existence
- `! -f "$path"` → exit **3** + `[aod] ERROR: config file does not exist: <path>`.

### Step 3: Read once into buffer (TOCTOU mitigation)
- `local content; content=$(cat "$path")` — single read.
- If `cat` fails (read error, permission denied) → propagate non-zero exit.

### Step 4: Per-line iteration
- Iterate `$content` via `while IFS= read -r line` on here-string `<<< "$content"`.
- For each line:
  - **CRLF strip**: `line="${line%$'\r'}"`.
  - **Leading-whitespace strip** (per B-3 path-a): `line="${line#"${line%%[![:space:]]*}"}"`.
  - **Skip blank**: `[ -z "$line" ] && continue`.
  - **Skip comment**: `[ "${line:0:1}" = "#" ] && continue`.
  - **Validate against regex** (mode-dependent — see Step 5).
  - **Whitelist check** (if provided — see Step 6).
  - **Stage** `(KEY, VALUE)` pair internally — NOT yet assigned to caller scope.

### Step 5: Per-line regex validation

**Upper-case mode** (default, when `<key_case>=upper`):

```regex
^[A-Z_][A-Z_0-9]*=("[^"$\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]*)$
```

**Lower-case mode** (when `<key_case>=lower`):

```regex
^[a-z_][a-z_0-9]*=("[^"$\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]*)$
```

**Regex breakdown** (per spec FR-001 step 5):
- `^[A-Z_][A-Z_0-9]*` (upper) or `[a-z_][a-z_0-9]*` (lower): KEY — uppercase/lowercase + underscore + digit; must start with letter/underscore (no leading digit).
- `=`: literal.
- `"[^"$\\`]*"`: double-quoted value, no embedded `"`, `$`, `\`, or backtick — rejects command substitution `$(...)`, parameter expansion `${...}`, escape sequences, backtick command substitution.
- `|'[^']*'`: single-quoted value, anything except `'` (single-quotes inhibit interpolation in bash).
- `|[A-Za-z0-9._/:@+=-]*`: unquoted value, allowlisted character class only, **zero-or-more (per B-1)** — permits the bare `KEY=` form (empty unquoted value) which is required by the version-file contract.
- `$`: end of line.

**On regex failure**: exit **8** + `[aod] ERROR: malformed line $LINENO in $path: $TRUNCATED_CONTENT` (truncated to 80 chars).

### Step 6: Whitelist enforcement (if `<allowed_keys_array_name>` provided)

- For each parsed KEY:
  - Check membership in the named bash array.
  - **Not found** → exit **8** + `[aod] ERROR: disallowed key '$KEY' in $path (line $LINENO); allowed: $ALLOWED_LIST`.
- After parsing all lines:
  - For each REQUIRED key in the whitelist (= every member of the named array):
    - Verify it is present in the parsed set.
    - **Missing** → exit **8** + `[aod] ERROR: required key '$MISSING_KEY' missing from $path; expected: $ALLOWED_LIST`.

### Step 7: Defensive identifier check + `printf -v` assignment

For each staged `(KEY, VALUE)` pair:
- **Defensive identifier check** (per H-1): construct `target="${var_prefix}${KEY}"`. If `! [[ "$target" =~ ^[A-Za-z_][A-Za-z_0-9]*$ ]]` → exit **1** + `[aod] ERROR: constructed identifier '$target' is not a valid bash identifier`.
- **Strip surrounding quotes**: if `VALUE` starts AND ends with `"` (or `'`), strip both.
- **Assign**: `printf -v "$target" '%s' "$VALUE"`. The `printf -v` does NOT interpret `$VALUE` as bash; the value lands as a literal string.

### Exit codes (canonicalized)

| Code | Meaning | Source |
|---|---|---|
| `0` | Success — all keys assigned in caller scope | Step 7 complete |
| `1` | Argument error (invalid `<key_case>`, invalid `<var_prefix>`, missing `<path>`, defensive identifier failure) | Step 1 / Step 7 |
| `3` | File absent or unreadable | Step 2 / Step 3 |
| `8` | Validation failure (malformed line, disallowed key, missing whitelisted key) | Step 5 / Step 6 |

---

## Post-Conditions (Function Guarantees)

1. **No partial assignment**: if any line fails validation (Steps 5 or 6) or any constructed identifier fails the defensive check (Step 7), NO caller-scope variable is mutated.
2. **Single file read**: `cat "$path"` opens the file exactly once. The validate-then-assign pass operates on the in-memory buffer (TOCTOU mitigation per H-2).
3. **No bash interpretation of file content**: `printf -v` assigns the literal string. Command substitution `$(...)`, parameter expansion `${...}`, escape sequences, and backtick command substitution in file content are NEVER executed — the regex rejects them upfront in Step 5.
4. **Bash 3.2 compatibility**: no associative arrays, no `mapfile` / `readarray`, no `${var,,}` lowercase expansion. Verified primitives: `cat`, `printf -v`, `[[`, `=~`, parameter expansion `${var}`, indirect expansion `${!var}` (scalars only), here-string `<<<`, command substitution `$(...)`, while-read.
5. **Idempotency**: calling the function twice with the same arguments produces identical caller-scope state (assuming the file has not changed between calls).

---

## Internal `eval` Carve-Out (per ADR-040 Decision Item 7)

The function contains exactly ONE `eval` invocation, used for bash 3.2-compatible indirect array access:

```bash
eval "local keys=(\"\${${allowed_keys_array_name}[@]}\")"
```

**Audit-clarity rules** (DO NOT extend beyond this boundary):

1. The argument `${allowed_keys_array_name}` is a bash variable NAME, not user-supplied content.
2. The variable name MUST have been validated by Step 1 (caller pre-condition 3 verified via `${!var+set}` before this `eval` runs).
3. The expanded string is ONLY consumed by `local` — bash declares a local copy of the named array; no other operation parses or executes the result.
4. **No other `eval`** may be added to the function. The "no `eval` of file content" rule remains inviolable.
5. If a future bash 4+ migration drops the `eval`, replace with `local -n keys=...` (nameref) — recorded as future work in ADR-040.

---

## Test Surface (Test-1, ≥27 cases per FR-009)

| Case | Input shape | Expected exit | Verifies |
|---|---|---|---|
| 1-5 | Valid KV (no whitelist), various value shapes | 0 | Happy path |
| 6 | Valid KV (with whitelist), all keys present | 0 | Whitelist match |
| 7 | `KEY="$(rm -rf /)"` | 8 | Command substitution rejection |
| 8 | `KEY="unbalanced` (unbalanced quote) | 8 | Quote balance |
| 9 | `` KEY=`whoami` `` | 8 | Backtick rejection |
| 10 | `KEY="$VAR"` | 8 | Parameter expansion rejection |
| 11 | `key=value` (lowercase in upper-mode) | 8 | Mode enforcement |
| 12 | Whitelist provided; required key missing | 8 | Missing key |
| 13 | Whitelist provided; extra key present | 8 | Disallowed key |
| 14 | Line with only KEY and no `=` | 8 | Malformed line |
| 15 | Embedded literal newline in value | 8 | Newline rejection (regex implicit) |
| 16 | Embedded NUL in value | 8 | NUL rejection (regex implicit) |
| 17 | Bare `KEY=` (empty unquoted) | 0 | B-1 empty-value support |
| 18 | Invalid `<var_prefix>` (e.g., `1bad-prefix`) | 1 | H-1 defensive check |
| 19-23 | Trailing-newline / no-trailing-newline / CRLF / leading-whitespace / blank-line-followed-by-content | 0 | B-3 cases |
| 24 | Empty `<path>` | 1 | Argument error |
| 25 | Non-existent `<path>` | 3 | File-absent error |
| 26 | `<key_case>=lower` with lowercase keys | 0 | Lower-mode regex |
| 27 | `<key_case>=mixed` | 1 | Q-2.5 mode rejection |

---

## Cross-References

- Spec FR-001: [spec.md FR-001](../spec.md#functional-requirements)
- Plan Stream 1: [plan.md §Stream 1](../plan.md#stream-1--library-bring-up-critical-path-25-days-per-h-1)
- ADR-040 (dual-commit Proposed → Accepted): TBD post-Stream-3 commit at `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md`
- F-1 precedent: [.aod/scripts/bash/init-input.sh](../../../.aod/scripts/bash/init-input.sh) (`aod_init_read_validated`) — interactive analog
- F-1 ADR-038 (validation-triplet pattern): [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
