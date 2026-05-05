#!/usr/bin/env bash
# tests/fixtures/regenerate-config-load-baseline.sh — F-2 BLP-02 Wave 2 deliverable (T045)
#
# Regenerates `tests/fixtures/config-load/{valid,adversarial}/` by deriving
# canonical-fixture content from current contracts and source files. The
# resulting fixtures are consumed by:
#   - tests/scripts/test_template_config_load_unit.py (Test-1, ≥27 cases)
#   - tests/scripts/test_template_config_load_integration.py (Test-2, all 4 sites)
#   - tests/scripts/test_init_sh_defaults_env.py (Test-4, Site A end-to-end)
#
# This script ALSO regenerates the byte-identity baseline at
# `tests/fixtures/init-baseline-tree/` consumed by
# tests/scripts/test_init_sh_substitution.py (F-1 Test-1). The baseline drifted
# in Wave 3 due to legitimate F-2 changes (TECH_STACK added to all 5 stack pack
# defaults.env + eval/escape pass removal in template-substitute.sh). The
# regen path delegates to `tests/fixtures/regenerate-baseline.sh` so the
# F-1 byte-comparison contract stays authoritative.
#
# WHEN to regenerate
# ──────────────────
# Regenerate when:
#   - The `STACK_PACK_ALLOWED_KEYS` whitelist in `scripts/init.sh` changes
#     (add or remove a canonical-5 key — must update `contracts/stack-pack-
#     defaults-schema.md` in lockstep first).
#   - The `AOD_CANONICAL_PLACEHOLDERS` set in `.aod/scripts/bash/template-
#     substitute.sh` changes (the F-1 canonical-12 personalization key list).
#   - The aod-kit-version 5-field schema (version, sha, updated_at,
#     upstream_url, manifest_sha256) changes — see Site B (`template-git.sh`).
#   - A canonical stack pack's `defaults.env` is intentionally edited (the
#     valid fixtures mirror the source-of-truth pack config).
#   - Site A integration tests reference a new shipped pack added under
#     `stacks/` — extend the generator list below.
#
# WHEN NOT to regenerate (anti-patterns)
# ─────────────────────────────────────────
# - "The regex test is failing; let me regenerate the fixture to make it pass."
#   → No. This is the canonical "regenerate to mask a regression" trap. If the
#     loader rejects a fixture that previously passed, the loader CHANGED —
#     investigate WHY before regenerating. The regression-protection contract
#     exists precisely to catch silent semantic drift in the parser.
# - "I edited the loader's regex; the unit cases are now red."
#   → No. The fixtures encode the contract. Edit the contract first
#     (config-load-helper-contract.md + stack-pack-defaults-schema.md), then
#     edit the loader, then regenerate fixtures only if the contract
#     requires new fixture shapes.
# - "The CI matrix is failing on macOS; I'll regenerate locally on Linux."
#   → No. Investigate the platform delta first. Locale / line-ending /
#     bash-version differences are real bugs to fix in the loader, not paper
#     over with a new baseline. The CI matrix is the source of truth.
# - "I want to add a new stack pack and a new test case for it."
#   → Add the pack first, update `STACK_PACK_ALLOWED_KEYS` if needed, add the
#     pack-specific fixture-generator block below, THEN run this script.
#
# Inputs (sources of truth)
# ─────────────────────────
# Reads canonical content from:
#   - `stacks/nextjs-supabase/defaults.env`        → valid/defaults-env-nextjs-supabase
#   - `stacks/fastapi-react/defaults.env`          → valid/defaults-env-fastapi-react
#   - This script's CANONICAL_VERSION_FIELDS heredoc → valid/aod-kit-version-valid
#   - This script's CANONICAL_PERSONALIZATION_KEYS heredoc → valid/personalization-env-valid
#
# Adversarial fixtures are deterministically generated from heredocs in this
# script; the adversarial corpus enumerates Test-1 and Test-2 rejection cases.
# Each adversarial fixture carries the L-2 `# DO NOT SOURCE` header to deter
# accidental `source` invocation by reviewers or grep-greedy contributors.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONFIG_LOAD_DIR="${REPO_ROOT}/tests/fixtures/config-load"
VALID_DIR="${CONFIG_LOAD_DIR}/valid"
ADVERSARIAL_DIR="${CONFIG_LOAD_DIR}/adversarial"

