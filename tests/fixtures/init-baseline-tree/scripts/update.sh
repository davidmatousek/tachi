#!/usr/bin/env bash
# =============================================================================
# scripts/update.sh — Adopter-facing CLI for upstream → downstream template updates
# =============================================================================
# Part of feature 129 (downstream template update mechanism).
#
# This is the entry point invoked by `make update` and the `/aod.update` slash
# command. It orchestrates the full update pipeline:
#
#   preflight → fetch → plan → validate → stage → preview → apply → cleanup
#
# Direction of data flow: upstream template → downstream adopter project.
#
# Bash 3.2 compatible (macOS default `/bin/bash`).
#
# See:
#   - specs/129-downstream-template-update/contracts/cli-contract.md
#   - specs/129-downstream-template-update/contracts/manifest-schema.md
#   - specs/129-downstream-template-update/contracts/version-schema.md
#   - specs/129-downstream-template-update/data-model.md §Entity 5 (lock)
#   - specs/129-downstream-template-update/plan.md §C2 (pipeline)
#
# Exit codes (authoritative — see cli-contract.md):
#   0  success (or dry-run completed)
#   1  generic failure
#   2  lock contention
#   3  missing prerequisites
#   4  cross-filesystem staging
#   5  manifest coverage violation
#   6  guard-list violation
#   7  retag detected without --force-retag
#   8  residual placeholder after substitution
#   9  network failure
#  10  user declined preview
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Library sourcing
# -----------------------------------------------------------------------------
# Resolve our own directory so we can source the template-*.sh libraries
# from `.aod/scripts/bash/` relative to the repo root.
AOD_UPDATE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AOD_UPDATE_REPO_ROOT="$(dirname "$AOD_UPDATE_SCRIPT_DIR")"
AOD_UPDATE_LIB_DIR="$AOD_UPDATE_REPO_ROOT/.aod/scripts/bash"

# shellcheck source=/dev/null
. "$AOD_UPDATE_LIB_DIR/template-json.sh"
# shellcheck source=/dev/null
. "$AOD_UPDATE_LIB_DIR/template-validate.sh"
# shellcheck source=/dev/null
. "$AOD_UPDATE_LIB_DIR/template-manifest.sh"
# shellcheck source=/dev/null
. "$AOD_UPDATE_LIB_DIR/template-git.sh"
# shellcheck source=/dev/null
. "$AOD_UPDATE_LIB_DIR/template-substitute.sh"

# -----------------------------------------------------------------------------
# USER_OWNED_GUARD — Hardcoded user-owned guard list (FR-007 / plan §C4)
# -----------------------------------------------------------------------------
# Patterns here are EXACT-PATH MATCHES anchored to the repo root. The glob
# vocabulary matches `aod_template_glob_match` from template-manifest.sh:
#   `**` matches any sequence of characters including `/`
#   `*`  matches any chars within a single segment (no `/`)
#
# Anchored-path semantics examples:
#   - `roadmap.md` matches ONLY `./roadmap.md` at the repo root.
#   - It does NOT match `docs/product/roadmap.md` (that would need
#     `docs/product/roadmap.md` or `**/roadmap.md` explicitly).
#   - `docs/product/**` matches `docs/product/a.md`, `docs/product/nested/b.md`,
#     but NOT `docs/product` (the dir itself — we only protect entries).
#
# Why this array lives in scripts/update.sh (not in a shared library):
#   - Tamper-resistance. A malicious or buggy manifest/library change cannot
#     remove protections by editing one shared location. The executable
#     entry point carries its own floor.
#   - The guard list is fixed behavior of the /aod.update CLI; it is not
#     data callers should be able to substitute.
#
# Precedence (see contracts/manifest-schema.md):
#   ignore > guard > user > scaffold > merge > personalized > owned
# Guard overrides every manifest write category — even if a manifest entry
# says `owned|docs/product/foo.md`, this array blocks the write.
#
# To add or remove patterns, update:
#   1. This array.
#   2. tests/unit/guard-list.bats.
#   3. specs/129-downstream-template-update/plan.md §C4.
# -----------------------------------------------------------------------------
readonly USER_OWNED_GUARD=(
  'docs/product/**'
  'docs/architecture/**'
  'brands/**'
  '.aod/memory/**'
  'specs/**'
  'roadmap.md'
  'okrs.md'
  'CHANGELOG.md'
)

# -----------------------------------------------------------------------------
# aod_template_update_validate_guards
# -----------------------------------------------------------------------------
# Iterate a list of (path, operation) tuples and assert each path passes
# `aod_template_assert_guard` against USER_OWNED_GUARD. Exit code 6 with a
# list of offenders if any match.
#
# Input: newline-delimited `<path>|<operation>` tuples on stdin. Lines where
# `<operation>` is `skip` or `ignore` are not checked (no write planned).
#
# Exit codes:
#   0 — no violations
#   6 — one or more guard violations (details printed to stderr)
# -----------------------------------------------------------------------------
aod_template_update_validate_guards() {
    local violations=0
    local line path op

    while IFS= read -r line || [ -n "$line" ]; do
        if [ -z "$line" ]; then
            continue
        fi
        case "$line" in
            *'|'*) : ;;
            *)
                echo "[aod] ERROR: validate_guards: malformed tuple '$line' (expected <path>|<op>)" >&2
                violations=$((violations + 1))
                continue
                ;;
        esac
        path="${line%%|*}"
        op="${line#*|}"
        case "$op" in
            skip|ignore)
                # Non-writing operations — guard doesn't apply.
                continue
                ;;
        esac
        if ! aod_template_assert_guard "$path" USER_OWNED_GUARD; then
            violations=$((violations + 1))
        fi
    done

    if [ "$violations" -gt 0 ]; then
        echo "[aod] ERROR: validate_guards: $violations guard violation(s) detected; refusing to apply update" >&2
        exit 6
    fi
    return 0
}

