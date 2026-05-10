#!/usr/bin/env bash
# =============================================================================
# tests/fixtures/gitleaks-rule-interaction/run.sh
# =============================================================================
# F-5 gitleaks rule-interaction matrix runner.
#
# Per Architect CONCERN-1 (HIGH): co-located here, NOT under `tests/scripts/`
# (which is pytest-only territory).
#
# Iterates 16 fixtures across 4 subdirectories, sets up a simulated repo path
# under a tmpdir to exercise path-allow-list semantics, invokes gitleaks
# against each scenario, and compares finding count to the expected outcome.
#
# Exit codes: 0 if all 16 pass, 1 if any fail.
#
# Bash 3.2 compatible.
# =============================================================================

set -e

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FIXTURES="$ROOT/tests/fixtures/gitleaks-rule-interaction"
CONFIG="$ROOT/.gitleaks.toml"

if [ ! -f "$CONFIG" ]; then
  echo "ERROR: .gitleaks.toml not found at $CONFIG" >&2
  exit 1
fi

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "ERROR: gitleaks binary not found on PATH (install via brew, asdf, or pre-commit env)" >&2
  exit 1
fi

TMPBASE="$(mktemp -d -t gitleaks-rule-interaction-XXXXXX)"
trap 'rm -rf "$TMPBASE"' EXIT

PASS=0
FAIL=0
TOTAL=0
FAIL_DETAILS=""

# Colors (skip if NO_COLOR or non-tty)
if [ -n "${NO_COLOR:-}" ] || [ ! -t 1 ]; then
  RED=''
  GREEN=''
  NC=''
else
  RED=$'\033[0;31m'
  GREEN=$'\033[0;32m'
  NC=$'\033[0m'
fi

# ---------------------------------------------------------------------------
# scan_case <case_id> <subdir> <fixture_filename> <sim_path> <expected>
# ---------------------------------------------------------------------------
#   case_id          short label for logging
#   subdir           subdirectory under tests/fixtures/gitleaks-rule-interaction/
#   fixture_filename file name under <subdir>
#   sim_path         simulated repo-relative path under TMPBASE/case-<id>/
#                    (gitleaks path-allow-list matches against this prefix)
#   expected         "fire" or "nofire"
scan_case() {
  case_id="$1"
  subdir="$2"
  fixture_filename="$3"
  sim_path="$4"
  expected="$5"

  TOTAL=$((TOTAL + 1))

  case_dir="$TMPBASE/case-$case_id"
  target="$case_dir/$sim_path"
  mkdir -p "$(dirname "$target")"
  cp "$FIXTURES/$subdir/$fixture_filename" "$target"

  report="$case_dir/report.json"
  # gitleaks dir scans the path recursively. Suppress stdout/stderr; rely on
  # the JSON report for finding count. Tolerate non-zero exit (findings are
  # success in this context).
  gitleaks dir "$case_dir" \
    --config="$CONFIG" \
    --no-banner \
    --report-format=json \
    --report-path="$report" \
    >/dev/null 2>&1 || true

  findings=0
  if [ -s "$report" ]; then
    # Each finding has a "RuleID" key; count occurrences. Avoid the
    # `grep -c ... || echo 0` antipattern (concatenates "0\n0" on no-match
    # because grep STILL outputs "0" before exiting non-zero).
    count=$(grep -c '"RuleID"' "$report" 2>/dev/null) || count=0
    findings=$count
  fi

  if [ "$expected" = "fire" ] && [ "$findings" -ge 1 ]; then
    PASS=$((PASS + 1))
    printf "%sPASS%s %s (expected fire, got %s finding(s))\n" "$GREEN" "$NC" "$case_id" "$findings"
  elif [ "$expected" = "nofire" ] && [ "$findings" -eq 0 ]; then
    PASS=$((PASS + 1))
    printf "%sPASS%s %s (expected nofire, got %s finding(s))\n" "$GREEN" "$NC" "$case_id" "$findings"
  else
    FAIL=$((FAIL + 1))
    printf "%sFAIL%s %s (expected %s, got %s finding(s))\n" "$RED" "$NC" "$case_id" "$expected" "$findings"
    FAIL_DETAILS="${FAIL_DETAILS}  $case_id (expected $expected, got $findings) -- report: $report\n"
  fi
}

echo "=== F-5 gitleaks rule-interaction matrix (16 cases) ==="
echo ""

# T009 — should-fire (6 cases). Path: a generic neutral path under TMPBASE/case-N/
# (NOT under any allow-listed prefix), so the rules SHOULD fire.
scan_case "01-github-pat"          "staged-credential" "github-pat.txt"                    "src/secrets.txt"  "fire"
scan_case "02-aws-access-key"      "staged-credential" "aws-access-key.txt"                "src/secrets.txt"  "fire"
scan_case "03-openai-key"          "staged-credential" "openai-key.txt"                    "src/secrets.txt"  "fire"
scan_case "04-anthropic-key"       "staged-credential" "anthropic-key.txt"                 "src/secrets.txt"  "fire"
scan_case "05-private-key"         "staged-credential" "private-key-block.pem"             "src/key.pem"      "fire"
scan_case "06-personalization-env" "staged-credential" "personalization-env-populated.env" "src/config.env"   "fire"

# T010 — should-NOT-fire (4 placeholder cases). Same neutral path; suppression
# comes from allow-list 1 regexes (placeholder/env-var patterns).
scan_case "07-env-var-ref"         "placeholder"       "env-var-reference.txt"   "src/config.txt"   "nofire"
scan_case "08-openai-placeholder"  "placeholder"       "openai-placeholder.env"  "src/config.env"   "nofire"
scan_case "09-sk-placeholder"      "placeholder"       "sk-placeholder.env"      "src/config.env"   "nofire"
scan_case "10-sk-test-stripe"      "placeholder"       "sk-test-stripe.env"      "src/config.env"   "nofire"

# T011 — should-NOT-fire (4 path-allow-listed cases). Suppression comes from
# allow-list 2 path regexes; runner places fixture at the matching path.
scan_case "11-personalization-template" "path-allow-listed" "personalization-env-example"          ".aod/personalization.env.example" "nofire"
scan_case "12-tests-fixtures"           "path-allow-listed" "tests-fixtures-fake-aws.txt"          "tests/fixtures/sample.txt"        "nofire"
scan_case "13-docs-placeholder"         "path-allow-listed" "docs-placeholder.md"                  "docs/example.md"                   "nofire"
scan_case "14-security-exceptions-auto" "path-allow-listed" "security-exceptions-jsonl-auto.jsonl" ".security/exceptions.jsonl"        "nofire"

# T012 — should-NOT-fire (2 excluded-path cases). Suppression comes from
# allow-list 3 path regexes; runner places fixture under simulated
# node_modules/ or archive/ subdir.
scan_case "15-node-modules" "path-excluded" "node-modules-credential.txt" "node_modules/sub/leak.txt" "nofire"
scan_case "16-archive"      "path-excluded" "archive-credential.txt"      "archive/old/leak.txt"      "nofire"

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed (${TOTAL} total) ==="

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "Failed cases:"
  printf "%b" "$FAIL_DETAILS"
  exit 1
fi
exit 0
