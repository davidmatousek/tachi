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
#       Reads one line of stdin byte-by-byte (bash 3.2 `read -r -n 1 -d ""`)
#       so NUL bytes can be detected BEFORE bash truncates the value, then
#       validates against a rejection ladder for NUL bytes, control
#       characters, and over-length input. Re-prompts up to 3 times; exits
#       non-zero on the 3rd consecutive rejection.
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
#   1. NUL byte (0x00)                       → "NUL byte not allowed"
#   2. Any 0x01–0x1F or 0x7F control char    → "control character not allowed"
#   3. Length > max_len                      → "over-length (max N chars)"
#
# Embedded LF cannot occur — the byte-by-byte loop breaks on the first LF,
# leaving the rest of stdin (including extra LFs) intact for the next prompt.
# This means input is implicitly single-line by construction.
#
# Empty input is accepted (length 0 ≤ max_len; no character classes match).
# The caller is responsible for downstream domain-specific empty-check rules
# (e.g., GITHUB_REPO defaults empty input to PROJECT_NAME).
#
# Implementation notes:
#   - Uses `read -r -n 1 -d ""` to read exactly one byte at a time. NUL is
#     inferred from a successful read whose target var is empty (bash truncates
#     the variable assignment at NUL). LF is detected explicitly and breaks
#     the read loop without being appended to the answer.
#   - Uses `IFS=` on the read so leading/trailing whitespace are preserved
#     verbatim per FR-005 cases 7-8.
#   - Uses `printf -v` (NOT `eval`) for safe variable assignment; bash 3.2
#     supports `printf -v` for scalars.
#   - Prompt and rejection messages both emit to stderr (matching `read -p`
#     semantics for piped invocations — prompt never contaminates stdout).
#   - Does NOT use `head -n 1` to a tmpfile: macOS BSD `head` over-reads on
#     a pipe (consumes more than one line into its buffer), which would
#     discard subsequent prompt input on a piped stdin.
#
# Arguments:
#   $1 — prompt string (non-empty; written verbatim to stdout)
#   $2 — bash variable name to populate on success (must match
#        [A-Za-z_][A-Za-z0-9_]*)
#   $3 — max accepted character length (positive integer)
#
# Pre-conditions:
#   - Caller is bash 3.2+ with stdin (terminal or pipe).
#   - $var_name does not collide with internal locals (prompt, var_name,
#     max_len, answer, attempt, reason, nul_seen, byte).
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
    local nul_seen
    local byte

    if [ -z "$prompt" ] || [ -z "$var_name" ] || [ "$max_len" -le 0 ] 2>/dev/null; then
        echo "[init] FATAL: aod_init_read_validated requires <prompt> <var_name> <max_len>" >&2
        exit 1
    fi

    while [ "$attempt" -lt 3 ]; do
        reason=""
        answer=""
        nul_seen=0

        # Print prompt to stderr (matching `read -p` semantics: prompt goes
        # to the controlling terminal, not stdout, so it never contaminates
        # piped output).
        printf '%s' "$prompt" >&2

        # Read one line byte-by-byte so we can detect NUL bytes BEFORE bash
        # `read` truncates the string. Bash scalar strings CANNOT contain
        # NUL — when `read` encounters one, the variable is set to the
        # bytes BEFORE the NUL (so a 1-byte read of NUL produces an empty
        # string with read returning success). We exploit that: any 1-byte
        # `read` whose target var has length 0 AND whose return code was 0
        # (not EOF) must have consumed a NUL.
        #
        # Why byte-by-byte instead of `head -n 1` to a tmpfile + tr-count?
        # macOS BSD `head -n 1` over-reads on a pipe (consumes more than
        # one line into its internal buffer), which would discard
        # subsequent prompt input on a piped stdin. `read -r -n 1 -d ""`
        # is bash-builtin (bash 3.2+) and reads exactly one byte at a
        # time, leaving the rest of stdin intact for the next prompt.
        # `IFS=` preserves leading/trailing whitespace per FR-005 cases
        # 7-8. The `-d ""` empties the read delimiter so that LF is
        # treated as just another byte we have to recognize and break on
        # explicitly (otherwise `read` would strip the trailing LF and
        # we'd lose the loop-exit signal).
        #
        # Compatibility: `read -n N` requires bash 3.2 (have it); `-d ""`
        # is bash 3.0+. POSIX shells (dash) lack `-n`, but init-input.sh
        # is bash-only per shebang.
        while IFS= read -r -n 1 -d '' byte; do
            # Empty $byte after a successful read means the underlying
            # byte was NUL (bash truncated to "").
            if [ -z "$byte" ]; then
                nul_seen=1
                continue
            fi
            # End of line: stop appending; leave rest of stdin for the
            # next prompt.
            if [ "$byte" = $'\n' ]; then
                break
            fi
            answer="$answer$byte"
            # Safety cap: if input exceeds 4 * max_len bytes (UTF-8 worst
            # case for max_len characters), stop reading to bound memory.
            # Length check below will reject. Avoids unbounded reads on a
            # malicious stdin that never sends LF.
            if [ "${#answer}" -gt $((max_len * 4 + 16)) ]; then
                break
            fi
        done
        # If `read` returned non-zero (EOF before LF), the while-condition
        # exits the loop with whatever we accumulated. An empty answer at
        # EOF is valid (length 0; no character classes match).

        # Order-sensitive ladder: NUL takes precedence over cntrl-class
        # so the test gets the specific "NUL byte" reason class.
        if [ "$nul_seen" -eq 1 ]; then
            reason="NUL byte not allowed"
        fi

        if [ -z "$reason" ]; then
            # POSIX cntrl class catches 0x01-0x1F + 0x7F. NUL is already
            # caught above. Bracketed to avoid parameter-expansion
            # surprises in [[ ]] regex.
            if [[ "$answer" =~ [[:cntrl:]] ]]; then
                reason="control character not allowed"
            fi
        fi

        # F-2 BLP-02 Wave 2 amendment per B-2 Path R-2 (T032): reject
        # shell metacharacters `$`, `\`, backtick at the prompt boundary.
        # This is the UPSTREAM defense that lets template-substitute.sh
        # remove its writer escape pass (T031): if the prompt rejects
        # these characters, the writer never sees them and the
        # snapshot file is bash-sourceable without escape.
        # CHANGELOG migration guidance for adopters whose existing
        # PROJECT_NAME / PROJECT_DESCRIPTION contains these chars lands
        # at T053. Order matters: this MUST land BEFORE the over-length
        # check so the more-specific class is named first.
        if [ -z "$reason" ]; then
            if [[ "$answer" =~ [\$\\\`] ]]; then
                reason="metachar (\$, \\, backtick) not allowed"
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