if ! command -v cp >/dev/null 2>&1; then
    echo "[regen-config-load] FATAL: cp not on PATH" >&2
    exit 1
fi

mkdir -p "$VALID_DIR" "$ADVERSARIAL_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Valid fixtures
# ─────────────────────────────────────────────────────────────────────────────

# 1. defaults-env-nextjs-supabase — derive from the shipped pack with the
#    placeholder-bearing comment header stripped. The source pack's comment
#    contains literal canonical-placeholder markers (DOUBLE-BRACE forms of
#    TECH_STACK_* and CLOUD_PROVIDER) — those tokens cause the F-1
#    byte-identity regen scan to flag the test fixture itself as a
#    substitution target, which would corrupt the test data. Strip ALL
#    comment lines from the copy; the KV semantic content is the contract
#    surface the loader exercises.
#
#    Test-4 Site A case 1 verifies init.sh loads this cleanly via the
#    refactored aod_template_load_kv_file path on macOS bash 3.2 + Linux 5.x.
NEXTJS_SUPABASE_SRC="${REPO_ROOT}/stacks/nextjs-supabase/defaults.env"
NEXTJS_SUPABASE_DST="${VALID_DIR}/defaults-env-nextjs-supabase"
if [ ! -f "$NEXTJS_SUPABASE_SRC" ]; then
    echo "[regen-config-load] FATAL: source pack missing: $NEXTJS_SUPABASE_SRC" >&2
    exit 1
fi
echo "[regen-config-load] generating ${NEXTJS_SUPABASE_DST#$REPO_ROOT/}"
grep -v '^#' "$NEXTJS_SUPABASE_SRC" > "$NEXTJS_SUPABASE_DST"

# 2. defaults-env-fastapi-react — same comment-strip pattern as nextjs-supabase
#    (avoid canonical-placeholder leakage into the test fixture).
FASTAPI_REACT_SRC="${REPO_ROOT}/stacks/fastapi-react/defaults.env"
FASTAPI_REACT_DST="${VALID_DIR}/defaults-env-fastapi-react"
if [ ! -f "$FASTAPI_REACT_SRC" ]; then
    echo "[regen-config-load] FATAL: source pack missing: $FASTAPI_REACT_SRC" >&2
    exit 1
fi
echo "[regen-config-load] generating ${FASTAPI_REACT_DST#$REPO_ROOT/}"
grep -v '^#' "$FASTAPI_REACT_SRC" > "$FASTAPI_REACT_DST"

# 3. aod-kit-version-valid — generate the canonical 5-field lowercase form
#    per Site B (`template-git.sh:568+` per-field validators).
#    Used by:
#      - Test-1 case_26a (lower-mode regex coverage)
#      - Test-2 Site-B-valid path (round-trip through aod_template_read_version_file)
#    The values here are placeholder fixtures — chose semantic-version + 40-char
#    SHA-1-ish + ISO-8601 UTC + canonical https URL + 64-char SHA-256-ish to
#    exercise the per-field regex validators with realistic shapes.
AOD_KIT_VERSION_DST="${VALID_DIR}/aod-kit-version-valid"
echo "[regen-config-load] generating ${AOD_KIT_VERSION_DST#$REPO_ROOT/}"
cat > "$AOD_KIT_VERSION_DST" <<'EOF'
version='4.28.0'
sha=abc123def456abc123def456abc123def456abcd
updated_at=2026-05-04T12:00:00Z
upstream_url=https://github.com/example/upstream
manifest_sha256=abc123def456abc123def456abc123def456abc123def456abc123def456abcd
EOF

