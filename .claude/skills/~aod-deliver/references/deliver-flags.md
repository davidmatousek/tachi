# Deliver Flags: Step 0 — Parse Arguments (Feature 139 — PRD FR-001, FR-002, FR-034)

This reference is loaded at Step 0, on every `/aod.deliver` run.

**Carry-forward**: After executing all sub-steps below, the following values MUST be carried forward into the agent context for use by downstream INLINE steps. These are NOT persistent shell variables across separate tool calls — the agent MUST re-derive or hold them in working context:

| Variable / Value | Downstream Consumer |
|---|---|
| `AOD_NO_TESTS_FOUND` (true/false) | Step 9d gate decision (Path A vs Path B) |
| `AOD_NO_TESTS_REASON` (captured reason string) | Step 9d Path A display + Step 10 delivery doc |
| `AOD_REQUIRE_TESTS_FOUND` (true/false) | Observability only (deprecated flag) |
| `invocation_command` (full `$0 $@` before parsing) | Step 11c.1 `e2e_validation.invocation_command` field |

No mutation of `AOD_NO_TESTS_FOUND`, `AOD_NO_TESTS_REASON`, or `invocation_command` occurs between Step 0 and their downstream consumers. Carry them verbatim.

---

## Step 0: Parse Arguments (Feature 139 — PRD FR-001, FR-002, FR-034)

Parse `/aod.deliver` invocation flags before any other step runs. The E2E validation gate (Step 9d) is HARD-DEFAULT; the only legitimate path to skip it is an explicit `--no-tests=<reason>` opt-out accepted here at Step 0 with an audit-logged reason.

### 0a: Source the Flag Parser Library

```bash
source .aod/scripts/bash/deliver-flag-parse.sh
```

The library exposes `parse_no_tests`, `validate_reason_length`, `deprecation_notice`, and `reject_flag_conflict`. See `specs/139-delivery-verified-not-documented/contracts/audit-log.md` for the complementary audit contract.

### 0b: Parse Flags

Invoke `parse_no_tests` with the full argument list received from `/aod.deliver`. The parser accepts both `--no-tests=<reason>` (equals form, preferred) and `--no-tests <reason>` (space form). It also captures the deprecated `--require-tests` flag for notice emission.

```bash
parse_no_tests "$@"
# Globals set by parse_no_tests:
#   AOD_NO_TESTS_FOUND        (true | false)
#   AOD_NO_TESTS_REASON       (captured reason; empty if flag absent)
#   AOD_REQUIRE_TESTS_FOUND   (true | false)
```

### 0c: Reject Flag Conflict

`--no-tests` and `--require-tests` cannot be combined — `--require-tests` was the former opt-in to hard-gate (now default), and an explicit opt-out alongside it is a contradictory invocation.

```bash
if ! reject_flag_conflict; then
  # Exit code 2 (flag conflict, aligned with PRD 130 taxonomy).
  # Library already emitted stderr error message.
  exit 2
fi
```

### 0d: Validate Opt-Out Reason Length

When `--no-tests=<reason>` is present, enforce the 10–500 character bound on `<reason>` BEFORE any gate logic runs. Short or missing reasons are rejected — the audit trail must be meaningful.

```bash
if [ "$AOD_NO_TESTS_FOUND" = "true" ]; then
  if ! validate_reason_length "$AOD_NO_TESTS_REASON"; then
    # Stderr already emitted by library: "Error: --no-tests reason must be 10-500 chars (got N)"
    exit 1
  fi
  # NOTE: Audit log append is added in Wave 4 / US-2 / T018 (this skill,
  # Step 0e). Landing the parse + validation here at Wave 3 keeps US-1's
  # hard-gate path free of bypass vulnerabilities while the audit
  # integration lands on a separate task.
fi
```

### 0e: Emit Deprecation Notice for `--require-tests`

The former `--require-tests` flag is now a silent no-op — hard-gate is the default. Per Constitution Principle III (Backward Compat, NON-NEGOTIABLE), the flag is accepted for 2 release cycles with a stderr deprecation notice. Removed in the 3rd release.

