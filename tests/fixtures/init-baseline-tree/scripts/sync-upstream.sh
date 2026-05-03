#!/usr/bin/env bash
# scripts/sync-upstream.sh — Sync upstream AOD template changes into adopter projects
#
# Provides 4 subcommands:
#   setup    — Configure the upstream AOD template repository as a git remote
#   check    — Detect and display categorized upstream changes
#   merge    — Safely merge upstream changes with backup and .aod/memory/ protection
#   validate — Post-sync integrity checks (file existence, YAML, placeholders)
#
# Usage:
#   sync-upstream.sh <subcommand> [options]
#   sync-upstream.sh setup [--url <url>]
#   sync-upstream.sh check
#   sync-upstream.sh merge [--dry-run]
#   sync-upstream.sh validate
#
# Global flags:
#   --dry-run    Preview operations without modifying files
#   --json       Output in JSON format (where supported)
#   --help       Show this help message

set -euo pipefail

# Source shared utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$REPO_ROOT/.aod/scripts/bash/common.sh" ]]; then
    source "$REPO_ROOT/.aod/scripts/bash/common.sh"
fi

# Colors (defined locally per Architect review — common.sh does not export these)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Canonical upstream URL
CANONICAL_URL="https://github.com/davidmatousek/agentic-oriented-development-kit.git"

# Global flags
DRY_RUN=false
JSON_OUTPUT=false

# Pre-scan for --json flag to ensure error messages use correct format
for arg in "$@"; do
    if [[ "$arg" == "--json" ]]; then
        JSON_OUTPUT=true
        break
    fi
done

# ============================================================================
# JSON OUTPUT HELPERS
# ============================================================================
# Factored into .aod/scripts/bash/template-json.sh (feature 129, T011).
# Local functions below are thin wrappers delegating to the factored helpers
# so behavior is preserved byte-for-byte relative to the pre-factor baseline.

# Resolve template-*.sh library locations with fallback strategies so this
# block works both when sync-upstream.sh is executed normally AND when it is
# sliced by the BATS test harness (which sources a temp copy and loses the
# original SCRIPT_DIR). Strategy: try REPO_ROOT first; fall back to
# `git rev-parse --show-toplevel` from the caller's CWD.
_aod_template_lib_dir=""
if [[ -d "$REPO_ROOT/.aod/scripts/bash" ]]; then
    _aod_template_lib_dir="$REPO_ROOT/.aod/scripts/bash"
else
    _aod_git_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "$_aod_git_root" ]] && [[ -d "$_aod_git_root/.aod/scripts/bash" ]]; then
        _aod_template_lib_dir="$_aod_git_root/.aod/scripts/bash"
    fi
    unset _aod_git_root
fi

# shellcheck source=../.aod/scripts/bash/template-json.sh
if [[ -n "$_aod_template_lib_dir" ]] && [[ -f "$_aod_template_lib_dir/template-json.sh" ]]; then
    source "$_aod_template_lib_dir/template-json.sh"
fi

# shellcheck source=../.aod/scripts/bash/template-validate.sh
if [[ -n "$_aod_template_lib_dir" ]] && [[ -f "$_aod_template_lib_dir/template-validate.sh" ]]; then
    source "$_aod_template_lib_dir/template-validate.sh"
fi
unset _aod_template_lib_dir

# Escape special characters for JSON string values
# Handles: backslashes, double quotes, tabs
# Note: Newlines in file paths are documented as unsupported (spec limitation)
# Delegates to aod_template_json_escape (T011 factor-out). When the library
# could not be located (e.g., sliced-script test harness with a tmp REPO_ROOT),
# the inline fallback preserves the exact pre-factor behavior.
if ! declare -f aod_template_json_escape >/dev/null 2>&1; then
    aod_template_json_escape() {
        printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g'
    }
fi

json_escape() {
    aod_template_json_escape "$1"
}

# Output JSON to stdout when JSON_OUTPUT is enabled
# Usage: json_output '{"key": "value"}'
# Retained as a thin wrapper (gating behavior is caller-side and not factored).
json_output() {
    local json="$1"
    if $JSON_OUTPUT; then
        printf '%s\n' "$json"
    fi
}

# ============================================================================
# FILE OWNERSHIP CATEGORIES
# ============================================================================

