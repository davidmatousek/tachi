#!/usr/bin/env bash
# =============================================================================
# bootstrap.sh — Downstream-adopter bootstrap subcommand implementation
# =============================================================================
# Part of Feature 134 (Downstream Update Bootstrap + Placeholder Migration).
#
# Referenced by plan.md §Components:
#   - Owns: overwrite-guard (FR-002-a), PLSK-fingerprint guard (FR-002-b),
#     upstream URL resolution (FR-003), shallow-clone orchestration via F129
#     fetch helper (FR-004, FR-005), auto-discovery heuristics (FR-006),
#     confirmation UX (FR-007), atomic personalization + version-file writes
#     (FR-008).
#
# Data flow (plan.md §System Design):
#   scripts/update.sh --bootstrap
#     └─> bootstrap.sh:aod_bootstrap_main
#          ├─> guard_check_overwrite()            # FR-002-a
#          ├─> guard_check_plsk_fingerprint()     # FR-002-b
#          ├─> resolve_upstream_url()             # FR-003
#          ├─> aod_template_fetch_upstream(...)   # F129 helper
#          ├─> compute_version_fields()           # sha, version, updated_at, manifest_sha256
#          ├─> auto_discover_8()                  # FR-006
#          ├─> always_prompt_4_or_env()           # FR-006 + FR-007
#          ├─> confirm_summary()                  # FR-007
#          ├─> aod_template_init_personalization  # F129 helper, writes first
#          └─> aod_template_write_version_file    # F129 helper, commit point
#
# Bash 3.2 compatible (macOS default /bin/bash). No declare -A, readarray,
# ${var^}/${var,,}, or |&. Per FR-018 + CLAUDE.md KB Entry 6.
#
# Helper-call pattern: every invocation of `aod_template_*` is wrapped in a
# `set +e` / `set -e` bracket that captures rc into a `local` variable BEFORE
# any other command executes. Precedent: scripts/check-manifest-coverage.sh:
# 115-118 (F132 silent-exit-5 prevention per FR-017).
#
# See:
#   - specs/134-update-bootstrap-placeholder-migration/plan.md §Components
#   - specs/134-update-bootstrap-placeholder-migration/spec.md FR-001..FR-019
#   - specs/134-update-bootstrap-placeholder-migration/contracts/cli-contract.md
#   - specs/134-update-bootstrap-placeholder-migration/data-model.md §Entity 5
# =============================================================================

set -euo pipefail

# Guard against double-sourcing (consistent with template-*.sh convention).
if [ -n "${AOD_BOOTSTRAP_SH_SOURCED:-}" ]; then
    return 0
fi
readonly AOD_BOOTSTRAP_SH_SOURCED=1

# -----------------------------------------------------------------------------
# Resolve repo-root + lib-dir so the helpers we depend on are always sourceable
# regardless of caller CWD. BASH_SOURCE[0] is the path to THIS file; its grand-
# parent directory is the repo root.
# -----------------------------------------------------------------------------
_aod_bootstrap_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_aod_bootstrap_lib_dir="$_aod_bootstrap_script_dir"
_aod_bootstrap_repo_root="$(cd "$_aod_bootstrap_script_dir/../../.." && pwd)"

# -----------------------------------------------------------------------------
# Source F129 helpers — AOD_CANONICAL_PLACEHOLDERS (single source of truth per
# T005 + data-model.md Entity 2), aod_template_init_personalization (FR-008),
# aod_template_fetch_upstream (FR-005), aod_template_write_version_file
# (FR-004). Per plan.md §Decision 5, helper signatures are API-stable through
# F134 delivery — this file only calls them, never redefines.
#
# Dynamically resolved library path (verified on disk at bootstrap-time).
# shellcheck disable=SC1091
. "$_aod_bootstrap_lib_dir/template-substitute.sh"
# shellcheck disable=SC1091
. "$_aod_bootstrap_lib_dir/template-git.sh"

# -----------------------------------------------------------------------------
# Canonical default upstream URL per FR-003. Documented here + in
# docs/guides/DOWNSTREAM_UPDATE.md (US-5).
# -----------------------------------------------------------------------------
AOD_BOOTSTRAP_DEFAULT_UPSTREAM_URL="https://github.com/davidmatousek/agentic-oriented-development-kit.git"

# =============================================================================
# Guards (FR-002-a, FR-002-b) — MUST be invoked FIRST in aod_bootstrap_main
# (per architect A-1 ordering: before any fetch, before any staging dir).
# =============================================================================

# -----------------------------------------------------------------------------
# guard_check_overwrite — FR-002-a
# -----------------------------------------------------------------------------
# Refuses `--bootstrap` with exit 2 when the adopter's repo already has a
# version pin at .aod/aod-kit-version. The pin is the authoritative
# "bootstrapped" signal (data-model.md §Entity 1): its presence transitions
# the repo to the terminal `bootstrapped` state.
#
# Behavior:
#   - Writes "refusing to overwrite existing .aod/aod-kit-version" to stderr
#   - Exits 2
#   - Called BEFORE any network call and BEFORE any staging dir is created
#     (so no trap is required when this path triggers)
#
# Inputs: AOD_BOOTSTRAP_REPO_ROOT (set by aod_bootstrap_main prior to call)
# Outputs: none (exits on trigger)
# -----------------------------------------------------------------------------
guard_check_overwrite() {
    local version_pin
    version_pin="$AOD_BOOTSTRAP_REPO_ROOT/.aod/aod-kit-version"
    if [ -f "$version_pin" ]; then
        printf 'refusing to overwrite existing .aod/aod-kit-version\n' >&2
        exit 2
    fi
    return 0
}

