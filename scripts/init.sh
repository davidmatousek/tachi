#!/bin/bash
# scripts/init.sh - Agentic-Oriented-Development-Kit Initialization

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Agentic-Oriented-Development-Kit - Project Initialization${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js is required but not installed.${NC}" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo -e "${RED}Git is required but not installed.${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Interactive prompts
read -p "Project Name: " PROJECT_NAME
read -p "Project Description: " PROJECT_DESCRIPTION
read -p "GitHub Organization: " GITHUB_ORG
read -p "GitHub Repository [$PROJECT_NAME]: " GITHUB_REPO
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
  # Extract display name for TECH_STACK placeholder
  TECH_STACK=$(head -1 "stacks/$SELECTED_PACK/STACK.md" | sed 's/^# //' | sed 's/ Stack$//')
  # Load all defaults from pack (database, auth, vector, cloud provider, etc.)
  if [ -f "stacks/$SELECTED_PACK/defaults.env" ]; then
    source "stacks/$SELECTED_PACK/defaults.env"
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
RATIFICATION_DATE=$(date +%Y-%m-%d)
CURRENT_DATE=$(date +%Y-%m-%d)

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

echo ""
echo -e "${YELLOW}🔄 Replacing template variables...${NC}"

# Bootstrap: replace upstream marketing README with the templated scaffold
# so replace_in_files (below) substitutes tokens in the right file.
# Note: make init is one-shot per project — re-running overwrites root README.
if [ -f ".aod/scaffold/README.md" ]; then
  cp .aod/scaffold/README.md README.md
else
  echo -e "${YELLOW}⚠ .aod/scaffold/README.md missing — using existing root README. Sync may be incomplete.${NC}" >&2
fi

# Function to replace in files (cross-platform)
replace_in_files() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    find . -type f \
      -not -path "./.git/*" \
      -not -path "./node_modules/*" \
      -not -name "*.png" -not -name "*.jpg" -not -name "*.ico" \
      -exec sed -i '' \
        -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
        -e "s|{{PROJECT_DESCRIPTION}}|$PROJECT_DESCRIPTION|g" \
        -e "s|{{GITHUB_ORG}}|$GITHUB_ORG|g" \
        -e "s|{{GITHUB_REPO}}|$GITHUB_REPO|g" \
        -e "s|{{AI_AGENT}}|$AI_AGENT|g" \
        -e "s|{{TECH_STACK}}|$TECH_STACK|g" \
        -e "s|{{TECH_STACK_DATABASE}}|$TECH_STACK_DATABASE|g" \
        -e "s|{{TECH_STACK_VECTOR}}|$TECH_STACK_VECTOR|g" \
        -e "s|{{TECH_STACK_AUTH}}|$TECH_STACK_AUTH|g" \
        -e "s|{{RATIFICATION_DATE}}|$RATIFICATION_DATE|g" \
        -e "s|{{CURRENT_DATE}}|$CURRENT_DATE|g" \
        -e "s|{{CLOUD_PROVIDER}}|$CLOUD_PROVIDER|g" \
        {} +
  else
    # Linux
    find . -type f \
      -not -path "./.git/*" \
      -not -path "./node_modules/*" \
      -not -name "*.png" -not -name "*.jpg" -not -name "*.ico" \
      -exec sed -i \
        -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
        -e "s|{{PROJECT_DESCRIPTION}}|$PROJECT_DESCRIPTION|g" \
        -e "s|{{GITHUB_ORG}}|$GITHUB_ORG|g" \
        -e "s|{{GITHUB_REPO}}|$GITHUB_REPO|g" \
        -e "s|{{AI_AGENT}}|$AI_AGENT|g" \
        -e "s|{{TECH_STACK}}|$TECH_STACK|g" \
        -e "s|{{TECH_STACK_DATABASE}}|$TECH_STACK_DATABASE|g" \
        -e "s|{{TECH_STACK_VECTOR}}|$TECH_STACK_VECTOR|g" \
        -e "s|{{TECH_STACK_AUTH}}|$TECH_STACK_AUTH|g" \
        -e "s|{{RATIFICATION_DATE}}|$RATIFICATION_DATE|g" \
        -e "s|{{CURRENT_DATE}}|$CURRENT_DATE|g" \
        -e "s|{{CLOUD_PROVIDER}}|$CLOUD_PROVIDER|g" \
        {} +
  fi
}

replace_in_files

echo -e "${GREEN}✓ Template variables replaced${NC}"

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
      labels_output=$(bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_labels' 2>&1) || true
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

# Clean up instructional text from constitution (contains literal {{ examples)
CONSTITUTION=".aod/memory/constitution.md"
if [ -f "$CONSTITUTION" ]; then
  echo -e "${YELLOW}🔄 Cleaning up constitution template instructions...${NC}"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # Remove HTML comment block at top (lines starting with <!-- through -->)
    sed -i '' '/^<!--$/,/^-->$/d' "$CONSTITUTION"
    # Remove "Template Instructions" section at bottom (## Template Instructions to EOF)
    sed -i '' '/^## Template Instructions$/,$d' "$CONSTITUTION"
  else
    sed -i '/^<!--$/,/^-->$/d' "$CONSTITUTION"
    sed -i '/^## Template Instructions$/,$d' "$CONSTITUTION"
  fi
  echo -e "${GREEN}✓ Constitution template instructions removed${NC}"
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

# ── Personalization env: write .aod/personalization.env BEFORE self-delete ──
# Per feature 129 (T046, plan §C5): capture the 12 canonical placeholder
# values as an init-time snapshot. /aod.update reads this file on every run
# and uses bash parameter expansion (NOT sed) to re-substitute placeholders
# into personalized-category files.
#
# RATIFICATION_DATE and CURRENT_DATE are captured HERE — init-time snapshots
# that /aod.update MUST NEVER recompute. If the adopter ever deletes these
# keys later, /aod.update halts with exit 8 (see tests/integration/
# init-only-snapshot.bats).
#
# ORDER IS LOAD-BEARING — this runs AFTER the version-pin write above and
# BEFORE the `rm -f scripts/init.sh` self-delete below. Both files must
# exist when /aod.update first runs.
echo -e "${YELLOW}🔄 Writing personalization snapshot (.aod/personalization.env)...${NC}"

# Source template-substitute.sh for aod_template_init_personalization.
if [ -f ".aod/scripts/bash/template-substitute.sh" ]; then
  # shellcheck disable=SC1091
  source .aod/scripts/bash/template-substitute.sh
else
  echo -e "${RED}ERROR: .aod/scripts/bash/template-substitute.sh not found — cannot write personalization.env${NC}" >&2
  exit 1
fi

# The caller-scope vars PROJECT_NAME, PROJECT_DESCRIPTION, ..., CLOUD_PROVIDER
# have been set by the prompts above. RATIFICATION_DATE and CURRENT_DATE were
# captured at line 86-87 via `date +%Y-%m-%d`. The helper validates all 12
# values present + newline-free, then writes atomically (.tmp → mv).
if aod_template_init_personalization ".aod/personalization.env"; then
  echo -e "${GREEN}✓ Personalization snapshot written (.aod/personalization.env)${NC}"
else
  echo -e "${RED}ERROR: failed to write .aod/personalization.env${NC}" >&2
  exit 1
fi

# Remove this init script (one-time use)
rm -f scripts/init.sh

echo ""
echo -e "${GREEN}🎉 Project initialized successfully!${NC}"
echo ""
# Board status
case "$BOARD_STATUS" in
  created)
    echo -e "  ${GREEN}✓${NC} GitHub Projects board + 7 stage labels: Created"
    ;;
  already_exists)
    echo -e "  ${GREEN}✓${NC} GitHub Projects board + 7 stage labels: Already configured"
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
