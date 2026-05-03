#!/usr/bin/env bash

# GitHub Issue lifecycle integration for AOD
#
# Provides functions for creating/updating GitHub Issues with stage:* labels.
# All functions gracefully degrade — they return 0 on failure and emit warnings.
#
# Usage: source this file, then call functions directly.
#
# Functions:
#   aod_gh_check_available    — verify gh CLI + remote configured
#   aod_gh_check_board_prereqs — verify gh version >= 2.40 and project scope
#   aod_gh_validate_cache     — validate board cache file integrity
#   aod_gh_check_board        — board availability check (prereqs + cache + hint)
#   aod_gh_setup_board        — one-time board creation + Status field config + cache
#   aod_gh_add_to_board       — add issue to Projects board and set Status column
#   aod_gh_move_on_board      — move issue to new Status column (auto-adds if missing)
#   aod_gh_create_issue       — create issue with stage:* label (or update existing)
#   aod_gh_update_stage       — transition issue to new stage label
#   aod_gh_reconcile_board    — reconcile all open issues: label ↔ board column
#   aod_gh_find_issue         — find existing issue by number or title match
#
# Expected Issue body format:
#   # Title
#   ## ICE Score
#   Impact: N, Confidence: N, Effort: N = **Total**
#   ## Evidence
#   [evidence statement]
#   ## User Story
#   As a [role], I want [capability], so that [benefit].
#   ## Acceptance Criteria
#   - [ ] Criterion 1
#   ## Metadata
#   - Source: [Brainstorm | Customer Feedback | ...]
#   - Priority: [P0 | P1 | P2 | P3]

set -euo pipefail

# All stage labels used by the AOD lifecycle
AOD_STAGE_LABELS=("stage:discover" "stage:define" "stage:plan" "stage:build" "stage:deliver" "stage:document" "stage:done")

# Board column mapping: AOD stage name → GitHub Projects Status option name
# Note: Uses a function instead of `declare -A` for bash 3.2 compatibility (macOS default).
aod_stage_to_column() {
    case "$1" in
        discover) echo "Discover" ;;
        define)   echo "Define" ;;
        plan)     echo "Plan" ;;
        build)    echo "Build" ;;
        deliver)  echo "Deliver" ;;
        document) echo "Document" ;;
        done)     echo "Done" ;;
        *)        echo "" ;;
    esac
}

# Board cache file — stores project ID, field IDs, option IDs after setup
AOD_BOARD_CACHE=".aod/memory/github-project.json"

# Hint marker — prevents repeated first-run tips
AOD_HINT_MARKER=".aod/memory/.board-hint-shown"

# One-time warning marker paths for board prerequisite checks
AOD_GH_VERSION_WARNED=".aod/memory/.gh-version-warned"
AOD_GH_SCOPE_WARNED=".aod/memory/.gh-scope-warned"

