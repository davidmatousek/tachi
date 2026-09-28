#!/usr/bin/env bash
# scripts/install.sh
#
# Install tachi into the current project directory.
# Copies all distributable files listed in INSTALL_MANIFEST.md from
# the tachi source directory to the current working directory.
#
# Usage:
#   ./install.sh [--source <path>] [--version <tag>] [--follow-symlinks] [--help]
#
# Options:
#   --source <path>  Path to tachi source directory (auto-detected if omitted)
#   --version <tag>  Install files from a specific tagged version (e.g., v4.48.0) # x-release-please-version
#   --follow-symlinks  Install through symlinked destinations (for example a linked
#                      `.claude/skills`). Without it, install.sh stops before writing
#                      anything when a destination is a symlink. With it, install.sh
#                      follows links at or above each installed path, names every
#                      resolved destination, and only copies: it never deletes through
#                      a link. Even with it, install.sh refuses broken, looping or
#                      wrong-type links (a file where a folder is needed, or the
#                      reverse), links nested inside an installed folder, and
#                      destinations inside the tachi source clone.
#   --help           Show this usage information
#
# Examples:
#   cd ~/Projects/my-app && ~/Projects/tachi/scripts/install.sh
#   ./install.sh --source ~/Projects/tachi
#   ./install.sh --version v4.48.0 # x-release-please-version

set -euo pipefail

# Prevents `cd` from consulting CDPATH and printing an unexpected directory
# name to stdout, which would corrupt every `$(cd ... && pwd ...)` capture
# below (contracts/installer-cli.md Sec. "Implementation constraints").
unset CDPATH

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
  echo "Usage: $(basename "$0") [--source <path>] [--version <tag>] [--follow-symlinks] [--help]"
  echo ""
  echo "Install tachi into the current project directory."
  echo ""
  echo "Options:"
  echo "  --source <path>  Path to tachi source directory (auto-detected if omitted)"
  echo "  --version <tag>  Install files from a specific tagged version (e.g., v4.48.0)" # x-release-please-version
  echo "  --follow-symlinks  Install through symlinked destinations (for example a linked \`.claude/skills\`)."
  echo "                     Without it, install.sh stops before writing anything when a destination is a symlink."
  echo "                     With it, install.sh follows links at or above each installed path, names every"
  echo "                     resolved destination, and only copies: it never deletes through a link."
  echo "                     Even with it, install.sh refuses broken, looping or wrong-type links (a file where a"
  echo "                     folder is needed, or the reverse), links nested inside an installed folder, and"
  echo "                     destinations inside the tachi source clone."
  echo "  --help           Show this usage information"
  echo ""
  echo "Run this script from the root of the project where you want tachi installed."
  exit 0
}

