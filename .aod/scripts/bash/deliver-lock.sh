# LIBRARY — source before calling functions
# Feature 139 delivery concurrency lock + crash-recovery sentinel.
# Prevents concurrent /aod.deliver runs on the same feature and lets the next
# invocation detect abandoned auto-fix-loop state from a crashed prior run.
#
# Canonical contracts:
#   specs/139-delivery-verified-not-documented/data-model.md §10 Delivery Lock
#   specs/139-delivery-verified-not-documented/data-model.md §11 Crash-Recovery Sentinel
#   specs/139-delivery-verified-not-documented/plan.md §Research R-7 Lockfile Stale Detection
#   specs/139-delivery-verified-not-documented/spec.md US-7 (FR-026..FR-031)
#
# Public functions:
#   acquire_lock              — atomically create .aod/locks/deliver-{NNN}.lock; returns 0|11|1
#   release_lock              — remove lockfile (idempotent); returns 0
#   check_stale               — inspect lock without modifying; returns 0|11|2
#   detect_abandoned_sentinel — flag sentinel with no active lock; returns 0|12
#   write_sentinel            — atomic heartbeat write to .aod/state/deliver-{NNN}.state.json
#   write_heartbeat_sentinel  — US-8 auto-fix loop heartbeat; called before every heal commit
#   remove_sentinel           — remove sentinel (idempotent); returns 0
#
# Internal helpers:
#   _atomic_write_sentinel    — write-then-rename for sentinel paths (T043; see data-model.md §11)
#
# Exit/return codes (canonical per data-model.md §Exit Code Taxonomy):
#   0   fresh-acquire OK / success / no contention
#   1   runtime error (jq missing, write failure, etc.)
#   2   stale lock — reap allowed (internal to check_stale)
#   11  concurrent invocation (live or recent-dead holder)
#   12  abandoned heal (sentinel present with no active lock)
#
# Bash 3.2 compatible (macOS): no `declare -A`, no `${var,,}`, no `readarray`,
# no `|&`, no `yq`. Portable `stat` via dual-OS detection (-f %m | -c %Y).
# Library never calls `exit` — caller owns process lifecycle.

# Directory roots. Caller runs from repo root; override via env for tests.
AOD_LOCK_DIR="${AOD_LOCK_DIR:-.aod/locks}"
AOD_STATE_DIR="${AOD_STATE_DIR:-.aod/state}"

# Default heal budget (seconds) used when caller passes empty/zero — matches
# plan.md §Research R-7 safety envelope (stale threshold = 2 × budget).
AOD_DEFAULT_HEAL_BUDGET_SECONDS="${AOD_DEFAULT_HEAL_BUDGET_SECONDS:-3600}"

# Extract the NNN prefix (digits before the first hyphen) from a feature id.
# "139-delivery-verified-not-documented" -> "139".
_lock_feature_nnn() {
    local feature="${1:-}"
    printf '%s' "${feature%%-*}"
}

# Build the lockfile path for a feature.
_lock_path() {
    local feature="${1:-}"
    local nnn
    nnn=$(_lock_feature_nnn "$feature")
    printf '%s/deliver-%s.lock' "$AOD_LOCK_DIR" "$nnn"
}

# Build the sentinel path for a feature.
_sentinel_path() {
    local feature="${1:-}"
    local nnn
    nnn=$(_lock_feature_nnn "$feature")
    printf '%s/deliver-%s.state.json' "$AOD_STATE_DIR" "$nnn"
}

# Atomic write-then-rename for sentinel paths (T043).
#
# Pattern: write full JSON to `${sentinel_path}.tmp`, then `mv` over the
# final path. On POSIX, `mv` within the same filesystem is atomic — a
# concurrent reader sees either the prior sentinel or the new one, never
# a half-written file. Contrast with lockfile acquisition, which uses
# `set -o noclobber` for exclusive-create semantics; both mechanisms
# serve different goals (noclobber = mutual-exclusion, rename = torn-read
# prevention). See data-model.md §11 for the full rationale.
#
# Callers must have already populated the `.tmp` file; this helper only
# performs the atomic publish step. Returns 0 on success, 1 on failure.
#
# Args:
#   $1 feature  — used to derive the sentinel path (consistency with other helpers)
#   $2 tmp_path — path to the pre-written temp file (absolute or relative)
_atomic_write_sentinel() {
    local feature="${1:-}"
    local tmp_path="${2:-}"
    local sentinel
    sentinel=$(_sentinel_path "$feature")

    if [ ! -e "$tmp_path" ]; then
        echo "_atomic_write_sentinel: temp file missing: $tmp_path" >&2
        return 1
    fi

    if ! mv "$tmp_path" "$sentinel" 2>/dev/null; then
        echo "_atomic_write_sentinel: cannot publish $sentinel" >&2
        rm -f "$tmp_path" 2>/dev/null
        return 1
    fi

    return 0
}

