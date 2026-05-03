#!/usr/bin/env bash
# =============================================================================
# template-manifest.sh — Manifest parser, glob matcher, category resolver
# =============================================================================
# Part of feature 129 (downstream template update mechanism).
#
# Bash 3.2 compatible. Sourced by scripts/update.sh and scripts/sync-upstream.sh.
#
# Public functions (prefix: aod_template_):
#   - aod_template_parse_manifest          Parse .aod/template-manifest.txt into
#                                          <category>|<path-or-glob> tuples.
#   - aod_template_glob_match              Glob matcher (bash regex under the
#                                          hood for anchored whole-path matching).
#                                          Supports `**` and `*` semantics:
#                                            `**` matches any sequence (incl. `/`)
#                                            `*`  matches a single segment (no `/`)
#   - aod_template_category_for_path       Resolve a path to its winning category
#                                          via precedence.
#   - aod_template_resolve_precedence      Apply ignore > guard > user > scaffold
#                                          > merge > personalized > owned order.
#
# NOT factored from scripts/sync-upstream.sh — category model differs.
# See contracts/library-api.md §template-manifest.sh for API details.
# See contracts/manifest-schema.md for precedence + path/glob semantics.
#
# Bodies implemented in T014 (feature 129).
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_TEMPLATE_MANIFEST_SH_SOURCED:-}" ]; then
  return 0
fi
readonly AOD_TEMPLATE_MANIFEST_SH_SOURCED=1

# Ensure template-validate.sh is available for aod_template_assert_safe_path.
# Soft dependency: if not loaded, we emit a degraded error (the caller should
# normally source both libraries together).
_aod_manifest_require_validate() {
    if ! declare -f aod_template_assert_safe_path >/dev/null 2>&1; then
        echo "[aod] ERROR: template-manifest.sh requires template-validate.sh to be sourced first" >&2
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# aod_template_parse_manifest <manifest_path>
# -----------------------------------------------------------------------------
# Parse a manifest file (.aod/template-manifest.txt by convention) and emit
# `<category>|<path-or-glob>` tuples to stdout. Skips blank lines and comment
# lines (those starting with `#`, optionally preceded by whitespace). Rejects
# unsafe paths via aod_template_assert_safe_path.
#
# Valid categories (must match exactly): owned, personalized, user, scaffold,
# merge, ignore.
#
# Arguments:
#   $1 — path to the manifest file
# Output:
#   One `<category>|<path>` tuple per line to stdout.
# Return:
#   0 on success
#   1 if the file is missing, unreadable, or contains malformed lines
# Errors (stderr):
#   - "manifest file not found"
#   - "manifest malformed at line N: missing separator"
#   - "manifest malformed at line N: invalid category"
#   - "manifest malformed at line N: unsafe path"
# -----------------------------------------------------------------------------
aod_template_parse_manifest() {
    local manifest="${1:-}"

    if [ -z "$manifest" ]; then
        echo "[aod] ERROR: aod_template_parse_manifest requires a manifest path" >&2
        return 1
    fi
    if [ ! -f "$manifest" ]; then
        echo "[aod] ERROR: manifest file not found: $manifest" >&2
        return 1
    fi

    _aod_manifest_require_validate || return 1

    local line_num=0
    local rc=0
    local line stripped category path_glob

    while IFS= read -r line || [ -n "$line" ]; do
        line_num=$((line_num + 1))

        # Strip trailing carriage return (CRLF tolerance for Windows-edited manifests).
        # Bash 3.2 / POSIX compatible parameter expansion.
        line="${line%$'\r'}"

        # Strip leading whitespace for blank/comment detection
        stripped="${line#"${line%%[![:space:]]*}"}"

        # Skip blank lines
        if [ -z "$stripped" ]; then
            continue
        fi

        # Skip comment lines
        case "$stripped" in
            '#'*) continue ;;
        esac

        # Require the separator `|`
        case "$line" in
            *'|'*) : ;;
            *)
                echo "[aod] ERROR: manifest malformed at line ${line_num}: missing '|' separator: $line" >&2
                rc=1
                continue
                ;;
        esac

        # Split on the FIRST `|` (bash 3.2 compatible)
        category="${line%%|*}"
        path_glob="${line#*|}"

        # Validate category (must be one of the 6 known values)
        case "$category" in
            owned|personalized|user|scaffold|merge|ignore) : ;;
            *)
                echo "[aod] ERROR: manifest malformed at line ${line_num}: invalid category '$category'" >&2
                rc=1
                continue
                ;;
        esac

        # Reject empty path
        if [ -z "$path_glob" ]; then
            echo "[aod] ERROR: manifest malformed at line ${line_num}: empty path after separator" >&2
            rc=1
            continue
        fi

        # Validate the path/glob pattern is safe (rejects .., ~, absolute)
        if ! aod_template_assert_safe_path "$path_glob" 2>/dev/null; then
            echo "[aod] ERROR: manifest malformed at line ${line_num}: unsafe path '$path_glob'" >&2
            rc=1
            continue
        fi

        printf '%s|%s\n' "$category" "$path_glob"
    done < "$manifest"

    return $rc
}

