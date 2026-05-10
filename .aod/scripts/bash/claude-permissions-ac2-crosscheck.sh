#!/usr/bin/env bash
# =============================================================================
# claude-permissions-ac2-crosscheck.sh — F-4 AC-2 cross-check (FR-002)
# =============================================================================
# Verifies that every non-built-in rule in `.claude/settings.json` appears in
# the §4 per-rule rationale table of `docs/standards/CLAUDE_PERMISSIONS.md`,
# AND that every §4 table row references a rule present in settings.json.
#
# Implements the awk-section-marker form codified in PR #278 commit ec0b628
# (architect P1 Minor #2 reconciliation). Section extraction is restricted to
# §4 so §5 (built-in read-only set) and §6 (opt-out paths) illustrative
# examples don't produce false-positive orphans. Markdown-pipe unescape
# (`\|` → `|`) ensures clean diff against JSON-literal rules containing pipes
# such as `Bash(curl * | sh)`.
#
# Invocation contexts:
#   - `.pre-commit-config.yaml` local hook on edits to `.claude/settings.json`
#     or `docs/standards/CLAUDE_PERMISSIONS.md` (issue #280)
#   - Manual run from repo root: `bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`
#   - Future CI workflow per #281
#
# Bash 3.2 compatible (macOS-native). No associative arrays, no `mapfile`.
#
# Exit codes:
#   0 — empty diff (PASS); JSON rules and §4 table rows match exactly.
#   1 — non-empty diff (FAIL); structured stderr lists the orphans.
#   2 — invariant violation (missing files, jq parse error, awk section empty).
# =============================================================================

set -u

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SETTINGS="${ROOT}/.claude/settings.json"
DOCS="${ROOT}/docs/standards/CLAUDE_PERMISSIONS.md"

if [ ! -f "$SETTINGS" ]; then
  echo "[ac2-crosscheck] FATAL: $SETTINGS not found" >&2
  exit 2
fi
if [ ! -f "$DOCS" ]; then
  echo "[ac2-crosscheck] FATAL: $DOCS not found" >&2
  exit 2
fi

TMP="$(mktemp -d -t ac2-crosscheck.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

RULES="${TMP}/rules.txt"
DOC_RULES="${TMP}/doc-rules.txt"

# Extract every rule from settings.json (deny + ask + allow combined).
# `jq` exits non-zero on parse error; the `||` branch reports it.
if ! jq -r '.permissions.deny[], .permissions.ask[], .permissions.allow[]' \
     "$SETTINGS" 2>/dev/null | sort -u > "$RULES"; then
  echo "[ac2-crosscheck] FATAL: jq parse failed on $SETTINGS" >&2
  exit 2
fi

# Extract rules from §4 (Per-rule rationale table) of CLAUDE_PERMISSIONS.md.
# `awk '/^## 4\./,/^## 5\./'` selects the inclusive block between §4 and §5
# headers. `grep -E '^\| \`'` keeps only table data rows (the header row
# starts with `| Rule |` not `| \`Bash...`). `sed -E` extracts the
# back-tick-quoted rule literal. The final `sed 's/\\|/|/g'` unescapes the
# markdown pipe character.
awk '/^## 4\./,/^## 5\./' "$DOCS" \
  | grep -E '^\| `' \
  | sed -E 's/^\| `([^`]+)` \|.*/\1/' \
  | sed 's/\\|/|/g' \
  | sort -u > "$DOC_RULES"

if [ ! -s "$DOC_RULES" ]; then
  echo "[ac2-crosscheck] FATAL: §4 extraction produced empty rule list — verify section headers (## 4. … ## 5.) in $DOCS" >&2
  exit 2
fi

# Compare. `diff -u` produces a unified diff; we use plain `diff` here so the
# orphan classification (left-only vs right-only) is unambiguous.
if diff "$RULES" "$DOC_RULES" > "${TMP}/diff.out" 2>&1; then
  exit 0
fi

# Non-empty diff. Print structured stderr and fail.
{
  echo ""
  echo "──────────────────────────────────────────────────────────────"
  echo "Commit refused: F-4 AC-2 cross-check (FR-002) found drift between"
  echo "  .claude/settings.json  ↔  docs/standards/CLAUDE_PERMISSIONS.md §4"
  echo ""
  echo "  Diff (< rules in settings.json missing from §4 table;"
  echo "        > rows in §4 table referencing rules not in settings.json):"
  echo ""
  sed 's/^/      /' "${TMP}/diff.out"
  echo ""
  echo "  Fix: add the missing rule to the §4 per-rule rationale table"
  echo "       OR remove the orphaned table row, depending on intent."
  echo "       Reference: docs/standards/CLAUDE_PERMISSIONS.md §4"
  echo "                  (Per-rule rationale table)"
  echo "──────────────────────────────────────────────────────────────"
} >&2

exit 1
