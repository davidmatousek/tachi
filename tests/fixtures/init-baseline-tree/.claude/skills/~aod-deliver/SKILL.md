---
name: ~aod-deliver
description: "Structured delivery retrospective for the AOD Lifecycle's Deliver stage. Validates Definition of Done, captures delivery metrics (estimated vs. actual duration), logs surprises, feeds new ideas back into discovery via GitHub Issues, and creates Institutional Knowledge entries. Use this skill when you need to close a feature, run a delivery retrospective, capture lessons learned, or complete the AOD lifecycle."
---

# AOD Deliver Skill

## Purpose

Close a completed feature with a structured retrospective that captures delivery metrics, surprises, and lessons learned. New ideas from the retrospective feed back into the Discover stage, completing the AOD Lifecycle loop.

**Entry point**: `/aod.deliver`

## Prerequisites

- A feature branch exists with completed work (typically after `/aod.build [--no-security] [--no-simplify] [--no-docs]`)
- `.aod/spec.md` exists with the feature specification
- `.aod/tasks.md` exists with task definitions
- `.aod/scripts/bash/github-lifecycle.sh` is available for GitHub operations

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

Step 11 (added by T042) is responsible for the symmetric `release_lock` call on every clean exit path. Additionally, if bash-level trap handling is available in the execution environment, wrap the skill in:

```bash
trap 'release_lock "$FEATURE" 2>/dev/null' EXIT
```

For Markdown-described skill execution (the Claude Code interpreter walks the steps; no long-lived shell wrapping), the invariant is documented on Step 11: "Step 11 MUST run before any `exit` from Steps 1-10 on clean paths. On crash/SIGKILL, the sentinel-plus-no-lock state will trigger exit 12 on the next invocation."

**Output state after Step 0.5**:

| Variable | Purpose | Used In |
|----------|---------|---------|
| `FEATURE` | Feature branch name (e.g., `139-delivery-verified-not-documented`) | All downstream steps |
| `HEAL_BUDGET` | Configured heal-attempt wall-clock budget (seconds) | Step 9c.5 (US-8 Wave 5) + Step 11 release |
| Lockfile written | `.aod/locks/deliver-$NNN.lock` present with `$$` as holder | Step 11 release path |

**Reference contracts**:
- Lock data model: `specs/139-delivery-verified-not-documented/data-model.md §10 Delivery Lock`
- Sentinel data model: `specs/139-delivery-verified-not-documented/data-model.md §11 Crash-Recovery Sentinel`
- Exit code taxonomy: `specs/139-delivery-verified-not-documented/contracts/halt-record.md §Channel 3 Exit Code`
- Library: `.aod/scripts/bash/deliver-lock.sh`

---

## Step 1: Validate Definition of Done

**GitHub Lifecycle Update (early)**: If a GitHub Issue exists for this feature, update its stage label to `stage:deliver` using `aod_gh_update_stage` from `.aod/scripts/bash/github-lifecycle.sh`. This moves the issue to the Deliver column on the Projects board at the *start* of the delivery retrospective. If `gh` is unavailable, skip silently (graceful degradation).

Check that the feature meets the Definition of Done criteria:

1. **Read `.aod/tasks.md`** and count incomplete tasks (lines matching `- [ ]`).
2. **Read `.aod/spec.md`** to extract the feature name and scope.
3. **Check for open blockers**: Search tasks.md for any items marked `BLOCKED`.

### Validation Results

**If incomplete tasks exist**: Display count and list them:

```
DEFINITION OF DONE — INCOMPLETE

Feature: {feature_name}
Incomplete Tasks: {count}

{list of incomplete task descriptions}

Options:
  (A) Mark remaining tasks as complete and proceed
  (B) Abort delivery — finish tasks first
```

Use AskUserQuestion to let the user choose.

**If all tasks complete**: Proceed to Step 2.

```
DEFINITION OF DONE — PASSED

Feature: {feature_name}
Tasks: {total} complete, 0 remaining
```

---

## Step 2: Capture Delivery Metrics

### Estimated Duration

Use AskUserQuestion:

```
Question: "How long did you originally estimate this feature would take?"
Header: "Estimate"
Options:
  - "1-2 days": "A quick feature or fix"
  - "3-5 days": "About a week of work"
  - "1-2 weeks": "A moderate feature spanning multiple days"
  - "3+ weeks": "A large feature requiring significant effort"
```

Allow "Other" for custom estimates (e.g., "4 sprints", "3 months").

### Actual Duration

Compute automatically from the feature branch creation date:

```bash
# Get the date of the first commit on this branch (not on main)
git log main..HEAD --reverse --format="%ai" | head -1
```

If the branch has no commits diverged from main, use the earliest commit date on the current branch.

Calculate the difference between the branch start date and today's date. Express as:
- "N days" if < 14 days
- "N weeks" if >= 14 days and < 60 days
- "N months" if >= 60 days

Store both `estimated_duration` and `actual_duration`.

---

## Step 3: Capture Surprise Log

Use AskUserQuestion:

```
Question: "What surprised you most during this feature? (One sentence minimum)"
Header: "Surprises"
Options:
  - "Scope was larger than expected": "The feature required more work than initially scoped"
  - "Dependencies were complex": "Integrations or dependencies added unexpected complexity"
  - "Smooth sailing": "Everything went roughly as planned — no major surprises"
```

Allow "Other" for custom surprise statements (required — must be at least 1 sentence).

**Validation**: If the user provides empty or very short text (<10 chars), re-prompt: "Please provide at least one sentence describing what surprised you."

Store as `surprise_log`.

---

## Step 4: Capture Next Ideas (Optional Feedback Loop)

Use AskUserQuestion:

```
Question: "Did this feature reveal any new ideas or follow-up work? (Optional — select 'None' to skip)"
Header: "Next ideas"
Options:
  - "Yes — let me describe": "I have one or more ideas for follow-up features or improvements"
  - "None": "No new ideas emerged from this feature"
```

**If "Yes"**: Ask the user to describe each idea. For each idea provided:

1. **MUST** use the standalone `create-issue.sh` script to create the GitHub Issue (do NOT call `gh issue create` directly — the script handles both issue creation and project board sync):
   ```bash
   bash .aod/scripts/bash/create-issue.sh \
     --title "{idea_description}" \
     --body "$BODY" \
     --stage discover \
     --type retro
   ```
   Where `$BODY` contains:
   ```markdown
   # {idea_description}

   ## ICE Score
   Impact: —, Confidence: —, Effort: — = **Not yet scored**

   ## Evidence
   Retrospective: Emerged during delivery of {feature_name}

   ## Metadata
   - Source: Retrospective
   - Priority: Not yet scored
   - Date: {YYYY-MM-DD}
   - Status: New (from retrospective)
   - Origin Feature: {feature_name}
   ```
   The script applies the `type:retro` label automatically and adds the issue to the Projects board with the correct Status column.

2. If `gh` is unavailable, log the idea to stdout with guidance:
   ```
   NEW IDEA FROM RETROSPECTIVE (GitHub unavailable — capture manually):
   Idea: {idea_description}
   Suggested next step: Run `/aod.idea {idea_description}` to formally capture and score.
   ```

Store ideas as `next_ideas[]`.

**If "None"**: Skip and proceed to Step 5.

---

## Step 5: Capture Lessons Learned

Use AskUserQuestion:

```
Question: "What is the key lesson learned from this feature that future developers should know?"
Header: "Lesson"
Options:
  - "Technical pattern": "A reusable technical approach or architecture decision worth documenting"
  - "Process improvement": "A workflow or process change that would help future features"
  - "Tooling insight": "A tool, library, or configuration finding worth preserving"
```

Allow "Other" for custom lesson descriptions.

After category selection, prompt for the full lesson text:
"Describe the lesson in 2-3 sentences. What was the problem, what did you learn, and how should it be applied?"