# -----------------------------------------------------------------------------
# guard_check_plsk_fingerprint — FR-002-b (sharpened, Decision 1)
# -----------------------------------------------------------------------------
# Refuses `--bootstrap` with exit 2 when the current working tree matches the
# PLSK meta-template fingerprint — a confused-deputy protection against
# running the adopter-facing bootstrap from inside the PLSK repo itself.
#
# Sharpened per Decision 1 (plan.md §Phase 0):
#   2-file presence AND (CANONICAL_URL grep-match OR git remote origin matches
#   product-led-spec-kit path). Either signal is sufficient; both together
#   would indicate a genuine PLSK checkout.
#
# Inputs: AOD_BOOTSTRAP_REPO_ROOT
# Outputs: none (exits on trigger)
# -----------------------------------------------------------------------------
guard_check_plsk_fingerprint() {
    local sync_script manifest root
    root="$AOD_BOOTSTRAP_REPO_ROOT"
    sync_script="$root/scripts/sync-upstream.sh"
    manifest="$root/.aod/template-manifest.txt"

    # Precondition: both fingerprint files present. If either absent, not PLSK.
    if [ ! -f "$sync_script" ] || [ ! -f "$manifest" ]; then
        return 0
    fi

    # Sharpening signal 1: CANONICAL_URL grep match in sync-upstream.sh
    if grep -qE '^CANONICAL_URL="https://github.com/davidmatousek/agentic-oriented-development-kit.git"' "$sync_script" 2>/dev/null; then
        printf 'refusing to bootstrap from within PLSK itself — this command is for downstream AOD-kit adopters\n' >&2
        exit 2
    fi

    # Sharpening signal 2: git remote origin URL matches PLSK path.
    # Execute git from within $root so the check is scoped to the working
    # tree under test, not some parent directory.
    local remote_url
    remote_url="$(cd "$root" 2>/dev/null && git remote get-url origin 2>/dev/null || true)"
    if [ -n "$remote_url" ] && printf '%s' "$remote_url" | grep -qE 'product-led-spec-kit(\.git)?$'; then
        printf 'refusing to bootstrap from within PLSK itself — this command is for downstream AOD-kit adopters\n' >&2
        exit 2
    fi

    return 0
}

# =============================================================================
# Upstream URL resolution (FR-003)
# =============================================================================

