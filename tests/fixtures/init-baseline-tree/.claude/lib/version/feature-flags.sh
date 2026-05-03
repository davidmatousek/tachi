#!/usr/bin/env bash
# Feature Flag Computation for Agentic Oriented Development Kit
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Computes feature flags based on detected Claude Code version.
# Loads feature definitions from config/feature-flags.json.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${FEATURE_FLAGS_SCRIPT_DIR:-}" ]]; then
    readonly FEATURE_FLAGS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
FEATURE_FLAGS_CONFIG_FILE="${FEATURE_FLAGS_SCRIPT_DIR}/../../config/feature-flags.json"

# Source version detection if not already loaded
if [[ -z "${AOD_CLAUDE_VERSION:-}" ]]; then
    source "${FEATURE_FLAGS_SCRIPT_DIR}/detect.sh"
fi

# Feature flag exports
export AOD_FEATURE_CONTEXT_FORKING=false
export AOD_FEATURE_PARALLEL_EXECUTION=false
export AOD_FEATURE_TASK_DEPENDENCIES=false
export AOD_FEATURE_GRACEFUL_DEGRADATION=true

# ============================================================================
# Feature Flag Functions
# ============================================================================

# Parse minimum version for a feature from config
# Usage: get_feature_min_version "context_forking"
get_feature_min_version() {
    local feature="$1"
    local min_version=""

    if [[ -f "$FEATURE_FLAGS_CONFIG_FILE" ]] && command -v jq &>/dev/null; then
        min_version=$(jq -r ".features.${feature}.minimum_version // \"2.1.16\"" "$FEATURE_FLAGS_CONFIG_FILE" 2>/dev/null || echo "2.1.16")
    else
        # Fallback defaults if jq not available
        case "$feature" in
            context_forking)    min_version="2.1.0" ;;
            parallel_execution) min_version="2.1.16" ;;
            task_dependencies)  min_version="2.1.16" ;;
            graceful_degradation) min_version="2.1.15" ;;
            *)                  min_version="2.1.16" ;;
        esac
    fi

    echo "$min_version"
}

# Check if a feature is enabled based on version
# Usage: is_feature_enabled "context_forking"
is_feature_enabled() {
    local feature="$1"
    local min_version
    min_version=$(get_feature_min_version "$feature")

    # Check environment override first
    local env_var="AOD_FEATURE_$(echo "$feature" | tr '[:lower:]' '[:upper:]')"
    local override="${!env_var:-}"

    if [[ "$override" == "true" || "$override" == "false" ]]; then
        [[ "$override" == "true" ]]
        return $?
    fi

    # Check version requirement
    if [[ "$AOD_CLAUDE_DETECTED" == "true" ]]; then
        is_version_supported "$min_version"
        return $?
    fi

    return 1
}

# Compute all feature flags
compute_feature_flags() {
    # Context Forking (v2.1.0+)
    if is_feature_enabled "context_forking"; then
        export AOD_FEATURE_CONTEXT_FORKING=true
    else
        export AOD_FEATURE_CONTEXT_FORKING=false
    fi

    # Parallel Execution (v2.1.16+)
    if is_feature_enabled "parallel_execution"; then
        export AOD_FEATURE_PARALLEL_EXECUTION=true
    else
        export AOD_FEATURE_PARALLEL_EXECUTION=false
    fi

    # Task Dependencies (v2.1.16+)
    if is_feature_enabled "task_dependencies"; then
        export AOD_FEATURE_TASK_DEPENDENCIES=true
    else
        export AOD_FEATURE_TASK_DEPENDENCIES=false
    fi

    # Graceful Degradation (v2.1.15+) - enabled by default
    if is_feature_enabled "graceful_degradation"; then
        export AOD_FEATURE_GRACEFUL_DEGRADATION=true
    else
        export AOD_FEATURE_GRACEFUL_DEGRADATION=true  # Always true
    fi
}

# Get all feature flags as JSON
get_feature_flags_json() {
    cat <<EOF
{
  "version": "$AOD_CLAUDE_VERSION",
  "full_features": $AOD_FULL_FEATURES,
  "flags": {
    "context_forking": $AOD_FEATURE_CONTEXT_FORKING,
    "parallel_execution": $AOD_FEATURE_PARALLEL_EXECUTION,
    "task_dependencies": $AOD_FEATURE_TASK_DEPENDENCIES,
    "graceful_degradation": $AOD_FEATURE_GRACEFUL_DEGRADATION
  }
}
EOF
}

# Print feature flags summary
print_feature_flags() {
    echo "=== AOD Kit Feature Flags ==="
    echo "Claude Version: $AOD_CLAUDE_VERSION"
    echo ""
    echo "Features:"
    echo "  context_forking:      $AOD_FEATURE_CONTEXT_FORKING"
    echo "  parallel_execution:   $AOD_FEATURE_PARALLEL_EXECUTION"
    echo "  task_dependencies:    $AOD_FEATURE_TASK_DEPENDENCIES"
    echo "  graceful_degradation: $AOD_FEATURE_GRACEFUL_DEGRADATION"
}

# ============================================================================
# Script execution
# ============================================================================

# Auto-compute flags on source
compute_feature_flags

# If run directly, output flags
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    print_feature_flags
    echo ""
    echo "JSON Output:"
    get_feature_flags_json
fi
