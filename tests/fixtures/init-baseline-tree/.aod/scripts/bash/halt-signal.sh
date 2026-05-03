# LIBRARY — source before calling functions
# Feature 139 three-channel halt protocol: stdout message + JSON halt record + exit code 10.
# Canonical contract: specs/139-delivery-verified-not-documented/contracts/halt-record.md

# Directory holding per-feature halt records. Caller runs from repo root.
AOD_HALT_STATE_DIR="${AOD_HALT_STATE_DIR:-.aod/state}"

# Canonical exit code for halt-for-review (Channel 3). Caller invokes `exit "$(halt_exit_code)"`.
# Library functions never call `exit` directly — caller owns process lifecycle.
halt_exit_code() {
    echo 10
}

# Extract the NNN prefix (digits before the first hyphen) from a feature identifier.
# Example: "139-delivery-verified-not-documented" -> "139".
# Echoes the extracted prefix. Returns 0 always (caller validates if needed).
_halt_feature_nnn() {
    local feature="${1:-}"
    printf '%s' "${feature%%-*}"
}

# Channel 1: emit the human-readable halt line to stdout.
# Args:
#   $1 heal_pr_url          URL of opened heal-PR (may be empty)
#   $2 local_artifact_path  Fallback path to test artifacts (used when url is empty)
# Writes a single line to stdout (NOT stderr) per contracts/halt-record.md.
emit_halt_stdout() {
    local heal_pr_url="${1:-}"
    local local_artifact_path="${2:-}"

    if [ -n "$heal_pr_url" ]; then
        echo "Halted — heal-PR ${heal_pr_url} requires human review"
    else
        echo "Halted — test failures logged at ${local_artifact_path}; heal-PR unavailable"
    fi
}

# Channel 2: atomically write the machine-readable halt record to
# ${AOD_HALT_STATE_DIR}/deliver-{NNN}.halt.json via write-then-rename.
# Args:
#   $1 feature          Feature id, e.g. "139-delivery-verified-not-documented"
#   $2 reason           One of: e2e_fail | ac_coverage_fail | abandoned_heal
#   $3 heal_pr_url      URL or empty string (serialized as null when empty)
#   $4 heal_pr_number   Integer as string, or empty (serialized as null when empty)
#   $5 scenarios_json   JSON array string (e.g., '["A","B"]' or '[]')
#   $6 recovery_status  One of: not_attempted | recovered | exhausted | scope_guard_escalated
# Returns:
#   0 on successful atomic write
#   1 on any write failure (mkdir/jq/mv). Caller continues per ADR-006:
#     stdout + exit code 10 remain as the two backup channels.
write_halt_record() {
    local feature="${1:-}"
    local reason="${2:-}"
    local heal_pr_url="${3:-}"
    local heal_pr_number="${4:-}"
    local scenarios_json="${5:-[]}"
    local recovery_status="${6:-}"

    local nnn
    nnn=$(_halt_feature_nnn "$feature")

    local tmp="${AOD_HALT_STATE_DIR}/deliver-${nnn}.halt.json.tmp"
    local final="${AOD_HALT_STATE_DIR}/deliver-${nnn}.halt.json"

    if ! command -v jq >/dev/null 2>&1; then
        echo "Halt record write failed; degraded to stdout+exit channels" >&2
        return 1
    fi

    if ! mkdir -p "$AOD_HALT_STATE_DIR" 2>/dev/null; then
        echo "Halt record write failed; degraded to stdout+exit channels" >&2
        return 1
    fi

    # ISO-8601 UTC timestamp, e.g. 2026-04-22T14:30:00Z.
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # heal_pr_number is optional: empty string -> JSON null; otherwise pass as number.
    local pr_number_json
    if [ -z "$heal_pr_number" ]; then
        pr_number_json="null"
    else
        pr_number_json="$heal_pr_number"
    fi

    # heal_pr_url is optional: empty string -> JSON null; otherwise JSON string.
    # Default scenarios_json to a valid empty array if caller passed empty.
    if [ -z "$scenarios_json" ]; then
        scenarios_json="[]"
    fi

    if [ -n "$heal_pr_url" ]; then
        jq -n \
            --argjson ver 1 \
            --arg ts "$timestamp" \
            --arg feature "$feature" \
            --arg reason "$reason" \
            --arg heal_pr_url "$heal_pr_url" \
            --argjson heal_pr_number "$pr_number_json" \
            --argjson failing_scenarios "$scenarios_json" \
            --arg recovery_status "$recovery_status" \
            '{
                version: $ver,
                timestamp: $ts,
                feature: $feature,
                reason: $reason,
                heal_pr_url: $heal_pr_url,
                heal_pr_number: $heal_pr_number,
                failing_scenarios: $failing_scenarios,
                recovery_status: $recovery_status
            }' > "$tmp" 2>/dev/null || {
            echo "Halt record write failed; degraded to stdout+exit channels" >&2
            rm -f "$tmp" 2>/dev/null
            return 1
        }
    else
        jq -n \
            --argjson ver 1 \
            --arg ts "$timestamp" \
            --arg feature "$feature" \
            --arg reason "$reason" \
            --argjson heal_pr_number "$pr_number_json" \
            --argjson failing_scenarios "$scenarios_json" \
            --arg recovery_status "$recovery_status" \
            '{
                version: $ver,
                timestamp: $ts,
                feature: $feature,
                reason: $reason,
                heal_pr_url: null,
                heal_pr_number: $heal_pr_number,
                failing_scenarios: $failing_scenarios,
                recovery_status: $recovery_status
            }' > "$tmp" 2>/dev/null || {
            echo "Halt record write failed; degraded to stdout+exit channels" >&2
            rm -f "$tmp" 2>/dev/null
            return 1
        }
    fi

    # Atomic publish: rename is atomic within a single filesystem.
    if ! mv "$tmp" "$final" 2>/dev/null; then
        echo "Halt record write failed; degraded to stdout+exit channels" >&2
        rm -f "$tmp" 2>/dev/null
        return 1
    fi

    return 0
}
