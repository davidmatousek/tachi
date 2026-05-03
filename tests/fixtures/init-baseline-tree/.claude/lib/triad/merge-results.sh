#!/usr/bin/env bash
# Result Merging Logic for Forked Context Reviews
# Feature: 002-anthropic-updates-integration
# Created: 2026-01-24
#
# Merges results from parallel PM, Architect, and Tech-Lead reviews
# executed in forked contexts.

set -euo pipefail

# Constants (guard against re-source)
if [[ -z "${MERGE_RESULTS_SCRIPT_DIR:-}" ]]; then
    readonly MERGE_RESULTS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# ============================================================================
# Result Status Constants
# ============================================================================

# Review verdicts (in order of severity) - guard against re-source
if [[ -z "${STATUS_APPROVED:-}" ]]; then
    STATUS_APPROVED="APPROVED"
    STATUS_APPROVED_WITH_CONCERNS="APPROVED_WITH_CONCERNS"
    STATUS_CHANGES_REQUESTED="CHANGES_REQUESTED"
    STATUS_BLOCKED="BLOCKED"
    STATUS_FEASIBLE="FEASIBLE"
    STATUS_FEASIBLE_WITH_MODIFICATIONS="FEASIBLE_WITH_MODIFICATIONS"
    STATUS_NOT_FEASIBLE="NOT_FEASIBLE"
fi

# ============================================================================
# Result Merging Functions
# ============================================================================

# Get severity rank for a status (higher = more severe)
# Usage: get_status_severity "APPROVED"
get_status_severity() {
    local status="$1"
    case "$status" in
        "$STATUS_APPROVED"|"$STATUS_FEASIBLE")
            echo "1" ;;
        "$STATUS_APPROVED_WITH_CONCERNS"|"$STATUS_FEASIBLE_WITH_MODIFICATIONS")
            echo "2" ;;
        "$STATUS_CHANGES_REQUESTED")
            echo "3" ;;
        "$STATUS_BLOCKED"|"$STATUS_NOT_FEASIBLE")
            echo "4" ;;
        *)
            echo "0" ;;  # Unknown status
    esac
}

# Merge two statuses, returning the more severe one
# Usage: merge_two_statuses "APPROVED" "APPROVED_WITH_CONCERNS"
merge_two_statuses() {
    local status1="$1"
    local status2="$2"

    local sev1 sev2
    sev1=$(get_status_severity "$status1")
    sev2=$(get_status_severity "$status2")

    if (( sev1 >= sev2 )); then
        echo "$status1"
    else
        echo "$status2"
    fi
}

# Merge multiple review statuses
# Usage: merge_review_statuses "APPROVED" "APPROVED_WITH_CONCERNS" "APPROVED"
merge_review_statuses() {
    local merged=""

    for status in "$@"; do
        if [[ -z "$merged" ]]; then
            merged="$status"
        else
            merged=$(merge_two_statuses "$merged" "$status")
        fi
    done

    echo "$merged"
}

# Check if overall result is approved (can proceed)
# Usage: is_approved "APPROVED_WITH_CONCERNS"
is_approved() {
    local status="$1"
    local severity
    severity=$(get_status_severity "$status")

    # Severity 1 or 2 means approved (can proceed)
    (( severity <= 2 ))
}

# Check if result requires changes
# Usage: requires_changes "CHANGES_REQUESTED"
requires_changes() {
    local status="$1"
    [[ "$status" == "$STATUS_CHANGES_REQUESTED" ]]
}

# Check if result is blocked
# Usage: is_blocked "BLOCKED"
is_blocked() {
    local status="$1"
    [[ "$status" == "$STATUS_BLOCKED" || "$status" == "$STATUS_NOT_FEASIBLE" ]]
}

# ============================================================================
# Review Result Structure
# ============================================================================