# -----------------------------------------------------------------------------
# aod_template_update_validate_no_symlinks
# -----------------------------------------------------------------------------
# Iterate a list of file paths (one per line on stdin) and assert each is not
# a symlink via `aod_template_assert_no_symlink`. Exit code 1 with a list of
# offenders if any are symlinks (per cli-contract.md step 16).
#
# Exit codes:
#   0 — no symlinks
#   1 — one or more symlinks detected
# -----------------------------------------------------------------------------
aod_template_update_validate_no_symlinks() {
    local violations=0
    local file

    while IFS= read -r file || [ -n "$file" ]; do
        if [ -z "$file" ]; then
            continue
        fi
        if ! aod_template_assert_no_symlink "$file"; then
            violations=$((violations + 1))
        fi
    done

    if [ "$violations" -gt 0 ]; then
        echo "[aod] ERROR: validate_no_symlinks: $violations symlink(s) detected; refusing to apply update" >&2
        exit 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# aod_template_update_stage_substitute
# -----------------------------------------------------------------------------
# Iterate a list of already-staged personalized files (one absolute path per
# line on stdin) and run, for each file, the substitution + residual-scan
# pair from template-substitute.sh.
#
# Exit codes:
#   0  — all files substituted + clean
#   1  — IO or argument failure
#   3  — personalization.env missing
#   8  — load validation failure OR residual placeholder detected
# -----------------------------------------------------------------------------
aod_template_update_stage_substitute() {
    local env_path="${AOD_PERSONALIZATION_ENV_PATH:-.aod/personalization.env}"

    if [ -z "${AOD_PERSONALIZATION_PROJECT_NAME:-}" ]; then
        if ! aod_template_load_personalization_env "$env_path"; then
            local rc=$?
            echo "[aod] ERROR: stage_substitute: failed to load personalization env ($env_path) — rc=$rc" >&2
            return "$rc"
        fi
    fi

    local file rc
    while IFS= read -r file || [ -n "$file" ]; do
        if [ -z "$file" ]; then
            continue
        fi
        if [ ! -f "$file" ]; then
            echo "[aod] ERROR: stage_substitute: staged file missing or not regular: $file" >&2
            return 1
        fi

        aod_template_substitute_placeholders "$file" "$file"
        rc=$?
        if [ "$rc" -ne 0 ]; then
            echo "[aod] ERROR: stage_substitute: substitution failed for $file (rc=$rc)" >&2
            return "$rc"
        fi

        aod_template_assert_no_residual "$file"
        rc=$?
        if [ "$rc" -ne 0 ]; then
            return "$rc"
        fi
    done

    return 0
}

# =============================================================================
# Pipeline state (populated by each phase)
# =============================================================================

# Flags (populated by argparse)
UPDATE_DRY_RUN=0
UPDATE_YES=0
UPDATE_JSON=0
UPDATE_EDGE=0
UPDATE_FORCE_RETAG=0
UPDATE_UPSTREAM_URL_OVERRIDE=""
UPDATE_APPLY_EXPLICIT=0
UPDATE_MODE=""            # "dry-run" | "apply" after precedence resolution

# Preflight state
UPDATE_ADOPTER_ROOT=""    # absolute path to adopter project root
UPDATE_STAGING_ROOT=""    # parent dir for staging UUID subdirs (typically .aod/update-tmp)
UPDATE_UUID=""            # 16-char hex nonce for this run's staging subdir
UPDATE_RUN_DIR=""         # $UPDATE_STAGING_ROOT/$UPDATE_UUID
UPDATE_STAGED_DIR=""      # $UPDATE_RUN_DIR/staged
UPDATE_UPSTREAM_DIR=""    # $UPDATE_RUN_DIR/upstream
UPDATE_LOCK_PATH=""       # .aod/update.lock
UPDATE_LOCK_NONCE=""      # 16-char hex — this run's lock nonce
UPDATE_LOCK_ACQUIRED=0    # 1 once our process owns the lock

# Fetch/plan state
UPDATE_NEW_SHA=""
UPDATE_NEW_TAG=""
UPDATE_NEW_MANIFEST_SHA=""
UPDATE_MANIFEST_DRIFT=0
# Each entry is TAB-delimited: path<TAB>category<TAB>winning_entry<TAB>change_type<TAB>action
# TAB is used (not `|`) because `winning_entry` itself contains `|` internally
# (format: `<category>|<glob-pattern>`). Using TAB keeps the 5-field shape
# unambiguous under bash 3.2 `${var%%...}` / `${var#...}` parsing.
UPDATE_OPERATIONS=()
UPDATE_START_TS=""
# Field separator used in UPDATE_OPERATIONS entries. Kept as a variable so the
# parser helpers can reference it consistently.
UPDATE_OP_SEP=$'\t'

# =============================================================================
# Helpers
# =============================================================================

# Parse one UPDATE_OPERATIONS tuple into positional outputs. Callers use
# `IFS=$'\t' read -r path cat winning change action <<< "$op"` inline; this
# helper is here for documentation purposes only.
#
# Tuple format: path<TAB>category<TAB>winning_entry<TAB>change_type<TAB>action
#
# winning_entry itself may contain `|` (format is `<cat>|<pattern>`).

# Portable sha256. BSD has `shasum -a 256`, GNU has `sha256sum`. Both emit
# `<hex>  <file>` — extract the hex prefix.
_aod_update_sha256() {
    local path="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$path" | awk '{print $1}'
    else
        shasum -a 256 "$path" | awk '{print $1}'
    fi
}

# Portable 16-char hex nonce from /dev/urandom.
_aod_update_random_hex() {
    od -An -N8 -tx1 /dev/urandom 2>/dev/null | tr -d ' \n'
}

# ISO 8601 UTC timestamp.
_aod_update_iso_utc() {
    date -u +%Y-%m-%dT%H:%M:%SZ
}

# -----------------------------------------------------------------------------
# aod_update_print_usage
# -----------------------------------------------------------------------------
aod_update_print_usage() {
    cat <<'EOF'
Usage: scripts/update.sh [flags]

Apply upstream template updates to this adopter project.
Direction: upstream → downstream.

Flags:
  --dry-run, -n          Fetch + preview only. No writes outside staging dir.
                         Wins over --apply.
  --yes, -y              Skip the confirmation prompt (still applies).
  --json                 Emit structured JSON (schema_version 1.0). No colors.
  --edge                 Fetch upstream main HEAD instead of latest tag.
  --force-retag          Proceed even if the upstream tag SHA changed (supply-
                         chain tripwire override; logs a warning).
  --upstream-url=<url>   Override the recorded upstream URL. Must be https://
                         unless --force-retag is also passed.
  --apply                Explicit apply flag. Default in interactive TTY when
                         CI is unset. Dry-run wins if both are passed.
  --help, -h             Print this help and exit.

Exit codes:
   0  success (or dry-run completed)
   1  generic failure
   2  lock contention (another /aod.update is running)
   3  missing prerequisites (.aod/aod-kit-version absent or malformed)
   4  cross-filesystem staging (atomicity violation pre-flight)
   5  manifest coverage violation (upstream has uncategorized files)
   6  guard-list violation (manifest tried to write user-owned path)
   7  retag detected without --force-retag
   8  residual placeholder after substitution
   9  network failure during upstream fetch
  10  user declined preview

Examples:
  scripts/update.sh --dry-run     # preview, do not write
  scripts/update.sh --yes         # apply without confirmation prompt
  make update ARGS=--dry-run      # same, via Make target
  /aod.update --dry-run           # same, via slash command

See docs/guides/DOWNSTREAM_UPDATE.md for the full adopter walkthrough.
EOF
}

# -----------------------------------------------------------------------------
# aod_update_parse_flags "$@"
# -----------------------------------------------------------------------------
# Parse CLI flags into UPDATE_* variables. Invalid flags exit 1 with usage.
# -----------------------------------------------------------------------------
aod_update_parse_flags() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --dry-run|-n)
                UPDATE_DRY_RUN=1
                shift
                ;;
            --yes|-y)
                UPDATE_YES=1
                shift
                ;;
            --json)
                UPDATE_JSON=1
                shift
                ;;
            --edge)
                UPDATE_EDGE=1
                shift
                ;;
            --force-retag)
                UPDATE_FORCE_RETAG=1
                shift
                ;;
            --apply)
                UPDATE_APPLY_EXPLICIT=1
                shift
                ;;
            --upstream-url=*)
                UPDATE_UPSTREAM_URL_OVERRIDE="${1#--upstream-url=}"
                shift
                ;;
            --upstream-url)
                echo "[aod] ERROR: --upstream-url requires a value (use --upstream-url=<url>)" >&2
                aod_update_print_usage >&2
                exit 1
                ;;
            --help|-h)
                aod_update_print_usage
                exit 0
                ;;
            --)
                shift
                break
                ;;
            -*)
                echo "[aod] ERROR: unknown flag: $1" >&2
                aod_update_print_usage >&2
                exit 1
                ;;
            *)
                echo "[aod] ERROR: unexpected positional argument: $1" >&2
                aod_update_print_usage >&2
                exit 1
                ;;
        esac
    done

    # Resolve UPDATE_MODE per cli-contract.md §Flag precedence:
    #   1. --dry-run always wins over --apply.
    #   2. --yes is orthogonal.
    #   3. CI env set + neither --apply nor --dry-run → dry-run.
    #   4. stdin not a TTY + neither --yes nor --dry-run → dry-run (fail-safe).
    if [ "$UPDATE_DRY_RUN" = "1" ]; then
        UPDATE_MODE="dry-run"
    elif [ "$UPDATE_APPLY_EXPLICIT" = "1" ]; then
        UPDATE_MODE="apply"
    elif [ -n "${CI:-}" ]; then
        UPDATE_MODE="dry-run"
    elif [ ! -t 0 ] && [ "$UPDATE_YES" != "1" ]; then
        UPDATE_MODE="dry-run"
    else
        UPDATE_MODE="apply"
    fi
}

# =============================================================================
# Preflight phase
# =============================================================================

# -----------------------------------------------------------------------------
# aod_update_preflight
# -----------------------------------------------------------------------------
# Per cli-contract.md steps 3-5:
#   3. Verify `.aod/aod-kit-version` exists and parses cleanly.
#   4. Verify same-FS staging via device number comparison.
#   5. Create UUID staging subdir.
# -----------------------------------------------------------------------------
aod_update_preflight() {
    UPDATE_ADOPTER_ROOT="$(pwd)"

    # Step 3: read + validate version file.
    local version_file="$UPDATE_ADOPTER_ROOT/.aod/aod-kit-version"
    if [ ! -f "$version_file" ]; then
        echo "[aod] ERROR: .aod/aod-kit-version not found — adopter project not bootstrapped." >&2
        echo "[aod] Run scripts/init.sh to bootstrap, or see docs/guides/DOWNSTREAM_UPDATE.md." >&2
        exit 3
    fi

    # aod_template_read_version_file exits 3 on malformed; propagate.
    if ! aod_template_read_version_file "$version_file"; then
        # function already emitted diagnostic
        exit 3
    fi

    # Step 4: same-filesystem check for staging.
    # Respect AOD_UPDATE_TMP_DIR env override (tests + advanced users).
    local staging_root="${AOD_UPDATE_TMP_DIR:-$UPDATE_ADOPTER_ROOT/.aod/update-tmp}"
    if [ ! -d "$staging_root" ]; then
        if ! mkdir -p "$staging_root" 2>/dev/null; then
            echo "[aod] ERROR: could not create staging dir: $staging_root" >&2
            exit 1
        fi
    fi

    local root_dev staging_dev
    root_dev="$(aod_template_fs_device "$UPDATE_ADOPTER_ROOT" 2>/dev/null || echo '')"
    staging_dev="$(aod_template_fs_device "$staging_root" 2>/dev/null || echo '')"
    if [ -z "$root_dev" ] || [ -z "$staging_dev" ]; then
        echo "[aod] ERROR: could not determine filesystem device for preflight same-fs check" >&2
        echo "[aod] (project root: $UPDATE_ADOPTER_ROOT; staging: $staging_root)" >&2
        exit 4
    fi
    if [ "$root_dev" != "$staging_dev" ]; then
        echo "[aod] ERROR: cross-filesystem staging is not atomic — refusing to run." >&2
        echo "[aod] project root device: $root_dev" >&2
        echo "[aod] staging dir device:  $staging_dev (path: $staging_root)" >&2
        echo "[aod] Set AOD_UPDATE_TMP_DIR to a path on the same filesystem as the project root," >&2
        echo "[aod] or unset it to use the default .aod/update-tmp/." >&2
        exit 4
    fi

    UPDATE_STAGING_ROOT="$staging_root"

    # Step 5: create per-run UUID subdir.
    UPDATE_UUID="$(_aod_update_random_hex)"
    if [ -z "$UPDATE_UUID" ]; then
        echo "[aod] ERROR: failed to generate UUID from /dev/urandom" >&2
        exit 1
    fi
    UPDATE_RUN_DIR="$UPDATE_STAGING_ROOT/$UPDATE_UUID"
    UPDATE_STAGED_DIR="$UPDATE_RUN_DIR/staged"
    UPDATE_UPSTREAM_DIR="$UPDATE_RUN_DIR/upstream"
    if ! mkdir -p "$UPDATE_STAGED_DIR" 2>/dev/null; then
        echo "[aod] ERROR: could not create run dir: $UPDATE_RUN_DIR" >&2
        exit 1
    fi

    # Export for downstream helpers (tests / subcommands).
    export AOD_STAGING_DIR="$UPDATE_STAGED_DIR"

    UPDATE_START_TS="$(_aod_update_iso_utc)"
}