# -----------------------------------------------------------------------------
# resolve_upstream_url — FR-003
# -----------------------------------------------------------------------------
# Priority order:
#   1. --upstream-url=<url> flag (captured into AOD_BOOTSTRAP_URL_OVERRIDE by parse_flags)
#   2. AOD_UPSTREAM_URL env var
#   3. grep CANONICAL_URL= from scripts/sync-upstream.sh (robust; not
#      line-number-dependent)
#   4. Documented default: AOD_BOOTSTRAP_DEFAULT_UPSTREAM_URL (interactive only)
#   5. --yes mode without any of above + no CANONICAL_URL in sync-upstream.sh:
#      fail-fast with "upstream URL not set" guidance.
#
# Output: echoes the resolved URL to stdout. Non-zero exit on --yes-mode
# failure path.
# -----------------------------------------------------------------------------
resolve_upstream_url() {
    # Priority 1: --upstream-url flag override
    if [ -n "${AOD_BOOTSTRAP_URL_OVERRIDE:-}" ]; then
        printf '%s\n' "$AOD_BOOTSTRAP_URL_OVERRIDE"
        return 0
    fi

    # Priority 2: env var override
    if [ -n "${AOD_UPSTREAM_URL:-}" ]; then
        printf '%s\n' "$AOD_UPSTREAM_URL"
        return 0
    fi

    # Priority 3: grep CANONICAL_URL= from scripts/sync-upstream.sh
    local sync_script grep_line url
    sync_script="$AOD_BOOTSTRAP_REPO_ROOT/scripts/sync-upstream.sh"
    if [ -f "$sync_script" ]; then
        # grep -m1 returns first match; -E enables ERE for `=`. Extract the
        # value between the two double-quotes. Bash 3.2 safe: no regex
        # back-references; sed does the field split.
        grep_line="$(grep -m1 -E '^CANONICAL_URL=' "$sync_script" 2>/dev/null || true)"
        if [ -n "$grep_line" ]; then
            # Strip prefix up to the first quote, then trailing quote +
            # optional whitespace/comment. Works for both `VAR="..."` and
            # `VAR="..."  # comment`.
            url="$(printf '%s' "$grep_line" | sed -E 's/^CANONICAL_URL="([^"]*)".*/\1/')"
            if [ -n "$url" ]; then
                printf '%s\n' "$url"
                return 0
            fi
        fi
    fi

    # Priority 4/5: fall back to interactive prompt (default URL) OR fail
    # fast in --yes mode.
    if [ "${AOD_BOOTSTRAP_YES:-0}" = "1" ]; then
        printf 'Error: --yes mode requires AOD_UPSTREAM_URL env var or --upstream-url flag when CANONICAL_URL is not discoverable in scripts/sync-upstream.sh\n' >&2
        exit 1
    fi

    # Interactive: prompt with documented default.
    local reply tty_src=""
    if [ -r /dev/tty ]; then
        tty_src="/dev/tty"
    fi
    printf 'Enter upstream URL [default: %s]: ' "$AOD_BOOTSTRAP_DEFAULT_UPSTREAM_URL" >&2
    if [ -n "$tty_src" ]; then
        IFS= read -r reply < "$tty_src" || reply=""
    else
        IFS= read -r reply || reply=""
    fi
    if [ -z "$reply" ]; then
        reply="$AOD_BOOTSTRAP_DEFAULT_UPSTREAM_URL"
    fi
    printf '%s\n' "$reply"
    return 0
}

# =============================================================================
# Auto-discovery (FR-006) — 8 fields auto + 4 always-prompt
# =============================================================================

# -----------------------------------------------------------------------------
# _aod_bootstrap_set_confidence <field> <high|prompt|low>
# -----------------------------------------------------------------------------
# Record the confidence level for <field> in the per-field _confidence shell
# variable used by confirm_summary() to render the third column.
#
# Bash 3.2 has no associative arrays; we use `eval` with a strict regex
# whitelist on the field name to avoid code-injection risk.
# -----------------------------------------------------------------------------
_aod_bootstrap_set_confidence() {
    local field="$1"
    # level is consumed below via eval-indirect reference.
    # shellcheck disable=SC2034
    local level="$2"
    # Only allow canonical UPPER_UNDERSCORE names — defends against command
    # injection via eval.
    case "$field" in
        *[!A-Z0-9_]*)
            printf '[aod] ERROR: internal: invalid field name for confidence assignment: %s\n' "$field" >&2
            exit 1
            ;;
    esac
    eval "_confidence_${field}=\"\$level\""
}

# -----------------------------------------------------------------------------
# auto_discover_8 — FR-006 auto-discovered fields
# -----------------------------------------------------------------------------
# Resolves 8 canonical values from repo state. Each field sets the
# eponymous caller-scope shell variable (PROJECT_NAME etc. — which the F129
# aod_template_init_personalization helper reads from caller scope) and a
# parallel _confidence_<field> variable (high/prompt/low).
#
# `gh`-dependent paths degrade gracefully to prompt (interactive) or env var
# (--yes mode). `gh` absence never aborts the bootstrap.
#
# Sources per data-model.md §Entity 5:
#   PROJECT_NAME         jq .name package.json → pyproject.toml name → basename(cwd)
#   PROJECT_DESCRIPTION  jq .description package.json → pyproject.toml description → gh repo view
#   GITHUB_ORG           gh repo view --json nameWithOwner (split on /)
#   GITHUB_REPO          (same)
#   AI_AGENT             literal "Claude Code" default
#   TECH_STACK           single-manifest detection
#   RATIFICATION_DATE    grep Ratified .aod/memory/constitution.md
#   CURRENT_DATE         date +%Y-%m-%d
# -----------------------------------------------------------------------------
auto_discover_8() {
    # All caller-scope canonical vars (PROJECT_NAME, PROJECT_DESCRIPTION,
    # GITHUB_ORG, GITHUB_REPO, AI_AGENT, TECH_STACK, RATIFICATION_DATE,
    # CURRENT_DATE) are read by aod_template_init_personalization via its
    # eval-based caller-scope contract (template-substitute.sh:510-511).
    # shellcheck disable=SC2034
    local root="$AOD_BOOTSTRAP_REPO_ROOT"

    # -------- CURRENT_DATE (always high confidence) --------
    if [ -z "${AOD_BOOTSTRAP_CURRENT_DATE:-}" ]; then
        CURRENT_DATE="$(date +%Y-%m-%d)"
        _aod_bootstrap_set_confidence CURRENT_DATE high
    else
        CURRENT_DATE="$AOD_BOOTSTRAP_CURRENT_DATE"
        _aod_bootstrap_set_confidence CURRENT_DATE high
    fi

    # -------- PROJECT_NAME --------
    if [ -n "${AOD_BOOTSTRAP_PROJECT_NAME:-}" ]; then
        PROJECT_NAME="$AOD_BOOTSTRAP_PROJECT_NAME"
        _aod_bootstrap_set_confidence PROJECT_NAME high
    elif [ -f "$root/package.json" ] && command -v jq >/dev/null 2>&1; then
        local pkg_name
        pkg_name="$(jq -r '.name // ""' "$root/package.json" 2>/dev/null || true)"
        if [ -n "$pkg_name" ] && [ "$pkg_name" != "null" ]; then
            PROJECT_NAME="$pkg_name"
            _aod_bootstrap_set_confidence PROJECT_NAME high
        else
            PROJECT_NAME="$(basename "$root")"
            _aod_bootstrap_set_confidence PROJECT_NAME low
        fi
    elif [ -f "$root/pyproject.toml" ]; then
        local py_name
        py_name="$(grep -m1 -E '^name[[:space:]]*=' "$root/pyproject.toml" 2>/dev/null | sed -E 's/^name[[:space:]]*=[[:space:]]*["'"'"']([^"'"'"']+)["'"'"'].*/\1/' || true)"
        if [ -n "$py_name" ]; then
            PROJECT_NAME="$py_name"
            _aod_bootstrap_set_confidence PROJECT_NAME high
        else
            PROJECT_NAME="$(basename "$root")"
            _aod_bootstrap_set_confidence PROJECT_NAME low
        fi
    else
        PROJECT_NAME="$(basename "$root")"
        _aod_bootstrap_set_confidence PROJECT_NAME low
    fi

    # -------- PROJECT_DESCRIPTION --------
    if [ -n "${AOD_BOOTSTRAP_PROJECT_DESCRIPTION:-}" ]; then
        PROJECT_DESCRIPTION="$AOD_BOOTSTRAP_PROJECT_DESCRIPTION"
        _aod_bootstrap_set_confidence PROJECT_DESCRIPTION high
    else
        PROJECT_DESCRIPTION=""
        if [ -f "$root/package.json" ] && command -v jq >/dev/null 2>&1; then
            PROJECT_DESCRIPTION="$(jq -r '.description // ""' "$root/package.json" 2>/dev/null || true)"
            if [ "$PROJECT_DESCRIPTION" = "null" ]; then
                PROJECT_DESCRIPTION=""
            fi
        fi
        if [ -z "$PROJECT_DESCRIPTION" ] && [ -f "$root/pyproject.toml" ]; then
            PROJECT_DESCRIPTION="$(grep -m1 -E '^description[[:space:]]*=' "$root/pyproject.toml" 2>/dev/null | sed -E 's/^description[[:space:]]*=[[:space:]]*["'"'"']([^"'"'"']+)["'"'"'].*/\1/' || true)"
        fi
        if [ -z "$PROJECT_DESCRIPTION" ] && command -v gh >/dev/null 2>&1; then
            # gh degrades to low when not authenticated; swallow errors.
            PROJECT_DESCRIPTION="$(gh repo view --json description --jq '.description // ""' 2>/dev/null || true)"
        fi
        if [ -n "$PROJECT_DESCRIPTION" ]; then
            _aod_bootstrap_set_confidence PROJECT_DESCRIPTION high
        else
            # Fail-safe placeholder — low confidence.
            PROJECT_DESCRIPTION="(none found)"
            _aod_bootstrap_set_confidence PROJECT_DESCRIPTION low
        fi
    fi

    # -------- GITHUB_ORG + GITHUB_REPO --------
    local gh_nwo=""
    if [ -n "${AOD_BOOTSTRAP_GITHUB_ORG:-}" ]; then
        GITHUB_ORG="$AOD_BOOTSTRAP_GITHUB_ORG"
        _aod_bootstrap_set_confidence GITHUB_ORG high
    fi
    if [ -n "${AOD_BOOTSTRAP_GITHUB_REPO:-}" ]; then
        GITHUB_REPO="$AOD_BOOTSTRAP_GITHUB_REPO"
        _aod_bootstrap_set_confidence GITHUB_REPO high
    fi

    # If either not set by env, try gh.
    if [ -z "${GITHUB_ORG:-}" ] || [ -z "${GITHUB_REPO:-}" ]; then
        if command -v gh >/dev/null 2>&1; then
            gh_nwo="$(cd "$root" 2>/dev/null && gh repo view --json nameWithOwner --jq '.nameWithOwner // ""' 2>/dev/null || true)"
        fi
        if [ -n "$gh_nwo" ] && printf '%s' "$gh_nwo" | grep -q '/'; then
            if [ -z "${GITHUB_ORG:-}" ]; then
                GITHUB_ORG="${gh_nwo%%/*}"
                _aod_bootstrap_set_confidence GITHUB_ORG high
            fi
            if [ -z "${GITHUB_REPO:-}" ]; then
                GITHUB_REPO="${gh_nwo#*/}"
                _aod_bootstrap_set_confidence GITHUB_REPO high
            fi
        else
            # gh absent or no repo — degrade to prompt-or-fail.
            if [ -z "${GITHUB_ORG:-}" ]; then
                GITHUB_ORG="(unknown)"
                _aod_bootstrap_set_confidence GITHUB_ORG prompt
            fi
            if [ -z "${GITHUB_REPO:-}" ]; then
                GITHUB_REPO="$PROJECT_NAME"
                _aod_bootstrap_set_confidence GITHUB_REPO prompt
            fi
        fi
    fi

    # -------- AI_AGENT --------
    if [ -n "${AOD_BOOTSTRAP_AI_AGENT:-}" ]; then
        AI_AGENT="$AOD_BOOTSTRAP_AI_AGENT"
        _aod_bootstrap_set_confidence AI_AGENT high
    else
        # AI_AGENT is read by aod_template_init_personalization via its
        # caller-scope contract (template-substitute.sh:510-511).
        # shellcheck disable=SC2034
        AI_AGENT="Claude Code"
        _aod_bootstrap_set_confidence AI_AGENT prompt
    fi

    # -------- TECH_STACK --------
    if [ -n "${AOD_BOOTSTRAP_TECH_STACK:-}" ]; then
        TECH_STACK="$AOD_BOOTSTRAP_TECH_STACK"
        _aod_bootstrap_set_confidence TECH_STACK high
    else
        local found_stacks=""
        local stack_count=0
        if [ -f "$root/pyproject.toml" ]; then
            found_stacks="Python"
            stack_count=$((stack_count + 1))
        fi
        if [ -f "$root/package.json" ]; then
            found_stacks="Node.js"
            stack_count=$((stack_count + 1))
        fi
        if [ -f "$root/go.mod" ]; then
            found_stacks="Go"
            stack_count=$((stack_count + 1))
        fi
        if [ -f "$root/Cargo.toml" ]; then
            found_stacks="Rust"
            stack_count=$((stack_count + 1))
        fi
        if [ -f "$root/Package.swift" ]; then
            found_stacks="Swift"
            stack_count=$((stack_count + 1))
        fi
        if [ "$stack_count" -eq 1 ]; then
            TECH_STACK="$found_stacks"
            _aod_bootstrap_set_confidence TECH_STACK high
        elif [ "$stack_count" -gt 1 ]; then
            TECH_STACK="(multiple manifests)"
            _aod_bootstrap_set_confidence TECH_STACK prompt
        else
            # TECH_STACK is read by aod_template_init_personalization via its
            # caller-scope contract (template-substitute.sh:510-511).
            # shellcheck disable=SC2034
            TECH_STACK="(unknown)"
            _aod_bootstrap_set_confidence TECH_STACK prompt
        fi
    fi

    # -------- RATIFICATION_DATE --------
    if [ -n "${AOD_BOOTSTRAP_RATIFICATION_DATE:-}" ]; then
        RATIFICATION_DATE="$AOD_BOOTSTRAP_RATIFICATION_DATE"
        _aod_bootstrap_set_confidence RATIFICATION_DATE high
    else
        local const_file="$root/.aod/memory/constitution.md"
        local ratified_line=""
        if [ -f "$const_file" ]; then
            ratified_line="$(grep -m1 -E 'Ratified' "$const_file" 2>/dev/null || true)"
        fi
        # Extract an ISO date (YYYY-MM-DD) from whatever context the line has.
        if [ -n "$ratified_line" ]; then
            RATIFICATION_DATE="$(printf '%s' "$ratified_line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -n1)"
        fi
        if [ -n "${RATIFICATION_DATE:-}" ]; then
            _aod_bootstrap_set_confidence RATIFICATION_DATE high
        else
            RATIFICATION_DATE="$CURRENT_DATE"
            _aod_bootstrap_set_confidence RATIFICATION_DATE low
        fi
    fi

    return 0
}

