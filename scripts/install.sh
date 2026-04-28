#!/usr/bin/env bash
# scripts/install.sh
#
# Install tachi into the current project directory.
# Copies all distributable files listed in INSTALL_MANIFEST.md from
# the tachi source directory to the current working directory.
#
# Usage:
#   ./install.sh [--source <path>] [--version <tag>] [--help]
#
# Options:
#   --source <path>  Path to tachi source directory (auto-detected if omitted)
#   --version <tag>  Install files from a specific tagged version (e.g., v4.25.0) # x-release-please-version
#   --help           Show this usage information
#
# Examples:
#   cd ~/Projects/my-app && ~/Projects/tachi/scripts/install.sh
#   ./install.sh --source ~/Projects/tachi
#   ./install.sh --version v4.25.0 # x-release-please-version

set -euo pipefail

# --- Color constants ----------------------------------------------------------

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
NC=$'\033[0m' # No Color

# --- Helpers ------------------------------------------------------------------

die() {
  printf '%sError: %s%s\n' "$RED" "$1" "$NC" >&2
  exit 1
}

usage() {
  echo "Usage: $(basename "$0") [--source <path>] [--version <tag>] [--help]"
  echo ""
  echo "Install tachi into the current project directory."
  echo ""
  echo "Options:"
  echo "  --source <path>  Path to tachi source directory (auto-detected if omitted)"
  echo "  --version <tag>  Install files from a specific tagged version (e.g., v4.25.0)" # x-release-please-version
  echo "  --help           Show this usage information"
  echo ""
  echo "Run this script from the root of the project where you want tachi installed."
  exit 0
}

# --- Variables ----------------------------------------------------------------

VERSION_TAG=""
ORIGINAL_REF=""

# --- Source auto-detection ----------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Argument parsing --------------------------------------------------------

while [ $# -gt 0 ]; do
  case "$1" in
    --source)
      [ $# -ge 2 ] || die "--source requires a path argument"
      SOURCE_DIR="$2"
      shift 2
      ;;
    --version)
      [ $# -ge 2 ] || die "--version requires a tag argument"
      VERSION_TAG="$2"
      shift 2
      ;;
    --help)
      usage
      ;;
    *)
      die "Unknown option: $1 (use --help for usage)"
      ;;
  esac
done

# --- Environment validation --------------------------------------------------

[ -d "$SOURCE_DIR" ] || die "Source directory not found: $SOURCE_DIR"

MANIFEST_FILE="${SOURCE_DIR}/INSTALL_MANIFEST.md"
[ -f "$MANIFEST_FILE" ] || die "INSTALL_MANIFEST.md not found in: $SOURCE_DIR"

if [ -n "$VERSION_TAG" ] && ! command -v git >/dev/null 2>&1; then
  die "--version requires git but git is not available on PATH"
fi

TARGET_DIR="$(pwd)"
if [ "$(cd "$SOURCE_DIR" && pwd)" = "$TARGET_DIR" ]; then
  die "Cannot install tachi into its own source directory. Run this from your target project root."
fi

# --- Version checkout --------------------------------------------------------

if [ -n "$VERSION_TAG" ]; then
  if [ -n "$(git -C "$SOURCE_DIR" status --porcelain)" ]; then
    die "Source repository has uncommitted changes. Commit or stash them before using --version."
  fi

  ORIGINAL_REF="$(git -C "$SOURCE_DIR" rev-parse --abbrev-ref HEAD)"
  if [ "$ORIGINAL_REF" = "HEAD" ]; then
    ORIGINAL_REF="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
  fi

  # Guard variable prevents restore if checkout never happened
  cleanup() {
    if [ -n "$ORIGINAL_REF" ]; then
      git -C "$SOURCE_DIR" checkout "$ORIGINAL_REF" --quiet 2>/dev/null || true
    fi
  }
  trap cleanup EXIT

  if ! git -C "$SOURCE_DIR" rev-parse --verify "refs/tags/$VERSION_TAG" >/dev/null 2>&1; then
    echo "Tag '$VERSION_TAG' not found. Available version tags:"
    git -C "$SOURCE_DIR" tag -l 'v*' --sort=-v:refname
    die "Invalid version tag: $VERSION_TAG"
  fi

  git -C "$SOURCE_DIR" checkout "$VERSION_TAG" --quiet
fi

# --- Deprecated-file cleanup -------------------------------------------------
# Remove old (pre-namespace) command files from the target directory.
# Ensures upgrades from tachi <5.0 leave no stale unprefixed command files.

