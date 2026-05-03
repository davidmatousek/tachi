---
description: Execute implementation with Architect checkpoints at critical phases - Streamlined v2
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Arguments

Parse optional flags from `$ARGUMENTS`. Flags can appear anywhere in the arguments string.

**Step 0a: Parse --no-security**

1. If `$ARGUMENTS` contains `--no-security`:
   - Set `skip_security = true`
   - Strip `--no-security` from `$ARGUMENTS` (trim extra whitespace)
   - Continue to Step 0b with remaining arguments

2. If `$ARGUMENTS` does NOT contain `--no-security`:
   - Set `skip_security = false`
   - Continue to Step 0b with `$ARGUMENTS` unchanged

**Step 0b: Parse --orchestrated**

1. If `$ARGUMENTS` contains `--orchestrated`:
   - Set `orchestrated = true`
   - Strip `--orchestrated` from `$ARGUMENTS` (trim extra whitespace)
2. If `$ARGUMENTS` does NOT contain `--orchestrated`:
   - Set `orchestrated = false`

**Step 0c: Parse --autonomous**

1. If `$ARGUMENTS` contains `--autonomous`:
   - Set `autonomous = true`
   - Strip `--autonomous` from `$ARGUMENTS` (trim extra whitespace)
2. If `$ARGUMENTS` does NOT contain `--autonomous`:
   - Set `autonomous = false`

**Step 0d: Parse --no-design-check**

1. If `$ARGUMENTS` contains `--no-design-check`:
   - Set `skip_design_check = true`
   - Strip `--no-design-check` from `$ARGUMENTS` (trim extra whitespace)
   - Continue to Step 0e with remaining arguments

2. If `$ARGUMENTS` does NOT contain `--no-design-check`:
   - Set `skip_design_check = false`
   - Continue to Step 0e with `$ARGUMENTS` unchanged

**Step 0e: Parse --no-tests**

1. If `$ARGUMENTS` contains `--no-tests`:
   - Set `skip_tests = true`
   - Strip `--no-tests` from `$ARGUMENTS` (trim extra whitespace)
   - Continue to Step 0f with remaining arguments

2. If `$ARGUMENTS` does NOT contain `--no-tests`:
   - Set `skip_tests = false`
   - Continue to Step 0f with `$ARGUMENTS` unchanged

**Step 0f: Parse --require-tests**

1. If `$ARGUMENTS` contains `--require-tests`:
   - Set `require_tests = true`
   - Strip `--require-tests` from `$ARGUMENTS` (trim extra whitespace)
   - **Conflict check**: If both `skip_tests` and `require_tests` are true, `skip_tests` takes precedence (test execution is skipped entirely). Display: `"Warning: --no-tests and --require-tests both present. --no-tests takes precedence (tests skipped)."`
   - Continue to Step 0g with remaining arguments

2. If `$ARGUMENTS` does NOT contain `--require-tests`:
   - Set `require_tests = false`
   - Continue to Step 0g with `$ARGUMENTS` unchanged

**Step 0g: Pre-Flight Validation (Session Resume)**

Before proceeding, check for uncommitted work and handoff prerequisites:

1. Run `git status --porcelain`. If output is non-empty:
   - Display: `"Pre-flight: {N} uncommitted change(s) detected. Auto-committing."`
   - Stage and commit with message `"chore(NNN): checkpoint before build resume"`, then continue

2. Check for `specs/{NNN}-*/NEXT-SESSION.md` (derive NNN from current branch):
   - If found: read the file, display the **Next Actions** section
   - Ask: `"Handoff found. Are all prerequisites met? [Yes / Review]"`
   - If **Review**: display full NEXT-SESSION.md, then re-ask
   - If **Yes**: continue to Step 1
   - If `autonomous == true`: auto-select **Yes**
   - If not found: continue silently

## Overview

Executes feature implementation with Architect checkpoint reviews at priority boundaries.

**Flow**: Validate tasks → Check checklists → Load context → Setup project → Execute waves with parallel agents → Checkpoint reviews → Final validation → Design quality gate → Security scan → Report completion

**Key Feature**: Architect reviews at P0->P1->P2 boundaries for governed quality gates.

## Step 1: Validate Prerequisites

1. Get branch: `git branch --show-current` --> must match `NNN-*` pattern
2. Find tasks: `specs/{NNN}-*/tasks.md` --> must exist
3. Parse frontmatter: Verify all three sign-offs (PM, Architect, Team-Lead) are APPROVED
4. Find assignments: `specs/{NNN}-*/agent-assignments.md` --> must exist
5. If validation fails: Show error with required workflow order and exit
6. Detect resume state: Scan tasks.md for `[X]` marked tasks. Count completed vs total tasks per wave from agent-assignments.md.
   - If resuming (some waves complete): Display "RESUMING: Waves 1-N complete, starting at Wave {N+1}"
   - If fresh start: Display "Starting implementation from Wave 1"
