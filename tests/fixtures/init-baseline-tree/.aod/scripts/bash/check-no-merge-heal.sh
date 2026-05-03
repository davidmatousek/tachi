#!/usr/bin/env bash
# ============================================================================
# check-no-merge-heal.sh — FR-023 invariant observability hook
# ============================================================================
#
# Purpose:
#   Verify FR-023 invariant "No AOD skill auto-merges any PR labeled `e2e-heal`"
#   (see specs/139-delivery-verified-not-documented/contracts/scope-guard-decision.md
#   and specs/139-delivery-verified-not-documented/spec.md FR-023).
#
#   Heal-PRs are opened by `/aod.deliver` when the auto-fix loop exhausts its
#   budget (default 2 attempts). Such PRs carry the `e2e-heal` + `requires-review`
#   labels and MUST be reviewed by a human — never auto-merged by any AOD skill
#   or helper script. This check scans the kit's own code for any pattern that
#   would violate that invariant.
#
# What it scans:
#   - .claude/skills/**/*.md   — all skill files
#   - .aod/scripts/bash/**/*.sh — all kit scripts
#   Pattern: `gh pr merge.*e2e-heal` (case-sensitive)
#
# Exclusions:
#   1. This check script itself (would match its own documentation).
#   2. Lines that intentionally document the banned pattern — identified by
#      the presence of `banned`, `forbidden`, or `invariant.*no.*merge` on the
#      same line. Such lines describe the invariant rather than violate it.
#
# Exit codes:
#   0 — invariant holds (no violating matches found)
#   1 — violation found; offending file:line:content printed to stderr
#
# Bash 3.2 compatible (no associative arrays, no mapfile/readarray, no pipe-&).
#
# ----------------------------------------------------------------------------
# MANUAL USAGE
# ----------------------------------------------------------------------------
#
#   bash .aod/scripts/bash/check-no-merge-heal.sh
#
# Run from repo root. No arguments. Output is a single success line on stdout
# or a multi-line violation block on stderr.
#
# ----------------------------------------------------------------------------
# CI INTEGRATION (adopter-side)
# ----------------------------------------------------------------------------
#
# Recommended: run as a pre-merge check on PRs that modify `.claude/skills/`
# or `.aod/scripts/bash/`. The kit does NOT wire this into a default AOD Kit
# CI workflow — adopters integrate per their platform.
#
# GitHub Actions snippet (drop into any workflow triggered on pull_request):
#
#   - name: Verify heal-PR no-auto-merge invariant
#     run: bash .aod/scripts/bash/check-no-merge-heal.sh
#
# GitLab CI snippet:
#
#   heal-invariant:
#     script: bash .aod/scripts/bash/check-no-merge-heal.sh
#
# Pre-commit hook (.git/hooks/pre-commit or pre-commit framework):
#
#   bash .aod/scripts/bash/check-no-merge-heal.sh || exit 1
#
# NOTE: Wiring this into the default AOD Kit CI is explicitly OUT OF SCOPE for
# PRD 139. The kit provides the observability hook; adopters decide where to
# run it based on their platform (GitHub Actions, GitLab CI, Jenkins, pre-commit
# hooks, etc.). See docs/guides/DELIVERY_HARD_GATE_MIGRATION.md §"CI Integration:
# No-Auto-Merge Invariant" for rationale and additional adopter guidance.
#
# ============================================================================

set -euo pipefail

# Resolve repo root (two levels up from .aod/scripts/bash/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

SELF_PATH="${SCRIPT_DIR}/check-no-merge-heal.sh"
SKILLS_DIR="${REPO_ROOT}/.claude/skills"
SCRIPTS_DIR="${REPO_ROOT}/.aod/scripts/bash"

PATTERN='gh pr merge.*e2e-heal'
# Exclusion regex: lines documenting the banned pattern rather than invoking it.
EXCLUDE_PATTERN='banned|forbidden|invariant.*no.*merge'

# Collect matches into a temp file; bash 3.2 friendly (no process substitution
# into arrays; no mapfile/readarray).
TMP_MATCHES="$(mktemp -t check-no-merge-heal.XXXXXX)"
trap 'rm -f "${TMP_MATCHES}"' EXIT

# Scan .claude/skills/**/*.md — use find + grep for recursive file-type filter.
# `grep -H` forces filename prefix even when a single file is passed (so that
# xargs invocations with one file still produce "path:line:content" tuples).
if [ -d "${SKILLS_DIR}" ]; then
  find "${SKILLS_DIR}" -type f -name '*.md' -print0 \
    | xargs -0 grep -H -n -E "${PATTERN}" 2>/dev/null \
    | grep -v -E "${EXCLUDE_PATTERN}" \
    >> "${TMP_MATCHES}" || true
fi

# Scan .aod/scripts/bash/**/*.sh.
if [ -d "${SCRIPTS_DIR}" ]; then
  find "${SCRIPTS_DIR}" -type f -name '*.sh' -print0 \
    | xargs -0 grep -H -n -E "${PATTERN}" 2>/dev/null \
    | grep -v -E "${EXCLUDE_PATTERN}" \
    >> "${TMP_MATCHES}" || true
fi

# Drop any match that came from this check script itself.
if [ -s "${TMP_MATCHES}" ]; then
  FILTERED="$(mktemp -t check-no-merge-heal-f.XXXXXX)"
  trap 'rm -f "${TMP_MATCHES}" "${FILTERED}"' EXIT
  grep -v -F "${SELF_PATH}" "${TMP_MATCHES}" > "${FILTERED}" || true
  mv "${FILTERED}" "${TMP_MATCHES}"
fi

if [ -s "${TMP_MATCHES}" ]; then
  {
    echo "[check-no-merge-heal] INVARIANT VIOLATION: auto-merge pattern found on e2e-heal PRs"
    echo "[check-no-merge-heal] No AOD skill or script may invoke 'gh pr merge' on an 'e2e-heal' PR."
    echo "[check-no-merge-heal] Offending matches (file:line:content):"
    cat "${TMP_MATCHES}"
  } >&2
  exit 1
fi

echo "[check-no-merge-heal] invariant holds ✓"
exit 0
