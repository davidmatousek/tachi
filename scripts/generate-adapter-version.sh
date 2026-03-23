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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../.aod/scripts/bash/common.sh"
REPO_ROOT="$(get_repo_root)"

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
  local filename="${1##*/}"

  case "$filename" in
    *.agent.md) filename="${filename%.agent.md}" ;;
    *.md)       filename="${filename%.md}" ;;
    *.mdc)      filename="${filename%.mdc}" ;;
    *.yml)      filename="${filename%.yml}" ;;
    *.yaml)     filename="${filename%.yaml}" ;;
  esac

  # Strip leading numeric prefix with dash (generic adapter: "00-", "01-", etc.)
  if [[ "$filename" =~ ^[0-9]+-(.+)$ ]]; then
    filename="${BASH_REMATCH[1]}"
  fi

  echo "$filename"
}

compute_sha256() {
  local output
  output="$(shasum -a 256 "$1")"
  echo "${output%% *}"
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

  echo "$adapter_dir"
}

# Resolve source path, verify it exists, compute checksum, and emit manifest YAML.
# Used by both github-actions and file-transformation adapter paths.
process_agent() {
  local adapter_filename="$1"
  local base_name="$2"

  local source_path
  source_path="$(resolve_source "$base_name")"
  if [ -z "$source_path" ]; then
    echo "Warning: No source mapping for '$adapter_filename' (base name: '$base_name')" >&2
    return 1
  fi

  local source_fullpath="${REPO_ROOT}/${source_path}"
  if [ ! -f "$source_fullpath" ]; then
    echo "Warning: Source file not found: $source_path" >&2
    return 1
  fi

  local sha256
  sha256="$(compute_sha256 "$source_fullpath")"
  echo "  - file: ${adapter_filename}"
  echo "    source: ${source_path}"
  echo "    sha256: ${sha256}"
}

# --- Main ---------------------------------------------------------------------

if [ $# -ne 1 ]; then
  usage
fi

ADAPTER_DIR="$1"

if [ ! -d "$ADAPTER_DIR" ]; then
  echo "Error: Adapter directory not found: $ADAPTER_DIR" >&2
  exit 1
fi

SOURCE_VERSION="$(git rev-parse --short HEAD)"
GENERATED_DATE="$(date +%Y-%m-%d)"
CONTENT_DIR="$(detect_content_dir "$ADAPTER_DIR")"
ADAPTER_NAME="${ADAPTER_DIR##*/}"
AGENT_COUNT=0
VERSION_FILE="${ADAPTER_DIR}/VERSION"

{
  echo "source_version: ${SOURCE_VERSION}"
  echo "generated_date: ${GENERATED_DATE}"
  echo "agent_manifest:"

  if [ "$ADAPTER_NAME" = "github-actions" ]; then
    # GitHub Actions references all source agents at runtime via LLM API
    for base_name in $ALL_AGENTS; do
      if process_agent "${base_name}.md" "$base_name"; then
        AGENT_COUNT=$((AGENT_COUNT + 1))
      fi
    done
  else
    for filepath in "$CONTENT_DIR"/*; do
      [ -f "$filepath" ] || continue

      filename="${filepath##*/}"

      case "$filename" in
        README.md|VERSION|*.yaml|*.yml|.gitkeep) continue ;;
      esac

      base_name="$(extract_base_name "$filename")"

      if process_agent "$filename" "$base_name"; then
        AGENT_COUNT=$((AGENT_COUNT + 1))
      fi
    done
  fi
} > "$VERSION_FILE"

echo "Generated ${VERSION_FILE}"
echo "  source_version: ${SOURCE_VERSION}"
echo "  generated_date: ${GENERATED_DATE}"
echo "  agents: ${AGENT_COUNT}"