# Portable mtime (epoch seconds) for a file. Echoes the epoch int on success,
# empty string on failure. macOS uses `stat -f %m`, Linux uses `stat -c %Y`.
_lock_mtime_epoch() {
    local path="${1:-}"
    local mtime
    mtime=$(stat -f %m "$path" 2>/dev/null)
    if [ -z "$mtime" ]; then
        mtime=$(stat -c %Y "$path" 2>/dev/null)
    fi
    printf '%s' "$mtime"
}

# Current epoch seconds (portable via `date -u +%s`).
_lock_now_epoch() {
    date -u +%s
}

# Inspect a lockfile for staleness. Pure read; does NOT modify state.
# Args:
#   $1 feature
#   $2 heal_budget_seconds (integer; 0/empty → AOD_DEFAULT_HEAL_BUDGET_SECONDS)
# Returns:
#   0  no lock present (fresh-acquire OK)
#   11 lock held by live PID OR dead PID + young lock (recent crash; do not reap)
#   2  lock held by dead PID AND old lock (mtime age > 2 × budget; reap allowed)
#   1  runtime error (unreadable lockfile, jq missing, etc.)
check_stale() {
    local feature="${1:-}"
    local budget="${2:-}"
    local lockfile
    lockfile=$(_lock_path "$feature")

    if [ ! -e "$lockfile" ]; then
        return 0
    fi

    if ! command -v jq >/dev/null 2>&1; then
        echo "check_stale: jq not found on PATH" >&2
        return 1
    fi

    # Normalize budget; any non-positive value falls back to default.
    if [ -z "$budget" ] || [ "$budget" -le 0 ] 2>/dev/null; then
        budget="$AOD_DEFAULT_HEAL_BUDGET_SECONDS"
    fi

    # Read PID; tolerate empty/partial file (readers must be defensive per
    # data-model.md §10 — writer creates visible file only after content fill).
    local pid
    pid=$(jq -r '.pid // empty' "$lockfile" 2>/dev/null)

    if [ -z "$pid" ]; then
        # Content not yet written or malformed. Treat as concurrent — the writer
        # is either mid-acquire or corrupted; bias toward safety (no reap).
        return 11
    fi

    if kill -0 "$pid" 2>/dev/null; then
        # Live holder — concurrent invocation.
        return 11
    fi

    # Dead PID; decide by lockfile age vs. 2 × budget.
    local mtime now age threshold
    mtime=$(_lock_mtime_epoch "$lockfile")
    if [ -z "$mtime" ]; then
        echo "check_stale: cannot stat $lockfile" >&2
        return 1
    fi
    now=$(_lock_now_epoch)
    age=$(( now - mtime ))
    threshold=$(( budget * 2 ))

    if [ "$age" -gt "$threshold" ]; then
        # Old enough to safely reap.
        return 2
    fi

    # Dead PID but young lock — a recent crash. Do NOT reap blindly; force the
    # caller to abort so a human can inspect.
    return 11
}