**Validation**: Require at least 20 characters of lesson text.

Store as `lesson_category` and `lesson_text`.

---

## Step 6: Write Institutional Knowledge Entry

Append a new entry to `docs/INSTITUTIONAL_KNOWLEDGE.md` in the `## Knowledge Entries` section.

Determine the next entry number by scanning existing `### Entry N:` headers and incrementing.

```markdown
### Entry {N}: {feature_name} — Delivery Retrospective

## [{lesson_category}] - {one_line_summary}

**Date**: {YYYY-MM-DD}
**Context**: Delivery retrospective for {feature_name}. Estimated: {estimated_duration}, Actual: {actual_duration}.

**Problem**:
{lesson_text — first sentence or clause describing the challenge}

**Solution**:
{lesson_text — remaining sentences describing the approach/learning}

**Why This Matters**:
Captured during structured delivery retrospective. {surprise_log}

**Tags**: #retrospective #delivery #{lesson_category_tag}

### Related Files:
- `.aod/spec.md` — Feature specification
- `.aod/tasks.md` — Task breakdown

---
```

Map `lesson_category` to tags:
- "Technical pattern" → `#architecture #pattern`
- "Process improvement" → `#process #workflow`
- "Tooling insight" → `#tooling #configuration`
- Other → `#general`

---

## Step 7: Post Delivery Metrics to GitHub Issue

If a GitHub Issue exists for this feature (search by feature name or branch):

1. Find the issue: `aod_gh_find_issue "{feature_name}"` or search by branch name
2. Add a comment with delivery metrics:
   ```markdown
   ## Delivery Metrics

   | Metric | Value |
   |--------|-------|
   | Delivery Date | {YYYY-MM-DD} |
   | Estimated Duration | {estimated_duration} |
   | Actual Duration | {actual_duration} |
   | Surprise Log | {surprise_log} |
   | Lessons Learned | {lesson_category}: {one_line_summary} |
   | New Ideas | {count of next_ideas or "None"} |
   ```
3. Note: The issue was already transitioned to `stage:deliver` in Step 1.

---

## Step 8: Regenerate BACKLOG.md

Run `.aod/scripts/bash/backlog-regenerate.sh` to update the backlog snapshot with the newly delivered item. If `gh` is unavailable, skip silently.

---

## Step 9: Run E2E Validation Gate

Run automated E2E validation against the feature's acceptance criteria before collecting test evidence. This step is **non-fatal** by default (ADR-006): if the tester agent fails to launch, crashes, or times out, log the error and proceed to Step 10. The E2E validation gate supports two modes:

- **Soft gate** (default): Warn on test failure, let the developer decide whether to proceed or abort
- **Hard gate** (`--require-tests`): Block delivery if any test fails

The gate decision is made in sub-step 9d based on the `require_tests` flag passed from the command's flag parsing (Step 0).

### 9a: Read Active Pack Test Contract

Replace filesystem-based Playwright detection with a deterministic lookup against the active stack pack's `STACK.md` contract. See `specs/130-e2e-hard-gate/contracts/deliver-step9-integration.md` §Step 9a for the full contract; see `specs/130-e2e-hard-gate/data-model.md` §2 for the exit-code taxonomy and §3 for the `e2e_validation.*` payload shape (plan Decision 4).

**1. Resolve the active pack**:

Read `.aod/stack-active.json` and extract the `.pack` key (e.g., via `jq -r '.pack' .aod/stack-active.json 2>/dev/null`).

- **If the file is absent OR the JSON is malformed** (jq exits non-zero, or `.pack` is null/empty): skip Step 9 entirely. Proceed directly to Step 10. This preserves the backward-compatibility path for projects not using stack packs (FR-011) and defends against `.aod/stack-active.json` schema drift (plan Decision 4, architect LOW-4). Do NOT set `e2e_validation.*` fields — Step 11c falls through to the legacy path.

**2. Invoke the contract lint** on the active pack's `STACK.md`:

```bash
LINT_STDERR=$(bash .aod/scripts/bash/stack-contract-lint.sh "stacks/$ACTIVE_PACK/STACK.md" 2>&1 >/dev/null)
LINT_EXIT=$?
```

On exit code `0`, parse the extracted fields (`TEST_COMMAND`, `E2E_COMMAND`, `E2E_OPT_OUT`) from the lint's stdout for use in Step 9b.

**3. Branch on exit code** (taxonomy from data-model.md §2):

- **Exit 0 (valid)**: If `E2E_OPT_OUT` is set → store `e2e_validation.status = "skipped"`, `e2e_validation.skip_reason = "opt_out: $E2E_OPT_OUT"`. Do NOT populate `e2e_validation.command` (plan Decision 4 — `command` is populated only for pass/fail). Proceed to Step 10. Else → `E2E_COMMAND` is set; pass it forward to Step 9b.
- **Exit 1 (runtime error), 2 (missing `test_command`), 3 (XOR violation), 4 (unknown key), 5 (missing contract block)**: Store `e2e_validation.status = "error"`, `e2e_validation.error = "$LINT_STDERR"`. Do NOT populate `e2e_validation.command`. Skip Step 9b and proceed to Step 10. This is NOT a hard-block on delivery — the hard-block is reserved for real E2E test failures under `--require-tests` (Step 9d).

**Output state after 9a**:
- `e2e_validation.status` (enum: `"skipped"` | `"error"` | unset when proceeding to 9b)
- `e2e_validation.skip_reason` (present when `status == "skipped"`; the opt-out reason)
- `e2e_validation.error` (present when `status == "error"`; the lint stderr diagnostic)
- `e2e_validation.command` (absent here — populated later only when `status` resolves to `"pass"` or `"fail"` via Steps 9b/9c per data-model §3)
- `E2E_COMMAND` shell variable (populated only when proceeding to Step 9b; sourced from the parsed contract)

### 9a.5: AC-Coverage Pre-Gate (US-4, Feature 139 — FR-006..FR-011)

Before invoking the tester agent, verify every Acceptance Criterion in `spec.md` is mapped to at least one test scenario. This is the core promise of User Story 4: bind *what we promised* (spec ACs) to *what we verified* (scenarios) before the runner ever executes. Runs only when Step 9a did not short-circuit the gate (i.e., `e2e_validation.status` is still unset after 9a).

**When this step runs**:
- `E2E_COMMAND` was resolved successfully in Step 9a (pack has a real contract; not opt-out, not error)
- `e2e_validation.status` is unset entering 9a.5

**When this step is skipped**:
- Step 9a short-circuited with `status = "skipped"` or `status = "error"` — AC-coverage is irrelevant because the gate is already bypassed
- `.aod/stack-active.json` was absent/malformed (Step 9a proceeded directly to Step 10, this step never reached)

**1. Source the AC-coverage parser library**:

```bash
source .aod/scripts/bash/ac-coverage-parse.sh
```

**2. Resolve spec path**:

From the current branch name, derive `specs/{NNN}-*/spec.md` via:

```bash
FEATURE=$(git branch --show-current)
NNN="${FEATURE%%-*}"
SPEC_PATH=$(ls -d specs/${NNN}-*/spec.md 2>/dev/null | head -1)
```

**3. Run strict parse + coverage map**:

```bash
ACS_JSON=$(parse_acs_strict "$SPEC_PATH")
PARSE_RC=$?

# Scenarios directory: tests/e2e/ is the canonical root; individual packs may
# declare alternatives but the parser scans recursively for @US-NN-AC-N tags
# across *.feature, *.test.{ts,tsx,js,jsx}, *.spec.{ts,tsx,js,jsx} regardless.
SCENARIOS_DIR="tests/e2e/"

COVERAGE_JSON=$(printf '%s' "$ACS_JSON" | build_ac_scenario_map - "$SCENARIOS_DIR")
MAP_RC=$?
```

