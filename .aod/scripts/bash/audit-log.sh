# LIBRARY — source before calling functions
# Feature 139 opt-out audit log: line-atomic JSONL append to .aod/audit/deliver-opt-outs.jsonl.
# Canonical contract: specs/139-delivery-verified-not-documented/contracts/audit-log.md

# Default audit log path (repo-relative; caller operates in repo root).
AOD_AUDIT_LOG_FILE="${AOD_AUDIT_LOG_FILE:-.aod/audit/deliver-opt-outs.jsonl}"

# Append a single opt-out record as a compact JSONL line.
# Args:
#   $1 timestamp  ISO-8601 UTC (e.g., 2026-04-22T14:30:00Z)
#   $2 invoker    User identifier (e.g., git email) or literal "autonomous"
#   $3 feature    Feature identifier (e.g., 139-delivery-verified-not-documented)
#   $4 reason     Free-text reason (10-500 chars; caller validates length)
#   $5 mode       "interactive" | "autonomous"
# Returns:
#   0 on successful append
#   1 if rendered JSON line exceeds 700 bytes (rejected — not truncated)
#   2 on runtime error (jq missing, mkdir/write failure)
append_opt_out_line() {
    local timestamp="${1:-}"
    local invoker="${2:-}"
    local feature="${3:-}"
    local reason="${4:-}"
    local mode="${5:-}"
    local line
    local dir

    if ! command -v jq >/dev/null 2>&1; then
        echo "append_opt_out_line: jq not found on PATH" >&2
        return 2
    fi

    # Build compact JSON via jq --arg to avoid shell-quoting bugs.
    line=$(jq -c -n \
        --arg ts "$timestamp" \
        --arg invoker "$invoker" \
        --arg feature "$feature" \
        --arg reason "$reason" \
        --arg mode "$mode" \
        '{timestamp: $ts, invoker: $invoker, feature: $feature, reason: $reason, mode: $mode}') || {
        echo "append_opt_out_line: jq failed to build JSON" >&2
        return 2
    }

    # Defense-in-depth size check; caller already bounds reason to 500 chars.
    if [ "${#line}" -gt 700 ]; then
        echo "Audit line too long (${#line} bytes); rejecting append" >&2
        return 1
    fi

    dir=$(dirname "$AOD_AUDIT_LOG_FILE")
    mkdir -p "$dir" 2>/dev/null || {
        echo "append_opt_out_line: cannot create directory $dir" >&2
        return 2
    }

    # POSIX guarantees atomicity for single writes <= PIPE_BUF (>=512 bytes);
    # our 700-byte cap keeps appends line-atomic across concurrent invocations.
    printf '%s\n' "$line" >> "$AOD_AUDIT_LOG_FILE" 2>/dev/null || {
        echo "append_opt_out_line: cannot append to $AOD_AUDIT_LOG_FILE" >&2
        return 2
    }

    return 0
}
