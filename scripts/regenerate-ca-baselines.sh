#!/usr/bin/env bash
# =============================================================================
# regenerate-ca-baselines.sh — the single canonical CA-baseline regen + sidecar
#                              emitter (Feature 329 / FR-002 / OQ-1)
# =============================================================================
#
# Formalizes the manual recipe in
#   specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md
# (authority: ADR-037 D-9 intentional CA-page baseline updates; ADR-021
# SOURCE_DATE_EPOCH determinism) into an executable script, and — as its FINAL
# step — emits the fingerprint sidecar
#   examples/ca-baseline-fingerprints.json
# that scripts/check-catalog-drift.py compares the live tree against.
#
# Why emission is the last step (cheat-resistance — Risk-1 / OQ-1): the sidecar
# becomes a genuine byproduct of regeneration. A developer cannot advance the
# expected fingerprints the CI guard enforces without actually re-rendering the 6
# baselines first. NEVER hand-edit examples/ca-baseline-fingerprints.json — advance
# it only by re-running this script.
#
# Determinism boundary (NFR-001): this script and the T001 pre-state are the ONLY
# places `typst` rendering runs. Neither the guard (`--check`) nor any CI-triggered
# job renders or hits the network.
#
# Run locally (NOT in CI). Requires `typst` on PATH and a Python with PyYAML.
# Override the interpreter when your default `python3` lacks PyYAML, e.g.:
#   PYTHON=.venv/bin/python scripts/regenerate-ca-baselines.sh
#
# bash 3.2.57+ compatible (macOS bundled /bin/bash): no associative arrays,
# no `mapfile`, no `${var,,}`.
# =============================================================================
set -euo pipefail

# --- Resolve repo root from this script's location (runnable from anywhere) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

PYTHON="${PYTHON:-python3}"

# MUST equal the byte-identity suite constant (test_backward_compatibility.py)
# and the guard's SOURCE_DATE_EPOCH — do not change without regenerating all
# baselines in the same commit.
export SOURCE_DATE_EPOCH=1700000000

# The 6 byte-identity-gated baselines (BASELINE_EXAMPLES, contract Decision D2).
# The 2 sample-report baselines (predictive-ml-app, mobile-banking-app) are
# deliberately excluded — they are not byte-identity-gated.
BASELINE_EXAMPLES="web-app microservices ascii-web-api mermaid-agentic-app free-text-microservice maestro-reference"

TEMPLATE_DIR="templates/tachi/security-report"
REPORT_DATA_TYP="${TEMPLATE_DIR}/report-data.typ"
TEMPLATE_MAIN="${TEMPLATE_DIR}/main.typ"

# Render PDFs into a throwaway temp dir (mirrors the byte-identity suite, which
# renders to its pytest tmp_path), then move into place. NEVER render to a
# fixed name inside examples/<name>/ — maestro-reference commits a separate
# `security-report.pdf` sample, which a render-in-place would clobber.
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ca-baselines.XXXXXX")"
trap 'rm -rf "${TMP_DIR}"' EXIT

# --- Preflight ---------------------------------------------------------------
if ! command -v typst >/dev/null 2>&1; then
  echo "regenerate-ca-baselines: ERROR — 'typst' not found on PATH (local rendering required)." >&2
  exit 1
fi
echo "regenerate-ca-baselines: typst $(typst --version 2>/dev/null | head -1)"
echo "regenerate-ca-baselines: python $(${PYTHON} --version 2>&1)"
echo "regenerate-ca-baselines: SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}"

# --- Regenerate each baseline (sequential — shared report-data.typ is mutated) ---
for name in ${BASELINE_EXAMPLES}; do
  echo "regenerate-ca-baselines: [${name}] extract → compile"
  "${PYTHON}" scripts/extract-report-data.py \
    --target-dir "examples/${name}" \
    --output "${REPORT_DATA_TYP}" \
    --template-dir "${TEMPLATE_DIR}"
  # typst 0.14.2 infers the output format from the extension, and ".baseline" is
  # not a recognized format — so render to a real ".pdf" in TMP_DIR (mirroring the
  # working invocation in tests/scripts/test_backward_compatibility.py, which
  # renders to its pytest tmp_path) and move it into place. Rendering outside the
  # example dir guarantees byte-identity with the suite AND avoids clobbering the
  # committed examples/maestro-reference/security-report.pdf sample.
  typst compile "${TEMPLATE_MAIN}" \
    "${TMP_DIR}/security-report.pdf" \
    --root .
  mv -f "${TMP_DIR}/security-report.pdf" \
        "examples/${name}/security-report.pdf.baseline"
done

# --- D-9 invariant 5: restore the shared extraction output (no residue) ------
# report-data.typ is gitignored (.gitignore) — a transient build artifact never
# committed — so this restore is best-effort: it succeeds if the file is tracked
# (legacy state) and is a harmless no-op when ignored. `|| true` keeps `set -e`
# from aborting on the "pathspec did not match" case.
git checkout -- "${REPORT_DATA_TYP}" 2>/dev/null || true

# --- FINAL STEP: emit the sidecar from the freshly-regenerated tree (OQ-1) ----
echo "regenerate-ca-baselines: emit fingerprint sidecar"
"${PYTHON}" scripts/check-catalog-drift.py --emit

echo "regenerate-ca-baselines: done — 6 baselines regenerated + sidecar emitted."
echo "  Review: git status  (expect changed baselines only if content changed, plus examples/ca-baseline-fingerprints.json)"