**4. Branch on parse exit code** (taxonomy from `ac-coverage-parse.sh` header):

- **Exit 0 (strict parse succeeded)**: Continue to step 5 (gate decision).
- **Exit 2 (spec path missing/unreadable)**: Emit stderr warning and skip the pre-gate (store `e2e_validation.ac_coverage.status = "skipped"`, `e2e_validation.ac_coverage.skip_reason = "spec_missing"`). Proceed to Step 9b — existing tester flow surfaces the missing-spec condition. Do NOT halt here; delivery without spec is an upstream governance failure handled elsewhere.
- **Exit 3 (legacy prose ACs detected)**: **Tier 2 descope branch** (per tasks.md Phase 6 header):
  - **Default (halt)**: Emit Step 9e-style halt with `reason = "ac_coverage_fail"`, `scenarios = []`, `recovery_status = "not_attempted"`. Human-readable stderr message:
    ```
    Halted — legacy prose ACs detected in $SPEC_PATH. Retrofit spec ACs to
    Given/When/Then format before delivering. See:
    docs/guides/AC_COVERAGE_MIGRATION.md
    ```
    Delivery halts with exit 10 (see Step 9e halt emission sub-step — AC-coverage fail reuses the same channels as e2e_fail, distinguished by `reason` enum).
  - **Tier 2 descope (build-phase flag, when burn-rate triggers)**: If `AOD_AC_COVERAGE_WARN_ONLY == "true"` in the environment AND `heal_attempts == 0` (no auto-fix configured), downgrade to warn-only: emit the same stderr message, store `e2e_validation.ac_coverage.status = "warn_legacy_prose"`, and proceed to Step 9b. This branch exists for backward-compat during initial rollout and is opt-in via env; the Tier 2 descope trigger documents when it is acceptable to activate.
- **Exit 4 (invalid [MANUAL-ONLY] reason)**: Halt with `reason = "ac_coverage_fail"`. Stderr message names the AC ID and the minimum reason length (10 chars). Same halt channels as exit 3 default path.
- **Exit 1 (runtime error — jq/awk failure)**: Non-fatal per ADR-006. Store `e2e_validation.ac_coverage.status = "error"`, `e2e_validation.ac_coverage.error = "parse_runtime_failure"`, proceed to Step 9b. The tester-gate still runs; we just lose the AC-coverage evidence in the delivery doc.

**5. Gate decision based on coverage map** (only when parse exit 0):

Parse `uncovered_acs` from the coverage JSON:

```bash
UNCOVERED_ACS=$(printf '%s' "$COVERAGE_JSON" | jq -c '.uncovered_acs')
UNCOVERED_COUNT=$(printf '%s' "$UNCOVERED_ACS" | jq 'length')
```

- **`UNCOVERED_COUNT == 0` (all ACs covered or manual-only)**: **PASS** the pre-gate. Store `e2e_validation.ac_coverage = $COVERAGE_JSON` (the full map including `total_acs`, `covered_count`, `uncovered_acs: []`, `manual_only_acs[]`, `coverage_by_ac[]`) for Step 10 rendering. Proceed to Step 9b.

- **`UNCOVERED_COUNT > 0`**: **HALT** via the Step 9e protocol. Before invoking the halt emission, set:
  - `HALT_REASON = "ac_coverage_fail"`
  - `SCENARIOS_JSON = $UNCOVERED_ACS` (reuse the halt-record `failing_scenarios` field to carry the uncovered AC IDs — per `contracts/halt-record.md`, the array is an opaque string list that orchestrators pattern-match on by `reason`)
  - `RECOVERY_STATUS = "not_attempted"` (auto-fix loop cannot add missing scenarios; human authorship required)
  - `HEAL_PR_URL = ""` and `HEAL_PR_NUMBER = ""` (no heal-PR for AC-coverage failures; the fix is spec+scenario authorship, not patching)

  Emit stdout line:
  ```
  Halted — $UNCOVERED_COUNT acceptance criterion(s) without scenarios: $(printf '%s' "$UNCOVERED_ACS" | jq -r '. | join(", ")')
  Mark these ACs [MANUAL-ONLY] <reason> in spec.md, or author missing scenarios. See:
  docs/guides/AC_COVERAGE_MIGRATION.md
  ```

  Then jump to Step 9e (halt signal emission) with the above context. Step 9e writes the halt record (channel 2) and returns exit 10 (channel 3) as it does for e2e_fail halts — the only difference is the `reason` enum value distinguishing the halt cause.

**6. Store coverage payload for Step 10**:

On pass path (UNCOVERED_COUNT == 0), the full `$COVERAGE_JSON` is stored as `e2e_validation.ac_coverage`. Step 10 (render doc) reads `e2e_validation.ac_coverage.coverage_by_ac[]` to render the AC→scenario table and `e2e_validation.ac_coverage.manual_only_acs[]` to render the Manual Validation subsection. Shape per `ac-coverage-parse.sh build_ac_scenario_map`:

```json
{
  "total_acs": 5,
  "covered_count": 4,
  "uncovered_acs": [],
  "manual_only_acs": ["US-03-AC-2"],
  "coverage_by_ac": [
    {"ac_id": "US-01-AC-1", "scenarios": ["tests/e2e/login.feature:12"], "manual_only": false},
    ...
  ]
}
```

**Output state after 9a.5**:
- `e2e_validation.ac_coverage` (full coverage map when parse+gate succeeded; `status = "skipped"|"error"|"warn_legacy_prose"` sub-object when degraded)
- `HALT_REASON` shell variable (set only on halt path; consumed by Step 9e)
- `SCENARIOS_JSON` shell variable (set only on halt path; carries uncovered AC list into halt record)

**Reference contracts**:
- AC parser: `.aod/scripts/bash/ac-coverage-parse.sh`
- Halt record: `specs/139-delivery-verified-not-documented/contracts/halt-record.md`
- Migration guide: `docs/guides/AC_COVERAGE_MIGRATION.md`
- Canonical AC ID format: `US-{NN}-AC-{N}` (e.g., `US-01-AC-1`)

### 9b: Invoke Tester Agent

Launch the tester agent to generate and execute BDD/Gherkin E2E scenarios from the feature's acceptance criteria.

1. **Resolve spec path**: Find `specs/{NNN}-*/spec.md` using the feature number from the current branch
2. **Launch tester agent** via the Agent tool:
   ```
   Agent tool:
     subagent_type: "tester"
     prompt: |
       Generate and execute BDD/Gherkin E2E scenarios for the feature specification.

       Input:
       - Feature spec: {spec_path}
       - E2E runner command: ${E2E_COMMAND}
       - Output directory: .aod/test-results/

       Instructions:
       1. Read the feature spec and extract acceptance criteria from all user stories
       2. Generate Gherkin scenarios (.feature files) from the acceptance criteria
       3. Execute scenarios by invoking the declared E2E runner command
       4. Write test results to .aod/test-results/

       Subagent Return Policy:
       - Return ONLY: status (pass/fail/error), item count ({passed}/{total}), and results file path (.aod/results/tester.md)
       - Write detailed findings (failing scenario names, error details, execution logs) to .aod/results/tester.md BEFORE returning
       - Max return: 15 lines / ~200 tokens
     timeout: 300000  # 5 minutes
   ```
3. **Handle timeout**: If the agent does not return within 5 minutes:
   - Display: `"E2E validation timed out after 5 minutes ({elapsed}s elapsed)"`
   - Use AskUserQuestion: "(A) Continue waiting, (B) Abort E2E validation and proceed"
   - If Abort: store `e2e_validation.status = "error"`, `e2e_validation.error = "timeout"`, proceed to Step 10

4. **Handle agent failure**: If the agent fails to launch or crashes:
   - Display: `"E2E validation error: {error_message}"`
   - Store `e2e_validation.status = "error"`, `e2e_validation.error = "{error_message}"`
   - Proceed to Step 10 (non-fatal per ADR-006)