# -----------------------------------------------------------------------------
# always_prompt_4_or_env — FR-006 + FR-007 always-prompt fields
# -----------------------------------------------------------------------------
# For each of TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH,
# CLOUD_PROVIDER — resolve via:
#   1. AOD_BOOTSTRAP_<FIELD> env var if set
#   2. Interactive prompt (in interactive mode)
#   3. Fail-fast with "--yes mode requires AOD_BOOTSTRAP_<FIELD>" stderr + exit 1
#
# These 4 fields are architecture decisions with no reliable auto-discovery,
# so the prompt is unconditional when no env var is set.
# -----------------------------------------------------------------------------
always_prompt_4_or_env() {
    local field tty_src=""
    if [ -r /dev/tty ]; then
        tty_src="/dev/tty"
    fi

    for field in TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER; do
        local env_var_name="AOD_BOOTSTRAP_${field}"
        local env_value
        # Indirect expansion (bash 3.2 safe via eval+escape).
        eval "env_value=\"\${${env_var_name}:-}\""

        if [ -n "$env_value" ]; then
            eval "${field}=\"\$env_value\""
            _aod_bootstrap_set_confidence "$field" high
            continue
        fi

        if [ "${AOD_BOOTSTRAP_YES:-0}" = "1" ]; then
            printf 'Error: --yes mode requires %s for field %s (no auto-discovery possible)\n' "$env_var_name" "$field" >&2
            exit 1
        fi

        # Interactive prompt.
        local reply=""
        printf 'Enter %s: ' "$field" >&2
        if [ -n "$tty_src" ]; then
            IFS= read -r reply < "$tty_src" || reply=""
        else
            IFS= read -r reply || reply=""
        fi
        if [ -z "$reply" ]; then
            printf 'Error: %s cannot be empty\n' "$field" >&2
            exit 1
        fi
        eval "${field}=\"\$reply\""
        _aod_bootstrap_set_confidence "$field" prompt
    done

    return 0
}

