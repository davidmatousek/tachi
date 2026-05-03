#!/usr/bin/env bash
# Blocking/Ready Status Computation for Task Dependencies
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Computes which tasks are ready to execute based on dependency completion.
# Uses file-based approach for bash 3.x compatibility.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${DEPENDENCY_RESOLVER_SCRIPT_DIR:-}" ]]; then
    DEPENDENCY_RESOLVER_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Source parser if not already loaded
source "${DEPENDENCY_RESOLVER_SCRIPT_DIR}/parser.sh" 2>/dev/null || true

# ============================================================================
# Task Status Constants
# ============================================================================

STATUS_PENDING="pending"
STATUS_READY="ready"
STATUS_BLOCKED="blocked"
STATUS_IN_PROGRESS="in_progress"
STATUS_COMPLETED="completed"
STATUS_FAILED="failed"

# ============================================================================
# Temporary File Management (bash 3.x compatible)
# ============================================================================

RESOLVER_TEMP_DIR=""
TASK_STATUS_FILE=""
TASK_DEPS_FILE=""

init_resolver_temp() {
    RESOLVER_TEMP_DIR=$(mktemp -d)
    TASK_STATUS_FILE="${RESOLVER_TEMP_DIR}/status"
    TASK_DEPS_FILE="${RESOLVER_TEMP_DIR}/deps"
    touch "$TASK_STATUS_FILE" "$TASK_DEPS_FILE"
}

cleanup_resolver_temp() {
    if [[ -n "$RESOLVER_TEMP_DIR" ]] && [[ -d "$RESOLVER_TEMP_DIR" ]]; then
        rm -rf "$RESOLVER_TEMP_DIR"
    fi
}

trap cleanup_resolver_temp EXIT

# ============================================================================
# Status File Operations
# ============================================================================

get_task_status() {
    local task_id="$1"
    grep "^${task_id}:" "$TASK_STATUS_FILE" 2>/dev/null | cut -d: -f2 || echo "$STATUS_PENDING"
}

set_task_status() {
    local task_id="$1"
    local status="$2"

    # Remove existing entry
    grep -v "^${task_id}:" "$TASK_STATUS_FILE" > "${TASK_STATUS_FILE}.tmp" 2>/dev/null || true
    mv "${TASK_STATUS_FILE}.tmp" "$TASK_STATUS_FILE"

    # Add new entry
    echo "${task_id}:${status}" >> "$TASK_STATUS_FILE"
}

get_task_deps() {
    local task_id="$1"
    grep "^${task_id}:" "$TASK_DEPS_FILE" 2>/dev/null | cut -d: -f2 || true
}

get_all_task_ids() {
    cut -d: -f1 "$TASK_STATUS_FILE" 2>/dev/null | sort -u
}

# ============================================================================
# Status Tracking
# ============================================================================

# Initialize task statuses from tasks.md
init_task_statuses() {
    local tasks_file="$1"

    # Initialize temp files
    init_resolver_temp

    # Parse task statuses from file
    while IFS= read -r line || [[ -n "$line" ]]; do
        if echo "$line" | grep -qE '^\s*-\s*\[\s*[x ]?\s*\]\s*T[0-9]{3}'; then
            local task_id
            task_id=$(echo "$line" | grep -oE 'T[0-9]{3}' | head -1)

            # Check if task is completed (has [x])
            if echo "$line" | grep -qE '^\s*-\s*\[\s*[xX]\s*\]'; then
                echo "${task_id}:${STATUS_COMPLETED}" >> "$TASK_STATUS_FILE"
            else
                echo "${task_id}:${STATUS_PENDING}" >> "$TASK_STATUS_FILE"
            fi
        fi
    done < "$tasks_file"

    # Load dependencies
    parse_tasks_file "$tasks_file" > "$TASK_DEPS_FILE"
}

# Mark a task as completed
mark_completed() {
    local task_id="$1"
    set_task_status "$task_id" "$STATUS_COMPLETED"
}

# Mark a task as in progress
mark_in_progress() {
    local task_id="$1"
    set_task_status "$task_id" "$STATUS_IN_PROGRESS"
}

# Mark a task as failed
mark_failed() {
    local task_id="$1"
    set_task_status "$task_id" "$STATUS_FAILED"
}

# ============================================================================
# Ready/Blocked Computation
# ============================================================================