# Create a merged review result
# Usage: create_merged_result "APPROVED" "findings..." "recommendations..."
create_merged_result() {
    local final_status="$1"
    local pm_status="${2:-}"
    local architect_status="${3:-}"
    local teamlead_status="${4:-}"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat <<EOF
## Merged Triad Review Results

**Merge Timestamp**: ${timestamp}
**Final Status**: ${final_status}

### Individual Reviews

| Reviewer | Status | Required |
|----------|--------|----------|
| PM | ${pm_status:-N/A} | ${pm_status:+Yes} |
| Architect | ${architect_status:-N/A} | ${architect_status:+Yes} |
| Team-Lead | ${teamlead_status:-N/A} | ${teamlead_status:+Yes} |

### Merge Decision

**Rule**: Most severe status determines outcome

**Outcome**: ${final_status}

EOF

    # Add action guidance based on status
    case "$final_status" in
        "$STATUS_APPROVED"|"$STATUS_FEASIBLE")
            echo "**Action**: Proceed to next phase"
            ;;
        "$STATUS_APPROVED_WITH_CONCERNS"|"$STATUS_FEASIBLE_WITH_MODIFICATIONS")
            echo "**Action**: Proceed with concerns tracked in documentation"
            ;;
        "$STATUS_CHANGES_REQUESTED")
            echo "**Action**: Address requested changes before proceeding"
            ;;
        "$STATUS_BLOCKED"|"$STATUS_NOT_FEASIBLE")
            echo "**Action**: HALT - Critical issues must be resolved"
            ;;
    esac
}

# ============================================================================
# Parallel Review Result Processing
# ============================================================================

# Process results from parallel PM and Architect reviews
# Usage: process_dual_review "$pm_result" "$architect_result"
process_dual_review() {
    local pm_result="$1"
    local architect_result="$2"

    # Extract statuses (assume first word after "Status:" line)
    local pm_status architect_status
    pm_status=$(echo "$pm_result" | grep -E "^\*\*Status\*\*:" | head -1 | sed 's/.*: //' | tr -d '[:space:]' || echo "UNKNOWN")
    architect_status=$(echo "$architect_result" | grep -E "^\*\*Status\*\*:" | head -1 | sed 's/.*: //' | tr -d '[:space:]' || echo "UNKNOWN")

    # Merge statuses
    local final_status
    final_status=$(merge_review_statuses "$pm_status" "$architect_status")

    # Create merged result
    create_merged_result "$final_status" "$pm_status" "$architect_status"
}

# Process results from parallel triple review (PM + Architect + Team-Lead)
# Usage: process_triple_review "$pm_result" "$architect_result" "$teamlead_result"
process_triple_review() {
    local pm_result="$1"
    local architect_result="$2"
    local teamlead_result="$3"

    # Extract statuses
    local pm_status architect_status teamlead_status
    pm_status=$(echo "$pm_result" | grep -E "^\*\*Status\*\*:" | head -1 | sed 's/.*: //' | tr -d '[:space:]' || echo "UNKNOWN")
    architect_status=$(echo "$architect_result" | grep -E "^\*\*Status\*\*:" | head -1 | sed 's/.*: //' | tr -d '[:space:]' || echo "UNKNOWN")
    teamlead_status=$(echo "$teamlead_result" | grep -E "^\*\*Status\*\*:" | head -1 | sed 's/.*: //' | tr -d '[:space:]' || echo "UNKNOWN")

    # Merge all three statuses
    local final_status
    final_status=$(merge_review_statuses "$pm_status" "$architect_status" "$teamlead_status")

    # Create merged result
    create_merged_result "$final_status" "$pm_status" "$architect_status" "$teamlead_status"
}

# ============================================================================
# Frontmatter Update Helpers
# ============================================================================

# Generate sign-off frontmatter for merged results
# Usage: generate_signoff_frontmatter "APPROVED" "pm" "2026-01-24"
generate_signoff_frontmatter() {
    local status="$1"
    local reviewer="$2"
    local date="$3"
    local notes="${4:-}"

    cat <<EOF
- **${reviewer}_signoff**: ${status}
- **${reviewer}_signoff_date**: ${date}
EOF

    if [[ -n "$notes" ]]; then
        echo "- **${reviewer}_signoff_notes**: ${notes}"
    fi
}

# ============================================================================
# Script Execution
# ============================================================================

# If run directly, run demo
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "=== Merge Results Demo ==="
    echo ""

    # Demo: Merge two statuses
    echo "Merging APPROVED + APPROVED_WITH_CONCERNS:"
    merge_review_statuses "APPROVED" "APPROVED_WITH_CONCERNS"
    echo ""

    echo "Merging APPROVED + CHANGES_REQUESTED:"
    merge_review_statuses "APPROVED" "CHANGES_REQUESTED"
    echo ""

    echo "Merging triple: APPROVED + APPROVED_WITH_CONCERNS + FEASIBLE:"
    merge_review_statuses "APPROVED" "APPROVED_WITH_CONCERNS" "FEASIBLE"
    echo ""

    # Demo: Create merged result
    echo "=== Merged Result Example ==="
    create_merged_result "APPROVED_WITH_CONCERNS" "APPROVED" "APPROVED_WITH_CONCERNS"
fi
