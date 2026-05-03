#!/usr/bin/env bash
# =============================================================================
# template-json.sh — JSON output helpers (schema_version 1.0)
# =============================================================================
# Part of feature 129 (downstream template update mechanism).
#
# Bash 3.2 compatible. Sourced by scripts/update.sh and scripts/sync-upstream.sh.
#
# Public functions (prefix: aod_template_):
#   - aod_template_json_escape             Escape a value for JSON string embedding.
#   - aod_template_json_kv                 Emit a "key":"value" pair.
#   - aod_template_json_array_append       Append an element to a JSON array buffer.
#   - aod_template_json_emit_envelope      Emit the schema_version 1.0 envelope.
#
# Clean factor-out from scripts/sync-upstream.sh:54-72.
# See contracts/library-api.md §template-json.sh and contracts/json-output-schema.md
# for API and shape details.
#
# Bodies implemented in T011 (feature 129).
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_TEMPLATE_JSON_SH_SOURCED:-}" ]; then
  return 0
fi
readonly AOD_TEMPLATE_JSON_SH_SOURCED=1

# -----------------------------------------------------------------------------
# aod_template_json_escape <string>
# -----------------------------------------------------------------------------
# Escape a string for inclusion in a JSON string literal (without surrounding
# quotes). Handles: backslash, double-quote, tab. NUL is rejected (caller's
# responsibility to validate; we simply treat it as an unsupported byte). The
# factored-out baseline preserves sync-upstream.sh:61-63 semantics exactly —
# newlines and other control chars are NOT escaped because the original
# implementation documented them as unsupported (spec limitation).
#
# Arguments:
#   $1 — the raw string to escape
# Output:
#   escaped string to stdout (no surrounding quotes)
# Return:
#   0 always (sed never fails on well-formed input)
# -----------------------------------------------------------------------------
aod_template_json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g'
}

# -----------------------------------------------------------------------------
# aod_template_json_kv <key> <value>
# -----------------------------------------------------------------------------
# Emit a JSON key-value pair (no surrounding braces or trailing comma).
# Values are escaped via aod_template_json_escape.
#
# Arguments:
#   $1 — JSON key (caller is responsible for ensuring it is JSON-safe;
#        typically ASCII [a-zA-Z0-9_])
#   $2 — raw value to escape + embed
# Output:
#   "<key>":"<escaped-value>" to stdout (no trailing newline)
# Return:
#   0 always
# -----------------------------------------------------------------------------
aod_template_json_kv() {
    local key="$1"
    local value="$2"
    printf '"%s":"%s"' "$key" "$(aod_template_json_escape "$value")"
}

# -----------------------------------------------------------------------------
# aod_template_json_array_append <array_var> <element>
# -----------------------------------------------------------------------------
# Append a pre-serialized JSON element (a string literal, an object, a number,
# etc.) to a named JSON-array-fragment accumulator variable. The accumulator
# holds the comma-separated body of the array (no surrounding brackets). Callers
# compose the final array by wrapping "[${accumulator}]".
#
# Arguments:
#   $1 — name of the shell variable holding the current accumulator (may be empty)
#   $2 — the new element, already JSON-formatted (e.g., '"foo"' or '{"k":1}')
# Side effects:
#   Updates the named variable in the caller's scope (via `eval`).
# Return:
#   0 always
# -----------------------------------------------------------------------------
aod_template_json_array_append() {
    local var_name="$1"
    local element="$2"
    local current=""
    eval "current=\${$var_name:-}"
    if [ -z "$current" ]; then
        eval "$var_name=\"\$element\""
    else
        eval "$var_name=\"\${current},\${element}\""
    fi
}

# -----------------------------------------------------------------------------
# aod_template_json_emit_envelope <key1> <value1> [<key2> <value2> ...]
# -----------------------------------------------------------------------------
# Emit a schema_version 1.0 JSON envelope. The first two fields are always
# `schema_version` and any caller-supplied pairs follow. Pairs MUST be provided
# as alternating key/value arguments. Values may contain any bytes except NUL
# and control chars not handled by aod_template_json_escape; the caller is
# responsible for pre-serializing non-string values (numbers, booleans, arrays,
# objects) and passing a sentinel key suffix — see below.
#
# Sentinel for non-string values:
#   If a key ends with "@raw", the trailing value is emitted verbatim WITHOUT
#   quoting or escaping (used for pre-formatted arrays / objects / numbers).
#   The "@raw" suffix is stripped from the output key.
#
# Arguments:
#   $@ — alternating key/value pairs
# Output:
#   One-line JSON envelope to stdout, terminated by \n.
# Return:
#   0 on success; 2 if arguments are unbalanced (odd count).
# -----------------------------------------------------------------------------
aod_template_json_emit_envelope() {
    if [ $(( $# % 2 )) -ne 0 ]; then
        echo "[aod] ERROR: aod_template_json_emit_envelope requires an even number of arguments (key/value pairs)" >&2
        return 2
    fi

    local out='{"schema_version":"1.0"'
    local key value esc_value
    while [ $# -gt 0 ]; do
        key="$1"
        value="$2"
        shift 2
        # Sentinel: @raw suffix → emit value verbatim (for pre-formatted JSON fragments)
        case "$key" in
            *@raw)
                key="${key%@raw}"
                out="${out},\"${key}\":${value}"
                ;;
            *)
                esc_value="$(aod_template_json_escape "$value")"
                out="${out},\"${key}\":\"${esc_value}\""
                ;;
        esac
    done
    out="${out}}"
    printf '%s\n' "$out"
}
