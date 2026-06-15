# Delivery Lock: Step 0.5 (Acquire) + Step 14 (Release)

This reference is loaded on every `/aod.deliver` run — once at Step 0.5 to acquire the lock, and once at Step 14 to release it.

**CRITICAL INVARIANT**: All `acquire_lock`, `release_lock`, and `trap … EXIT` commands in this reference MUST execute as **top-level parent-shell commands** in the agent's execution environment. They MUST NOT be wrapped in a subshell or `bash -c`. A leaked lock blocks ALL future deliveries on this feature until manually cleared.

**Re-derivation note**: `FEATURE` and `HEAL_BUDGET` are re-derived inside each step below using `git branch --show-current` and `jq` respectively. These values are NOT assumed to persist across separate tool calls — each step computes them fresh from the live environment.

---

## Step 0.5: Acquire Delivery Lock (US-7, Feature 139 — FR-026..FR-030)

Before any gate logic runs, acquire an exclusive delivery lock to prevent concurrent `/aod.deliver` invocations on the same feature from corrupting branch state (e.g., interleaved auto-fix commits, duplicate heal-PRs, or double-appended audit lines). Also detect abandoned crash-recovery sentinels from prior crashed invocations.

**Why this runs after Step 0** (not before): Flag parsing at Step 0 is pure argument validation — it does not touch disk or mutate repository state. The audit log write at Step 0g IS a disk mutation, so in strict correctness terms the lock would ideally precede it. However, the audit log is append-only, line-atomic under concurrent writes (per `contracts/audit-log.md`), and non-gating; concurrent appends are safe. The lock's job is to protect the stateful auto-fix/commit logic from Step 9 onward, and the lock is acquired well before that.

**1. Source the delivery lock library**:

```bash
source .aod/scripts/bash/deliver-lock.sh
```

The library exposes `acquire_lock`, `release_lock`, `check_stale`, `detect_abandoned_sentinel`, and `write_heartbeat_sentinel`. See `specs/139-delivery-verified-not-documented/data-model.md §10 Delivery Lock` and `§11 Crash-Recovery Sentinel` for the canonical contracts.

**2. Resolve feature identifier and heal budget**:

```bash
FEATURE=$(git branch --show-current 2>/dev/null)

if [ -z "$FEATURE" ]; then
  echo "Error: /aod.deliver must run on a feature branch (git branch --show-current returned empty)" >&2
  exit 1
fi

# Heal budget drives the stale-lock threshold (2× budget) used by check_stale.
# Falls back to 300s (5 min) when .aod/config.json is absent or the key is unset,
# matching the default in .aod/config.json.example.
HEAL_BUDGET=$(jq -r '.deliver.heal_budget_seconds // 300' .aod/config.json 2>/dev/null || echo "300")
```

**3. Acquire the lock**:

```bash
acquire_lock "$FEATURE" "$HEAL_BUDGET"
ACQUIRE_RC=$?
```

Branch on the return code (taxonomy from `deliver-lock.sh` header):

- **Exit 0 (acquired)**: Lock file `.aod/locks/deliver-$NNN.lock` now contains `{pid: $$, start_timestamp, heal_budget_seconds}` JSON, published atomically via write-then-rename. Proceed to step 4.

- **Exit 11 (concurrent invocation)**: Another `/aod.deliver` is active for this feature (live PID holder OR dead PID with young lock — recent crash, do-not-reap). Emit error and abort:

  ```bash
  LOCKFILE=".aod/locks/deliver-${FEATURE%%-*}.lock"
  HOLDER_PID=$(jq -r '.pid // "unknown"' "$LOCKFILE" 2>/dev/null)
  HOLDER_TS=$(jq -r '.start_timestamp // "unknown"' "$LOCKFILE" 2>/dev/null)
  echo "Another /aod.deliver invocation is active (PID ${HOLDER_PID}, started ${HOLDER_TS})." >&2
  echo "Retry once the holder completes, or wait for the 2× heal_budget stale threshold (${HEAL_BUDGET}s × 2) to elapse before the lock can be reaped." >&2
  exit 11
  ```

