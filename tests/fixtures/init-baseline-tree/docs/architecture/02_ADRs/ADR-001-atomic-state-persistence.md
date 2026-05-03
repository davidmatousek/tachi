# ADR-001: Atomic State Persistence via Write-Then-Rename

**Status**: Accepted
**Date**: 2026-02-11
**Deciders**: Architect
**Feature**: 022 (Full Lifecycle Orchestrator)

---

## Context

Feature 022 introduced a full lifecycle orchestrator (`/aod.run`) that chains all 5 AOD stages (Discover, Define, Plan, Build, Deliver) with disk-persisted state for session resilience. The orchestrator must survive session crashes, context overflows, and mid-stage interruptions without losing progress.

The state file (`.aod/run-state.json`) is written after every stage transition and at checkpoints within stages. A corrupted or partially-written state file would strand an in-progress orchestration.

**Constraints**:
- macOS ships Bash 3.2 (no modern Bash features)
- No external databases or services allowed (local-first principle)
- State format must be human-readable for debugging
- Must work on both macOS and Linux

---

## Decision

We will use **write-then-rename** (also known as atomic rename) for all state file writes, implemented in `.aod/scripts/bash/run-state.sh`.

The pattern:
1. Write the complete JSON state to a temporary file (`.aod/run-state.json.tmp`)
2. Use `mv` to atomically rename the temp file to the target path (`.aod/run-state.json`)

All state mutations go through `aod_state_write()` which enforces this pattern. JSON processing uses `jq` for parsing, validation, and field manipulation.

---

## Rationale

**Reasons**:
1. **Crash safety**: On POSIX systems, `mv` within the same filesystem is atomic. If the process dies mid-write, only the temp file is affected; the previous state file remains intact.
2. **No partial writes**: Readers never see a half-written JSON file. The state is either the old complete version or the new complete version.
3. **Zero dependencies**: Uses only `mv` and file I/O -- no file locking libraries, databases, or external services required.
4. **Bash 3.2 compatible**: The pattern uses only basic shell operations available in macOS's default Bash.
5. **Human-readable**: JSON format allows developers to inspect and manually edit state for recovery scenarios.
6. **Proven pattern**: Write-then-rename is a well-established technique used by editors (Vim), databases (SQLite WAL), and package managers (npm).

---

## Alternatives Considered

### Alternative 1: Direct In-Place Write
**Pros**:
- Simpler implementation (just write to the target file)

**Cons**:
- Partial write on crash leaves corrupted JSON
- No recovery path without backup
- Reader could see incomplete data

**Why Not Chosen**: Single point of failure. A crash during write corrupts the state with no recovery.

### Alternative 2: File Locking (flock)
**Pros**:
- Prevents concurrent access
- Standard POSIX mechanism

**Cons**:
- `flock` is not available on macOS by default (requires `brew install flock`)
- Stale locks require manual cleanup after crashes
- Does not prevent partial writes (only prevents concurrent writes)

**Why Not Chosen**: Adds a dependency, does not solve the partial-write problem, and stale locks create operational burden.

### Alternative 3: SQLite Database
**Pros**:
- ACID transactions
- Built-in crash recovery

**Cons**:
- Adds a binary dependency (sqlite3)
- State is not human-readable without tooling
- Overkill for a single JSON document

**Why Not Chosen**: Violates the simplicity principle. The orchestrator manages a single state document, not relational data.

### Alternative 4: Append-Only Log
**Pros**:
- Never loses data (new entries appended)
- Natural audit trail

**Cons**:
- Requires compaction/replay logic
- Harder to read current state (must replay)
- More complex implementation

**Why Not Chosen**: Added complexity without proportional benefit. The state file already includes `error_log` and `gate_rejections` arrays for audit trail.

---

## Consequences

### Positive
- State file survives process crashes and context overflows
- Developers can inspect `.aod/run-state.json` directly for debugging
- Recovery from corruption is possible via artifact-based state reconstruction
- No new binary dependencies beyond `jq` (already needed for JSON manipulation)

### Negative
- Brief window where both `.tmp` and final file exist (negligible risk)
- `jq` is a required dependency (not pre-installed on all systems)
- No built-in concurrent access protection (not needed for single-agent orchestration)

### Mitigation
- `aod_state_validate()` detects corruption and routes to recovery flow
- Corrupted state files are archived with timestamps before recovery
- The SKILL.md documents a full corrupted-state recovery algorithm

---

## Related Decisions

- Bash 3.2 compatibility constraint (see KB Entry 6 in `docs/INSTITUTIONAL_KNOWLEDGE.md`)
- `jq` as JSON processor (no viable Bash-native alternative for complex JSON manipulation)

---

## References

- `.aod/scripts/bash/run-state.sh` -- Implementation
- `.claude/skills/~aod-run/SKILL.md` -- Orchestrator skill (references state management)
- [POSIX rename() atomicity](https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html)