# Classify a file path into an ownership category.
# Uses case-statement pattern for bash 3.2 compatibility (no associative arrays).
file_category() {
    local path="$1"
    case "$path" in
        .claude/skills/*)       echo "Skills" ;;
        .claude/rules/*)        echo "Rules" ;;
        .claude/agents/*)       echo "Agents" ;;
        .claude/commands/*)     echo "Commands" ;;
        .claude/lib/*)          echo "Scripts" ;;
        .claude/config/*)       echo "Config" ;;
        scripts/*)              echo "Scripts" ;;
        .aod/scripts/*)         echo "Scripts" ;;
        .aod/templates/*)       echo "Templates" ;;
        docs/core_principles/*) echo "Docs" ;;
        docs/standards/*)       echo "Docs" ;;
        docs/architecture/*)    echo "Docs" ;;
        docs/devops/*)          echo "Docs" ;;
        docs/guides/*)          echo "Docs" ;;
        docs/product/*)         echo "Docs" ;;
        docs/testing/*)         echo "Docs" ;;
        docs/*)                 echo "Docs" ;;
        CLAUDE.md)              echo "Core" ;;
        Makefile)               echo "Core" ;;
        .gitignore)             echo "Core" ;;
        LICENSE)                echo "Core" ;;
        .env.example)           echo "Core" ;;
        MIGRATION.md)           echo "Core" ;;
        *)                      echo "Other" ;;
    esac
}

# ============================================================================
# USAGE / HELP
# ============================================================================

show_help() {
    cat <<'HELPEOF'
Usage: sync-upstream.sh <subcommand> [options]

Push local template improvements back to the public PLSK repo.
Direction: user → PLSK.

This is the opposite direction of scripts/update.sh (PLSK → user), which
applies upstream template updates to your adopter project. Use /aod.update
(or `make update`) for that direction.

Subcommands:
  setup      Configure the upstream remote (one-time)
  check      Show what changed upstream since last sync
  merge      Safely merge upstream changes (creates backup)
  validate   Post-sync integrity checks

Global Options:
  --dry-run  Preview without making changes
  --json     Output in JSON format (where supported)
  --help     Show this help message

Examples:
  # First-time setup
  sync-upstream.sh setup

  # Setup with custom upstream URL
  sync-upstream.sh setup --url https://github.com/myorg/my-template.git

  # Check for upstream changes
  sync-upstream.sh check

  # Preview what a merge would do
  sync-upstream.sh merge --dry-run

  # Merge upstream changes
  sync-upstream.sh merge

  # Validate project integrity after merge
  sync-upstream.sh validate

Documentation:
  See docs/guides/UPSTREAM_SYNC.md for the full step-by-step guide.
  For the opposite direction (PLSK → user), see:
    - /aod.update slash command
    - docs/guides/DOWNSTREAM_UPDATE.md
HELPEOF
}

# ============================================================================
# SUBCOMMAND: setup
# ============================================================================

cmd_setup() {
    local custom_url=""

    # JSON output tracking variables (Wave 2: T012)
    local setup_status=""
    local setup_remote="upstream"
    local setup_url=""

    # Parse setup-specific flags
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --url)
                if [[ $# -lt 2 ]]; then
                    echo -e "${RED}Error: --url requires a value${NC}" >&2
                    return 1
                fi
                custom_url="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Error: Unknown option for setup: $1${NC}" >&2
                return 1
                ;;
        esac
    done

    local url="${custom_url:-$CANONICAL_URL}"
    setup_url="$url"

    # Validate URL format
    if [[ -n "$custom_url" ]]; then
        if [[ ! "$custom_url" =~ ^https:// ]] && [[ ! "$custom_url" =~ ^git@ ]]; then
            echo -e "${RED}Error: URL must start with https:// or git@${NC}" >&2
            echo "  Example: https://github.com/org/repo.git" >&2
            echo "  Example: git@github.com:org/repo.git" >&2
            return 1
        fi
    fi

    # Check if upstream remote already exists
    if git remote get-url upstream >/dev/null 2>&1; then
        local existing_url
        existing_url=$(git remote get-url upstream)
        setup_status="already_configured"
        setup_url="$existing_url"

        # JSON output for already_configured (T013)
        if $JSON_OUTPUT; then
            json_output "{\"schema_version\":\"1.0\",\"status\":\"already_configured\",\"remote\":\"$setup_remote\",\"url\":\"$(json_escape "$setup_url")\"}"
            return 0
        fi

        echo -e "${GREEN}Upstream remote already configured${NC}"
        echo "  URL: $existing_url"

        # Check if URL matches
        if [[ -n "$custom_url" ]] && [[ "$existing_url" != "$custom_url" ]]; then
            echo -e "${YELLOW}Warning: Current URL differs from requested URL${NC}"
            echo "  Current:   $existing_url"
            echo "  Requested: $custom_url"
            echo ""
            echo "  To update: git remote set-url upstream $custom_url"
        fi
        return 0
    fi

    # Add upstream remote
    if $DRY_RUN; then
        setup_status="dry_run"

        # JSON output for dry_run (T013)
        if $JSON_OUTPUT; then
            json_output "{\"schema_version\":\"1.0\",\"status\":\"dry_run\",\"remote\":\"$setup_remote\",\"url\":\"$(json_escape "$setup_url")\"}"
            return 0
        fi

        echo -e "${YELLOW}[DRY-RUN]${NC} Would add upstream remote:"
        echo "  git remote add upstream $url"
        echo "  git fetch upstream"
        return 0
    fi

    echo -e "${BLUE}Adding upstream remote...${NC}"
    echo "  URL: $url"
    git remote add upstream "$url"

    echo -e "${BLUE}Fetching upstream refs...${NC}"
    if ! git fetch upstream 2>&1; then
        setup_status="error"

        # JSON output for error (T013)
        if $JSON_OUTPUT; then
            json_output "{\"schema_version\":\"1.0\",\"status\":\"error\",\"remote\":\"$setup_remote\",\"url\":\"$(json_escape "$setup_url")\",\"error\":\"Failed to fetch from upstream\"}"
            return 1
        fi

        echo -e "${RED}Error: Failed to fetch from upstream${NC}" >&2
        echo "  Check that the URL is correct and you have network access." >&2
        echo "  URL: $url" >&2
        echo ""
        echo "  To remove and retry: git remote remove upstream" >&2
        return 1
    fi

    setup_status="configured"

    # JSON output for successful configuration (T013)
    if $JSON_OUTPUT; then
        json_output "{\"schema_version\":\"1.0\",\"status\":\"configured\",\"remote\":\"$setup_remote\",\"url\":\"$(json_escape "$setup_url")\"}"
        # Still run gitattributes setup even in JSON mode
        _ensure_gitattributes
        return 0
    fi

    echo -e "${GREEN}Upstream remote configured successfully${NC}"
    echo "  Remote: upstream"
    echo "  URL:    $url"
    echo ""
    echo "  Next: Run 'sync-upstream.sh check' to see available changes."

    # Add .gitattributes entries for adopter-owned paths
    _ensure_gitattributes
}

# ============================================================================
# SUBCOMMAND: check
# ============================================================================

cmd_check() {
    # Verify upstream remote exists
    if ! git remote get-url upstream >/dev/null 2>&1; then
        # JSON output for error (T006)
        if $JSON_OUTPUT; then
            json_output '{"schema_version":"1.0","status":"error","error":"No upstream remote configured"}'
        else
            echo -e "${RED}Error: No 'upstream' remote configured${NC}" >&2
            echo "  Run: sync-upstream.sh setup" >&2
        fi
        return 1
    fi

    if ! $JSON_OUTPUT; then echo -e "${BLUE}Fetching upstream changes...${NC}"; fi
    if ! git fetch upstream 2>&1; then
        if $JSON_OUTPUT; then
            json_output '{"schema_version":"1.0","status":"error","error":"Failed to fetch from upstream"}'
        else
            echo -e "${RED}Error: Failed to fetch from upstream${NC}" >&2
        fi
        return 1
    fi

    # Determine sync point
    local sync_point=""
    if sync_point=$(git merge-base HEAD upstream/main 2>/dev/null); then
        : # sync_point is set
    else
        if ! $JSON_OUTPUT; then
            echo -e "${YELLOW}Warning: No shared history found (repo may have been cloned, not forked)${NC}"
            echo "  Using upstream/main directly for comparison."
            echo ""
        fi
        sync_point=""
    fi

    # Get changed files
    local diff_target="upstream/main"
    local diff_stat=""
    if [[ -n "$sync_point" ]]; then
        diff_stat=$(git diff --stat "${sync_point}..upstream/main" 2>/dev/null || true)
    else
        diff_stat=$(git diff --stat "upstream/main" 2>/dev/null || true)
    fi

    # Handle "already up to date"
    if [[ -z "$diff_stat" ]]; then
        local sync_date=""
        if [[ -n "$sync_point" ]]; then
            sync_date=$(git log -1 --format='%ci' "$sync_point" 2>/dev/null || echo "unknown")
        else
            sync_date="N/A"
        fi

        # JSON output for up-to-date state (T005)
        if $JSON_OUTPUT; then
            json_output '{"schema_version":"1.0","status":"up_to_date","total_files":0,"categories":{}}'
            return 0
        fi

        echo -e "${GREEN}Already up to date${NC}"
        echo "  Last sync point: $sync_date"
        return 0
    fi

    # Parse and categorize changed files
    # JSON output tracking: category counts collected for Wave 3 JSON output (T004)
    local skills=0 rules=0 agents=0 commands=0 scripts=0 templates=0 docs=0 core=0 config=0 other=0
    local total=0

    while IFS= read -r line; do
        # Skip the summary line (e.g., "10 files changed, 50 insertions...")
        if echo "$line" | grep -q "files\? changed"; then
            continue
        fi
        # Skip empty lines
        if [[ -z "$line" ]]; then
            continue
        fi

        # Extract file path (first field, strip leading whitespace)
        local filepath
        filepath=$(echo "$line" | sed 's/^[[:space:]]*//' | cut -d'|' -f1 | sed 's/[[:space:]]*$//')

        if [[ -z "$filepath" ]]; then
            continue
        fi

        local cat
        cat=$(file_category "$filepath")
        total=$((total + 1))

        case "$cat" in
            Skills)    skills=$((skills + 1)) ;;
            Rules)     rules=$((rules + 1)) ;;
            Agents)    agents=$((agents + 1)) ;;
            Commands)  commands=$((commands + 1)) ;;
            Scripts)   scripts=$((scripts + 1)) ;;
            Templates) templates=$((templates + 1)) ;;
            Docs)      docs=$((docs + 1)) ;;
            Core)      core=$((core + 1)) ;;
            Config)    config=$((config + 1)) ;;
            Other)     other=$((other + 1)) ;;
        esac
    done <<EOF