# 4. personalization-env-valid — generate the canonical-12 personalization
#    key set (F-1 canonical contract per personalization-schema.md). All 12
#    keys are required and double-quoted with allowlist-safe values. Used by:
#      - Test-2 Site-C-valid path (round-trip through aod_template_load_personalization_env)
PERSONALIZATION_DST="${VALID_DIR}/personalization-env-valid"
echo "[regen-config-load] generating ${PERSONALIZATION_DST#$REPO_ROOT/}"
cat > "$PERSONALIZATION_DST" <<'EOF'
PROJECT_NAME="tachi"
PROJECT_DESCRIPTION="Source-pattern hardening test fixture"
GITHUB_ORG="example-org"
GITHUB_REPO="example-repo"
AI_AGENT="Claude Code"
TECH_STACK="Next.js + TypeScript"
TECH_STACK_DATABASE="PostgreSQL (Supabase)"
TECH_STACK_VECTOR="pgvector"
TECH_STACK_AUTH="Supabase Auth"
RATIFICATION_DATE="2026-05-04"
CURRENT_DATE="2026-05-05"
CLOUD_PROVIDER="Vercel"
EOF

# ─────────────────────────────────────────────────────────────────────────────
# Adversarial fixtures
# ─────────────────────────────────────────────────────────────────────────────
#
# Each adversarial fixture carries the L-2 `# DO NOT SOURCE` header. The
# fixtures correspond to Test-1 (unit) and Test-2 (integration) rejection
# cases. Some fixtures already exist on disk from prior waves (T018, T020);
# they are regenerated deterministically here to keep the script the single
# source of truth — re-running the script must yield byte-identical output.

# 5. malicious-pack-defaults.env — Site A injection attempt (T018 origin).
#    Pre-F-2 init.sh `source` would execute the CUSTOM_HOOK command
#    substitution and create /tmp/F-256-pwned. Post-F-2 the loader rejects
#    with exit 8 BEFORE any `printf -v` runs — the regex rejects the line.
MALICIOUS_PACK_DST="${ADVERSARIAL_DIR}/malicious-pack-defaults.env"
echo "[regen-config-load] generating ${MALICIOUS_PACK_DST#$REPO_ROOT/}"
cat > "$MALICIOUS_PACK_DST" <<'EOF'
# DO NOT SOURCE — malicious test fixture (L-2 header)
# Adversarial fixture used by tests/scripts/test_init_sh_defaults_env.py case 2.
# A pre-F-2 init.sh would `source` this file as bash, executing the
# command substitution in CUSTOM_HOOK and creating /tmp/F-256-pwned.
# The post-F-2 library MUST reject this file with exit 8 BEFORE any
# command substitution can fire.
TECH_STACK="malicious"
TECH_STACK_DATABASE="malicious"
TECH_STACK_VECTOR="malicious"
TECH_STACK_AUTH="malicious"
CLOUD_PROVIDER="malicious"
CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"
EOF

# 6. missing-key-pack-defaults.env — Site A whitelist-missing case (T018).
#    Omits CLOUD_PROVIDER from the canonical 5-key whitelist. Post-F-2 the
#    loader's post-pass completeness check rejects with exit 8 + missing-key
#    error message naming CLOUD_PROVIDER.
MISSING_KEY_DST="${ADVERSARIAL_DIR}/missing-key-pack-defaults.env"
echo "[regen-config-load] generating ${MISSING_KEY_DST#$REPO_ROOT/}"
cat > "$MISSING_KEY_DST" <<'EOF'
# DO NOT SOURCE — adversarial test fixture (L-2 header)
# Adversarial fixture used by tests/scripts/test_init_sh_defaults_env.py case 3.
# This fixture deliberately omits CLOUD_PROVIDER from the canonical 5-key
# whitelist. The post-F-2 library MUST reject this file with exit 8 +
# missing-key error message via STACK_PACK_ALLOWED_KEYS post-pass check.
TECH_STACK="incomplete-stack"
TECH_STACK_DATABASE="some-database"
TECH_STACK_VECTOR="N/A"
TECH_STACK_AUTH="JWT"
EOF