# resolve PATH -> prints the physical path; returns 1 if unresolvable (dangling, or > 32 hops)
# 32 is the cross-platform-safe minimum of Darwin's MAXSYMLINKS (32) and
# Linux's SYMLOOP_MAX (commonly 40): a chain this ceiling accepts is one the
# real OS can always walk during the copy phase, on either platform
# (SEC-K3-01).
resolve() {
  local p=$1 hops=0 t d
  while [ -L "$p" ]; do
    hops=$((hops + 1)); [ "$hops" -le 32 ] || return 1
    t=$(readlink "$p") || return 1
    case $t in /*) p=$t ;; *) p=$(dirname "$p")/$t ;; esac
  done
  [ -e "$p" ] || return 1
  if [ -d "$p" ]; then (cd -P "$p" && pwd -P)
  else d=$(cd -P "$(dirname "$p")" && pwd -P) || return 1; printf '%s/%s\n' "$d" "$(basename "$p")"
  fi
}

# phys_dest PATH -> prints where PATH physically is, or would be once created:
# resolve() of its deepest existing component, plus the components that do not exist yet.
# Returns 1 when the walk meets a dangling link (already refused as unresolvable).
phys_dest() {
  local q=$1 rest="" d
  while [ ! -e "$q" ]; do
    [ -L "$q" ] && return 1
    rest="/$(basename "$q")$rest"
    q=$(dirname "$q")
  done
  d=$(resolve "$q") || return 1
  printf '%s%s\n' "$d" "$rest"
}

# under PATH ROOT -> 0 if PATH (physical; its tail may not exist yet) is ROOT or lies under it.
# Compares identity ([ -ef ]: same device and inode), so case variants and firmlinks cannot bypass it.
under() {
  local x=$1 root=$2
  while [ ! -e "$x" ]; do x=${x%/*}; [ -n "$x" ] || x=/; done
  while :; do
    [ "$x" -ef "$root" ] && return 0
    [ "$x" = / ] && return 1
    x=${x%/*}; [ -n "$x" ] || x=/
  done
}

# wrong_type NEED RESOLVED -> 0 if RESOLVED's actual type does not match NEED
# ("dir" or "file"). Used only after resolve() has already succeeded.
wrong_type() {
  local need=$1 resolved=$2
  case $need in
    dir) [ ! -d "$resolved" ] ;;
    file) [ -d "$resolved" ] ;;
    *) return 1 ;;
  esac
}

# strict_prefixes REL -> prints each strict prefix of slash-separated REL, one
# per line, shortest first (e.g. "a/b/c" -> "a", then "a/b"). Prints nothing
# for a single-segment REL. Used to build the checked set's "ancestor" and
# "cleanup-ancestor" origins (contracts/installer-cli.md "The checked set").
# Splits via parameter expansion only (never `set -- $rel`/IFS word-splitting)
# so a glob metacharacter (`*`, `?`, `[...]`) in REL is always a literal path
# segment, never pathname-expanded against files in the caller's working
# directory (SEC-K3-02).
strict_prefixes() {
  local p="" seg rest=$1
  while [ "$rest" != "${rest#*/}" ]; do
    seg=${rest%%/*}
    rest=${rest#*/}
    p="${p:+$p/}$seg"
    printf '%s\n' "$p"
  done
}

# parse_manifest FILE -> prints each manifest entry (one per line), skipping
# blank lines and comment lines, between the BEGIN/END markers. Moved here
# (from its former site just above the copy loop) so the pre-flight (Order
# of operations step 5) can call it before the copy loop is reached.
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

# --- Variables ----------------------------------------------------------------

VERSION_TAG=""
ORIGINAL_REF=""
FOLLOW_SYMLINKS=0

# The five pre-namespace command files a target project may still have lying
# around from a tachi <5.0 install. Declared here (rather than at the
# cleanup site below) so the pre-flight's checked-set builder can reference
# it before the cleanup loop is reached.
DEPRECATED_COMMANDS=(
  ".claude/commands/threat-model.md"
  ".claude/commands/risk-score.md"
  ".claude/commands/compensating-controls.md"
  ".claude/commands/infographic.md"
  ".claude/commands/security-report.md"
)

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
    --follow-symlinks)
      FOLLOW_SYMLINKS=1
      shift
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

# --- Resolve physical roots (Order of operations, step 2) --------------------

if ! TARGET_P=$(cd -P "$TARGET_DIR" && pwd -P); then
  die "Could not resolve the physical path of the target directory: $TARGET_DIR"
fi
if ! SRC_P=$(cd -P "$SOURCE_DIR" && pwd -P); then
  die "Could not resolve the physical path of the tachi source directory: $SOURCE_DIR"
fi

# --- Project-root containment (S-2; identity-based per ruling AR-1) ----------
# Replaces the old logical string-equality guard. `[ -ef ]`-based identity
# comparison catches case variants and firmlinks that a string-prefix test
# would miss.

if under "$TARGET_P" "$SRC_P"; then
  containment_msg=$(printf 'the target project is the tachi source clone or lies inside it. Nothing was written.\n  project:     %s\n  tachi clone: %s\nRun install.sh from your own project directory, outside the tachi clone.' "$TARGET_P" "$SRC_P")
  die "$containment_msg"
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

  # The restore always runs on EXIT once trapped below; the guard is a
  # harmless no-op when no checkout ever happened (ORIGINAL_REF unset).
  cleanup() {
    rc=$?
    if [ -n "${ORIGINAL_REF:-}" ]; then
      if ! git -C "$SOURCE_DIR" checkout "$ORIGINAL_REF" --quiet; then
        printf '%s\n' "Warning: could not restore the tachi source repo to its original ref '$ORIGINAL_REF'." \
                      "  Restore it with: git -C '$SOURCE_DIR' checkout '$ORIGINAL_REF'" >&2
      fi
    fi
    exit "$rc"
  }
  trap cleanup EXIT

  if ! git -C "$SOURCE_DIR" rev-parse --verify "refs/tags/$VERSION_TAG" >/dev/null 2>&1; then
    echo "Tag '$VERSION_TAG' not found. Available version tags:"
    git -C "$SOURCE_DIR" tag -l 'v*' --sort=-v:refname
    die "Invalid version tag: $VERSION_TAG"
  fi

  git -C "$SOURCE_DIR" checkout "$VERSION_TAG" --quiet
