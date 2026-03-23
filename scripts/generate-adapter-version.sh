#!/bin/bash
# scripts/generate-adapter-version.sh
#
# Generate a VERSION file for a platform adapter directory.
# Computes Git commit SHA and SHA-256 checksums for each agent source file
# referenced by the adapter's transformed files.
#
# Usage:
#   ./scripts/generate-adapter-version.sh <adapter-dir>
#
# Examples:
#   ./scripts/generate-adapter-version.sh adapters/claude-code
#   ./scripts/generate-adapter-version.sh adapters/generic
#   ./scripts/generate-adapter-version.sh adapters/cursor
#   ./scripts/generate-adapter-version.sh adapters/copilot
#   ./scripts/generate-adapter-version.sh adapters/github-actions
#
# Output:
#   Writes a VERSION YAML file to <adapter-dir>/VERSION containing:
#     - source_version: short Git commit SHA at HEAD
#     - generated_date: current date (YYYY-MM-DD)
#     - agent_manifest: list of adapter files with source paths and SHA-256 checksums
#
# Compatibility:
#   macOS (bash 3.2+) and Linux. Uses shasum -a 256 for checksums.

set -euo pipefail

# --- Configuration -----------------------------------------------------------

REPO_ROOT="$(git rev-parse --show-toplevel)"

# All 14 agent base names in canonical order
ALL_AGENTS="orchestrator spoofing tampering repudiation info-disclosure denial-of-service privilege-escalation prompt-injection data-poisoning model-theft agent-autonomy tool-abuse threat-report threat-infographic"

# --- Functions ----------------------------------------------------------------

usage() {
  echo "Usage: $0 <adapter-dir>"
  echo ""
  echo "  adapter-dir  Path to the adapter directory (e.g., adapters/claude-code)"
  echo ""
  echo "Generates a VERSION file at <adapter-dir>/VERSION with source SHA,"
  echo "generation date, and SHA-256 checksums for all agent source files."
  exit 1
}

# Map a base agent name to its source file path relative to repo root.
# Returns empty string if no mapping exists.
resolve_source() {
  local base_name="$1"
  case "$base_name" in
    orchestrator)        echo "agents/orchestrator.md" ;;
    spoofing)            echo "agents/stride/spoofing.md" ;;
    tampering)           echo "agents/stride/tampering.md" ;;
    repudiation)         echo "agents/stride/repudiation.md" ;;
    info-disclosure)     echo "agents/stride/info-disclosure.md" ;;
    denial-of-service)   echo "agents/stride/denial-of-service.md" ;;
    privilege-escalation) echo "agents/stride/privilege-escalation.md" ;;
    prompt-injection)    echo "agents/ai/prompt-injection.md" ;;
    data-poisoning)      echo "agents/ai/data-poisoning.md" ;;
    model-theft)         echo "agents/ai/model-theft.md" ;;
    agent-autonomy)      echo "agents/ai/agent-autonomy.md" ;;
    tool-abuse)          echo "agents/ai/tool-abuse.md" ;;
    threat-report)       echo "agents/threat-report.md" ;;
    threat-infographic)  echo "agents/threat-infographic.md" ;;
    *)                   echo "" ;;
  esac
}

# Extract the base agent name from an adapter file name.
# Handles platform-specific naming conventions:
#   - Generic:  "00-orchestrator.md"       -> "orchestrator"
#   - Claude:   "orchestrator.md"          -> "orchestrator"
#   - Cursor:   "orchestrator.mdc"         -> "orchestrator"
#   - Copilot:  "orchestrator.agent.md"    -> "orchestrator"
extract_base_name() {
  local filename="$1"

  # Strip directory path, keep only the file name
  filename="$(basename "$filename")"

  # Strip .agent.md extension (Copilot) before other extensions
  case "$filename" in
    *.agent.md) filename="${filename%.agent.md}" ;;
    *.md)       filename="${filename%.md}" ;;
    *.mdc)      filename="${filename%.mdc}" ;;
    *.yml)      filename="${filename%.yml}" ;;
    *.yaml)     filename="${filename%.yaml}" ;;
  esac

  # Strip leading numeric prefix with dash (generic adapter: "00-", "01-", etc.)
  filename="$(echo "$filename" | sed 's/^[0-9][0-9]*-//')"

  echo "$filename"
}

