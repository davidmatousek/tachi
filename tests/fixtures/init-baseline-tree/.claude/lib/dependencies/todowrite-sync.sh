#!/usr/bin/env bash
# TodoWrite Synchronization for Dependency Tracking
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Provides utilities to sync task dependency status with TodoWrite
# for visibility in the Claude Code UI.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${TODOWRITE_SYNC_SCRIPT_DIR:-}" ]]; then
    readonly TODOWRITE_SYNC_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Source resolver if not already loaded
source "${TODOWRITE_SYNC_SCRIPT_DIR}/resolver.sh" 2>/dev/null || true

# ============================================================================
# TodoWrite Format Conversion
# ============================================================================

# Convert task status to TodoWrite format
# Usage: to_todowrite_status "ready"
to_todowrite_status() {
    local dep_status="$1"

    case "$dep_status" in
        "ready"|"pending")
            echo "pending" ;;
        "in_progress")
            echo "in_progress" ;;
        "completed")
            echo "completed" ;;
        "blocked"|"failed")
            echo "pending" ;;  # TodoWrite doesn't have blocked/failed
        *)
            echo "pending" ;;
    esac
}

# Generate TodoWrite JSON entry for a task
# Usage: task_to_todo_json "T001" "Create version detection" "ready"
task_to_todo_json() {
    local task_id="$1"
    local description="$2"
    local status="$3"
    local blocking_deps="${4:-}"

    local todo_status active_form
    todo_status=$(to_todowrite_status "$status")

    # Generate active form based on description
    # Convert imperative to present continuous
    # "Create X" -> "Creating X"
    active_form=$(echo "$description" | sed 's/^Create/Creating/' |
                                        sed 's/^Implement/Implementing/' |
                                        sed 's/^Update/Updating/' |
                                        sed 's/^Run/Running/' |
                                        sed 's/^Add/Adding/' |
                                        sed 's/^Fix/Fixing/')

    # Add blocking info if blocked
    local content="$task_id: $description"
    if [[ "$status" == "blocked" ]] && [[ -n "$blocking_deps" ]]; then
        content="$task_id: $description [Blocked by: $blocking_deps]"
    fi

    cat <<EOF
{
  "content": "$content",
  "status": "$todo_status",
  "activeForm": "$active_form"
}
EOF
}

# Generate TodoWrite JSON array for all tasks
# Usage: tasks_to_todo_json "specs/002/tasks.md"
tasks_to_todo_json() {
    local tasks_file="$1"

    # Initialize task statuses
    init_task_statuses "$tasks_file"

    echo "["
    local first=true

    # Read task descriptions from file
    while IFS= read -r line || [[ -n "$line" ]]; do
        if echo "$line" | grep -qE '^\s*-\s*\[\s*[x ]?\s*\]\s*T[0-9]{3}'; then
            local task_id description status blocking

            task_id=$(echo "$line" | grep -oE 'T[0-9]{3}' | head -1)
            # Extract description (everything after task ID until end or labels)
            description=$(echo "$line" | sed "s/.*$task_id//" | sed 's/\[.*//g' | sed 's/^\s*//' | tr -d '\n')
            status=$(get_effective_status "$task_id")
            blocking=$(get_blocking_deps "$task_id")

            if [[ "$first" != "true" ]]; then
                echo ","
            fi
            first=false

            task_to_todo_json "$task_id" "$description" "$status" "$blocking"
        fi
    done < "$tasks_file"

    echo ""
    echo "]"
}

# ============================================================================
# Status Update Utilities
# ============================================================================