```bash
if [ "$AOD_REQUIRE_TESTS_FOUND" = "true" ]; then
  # Resolve version tokens — single source of truth:
  #   1. Prefer `git describe --tags --abbrev=0 2>/dev/null` (nearest release tag)
  #   2. Fallback to reading `.aod/VERSION` if present
  #   3. Final fallback to "current" / "next" sentinels if neither resolves
  CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || cat .aod/VERSION 2>/dev/null || echo "current")
  # Removal version = next-minor bump of CURRENT_VERSION (adopters may override
  # by editing .aod/VERSION). Exact computation policy lives in
  # docs/guides/DELIVERY_HARD_GATE_MIGRATION.md — for now, caller can pass
  # a static placeholder until T067 (Wave 7 polish) lands a resolver helper.
  REMOVAL_VERSION=${REMOVAL_VERSION:-"next+2 releases"}

  deprecation_notice "$CURRENT_VERSION" "$REMOVAL_VERSION"
  # Flag has no runtime effect — continue as if absent.
fi
```

### 0f: Output State After Step 0

These shell variables carry forward into Step 9d:

| Variable | Purpose | Used In |
|----------|---------|---------|
| `AOD_NO_TESTS_FOUND` | Controls Path A vs. Path B selection in Step 9d | Step 9d gate decision |
| `AOD_NO_TESTS_REASON` | Populates `e2e_validation.opt_out_reason` + audit line | Step 9d Path A + Step 10 delivery doc |
| `AOD_REQUIRE_TESTS_FOUND` | No runtime effect — captured for observability only | (none — deprecated) |

No mutation of these variables occurs between Step 0 and Step 9d.

### 0g: Audit Log Emission (US-2, Feature 139 — FR-034)

If `--no-tests=<reason>` was accepted in Step 0a-0f (`AOD_NO_TESTS_FOUND == true` AND length validation passed), append an opt-out line to `.aod/audit/deliver-opt-outs.jsonl` before proceeding. This fulfills PRD FR-034 (single JSON line per opt-out with line-atomic append under concurrent writes).

**When this sub-step runs**:
- `AOD_NO_TESTS_FOUND == true` AND reason-length validation in Step 0d passed
- Skipped entirely when no `--no-tests` flag is present (no opt-out → no audit line)
- Runs BEFORE gate logic (Step 1+) so the audit trail is written even if later steps abort

**1. Resolve contextual fields**:

- `TIMESTAMP`: ISO-8601 UTC from `date -u +"%Y-%m-%dT%H:%M:%SZ"` (matches audit-log.md schema)
- `INVOKER`:
  - Interactive mode: `git config user.email` output. If empty or git unavailable, fall back to literal `"unknown"`.
  - Autonomous mode (`--autonomous` flag): literal `"autonomous"`.
- `FEATURE`: full branch name from `git branch --show-current` (e.g., `139-delivery-verified-not-documented`). The `NNN-name` form is the canonical feature identifier per `contracts/audit-log.md`.
- `REASON`: `$AOD_NO_TESTS_REASON` (already length-validated 10-500 chars in Step 0d).
- `MODE`: `"autonomous"` if `--autonomous` is set, else `"interactive"`.

**2. Source the audit-log library and append**:

```bash
source .aod/scripts/bash/audit-log.sh

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$autonomous" = "true" ]; then
  INVOKER="autonomous"
  MODE="autonomous"
else
  INVOKER=$(git config user.email 2>/dev/null)
  [ -z "$INVOKER" ] && INVOKER="unknown"
  MODE="interactive"
fi

FEATURE=$(git branch --show-current 2>/dev/null)

append_opt_out_line "$TIMESTAMP" "$INVOKER" "$FEATURE" "$AOD_NO_TESTS_REASON" "$MODE" || {
  # Best-effort — library already emitted stderr diagnostic (jq missing,
  # mkdir failure, write failure). Per ADR-006, audit-log failure does NOT
  # halt delivery; the opt-out proceeds with the stderr trail as record.
  echo "[WARN] audit-log append failed; proceeding without audit line (see stderr above)" >&2
}
```

**3. Continue regardless**:

Proceed to Step 1 (DoD validation) whether `append_opt_out_line` returned 0 or non-zero. The audit log is a best-effort observability channel per ADR-006; it does not gate delivery. The opt-out remains visible in the Manual Validation section of `delivery.md` (Step 10 / Step 11c) and in the stdout emission at Step 9d Path A.

**Reference contracts**:
- Line schema: `specs/139-delivery-verified-not-documented/contracts/audit-log.md`
- Library: `.aod/scripts/bash/audit-log.sh`
- Wave 3 counterpart: `AOD_NO_TESTS_REASON` already length-validated; this step is purely audit emission.
