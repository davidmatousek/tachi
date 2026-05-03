#!/usr/bin/env bash
# LIBRARY — source before calling functions
# Scope guard for /aod.deliver auto-fix loop (US-9). Deterministic authorization — no LLM.
# Bash 3.2 compatible — awk for regex, no declare -A, no readarray, no yq.
#
# Canonical contracts:
#   specs/139-delivery-verified-not-documented/contracts/scope-guard-decision.md
#   specs/139-delivery-verified-not-documented/contracts/stack-pack-test-paths.md
#   specs/139-delivery-verified-not-documented/plan.md §Research R-4, R-5
#
# Public functions:
#   detect_framework          — inspect repo root for playwright/cypress/jest configs
#   check_diff_paths          — Layer 1: file paths must match test_paths globs
#   check_diff_rules          — Layer 2: line-content rule set (6 rules)
#   evaluate_scope_guard      — orchestrator; returns allowed|rejected JSON
#   get_test_paths            — read stack pack's test_paths, fall back to defaults
#
# Internal helpers:
#   _check_balanced_diff      — reject malformed diffs missing paired headers
#   _extract_diff_paths       — scrape +++/---/rename headers into path list
#   _match_any_glob           — glob-match a path against an array of globs
#
# Exit/return semantics:
#   Library functions echo JSON to stdout and always return 0.
#   Caller inspects `.decision` field ("allowed" | "rejected") via jq.
#
# Bash 3.2 compatible (macOS): no `declare -A`, no `${var,,}`, no `readarray`,
# no `|&`, no `yq`, no `grep -P`.

# Re-source guard — idempotent when sourced multiple times.
if [ -n "${AOD_SCOPE_GUARD_SH_LOADED:-}" ]; then
    return 0 2>/dev/null || true
fi
AOD_SCOPE_GUARD_SH_LOADED=1

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Default test_paths globs — applied when active pack omits the key (or when
# no pack is active). See plan.md §Research R-5 and T054 (architect M-2 Option B).
# NOTE: Bare `**/test-utils/**` and `**/__tests__/**` are intentionally absent;
# they matched production source directories (e.g., frontend/src/components/test-utils/).
# Replaced with rooted variants under tests/ and e2e/.
AOD_SCOPE_GUARD_DEFAULT_TEST_PATHS='[
  "tests/",
  "e2e/",
  "backend/tests/",
  "frontend/tests/",
  "frontend/e2e/",
  "**/*.test.ts",
  "**/*.spec.ts",
  "**/*.test.tsx",
  "**/*.spec.tsx",
  "**/*.test.js",
  "**/*.spec.js",
  "tests/test-utils/**",
  "e2e/test-utils/**",
  "tests/__tests__/**",
  "e2e/__tests__/**"
]'

# -----------------------------------------------------------------------------
# detect_framework
# -----------------------------------------------------------------------------
# Args:
#   $1 repo_root — directory to inspect (defaults to current working dir)
# Echoes: "playwright" | "cypress" | "jest" | "unknown"
# Always returns 0.
detect_framework() {
    local repo_root="${1:-.}"

    # Playwright config detection — canonical config filenames.
    local ext
    for ext in ts js mjs cjs; do
        if [ -f "${repo_root}/playwright.config.${ext}" ]; then
            echo "playwright"
            return 0
        fi
    done

    # Cypress — newer config forms AND legacy cypress.json.
    for ext in ts js mjs cjs; do
        if [ -f "${repo_root}/cypress.config.${ext}" ]; then
            echo "cypress"
            return 0
        fi
    done
    if [ -f "${repo_root}/cypress.json" ]; then
        echo "cypress"
        return 0
    fi

    # Jest — config file OR `jest` key in package.json.
    for ext in ts js mjs cjs; do
        if [ -f "${repo_root}/jest.config.${ext}" ]; then
            echo "jest"
            return 0
        fi
    done
    if [ -f "${repo_root}/package.json" ] && command -v jq >/dev/null 2>&1; then
        if jq -e '.jest // empty' "${repo_root}/package.json" >/dev/null 2>&1; then
            echo "jest"
            return 0
        fi
    fi

    echo "unknown"
    return 0
}