$diff_stat
EOF

    # JSON output for changes available (T005)
    if $JSON_OUTPUT; then
        # Build categories object - only include non-zero counts
        local categories=""
        if [[ $skills -gt 0 ]];    then categories="${categories}\"Skills\":$skills,"; fi
        if [[ $rules -gt 0 ]];     then categories="${categories}\"Rules\":$rules,"; fi
        if [[ $agents -gt 0 ]];    then categories="${categories}\"Agents\":$agents,"; fi
        if [[ $commands -gt 0 ]];  then categories="${categories}\"Commands\":$commands,"; fi
        if [[ $scripts -gt 0 ]];   then categories="${categories}\"Scripts\":$scripts,"; fi
        if [[ $templates -gt 0 ]]; then categories="${categories}\"Templates\":$templates,"; fi
        if [[ $docs -gt 0 ]];      then categories="${categories}\"Docs\":$docs,"; fi
        if [[ $core -gt 0 ]];      then categories="${categories}\"Core\":$core,"; fi
        if [[ $config -gt 0 ]];    then categories="${categories}\"Config\":$config,"; fi
        if [[ $other -gt 0 ]];     then categories="${categories}\"Other\":$other,"; fi
        # Remove trailing comma
        categories="${categories%,}"

        json_output "{\"schema_version\":\"1.0\",\"status\":\"changes_available\",\"total_files\":$total,\"categories\":{$categories}}"
        return 0
    fi

    # Display categorized summary
    echo -e "${BLUE}Upstream changes available:${NC}"
    echo ""
    if [[ $skills -gt 0 ]];    then echo -e "  Skills:    ${GREEN}$skills files${NC}"; fi
    if [[ $rules -gt 0 ]];     then echo -e "  Rules:     ${GREEN}$rules files${NC}"; fi
    if [[ $agents -gt 0 ]];    then echo -e "  Agents:    ${GREEN}$agents files${NC}"; fi
    if [[ $commands -gt 0 ]];  then echo -e "  Commands:  ${GREEN}$commands files${NC}"; fi
    if [[ $scripts -gt 0 ]];   then echo -e "  Scripts:   ${GREEN}$scripts files${NC}"; fi
    if [[ $templates -gt 0 ]]; then echo -e "  Templates: ${GREEN}$templates files${NC}"; fi
    if [[ $docs -gt 0 ]];      then echo -e "  Docs:      ${GREEN}$docs files${NC}"; fi
    if [[ $core -gt 0 ]];      then echo -e "  Core:      ${GREEN}$core files${NC}"; fi
    if [[ $config -gt 0 ]];    then echo -e "  Config:    ${GREEN}$config files${NC}"; fi
    if [[ $other -gt 0 ]];     then echo -e "  Other:     ${GREEN}$other files${NC}"; fi
    echo ""
    echo -e "  ${BLUE}Total: $total files changed${NC}"
    echo ""
    echo "  Next: Run 'sync-upstream.sh merge --dry-run' to preview the merge."
}

