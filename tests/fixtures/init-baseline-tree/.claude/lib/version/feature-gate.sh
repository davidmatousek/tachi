#!/usr/bin/env bash
# Feature-Gated Command Paths
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Provides utilities for feature-gated command execution.
# Selects parallel or sequential execution based on version capabilities.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${FEATURE_GATE_SCRIPT_DIR:-}" ]]; then
    FEATURE_GATE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Source dependencies if not already loaded
source "${FEATURE_GATE_SCRIPT_DIR}/detect.sh" 2>/dev/null || true
source "${FEATURE_GATE_SCRIPT_DIR}/feature-flags.sh" 2>/dev/null || true
source "${FEATURE_GATE_SCRIPT_DIR}/degradation.sh" 2>/dev/null || true

# ============================================================================
# Execution Mode Selection
# ============================================================================

# Determine if parallel execution is available
# Returns: 0 if parallel available, 1 otherwise
can_use_parallel() {
    if [[ "${AOD_FEATURE_PARALLEL_EXECUTION:-false}" == "true" ]]; then
        return 0
    fi
    return 1
}

# Determine if context forking is available
# Returns: 0 if forking available, 1 otherwise
can_use_context_fork() {
    if [[ "${AOD_FEATURE_CONTEXT_FORKING:-false}" == "true" ]]; then
        return 0
    fi
    return 1
}

# Get recommended execution mode
# Returns: "parallel" or "sequential"
get_execution_mode() {
    if can_use_parallel && can_use_context_fork; then
        echo "parallel"
    else
        echo "sequential"
    fi
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

# Run pre-flight checks for Triad commands
# Outputs status messages and returns execution mode
run_preflight_checks() {
    local operation="${1:-triad_command}"

    echo "[TRIAD] Pre-flight check for $operation"
    echo "[TRIAD] Claude Code Version: ${AOD_CLAUDE_VERSION:-unknown}"

    local mode
    mode=$(get_execution_mode)

    if [[ "$mode" == "parallel" ]]; then
        echo "[TRIAD] Execution Mode: PARALLEL (v2.1.16+ features enabled)"
        echo "[TRIAD] - Context forking: Enabled"
        echo "[TRIAD] - Parallel reviews: Enabled"
    else
        echo "[TRIAD] Execution Mode: SEQUENTIAL (limited features)"

        # Log degradation details
        if ! can_use_parallel; then
            echo "[TRIAD] - Parallel execution: DISABLED (requires v2.1.16+)"
        fi
        if ! can_use_context_fork; then
            echo "[TRIAD] - Context forking: DISABLED (requires v2.1.0+)"
        fi
    fi

    echo "$mode"
}

# ============================================================================
# Gated Execution Helpers
# ============================================================================

# Execute dual review (PM + Architect) with appropriate mode
# Usage: execute_dual_review "feature_dir" "plan_path"
execute_dual_review_guidance() {
    local mode
    mode=$(get_execution_mode)

    if [[ "$mode" == "parallel" ]]; then
        cat <<'EOF'
## Parallel Dual Review (v2.1.16+)

Execute PM and Architect reviews in parallel using a SINGLE message with TWO Task calls:

```python
# In a single response, invoke both agents:
Task(
    subagent_type="product-manager",
    description="PM sign-off for plan feasibility",
    prompt="..."
)
Task(
    subagent_type="architect",
    description="Architect sign-off for technical design",
    prompt="..."
)
```

Both agents execute simultaneously in isolated forked contexts.
Total time = max(PM time, Architect time) + merge overhead.
EOF
    else
        cat <<'EOF'
## Sequential Dual Review (v2.1.15)

Execute PM and Architect reviews sequentially:

**Step 1**: Invoke PM agent, wait for completion
```python
Task(
    subagent_type="product-manager",
    description="PM sign-off for plan feasibility",
    prompt="..."
)
```

**Step 2**: After PM completes, invoke Architect agent
```python
Task(
    subagent_type="architect",
    description="Architect sign-off for technical design",
    prompt="..."
)
```

Total time = PM time + Architect time.
Note: Upgrade to v2.1.16 for parallel execution.
EOF
    fi
}

# Execute triple review (PM + Architect + Tech-Lead) with appropriate mode
execute_triple_review_guidance() {
    local mode
    mode=$(get_execution_mode)

    if [[ "$mode" == "parallel" ]]; then
        cat <<'EOF'
## Parallel Triple Review (v2.1.16+)

Execute all three reviews in parallel using a SINGLE message with THREE Task calls:

```python
Task(subagent_type="product-manager", ...)
Task(subagent_type="architect", ...)
Task(subagent_type="team-lead", ...)
```

All three execute simultaneously in isolated forked contexts.
EOF
    else
        cat <<'EOF'
## Sequential Triple Review (v2.1.15)

Execute reviews sequentially:

1. PM review → wait for completion
2. Architect review → wait for completion
3. Tech-Lead review → wait for completion

Upgrade to v2.1.16 for parallel execution and faster Triad cycles.
EOF
    fi
}

# ============================================================================
# Status Reporting
# ============================================================================

# Generate feature status report
generate_feature_status() {
    cat <<EOF
## AOD Kit Feature Status

**Claude Code Version**: ${AOD_CLAUDE_VERSION:-unknown}
**Detection Method**: ${AOD_VERSION_DETECTION_METHOD:-unknown}
**Full Features**: ${AOD_FULL_FEATURES:-false}

### Feature Flags

| Feature | Status | Required Version |
|---------|--------|------------------|
| Context Forking | ${AOD_FEATURE_CONTEXT_FORKING:-false} | v2.1.0+ |
| Parallel Execution | ${AOD_FEATURE_PARALLEL_EXECUTION:-false} | v2.1.16+ |
| Task Dependencies | ${AOD_FEATURE_TASK_DEPENDENCIES:-false} | v2.1.16+ |
| Graceful Degradation | ${AOD_FEATURE_GRACEFUL_DEGRADATION:-true} | v2.1.15+ |

### Execution Mode

**Recommended Mode**: $(get_execution_mode)

EOF

    if [[ "${AOD_FULL_FEATURES:-false}" != "true" ]]; then
        echo "**Upgrade Recommended**: Run 'claude upgrade' for full features"
    fi
}

# ============================================================================
# Script Execution
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:---status}" in
        --preflight)
            run_preflight_checks "${2:-triad_command}"
            ;;
        --dual-review)
            execute_dual_review_guidance
            ;;
        --triple-review)
            execute_triple_review_guidance
            ;;
        --status)
            generate_feature_status
            ;;
        *)
            echo "Usage: $0 [--preflight|--dual-review|--triple-review|--status]"
            echo ""
            echo "Feature-gated command path selection."
            ;;
    esac
fi
