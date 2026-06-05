#!/usr/bin/env bash
set -euo pipefail

ROOT="."
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="${2:-}"
      shift 2
      ;;
    --root=*)
      ROOT="${1#*=}"
      shift
      ;;
    --help|-h)
      echo "usage: coverage-audit.sh [--root PATH]"
      exit 0
      ;;
    *)
      ROOT="$1"
      shift
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -d "$ROOT" ]]; then
  echo "missing repository root: $ROOT" >&2
  exit 1
fi

cd "$REPO_ROOT"
cargo run -p tachi-cli --bin coverage-audit -- --root "$ROOT"
