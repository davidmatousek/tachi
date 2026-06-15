#!/usr/bin/env bash
# =============================================================================
# template-git.sh — Upstream fetch, diff, retag detection, fs-device helper
# =============================================================================
# Part of feature 129 (downstream template update mechanism).
#
# Bash 3.2 compatible. Sourced by scripts/update.sh and scripts/init.sh.
#
# Public functions (prefix: aod_template_):
#   - aod_template_fetch_upstream          Clone upstream via HTTPS (depth=1) to
#                                          a staging dir. Enforces `https://`
#                                          or `file://` prefix.
#   - aod_template_compute_diff            git diff --name-status on two working
#                                          trees (between fetched upstream and
#                                          adopter).
#   - aod_template_detect_retag            Compare fetched SHA to recorded SHA;
#                                          exit 7 on mismatch unless --force-retag.
#                                          STUB in T015 — body implemented in T026.
#   - aod_template_fs_device               Emit filesystem device number.
#                                          Uses `stat -f %d` on BSD, `stat -c %d`
#                                          on GNU. NOT `%T` (filesystem type name).
#   - aod_template_write_version_file      Atomic writer for .aod/aod-kit-version.
#                                          Validates all 5 fields before commit.
#                                          Exit 3 on any field validation failure.
#   - aod_template_read_version_file       Sources + validates the version file;
#                                          exports AOD_VERSION_* vars. Exit 3 on
#                                          absent/malformed.
#
# All NEW code — sync-upstream.sh's cmd_setup is a git-remote flow, not fetch-to-temp.
# See contracts/library-api.md §template-git.sh for API details.
# Constitution §IV: use `stat -f %d` / `stat -c %d` (device number), NOT `%T`
# (filesystem type name) which would false-pass two distinct APFS volumes.
#
# Phase-2 bodies implemented in T015 (feature 129); version file I/O is T023/T024
# and retag detection body is T026 (all in Wave 3).
# =============================================================================

# Guard against double-sourcing.
if [ -n "${AOD_TEMPLATE_GIT_SH_SOURCED:-}" ]; then
  return 0
fi
readonly AOD_TEMPLATE_GIT_SH_SOURCED=1