# =============================================================================
# --yes mode gates (FR-007) — T034
# =============================================================================

# -----------------------------------------------------------------------------
# validate_yes_mode — FR-007 + SC-006 fail-closed gate for non-interactive runs
# -----------------------------------------------------------------------------
# Invariant: this function runs AFTER auto_discover_8 and always_prompt_4_or_env
# have populated the caller-scope canonical variables and their parallel
# _confidence_<field> markers; it runs BEFORE any write call (neither
# aod_template_init_personalization nor aod_template_write_version_file has
# been invoked yet). The contract is binary: either every field is write-ready,
# or we exit 1 with a stderr message naming the first unsatisfied field and
# zero files written.
#
# Behavior in --yes mode (AOD_BOOTSTRAP_YES=1):
#   - Iterate AOD_CANONICAL_PLACEHOLDERS in source order (deterministic).
#   - For each field, read its parallel _confidence_<field> marker.
#   - `low` confidence without a corresponding AOD_BOOTSTRAP_<FIELD> env
#     override → emit stderr naming the field and exit 1.
#   - `high` and `prompt` confidence pass (`prompt` in --yes mode means the
#     user provided an env override or the field's default is deterministic —
#     e.g., AI_AGENT=Claude Code, CURRENT_DATE=$(date +%Y-%m-%d)).
#   - Always-prompt fields (TECH_STACK_DATABASE, etc.) are already gated by
#     always_prompt_4_or_env() which itself fails-fast on missing env var in
#     --yes mode; we never see those fields with unset values here.
#
# Behavior in interactive mode (AOD_BOOTSTRAP_YES unset or 0): no-op. Low
# confidence is signalled in the summary table (confirm_summary) where the
# user may edit via re-prompt.
#
# Per spec FR-007: "No global 'accept-all' escape hatch is permitted". The
# operator MUST name each unsatisfied field explicitly via its env var.
#
# Zero-file-written guarantee: this function returns only via `exit 1`
# (failure) or `return 0` (success). The main orchestrator invokes it BEFORE
# either aod_template_init_personalization or aod_template_write_version_file.
# The staging dir is cleaned by the trap EXIT registered in aod_bootstrap_main.
# -----------------------------------------------------------------------------
validate_yes_mode() {
    # No-op in interactive mode.
    if [ "${AOD_BOOTSTRAP_YES:-0}" != "1" ]; then
        return 0
    fi

    local field conf env_var_name env_value
    for field in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        eval "conf=\"\${_confidence_${field}:-unknown}\""

        case "$conf" in
            low)
                # Low-confidence auto-discovery. Gate on the per-field env
                # override. If set (even to empty string by operator), the
                # env override would have been picked up in auto_discover_8
                # and confidence upgraded to `high` — so by the time we see
                # `low` here, the override is definitively absent.
                env_var_name="AOD_BOOTSTRAP_${field}"
                eval "env_value=\"\${${env_var_name}:-}\""
                if [ -z "$env_value" ]; then
                    printf 'Error: --yes mode requires %s for field %s (auto-discovery returned low confidence)\n' \
                        "$env_var_name" "$field" >&2
                    exit 1
                fi
                ;;
            unknown)
                # A field lacks a confidence marker entirely — indicates an
                # incomplete auto_discover_8 / always_prompt_4_or_env pass.
                # This is an internal invariant violation; surface it
                # loudly rather than silently accepting the unknown state.
                printf 'Error: --yes mode internal invariant violation: no confidence marker set for field %s\n' \
                    "$field" >&2
                exit 1
                ;;
            high|prompt)
                # high: env override or deterministic auto-discovery succeeded.
                # prompt: deterministic default (AI_AGENT) OR env override
                #         picked up by always_prompt_4_or_env.
                # Both are acceptable for --yes mode.
                :
                ;;
            *)
                # Future-proof: unrecognized confidence marker — fail closed.
                printf 'Error: --yes mode unrecognized confidence marker %q for field %s\n' \
                    "$conf" "$field" >&2
                exit 1
                ;;
        esac
    done

    return 0
}

