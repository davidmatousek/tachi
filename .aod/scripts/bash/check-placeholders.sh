#!/usr/bin/env bash
# =============================================================================
# check-placeholders.sh — Legacy placeholder drift scanner
# =============================================================================
# Part of feature 134 (downstream update bootstrap + placeholder migration).
#
# See specs/134-update-bootstrap-placeholder-migration/plan.md §Components and
# §System Design Data Flow (scanner flow) for architectural context, and
# specs/134-update-bootstrap-placeholder-migration/contracts/cli-contract.md
# for the externally-observable stdout / stderr / exit-code contract.
#
# Bash 3.2 compatible. Sourced by scripts/update.sh (via --check-placeholders
# dispatch). Reuses AOD_CANONICAL_PLACEHOLDERS from template-substitute.sh as
# the single source of truth for the canonical 12-placeholder allow-list —
# this file MUST NOT redefine those names (data-model.md §Entity 2).
#
# Public functions (prefix: aod_check_placeholders_):
#   - aod_check_placeholders_main        Orchestrator invoked by scripts/update.sh
#                                        --check-placeholders. Emits findings +
#                                        migration guide on drift (exit 13) or
#                                        exits silently on clean repo (exit 0).
#
# Internal functions (underscored):
#   - _compute_scan_scope                FR-011 — git ls-files minus exclusions
#   - _scan_files                        FR-012 — grep over scope, deterministic
#                                        order (git ls-files order, then line no)
#   - _filter_canonical                  FR-013 — subtract AOD_CANONICAL_PLACEHOLDERS
#   - _emit_findings                     FR-013 — stdout <path>:<line>: {{<name>}}
#   - _emit_migration_table              FR-015 — version-stamped LEGACY_MAP dump
#   - _legacy_map_lookup                 Parallel-array lookup by legacy name
#
# FR-016 compliance: this scanner NEVER writes any file under any circumstance.
# Flag-only enforcement — every output path goes to stdout or stderr.
#
# FR-017 compliance: every call to a helper that may return non-zero under
# set -euo pipefail is wrapped in a set +e / set -e bracket (precedent:
# scripts/check-manifest-coverage.sh:115-118, feature 132).
#
# FR-018 compliance: bash 3.2 — no declare -A, no readarray/mapfile, no
# ${var^}/${var,,}, no |& shorthand. Parallel arrays (LEGACY_MAP_KEYS /
# LEGACY_MAP_VALUES) per legacy-map-schema.md.
# =============================================================================

set -euo pipefail

# Guard against double-sourcing. Matches template-substitute.sh pattern.
if [ -n "${AOD_CHECK_PLACEHOLDERS_SH_SOURCED:-}" ]; then
    return 0
fi
readonly AOD_CHECK_PLACEHOLDERS_SH_SOURCED=1

# -----------------------------------------------------------------------------
# Source AOD_CANONICAL_PLACEHOLDERS — single source of truth per data-model.md
# §Entity 2 invariant "F134 code reads the array; it MUST NOT redefine it."
# -----------------------------------------------------------------------------
# Resolve repo root relative to this file so the scanner works when invoked
# from any CWD (as long as the .aod/scripts/bash/ tree is intact).
_AOD_CHECK_PLACEHOLDERS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./template-substitute.sh
. "$_AOD_CHECK_PLACEHOLDERS_DIR/template-substitute.sh"

# -----------------------------------------------------------------------------
# LEGACY_MAP — version-stamped parallel arrays per
# contracts/legacy-map-schema.md §Initial contents.
#
# Invariants enforced by BATS (tests/integration/134-*.bats):
#   1. ${#LEGACY_MAP_KEYS[@]} == ${#LEGACY_MAP_VALUES[@]}
#   2. LEGACY_MAP_VERSION is a valid YYYY-MM-DD date string
#   3. Each LEGACY_MAP_KEYS entry is unique
#   4. No LEGACY_MAP_KEYS entry appears in AOD_CANONICAL_PLACEHOLDERS
#
# Extension process: append to both arrays at the same index, bump VERSION,
# update BATS fixture, commit atomically (schema §Extension process).
# -----------------------------------------------------------------------------
LEGACY_MAP_VERSION="2026-04-24"

LEGACY_MAP_KEYS=(
    "DATABASE_TYPE"
    "DATABASE_PROVIDER"
    "VECTOR_DB"
    "AUTH_PROVIDER"
    "PROJECT_URL"
)

LEGACY_MAP_VALUES=(
    "TECH_STACK_DATABASE"
    "TECH_STACK_DATABASE"
    "TECH_STACK_VECTOR"
    "TECH_STACK_AUTH"
    "(no canonical — pending Issue #68)"
)