### 9c: Parse Test Results

Read and parse the tester agent's return value and detailed results.

1. **Parse agent return**: Extract status (`pass`/`fail`/`error`), item count (`{passed}/{total}`), and results file path
2. **Read detailed results**: If status is `fail`, read `.aod/results/tester.md` to extract:
   - Failing scenario names
   - Error messages for each failure
   - Total, passed, failed, and skipped counts
3. **Store results** in the `e2e_validation` data structure:
   - `e2e_validation.status`: `"pass"` | `"fail"` | `"error"` | `"skipped"`
   - `e2e_validation.total`: Total test count
   - `e2e_validation.passed`: Passed test count
   - `e2e_validation.failed`: Failed test count
   - `e2e_validation.skipped`: Skipped test count
   - `e2e_validation.failing_scenarios[]`: List of failing scenario names (empty if all pass)
4. **Display summary**:
   ```
   E2E Validation: {status}
   Tests: {passed}/{total} passed ({failed} failed, {skipped} skipped)
   ```
   If any failures, also display:
   ```
   Failing scenarios:
     - {scenario_name_1}
     - {scenario_name_2}
   ```
5. Proceed to sub-step 9c.5 (Auto-Fix Loop) when `e2e_validation.status == "fail"` AND `heal_attempts > 0`; otherwise proceed directly to sub-step 9d (Gate Decision)

### 9c.5: Auto-Fix Loop (US-8, Feature 139 — FR-017..FR-023)

When tests fail and `heal_attempts > 0` in `.aod/config.json`, attempt auto-recovery before gate decision. The loop lives strictly between Step 9c (Parse Test Results) and Step 9d (Gate Decision) — if tests pass at any attempt, execution jumps directly to Step 9d with `gate_result = "pass"`. On exhaustion or scope-guard escalation, Step 9d fires the halt path (Step 9e → heal-PR).

**Preconditions**:
- `e2e_validation.status == "fail"` (from Step 9c)
- `e2e_validation.failed > 0` and `e2e_validation.failing_scenarios[]` non-empty
- Skip this step entirely when preconditions are not met

**1. Read config**:

```bash
HEAL_ATTEMPTS=$(jq -r '.deliver.heal_attempts // 0' .aod/config.json 2>/dev/null || echo 0)
HEAL_MULTIPLIER=$(jq -r '.deliver.heal_max_timeout_multiplier // 1.5' .aod/config.json 2>/dev/null || echo 1.5)
```

**2. Short-circuit on `HEAL_ATTEMPTS == 0`**:

If `HEAL_ATTEMPTS` is `0`, skip the loop entirely (config-level opt-out):
- Set `e2e_validation.recovery_status = "skipped_via_config"`
- Set `e2e_validation.recovery_actions = []`
- Emit NO heartbeat sentinel (no auto-fix work will run)
- Proceed directly to Step 9d — the gate decision will halt via Path B (heal-PR escalation) since tests still failed.

**3. Initialize loop state**:

- `recovery_status = "pending"` — will be finalized on loop exit
- `recovery_actions = []` — append one record per attempt regardless of outcome
- `FEATURE` — current branch name (e.g., `139-delivery-verified-not-documented`)

**4. Loop** (`attempt` in `1..HEAL_ATTEMPTS`):

   a. **Heartbeat sentinel** (FR-029): BEFORE any heal work begins for this attempt, call:

   ```bash
   source .aod/scripts/bash/deliver-lock.sh
   write_heartbeat_sentinel "$FEATURE" "$attempt" "$HEAL_ATTEMPTS"
   ```

   Integrates with US-7 crash recovery: if the skill crashes mid-attempt, the next `/aod.deliver` invocation's `detect_abandoned_sentinel` (Step 0.5) will halt with exit 12. Heartbeat refresh is integral — every attempt overwrites the sentinel with a fresh `last_heartbeat` timestamp, so an abandoned process is distinguishable from an actively-running loop.

   b. **Invoke tester in `mode: heal`**: pass the failing scenario, `test_paths`, `framework`, `max_timeout_multiplier`, `attempt_number`. The tester returns a proposed diff on stdout and a human-readable description on stderr. See `.claude/agents/tester.md` §9 "Operating Modes → Mode: heal" for the full input/output contract.

   c. **Scope-guard evaluation** (wired in full by T056 — see Step 9c.5 scope-guard evaluation bullet below): call `evaluate_scope_guard` on the proposed diff. Library returns a JSON decision record with `{decision, reason, violating_lines}`.

   d. **Branch on scope-guard decision**:

      - **`allowed`**: apply the diff with `git apply --index`, commit using the T048 format, then re-run tests via the tester agent (non-heal mode — just execute and report). If tests pass → set `recovery_status = "recovered"`, break the loop, proceed to Step 9d with `gate_result = "pass"`. If tests still fail → append the attempt record and continue to the next iteration.

      - **`rejected`**: abort the loop immediately. Append the attempt record with `scope_guard_decision: "rejected"` and `scope_guard_reason` populated. Set `recovery_status = "scope_guard_escalated"`. Surface the rejection reason into the heal-PR body (pass via `HEAL_PR_*` env vars when Step 9e invokes `heal-pr.sh`). Break loop.

   e. **Append attempt record** to `e2e_validation.recovery_actions[]` (payload shape defined in T049 below). Each attempt adds exactly one record, regardless of outcome.

**5. On loop exhaustion** (all `HEAL_ATTEMPTS` used, tests still failing):

- Set `recovery_status = "escalated_to_heal_pr"` (or `"exhausted"` — both enum values map to the same downstream behavior; use `"exhausted"` when loop iterated fully without scope-guard rejection)
- Proceed to Step 9d — the gate decision will halt (Path B) and Step 9e will invoke `heal-pr.sh` with the full `recovery_actions[]` context

**6. Commit format enforcement** (US-8, T048):

Every auto-fix commit MUST match this exact format:

```
e2e-heal(attempt {N}/{M}): {description}
```

Where `{N}` is the current attempt number (1-indexed), `{M}` is `HEAL_ATTEMPTS`, and `{description}` is the tester's stderr output trimmed to a single line.

After applying a scope-guard-allowed diff, compose and validate the commit message:

```bash
_validate_heal_commit_msg() {
  local msg="$1"
  if ! echo "$msg" | grep -qE '^e2e-heal\(attempt [0-9]+/[0-9]+\): .+'; then
    echo "[auto-fix] rejecting commit — message does not match 'e2e-heal(attempt N/M): ...' format" >&2
    return 1
  fi
  return 0
}

COMMIT_MSG="e2e-heal(attempt ${attempt}/${HEAL_ATTEMPTS}): ${description_from_tester_stderr}"
if _validate_heal_commit_msg "$COMMIT_MSG"; then
  git commit -m "$COMMIT_MSG"
else
  # Refuse to commit — treat as scope-guard-equivalent failure; append record and break loop.
  recovery_status="escalated_to_heal_pr"
  break
fi
```

Rationale: commit history becomes machine-auditable; `specs/{NNN}-*/delivery.md` Recovery Actions table (Step 11c.1 T037) filters by this prefix; rollback scripts can `git revert` by grepping the prefix.

**7. Scope-guard evaluation** (US-9 wiring, T056):

```bash
# Source scope-guard library
source .aod/scripts/bash/scope-guard.sh

# Resolve test_paths (stack pack or defaults)
TEST_PATHS=$(get_test_paths)

# Detect framework
FRAMEWORK=$(detect_framework "$(pwd)")

# Evaluate the proposed diff (diff content passed as a raw string is auto-materialized by the library)
SCOPE_GUARD_RESULT=$(evaluate_scope_guard "$PROPOSED_DIFF" "$TEST_PATHS" "$FRAMEWORK" "$HEAL_MULTIPLIER")
SCOPE_GUARD_DECISION=$(echo "$SCOPE_GUARD_RESULT" | jq -r '.decision')
SCOPE_GUARD_REASON=$(echo "$SCOPE_GUARD_RESULT" | jq -r '.reason // empty')
SCOPE_GUARD_VIOLATING_LINES=$(echo "$SCOPE_GUARD_RESULT" | jq -c '.violating_lines // []')
```