# =============================================================================
# Confirmation UX (FR-007)
# =============================================================================

# -----------------------------------------------------------------------------
# confirm_summary — FR-007
# -----------------------------------------------------------------------------
# Emit summary table matching cli-contract.md §Stdout format and prompt
# [y/N]. In --yes mode this function is a no-op (caller already gated).
#
# Uses aod_update_confirm-style tty-preference logic inline here (we can't
# source scripts/update.sh because that would trigger its own dispatcher).
# The behavior matches the existing precedent at scripts/update.sh:1516-1540.
#
# Returns 0 on confirm, 1 on decline (caller exits 0 on decline per
# @US-1-AC-2 and cli-contract.md Exit Code 0 "confirmed").
# -----------------------------------------------------------------------------
confirm_summary() {
    if [ "${AOD_BOOTSTRAP_YES:-0}" = "1" ]; then
        # --yes mode: skip prompt entirely.
        printf -- '--yes mode: skipping confirmation (all 12 fields resolved from auto-discovery + env vars)\n'
        return 0
    fi

    # Render summary table (stdout — adopters may paste into support threads).
    printf '\n'
    printf '+------------------------------+-----------------+------------+\n'
    printf '| %-28s | %-15s | %-10s |\n' "Field" "Value" "Confidence"
    printf '+------------------------------+-----------------+------------+\n'
    local field val conf
    for field in "${AOD_CANONICAL_PLACEHOLDERS[@]}"; do
        eval "val=\"\${${field}:-}\""
        eval "conf=\"\${_confidence_${field}:-unknown}\""
        printf '| %-28s | %-15s | %-10s |\n' "$field" "$val" "$conf"
    done
    printf '+------------------------------+-----------------+------------+\n'
    printf '\n'

    # Prompt — tty-preferred so prompt works when stdin was consumed.
    local tty_src="" reply=""
    if [ -r /dev/tty ]; then
        tty_src="/dev/tty"
    fi
    printf 'Confirm and write? [y/N]: '
    if [ -n "$tty_src" ]; then
        IFS= read -r reply < "$tty_src" || reply=""
    else
        IFS= read -r reply || reply=""
    fi
    case "$reply" in
        y|Y) return 0 ;;
        *)   return 1 ;;
    esac
}

# =============================================================================
# Main (FR-004, FR-005, FR-008, FR-017) — T014 / T015 / T030
# =============================================================================