# =============================================================================
# Lock phase (data-model.md §Entity 5)
# =============================================================================

# -----------------------------------------------------------------------------
# aod_update_acquire_lock
# -----------------------------------------------------------------------------
# Acquire `.aod/update.lock`. Uses flock fast-path where available; otherwise
# PID+nonce+timestamp atomic-create via `set -o noclobber` (macOS primary path).
#
# On contention: examine holder. If alive AND timestamp < 1h → exit 2. If dead
# OR stale (>1h) → force-acquire with nonce re-verify; retry up to 3x.
#
# Sets UPDATE_LOCK_ACQUIRED=1 on success. Registers EXIT trap for release.
# Exit 2 on contention.
# -----------------------------------------------------------------------------
aod_update_acquire_lock() {
    UPDATE_LOCK_PATH="$UPDATE_ADOPTER_ROOT/.aod/update.lock"
    UPDATE_LOCK_NONCE="$(_aod_update_random_hex)"
    local pid=$$
    local ts
    ts="$(date -u +%s)"
    local iso_ts
    iso_ts="$(_aod_update_iso_utc)"
    local cmdline="scripts/update.sh"

    # Ensure parent dir exists.
    if ! mkdir -p "$(dirname "$UPDATE_LOCK_PATH")" 2>/dev/null; then
        echo "[aod] ERROR: could not create lock parent dir" >&2
        exit 1
    fi

    local attempt=0
    local max_attempts=3
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))

        # Try atomic create via noclobber (`set -o noclobber` + `>`). O_EXCL
        # under the hood — fails if target exists.
        if (
            set -o noclobber
            printf 'pid=%s\nnonce=%s\nstarted_at=%s\ncmdline=%s\n' \
                "$pid" "$UPDATE_LOCK_NONCE" "$iso_ts" "$cmdline" \
                > "$UPDATE_LOCK_PATH"
        ) 2>/dev/null; then
            UPDATE_LOCK_ACQUIRED=1
            return 0
        fi

        # Lock exists — inspect holder.
        if [ ! -f "$UPDATE_LOCK_PATH" ]; then
            # Racing with another creator that removed it between the create
            # failure and our read. Retry.
            continue
        fi

        local holder_pid="" holder_nonce="" holder_started=""
        # Parse the lock file safely (no sourcing — we don't trust contents).
        holder_pid="$(grep -m1 '^pid=' "$UPDATE_LOCK_PATH" 2>/dev/null | cut -d= -f2)"
        holder_nonce="$(grep -m1 '^nonce=' "$UPDATE_LOCK_PATH" 2>/dev/null | cut -d= -f2)"
        holder_started="$(grep -m1 '^started_at=' "$UPDATE_LOCK_PATH" 2>/dev/null | cut -d= -f2)"

        # Liveness probe (bash 3.2: `kill -0` + `2>/dev/null`).
        local alive=0
        if [ -n "$holder_pid" ]; then
            case "$holder_pid" in
                ''|*[!0-9]*)
                    alive=0
                    ;;
                *)
                    if kill -0 "$holder_pid" 2>/dev/null; then
                        alive=1
                    fi
                    ;;
            esac
        fi

        # Staleness — compute age in seconds from ISO timestamp. We parse the
        # ISO by stripping non-numeric and converting via `date -j` (BSD) or
        # `date -d` (GNU). Fallback: treat as fresh if parse fails.
        local holder_epoch=0
        if [ -n "$holder_started" ]; then
            # BSD: date -u -j -f '%Y-%m-%dT%H:%M:%SZ' "$ts" +%s
            # GNU: date -u -d "$ts" +%s
            holder_epoch="$(date -u -j -f '%Y-%m-%dT%H:%M:%SZ' "$holder_started" +%s 2>/dev/null || \
                            date -u -d "$holder_started" +%s 2>/dev/null || echo 0)"
        fi
        local age=0
        if [ -n "$holder_epoch" ] && [ "$holder_epoch" -gt 0 ]; then
            age=$((ts - holder_epoch))
        fi

        if [ "$alive" = "1" ] && [ "$age" -lt 3600 ]; then
            # Live holder within 1h window — contention.
            echo "[aod] ERROR: update.lock held by PID $holder_pid (nonce $holder_nonce, started $holder_started)" >&2
            echo "[aod] Another /aod.update invocation is running in this adopter project." >&2
            exit 2
        fi

        if [ "$alive" = "1" ] && [ "$age" -ge 3600 ]; then
            # Live but stale — documented ambiguous case. Per data-model.md we
            # refuse to force-acquire on a live PID regardless of age (PID
            # still alive means something is running). Exit 2.
            echo "[aod] ERROR: update.lock held by live PID $holder_pid but started >1h ago ($holder_started)" >&2
            echo "[aod] Refusing to force-acquire a live-held lock. Inspect the holder and kill it if stuck." >&2
            exit 2
        fi

        if [ "$alive" = "0" ] && [ "$age" -lt 3600 ]; then
            # Dead PID within 1h — conservative refusal per data-model.md §2d.
            echo "[aod] ERROR: update.lock holder PID $holder_pid is dead but lock is <1h old (nonce $holder_nonce)" >&2
            echo "[aod] Stale lock from recent crash; manually remove .aod/update.lock if you are sure." >&2
            exit 2
        fi

        # Dead + stale (>1h). Force-acquire with nonce re-verify.
        # Write our line to a .tmp, mv over, re-read and confirm our nonce.
        local lock_tmp="${UPDATE_LOCK_PATH}.tmp.$$"
        if ! printf 'pid=%s\nnonce=%s\nstarted_at=%s\ncmdline=%s\n' \
                "$pid" "$UPDATE_LOCK_NONCE" "$iso_ts" "$cmdline" \
                > "$lock_tmp" 2>/dev/null; then
            rm -f "$lock_tmp" 2>/dev/null || true
            continue
        fi
        if ! mv "$lock_tmp" "$UPDATE_LOCK_PATH" 2>/dev/null; then
            rm -f "$lock_tmp" 2>/dev/null || true
            continue
        fi

        # Nonce re-verify.
        local observed_nonce
        observed_nonce="$(grep -m1 '^nonce=' "$UPDATE_LOCK_PATH" 2>/dev/null | cut -d= -f2)"
        if [ "$observed_nonce" = "$UPDATE_LOCK_NONCE" ]; then
            UPDATE_LOCK_ACQUIRED=1
            return 0
        fi
        # Someone else won the force-acquire race — retry.
    done

    echo "[aod] ERROR: could not acquire update.lock after $max_attempts attempts (force-acquire race exhausted)" >&2
    exit 2
}

# -----------------------------------------------------------------------------
# aod_update_release_lock
# -----------------------------------------------------------------------------
# Remove the lock file IFF our nonce still matches. Prevents zombie-PID-reuse
# from deleting a lock that some other process force-acquired.
# -----------------------------------------------------------------------------
aod_update_release_lock() {
    if [ "$UPDATE_LOCK_ACQUIRED" != "1" ]; then
        return 0
    fi
    if [ -z "$UPDATE_LOCK_PATH" ] || [ ! -f "$UPDATE_LOCK_PATH" ]; then
        return 0
    fi

    local observed_nonce
    observed_nonce="$(grep -m1 '^nonce=' "$UPDATE_LOCK_PATH" 2>/dev/null | cut -d= -f2 || echo '')"
    if [ "$observed_nonce" = "$UPDATE_LOCK_NONCE" ]; then
        rm -f "$UPDATE_LOCK_PATH" 2>/dev/null || true
    fi
}

# -----------------------------------------------------------------------------
# aod_update_cleanup_on_exit — EXIT trap
# -----------------------------------------------------------------------------
# On success: remove staging run dir + release lock.
# On failure: preserve staging run dir + release lock.
# Classification: we're in "success" iff the exit code that triggered trap is
# 0. The trap uses `$?` captured by the trap statement itself.
# -----------------------------------------------------------------------------
aod_update_cleanup_on_exit() {
    local exit_code=$?
    # Release lock unconditionally.
    aod_update_release_lock || true
    # Success or user-decline → cleanup staging. All other non-zero → preserve.
    if [ "$exit_code" -eq 0 ] || [ "$exit_code" -eq 10 ]; then
        if [ -n "$UPDATE_RUN_DIR" ] && [ -d "$UPDATE_RUN_DIR" ]; then
            rm -rf "$UPDATE_RUN_DIR" 2>/dev/null || true
        fi
    fi
    return 0
}

