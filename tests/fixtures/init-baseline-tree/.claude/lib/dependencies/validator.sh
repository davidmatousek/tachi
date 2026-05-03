#!/usr/bin/env bash
# Circular Dependency Detection and Validation
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Validates task dependencies for cycles and other issues.
# Uses file-based approach for bash 3.x compatibility.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${DEPENDENCY_VALIDATOR_SCRIPT_DIR:-}" ]]; then
    DEPENDENCY_VALIDATOR_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Source parser if not already loaded
source "${DEPENDENCY_VALIDATOR_SCRIPT_DIR}/parser.sh" 2>/dev/null || true

# ============================================================================
# Temporary File Management
# ============================================================================

# Create temp files for state tracking (bash 3.x compatible)
VALIDATOR_TEMP_DIR=""
VISITED_FILE=""
IN_STACK_FILE=""
DEPS_FILE=""
CYCLE_PATH_FILE=""

init_temp_files() {
    VALIDATOR_TEMP_DIR=$(mktemp -d)
    VISITED_FILE="${VALIDATOR_TEMP_DIR}/visited"
    IN_STACK_FILE="${VALIDATOR_TEMP_DIR}/in_stack"
    DEPS_FILE="${VALIDATOR_TEMP_DIR}/deps"
    CYCLE_PATH_FILE="${VALIDATOR_TEMP_DIR}/cycle_path"
    touch "$VISITED_FILE" "$IN_STACK_FILE" "$DEPS_FILE" "$CYCLE_PATH_FILE"
}

cleanup_temp_files() {
    if [[ -n "$VALIDATOR_TEMP_DIR" ]] && [[ -d "$VALIDATOR_TEMP_DIR" ]]; then
        rm -rf "$VALIDATOR_TEMP_DIR"
    fi
}

# Trap to ensure cleanup
trap cleanup_temp_files EXIT

# ============================================================================
# State Management (file-based)
# ============================================================================

is_visited() {
    local task="$1"
    grep -q "^${task}$" "$VISITED_FILE" 2>/dev/null
}

mark_visited() {
    local task="$1"
    echo "$task" >> "$VISITED_FILE"
}

is_in_stack() {
    local task="$1"
    grep -q "^${task}$" "$IN_STACK_FILE" 2>/dev/null
}

add_to_stack() {
    local task="$1"
    echo "$task" >> "$IN_STACK_FILE"
    echo "$task" >> "$CYCLE_PATH_FILE"
}

remove_from_stack() {
    local task="$1"
    # Remove last occurrence from stack file
    grep -v "^${task}$" "$IN_STACK_FILE" > "${IN_STACK_FILE}.tmp" 2>/dev/null || true
    mv "${IN_STACK_FILE}.tmp" "$IN_STACK_FILE"
}

get_deps() {
    local task="$1"
    grep "^${task}:" "$DEPS_FILE" 2>/dev/null | cut -d: -f2 || true
}

# ============================================================================
# Cycle Detection (DFS-based)
# ============================================================================

# Load dependencies into file
load_dependencies() {
    local tasks_file="$1"
    parse_tasks_file "$tasks_file" > "$DEPS_FILE"
}