# -----------------------------------------------------------------------------
# aod_template_fetch_upstream <url> <ref> <destdir>
# -----------------------------------------------------------------------------
# Fetch a specific upstream ref (tag or branch) into <destdir> via a shallow
# git clone. Enforces the URL scheme whitelist at fetch time:
#   - `https://`  (preferred, the primary supply-chain path)
#   - `file://`   (allowed so integration tests can use a local bare repo)
# Rejects `git@`, `git://`, `ssh://`, and other schemes.
#
# This is NEW code — sync-upstream.sh uses `git remote add upstream + git merge`
# which is an in-place flow, whereas /aod.update fetches to a disposable temp
# directory and never mutates the adopter's remotes or branches.
#
# Arguments:
#   $1 — upstream URL
#   $2 — ref (tag name, branch name, or commit-ish); empty string means HEAD
#        of the default branch
#   $3 — destination directory (must not already exist; will be created)
# Return:
#   0 on success
#   1 on invalid arguments
#   2 on unsupported URL scheme
#   9 on network/auth/clone failure
# -----------------------------------------------------------------------------
aod_template_fetch_upstream() {
    local url="${1:-}"
    local ref="${2:-}"
    local destdir="${3:-}"

    if [ -z "$url" ] || [ -z "$destdir" ]; then
        echo "[aod] ERROR: aod_template_fetch_upstream requires <url> and <destdir>" >&2
        return 1
    fi

    # Enforce URL scheme whitelist
    case "$url" in
        'https://'*|'file://'*) : ;;
        *)
            echo "[aod] ERROR: upstream URL must start with https:// or file:// (rejected: $url)" >&2
            return 2
            ;;
    esac

    if [ -e "$destdir" ]; then
        echo "[aod] ERROR: destination already exists: $destdir" >&2
        return 1
    fi

    # Ensure parent dir exists (git clone will create the leaf)
    local parent
    parent="$(dirname "$destdir")"
    if [ ! -d "$parent" ]; then
        echo "[aod] ERROR: destination parent directory does not exist: $parent" >&2
        return 1
    fi

    local clone_rc=0
    if [ -n "$ref" ]; then
        git clone --depth=1 --branch "$ref" --quiet "$url" "$destdir" 2>&1 || clone_rc=$?
    else
        git clone --depth=1 --quiet "$url" "$destdir" 2>&1 || clone_rc=$?
    fi

    if [ $clone_rc -ne 0 ]; then
        echo "[aod] ERROR: upstream fetch failed (exit $clone_rc) for url=$url ref=$ref" >&2
        # Clean up any partial checkout so callers can retry without conflict
        rm -rf "$destdir" 2>/dev/null || true
        return 9
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_compute_diff <tree_a> <tree_b>
# -----------------------------------------------------------------------------
# Emit a list of file-level differences between two working trees as
# `<status>\t<path>` pairs, one per line. Uses `git diff --no-index` which
# does NOT require either directory to be a git repo.
#
# Status codes emitted:
#   A — added (present in tree_b, absent in tree_a)
#   D — deleted (present in tree_a, absent in tree_b)
#   M — modified (present in both, differ in content)
#   R — renamed (if git detects one; rare with --no-index)
#
# git diff --no-index exits 0 on no-diff, 1 on diff-found, >1 on error.
#
# Arguments:
#   $1 — tree_a (reference / upstream)
#   $2 — tree_b (comparison / local)
# Output:
#   `<status>\t<path>` lines to stdout. Paths are printed relative to tree_b
#   where possible.
# Return:
#   0 on success (whether or not differences exist)
#   1 on argument or invocation error
# -----------------------------------------------------------------------------
aod_template_compute_diff() {
    local tree_a="${1:-}"
    local tree_b="${2:-}"

    if [ -z "$tree_a" ] || [ -z "$tree_b" ]; then
        echo "[aod] ERROR: aod_template_compute_diff requires <tree_a> <tree_b>" >&2
        return 1
    fi
    if [ ! -d "$tree_a" ]; then
        echo "[aod] ERROR: tree_a is not a directory: $tree_a" >&2
        return 1
    fi
    if [ ! -d "$tree_b" ]; then
        echo "[aod] ERROR: tree_b is not a directory: $tree_b" >&2
        return 1
    fi

    # git diff --no-index returns exit 0 (no-diff) or 1 (diff-found); both are
    # success for our purposes. Exit >=2 is a real error.
    local diff_out diff_rc=0
    diff_out="$(git diff --no-index --name-status -- "$tree_a" "$tree_b" 2>&1)" || diff_rc=$?

    if [ $diff_rc -gt 1 ]; then
        echo "[aod] ERROR: git diff failed (exit $diff_rc): $diff_out" >&2
        return 1
    fi

    if [ -n "$diff_out" ]; then
        printf '%s\n' "$diff_out"
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_detect_retag <url> <tag> <expected_sha> [--force-retag]
# -----------------------------------------------------------------------------
# Resolve <tag> in <url> via `git ls-remote`; compare to <expected_sha>.
# Retag detection is the supply-chain tripwire for FR-004 — a mismatch between
# the upstream's current tag SHA and our recorded SHA means the tag has been
# moved (commonly an attack vector for replacing "trusted" releases).
#
# Override mechanism:
#   - `FORCE_RETAG=1` environment variable
#   - `--force-retag` as a 4th positional argument
# Either will downgrade the mismatch from exit 7 to a warning + exit 0.
#
# Arguments:
#   $1 — url (https:// or file://; enforced by the fetch layer, not here — this
#        call uses `git ls-remote` which honors any scheme git supports)
#   $2 — tag (annotated or lightweight)
#   $3 — expected_sha (40-hex; must match what ls-remote resolves <tag> to)
#   $4 — optional override flag (`--force-retag`)
# Return:
#   0  — SHA matches, or SHA differs AND override engaged
#   7  — SHA mismatch (retag detected; no override)
#   9  — ls-remote failed (network, auth, URL unreachable, tag missing)
#   1  — argument error
# -----------------------------------------------------------------------------
aod_template_detect_retag() {
    local url="${1:-}"
    local tag="${2:-}"
    local expected_sha="${3:-}"
    local force_flag="${4:-}"

    if [ -z "$url" ] || [ -z "$tag" ] || [ -z "$expected_sha" ]; then
        echo "[aod] ERROR: aod_template_detect_retag requires <url> <tag> <expected_sha>" >&2
        return 1
    fi

    # Determine whether override is engaged
    local override=0
    if [ "${FORCE_RETAG:-0}" = "1" ] || [ "$force_flag" = "--force-retag" ]; then
        override=1
    fi

    # Resolve the tag via ls-remote. Output format:
    #   <sha>\trefs/tags/<tag>
    # or
    #   <sha>\trefs/tags/<tag>^{}    (for annotated tags — peeled entry)
    local ls_out ls_rc=0
    ls_out="$(git ls-remote "$url" "refs/tags/$tag" 2>&1)" || ls_rc=$?

    if [ $ls_rc -ne 0 ]; then
        echo "[aod] ERROR: could not resolve tag $tag at $url (git ls-remote exit $ls_rc)" >&2
        return 9
    fi

    if [ -z "$ls_out" ]; then
        echo "[aod] ERROR: tag $tag not found at $url" >&2
        return 9
    fi

    # Prefer the peeled entry (`refs/tags/<tag>^{}`) when present — that's the
    # commit an annotated tag points to. Fall back to the direct entry.
    local actual_sha=""
    # Peeled line (annotated tag)
    actual_sha="$(printf '%s\n' "$ls_out" | awk -v t="refs/tags/$tag^{}" '$2 == t { print $1; exit }')"
    if [ -z "$actual_sha" ]; then
        # Direct line (lightweight tag)
        actual_sha="$(printf '%s\n' "$ls_out" | awk -v t="refs/tags/$tag" '$2 == t { print $1; exit }')"
    fi

    if [ -z "$actual_sha" ]; then
        echo "[aod] ERROR: git ls-remote returned no SHA for tag $tag at $url" >&2
        return 9
    fi

    if [ "$actual_sha" = "$expected_sha" ]; then
        return 0
    fi

    # SHA mismatch — possible retag
    if [ $override -eq 1 ]; then
        echo "[aod] WARN: upstream tag $tag has been retagged: expected $expected_sha, got $actual_sha (override engaged)" >&2
        return 0
    fi

    echo "[aod] ERROR: upstream tag $tag has been retagged: expected $expected_sha, got $actual_sha" >&2
    echo "[aod] If this is intentional (e.g., upstream maintainer force-moved the tag), re-run with --force-retag." >&2
    return 7
}

# -----------------------------------------------------------------------------
# aod_template_fs_device <path>
# -----------------------------------------------------------------------------
# Emit the POSIX device number (filesystem identity) of <path>.
# Uses `stat -f %d` on BSD (macOS, FreeBSD) and `stat -c %d` on GNU (Linux).
#
# CRITICAL: this function MUST use `%d` (device number) and NOT `%T`
# (filesystem type name). Two distinct APFS volumes share the type name
# "apfs" but have different device numbers; `%T` would false-pass them as
# the same filesystem and break the atomic rename(2) guarantee relied on
# by ADR-001. See plan.md §Constitution Check Principle IV for rationale.
#
# Arguments:
#   $1 — path (must exist)
# Output:
#   Numeric device ID to stdout (one line, no trailing newline added
#   beyond what `echo` supplies).
# Return:
#   0 on success
#   1 on error (path missing, or neither stat flavor works)
# -----------------------------------------------------------------------------
aod_template_fs_device() {
    local path="${1:-}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: aod_template_fs_device requires <path>" >&2
        return 1
    fi
    if [ ! -e "$path" ]; then
        echo "[aod] ERROR: path does not exist: $path" >&2
        return 1
    fi

    # Detect OS flavor of stat. Prefer `uname` (portable) over trial-and-error.
    local uname_s=""
    uname_s="$(uname -s 2>/dev/null || echo '')"

    local device=""
    case "$uname_s" in
        Darwin|FreeBSD|NetBSD|OpenBSD|DragonFly)
            # BSD-style stat
            device="$(stat -f %d "$path" 2>/dev/null || true)"
            ;;
        Linux|GNU*|CYGWIN*|MINGW*|MSYS*)
            # GNU-style stat
            device="$(stat -c %d "$path" 2>/dev/null || true)"
            ;;
        *)
            # Unknown OS — try both, BSD first (most common non-Linux is macOS)
            device="$(stat -f %d "$path" 2>/dev/null || stat -c %d "$path" 2>/dev/null || true)"
            ;;
    esac

    if [ -z "$device" ]; then
        echo "[aod] ERROR: could not determine filesystem device for $path (neither BSD nor GNU stat worked)" >&2
        return 1
    fi

    # Must be numeric
    case "$device" in
        ''|*[!0-9-]*)
            echo "[aod] ERROR: stat returned non-numeric device id '$device' for $path" >&2
            return 1
            ;;
    esac

    printf '%s\n' "$device"
    return 0
}

