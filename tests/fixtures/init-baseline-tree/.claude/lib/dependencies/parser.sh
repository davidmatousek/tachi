#!/usr/bin/env bash
# Dependency Parser for tasks.md Format
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Parses task dependencies from tasks.md files in various formats.
# Supports: "Depends on: T001, T002" and "depends_on: [T001, T002]" formats.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${DEPENDENCY_PARSER_SCRIPT_DIR:-}" ]]; then
    readonly DEPENDENCY_PARSER_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# ============================================================================
# Task Parsing Functions
# ============================================================================

# Extract task ID from a line (e.g., "- [ ] T001 Create..." -> "T001")
# Usage: extract_task_id "- [ ] T001 Create version detection"
extract_task_id() {
    local line="$1"
    echo "$line" | grep -oE 'T[0-9]{3}' | head -1 || true
}

# Extract dependencies from a task line or metadata
# Supports formats:
#   - "Depends on: T001, T002"
#   - "**Depends on**: T001, T002"
#   - "depends_on: [T001, T002]"
# Usage: extract_dependencies "- [ ] T005 ... (Depends on: T001-T004)"
extract_dependencies() {
    local line="$1"
    local deps=""
    local dep_portion=""

    # Format 1: "Depends on: T001, T002" or "(Depends on: T001-T004)"
    # Only extract the part AFTER "Depends on:"
    if echo "$line" | grep -qiE '[Dd]epends\s*on[:\s]'; then
        # Extract only after "Depends on" marker
        dep_portion=$(echo "$line" | sed -E 's/.*[Dd]epends[[:space:]]*on[[:space:]]*:?[[:space:]]*//' | sed 's/).*//')
        deps=$(echo "$dep_portion" | grep -oE 'T[0-9]{3}' | tr '\n' ' ')
    fi

    # Format 2: "depends_on: [T001, T002]" - extract content between brackets
    if echo "$line" | grep -qE 'depends_on.*\['; then
        dep_portion=$(echo "$line" | sed -E 's/.*depends_on[[:space:]]*:[[:space:]]*\[//' | sed 's/\].*//')
        deps=$(echo "$dep_portion" | grep -oE 'T[0-9]{3}' | tr '\n' ' ')
    fi

    # Output the dependencies, trimmed
    if [[ -n "$deps" ]]; then
        echo "$deps" | xargs
    fi
}

# Parse a tasks.md file and output task dependency map
# Usage: parse_tasks_file "specs/002/tasks.md"
# Output format: "TASK_ID:DEP1,DEP2,DEP3" (one per line)
parse_tasks_file() {
    local tasks_file="$1"

    if [[ ! -f "$tasks_file" ]]; then
        echo "ERROR: Tasks file not found: $tasks_file" >&2
        return 1
    fi

    local current_task=""
    local in_dependencies=false

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Check for task line (checkbox format)
        if echo "$line" | grep -qE '^\s*-\s*\[\s*[x ]?\s*\]\s*T[0-9]{3}'; then
            current_task=$(extract_task_id "$line")
            local line_deps
            line_deps=$(extract_dependencies "$line")

            if [[ -n "$current_task" ]]; then
                if [[ -n "$line_deps" ]]; then
                    echo "${current_task}:${line_deps// /,}"
                else
                    echo "${current_task}:"
                fi
            fi
        # Check for dependency table row
        elif [[ -n "$current_task" ]] && echo "$line" | grep -qiE 'depends'; then
            local table_deps
            table_deps=$(extract_dependencies "$line")
            if [[ -n "$table_deps" ]]; then
                echo "${current_task}:${table_deps// /,}"
            fi
        fi
    done < "$tasks_file"
}

# Parse dependency table section specifically
# Usage: parse_dependency_table "specs/002/tasks.md"
parse_dependency_table() {
    local tasks_file="$1"
    local in_table=false

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Detect table header
        if echo "$line" | grep -qE '^\|\s*Task\s*\|.*Depends'; then
            in_table=true
            continue
        fi

        # Skip separator row
        if [[ "$in_table" == "true" ]] && echo "$line" | grep -qE '^\|[-:|]+\|'; then
            continue
        fi

        # Parse table rows
        if [[ "$in_table" == "true" ]] && echo "$line" | grep -qE '^\|.*T[0-9]{3}'; then
            local task_id deps
            task_id=$(echo "$line" | grep -oE 'T[0-9]{3}' | head -1)
            deps=$(echo "$line" | awk -F'|' '{print $3}' | grep -oE 'T[0-9]{3}' | tr '\n' ',' | sed 's/,$//')

            if [[ -n "$task_id" ]]; then
                echo "${task_id}:${deps:-}"
            fi
        fi

        # End of table
        if [[ "$in_table" == "true" ]] && ! echo "$line" | grep -qE '^\|'; then
            in_table=false
        fi
    done < "$tasks_file"
}

# Get all task IDs from a tasks file
# Usage: get_all_tasks "specs/002/tasks.md"
get_all_tasks() {
    local tasks_file="$1"
    grep -oE 'T[0-9]{3}' "$tasks_file" | sort -u
}

# Get dependencies for a specific task
# Usage: get_task_dependencies "T005" "specs/002/tasks.md"
get_task_dependencies() {
    local task_id="$1"
    local tasks_file="$2"

    local deps
    deps=$(parse_tasks_file "$tasks_file" | grep "^${task_id}:" | cut -d: -f2)
    echo "${deps:-}"
}

# Build adjacency list (task -> dependents)
# Usage: build_adjacency_list "specs/002/tasks.md"
build_adjacency_list() {
    local tasks_file="$1"

    # For each dependency pair, output reverse relationship
    parse_tasks_file "$tasks_file" | while IFS=: read -r task deps; do
        if [[ -n "$deps" ]]; then
            for dep in ${deps//,/ }; do
                echo "${dep}:${task}"
            done
        fi
    done | sort
}

# ============================================================================
# Output Formats
# ============================================================================

# Output dependencies as JSON
# Usage: dependencies_to_json "specs/002/tasks.md"
dependencies_to_json() {
    local tasks_file="$1"

    echo "{"
    echo '  "tasks": {'

    local first=true
    parse_tasks_file "$tasks_file" | while IFS=: read -r task deps; do
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false

        local deps_json="[]"
        if [[ -n "$deps" ]]; then
            deps_json="[\"${deps//,/\", \"}\"]"
        fi
        printf '    "%s": { "depends_on": %s }' "$task" "$deps_json"
    done

    echo ""
    echo "  }"
    echo "}"
}

# ============================================================================
# Script Execution
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <tasks.md> [--json|--table|--adjacency]"
        echo ""
        echo "Parses task dependencies from a tasks.md file."
        echo ""
        echo "Options:"
        echo "  --json      Output as JSON"
        echo "  --table     Parse dependency table specifically"
        echo "  --adjacency Build reverse adjacency list"
        exit 1
    fi

    tasks_file="$1"
    format="${2:---default}"

    case "$format" in
        --json)
            dependencies_to_json "$tasks_file"
            ;;
        --table)
            parse_dependency_table "$tasks_file"
            ;;
        --adjacency)
            build_adjacency_list "$tasks_file"
            ;;
        *)
            echo "=== Task Dependencies ==="
            echo "File: $tasks_file"
            echo ""
            parse_tasks_file "$tasks_file"
            ;;
    esac
fi