# ============================================================================
# SUBCOMMAND: merge
# ============================================================================

cmd_merge() {
    # JSON output tracking variables (Wave 2: T007)
    local merge_status=""
    local merge_files_changed=0
    local merge_conflict_count=0
    local merge_conflicts=""  # Newline-separated list for bash 3.2 compatibility
    local merge_memory_preserved=false

    # --- Pre-flight checks ---

    # Check for clean working tree
    local status_output
    status_output=$(git status --porcelain 2>/dev/null)
    if [[ -n "$status_output" ]]; then
        echo -e "${RED}Error: Working tree has uncommitted changes${NC}" >&2
        echo "  Please commit or stash your changes before merging." >&2
        echo "" >&2
        echo "  git stash       # Stash changes temporarily" >&2
        echo "  git add -A && git commit -m 'WIP: save before sync'" >&2
        return 1
    fi

    # Verify upstream remote
    if ! git remote get-url upstream >/dev/null 2>&1; then
        echo -e "${RED}Error: No 'upstream' remote configured${NC}" >&2
        echo "  Run: sync-upstream.sh setup" >&2
        return 1
    fi

    # Fetch latest
    if ! $JSON_OUTPUT; then
        echo -e "${BLUE}Fetching upstream...${NC}"
        if ! git fetch upstream 2>&1; then
            echo -e "${RED}Error: Failed to fetch from upstream${NC}" >&2
            return 1
        fi
    else
        if ! git fetch upstream >/dev/null 2>&1; then
            json_output "{\"schema_version\":\"1.0\",\"status\":\"error\",\"error\":\"Failed to fetch from upstream\"}"
            return 1
        fi
    fi

    # Detect shared vs unrelated history
    local has_shared_history=true
    if ! git merge-base HEAD upstream/main >/dev/null 2>&1; then
        has_shared_history=false
    fi

    # --- Dry-run mode ---
    if $DRY_RUN; then
        merge_status="dry_run"
        if ! $JSON_OUTPUT; then
            echo -e "${YELLOW}[DRY-RUN]${NC} Previewing merge (no changes will be made)..."
            echo ""
        fi

        local dry_run_stat=""
        local dry_run_conflicts=""
        if $has_shared_history; then
            if git merge --no-commit upstream/main >/dev/null 2>&1; then
                dry_run_stat=$(git diff --cached --stat 2>/dev/null || true)
                if ! $JSON_OUTPUT; then
                    echo "$dry_run_stat"
                fi
                git merge --abort >/dev/null 2>&1 || true
            else
                if ! $JSON_OUTPUT; then
                    echo -e "${YELLOW}Merge would produce conflicts:${NC}"
                fi
                dry_run_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || true)
                if ! $JSON_OUTPUT; then
                    echo "$dry_run_conflicts"
                fi
                git merge --abort >/dev/null 2>&1 || true
            fi
        else
            if ! $JSON_OUTPUT; then
                echo -e "${YELLOW}Note: Unrelated histories — merge will use --allow-unrelated-histories${NC}"
            fi
            if git merge --no-commit --allow-unrelated-histories upstream/main >/dev/null 2>&1; then
                dry_run_stat=$(git diff --cached --stat 2>/dev/null || true)
                if ! $JSON_OUTPUT; then
                    echo "$dry_run_stat"
                fi
                git merge --abort >/dev/null 2>&1 || true
            else
                if ! $JSON_OUTPUT; then
                    echo -e "${YELLOW}Merge would produce conflicts:${NC}"
                fi
                dry_run_conflicts=$(git diff --name-only --diff-filter=U 2>/dev/null || true)
                if ! $JSON_OUTPUT; then
                    echo "$dry_run_conflicts"
                fi
                git merge --abort >/dev/null 2>&1 || true
            fi
        fi

        # Track files that would change for JSON output (T007)
        if [[ -n "$dry_run_stat" ]]; then
            # Extract file count from stat summary line (e.g., "10 files changed")
            merge_files_changed=$(echo "$dry_run_stat" | grep -oE '[0-9]+ files? changed' | grep -oE '^[0-9]+' || echo "0")
        fi
        if [[ -n "$dry_run_conflicts" ]]; then
            merge_conflicts="$dry_run_conflicts"
            merge_conflict_count=$(echo "$dry_run_conflicts" | wc -l | tr -d ' ')
        fi

        # JSON output for dry-run (T008, T009)
        if $JSON_OUTPUT; then
            # Build conflicts JSON array
            local conflicts_json="[]"
            if [[ -n "$merge_conflicts" ]]; then
                conflicts_json="["
                local first=true
                while IFS= read -r conflict_file; do
                    if [[ -n "$conflict_file" ]]; then
                        if $first; then
                            first=false
                        else
                            conflicts_json="${conflicts_json},"
                        fi
                        conflicts_json="${conflicts_json}\"$(json_escape "$conflict_file")\""
                    fi
                done <<EOF
