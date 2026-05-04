#!/usr/bin/env bash
# tests/fixtures/regenerate-baseline.sh — F-248 BLP-02 Wave 1 deliverable (T013)
#                                         + F-250 substitution-target restriction
#
# Regenerates `tests/fixtures/init-baseline-tree/` by running scripts/init.sh
# against a tmpdir clone of the current repo with the canonical fixture
# inputs. The resulting baseline is the byte-comparison contract consumed
# by `test_init_sh_substitution.py` (Test-1).
#
# F-250 SCOPE RESTRICTION
# ───────────────────────
# The baseline now captures ONLY files that are SUBSTITUTION TARGETS — i.e.,
# files whose source content (pre-substitution) contains at least one of
# the canonical `{{KEY}}` placeholders. The full source tree (~600 files)
# is NOT copied; only ~5-10 files containing canonical placeholders.
#
# Rationale: pre-F-250, the baseline copied the full tree, so ANY content
# edit to ANY file (docs, specs, generated artifacts) caused a stale-baseline
# CI failure on the next PR. The recurring "regenerate baseline" maintenance
# tax conflated two distinct contracts — substitution semantics vs. file
# bag parity — neither of which the broad scope served well. Restricting
# to substitution targets:
#   - Catches genuine substitution regressions (case_1 ampersand, multibyte,
#     locale issues) on the small set of files that actually get substituted.
#   - Tolerates routine repo growth (new docs, specs, test artifacts) without
#     fail-on-every-PR drift.
#   - Reduces baseline size from ~600 files to ~5-10, making `git diff`
#     review trivial and regen runs fast.
#
# WHEN to regenerate
# ──────────────────
# Regenerate when:
#   - A new file with canonical `{{KEY}}` placeholders is added to the repo.
#   - An existing placeholder-bearing file is intentionally edited.
#   - The canonical placeholder set itself changes
#     (AOD_CANONICAL_PLACEHOLDERS in template-substitute.sh).
#
# DO NOT regenerate to mask a substitution-semantics regression. If a
# byte-comparison fails after a code change, investigate whether the
# substitution mechanism itself drifted before regenerating.
#
# WHEN NOT to regenerate (anti-patterns)
# ─────────────────────────────────────────
# - "The test is failing on my machine; let me regenerate locally."
#   → No. Investigate the platform delta first (locale, line endings,
#     bash version). The CI matrix is the source of truth.
# - "I added a new placeholder and the baseline is now stale."
#   → Update the canonical-12 array in template-substitute.sh, then
#     update personalization-schema.md, THEN regenerate this baseline
#     in lockstep. Skipping the schema/contract updates is a violation.
# - "I edited a non-placeholder file (README.md, docs, specs) and CI
#   complains about baseline drift."
#   → This should NOT happen post-F-250. The baseline only includes
#     substitution targets; non-target edits are tolerated. If you do see
#     a drift fail on a non-target file, the baseline restriction logic
#     below is broken — investigate.
#
# Inputs
# ──────
# Reads the canonical fixture inputs from the CANONICAL_INPUTS section
# below. Modify those lines if the fixture contract intentionally changes.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BASELINE_DIR="${REPO_ROOT}/tests/fixtures/init-baseline-tree"

if ! command -v git >/dev/null 2>&1; then
    echo "[regen] FATAL: git not on PATH" >&2
    exit 1
fi