7. **GitHub Lifecycle Update (early)**: Move the feature's GitHub Issue to `stage:build` at the *start* of implementation. The issue number is the NNN prefix extracted from the branch in step 1 (e.g., branch `086-my-feature` → issue `86`). Run:
   ```bash
   bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage NNN build'
   ```
   Then regenerate BACKLOG.md:
   ```bash
   bash .aod/scripts/bash/backlog-regenerate.sh
   ```
   If `gh` is unavailable or the issue does not exist, skip silently (graceful degradation).

## Step 2: Check Checklists and Load Context

### 2a: Check Checklists Status

If `specs/{NNN}-*/checklists/` exists:

1. Scan all checklist files in the checklists/ directory
2. For each checklist, count:
   - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
   - Completed items: Lines matching `- [X]` or `- [x]`
   - Incomplete items: Lines matching `- [ ]`
3. Create a status table:

   | Checklist | Total | Completed | Incomplete | Status |
   |-----------|-------|-----------|------------|--------|
   | ux.md     | 12    | 12        | 0          | PASS   |
   | test.md   | 8     | 5         | 3          | FAIL   |
   | security.md | 6   | 6         | 0          | PASS   |

4. Calculate overall status:
   - **PASS**: All checklists have 0 incomplete items
   - **FAIL**: One or more checklists have incomplete items

5. **If any checklist is incomplete**:
   - Display the table with incomplete item counts
   - **If `autonomous == true`**: Auto-select `"Proceed"`. Display: `"Auto-selected: Proceed past incomplete checklists (autonomous mode)"`. Continue to step 2b.
   - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
   - Wait for user response before continuing
   - If user says "no" or "wait" or "stop", halt execution
   - If user says "yes" or "proceed" or "continue", proceed to step 2b

6. **If all checklists are complete**: Display the table showing all checklists passed, proceed to step 2b

### 2b: Load Implementation Context

1. **REQUIRED**: Read `tasks.md` for the complete task list and execution plan
2. **REQUIRED**: Read `plan.md` for tech stack, architecture, and file structure
3. **REQUIRED**: Read `spec.md` for requirements context
4. **REQUIRED**: Parse `agent-assignments.md` for task->agent mapping and wave definitions
5. **IF EXISTS**: Read `data-model.md` for entities and relationships
6. **IF EXISTS**: Read `contracts/` for API specifications and test requirements
7. **IF EXISTS**: Read `research.md` for technical decisions and constraints
8. **IF EXISTS**: Read `quickstart.md` for integration scenarios
9. **IF EXISTS**: Read `.aod/stack-active.json` for active stack pack state. If a pack is active, note the pack name for agent dispatch in Step 4.

### 2c: Define Checkpoints

| Checkpoint | After Waves | Description | Blocking |
|------------|-------------|-------------|----------|
| P0 | 1, 2 | POC validation - Go/No-Go decision | Yes |
| P1 | 3, 4, 5 | Core functionality - Production cutover | Yes |
| P2 | 6, 7 | All features - Pre-final review | No |

## Step 3: Project Setup Verification

Before executing waves, verify the project environment is properly configured.

**Detection and Creation Logic**:
- Check if the repository is a git repo (`git rev-parse --git-dir 2>/dev/null`) --> create/verify `.gitignore` if so
- Check if `Dockerfile*` exists or Docker in plan.md --> create/verify `.dockerignore`
- Check if `.eslintrc*` or `eslint.config.*` exists --> create/verify `.eslintignore`
- Check if `.prettierrc*` exists --> create/verify `.prettierignore`
- Check if `.npmrc` or `package.json` exists --> create/verify `.npmignore` (if publishing)
- Check if terraform files (`*.tf`) exist --> create/verify `.terraformignore`
- Check if helm charts present --> create/verify `.helmignore`

**If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only.
**If ignore file missing**: Create with full pattern set for detected technology.

**Common Patterns by Technology** (from plan.md tech stack):
- **Node.js/JavaScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
- **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
- **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
- **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
- **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
- **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

