#!/usr/bin/env bash
# =============================================================================
# template-config-load.sh — canonical KV-file load primitive
# =============================================================================
# F-2 BLP-02 Wave 2 (Source-Pattern Hardening)
# ADR: docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md
# Contract: contracts/config-load-helper-contract.md
# Bash 3.2 compatible (verified against /bin/bash on macOS 14+).
# Audit-clarity: contains ONE internal eval carve-out for bash 3.2 indirect
# array access (Step 6 keys array). All caller-side eval has been removed
# across F-2.
#
# Public function:
#   aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] \
#                              [<key_case>]
#
# Behavior (per contracts/config-load-helper-contract.md §Behavior):
#   Step 1 — argument validation (path / var_prefix regex / key_case enum)
#   Step 2 — file existence check (return 3 with error)
#   Step 3 — single `cat $path` into in-memory buffer (TOCTOU mitigation, H-2)
#   Step 4 — per-line iteration via `while IFS= read -r line` on here-string
#            with CRLF strip + leading-whitespace strip + blank/comment skip
#   Step 5 — per-line regex validation (mode-dependent; B-1 zero-or-more value)
#   Step 6 — whitelist enforcement (in-pass for unknown-key + post-pass for
#            missing-key completeness)
#   Step 7 — defensive identifier check (H-1) + `printf -v` assignment (NOT
#            eval; quote stripping for surrounding quotes)
#
# Exit codes:
#   0 — success; all keys assigned in caller scope
#   1 — argument error (Step 1 / Step 7 defensive identifier failure)
#   3 — file absent or unreadable (Step 2)
#   8 — validation failure (malformed line / disallowed key / missing key)
#
# Bash 3.2 constraints (NFR-001):
#   - NO associative arrays (declare -A)
#   - NO mapfile / readarray
#   - NO ${var,,} / ${var^^} lowercase/uppercase parameter expansion
#   - Scalar ${!var} only (eval carve-out for indirect array access)
#   - printf -v is bash 3.1+ compatible
#   - <<< "$content" here-string is bash 3.2 compatible
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_TEMPLATE_CONFIG_LOAD_SH_SOURCED:-}" ]; then
    return 0
fi
readonly AOD_TEMPLATE_CONFIG_LOAD_SH_SOURCED=1


