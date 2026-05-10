#!/bin/bash
# scripts/init.sh - Agentic-Oriented-Development-Kit Initialization

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Source the substitution helper library (F-248 T015 — was a lazy source at
# snapshot-write time pre-F-248; eager top-level source so that the same
# helper functions are available to both the substitution loop AND the
# snapshot-write block. NFR-001: bash 3.2 compatible.
if [ -f ".aod/scripts/bash/template-substitute.sh" ]; then
  # shellcheck disable=SC1091
  source .aod/scripts/bash/template-substitute.sh
else
  echo -e "${RED}ERROR: .aod/scripts/bash/template-substitute.sh not found — required for substitution${NC}" >&2
  exit 1
fi

# Source the input validation helper (F-248 T023). Provides aod_init_read_validated
# which wraps `read -r -p` with a rejection ladder (newline / NUL / control char
# / over-length / metacharacters per F-2 amendment) per FR-005.
if [ -f ".aod/scripts/bash/init-input.sh" ]; then
  # shellcheck disable=SC1091
  source .aod/scripts/bash/init-input.sh
else
  echo -e "${RED}ERROR: .aod/scripts/bash/init-input.sh not found — required for prompt input validation${NC}" >&2
  exit 1
fi

# Source the canonical KV-file load primitive (F-2 T015). Provides
# aod_template_load_kv_file which replaces caller-side `source` of config
# files with regex-validated, whitelist-enforced caller-scope assignment.
# Used by Site A (defaults.env), Site B (aod-kit-version), Site D
# (personalization.env) per ADR-040. NFR-001: bash 3.2 compatible.
if [ -f ".aod/scripts/bash/template-config-load.sh" ]; then
  # shellcheck disable=SC1091
  source .aod/scripts/bash/template-config-load.sh
else
  echo -e "${RED}ERROR: .aod/scripts/bash/template-config-load.sh not found — required for safe config-file load${NC}" >&2
  exit 1
fi

# F-5 (T015): parse --no-precommit / --precommit flag overrides for the
# opt-in pre-commit secret-scanning hook prompt. These flags affect ONLY
# the first-run init.sh invocation; post-init opt-out is `pre-commit
# uninstall` from the repo root (per docs/standards/PRECOMMIT_HOOKS.md
# §Re-init-Behavior). Default behavior: TTY check baseline (prompt fires
# if interactive; auto-skipped otherwise).
PRECOMMIT_FLAG=""  # "" = TTY-default; "skip" = --no-precommit; "force" = --precommit
for arg in "$@"; do
  case "$arg" in
    --no-precommit) PRECOMMIT_FLAG="skip" ;;
    --precommit)    PRECOMMIT_FLAG="force" ;;
  esac
done

echo -e "${BLUE}🚀 Agentic-Oriented-Development-Kit - Project Initialization${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js is required but not installed.${NC}" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo -e "${RED}Git is required but not installed.${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Re-init pre-flight check (F-248 T016, FR-003): if .aod/personalization.env
# already exists, this project has already been initialized. init.sh self-
# deletes after a successful run, so seeing the file at this point means
# either (a) a previous run was interrupted before self-delete, or (b) the
# operator is running from a non-personalized clone but accidentally pulled
# in the snapshot. Halt to prevent re-init.
if [ -f ".aod/personalization.env" ]; then
  echo -e "${RED}ERROR: .aod/personalization.env already exists.${NC}" >&2
  echo "       This project has already been initialized. Re-running init.sh on a personalized adopter project is not supported." >&2
  echo "       (init.sh self-deletes after a successful run; if you are seeing this on a fresh checkout, the previous run was interrupted — delete .aod/personalization.env and retry.)" >&2
  exit 1
fi

# Interactive prompts (F-248 T024-T027 — wrapped with aod_init_read_validated
# per FR-005 input validation contract; max_len limits per spec quickstart §C2)
aod_init_read_validated "Project Name: " PROJECT_NAME 100
aod_init_read_validated "Project Description: " PROJECT_DESCRIPTION 300
aod_init_read_validated "GitHub Organization: " GITHUB_ORG 39
aod_init_read_validated "GitHub Repository [$PROJECT_NAME]: " GITHUB_REPO 100
GITHUB_REPO=${GITHUB_REPO:-$PROJECT_NAME}