# =============================================================================
# Fetch phase (cli-contract.md steps 6-9)
# =============================================================================

aod_update_fetch() {
    local url="${UPDATE_UPSTREAM_URL_OVERRIDE:-$AOD_VERSION_UPSTREAM_URL}"
    local target_ref=""
    local fetch_mode=""   # "tag" | "main"

    if [ "$UPDATE_EDGE" = "1" ]; then
        target_ref="main"
        fetch_mode="main"
    else
        # Default: fetch latest tag. Use ls-remote to discover tags before
        # pulling the whole tree.
        local tags_raw=""
        tags_raw="$(git ls-remote --tags --refs "$url" 2>&1)" || {
            echo "[aod] ERROR: could not list upstream tags at $url" >&2
            exit 9
        }
        # Extract tag names (refs/tags/<tag>) and pick the largest version-sorted.
        # version-sort handles semver-ish tags correctly; plain sort as fallback.
        local latest_tag=""
        latest_tag="$(printf '%s\n' "$tags_raw" \
            | awk '{ sub(/refs\/tags\//, "", $2); print $2 }' \
            | grep -v '\^{}$' \
            | sort -V 2>/dev/null | tail -n1 \
            || printf '%s\n' "$tags_raw" | awk '{ sub(/refs\/tags\//, "", $2); print $2 }' \
                 | grep -v '\^{}$' | sort | tail -n1)"

        if [ -n "$latest_tag" ]; then
            target_ref="$latest_tag"
            fetch_mode="tag"
        else
            # No tags — fall back to main.
            target_ref="main"
            fetch_mode="main"
        fi
    fi

    # Fetch the tree at the chosen ref.
    if ! aod_template_fetch_upstream "$url" "$target_ref" "$UPDATE_UPSTREAM_DIR"; then
        local rc=$?
        if [ "$rc" = "9" ]; then
            exit 9
        fi
        exit "$rc"
    fi

    # Resolve fetched HEAD SHA.
    UPDATE_NEW_SHA="$(git -C "$UPDATE_UPSTREAM_DIR" rev-parse HEAD 2>/dev/null || echo '')"
    if [ -z "$UPDATE_NEW_SHA" ]; then
        echo "[aod] ERROR: could not resolve upstream HEAD SHA at $UPDATE_UPSTREAM_DIR" >&2
        exit 9
    fi

    # Record the target tag (may be empty for --edge / untagged).
    if [ "$fetch_mode" = "tag" ]; then
        UPDATE_NEW_TAG="$target_ref"
    else
        UPDATE_NEW_TAG="$(git -C "$UPDATE_UPSTREAM_DIR" describe --tags --exact-match HEAD 2>/dev/null || echo '')"
    fi

    # Compute SHA-256 of fetched manifest.
    local upstream_manifest="$UPDATE_UPSTREAM_DIR/.aod/template-manifest.txt"
    if [ ! -f "$upstream_manifest" ]; then
        echo "[aod] ERROR: upstream is missing .aod/template-manifest.txt" >&2
        exit 5
    fi
    UPDATE_NEW_MANIFEST_SHA="$(_aod_update_sha256 "$upstream_manifest")"

    # Manifest drift detection (informational — does not halt).
    if [ "$UPDATE_NEW_MANIFEST_SHA" != "$AOD_VERSION_MANIFEST_SHA256" ]; then
        UPDATE_MANIFEST_DRIFT=1
    fi

    # Retag detection — only applies when the adopter's pinned tag NAME equals
    # the target tag name but SHAs differ. A different tag name is a normal
    # upgrade, not a retag.
    if [ -n "$UPDATE_NEW_TAG" ] && [ "$UPDATE_EDGE" != "1" ] && [ -n "$AOD_VERSION_VERSION" ]; then
        if [ "$UPDATE_NEW_TAG" = "$AOD_VERSION_VERSION" ] && \
           [ "$UPDATE_NEW_SHA" != "$AOD_VERSION_SHA" ]; then
            if [ "$UPDATE_FORCE_RETAG" != "1" ]; then
                echo "[aod] ERROR: upstream tag $UPDATE_NEW_TAG has been retagged." >&2
                echo "[aod] recorded SHA: $AOD_VERSION_SHA" >&2
                echo "[aod] current SHA:  $UPDATE_NEW_SHA" >&2
                echo "[aod] Re-run with --force-retag if this is expected." >&2
                exit 7
            else
                echo "[aod] WARN: upstream tag $UPDATE_NEW_TAG retagged (recorded $AOD_VERSION_SHA, now $UPDATE_NEW_SHA); override engaged." >&2
            fi
        fi
    fi
}

# =============================================================================
# Plan phase (cli-contract.md steps 10-13)
# =============================================================================

# Compare two files byte-by-byte. Returns 0 if identical, 1 if differ, 2 if
# either is missing (caller semantics).
_aod_update_files_identical() {
    local a="$1"
    local b="$2"
    if [ ! -f "$a" ] || [ ! -f "$b" ]; then
        return 2
    fi
    cmp -s "$a" "$b"
}


aod_update_plan() {
    local upstream_manifest="$UPDATE_UPSTREAM_DIR/.aod/template-manifest.txt"

    # Enumerate upstream tracked files.
    local tracked_list="$UPDATE_RUN_DIR/upstream-files.txt"
    if ! git -C "$UPDATE_UPSTREAM_DIR" ls-files > "$tracked_list" 2>/dev/null; then
        echo "[aod] ERROR: could not enumerate upstream tracked files" >&2
        exit 1
    fi

    UPDATE_OPERATIONS=()
    local uncategorized_count=0
    local uncategorized_list=""

    local path winning category action change_type
    local adopter_path upstream_path

    while IFS= read -r path || [ -n "$path" ]; do
        if [ -z "$path" ]; then
            continue
        fi

        # Resolve winning category via precedence. Pipe stderr to /dev/null
        # so coverage-violation path emits ONE error from the collector below.
        # Bracket with set +e / set -e so rc=5 (uncategorized) and rc=1
        # (helper-internal error) are captured in cat_rc instead of aborting
        # the script via errexit. Matches check-manifest-coverage.sh:115-118.
        set +e
        winning="$(aod_template_category_for_path "$path" "$upstream_manifest" 2>/dev/null)"
        local cat_rc=$?
        set -e
        # Route rc=5 (uncategorized) to the coverage-violation collector below.
        # Route any OTHER non-zero rc (helper-internal error: malformed manifest,
        # library not sourced, missing args) to the defensive error branch — this
        # is checked BEFORE the `-z "$winning"` fallback so the rc=1 diagnostic
        # fires instead of being silently treated as uncategorized (FR-002).
        # rc=0 with empty winning is a degenerate "helper succeeded but returned
        # nothing" case handled as uncategorized for safety.
        if [ "$cat_rc" = "5" ]; then
            uncategorized_count=$((uncategorized_count + 1))
            if [ -z "$uncategorized_list" ]; then
                uncategorized_list="$path"
            else
                uncategorized_list="$uncategorized_list
$path"
            fi
            continue
        elif [ "$cat_rc" != "0" ]; then
            echo "[aod] ERROR: category lookup failed for $path (rc=$cat_rc)" >&2
            exit 1
        elif [ -z "$winning" ]; then
            uncategorized_count=$((uncategorized_count + 1))
            if [ -z "$uncategorized_list" ]; then
                uncategorized_list="$path"
            else
                uncategorized_list="$uncategorized_list
$path"
            fi
            continue
        fi

        category="${winning%%|*}"

        # change_type: compare upstream to adopter.
        adopter_path="$UPDATE_ADOPTER_ROOT/$path"
        upstream_path="$UPDATE_UPSTREAM_DIR/$path"
        if [ ! -e "$adopter_path" ]; then
            change_type="added"
        elif _aod_update_files_identical "$upstream_path" "$adopter_path"; then
            change_type="unchanged"
        else
            change_type="modified"
        fi

        # Action by category.
        case "$category" in
            owned)
                # Unchanged owned files don't need a copy operation (would
                # be a no-op mv). Skip to keep the preview honest and avoid
                # write churn when nothing changed.
                if [ "$change_type" = "unchanged" ]; then
                    action="skip"
                else
                    action="copy"
                fi
                ;;
            personalized)
                # A personalized file is `unchanged` iff the upstream raw
                # bytes byte-match the adopter's current bytes. Under that
                # equality, any substitution would be a no-op from the
                # adopter's perspective (either both have placeholders — an
                # uncommon rest state but still nothing for us to churn — or
                # both are already fully substituted to the same values).
                #
                # If the bytes differ, re-substitute to produce the correct
                # adopter-side bytes. (The difference may arise from upstream
                # evolving the file, from the adopter's personalization.env
                # being edited since pin, or from a fresh bootstrap where
                # upstream has raw placeholders but adopter has been
                # substituted already.)
                #
                # This simple raw-byte equality keeps the no-changes path
                # stable while also guaranteeing re-substitute when either
                # side has drifted. See contracts/cli-contract.md step 20/21.
                if [ "$change_type" = "unchanged" ]; then
                    # Raw upstream bytes match adopter bytes — no net change.
                    action="skip"
                else
                    action="substitute"
                fi
                ;;
            user)
                action="skip"
                ;;
            scaffold)
                # P0: copy-if-missing. Skip if adopter already has it.
                if [ -e "$UPDATE_ADOPTER_ROOT/$path" ]; then
                    action="skip"
                else
                    action="copy"
                fi
                ;;
            merge)
                # Only warn for files that actually changed — unchanged merge
                # files need no adopter action.
                if [ "$change_type" = "unchanged" ]; then
                    action="skip"
                else
                    action="warn-and-skip"
                fi
                ;;
            ignore)
                action="skip"
                ;;
            *)
                echo "[aod] ERROR: unknown category '$category' for $path" >&2
                exit 1
                ;;
        esac

        UPDATE_OPERATIONS+=("${path}${UPDATE_OP_SEP}${category}${UPDATE_OP_SEP}${winning}${UPDATE_OP_SEP}${change_type}${UPDATE_OP_SEP}${action}")
    done < "$tracked_list"

    if [ "$uncategorized_count" -gt 0 ]; then
        echo "[aod] ERROR: manifest coverage violation — $uncategorized_count upstream file(s) not categorized:" >&2
        printf '%s\n' "$uncategorized_list" | sed 's/^/  - /' >&2
        exit 5
    fi
}