Branch logic per FR-018..FR-019 loop behavior:
- `SCOPE_GUARD_DECISION == "allowed"`: apply diff with `git apply --index`, commit per the T048 format above, re-run tests.
- `SCOPE_GUARD_DECISION == "rejected"`: DO NOT APPLY. Append a `recovery_actions[]` record with `scope_guard_decision: "rejected"` and `scope_guard_reason` populated. Break loop. Set `recovery_status = "scope_guard_escalated"`.

The scope-guard library is deterministic (no LLM judgment) — same diff + same `test_paths` + same `framework` always yields the same decision. Contract: `specs/139-delivery-verified-not-documented/contracts/scope-guard-decision.md`.

**8. Payload accumulation** (US-8, T049):

The `e2e_validation` payload extends PRD 130's delivered schema with two additive fields:

```json
{
  "...PRD 130 existing fields...": "...",
  "recovery_status": "pending | recovered | exhausted | scope_guard_escalated | skipped_via_config | escalated_to_heal_pr",
  "recovery_actions": [
    {
      "attempt_number": 1,
      "commit_sha": "abc123...",
      "description": "Updated selector [data-testid=\"old\"] to [data-testid=\"new\"]",
      "outcome": "passed | still_failing",
      "scope_guard_decision": "allowed | rejected",
      "scope_guard_reason": null
    }
  ],
  "ac_coverage": { ... }
}
```

Construction rules:
- `recovery_status` starts `"pending"` when loop enters; receives a final value on exit (one of: `recovered`, `exhausted`, `scope_guard_escalated`, `skipped_via_config`, `escalated_to_heal_pr`)
- Each attempt appends exactly one record to `recovery_actions[]` regardless of outcome (allowed+passed, allowed+still_failing, rejected)
- `commit_sha` is empty-string for rejected attempts (no commit was made)
- `scope_guard_reason` is `null` when `scope_guard_decision: "allowed"`, populated from `SCOPE_GUARD_REASON` when `rejected`
- On `heal_attempts == 0` skip: `recovery_status = "skipped_via_config"`, `recovery_actions = []`
- This payload flows into Step 11c.1 where T037 (Wave 4b) renders the Recovery Actions table under "Execution Evidence"

Reference schema: `specs/139-delivery-verified-not-documented/data-model.md`.
Tester contract: `.claude/agents/tester.md` §9.
Scope-guard contract: `specs/139-delivery-verified-not-documented/contracts/scope-guard-decision.md`.

**9. Proceed to Step 9d**: Gate decision consumes `e2e_validation.status` (possibly now `"pass"` if the loop recovered), `recovery_status`, and `recovery_actions[]` to make its final halt/proceed determination.

### 9d: Gate Decision

Evaluate test results and determine whether delivery should proceed, based on gate mode and test outcome.

**Inputs**: `e2e_validation.status`, `e2e_validation.failed`, `e2e_validation.failing_scenarios[]`, `require_tests` flag (from command Step 0), `autonomous` flag (from command Step 0).

**Decision paths**:

1. **All tests pass** (`e2e_validation.status == "pass"`):
   - Display: `"E2E Validation Gate: PASSED — all tests passed"`
   - Store `e2e_validation.gate_mode = "soft"` or `"hard"` (based on `require_tests` flag)
   - Store `e2e_validation.gate_result = "pass"`
   - Proceed to Step 10

2. **Tests fail + Status is "error" or "skipped"** (from sub-steps 9a-9c):
   - These statuses bypass the gate entirely — they were already handled in prior sub-steps
   - Store `e2e_validation.gate_mode = "hard"` (no valid gate evaluation ran; default to hard posture)
   - Store `e2e_validation.gate_result = "skip"`
   - Proceed to Step 10

3. **Tests fail + delivery halts** — HARD-GATE DEFAULT (Feature 139, PRD FR-001/FR-002; no autonomous override):

   The gate decision is identical in interactive and autonomous modes — `/aod.deliver` halts on test failure unless an explicit opt-out was accepted at Step 0 via `--no-tests=<reason>`. This replaces the former soft-gate default and autonomous override.

   **Path A — Opt-out accepted** (`AOD_NO_TESTS_FOUND == true` from Step 0, regardless of mode):
   - Display:
     ```
     E2E Validation Gate: SKIPPED via --no-tests opt-out
     Reason: {AOD_NO_TESTS_REASON}
     Failing scenarios (recorded for audit trail):
       - {scenario_name_1}
       - {scenario_name_2}
     ```
   - Store `e2e_validation.gate_mode = "skipped_via_opt_out"`
   - Store `e2e_validation.gate_result = "skip"`
   - Store `e2e_validation.opt_out_reason = AOD_NO_TESTS_REASON` (surfaces in Manual Validation section of delivery.md)
   - Proceed to Step 10 (audit line already appended at Step 0 when the flag was accepted — T018 Wave 4 integration)

   **Path B — No opt-out → HALT** (both modes, default):
   - Display error:
     ```
     E2E Validation Gate: HALTED — {failed_count} test(s) failed (hard-gate default)

     Failing scenarios:
       - {scenario_name_1}
       - {scenario_name_2}

     Delivery halted. Options:
       1. Fix the failing tests and re-run /aod.deliver
       2. Opt out explicitly with /aod.deliver --no-tests="<reason ≥10 chars>"
          (opt-outs are audit-logged to .aod/audit/deliver-opt-outs.jsonl)
     ```
   - Store `e2e_validation.gate_mode = "hard"`
   - Store `e2e_validation.gate_result = "block"`
   - Store `e2e_validation.failing_scenarios[]` (already populated at Step 9c)
   - Proceed to Step 9e (Halt Signal Emission) — do NOT proceed to Step 10

### 9e: Halt Signal Emission (Feature 139 — PRD FR-011, FR-024..FR-025)

Invoked when Step 9d Path B halts delivery. Emits the halt across three channels so orchestrators and human operators can branch on any one. See `specs/139-delivery-verified-not-documented/contracts/halt-record.md` for the full contract.

**When this step runs**:
- Reached via Step 9d Path B (hard-gate halt) — either interactive or autonomous mode
- NOT reached when Path A (opt-out accepted) fires — that path proceeds to Step 10
- NOT reached when Path 1 (all pass) or Path 2 (error/skipped) fires

**1. Source the halt-signal library**:

```bash
source .aod/scripts/bash/halt-signal.sh
```

**2. Resolve contextual fields**:

- `FEATURE`: current branch name (e.g., `139-delivery-verified-not-documented`)
- `HEAL_PR_URL`: populated by heal-PR creation (Wave 4+ integration; empty string until T032 lands)
- `HEAL_PR_NUMBER`: same — empty integer until heal-PR wiring
- `SCENARIOS_JSON`: JSON array of `e2e_validation.failing_scenarios[]`, built via `jq -c -n '$ARGS.positional' --args "${failing[@]}"`
- `RECOVERY_STATUS`: `"not_attempted"` at Wave 3 floor (auto-fix loop lands in Wave 5 / US-8); will become `"exhausted"` or `"scope_guard_escalated"` once T047 wires the loop
- `HALT_REASON`: `"e2e_fail"` (enum value from `contracts/halt-record.md` §Channel 2); `"ac_coverage_fail"` and `"abandoned_heal"` are reserved for US-4 (Wave 4) and US-7 (Wave 4) paths

**3. Channel 1 — stdout line** (interactive + autonomous):

