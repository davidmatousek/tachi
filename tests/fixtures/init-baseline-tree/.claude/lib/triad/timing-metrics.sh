#!/usr/bin/env bash
# Timing Metrics Collection for Parallel vs Sequential Comparison
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Collects timing data for Triad review operations to compare
# parallel vs sequential execution performance.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${TIMING_METRICS_SCRIPT_DIR:-}" ]]; then
    TIMING_METRICS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Metrics storage
TIMING_START_TIME=""
TIMING_END_TIME=""
TIMING_OPERATION=""
TIMING_MODE=""  # "parallel" or "sequential"

# ============================================================================
# Timer Functions
# ============================================================================

# Start timing an operation
# Usage: start_timer "operation_name" "parallel|sequential"
start_timer() {
    TIMING_OPERATION="${1:-unknown}"
    TIMING_MODE="${2:-sequential}"
    TIMING_START_TIME=$(date +%s.%N 2>/dev/null || date +%s)

    # Log start
    echo "[TIMING] Starting $TIMING_OPERATION ($TIMING_MODE mode) at $(date '+%Y-%m-%d %H:%M:%S')" >&2
}

# Stop timer and get duration
# Usage: stop_timer
# Returns: duration in seconds
stop_timer() {
    TIMING_END_TIME=$(date +%s.%N 2>/dev/null || date +%s)

    # Calculate duration
    local duration
    if command -v bc &>/dev/null; then
        duration=$(echo "$TIMING_END_TIME - $TIMING_START_TIME" | bc)
    else
        # Fallback to integer arithmetic
        duration=$((${TIMING_END_TIME%.*} - ${TIMING_START_TIME%.*}))
    fi

    echo "[TIMING] Completed $TIMING_OPERATION in ${duration}s" >&2
    echo "$duration"
}

# Get elapsed time without stopping
# Usage: get_elapsed
# Returns: current elapsed time in seconds
get_elapsed() {
    local current_time
    current_time=$(date +%s.%N 2>/dev/null || date +%s)

    local elapsed
    if command -v bc &>/dev/null; then
        elapsed=$(echo "$current_time - $TIMING_START_TIME" | bc)
    else
        elapsed=$((${current_time%.*} - ${TIMING_START_TIME%.*}))
    fi

    echo "$elapsed"
}

# ============================================================================
# Metrics Recording
# ============================================================================

# Log a timing event to metrics file
# Usage: log_timing_event "operation" "mode" "duration" "notes"
log_timing_event() {
    local operation="$1"
    local mode="$2"
    local duration="$3"
    local notes="${4:-}"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Create metrics directory if needed
    local metrics_dir="${TIMING_METRICS_SCRIPT_DIR}/../../../.claude/metrics"
    mkdir -p "$metrics_dir" 2>/dev/null || true

    local metrics_file="${metrics_dir}/timing.csv"

    # Create header if file doesn't exist
    if [[ ! -f "$metrics_file" ]]; then
        echo "timestamp,operation,mode,duration_seconds,notes" > "$metrics_file"
    fi

    # Append record
    echo "${timestamp},${operation},${mode},${duration},\"${notes}\"" >> "$metrics_file"
}

# ============================================================================
# Comparison Functions
# ============================================================================

# Calculate time savings from parallel execution
# Usage: calculate_time_savings "sequential_time" "parallel_time"
# Returns: Percentage saved
calculate_time_savings() {
    local sequential="$1"
    local parallel="$2"

    if command -v bc &>/dev/null; then
        local saved
        saved=$(echo "scale=2; (($sequential - $parallel) / $sequential) * 100" | bc)
        echo "$saved"
    else
        # Simple integer math fallback
        local saved
        saved=$(( ((sequential - parallel) * 100) / sequential ))
        echo "$saved"
    fi
}