# =============================================================================
# Validate phase (cli-contract.md steps 14-16)
# =============================================================================

aod_update_validate() {
    local op path cat winning change action
    local guard_input=""
    local symlink_input=""

    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"

        # Safe-path check (always).
        if ! aod_template_assert_safe_path "$path" >/dev/null 2>&1; then
            echo "[aod] ERROR: unsafe upstream path: $path" >&2
            exit 1
        fi

        # Guard check only for write operations.
        case "$action" in
            copy|substitute)
                if [ -z "$guard_input" ]; then
                    guard_input="$path|$action"
                else
                    guard_input="$guard_input
$path|$action"
                fi
                local upstream_abs="$UPDATE_UPSTREAM_DIR/$path"
                if [ -z "$symlink_input" ]; then
                    symlink_input="$upstream_abs"
                else
                    symlink_input="$symlink_input
$upstream_abs"
                fi
                ;;
        esac
    done

    # Guard phase (step 14). Exits 6 on violation.
    if [ -n "$guard_input" ]; then
        printf '%s\n' "$guard_input" | aod_template_update_validate_guards
    fi

    # Symlink phase (step 16). Exits 1 on violation.
    if [ -n "$symlink_input" ]; then
        printf '%s\n' "$symlink_input" | aod_template_update_validate_no_symlinks
    fi
}

# =============================================================================
# Stage phase (cli-contract.md steps 17-19)
# =============================================================================

# Copy a file preserving mode. Creates parent dirs as needed.
_aod_update_copy_preserve_mode() {
    local src="$1"
    local dst="$2"
    local parent
    parent="$(dirname "$dst")"
    if ! mkdir -p "$parent" 2>/dev/null; then
        return 1
    fi
    # cp -p preserves mode + mtime on both BSD and GNU.
    cp -p "$src" "$dst" 2>/dev/null || return 1
    return 0
}

aod_update_stage() {
    local op path cat winning change action
    local substitute_list=""

    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"

        case "$action" in
            copy|substitute)
                local src="$UPDATE_UPSTREAM_DIR/$path"
                local dst="$UPDATE_STAGED_DIR/$path"
                if ! _aod_update_copy_preserve_mode "$src" "$dst"; then
                    echo "[aod] ERROR: stage copy failed for $path" >&2
                    exit 1
                fi
                if [ "$action" = "substitute" ]; then
                    if [ -z "$substitute_list" ]; then
                        substitute_list="$dst"
                    else
                        substitute_list="$substitute_list
$dst"
                    fi
                fi
                ;;
            warn-and-skip)
                echo "[skip ] $path                    (merge category, P0 defer)" >&2
                ;;
            skip)
                : ;;
        esac
    done

    # Point the substitute loader at the adopter's personalization.env.
    export AOD_PERSONALIZATION_ENV_PATH="$UPDATE_ADOPTER_ROOT/.aod/personalization.env"

    # Substitute + residual-scan. aod_template_update_stage_substitute returns
    # 0 on success; 3 on env missing; 8 on residual or load failure; 1 on IO.
    if [ -n "$substitute_list" ]; then
        local sub_rc=0
        printf '%s\n' "$substitute_list" | aod_template_update_stage_substitute || sub_rc=$?
        if [ "$sub_rc" != "0" ]; then
            # Preserve staging; propagate the rc.
            exit "$sub_rc"
        fi
    fi
}

# =============================================================================
# Preview phase (cli-contract.md steps 20-22)
# =============================================================================

# Count non-skip operations that will actually write bytes to the adopter.
# A "write" requires BOTH:
#   - A write action (copy or substitute)
#   - A change_type that is not `unchanged` (unchanged means post-substitution
#     bytes equal the adopter's current bytes; re-writing them is a no-op)
#
# Defense-in-depth: the plan phase already marks personalized:unchanged as
# `skip`, but this check is tolerant of either labelling so future plan-phase
# refactors won't silently break the no-changes short-circuit.
_aod_update_count_writes() {
    local op path cat winning change action
    local count=0
    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"
        # Unchanged never counts, regardless of recorded action.
        if [ "$change" = "unchanged" ]; then
            continue
        fi
        case "$action" in
            copy|substitute)
                count=$((count + 1))
                ;;
        esac
    done
    echo "$count"
}

# Count by category+change_type. Emits `<category> <added> <modified> <removed> <unchanged>`
# for each of the 4 non-hidden categories.
_aod_update_category_counts() {
    local op path cat winning change action
    local owned_added=0 owned_modified=0 owned_removed=0 owned_unchanged=0
    local per_added=0 per_modified=0 per_removed=0 per_unchanged=0
    local scaffold_added=0 scaffold_modified=0 scaffold_removed=0 scaffold_unchanged=0
    local merge_added=0 merge_modified=0 merge_removed=0 merge_unchanged=0

    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"
        case "$cat:$change" in
            owned:added)        owned_added=$((owned_added + 1)) ;;
            owned:modified)     owned_modified=$((owned_modified + 1)) ;;
            owned:removed)      owned_removed=$((owned_removed + 1)) ;;
            owned:unchanged)    owned_unchanged=$((owned_unchanged + 1)) ;;
            personalized:added)     per_added=$((per_added + 1)) ;;
            personalized:modified)  per_modified=$((per_modified + 1)) ;;
            personalized:removed)   per_removed=$((per_removed + 1)) ;;
            personalized:unchanged) per_unchanged=$((per_unchanged + 1)) ;;
            scaffold:added)     scaffold_added=$((scaffold_added + 1)) ;;
            scaffold:modified)  scaffold_modified=$((scaffold_modified + 1)) ;;
            scaffold:removed)   scaffold_removed=$((scaffold_removed + 1)) ;;
            scaffold:unchanged) scaffold_unchanged=$((scaffold_unchanged + 1)) ;;
            merge:added)        merge_added=$((merge_added + 1)) ;;
            merge:modified)     merge_modified=$((merge_modified + 1)) ;;
            merge:removed)      merge_removed=$((merge_removed + 1)) ;;
            merge:unchanged)    merge_unchanged=$((merge_unchanged + 1)) ;;
        esac
    done

    printf 'owned %d %d %d %d\n' "$owned_added" "$owned_modified" "$owned_removed" "$owned_unchanged"
    printf 'personalized %d %d %d %d\n' "$per_added" "$per_modified" "$per_removed" "$per_unchanged"
    printf 'scaffold %d %d %d %d\n' "$scaffold_added" "$scaffold_modified" "$scaffold_removed" "$scaffold_unchanged"
    printf 'merge %d %d %d %d\n' "$merge_added" "$merge_modified" "$merge_removed" "$merge_unchanged"
}

