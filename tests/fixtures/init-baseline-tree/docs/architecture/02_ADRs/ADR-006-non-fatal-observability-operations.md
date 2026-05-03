# ADR-006: Non-Fatal Error Handling for Observability Operations

**Status**: Accepted
**Date**: 2026-02-14
**Deciders**: Architect, Feature 054 Implementation Team
**Feature**: 054 - Parallel Execution Hardening

---

## Context

The orchestrator includes observability operations such as circuit-breaker churn detection and state management helpers in `run-state.sh`. These functions enhance operational visibility and resilience:

- `aod_state_record_failure(op, error)` - Record operation failure for circuit-breaker
- `aod_state_check_circuit_breaker()` - Check if circuit-breaker is tripped (3+ consecutive failures)
- `aod_state_reset_circuit_breaker()` - Reset circuit-breaker state

These functions improve operational awareness for parallel Triad reviews and detect churn loops (repeated failures with identical error signatures).

**The key constraint**: Observability is an enhancement layer, not a critical path. Any failure in these functions must never block the primary skill execution. If `jq` is unavailable, the state file is corrupted, or a write fails, the skill must continue normally with conservative defaults.

---

## Decision

We will implement all observability operations with **comprehensive non-fatal error handling** using three techniques:

1. **Function-level wrapping**: Entire function body wrapped in `{ ... } 2>/dev/null || true`
2. **Fallback return values**: Every function returns a safe default on any error
3. **Early exit on missing prerequisites**: Functions return 0 (success) when state file lacks required fields

---

## Rationale

### Why Non-Fatal?

**Observability is informational, not transactional.** Unlike state writes that affect orchestration flow (e.g., `current_stage`), circuit-breaker status and operational metrics are purely informational. A missed detection may delay intervention, but won't corrupt the workflow. A blocked skill due to `jq` missing would be worse than a missed observability signal.

**Prior art in the codebase**: Feature 038 established the "Non-Fatal Wrapper" pattern for standalone commands. Feature 054 extends this pattern to the underlying bash functions themselves, making non-fatality intrinsic rather than caller-dependent.

**Graceful degradation hierarchy**:
1. Best case: Observability functions operate normally, providing full visibility
2. Degraded case: Some observability data missing, skill executes normally
3. Worst case: Observability operations silently fail, skill executes normally without enhanced monitoring

### Design Choices

**Choice 1: Wrap entire function body, not individual statements**

```bash
# CHOSEN: Single wrapper
aod_state_record_failure() {
    {
        # ... all logic ...
    } 2>/dev/null || true
    return 0
}

# REJECTED: Per-statement handling
aod_state_record_failure() {
    aod_state_check_jq || return 0  # Would need this on every call
    state=$(aod_state_read) || return 0
    # ... 10+ more statements each needing || return 0
}
```

**Rationale**: Single wrapper is more maintainable and guarantees non-fatality regardless of future changes to function internals.

**Choice 2: Return fallback values from stdout, not error codes**

```bash
aod_state_check_circuit_breaker() {
    { ... } 2>/dev/null || echo "closed"  # Fallback to stdout
    return 0  # Always success
}
```

**Rationale**: Callers use `$(aod_state_check_circuit_breaker)` for value capture. A non-zero exit code would be ignored; a missing stdout value would cause downstream errors. Explicit fallback ensures callers always receive usable data.

**Choice 3: Validate input defensively, don't trust callers**

```bash
aod_state_record_failure() {
    local op="$1"
    local error="$2"

    # Invalid input -> warning + fallback
    if [[ -z "$op" || -z "$error" ]]; then
        echo "[aod] WARNING: Missing parameters, skipping failure recording" >&2
        return 0
    fi
    # ...
}
```

**Rationale**: Observability functions are called from skill code during governance gates. A typo or calculation error in the skill should not cascade into a hard failure.

---

## Alternatives Considered

### Alternative 1: Strict Error Handling with Caller Guards

Make observability functions fail loudly, require callers to wrap in `|| true`.

**Pros**:
- Clearer debugging: Errors are visible
- Forces callers to acknowledge observability operations can fail

**Cons**:
- Every caller must remember to add guards
- Violates "non-fatal by design" principle established in Feature 038
- Skills would need to duplicate error-suppression logic

**Why Not Chosen**: Shifts complexity to callers; historical evidence shows callers forget guards and cause production failures.

### Alternative 2: Conditional Execution Based on Prerequisites

Check for `jq` and state file existence before each operation; skip silently if missing.

**Pros**:
- Explicit skip logic is documentable
- No reliance on shell error suppression

**Cons**:
- Doesn't handle mid-function failures (e.g., `jq` crashes, disk full)
- Duplicates prerequisite checks across multiple functions

**Why Not Chosen**: Partial solution; full-function wrapping is more robust.

### Alternative 3: Feature Flag to Enable/Disable Observability

Allow users to disable observability entirely via environment variable.

**Pros**:
- Clean opt-out for users experiencing issues
- Clear documentation of what's enabled/disabled

**Cons**:
- Adds configuration complexity
- Observability should "just work" without user intervention
- Users would need to know the flag exists to use it

**Why Not Chosen**: Non-fatal design makes feature flags unnecessary; broken operations degrade gracefully.

---

## Consequences

### Positive

- Observability operations can never block skill execution
- No new dependencies (relies on existing `jq` with fallback)
- Consistent with established non-fatal patterns (Features 038, 042, 049)
- Callers don't need to understand observability internals
- Backward compatible: Existing code ignores new state fields

### Negative

- Errors are silently suppressed; debugging requires enabling verbose mode
- Circuit-breaker may fail to detect churn if state writes fail

### Mitigation

- **Diagnostic logging**: Circuit-breaker logs churn detection to `error_log` array before pausing
- **Warning messages**: Invalid inputs emit warnings to stderr before falling back
- **Explicit fallbacks**: All functions document their fallback values in comments

---

## Implementation Notes

### Circuit-Breaker State Schema

```json
{
  "circuit_breaker": {
    "status": "closed",           // "open" after 3+ identical failures
    "failure_count": 0,           // Resets on success or signature change
    "last_error_signature": null, // "operation:error_type" pattern
    "last_failure_at": null       // ISO8601 timestamp
  }
}
```

### Error Signature Comparison

Circuit-breaker compares `operation_name:error_type` strings. If consecutive failures have different signatures, the counter resets (transient, unrelated issues). Only identical signatures accumulate toward the 3-failure threshold.

---

## Related Decisions

- Pattern: Non-Fatal Observability Wrapper (Feature 038)
- Pattern: Graceful CLI Degradation (Feature 022)

---

## References

- Feature 054 Spec: `specs/054-parallel-execution-budget-hardening/spec.md`
- Implementation: `.aod/scripts/bash/run-state.sh`
- Prior pattern: `docs/architecture/03_patterns/README.md#pattern-non-fatal-observability-wrapper`