# Check if all dependencies of a task are completed
are_dependencies_met() {
    local task_id="$1"
    local deps
    deps=$(get_task_deps "$task_id")

    # No dependencies = ready
    if [[ -z "$deps" ]]; then
        return 0
    fi

    # Check each dependency
    for dep in ${deps//,/ }; do
        local dep_status
        dep_status=$(get_task_status "$dep")
        if [[ "$dep_status" != "$STATUS_COMPLETED" ]]; then
            return 1  # Dependency not complete
        fi
    done

    return 0  # All dependencies complete
}

# Get the status of a task (considering dependencies)
get_effective_status() {
    local task_id="$1"
    local current_status
    current_status=$(get_task_status "$task_id")

    # If already completed, in progress, or failed, return that
    if [[ "$current_status" == "$STATUS_COMPLETED" ]] ||
       [[ "$current_status" == "$STATUS_IN_PROGRESS" ]] ||
       [[ "$current_status" == "$STATUS_FAILED" ]]; then
        echo "$current_status"
        return
    fi

    # Check if dependencies are met
    if are_dependencies_met "$task_id"; then
        echo "$STATUS_READY"
    else
        echo "$STATUS_BLOCKED"
    fi
}

# Get all tasks that are ready to execute
get_ready_tasks() {
    for task_id in $(get_all_task_ids); do
        if [[ $(get_effective_status "$task_id") == "$STATUS_READY" ]]; then
            echo "$task_id"
        fi
    done
}

# Get all tasks that are blocked
get_blocked_tasks() {
    for task_id in $(get_all_task_ids); do
        if [[ $(get_effective_status "$task_id") == "$STATUS_BLOCKED" ]]; then
            echo "$task_id"
        fi
    done
}

# Get blocking dependencies for a task
get_blocking_deps() {
    local task_id="$1"
    local deps blocking
    deps=$(get_task_deps "$task_id")
    blocking=""

    if [[ -n "$deps" ]]; then
        for dep in ${deps//,/ }; do
            local dep_status
            dep_status=$(get_task_status "$dep")
            if [[ "$dep_status" != "$STATUS_COMPLETED" ]]; then
                blocking="$blocking$dep "
            fi
        done
    fi

    echo "$blocking" | xargs
}

# ============================================================================
# Execution Wave Computation
# ============================================================================

# Compute execution waves (topological sort by levels)
compute_execution_waves() {
    local wave=1
    local processed=0
    local total
    total=$(get_all_task_ids | wc -l | tr -d ' ')

    # Create temp file for wave tracking
    local wave_status_file="${RESOLVER_TEMP_DIR}/wave_status"
    cp "$TASK_STATUS_FILE" "$wave_status_file"

    while (( processed < total )); do
        local wave_tasks=""

        # Find all tasks ready in this wave
        for task_id in $(cut -d: -f1 "$wave_status_file" | sort -u); do
            local status
            status=$(grep "^${task_id}:" "$wave_status_file" | cut -d: -f2)

            if [[ "$status" == "$STATUS_PENDING" ]]; then
                local deps can_run
                deps=$(get_task_deps "$task_id")
                can_run=true

                if [[ -n "$deps" ]]; then
                    for dep in ${deps//,/ }; do
                        local dep_status
                        dep_status=$(grep "^${dep}:" "$wave_status_file" 2>/dev/null | cut -d: -f2 || echo "$STATUS_PENDING")
                        if [[ "$dep_status" != "$STATUS_COMPLETED" ]]; then
                            can_run=false
                            break
                        fi
                    done
                fi

                if [[ "$can_run" == "true" ]]; then
                    wave_tasks="$wave_tasks $task_id"
                fi
            fi
        done

        # If no tasks can run but we haven't processed all, there's a problem
        if [[ -z "$wave_tasks" ]] && (( processed < total )); then
            echo "ERROR: Unable to schedule remaining tasks (possible cycle)" >&2
            break
        fi

        # Output wave
        if [[ -n "$wave_tasks" ]]; then
            echo "Wave $wave:$wave_tasks"

            # Mark wave tasks as completed for next iteration
            for task_id in $wave_tasks; do
                grep -v "^${task_id}:" "$wave_status_file" > "${wave_status_file}.tmp" 2>/dev/null || true
                mv "${wave_status_file}.tmp" "$wave_status_file"
                echo "${task_id}:${STATUS_COMPLETED}" >> "$wave_status_file"
                ((processed++))
            done
        fi

        ((wave++))
    done
}

# ============================================================================
# Status Report
# ============================================================================

# Generate a status report for all tasks
generate_status_report() {
    echo "=== Task Dependency Status Report ==="
    echo ""
    echo "| Task | Status | Dependencies | Blocking |"
    echo "|------|--------|--------------|----------|"

    for task_id in $(get_all_task_ids); do
        local status deps blocking status_icon
        status=$(get_effective_status "$task_id")
        deps=$(get_task_deps "$task_id")
        blocking=$(get_blocking_deps "$task_id")

        # Format status with emoji
        case "$status" in
            "$STATUS_COMPLETED")    status_icon="✅ completed" ;;
            "$STATUS_IN_PROGRESS")  status_icon="🔄 in_progress" ;;
            "$STATUS_READY")        status_icon="🟢 ready" ;;
            "$STATUS_BLOCKED")      status_icon="🔴 blocked" ;;
            "$STATUS_FAILED")       status_icon="❌ failed" ;;
            *)                      status_icon="⚪ $status" ;;
        esac

        echo "| $task_id | $status_icon | ${deps:-None} | ${blocking:-None} |"
    done
}

# ============================================================================
# Script Execution
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <tasks.md> [--ready|--blocked|--waves|--report]"
        echo ""
        echo "Computes task readiness based on dependencies."
        exit 1
    fi

    tasks_file="$1"
    mode="${2:---report}"

    # Initialize from tasks file
    init_task_statuses "$tasks_file"

    case "$mode" in
        --ready)
            echo "Ready tasks:"
            get_ready_tasks
            ;;
        --blocked)
            echo "Blocked tasks:"
            get_blocked_tasks
            ;;
        --waves)
            echo "Execution Waves:"
            compute_execution_waves
            ;;
        --report)
            generate_status_report
            ;;
        *)
            generate_status_report
            ;;
    esac
fi