# -----------------------------------------------------------------------------
# aod_update_preview_human (T070)
# -----------------------------------------------------------------------------
# Render the human-readable preview per contracts/cli-contract.md §Stdout/Stderr.
#
# Sections (in order):
#   1. Header banner — `AOD-kit update: upstream → downstream`
#   2. Current pin + Target lines with version, sha, manifest sha256
#   3. (optional) Manifest-drift banner
#   4. Category summary table — owned / personalized / scaffold / merge, plus
#      hidden/not-inspected rows for user + ignore
#   5. Per-file lists grouped by section:
#      - Owned changes (action=copy): `+` added / `~` modified
#      - Personalized changes (action=substitute): `+` added / `~` modified
#      - Merge changes (action=warn-and-skip): `!` (P0 defer)
#
# When there are zero pending writes, emit a single short "Already up to
# date" line and exit early (the no-changes short-circuit).
# -----------------------------------------------------------------------------
aod_update_preview_human() {
    local writes
    writes="$(_aod_update_count_writes)"

    # Short-cut: no pending writes → "already up to date".
    if [ "$writes" = "0" ]; then
        cat <<EOF
AOD-kit update: upstream → downstream

Current pin:  ${AOD_VERSION_VERSION:-<untagged>}  (sha ${AOD_VERSION_SHA}, manifest sha256 ${AOD_VERSION_MANIFEST_SHA256})
Target:       ${UPDATE_NEW_TAG:-<untagged>}  (sha ${UPDATE_NEW_SHA}, manifest sha256 ${UPDATE_NEW_MANIFEST_SHA})

Already up to date — 0 added, 0 modified, 0 removed.
EOF
        return 0
    fi

    cat <<EOF
AOD-kit update: upstream → downstream

Current pin:  ${AOD_VERSION_VERSION:-<untagged>}  (sha ${AOD_VERSION_SHA}, manifest sha256 ${AOD_VERSION_MANIFEST_SHA256})
Target:       ${UPDATE_NEW_TAG:-<untagged>}  (sha ${UPDATE_NEW_SHA}, manifest sha256 ${UPDATE_NEW_MANIFEST_SHA})

EOF

    if [ "$UPDATE_MANIFEST_DRIFT" = "1" ]; then
        echo "Manifest drift: manifest SHA-256 changed since last pin (inspect diff)"
        echo ""
    fi

    echo "Category      Added  Modified  Removed  Unchanged"
    local line
    _aod_update_category_counts | while read -r line; do
        # Each line: "<category> <a> <m> <r> <u>"
        set -- $line
        printf '%-13s %-6s %-9s %-8s %s\n' "$1" "$2" "$3" "$4" "$5"
    done
    echo "user          —      —         —        —        (hidden by policy)"
    echo "ignore        —      —         —        —        (not inspected)"
    echo ""

    # Per-file list for owned + personalized + merge.
    local op path category winning change_type action
    local printed_owned=0 printed_personalized=0 printed_merge=0

    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path category winning change_type action <<< "$op"

        case "$category:$action" in
            owned:copy)
                if [ "$printed_owned" = "0" ]; then
                    echo "Owned changes (will be overwritten):"
                    printed_owned=1
                fi
                case "$change_type" in
                    added)    printf '  + %s\n' "$path" ;;
                    modified) printf '  ~ %s\n' "$path" ;;
                    *)        printf '  = %s\n' "$path" ;;
                esac
                ;;
            personalized:substitute)
                if [ "$printed_personalized" = "0" ]; then
                    if [ "$printed_owned" = "1" ]; then echo ""; fi
                    echo "Personalized changes (placeholders re-applied):"
                    printed_personalized=1
                fi
                case "$change_type" in
                    added)    printf '  + %s\n' "$path" ;;
                    modified) printf '  ~ %s\n' "$path" ;;
                    *)        printf '  = %s\n' "$path" ;;
                esac
                ;;
            merge:warn-and-skip)
                if [ "$printed_merge" = "0" ]; then
                    if [ "$printed_personalized" = "1" ] || [ "$printed_owned" = "1" ]; then echo ""; fi
                    echo "Merge changes (P0 warn-and-skip — resolve manually):"
                    printed_merge=1
                fi
                printf '  ! %s\n' "$path"
                ;;
        esac
    done
    echo ""
}

# -----------------------------------------------------------------------------
# _aod_update_json_counts_for_cat <category>
# -----------------------------------------------------------------------------
# Helper for JSON renderer: emit the `{added, modified, removed, unchanged}`
# counts for <category> as a pre-formatted JSON object body (no outer braces).
# Used to build the counts_by_category object in the envelope.
# -----------------------------------------------------------------------------
_aod_update_json_counts_for_cat() {
    local target_cat="$1"
    local op path cat winning change action
    local a=0 m=0 r=0 u=0
    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"
        if [ "$cat" != "$target_cat" ]; then
            continue
        fi
        case "$change" in
            added)     a=$((a + 1)) ;;
            modified)  m=$((m + 1)) ;;
            removed)   r=$((r + 1)) ;;
            unchanged) u=$((u + 1)) ;;
        esac
    done
    printf '{"added":%d,"modified":%d,"removed":%d,"unchanged":%d}' "$a" "$m" "$r" "$u"
}

# -----------------------------------------------------------------------------
# _aod_update_json_hidden_count <category>
# -----------------------------------------------------------------------------
# Emit the count of operations in <category> as JSON (`user` and `ignore` are
# reported as `{"hidden":N}` and `{"excluded":N}` respectively per the schema).
# -----------------------------------------------------------------------------
_aod_update_json_hidden_count() {
    local target_cat="$1"
    local field="$2"  # "hidden" or "excluded"
    local op path cat winning change action
    local n=0
    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"
        if [ "$cat" = "$target_cat" ]; then
            n=$((n + 1))
        fi
    done
    printf '{"%s":%d}' "$field" "$n"
}

# -----------------------------------------------------------------------------
# _aod_update_total_upstream_files
# -----------------------------------------------------------------------------
_aod_update_total_upstream_files() {
    echo "${#UPDATE_OPERATIONS[@]}"
}

# -----------------------------------------------------------------------------
# _aod_update_render_operation_json <path> <category> <winning> <change_type>
#                                   <action>
# -----------------------------------------------------------------------------
# Emit a single `operations[]` element as a JSON object string. Fields per
# contracts/json-output-schema.md §operations[]. Optional fields (upstream_sha,
# local_sha, status, reason, placeholders_applied) are elided when not known.
# -----------------------------------------------------------------------------
_aod_update_render_operation_json() {
    local path="$1"
    local category="$2"
    local winning="$3"
    local change_type="$4"
    local action="$5"

    # Each value is escape-safe via aod_template_json_escape.
    local p_esc c_esc w_esc ct_esc a_esc status
    p_esc="$(aod_template_json_escape "$path")"
    c_esc="$(aod_template_json_escape "$category")"
    w_esc="$(aod_template_json_escape "$winning")"
    ct_esc="$(aod_template_json_escape "$change_type")"
    a_esc="$(aod_template_json_escape "$action")"

    # status field: "planned" for preview/dry-run output. Apply-time output
    # would rewrite this to "applied" etc., but current path only emits once
    # at preview time.
    if [ "$UPDATE_MODE" = "dry-run" ]; then
        status="planned"
    else
        # In apply mode, this JSON is emitted AFTER the apply phase so we use
        # "applied" for writes + "skipped" for skips + "protected" for user.
        case "$category:$action" in
            user:*)              status="protected" ;;
            *:skip|*:warn-and-skip) status="skipped" ;;
            *)                   status="applied" ;;
        esac
    fi

    printf '{"path":"%s","category":"%s","winning_entry":"%s","change_type":"%s","action":"%s","status":"%s"}' \
        "$p_esc" "$c_esc" "$w_esc" "$ct_esc" "$a_esc" "$status"
}

# -----------------------------------------------------------------------------
# _aod_update_render_manifest_drift_json
# -----------------------------------------------------------------------------
# Emit the `manifest_drift` object per schema. Currently P0 only populates
# `hash_changed` and empty transition arrays; richer drift analysis (entry-by-
# entry diff) is 129b scope.
# -----------------------------------------------------------------------------
_aod_update_render_manifest_drift_json() {
    local changed="false"
    if [ "$UPDATE_MANIFEST_DRIFT" = "1" ]; then
        changed="true"
    fi
    printf '{"hash_changed":%s,"user_to_owned_transitions":[],"user_to_personalized_transitions":[],"added_entries":0,"removed_entries":0,"category_changed_entries":0}' "$changed"
}

# -----------------------------------------------------------------------------
# _aod_update_render_summary_json
# -----------------------------------------------------------------------------
# Emit the `summary` object: total_upstream_files + counts_by_category.
# -----------------------------------------------------------------------------
_aod_update_render_summary_json() {
    local total owned_c per_c scaff_c merge_c user_c ignore_c
    total="$(_aod_update_total_upstream_files)"
    owned_c="$(_aod_update_json_counts_for_cat owned)"
    per_c="$(_aod_update_json_counts_for_cat personalized)"
    scaff_c="$(_aod_update_json_counts_for_cat scaffold)"
    merge_c="$(_aod_update_json_counts_for_cat merge)"
    user_c="$(_aod_update_json_hidden_count user hidden)"
    ignore_c="$(_aod_update_json_hidden_count ignore excluded)"
    printf '{"total_upstream_files":%d,"counts_by_category":{"owned":%s,"personalized":%s,"scaffold":%s,"merge":%s,"user":%s,"ignore":%s}}' \
        "$total" "$owned_c" "$per_c" "$scaff_c" "$merge_c" "$user_c" "$ignore_c"
}