# -----------------------------------------------------------------------------
# _check_balanced_diff (T053)
# -----------------------------------------------------------------------------
# Validates that the diff has balanced headers:
#   - every `--- a/X` has a matching `+++ b/Y`
#   - every `rename from X` has a matching `rename to Y`
# Echoes empty string on success, or rejection reason on failure.
# Always returns 0 — caller checks stdout content.
_check_balanced_diff() {
    local diff_file="${1:-}"

    if [ ! -r "$diff_file" ]; then
        echo "Malformed diff: cannot read input"
        return 0
    fi

    # Count headers. awk is portable; grep -c would also work but less explicit.
    local counts
    counts=$(awk '
        /^--- / { minus++ }
        /^\+\+\+ / { plus++ }
        /^rename from / { rfrom++ }
        /^rename to / { rto++ }
        END {
            printf "%d %d %d %d", (minus+0), (plus+0), (rfrom+0), (rto+0)
        }
    ' "$diff_file")

    local minus_count plus_count rfrom_count rto_count
    minus_count=$(echo "$counts" | awk '{print $1}')
    plus_count=$(echo "$counts" | awk '{print $2}')
    rfrom_count=$(echo "$counts" | awk '{print $3}')
    rto_count=$(echo "$counts" | awk '{print $4}')

    if [ "$minus_count" != "$plus_count" ]; then
        echo "Malformed diff: missing paired header"
        return 0
    fi

    if [ "$rfrom_count" != "$rto_count" ]; then
        echo "Malformed diff: missing paired header"
        return 0
    fi

    echo ""
    return 0
}

# -----------------------------------------------------------------------------
# _extract_diff_paths
# -----------------------------------------------------------------------------
# Emit one repo-relative path per line for every file touched by the diff.
# Sources scanned: `+++ b/X`, `--- a/X`, `rename from X`, `rename to Y`.
# Filters out `/dev/null` and dedupes.
_extract_diff_paths() {
    local diff_file="${1:-}"

    awk '
        /^\+\+\+ b\// {
            path = $0
            sub(/^\+\+\+ b\//, "", path)
            if (path != "/dev/null" && path != "") print path
            next
        }
        /^--- a\// {
            path = $0
            sub(/^--- a\//, "", path)
            if (path != "/dev/null" && path != "") print path
            next
        }
        /^rename from / {
            path = $0
            sub(/^rename from /, "", path)
            if (path != "") print path
            next
        }
        /^rename to / {
            path = $0
            sub(/^rename to /, "", path)
            if (path != "") print path
            next
        }
    ' "$diff_file" | awk '!seen[$0]++'
}

# -----------------------------------------------------------------------------
# _match_any_glob
# -----------------------------------------------------------------------------
# Returns 0 (match) if $path matches ANY glob in the newline-separated $globs.
# Returns 1 if no glob matches.
#
# Glob semantics:
#   - `tests/`               — prefix match (any file under tests/)
#   - `backend/tests/`       — prefix match
#   - `**/*.test.ts`         — doublestar: any .test.ts file at any depth
#   - `tests/test-utils/**`  — prefix plus anything below
#   - plain `**`             — matches anything
# Bash 3.2: use [[ ... == glob ]] with extglob-off (default). Doublestar via
# `==` does NOT cross path separators on bash 3.2 — we special-case `**` by
# translating to a shell-friendly pattern or using case-based prefix checks.
_match_any_glob() {
    local path="${1:-}"
    local globs="${2:-}"
    local glob
    local IFS_SAVE="$IFS"

    # Split globs on newlines without array-syntax issues on bash 3.2.
    IFS=$'\n'
    set -f  # disable globbing while iterating glob strings literally
    for glob in $globs; do
        [ -z "$glob" ] && continue

        # Strip surrounding whitespace (defensive for awk-extracted values).
        glob="${glob# }"
        glob="${glob% }"

        # Case 1: trailing slash — prefix match.
        case "$glob" in
            */)
                local prefix="$glob"
                case "$path" in
                    "$prefix"*)
                        IFS="$IFS_SAVE"; set +f
                        return 0
                        ;;
                esac
                continue
                ;;
        esac

        # Case 2: `**/<suffix>` — doublestar prefix; suffix is a simple glob.
        case "$glob" in
            '**/'*)
                local suffix="${glob#\*\*/}"
                # Check both direct match (basename level) and any-depth match.
                # shellcheck disable=SC2053
                if [[ "$path" == $suffix ]]; then
                    IFS="$IFS_SAVE"; set +f
                    return 0
                fi
                # Any-depth: check each `**/<suffix>` expansion by walking
                # path components and testing the tail against suffix glob.
                local sub="$path"
                while [ "$sub" != "${sub#*/}" ]; do
                    sub="${sub#*/}"
                    # shellcheck disable=SC2053
                    if [[ "$sub" == $suffix ]]; then
                        IFS="$IFS_SAVE"; set +f
                        return 0
                    fi
                done
                continue
                ;;
        esac

        # Case 3: `<prefix>/**` — prefix match (everything below).
        case "$glob" in
            *'/**')
                local dir="${glob%\/\*\*}"
                case "$path" in
                    "$dir"/*)
                        IFS="$IFS_SAVE"; set +f
                        return 0
                        ;;
                esac
                continue
                ;;
        esac

        # Case 4: `<prefix>/**/<suffix>` — rooted doublestar.
        case "$glob" in
            *'/**/'*)
                local dir="${glob%%/\*\*/*}"
                local suffix="${glob#*/\*\*/}"
                case "$path" in
                    "$dir"/*)
                        # Trim prefix, then check each tail against suffix.
                        local tail="${path#"$dir"/}"
                        # shellcheck disable=SC2053
                        if [[ "$tail" == $suffix ]]; then
                            IFS="$IFS_SAVE"; set +f
                            return 0
                        fi
                        local sub2="$tail"
                        while [ "$sub2" != "${sub2#*/}" ]; do
                            sub2="${sub2#*/}"
                            # shellcheck disable=SC2053
                            if [[ "$sub2" == $suffix ]]; then
                                IFS="$IFS_SAVE"; set +f
                                return 0
                            fi
                        done
                        ;;
                esac
                continue
                ;;
        esac

        # Case 5: literal glob (no `**`, no trailing slash).
        # shellcheck disable=SC2053
        if [[ "$path" == $glob ]]; then
            IFS="$IFS_SAVE"; set +f
            return 0
        fi
    done

    IFS="$IFS_SAVE"
    set +f
    return 1
}

# -----------------------------------------------------------------------------
# check_diff_paths (Layer 1)
# -----------------------------------------------------------------------------
# Args:
#   $1 diff_file         — path to unified diff
#   $2 test_paths_json   — JSON array of glob patterns
# Echoes: JSON result `{"decision": "allowed"}` or rejection record.
check_diff_paths() {
    local diff_file="${1:-}"
    local test_paths_json="${2:-[]}"
    local globs
    local path

    if ! command -v jq >/dev/null 2>&1; then
        jq_fallback_reject "scope_guard: jq not found on PATH"
        return 0
    fi

    # Convert JSON array to newline-separated glob list.
    globs=$(printf '%s' "$test_paths_json" | jq -r '.[]' 2>/dev/null)
    if [ -z "$globs" ]; then
        # No globs declared — reject everything to be safe.
        jq -n --arg reason "File scope check: no test_paths declared" \
            '{decision: "rejected", reason: $reason, violating_lines: []}'
        return 0
    fi

    # Walk every changed path; first offender wins.
    local offenders=""
    while IFS= read -r path; do
        [ -z "$path" ] && continue
        if ! _match_any_glob "$path" "$globs"; then
            offenders="${offenders}${path}"$'\n'
        fi
    done <<EOF
$(_extract_diff_paths "$diff_file")
EOF

    if [ -n "$offenders" ]; then
        local first
        first=$(printf '%s' "$offenders" | head -n 1)
        jq -n \
            --arg reason "File ${first} is outside declared test_paths" \
            --arg line "$first" \
            '{decision: "rejected", reason: $reason, rule: "layer1_path", violating_lines: [$line]}'
        return 0
    fi

    jq -n '{decision: "allowed"}'
    return 0
}

# -----------------------------------------------------------------------------
# check_diff_rules (Layer 2)
# -----------------------------------------------------------------------------
# Args:
#   $1 diff_file        — path to unified diff
#   $2 framework        — "playwright" | "cypress" | "jest" | "unknown"
#   $3 max_multiplier   — float; ratio new/old timeout beyond which we reject
# Echoes: JSON `{"decision": "allowed"}` or rejection record.
check_diff_rules() {
    local diff_file="${1:-}"
    local framework="${2:-unknown}"
    local max_multiplier="${3:-1.5}"

    if ! command -v jq >/dev/null 2>&1; then
        jq_fallback_reject "scope_guard: jq not found on PATH"
        return 0
    fi

    # ---- Rule 6 (pre-check): symlink creation/deletion ----
    # New file with mode 120000 = symlink creation; deleted file mode 120000 = symlink removal.
    # Detect via explicit "new file mode 120000" / "deleted file mode 120000" headers.
    local symlink_line
    symlink_line=$(awk '
        /^new file mode 120000/ { print; exit }
        /^deleted file mode 120000/ { print; exit }
    ' "$diff_file")
    if [ -n "$symlink_line" ]; then
        jq -n \
            --arg reason "Fix contains symlink creation/deletion (line: '${symlink_line}')" \
            --arg line "$symlink_line" \
            '{decision: "rejected", reason: $reason, rule: "rule6_symlink", violating_lines: [$line]}'
        return 0
    fi

    # ---- Rule 4: spec.md / acceptance-criteria.md path modifications ----
    # File paths appearing in diff headers must not be spec.md or acceptance-criteria.md.
    local spec_hit
    spec_hit=$(_extract_diff_paths "$diff_file" | awk '
        /spec\.md$/ { print; exit }
        /acceptance-criteria\.md$/ { print; exit }
    ')
    if [ -n "$spec_hit" ]; then
        jq -n \
            --arg reason "Fix would modify specification or acceptance criteria (path: '${spec_hit}')" \
            --arg line "$spec_hit" \
            '{decision: "rejected", reason: $reason, rule: "rule4_spec_modification", violating_lines: [$line]}'
        return 0
    fi

    # ---- Scan added lines (prefix `+` excluding `+++`) and removed lines (`-` excluding `---`) ----
    # Rule 1 (assertion), Rule 2 (skip/delete), Rule 3 (timeout multiplier).

    # Rule 1: assertion modification on added lines.
    # NOTE: awk on macOS (BSD) does not support \b word-boundary. We emulate it
    # with a (start-of-line|non-word-char) prefix group. Prepend a sentinel
    # non-word char to avoid missing matches at column 0.
    local r1_hit
    r1_hit=$(awk '
        /^\+\+\+/ { next }
        /^\+/ {
            line = substr($0, 2)
            probe = " " line
            if (match(probe, /[^a-zA-Z0-9_]expect[[:space:]]*\(/) \
                || match(probe, /[^a-zA-Z0-9_]assert[[:space:]]*\(/) \
                || match(probe, /[^a-zA-Z0-9_]assertEquals[[:space:]]*\(/) \
                || match(probe, /[^a-zA-Z0-9_]assertTrue[[:space:]]*\(/) \
                || match(probe, /[^a-zA-Z0-9_]assertFalse[[:space:]]*\(/) \
                || match(probe, /[^a-zA-Z0-9_]should\./) \
                || match(probe, /[^a-zA-Z0-9_]shouldBe/) \
                || match(probe, /[^a-zA-Z0-9_]shouldEqual/)) {
                print line
                exit
            }
        }
    ' "$diff_file")
    if [ -n "$r1_hit" ]; then
        jq -n \
            --arg reason "Fix would modify assertion (line: '${r1_hit}')" \
            --arg line "$r1_hit" \
            '{decision: "rejected", reason: $reason, rule: "rule1_assertion", violating_lines: [$line]}'
        return 0
    fi

    # Rule 2a: added `.skip` / `xit`/`xtest`/`xdescribe` declarations.
    local r2a_hit
    r2a_hit=$(awk '
        /^\+\+\+/ { next }
        /^\+/ {
            line = substr($0, 2)
            probe = " " line
            if (match(probe, /[^a-zA-Z0-9_](it|test|describe)\.skip[[:space:]]*\(/) \
                || match(probe, /[^a-zA-Z0-9_](xit|xtest|xdescribe)[[:space:]]*\(/)) {
                print line
                exit
            }
        }
    ' "$diff_file")
    if [ -n "$r2a_hit" ]; then
        jq -n \
            --arg reason "Fix would skip or delete test (line: '${r2a_hit}')" \
            --arg line "$r2a_hit" \
            '{decision: "rejected", reason: $reason, rule: "rule2_test_skip", violating_lines: [$line]}'
        return 0
    fi

    # Rule 2b: removal of test declarations via `^-` lines containing `it|test|describe (`.
    # Exclude lines where the removed test declaration is CONVERTED (paired with a
    # corresponding `+` line keeping the declaration). The pattern we reject:
    # a `-` line with `it|test|describe (` that has no matching retained/skipped form.
    # Simpler & contract-aligned: any `-` containing an active test-declaration call
    # represents a removal candidate. (False positives on `it.skip -> it` renaming
    # are an acceptable conservative bias.)
    local r2b_hit
    r2b_hit=$(awk '
        /^---/ { next }
        /^-/ {
            line = substr($0, 2)
            probe = " " line
            if (match(probe, /[^a-zA-Z0-9_](it|test|describe)[[:space:]]*\(/)) {
                print line
                exit
            }
        }
    ' "$diff_file")
    if [ -n "$r2b_hit" ]; then
        jq -n \
            --arg reason "Fix would skip or delete test (line: '${r2b_hit}')" \
            --arg line "$r2b_hit" \
            '{decision: "rejected", reason: $reason, rule: "rule2_test_deletion", violating_lines: [$line]}'
        return 0
    fi

    # Rule 3: timeout multiplier enforcement. Per-framework regex sets.
    # Algorithm: pair `^-` and `^+` lines within the same hunk. For each pair
    # where both match a framework timeout pattern, extract numeric values and
    # compute new/old ratio. Reject if ratio > max_multiplier.
    # Pure-addition (new timeout with no removed counterpart) also rejects.
    local r3_result
    r3_result=$(_check_timeouts "$diff_file" "$framework" "$max_multiplier")
    if [ -n "$r3_result" ]; then
        # _check_timeouts echoes: "RATIO|LINE" on reject, empty on accept.
        # Special marker "ADDITION|LINE" for pure-addition case.
        local kind line ratio reason
        kind=$(printf '%s' "$r3_result" | awk -F'|' '{print $1}')
        line=$(printf '%s' "$r3_result" | awk -F'|' '{ $1=""; sub(/^[ \t]*/,""); print }')
        if [ "$kind" = "ADDITION" ]; then
            reason="Timeout added where none existed; benefits from review (line: '${line}')"
        else
            ratio="$kind"
            reason="Timeout increased by ${ratio}x, exceeds max multiplier ${max_multiplier} (line: '${line}')"
        fi
        jq -n \
            --arg reason "$reason" \
            --arg line "$line" \
            '{decision: "rejected", reason: $reason, rule: "rule3_timeout", violating_lines: [$line]}'
        return 0
    fi

    # All rules passed.
    jq -n '{decision: "allowed"}'
    return 0
}

# -----------------------------------------------------------------------------
# _check_timeouts
# -----------------------------------------------------------------------------
# Scan diff for timeout changes under the active framework.
# Echoes "RATIO|LINE" on reject (ratio > multiplier) or "ADDITION|LINE" when
# a timeout is added where none existed. Echoes empty string on accept.
#
# Strategy (per framework):
#   - Enumerate candidate `^-` lines with a timeout number.
#   - For each hunk, find the corresponding `^+` line with a matching pattern.
#   - Compute new/old; compare to multiplier via awk.
_check_timeouts() {
    local diff_file="${1:-}"
    local framework="${2:-unknown}"
    local max_multiplier="${3:-1.5}"

    # Framework -> awk regex (used to extract numeric timeout values).
    # Patterns MUST contain a single capturing-group-equivalent via match()+RSTART/RLENGTH.
    # We keep them simple: find "timeout: N" and "setTimeout(N)" as the two dominant shapes,
    # plus positional-3rd-arg for Jest.
    local tmp_old tmp_new
    tmp_old=$(mktemp 2>/dev/null || echo "/tmp/sg_old_$$")
    tmp_new=$(mktemp 2>/dev/null || echo "/tmp/sg_new_$$")

    # Extract (line_no, number, line_text) from `^-` lines matching any timeout pattern.
    awk -v fw="$framework" '
        BEGIN {
            # Dominant patterns — framework-agnostic in shape; framework only affects
            # which APIs we trust to be timeout-bearing. Conservative fallback: any
            # timeout-like identifier for unknown framework.
        }
        /^---/ { next }
        /^-/ {
            line = substr($0, 2)
            n = -1
            which = ""
            # Playwright: test.setTimeout(N)
            if (match(line, /test\.setTimeout[[:space:]]*\([[:space:]]*[0-9]+[[:space:]]*\)/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) {
                    n = substr(s, RSTART, RLENGTH) + 0
                    which = "setTimeout"
                }
            }
            # Jest/Vitest: jest.setTimeout(N) / vi.setConfig({testTimeout:N})
            else if (match(line, /jest\.setTimeout[[:space:]]*\([[:space:]]*[0-9]+[[:space:]]*\)/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) {
                    n = substr(s, RSTART, RLENGTH) + 0
                    which = "jestSetTimeout"
                }
            }
            else if (match(line, /testTimeout[[:space:]]*:[[:space:]]*[0-9]+/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) {
                    n = substr(s, RSTART, RLENGTH) + 0
                    which = "testTimeout"
                }
            }
            # Cypress: Cypress.config("defaultCommandTimeout", N)
            else if (match(line, /Cypress\.config[[:space:]]*\([^)]*defaultCommandTimeout[^)]*,[[:space:]]*[0-9]+[[:space:]]*\)/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /,[[:space:]]*[0-9]+/)) {
                    num_s = substr(s, RSTART, RLENGTH)
                    if (match(num_s, /[0-9]+/)) {
                        n = substr(num_s, RSTART, RLENGTH) + 0
                        which = "defaultCommandTimeout"
                    }
                }
            }
            # Generic object-literal: { timeout: N }  (Playwright locator opts, Cypress command opts)
            else if (match(line, /timeout[[:space:]]*:[[:space:]]*[0-9]+/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) {
                    n = substr(s, RSTART, RLENGTH) + 0
                    which = "timeoutOpt"
                }
            }
            # Unknown-framework fallback: broad identifier match.
            else if (fw == "unknown") {
                if (match(line, /[tT]imeout[[:space:]]*[=:][[:space:]]*[0-9]+/)) {
                    s = substr(line, RSTART, RLENGTH)
                    if (match(s, /[0-9]+/)) {
                        n = substr(s, RSTART, RLENGTH) + 0
                        which = "fallback"
                    }
                }
            }
            if (n >= 0) {
                printf "%d\t%s\t%s\n", n, which, line
            }
        }
    ' "$diff_file" > "$tmp_old"

    # Same extraction for `^+` lines.
    awk -v fw="$framework" '
        /^\+\+\+/ { next }
        /^\+/ {
            line = substr($0, 2)
            n = -1
            which = ""
            if (match(line, /test\.setTimeout[[:space:]]*\([[:space:]]*[0-9]+[[:space:]]*\)/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) { n = substr(s, RSTART, RLENGTH) + 0; which = "setTimeout" }
            }
            else if (match(line, /jest\.setTimeout[[:space:]]*\([[:space:]]*[0-9]+[[:space:]]*\)/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) { n = substr(s, RSTART, RLENGTH) + 0; which = "jestSetTimeout" }
            }
            else if (match(line, /testTimeout[[:space:]]*:[[:space:]]*[0-9]+/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) { n = substr(s, RSTART, RLENGTH) + 0; which = "testTimeout" }
            }
            else if (match(line, /Cypress\.config[[:space:]]*\([^)]*defaultCommandTimeout[^)]*,[[:space:]]*[0-9]+[[:space:]]*\)/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /,[[:space:]]*[0-9]+/)) {
                    num_s = substr(s, RSTART, RLENGTH)
                    if (match(num_s, /[0-9]+/)) { n = substr(num_s, RSTART, RLENGTH) + 0; which = "defaultCommandTimeout" }
                }
            }
            else if (match(line, /timeout[[:space:]]*:[[:space:]]*[0-9]+/)) {
                s = substr(line, RSTART, RLENGTH)
                if (match(s, /[0-9]+/)) { n = substr(s, RSTART, RLENGTH) + 0; which = "timeoutOpt" }
            }
            else if (fw == "unknown") {
                if (match(line, /[tT]imeout[[:space:]]*[=:][[:space:]]*[0-9]+/)) {
                    s = substr(line, RSTART, RLENGTH)
                    if (match(s, /[0-9]+/)) { n = substr(s, RSTART, RLENGTH) + 0; which = "fallback" }
                }
            }
            if (n >= 0) {
                printf "%d\t%s\t%s\n", n, which, line
            }
        }
    ' "$diff_file" > "$tmp_new"

    # If there are no `^+` timeout lines → nothing to check, accept.
    if [ ! -s "$tmp_new" ]; then
        rm -f "$tmp_old" "$tmp_new"
        echo ""
        return 0
    fi

    # Pair each new-line with first old-line of the same `which`.
    # If no matching old-line → pure addition → reject.
    local result=""
    local new_n new_which new_line old_n old_which
    while IFS=$'\t' read -r new_n new_which new_line; do
        [ -z "$new_n" ] && continue
        # Look for first old-line with same `which`.
        local old_match
        old_match=$(awk -F'\t' -v w="$new_which" '$2 == w { print; exit }' "$tmp_old")
        if [ -z "$old_match" ]; then
            result="ADDITION|${new_line}"
            break
        fi
        old_n=$(printf '%s' "$old_match" | awk -F'\t' '{print $1}')
        # Compare ratio via awk (floating-point safe).
        local verdict ratio_str
        verdict=$(awk -v n="$new_n" -v o="$old_n" -v m="$max_multiplier" '
            BEGIN {
                if (o == 0) { printf "REJECT %s", "inf"; exit }
                r = n / o
                if (r > m) { printf "REJECT %.2f", r } else { printf "OK %.2f", r }
            }
        ')
        ratio_str=$(printf '%s' "$verdict" | awk '{print $2}')
        case "$verdict" in
            REJECT*)
                result="${ratio_str}|${new_line}"
                break
                ;;
        esac
    done < "$tmp_new"

    rm -f "$tmp_old" "$tmp_new"
    echo "$result"
    return 0
}

# -----------------------------------------------------------------------------
# jq_fallback_reject
# -----------------------------------------------------------------------------
# Used when `jq` is unavailable — emit a minimal JSON rejection by hand.
jq_fallback_reject() {
    local reason="${1:-unknown error}"
    printf '{"decision":"rejected","reason":"%s","violating_lines":[]}\n' "$reason"
}

# -----------------------------------------------------------------------------
# evaluate_scope_guard
# -----------------------------------------------------------------------------
# Args:
#   $1 diff_input        — unified diff as a file path OR raw diff content string
#                          (multi-line strings are auto-materialized to a temp file);
#                          "/dev/stdin" or "-" reads from stdin
#   $2 test_paths_json   — JSON array of glob patterns (from get_test_paths)
#   $3 framework         — "playwright" | "cypress" | "jest" | "unknown"
#   $4 max_multiplier    — float (default 1.5)
#
# Echoes: JSON decision record matching contracts/scope-guard-decision.md.
# Always returns 0. Caller parses `.decision`.
evaluate_scope_guard() {
    local diff_input="${1:-}"
    local test_paths_json="${2:-$AOD_SCOPE_GUARD_DEFAULT_TEST_PATHS}"
    local framework="${3:-unknown}"
    local max_multiplier="${4:-1.5}"
    local diff_file="$diff_input"

    # Classify input:
    #   - "/dev/stdin" or "-" or empty → read from stdin
    #   - Existing readable file → use as-is
    #   - Otherwise treat as raw diff content and materialize to a temp file
    local owned_tmp=""
    if [ "$diff_input" = "/dev/stdin" ] || [ "$diff_input" = "-" ] || [ -z "$diff_input" ]; then
        owned_tmp=$(mktemp 2>/dev/null || echo "/tmp/sg_stdin_$$")
        cat > "$owned_tmp"
        diff_file="$owned_tmp"
    elif [ ! -f "$diff_input" ] || [ ! -r "$diff_input" ]; then
        # Raw content string passed as argument.
        owned_tmp=$(mktemp 2>/dev/null || echo "/tmp/sg_content_$$")
        printf '%s' "$diff_input" > "$owned_tmp"
        diff_file="$owned_tmp"
    fi

    # Pre-check: balanced-diff validation (T053).
    local balance_err
    balance_err=$(_check_balanced_diff "$diff_file")
    if [ -n "$balance_err" ]; then
        if command -v jq >/dev/null 2>&1; then
            jq -n \
                --arg reason "$balance_err" \
                '{decision: "rejected", reason: $reason, rule: "malformed_diff", violating_lines: []}'
        else
            jq_fallback_reject "$balance_err"
        fi
        [ -n "$owned_tmp" ] && rm -f "$owned_tmp"
        return 0
    fi

    # Layer 1: path check.
    local l1_out l1_decision
    l1_out=$(check_diff_paths "$diff_file" "$test_paths_json")
    l1_decision=$(printf '%s' "$l1_out" | jq -r '.decision' 2>/dev/null)
    if [ "$l1_decision" = "rejected" ]; then
        printf '%s\n' "$l1_out"
        [ -n "$owned_tmp" ] && rm -f "$owned_tmp"
        return 0
    fi

    # Layer 2: content rules.
    local l2_out
    l2_out=$(check_diff_rules "$diff_file" "$framework" "$max_multiplier")
    printf '%s\n' "$l2_out"

    [ -n "$owned_tmp" ] && rm -f "$owned_tmp"
    return 0
}

# -----------------------------------------------------------------------------
# get_test_paths (T055)
# -----------------------------------------------------------------------------
# Reads active stack pack's STACK.md for the `test_paths:` YAML array under
# Section 7's aod-test-contract fence. Falls back to defaults when the pack
# is absent or the key is missing.
#
# Args:
#   $1 pack_stack_md — optional path to STACK.md; when omitted, auto-resolve
#                      via .aod/stack-active.json -> stacks/<pack>/STACK.md
#
# Echoes: JSON array of glob patterns.
get_test_paths() {
    local pack_stack_md="${1:-}"

    if [ -z "$pack_stack_md" ]; then
        # Auto-resolve active pack.
        local active_json="${AOD_STACK_ACTIVE_JSON:-.aod/stack-active.json}"
        if [ -f "$active_json" ] && command -v jq >/dev/null 2>&1; then
            local pack
            pack=$(jq -r '.pack // .active // empty' "$active_json" 2>/dev/null)
            if [ -n "$pack" ] && [ -f "stacks/${pack}/STACK.md" ]; then
                pack_stack_md="stacks/${pack}/STACK.md"
            fi
        fi
    fi

    # Pack absent — return defaults.
    if [ -z "$pack_stack_md" ] || [ ! -r "$pack_stack_md" ]; then
        printf '%s\n' "$AOD_SCOPE_GUARD_DEFAULT_TEST_PATHS"
        return 0
    fi

    # Extract YAML block between aod-test-contract sentinels.
    local yaml_block
    yaml_block=$(awk '/<!-- BEGIN: aod-test-contract -->/,/<!-- END: aod-test-contract -->/' "$pack_stack_md" \
        | sed -n '/^```yaml/,/^```$/p' \
        | sed '1d;$d')

    # Parse test_paths: array via awk/sed (bash 3.2 compatible).
    local paths
    paths=$(printf '%s\n' "$yaml_block" | awk '
        /^test_paths:/ { in_block=1; next }
        in_block && /^[[:space:]]+-[[:space:]]/ {
            sub(/^[[:space:]]+-[[:space:]]*/, "")
            gsub(/^["'\'']|["'\'']$/, "")
            print
            next
        }
        in_block && /^[^[:space:]]/ { in_block=0 }
    ')

    if [ -z "$paths" ]; then
        # Key absent in pack — return defaults.
        printf '%s\n' "$AOD_SCOPE_GUARD_DEFAULT_TEST_PATHS"
        return 0
    fi

    # Convert line-list to JSON array via jq (or hand-roll fallback).
    if command -v jq >/dev/null 2>&1; then
        printf '%s\n' "$paths" | jq -R -s -c 'split("\n") | map(select(length > 0))'
    else
        # Minimal fallback: wrap each line in quotes, comma-join.
        local first=1
        printf '['
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            if [ "$first" -eq 1 ]; then
                first=0
            else
                printf ','
            fi
            # Naively escape double-quotes.
            local esc
            esc=$(printf '%s' "$line" | sed 's/"/\\"/g')
            printf '"%s"' "$esc"
        done <<EOF
$paths
EOF
        printf ']\n'
    fi
    return 0
}
