# Render Tables: Step 11c.1 — Feature 139 Template Fields

This reference is loaded ONLY when `e2e_validation.status` is set (i.e., E2E validation was entered during Step 9). On a no-E2E close (Step 9 skipped because `.aod/stack-active.json` is absent), this reference is NOT loaded — Step 11c.1 renders "N/A" inline without loading this file.

---

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