# Get tasks that need status update in TodoWrite
# (tasks whose effective status differs from current TodoWrite status)
# Usage: get_status_changes "specs/002/tasks.md"
get_status_changes() {
    local tasks_file="$1"

    init_task_statuses "$tasks_file"

    for task_id in "${!TASK_STATUS[@]}"; do
        local current_status effective_status
        current_status="${TASK_STATUS[$task_id]}"
        effective_status=$(get_effective_status "$task_id")

        # Report if effective status differs meaningfully
        if [[ "$current_status" != "$effective_status" ]]; then
            # Only report if it's a meaningful change
            if [[ "$effective_status" == "ready" ]] && [[ "$current_status" == "pending" ]]; then
                echo "$task_id: pending -> ready (dependencies met)"
            elif [[ "$effective_status" == "blocked" ]] && [[ "$current_status" != "blocked" ]]; then
                echo "$task_id: $current_status -> blocked (waiting: $(get_blocking_deps "$task_id"))"
            fi
        fi
    done
}

# Generate a summary suitable for TodoWrite update notification
# Usage: generate_update_summary "specs/002/tasks.md"
generate_update_summary() {
    local tasks_file="$1"

    init_task_statuses "$tasks_file"

    local ready_count blocked_count completed_count total_count
    ready_count=0
    blocked_count=0
    completed_count=0
    total_count=${#TASK_STATUS[@]}

    for task_id in "${!TASK_STATUS[@]}"; do
        local status
        status=$(get_effective_status "$task_id")

        case "$status" in
            "ready")     ((ready_count++)) ;;
            "blocked")   ((blocked_count++)) ;;
            "completed") ((completed_count++)) ;;
        esac
    done

    local in_progress_count=$((total_count - ready_count - blocked_count - completed_count))

    cat <<EOF
## Task Progress Summary

**Total Tasks**: $total_count

| Status | Count | Tasks |
|--------|-------|-------|
| ✅ Completed | $completed_count | $(for t in "${!TASK_STATUS[@]}"; do [[ "$(get_effective_status "$t")" == "completed" ]] && echo -n "$t "; done) |
| 🟢 Ready | $ready_count | $(get_ready_tasks | tr '\n' ' ') |
| 🔴 Blocked | $blocked_count | $(get_blocked_tasks | tr '\n' ' ') |
| 🔄 In Progress | $in_progress_count | $(for t in "${!TASK_STATUS[@]}"; do [[ "$(get_effective_status "$t")" == "in_progress" ]] && echo -n "$t "; done) |

**Next Actions**: $(get_ready_tasks | head -3 | tr '\n' ', ')
EOF
}

# ============================================================================
# Integration Helpers
# ============================================================================

# Generate instruction for user to update TodoWrite
# Usage: generate_todowrite_instruction "specs/002/tasks.md"
generate_todowrite_instruction() {
    local tasks_file="$1"

    init_task_statuses "$tasks_file"

    local ready_tasks
    ready_tasks=$(get_ready_tasks | tr '\n' ' ')

    if [[ -n "$ready_tasks" ]]; then
        cat <<EOF
## TodoWrite Update Instructions

The following tasks are ready to execute:

\`\`\`
$ready_tasks
\`\`\`

To update TodoWrite, mark these tasks as \`in_progress\` when starting:

\`\`\`json
{
  "todos": [
$(for task in $ready_tasks; do
    echo "    {\"content\": \"$task\", \"status\": \"in_progress\", \"activeForm\": \"Executing $task\"},"
done)
  ]
}
\`\`\`

When a task completes, mark it as \`completed\`.
EOF
    else
        echo "No tasks currently ready. Check blocked tasks for dependencies."
    fi
}

# ============================================================================
# Script Execution
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <tasks.md> [--json|--changes|--summary|--instructions]"
        echo ""
        echo "Syncs task dependencies with TodoWrite format."
        exit 1
    fi

    tasks_file="$1"
    mode="${2:---summary}"

    case "$mode" in
        --json)
            tasks_to_todo_json "$tasks_file"
            ;;
        --changes)
            get_status_changes "$tasks_file"
            ;;
        --summary)
            generate_update_summary "$tasks_file"
            ;;
        --instructions)
            generate_todowrite_instruction "$tasks_file"
            ;;
        *)
            generate_update_summary "$tasks_file"
            ;;
    esac
fi
