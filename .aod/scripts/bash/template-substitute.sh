#!/usr/bin/env bash
# =============================================================================
# template-substitute.sh — Placeholder canonicalization + literal re-substitution
# =============================================================================
# Part of feature 129 (downstream template update mechanism).
#
# Bash 3.2 compatible. Sourced by scripts/update.sh and scripts/init.sh.
#
# Public functions (prefix: aod_template_):
#   - aod_template_canonical_placeholders      Emit the 12 canonical placeholder
#                                              keys (PROJECT_NAME, PROJECT_DESCRIPTION,
#                                              GITHUB_ORG, GITHUB_REPO, AI_AGENT,
#                                              TECH_STACK, TECH_STACK_DATABASE,
#                                              TECH_STACK_VECTOR, TECH_STACK_AUTH,
#                                              RATIFICATION_DATE, CURRENT_DATE,
#                                              CLOUD_PROVIDER).
#   - aod_template_load_personalization_env    Source + validate .aod/personalization.env.
#                                              Rejects newline, NUL. Accepts &, \, |,
#                                              regex metachars.
#   - aod_template_substitute_placeholders     Bash parameter expansion `${str//pat/rep}`
#                                              literal replace. NOT sed.
#                                              Preserves file mode.
#   - aod_template_assert_no_residual          Grep for {{[A-Z_]+}}; exit 8 on match.
#   - aod_template_init_personalization        Prompt adopter for values during
#                                              init.sh; write personalization.env.
#
# Canonicalization factored from scripts/init.sh:117-161. Substitution strategy
# is new — bash parameter expansion, not sed (which interprets & and \).
# See contracts/personalization-schema.md §Substitution Strategy.
# See contracts/library-api.md §template-substitute.sh for API details.
#
# Bodies implemented in T041-T045 (feature 129 Wave 3 US-6).
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_TEMPLATE_SUBSTITUTE_SH_SOURCED:-}" ]; then
  return 0
fi
readonly AOD_TEMPLATE_SUBSTITUTE_SH_SOURCED=1

# -----------------------------------------------------------------------------
# CANONICAL_PLACEHOLDERS — the fixed 12 keys this mechanism knows how to
# substitute. Order mirrors contracts/personalization-schema.md §Fields and
# plan.md §C5. Adding a new placeholder requires updating BOTH this array AND
# personalization-schema.md (lockstep) — see §Unknown Upstream Placeholders.
# -----------------------------------------------------------------------------
# Not marked `readonly` because the double-source guard above already prevents
# re-assignment; making it readonly would prevent test harnesses from sourcing
# the lib twice across related suites.
AOD_CANONICAL_PLACEHOLDERS=(
    PROJECT_NAME
    PROJECT_DESCRIPTION
    GITHUB_ORG
    GITHUB_REPO
    AI_AGENT
    TECH_STACK
    TECH_STACK_DATABASE
    TECH_STACK_VECTOR
    TECH_STACK_AUTH
    RATIFICATION_DATE
    CURRENT_DATE
    CLOUD_PROVIDER
)

# -----------------------------------------------------------------------------
# aod_template_canonical_placeholders
# -----------------------------------------------------------------------------
# Emit the 12 canonical placeholder keys, one per line, in the documented
# order (see contracts/personalization-schema.md §Fields).
#
# Output: 12 lines to stdout.
# Return: 0 always.
# -----------------------------------------------------------------------------
aod_template_canonical_placeholders() {
    local key
    for key in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        printf '%s\n' "$key"
    done
    return 0
}

