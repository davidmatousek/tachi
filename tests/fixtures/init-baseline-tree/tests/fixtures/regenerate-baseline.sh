#!/usr/bin/env bash
# tests/fixtures/regenerate-baseline.sh — F-248 BLP-02 Wave 1 deliverable (T013)
#
# Regenerates `tests/fixtures/init-baseline-tree/` by running scripts/init.sh
# against a tmpdir clone of the current repo with the canonical fixture
# inputs. The resulting personalized tree is the byte-comparison baseline
# consumed by `test_init_sh_substitution.py` (Test-1).
#
# WHEN to regenerate
# ──────────────────
# Regenerate ONLY when the canonical placeholder set legitimately expands
# (e.g., AOD_CANONICAL_PLACEHOLDERS gains a 13th key under Q-1 Option a
# fallback) or when an upstream content change in `tachi` legitimately
# alters the expected output bytes (new docs file added, existing doc
# edited intentionally).
#
# DO NOT regenerate to mask a substitution-semantics regression. If a
# Test-1 byte-comparison fails after a code change, investigate whether
# the substitution mechanism itself drifted before regenerating. The
# baseline is the contract; regeneration is the rare, deliberate update
# of that contract.
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

echo "[regen] copying personalized tree → ${BASELINE_DIR}"
rm -rf "$BASELINE_DIR"
mkdir -p "$BASELINE_DIR"

# Mirror init.sh's find filter: exclude .git/, node_modules/, *.png/jpg/ico.
# Use rsync if available (preserves modes); fall back to find+cp.
if command -v rsync >/dev/null 2>&1; then
    rsync -a \
        --exclude='.git/' \
        --exclude='node_modules/' \
        --exclude='*.png' \
        --exclude='*.jpg' \
        --exclude='*.ico' \
        --exclude='tests/fixtures/init-baseline-tree/' \
        "${CLONE_ROOT}/" "${BASELINE_DIR}/"
else
    (cd "$CLONE_ROOT" && find . -type f \
        -not -path './.git/*' \
        -not -path './node_modules/*' \
        -not -path './tests/fixtures/init-baseline-tree/*' \
        -not -name '*.png' -not -name '*.jpg' -not -name '*.ico' \
        -print0 | while IFS= read -r -d '' f; do
            mkdir -p "${BASELINE_DIR}/$(dirname "$f")"
            cp -p "$f" "${BASELINE_DIR}/$f"
        done)
fi

echo "[regen] baseline regenerated. Files: $(find "$BASELINE_DIR" -type f | wc -l | tr -d ' ')"
echo "[regen] commit the diff under ${BASELINE_DIR}/"