# -----------------------------------------------------------------------------
# aod_template_write_version_file
#   <dest_path> <version> <sha> <updated_at> <upstream_url> <manifest_sha256>
# -----------------------------------------------------------------------------
# Atomic writer for `.aod/aod-kit-version` (contracts/version-schema.md).
# Validates EVERY field via regex before committing the .tmp → final rename.
# Any malformed field aborts the write with exit 3 and leaves the target file
# (if present) byte-identical.
#
# Atomicity pattern (see plan.md §C3 + .aod/scripts/bash/run-state.sh):
#   1. Write KV pairs to <dest_path>.tmp
#   2. Verify the .tmp file parses (belt & braces)
#   3. `mv <dest_path>.tmp <dest_path>`  (POSIX atomic rename)
#
# Field validation (contracts/version-schema.md §Write Protocol):
#   - version: any string (empty allowed — install may be off a non-tagged commit)
#   - sha: ^[0-9a-f]{40}$  (40-char lowercase hex)
#   - updated_at: ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$
#   - upstream_url: starts with `https://` (ssh/git@/http rejected)
#   - manifest_sha256: ^[0-9a-f]{64}$  (64-char lowercase hex)
#
# Same-filesystem pre-flight:
#   We compare the device of <dest_path>.tmp's parent to <dest_path>'s parent
#   using aod_template_fs_device. Since .tmp is colocated with the target,
#   this is effectively a sanity check — both paths MUST resolve to the same
#   device for `mv` to be atomic on POSIX. If the pre-flight returns a device
#   mismatch we halt (exit code 3 — same family as other validation failures).
#
# Return:
#   0  — success; .aod/aod-kit-version is at the new content
#   1  — argument error
#   3  — field validation failure OR same-fs pre-flight failure
# -----------------------------------------------------------------------------
aod_template_write_version_file() {
    if [ $# -lt 6 ]; then
        echo "[aod] ERROR: aod_template_write_version_file requires 6 arguments: <dest_path> <version> <sha> <updated_at> <upstream_url> <manifest_sha256>" >&2
        return 1
    fi

    local dest_path="$1"
    local version="$2"
    local sha="$3"
    local updated_at="$4"
    local upstream_url="$5"
    local manifest_sha256="$6"

    if [ -z "$dest_path" ]; then
        echo "[aod] ERROR: aod_template_write_version_file: dest_path must not be empty" >&2
        return 1
    fi

    # ---- field validation (fail-fast BEFORE any .tmp creation) ----

    # sha: 40-char lowercase hex
    case "$sha" in
        ''|*[!0-9a-f]*)
            echo "[aod] ERROR: invalid sha (must be 40-char lowercase hex): $sha" >&2
            return 3
            ;;
    esac
    # Length check (bash 3.2 compatible: ${#var})
    if [ ${#sha} -ne 40 ]; then
        echo "[aod] ERROR: invalid sha length (expected 40, got ${#sha}): $sha" >&2
        return 3
    fi

    # manifest_sha256: 64-char lowercase hex
    case "$manifest_sha256" in
        ''|*[!0-9a-f]*)
            echo "[aod] ERROR: invalid manifest_sha256 (must be 64-char lowercase hex): $manifest_sha256" >&2
            return 3
            ;;
    esac
    if [ ${#manifest_sha256} -ne 64 ]; then
        echo "[aod] ERROR: invalid manifest_sha256 length (expected 64, got ${#manifest_sha256}): $manifest_sha256" >&2
        return 3
    fi

    # updated_at: ISO 8601 UTC with trailing Z.
    # Format: YYYY-MM-DDTHH:MM:SSZ  (19 chars body + Z = 20 total)
    if [ -z "$updated_at" ]; then
        echo "[aod] ERROR: updated_at must not be empty" >&2
        return 3
    fi
    # Bash 3.2 regex matching via [[ =~ ]] (available since bash 3.0).
    if ! [[ "$updated_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
        echo "[aod] ERROR: invalid updated_at (expected YYYY-MM-DDTHH:MM:SSZ): $updated_at" >&2
        return 3
    fi

    # upstream_url: must start with https://
    # Exception: file:// is accepted for local-fixture integration tests only
    # (matches aod_template_fetch_upstream's documented scheme whitelist).
    # http://, ssh://, git@ are rejected to preserve the supply-chain posture.
    if [ -z "$upstream_url" ]; then
        echo "[aod] ERROR: upstream_url must not be empty" >&2
        return 3
    fi
    case "$upstream_url" in
        'https://'*|'file://'*) : ;;
        *)
            echo "[aod] ERROR: upstream_url must start with https:// (got: $upstream_url)" >&2
            return 3
            ;;
    esac

    # version: no format constraint — may be empty string or any git tag name.
    # We validate only by forbidding newlines (which would corrupt the KV file).
    case "$version" in
        *$'\n'*)
            echo "[aod] ERROR: version must not contain newlines" >&2
            return 3
            ;;
    esac

    # ---- parent directory must exist ----
    local parent_dir
    parent_dir="$(dirname "$dest_path")"
    if [ ! -d "$parent_dir" ]; then
        echo "[aod] ERROR: parent directory does not exist: $parent_dir" >&2
        return 1
    fi

    local tmp_path="${dest_path}.tmp"

    # ---- write .tmp ----
    # Use a single printf invocation for atomicity-of-write within the tmp file.
    # Order the fields as per the canonical example in version-schema.md.
    if ! printf 'version=%s\nsha=%s\nupdated_at=%s\nupstream_url=%s\nmanifest_sha256=%s\n' \
            "$version" "$sha" "$updated_at" "$upstream_url" "$manifest_sha256" \
            > "$tmp_path" 2>/dev/null; then
        echo "[aod] ERROR: could not write .tmp version file: $tmp_path" >&2
        rm -f "$tmp_path" 2>/dev/null || true
        return 1
    fi

    # ---- same-filesystem pre-flight ----
    # Both tmp and dest live in the same parent dir, so their devices should
    # match. If this check somehow fails, the mv below would NOT be atomic —
    # so we bail before committing.
    local tmp_dev parent_dev
    tmp_dev="$(aod_template_fs_device "$tmp_path" 2>/dev/null || echo '')"
    parent_dev="$(aod_template_fs_device "$parent_dir" 2>/dev/null || echo '')"
    if [ -z "$tmp_dev" ] || [ -z "$parent_dev" ] || [ "$tmp_dev" != "$parent_dev" ]; then
        echo "[aod] ERROR: same-filesystem pre-flight failed for $tmp_path → $dest_path (devices: tmp=$tmp_dev parent=$parent_dev)" >&2
        rm -f "$tmp_path" 2>/dev/null || true
        return 3
    fi

    # ---- belt-and-braces: re-parse the tmp file ----
    # Guard against the shell-injection-of-values case by checking that the
    # round-tripped values match what we just wrote. Sourcing in a subshell
    # avoids polluting the caller's scope (SC2030/SC2031 info warnings about
    # the subshell-local vars are intentional — we specifically WANT the
    # variables to be isolated inside the $( ... ) subshell).
    local roundtrip_output rc
    # shellcheck disable=SC2030,SC2031
    roundtrip_output="$(
        set +e
        set +u
        version=''
        sha=''
        updated_at=''
        upstream_url=''
        manifest_sha256=''
        # shellcheck disable=SC1090
        source "$tmp_path" 2>/dev/null
        printf '%s|%s|%s|%s|%s' \
            "$version" "$sha" "$updated_at" "$upstream_url" "$manifest_sha256"
    )"
    rc=$?
    # The caller-scope $version/etc. here refer to the positional parameters
    # captured at the top of this function, NOT the subshell-local blanked
    # copies above — suppress SC2031 for the intentional reference.
    # shellcheck disable=SC2031
    local expected="${version}|${sha}|${updated_at}|${upstream_url}|${manifest_sha256}"
    if [ $rc -ne 0 ] || [ "$roundtrip_output" != "$expected" ]; then
        echo "[aod] ERROR: round-trip validation failed for $tmp_path" >&2
        rm -f "$tmp_path" 2>/dev/null || true
        return 3
    fi

    # ---- atomic commit ----
    if ! mv "$tmp_path" "$dest_path" 2>/dev/null; then
        echo "[aod] ERROR: atomic rename failed: $tmp_path → $dest_path" >&2
        rm -f "$tmp_path" 2>/dev/null || true
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# aod_template_read_version_file <path>
# -----------------------------------------------------------------------------
# Source <path>, validate all 5 required fields, and export them as
# AOD_VERSION_* shell variables in the caller's scope.
#
# Exports:
#   AOD_VERSION_VERSION
#   AOD_VERSION_SHA
#   AOD_VERSION_UPDATED_AT
#   AOD_VERSION_UPSTREAM_URL
#   AOD_VERSION_MANIFEST_SHA256
#
# Return:
#   0 — file read, all 5 fields present + valid, AOD_VERSION_* exported
#   3 — absent file OR malformed content (ANY field invalid)
# -----------------------------------------------------------------------------
aod_template_read_version_file() {
    local path="${1:-}"

    if [ -z "$path" ]; then
        echo "[aod] ERROR: aod_template_read_version_file requires <path>" >&2
        return 3
    fi

    if [ ! -f "$path" ]; then
        echo "[aod] ERROR: version file does not exist: $path" >&2
        return 3
    fi

    # Source in the caller's scope, but reset the 5 names first so a
    # malformed file can't leak stale values from the environment.
    local version='' sha='' updated_at='' upstream_url='' manifest_sha256=''
    # shellcheck disable=SC1090
    source "$path" || {
        echo "[aod] ERROR: failed to source version file: $path" >&2
        return 3
    }

    # Validate each field with the same regexes as the writer (keeps the
    # two functions symmetric — what we accept on write we accept on read).
    if [ -z "$sha" ]; then
        echo "[aod] ERROR: version file missing or empty 'sha' field: $path" >&2
        return 3
    fi
    case "$sha" in
        ''|*[!0-9a-f]*)
            echo "[aod] ERROR: version file has invalid sha: $sha" >&2
            return 3
            ;;
    esac
    if [ ${#sha} -ne 40 ]; then
        echo "[aod] ERROR: version file sha has wrong length (expected 40): $sha" >&2
        return 3
    fi

    if [ -z "$manifest_sha256" ]; then
        echo "[aod] ERROR: version file missing or empty 'manifest_sha256' field: $path" >&2
        return 3
    fi
    case "$manifest_sha256" in
        ''|*[!0-9a-f]*)
            echo "[aod] ERROR: version file has invalid manifest_sha256: $manifest_sha256" >&2
            return 3
            ;;
    esac
    if [ ${#manifest_sha256} -ne 64 ]; then
        echo "[aod] ERROR: version file manifest_sha256 has wrong length (expected 64): $manifest_sha256" >&2
        return 3
    fi

    if [ -z "$updated_at" ]; then
        echo "[aod] ERROR: version file missing or empty 'updated_at' field: $path" >&2
        return 3
    fi
    if ! [[ "$updated_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
        echo "[aod] ERROR: version file has invalid updated_at: $updated_at" >&2
        return 3
    fi

    if [ -z "$upstream_url" ]; then
        echo "[aod] ERROR: version file missing or empty 'upstream_url' field: $path" >&2
        return 3
    fi
    # Accept https:// (production) and file:// (local-fixture integration tests).
    # Matches aod_template_fetch_upstream's documented scheme whitelist.
    case "$upstream_url" in
        'https://'*|'file://'*) : ;;
        *)
            echo "[aod] ERROR: version file has invalid upstream_url (must start with https://): $upstream_url" >&2
            return 3
            ;;
    esac

    # version may be empty; no further validation.

    # Export under a namespaced prefix so the caller's own $version etc. vars
    # are not clobbered.
    AOD_VERSION_VERSION="$version"
    AOD_VERSION_SHA="$sha"
    AOD_VERSION_UPDATED_AT="$updated_at"
    AOD_VERSION_UPSTREAM_URL="$upstream_url"
    AOD_VERSION_MANIFEST_SHA256="$manifest_sha256"
    export AOD_VERSION_VERSION AOD_VERSION_SHA AOD_VERSION_UPDATED_AT \
           AOD_VERSION_UPSTREAM_URL AOD_VERSION_MANIFEST_SHA256

    return 0
}