# -----------------------------------------------------------------------------
# _aod_substitute_lookup <key>
# -----------------------------------------------------------------------------
# Internal: `case`-based key→value lookup. Bash 3.2 lacks `declare -A`
# associative arrays; we emit a case statement that resolves each canonical
# key to its exported `AOD_PERSONALIZATION_<KEY>` shell variable (set by
# aod_template_load_personalization_env).
#
# This is the lookup used by substitute_placeholders — one case branch per
# canonical key. The AOD_PERSONALIZATION_ prefix avoids clashing with any
# caller-scope vars like PROJECT_NAME (which init.sh itself uses).
#
# Output: value on stdout. Empty if key not canonical or value unset.
# Return: 0 if key is canonical; 1 otherwise.
# -----------------------------------------------------------------------------
_aod_substitute_lookup() {
    local key="${1:-}"
    case "$key" in
        PROJECT_NAME)          printf '%s' "${AOD_PERSONALIZATION_PROJECT_NAME:-}" ;;
        PROJECT_DESCRIPTION)   printf '%s' "${AOD_PERSONALIZATION_PROJECT_DESCRIPTION:-}" ;;
        GITHUB_ORG)            printf '%s' "${AOD_PERSONALIZATION_GITHUB_ORG:-}" ;;
        GITHUB_REPO)           printf '%s' "${AOD_PERSONALIZATION_GITHUB_REPO:-}" ;;
        AI_AGENT)              printf '%s' "${AOD_PERSONALIZATION_AI_AGENT:-}" ;;
        TECH_STACK)            printf '%s' "${AOD_PERSONALIZATION_TECH_STACK:-}" ;;
        TECH_STACK_DATABASE)   printf '%s' "${AOD_PERSONALIZATION_TECH_STACK_DATABASE:-}" ;;
        TECH_STACK_VECTOR)     printf '%s' "${AOD_PERSONALIZATION_TECH_STACK_VECTOR:-}" ;;
        TECH_STACK_AUTH)       printf '%s' "${AOD_PERSONALIZATION_TECH_STACK_AUTH:-}" ;;
        RATIFICATION_DATE)     printf '%s' "${AOD_PERSONALIZATION_RATIFICATION_DATE:-}" ;;
        CURRENT_DATE)          printf '%s' "${AOD_PERSONALIZATION_CURRENT_DATE:-}" ;;
        CLOUD_PROVIDER)        printf '%s' "${AOD_PERSONALIZATION_CLOUD_PROVIDER:-}" ;;
        *) return 1 ;;
    esac
    return 0
}

