#!/usr/bin/env bash
# =============================================================================
# template-validate.sh — Path sanitization, symlink rejection, residual scan
# =============================================================================
# Part of feature 129 (downstream template update mechanism).
#
# Bash 3.2 compatible. Sourced by scripts/update.sh and scripts/sync-upstream.sh.
#
# Public functions (prefix: aod_template_):
#   - aod_template_assert_safe_path        Reject `..`, `~`, absolute paths.
#   - aod_template_assert_no_symlink       Reject symlinks via test -L.
#   - aod_template_scan_residual_placeholders   Grep for {{[A-Z_]+}} in a file.
#                                               Factored from sync-upstream.sh:812-839.
#   - aod_template_assert_guard            Match path against USER_OWNED_GUARD
#                                          array (passed by name). (T032, Wave 3.)
#
# Mixed factor-out: residual scan is factored from sync-upstream.sh; safe-path
# and no-symlink helpers are new code for feature 129.
# See contracts/library-api.md §template-validate.sh for API details.
#
# Bodies implemented in T012 (scan_residual_placeholders), T013 (assert_safe_path,
# assert_no_symlink). T032 (assert_guard) is Wave 3.
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_TEMPLATE_VALIDATE_SH_SOURCED:-}" ]; then
  return 0
fi
readonly AOD_TEMPLATE_VALIDATE_SH_SOURCED=1

