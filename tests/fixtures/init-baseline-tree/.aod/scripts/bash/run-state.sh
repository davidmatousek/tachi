#!/usr/bin/env bash

# run-state.sh — Atomic read/write/validate for .aod/run-state.json
#
# Function library for the Full Lifecycle Orchestrator (Feature 022).
# Persists orchestration state to disk using write-then-rename for atomicity.
#
# Usage: source this file, then call functions directly.
#   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_read'
#
# Functions:
#   aod_state_read          — Read and output current state JSON
#   aod_state_write <json>  — Atomically write state JSON to disk
#   aod_state_validate      — Validate state file schema and integrity
#   aod_state_create <json> — Create initial state file (fails if exists)
#   aod_state_exists        — Check if state file exists (exit 0/1)
#   aod_state_is_stale      — Check if state is older than 7 days
#   aod_state_archive <dst> — Copy state to archive location
#   aod_state_get <field>   — Extract a top-level field from state
#   aod_state_set <field> <value> — Update a top-level field atomically
#   aod_state_append <field> <json> — Append JSON object to array field
#   aod_state_get_multi <f1> <f2>.. — Extract multiple fields, pipe-delimited
#   aod_state_get_loop_context      — Core Loop context: stage|substage|status
#   aod_state_get_governance_cache <art> <rev> — Read cached governance verdict
#   aod_state_cache_governance <art> <rev> <status> <summary> — Cache verdict
#   aod_state_clear_governance_cache <art> — Invalidate cache for artifact
#
# Requires: jq (JSON processor)
# Bash 3.2 compatible (macOS default)

set -euo pipefail

# State file paths
AOD_STATE_FILE=".aod/run-state.json"
AOD_STATE_TMP=".aod/run-state.json.tmp"

# Schema version
AOD_STATE_SCHEMA_VERSION="1.0"

# Stale threshold in seconds (7 days)
AOD_STALE_THRESHOLD=604800

# ============================================================================
# Prerequisites
# ============================================================================

aod_state_check_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        echo "[aod] ERROR: jq is required but not installed." >&2
        echo "[aod] Install with: brew install jq (macOS) or apt-get install jq (Linux)" >&2
        return 1
    fi
}

# ============================================================================
# Core Functions
# ============================================================================

# Check if state file exists
# Returns: 0 if exists, 1 if not
aod_state_exists() {
    [[ -f "$AOD_STATE_FILE" ]]
}

# Read and output current state JSON
# Returns: JSON to stdout, or error to stderr
aod_state_read() {
    aod_state_check_jq || return 1

    if ! aod_state_exists; then
        echo "[aod] ERROR: No state file found at $AOD_STATE_FILE" >&2
        return 1
    fi

    local content
    content=$(cat "$AOD_STATE_FILE") || {
        echo "[aod] ERROR: Could not read $AOD_STATE_FILE" >&2
        return 1
    }

    # Validate it's valid JSON
    if ! echo "$content" | jq . >/dev/null 2>&1; then
        echo "[aod] ERROR: State file is not valid JSON" >&2
        return 1
    fi

    echo "$content"
}

# Atomically write state JSON to disk (write-then-rename)
# Args: $1 = JSON string
aod_state_write() {
    aod_state_check_jq || return 1

    local json="$1"

    # Validate JSON before writing
    if ! echo "$json" | jq . >/dev/null 2>&1; then
        echo "[aod] ERROR: Invalid JSON provided to aod_state_write" >&2
        return 1
    fi

    # Update the updated_at timestamp
    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    json=$(echo "$json" | jq --arg ts "$now" '.updated_at = $ts')

    # Write to temp file, then rename (atomic on POSIX)
    echo "$json" | jq . > "$AOD_STATE_TMP" || {
        echo "[aod] ERROR: Failed to write temp state file" >&2
        rm -f "$AOD_STATE_TMP"
        return 1
    }

    mv "$AOD_STATE_TMP" "$AOD_STATE_FILE" || {
        echo "[aod] ERROR: Failed to rename temp state file (atomic write failed)" >&2
        return 1
    }
}