# Compute SHA-256 checksum of a file (macOS compatible via shasum).
compute_sha256() {
  local filepath="$1"
  shasum -a 256 "$filepath" | awk '{print $1}'
}

# Detect the agent content subdirectory within an adapter directory.
# Returns the first matching subdirectory: agents/, prompts/, rules/
# Falls back to the adapter directory itself for github-actions.
detect_content_dir() {
  local adapter_dir="$1"
  local subdir

  for subdir in agents prompts rules; do
    if [ -d "${adapter_dir}/${subdir}" ]; then
      echo "${adapter_dir}/${subdir}"
      return
    fi
  done

  # GitHub Actions adapter has no agent subdirectory; use the adapter root
  echo "$adapter_dir"
}

# Write a single manifest entry to stdout.
write_manifest_entry() {
  local adapter_filename="$1"
  local source_path="$2"
  local sha256="$3"

  echo "  - file: ${adapter_filename}"
  echo "    source: ${source_path}"
  echo "    sha256: ${sha256}"
}

# --- Main ---------------------------------------------------------------------

if [ $# -ne 1 ]; then
  usage
fi

ADAPTER_DIR="$1"

# Validate adapter directory exists
if [ ! -d "$ADAPTER_DIR" ]; then
  echo "Error: Adapter directory not found: $ADAPTER_DIR" >&2
  exit 1
fi

# Compute Git commit SHA
SOURCE_VERSION="$(git rev-parse --short HEAD)"

# Current date
GENERATED_DATE="$(date +%Y-%m-%d)"

# Detect the content directory (agents/, prompts/, rules/, or adapter root)
CONTENT_DIR="$(detect_content_dir "$ADAPTER_DIR")"

# Temporary file to collect manifest entries
MANIFEST_TMP="$(mktemp)"
trap 'rm -f "$MANIFEST_TMP"' EXIT

AGENT_COUNT=0

# Determine adapter type
ADAPTER_NAME="$(basename "$ADAPTER_DIR")"

if [ "$ADAPTER_NAME" = "github-actions" ]; then
  # GitHub Actions adapter references all source agents at runtime via LLM API.
  # Generate manifest from the full canonical agent list.
  for base_name in $ALL_AGENTS; do
    source_path="$(resolve_source "$base_name")"
    source_fullpath="${REPO_ROOT}/${source_path}"

    if [ ! -f "$source_fullpath" ]; then
      echo "Warning: Source file not found: $source_path" >&2
      continue
    fi

    sha256="$(compute_sha256 "$source_fullpath")"
    write_manifest_entry "${base_name}.md" "$source_path" "$sha256" >> "$MANIFEST_TMP"
    AGENT_COUNT=$((AGENT_COUNT + 1))
  done
else
  # File-transformation adapters: scan the content directory for agent files.
  for filepath in "$CONTENT_DIR"/*; do
    [ -f "$filepath" ] || continue

    filename="$(basename "$filepath")"

    # Skip non-agent files
    case "$filename" in
      README.md|VERSION|*.yaml|*.yml) continue ;;
    esac

    # Extract the base agent name
    base_name="$(extract_base_name "$filename")"

    # Look up the source path
    source_path="$(resolve_source "$base_name")"
    if [ -z "$source_path" ]; then
      echo "Warning: No source mapping for adapter file '$filename' (base name: '$base_name')" >&2
      continue
    fi

    # Verify source file exists
    source_fullpath="${REPO_ROOT}/${source_path}"
    if [ ! -f "$source_fullpath" ]; then
      echo "Warning: Source file not found: $source_path" >&2
      continue
    fi

    # Compute checksum of the SOURCE file (not the adapter file)
    sha256="$(compute_sha256 "$source_fullpath")"
    write_manifest_entry "$filename" "$source_path" "$sha256" >> "$MANIFEST_TMP"
    AGENT_COUNT=$((AGENT_COUNT + 1))
  done
fi

# Write VERSION file
VERSION_FILE="${ADAPTER_DIR}/VERSION"

{
  echo "source_version: ${SOURCE_VERSION}"
  echo "generated_date: ${GENERATED_DATE}"
  echo "agent_manifest:"
  cat "$MANIFEST_TMP"
} > "$VERSION_FILE"

echo "Generated ${VERSION_FILE}"
echo "  source_version: ${SOURCE_VERSION}"
echo "  generated_date: ${GENERATED_DATE}"
echo "  agents: ${AGENT_COUNT}"