# Generate timing summary for a review operation
# Usage: generate_timing_summary "triad.plan" "parallel" "45.2"
generate_timing_summary() {
    local operation="$1"
    local mode="$2"
    local duration="$3"

    cat <<EOF
## Timing Summary

**Operation**: ${operation}
**Execution Mode**: ${mode}
**Duration**: ${duration}s

EOF

    if [[ "$mode" == "parallel" ]]; then
        cat <<EOF
**Parallel Execution Benefits**:
- PM and Architect reviews ran simultaneously
- Total time = max(PM time, Architect time) + overhead
- Estimated time saved: ~50% vs sequential

EOF
    else
        cat <<EOF
**Sequential Execution**:
- PM and Architect reviews ran one after another
- Total time = PM time + Architect time
- Consider upgrading to Claude Code v2.1.16 for parallel execution

EOF
    fi
}

# ============================================================================
# Aggregate Metrics
# ============================================================================

# Get average timing for an operation
# Usage: get_average_timing "triad.plan" "parallel"
get_average_timing() {
    local operation="$1"
    local mode="${2:-}"
    local metrics_file="${TIMING_METRICS_SCRIPT_DIR}/../../../.claude/metrics/timing.csv"

    if [[ ! -f "$metrics_file" ]]; then
        echo "0"
        return
    fi

    local filter_cmd="grep \"$operation\""
    if [[ -n "$mode" ]]; then
        filter_cmd="$filter_cmd | grep \"$mode\""
    fi

    # Calculate average (skip header)
    local sum count avg
    sum=0
    count=0

    while IFS=, read -r ts op md dur notes; do
        if [[ "$op" == "$operation" ]] && { [[ -z "$mode" ]] || [[ "$md" == "$mode" ]]; }; then
            sum=$(echo "$sum + ${dur:-0}" | bc 2>/dev/null || echo "$sum")
            ((count++))
        fi
    done < <(tail -n +2 "$metrics_file")

    if (( count > 0 )); then
        avg=$(echo "scale=2; $sum / $count" | bc 2>/dev/null || echo "0")
        echo "$avg"
    else
        echo "0"
    fi
}

# Generate metrics report
# Usage: generate_metrics_report
generate_metrics_report() {
    local metrics_file="${TIMING_METRICS_SCRIPT_DIR}/../../../.claude/metrics/timing.csv"

    echo "=== Triad Timing Metrics Report ==="
    echo ""

    if [[ ! -f "$metrics_file" ]]; then
        echo "No metrics recorded yet."
        return
    fi

    echo "| Operation | Mode | Avg Duration | Count |"
    echo "|-----------|------|--------------|-------|"

    # Group by operation and mode
    for op in "triad.plan" "triad.tasks" "triad.implement"; do
        for mode in "parallel" "sequential"; do
            local count=0
            local sum=0

            while IFS=, read -r ts operation md dur notes; do
                if [[ "$operation" == "$op" ]] && [[ "$md" == "$mode" ]]; then
                    ((count++))
                    sum=$(echo "$sum + ${dur:-0}" | bc 2>/dev/null || echo "$sum")
                fi
            done < <(tail -n +2 "$metrics_file")

            if (( count > 0 )); then
                local avg
                avg=$(echo "scale=2; $sum / $count" | bc 2>/dev/null || echo "0")
                echo "| $op | $mode | ${avg}s | $count |"
            fi
        done
    done

    echo ""
    echo "**Recommendations**:"
    local parallel_avg sequential_avg

    parallel_avg=$(get_average_timing "triad.plan" "parallel")
    sequential_avg=$(get_average_timing "triad.plan" "sequential")

    if [[ "$sequential_avg" != "0" ]] && [[ "$parallel_avg" != "0" ]]; then
        local savings
        savings=$(calculate_time_savings "$sequential_avg" "$parallel_avg")
        echo "- Parallel execution saves ~${savings}% on average"
    fi
}

# ============================================================================
# Script Execution
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:---report}" in
        --demo)
            echo "=== Timing Demo ==="
            start_timer "demo_operation" "parallel"
            sleep 1
            duration=$(stop_timer)
            log_timing_event "demo_operation" "parallel" "$duration" "Demo test"
            echo "Duration: ${duration}s"
            ;;
        --report)
            generate_metrics_report
            ;;
        *)
            echo "Usage: $0 [--demo|--report]"
            echo ""
            echo "Timing metrics collection for Triad operations."
            ;;
    esac
fi