# Create initial state file (fails if one already exists)
# Args: $1 = JSON string
aod_state_create() {
    aod_state_check_jq || return 1

    if aod_state_exists; then
        echo "[aod] ERROR: State file already exists at $AOD_STATE_FILE" >&2
        echo "[aod] Use --resume to continue, or delete the file to start fresh." >&2
        return 1
    fi

    # Ensure .aod directory exists
    mkdir -p "$(dirname "$AOD_STATE_FILE")"

    aod_state_write "$1"
}

# Validate state file schema and integrity
# Returns: 0 if valid, 1 if invalid (details on stderr)
aod_state_validate() {
    aod_state_check_jq || return 1

    if ! aod_state_exists; then
        echo "[aod] VALIDATE: No state file found" >&2
        return 1
    fi

    local state
    state=$(aod_state_read) || return 1

    local errors=0

    # Check schema version
    local version
    version=$(echo "$state" | jq -r '.version // empty')
    if [[ -z "$version" ]]; then
        echo "[aod] VALIDATE: Missing schema version" >&2
        errors=$((errors + 1))
    elif [[ "$version" != "$AOD_STATE_SCHEMA_VERSION" ]]; then
        echo "[aod] VALIDATE: Unknown schema version: $version (expected $AOD_STATE_SCHEMA_VERSION)" >&2
        errors=$((errors + 1))
    fi

    # Check required fields
    local field
    for field in feature_id feature_name idea branch current_stage started_at updated_at; do
        local val
        val=$(echo "$state" | jq -r ".$field // empty")
        if [[ -z "$val" ]]; then
            echo "[aod] VALIDATE: Missing required field: $field" >&2
            errors=$((errors + 1))
        fi
    done

    # Check feature_id format (3 digits)
    local fid
    fid=$(echo "$state" | jq -r '.feature_id // empty')
    if [[ -n "$fid" ]] && ! echo "$fid" | grep -qE '^[0-9]{3}$'; then
        echo "[aod] VALIDATE: feature_id must be 3 digits, got: $fid" >&2
        errors=$((errors + 1))
    fi

    # Check current_stage is valid
    local stage
    stage=$(echo "$state" | jq -r '.current_stage // empty')
    case "$stage" in
        discover|define|plan|build|deliver|document) ;;
        *)
            echo "[aod] VALIDATE: Invalid current_stage: $stage" >&2
            errors=$((errors + 1))
            ;;
    esac

    # Check governance_tier is valid
    local tier
    tier=$(echo "$state" | jq -r '.governance_tier // empty')
    if [[ -n "$tier" ]]; then
        case "$tier" in
            light|standard|full) ;;
            *)
                echo "[aod] VALIDATE: Invalid governance_tier: $tier" >&2
                errors=$((errors + 1))
                ;;
        esac
    fi

    # Check governance_cache structure (optional field — backward compatible)
    local gc_type
    gc_type=$(echo "$state" | jq -r '.governance_cache | type // "null"')
    if [[ "$gc_type" != "null" ]]; then
        if [[ "$gc_type" != "object" ]]; then
            echo "[aod] VALIDATE: governance_cache must be an object, got: $gc_type" >&2
            errors=$((errors + 1))
        else
            # Validate each artifact entry
            local artifact
            for artifact in $(echo "$state" | jq -r '.governance_cache | keys[]' 2>/dev/null); do
                local art_type
                art_type=$(echo "$state" | jq -r ".governance_cache.\"$artifact\" | type")
                if [[ "$art_type" != "object" ]]; then
                    echo "[aod] VALIDATE: governance_cache.$artifact must be an object, got: $art_type" >&2
                    errors=$((errors + 1))
                    continue
                fi
                # Validate each reviewer entry
                local reviewer
                for reviewer in $(echo "$state" | jq -r ".governance_cache.\"$artifact\" | keys[]" 2>/dev/null); do
                    local entry
                    entry=$(echo "$state" | jq ".governance_cache.\"$artifact\".\"$reviewer\"")
                    # Check required fields: status, date, summary
                    local rf
                    for rf in status date summary; do
                        local rv
                        rv=$(echo "$entry" | jq -r ".$rf // empty")
                        if [[ -z "$rv" ]]; then
                            echo "[aod] VALIDATE: governance_cache.$artifact.$reviewer missing required field: $rf" >&2
                            errors=$((errors + 1))
                        fi
                    done
                    # Check status enum
                    local gc_status
                    gc_status=$(echo "$entry" | jq -r '.status // empty')
                    if [[ -n "$gc_status" ]]; then
                        case "$gc_status" in
                            APPROVED|APPROVED_WITH_CONCERNS|CHANGES_REQUESTED|BLOCKED|BLOCKED_OVERRIDDEN) ;;
                            *)
                                echo "[aod] VALIDATE: governance_cache.$artifact.$reviewer has invalid status: $gc_status" >&2
                                errors=$((errors + 1))
                                ;;
                        esac
                    fi
                done
            done
        fi
    fi

    # Check stages map exists
    local stages_type
    stages_type=$(echo "$state" | jq -r '.stages | type // empty')
    if [[ "$stages_type" != "object" ]]; then
        echo "[aod] VALIDATE: stages field must be an object" >&2
        errors=$((errors + 1))
    fi

    if [[ "$errors" -gt 0 ]]; then
        echo "[aod] VALIDATE: $errors error(s) found" >&2
        return 1
    fi

    echo "[aod] VALIDATE: State file is valid (v$version)"
    return 0
}