- **Exit 1 (runtime error)**: jq missing, mkdir failure, or atomic-create race failure. Emit error and abort with exit 1 (not 11 — this is a runtime bug, not a concurrency condition).

**4. Detect abandoned crash-recovery sentinel** (FR-030):

```bash
detect_abandoned_sentinel "$FEATURE"
SENTINEL_RC=$?
```

- **Exit 0 (no sentinel OR sentinel + active lock)**: Clean. Proceed to Step 1.
- **Exit 12 (abandoned heal detected)**: A prior invocation crashed mid-auto-fix-loop leaving a state sentinel behind, and no active lock exists to explain it. The library already emitted a multi-line cleanup prompt to stdout naming the partial state (phase, attempt, last_commit, last_heartbeat). Release the lock we just acquired (so the cleanup can remove it too) and abort:

  ```bash
  release_lock "$FEATURE"
  # detect_abandoned_sentinel already wrote the cleanup prompt to stdout.
  # Per data-model §11 lifecycle: operator inspects branch, removes sentinel,
  # re-invokes /aod.deliver.
  exit 12
  ```

  Do NOT automatically remove the sentinel — the policy (per spec.md US-7 AC-3 and assumptions) is "halt with manual-cleanup prompt"; auto-recovery from partial state is deferred to a future PRD.

**5. Register lock release on clean exit**:

Step 14 (in this same reference file) is responsible for the symmetric `release_lock` call on every clean exit path. Additionally, if bash-level trap handling is available in the execution environment, wrap the skill in:

```bash
trap 'release_lock "$FEATURE" 2>/dev/null' EXIT
```

For Markdown-described skill execution (the Claude Code interpreter walks the steps; no long-lived shell wrapping), the invariant is documented on Step 14: "Step 14 MUST run before any `exit` from Steps 1-13 on clean paths. On crash/SIGKILL, the sentinel-plus-no-lock state will trigger exit 12 on the next invocation."

**Output state after Step 0.5**:

| Variable | Purpose | Used In |
|----------|---------|---------|
| `FEATURE` | Feature branch name (e.g., `139-delivery-verified-not-documented`) | All downstream steps |
| `HEAL_BUDGET` | Configured heal-attempt wall-clock budget (seconds) | Step 9c.5 (US-8 Wave 5) + Step 14 release |
| Lockfile written | `.aod/locks/deliver-$NNN.lock` present with `$$` as holder | Step 14 release path |

**Reference contracts**:
- Lock data model: `specs/139-delivery-verified-not-documented/data-model.md §10 Delivery Lock`
- Sentinel data model: `specs/139-delivery-verified-not-documented/data-model.md §11 Crash-Recovery Sentinel`
- Exit code taxonomy: `specs/139-delivery-verified-not-documented/contracts/halt-record.md §Channel 3 Exit Code`
- Library: `.aod/scripts/bash/deliver-lock.sh`

---

## Step 14: Release Delivery Lock & Cleanup (US-7, Feature 139 — FR-031)

Runs on every clean exit path (success, halt after Step 9e, opt-out accepted in Step 9d Path A). This is the symmetric counterpart to Step 0.5's `acquire_lock` call. The T041 task description referred to this as "Step 11" in task-local numbering; in the actual skill it lands after the existing Steps 11 (render doc), 12 (close issue), and 13 (prompt for /aod.document) — placement preserves the invariant that **lock release is the final act of every clean invocation**.

**When this step runs**:
- After Step 13 completes (clean success path — full retrospective + delivery doc + issue close + prompt)
- When jumping here from Step 9e halt emission (hard-gate halt path — release lock on halt so operator can inspect without the lock in the way)
- When jumping here from Step 9d Path A after opt-out (delivery proceeded via opt-out; lock released at end same as success)

**When this step is NOT reached**:
- Step 0.5 exit 11 (concurrent invocation) — we never acquired the lock; nothing to release
- Step 0.5 exit 12 (abandoned sentinel) — release was already called inline in Step 0.5 before aborting
- Crash / SIGKILL / uncaught exception mid-invocation — lock + sentinel persist by design; next invocation's `detect_abandoned_sentinel` surfaces the state with exit 12