# DFS to detect cycle starting from a task
# Returns 0 if cycle found, 1 otherwise
dfs_visit() {
    local task="$1"

    # Mark as visited and add to stack
    mark_visited "$task"
    add_to_stack "$task"

    # Get dependencies
    local deps
    deps=$(get_deps "$task")

    if [[ -n "$deps" ]]; then
        for dep in ${deps//,/ }; do
            # If dependency is in current stack, we found a cycle
            if is_in_stack "$dep"; then
                echo "$dep" >> "$CYCLE_PATH_FILE"
                return 0  # Cycle found
            fi

            # If not visited, recurse
            if ! is_visited "$dep"; then
                if dfs_visit "$dep"; then
                    return 0  # Propagate cycle found
                fi
            fi
        done
    fi

    # Remove from current path (backtrack)
    remove_from_stack "$task"

    return 1  # No cycle found from this node
}

# Detect circular dependencies in a tasks file
# Usage: detect_cycles "specs/002/tasks.md"
# Returns: 0 if cycles found, 1 if no cycles
detect_cycles() {
    local tasks_file="$1"

    # Initialize temp files
    init_temp_files

    # Load dependencies
    load_dependencies "$tasks_file"

    # Get all tasks
    local all_tasks
    all_tasks=$(cut -d: -f1 "$DEPS_FILE" | sort -u)

    # Run DFS from each unvisited task
    for task in $all_tasks; do
        if ! is_visited "$task"; then
            if dfs_visit "$task"; then
                return 0  # Cycle found
            fi
        fi
    done

    return 1  # No cycles
}

# Get the cycle path (if any)
get_cycle_path() {
    if [[ -f "$CYCLE_PATH_FILE" ]]; then
        cat "$CYCLE_PATH_FILE" | tr '\n' ' -> ' | sed 's/ -> $//'
    fi
}

# ============================================================================
# Validation Functions
# ============================================================================

# Validate that all dependencies reference existing tasks
validate_references() {
    local tasks_file="$1"
    local errors=""
    local has_errors=false

    # Get all valid task IDs
    local all_tasks
    all_tasks=$(get_all_tasks "$tasks_file")

    # Check each dependency reference
    while IFS=: read -r task deps; do
        if [[ -n "$deps" ]]; then
            for dep in ${deps//,/ }; do
                if ! echo "$all_tasks" | grep -q "^${dep}$"; then
                    errors="${errors}  - $task references non-existent task $dep\n"
                    has_errors=true
                fi
            done
        fi
    done < <(parse_tasks_file "$tasks_file")

    if [[ "$has_errors" == "true" ]]; then
        echo "Reference Errors:"
        echo -e "$errors"
        return 1
    fi

    return 0
}

# Validate no self-references
validate_no_self_reference() {
    local tasks_file="$1"
    local errors=""
    local has_errors=false

    while IFS=: read -r task deps; do
        if [[ -n "$deps" ]] && echo "$deps" | grep -q "$task"; then
            errors="${errors}  - $task references itself\n"
            has_errors=true
        fi
    done < <(parse_tasks_file "$tasks_file")

    if [[ "$has_errors" == "true" ]]; then
        echo "Self-Reference Errors:"
        echo -e "$errors"
        return 1
    fi

    return 0
}

# Run all validations
validate_all() {
    local tasks_file="$1"
    local has_errors=false

    echo "=== Dependency Validation ==="
    echo "File: $tasks_file"
    echo ""

    # Check references
    echo "Checking references..."
    if ! validate_references "$tasks_file"; then
        has_errors=true
    else
        echo "  ✅ All references valid"
    fi
    echo ""

    # Check self-references
    echo "Checking for self-references..."
    if ! validate_no_self_reference "$tasks_file"; then
        has_errors=true
    else
        echo "  ✅ No self-references"
    fi
    echo ""

    # Check cycles
    echo "Checking for circular dependencies..."
    if detect_cycles "$tasks_file"; then
        echo "  ❌ Circular dependency detected!"
        echo "  Cycle: $(get_cycle_path)"
        has_errors=true
    else
        echo "  ✅ No circular dependencies"
    fi
    echo ""

    if [[ "$has_errors" == "true" ]]; then
        echo "❌ Validation FAILED"
        return 1
    else
        echo "✅ Validation PASSED"
        return 0
    fi
}

# ============================================================================
# Script Execution
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <tasks.md> [--cycles-only|--refs-only]"
        echo ""
        echo "Validates task dependencies for issues."
        exit 1
    fi

    tasks_file="$1"
    mode="${2:---all}"

    case "$mode" in
        --cycles-only)
            if detect_cycles "$tasks_file"; then
                echo "Cycle detected: $(get_cycle_path)"
                exit 1
            else
                echo "No cycles detected"
                exit 0
            fi
            ;;
        --refs-only)
            validate_references "$tasks_file"
            ;;
        *)
            validate_all "$tasks_file"
            ;;
    esac
fi
