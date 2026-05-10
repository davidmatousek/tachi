#!/usr/bin/env bash
# =============================================================================
# precommit-wrap.sh — gitleaks invocation wrapper for the pre-commit hook
# =============================================================================
# Part of feature 282 (F-5 pre-commit secret-scanning defaults, BLP-02 5/5).
#
# Invoked by `.pre-commit-config.yaml` as the entry point for the gitleaks
# hook. Wraps `gitleaks git --pre-commit --redact --staged --verbose` so we
# can augment the refused-commit stderr with the four-item structured
# contract (rule ID + file:line + bypass guidance + docs link).
#
# Pre-Mortem FM-5 pattern: capture exit code BEFORE stderr augmentation so a
# failure inside the augmentation block cannot mask gitleaks' own exit code.
# Reference: .aod/scripts/bash/init-input.sh (rejection-ladder precedent).
#
# Scope: LOCAL-ONLY. The CI parity workflow at `.github/workflows/gitleaks.yml`
# invokes gitleaks directly to preserve native SARIF output for GitHub Code
# Scanning compatibility (per spec PM-5 / ADR-042 §Decision).
#
# Bash 3.2 compatible (macOS-native). No associative arrays, no `mapfile`,
# no `${var,,}`, no `&>` redirection.
#
# Exit codes: gitleaks' own exit code is preserved verbatim. The wrapper
# never alters rc — only augments stderr on rc != 0.
#
# See ADR-042 §Decision and docs/standards/PRECOMMIT_HOOKS.md for design.
# =============================================================================

# Use explicit error handling (NOT `set -e`) so we can capture gitleaks' rc
# without an early bail-out. The exit-code-capture pattern below is the
# critical FM-5 defense.

# Locate repo root (pre-commit invokes hooks from repo root; the
# `git rev-parse` form is defensive against odd invocation contexts).
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Run gitleaks against staged content. Flags chosen to mirror the gitleaks
# upstream default pre-commit hook contract (--pre-commit, --redact, --staged,
# --verbose). The --config path is repo-relative.
gitleaks git --pre-commit --redact --staged --verbose --config="${ROOT}/.gitleaks.toml"
rc=$?

# FM-5 pattern: capture rc before any further work. The augmentation block
# runs only on non-zero rc and emits to stderr, then we exit with the
# preserved rc. This guarantees gitleaks' exit code reaches the pre-commit
# framework regardless of what the augmentation block does.
if [ "$rc" -ne 0 ]; then
  {
    echo ""
    echo "──────────────────────────────────────────────────────────────"
    echo "Commit refused: secret-scanning hook (gitleaks) found a match."
    echo ""
    echo "  Rule ID and file:line — see gitleaks output above."
    echo ""
    echo "  Bypass for a known-good case (e.g., a placeholder-only fixture):"
    echo "      SKIP=gitleaks git commit ..."
    echo ""
    echo "  Full bypass / opt-out / remediation guide:"
    echo "      docs/standards/PRECOMMIT_HOOKS.md"
    echo "──────────────────────────────────────────────────────────────"
  } >&2
fi

exit $rc
