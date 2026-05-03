# LIBRARY — source before calling functions
# Feature 139 /aod.deliver flag parsing + validation.
# Handles two flags: --no-tests=<reason> (opt-out, reason 10-500 chars)
# and --require-tests (deprecated, silent no-op with stderr notice).
# Serves tasks T008 (core parser + validator) and T020 (deprecation notice format).
# Canonical contracts: specs/139-delivery-verified-not-documented/spec.md US-1 + US-2.
#
# Public functions:
#   parse_no_tests           — scan argv, set AOD_* globals (no validation)
#   validate_reason_length   — length-check the captured reason (10-500)
#   deprecation_notice       — emit stderr deprecation notice (self-discovers
#                              version from .aod/VERSION or git tag)
#   reject_flag_conflict     — reject --no-tests + --require-tests combination
#
# Side-effect globals (AOD_ prefix to avoid collision):
#   AOD_NO_TESTS_FOUND        true|false
#   AOD_NO_TESTS_REASON       captured reason ("" if flag absent or empty)
#   AOD_REQUIRE_TESTS_FOUND   true|false
#
# Bash 3.2 compatible: no `declare -A`, no `${var,,}`, no `readarray`, no `|&`.

# Parse flags from argv. Sets AOD_NO_TESTS_FOUND / AOD_NO_TESTS_REASON /
# AOD_REQUIRE_TESTS_FOUND. Accepts both `--no-tests=<reason>` (equals form,
# preferred) and `--no-tests <reason>` (space form). Does NOT validate reason
# length — call validate_reason_length separately. Does NOT reject conflict —
# call reject_flag_conflict after parsing.
# Args: all remaining argv (typical call: parse_no_tests "$@")
parse_no_tests() {
    # Reset globals on every invocation.
    AOD_NO_TESTS_FOUND=false
    AOD_NO_TESTS_REASON=""
    AOD_REQUIRE_TESTS_FOUND=false

    local arg
    local next_is_reason=false

    while [ $# -gt 0 ]; do
        arg="$1"

        if [ "$next_is_reason" = true ]; then
            # Previous arg was bare --no-tests; capture this positional reason.
            AOD_NO_TESTS_REASON="$arg"
            next_is_reason=false
            shift
            continue
        fi

        case "$arg" in
            --no-tests=*)
                # Equals form: strip the --no-tests= prefix, keep everything after.
                AOD_NO_TESTS_FOUND=true
                AOD_NO_TESTS_REASON="${arg#*=}"
                ;;
            --no-tests)
                # Space form: mark found, capture next argv as reason.
                AOD_NO_TESTS_FOUND=true
                next_is_reason=true
                ;;
            --require-tests)
                AOD_REQUIRE_TESTS_FOUND=true
                ;;
            *)
                # Other flags are parsed by other parts of the skill.
                ;;
        esac
        shift
    done

    return 0
}

# Validate that a reason string is between 10 and 500 characters inclusive.
# Args:
#   $1 reason
# Returns:
#   0 if 10 <= length <= 500
#   1 otherwise (stderr: descriptive error with observed length)
validate_reason_length() {
    local reason="${1:-}"
    local len=${#reason}

    if [ "$len" -lt 10 ] || [ "$len" -gt 500 ]; then
        echo "Error: --no-tests reason must be 10-500 chars (got ${len})" >&2
        return 1
    fi
    return 0
}

# Resolve the semver "core" (major.minor.patch) from a raw version string.
# Strips a leading "v" and any pre-release/build suffix (everything from the
# first "-" or "+" after the numeric triple). Echoes the core, or the empty
# string if nothing numeric could be extracted.
# Example: "v2.0.0-pre-speckit-removal" -> "2.0.0"; "2.1.3" -> "2.1.3".
# Bash 3.2 compatible — uses parameter expansion only.
_semver_core() {
    local raw="${1:-}"
    # Strip leading "v".
    raw="${raw#v}"
    # Strip the first "-<suffix>" or "+<suffix>" (pre-release / build metadata).
    raw="${raw%%-*}"
    raw="${raw%%+*}"
    printf '%s' "$raw"
}

# Bump a semver core by N minor versions. Echoes the bumped core.
# Args:
#   $1 core   e.g., "2.0.0"
#   $2 bump   e.g., 2
# Returns 0 on success, 1 if the core is not a valid M.m.p triple.
_semver_bump_minor() {
    local core="${1:-}"
    local bump="${2:-0}"
    local major minor patch

    # Validate M.m.p shape with three numeric parts.
    case "$core" in
        [0-9]*.[0-9]*.[0-9]*) ;;
        *) return 1 ;;
    esac

    major="${core%%.*}"
    local rest="${core#*.}"
    minor="${rest%%.*}"
    patch="${rest#*.}"

    minor=$((minor + bump))
    printf '%s.%s.%s' "$major" "$minor" "$patch"
    return 0
}

# Emit a stderr deprecation notice for the --require-tests flag.
# Self-discovers the current and removal versions from a single source of
# truth: (1) `.aod/VERSION` file if present, (2) nearest git tag by
# sort=-v:refname, (3) fallback "unknown" / "TBD". The removal version is
# always current + 2 minor versions (e.g., 2.0.0 -> 2.2.0).
# No args. Returns 0 always.
deprecation_notice() {
    local current=""
    local removal=""
    local raw=""
    local core=""
    local bumped=""

    # Source-of-truth precedence: VERSION file > git tag > unknown.
    if [ -f ".aod/VERSION" ]; then
        raw=$(head -n1 .aod/VERSION 2>/dev/null | tr -d '[:space:]')
    fi
    if [ -z "$raw" ] && command -v git >/dev/null 2>&1; then
        raw=$(git tag --list --sort=-v:refname 2>/dev/null | head -n1)
    fi

    if [ -n "$raw" ]; then
        core=$(_semver_core "$raw")
        if [ -n "$core" ]; then
            bumped=$(_semver_bump_minor "$core" 2) || bumped=""
        fi
    fi

    if [ -n "$core" ] && [ -n "$bumped" ]; then
        current="v${core}"
        removal="v${bumped}"
    else
        current="unknown"
        removal="TBD"
    fi

    echo "[deprecated] --require-tests is now default (${current}); flag accepted but has no effect. Will be removed in ${removal}." >&2
    return 0
}

# Reject the conflicting --no-tests + --require-tests combination.
# Reads AOD_NO_TESTS_FOUND + AOD_REQUIRE_TESTS_FOUND set by parse_no_tests.
# Returns:
#   0 if no conflict (at most one of the two flags present)
#   2 if both present (stderr: conflict error; matches PRD 130 flag-error code)
reject_flag_conflict() {
    if [ "${AOD_NO_TESTS_FOUND:-false}" = true ] && [ "${AOD_REQUIRE_TESTS_FOUND:-false}" = true ]; then
        echo "Error: --no-tests and --require-tests cannot be combined" >&2
        return 2
    fi
    return 0
}
