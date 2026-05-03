#!/usr/bin/env bash
# =============================================================================
# init-input.sh — Interactive prompt input validation helper
# =============================================================================
# Part of feature 248 (substitution surface hardening, BLP-02 Wave 1).
#
# Bash 3.2 compatible. Sourced by scripts/init.sh.
#
# Public function (prefix: aod_init_):
#   - aod_init_read_validated <prompt> <var_name> <max_len>
#       Wraps `read -r -p` with a rejection ladder for newlines, NUL bytes,
#       control characters, and over-length input. Re-prompts up to 3 times;
#       exits non-zero on the 3rd consecutive rejection.
#
# See contracts/init-input-helper-contract.md for full behavior contract.
# See ADR-038 §Decision for the validation triplet pattern (regex-validate →
# reject-on-mismatch → `printf -v` assignment).
#
# Compatibility constraints (NFR-001):
#   - bash 3.2.57 (macOS default) and bash 5.x (Linux CI)
#   - No associative arrays, no `mapfile`, no `${var,,}` lowercase expansion
#   - No `&>` redirection
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_INIT_INPUT_SH_SOURCED:-}" ]; then
  return 0
fi
readonly AOD_INIT_INPUT_SH_SOURCED=1

# -----------------------------------------------------------------------------
# aod_init_read_validated <prompt> <var_name> <max_len>
# -----------------------------------------------------------------------------
# Read user input from an interactive prompt and validate against a rejection
# ladder. On success, set the variable named by $var_name in caller scope to
# the validated answer. On 3 consecutive rejections, exit 1 with a FATAL
# message.
#
# Rejection ladder (in order):
#   1. Embedded literal newline character    → "newline not allowed"
#   2. NUL byte (0x00)                       → "NUL byte not allowed"
#   3. Any 0x00–0x1F control character        → "control character not allowed"
#   4. Length > max_len                      → "over-length (max N chars)"
#
# Empty input is accepted (length 0 ≤ max_len; no character classes match).
# The caller is responsible for downstream domain-specific empty-check rules
# (e.g., GITHUB_REPO defaults empty input to PROJECT_NAME).
#
# Implementation notes:
#   - Uses `read -r` to disable backslash continuation; preserves literal
#     backslashes in input (FR-005 requires `Cats\Dogs` etc. survive).
#   - Uses `printf -v` (NOT `eval`) for safe variable assignment; bash 3.2
#     supports `printf -v` for scalars.
#   - Reasons are emitted to stderr; the prompt itself is emitted to stdout
#     by `read -r -p`. FATAL message is also stderr.
#
# Arguments:
#   $1 — prompt string (non-empty; written verbatim to stdout)
#   $2 — bash variable name to populate on success (must match
#        [A-Za-z_][A-Za-z0-9_]*)
#   $3 — max accepted character length (positive integer)
#
# Pre-conditions:
#   - Caller is interactive bash 3.2+ (terminal attached to stdin).
#   - $var_name does not collide with internal locals (prompt, var_name,
#     max_len, answer, attempt, reason).
#   - Function is sourced (not exec'd in subshell) so `printf -v` writes to
#     caller scope.
#
# Return:
#   0 — input accepted; variable set
#   1 — 3 consecutive rejections; FATAL printed; SCRIPT EXITS via `exit 1`
#       (caller does NOT regain control on 3-strikes path; the calling
#       script terminates).
# -----------------------------------------------------------------------------
aod_init_read_validated() {
    local prompt="${1:-}"
    local var_name="${2:-}"
    local max_len="${3:-0}"
    local answer
    local attempt=0
    local reason

    if [ -z "$prompt" ] || [ -z "$var_name" ] || [ "$max_len" -le 0 ] 2>/dev/null; then
        echo "[init] FATAL: aod_init_read_validated requires <prompt> <var_name> <max_len>" >&2
        exit 1
    fi

    while [ "$attempt" -lt 3 ]; do
        # shellcheck disable=SC2162  # -r flag is set
        read -r -p "$prompt" answer

        reason=""
        # Order-sensitive ladder: newline check fires first with a specific
        # message; remaining control chars (0x01-0x1F, 0x7F) and NUL fall
        # through to the cntrl-class check below.
        #
        # Note on NUL: bash scalar strings CANNOT contain NUL bytes. If a
        # NUL was on the wire, bash truncates the string at the NUL during
        # `read`. We deliberately do NOT add an explicit `*$'\0'*` case
        # because $'\0' expands to a literal NUL which terminates the C
        # string of the case pattern, collapsing it to `**` and matching
        # all input. The cntrl-class check below catches any NUL that
        # somehow survives bash string semantics (defense-in-depth).
        case "$answer" in
            *$'\n'*)
                reason="newline not allowed"
                ;;
        esac

        if [ -z "$reason" ]; then
            # Use bash regex with POSIX cntrl class for control chars
            # (0x00–0x1F + 0x7F). Brackets the regex to avoid surprising
            # parameter-expansion interaction.
            if [[ "$answer" =~ [[:cntrl:]] ]]; then
                reason="control character not allowed"
            fi
        fi

        if [ -z "$reason" ] && [ "${#answer}" -gt "$max_len" ]; then
            reason="over-length (max $max_len chars)"
        fi

        if [ -z "$reason" ]; then
            # `printf -v` requires bash 3.1+; bash 3.2 supports it.
            # Quote the format string to ensure literal `%s` substitution.
            printf -v "$var_name" '%s' "$answer"
            return 0
        fi

        echo "[init] Input rejected: $reason; please re-enter." >&2
        attempt=$((attempt + 1))
    done

    echo "[init] FATAL: 3 consecutive invalid inputs for $var_name; aborting." >&2
    exit 1
}