DEPRECATED_COMMANDS=(
  ".claude/commands/threat-model.md"
  ".claude/commands/risk-score.md"
  ".claude/commands/compensating-controls.md"
  ".claude/commands/infographic.md"
  ".claude/commands/security-report.md"
)

CLEANUP_COUNT=0
for dep_file in "${DEPRECATED_COMMANDS[@]}"; do
  target_path="${TARGET_DIR}/${dep_file}"
  if [ -f "$target_path" ]; then
    rm -f "$target_path"
    printf '  Removed deprecated: %s\n' "$dep_file"
    CLEANUP_COUNT=$((CLEANUP_COUNT + 1))
  fi
done

if [ "$CLEANUP_COUNT" -gt 0 ]; then
  printf '  Cleaned up %d deprecated command file(s)\n' "$CLEANUP_COUNT"
fi

# --- Manifest parsing --------------------------------------------------------

parse_manifest() {
  local manifest="$1"
  local in_section=false

  while IFS= read -r line; do
    if [ "$line" = "<!-- BEGIN MANIFEST -->" ]; then
      in_section=true
      continue
    fi
    if [ "$line" = "<!-- END MANIFEST -->" ]; then
      in_section=false
      continue
    fi
    if [ "$in_section" = true ]; then
      # Skip blank lines and comments
      case "$line" in
        ""|\#*) continue ;;
      esac
      echo "$line"
    fi
  done < "$manifest"
}

# --- File copy loop ----------------------------------------------------------

COPY_SUCCESS=0
COPY_FAIL=0

while IFS= read -r entry; do
  src_path="${SOURCE_DIR}/${entry}"

  case "$entry" in
    */)
      # Directory (trailing slash)
      if [ -d "$src_path" ]; then
        mkdir -p "${TARGET_DIR}/${entry}"
        cp -r "${src_path}." "${TARGET_DIR}/${entry}" # trailing dot copies contents, not the directory itself
        COPY_SUCCESS=$((COPY_SUCCESS + 1))
      else
        printf '%sWarning: directory not found: %s%s\n' "$RED" "$entry" "$NC" >&2
        COPY_FAIL=$((COPY_FAIL + 1))
      fi
      ;;
    *)
      # Individual file
      if [ -f "$src_path" ]; then
        target_parent="$(dirname "${TARGET_DIR}/${entry}")"
        mkdir -p "$target_parent"
        cp "$src_path" "${TARGET_DIR}/${entry}"
        COPY_SUCCESS=$((COPY_SUCCESS + 1))
      else
        printf '%sWarning: file not found: %s%s\n' "$RED" "$entry" "$NC" >&2
        COPY_FAIL=$((COPY_FAIL + 1))
      fi
      ;;
  esac
done < <(parse_manifest "$MANIFEST_FILE")

# --- Summary output ----------------------------------------------------------

INSTALLED_VERSION="untagged"
if command -v git >/dev/null 2>&1 && [ -d "${SOURCE_DIR}/.git" ]; then
  # Fetch tags so git describe finds release-please tags created on GitHub
  git -C "$SOURCE_DIR" fetch --tags --quiet 2>/dev/null || true
  INSTALLED_VERSION="$(git -C "$SOURCE_DIR" describe --tags --always 2>/dev/null || echo "untagged")"
fi

echo ""
printf '%stachi installed successfully%s\n' "$GREEN" "$NC"
echo "  Version:  $INSTALLED_VERSION"
echo "  Source:   $SOURCE_DIR"
echo "  Copied:   $COPY_SUCCESS item(s)"
if [ "$COPY_FAIL" -gt 0 ]; then
  printf '  %sFailed:   %d item(s)%s\n' "$RED" "$COPY_FAIL" "$NC"
  exit 1
fi

# --- Prerequisite courtesy warning -------------------------------------------
# mmdc (@mermaid-js/mermaid-cli) is a hard prerequisite for attack path
# rendering in /tachi.security-report. The per-command preflight gate is the
# enforcement point; this warning is a best-effort early signal at install
# time. See README "Prerequisites" section and ADR-022.

if ! command -v mmdc >/dev/null 2>&1; then
  echo ""
  printf '%sWarning:%s mmdc (@mermaid-js/mermaid-cli) is not on PATH.\n' "$RED" "$NC" >&2
  echo "  mmdc is a prerequisite for attack path rendering in /tachi.security-report." >&2
  echo "  Install with: npm install -g @mermaid-js/mermaid-cli" >&2
  echo "  See README.md Prerequisites section for the full install guide." >&2
fi