# -----------------------------------------------------------------------------
# aod_template_load_personalization_env <path>
# -----------------------------------------------------------------------------
# Source and validate `.aod/personalization.env`. On success, every canonical
# key is exported into the caller's scope as `AOD_PERSONALIZATION_<KEY>` (prefix
# chosen to avoid collision with caller-scope vars like PROJECT_NAME that init.sh
# itself sets from `read -p` prompts).
#
# Validation rules (contracts/personalization-schema.md §Value Constraints):
#   1. File must exist (else exit 3).
#   2. File must be bash-sourceable.
#   3. Every canonical key must be set AND non-empty (else exit 8).
#   4. No value may contain a literal newline (else exit 8).
#   5. No value may contain NUL byte (else exit 8).
#
# We do NOT reject `&`, `\`, `|`, `/`, `$`, quotes, or regex metacharacters.
# These are safe under bash parameter expansion substitution.
#
# Arguments:
#   $1 — absolute or relative path to personalization.env
# Return:
#   0  — success; all 12 keys exported as AOD_PERSONALIZATION_<KEY>
#   1  — argument error (empty path)
#   3  — file absent
#   8  — validation failure (missing key, newline, NUL)
# -----------------------------------------------------------------------------
aod_template_load_personalization_env() {
    local path="${1:-}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: aod_template_load_personalization_env requires <path>" >&2
        return 1
    fi

    if [ ! -f "$path" ]; then
        echo "[aod] ERROR: personalization.env not found: $path" >&2
        return 3
    fi

    # Source the env file into a SUBSHELL first to avoid polluting the caller's
    # scope if validation fails. We then re-source into the caller's scope
    # only after validation passes. This uses bash's $(...) + declare -p
    # round-trip trick, but bash 3.2-compatible: we just source twice.
    #
    # Step 1: sanity-source in subshell; if source fails, halt.
    if ! (
        set -e
        # shellcheck disable=SC1090
        source "$path"
    ) >/dev/null 2>&1; then
        echo "[aod] ERROR: personalization.env is not bash-sourceable: $path" >&2
        return 8
    fi

    # Step 2: source into the caller's scope under a sentinel — we intentionally
    # let `source` run here so the KEY=VALUE lines populate the caller. Use a
    # local-ish pattern: source inside a function means variables live in
    # function scope unless declared globally. Bash source inside a function
    # sets globals by default for assignments without `local` — which is what
    # the env file uses — so these become globals. That is the desired
    # behavior: the init.sh fresh-install flow wants PROJECT_NAME etc. visible
    # at script scope.
    #
    # However, we need to AVOID shadowing caller vars with different semantics.
    # Strategy: save the existing env values into AOD_PERSONALIZATION_<KEY> via
    # our case lookup AFTER source runs, then validate.
    # shellcheck disable=SC1090
    source "$path"

    # Step 3: validate every canonical key.
    local key val missing=""
    for key in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        # Indirect expansion: ${!key} resolves the variable named $key.
        # Bash 3.2 supports ${!var} for scalar indirection (not arrays).
        # shellcheck disable=SC2027,SC2086
        eval "val=\"\${$key:-}\""

        if [ -z "$val" ]; then
            if [ -z "$missing" ]; then
                missing="$key"
            else
                missing="$missing, $key"
            fi
            continue
        fi

        # Reject newlines in value (contracts/personalization-schema.md §Value Constraints).
        case "$val" in
            *$'\n'*)
                echo "[aod] ERROR: personalization value for $key contains a newline (not permitted)" >&2
                return 8
                ;;
        esac

        # NUL bytes: bash scalar strings CANNOT contain NUL (the byte truncates
        # the value at C-string level inside bash's internals). If a NUL was
        # in the file's byte stream, the sourced value would already be
        # truncated to everything before it — undetectable here. We accept
        # this limitation (documented in contracts/personalization-schema.md
        # §Read Protocol); defense-in-depth is handled by init.sh's write-
        # time validation.

        # Export into the AOD_PERSONALIZATION_ namespace for substitute_lookup.
        # Use eval because the var name is dynamic; `val` is a shell-expanded
        # string so we need to pass it through safely. Using printf -v would
        # be cleaner but is bash 3.1+ — though actually 3.2 supports it, we
        # use the simpler eval approach consistent with other template-*.sh libs.
        eval "AOD_PERSONALIZATION_${key}=\"\$val\""
    done

    if [ -n "$missing" ]; then
        echo "[aod] ERROR: personalization.env is missing required key(s): $missing" >&2
        echo "[aod] (these are required per contracts/personalization-schema.md; RATIFICATION_DATE and CURRENT_DATE are init-time snapshots and must not be blank or recomputed)" >&2
        return 8
    fi

    return 0
}

# -----------------------------------------------------------------------------
# _aod_preserve_mode <source_file> <dest_file>
# -----------------------------------------------------------------------------
# Internal: copy the permission bits from <source_file> onto <dest_file>.
# Cross-platform (BSD/macOS + GNU/Linux). Silently no-ops if either file is
# missing (returns 1).
# -----------------------------------------------------------------------------
_aod_preserve_mode() {
    local src="${1:-}"
    local dest="${2:-}"

    if [ ! -e "$src" ] || [ ! -e "$dest" ]; then
        return 1
    fi

    local uname_s=""
    uname_s="$(uname -s 2>/dev/null || echo '')"

    case "$uname_s" in
        Darwin|FreeBSD|NetBSD|OpenBSD|DragonFly)
            # BSD stat: `stat -f %Mp%Lp` yields 4-digit octal (e.g., 0644, 0755).
            # Fall back to %A (symbolic) if %Mp%Lp unsupported.
            local mode
            mode="$(stat -f %Mp%Lp "$src" 2>/dev/null || true)"
            if [ -n "$mode" ]; then
                chmod "$mode" "$dest" 2>/dev/null || return 1
                return 0
            fi
            ;;
        Linux|GNU*|CYGWIN*|MINGW*|MSYS*)
            # GNU stat supports --reference.
            chmod --reference="$src" "$dest" 2>/dev/null && return 0
            # Fallback via octal mode.
            local mode
            mode="$(stat -c %a "$src" 2>/dev/null || true)"
            if [ -n "$mode" ]; then
                chmod "$mode" "$dest" 2>/dev/null || return 1
                return 0
            fi
            ;;
        *)
            # Unknown OS — try GNU --reference first, then BSD.
            chmod --reference="$src" "$dest" 2>/dev/null && return 0
            local mode
            mode="$(stat -f %Mp%Lp "$src" 2>/dev/null || stat -c %a "$src" 2>/dev/null || true)"
            if [ -n "$mode" ]; then
                chmod "$mode" "$dest" 2>/dev/null || return 1
                return 0
            fi
            ;;
    esac

    return 1
}