# -----------------------------------------------------------------------------
# aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] \
#                            [<key_case>]
# -----------------------------------------------------------------------------
# Load a KV-format config file safely — read once into a buffer, validate each
# line against a strict regex, optionally enforce a whitelist of allowed keys,
# then assign caller-scope variables via `printf -v` (NEVER `eval` of file
# content).
#
# Arguments:
#   $1 — path           — file path (non-empty; existence checked at Step 2)
#   $2 — var_prefix     — bash-identifier prefix or empty ("" allowed for B-1
#                          version-file site at template-git.sh)
#   $3 — allowed_keys_array_name — name of a bash indexed array (optional;
#                          when provided, BOTH unknown-key rejection AND
#                          missing-required-key detection apply)
#   $4 — key_case       — "upper" (default) or "lower" — anything else exits 1
#
# Pre-conditions (caller responsibilities):
#   - var_prefix matches ^[A-Z_][A-Z_0-9]*$ OR is empty
#   - allowed_keys_array_name (if provided) names an existing bash array
#   - key_case is "upper" or "lower" — never "mixed", "Mixed", etc.
#   - bash 3.2.57+ runtime
#
# Post-conditions (function guarantees):
#   - No partial assignment on validation failure (atomic two-pass)
#   - Single file read via cat (TOCTOU mitigation, H-2)
#   - No bash interpretation of file content (printf -v is literal)
#   - Idempotent on repeat calls with identical args + unchanged file
# -----------------------------------------------------------------------------
aod_template_load_kv_file() {
    # ---- Step 1: argument validation -----------------------------------
    local path="${1:-}"
    local var_prefix="${2-}"
    local allowed_keys_array_name="${3:-}"
    local key_case="${4:-upper}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: aod_template_load_kv_file requires <path> argument" >&2
        return 1
    fi

    # var_prefix must match ^[A-Za-z_][A-Za-z_0-9]*$ OR be empty. The regex
    # tolerates both upper and lower (Site B uses empty string; Sites A + D
    # use prefixes "STACK_" and "AOD_PERSONALIZATION_"). Per H-1 we run the
    # defensive check both here AND at Step 7 — the Step 1 form catches an
    # invalid prefix before any file I/O; Step 7 catches the impossible-but-
    # possible case where file content combined with a valid prefix produces
    # an invalid identifier (e.g., var_prefix="" with KEY="0BAD" — never
    # matches the KV regex but defense in depth is cheap).
    if [ -n "$var_prefix" ] && ! [[ "$var_prefix" =~ ^[A-Za-z_][A-Za-z_0-9]*$ ]]; then
        echo "[aod] ERROR: invalid <var_prefix>: '$var_prefix' (must match [A-Za-z_][A-Za-z_0-9]*)" >&2
        return 1
    fi

    # key_case must be "upper" or "lower". Anything else (including "mixed",
    # empty string when 4th arg is supplied as "", etc.) is exit 1 per Q-2.5.
    if [ "$key_case" != "upper" ] && [ "$key_case" != "lower" ]; then
        echo "[aod] ERROR: invalid <key_case>: '$key_case' (allowed: upper, lower)" >&2
        return 1
    fi

    # ---- Step 2: file existence -----------------------------------------
    if [ ! -f "$path" ]; then
        echo "[aod] ERROR: config file does not exist: $path" >&2
        return 3
    fi

    # ---- Step 2b: NUL-byte pre-check ------------------------------------
    # Bash variables are NUL-terminated; command substitution silently
    # truncates content at the first NUL byte. Without this pre-check, an
    # adversarial fixture like `KEY=foo<NUL>bar\n` would be loaded as
    # `KEY=foobar\n` (one valid KV line) — bypassing the NUL-rejection
    # promise in FR-005 AC-5.4. We compare the file's raw byte count
    # against its NUL-stripped byte count via `tr -d '\000'`. Any
    # difference signals one or more NUL bytes are present. This idiom
    # is bash 3.2 + BSD coreutils compatible (no `grep -q $'\x00'` which
    # silently matches everywhere because bash collapses an embedded
    # NUL in argv to an empty string).
    local _raw_size _nonnul_size
    _raw_size=$(LC_ALL=C wc -c < "$path" | tr -d ' ')
    _nonnul_size=$(LC_ALL=C tr -d '\000' < "$path" | wc -c | tr -d ' ')
    if [ "$_raw_size" != "$_nonnul_size" ]; then
        echo "[aod] ERROR: file contains NUL byte (rejected): $path" >&2
        return 8
    fi

    # ---- Step 3: read once into buffer (TOCTOU mitigation, H-2) ---------
    # Single cat — open the file exactly once. The validate-then-assign pass
    # operates on $content, not on $path. This collapses the TOCTOU race
    # window from "between two operations" to "before cat opens" (per ADR-040
    # §Decision Item 5). The race window is bounded but non-zero; defense in
    # depth via 0600 mode on .aod/personalization.env applies upstream.
    local content
    content="$(cat "$path")" || {
        local cat_rc=$?
        echo "[aod] ERROR: failed to read config file: $path (cat exit $cat_rc)" >&2
        return 3
    }

    # ---- Step 6 prep: load the whitelist into a local array -------------
    # Internal eval carve-out (audit-clarity per ADR-040 Decision Item 7):
    # bash 3.2 has no nameref (`local -n`) and no array indirect expansion
    # `${!array[@]}` for arrays. The single supported pattern for
    # caller-array-by-name access in bash 3.2 is `eval` against a validated
    # array NAME (not user-supplied content). The argument
    # ${allowed_keys_array_name} is a bash variable name passed by an
    # in-repo caller (init.sh, template-substitute.sh). It is NEVER
    # user-controlled — it arrives only from the post-F-2 in-repo call sites.
    #
    # No other `eval` may be added to this function. The "no eval of file
    # content" rule remains inviolable. If a future bash 4+ migration drops
    # the `eval`, replace with `local -n keys=...` (nameref).
    local _has_whitelist=0
    local _whitelist_keys=()
    if [ -n "$allowed_keys_array_name" ]; then
        # Defensive check on the array NAME itself — must be a valid bash
        # identifier. This protects against a buggy caller passing an
        # injection payload as the 3rd argument (defense in depth even
        # though all in-repo callers pass literal names).
        if ! [[ "$allowed_keys_array_name" =~ ^[A-Za-z_][A-Za-z_0-9]*$ ]]; then
            echo "[aod] ERROR: invalid <allowed_keys_array_name>: '$allowed_keys_array_name'" >&2
            return 1
        fi
        # Single eval — load named array into _whitelist_keys local copy.
        # The expanded string is consumed ONLY by `local`; no other operation
        # parses or executes the result.
        eval "_whitelist_keys=(\"\${${allowed_keys_array_name}[@]}\")"
        _has_whitelist=1
    fi

    # ---- Step 4 + 5 + 6: parse, validate, and stage (key, value) pairs --
    # Bash 3.2 has no associative arrays, so we stage parsed pairs in two
    # parallel indexed arrays (_parsed_keys[i], _parsed_values[i]). After the
    # full pass we then run Step 7 (defensive identifier check + printf -v
    # assignment) on each staged pair. This guarantees no partial assignment
    # on failure (post-condition 1 of the contract).
    local _parsed_keys=()
    local _parsed_values=()
    local _seen_keys=()
    local lineno=0
    local line
    local key
    local value
    local truncated

    # Build the regex once. The unquoted-value class uses `*` (NOT `+`) per
    # B-1 to permit bare KEY= empty values (required by version-file
    # contract). The double-quoted alternative explicitly excludes `"`, `$`,
    # `\`, and backtick to reject command substitution / parameter expansion
    # / escape sequences / backtick command substitution. The single-quoted
    # alternative permits anything except `'` (single-quotes inhibit bash
    # interpolation by definition).
    local kv_regex
    if [ "$key_case" = "lower" ]; then
        kv_regex='^[a-z_][a-z_0-9]*=("[^"$\\`]*"|'\''[^'\'']*'\''|[A-Za-z0-9._/:@+=-]*)$'
    else
        kv_regex='^[A-Z_][A-Z_0-9]*=("[^"$\\`]*"|'\''[^'\'']*'\''|[A-Za-z0-9._/:@+=-]*)$'
    fi

    # Iterate lines via while-read on the here-string. Bash 3.2 here-string
    # is fully supported. `IFS=` keeps internal whitespace in the line; the
    # `read -r` flag prevents backslash interpretation.
    while IFS= read -r line; do
        lineno=$((lineno + 1))

        # Strip trailing CR for CRLF tolerance (Windows-edited config).
        line="${line%$'\r'}"

        # Strip leading whitespace (path-a per B-3, mirrors init.sh:217).
        # Bash 3.2 compatible parameter-expansion idiom: peel off any prefix
        # up to (but not including) the first non-whitespace character.
        line="${line#"${line%%[![:space:]]*}"}"

        # Skip blank lines (post-strip).
        if [ -z "$line" ]; then
            continue
        fi

        # Skip comment lines (lines starting with #).
        if [ "${line:0:1}" = "#" ]; then
            continue
        fi

        # Per-line regex validation.
        if ! [[ "$line" =~ $kv_regex ]]; then
            # Truncate to 80 chars for the error message. Bash 3.2 substring
            # parameter expansion is supported.
            truncated="${line:0:80}"
            echo "[aod] ERROR: malformed line $lineno in $path: $truncated" >&2
            return 8
        fi

        # Extract key and value. The key is everything before the first =.
        key="${line%%=*}"
        # The value is everything after the first =.
        value="${line#*=}"

        # Strip surrounding quotes (single OR double, but not mixed). The
        # regex already verified that quoted values are balanced, so we can
        # simply peel off matching outer quotes.
        if [ "${value:0:1}" = '"' ] && [ "${value: -1}" = '"' ]; then
            value="${value:1:${#value}-2}"
        elif [ "${value:0:1}" = "'" ] && [ "${value: -1}" = "'" ]; then
            value="${value:1:${#value}-2}"
        fi

        # In-pass whitelist check (unknown-key rejection). Bash 3.2 does
        # array membership via for-loop linear scan (no `[[ in array ]]`).
        if [ "$_has_whitelist" = "1" ]; then
            local _k _found=0
            for _k in "${_whitelist_keys[@]}"; do
                if [ "$_k" = "$key" ]; then
                    _found=1
                    break
                fi
            done
            if [ "$_found" = "0" ]; then
                echo "[aod] ERROR: disallowed key '$key' in $path (line $lineno); allowed: ${_whitelist_keys[*]}" >&2
                return 8
            fi
        fi

        # Stage the (key, value) pair. We append to parallel indexed arrays;
        # the order of staged pairs matches the order of valid lines in the
        # file. Step 7 (next pass) consumes _parsed_keys + _parsed_values.
        _parsed_keys[${#_parsed_keys[@]}]="$key"
        _parsed_values[${#_parsed_values[@]}]="$value"
        _seen_keys[${#_seen_keys[@]}]="$key"
    done <<< "$content"

    # ---- Step 6 post-pass: missing-key completeness check ---------------
    if [ "$_has_whitelist" = "1" ]; then
        local _required _seen _present
        for _required in "${_whitelist_keys[@]}"; do
            _present=0
            for _seen in "${_seen_keys[@]}"; do
                if [ "$_seen" = "$_required" ]; then
                    _present=1
                    break
                fi
            done
            if [ "$_present" = "0" ]; then
                echo "[aod] ERROR: required key '$_required' missing from $path; expected: ${_whitelist_keys[*]}" >&2
                return 8
            fi
        done
    fi

    # ---- Step 7: defensive identifier check + printf -v assignment ------
    # Iterate the staged pairs. Per H-1, verify the constructed identifier
    # ${var_prefix}${KEY} is a valid bash identifier BEFORE the printf -v.
    # printf -v with an invalid target name fails with exit 2 and prints
    # to stderr — but the defensive check is preferred for clarity (the
    # contract guarantees exit 1 for this path, not exit 2).
    local i target
    local n=${#_parsed_keys[@]}
    for ((i = 0; i < n; i++)); do
        key="${_parsed_keys[$i]}"
        value="${_parsed_values[$i]}"
        target="${var_prefix}${key}"
        if ! [[ "$target" =~ ^[A-Za-z_][A-Za-z_0-9]*$ ]]; then
            echo "[aod] ERROR: constructed identifier '$target' is not a valid bash identifier" >&2
            return 1
        fi
        printf -v "$target" '%s' "$value"
    done

    return 0
}