fi

# --- Pre-flight (Order of operations, step 5; data-model.md Sec. 2) ---------
# Reads the checked-out manifest, builds the checked set, classifies every
# linked component, checks destination containment, and either refuses
# (die, nothing written) or reports opt-ins and continues. Writes nothing.

# The checked set: one line per (component, need, origin) triple, TAB-
# delimited. A component may appear on multiple lines (one per origin it
# has) -- M8 forbids associative arrays, so origins are recovered later by
# grepping this newline-delimited string rather than aggregated up front.
CHECKED_SET=""

while IFS= read -r manifest_entry; do
  [ -n "$manifest_entry" ] || continue
  entry_stripped=${manifest_entry%/}
  if [ "$manifest_entry" != "$entry_stripped" ]; then
    entry_need=dir
  else
    # shellcheck disable=SC2209 # literal string "file", not the file(1) command
    entry_need=file
  fi

  while IFS= read -r prefix; do
    [ -n "$prefix" ] || continue
    CHECKED_SET="${CHECKED_SET}${TARGET_P}/${prefix}"$'\t'"dir"$'\t'"ancestor"$'\n'
  done < <(strict_prefixes "$entry_stripped")

  CHECKED_SET="${CHECKED_SET}${TARGET_P}/${entry_stripped}"$'\t'"${entry_need}"$'\t'"entry"$'\n'

  if [ "$manifest_entry" != "$entry_stripped" ] && [ -d "${SRC_P}/${entry_stripped}" ]; then
    while IFS= read -r subtree_rel; do
      [ -n "$subtree_rel" ] || continue
      subtree_relp=${subtree_rel#./}
      CHECKED_SET="${CHECKED_SET}${TARGET_P}/${entry_stripped}/${subtree_relp}"$'\t'""$'\t'"subtree:${entry_stripped}"$'\n'
    done < <(cd "${SRC_P}/${entry_stripped}" && find . -mindepth 1)
  fi
done < <(parse_manifest "$MANIFEST_FILE")

for dep_file in "${DEPRECATED_COMMANDS[@]}"; do
  CHECKED_SET="${CHECKED_SET}${TARGET_P}/${dep_file}"$'\t'"file"$'\t'"cleanup-file"$'\n'
  while IFS= read -r prefix; do
    [ -n "$prefix" ] || continue
    CHECKED_SET="${CHECKED_SET}${TARGET_P}/${prefix}"$'\t'"dir"$'\t'"cleanup-ancestor"$'\n'
  done < <(strict_prefixes "$dep_file")
done

# Classify every unique LINKED component (data-model.md Sec. 2.1 precedence:
# 1 cleanup-only, 2 unresolvable, 3 nested, 4/5 inside/outside against
# TARGET_P). Report lines are built here, already formatted; §2.2's
# destination containment against SRC_P is a separate pass below.
ALWAYS_REFUSED=""
FLAG_ELIGIBLE=""
FOLLOW_REPORT=""
SKIP_CLEANUP_FILES=""

UNIQUE_COMPONENTS=$(printf '%s' "$CHECKED_SET" | cut -f1 | LC_ALL=C sort -u)

while IFS= read -r component; do
  [ -n "$component" ] || continue
  [ -L "$component" ] || continue
  comp_rel=${component#"${TARGET_P}/"}

  origins=$(printf '%s\n' "$CHECKED_SET" | awk -F'\t' -v c="$component" '$1 == c {print $3}' | LC_ALL=C sort -u)
  comp_need=$(printf '%s\n' "$CHECKED_SET" | awk -F'\t' -v c="$component" '$1 == c && $2 != "" {print $2; exit}')

  # 1. cleanup-only: origins are EXACTLY {cleanup-file}.
  if [ "$origins" = "cleanup-file" ]; then
    SKIP_CLEANUP_FILES="${SKIP_CLEANUP_FILES}${comp_rel}"$'\n'
    if cleanup_resolved=$(resolve "$component"); then
      FLAG_ELIGIBLE="${FLAG_ELIGIBLE}  ${comp_rel} -> ${cleanup_resolved}   [deprecated tachi command: with --follow-symlinks it is skipped, never deleted]"$'\n'
    else
      cleanup_readlink=$(readlink "$component" 2>/dev/null || printf '')
      FLAG_ELIGIBLE="${FLAG_ELIGIBLE}  ${comp_rel} -> '${cleanup_readlink}'   [deprecated tachi command: with --follow-symlinks it is skipped, never deleted]"$'\n'
    fi
    continue
  fi

  is_nested=0
  nested_entry=""
  case $origins in
    *subtree:*)
      is_nested=1
      nested_entry=$(printf '%s\n' "$origins" | grep '^subtree:' | head -n 1 | cut -d: -f2-)
      ;;
  esac

  # 2. unresolvable: dangling/looping, or (once resolved) the wrong type.
  if ! resolved=$(resolve "$component"); then
    readlink_text=$(readlink "$component" 2>/dev/null || printf '')
    ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${comp_rel} -> '${readlink_text}'   [broken, looping or wrong-type link]"$'\n'
    continue
  fi

  if [ -n "$comp_need" ] && wrong_type "$comp_need" "$resolved"; then
    if [ "$comp_need" = dir ]; then
      ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${comp_rel} -> ${resolved}   [link to a file where a folder is needed]"$'\n'
    else
      ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${comp_rel} -> ${resolved}   [link to a folder where a file is needed]"$'\n'
    fi
    continue
  fi

  # 3. nested: subtree ∈ origins.
  if [ "$is_nested" = 1 ]; then
    ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${comp_rel} -> ${resolved}   [nested link inside ${nested_entry}: the copy cannot pass through it]"$'\n'
    continue
  fi

  # 4/5. inside or outside TARGET_P -- flag-eligible.
  if under "$resolved" "$TARGET_P"; then where=inside; else where=outside; fi
  FLAG_ELIGIBLE="${FLAG_ELIGIBLE}  ${comp_rel} -> ${resolved}   [${where} project]"$'\n'
  FOLLOW_REPORT="${FOLLOW_REPORT}  ${comp_rel} -> ${resolved}"$'\n'

  case $origins in
    *cleanup-ancestor*)
      for dep_file in "${DEPRECATED_COMMANDS[@]}"; do
        case $dep_file in
          "$comp_rel"/*) SKIP_CLEANUP_FILES="${SKIP_CLEANUP_FILES}${dep_file}"$'\n' ;;
        esac
      done
      ;;
  esac
done < <(printf '%s\n' "$UNIQUE_COMPONENTS")

# Destination containment (data-model.md Sec. 2.2): every manifest entry,
# and every cleanup file that is not itself a link (cleanup-only above
# already governs those), must not physically resolve inside SRC_P -- this
# runs with or without the flag; there is no remedy. Also N11: a directory
# entry's own destination must not physically CONTAIN SRC_P (the clone
# nested inside one of its own destinations) -- same identity walk,
# reversed. phys_dest failing here means a dangling ancestor, already
# refused above (Sec. 2.1); skip silently per the contract.
while IFS= read -r manifest_entry; do
  [ -n "$manifest_entry" ] || continue
  entry_stripped=${manifest_entry%/}
  entry_path="${TARGET_P}/${entry_stripped}"

  if dest=$(phys_dest "$entry_path"); then
    # elif, not a second independent if: when dest == SRC_P exactly (a link
    # straight at the clone root), both directions of under() are true by
    # identity -- without elif this would print both lines for one entry.
    if under "$dest" "$SRC_P"; then
      ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${entry_stripped} -> ${dest}   [inside the tachi source clone ${SRC_P}]"$'\n'
    elif [ "$manifest_entry" != "$entry_stripped" ] && under "$SRC_P" "$dest"; then
      ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${entry_stripped} -> ${dest}   [the tachi source clone lies inside this destination]"$'\n'
    fi
  fi
done < <(parse_manifest "$MANIFEST_FILE")

for dep_file in "${DEPRECATED_COMMANDS[@]}"; do
  dep_path="${TARGET_P}/${dep_file}"
  [ -L "$dep_path" ] && continue
  if dest=$(phys_dest "$dep_path"); then
    if under "$dest" "$SRC_P"; then
      ALWAYS_REFUSED="${ALWAYS_REFUSED}  ${dep_file} -> ${dest}   [inside the tachi source clone ${SRC_P}]"$'\n'
    fi
  fi
done

# Reports (contracts/installer-cli.md Sec. "Messages"), sorted (and, as a
# side effect, deduplicated) for determinism -- a component classified by
# more than one check can otherwise appear twice.
sorted_refused=""
[ -n "$ALWAYS_REFUSED" ] && sorted_refused=$(printf '%s' "$ALWAYS_REFUSED" | LC_ALL=C sort -u)
sorted_flagged=""
[ -n "$FLAG_ELIGIBLE" ] && sorted_flagged=$(printf '%s' "$FLAG_ELIGIBLE" | LC_ALL=C sort -u)

refused_block=""
if [ -n "$sorted_refused" ]; then
  refused_block="install stopped: destination(s) tachi cannot install through. Nothing was written."$'\n'"${sorted_refused}"$'\n'"--follow-symlinks cannot help with these. Replace or remove each link listed above (or move the tachi clone out of the listed destination), then re-run."
fi

flagged_block=""
if [ "$FOLLOW_SYMLINKS" -eq 0 ] && [ -n "$sorted_flagged" ]; then
  flagged_block="symlinked destination(s) found. Nothing was written."$'\n'"${sorted_flagged}"$'\n'"Re-run with --follow-symlinks to install through these links (it only copies and never deletes through a link), or replace each link with a real directory or file."
fi

if [ -n "$refused_block" ] && [ -n "$flagged_block" ]; then
  die "${refused_block}"$'\n\n'"${flagged_block}"
elif [ -n "$refused_block" ]; then
  die "$refused_block"
elif [ -n "$flagged_block" ]; then
  die "$flagged_block"
fi

# Proceeding (with the flag): name every followed destination before any
# copying happens (Order of operations step 5 ends here; step 7 does the
# actual copying, unmodified -- cp/mkdir -p already write through a
# destination symlink at its point of use, so no separate "follow" logic is
# needed there).
if [ -n "$FOLLOW_REPORT" ]; then
  sorted_follow=$(printf '%s' "$FOLLOW_REPORT" | LC_ALL=C sort -u)
  printf '\nFollowing symlinked destination(s) (--follow-symlinks):\n%s\n' "$sorted_follow"
fi

# --- Deprecated-file cleanup -------------------------------------------------
# Remove old (pre-namespace) command files from the target directory.
# Ensures upgrades from tachi <5.0 leave no stale unprefixed command files.

CLEANUP_COUNT=0
for dep_file in "${DEPRECATED_COMMANDS[@]}"; do
  # Order of operations step 6: a deprecated path with a link as the file
  # itself or as an ancestor was either already refused in step 5 (no
  # flag), or is listed here in SKIP_CLEANUP_FILES (with the flag) -- never
  # deleted through a link either way.
  if printf '%s\n' "$SKIP_CLEANUP_FILES" | grep -Fxq "$dep_file"; then
    printf '  Skipped cleanup (symlinked path, not deleted): %s\n' "$dep_file"
    continue
  fi
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

# Summary additions (Order of operations step 8; contracts/installer-cli.md
# Sec. "Messages"): recap what pre-flight followed and what cleanup skipped,
# reusing the same FOLLOW_REPORT/SKIP_CLEANUP_FILES strings from steps 5/6.
if [ -n "$FOLLOW_REPORT" ]; then
  printf 'Installed through symlink(s):\n%s\n' "$(printf '%s' "$FOLLOW_REPORT" | LC_ALL=C sort -u)"
fi
if [ -n "$SKIP_CLEANUP_FILES" ]; then
  printf 'Skipped cleanup (symlinked path, not deleted):\n'
  while IFS= read -r skipped_path; do
    [ -n "$skipped_path" ] || continue
    printf '  %s\n' "$skipped_path"
  done < <(printf '%s' "$SKIP_CLEANUP_FILES" | LC_ALL=C sort -u)
fi

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
