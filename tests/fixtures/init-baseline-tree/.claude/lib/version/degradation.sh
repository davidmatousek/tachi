#!/usr/bin/env bash
# Graceful Degradation Messaging for Agentic Oriented Development Kit
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Provides user-friendly messages when features are unavailable
# due to Claude Code version constraints.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${DEGRADATION_SCRIPT_DIR:-}" ]]; then
    readonly DEGRADATION_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Source dependencies if not already loaded
if [[ -z "${AOD_CLAUDE_VERSION:-}" ]]; then
    source "${DEGRADATION_SCRIPT_DIR}/detect.sh"
fi
if [[ -z "${AOD_FEATURE_CONTEXT_FORKING:-}" ]]; then
    source "${DEGRADATION_SCRIPT_DIR}/feature-flags.sh"
fi

# ============================================================================
# Message Templates
# ============================================================================

# Get feature unavailable message
# Usage: get_unavailable_message "context_forking"
get_unavailable_message() {
    local feature="$1"
    local current_version="${AOD_CLAUDE_VERSION:-unknown}"

    case "$feature" in
        context_forking)
            cat <<EOF
⚠️ Context Forking Unavailable

Feature: Isolated context forks for parallel agent reviews
Required: Claude Code v2.1.0 or higher
Current: v${current_version}

Fallback: Reviews will execute sequentially (PM → Architect → Tech-Lead)

To enable: Upgrade Claude Code with 'claude upgrade'
Docs: See MIGRATION.md for upgrade instructions
EOF
            ;;
        parallel_execution)
            cat <<EOF
⚠️ Parallel Execution Limited

Feature: Parallel Task calls with memory leak fixes
Required: Claude Code v2.1.16 or higher
Current: v${current_version}

Fallback: Agent tasks will execute sequentially
Impact: Triad reviews may take longer (5-7 min vs 3-4 min)

To enable: Upgrade Claude Code with 'claude upgrade'
Docs: See MIGRATION.md for upgrade instructions
EOF
            ;;
        task_dependencies)
            cat <<EOF
⚠️ Task Dependency Tracking Unavailable

Feature: Native task dependency enforcement
Required: Claude Code v2.1.16 or higher
Current: v${current_version}

Fallback: Manual coordination required for task ordering
Impact: No automatic prerequisite blocking

To enable: Upgrade Claude Code with 'claude upgrade'
Docs: See MIGRATION.md for upgrade instructions
EOF
            ;;
        *)
            echo "⚠️ Feature '$feature' requires a newer Claude Code version."
            ;;
    esac
}

# Get upgrade recommendation message
get_upgrade_recommendation() {
    local current_version="${AOD_CLAUDE_VERSION:-unknown}"
    local recommended="2.1.16"

    cat <<EOF
🔄 Upgrade Recommended

Current Claude Code: v${current_version}
Recommended: v${recommended}

Upgrade Benefits:
  ✅ Parallel Triad reviews (3-4 min vs 5-7 min)
  ✅ Context isolation (no cross-agent pollution)
  ✅ Memory leak fixes for long workflows
  ✅ Native task dependency support

How to upgrade:
  claude upgrade

After upgrade:
  1. Restart your terminal
  2. Run 'claude --version' to verify
  3. AOD Kit will auto-detect new features
EOF
}

# Get version status banner
get_version_banner() {
    local current_version="${AOD_CLAUDE_VERSION:-unknown}"

    if [[ "$AOD_FULL_FEATURES" == "true" ]]; then
        cat <<EOF
✅ Claude Code v${current_version} - Full Features Enabled
   • Context forking: Enabled
   • Parallel execution: Enabled
   • Task dependencies: Enabled
EOF
    elif [[ "$AOD_CLAUDE_DETECTED" == "true" ]]; then
        cat <<EOF
⚠️ Claude Code v${current_version} - Limited Features
   • Context forking: ${AOD_FEATURE_CONTEXT_FORKING}
   • Parallel execution: ${AOD_FEATURE_PARALLEL_EXECUTION}
   • Task dependencies: ${AOD_FEATURE_TASK_DEPENDENCIES}

   Run 'claude upgrade' for full features
EOF
    else
        cat <<EOF
❓ Claude Code Version Unknown
   Features running in conservative mode.
   Some optimizations may be disabled.

   If you're in Claude Code, run detection manually:
   source .claude/lib/version/detect.sh
EOF
    fi
}

# ============================================================================
# Degradation Handlers
# ============================================================================

# Check feature and show message if unavailable
# Usage: require_feature "context_forking" || handle_degradation
require_feature() {
    local feature="$1"
    local flag_var="AOD_FEATURE_$(echo "$feature" | tr '[:lower:]' '[:upper:]')"
    local flag_value="${!flag_var:-false}"

    if [[ "$flag_value" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Warn user about unavailable feature (non-blocking)
warn_feature_unavailable() {
    local feature="$1"

    if ! require_feature "$feature"; then
        echo ""
        get_unavailable_message "$feature"
        echo ""
    fi
}

# Fail if feature is required but unavailable
fail_feature_unavailable() {
    local feature="$1"

    if ! require_feature "$feature"; then
        echo ""
        get_unavailable_message "$feature"
        echo ""
        echo "❌ Cannot proceed without this feature."
        return 1
    fi
}

# Log degradation event for tracking
log_degradation_event() {
    local feature="$1"
    local fallback_action="$2"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Log to stderr for visibility
    >&2 echo "[DEGRADATION] $timestamp - Feature: $feature, Fallback: $fallback_action"

    # Could also log to file for analytics
    # echo "$timestamp,$feature,$fallback_action,$AOD_CLAUDE_VERSION" >> .aod/logs/degradation.csv
}

# ============================================================================
# Script execution
# ============================================================================

# If run directly, show version banner and recommendations
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    get_version_banner

    if [[ "$AOD_FULL_FEATURES" != "true" ]]; then
        echo ""
        get_upgrade_recommendation
    fi
fi