# -----------------------------------------------------------------------------
# Hardcoded scan-scope exclusions (FR-011).
#
# These files legitimately reference placeholder names as documentation
# literals (PRDs, specs, changelog, design guides) and MUST NOT be scanned.
# Matched against the path returned by `git ls-files` — a simple prefix /
# glob match per entry. Any path that matches ANY exclusion is dropped.
# -----------------------------------------------------------------------------
_aod_check_placeholders_is_excluded() {
    local path="$1"

    # Exact-file exclusions
    case "$path" in
        "docs/guides/DOWNSTREAM_UPDATE.md") return 0 ;;
        "CHANGELOG.md") return 0 ;;
    esac

    # Prefix/suffix pattern exclusions
    case "$path" in
        "docs/product/02_PRD/"*.md) return 0 ;;
        "specs/"*/"spec.md") return 0 ;;
        "specs/"*/"plan.md") return 0 ;;
        "specs/"*/"tasks.md") return 0 ;;
        "specs/"*/"delivery.md") return 0 ;;
        ".claude/"*.md) return 0 ;;
    esac

    return 1
}

# -----------------------------------------------------------------------------
# _compute_scan_scope (FR-011)
#
# Emits one scan-target path per line to stdout, in `git ls-files` order,
# minus the hardcoded exclusion list. Uses `git ls-files -z` + bash-3.2-safe
# NUL-delimited while loop (no readarray / mapfile — see CLAUDE.md KB Entry 6).
#
# Exits 1 with stderr message if not inside a git working tree.
#
# Args: none
# Stdout: one path per line (relative to repo root, git ls-files form)
# Stderr: error on not-in-git-repo
# Return: 0 on success, 1 on not-in-git-repo
# -----------------------------------------------------------------------------
_compute_scan_scope() {
    # Is this a git repo? `git rev-parse --is-inside-work-tree` returns
    # non-zero with stderr if not. We silence stderr because the helper
    # emits its own typed error per cli-contract.md §Stderr messages.
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        printf 'Error: --check-placeholders must be run from within a git repository\n' >&2
        return 1
    fi

    local path
    while IFS= read -r -d '' path; do
        if _aod_check_placeholders_is_excluded "$path"; then
            continue
        fi
        printf '%s\n' "$path"
    done < <(git ls-files -z)
}

# -----------------------------------------------------------------------------
# _scan_files (FR-012)
#
# Reads scope paths from stdin (one per line) and emits raw grep findings to
# stdout. Format: `<path>:<line>:<match>` (grep -Hn output for the pattern
# `\{\{[A-Z_][A-Z0-9_]*\}\}`).
#
# The F129 substitution engine uses a narrower pattern (`[A-Z_]+` — no digits);
# the scanner broadens to `[A-Z_][A-Z0-9_]*` so any future canonical addition
# with digits is not silently skipped (FR-012 rationale + spec P3 follow-up).
#
# Determinism: scope arrives in `git ls-files` order; grep emits findings in
# file order, then ascending line number within file — which is exactly the
# ordering cli-contract.md §Stdout format specifies. No explicit sort needed.
#
# Args: none (reads scope from stdin)
# Stdout: raw `<path>:<line>:<match>` grep lines
# Return: 0 always (grep rc=1 on "no matches in this file" is expected and
#         normalised below; rc>=2 indicates a real grep error)
# -----------------------------------------------------------------------------
_scan_files() {
    local path
    local grep_rc=0

    while IFS= read -r path; do
        if [ -z "$path" ]; then
            continue
        fi
        if [ ! -f "$path" ]; then
            # Tracked but missing (e.g., submodule path, deleted untracked);
            # skip silently — scanner reports drift in present tree only.
            continue
        fi

        # FR-017: bracket grep with set +e / set -e so rc=1 (no matches) does
        # not trip errexit. rc=0 (found), rc=1 (none), rc>=2 (I/O error).
        set +e
        grep -Hn -E '\{\{[A-Z_][A-Z0-9_]*\}\}' "$path"
        grep_rc=$?
        set -e

        if [ "$grep_rc" -ge 2 ]; then
            printf 'Warning: grep failed on %s (rc=%d)\n' "$path" "$grep_rc" >&2
        fi
    done

    return 0
}

# -----------------------------------------------------------------------------
# _is_canonical <name>
#
# Returns 0 iff <name> is in AOD_CANONICAL_PLACEHOLDERS. bash 3.2 compatible —
# linear scan, no associative arrays. Called once per grep match; the constant
# factor is the canonical set's size (12) — negligible versus I/O cost.
#
# Args: $1 — placeholder name without braces (e.g., PROJECT_NAME)
# Return: 0 if canonical, 1 otherwise
# -----------------------------------------------------------------------------
_is_canonical() {
    local candidate="$1"
    local canonical
    for canonical in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        if [ "$candidate" = "$canonical" ]; then
            return 0
        fi
    done
    return 1
}