# -----------------------------------------------------------------------------
# aod_template_scan_residual_placeholders <file>
# -----------------------------------------------------------------------------
# Scan a file for residual `{{[A-Z_]+}}` placeholders. If no argument is given,
# reads from stdin and treats the input as a single logical file (no filename
# prefix in matches).
#
# Factored from scripts/sync-upstream.sh:812-839. The original implementation
# scanned a fixed list of files using `grep -n '{{[A-Z_]*}}' <file>`. The
# factored helper accepts an arbitrary path.
#
# Note: the historical regex used `[A-Z_]*` (zero-or-more). Per the contract
# (library-api.md §template-validate.sh), the canonical residual pattern is
# `{{[A-Z_]+}}` (one-or-more). We use the one-or-more form here since any
# legitimate placeholder has at least one character; `{{}}` is not a
# placeholder. This change is a TIGHTENING of the regex and does not affect
# the legacy sync-upstream scan_files list (those files' placeholders all have
# ≥1 uppercase char).
#
# Arguments:
#   $1 — path to a file to scan (optional; if omitted, reads stdin)
# Output:
#   matching `grep -n` lines to stdout, prefixed with `<file>:` when a file
#   path was provided.
# Return:
#   0 if no residual placeholders found
#   1 if one or more residual placeholders found
# -----------------------------------------------------------------------------
aod_template_scan_residual_placeholders() {
    local file="${1:-}"
    local matches=""

    if [ -n "$file" ]; then
        if [ ! -f "$file" ]; then
            echo "[aod] ERROR: scan target not a regular file: $file" >&2
            return 1
        fi
        matches=$(grep -nE '\{\{[A-Z_]+\}\}' "$file" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            # Prefix each match line with the file path for downstream tooling
            printf '%s\n' "$matches" | sed "s|^|${file}:|"
            return 1
        fi
    else
        matches=$(grep -nE '\{\{[A-Z_]+\}\}' 2>/dev/null || true)
        if [ -n "$matches" ]; then
            printf '%s\n' "$matches"
            return 1
        fi
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_assert_safe_path <path>
# -----------------------------------------------------------------------------
# Assert a path is safe for use as a manifest target or staging target.
# Rejects:
#   - absolute paths (leading `/`)
#   - parent references (`..` as any path segment)
#   - home expansion (leading `~` or `~/...`)
#   - the literal `.` or empty path
#
# Bash 3.2 compatible; uses `case` pattern matching per style consistency
# with the rest of the codebase (plan §C4 convention).
#
# Arguments:
#   $1 — the path to validate
# Return:
#   0 if safe
#   1 if rejected (stderr: named offending path + rule broken)
# -----------------------------------------------------------------------------
aod_template_assert_safe_path() {
    local path="${1:-}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: empty path rejected by aod_template_assert_safe_path" >&2
        return 1
    fi

    # Reject absolute paths
    case "$path" in
        /*)
            echo "[aod] ERROR: absolute path rejected: $path (must be relative to repo root)" >&2
            return 1
            ;;
    esac

    # Reject home expansion
    case "$path" in
        '~'|'~/'*|*/'~'|*/'~/'*)
            echo "[aod] ERROR: home expansion rejected: $path (~ not allowed in path)" >&2
            return 1
            ;;
    esac

    # Reject `..` as any segment (start, middle, end, or sole)
    case "$path" in
        '..'|'../'*|*'/..'|*'/../'*)
            echo "[aod] ERROR: parent reference rejected: $path (.. not allowed in path)" >&2
            return 1
            ;;
    esac

    # Reject `.` as sole segment (covers empty-relative "."). We do NOT reject
    # `./foo` or paths containing `.` mid-segment (they are valid filenames).
    case "$path" in
        '.')
            echo "[aod] ERROR: current-dir reference rejected: $path" >&2
            return 1
            ;;
    esac

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_assert_no_symlink <path>
# -----------------------------------------------------------------------------
# Reject <path> if it is a symlink (regardless of target validity).
# Uses `test -L` which returns true for symlinks even when the target is
# missing or broken.
#
# Arguments:
#   $1 — path to check (absolute or relative)
# Return:
#   0 if not a symlink
#   1 if it is a symlink (stderr: named offending path)
# -----------------------------------------------------------------------------
aod_template_assert_no_symlink() {
    local path="${1:-}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: empty path rejected by aod_template_assert_no_symlink" >&2
        return 1
    fi

    if [ -L "$path" ]; then
        echo "[aod] ERROR: symlink rejected: $path (template update refuses to follow or overwrite symlinks)" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_assert_guard <target_path> <guard_array_name>
# -----------------------------------------------------------------------------
# Assert that <target_path> does NOT match any pattern in the guard array
# referenced by <guard_array_name> (indirect name reference via `eval`).
#
# The guard array is expected to be a bash array literal defined as `readonly`
# in scripts/update.sh (see plan §C4 — tamper-resistance). Patterns use the
# SAME glob syntax as manifest entries (`**` = any segments, `*` = single
# segment), and the match is ANCHORED to the repo-root-relative path.
#
# Precedence (per contracts/manifest-schema.md): guard overrides all manifest
# categorizations except `ignore`. If a manifest entry authorizes a write to
# `docs/product/foo.md` as `owned`, this function still rejects the write
# because `docs/product/**` is in the guard list.
#
# Bash 3.2 compatibility: uses `eval` + indirect expansion to iterate the
# named array (bash 3.2 supports `${!var}` and `${name[@]}` expansion, but
# iterating an array by name reference requires `eval` to preserve word
# boundaries in 3.2 — nameref `declare -n` is bash 4.3+).
#
# Arguments:
#   $1 — the target path to test (relative, repo-rooted)
#   $2 — the name of the guard array variable (e.g., USER_OWNED_GUARD)
# Return:
#   0 if the path matches NO guard pattern (safe to write)
#   6 if the path matches at least one guard pattern (exit code per cli-contract.md)
#   1 on malformed arguments (empty path or array name)
# Side effects (stderr on rejection):
#   "[aod] ERROR: guard violation: <path> matched guard pattern <pattern>"
# -----------------------------------------------------------------------------
aod_template_assert_guard() {
    local path="${1:-}"
    local array_name="${2:-}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: aod_template_assert_guard requires a non-empty target path" >&2
        return 1
    fi
    if [ -z "$array_name" ]; then
        echo "[aod] ERROR: aod_template_assert_guard requires a guard-array name" >&2
        return 1
    fi

    # Require aod_template_glob_match (declared in template-manifest.sh). Soft
    # dependency — the caller should have sourced both libs.
    if ! declare -f aod_template_glob_match >/dev/null 2>&1; then
        echo "[aod] ERROR: aod_template_assert_guard requires template-manifest.sh (aod_template_glob_match not defined)" >&2
        return 1
    fi

    # Expand the named array into a local copy via `eval`. Bash 3.2 does not
    # support `declare -n` (namerefs), so we serialize then re-parse.
    # Pattern below is bash 3.2 safe: `${ARR[@]}` is expanded inside eval's
    # single-quoted arg against the caller's scope.
    local patterns=()
    eval "patterns=(\"\${${array_name}[@]}\")" 2>/dev/null || {
        echo "[aod] ERROR: aod_template_assert_guard: guard array '$array_name' is not set or not an array" >&2
        return 1
    }

    if [ "${#patterns[@]}" -eq 0 ]; then
        # Empty guard array — nothing to check, path passes. This is the
        # expected state only during bootstrap; production code always
        # supplies a populated array.
        return 0
    fi

    local pattern
    for pattern in "${patterns[@]}"; do
        if aod_template_glob_match "$pattern" "$path"; then
            echo "[aod] ERROR: guard violation: $path matched guard pattern '$pattern' (user-owned path — manifest cannot overwrite)" >&2
            return 6
        fi
    done

    return 0
}
