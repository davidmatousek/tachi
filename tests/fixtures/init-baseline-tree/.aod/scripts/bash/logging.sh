#!/usr/bin/env bash
# logging.sh - Simple logging utility for AOD workflows
#
# Usage:
#   source .aod/scripts/bash/logging.sh
#   aod_log "Your message here"
#
# Environment Variables:
#   AOD_LOG_FILE - Override default log path (default: .aod/logs/aod.log)
#
# Output Format:
#   {ISO8601_TIMESTAMP} {MESSAGE}
#   Example: 2026-02-13T10:30:00Z Stage started

# Default log file path (can be overridden via environment variable)
AOD_LOG_FILE="${AOD_LOG_FILE:-.aod/logs/aod.log}"

# Log a timestamped message to the log file
# Usage: aod_log "message"
# Returns: 0 on success, 1 on failure
aod_log() {
    local message="$1"
    local timestamp

    # Generate ISO 8601 UTC timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Ensure log directory exists
    mkdir -p "$(dirname "$AOD_LOG_FILE")" 2>/dev/null || {
        echo "[aod] Warning: Cannot create log directory" >&2
        return 1
    }

    # Append formatted log entry to file
    echo "$timestamp $message" >> "$AOD_LOG_FILE" 2>/dev/null || {
        echo "[aod] Warning: Cannot write to log file" >&2
        return 1
    }

    return 0
}