# Compute number of stack packs at HEAD so the "Other" choice index is correct.
PACK_COUNT=0
for d in "${REPO_ROOT}"/stacks/*/; do
    [ -f "${d}STACK.md" ] && PACK_COUNT=$((PACK_COUNT + 1))
done
OTHER_INDEX=$((PACK_COUNT + 1))

# Canonical fixture inputs (one per init.sh prompt, in order).
CANONICAL_INPUTS="tachi
threat modeling sidecar
benchmark-test-org

1
${OTHER_INDEX}
Python + FastAPI
PostgreSQL

Y
"

TMPDIR=$(mktemp -d -t aod-regen-baseline-XXXX)
trap 'rm -rf "$TMPDIR"' EXIT

CLONE_ROOT="${TMPDIR}/tachi"
HEAD_SHA="$(cd "$REPO_ROOT" && git rev-parse HEAD)"
echo "[regen] cloning ${REPO_ROOT} HEAD=${HEAD_SHA:0:8} → ${CLONE_ROOT}"
git clone --quiet "file://${REPO_ROOT}" "$CLONE_ROOT"
(cd "$CLONE_ROOT" && git checkout --quiet "$HEAD_SHA")

# F-250 amendment: overlay uncommitted working-tree changes onto the clone.
#
# Without this overlay, regen reflects ONLY the committed HEAD state — so a
# maintainer iterating with edits in flight (e.g., during /aod.build) gets a
# baseline that doesn't match their working tree. CI then fails on the next
# push because the freshly-committed source diverges from the stale baseline.
#
# Three working-tree mutation classes are overlaid:
#   - Modified tracked files (M)   → cp from REPO_ROOT to CLONE_ROOT
#   - New untracked-not-ignored (?) → cp + mkdir parent
#   - Deleted tracked files (D)    → rm from CLONE_ROOT
# Gitignored files (.aod/update-tmp/, .aod/results/, etc.) are excluded
# automatically because `git ls-files --others --exclude-standard` honors
# .gitignore.
UNCOMMITTED=$(cd "$REPO_ROOT" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$UNCOMMITTED" -gt 0 ]; then
    echo "[regen] overlaying $UNCOMMITTED uncommitted working-tree change(s) onto clone…"
    # Modified tracked files
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        if [ -f "${REPO_ROOT}/${f}" ]; then
            cp "${REPO_ROOT}/${f}" "${CLONE_ROOT}/${f}" 2>/dev/null || true
        fi
    done < <(cd "$REPO_ROOT" && git diff HEAD --name-only --diff-filter=M 2>/dev/null)
    # New untracked-not-ignored files
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        if [ -f "${REPO_ROOT}/${f}" ]; then
            mkdir -p "${CLONE_ROOT}/$(dirname "$f")"
            cp "${REPO_ROOT}/${f}" "${CLONE_ROOT}/${f}" 2>/dev/null || true
        fi
    done < <(cd "$REPO_ROOT" && git ls-files --others --exclude-standard 2>/dev/null)
    # Deleted tracked files
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        rm -f "${CLONE_ROOT}/${f}"
    done < <(cd "$REPO_ROOT" && git diff HEAD --name-only --diff-filter=D 2>/dev/null)
fi

FAKE_HOME="${TMPDIR}/fake_home"
mkdir -p "$FAKE_HOME"

echo "[regen] running scripts/init.sh with canonical inputs (LC_ALL=C, HOME isolated, dates pinned to 2026-05-04)"
(
    cd "$CLONE_ROOT"
    # AOD_*_DATE_OVERRIDE pin RATIFICATION_DATE + CURRENT_DATE to the same
    # wall-clock value used by the test harness (init_sh_helpers.py). Without
    # this, the baseline captures the regen-time local date (e.g., dev EDT
    # 2026-05-03) which Test-1 then byte-compares against the test-time
    # date (e.g., ubuntu CI UTC 2026-05-04) → false drift on every TZ-edge run.
    #
    # IMPORTANT: env-var prefixes apply to the FIRST command in a pipeline
    # only, so they MUST be on the `bash` invocation (consumer), NOT the
    # `printf` (producer). Putting them on printf was a bug that silently
    # used the regen-machine's wall-clock date instead.
    printf '%s' "$CANONICAL_INPUTS" | \
        LC_ALL=C HOME="$FAKE_HOME" \
        AOD_RATIFICATION_DATE_OVERRIDE=2026-05-04 \
        AOD_CURRENT_DATE_OVERRIDE=2026-05-04 \
        bash ./scripts/init.sh > /dev/null 2>&1
) || {
    echo "[regen] FATAL: init.sh failed in tmpdir clone — baseline NOT regenerated" >&2
    exit 1
}

# F-250 SUBSTITUTION-TARGET RESTRICTION
# ─────────────────────────────────────
# Identify SUBSTITUTION TARGETS — files in the SOURCE tree (REPO_ROOT)
# that contain at least one canonical `{{KEY}}` placeholder. Only these
# files participate in the byte-comparison contract; non-target files
# pass through init.sh as a copy and are not part of this baseline.
#
# Scan the SOURCE (REPO_ROOT), not the post-init CLONE_ROOT, because
# init.sh has already substituted away the placeholders in the clone —
# the clone's `{{KEY}}` markers are gone after the substitution loop runs.

PLACEHOLDER_REGEX='\{\{(PROJECT_NAME|PROJECT_DESCRIPTION|GITHUB_ORG|GITHUB_REPO|AI_AGENT|TECH_STACK|TECH_STACK_DATABASE|TECH_STACK_VECTOR|TECH_STACK_AUTH|RATIFICATION_DATE|CURRENT_DATE|CLOUD_PROVIDER)\}\}'

TARGET_LIST=$(mktemp)
trap 'rm -rf "$TMPDIR" "$TARGET_LIST"' EXIT

echo "[regen] scanning source for substitution targets (canonical placeholders)…"
# Use `git ls-files` (cached + others-not-ignored) to honor .gitignore
# automatically. A bare `find` would match gitignored files like
# `.aod/results/*.md` (review artifacts that mention canonical placeholders
# in agent docs) and inflate TARGET_COUNT with files init.sh never sees.
# The init-baseline-tree itself is gitignored via tests/fixtures/.gitignore
# (or excluded explicitly below), and binary assets like *.png are out-of-
# scope for substitution by definition.
(cd "$REPO_ROOT" && git ls-files -z --cached --others --exclude-standard \
    | xargs -0 grep -lE "$PLACEHOLDER_REGEX" 2>/dev/null \
    | grep -vE '^tests/fixtures/init-baseline-tree/' \
    | grep -vE '\.(png|jpg|ico)$' \
    | sort) > "$TARGET_LIST" || true

TARGET_COUNT=$(grep -c '' "$TARGET_LIST" 2>/dev/null || echo 0)
if [ "$TARGET_COUNT" -lt 1 ]; then
    echo "[regen] FATAL: no substitution targets found in source." >&2
    echo "[regen]        The placeholder regex or source scan logic is broken." >&2
    exit 1
fi
echo "[regen] found $TARGET_COUNT substitution target(s):"
sed 's/^/[regen]   /' "$TARGET_LIST"

echo "[regen] copying post-substitution bytes → ${BASELINE_DIR}"
rm -rf "$BASELINE_DIR"
mkdir -p "$BASELINE_DIR"

MISSING_COUNT=0
while IFS= read -r rel; do
    [ -z "$rel" ] && continue
    src="${CLONE_ROOT}/${rel}"
    dst="${BASELINE_DIR}/${rel}"
    if [ ! -f "$src" ]; then
        echo "[regen]   note: target $rel removed by init.sh (e.g., self-delete) — skipping" >&2
        MISSING_COUNT=$((MISSING_COUNT + 1))
        continue
    fi
    mkdir -p "$(dirname "$dst")"
    cp -p "$src" "$dst"
done < "$TARGET_LIST"

FINAL_COUNT=$(find "$BASELINE_DIR" -type f | wc -l | tr -d ' ')
echo "[regen] baseline regenerated. Files: ${FINAL_COUNT} (skipped ${MISSING_COUNT} init.sh-removed)"
echo "[regen] commit the diff under ${BASELINE_DIR}/"
