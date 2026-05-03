#!/usr/bin/env bash

# PostToolUse hook: reconcile GitHub Projects board after stage label changes
#
# Fires after any Bash tool call. Checks if the command touched stage labels
# (via aod_gh_update_stage or gh issue edit --add-label stage:*).
# If so, runs a targeted reconciliation for the affected issue.
#
# Exit codes:
#   0 = allow (always — this is observational, never blocks)

set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

# Extract the command that was executed
COMMAND=$(printf '%s\n' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Only react to commands that change stage labels
if ! printf '%s\n' "$COMMAND" | grep -qiE 'aod_gh_update_stage|add-label.*stage:|stage:.*add-label'; then
    exit 0
fi

# Find the repo root (where .aod/ lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source lifecycle functions
if [[ ! -f "$REPO_ROOT/.aod/scripts/bash/github-lifecycle.sh" ]]; then
    exit 0
fi

# shellcheck source=/dev/null
source "$REPO_ROOT/.aod/scripts/bash/github-lifecycle.sh"

# Try to extract the issue number from the command
ISSUE_NUM=""

# Pattern 1: aod_gh_update_stage <number> <stage>
ISSUE_NUM=$(printf '%s\n' "$COMMAND" | grep -oE 'aod_gh_update_stage\s+([0-9]+)' | grep -oE '[0-9]+' | head -1) || true

# Pattern 2: gh issue edit <number> --add-label stage:*
if [[ -z "$ISSUE_NUM" ]]; then
    ISSUE_NUM=$(printf '%s\n' "$COMMAND" | grep -oE 'gh\s+issue\s+edit\s+([0-9]+)' | grep -oE '[0-9]+' | head -1) || true
fi

if [[ -z "$ISSUE_NUM" ]]; then
    exit 0
fi

# Get the current stage label for this issue
CURRENT_LABEL=$(gh issue view "$ISSUE_NUM" --json labels --jq '.labels[].name' 2>/dev/null | grep '^stage:' | head -1) || true

if [[ -z "$CURRENT_LABEL" ]]; then
    exit 0
fi

EXPECTED_STAGE="${CURRENT_LABEL#stage:}"

# Get the issue URL
ISSUE_URL=$(gh issue view "$ISSUE_NUM" --json url --jq '.url' 2>/dev/null) || true

if [[ -z "$ISSUE_URL" ]]; then
    exit 0
fi

# Verify board column matches — fix if not
aod_gh_move_on_board "$ISSUE_URL" "$EXPECTED_STAGE" 2>/dev/null || true

exit 0