# Check if state is older than 7 days
# Returns: 0 if stale, 1 if fresh, 2 if error
aod_state_is_stale() {
    aod_state_check_jq || return 2

    if ! aod_state_exists; then
        return 2
    fi

    local state
    state=$(aod_state_read) || return 2

    local updated_at
    updated_at=$(echo "$state" | jq -r '.updated_at // empty')
    if [[ -z "$updated_at" ]]; then
        echo "[aod] WARNING: No updated_at timestamp in state file" >&2
        return 2
    fi

    # Convert ISO 8601 to epoch (portable: works on macOS and Linux)
    local state_epoch now_epoch
    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        state_epoch=$(date -d "$updated_at" +%s 2>/dev/null) || return 2
    else
        # BSD date (macOS)
        # Convert ISO 8601 to a format BSD date understands
        local cleaned
        cleaned=$(echo "$updated_at" | tr 'T' ' ' | tr -d 'Z')
        state_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$cleaned" +%s 2>/dev/null) || return 2
    fi
    now_epoch=$(date +%s)

    local age
    age=$((now_epoch - state_epoch))

    if [[ "$age" -gt "$AOD_STALE_THRESHOLD" ]]; then
        local days
        days=$((age / 86400))
        echo "[aod] WARNING: State file is $days days old (threshold: 7 days)" >&2
        return 0
    fi

    return 1
}

# Archive state file to a destination path
# Args: $1 = destination path (e.g., specs/022-*/run-state.json)
aod_state_archive() {
    local dest="$1"

    if ! aod_state_exists; then
        echo "[aod] ERROR: No state file to archive" >&2
        return 1
    fi

    mkdir -p "$(dirname "$dest")"
    cp "$AOD_STATE_FILE" "$dest" || {
        echo "[aod] ERROR: Failed to archive state to $dest" >&2
        return 1
    }

    echo "[aod] State archived to $dest"
}

# Extract a top-level field from state
# Args: $1 = field name (jq path, e.g., ".current_stage" or ".stages.discover.status")
aod_state_get() {
    aod_state_check_jq || return 1

    local field="$1"
    local state
    state=$(aod_state_read) || return 1

    echo "$state" | jq -r "$field // empty"
}

# Update a top-level field atomically
# Args: $1 = field name (jq path), $2 = value (string)
aod_state_set() {
    aod_state_check_jq || return 1

    local field="$1"
    local value="$2"

    local state
    state=$(aod_state_read) || return 1

    # Use jq to set the field
    state=$(echo "$state" | jq --arg v "$value" "$field = \$v")

    aod_state_write "$state"
}