# -----------------------------------------------------------------------------
# _aod_bootstrap_parse_flags "$@"
# -----------------------------------------------------------------------------
# Parse --yes and --upstream-url=<url> from caller-forwarded args.
# Unknown flags pass silently (dispatcher in scripts/update.sh already rejected
# mutex violations).
# -----------------------------------------------------------------------------
_aod_bootstrap_parse_flags() {
    AOD_BOOTSTRAP_YES="${AOD_BOOTSTRAP_YES:-0}"
    AOD_BOOTSTRAP_URL_OVERRIDE="${AOD_BOOTSTRAP_URL_OVERRIDE:-}"
    while [ $# -gt 0 ]; do
        case "$1" in
            --yes|-y)
                AOD_BOOTSTRAP_YES=1
                shift
                ;;
            --upstream-url=*)
                AOD_BOOTSTRAP_URL_OVERRIDE="${1#--upstream-url=}"
                shift
                ;;
            --upstream-url)
                printf '[aod] ERROR: --upstream-url requires a value (use --upstream-url=<url>)\n' >&2
                exit 1
                ;;
            --bootstrap)
                # Subcommand marker — already consumed by dispatcher but may
                # be forwarded; ignore.
                shift
                ;;
            --)
                shift
                break
                ;;
            *)
                # Ignore unrecognized flags (dispatcher vets them for mutex
                # violations); mismatch here indicates future forward-compat
                # growth.
                shift
                ;;
        esac
    done
}