# -----------------------------------------------------------------------------
# aod_template_glob_match <pattern> <path>
# -----------------------------------------------------------------------------
# Test whether a glob pattern matches a path. Anchored to the full path (no
# implicit prefix match).
#
# Glob semantics (bash 3.2 compatible):
#   - `**` matches any sequence of characters, including path separators.
#   - `*`  matches any sequence WITHIN a single path segment (no `/`).
#   - Literal characters match themselves.
#
# Implementation: translate the glob into an anchored extended regex and use
# bash's `[[ =~ ]]` operator. Bash 3.2 supports `=~` in `[[ ]]` tests; no
# globstar / extglob required.
#
# Arguments:
#   $1 — glob pattern (relative, repo-rooted)
#   $2 — path to test (relative, repo-rooted)
# Return:
#   0 on match
#   1 on no match or invalid arguments
# -----------------------------------------------------------------------------
aod_template_glob_match() {
    local pattern="${1:-}"
    local path="${2:-}"

    if [ -z "$pattern" ] || [ -z "$path" ]; then
        return 1
    fi

    # Build a regex from the glob. Process `**` before `*` by using a sentinel
    # for `**` that cannot clash with input (null bytes not representable in
    # bash strings; use a rare char sequence instead).
    local p="$pattern"
    local sentinel=$'\x01\x02STAR_STAR\x02\x01'
    local regex=""
    local i=0
    local len=${#p}
    local ch next

    # Stage 1: replace `**` with sentinel.
    # Bash 3.2 has no string-replace of substrings with special chars via sed
    # reliably; do it char-by-char instead.
    local tmp=""
    while [ $i -lt $len ]; do
        ch="${p:$i:1}"
        if [ "$ch" = "*" ] && [ $((i + 1)) -lt $len ] && [ "${p:$((i + 1)):1}" = "*" ]; then
            tmp="${tmp}${sentinel}"
            i=$((i + 2))
        else
            tmp="${tmp}${ch}"
            i=$((i + 1))
        fi
    done

    # Stage 2: walk the (now de-`**`ed) string, converting:
    #   `*` → `[^/]*`     (single-segment wildcard)
    #   regex metachars → escaped
    #   sentinel → `.*`   (multi-segment wildcard)
    i=0
    len=${#tmp}
    while [ $i -lt $len ]; do
        # Sentinel detection: compare a slice equal to sentinel length
        if [ $((i + ${#sentinel})) -le $len ] && [ "${tmp:$i:${#sentinel}}" = "$sentinel" ]; then
            regex="${regex}.*"
            i=$((i + ${#sentinel}))
            continue
        fi

        ch="${tmp:$i:1}"
        case "$ch" in
            '*')
                regex="${regex}[^/]*"
                ;;
            '.'|'+'|'?'|'('|')'|'['|']'|'{'|'}'|'^'|'$'|'|'|'\\')
                regex="${regex}\\${ch}"
                ;;
            *)
                regex="${regex}${ch}"
                ;;
        esac
        i=$((i + 1))
    done

    # Anchor the regex to match the full path.
    regex="^${regex}\$"

    # Use bash's [[ =~ ]] (available in bash 3.2).
    if [[ "$path" =~ $regex ]]; then
        return 0
    fi
    return 1
}

# -----------------------------------------------------------------------------
# aod_template_resolve_precedence (reads stdin)
# -----------------------------------------------------------------------------
# Given a newline-delimited list of `<category>|<entry>` candidate matches on
# stdin, return the single winning line. Precedence (highest wins):
#   ignore > guard > user > scaffold > merge > personalized > owned
#
# The `guard` category is reserved for the hardcoded user-owned guard list
# (FR-007) — manifest entries cannot legitimately produce guard matches; the
# guard layer is applied externally by aod_template_assert_guard. This helper
# honors `guard` in the precedence table for completeness, so callers that
# stream guard candidates alongside manifest candidates get correct results.
#
# Output (stdout):
#   The single winning `<category>|<entry>` line. Empty output if no input.
# Return:
#   0 on success
#   1 if the input contains a line with an unknown category
# -----------------------------------------------------------------------------
aod_template_resolve_precedence() {
    local winner=""
    local winner_rank=99
    local line category rank
    local rc=0

    while IFS= read -r line || [ -n "$line" ]; do
        if [ -z "$line" ]; then
            continue
        fi
        case "$line" in
            *'|'*) : ;;
            *)
                echo "[aod] ERROR: precedence input malformed: $line" >&2
                rc=1
                continue
                ;;
        esac

        category="${line%%|*}"
        case "$category" in
            ignore)       rank=0 ;;
            guard)        rank=1 ;;
            user)         rank=2 ;;
            scaffold)     rank=3 ;;
            merge)        rank=4 ;;
            personalized) rank=5 ;;
            owned)        rank=6 ;;
            *)
                echo "[aod] ERROR: precedence input has unknown category '$category' in line: $line" >&2
                rc=1
                continue
                ;;
        esac

        if [ $rank -lt $winner_rank ]; then
            winner_rank=$rank
            winner="$line"
        fi
    done

    if [ -n "$winner" ]; then
        printf '%s\n' "$winner"
    fi
    return $rc
}