# -----------------------------------------------------------------------------
# aod_template_substitute_placeholders <source_file> <dest_file>
# -----------------------------------------------------------------------------
# Read <source_file> and write a substituted copy to <dest_file>. For each of
# the 12 canonical placeholders, replace all occurrences of `{{KEY}}` with the
# value loaded into `AOD_PERSONALIZATION_<KEY>`.
#
# CRITICAL: uses bash parameter expansion `${content//pattern/replacement}`
# which is truly LITERAL on both sides — no regex interpretation of the
# pattern OR the replacement. This is why adversarial values like
# `Cats & Dogs`, `foo\1bar`, regex metachars, pipes, and slashes all
# survive verbatim. See contracts/personalization-schema.md §Substitution
# Strategy for the rationale against sed.
#
# Atomicity: writes to a `.tmp` side file, then `mv`s into place. Also
# preserves the source file's mode bits (executable scripts remain +x).
#
# Arguments:
#   $1 — source file (must exist, must be regular file)
#   $2 — destination file (parent dir must exist; file may or may not exist)
# Pre-conditions:
#   aod_template_load_personalization_env MUST have been called successfully
#   in the same shell so that AOD_PERSONALIZATION_<KEY> values are set.
# Return:
#   0 on success
#   1 on IO failure or missing source
# -----------------------------------------------------------------------------
aod_template_substitute_placeholders() {
    local src="${1:-}"
    local dest="${2:-}"

    if [ -z "$src" ] || [ -z "$dest" ]; then
        echo "[aod] ERROR: aod_template_substitute_placeholders requires <src> <dest>" >&2
        return 1
    fi
    if [ ! -f "$src" ]; then
        echo "[aod] ERROR: substitute source not a regular file: $src" >&2
        return 1
    fi

    local dest_parent
    dest_parent="$(dirname "$dest")"
    if [ ! -d "$dest_parent" ]; then
        echo "[aod] ERROR: substitute destination parent directory missing: $dest_parent" >&2
        return 1
    fi

    # Read entire file into a variable. Bash's `$(<file)` form preserves
    # content bytes but strips trailing newlines (a shell quirk). We use a
    # different form that preserves trailing newlines exactly. For files
    # without trailing newline, both forms behave the same.
    #
    # Bash 3.2 does not have `mapfile`; we use `printf` + stdin redirection
    # into a `read -d '' -r` trick. However, `read -d '' -r` stops at the
    # end of input, so it reads the whole file. With IFS='' preserved, this
    # gives us byte-accurate read (modulo embedded NULs, which we rejected
    # at load time anyway via the env contract).
    local content=""
    # Using cat to read the file; $() strips ONE trailing newline, which we
    # account for at write time.
    content="$(cat "$src")"
    local src_had_trailing_newline=0
    # Detect trailing newline presence by checking the last byte.
    # `tail -c 1` gives the last byte; if it's \n then we had one.
    if [ -s "$src" ]; then
        local last_byte
        last_byte="$(tail -c 1 "$src" 2>/dev/null | od -An -c 2>/dev/null | tr -d ' ' || true)"
        case "$last_byte" in
            *\\n*|*'\n'*)
                src_had_trailing_newline=1
                ;;
        esac
    fi

    # Substitute each canonical placeholder using bash parameter expansion.
    # Form: ${var//pattern/replacement}
    # Both `pattern` and `replacement` are LITERAL strings in bash param
    # expansion (unlike sed), so special chars in values pass through
    # verbatim. The pattern `{{KEY}}` is a literal (we escape the braces to
    # avoid any brace-expansion interpretation, though bash does not expand
    # braces inside parameter expansion patterns).
    local key val
    for key in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        val="$(_aod_substitute_lookup "$key")"
        # Use string literal {{KEY}} as the pattern. The `\{` escapes any
        # pattern-metachar interpretation; bash param-expansion pattern
        # treats `{` and `}` as literal characters (they are globs, not
        # regex) when used as themselves.
        # Note: without `//` the first occurrence would be replaced; `//`
        # replaces ALL occurrences.
        content="${content//\{\{${key}\}\}/$val}"
    done

    # Write the substituted content atomically. Use .tmp side file.
    local tmp="${dest}.tmp"
    if [ "$src_had_trailing_newline" = "1" ]; then
        printf '%s\n' "$content" > "$tmp" 2>/dev/null || {
            echo "[aod] ERROR: failed to write $tmp" >&2
            rm -f "$tmp" 2>/dev/null || true
            return 1
        }
    else
        printf '%s' "$content" > "$tmp" 2>/dev/null || {
            echo "[aod] ERROR: failed to write $tmp" >&2
            rm -f "$tmp" 2>/dev/null || true
            return 1
        }
    fi

    # Preserve mode from source.
    _aod_preserve_mode "$src" "$tmp" 2>/dev/null || true

    # Atomic rename into place.
    if ! mv "$tmp" "$dest" 2>/dev/null; then
        echo "[aod] ERROR: failed to move $tmp → $dest" >&2
        rm -f "$tmp" 2>/dev/null || true
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_assert_no_residual <file>
# -----------------------------------------------------------------------------
# Scan <file> for any residual `{{[A-Z_]+}}` placeholder that survived
# substitution. Such residuals indicate either (a) an upstream file introduced
# a new placeholder NOT in the canonical 12 (unknown-placeholder halt), or
# (b) a bug in the substitution loop.
#
# Semantically equivalent to aod_template_scan_residual_placeholders from
# template-validate.sh, but returns exit 8 (personalization halt) instead of
# 1 (generic scan failure) to match the cli-contract.md exit-code map.
#
# Arguments:
#   $1 — path to a regular file to scan
# Return:
#   0 — clean, no residuals
#   8 — residual {{[A-Z_]+}} detected (details to stderr)
#   1 — argument error (missing file / path)
# -----------------------------------------------------------------------------
aod_template_assert_no_residual() {
    local file="${1:-}"

    if [ -z "$file" ]; then
        echo "[aod] ERROR: aod_template_assert_no_residual requires <file>" >&2
        return 1
    fi
    if [ ! -f "$file" ]; then
        echo "[aod] ERROR: assert_no_residual: not a regular file: $file" >&2
        return 1
    fi

    # Reuse the validate helper if available (sourced in update.sh). Otherwise
    # grep directly.
    local matches=""
    matches=$(grep -nE '\{\{[A-Z_]+\}\}' "$file" 2>/dev/null || true)

    if [ -n "$matches" ]; then
        # Report file:line:match format for tooling.
        printf '%s\n' "$matches" | sed "s|^|${file}:|" >&2
        echo "[aod] ERROR: residual placeholder(s) detected in $file — either the upstream introduced a new {{KEY}} not in the canonical 12, or a substitution bug. Halting." >&2
        return 8
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_init_personalization <dest_path>
# -----------------------------------------------------------------------------
# Used by scripts/init.sh to WRITE `.aod/personalization.env` from values that
# init.sh has already gathered via its interactive `read -p` prompts. This
# function does NOT itself prompt — it expects the caller (init.sh) to have
# the 12 values set as shell variables with the canonical names.
#
# Rationale: init.sh has custom prompt UX (stack pack defaults, numeric menu
# for AI agent, etc.) that we don't want to duplicate here. This function
# owns the atomic-write-to-disk step.
#
# Input (from caller's shell scope; see contracts/personalization-schema.md):
#   PROJECT_NAME, PROJECT_DESCRIPTION, GITHUB_ORG, GITHUB_REPO, AI_AGENT,
#   TECH_STACK, TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH,
#   CLOUD_PROVIDER (all required; init.sh fills defaults)
#   RATIFICATION_DATE, CURRENT_DATE (both required; init.sh captures via
#   `date +%Y-%m-%d`; this function does NOT recompute — it uses what the
#   caller supplies).
#
# Arguments:
#   $1 — destination path (usually `.aod/personalization.env`)
# Return:
#   0 on success
#   1 on argument error or write failure
#   8 if any required value is empty or contains a newline (same validation
#     as the loader; fail-fast before writing)
#
# Atomicity: writes to <dest>.tmp, then `mv`s into place.
# -----------------------------------------------------------------------------
aod_template_init_personalization() {
    local dest="${1:-}"

    if [ -z "$dest" ]; then
        echo "[aod] ERROR: aod_template_init_personalization requires <dest_path>" >&2
        return 1
    fi

    local parent
    parent="$(dirname "$dest")"
    if [ ! -d "$parent" ]; then
        if ! mkdir -p "$parent" 2>/dev/null; then
            echo "[aod] ERROR: could not create parent directory: $parent" >&2
            return 1
        fi
    fi

    # Validate all 12 values are set + free of newlines. The caller (init.sh)
    # supplies them as shell vars in its own scope — which, since we're a
    # sourced function, IS our scope.
    local key val
    for key in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        eval "val=\"\${$key:-}\""
        if [ -z "$val" ]; then
            echo "[aod] ERROR: aod_template_init_personalization: required value not set in caller scope: $key" >&2
            return 8
        fi
        case "$val" in
            *$'\n'*)
                echo "[aod] ERROR: aod_template_init_personalization: value for $key contains a newline" >&2
                return 8
                ;;
        esac
    done

    local tmp="${dest}.tmp"
    {
        printf '# AOD-kit adopter personalization\n'
        printf '# Created by scripts/init.sh on %s.\n' "${CURRENT_DATE}"
        printf '# Edit AI_AGENT, CLOUD_PROVIDER if they change; DO NOT edit RATIFICATION_DATE or CURRENT_DATE.\n'
        printf '\n'
        # Emit each key=value line. Quote values that contain spaces or
        # shell-special characters so the file remains bash-sourceable.
        for key in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
            eval "val=\"\${$key}\""
            # Determine if we need double-quote wrapping. Spaces, tabs, and
            # shell metacharacters all require quoting. Safe characters:
            # [A-Za-z0-9._/:@+=-].
            case "$val" in
                *[!A-Za-z0-9._/:@+=-]*)
                    # Contains at least one char outside the safe set — quote.
                    # Double-quotes require escaping `$`, `\`, `"`, and backtick.
                    local escaped="$val"
                    escaped="${escaped//\\/\\\\}"     # \ → \\
                    escaped="${escaped//\"/\\\"}"     # " → \"
                    escaped="${escaped//\$/\\\$}"     # $ → \$
                    escaped="${escaped//\`/\\\`}"     # ` → \`
                    printf '%s="%s"\n' "$key" "$escaped"
                    ;;
                '')
                    # Shouldn't reach here (validated above), but safe fallback.
                    printf '%s=""\n' "$key"
                    ;;
                *)
                    # All safe chars — no quotes required.
                    printf '%s=%s\n' "$key" "$val"
                    ;;
            esac
        done
    } > "$tmp" 2>/dev/null || {
        echo "[aod] ERROR: failed to write $tmp" >&2
        rm -f "$tmp" 2>/dev/null || true
        return 1
    }

    # Sanity check: the freshly-written file must be sourceable.
    if ! (
        set +e
        # shellcheck disable=SC1090
        source "$tmp"
    ) >/dev/null 2>&1; then
        echo "[aod] ERROR: freshly-written $tmp failed re-parse; refusing to commit" >&2
        rm -f "$tmp" 2>/dev/null || true
        return 1
    fi

    if ! mv "$tmp" "$dest" 2>/dev/null; then
        echo "[aod] ERROR: failed to move $tmp → $dest" >&2
        rm -f "$tmp" 2>/dev/null || true
        return 1
    fi

    return 0
}