```bash
emit_halt_stdout "$HEAL_PR_URL" ".aod/results/tester.md"
```

The library emits either `"Halted — heal-PR <URL> requires human review"` (preferred form, when URL is populated) or the fallback `"Halted — test failures logged at .aod/results/tester.md; heal-PR unavailable"` when URL is empty. Per T016 (Feature 139), this stdout line is REQUIRED on every hard-gate halt — both modes.

**4. Channel 2 — halt record file** (autonomous mode only):

Only write the machine-readable halt record when `autonomous == true` — the record is the orchestrator's branch signal and interactive operators do not need it.

```bash
if [ "$autonomous" = "true" ]; then
  write_halt_record \
    "$FEATURE" \
    "$HALT_REASON" \
    "$HEAL_PR_URL" \
    "$HEAL_PR_NUMBER" \
    "$SCENARIOS_JSON" \
    "$RECOVERY_STATUS"
fi
```

Write failure is non-fatal (ADR-006 non-fatal observability): the library returns non-zero and emits a stderr degradation notice, but Channels 1 and 3 still fire. Orchestrators tolerating the degraded signal path read stdout + exit code as sufficient.

**5. Channel 3 — exit code 10**:

Halt-for-review exit code is canonical `10` per PRD 139 additive exit-code taxonomy (extends PRD 130's 0-5; no collision).

```bash
exit "$(halt_exit_code)"
```

`halt_exit_code` echoes the literal `10`. The caller (this skill at top level) performs the actual `exit` so library functions never terminate the process directly.

**6. Do NOT proceed to Step 10**:

Process terminates at exit 10. Step 10 (Collect Test Evidence), Step 11 (Generate Delivery Document), Step 12 (Close Issue), and Step 13 (Prompt for /aod.document) are all skipped. The failure is recorded for review; delivery must be re-attempted after fixes (or explicit opt-out) before the feature can be closed.

**Integration notes** (for later waves):
- T032 (Wave 4 / US-5): heal-PR creation populates `HEAL_PR_URL` and `HEAL_PR_NUMBER` before Step 9e fires — until then, the fallback stdout form is emitted.
- T047 (Wave 5 / US-8): auto-fix loop determines final `RECOVERY_STATUS` before halt record is written — until then, `"not_attempted"` is correct.
- T022-T023 (Wave 4 / US-3): `~aod-orchestrate` and `~aod-run` skills read the halt record and branch.

---

## Step 10: Collect Test Evidence

Collect and archive test artifacts for the delivery audit trail. This step is entirely **non-fatal** (ADR-006): if any sub-step fails, log the error and continue to Step 11. The delivery workflow must never be blocked by test evidence collection.

### 10a: Auto-Detect Test Artifacts

Scan these specific locations at the **project root only** (no recursive scanning):

1. `.aod/test-results/` — AOD convention directory
2. `test-results/` — project root test results
3. `coverage/` — project root coverage reports
4. Files matching `junit*.xml`, `test-report.*`, `coverage.*` in the project root

Collect all discovered files into a `detected_files` list with file paths and sizes.

### 10b: Confirm or Prompt

**If files found**: Display discovered files with sizes:

```
Test artifacts detected:
  - test-results/junit.xml (12 KB)
  - coverage/lcov.info (45 KB)

Archive these to specs/{NNN}-*/test-results/? (Y/n/add more)
```

Use AskUserQuestion with options:
- "Archive all" — proceed with detected files
- "Add more" — prompt for additional file paths, then archive all
- "Skip" — no test evidence archived

**If no files found**: Use AskUserQuestion:

```
Question: "No test artifacts found in standard locations. What would you like to do?"
Header: "Test evidence"
Options:
  - "Provide paths": "Enter custom file paths to archive"
  - "Skip": "No test evidence for this feature"
```

### 10c: File Size Check

Before copying, check file sizes:
- Warn if any individual file exceeds 10 MB
- Warn if total size exceeds 50 MB per feature
- Display warning but do NOT block archival — the developer decides

### 10d: Sensitive Data Warning

Display once before archival:
```
Reminder: Review test artifacts for sensitive data (API keys, tokens, PII) before archival.
```

### 10e: Copy Files to Archive

Copy confirmed files to `specs/{NNN}-*/test-results/`:
1. Create directory if needed: `mkdir -p specs/{NNN}-*/test-results/`
2. Copy each file preserving original filenames
3. If copy fails for any file, log the error and continue with remaining files

### 10f: Extract Summary Metrics (Best-Effort)

Extract metrics from recognized formats:

**JUnit XML**: Parse `<testsuites>` or `<testsuite>` root element attributes using `xmllint --xpath`:
```bash
xmllint --xpath "string(/testsuites/@tests)" file.xml 2>/dev/null || \
xmllint --xpath "string(/testsuite/@tests)" file.xml 2>/dev/null
```
Extract: `tests`, `failures`, `errors`, `skipped` attributes.

**LCOV (.info/.lcov)**: Sum `LF:` and `LH:` records:
```bash
LF=$(grep "^LF:" file.lcov 2>/dev/null | cut -d: -f2 | paste -sd+ | bc)
LH=$(grep "^LH:" file.lcov 2>/dev/null | cut -d: -f2 | paste -sd+ | bc)
```
Compute coverage: `(LH / LF) * 100`.

**Other formats**: Archive as-is. Summary = "Manual review required".

If parsing fails for any format, use "Manual review required" as the summary.

### 10g: Store Test Evidence Data

Store the following for use in Step 11 (delivery document generation):
- `test_evidence.files[]`: List of archived files with paths and summaries
- `test_evidence.metrics`: Aggregate metrics (tests run, passed, failed, coverage %)
- `test_evidence.skipped`: Boolean indicating if evidence was skipped
- `test_evidence.notes`: Context string for the Notes field

---

## Step 11: Generate Delivery Document

Generate a persistent delivery document from retrospective data collected in Steps 1-8, E2E validation results from Step 9, and test evidence from Step 10.

### 11a: Re-ground on Template

Re-read `.aod/templates/delivery-template.md` before generating the document (KB Entry 9 re-grounding). This ensures the output structure matches the standardized template exactly.

### 11b: Resolve Specs Directory

Resolve the specs directory from the branch name:
1. Get the feature number from the branch: `git branch --show-current` → extract NNN prefix
2. Find the specs directory: `specs/{NNN}-*/`
3. If the directory does not exist, create it: `mkdir -p specs/{NNN}-{feature_kebab_name}/`

Store the resolved path as `specs_dir`.

### 11c: Populate Delivery Document

Using the template structure from `.aod/templates/delivery-template.md`, populate all sections from retrospective data:

1. **Header**: Feature number, name, today's date, branch name, PR number (from draft PR or git log)
2. **What Was Delivered**: Read `.aod/spec.md` for completed user stories and `.aod/tasks.md` for major completed tasks. Summarize as 3-7 user-visible outcomes (not implementation details).
3. **How to See & Test**: Extract verification steps from three sources and merge into numbered steps a developer can follow immediately:
   - **From `.aod/spec.md`**: Read each acceptance scenario's **Then** clause — each maps to one or more verification steps.
   - **From `.aod/plan.md`**: Extract any test commands, run commands, or manual testing instructions mentioned in the plan.
   - **From `.aod/tasks.md`**: Extract verification steps from task descriptions and checkpoint criteria.
   - **Format**: Number each step. Include specific CLI commands, file paths, or UI actions. Avoid vague instructions like "verify it works" — instead specify *what* to check and *how* (e.g., "Run `/aod.deliver 091` and confirm `specs/091-*/delivery.md` exists").
4. **Delivery Metrics**: Table with estimated_duration, actual_duration, and variance (computed as over/under/on-target)
5. **Surprise Log**: From `surprise_log` captured in Step 3
6. **Lessons Learned**: Table with `lesson_category`, `lesson_text`, and KB entry reference from Step 6
7. **Feedback Loop**: Count of `next_ideas` and list of each idea with GitHub Issue number
8. **Source Artifacts**: Paths to spec.md, plan.md, tasks.md, and PRD (from spec.md frontmatter if available)
9. **Test Evidence**: Populate both subsections of the Test Evidence section:
   - **E2E Validation Gate**: Read `e2e_validation.status`, `e2e_validation.gate_mode`, `e2e_validation.gate_result`, `e2e_validation.total`, `e2e_validation.passed`, `e2e_validation.failed`, `e2e_validation.skipped`, and `e2e_validation.failing_scenarios[]` from Step 9 output. Populate the E2E Validation Gate table and Failure Details field. If `e2e_validation.status` is `"skipped"`, use "N/A" for counts; for Failure Details, render `e2e_validation.skip_reason` when present (Feature 130 rich-shape — opt-out reason) else fall back to "E2E validation skipped" (legacy payloads). If `e2e_validation.status` is `"error"`, use "Error" for Status and the error message for Failure Details.
   - **Archived Artifacts**: Populate from `test_evidence` data collected in Step 10. If `test_evidence.skipped` is true, use "No test artifacts archived for this feature." If metrics were parsed successfully, populate the artifact table and Archived Artifact Metrics (tests run, passed, failed, coverage). If metrics could not be parsed, use "Manual review required" for the summary column.
10. **Documentation Updates**: Agent table populated from Step 3 of the command (documentation agent results)
11. **Cleanup**: Checklist items (left unchecked — will be checked during command Steps 7-11)

### 11c.1: Render Feature 139 Template Fields (US-6, FR-012..FR-014)

The post-T036 `.aod/templates/delivery-template.md` rewrite introduces three distinct Test Evidence subsections. This sub-step populates the new fields from the accumulated `e2e_validation.*` payload so a reviewer can answer "did the gate run, what ACs are mapped, what was opted out" at a glance.

**Test Evidence is now split into three subsections** (per PRD FR-004 + spec FR-012..FR-014):

1. **Test Scenarios (Living Documentation)** — answers *"what scenarios exist?"*
2. **Execution Evidence** — answers *"what happened when they ran?"*
3. **Manual Validation** — answers *"what was not automated?"* (conditional)

Populate each subsection as follows:

**1. Test Scenarios subsection**:

Template placeholders:
- `{#if e2e_validation.ac_coverage}` → iterate `e2e_validation.ac_coverage.coverage_by_ac[]` to render the AC→scenario mapping table. For each AC:
  - `{ac_id}` — from `coverage_by_ac[i].ac_id` (e.g., `US-01-AC-1`)
  - `{gwt_summary}` — short Given/When/Then summary (truncate to ~80 chars per cell for scan-ability; full text lives in the collapsible Gherkin block)
  - `{scenario_refs_or_manual_reason}` — if `coverage_by_ac[i].manual_only == true`: render `[MANUAL-ONLY] <reason>` from the matching `manual_only_acs[]` entry. Else render the `scenarios[]` array joined as `file:line, file:line, ...`.
  - `{Covered|Manual|Uncovered}` — derived: `manual_only == true` → `Manual`; `scenarios.length > 0` → `Covered`; else `Uncovered`.
- Totals line uses `total_acs`, `covered_count`, `manual_only_acs.length`, `uncovered_acs.length`.

**Empty-state handling** (FR-014):
- If `e2e_validation.ac_coverage.total_acs == 0` OR `e2e_validation.ac_coverage` is absent: render the `{#unless}` branch from the template — explicit row `| — | (No scenarios declared — zero ACs in spec.md) | — | — |`. Do NOT silently hide the table.

**Full Gherkin `<details>` block**:
- Iterate `e2e_validation.scenarios[]` (populated by tester agent in Step 9b); each element renders as a `gherkin`-fenced code block with `scenarios[i].gherkin_source`.
- When `scenarios[]` is empty, render the `{#unless}` branch with the `_(No scenarios declared — zero ACs in spec.md)_` italic.

**2. Execution Evidence subsection**:

- **E2E Validation Gate table**: populate all rows from `e2e_validation.{status,gate_mode,gate_result,passed,total,failed,skipped,duration_seconds}` exactly as the pre-existing Step 11c.9 logic did. This is unchanged by US-6; the fields are reused under the new subsection heading.
- **Failure Details**: comma-joined `e2e_validation.failing_scenarios[]`, else `"None"` on all-pass, else `"N/A"` on skipped/error.
- **Per-Scenario Results table**: iterate `e2e_validation.scenario_results[]` (populated by tester in Step 9b). Columns: name, status, duration_ms.
- **Command**: render `e2e_validation.invocation_command` (the full `/aod.deliver ...` line the user ran — captured at Step 0 before flag parsing). Fenced as ```bash.
- **Artifacts table**: rows from `test_evidence.files[]` (collected in Step 10). Columns: type, path, summary.
- **Archived Artifact Metrics** and **Notes**: pre-existing fields; continue populating from `test_evidence.metrics` as before.

**Recovery Actions table** (conditional, `{#if recovery_actions}` branch):

Render ONLY when `e2e_validation.recovery_actions[]` is non-empty. For each attempt:

| Attempt | Commit | Message | Result |
|---------|--------|---------|--------|
| `{attempt_number}/{total_attempts}` | `{commit_hash_short}` (7-char) | `{commit_message}` (e.g., `e2e-heal(attempt 1/2): update data-testid selector`) | `{result: pass\|fail}` |

Also render `**Final Recovery Status**: `{recovery_status: not_attempted|recovered|exhausted|scope_guard_escalated}`` below the table.

When `e2e_validation.recovery_actions[]` is empty (no auto-fix ran), omit the entire subsection — do NOT render an empty table. Template's `{#if}` conditional handles this.

**3. Manual Validation subsection** (conditional):

Render ONLY when:
- `e2e_validation.opt_out` exists and non-null (an accepted `--no-tests=<reason>` was logged at Step 0g), OR
- `e2e_validation.ac_coverage.manual_only_acs[]` is non-empty (at least one AC carried a `[MANUAL-ONLY] <reason>` marker)

Template uses `{#if opt_out or manual_only_acs}` — both paths may fire simultaneously; render both blocks inline:

- **Opt-out block** (`{#if opt_out}` branch):
  - `e2e_validation.opt_out.reason` — from `AOD_NO_TESTS_REASON` captured at Step 0d
  - `e2e_validation.opt_out.invoker` — from Step 0g resolution (git email or `"autonomous"`)
  - `e2e_validation.opt_out.timestamp` — from Step 0g UTC timestamp
  - Trailing note: `"See .aod/audit/deliver-opt-outs.jsonl for the full audit trail."` (template literal)

- **Manual-only ACs list** (`{#if manual_only_acs}` branch):
  - Iterate `e2e_validation.ac_coverage.manual_only_acs[]` (array of AC IDs) joined with `coverage_by_ac[]` lookup for reasons.
  - For each entry: `- AC {ac_id}: [MANUAL-ONLY] {reason}`. The reason comes from the matching `coverage_by_ac[i].manual_reason` (parsed by `ac-coverage-parse.sh` from the spec.md marker).

When neither condition is met, the entire `### Manual Validation` heading is suppressed — the template's outer `{#if opt_out or manual_only_acs}` block drops it.

**Payload construction**:

The `e2e_validation` payload consumed by this rendering step accumulates across multiple prior steps:

| Field | Populated In | Source |
|-------|--------------|--------|
| `e2e_validation.ac_coverage.*` | Step 9a.5 | `$COVERAGE_JSON` (from `build_ac_scenario_map`) |
| `e2e_validation.scenarios[]` | Step 9b | tester agent output |
| `e2e_validation.scenario_results[]` | Step 9c | tester agent parsed results |
| `e2e_validation.{status,gate_mode,gate_result,passed,total,failed,skipped,duration_seconds,failing_scenarios}` | Steps 9b-9d | canonical fields from PRD 130 + 9d assignments |
| `e2e_validation.invocation_command` | Step 0 | original `$0 $@` captured before parsing |
| `e2e_validation.recovery_actions[]` | Step 9c.5 (US-8) | auto-fix loop per-attempt records |
| `e2e_validation.recovery_status` | Step 9c.5 (US-8) | final loop outcome: `pending \| recovered \| exhausted \| scope_guard_escalated \| skipped_via_config \| escalated_to_heal_pr` |
| `e2e_validation.opt_out.{reason,invoker,timestamp,mode}` | Step 0g | audit-log inputs |
| `e2e_validation.ac_coverage.manual_only_acs[]` | Step 9a.5 | coverage map |

When `heal_attempts == 0` in `.aod/config.json` OR all tests pass on first run, `recovery_actions[]` is empty and the Recovery Actions subsection is suppressed by the template's `{#if recovery_actions}` conditional. `recovery_status` is `"skipped_via_config"` in the former case and `"pending"` (never transitioned) in the latter.

**Reference**: `.aod/templates/delivery-template.md` post-T036 rewrite.

### 11d: Write Delivery Document

Write the populated document to `{specs_dir}/delivery.md` using the Write tool.

Store the delivery document path in variable `delivery_doc_path` for use in Step 12.

### 11e: Non-Fatal Fallback Guard

If the file write in Step 11d fails (permissions, disk full, or any error), display the full delivery document content in the terminal as a fallback. The deliver workflow MUST NOT be blocked by a file write failure (FR-009, KB Entry 14).

**Missing optional data handling**: If `surprise_log`, `next_ideas`, or `lesson_text` are empty or unavailable, use "None" or "N/A" for those sections rather than leaving them blank or erroring.

### 11f: Mark Draft PR Ready

If a draft PR exists for the current branch, mark it ready for review:

```bash
# Find draft PR for current branch
PR_NUMBER=$(gh pr list --head "$(git branch --show-current)" --state open --json number --jq '.[0].number')

# Mark ready if found
if [ -n "$PR_NUMBER" ]; then
  gh pr ready "$PR_NUMBER"
fi
```

If `gh` is unavailable or no draft PR exists, skip silently (graceful degradation). If no draft PR exists, create a regular PR: `gh pr create --title "{NNN}: {Feature Name}" --body "..."`.

### 11g: Display Delivery Document

After writing (or after fallback display if write failed), show the full document content in the terminal so the developer can review it immediately.

```
AOD DELIVERY COMPLETE

Feature: {feature_name}
Delivery Document: {delivery_doc_path}

{Full content of the generated delivery.md}
```

---

## Step 12: Close Issue and Transition to Done

After all retrospective steps are complete, metrics posted, and KB entries created:

1. **Transition to `stage:done`**: Run `source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage "$issue_number" "done"` to move the label from `stage:deliver` to `stage:done`. This moves the issue to the Done column on the Projects board.
2. **Close the GitHub Issue**: Run `gh issue close "$issue_number" --comment "Feature delivered. Retrospective complete. See: specs/{NNN}-*/delivery.md"` where `{NNN}-*` is resolved from the `delivery_doc_path` variable set in Step 11d. This cross-references the delivery document from the GitHub Issue.
3. **Regenerate BACKLOG.md**: Run `.aod/scripts/bash/backlog-regenerate.sh` to remove the now-done item from the active backlog.
4. If `gh` is unavailable, skip silently (graceful degradation).

This step MUST be the very last GitHub operation, after all metrics, KB entries, and backlog regeneration from Step 8 are complete.

---

## Step 13: Prompt for /aod.document

After delivery is complete, prompt the user about the next lifecycle step:

```
Next step: Run `/aod.document` for post-delivery quality review.
This covers code simplification, docstrings, CHANGELOG, and API docs.

Run `/aod.document` now? (Y/n)
```

- If user selects "Y" or presses enter: Invoke `/aod.document`
- If user selects "n": Display: `"Skipped. Run /aod.document when ready for post-delivery quality review."`

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

---

## Edge Cases

- **No tasks.md**: Skip DoD validation, warn user
- **No spec.md**: Use branch name as feature name
- **Branch has no diverged commits**: Use today's date for actual duration calculation
- **gh CLI unavailable**: Skip all GitHub operations (issue creation, comments, label updates, backlog regeneration) — graceful degradation
- **Empty surprise log**: Re-prompt (required field)
- **Empty lesson text**: Re-prompt (required field)
- **INSTITUTIONAL_KNOWLEDGE.md missing**: Create it with standard header before appending
- **User selects "Mark remaining tasks as complete"**: Update tasks.md to mark all `- [ ]` as `- [x]` before proceeding
- **Multiple ideas from retrospective**: Create one GitHub Issue per idea

## Quality Checklist

- [ ] Definition of Done validated (all tasks complete or user override)
- [ ] Estimated duration captured from user
- [ ] Actual duration computed from branch creation date
- [ ] Surprise log captured (minimum 1 sentence)
- [ ] Next ideas prompted (optional; each creates GitHub Issue with `stage:discover`)
- [ ] Lessons learned captured with category and full description
- [ ] KB entry appended to INSTITUTIONAL_KNOWLEDGE.md with correct entry number
- [ ] Delivery metrics posted to GitHub Issue as comment
- [ ] Issue transitioned to `stage:deliver` label (start of retrospective)
- [ ] BACKLOG.md regenerated
- [ ] Test evidence collected or skipped (non-fatal, per ADR-006)
- [ ] Retrospective summary displayed with all metrics
- [ ] Issue transitioned to `stage:done` label (end of retrospective)
- [ ] GitHub Issue closed with closing comment
- [ ] User prompted to run `/aod.document` for post-delivery quality review

---

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "AC-coverage gate is too strict, I'll mark them MANUAL-ONLY" | `[MANUAL-ONLY]` is for non-automatable ACs (e.g. visual review). Don't use it as an escape hatch. |
| "I'll add `--no-tests` to bypass the failing E2E once" | Step 0d (line 60) requires `--no-tests=<reason>` with 10-500 chars; reason is appended to the audit log. |
| "MANUAL-ONLY needs no reason for trivial ACs" | Step 9a.5 exit 4 (line 607) halts with reason length below 10 chars; the AC ID and minimum are emitted to stderr. |
| "Pack contract block is missing — I'll silently skip the gate" | Step 9a exit 5 (line 542) routes through the unified error branch; status becomes `e2e_validation.status = "error"`. |
| "I can pass both `--no-tests` and `--require-tests` to be safe" | Step 0c (line 47) rejects this contradiction with exit 2; `--require-tests` is the deprecated former opt-in. |
| "Uncovered ACs can be deferred — I'll fix them post-merge" | Step 9a.5 step 5 (line 621) HALTS via Step 9e with `reason = "ac_coverage_fail"`, exit 10; no merge happens. |

## Red Flags

- Agent invokes `/aod.deliver` with `--no-tests=skip` (5 chars) and is surprised by Step 0d (line 60) rejection.
- Agent passes `--no-tests --require-tests` together, ignoring Step 0c (line 47) flag-conflict exit 2.
- Agent's `[MANUAL-ONLY]` reason is a placeholder like "TODO" instead of meeting Step 9a.5 (line 607) 10-char minimum.
- Agent skips the AC-coverage gate (Step 9a.5 line 553) when `e2e_validation.status` is unset and pack has a real contract.
- Agent treats Step 9a exit 5 (line 542) as a hard-block when it should resolve to `e2e_validation.status = "error"` and proceed to Step 10.
- Agent's audit log lacks the `<reason>` per Step 0d (line 71) integration note despite an active `--no-tests` opt-out.