# -----------------------------------------------------------------------------
# aod_bootstrap_main "$@" — T014 (CRITICAL)
# -----------------------------------------------------------------------------
# Per FR-004 + FR-005 + FR-008 + FR-017, orchestrates the full bootstrap
# flow. Ordering is architecturally load-bearing per architect A-1:
#   1. Guards FIRST (overwrite + PLSK) — before any network or staging
#   2. Resolve upstream URL
#   3. Create staging dir + register trap EXIT
#   4. Invoke aod_template_fetch_upstream with F132 `set +e` bracket
#   5. Compute version-file fields (sha, version, updated_at, manifest_sha256)
#   6. Auto-discover 8 canonical values
#   7. Always-prompt 4 (or env var)
#   8. Confirm (or skip in --yes mode)
#   9. Write personalization.env FIRST (aod_template_init_personalization)
#  10. Write aod-kit-version LAST (aod_template_write_version_file) — this
#      is the atomic transaction commit per data-model.md §Cross-Entity
#      Relationships.
# -----------------------------------------------------------------------------
aod_bootstrap_main() {
    # Parse --yes / --upstream-url from forwarded args.
    _aod_bootstrap_parse_flags "$@"

    # Resolve repo root (caller-independent — anchor to the library location).
    AOD_BOOTSTRAP_REPO_ROOT="${AOD_BOOTSTRAP_REPO_ROOT:-$_aod_bootstrap_repo_root}"

    # ---- Step 1: GUARDS FIRST (T028, T029 wired via T030) ----
    guard_check_overwrite
    guard_check_plsk_fingerprint

    # ---- Step 2: Resolve upstream URL (FR-003) ----
    local upstream_url
    upstream_url="$(resolve_upstream_url)"
    printf 'Resolving upstream URL... %s\n' "$upstream_url"

    # ---- Step 3: Staging dir + trap EXIT (FR-017) ----
    # The staging dir lives under the adopter's repo to preserve
    # same-filesystem semantics for the F129 helper's atomic mv. The trap is
    # registered AFTER the dir is known so an earlier failure cannot trigger
    # a spurious rm -rf "".
    local staging_dir
    staging_dir="$AOD_BOOTSTRAP_REPO_ROOT/.aod/aod-kit-staging-$$"

    # Ensure parent exists (.aod/ is the adopter's directory).
    if [ ! -d "$AOD_BOOTSTRAP_REPO_ROOT/.aod" ]; then
        mkdir -p "$AOD_BOOTSTRAP_REPO_ROOT/.aod" 2>/dev/null || {
            printf '[aod] ERROR: could not create .aod/ directory under %s\n' "$AOD_BOOTSTRAP_REPO_ROOT" >&2
            exit 1
        }
    fi

    # Clean any stale staging-dir from a previous crash (same-pid race is
    # impossible; same-pid re-invocation means the previous process is the
    # same shell). If dir exists, rm it — fetch_upstream refuses non-empty
    # destinations.
    rm -rf "$staging_dir" 2>/dev/null || true

    # Register cleanup trap. Double-quoted trap string with $staging_dir
    # expansion at trap-installation time — the staging path is known and
    # stable; early expansion is intentional here (same pattern F129 uses
    # for its staging dir trap at scripts/update.sh:1627).
    # shellcheck disable=SC2064
    trap "rm -rf '$staging_dir' 2>/dev/null || true" EXIT INT TERM

    # ---- Step 4: Fetch upstream via F129 helper (FR-005, FR-017 pattern) ----
    printf 'Fetching upstream (shallow clone)... '
    local ref="${AOD_UPSTREAM_REF:-}"
    # F132 rc-capture bracket — MANDATORY per FR-017. Precedent:
    # scripts/check-manifest-coverage.sh:115-118.
    set +e
    aod_template_fetch_upstream "$upstream_url" "$ref" "$staging_dir"
    local fetch_rc=$?
    set -e
    if [ "$fetch_rc" -ne 0 ]; then
        # aod_template_fetch_upstream returns 9 on network failure; propagate
        # per FR-014. Any other non-zero rc is also fatal; surface the rc.
        printf 'failed (rc=%d)\n' "$fetch_rc" >&2
        if [ "$fetch_rc" -eq 9 ]; then
            exit 9
        fi
        # Non-9 helper failure — surface distinct exit (reuse 1 per
        # cli-contract.md; helper stderr already printed).
        exit 1
    fi
    printf 'done\n'

    # ---- Step 5: Compute version-file fields ----
    printf 'Computing manifest SHA-256... '
    local sha version updated_at manifest_sha256 manifest_file

    # sha: HEAD of the fetched clone.
    set +e
    sha="$(cd "$staging_dir" && git rev-parse HEAD 2>/dev/null)"
    local sha_rc=$?
    set -e
    if [ "$sha_rc" -ne 0 ] || [ -z "$sha" ]; then
        printf 'failed: could not compute sha from staging clone\n' >&2
        exit 1
    fi

    # version: most recent tag, else fall back to the 40-char SHA.
    # `|| true` guards against `git describe` exiting non-zero when no tags.
    set +e
    version="$(cd "$staging_dir" && git describe --tags --abbrev=0 --always 2>/dev/null)"
    local ver_rc=$?
    set -e
    if [ "$ver_rc" -ne 0 ] || [ -z "$version" ]; then
        version="$sha"
    fi

    # updated_at: ISO 8601 UTC per the F129 writer's validation.
    updated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # manifest_sha256: computed LOCALLY from the cloned file (FR-005).
    manifest_file="$staging_dir/.aod/template-manifest.txt"
    if [ ! -f "$manifest_file" ]; then
        printf 'failed: manifest not found in staging clone at %s\n' "$manifest_file" >&2
        exit 1
    fi
    # shasum -a 256 is available on macOS (BSD) and Linux (GNU coreutils).
    set +e
    manifest_sha256="$(shasum -a 256 "$manifest_file" 2>/dev/null | awk '{print $1}')"
    local sha_sum_rc=$?
    set -e
    if [ "$sha_sum_rc" -ne 0 ] || [ -z "$manifest_sha256" ]; then
        printf 'failed: shasum -a 256 failed on manifest file\n' >&2
        exit 1
    fi
    printf 'done\n'

    # ---- Step 6: Auto-discover 8 + always-prompt 4 ----
    printf 'Auto-discovering 8 canonical values... '
    auto_discover_8
    printf 'done\n'

    always_prompt_4_or_env

    # ---- Step 6.5: --yes mode fail-closed gate (T034) ----
    # MUST run after auto_discover_8 + always_prompt_4_or_env (confidence
    # markers populated) and BEFORE any write call. Any low-confidence
    # auto-discovered field without an AOD_BOOTSTRAP_<FIELD> env override
    # causes exit 1 with zero files written. No-op in interactive mode.
    validate_yes_mode

    # ---- Step 7: Confirm summary (or skip in --yes mode) ----
    if ! confirm_summary; then
        # Decline path — @US-1-AC-2. Clean exit with status 0 (user
        # interaction is the answer; no error occurred). Staging dir cleaned
        # via trap EXIT.
        printf 'Bootstrap cancelled by user.\n' >&2
        exit 0
    fi

    # ---- Step 8: Write personalization.env FIRST (FR-008) ----
    # Per data-model.md §Cross-Entity Relationships: personalization write
    # happens BEFORE the version-file commit. The version-file is the atomic
    # transaction sentinel — its presence IS the "bootstrapped" signal. If
    # personalization write fails, the user retries and both files are
    # re-written; if version-file write fails, the user retries and
    # personalization is (idempotently) overwritten with the same values.
    printf 'Writing .aod/personalization.env... '
    local personalization_dest="$AOD_BOOTSTRAP_REPO_ROOT/.aod/personalization.env"
    set +e
    aod_template_init_personalization "$personalization_dest"
    local init_rc=$?
    set -e
    if [ "$init_rc" -ne 0 ]; then
        printf 'failed (rc=%d)\n' "$init_rc" >&2
        # Helper already emitted a stderr diagnostic.
        exit 1
    fi
    printf 'done\n'

    # ---- Step 9: Write aod-kit-version LAST (atomic transaction commit) ----
    printf 'Writing .aod/aod-kit-version... '
    local version_dest="$AOD_BOOTSTRAP_REPO_ROOT/.aod/aod-kit-version"
    set +e
    aod_template_write_version_file \
        "$version_dest" \
        "$version" \
        "$sha" \
        "$updated_at" \
        "$upstream_url" \
        "$manifest_sha256"
    local write_rc=$?
    set -e
    if [ "$write_rc" -ne 0 ]; then
        printf 'failed (rc=%d)\n' "$write_rc" >&2
        exit 1
    fi
    printf 'done\n'

    # ---- Success footer ----
    printf '\n'
    if [ "${AOD_BOOTSTRAP_YES:-0}" = "1" ]; then
        printf 'Bootstrap complete.\n'
    else
        printf 'Bootstrap complete. Next: make update --check-placeholders && make update --dry-run\n'
    fi

    return 0
}