# Acquire the delivery lock atomically. Writes {pid, start_timestamp,
# heal_budget_seconds} JSON to .aod/locks/deliver-{NNN}.lock.
#
# Atomicity: uses `set -o noclobber` to reserve the target path, then writes
# full JSON to a `.tmp` sibling and renames over the reserved path. The visible
# lockfile is therefore always either (a) a zero-byte reservation (transient,
# microseconds) or (b) the fully-formed final JSON. Readers that see the
# reservation tolerate empty `.pid` per check_stale (returns 11 — bias safe).
#
# Args:
#   $1 feature                 e.g. "139-delivery-verified-not-documented"
#   $2 heal_budget_seconds     integer; empty/0 → AOD_DEFAULT_HEAL_BUDGET_SECONDS
# Returns:
#   0  acquired (fresh or reaped stale)
#   11 concurrent invocation (live or recent-dead holder)
#   1  runtime error
acquire_lock() {
    local feature="${1:-}"
    local budget="${2:-}"

    if [ -z "$feature" ]; then
        echo "acquire_lock: feature argument required" >&2
        return 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        echo "acquire_lock: jq not found on PATH" >&2
        return 1
    fi

    if [ -z "$budget" ] || [ "$budget" -le 0 ] 2>/dev/null; then
        budget="$AOD_DEFAULT_HEAL_BUDGET_SECONDS"
    fi

    local lockfile
    lockfile=$(_lock_path "$feature")

    if ! mkdir -p "$AOD_LOCK_DIR" 2>/dev/null; then
        echo "acquire_lock: cannot create $AOD_LOCK_DIR" >&2
        return 1
    fi

    # Attempt atomic create via noclobber. Subshell scopes the option so the
    # caller's shell settings are untouched.
    local acquired=0
    ( set -o noclobber; : > "$lockfile" ) 2>/dev/null && acquired=1

    if [ "$acquired" -eq 0 ]; then
        # Path exists — decide stale vs. concurrent.
        local stale_rc
        check_stale "$feature" "$budget"
        stale_rc=$?
        case "$stale_rc" in
            11) return 11 ;;  # live or recent-dead holder
            2)
                # Old stale lock — reap and retry once.
                rm -f "$lockfile" 2>/dev/null
                ( set -o noclobber; : > "$lockfile" ) 2>/dev/null && acquired=1
                if [ "$acquired" -eq 0 ]; then
                    # Someone else won the reap race — treat as concurrent.
                    return 11
                fi
                ;;
            1)  return 1 ;;
            *)  return 1 ;;
        esac
    fi

    # Lockfile path reserved. Build JSON into .tmp then rename over the
    # reservation to publish atomically.
    local tmp="${lockfile}.tmp"
    local pid=$$
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if ! jq -n \
        --argjson pid "$pid" \
        --arg ts "$timestamp" \
        --argjson budget "$budget" \
        '{pid: $pid, start_timestamp: $ts, heal_budget_seconds: $budget}' \
        > "$tmp" 2>/dev/null; then
        echo "acquire_lock: jq failed to build lock JSON" >&2
        rm -f "$tmp" "$lockfile" 2>/dev/null
        return 1
    fi

    if ! mv "$tmp" "$lockfile" 2>/dev/null; then
        echo "acquire_lock: cannot publish $lockfile" >&2
        rm -f "$tmp" "$lockfile" 2>/dev/null
        return 1
    fi

    return 0
}

# Release the delivery lock. Best-effort; idempotent.
# Args:
#   $1 feature
# Returns:
#   0 (always)
release_lock() {
    local feature="${1:-}"
    local lockfile
    lockfile=$(_lock_path "$feature")
    rm -f "$lockfile" 2>/dev/null
    return 0
}

