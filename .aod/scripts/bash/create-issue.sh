#!/usr/bin/env bash

# Standalone entrypoint for creating a GitHub Issue with board sync.
#
# Unlike sourcing github-lifecycle.sh and calling aod_gh_create_issue(),
# this script can be run directly: bash .aod/scripts/bash/create-issue.sh ...
#
# It delegates to the library functions, which handle both issue creation
# and project-board sync. Board sync warnings are visible on stderr.
#
# Usage:
#   bash .aod/scripts/bash/create-issue.sh \
#     --title "Feature title" \
#     --body "Markdown body" \
#     --stage discover \
#     [--type idea]
#
# Output (stdout): the created/updated issue number (e.g. "80")
# Errors/warnings go to stderr.

set -euo pipefail

# --- Resolve repo root ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
REPO_ROOT=$(get_repo_root)
cd "$REPO_ROOT"

# Source the library
source ".aod/scripts/bash/github-lifecycle.sh"

# --- Parse arguments ---
TITLE=""
BODY=""
STAGE="discover"
ISSUE_TYPE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --title)
            [[ $# -ge 2 ]] || { echo "[aod] Error: --title requires a value" >&2; exit 1; }
            TITLE="$2"; shift 2 ;;
        --body)
            [[ $# -ge 2 ]] || { echo "[aod] Error: --body requires a value" >&2; exit 1; }
            BODY="$2"; shift 2 ;;
        --stage)
            [[ $# -ge 2 ]] || { echo "[aod] Error: --stage requires a value" >&2; exit 1; }
            STAGE="$2"; shift 2 ;;
        --type)
            [[ $# -ge 2 ]] || { echo "[aod] Error: --type requires a value" >&2; exit 1; }
            ISSUE_TYPE="$2"; shift 2 ;;
        *)
            echo "[aod] Error: Unknown argument '$1'" >&2
            echo "Usage: bash create-issue.sh --title \"...\" --body \"...\" --stage discover [--type idea]" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$TITLE" ]]; then
    echo "[aod] Error: --title is required." >&2
    exit 1
fi

# Validate stage
case "$STAGE" in
    discover|define|plan|build|deliver|done) ;;
    *) echo "[aod] Error: Invalid stage '$STAGE'. Valid: discover, define, plan, build, deliver, done" >&2; exit 1 ;;
esac

# --- Verify gh is available ---
# Gate before the library call so a missing gh emits exactly one wrapper-level
# message (FR-004 / US3 Independent Test). Other failure modes (auth, rate limit,
# network) flow through `aod_gh_create_issue` and surface real `gh` stderr via
# T010's mktemp pattern.
if ! command -v gh >/dev/null 2>&1; then
    echo "[aod] gh not found on PATH. Skipping issue creation." >&2
    exit 0
fi

# --- Create the issue (includes board sync) ---
issue_number=$(aod_gh_create_issue "$TITLE" "$BODY" "$STAGE" "$ISSUE_TYPE")

if [[ -z "$issue_number" ]]; then
    # Library already surfaced the real cause via stderr; exit 0 to keep the
    # broader flow non-blocking.
    exit 0
fi

echo "$issue_number"
