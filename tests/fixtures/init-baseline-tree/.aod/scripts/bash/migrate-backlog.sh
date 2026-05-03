#!/usr/bin/env bash

# Migrate existing backlog items from 01_IDEAS.md and 02_USER_STORIES.md
# to GitHub Issues with appropriate stage:* labels.
#
# Usage: ./migrate-backlog.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be created without actually creating Issues
#
# Migration logic:
#   - Delivered items → stage:deliver
#   - "In PRD" items → stage:define
#   - "Validated" / "Ready for PRD" items → stage:discover
#   - "Scoring" / "Deferred" items → stage:discover
#
# After migration, archives old files to docs/product/_backlog/archive/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
source "$SCRIPT_DIR/github-lifecycle.sh"

DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
    esac
done

REPO_ROOT=$(get_repo_root)
IDEAS_FILE="$REPO_ROOT/docs/product/_backlog/01_IDEAS.md"
STORIES_FILE="$REPO_ROOT/docs/product/_backlog/02_USER_STORIES.md"
ARCHIVE_DIR="$REPO_ROOT/docs/product/_backlog/archive"

# Check prerequisites
if ! aod_gh_check_available; then
    echo "[aod] Cannot migrate backlog without GitHub access." >&2
    exit 1
fi

if [[ ! -f "$IDEAS_FILE" ]]; then
    echo "[aod] No 01_IDEAS.md found — nothing to migrate." >&2
    exit 0
fi

# Ensure archive directory exists
mkdir -p "$ARCHIVE_DIR"

echo "[aod] Starting backlog migration..."
echo ""

# Parse IDEAS table and create GitHub Issues
# Skip header rows (lines starting with | ID or |---|)
MIGRATED=0
SKIPPED=0

while IFS='|' read -r _ id idea source date status ice_score _; do
    # Trim whitespace
    id=$(echo "$id" | xargs)
    idea=$(echo "$idea" | xargs)
    source=$(echo "$source" | xargs)
    date=$(echo "$date" | xargs)
    status=$(echo "$status" | xargs)
    ice_score=$(echo "$ice_score" | xargs)

    # Skip non-data rows
    if [[ -z "$id" || "$id" == "ID" || "$id" == "----" || "$id" =~ ^-+$ ]]; then
        continue
    fi

    # Determine stage from status
    local_stage="discover"
    case "$status" in
        Delivered|delivered)
            local_stage="deliver"
            ;;
        "In PRD"|"in prd"|"In Define")
            local_stage="define"
            ;;
        "In Plan"|"Planning")
            local_stage="plan"
            ;;
        "In Build"|"Building"|"In Progress")
            local_stage="build"
            ;;
        *)
            local_stage="discover"
            ;;
    esac

    # Build issue body
    body="# $idea

## ICE Score
$ice_score

## Evidence
Migrated from legacy backlog — no evidence captured at original time.

## Metadata
- Source: $source
- Date: $date
- Original Status: $status
- Migrated: $(date +%Y-%m-%d)"

    title="$idea"
    # Truncate title to 256 chars (GitHub limit)
    if [[ ${#title} -gt 256 ]]; then
        title="${title:0:253}..."
    fi

    if $DRY_RUN; then
        echo "[dry-run] Would create Issue: $id → stage:$local_stage"
        echo "          Title: ${title:0:80}..."
    else
        result=$(aod_gh_create_issue "$title" "$body" "$local_stage" "idea")
        if [[ -n "$result" ]]; then
            echo "[aod] Migrated $id → Issue #$result (stage:$local_stage)"
            ((MIGRATED++))
        else
            echo "[aod] Warning: Failed to migrate $id"
            ((SKIPPED++))
        fi
    fi
done < <(tail -n +3 "$IDEAS_FILE")  # Skip header and separator rows

echo ""
echo "[aod] Migration complete: $MIGRATED migrated, $SKIPPED skipped"

# Archive old files (T065)
if ! $DRY_RUN && [[ $MIGRATED -gt 0 ]]; then
    echo ""
    echo "[aod] Archiving old backlog files..."

    if [[ -f "$IDEAS_FILE" ]]; then
        cp "$IDEAS_FILE" "$ARCHIVE_DIR/01_IDEAS.md"
        echo "[aod] Archived 01_IDEAS.md → archive/01_IDEAS.md"
    fi

    if [[ -f "$STORIES_FILE" ]]; then
        cp "$STORIES_FILE" "$ARCHIVE_DIR/02_USER_STORIES.md"
        echo "[aod] Archived 02_USER_STORIES.md → archive/02_USER_STORIES.md"
    fi

    echo "[aod] Note: Original files preserved. Use 'git mv' to move them if desired."
fi

# Regenerate BACKLOG.md
if ! $DRY_RUN; then
    echo ""
    echo "[aod] Regenerating BACKLOG.md..."
    "$SCRIPT_DIR/backlog-regenerate.sh" || echo "[aod] Warning: BACKLOG.md regeneration failed."
fi