# -----------------------------------------------------------------------------
# _filter_canonical (FR-013)
#
# Reads raw grep findings from stdin (`<path>:<line>:<match>` per line) and
# emits cleaned drift findings to stdout in the format
#   <path>:<line>: {{<name>}}
# with exactly one space between the trailing colon and the brace literal —
# matching cli-contract.md §Stdout format.
#
# Canonical names (members of AOD_CANONICAL_PLACEHOLDERS) are dropped; unknown
# legacy names (not in LEGACY_MAP_KEYS) are kept — the migration-table emitter
# produces a generic "unknown" row for any such name actually detected.
#
# A single grep line may contain multiple braces — the grep -E pattern matches
# the whole line, not each occurrence, so we extract ALL brace tokens on the
# line and emit a separate finding per token (per the "two occurrences in one
# file" assertion in @US-2-AC-1).
#
# Args: none (reads from stdin)
# Stdout: one finding per line, `<path>:<line>: {{<name>}}`
# Return: 0 always
# -----------------------------------------------------------------------------
_filter_canonical() {
    local line
    local path
    local lineno
    local rest
    local name
    local token

    while IFS= read -r line; do
        if [ -z "$line" ]; then
            continue
        fi
        # Split "path:lineno:rest" — path may contain no colons (safe because
        # our scan scope excludes none and we control `git ls-files` output).
        path="${line%%:*}"
        rest="${line#*:}"
        lineno="${rest%%:*}"
        rest="${rest#*:}"

        # Extract every `{{NAME}}` token on the line. bash 3.2 `=~` works,
        # but to keep the logic simple and portable we iterate via a trim
        # loop that greps each match off the remaining string.
        while [[ "$rest" == *"{{"* ]]; do
            # Strip everything up through the next `{{`
            token="${rest#*\{\{}"
            # Keep everything before the closing `}}`
            if [[ "$token" != *"}}"* ]]; then
                break
            fi
            name="${token%%\}\}*}"
            # Advance: consume the matched token so the next iteration finds
            # the following `{{...}}` on the same line.
            rest="${token#*\}\}}"

            # Validate the structural shape [A-Z_][A-Z0-9_]* — grep already
            # restricted the capture, but after our substring-extract the
            # token is re-tested defensively so rogue input from a future
            # pattern change cannot leak past.
            case "$name" in
                [A-Z_]*) ;;
                *) continue ;;
            esac
            # Second-pass filter: reject names with characters outside the
            # allowed set.
            if [[ "$name" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
                :
            else
                continue
            fi

            if _is_canonical "$name"; then
                continue
            fi

            printf '%s:%s: {{%s}}\n' "$path" "$lineno" "$name"
        done
    done

    return 0
}

# -----------------------------------------------------------------------------
# _legacy_map_lookup <legacy_name>
#
# Parallel-array lookup — returns the canonical equivalent (or guidance
# string) for a legacy name, or the empty string if the name is not in
# LEGACY_MAP_KEYS. bash 3.2 compatible — no associative arrays.
#
# Args: $1 — legacy placeholder name (e.g., DATABASE_TYPE)
# Stdout: canonical name or guidance string (empty if unknown)
# Return: 0 on found, 1 on unknown
# -----------------------------------------------------------------------------
_legacy_map_lookup() {
    local target="$1"
    local i=0
    local n=${#LEGACY_MAP_KEYS[@]}
    while [ "$i" -lt "$n" ]; do
        if [ "${LEGACY_MAP_KEYS[$i]}" = "$target" ]; then
            printf '%s' "${LEGACY_MAP_VALUES[$i]}"
            return 0
        fi
        i=$((i + 1))
    done
    return 1
}

# -----------------------------------------------------------------------------
# _emit_migration_table (FR-015)
#
# Reads the unique set of detected legacy names from stdin (one name per
# line — the caller strips duplicates) and emits the version-stamped
# migration guide to stdout, matching cli-contract.md §Stdout format:
#
#     Migration guide (as of <LEGACY_MAP_VERSION>):
#
#       Legacy name          → Canonical name
#       <KEY>                → <VALUE>
#       ...
#
#     See docs/guides/DOWNSTREAM_UPDATE.md for migration guidance.
#
# Only names actually detected get rows — canonical-pattern entries from
# LEGACY_MAP_KEYS not seen in this scan are NOT emitted (per schema §Rules).
# Unknown names (not in LEGACY_MAP_KEYS) get a single row with the generic
# "(unknown; remove or keep as literal)" guidance.
#
# Args: none (reads unique detected names from stdin)
# Stdout: migration table block
# Return: 0 always
# -----------------------------------------------------------------------------
_emit_migration_table() {
    printf 'Migration guide (as of %s):\n' "$LEGACY_MAP_VERSION"
    printf '\n'
    printf '  Legacy name          → Canonical name\n'

    local name
    local value
    local lookup_rc
    while IFS= read -r name; do
        if [ -z "$name" ]; then
            continue
        fi
        # FR-017: bracket the lookup so rc=1 (unknown) does not trip errexit.
        set +e
        value="$(_legacy_map_lookup "$name")"
        lookup_rc=$?
        set -e

        if [ "$lookup_rc" -eq 0 ]; then
            printf '  %-20s → %s\n' "$name" "$value"
        else
            printf '  %-20s → (unknown; remove or keep as literal)\n' "$name"
        fi
    done

    printf '\n'
    printf 'See docs/guides/DOWNSTREAM_UPDATE.md for migration guidance.\n'
}

# -----------------------------------------------------------------------------
# aod_check_placeholders_main (FR-014 + FR-016 + FR-017)
#
# Orchestrates the full scanner flow per plan.md §System Design Data Flow
# (scanner flow):
#
#   compute_scan_scope  →  scan_files  →  filter_canonical  →  (findings)
#                                                              ↓
#                                                      emit_migration_table
#
# Exit codes (cli-contract.md §Exit codes):
#   0   — No drift found (silent, no stdout)
#   1   — Scan setup failure (not in a git repo) — raised by _compute_scan_scope
#   13  — Drift found (findings + migration guide to stdout)
#
# NEVER writes any file (FR-016). Every rc-capture uses the F132 set +e /
# set -e bracket pattern (FR-017).
#
# Args: any — ignored for now (scanner takes no sub-flags per cli-contract.md
#       §Flags; future options per FR-010 P1 deferrals).
# Stdout: findings + migration table on drift
# Stderr: typed error on setup failure
# Return: 0 / 1 / 13 per exit-code table
# -----------------------------------------------------------------------------
aod_check_placeholders_main() {
    local scope=""
    local scope_rc=0
    local findings=""
    local unique_names=""

    # Step 1 — compute scope. FR-017 bracket: the helper may emit rc=1 on
    # "not in git repo", which must surface as exit 1 with its stderr.
    set +e
    scope="$(_compute_scan_scope)"
    scope_rc=$?
    set -e

    if [ "$scope_rc" -ne 0 ]; then
        return 1
    fi

    # Empty scope (e.g., a freshly-initialized git repo with zero tracked
    # files) is a clean-repo case — exit 0 silently per FR-014.
    if [ -z "$scope" ]; then
        return 0
    fi

    # Step 2 + 3 — scan + filter. FR-017 bracket guards the sub-pipeline so a
    # grep rc>=2 (real I/O error) does not silently abort; _scan_files
    # normalises grep rc=1 (no matches in a file) internally.
    set +e
    findings="$(printf '%s\n' "$scope" | _scan_files | _filter_canonical)"
    local scan_rc=$?
    set -e

    if [ "$scan_rc" -ne 0 ]; then
        # Unexpected failure in the scan pipeline; surface as setup error.
        printf 'Error: placeholder scan pipeline failed (rc=%d)\n' "$scan_rc" >&2
        return 1
    fi

    # Step 4 — exit 0 if no findings (FR-014 clean case).
    if [ -z "$findings" ]; then
        return 0
    fi

    # Step 5 — emit findings (FR-013 stdout format) and the migration table
    # (FR-015). The findings arrive from _filter_canonical already in the
    # deterministic order specified by cli-contract.md §Stdout format, so we
    # just print the buffered output verbatim.
    printf '%s\n' "$findings"
    printf '\n'

    # Compute the unique set of detected legacy names for the migration table.
    # awk is POSIX-standard; we keep insertion order (not sort) because the
    # table rows follow the order of first appearance in the findings — this
    # keeps the migration table alignment with the findings list stable.
    unique_names="$(printf '%s\n' "$findings" | awk '
        match($0, /\{\{[A-Z_][A-Z0-9_]*\}\}/) {
            token = substr($0, RSTART+2, RLENGTH-4)
            if (!(token in seen)) {
                seen[token] = 1
                print token
            }
        }
    ')"

    printf '%s\n' "$unique_names" | _emit_migration_table

    # FR-014 exit 13 — drift present.
    return 13
}

# If this file is executed directly (e.g., smoke-test), dispatch to main.
# Sourcing (the normal case from scripts/update.sh) does NOT hit this block.
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    aod_check_placeholders_main "$@"
    exit $?
fi