# Detect an abandoned heal: sentinel present AND no active lock.
# Concurrent case (sentinel + live lock) defers to the lock — the current
# invocation owns the state, so sentinel presence is expected.
#
# Args:
#   $1 feature
# Returns:
#   0  no sentinel, OR sentinel + active lock (concurrent takes precedence)
#   12 abandoned heal detected; multi-line cleanup prompt written to stdout
detect_abandoned_sentinel() {
    local feature="${1:-}"
    local sentinel lockfile
    sentinel=$(_sentinel_path "$feature")
    lockfile=$(_lock_path "$feature")

    if [ ! -e "$sentinel" ]; then
        return 0
    fi

    # If a lockfile exists, defer to it. The current run legitimately owns the
    # sentinel mid-loop; caller's lock check (acquire_lock / check_stale) will
    # surface any concurrency problem via exit 11.
    if [ -e "$lockfile" ]; then
        return 0
    fi

    # Sentinel alone: describe the abandoned state and recovery commands.
    local nnn
    nnn=$(_lock_feature_nnn "$feature")

    local phase="unknown"
    local attempt="unknown"
    local last_commit="unknown"
    local last_heartbeat="unknown"

    if command -v jq >/dev/null 2>&1; then
        local v
        v=$(jq -r '.phase // "unknown"' "$sentinel" 2>/dev/null); [ -n "$v" ] && phase="$v"
        v=$(jq -r '.attempt // "unknown"' "$sentinel" 2>/dev/null); [ -n "$v" ] && attempt="$v"
        v=$(jq -r '.last_commit_sha // "unknown"' "$sentinel" 2>/dev/null); [ -n "$v" ] && last_commit="$v"
        v=$(jq -r '.last_heartbeat // "unknown"' "$sentinel" 2>/dev/null); [ -n "$v" ] && last_heartbeat="$v"
    fi

    echo "Abandoned heal detected for feature ${feature}."
    echo "  Phase:          ${phase}"
    echo "  Last attempt:   ${attempt}"
    echo "  Last commit:    ${last_commit}"
    echo "  Last heartbeat: ${last_heartbeat}"
    echo ""
    echo "A prior /aod.deliver invocation crashed mid-auto-fix-loop. Manual"
    echo "cleanup is required before the next run can proceed. Inspect the"
    echo "branch for unpushed heal commits, then clear the state files:"
    echo ""
    echo "  rm ${sentinel}"
    echo "  rm ${lockfile}  # if it still exists"
    echo ""
    echo "After cleanup, re-run /aod.deliver. See spec.md US-7 and plan.md"
    echo "Research R-3 for the abandoned-heal recovery policy."

    return 12
}

# Write (or overwrite) the crash-recovery sentinel as an atomic heartbeat.
# Caller invokes before every auto-fix-loop commit (FR-029). Writes
# {phase, attempt, last_commit_sha, last_heartbeat} JSON to
# .aod/state/deliver-{NNN}.state.json via write-then-rename (T043).
#
# Args:
#   $1 feature
#   $2 phase             e.g. "auto_fix_loop"
#   $3 attempt           integer
#   $4 last_commit_sha   full or short SHA
# Returns:
#   0 on success
#   1 on runtime error (mkdir/jq/mv failure)
write_sentinel() {
    local feature="${1:-}"
    local phase="${2:-}"
    local attempt="${3:-}"
    local last_commit_sha="${4:-}"

    if [ -z "$feature" ]; then
        echo "write_sentinel: feature argument required" >&2
        return 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        echo "write_sentinel: jq not found on PATH" >&2
        return 1
    fi

    if ! mkdir -p "$AOD_STATE_DIR" 2>/dev/null; then
        echo "write_sentinel: cannot create $AOD_STATE_DIR" >&2
        return 1
    fi

    local sentinel
    sentinel=$(_sentinel_path "$feature")
    local tmp="${sentinel}.tmp"

    local heartbeat
    heartbeat=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Attempt serialized as number when integer, else string fallback.
    local attempt_json
    if [ -n "$attempt" ] && [ "$attempt" -eq "$attempt" ] 2>/dev/null; then
        attempt_json="$attempt"
    else
        # Let jq quote it as a string via --arg.
        attempt_json=""
    fi

    if [ -n "$attempt_json" ]; then
        if ! jq -n \
            --arg phase "$phase" \
            --argjson attempt "$attempt_json" \
            --arg sha "$last_commit_sha" \
            --arg ts "$heartbeat" \
            '{phase: $phase, attempt: $attempt, last_commit_sha: $sha, last_heartbeat: $ts}' \
            > "$tmp" 2>/dev/null; then
            echo "write_sentinel: jq failed to build sentinel JSON" >&2
            rm -f "$tmp" 2>/dev/null
            return 1
        fi
    else
        if ! jq -n \
            --arg phase "$phase" \
            --arg attempt "${attempt:-}" \
            --arg sha "$last_commit_sha" \
            --arg ts "$heartbeat" \
            '{phase: $phase, attempt: $attempt, last_commit_sha: $sha, last_heartbeat: $ts}' \
            > "$tmp" 2>/dev/null; then
            echo "write_sentinel: jq failed to build sentinel JSON" >&2
            rm -f "$tmp" 2>/dev/null
            return 1
        fi
    fi

    # Publish atomically via write-then-rename (T043 helper).
    _atomic_write_sentinel "$feature" "$tmp" || return 1

    return 0
}

