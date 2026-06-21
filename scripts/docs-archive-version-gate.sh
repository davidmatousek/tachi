#!/usr/bin/env bash
set -euo pipefail

root="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

scan_targets=(
  "$root/docs/architecture/02_ADRs"
  "$root/docs/product/02_PRD"
  "$root/docs/guides/CONSUMER_GUIDE_TACHI.md"
  "$root/docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md"
  "$root/docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md"
  "$root/docs/roadmap"
  "$root/examples"
)

existing_targets=()
for target in "${scan_targets[@]}"; do
  if [[ -e "$target" ]]; then
    existing_targets+=("$target")
  fi
done

patterns='actions/checkout@v[0-6]|actions-rs/toolchain@|github/codeql-action/upload-sarif@v3|codeql/upload-sarif@v3|::set-output|Node 20'

is_allowed() {
  case "$1" in
    docs/architecture/02_ADRs/ADR-013-sarif-output-format-adoption.md) return 0 ;;
    docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md) return 0 ;;
    docs/product/02_PRD/021-platform-adapters-2026-03-23.md) return 0 ;;
    docs/guides/CONSUMER_GUIDE_TACHI.md) return 0 ;;
    docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md) return 0 ;;
    docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md) return 0 ;;
    docs/roadmap/2026-06-15-rust-tauri-parity-issue-cards.md) return 0 ;;
    docs/roadmap/2026-06-15-rust-tauri-parity-remediation-roadmap.html.md) return 0 ;;
    docs/roadmap/2026-06-21-rust-tauri-parity-capability-matrix.md) return 0 ;;
    docs/roadmap/2026-06-21-rust-tauri-parity-issue-cards.md) return 0 ;;
    docs/roadmap/2026-06-21-rust-tauri-parity-remediation-roadmap.html.md) return 0 ;;
    docs/roadmap/2026-06-21-archived-docs-workflow-version-inventory.md) return 0 ;;
    docs/roadmap/2026-06-21-archived-docs-workflow-version-issue-cards.md) return 0 ;;
    docs/roadmap/2026-06-21-archived-docs-workflow-version-roadmap.html.md) return 0 ;;
    docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md) return 0 ;;
    docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md) return 0 ;;
    *) return 1 ;;
  esac
}

if [[ ${#existing_targets[@]} -eq 0 ]]; then
  printf 'docs/archive version gate passed\n'
  exit 0
fi

hits="$(
  rg -n --with-filename --no-heading -e "$patterns" "${existing_targets[@]}" \
    | while IFS=: read -r path line rest; do
      rel="${path#"$root"/}"
      if is_allowed "$rel"; then
        continue
      fi
      printf '%s:%s:%s\n' "$rel" "$line" "$rest"
    done
)"

if [[ -n "$hits" ]]; then
  printf 'FAIL: stale workflow-version references are still present in archived docs or examples\n' >&2
  printf '%s\n' "$hits" >&2
  exit 1
fi

printf 'docs/archive version gate passed\n'