**Tool-Specific Patterns**:
- **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
- **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
- **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`

## Step 4: Wave Execution with Checkpoints

For each wave:

1. **Skip if complete**: Check if all wave tasks marked `[X]` in tasks.md
2. **Group by agent**: Map tasks to specialized agents from agent-assignments.md
3. **Launch parallel**: Send **SINGLE message with multiple Task calls** for true parallelism
   - Use [Agent Registry](.claude/agents/) for task->agent mapping
   - Agent assignments from `agent-assignments.md` take precedence
   - **Stack pack persona injection**: If `.aod/stack-active.json` indicates an active pack, and the dispatched agent is Specialized (frontend-developer, senior-backend-engineer, security-analyst, tester, code-reviewer, devops) or Hybrid (ux-ui-designer, debugger), append to the agent's task prompt: "Before executing, read `stacks/{pack}/agents/{agent-name}.md` as supplementary stack-specific context for conventions, anti-patterns, and guardrails." Core agents (product-manager, architect, team-lead, orchestrator, web-researcher) MUST NOT receive persona injection.

4. **Verify completion**: Check all wave tasks marked `[X]`

5. **Post-wave test execution** (sub-step 4.5):

   Run the project's existing test suite after each wave that produces code changes to catch regressions early.

   **5a. Skip check**:
   - If `skip_tests == true`: skip entirely with message `"Test execution skipped (--no-tests)"`
   - Check if the wave produced code file changes via `git diff --name-only` filtered to source extensions (`.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go`, `.rs`, `.java`, `.rb`, `.cs`). If no code files changed: skip with message `"No code file changes in this wave. Skipping post-wave tests."`

   **5b. Detect test runner**:
   Follow this 5-level precedence chain. Use the first match:
   1. **Stack pack**: If `.aod/stack-active.json` exists and contains a `test_command` field, use that command
   2. **package.json**: If `package.json` exists and has a `scripts.test` entry (and it is not the default `echo "Error: no test specified"`), use `npm test`
   3. **pytest**: If `pytest.ini`, `pyproject.toml` (with `[tool.pytest]` section), or `setup.cfg` (with `[tool:pytest]` section) exists, use `pytest`
   4. **Makefile**: If `Makefile` exists and contains a `test:` target, use `make test`
   5. **None found**: Skip with message `"No test runner detected. Skipping post-wave tests."` and continue to sub-step 6 (checkpoint review)

   **5c. Execute tests and capture output**:
   - Run the detected test command
   - Capture stdout/stderr to `specs/{NNN}-*/test-results/wave-{NN}/failures.log`
   - Parse exit code and output for pass/fail/skip counts
   - Extract individual test names and statuses when structured output is available:
     - **Jest**: Parse JSON reporter output (if available) or summary lines
     - **pytest**: Parse JUnit XML output (if available) or summary line
     - **Other runners**: Parse summary line for aggregate counts
   - Surface only a summary line in context (per ADR-010 disk-offload principle): `"{pass} passed, {fail} failed, {skip} skipped"`
   - If output exceeds 3 failure names, show only the first 3 followed by `"... and {N} more"`

   **5c-cov. Capture coverage data** (when available):
   - Detect coverage tooling availability by checking:
     - **Jest**: If `--coverage` flag is supported (check `package.json` for `jest` config or `jest.config.*`), re-run with `npx jest --coverage --json` or check if coverage output was already produced
     - **pytest**: If `pytest-cov` is installed (check for `pytest-cov` in requirements files or `pyproject.toml`), re-run with `pytest --cov --cov-report=json` or check existing output
     - **Other runners**: Check for coverage output files in common locations (`coverage/`, `.nyc_output/`, `htmlcov/`)
   - If coverage tooling is available and produces output:
     - Write `specs/{NNN}-*/test-results/wave-{NN}/coverage.json` per data-model.md schema with `schema_version: "1.0"`
     - Calculate `delta_from_previous` by loading the previous wave's `coverage.json` (if it exists). Set to `0` if this is the first wave with coverage.
     - Calculate `new_code_coverage_pct` as the coverage percentage of files changed in this wave only (when the runner supports per-file reporting)
     - Display: `"Coverage: {total_coverage_pct}% ({delta:+n.n}% from previous wave)"`
   - If no coverage tooling is detected: skip silently. Do NOT fail or warn — coverage is opportunistic.

   **5d. Classify failures**:
   - Load previous wave's `results.json` from `specs/{NNN}-*/test-results/wave-{NN-1}/` (if it exists)
   - **When structured output is available** (individual test names from Jest JSON or pytest JUnit XML):
     - Compare at individual test level using test names as identifiers
     - **Regression**: Test existed in previous wave AND passed, now fails → gate-triggering
     - **New failure**: Test did not exist in previous wave results → warning, not regression
     - **Pre-existing**: Test existed in previous wave AND was already failing → informational only
   - **When only aggregate output is available** (no structured runner):
     - Compare total pass/fail/skip counts against previous wave
     - If fail count increased: classify the delta as potential regressions
     - If fail count unchanged or decreased: classify as pre-existing
   - **First wave** (no previous results): All failures classified as "pre-existing" or "new" — no regressions can be detected. Gate still runs but only reports results.

   **5e. Gate decision**:
   - **All tests pass**: Continue to sub-step 6 (checkpoint review). Display: `"All tests passed."`
   - **Regressions detected + soft gate** (default, `require_tests == false`):
     - Display regression details (test names if available, counts if not)
     - **If `autonomous == true`**: Auto-select "Skip with warning". Display: `"Auto-selected: Skip regressions with warning (autonomous mode)"`. Log decision as `"skip"` in `results.json`, continue to sub-step 6.
     - Otherwise prompt: `"Regressions detected. (A) Fix now via debugger agent, (B) Skip with warning, (C) Halt build"`
     - If Fix: invoke debugger agent with failure context, re-run tests after fix
     - If Skip: log decision as `"skip"` in `results.json`, continue to sub-step 6
     - If Halt: stop execution
   - **Regressions detected + hard gate** (`require_tests == true`):
     - Display: `"Hard gate: {count} regression(s) detected. Wave blocked until tests pass."`
     - **If `autonomous == true`**: Auto-invoke debugger agent (1 retry attempt). If fix succeeds, continue. If still failing after retry, halt build. Display: `"Auto-invoked debugger (autonomous mode). {result}"`
     - Otherwise: Invoke debugger agent to attempt fix
     - Re-run tests after fix attempt
     - If still failing: halt build
   - **Only new failures or pre-existing failures** (no regressions): Continue with informational message. Gate does not trigger on non-regression failures.
   - **Runner error** (non-zero exit code AND no parseable test results):
     - This is a test runner environment error, not a code regression
     - **If `autonomous == true`**: Auto-select "Skip and continue". Display: `"Auto-selected: Skip runner error (autonomous mode)"`. Log decision as `"error"` in `results.json`, continue.
     - Otherwise prompt: `"Test runner error (not a test failure). (A) Skip and continue, (B) Retry, (C) Halt build"`
     - Do NOT classify runner errors as regressions
   - Display summary: `"{pass} passed, {fail} failed, {skip} skipped — {regression_count} regression(s), {new_count} new, {preexisting_count} pre-existing"`

   **5f. Persist test artifacts**:
   - Create directory: `specs/{NNN}-*/test-results/wave-{NN}/` (where NN is the zero-padded wave number)
   - Write `results.json` to the wave directory with the following structure (per data-model.md schema):
     ```json
     {
       "schema_version": "1.0",
       "wave": {wave_number},
       "timestamp": "{ISO 8601 timestamp}",
       "test_runner": "{detected test command from 5b}",
       "execution_duration_ms": {duration},
       "gate_mode": "{soft|hard|off}",
       "gate_decision": "{pass|warn|skip|block|error}",
       "totals": { "pass": {n}, "fail": {n}, "skip": {n} },
       "classification": {
         "regressions": {n},
         "new_failures": {n},
         "pre_existing": {n}
       },
       "regressions": ["{test_name}", ...],
       "new_failures": ["{test_name}", ...],
       "pre_existing": ["{test_name}", ...],
       "tests": [{ "name": "{test_name}", "status": "{pass|fail|skip}", "duration_ms": {n} }, ...]
     }
     ```
   - The `tests` array is populated only when structured output is available (Jest JSON, pytest JUnit XML). Omit the field when only aggregate counts are available.
   - The `regressions`, `new_failures`, and `pre_existing` arrays contain test names when structured output is available; empty arrays when only aggregate counts are available.
   - Write `failures.log` to the wave directory only when `totals.fail > 0`. This file contains the raw stdout/stderr captured in sub-step 5c.
   - If the skip check (5a) caused test execution to be skipped, do NOT write any artifacts for this wave.

   **Post-wave test generation** (sub-step 4.6):

   After the regression gate passes (sub-step 4.5 complete), invoke the tester agent to generate unit and integration tests for code produced in the current wave.

   **6a. Skip check**:
   - If `skip_tests == true`: skip entirely (already handled by 5a, but guard here too)
   - If no code file changes in this wave: skip (no code to generate tests for)
   - If the regression gate halted the build: skip (build is stopping)

   **6b. Invoke tester agent**:
   - Launch the tester agent via the Agent tool with `subagent_type: "tester"`
   - Provide the agent with:
     - The wave's changed files: full diff if fewer than 10 files changed, file paths + function signatures if 10 or more files changed
     - Feature spec path: `specs/{NNN}-*/spec.md`
     - Active stack pack persona (if `.aod/stack-active.json` exists): append "Before executing, read `stacks/{pack}/agents/tester.md` as supplementary stack-specific context"
   - Scope: unit and integration tests ONLY — do NOT generate E2E tests
   - Per ADR-010: the tester agent writes details to `.aod/results/tester.md` and returns only status + count + path

   **6c. Execute generated tests**:
   - After the tester agent returns, re-run the test suite (using the same runner detected in 5b) to validate that generated tests pass
   - Append generated test results to the wave's `results.json` — add a `generated_tests` field:
     ```json
     "generated_tests": {
       "count": {number_of_tests_generated},
       "pass": {n},
       "fail": {n}
     }
     ```
   - If generated tests fail: log as informational (do NOT re-trigger the regression gate — these are new tests, not regressions)

6. **Checkpoint review** (if wave triggers checkpoint):
   - Launch architect agent for review
   - **Include test execution context**: If `results.json` exists for any wave in the checkpoint scope, include a "Test Execution Summary" section in the architect's review prompt:
     ```
     Test Execution Summary (Waves {start}-{end}):
     - Pass: {sum_pass} | Fail: {sum_fail} | Skip: {sum_skip}
     - Regressions: {sum_regressions}
     - Gate decisions: {Wave N: decision, ...}
     - Coverage: {end_pct}% ({delta:+n.n}% across checkpoint scope) | "No coverage data"
     ```
     This gives the architect visibility into test health when making checkpoint decisions. Omit this section if no waves in the checkpoint scope had test execution.
   - Parse STATUS: APPROVED / APPROVED_WITH_CONCERNS / CHANGES_REQUESTED / BLOCKED
   - If BLOCKED on blocking checkpoint: spawn debugger, retry, or exit
   - If CHANGES_REQUESTED: spawn appropriate agent to fix, retry review

7. **Wave continuation rule** (context-safe multi-wave execution):

   After each non-final wave, decide whether to **continue** or **stop**:

   **Continue to next wave** if:
   - `orchestrated == true` (no wave ceiling — orchestrator manages context), OR
   - This conversation has executed fewer than 3 waves so far

   **Stop and hand off** if:
   - `orchestrated == false` AND this conversation has executed 3 or more waves (hard ceiling)

   When `orchestrated == true`, log a soft warning at wave 5:
   ```
   Note: Wave 5+ reached. Context usage may be high. Continuing under orchestrated mode.
   ```

   **When continuing**: Display a brief wave summary and proceed to the next wave:
   ```
   WAVE {N}/{total} COMPLETE — {completed}/{total} tasks ({percentage}%)
   Continuing to Wave {N+1}...
   ```

   **When stopping** (only when `orchestrated == false`): Run `/continue` to generate a NEXT-SESSION.md handoff file.

   **Re-ground before output**: Re-read the template below exactly. Do not paraphrase, do not substitute final-completion commentary (e.g., "IMPLEMENTATION COMPLETE", "READY FOR DEPLOYMENT", "structural complete"), and do not add status qualifiers. Those strings are reserved for Step 8 (true final completion) and MUST NOT appear when stopping at the wave ceiling — their presence would misrepresent pending work as finished.

   Then display:
   ```
   WAVE {N}/{total} COMPLETE

   Tasks completed this wave: {count}
   Total progress: {completed}/{total} tasks ({percentage}%)

   Next: Wave {N+1} — {brief description from agent-assignments.md}

   To continue: Start a new conversation and run `/aod.build`
   The command will automatically resume from Wave {N+1}.

   Resume prompt:
     claude "Resume {feature} implementation (branch: {branch}). Waves 1-{N} complete. Run /aod.build to continue with Wave {N+1}."
   ```
   Then **STOP EXECUTION**.

   **Last wave exception**: If this is the LAST wave, always proceed to Step 5 (Final Validation) regardless of context state.

### Implementation Execution Rules

During wave execution, agents must follow these rules:

- **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
- **File-based coordination**: Tasks affecting the same files must run sequentially within a wave
- **Setup first**: Initialize project structure, dependencies, configuration in early waves
- **Tests before code**: Write tests for contracts, entities, and integration scenarios first
- **Core development**: Implement models, services, CLI commands, endpoints
- **Integration work**: Database connections, middleware, logging, external services
- **Polish and validation**: Unit tests, performance optimization, documentation

### Progress Tracking and Error Handling

- Report progress after each completed task
- Halt execution if any non-parallel task fails
- For parallel tasks [P], continue with successful tasks, report failed ones
- Provide clear error messages with context for debugging
- Suggest next steps if implementation cannot proceed
- **IMPORTANT**: For completed tasks, mark the task as `[X]` in tasks.md

## Step 5: Final Validation (Last Wave Only)

This step runs ONLY after the LAST wave completes (i.e., all tasks in all waves are marked `[X]`). For non-final waves, the wave continuation rule (sub-step 7) stops execution instead.

After all waves complete:

1. Verify all tasks marked `[X]`
2. Check that implemented features match the original specification
3. Validate that tests pass and coverage meets requirements
4. Confirm the implementation follows the technical plan
5. Launch final reviews in parallel (single message, multiple Task calls):

| Agent | subagent_type | Focus |
|-------|---------------|-------|
| Architect | architect | Overall architecture, security, production readiness |
| Code Review | code-reviewer | Code quality (if code files changed) |
| Security | security-analyst | Security posture (if auth/secrets changed) |

6. Parse all STATUS results

## Step 6: Design Quality Gate (Last Wave Only)

This step runs ONLY after Step 5 (Final Validation) completes. It validates UI output against codified design standards.

### 6a: Check Skip Conditions

1. If `skip_design_check` is true (from Step 0d):
   - Write `specs/{NNN}-*/design-check.md` with content: `Design Quality Check: Skipped (--no-design-check)` + current timestamp
   - Record: design_check_status = "Skipped (--no-design-check)"
   - Proceed to Step 7

2. If no UI files changed (pre-check via `git diff --name-only main...HEAD` filtered to `*.css`, `*.jsx`, `*.tsx`, `*.html`):
   - Record: design_check_status = "Skipped (no UI files changed)"
   - Proceed to Step 7

### 6b: Run Automated Checks

Run these 4 grep-based checks on files changed on the feature branch:

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Font compliance | Grep for banned font names (Inter, Roboto, Arial, Open Sans, Lato) as primary font in CSS/JSX/TSX files | Zero occurrences as primary font declaration |
| Spacing compliance | Grep for arbitrary Tailwind values (`\[.*px\]`, `\[.*rem\]`) in new/modified files | Zero occurrences |
| Shadow count | Grep for distinct `--shadow-` custom property definitions | ≤ 5 named levels |
| Reduced motion | Grep for `motion-safe:` / `motion-reduce:` / `prefers-reduced-motion` | Present if animations exist in changed files |

### 6c: Handle Results

1. **PASSED** (all checks pass): Record design_check_status = "Passed"; proceed to Step 7
2. **FINDINGS** (one or more checks fail):
   - Display findings table with file locations and specific violations
   - **If `autonomous == true`**: Auto-acknowledge findings. Record design_check_status = "Findings acknowledged ({count} finding(s))"; proceed to Step 7.
   - Otherwise ask: "Design quality findings detected. (A) Fix now, (B) Acknowledge and proceed, (C) Abort build"
   - If Fix now: halt build; display "Fix the identified issues and re-run `/aod.build`"
   - If Acknowledge: record design_check_status = "Findings acknowledged ({count} finding(s))"; proceed to Step 7
   - If Abort: stop execution

## Step 7: Security Scan (Last Wave Only)

This step runs ONLY after Step 6 (Design Quality Gate) completes. It analyzes all code files and dependency manifests changed on the feature branch for OWASP Top 10 vulnerabilities and known CVE patterns.

### 7a: Check Skip Conditions

1. If `skip_security` is true (from Step 0a):
   - Write `specs/{NNN}-*/security-scan.md` with content: `Security Scan: Skipped (--no-security)` + current timestamp
   - Record: security_status = "Skipped (--no-security)"
   - Proceed to Step 8

2. If no code files and no dependency manifests changed (pre-check via `git diff --name-only main...HEAD`):
   - Record: security_status = "Skipped (no code or manifest files changed)"
   - Proceed to Step 8

### 7b: Invoke /security Skill

Invoke the `security` skill via the Skill tool:
```
Skill tool: skill="security"
```

The skill handles all analysis steps internally (file detection, SAST, SCA, severity gate, artifact writing, commit strategy). Parse the result on completion.

### 7c: Handle Result

1. **PASSED** (no findings): Record security_status = "Passed — no issues found"; proceed to Step 8
2. **FINDINGS ACKNOWLEDGED**: Record security_status = "Findings acknowledged ({count} finding(s))"; proceed to Step 8
3. **BLOCKED** (developer selected "Fix now" or "Abort"):
   - If Fix now: halt build session; display "Fix the identified issues and re-run `/aod.build` to resume at Step 7"
   - If Abort: stop execution entirely
4. **ERROR**:
   - **If `autonomous == true`**: Auto-select `"Skip and complete build"`. Display: `"Auto-selected: Skip security scan error (autonomous mode)"`. Record security_status = "Error — skipped ({error_message})"; proceed to Step 8.
   - Surface AskUserQuestion: "Security scan encountered an error: {error_message}. (A) Retry, (B) Skip and complete build, (C) Abort build"
   - If Retry: re-invoke skill (step 7b)
   - If Skip: record security_status = "Error — skipped ({error_message})"; proceed to Step 8
   - If Abort: stop execution

## Step 8: Report Completion (MANDATORY — continue immediately after Step 7)

**IMPORTANT**: After Step 7 completes (whether scan passed, was acknowledged, or was skipped), you MUST immediately proceed to this step. Do NOT stop or wait for user input between Steps 7 and 8.

**Re-ground before output**: Re-read the template below exactly. Do not paraphrase or substitute checkpoint/review commentary into the template structure.

Display summary:
```
IMPLEMENTATION COMPLETE