# Write the US-8 auto-fix-loop heartbeat sentinel (T044).
#
# Called by the auto-fix loop (SKILL.md Step 9c.5) before every heal commit
# to satisfy FR-029. The sentinel's mtime is refreshed on every write, so an
# actively-running heal loop keeps its sentinel "young" relative to the stale
# threshold used by check_stale (2 × heal_budget_seconds). If the loop crashes,
# the sentinel stops refreshing and detect_abandoned_sentinel will surface it
# on the next /aod.deliver invocation (exit 12).
#
# Writes atomic via _atomic_write_sentinel (see data-model.md §11 for the
# write-then-rename rationale).
#
# Schema (published JSON):
#   schema_version: int  — currently 1
#   feature:        str  — NNN prefix only (e.g. "139")
#   pid:            int  — current process ID ($$)
#   last_heartbeat: str  — ISO-8601 UTC (Z suffix)
#   attempt:        int  — current 1-indexed attempt number
#   max_attempts:   int  — configured ceiling from .aod/config.json heal_attempts
#   stage:          str  — fixed literal "auto_fix_attempt"
#
# Args:
#   $1 feature          — full feature id or NNN prefix
#   $2 attempt_number   — integer ≥ 1
#   $3 max_attempts     — integer ≥ 1
# Returns:
#   0 on success
#   1 on runtime error (missing arg, jq missing, mkdir/jq/mv failure)
write_heartbeat_sentinel() {
    local feature="${1:-}"
    local attempt_number="${2:-}"
    local max_attempts="${3:-}"

    if [ -z "$feature" ]; then
        echo "write_heartbeat_sentinel: feature argument required" >&2
        return 1
    fi

    if [ -z "$attempt_number" ] || ! [ "$attempt_number" -eq "$attempt_number" ] 2>/dev/null; then
        echo "write_heartbeat_sentinel: attempt_number must be integer (got: '${attempt_number}')" >&2
        return 1
    fi

    if [ -z "$max_attempts" ] || ! [ "$max_attempts" -eq "$max_attempts" ] 2>/dev/null; then
        echo "write_heartbeat_sentinel: max_attempts must be integer (got: '${max_attempts}')" >&2
        return 1
    fi

    if ! command -v jq >/dev/null 2>&1; then
        echo "write_heartbeat_sentinel: jq not found on PATH" >&2
        return 1
    fi

    if ! mkdir -p "$AOD_STATE_DIR" 2>/dev/null; then
        echo "write_heartbeat_sentinel: cannot create $AOD_STATE_DIR" >&2
        return 1
    fi

    local sentinel
    sentinel=$(_sentinel_path "$feature")
    local tmp="${sentinel}.tmp"

    local nnn
    nnn=$(_lock_feature_nnn "$feature")

    local heartbeat
    heartbeat=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if ! jq -n \
        --argjson schema_version 1 \
        --arg feature "$nnn" \
        --argjson pid "$$" \
        --arg ts "$heartbeat" \
        --argjson attempt "$attempt_number" \
        --argjson max_attempts "$max_attempts" \
        --arg stage "auto_fix_attempt" \
        '{schema_version: $schema_version, feature: $feature, pid: $pid, last_heartbeat: $ts, attempt: $attempt, max_attempts: $max_attempts, stage: $stage}' \
        > "$tmp" 2>/dev/null; then
        echo "write_heartbeat_sentinel: jq failed to build sentinel JSON" >&2
        rm -f "$tmp" 2>/dev/null
        return 1
    fi

    # Publish atomically via write-then-rename (T043 helper).
    _atomic_write_sentinel "$feature" "$tmp" || return 1

    return 0
}

# Remove the crash-recovery sentinel. Best-effort; idempotent.
# Called on clean exit (Step 11) per data-model.md §11 lifecycle.
# Args:
#   $1 feature
# Returns:
#   0 (always)
remove_sentinel() {
    local feature="${1:-}"
    local sentinel
    sentinel=$(_sentinel_path "$feature")
    rm -f "$sentinel" 2>/dev/null
    return 0
}