$merge_conflicts
EOF
                conflicts_json="${conflicts_json}]"
            fi

            json_output "{\"schema_version\":\"1.0\",\"status\":\"dry_run\",\"backup_branch\":\"\",\"files_changed\":$merge_files_changed,\"conflicts\":$conflicts_json,\"conflict_count\":$merge_conflict_count,\"memory_preserved\":false}"
            return 0
        fi

        echo ""
        echo -e "${YELLOW}[DRY-RUN]${NC} No files were modified."
        return 0
    fi

    # --- Create backup branch ---
    local backup_branch="pre-sync-backup-$(date +%Y%m%d-%H%M%S)"
    echo -e "${BLUE}Creating backup branch: ${backup_branch}${NC}"
    git branch "$backup_branch"

    # --- Backup .aod/memory/ (defense-in-depth) ---
    local memory_dir="$REPO_ROOT/.aod/memory"
    local memory_backup=""
    if [[ -d "$memory_dir" ]]; then
        memory_backup=$(mktemp -d)
        cp -R "$memory_dir/." "$memory_backup/"
        echo -e "${BLUE}Backed up .aod/memory/ to temporary location${NC}"
    fi

    # --- Merge ---
    local merge_result=0
    local merge_output=""

    echo -e "${BLUE}Merging upstream/main...${NC}"
    if $has_shared_history; then
        merge_output=$(git merge upstream/main --no-edit 2>&1) || merge_result=$?
    else
        echo -e "${YELLOW}Note: Using --allow-unrelated-histories (no shared git history)${NC}"
        merge_output=$(git merge upstream/main --allow-unrelated-histories --no-edit 2>&1) || merge_result=$?
    fi

    # --- Restore .aod/memory/ ---
    if [[ -n "$memory_backup" ]] && [[ -d "$memory_backup" ]]; then
        cp -R "$memory_backup/." "$memory_dir/"
        rm -rf "$memory_backup"
        # Stage the restored memory files to resolve any conflicts there
        git add "$memory_dir" 2>/dev/null || true
        merge_memory_preserved=true
        echo -e "${GREEN}.aod/memory/ restored from backup${NC}"
    fi

    # --- Report results ---
    echo ""
    if [[ $merge_result -eq 0 ]]; then
        # Clean merge - track for JSON output (T007)
        merge_status="success"
        # Extract actual file count from merge summary line (e.g., "10 files changed")
        merge_files_changed=$(echo "$merge_output" | grep -oE '[0-9]+ files? changed' | grep -oE '^[0-9]+' || echo "0")
        merge_conflict_count=0
        merge_conflicts=""

        # JSON output for successful merge (T008)
        if $JSON_OUTPUT; then
            json_output "{\"schema_version\":\"1.0\",\"status\":\"success\",\"backup_branch\":\"$(json_escape "$backup_branch")\",\"files_changed\":$merge_files_changed,\"conflicts\":[],\"conflict_count\":0,\"memory_preserved\":$merge_memory_preserved}"
            return 0
        fi

        echo -e "${GREEN}Merge completed successfully${NC}"
        echo "$merge_output" | grep -E "file(s)? changed|insertion|deletion" || true
        echo ""
        echo "  Backup branch: $backup_branch"
        echo "  .aod/memory/:  preserved"
        echo ""
        echo "  Next: Run 'sync-upstream.sh validate' to check project integrity."
    else
        # Merge with conflicts - track for JSON output (T007)
        merge_status="conflicts"
        local conflict_files
        conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null || true)
        merge_conflicts="$conflict_files"
        if [[ -n "$conflict_files" ]]; then
            merge_conflict_count=$(echo "$conflict_files" | wc -l | tr -d ' ')
        else
            merge_conflict_count=0
        fi

        echo -e "${YELLOW}Merge completed with $merge_conflict_count conflict(s)${NC}"
        echo ""
        echo "  Files with conflicts:"
        echo "$conflict_files" | while IFS= read -r f; do
            echo -e "    ${RED}$f${NC}"
        done
        echo ""
        echo "  Resolve conflicts:"
        echo "    1. Edit each conflicted file and resolve markers (<<<<<<< / ======= / >>>>>>>)"
        echo "    2. git add <resolved-file>"
        echo "    3. git commit (to complete the merge)"
        echo ""
        echo "  Or abort and restore:"
        echo "    git merge --abort"
        echo "    git checkout $backup_branch  # Restore pre-merge state"
        # JSON output for merge with conflicts (T008)
        if $JSON_OUTPUT; then
            # Build conflicts JSON array
            local conflicts_json="[]"
            if [[ -n "$merge_conflicts" ]]; then
                conflicts_json="["
                local first=true
                while IFS= read -r conflict_file; do
                    if [[ -n "$conflict_file" ]]; then
                        if $first; then
                            first=false
                        else
                            conflicts_json="${conflicts_json},"
                        fi
                        conflicts_json="${conflicts_json}\"$(json_escape "$conflict_file")\""
                    fi
                done <<EOF
