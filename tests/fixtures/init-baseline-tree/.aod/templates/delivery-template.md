# Delivery Document: Feature {FEATURE_NUMBER} — {FEATURE_NAME}

**Delivery Date**: {DATE}
**Branch**: `{BRANCH_NAME}`
**PR**: #{PR_NUMBER}

---

## What Was Delivered

{Bulleted list of 3-7 key accomplishments from completed user stories and major tasks. Focus on user-visible outcomes, not implementation details.}

---

## How to See & Test

{Numbered verification steps derived from acceptance criteria in spec.md, test/run commands from plan.md, and verification steps from tasks.md. Each step should include specific commands, file paths, or UI actions.}

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | {estimated_duration} |
| Actual Duration | {actual_duration} |
| Variance | {over/under/on-target with explanation} |

---

## Surprise Log

{What surprised the team during this feature. Captured during retrospective. Use "None" if nothing unexpected occurred.}

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| {lesson_category} | {lesson_text} | Entry {N} in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: {count or "None"}

{For each idea:}
- {idea_description} — Issue #{issue_number} (type:retro)

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/{NNN}-*/spec.md |
| Implementation Plan | specs/{NNN}-*/plan.md |
| Task Breakdown | specs/{NNN}-*/tasks.md |
| PRD | {prd_path from spec.md frontmatter} |

---

## Test Evidence

### Test Scenarios (Living Documentation)

This subsection answers: *"What scenarios exist?"* It maps every acceptance criterion in `spec.md` to the Gherkin scenario(s) that assert it. Full Gherkin is collapsed by default for scan-ability.

#### Acceptance Criteria Coverage

{#if e2e_validation.ac_coverage}
| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
{#each e2e_validation.ac_coverage.coverage_by_ac}
| {ac_id} | {gwt_summary} | {scenario_refs_or_manual_reason} | {Covered|Manual|Uncovered} |
{/each}

**Totals**: {e2e_validation.ac_coverage.total} ACs — {e2e_validation.ac_coverage.covered} covered, {e2e_validation.ac_coverage.manual_only} manual-only, {e2e_validation.ac_coverage.uncovered} uncovered
{/if}
{#unless e2e_validation.ac_coverage}
| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (No scenarios declared — zero ACs in spec.md) | — | — |
{/unless}

<details>
<summary>Full Gherkin</summary>

{#if e2e_validation.scenarios}
{#each e2e_validation.scenarios}
```gherkin
{gherkin_source}
```
{/each}
{/if}
{#unless e2e_validation.scenarios}
_(No scenarios declared — zero ACs in spec.md)_
{/unless}

</details>

### Execution Evidence

This subsection answers: *"What happened when they ran?"* The gate outcome, the command invoked, and any recovery actions that were applied.

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | {e2e_validation.status: pass/fail/skipped/error} |
| Gate Mode | {e2e_validation.gate_mode: hard/skipped-via-opt-out} |
| Gate Result | {e2e_validation.gate_result: pass/warn/block/skip} |
| Tests Passed | {e2e_validation.passed}/{e2e_validation.total} |
| Tests Failed | {e2e_validation.failed} |
| Tests Skipped | {e2e_validation.skipped} |
| Duration | {e2e_validation.duration_seconds}s |

**Failure Details**: {Comma-separated list of e2e_validation.failing_scenarios[], or "None" if all passed, or "N/A" if skipped/error}

#### Per-Scenario Results

| Scenario | Status | Duration |
|----------|--------|----------|
{#each e2e_validation.scenario_results}
| {name} | {status: pass/fail/skipped} | {duration_ms}ms |
{/each}

#### Command

```bash
{e2e_validation.invocation_command}
```

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| {artifact_type} | test-results/{filename} | {brief_summary} |

**Archived Artifact Metrics**:
- Tests Run: {test_count}
- Passed: {passed_count}
- Failed: {failed_count}
- Coverage: {coverage_pct or "N/A"}

**Notes**: {testing_context, e.g., "E2E validated via Playwright MCP", "Unit tests via pytest", or "No test artifacts archived for this feature"}

{#if recovery_actions}
#### Recovery Actions

Auto-fix loop committed the following attempts before the runner was re-invoked:

| Attempt | Commit | Message | Result |
|---------|--------|---------|--------|
{#each recovery_actions}
| {attempt_number}/{total_attempts} | `{commit_hash_short}` | {commit_message} | {result: pass/fail} |
{/each}

**Final Recovery Status**: `{recovery_status: not_attempted|recovered|exhausted|scope_guard_escalated}`
{/if}

{#if opt_out or manual_only_acs}
### Manual Validation

This subsection answers: *"What was not automated?"* Present when an opt-out was logged or any AC is marked `[MANUAL-ONLY]`.

{#if opt_out}
**Delivery proceeded with tests opted out.**

| Reason | Invoker | Timestamp |
|--------|---------|-----------|
| {opt_out.reason} | {opt_out.invoker} | {opt_out.timestamp} |

See `.aod/audit/deliver-opt-outs.jsonl` for the full audit trail.
{/if}

{#if manual_only_acs}
**Manual-only acceptance criteria** (carried from `spec.md`):

{#each manual_only_acs}
- AC {ac_id}: [MANUAL-ONLY] {reason}
{/each}
{/if}
{/if}

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | {count} | {status} |
| Architecture | architect | {count} | {status} |
| DevOps | devops | {count} | {status} |

---

## Cleanup

- [ ] Feature branch deleted
- [ ] All tasks complete
- [ ] No TBD/TODO in docs
- [ ] Committed and pushed
- [ ] GitHub Issue closed (`stage:done`)

**Feature {FEATURE_NUMBER} is now officially CLOSED.**