# 7. aod-kit-version-malformed — Site B injection attempt (T020 origin).
#    Pre-F-2 `source` would execute the `; touch /tmp/F-256-pwned` injection
#    AFTER assigning version='1.0'. Post-F-2 the loader's strict KV regex
#    rejects the line (semicolon not in unquoted-value class; even
#    quoted-value class rejects semicolons via the strict allowlist).
AOD_KIT_MALFORMED_DST="${ADVERSARIAL_DIR}/aod-kit-version-malformed"
echo "[regen-config-load] generating ${AOD_KIT_MALFORMED_DST#$REPO_ROOT/}"
cat > "$AOD_KIT_MALFORMED_DST" <<'EOF'
# DO NOT SOURCE — malicious test fixture (L-2 header)
# Adversarial fixture used by tests/scripts/test_template_config_load_integration.py
# Site-B-malformed case. A pre-F-2 `source` call would execute the
# `; touch /tmp/F-256-pwned` injection AFTER assigning version='1.0'.
# The post-F-2 library MUST reject this file with exit 8 (regex rejects
# ; / $ in unquoted values; even quoted values reject ; via the strict
# value class).
version='1.0'; touch /tmp/F-256-pwned
sha=abc123def456abc123def456abc123def456abcd
updated_at=2026-05-04T12:00:00Z
upstream_url=https://github.com/example/upstream
manifest_sha256=abc123def456abc123def456abc123def456abc123def456abc123def456abcd
EOF

# ─────────────────────────────────────────────────────────────────────────────
# Summary + validation pass
# ─────────────────────────────────────────────────────────────────────────────

VALID_COUNT=$(find "$VALID_DIR" -type f | wc -l | tr -d ' ')
ADVERSARIAL_COUNT=$(find "$ADVERSARIAL_DIR" -type f | wc -l | tr -d ' ')

echo "[regen-config-load] config-load fixtures regenerated:"
echo "[regen-config-load]   valid/        ${VALID_COUNT} file(s)"
echo "[regen-config-load]   adversarial/  ${ADVERSARIAL_COUNT} file(s)"

# Sanity check: every adversarial fixture MUST carry the L-2 `# DO NOT SOURCE`
# header. A future fixture-author who forgets the header would defeat the L-2
# convention; this check fails fast.
HEADER_VIOLATIONS=0
for f in "$ADVERSARIAL_DIR"/*; do
    [ -f "$f" ] || continue
    if ! head -n 5 "$f" | grep -q "DO NOT SOURCE"; then
        echo "[regen-config-load] WARNING: adversarial fixture missing L-2 header: $f" >&2
        HEADER_VIOLATIONS=$((HEADER_VIOLATIONS + 1))
    fi
done
if [ "$HEADER_VIOLATIONS" -gt 0 ]; then
    echo "[regen-config-load] FATAL: ${HEADER_VIOLATIONS} adversarial fixture(s) missing L-2 header" >&2
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Byte-identity baseline regen (init-baseline-tree)
# ─────────────────────────────────────────────────────────────────────────────
#
# The byte-identity baseline at tests/fixtures/init-baseline-tree/ drifted
# in F-2 Wave 3 due to legitimate F-2 changes:
#   - TECH_STACK key added to all 5 shipped stacks/*/defaults.env files
#   - .aod/scripts/bash/template-substitute.sh: eval removal + escape pass
#     removal (Site C — F-2 BLP-02 Wave 2)
#   - docs/architecture/01_system_design/README.md, docs/devops/CI_CD_GUIDE.md,
#     docs/INSTITUTIONAL_KNOWLEDGE.md content edits (placeholder-bearing files)
#
# Delegate to tests/fixtures/regenerate-baseline.sh (the F-1 source of truth
# for byte-identity contract). That script clones the repo, overlays
# uncommitted working-tree changes, runs init.sh against the canonical
# fixture inputs, and copies post-substitution bytes into init-baseline-tree/.
#
# This block is the ONLY place in the F-2 wave that triggers the byte-identity
# refresh. /aod.deliver re-runs Test-1 (test_init_sh_substitution.py) at the
# pre-merge gate; the baseline must already match by then.

F1_REGEN_SCRIPT="${REPO_ROOT}/tests/fixtures/regenerate-baseline.sh"
if [ -x "$F1_REGEN_SCRIPT" ]; then
    echo "[regen-config-load] delegating to F-1 byte-identity regen: ${F1_REGEN_SCRIPT#$REPO_ROOT/}"
    "$F1_REGEN_SCRIPT"
else
    echo "[regen-config-load] WARNING: F-1 regen script not executable or missing at $F1_REGEN_SCRIPT" >&2
    echo "[regen-config-load]          init-baseline-tree/ NOT refreshed; Test-1 byte-comparison may drift" >&2
fi

echo "[regen-config-load] DONE — review git diff and commit fixtures + baseline"
