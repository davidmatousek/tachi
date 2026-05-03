#!/usr/bin/env bash
# Version Detection Utility for Agentic Oriented Development Kit
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Detects Claude Code version at runtime and exports version info.
# Supports CLAUDECODE env var (official method) + CLI fallback.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${VERSION_DETECT_SCRIPT_DIR:-}" ]]; then
    readonly VERSION_DETECT_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
if [[ -z "${MIN_SUPPORTED_VERSION:-}" ]]; then
    readonly MIN_SUPPORTED_VERSION="2.1.15"
fi
if [[ -z "${FULL_FEATURES_VERSION:-}" ]]; then
    readonly FULL_FEATURES_VERSION="2.1.16"
fi

# Global exports
export AOD_CLAUDE_VERSION=""
export AOD_CLAUDE_DETECTED=false
export AOD_FULL_FEATURES=false

# ============================================================================
# Version Detection Functions
# ============================================================================

# Detect if running inside Claude Code environment
# Returns: 0 if in Claude Code, 1 otherwise
detect_claude_code_env() {
    if [[ -n "${CLAUDECODE:-}" ]]; then
        return 0
    fi
    return 1
}

# Parse version from claude CLI
# Returns: Version string (e.g., "2.1.16") or empty
parse_cli_version() {
    local version_output=""
    local parsed_version=""

    # Try to get version from claude CLI
    if command -v claude &>/dev/null; then
        version_output=$(claude --version 2>/dev/null || true)

        # Extract semantic version (e.g., "2.1.16" from various formats)
        parsed_version=$(echo "$version_output" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)

        if [[ -n "$parsed_version" ]]; then
            echo "$parsed_version"
            return 0
        fi
    fi

    return 1
}

# Compare semantic versions
# Usage: version_compare "2.1.16" "2.1.15"
# Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
version_compare() {
    local v1="$1"
    local v2="$2"

    # Split versions into arrays
    IFS='.' read -ra v1_parts <<< "$v1"
    IFS='.' read -ra v2_parts <<< "$v2"

    # Compare each part
    for i in 0 1 2; do
        local p1="${v1_parts[$i]:-0}"
        local p2="${v2_parts[$i]:-0}"

        if (( p1 > p2 )); then
            echo "1"
            return 0
        elif (( p1 < p2 )); then
            echo "-1"
            return 0
        fi
    done

    echo "0"
    return 0
}

# Check if version meets minimum requirement
# Usage: version_at_least "2.1.16" "2.1.15"
# Returns: 0 if v1 >= v2, 1 otherwise
version_at_least() {
    local version="$1"
    local required="$2"

    local cmp
    cmp=$(version_compare "$version" "$required")

    if [[ "$cmp" == "-1" ]]; then
        return 1
    fi
    return 0
}

# Main version detection function
# Sets global exports with detected version info
detect_version() {
    local detected_version=""
    local detection_method="unknown"

    # Method 1: Check CLAUDECODE env var (indicates we're in Claude Code)
    if detect_claude_code_env; then
        # Try to parse version from CLI
        detected_version=$(parse_cli_version || true)

        if [[ -n "$detected_version" ]]; then
            detection_method="cli"
        else
            # Fallback: assume minimum supported if in Claude Code but can't parse
            detected_version="$MIN_SUPPORTED_VERSION"
            detection_method="env_fallback"
        fi
    else
        # Not in Claude Code environment
        # Try CLI anyway (user might be testing outside Claude Code)
        detected_version=$(parse_cli_version || true)

        if [[ -n "$detected_version" ]]; then
            detection_method="cli_external"
        fi
    fi

    # Set exports
    if [[ -n "$detected_version" ]]; then
        export AOD_CLAUDE_VERSION="$detected_version"
        export AOD_CLAUDE_DETECTED=true
        export AOD_VERSION_DETECTION_METHOD="$detection_method"

        # Check if full features available
        if version_at_least "$detected_version" "$FULL_FEATURES_VERSION"; then
            export AOD_FULL_FEATURES=true
        else
            export AOD_FULL_FEATURES=false
        fi

        return 0
    else
        # Detection failed
        export AOD_CLAUDE_VERSION="unknown"
        export AOD_CLAUDE_DETECTED=false
        export AOD_FULL_FEATURES=false
        export AOD_VERSION_DETECTION_METHOD="failed"
        return 1
    fi
}

# Get human-readable version status
get_version_status() {
    if [[ "$AOD_CLAUDE_DETECTED" == "true" ]]; then
        if [[ "$AOD_FULL_FEATURES" == "true" ]]; then
            echo "Claude Code v${AOD_CLAUDE_VERSION} (full features)"
        else
            echo "Claude Code v${AOD_CLAUDE_VERSION} (limited features)"
        fi
    else
        echo "Claude Code version unknown"
    fi
}

# Check if a specific version is supported
# Usage: is_version_supported "context_forking"
is_version_supported() {
    local feature_min_version="${1:-$FULL_FEATURES_VERSION}"

    if [[ "$AOD_CLAUDE_DETECTED" != "true" ]]; then
        return 1
    fi

    version_at_least "$AOD_CLAUDE_VERSION" "$feature_min_version"
}

# ============================================================================
# Script execution (when sourced or run directly)
# ============================================================================

# Auto-detect on source
if [[ "${AOD_AUTO_DETECT:-true}" == "true" ]]; then
    detect_version || true
fi

# If run directly, output detection results
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    detect_version

    echo "=== AOD Kit Version Detection ==="
    echo "Claude Code Detected: $AOD_CLAUDE_DETECTED"
    echo "Version: $AOD_CLAUDE_VERSION"
    echo "Detection Method: ${AOD_VERSION_DETECTION_METHOD:-unknown}"
    echo "Full Features: $AOD_FULL_FEATURES"
    echo "Status: $(get_version_status)"
fi