# -----------------------------------------------------------------------------
# aod_update_render_json (T071)
# -----------------------------------------------------------------------------
# Emit the schema_version 1.0 JSON envelope per contracts/json-output-schema.md.
# One line, no pretty-printing. Written to stdout. No colors, no prompts, no
# progress bars. The `--json` flag selects this renderer over the human one.
#
# Uses template-json.sh helpers (aod_template_json_emit_envelope) with `@raw`
# sentinels for numeric/array/object values. String values pass through
# aod_template_json_escape inside _kv.
#
# Inputs (from module state populated by preflight/fetch/plan):
#   AOD_VERSION_*           — the "before" pin (version, sha, manifest_sha256, upstream_url)
#   UPDATE_NEW_TAG, SHA, MANIFEST_SHA   — the "after" pin
#   UPDATE_OPERATIONS       — populated by plan phase
#   UPDATE_MANIFEST_DRIFT   — 0 or 1
#   UPDATE_MODE             — "dry-run" or "apply" — determines `operation` field
#   UPDATE_START_TS         — ISO 8601 UTC when preflight completed
#
# Operation semantics (per contracts/json-output-schema.md):
#   - `operation: "dry-run"` when --dry-run is in effect
#   - `operation: "preview"` when preview is emitted before user decline or
#     before apply (we emit JSON at preview time in apply mode too so adopters
#     can see the plan before confirming)
#   - `operation: "apply"` when this JSON is rendered AFTER apply succeeds
# -----------------------------------------------------------------------------
aod_update_render_json() {
    local operation="${1:-preview}"
    local exit_code="${2:-0}"

    local end_ts duration started_epoch ended_epoch
    end_ts="$(_aod_update_iso_utc)"
    started_epoch="$(date -u -j -f '%Y-%m-%dT%H:%M:%SZ' "$UPDATE_START_TS" +%s 2>/dev/null || \
                     date -u -d "$UPDATE_START_TS" +%s 2>/dev/null || echo 0)"
    ended_epoch="$(date -u +%s)"
    if [ "$started_epoch" -gt 0 ]; then
        duration=$((ended_epoch - started_epoch))
    else
        duration=0
    fi

    # Build "before" object (pin state prior to run).
    local before_obj after_obj
    before_obj="$(printf '{"version":"%s","sha":"%s","manifest_sha256":"%s","upstream_url":"%s"}' \
        "$(aod_template_json_escape "${AOD_VERSION_VERSION:-}")" \
        "$(aod_template_json_escape "${AOD_VERSION_SHA:-}")" \
        "$(aod_template_json_escape "${AOD_VERSION_MANIFEST_SHA256:-}")" \
        "$(aod_template_json_escape "${AOD_VERSION_UPSTREAM_URL:-}")")"

    # Build "after" object. On dry-run / preview / decline, `after` equals `before`
    # (nothing was applied yet). On apply success, `after` reflects the fetched
    # target. We conservatively use the fetched target for both preview and
    # apply here; on abort the caller should set operation=preview with the
    # expectation that the consumer reads operation to decide.
    if [ "$operation" = "dry-run" ] || [ "$operation" = "preview" ]; then
        # For preview/dry-run, `after` is the PROSPECTIVE target — what the
        # apply would land on.
        after_obj="$(printf '{"version":"%s","sha":"%s","manifest_sha256":"%s"}' \
            "$(aod_template_json_escape "${UPDATE_NEW_TAG:-${AOD_VERSION_VERSION:-}}")" \
            "$(aod_template_json_escape "${UPDATE_NEW_SHA:-${AOD_VERSION_SHA:-}}")" \
            "$(aod_template_json_escape "${UPDATE_NEW_MANIFEST_SHA:-${AOD_VERSION_MANIFEST_SHA256:-}}")")"
    else
        # apply
        after_obj="$(printf '{"version":"%s","sha":"%s","manifest_sha256":"%s"}' \
            "$(aod_template_json_escape "${UPDATE_NEW_TAG:-${AOD_VERSION_VERSION:-}}")" \
            "$(aod_template_json_escape "${UPDATE_NEW_SHA:-${AOD_VERSION_SHA:-}}")" \
            "$(aod_template_json_escape "${UPDATE_NEW_MANIFEST_SHA:-${AOD_VERSION_MANIFEST_SHA256:-}}")")"
    fi

    # Build operations[] array — one object per UPDATE_OPERATIONS entry.
    local ops_body=""
    local op path category winning change_type action op_json
    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path category winning change_type action <<< "$op"
        op_json="$(_aod_update_render_operation_json "$path" "$category" "$winning" "$change_type" "$action")"
        aod_template_json_array_append ops_body "$op_json"
    done
    local ops_array="[${ops_body}]"

    # manifest_drift object
    local drift_obj summary_obj
    drift_obj="$(_aod_update_render_manifest_drift_json)"
    summary_obj="$(_aod_update_render_summary_json)"

    # warnings/errors — currently both empty; populate future signal as needed.
    local warnings_array="[]"
    local errors_array="[]"

    # Assemble via the envelope helper. Keys with @raw suffix emit value
    # literally (for numbers/arrays/objects).
    aod_template_json_emit_envelope \
        command         "aod.update" \
        operation       "$operation" \
        started_at      "${UPDATE_START_TS:-}" \
        ended_at        "$end_ts" \
        "duration_seconds@raw" "$duration" \
        "exit_code@raw"        "$exit_code" \
        "before@raw"           "$before_obj" \
        "after@raw"            "$after_obj" \
        "manifest_drift@raw"   "$drift_obj" \
        "summary@raw"          "$summary_obj" \
        "operations@raw"       "$ops_array" \
        "warnings@raw"         "$warnings_array" \
        "errors@raw"           "$errors_array"
}

# -----------------------------------------------------------------------------
# aod_update_preview — the dispatcher-facing preview entry point
# -----------------------------------------------------------------------------
# Chooses between JSON and human-readable renderers based on UPDATE_JSON.
# -----------------------------------------------------------------------------
aod_update_preview() {
    if [ "$UPDATE_JSON" = "1" ]; then
        local op
        if [ "$UPDATE_MODE" = "dry-run" ]; then
            op="dry-run"
        else
            op="preview"
        fi
        aod_update_render_json "$op" 0
    else
        aod_update_preview_human
    fi
}

# -----------------------------------------------------------------------------
# aod_update_confirm (T072)
# -----------------------------------------------------------------------------
# Interactive confirmation prompt. Returns 0 on approve, non-zero on decline.
#
# Call sites in the dispatcher ALREADY gate on `--yes` and `--dry-run` so this
# function only runs when a prompt is appropriate. It also handles:
#
#   - TTY detection for input source: prefers /dev/tty (so prompt works even
#     when stdin was consumed by a pipe); falls back to stdin.
#   - Strict y/Y-only acceptance per contract (anything else, including empty
#     reply, declines).
#   - No `${var^^}` / `${var,,}` (bash 3.2 incompat) — uses `case` directly.
#
# The dispatcher is responsible for verifying:
#   - --yes is absent
#   - --dry-run is absent
#   - CI env is not set (handled via UPDATE_MODE resolution in parse_flags)
# -----------------------------------------------------------------------------
aod_update_confirm() {
    # Prefer /dev/tty for prompt I/O — lets the prompt work even when the
    # caller piped stdin (e.g., `echo y | make update`).
    local tty_src
    if [ -r /dev/tty ]; then
        tty_src="/dev/tty"
    else
        tty_src=""
    fi

    printf 'Continue? [y/N] '
    local reply=""
    if [ -n "$tty_src" ]; then
        IFS= read -r reply < "$tty_src" || reply=""
    else
        IFS= read -r reply || reply=""
    fi

    # Strict case-insensitive y acceptance via `case` (bash 3.2 has no
    # ${var,,} case-lowering). Anything else → decline.
    case "$reply" in
        y|Y) return 0 ;;
        *)   return 1 ;;
    esac
}

# =============================================================================
# Apply phase (cli-contract.md steps 23-24)
# =============================================================================

aod_update_apply() {
    local op path cat winning change action
    local applied_count=0

    for op in "${UPDATE_OPERATIONS[@]}"; do
        IFS="$UPDATE_OP_SEP" read -r path cat winning change action <<< "$op"

        case "$action" in
            copy|substitute)
                local staged="$UPDATE_STAGED_DIR/$path"
                local target="$UPDATE_ADOPTER_ROOT/$path"
                local target_parent
                target_parent="$(dirname "$target")"
                if ! mkdir -p "$target_parent" 2>/dev/null; then
                    echo "[aod] ERROR: could not create parent dir: $target_parent" >&2
                    exit 1
                fi
                if ! mv "$staged" "$target" 2>/dev/null; then
                    echo "[aod] ERROR: atomic rename failed: $staged → $target" >&2
                    exit 1
                fi
                case "$action" in
                    copy)
                        printf '[apply] %s                 (copy)\n' "$path"
                        ;;
                    substitute)
                        printf '[apply] %s                 (substitute)\n' "$path"
                        ;;
                esac
                applied_count=$((applied_count + 1))
                ;;
            warn-and-skip)
                # Already logged in stage phase.
                : ;;
            skip)
                : ;;
        esac
    done

    # TEST-ONLY injection point for partial-failure integration test (T054).
    # Gated behind AOD_UPDATE_TEST_FAIL_AT_STAGE=24 env var — unset in all
    # production paths. When set, emits a synthetic failure AT the stage-24
    # boundary (after all stage-23 copies succeeded, before version-file write)
    # to exercise §Failure semantics invariants: staging preserved, version
    # pin unchanged, lock released.
    if [ "${AOD_UPDATE_TEST_FAIL_AT_STAGE:-}" = "24" ]; then
        echo "[aod] ERROR: TEST-ONLY stage-24 failure injection (AOD_UPDATE_TEST_FAIL_AT_STAGE=24). Applied $applied_count file(s); version pin NOT advanced." >&2
        exit 1
    fi

    # Write new version file (LAST). This is the commit point.
    local version_file="$UPDATE_ADOPTER_ROOT/.aod/aod-kit-version"
    local new_url="${UPDATE_UPSTREAM_URL_OVERRIDE:-$AOD_VERSION_UPSTREAM_URL}"
    local now
    now="$(_aod_update_iso_utc)"

    if ! aod_template_write_version_file \
            "$version_file" \
            "${UPDATE_NEW_TAG:-$AOD_VERSION_VERSION}" \
            "$UPDATE_NEW_SHA" \
            "$now" \
            "$new_url" \
            "$UPDATE_NEW_MANIFEST_SHA"; then
        local rc=$?
        echo "[aod] ERROR: failed to write version file (rc=$rc). Applied $applied_count file(s); version pin NOT advanced." >&2
        exit "$rc"
    fi

    printf '[apply] %s                 (atomic write)\n' ".aod/aod-kit-version"
}