Feature: {feature_number}
Tasks: {completed}/{total}
Waves: {wave_count}

Checkpoint Results:
- P0: {status}
- P1: {status}
- P2: {status}

Test Execution (Step 4.5):
- Waves tested: {waves_tested_count}/{total_wave_count}
- Total: {total_pass} passed, {total_fail} failed, {total_skip} skipped
- Regressions detected: {total_regressions}
- Gate decisions: {comma-separated list of "Wave N: {decision}" for each tested wave}
- Coverage trend: {start_pct}% → {end_pct}% ({delta}%) | "No coverage tooling detected"
- Artifacts: specs/{NNN}-*/test-results/

Final Validation:
- Architect: {status}
- Code Review: {status}
- Security: {status}

Design Quality Gate (Step 6):
- Font compliance: {status}
- Spacing compliance: {status}
- Shadow count: {status}
- Reduced motion: {status}
- /design-check: {design_check_status}

Security Scan (Step 7):
- SAST: {sast_status} ({code_file_count} file(s) scanned)
- SCA: {sca_status} ({manifest_count} manifest(s) audited)
- Report: specs/{NNN}-*/security-scan.md
- /security: {security_status}

{If all APPROVED: "READY FOR DEPLOYMENT"}
{If BLOCKED: "Issues require resolution"}