# -----------------------------------------------------------------------------
# aod_template_category_for_path <path> <manifest_path>
# -----------------------------------------------------------------------------
# Given a path and a manifest file, return the winning `<category>|<entry>`
# line for that path. Enumerates all manifest entries whose glob matches the
# path, then applies aod_template_resolve_precedence.
#
# Arguments:
#   $1 — relative path (repo-rooted)
#   $2 — manifest path
# Output (stdout):
#   The winning `<category>|<entry>` line; empty if no match.
# Return:
#   0 if at least one entry matched
#   5 if no manifest entry matched (uncategorized — maps to CLI exit code 5)
#   1 on malformed manifest or other error
# -----------------------------------------------------------------------------
aod_template_category_for_path() {
    local path="${1:-}"
    local manifest="${2:-}"

    if [ -z "$path" ] || [ -z "$manifest" ]; then
        echo "[aod] ERROR: aod_template_category_for_path requires <path> and <manifest>" >&2
        return 1
    fi

    local parsed
    parsed=$(aod_template_parse_manifest "$manifest") || return 1

    local candidates=""
    local tuple entry_cat entry_pattern

    # Enumerate manifest entries, collect matches
    while IFS= read -r tuple || [ -n "$tuple" ]; do
        if [ -z "$tuple" ]; then
            continue
        fi
        entry_cat="${tuple%%|*}"
        entry_pattern="${tuple#*|}"
        if aod_template_glob_match "$entry_pattern" "$path"; then
            if [ -z "$candidates" ]; then
                candidates="$tuple"
            else
                candidates="${candidates}
${tuple}"
            fi
        fi
    done <<EOF
$parsed
EOF

    if [ -z "$candidates" ]; then
        return 5
    fi

    printf '%s\n' "$candidates" | aod_template_resolve_precedence
    return 0
}