# Append a JSON object to an array field atomically
# Args: $1 = array field (jq path, e.g., ".error_log"), $2 = JSON object string
aod_state_append() {
    aod_state_check_jq || return 1

    local field="$1"
    local json_obj="$2"

    # Validate the JSON object
    if ! echo "$json_obj" | jq . >/dev/null 2>&1; then
        echo "[aod] ERROR: Invalid JSON object for append" >&2
        return 1
    fi

    local state
    state=$(aod_state_read) || return 1

    # Use jq to append the object to the array
    state=$(echo "$state" | jq --argjson obj "$json_obj" "$field += [\$obj]")

    aod_state_write "$state"
}

# ============================================================================
# Compound Helpers (Feature 030: Context Efficiency)
# ============================================================================

# Extract multiple fields in a single disk read, return pipe-delimited values
# Args: $1..$N = jq field expressions (e.g., ".current_stage" ".current_substage")
# Output: pipe-delimited values (e.g., "build|null|in_progress")
# Null/missing fields return literal "null"
aod_state_get_multi() {
    aod_state_check_jq || return 1
    local state
    state=$(aod_state_read) || return 1

    # Build compound jq filter: [.field1, .field2, ...] | map(. // "null" | tostring) | join("|")
    local fields=""
    local sep=""
    for f in "$@"; do
        fields="${fields}${sep}${f}"
        sep=", "
    done

    echo "$state" | jq -r "[${fields}] | map(. // \"null\" | tostring) | join(\"|\")"
}

# Core Loop context: stage + substage + stage status in one read
# Output: "plan|spec|in_progress" or "build|null|completed"
# Null-guarded: if current_stage is null, stage_status returns "pending"
aod_state_get_loop_context() {
    aod_state_check_jq || return 1
    local state
    state=$(aod_state_read) || return 1

    echo "$state" | jq -r '[
        (.current_stage // "null"),
        (.current_substage // "null"),
        (if .current_stage then (.stages[.current_stage].status // "pending") else "pending" end)
    ] | join("|")'
}

# Read cached governance verdict for artifact+reviewer
# Args: $1 = artifact key (e.g., "spec"), $2 = reviewer role (e.g., "pm")
# Output: "APPROVED|2026-02-11T14:30:00Z|PM approved" or "null" if not cached
aod_state_get_governance_cache() {
    aod_state_check_jq || return 1
    local artifact="$1"
    local reviewer="$2"
    local state
    state=$(aod_state_read) || return 1

    echo "$state" | jq -r --arg art "$artifact" --arg rev "$reviewer" \
        'if .governance_cache[$art][$rev] then
            [.governance_cache[$art][$rev].status,
             .governance_cache[$art][$rev].date,
             .governance_cache[$art][$rev].summary] | join("|")
         else "null" end'
}

# Cache a governance verdict in state file
# Args: $1 = artifact key (e.g., "spec", "plan", "tasks", "prd")
#        $2 = reviewer role (e.g., "pm", "architect", "techlead")
#        $3 = status (e.g., "APPROVED", "CHANGES_REQUESTED", "BLOCKED")
#        $4 = summary text
aod_state_cache_governance() {
    aod_state_check_jq || return 1
    local artifact="$1"
    local reviewer="$2"
    local status="$3"
    local summary="$4"
    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local state
    state=$(aod_state_read) || return 1

    # Ensure governance_cache structure exists, then set the entry
    state=$(echo "$state" | jq \
        --arg art "$artifact" \
        --arg rev "$reviewer" \
        --arg st "$status" \
        --arg dt "$now" \
        --arg sm "$summary" \
        '.governance_cache //= {} |
         .governance_cache[$art] //= {} |
         .governance_cache[$art][$rev] = {status: $st, date: $dt, summary: $sm}')

    aod_state_write "$state"
}

# Clear governance cache for an artifact (invalidation on stage re-invocation)
# Args: $1 = artifact key (e.g., "spec", "plan", "tasks")
aod_state_clear_governance_cache() {
    aod_state_check_jq || return 1
    local artifact="$1"

    local state
    state=$(aod_state_read) || return 1

    # Remove the artifact's cache entry if it exists
    state=$(echo "$state" | jq --arg art "$artifact" \
        'if .governance_cache and .governance_cache[$art] then del(.governance_cache[$art]) else . end')

    aod_state_write "$state"
}