**1. Source the delivery-lock library** (defensive — may already be loaded from Step 0.5):

```bash
source .aod/scripts/bash/deliver-lock.sh
```

**2. Release the lock** (idempotent per library contract):

```bash
release_lock "$FEATURE"
# release_lock returns 0 always (best-effort rm -f). Safe to call multiple times.
```

This removes `.aod/locks/deliver-$NNN.lock`. If the file is already absent (e.g., operator manually removed it), no error.

**3. Remove the crash-recovery sentinel** (clean-exit invariant per FR-031):

If an auto-fix-loop sentinel was written during Step 9c.5 (US-8 Wave 5) via `write_heartbeat_sentinel`, remove it now — the loop completed cleanly so the sentinel no longer represents abandoned state:

```bash
remove_sentinel "$FEATURE"
# remove_sentinel returns 0 always (best-effort rm -f .aod/state/deliver-$NNN.state.json).
```

For MVP (US-8 deferred), `write_heartbeat_sentinel` is never called, so `remove_sentinel` is a no-op. Keep the call anyway — it's idempotent and guards against future code that writes sentinels without a matching cleanup.

**4. Emit final status**:

Exit with the appropriate code based on the path taken through the skill:

| Path Reached Step 14 Via | Exit Code |
|---------------------------|-----------|
| Clean success (Steps 1-13 all ran) | `0` |
| Step 9e halt (hard-gate halt) | `10` |
| Step 9d Path A opt-out (delivery proceeded via `--no-tests=<reason>`) | `0` |

Note: Exit codes 11 and 12 (concurrency + abandoned sentinel guard) are Step 0.5 aborts and do NOT reach Step 14. If the skill reached Step 14 via Step 9e, the halt record was already written at Step 9e (Channel 2) and the stdout line was emitted (Channel 1); Step 14 adds the process exit (Channel 3).

```bash
# Final exit. Caller shell sees the code via $?.
exit ${HALT_EXIT_CODE:-0}
```

Where `HALT_EXIT_CODE` is set to `10` by Step 9e before jumping to Step 14, and left unset (default `0`) on success and opt-out paths.

**5. Trap handling** (when shell-level traps are available):

If the execution environment supports bash traps, the skill SHOULD register an EXIT trap at Step 0.5 that invokes `release_lock` even on unexpected termination (e.g., `SIGTERM` from parent orchestrator). This is the belt-and-suspenders guarantee that the lock is released on every code path — not just the documented clean exits:

```bash
# Registered in Step 0.5 after lock acquisition:
trap 'release_lock "$FEATURE" 2>/dev/null' EXIT
```

For Markdown-described skill execution (where Claude Code interprets the steps without wrapping in a long-lived shell), the trap is not available. The invariant is instead enforced by documentation: **Step 14 MUST run before any `exit` from Steps 1-13 on clean exit paths.** Step 9e (halt path) explicitly jumps to Step 14 rather than calling `exit` directly. This discipline is encoded in the halt-signal library contract — `halt_exit_code()` echoes the code but does NOT call `exit` itself (library functions never terminate the process; caller owns process lifecycle).

**Output state after Step 14**:
- Lockfile `.aod/locks/deliver-$NNN.lock` removed
- Sentinel `.aod/state/deliver-$NNN.state.json` removed (if present)
- Process exits with code 0 (success/opt-out) or 10 (halt)
- Next `/aod.deliver` invocation on same feature sees a clean slate

**Reference contracts**:
- Lifecycle invariant: `specs/139-delivery-verified-not-documented/data-model.md §10 Delivery Lock Lifecycle`
- Sentinel lifecycle: `specs/139-delivery-verified-not-documented/data-model.md §11 Crash-Recovery Sentinel Lifecycle`
- FR-031 clean-exit requirement: `specs/139-delivery-verified-not-documented/spec.md FR-031`
- Library: `.aod/scripts/bash/deliver-lock.sh` (`release_lock`, `remove_sentinel`)