# =============================================================================
# Dispatcher
# =============================================================================

aod_update_main() {
    aod_update_parse_flags "$@"

    aod_update_preflight

    # Register cleanup trap AFTER preflight succeeds (so we have sane state).
    trap 'aod_update_cleanup_on_exit' EXIT INT TERM

    aod_update_acquire_lock

    # TEST-ONLY injection point for lock-contention integration test (T053).
    # Gated behind AOD_UPDATE_TEST_STALL_AFTER_LOCK env var (secs as integer)
    # — unset in all production paths. When set, holds the lock for N seconds
    # so concurrent invocations deterministically observe the held lock.
    if [ -n "${AOD_UPDATE_TEST_STALL_AFTER_LOCK:-}" ]; then
        sleep "$AOD_UPDATE_TEST_STALL_AFTER_LOCK"
    fi

    aod_update_fetch
    aod_update_plan
    aod_update_validate
    aod_update_stage

    # In JSON mode, the preview is the ENTIRE stdout product — emit it in
    # apply-or-dry-run mode. Apply mode re-emits JSON (with operation="apply")
    # after apply completes; the preview call here emits operation="preview".
    local writes
    writes="$(_aod_update_count_writes)"

    if [ "$UPDATE_JSON" = "1" ]; then
        # JSON mode: emit a single JSON line describing the planned changes
        # (dry-run or preview). For --dry-run we emit and exit; for apply
        # mode we still emit the preview JSON, then (silently — no prompt)
        # short-circuit apply when writes==0 OR skip-prompt when --yes.
        # Prompts are unavailable in --json mode: adopters must pair --json
        # with --yes or --dry-run per cli-contract.md.
        aod_update_preview

        if [ "$UPDATE_MODE" = "dry-run" ]; then
            exit 0
        fi
        if [ "$writes" = "0" ]; then
            exit 0
        fi
        # JSON + apply: must have --yes (otherwise we can't prompt in JSON
        # mode). If --yes was not passed, we already fell back to dry-run
        # via stdin-non-TTY rule in parse_flags (when stdin is not a TTY).
        # Belt-and-suspenders: refuse to prompt in JSON mode.
        if [ "$UPDATE_YES" != "1" ]; then
            # Fall back to dry-run behavior.
            exit 0
        fi
        aod_update_apply >/dev/null 2>&1 || {
            local rc=$?
            aod_update_render_json "apply" "$rc"
            exit "$rc"
        }
        aod_update_render_json "apply" 0
        exit 0
    fi

    # Human-readable flow.
    aod_update_preview

    if [ "$UPDATE_MODE" = "dry-run" ]; then
        # Dry-run: clean staging (trap handles), exit 0.
        echo "[done ] Dry-run complete; no files written."
        exit 0
    fi

    if [ "$writes" = "0" ]; then
        # Nothing to apply — don't churn version pin.
        echo "[done ] Already up to date; nothing to apply."
        exit 0
    fi

    # Confirm before apply unless --yes or explicit CI automation.
    if [ "$UPDATE_YES" != "1" ]; then
        if ! aod_update_confirm; then
            echo "[abort] User declined. Staging cleaned." >&2
            exit 10
        fi
    fi

    aod_update_apply

    local end_ts duration
    end_ts="$(date -u +%s)"
    local start_epoch
    start_epoch="$(date -u -j -f '%Y-%m-%dT%H:%M:%SZ' "$UPDATE_START_TS" +%s 2>/dev/null || \
                   date -u -d "$UPDATE_START_TS" +%s 2>/dev/null || echo "$end_ts")"
    duration=$((end_ts - start_epoch))

    echo "[done ] Update complete in ${duration}s."
}

# =============================================================================
# Feature 134 subcommand dispatch (--bootstrap, --check-placeholders)
# =============================================================================
# Per FR-001, scripts/update.sh recognizes two additional subcommand entry
# points that are routed to dedicated library modules BEFORE the main F129
# update pipeline runs.
#
# Mutual exclusivity (FR-001):
#   - --bootstrap and --check-placeholders cannot appear together
#   - Neither can be combined with --dry-run / --apply / --json (which are
#     flags of the existing `make update` pipeline, not these subcommands)
#
# Violations exit 1 with a specific stderr message naming the conflicting
# flags. All other flag parsing (including --yes, --upstream-url=<url>) is
# delegated to the subcommand module's own parser.
#
# See: specs/134-update-bootstrap-placeholder-migration/contracts/cli-contract.md
# -----------------------------------------------------------------------------

aod_update_feature134_dispatch() {
    # Scan caller-forwarded args for the four flag classes we care about.
    # This is a pre-scan: it does NOT consume the args; the subcommand's
    # own parser (or aod_update_parse_flags for the default path) handles
    # that.
    local has_bootstrap=0
    local has_check_placeholders=0
    local has_dry_run=0
    local has_apply=0
    local has_json=0

    local arg
    for arg in "$@"; do
        case "$arg" in
            --bootstrap)               has_bootstrap=1 ;;
            --check-placeholders)      has_check_placeholders=1 ;;
            --dry-run|-n)              has_dry_run=1 ;;
            --apply)                   has_apply=1 ;;
            --json)                    has_json=1 ;;
        esac
    done

    # If neither subcommand flag present, fall through to the default F129
    # update pipeline (aod_update_main).
    if [ "$has_bootstrap" -eq 0 ] && [ "$has_check_placeholders" -eq 0 ]; then
        return 0
    fi

    # Mutex 1: --bootstrap + --check-placeholders
    if [ "$has_bootstrap" -eq 1 ] && [ "$has_check_placeholders" -eq 1 ]; then
        printf 'Error: --bootstrap and --check-placeholders are mutually exclusive.\n' >&2
        printf 'Usage: scripts/update.sh --bootstrap | --check-placeholders | --apply | --dry-run ...\n' >&2
        exit 1
    fi

    # Mutex 2: --bootstrap + any of --dry-run / --apply / --json
    if [ "$has_bootstrap" -eq 1 ]; then
        if [ "$has_dry_run" -eq 1 ]; then
            printf 'Error: --bootstrap and --dry-run are mutually exclusive.\n' >&2
            exit 1
        fi
        if [ "$has_apply" -eq 1 ]; then
            printf 'Error: --bootstrap and --apply are mutually exclusive.\n' >&2
            exit 1
        fi
        if [ "$has_json" -eq 1 ]; then
            printf 'Error: --bootstrap and --json are mutually exclusive.\n' >&2
            exit 1
        fi
    fi

    # Mutex 3: --check-placeholders + any of --dry-run / --apply / --json
    if [ "$has_check_placeholders" -eq 1 ]; then
        if [ "$has_dry_run" -eq 1 ]; then
            printf 'Error: --check-placeholders and --dry-run are mutually exclusive.\n' >&2
            exit 1
        fi
        if [ "$has_apply" -eq 1 ]; then
            printf 'Error: --check-placeholders and --apply are mutually exclusive.\n' >&2
            exit 1
        fi
        if [ "$has_json" -eq 1 ]; then
            printf 'Error: --check-placeholders and --json are mutually exclusive.\n' >&2
            exit 1
        fi
    fi

    # ---- Dispatch to the appropriate library module ----
    if [ "$has_bootstrap" -eq 1 ]; then
        # T015: source bootstrap.sh and invoke aod_bootstrap_main. Library
        # path is relative to scripts/update.sh via the already-resolved
        # AOD_UPDATE_LIB_DIR.
        # shellcheck disable=SC1091
        . "$AOD_UPDATE_LIB_DIR/bootstrap.sh"
        aod_bootstrap_main "$@"
        exit $?
    fi

    if [ "$has_check_placeholders" -eq 1 ]; then
        # T023: source check-placeholders.sh and invoke aod_check_placeholders_main.
        # Library path is relative to scripts/update.sh via the already-resolved
        # AOD_UPDATE_LIB_DIR.
        # shellcheck disable=SC1091
        . "$AOD_UPDATE_LIB_DIR/check-placeholders.sh"
        aod_check_placeholders_main "$@"
        exit $?
    fi

    # Unreachable.
    return 0
}

# -----------------------------------------------------------------------------
# Entry — only dispatch when executed directly (not when sourced by tests).
# -----------------------------------------------------------------------------
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Feature 134 subcommand dispatch runs BEFORE the default F129 pipeline
    # so --bootstrap / --check-placeholders can intercept and short-circuit.
    # On mutex violation this calls exit 1; on successful subcommand routing
    # it calls exit $? (either exit 0 for success or the subcommand's own
    # failure code). If neither flag present, this returns 0 and the default
    # pipeline runs.
    aod_update_feature134_dispatch "$@"
    aod_update_main "$@"
fi