Deferred Issues: {count}

Next: /aod.deliver FEATURE: {feature_number} - {feature_name}
Then: /aod.document (code quality review, CHANGELOG, docstrings)
```

**Generate build-wide summary.json**:

After displaying the completion report, aggregate all per-wave `results.json` files into a single `specs/{NNN}-*/test-results/summary.json`:

```json
{
  "schema_version": "1.0",
  "feature": "{NNN}-{feature-name}",
  "total_waves": {total_wave_count},
  "waves_tested": {waves_with_test_execution},
  "waves_skipped": {waves_where_tests_were_skipped},
  "totals": {
    "pass": {sum_of_all_wave_pass_counts},
    "fail": {sum_of_all_wave_fail_counts},
    "skip": {sum_of_all_wave_skip_counts}
  },
  "total_regressions": {sum_of_all_wave_regression_counts},
  "coverage_trend": {
    "start_pct": {first_wave_coverage_pct_or_null},
    "end_pct": {last_wave_coverage_pct_or_null},
    "delta": {end_minus_start_or_null}
  },
  "gate_decisions": [
    { "wave": {n}, "decision": "{pass|warn|skip|block|error}" }
  ]
}
```

- Set `coverage_trend` to `null` (not an object with null fields) when no coverage tooling was detected in any wave. This provides explicit null semantics per architect concern.
- `waves_tested` counts only waves where tests actually executed (not skipped by flag or no-code-change).
- `gate_decisions` includes one entry per wave that had test execution, in wave order.
- If no waves had test execution (e.g., `--no-tests` flag), write summary.json with `waves_tested: 0`, empty `gate_decisions`, and zeroed totals.

**Structured completion signal** (orchestrated mode only):

When `orchestrated == true`, append a machine-readable signal after the completion report:

```
<!-- AOD_BUILD_RESULT:COMPLETE:waves={wave_count}:tasks={completed}/{total} -->
```

When `orchestrated == true` and the build stops early (any reason):

```
<!-- AOD_BUILD_RESULT:PARTIAL:waves={completed_waves}/{total_waves}:tasks={completed}/{total}:reason={reason} -->
```

When `orchestrated == false` (standalone): no change — keep current display format only.

## Quality Checklist

- [ ] All Triad sign-offs approved before execution
- [ ] Checklists verified (or user acknowledged incomplete)
- [ ] Implementation context fully loaded (tasks, plan, spec, assignments)
- [ ] Project setup verified (ignore files for detected technologies)
- [ ] Agent-assignments.md parsed for task->agent mapping
- [ ] Waves executed with parallel agent spawning
- [ ] Wave continuation respected (max 3 waves standalone, no ceiling when orchestrated)
- [ ] --orchestrated flag parsed correctly (when present)
- [ ] --autonomous flag parsed correctly (when present)
- [ ] Autonomous defaults applied for incomplete checklists and security scan errors (when autonomous)
- [ ] Wave ceiling skipped when orchestrated (no hard stop at 3)
- [ ] Structured completion signal emitted when orchestrated
- [ ] TDD approach followed (tests before implementation)
- [ ] Architect checkpoint reviews at P0, P1, P2 boundaries
- [ ] Blocking checkpoint issues resolved before proceeding
- [ ] Final validation completed (Architect + Code + Security)
- [ ] All tasks marked [X] in tasks.md
- [ ] Design Quality Gate executed or explicitly skipped with reason (--no-design-check)
- [ ] Design quality findings acknowledged or build halted
- [ ] Design quality status recorded in completion report
- [ ] --no-design-check flag parsed correctly (when present)
- [ ] Security Scan step executed or explicitly skipped with reason (--no-security)
- [ ] Security scan findings acknowledged or build halted on CRITICAL/HIGH
- [ ] Security scan status recorded in completion report
- [ ] Implementation summary displayed
- [ ] --no-tests flag parsed correctly (when present)
- [ ] --require-tests flag parsed correctly (when present)
- [ ] Test execution ran after code-producing waves or was skipped with reason
- [ ] Test artifacts written to `specs/{NNN}-*/test-results/wave-{NN}/` when tests executed
- [ ] Test regression classification performed (regression/new/pre-existing)
- [ ] Autonomous mode gate decisions logged when `--autonomous` active
- [ ] Test summary included in completion report
- [ ] Coverage data captured when tooling available, skipped gracefully when not

Note: This command requires a complete task breakdown in tasks.md with Triad sign-offs. If tasks are incomplete or missing, run `/aod.tasks` first to generate the task list with governance approval. After build and delivery, run `/aod.document` for code quality review (simplification, docstrings, CHANGELOG, API docs).

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Architect checkpoint is overkill for this small change" | Small changes accumulate. The checkpoint catches drift, not the change. |
| "Test failure is flaky, I'll just re-run" | F139 was built to prevent this. Use `--no-tests` (build) or `--no-tests=<reason>` (deliver) only with audit log if you really need to skip. |
| "I'll skip Step 7 security scan — small change, no auth/secrets touched" | Step 7a records `Skipped (--no-security)` in `security-scan.md` only when the flag is explicit. Skipping silently leaves no audit trail. Pass `--no-security` (Step 0a) if intentional. |
| "I'll bump past the 3-wave ceiling so I can finish in one session" | Step 4 sub-step 7 caps standalone runs at 3 waves to prevent context overflow. `--orchestrated` (Step 0b) lifts the ceiling for `aod.run` only. |
| "tasks.md is mostly approved — I'll start `/aod.build` and let the last sign-off catch up" | Step 1 sub-step 3 verifies all three Triad sign-offs are APPROVED before any wave runs. Missing sign-offs error and exit before Wave 1 dispatches. |

## Red Flags

- Agent skips a per-wave Architect checkpoint at the P0 / P1 / P2 boundary (Step 4 sub-step 6) without recording an APPROVED status.
- Agent runs more than 3 waves in a single conversation while `orchestrated == false` (violates Step 4 sub-step 7 ceiling).
- Agent uses `--no-tests` (line 55) without `summary.json` reflecting `waves_tested: 0` (line 613) — silent skip, no audit trail.
- Agent invokes `/aod.build` while `tasks.md` has any of the three Triad sign-offs missing or set to CHANGES_REQUESTED.
- Agent re-runs `/aod.build` from Wave 1 instead of resuming from the last unmarked task per Step 1 sub-step 6 ("RESUMING: Waves 1-N complete").
- Agent uses `--autonomous` interactively (not via `aod.run` orchestrator) and rubber-stamps every checkpoint, security-scan, and design-quality finding without review.
- Agent's Step 8 completion summary omits the Test Execution, Design Quality Gate, or Security Scan sections.