$merge_conflicts
EOF
                conflicts_json="${conflicts_json}]"
            fi

            json_output "{\"schema_version\":\"1.0\",\"status\":\"conflicts\",\"backup_branch\":\"$(json_escape "$backup_branch")\",\"files_changed\":$merge_files_changed,\"conflicts\":$conflicts_json,\"conflict_count\":$merge_conflict_count,\"memory_preserved\":$merge_memory_preserved}"
            return 0
        fi

        echo ""
        echo "  Backup branch: $backup_branch"
        echo "  .aod/memory/:  preserved"
    fi
}

# ============================================================================
# SUBCOMMAND: validate
# ============================================================================

cmd_validate() {
    if ! $JSON_OUTPUT; then
        echo -e "${BLUE}Validating project integrity...${NC}"
        echo ""
    fi

    local pass_count=0
    local fail_count=0
    local warn_count=0

    # JSON output tracking: collect check results as JSON fragments (Wave 2: T010)
    # Format: newline-separated JSON objects for bash 3.2 compatibility
    local validate_checks=""

    # Helper to add a check result to the collection
    _add_check() {
        local name="$1"
        local status="$2"
        local message="$3"
        local remediation="${4:-}"
        local check_json
        if [[ -n "$remediation" ]]; then
            check_json="{\"name\":\"$(json_escape "$name")\",\"status\":\"$status\",\"message\":\"$(json_escape "$message")\",\"remediation\":\"$(json_escape "$remediation")\"}"
        else
            check_json="{\"name\":\"$(json_escape "$name")\",\"status\":\"$status\",\"message\":\"$(json_escape "$message")\"}"
        fi
        if [[ -z "$validate_checks" ]]; then
            validate_checks="$check_json"
        else
            validate_checks="$validate_checks
$check_json"
        fi
    }

    # --- Check 1: Expected AOD files exist ---
    if ! $JSON_OUTPUT; then echo -e "${BLUE}1. File existence checks${NC}"; fi
    local expected_dirs=(".aod" ".claude" "docs/core_principles" "scripts")
    for dir in "${expected_dirs[@]}"; do
        if [[ -d "$REPO_ROOT/$dir" ]]; then
            if ! $JSON_OUTPUT; then echo -e "   ${GREEN}PASS${NC} $dir/ exists"; fi
            pass_count=$((pass_count + 1))
            _add_check "dir_$dir" "pass" "$dir/ exists"
        else
            if ! $JSON_OUTPUT; then
                echo -e "   ${RED}FAIL${NC} $dir/ missing"
                echo "         Remediation: Check if upstream merge removed this directory"
            fi
            fail_count=$((fail_count + 1))
            _add_check "dir_$dir" "fail" "$dir/ missing" "Check if upstream merge removed this directory"
        fi
    done

    local expected_files=("CLAUDE.md" "Makefile" ".gitignore")
    for file in "${expected_files[@]}"; do
        if [[ -f "$REPO_ROOT/$file" ]]; then
            if ! $JSON_OUTPUT; then echo -e "   ${GREEN}PASS${NC} $file exists"; fi
            pass_count=$((pass_count + 1))
            _add_check "file_$file" "pass" "$file exists"
        else
            if ! $JSON_OUTPUT; then
                echo -e "   ${RED}FAIL${NC} $file missing"
                echo "         Remediation: Restore from backup branch or upstream"
            fi
            fail_count=$((fail_count + 1))
            _add_check "file_$file" "fail" "$file missing" "Restore from backup branch or upstream"
        fi
    done
    if ! $JSON_OUTPUT; then echo ""; fi

    # --- Check 2: YAML frontmatter validation ---
    if ! $JSON_OUTPUT; then echo -e "${BLUE}2. YAML frontmatter checks${NC}"; fi
    local yaml_files_checked=0
    while IFS= read -r specfile; do
        if [[ -z "$specfile" ]]; then
            continue
        fi
        yaml_files_checked=$((yaml_files_checked + 1))
        local relpath="${specfile#$REPO_ROOT/}"

        # Check for opening and closing --- delimiters
        local first_line
        first_line=$(head -1 "$specfile" 2>/dev/null || echo "")
        if [[ "$first_line" == "---" ]]; then
            # Look for closing ---
            local closing
            closing=$(tail -n +2 "$specfile" | grep -n "^---$" | head -1 | cut -d: -f1 || echo "")
            if [[ -n "$closing" ]] && [[ "$closing" -gt 0 ]]; then
                if ! $JSON_OUTPUT; then echo -e "   ${GREEN}PASS${NC} $relpath — valid frontmatter"; fi
                pass_count=$((pass_count + 1))
                _add_check "yaml_$relpath" "pass" "$relpath — valid frontmatter"
            else
                if ! $JSON_OUTPUT; then
                    echo -e "   ${RED}FAIL${NC} $relpath — missing closing --- delimiter"
                    echo "         Remediation: Add closing --- after YAML frontmatter block"
                fi
                fail_count=$((fail_count + 1))
                _add_check "yaml_$relpath" "fail" "$relpath — missing closing --- delimiter" "Add closing --- after YAML frontmatter block"
            fi
        else
            if ! $JSON_OUTPUT; then echo -e "   ${YELLOW}WARN${NC} $relpath — no YAML frontmatter found"; fi
            warn_count=$((warn_count + 1))
            _add_check "yaml_$relpath" "warn" "$relpath — no YAML frontmatter found"
        fi
    done < <(find "$REPO_ROOT/specs" -name "spec.md" -o -name "plan.md" -o -name "tasks.md" 2>/dev/null)

    if [[ $yaml_files_checked -eq 0 ]]; then
        if ! $JSON_OUTPUT; then echo -e "   ${YELLOW}WARN${NC} No spec/plan/tasks files found to validate"; fi
        warn_count=$((warn_count + 1))
        _add_check "yaml_files" "warn" "No spec/plan/tasks files found to validate"
    fi
    if ! $JSON_OUTPUT; then echo ""; fi

    # --- Check 3: Placeholder leak detection ---
    # T012 (feature 129): uses factored aod_template_scan_residual_placeholders
    # when available; falls back to the original inline scan when the library
    # was not sourced (e.g., sliced-script test harness). The output format and
    # per-file handling are preserved to keep the baseline BATS suite green.
    if ! $JSON_OUTPUT; then echo -e "${BLUE}3. Placeholder leak detection${NC}"; fi
    local placeholder_found=false
    local scan_files=("CLAUDE.md" ".aod/memory/constitution.md" "Makefile" "scripts/init.sh")
    for file in "${scan_files[@]}"; do
        local fullpath="$REPO_ROOT/$file"
        if [[ ! -f "$fullpath" ]]; then
            continue
        fi
        local matches=""
        if declare -f aod_template_scan_residual_placeholders >/dev/null 2>&1; then
            # Factored helper emits "<file>:<line>:<match>"; strip the leading
            # "<file>:" prefix to recover the original "<line>:<match>" shape
            # that the legacy output formatting expects.
            local raw
            raw=$(aod_template_scan_residual_placeholders "$fullpath" 2>/dev/null || true)
            if [[ -n "$raw" ]]; then
                matches=$(printf '%s\n' "$raw" | sed "s|^${fullpath}:||")
            fi
        else
            # Fallback: original inline scan (preserves exact behavior when
            # the factored helper is unavailable).
            matches=$(grep -n '{{[A-Z_]*}}' "$fullpath" 2>/dev/null || true)
        fi
        if [[ -n "$matches" ]]; then
            placeholder_found=true
            if ! $JSON_OUTPUT; then
                echo -e "   ${YELLOW}WARN${NC} $file — placeholder(s) found:"
                echo "$matches" | while IFS= read -r match; do
                    echo "         Line $match"
                done
            fi
            warn_count=$((warn_count + 1))
            _add_check "placeholder_$file" "warn" "$file — placeholder(s) found"
        fi
    done
    if ! $placeholder_found; then
        if ! $JSON_OUTPUT; then echo -e "   ${GREEN}PASS${NC} No leaked placeholders detected"; fi
        pass_count=$((pass_count + 1))
        _add_check "placeholder_scan" "pass" "No leaked placeholders detected"
    fi
    if ! $JSON_OUTPUT; then echo ""; fi

    # --- Check 4: Constitution integrity ---
    if ! $JSON_OUTPUT; then echo -e "${BLUE}4. Constitution integrity${NC}"; fi
    local constitution="$REPO_ROOT/.aod/memory/constitution.md"
    if [[ -f "$constitution" ]]; then
        local template_count
        template_count=$(grep -c '{{' "$constitution" 2>/dev/null || echo "0")
        local total_lines
        total_lines=$(wc -l < "$constitution" | tr -d ' ')
        if [[ "$template_count" -gt 0 ]]; then
            if ! $JSON_OUTPUT; then
                echo -e "   ${YELLOW}WARN${NC} constitution.md has $template_count unresolved template variable(s)"
                echo "         This may be expected if you haven't customized the constitution yet."
                echo "         Run: /aod.constitution to configure your project values"
            fi
            warn_count=$((warn_count + 1))
            _add_check "constitution" "warn" "constitution.md has $template_count unresolved template variable(s)" "Run /aod.constitution to configure your project values"
        else
            if ! $JSON_OUTPUT; then echo -e "   ${GREEN}PASS${NC} constitution.md — no template variables (customized)"; fi
            pass_count=$((pass_count + 1))
            _add_check "constitution" "pass" "constitution.md — no template variables (customized)"
        fi
    else
        if ! $JSON_OUTPUT; then
            echo -e "   ${RED}FAIL${NC} .aod/memory/constitution.md not found"
            echo "         Remediation: Restore from backup or re-run scripts/init.sh"
        fi
        fail_count=$((fail_count + 1))
        _add_check "constitution" "fail" ".aod/memory/constitution.md not found" "Restore from backup or re-run scripts/init.sh"
    fi
    if ! $JSON_OUTPUT; then echo ""; fi

    # JSON output for validate (T011)
    if $JSON_OUTPUT; then
        # Determine overall status
        local validate_status="pass"
        if [[ $fail_count -gt 0 ]]; then
            validate_status="fail"
        fi

        # Build checks JSON array from newline-separated JSON fragments
        local checks_json="["
        local first=true
        while IFS= read -r check_line; do
            if [[ -n "$check_line" ]]; then
                if $first; then
                    first=false
                else
                    checks_json="${checks_json},"
                fi
                checks_json="${checks_json}${check_line}"
            fi
        done <<EOF
$validate_checks
EOF
        checks_json="${checks_json}]"

        json_output "{\"schema_version\":\"1.0\",\"status\":\"$validate_status\",\"passed\":$pass_count,\"failed\":$fail_count,\"warnings\":$warn_count,\"checks\":$checks_json}"

        if [[ $fail_count -gt 0 ]]; then
            return 1
        fi
        return 0
    fi

    # --- Summary ---
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Validation Summary${NC}"
    echo -e "  ${GREEN}Passed:   $pass_count${NC}"
    echo -e "  ${RED}Failed:   $fail_count${NC}"
    echo -e "  ${YELLOW}Warnings: $warn_count${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ $fail_count -gt 0 ]]; then
        echo ""
        echo -e "${RED}Some checks failed. Review the issues above and apply remediations.${NC}"
        return 1
    elif [[ $warn_count -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}All critical checks passed. Review warnings above.${NC}"
        return 0
    else
        echo ""
        echo -e "${GREEN}All checks passed. Project integrity verified.${NC}"
        return 0
    fi
}

# ============================================================================
# HELPER: Ensure .gitattributes has adopter-owned path protections
# ============================================================================

_ensure_gitattributes() {
    local gitattributes="$REPO_ROOT/.gitattributes"
    local entry=".aod/memory/ merge=ours"

    if [[ -f "$gitattributes" ]]; then
        if grep -qF "$entry" "$gitattributes" 2>/dev/null; then
            return 0  # Already present
        fi
    fi

    echo -e "${BLUE}Adding .aod/memory/ merge protection to .gitattributes${NC}"
    if ! $DRY_RUN; then
        echo "$entry" >> "$gitattributes"
    fi
}

# ============================================================================
# ARGUMENT PARSING & DISPATCH
# ============================================================================

# Collect global flags and subcommand
SUBCOMMAND=""
SUBCOMMAND_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        setup|check|merge|validate)
            SUBCOMMAND="$1"
            shift
            # Collect remaining args, extracting global flags
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --dry-run) DRY_RUN=true; shift ;;
                    --json)    JSON_OUTPUT=true; shift ;;
                    *)         SUBCOMMAND_ARGS=("${SUBCOMMAND_ARGS[@]+"${SUBCOMMAND_ARGS[@]}"}" "$1"); shift ;;
                esac
            done
            break
            ;;
        *)
            if $JSON_OUTPUT; then
                json_output "{\"schema_version\":\"1.0\",\"status\":\"error\",\"error\":\"Unknown subcommand: $1\"}"
            else
                echo -e "${RED}Error: Unknown command or option: $1${NC}" >&2
                echo "" >&2
                echo "Usage: sync-upstream.sh <subcommand> [options]" >&2
                echo "Run 'sync-upstream.sh --help' for details." >&2
            fi
            exit 1
            ;;
    esac
done

# Verify git is available
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo -e "${RED}Error: Not a git repository (or git is not installed)${NC}" >&2
    echo "  This script must be run from within a git repository." >&2
    exit 1
fi

# Dispatch
case "$SUBCOMMAND" in
    setup)    cmd_setup "${SUBCOMMAND_ARGS[@]+"${SUBCOMMAND_ARGS[@]}"}" ;;
    check)    cmd_check ;;
    merge)    cmd_merge ;;
    validate) cmd_validate ;;
    "")
        echo -e "${RED}Error: No subcommand specified${NC}" >&2
        echo "" >&2
        show_help
        exit 1
        ;;
    *)
        echo -e "${RED}Error: Unknown subcommand: $SUBCOMMAND${NC}" >&2
        exit 1
        ;;
esac