# Load AOD_REPO and AOD_BOARD from .env if not already set
# AOD_REPO ensures gh commands target the correct repository.
# AOD_BOARD (optional) pins the project board number, skipping title-based discovery.
if [[ -f ".env" ]]; then
    if [[ -z "${AOD_REPO:-}" ]]; then
        AOD_REPO=$(grep -E '^AOD_REPO=' .env 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'") || true
    fi
    if [[ -z "${AOD_BOARD:-}" ]]; then
        AOD_BOARD=$(grep -E '^AOD_BOARD=' .env 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'") || true
    fi
fi

# Export GH_REPO at source time so ALL gh calls (including direct invocations
# in hooks and scripts) target the correct repository. Previously this was
# deferred to aod_gh_check_available(), which meant any gh call before that
# check (e.g., reconcile-board.sh) would resolve to the wrong repo when
# multiple remotes exist (origin + upstream).
if [[ -n "${AOD_REPO:-}" ]]; then
    export GH_REPO="$AOD_REPO"
fi

# Check board prerequisites: gh CLI version >= 2.40 and project scope
# Returns: 0 if both pass, 1 if not (with one-time warnings on stderr)
aod_gh_check_board_prereqs() {
    # Check gh version >= 2.40
    local gh_version
    gh_version=$(gh --version 2>/dev/null | head -1) || {
        echo "[aod] Warning: Could not determine gh CLI version. Board operations skipped." >&2
        return 1
    }

    # Parse version: "gh version X.Y.Z (YYYY-MM-DD)" → extract X.Y
    local version_number
    version_number=$(echo "$gh_version" | grep -oE '[0-9]+\.[0-9]+' | head -1)

    if [[ -z "$version_number" ]]; then
        echo "[aod] Warning: Could not parse gh CLI version. Board operations skipped." >&2
        return 1
    fi

    local major minor
    major=$(echo "$version_number" | cut -d. -f1)
    minor=$(echo "$version_number" | cut -d. -f2)

    if [[ "$major" -lt 2 ]] || { [[ "$major" -eq 2 ]] && [[ "$minor" -lt 40 ]]; }; then
        if [[ ! -f "$AOD_GH_VERSION_WARNED" ]]; then
            echo "[aod] Warning: gh CLI version $version_number is below 2.40. GitHub Projects board operations require gh >= 2.40. Please upgrade: https://cli.github.com" >&2
            mkdir -p "$(dirname "$AOD_GH_VERSION_WARNED")"
            touch "$AOD_GH_VERSION_WARNED"
        fi
        return 1
    fi

    # Check project scope via gh auth status
    local auth_output
    auth_output=$(gh auth status 2>&1) || true

    if ! echo "$auth_output" | grep -q "project"; then
        if [[ ! -f "$AOD_GH_SCOPE_WARNED" ]]; then
            echo "[aod] Warning: Projects board sync skipped — 'project' OAuth scope not detected. Run 'gh auth refresh -s project' to enable." >&2
            mkdir -p "$(dirname "$AOD_GH_SCOPE_WARNED")"
            touch "$AOD_GH_SCOPE_WARNED"
        fi
        return 1
    fi

    return 0
}

# Validate board cache file integrity and owner match
# Returns: 0 if cache valid, 1 if invalid (clears cache on mismatch)
aod_gh_validate_cache() {
    # Check cache file exists
    if [[ ! -f "$AOD_BOARD_CACHE" ]]; then
        return 1
    fi

    # Check valid JSON
    if ! jq empty "$AOD_BOARD_CACHE" 2>/dev/null; then
        echo "[aod] Warning: Board cache is not valid JSON. Clearing cache." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Verify required fields present
    local missing_fields=0
    for field in project_number project_id owner status_field_id status_options; do
        if [[ "$(jq -r ".$field // empty" "$AOD_BOARD_CACHE" 2>/dev/null)" == "" ]]; then
            missing_fields=1
            break
        fi
    done

    if [[ "$missing_fields" -eq 1 ]]; then
        echo "[aod] Warning: Board cache missing required fields. Clearing cache — run 'aod_gh_setup_board' to reconfigure." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Verify status_options has exactly 7 entries with non-empty option IDs
    local option_count
    option_count=$(jq '.status_options | length' "$AOD_BOARD_CACHE" 2>/dev/null)
    if [[ "$option_count" != "7" ]]; then
        echo "[aod] Warning: Board cache has $option_count status options (expected 7). Clearing cache — run 'aod_gh_setup_board' to reconfigure." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Check all option IDs are non-empty
    local empty_options
    empty_options=$(jq '[.status_options | to_entries[] | select(.value == "" or .value == null)] | length' "$AOD_BOARD_CACHE" 2>/dev/null)
    if [[ "$empty_options" != "0" ]]; then
        echo "[aod] Warning: Board cache contains empty option IDs. Clearing cache — run 'aod_gh_setup_board' to reconfigure." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Verify project_id starts with PVT_
    local project_id
    project_id=$(jq -r '.project_id' "$AOD_BOARD_CACHE" 2>/dev/null)
    if [[ "$project_id" != PVT_* ]]; then
        echo "[aod] Warning: Board cache has invalid project_id format. Clearing cache — run 'aod_gh_setup_board' to reconfigure." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Verify status_field_id starts with PVTSSF_
    local status_field_id
    status_field_id=$(jq -r '.status_field_id' "$AOD_BOARD_CACHE" 2>/dev/null)
    if [[ "$status_field_id" != PVTSSF_* ]]; then
        echo "[aod] Warning: Board cache has invalid status_field_id format. Clearing cache — run 'aod_gh_setup_board' to reconfigure." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Compare owner against current repo owner
    local cached_owner current_owner
    cached_owner=$(jq -r '.owner' "$AOD_BOARD_CACHE" 2>/dev/null)
    current_owner=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null) || {
        echo "[aod] Warning: Could not verify repo owner. Board cache kept but may be stale." >&2
        return 0
    }

    if [[ "$cached_owner" != "$current_owner" ]]; then
        echo "[aod] Warning: Repository owner changed (fork?). Cached owner '$cached_owner' does not match current owner '$current_owner'. Board cache cleared — run 'aod_gh_setup_board' to reconfigure." >&2
        rm -f "$AOD_BOARD_CACHE"
        return 1
    fi

    # Verify cached board title matches an accepted naming pattern
    # Skip title check when AOD_BOARD is explicitly pinned — the user chose this board.
    # Otherwise accept: "AOD Backlog" (legacy) or "{repo-name}-backlog" (convention)
    if [[ -z "${AOD_BOARD:-}" ]]; then
        local cached_title current_repo_name
        cached_title=$(jq -r '.board_title // empty' "$AOD_BOARD_CACHE" 2>/dev/null)
        if [[ -n "$cached_title" ]]; then
            current_repo_name=$(gh repo view --json name --jq '.name' 2>/dev/null) || current_repo_name=""
            local repo_title="${current_repo_name:+${current_repo_name}-backlog}"
            if [[ "$cached_title" != "AOD Backlog" && -n "$repo_title" && "$cached_title" != "$repo_title" ]]; then
                echo "[aod] Warning: Board title mismatch. Cached '$cached_title' is not 'AOD Backlog' or '$repo_title'. Board cache cleared — run 'aod_gh_setup_board' to reconfigure." >&2
                rm -f "$AOD_BOARD_CACHE"
                return 1
            fi
        fi
    fi

    return 0
}

# Session guard — set to 1 after first successful board check
_AOD_BOARD_CHECKED="${_AOD_BOARD_CHECKED:-0}"

# Check board availability: prereqs + cache validation + first-run hint
# Returns: 0 if board available, 1 if not
aod_gh_check_board() {
    # Return early if already validated this session
    if [[ "$_AOD_BOARD_CHECKED" == "1" ]]; then
        return 0
    fi

    # Check gh CLI is available first
    if ! aod_gh_check_available; then
        return 1
    fi

    # Check board-specific prerequisites (version + scope)
    if ! aod_gh_check_board_prereqs; then
        return 1
    fi

    # Validate cache — auto-setup board if missing
    if ! aod_gh_validate_cache; then
        # No valid cache — auto-invoke setup (idempotent, gracefully degrades)
        echo "[aod] No valid board cache found. Auto-setting up GitHub Projects board..." >&2
        aod_gh_setup_board

        # Re-validate after setup attempt
        if ! aod_gh_validate_cache; then
            # Setup didn't produce a valid cache — show hint once
            if [[ ! -f "$AOD_HINT_MARKER" ]]; then
                echo "[aod] Tip: Board auto-setup did not succeed. Check gh CLI permissions (project scope required)." >&2
                mkdir -p "$(dirname "$AOD_HINT_MARKER")"
                touch "$AOD_HINT_MARKER"
            fi
            return 1
        fi
    fi

    # All checks passed — mark as checked for this session
    _AOD_BOARD_CHECKED=1
    return 0
}

# One-time board setup: create GitHub Projects board, configure Status field, cache IDs
# Returns: 0 always (graceful degradation), JSON cache on stdout on success
aod_gh_setup_board() {
    # --- Section 1: Prerequisite checks and owner detection ---

    # Check gh CLI is available
    if ! aod_gh_check_available; then
        echo "[aod] Warning: Board setup requires gh CLI. Skipping." >&2
        return 0
    fi

    # Check board-specific prerequisites (version + scope)
    if ! aod_gh_check_board_prereqs; then
        echo "[aod] Warning: Board prerequisites not met. Skipping setup." >&2
        return 0
    fi

    # Auto-detect repo owner
    local owner
    owner=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null) || {
        echo "[aod] Warning: Could not detect repository owner. Board setup skipped." >&2
        return 0
    }

    if [[ -z "$owner" ]]; then
        echo "[aod] Warning: Repository owner is empty. Board setup skipped." >&2
        return 0
    fi

    # Detect owner type (User vs Organization)
    local owner_type
    owner_type=$(gh api "users/$owner" --jq '.type' 2>/dev/null) || {
        echo "[aod] Warning: Could not detect owner type for '$owner'. Board setup skipped." >&2
        return 0
    }

    # --- Section 2: Board creation (idempotent) ---

    local project_number=""
    local project_id=""
    local board_title=""

    # If AOD_BOARD is set, use it directly (skips title-based discovery)
    if [[ -n "${AOD_BOARD:-}" ]]; then
        project_number="$AOD_BOARD"
        echo "[aod] Board setup: owner=$owner (type=$owner_type), using AOD_BOARD=$project_number" >&2
        board_title=$(gh project view "$project_number" --owner "$owner" --format json --jq '.title' 2>/dev/null) || board_title="project-$project_number"
        project_id=$(gh project view "$project_number" --owner "$owner" --format json --jq '.id' 2>/dev/null) || {
            echo "[aod] Warning: Could not find project #$project_number for owner '$owner'. Board setup skipped." >&2
            return 0
        }
    else
        # Auto-detect: try "{repo}-backlog", then "AOD Backlog", then create
        local repo_name
        repo_name=$(gh repo view --json name --jq '.name' 2>/dev/null) || repo_name=""
        board_title="AOD Backlog"
        local repo_title=""
        if [[ -n "$repo_name" ]]; then
            repo_title="${repo_name}-backlog"
        fi

        local existing_board
        existing_board=$(gh project list --owner "$owner" --format json 2>/dev/null) || {
            echo "[aod] Warning: Could not list projects for '$owner'. Board setup skipped." >&2
            return 0
        }

        # First try {repo}-backlog, then fall back to "AOD Backlog"
        if [[ -n "$repo_title" ]]; then
            project_number=$(echo "$existing_board" | jq -r --arg title "$repo_title" '.projects[] | select(.title == $title) | .number' 2>/dev/null | head -1)
            if [[ -n "$project_number" && "$project_number" != "null" ]]; then
                board_title="$repo_title"
            fi
        fi
        if [[ -z "$project_number" || "$project_number" == "null" ]]; then
            project_number=$(echo "$existing_board" | jq -r --arg title "AOD Backlog" '.projects[] | select(.title == $title) | .number' 2>/dev/null | head -1)
            if [[ -n "$project_number" && "$project_number" != "null" ]]; then
                board_title="AOD Backlog"
            fi
        fi

        echo "[aod] Board setup: owner=$owner (type=$owner_type), board=$board_title" >&2
    fi

    if [[ -n "$project_number" && "$project_number" != "null" && -n "$project_id" && "$project_id" != "null" ]]; then
        # Reuse existing board (AOD_BOARD path already resolved project_id)
        echo "[aod] Found existing '$board_title' board (project #$project_number). Reusing." >&2
    elif [[ -n "$project_number" && "$project_number" != "null" ]]; then
        # Reuse existing board (title discovery path — resolve project_id)
        echo "[aod] Found existing '$board_title' board (project #$project_number). Reusing." >&2
        project_id=$(gh project view "$project_number" --owner "$owner" --format json --jq '.id' 2>/dev/null) || {
            echo "[aod] Warning: Could not get project ID for board #$project_number. Board setup skipped." >&2
            return 0
        }
    else
        # Create new board
        echo "[aod] Creating '$board_title' board..." >&2
        local create_result
        create_result=$(gh project create --owner "$owner" --title "$board_title" --format json 2>/dev/null) || {
            echo "[aod] Warning: Failed to create Projects board. Board setup skipped." >&2
            return 0
        }

        project_number=$(echo "$create_result" | jq -r '.number' 2>/dev/null)
        project_id=$(echo "$create_result" | jq -r '.id' 2>/dev/null)

        if [[ -z "$project_number" || "$project_number" == "null" ]]; then
            echo "[aod] Warning: Could not parse project number from create response. Board setup skipped." >&2
            return 0
        fi

        echo "[aod] Created board #$project_number." >&2
    fi

    if [[ -z "$project_id" || "$project_id" == "null" ]]; then
        echo "[aod] Warning: Could not resolve project ID. Board setup skipped." >&2
        return 0
    fi

    # --- Section 3: Status field configuration ---

    # Get Status field ID
    local fields_json
    fields_json=$(gh project field-list "$project_number" --owner "$owner" --format json 2>/dev/null) || {
        echo "[aod] Warning: Could not list project fields. Board setup skipped." >&2
        return 0
    }

    local status_field_id=""
    local status_field_name="Status"

    # Find the built-in Status field (type: ProjectV2SingleSelectField, name: Status)
    status_field_id=$(echo "$fields_json" | jq -r '.fields[] | select(.name == "Status" and .type == "ProjectV2SingleSelectField") | .id' 2>/dev/null | head -1)

    if [[ -z "$status_field_id" || "$status_field_id" == "null" ]]; then
        echo "[aod] Warning: Could not find Status field. Board setup skipped." >&2
        return 0
    fi

    echo "[aod] Configuring Status field ($status_field_id) with AOD lifecycle stages..." >&2

    # Update Status field options via GraphQL mutation
    local mutation_result
    mutation_result=$(gh api graphql -f query='
mutation($fieldId: ID!) {
  updateProjectV2Field(input: {
    fieldId: $fieldId,
    singleSelectOptions: [
      {name: "Discover", color: BLUE, description: ""},
      {name: "Define", color: PURPLE, description: ""},
      {name: "Plan", color: YELLOW, description: ""},
      {name: "Build", color: ORANGE, description: ""},
      {name: "Deliver", color: GREEN, description: ""},
      {name: "Document", color: PINK, description: ""},
      {name: "Done", color: GRAY, description: ""}
    ]
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
        options { id name }
      }
    }
  }
}' -f fieldId="$status_field_id" 2>/dev/null) || {
        # Fallback: create custom "AOD Stage" field if built-in Status mutation fails
        echo "[aod] Warning: Could not update built-in Status field. Attempting custom 'AOD Stage' field..." >&2
        status_field_name="AOD Stage"

        local fallback_result
        fallback_result=$(gh project field-create "$project_number" --owner "$owner" \
            --name "AOD Stage" --data-type "SINGLE_SELECT" \
            --single-select-options "Discover,Define,Plan,Build,Deliver,Document,Done" --format json 2>/dev/null) || {
            echo "[aod] Warning: Failed to create custom 'AOD Stage' field. Board setup skipped." >&2
            return 0
        }

        # Re-read fields to get the new field ID and options
        fields_json=$(gh project field-list "$project_number" --owner "$owner" --format json 2>/dev/null) || {
            echo "[aod] Warning: Could not re-read fields after creating custom field. Board setup skipped." >&2
            return 0
        }

        status_field_id=$(echo "$fields_json" | jq -r '.fields[] | select(.name == "AOD Stage" and .type == "ProjectV2SingleSelectField") | .id' 2>/dev/null | head -1)

        if [[ -z "$status_field_id" || "$status_field_id" == "null" ]]; then
            echo "[aod] Warning: Could not find newly created 'AOD Stage' field. Board setup skipped." >&2
            return 0
        fi

        # Build mutation_result-compatible JSON from field-list for option parsing
        mutation_result=$(echo "$fields_json" | jq '{data: {updateProjectV2Field: {projectV2Field: (.fields[] | select(.name == "AOD Stage"))}}}' 2>/dev/null)
    }

    # Parse option IDs from mutation response
    local discover_id define_id plan_id build_id deliver_id document_id done_id

    discover_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Discover") | .id' 2>/dev/null)
    define_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Define") | .id' 2>/dev/null)
    plan_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Plan") | .id' 2>/dev/null)
    build_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Build") | .id' 2>/dev/null)
    deliver_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Deliver") | .id' 2>/dev/null)
    document_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Document") | .id' 2>/dev/null)
    done_id=$(echo "$mutation_result" | jq -r '.data.updateProjectV2Field.projectV2Field.options[] | select(.name == "Done") | .id' 2>/dev/null)

    # Validate all option IDs are non-empty
    if [[ -z "$discover_id" || -z "$define_id" || -z "$plan_id" || -z "$build_id" || -z "$deliver_id" || -z "$document_id" || -z "$done_id" ]]; then
        echo "[aod] Warning: Could not parse all 7 option IDs from Status field configuration. Board setup skipped." >&2
        return 0
    fi

    echo "[aod] Status field configured with 7 AOD stages." >&2

    # --- Section 4: Cache writing and cleanup ---

    # Write cache JSON to .aod/memory/github-project.json
    local cache_json
    cache_json=$(jq -n \
        --argjson project_number "$project_number" \
        --arg project_id "$project_id" \
        --arg owner "$owner" \
        --arg owner_type "$owner_type" \
        --arg status_field_id "$status_field_id" \
        --arg status_field_name "$status_field_name" \
        --arg discover_id "$discover_id" \
        --arg define_id "$define_id" \
        --arg plan_id "$plan_id" \
        --arg build_id "$build_id" \
        --arg deliver_id "$deliver_id" \
        --arg document_id "$document_id" \
        --arg done_id "$done_id" \
        --arg board_title "$board_title" \
        --arg created_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{
            project_number: $project_number,
            project_id: $project_id,
            owner: $owner,
            owner_type: $owner_type,
            board_title: $board_title,
            status_field_id: $status_field_id,
            status_field_name: $status_field_name,
            status_options: {
                Discover: $discover_id,
                Define: $define_id,
                Plan: $plan_id,
                Build: $build_id,
                Deliver: $deliver_id,
                Document: $document_id,
                Done: $done_id
            },
            created_at: $created_at
        }')

    mkdir -p "$(dirname "$AOD_BOARD_CACHE")"
    echo "$cache_json" > "$AOD_BOARD_CACHE"

    # Link board to the repo so it appears in the repo's Projects tab
    if [[ -n "${repo_name:-}" ]]; then
        local repo_full
        repo_full=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null) || repo_full=""
        if [[ -n "$repo_full" ]]; then
            gh project link "$project_number" --owner "$owner" --repo "$repo_full" 2>/dev/null && \
                echo "[aod] Linked board to repo $repo_full." >&2 || \
                echo "[aod] Warning: Could not link board to repo. Link manually from the repo's Projects tab." >&2
        fi
    fi

    # Remove hint marker on successful setup
    rm -f "$AOD_HINT_MARKER"

    # Clear version/scope warning markers (setup success proves they're no longer relevant)
    rm -f "$AOD_GH_VERSION_WARNED"
    rm -f "$AOD_GH_SCOPE_WARNED"

    # Reset session guard so next check uses fresh cache
    _AOD_BOARD_CHECKED=0

    echo "[aod] Board setup complete. Cache written to $AOD_BOARD_CACHE" >&2
    echo "$cache_json"

    return 0
}

# Add an issue to the GitHub Projects board and set its Status column
# Args:
#   $1 = issue_url (required, full GitHub issue URL)
#   $2 = stage (required, one of: discover, define, plan, build, deliver, document, done)
# Returns: 0 always (graceful degradation), item ID on stdout on success
# Stderr: warnings on any failure
aod_gh_add_to_board() {
    local issue_url="${1:-}"
    local stage="${2:-}"

    if [[ -z "$issue_url" || -z "$stage" ]]; then
        echo "[aod] Warning: Missing issue_url or stage for board add. Skipping." >&2
        return 0
    fi

    # Check board availability (prereqs + cache); skip silently if unavailable
    if ! aod_gh_check_board; then
        return 0
    fi

    # --- Read cache values ---

    local project_number project_id owner status_field_id

    project_number=$(jq -r '.project_number' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read project_number from board cache. Board add skipped." >&2
        return 0
    }

    project_id=$(jq -r '.project_id' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read project_id from board cache. Board add skipped." >&2
        return 0
    }

    owner=$(jq -r '.owner' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read owner from board cache. Board add skipped." >&2
        return 0
    }

    status_field_id=$(jq -r '.status_field_id' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read status_field_id from board cache. Board add skipped." >&2
        return 0
    }

    # Defense-in-depth: verify cache values are non-empty before API calls
    if [[ -z "$project_number" || "$project_number" == "null" || -z "$project_id" || "$project_id" == "null" || -z "$owner" || "$owner" == "null" || -z "$status_field_id" || "$status_field_id" == "null" ]]; then
        echo "[aod] Warning: Board cache contains empty values. Board add skipped — run 'aod_gh_setup_board' to reconfigure." >&2
        return 0
    fi

    # --- Map stage to option ID ---

    local column_name
    column_name=$(aod_stage_to_column "$stage")

    if [[ -z "$column_name" ]]; then
        echo "[aod] Warning: Unknown stage '$stage'. Valid stages: discover, define, plan, build, deliver, done. Board add skipped." >&2
        return 0
    fi

    local option_id
    option_id=$(jq -r ".status_options.\"$column_name\"" "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read option ID for column '$column_name' from board cache. Board add skipped." >&2
        return 0
    }

    if [[ -z "$option_id" || "$option_id" == "null" ]]; then
        echo "[aod] Warning: No option ID found for stage '$stage' (column '$column_name'). Board add skipped." >&2
        return 0
    fi

    # --- Add issue to board ---

    local add_result item_add_stderr
    item_add_stderr=$(mktemp 2>/dev/null || echo "/tmp/aod-add-stderr-$$")
    add_result=$(gh project item-add "$project_number" --owner "$owner" --url "$issue_url" --format json 2>"$item_add_stderr") || {
        local add_err
        add_err=$(cat "$item_add_stderr" 2>/dev/null)
        rm -f "$item_add_stderr"
        if echo "$add_err" | grep -qiE 'rate.limit|abuse|secondary|retry.after|HTTP 403|API rate'; then
            echo "[aod] Warning: GitHub API rate limit hit. Board add skipped — retry in a few minutes." >&2
        elif echo "$add_err" | grep -qiE 'Could not resolve|not found|404|project.*not.*found'; then
            echo "[aod] Warning: Projects board not found (deleted?). Board cache cleared — run 'aod_gh_setup_board' to reconfigure." >&2
            rm -f "$AOD_BOARD_CACHE"
            _AOD_BOARD_CHECKED=0
        else
            echo "[aod] Warning: Failed to add issue to Projects board. Board add skipped." >&2
        fi
        return 0
    }
    rm -f "$item_add_stderr"

    local item_id
    item_id=$(printf '%s\n' "$add_result" | jq -r '.id' 2>/dev/null)

    if [[ -z "$item_id" || "$item_id" == "null" ]]; then
        echo "[aod] Warning: Could not parse item ID from board add response. Board status update skipped." >&2
        return 0
    fi

    # --- Set Status column ---

    local edit_stderr
    edit_stderr=$(mktemp 2>/dev/null || echo "/tmp/aod-edit-stderr-$$")
    gh project item-edit \
        --project-id "$project_id" \
        --id "$item_id" \
        --field-id "$status_field_id" \
        --single-select-option-id "$option_id" 2>"$edit_stderr" || {
        local edit_err
        edit_err=$(cat "$edit_stderr" 2>/dev/null)
        rm -f "$edit_stderr"
        if echo "$edit_err" | grep -qiE 'rate.limit|abuse|secondary|retry.after|HTTP 403|API rate'; then
            echo "[aod] Warning: GitHub API rate limit hit. Board status update skipped — retry in a few minutes." >&2
        else
            echo "[aod] Warning: Added issue to board but failed to set Status to '$column_name'. Continuing." >&2
        fi
        echo "$item_id"
        return 0
    }
    rm -f "$edit_stderr"

    echo "[aod] Added issue to board and set Status to '$column_name'." >&2
    echo "$item_id"

    return 0
}

# Move an issue to a new Status column on the GitHub Projects board
# If the issue is not on the board, auto-adds it via aod_gh_add_to_board.
# Optimization: gh project item-add is idempotent — returns existing item
# without duplicating — so we skip the expensive item-list search.
# Args:
#   $1 = issue_url (required, full GitHub issue URL)
#   $2 = new_stage (required, one of: discover, define, plan, build, deliver, document, done)
# Returns: 0 always (graceful degradation)
# Stderr: warnings on any failure
aod_gh_move_on_board() {
    local issue_url="${1:-}"
    local new_stage="${2:-}"

    if [[ -z "$issue_url" || -z "$new_stage" ]]; then
        echo "[aod] Warning: Missing issue_url or new_stage for board move. Skipping." >&2
        return 0
    fi

    # Check board availability (prereqs + cache); skip silently if unavailable
    if ! aod_gh_check_board; then
        return 0
    fi

    # --- Read cache values ---

    local project_number project_id owner status_field_id

    project_number=$(jq -r '.project_number' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read project_number from board cache. Board move skipped." >&2
        return 0
    }

    project_id=$(jq -r '.project_id' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read project_id from board cache. Board move skipped." >&2
        return 0
    }

    owner=$(jq -r '.owner' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read owner from board cache. Board move skipped." >&2
        return 0
    }

    status_field_id=$(jq -r '.status_field_id' "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read status_field_id from board cache. Board move skipped." >&2
        return 0
    }

    # Defense-in-depth: verify cache values are non-empty before API calls
    if [[ -z "$project_number" || "$project_number" == "null" || -z "$project_id" || "$project_id" == "null" || -z "$owner" || "$owner" == "null" || -z "$status_field_id" || "$status_field_id" == "null" ]]; then
        echo "[aod] Warning: Board cache contains empty values. Board move skipped — run 'aod_gh_setup_board' to reconfigure." >&2
        return 0
    fi

    # --- Map new_stage to option ID ---

    local column_name
    column_name=$(aod_stage_to_column "$new_stage")

    if [[ -z "$column_name" ]]; then
        echo "[aod] Warning: Unknown stage '$new_stage'. Valid stages: discover, define, plan, build, deliver, done. Board move skipped." >&2
        return 0
    fi

    local option_id
    option_id=$(jq -r ".status_options.\"$column_name\"" "$AOD_BOARD_CACHE" 2>/dev/null) || {
        echo "[aod] Warning: Could not read option ID for column '$column_name' from board cache. Board move skipped." >&2
        return 0
    }

    if [[ -z "$option_id" || "$option_id" == "null" ]]; then
        echo "[aod] Warning: No option ID found for stage '$new_stage' (column '$column_name'). Board move skipped." >&2
        return 0
    fi

    # --- Add-or-find item on board (idempotent) ---
    # gh project item-add is idempotent: if the issue is already on the board,
    # it returns the existing item without creating a duplicate. This saves
    # the expensive item-list search.

    local add_result move_add_stderr
    move_add_stderr=$(mktemp 2>/dev/null || echo "/tmp/aod-move-stderr-$$")
    add_result=$(gh project item-add "$project_number" --owner "$owner" --url "$issue_url" --format json 2>"$move_add_stderr") || {
        local move_err
        move_err=$(cat "$move_add_stderr" 2>/dev/null)
        rm -f "$move_add_stderr"
        if echo "$move_err" | grep -qiE 'rate.limit|abuse|secondary|retry.after|HTTP 403|API rate'; then
            echo "[aod] Warning: GitHub API rate limit hit. Board move skipped — retry in a few minutes." >&2
        elif echo "$move_err" | grep -qiE 'Could not resolve|not found|404|project.*not.*found'; then
            echo "[aod] Warning: Projects board not found (deleted?). Board cache cleared — run 'aod_gh_setup_board' to reconfigure." >&2
            rm -f "$AOD_BOARD_CACHE"
            _AOD_BOARD_CHECKED=0
        else
            echo "[aod] Warning: Failed to add/find issue on Projects board. Board move skipped." >&2
        fi
        return 0
    }
    rm -f "$move_add_stderr"

    local item_id
    item_id=$(printf '%s\n' "$add_result" | jq -r '.id' 2>/dev/null)

    if [[ -z "$item_id" || "$item_id" == "null" ]]; then
        echo "[aod] Warning: Could not parse item ID from board response. Board move skipped." >&2
        return 0
    fi

    # --- Update Status column ---

    local move_edit_stderr
    move_edit_stderr=$(mktemp 2>/dev/null || echo "/tmp/aod-move-edit-stderr-$$")
    gh project item-edit \
        --project-id "$project_id" \
        --id "$item_id" \
        --field-id "$status_field_id" \
        --single-select-option-id "$option_id" 2>"$move_edit_stderr" || {
        local move_edit_err
        move_edit_err=$(cat "$move_edit_stderr" 2>/dev/null)
        rm -f "$move_edit_stderr"
        if echo "$move_edit_err" | grep -qiE 'rate.limit|abuse|secondary|retry.after|HTTP 403|API rate'; then
            echo "[aod] Warning: GitHub API rate limit hit. Board status update skipped — retry in a few minutes." >&2
        else
            echo "[aod] Warning: Found issue on board but failed to update Status to '$column_name'. Continuing." >&2
        fi
        return 0
    }
    rm -f "$move_edit_stderr"

    echo "[aod] Moved issue to '$column_name' on board." >&2

    return 0
}

# Check if gh CLI is available and authenticated with a remote
# Returns: 0 if available, 1 if not (with warning on stderr)
aod_gh_check_available() {
    if ! command -v gh &>/dev/null; then
        echo "[aod] Warning: gh CLI not found. GitHub operations skipped." >&2
        return 1
    fi

    if ! gh auth status &>/dev/null; then
        echo "[aod] Warning: gh CLI not authenticated. Run 'gh auth login'. GitHub operations skipped." >&2
        return 1
    fi

    # Check if we have a remote configured
    if ! git remote get-url origin &>/dev/null; then
        echo "[aod] Warning: No git remote 'origin' configured. GitHub operations skipped." >&2
        return 1
    fi

    # GH_REPO is now exported at source time (top of file).
    # No need to set it here — kept as comment for traceability.

    return 0
}

# Find an existing GitHub Issue by number or title match
# Args: $1 = search query (issue number, #NNN, title, or [IDEA-NNN] tag)
# Returns: issue number on stdout, or empty string if not found
aod_gh_find_issue() {
    local search_query="${1:-}"

    if [[ -z "$search_query" ]]; then
        return 0
    fi

    # Numeric input bypasses API validation for performance — caller is
    # responsible for providing a valid issue number
    local stripped
    stripped=$(echo "$search_query" | sed 's/^#//')
    if echo "$stripped" | grep -q '^[0-9][0-9]*$'; then
        echo "$stripped"
        return 0
    fi

    # Fallback: search by exact title or tag in issue title
    local result
    result=$(gh issue list --search "\"$search_query\" in:title" --json number --limit 1 2>/dev/null) || return 0

    # Extract issue number from JSON
    local issue_number
    issue_number=$(echo "$result" | grep -o '"number":[0-9]*' | head -1 | cut -d: -f2)

    if [[ -n "$issue_number" && "$issue_number" != "null" ]]; then
        echo "$issue_number"
    fi
}

# Create a GitHub Issue with a stage:* label, or update if duplicate found
# Args:
#   $1 = title (required)
#   $2 = body (required, markdown)
#   $3 = stage (required, one of: discover, define, plan, build, deliver, document, done)
#   $4 = issue_type (optional, e.g., "idea" or "retro" — adds type:* label)
# Returns: 0 always (graceful degradation), issue number on stdout if created
aod_gh_create_issue() {
    local title="${1:-}"
    local body="${2:-}"
    local stage="${3:-discover}"
    local issue_type="${4:-}"

    if [[ -z "$title" ]]; then
        echo "[aod] Warning: No title provided for GitHub Issue. Skipping." >&2
        return 0
    fi

    if ! aod_gh_check_available; then
        return 0
    fi

    local label="stage:${stage}"

    # Ensure type:* label exists (idempotent — no error if already present)
    if [[ -n "$issue_type" ]]; then
        gh label create "type:${issue_type}" --force 2>/dev/null || true
    fi

    # Duplicate detection: title-based matching (sole mechanism)
    local existing_number=""
    existing_number=$(aod_gh_find_issue "$title")

    if [[ -n "$existing_number" ]]; then
        # Update existing issue instead of creating duplicate
        echo "[aod] Found existing Issue #${existing_number} — updating instead of creating duplicate." >&2
        if [[ -n "$issue_type" ]]; then
            gh issue edit "$existing_number" --body "$body" --add-label "$label" --add-label "type:${issue_type}" 2>/dev/null || {
                echo "[aod] Warning: Failed to update Issue #${existing_number}. Continuing." >&2
            }
        else
            gh issue edit "$existing_number" --body "$body" --add-label "$label" 2>/dev/null || {
                echo "[aod] Warning: Failed to update Issue #${existing_number}. Continuing." >&2
            }
        fi
        # Remove old stage labels
        for old_label in "${AOD_STAGE_LABELS[@]}"; do
            if [[ "$old_label" != "$label" ]]; then
                gh issue edit "$existing_number" --remove-label "$old_label" 2>/dev/null || true
            fi
        done

        # Sync to Projects board (non-blocking)
        local existing_url
        existing_url=$(gh issue view "$existing_number" --json url --jq '.url' 2>/dev/null) || true
        if [[ -n "$existing_url" ]]; then
            aod_gh_add_to_board "$existing_url" "$stage" >/dev/null || true
        fi

        echo "$existing_number"
        return 0
    fi

    # Create new issue
    local issue_number
    if [[ -n "$issue_type" ]]; then
        issue_number=$(gh issue create --title "$title" --body "$body" --label "$label" --label "type:${issue_type}" 2>/dev/null | grep -o '[0-9]*$') || {
            echo "[aod] Warning: Failed to create GitHub Issue. Continuing without tracking." >&2
            return 0
        }
    else
        issue_number=$(gh issue create --title "$title" --body "$body" --label "$label" 2>/dev/null | grep -o '[0-9]*$') || {
            echo "[aod] Warning: Failed to create GitHub Issue. Continuing without tracking." >&2
            return 0
        }
    fi

    if [[ -n "$issue_number" ]]; then
        echo "[aod] Created Issue #${issue_number} with label ${label}." >&2

        # Sync to Projects board (non-blocking)
        local issue_url
        issue_url=$(gh issue view "$issue_number" --json url --jq '.url' 2>/dev/null) || true
        if [[ -n "$issue_url" ]]; then
            aod_gh_add_to_board "$issue_url" "$stage" >/dev/null || true
        fi

        echo "$issue_number"
    fi

    return 0
}

# Update a GitHub Issue's stage label (remove old stage:* labels, add new one)
# Args:
#   $1 = issue number (required)
#   $2 = new stage (required, one of: discover, define, plan, build, deliver, document, done)
# Returns: 0 always (graceful degradation)
aod_gh_update_stage() {
    local issue_number="${1:-}"
    local new_stage="${2:-}"

    if [[ -z "$issue_number" || -z "$new_stage" ]]; then
        echo "[aod] Warning: Missing issue number or stage for label update. Skipping." >&2
        return 0
    fi

    if ! aod_gh_check_available; then
        return 0
    fi

    local new_label="stage:${new_stage}"

    # Remove all existing stage:* labels, then add the new one
    for old_label in "${AOD_STAGE_LABELS[@]}"; do
        if [[ "$old_label" != "$new_label" ]]; then
            gh issue edit "$issue_number" --remove-label "$old_label" 2>/dev/null || true
        fi
    done

    gh issue edit "$issue_number" --add-label "$new_label" 2>/dev/null || {
        echo "[aod] Warning: Failed to update stage label on Issue #${issue_number}. Continuing." >&2
    }

    # Sync to Projects board — preserve warnings (don't swallow stderr)
    local issue_url
    issue_url=$(gh issue view "$issue_number" --json url --jq '.url' 2>/dev/null) || true
    if [[ -n "$issue_url" ]]; then
        aod_gh_move_on_board "$issue_url" "$new_stage" || true
    fi

    return 0
}

# Reconcile all issues (open + closed): ensure board column matches stage:* label
# Compares each issue's label to its board Status, and fixes mismatches.
# Args: none
# Returns: 0 always (graceful degradation)
# Output: stderr messages for each mismatch found and fixed
aod_gh_reconcile_board() {
    if ! aod_gh_check_available; then
        return 0
    fi

    if ! aod_gh_check_board; then
        echo "[aod] Warning: Board not available. Reconciliation skipped." >&2
        return 0
    fi

    local owner project_number
    owner=$(jq -r '.owner' "$AOD_BOARD_CACHE" 2>/dev/null) || { return 0; }
    project_number=$(jq -r '.project_number' "$AOD_BOARD_CACHE" 2>/dev/null) || { return 0; }

    # Fetch all issues (open + closed) with stage:* labels
    local open_json closed_json issues_json
    open_json=$(gh issue list --json number,title,labels,url --state open --limit 200 2>/dev/null) || open_json="[]"
    closed_json=$(gh issue list --json number,title,labels,url --state closed --limit 200 2>/dev/null) || closed_json="[]"
    # Merge both lists
    issues_json=$(python3 -c "
import json, sys
open_items = json.loads(sys.argv[1])
closed_items = json.loads(sys.argv[2])
print(json.dumps(open_items + closed_items))
" "$open_json" "$closed_json" 2>/dev/null) || {
        echo "[aod] Warning: Failed to fetch issues for reconciliation." >&2
        return 0
    }

    # Fetch all board items with their status
    local board_json
    board_json=$(gh project item-list "$project_number" --owner "$owner" --format json --limit 200 2>/dev/null) || {
        echo "[aod] Warning: Failed to fetch board items for reconciliation." >&2
        return 0
    }

    local fixed=0
    local checked=0
    local mismatches=""

    # For each open issue with a stage:* label, check board column
    while IFS='|' read -r number url stage_label; do
        [[ -z "$number" ]] && continue
        checked=$((checked + 1))

        # Extract expected stage from label (e.g., "stage:deliver" → "deliver")
        local expected_stage="${stage_label#stage:}"
        local expected_column
        expected_column=$(aod_stage_to_column "$expected_stage")
        [[ -z "$expected_column" ]] && continue

        # Find this issue on the board and get its current Status
        local board_status
        board_status=$(printf '%s\n' "$board_json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data.get('items', []):
    content = item.get('content', {})
    if content.get('number') == ${number} and content.get('type') == 'Issue':
        print(item.get('status', ''))
        break
" 2>/dev/null) || board_status=""

        if [[ -z "$board_status" ]]; then
            # Issue not on board — add it
            aod_gh_move_on_board "$url" "$expected_stage" || true
            fixed=$((fixed + 1))
            mismatches="${mismatches}\n  #${number}: not on board → ${expected_column}"
        elif [[ "$board_status" != "$expected_column" ]]; then
            # Board column doesn't match label — fix it
            aod_gh_move_on_board "$url" "$expected_stage" || true
            fixed=$((fixed + 1))
            mismatches="${mismatches}\n  #${number}: ${board_status} → ${expected_column}"
        fi
    done < <(printf '%s\n' "$issues_json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for issue in data:
    labels = [l['name'] for l in issue.get('labels', [])]
    stage_labels = [l for l in labels if l.startswith('stage:')]
    if stage_labels:
        print(f\"{issue['number']}|{issue['url']}|{stage_labels[0]}\")
" 2>/dev/null)

    if [[ $fixed -gt 0 ]]; then
        echo "[aod] Board reconciliation: ${fixed} mismatch(es) fixed out of ${checked} checked.$(printf '%b' "$mismatches")" >&2
    else
        echo "[aod] Board reconciliation: ${checked} issues checked, all in sync." >&2
    fi

    return 0
}