echo ""
echo "Select AI Agent:"
echo "  1) Claude Code (recommended)"
echo "  2) Cursor"
echo "  3) GitHub Copilot"
read -p "Choice [1]: " AI_CHOICE
case $AI_CHOICE in
  2) AI_AGENT="cursor" ;;
  3) AI_AGENT="copilot" ;;
  *) AI_AGENT="claude" ;;
esac

# Discover available stack packs
echo ""
echo "Select Tech Stack:"
STACK_PACKS=()
STACK_INDEX=1
for pack_dir in stacks/*/; do
  pack_name=$(basename "$pack_dir")
  # Skip if not a directory or no STACK.md
  [ -f "$pack_dir/STACK.md" ] || continue
  # Extract display name from first line (strip leading "# ")
  display_name=$(head -1 "$pack_dir/STACK.md" | sed 's/^# //')
  STACK_PACKS+=("$pack_name")
  echo "  $STACK_INDEX) $display_name ($pack_name)"
  STACK_INDEX=$((STACK_INDEX + 1))
done
echo "  $STACK_INDEX) Other / Not yet defined"
OTHER_INDEX=$STACK_INDEX

read -p "Choice [$OTHER_INDEX]: " STACK_CHOICE
STACK_CHOICE=${STACK_CHOICE:-$OTHER_INDEX}

if [ "$STACK_CHOICE" -ge 1 ] 2>/dev/null && [ "$STACK_CHOICE" -lt "$OTHER_INDEX" ] 2>/dev/null; then
  SELECTED_PACK="${STACK_PACKS[$((STACK_CHOICE - 1))]}"
  # Extract display name for downstream prompts (substituted into STACK_TECH_STACK
  # below if defaults.env doesn't override).
  TECH_STACK_DISPLAY=$(head -1 "stacks/$SELECTED_PACK/STACK.md" | sed 's/^# //' | sed 's/ Stack$//')
  # Load all defaults from pack (database, auth, vector, cloud provider, etc.)
  # F-2 T016: replace `source defaults.env` with the canonical library load
  # primitive. STACK_PACK_ALLOWED_KEYS enforces the canonical 5-key surface
  # per contracts/stack-pack-defaults-schema.md. The "STACK_" prefix
  # disambiguates from canonical-12 personalization values that flow through
  # the same caller scope downstream.
  if [ -f "stacks/$SELECTED_PACK/defaults.env" ]; then
    STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
    if ! aod_template_load_kv_file "stacks/$SELECTED_PACK/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS; then
      echo -e "${RED}ERROR: failed to load stack pack defaults: stacks/$SELECTED_PACK/defaults.env${NC}" >&2
      echo -e "${RED}       (the file must contain the canonical 5 keys per contracts/stack-pack-defaults-schema.md)${NC}" >&2
      exit 1
    fi
    # Map STACK_-prefixed library outputs into the canonical-12 placeholder
    # variables expected downstream (init-personalization, etc.). The
    # STACK_TECH_STACK from defaults.env wins; fall back to the STACK.md
    # display name only if the pack omitted TECH_STACK (legacy path).
    TECH_STACK="${STACK_TECH_STACK:-$TECH_STACK_DISPLAY}"
    TECH_STACK_DATABASE="$STACK_TECH_STACK_DATABASE"
    TECH_STACK_VECTOR="$STACK_TECH_STACK_VECTOR"
    TECH_STACK_AUTH="$STACK_TECH_STACK_AUTH"
    CLOUD_PROVIDER="$STACK_CLOUD_PROVIDER"
    echo -e "  ${GREEN}✓ Loaded defaults from $SELECTED_PACK pack${NC}"
  fi
else
  # Custom stack — ask the essentials only
  read -p "Tech Stack (e.g., Python + FastAPI, Go + Gin): " TECH_STACK
  TECH_STACK=${TECH_STACK:-"Not yet defined"}
  read -p "Database (e.g., PostgreSQL, MySQL, SQLite): " TECH_STACK_DATABASE
  TECH_STACK_DATABASE=${TECH_STACK_DATABASE:-"Not yet defined"}
  read -p "Cloud Provider (e.g., Vercel, AWS, GCP) [optional]: " CLOUD_PROVIDER
fi

# Fill any remaining placeholders not set by pack or user
TECH_STACK_DATABASE=${TECH_STACK_DATABASE:-"Not yet defined"}
TECH_STACK_VECTOR=${TECH_STACK_VECTOR:-"Not yet defined"}
TECH_STACK_AUTH=${TECH_STACK_AUTH:-"Not yet defined"}
CLOUD_PROVIDER=${CLOUD_PROVIDER:-"Not yet defined"}
RATIFICATION_DATE="${AOD_RATIFICATION_DATE_OVERRIDE:-$(date +%Y-%m-%d)}"
CURRENT_DATE="${AOD_CURRENT_DATE_OVERRIDE:-$(date +%Y-%m-%d)}"

# Confirmation
echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "  Project Name:    $PROJECT_NAME"
echo "  Description:     $PROJECT_DESCRIPTION"
echo "  GitHub:          $GITHUB_ORG/$GITHUB_REPO"
echo "  AI Agent:        $AI_AGENT"
if [ -n "$SELECTED_PACK" ]; then
  echo "  Stack Pack:      $SELECTED_PACK ($TECH_STACK)"
  echo "  Database:        $TECH_STACK_DATABASE"
  echo "  Auth:            $TECH_STACK_AUTH"
  echo "  Cloud Provider:  $CLOUD_PROVIDER"
else
  echo "  Tech Stack:      $TECH_STACK"
  echo "  Database:        $TECH_STACK_DATABASE"
  echo "  Cloud Provider:  $CLOUD_PROVIDER"
fi
echo ""
read -p "Proceed with initialization? [Y/n]: " CONFIRM
if [[ $CONFIRM =~ ^[Nn]$ ]]; then
  echo "Initialization cancelled."
  exit 0
fi

# F-5 (T015 + T016): opt-in pre-commit secret-scanning hook prompt + install.
# Default Y in TTY contexts; auto-skipped in non-TTY (CI / piped stdin).
# Flag overrides (--no-precommit / --precommit) bypass the TTY check.
# T016 (Architect CONCERN-3): pre-commit framework v3.5.0 floor — below
# this version, hook install may silently partial-install or runtime-crash
# (see docs/standards/PRECOMMIT_HOOKS.md §Known-Limitations).
PRECOMMIT_DECISION="skip"
if [ "$PRECOMMIT_FLAG" = "force" ]; then
  PRECOMMIT_DECISION="install"
elif [ "$PRECOMMIT_FLAG" != "skip" ] && [ -t 0 ]; then
  read -p "Install pre-commit secret-scanning hook (gitleaks)? [Y/n] " response
  if [[ "${response:-Y}" =~ ^[Yy]$ ]]; then
    PRECOMMIT_DECISION="install"
  fi
fi

if [ "$PRECOMMIT_DECISION" = "install" ]; then
  if command -v pre-commit >/dev/null 2>&1; then
    PRECOMMIT_VER_NUM="$(pre-commit --version 2>/dev/null | awk '{print $2}')"
    PRECOMMIT_MAJOR="$(echo "$PRECOMMIT_VER_NUM" | awk -F'.' '{print $1}')"
    PRECOMMIT_MINOR="$(echo "$PRECOMMIT_VER_NUM" | awk -F'.' '{print $2}')"
    case "$PRECOMMIT_MAJOR" in *[!0-9]*|"") PRECOMMIT_MAJOR=0 ;; esac
    case "$PRECOMMIT_MINOR" in *[!0-9]*|"") PRECOMMIT_MINOR=0 ;; esac
    if [ "$PRECOMMIT_MAJOR" -gt 3 ] || { [ "$PRECOMMIT_MAJOR" -eq 3 ] && [ "$PRECOMMIT_MINOR" -ge 5 ]; }; then
      pre-commit install || echo "WARN: pre-commit install failed; install pre-commit framework manually and run 'pre-commit install'" >&2
    else
      echo "WARN: pre-commit framework version < 3.5.0 detected ($PRECOMMIT_VER_NUM); minimum supported is 3.5.0; please upgrade via 'pip install --upgrade pre-commit' or 'brew upgrade pre-commit'" >&2
    fi
  else
    echo "WARN: pre-commit framework not installed; secret-scanning hook NOT installed. Install pre-commit (e.g., 'pip install pre-commit' or 'brew install pre-commit') and re-run 'pre-commit install' from the repo root" >&2
  fi
fi

echo ""

# ── Personalization snapshot (F-248 T017 reorder per Architect B-2 P1) ──────
# Snapshot-write MUST happen BEFORE the substitution loop so that
# aod_template_load_personalization_env can populate AOD_PERSONALIZATION_<KEY>
# env vars that aod_template_substitute_placeholders consumes. This replaces
# the previous post-substitution snapshot-write at the bottom of init.sh.
#
# RATIFICATION_DATE and CURRENT_DATE are captured above via `date +%Y-%m-%d`.
# /aod.update reads this file on every run and uses bash parameter expansion
# (NOT sed) to re-substitute placeholders into personalized-category files.
echo -e "${YELLOW}🔄 Writing personalization snapshot (.aod/personalization.env)...${NC}"
if aod_template_init_personalization ".aod/personalization.env"; then
  echo -e "${GREEN}✓ Personalization snapshot written (.aod/personalization.env)${NC}"
else
  echo -e "${RED}ERROR: failed to write .aod/personalization.env${NC}" >&2
  exit 1
fi

# Load the snapshot back into the AOD_PERSONALIZATION_<KEY> namespace so the
# substitute helper can resolve {{KEY}} → value (F-248 T018, FR-002).
if ! aod_template_load_personalization_env ".aod/personalization.env"; then
  echo -e "${RED}ERROR: failed to load .aod/personalization.env into AOD_PERSONALIZATION_ namespace${NC}" >&2
  exit 1
fi

echo -e "${YELLOW}🔄 Replacing template variables...${NC}"

# F-248 T019 (FR-001): replace the previous sed-based replace_in_files()
# function with bash parameter expansion via aod_template_substitute_placeholders.
# Single bash branch handles BOTH macOS and Linux (no more $OSTYPE split).
# Process substitution `< <(...)` is bash 3.2 compatible.
#
# bash 3.2 hazard: piping to `while read` creates a subshell that masks
# errors. We use process substitution + a flag variable to capture failures
# (NOT `set -e` which is already on at script scope and gets confusing in
# pipe-subshell contexts).
FAILED_FILES=""
while IFS= read -r -d '' path; do
  if ! aod_template_substitute_placeholders "$path" "$path"; then
    FAILED_FILES="$FAILED_FILES $path"
  fi
done < <(find . -type f \
  -not -path "./.git/*" \
  -not -path "./node_modules/*" \
  -not -name "*.png" -not -name "*.jpg" -not -name "*.ico" \
  -not -name "*.pdf" -not -name "*.baseline" -not -name ".DS_Store" \
  -print0)
if [ -n "$FAILED_FILES" ]; then
  echo -e "${RED}ERROR: substitution failed on:$FAILED_FILES${NC}" >&2
  exit 1
fi

echo -e "${GREEN}✓ Template variables replaced${NC}"

# F-248 T020 (FR-004): post-loop residual scan, scoped to PERSONALIZED files
# per .aod/template-manifest.txt. The closed placeholder contract applies to
# personalized-category files (those that re-substitute on /aod.update), NOT
# to the whole tree which contains legitimate non-canonical tokens used by
# parallel templating systems (stack-pack scaffolds, brand archetypes,
# deployment-time docs). Halt on first orphan canonical placeholder.
if [ -f ".aod/template-manifest.txt" ]; then
  while IFS= read -r line; do
    # Skip comments and blank lines (with optional leading whitespace).
    case "$line" in
      '') continue ;;
    esac
    stripped="${line#"${line%%[![:space:]]*}"}"
    case "$stripped" in
      ''|'#'*) continue ;;
    esac
    # Match `personalized|<path>` lines; skip everything else.
    case "$line" in
      'personalized|'*)
        rel_path="${line#personalized|}"
        # Strip trailing carriage return if any (CRLF tolerance).
        rel_path="${rel_path%$'\r'}"
        if [ -f "./$rel_path" ]; then
          if ! aod_template_assert_no_residual "./$rel_path"; then
            echo -e "${RED}ERROR: residual {{KEY}} placeholder detected in personalized file — see file:line above${NC}" >&2
            exit 8
          fi
        fi
        ;;
    esac
  done < .aod/template-manifest.txt
fi

# Write AOD_REPO to .env for explicit GitHub repo targeting
# This ensures gh commands in github-lifecycle.sh always target the correct repo.
if [ -f ".env" ]; then
  if ! grep -q '^AOD_REPO=' .env 2>/dev/null; then
    echo "AOD_REPO=$GITHUB_ORG/$GITHUB_REPO" >> .env
  fi
else
  echo "AOD_REPO=$GITHUB_ORG/$GITHUB_REPO" > .env
fi
echo -e "${GREEN}✓ AOD_REPO set in .env ($GITHUB_ORG/$GITHUB_REPO)${NC}"

# Generate seeded product vision from user inputs
VISION_FILE="docs/product/01_Product_Vision/product-vision.md"
echo -e "${YELLOW}🔄 Seeding product vision...${NC}"
cat > "$VISION_FILE" << EOF
# Product Vision — $PROJECT_NAME

## Mission Statement
$PROJECT_DESCRIPTION

## Vision Statement
[To be refined during /aod.define]

## Core Value Proposition
[To be refined during /aod.define]

## Target Users
[To be refined during /aod.define]

## Success Metrics
[To be refined during /aod.define]
EOF
echo -e "${GREEN}✓ Product vision seeded (refine with /aod.define)${NC}"

# ── GitHub Projects board setup (non-blocking) ──────────────────────
BOARD_STATUS="skipped"

if command -v gh >/dev/null 2>&1; then
  # gh CLI found — single call to check auth + scope
  auth_output=$(gh auth status 2>&1) || true
  if echo "$auth_output" | grep -q "Logged in"; then
    if echo "$auth_output" | grep -q "project"; then
      # All prereqs met — attempt board creation in isolated subshell
      board_output=$(bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board' 2>&1) || true
      if [ -f ".aod/memory/github-project.json" ]; then
        # Cache file exists — board was created or already existed
        if echo "$board_output" | grep -q "Reusing"; then
          BOARD_STATUS="already_exists"
        else
          BOARD_STATUS="created"
        fi
      else
        BOARD_STATUS="error"
      fi
    else
      BOARD_STATUS="skipped_no_scope"
    fi
  else
    BOARD_STATUS="skipped_no_gh"
  fi
else
  BOARD_STATUS="skipped_no_gh"
fi

# F-248 T032 (FR-008): replace the previous sed-based instructional-block
# cleanup with `cp` from the pre-stripped clean template. This eliminates the
# OSTYPE branching (macOS BSD sed vs GNU sed) and removes a metachar-sensitive
# transformation. Both the substitution loop above and `aod.update` produce
# identical post-substitution constitution bytes by sourcing the same clean
# template. See ADR-038 §Decision item 3 for the dual-template rationale.
CONSTITUTION=".aod/memory/constitution.md"
CONSTITUTION_TEMPLATE=".aod/templates/constitution-clean.md"
if [ -f "$CONSTITUTION_TEMPLATE" ]; then
  echo -e "${YELLOW}🔄 Installing post-substitution constitution from clean template...${NC}"
  if cp "$CONSTITUTION_TEMPLATE" "$CONSTITUTION"; then
    # The clean template ships with literal {{KEY}} placeholders that the
    # whole-tree substitution loop above already replaced when it walked
    # `.aod/templates/`. Re-substitute here for safety in case the template
    # was added post-substitution (e.g., via /aod.update).
    if ! aod_template_substitute_placeholders "$CONSTITUTION" "$CONSTITUTION"; then
      echo -e "${RED}ERROR: failed to substitute placeholders in $CONSTITUTION${NC}" >&2
      exit 1
    fi
    echo -e "${GREEN}✓ Constitution installed from .aod/templates/constitution-clean.md${NC}"
  else
    echo -e "${RED}ERROR: failed to install constitution from $CONSTITUTION_TEMPLATE${NC}" >&2
    exit 1
  fi
else
  echo -e "${YELLOW}⚠  $CONSTITUTION_TEMPLATE not present; constitution unchanged.${NC}" >&2
fi

# ── Version pin: write .aod/aod-kit-version BEFORE self-delete ──────
# Per feature 129 (T025): record the template's version + SHA + upstream URL
# + manifest hash + UTC timestamp, so /aod.update has a known anchor point.
# ORDER IS LOAD-BEARING — this must run before the rm -f below. If the
# self-delete ran first and this write failed, the adopter would be stuck
# without init.sh and without a valid pin.
echo -e "${YELLOW}🔄 Writing version pin (.aod/aod-kit-version)...${NC}"

# Ensure .aod/ exists (it should already, but defensive)
mkdir -p .aod

# Source template-git.sh for aod_template_write_version_file
if [ -f ".aod/scripts/bash/template-git.sh" ]; then
  # shellcheck disable=SC1091
  source .aod/scripts/bash/template-git.sh
else
  echo -e "${RED}ERROR: .aod/scripts/bash/template-git.sh not found — cannot write version pin${NC}" >&2
  exit 1
fi

# Gather the 5 fields from the template's current git state
VERSION_TAG="$(git describe --tags --exact-match 2>/dev/null || echo '')"
VERSION_SHA="$(git rev-parse HEAD 2>/dev/null || echo '')"
VERSION_UPDATED_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
# upstream_url: use origin URL (git remote get-url origin). Rewrite SSH →
# HTTPS if needed, since the version-schema contract requires https://.
VERSION_UPSTREAM_URL="$(git remote get-url origin 2>/dev/null || echo '')"
case "$VERSION_UPSTREAM_URL" in
  'git@github.com:'*)
    # git@github.com:foo/bar.git → https://github.com/foo/bar.git
    VERSION_UPSTREAM_URL="https://github.com/${VERSION_UPSTREAM_URL#git@github.com:}"
    ;;
  'ssh://git@github.com/'*)
    VERSION_UPSTREAM_URL="https://github.com/${VERSION_UPSTREAM_URL#ssh://git@github.com/}"
    ;;
esac
# Final fallback if git had no origin configured at all
if [ -z "$VERSION_UPSTREAM_URL" ]; then
  VERSION_UPSTREAM_URL="https://github.com/davidmatousek/agentic-oriented-development-kit.git"
fi

# manifest_sha256: compute if .aod/template-manifest.txt exists (T076 creates
# it); otherwise write the all-zeros sentinel that update.sh will reject and
# force a re-init via the 129b bootstrap.
VERSION_MANIFEST_SHA=""
if [ -f ".aod/template-manifest.txt" ]; then
  if command -v shasum >/dev/null 2>&1; then
    VERSION_MANIFEST_SHA="$(shasum -a 256 .aod/template-manifest.txt | cut -d' ' -f1)"
  elif command -v sha256sum >/dev/null 2>&1; then
    VERSION_MANIFEST_SHA="$(sha256sum .aod/template-manifest.txt | cut -d' ' -f1)"
  fi
fi
if [ -z "$VERSION_MANIFEST_SHA" ]; then
  # Sentinel: 64 zeros. update.sh treats this as "manifest absent — rerun init".
  VERSION_MANIFEST_SHA="0000000000000000000000000000000000000000000000000000000000000000"
  echo -e "${YELLOW}⚠  .aod/template-manifest.txt missing — using all-zeros sentinel for manifest_sha256 (T076 will populate on next template update).${NC}" >&2
fi

if [ -z "$VERSION_SHA" ]; then
  echo -e "${RED}ERROR: could not determine git HEAD SHA (is this a git checkout?)${NC}" >&2
  exit 1
fi

if aod_template_write_version_file ".aod/aod-kit-version" \
    "$VERSION_TAG" "$VERSION_SHA" "$VERSION_UPDATED_AT" \
    "$VERSION_UPSTREAM_URL" "$VERSION_MANIFEST_SHA"; then
  echo -e "${GREEN}✓ Version pin written (.aod/aod-kit-version)${NC}"
else
  echo -e "${RED}ERROR: failed to write .aod/aod-kit-version${NC}" >&2
  exit 1
fi

# ── Personalization env was written + loaded ABOVE (F-248 T017 reorder) ────
# Per F-248 BLOCKING B-2 pattern P1, the snapshot-write moved to BEFORE the
# substitution loop so that AOD_PERSONALIZATION_<KEY> env vars populate the
# loop's lookup. The version-pin write above + the self-delete below remain
# in their original positions.

# Remove this init script (one-time use)
rm -f scripts/init.sh

echo ""
echo -e "${GREEN}🎉 Project initialized successfully!${NC}"
echo ""
echo -e "  ${GREEN}✓${NC} Personalization snapshot: .aod/personalization.env (local-only by default per F-248)"
echo "    → Re-personalization on /aod.update reads from this snapshot."
echo "    → Gitignored by default; opt-in commit via 'git rm --cached' + edit .gitignore."
echo ""
# Board status
case "$BOARD_STATUS" in
  created)
    echo -e "  ${GREEN}✓${NC} GitHub Projects board: Created (AOD Backlog)"
    ;;
  already_exists)
    echo -e "  ${GREEN}✓${NC} GitHub Projects board: Already configured"
    ;;
  skipped_no_gh)
    echo -e "  ${YELLOW}⚠${NC} GitHub Projects board: Skipped (gh CLI not found)"
    echo "    → Install gh: https://cli.github.com"
    echo "    → Then run: bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board'"
    ;;
  skipped_no_scope)
    echo -e "  ${YELLOW}⚠${NC} GitHub Projects board: Skipped (missing 'project' OAuth scope)"
    echo "    → Run: gh auth refresh -s project"
    echo "    → Then run: bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board'"
    ;;
  error)
    echo -e "  ${YELLOW}⚠${NC} GitHub Projects board: Failed (see above for details)"
    echo "    → Run manually: bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board'"
    ;;
esac
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "  1. Establish your product vision and design identity:"
echo "     /aod.foundation                    → Guided workshop (vision + brand)"
echo "     /aod.foundation --vision           → Vision only"
echo "     /aod.foundation --design           → Design identity only"
echo ""
echo "  2. Activate a stack pack (optional):"
echo "     /aod.stack list                    → See available packs"
echo "     /aod.stack use nextjs-supabase     → Activate conventions"
echo "     /aod.stack scaffold                → Scaffold project files"
echo ""
echo "  3. Create your first PRD:"
echo "     /aod.define <your-first-feature>"
echo ""
echo "  4. Follow the AOD workflow:"
echo "     /aod.spec          → Define requirements"
echo "     /aod.project-plan  → Create technical plan"
echo "     /aod.tasks         → Generate task list"
echo "     /aod.build         → Execute implementation"
echo ""
echo -e "${BLUE}📚 Key Documentation:${NC}"
echo "  - Getting Started:  docs/GETTING_STARTED.md"
echo "  - SDLC Triad:       docs/AOD_TRIAD.md"
echo "  - Constitution:     .aod/memory/constitution.md"
echo "  - Definition of Done: docs/standards/DEFINITION_OF_DONE.md"
echo ""
echo -e "${GREEN}Happy building! 🏗️${NC}"
