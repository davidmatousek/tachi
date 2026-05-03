---
name: ~aod-bugfix
description: "One-shot governed bug fix loop: diagnose → plan → implement → verify → document. TRIGGER when: user reports a bug, pastes an error message/stack trace/failing test, or asks to fix a bug. Runs 5 Whys root cause analysis, presents confirmation gate before any code changes, implements fix, verifies with tests, and generates KB entry for review."
---

# /aod.bugfix — One-Shot Bug Fix Command

## Pre-Run Safety

> Advisory (non-blocking): Before proceeding, consider stashing or committing any in-progress work (`git stash` or `git commit`). If Phase 3 fails mid-execution, partial edits can be reverted cleanly from a known-good state.

`[Phase 0] Acknowledging input...`

## Phase 0: Input Acknowledgment & Context Summary

Detect the input mode based on what the user provided:

**If pasted content (error message, stack trace, logs, or failing test output):**

First, check whether an error or symptom is identifiable in the pasted content:
- **If no error message or symptom is visible** (e.g., the paste contains only code, config, or prose with no failure signal): stop and ask specifically — "I don't see an error message or failure symptom in what you pasted. Can you share the actual error, exception, or unexpected behavior you're seeing?" Do not proceed to Phase 0b until a failure signal is present.

If an error or symptom is present, proceed with parsing:
- **Multi-error input**: If multiple errors or exceptions appear, identify the PRIMARY failure — the first error in chronological order or the root-level exception (not cascading/downstream errors). Scope all acknowledgment and analysis to the primary failure only. In the context summary output, briefly note how many secondary errors were present and that they are considered downstream (e.g., "Note: 2 additional errors detected — treated as downstream of primary failure"). Do not analyze secondary errors separately.
- **Stack trace summarization**: When a multiline stack trace is present, do not pass it through raw. Summarize it in one line, e.g.: "Received: TypeError in src/foo.ts, 12-frame stack trace starting at bar()". Use the actual error type, file, frame count, and top frame from the trace.
- List any additional files or modules named in the output (beyond those in the summary line)

After parsing, output a 2-3 line context summary before continuing, using this format:
```
Input received: <error type> in <file/module>
Primary failure: <one-sentence description of the root error>
Scope: <files/components involved, or "unknown — proceeding to KB check">
```

Then proceed directly to Phase 0b.

**If minimal input (brief description only, no pasted content):**
Ask up to 3 targeted clarifying questions before proceeding. Examples:
1. "What error message or exception are you seeing? Paste the full message or stack trace if available."
2. "Which file or function is failing, and what were you doing when it broke?"
3. "Do you have a failing test, log output, or reproduction steps to share?"

Do not ask a generic "give me more context" prompt. Ask specific, targeted questions based on what is missing.

After acknowledgment or after receiving clarification, announce:

`Proceeding to Phase 0b...`

## Phase 0b: KB Pre-Check

`[Phase 0b — KB Pre-Check]`

Extract keywords from the primary failure identified in Phase 0:
- Error type name (e.g., `TypeError`, `NullPointerException`)
- Affected file or module name (e.g., `src/foo.ts`, `auth.service`)
- Function name, if available (e.g., `bar`, `handleRequest`)

Use the most specific terms first. Run a Grep search against `docs/INSTITUTIONAL_KNOWLEDGE.md` for each keyword. Limit to the top 3 matching results to avoid noise.

**If one or more matches are found:**

Present each matching KB entry concisely (up to 3 matches), using this format per entry:
```
KB Entry #<N>: <symptom summary>
Root cause: <one-sentence root cause>
Fix summary: <one-sentence fix description>
```

Then offer two options:
```
Found a matching KB entry. How would you like to proceed?
  (a) Apply existing solution — routes through Phase 2 confirmation gate
  (b) Run fresh 5 Whys analysis — proceed to Phase 1
```

Wait for developer response before continuing.

- **On (a)**: Treat the KB entry's fix as the proposed fix plan and route directly to the Phase 2 confirmation gate. Do NOT skip the confirmation gate — SC-004 applies. The developer must confirm before any file edits.
- **On (b)**: Proceed to Phase 1.

**If no match is found:** Proceed immediately to Phase 1. Do not display a "no results found" message.

**If `docs/INSTITUTIONAL_KNOWLEDGE.md` is unavailable or Grep fails:** Note the failure as non-fatal (e.g., "KB pre-check unavailable — proceeding to Phase 1") and proceed to Phase 1 immediately. Do not block on this. (ADR-006 — non-fatal observability)

## Phase 1: Diagnose — 5 Whys Root Cause Analysis

`[Phase 1 — Diagnose]`

> Lazy-load: Read `docs/core_principles/01-FIVE_WHYS_METHODOLOGY.md` now (not at skill start). This file provides the methodology context for the analysis below.

### 5 Whys Inline Logic

Run the 5 Whys analysis inline — do not delegate to an external agent.

**Step 1 — State the problem clearly.**
Use the primary failure identified in Phase 0. Write a specific, factual, singular problem statement (not a vague symptom). Example format: "Function `X` in `src/foo.ts` throws `TypeError: cannot read property 'Y' of undefined` when `Z` is called with an empty input."

**Step 2 — Why? (Iteration 1)**
Ask "Why does this problem occur?" State the most likely answer with direct evidence from code, logs, or stack trace. Do not speculate without grounding the answer in something observable.

**Step 3 — Why? (Iteration 2)**
Ask "Why does [answer from iteration 1] happen?" Go one level deeper. Cite a specific line, file, config value, or pattern as evidence.

**Step 4 — Why? (Iteration 3)**
Ask "Why does [answer from iteration 2] happen?" Continue toward the systemic cause. Minimum 3 iterations are required before declaring a root cause.

**Step 5 — Why? (Iterations 4–5, if needed)**
Continue asking until one of the root cause signs is reached (maximum 5 iterations):
- Fixing it prevents recurrence
- It is a process or system issue, not a person
- Further "whys" become circular or repetitive
- The answer is a missing guard, missing validation, or missing contract

**Step 6 — Articulate the root cause in plain language.**
State the root cause as a single sentence describing the systemic issue. Format: "Root cause: [process/system description that, if fixed, prevents the primary failure from recurring]."

**Step 7 — Counterfactual validation.**
State explicitly: "If we fix [root cause], does the primary failure go away?" Answer must be YES before proceeding. If NO, continue iterating or surface what remains unclear.

---

**If root cause remains unclear after 5 iterations:**
- Surface exactly what was established (list the 5 answers) vs. what remains unknown (the specific gap).
- Ask the developer targeted questions — not generic. Examples: "Does this code path execute on every request or only under a specific condition?" or "Is there a config value or environment variable that controls this behavior?"
- Do not proceed to Phase 2 until a root cause is confirmed.

**If multiple plausible root causes emerge:**
- Present a ranked list (most likely first) with a one-sentence rationale for each ranking.
- Ask the developer to confirm which root cause to pursue.
- Do NOT proceed with multiple causes simultaneously — pick one and scope the fix to it.

### Debugger Escalation (Optional)

Escalate to the `debugger` agent only when inline 5 Whys cannot identify the root cause. Typical escalation triggers:
- Intermittent failures with no reproducible pattern in available evidence
- Missing context (e.g., no stack trace, no logs, no test output available)
- Complex concurrency or async issues where causal chain cannot be determined from static analysis

**How to escalate:**
Invoke the `debugger` agent as a subagent via the Agent tool. Pass the problem statement from Phase 0 and the partial 5 Whys findings as input context.

**Return constraint:**
The debugger must return at most 15 lines to this skill. Its full findings must be written to `.aod/results/debugger.md` before returning.

**After escalation:**
Use the debugger's root cause finding as the answer to Step 6 above, then proceed to Phase 2. If the debugger is unavailable, proceed to Phase 2 with the best root cause hypothesis established from the inline analysis — note in the Phase 2 confirmation gate that the root cause is a hypothesis, not confirmed.

Root cause confirmed. Proceeding to Phase 2...

## Phase 2: Plan Fix — Confirmation Gate

`[Phase 2 — Plan Fix]`

### Fix Plan Generation

Based on the root cause confirmed in Phase 1, generate a fix plan containing:

- **Affected files**: List each file by exact path (relative to project root)
- **Nature of change per file**: One-sentence description of what will change and why
- **Overall confidence level**: High / Medium / Low
  - **High**: Root cause is clear, fix is well-understood, no side effects anticipated
  - **Medium**: Root cause is clear but fix may have edge cases or downstream interactions
  - **Low**: Root cause is plausible but uncertain, or fix may affect other behavior in hard-to-predict ways

**If confidence is Low:**
- Before presenting the confirmation gate, ask 1–2 targeted clarifying questions grounded in the specific uncertainty (e.g., "Does this function have callers that depend on the current behavior?" or "Is there test coverage for the path this fix will change?")
- Do NOT present the confirmation gate until confidence reaches at least Medium
- Re-evaluate confidence after receiving the developer's answers; update the plan accordingly

### Confirmation Gate (SC-004 — Non-Deferrable)

Present the fix plan in a visible block before any files are modified:

```
Affected files:
  - <file1> (<change description>)
  - <file2> (<change description>)

Confidence: <High / Medium / Low>

Confirm fix plan? (yes / no)
```

**On yes:**
- Announce: `Confirmed. Proceeding to Phase 3...`
- Continue to Phase 3

**On no:**
- Do NOT proceed to Phase 3
- Present 1–3 alternative approaches based on different fix strategies or root cause angles:
  - **Alternative 1**: [different fix strategy — e.g., guard at the call site instead of inside the function]
  - **Alternative 2**: [different root cause angle — e.g., fix the data source that produces invalid input rather than the consumer]
  - **Alternative 3** *(if applicable)*: [structural or architectural alternative — e.g., refactor to eliminate the code path entirely]
- Ask: "Which alternative would you like to pursue?"
- If the developer declines all alternatives:
  - Offer two options: "Restart with new context" or "Abort"
  - **On restart**: return to Phase 0 and explicitly ask: "Please describe the bug or paste new context, and I'll start a fresh analysis."
  - **On abort**: output a summary block — what was analyzed, which files were identified, what root cause was established — then stop. Do not modify any files.

> **SC-004 Compliance**: No files are modified at any point before this confirmation gate is passed. This is a hard constraint, not a guideline.

## Phase 3: Implement Fix

`[Phase 3 — Implement]`

Apply edits EXACTLY as described in the confirmed fix plan from Phase 2.

**Implementation rules:**
- Only modify files explicitly listed in the confirmed plan — do NOT touch any other files
- Track each file as it is edited (maintain a running list of edited files)
- If any edit deviates from what was described in the confirmed plan: PAUSE, explain the deviation, and ask for re-confirmation before continuing
- After all edits are applied: display the implementation trace — "Edited: [file1], [file2], ..."

**Partial failure handling (FR-011):**

If an error occurs mid-implementation:
- STOP immediately
- Report EXACTLY which files were edited before the failure (from the running tracked list)
- Report which file/edit failed and why
- Do NOT attempt to continue or rollback automatically — let the developer decide
- State: "Implementation incomplete. Files edited before failure: [list]. Failed on: [file/action]."

After all edits complete successfully, announce: "Implementation complete. Proceeding to Phase 3b..."

## Phase 3b: Post-Implementation Commit Prompt

Display this non-blocking advisory to the developer (do NOT wait for a response before continuing to Phase 4):

> Consider committing your fix before verification runs — this lets you revert cleanly if tests reveal a regression.
>
> ```bash
> git add <edited files>
> git commit -m "fix: <one-line description from root cause>"
> ```
>
> This is optional. Phase 4 will begin momentarily.

Proceed to Phase 4 immediately regardless of whether the developer responds.

## Phase 4: Verify Fix

`[Phase 4 — Verify]`

Detect the test command using this priority order:

1. **Developer-provided**: If the developer passed a test command (in the original bug report or at any prior phase), use it exactly as given.
2. **Auto-detect**: If no test command was provided, check for these in order:
   - `npm test` — present if `package.json` exists with a `test` script
   - `pytest` — present if `pytest.ini`, `setup.cfg` with `[tool:pytest]`, or `pyproject.toml` with `[tool.pytest]` exists, or `pytest` is installed
   - `make test` — present if `Makefile` exists with a `test` target
   - `cargo test` — present if `Cargo.toml` exists
   - `go test ./...` — present if `go.mod` exists
   - `bundle exec rspec` — present if `Gemfile` with `rspec` exists
3. **No command found**: If none of the above are detected, result is **SKIPPED** — this is a valid outcome, not a failure.

Run the detected test command and report exactly one of three outcomes:

**PASS**
Show test output (abbreviated to last 20 lines if longer). Announce:
`Tests passed. Proceeding to Phase 5 — Document.`

**FAIL**
Regression detected. Show which specific test(s) failed (test name, file, and failure message). Do NOT mark implementation complete.
Ask the developer:
```
Tests are failing. Would you like to:
  (a) Retry the fix with an updated approach
  (b) Reset to pre-fix state and restart from Phase 0
```
Do not proceed to Phase 5 until the developer makes a choice. On (a), return to Phase 2 with revised plan. On (b), list the files edited during Phase 3 and instruct the developer to revert them (e.g., `git checkout -- <files>`), then return to Phase 0.

**SKIPPED**
No test command available or discoverable. Note this outcome in the completion summary and in the KB entry. Announce:
`No test suite detected. Verification skipped. Proceeding to Phase 5 — Document.`

`[Phase 5 — Document]` will begin next.

## Phase 5: Document — KB Entry Generation

Announce: `[Phase 5 — Document]`

### Step 1 — Runtime Format Extraction

Read `docs/INSTITUTIONAL_KNOWLEDGE.md` now (lazy-load — do not read it earlier in the skill). Extract the entry format by reading the template block under "How to Add Entries" and inspecting 1–2 existing entries to confirm the live format. Never hardcode the schema — always read from the file at runtime.

### Step 2 — Generate KB Entry Draft

Using the format extracted in Step 1, generate a draft entry populated with:

- **Symptom**: The primary failure description from Phase 0 (the one-sentence description of the root error from the context summary block)
- **Root cause**: The root cause statement articulated in Phase 1 Step 6
- **Fix applied**: The list of edited files from the Phase 3 implementation trace, with a one-sentence change description per file
- **Verification status**: PASS / FAIL / SKIPPED as reported by Phase 4
- **Prevention advice**: What to check or do in the future to avoid this class of bug — derived from the root cause. Write 1–3 actionable sentences.

### Step 3 — Show Draft for Developer Review

Display the full draft entry in a visible block. Then ask:

```
Approve this KB entry? (yes / edit / skip)
```

Wait for developer response before continuing.

### Step 4 — On "yes": Write to File

Write using read-full-append-write-back:
1. Read the FULL current content of `docs/INSTITUTIONAL_KNOWLEDGE.md`
2. Append the new entry at the end of the file content
3. Write the ENTIRE file back using the Write tool

**CRITICAL NOTE**: The Write tool overwrites the file completely. Never just append — always read the full file first to avoid data loss.

Confirm: `KB entry written to docs/INSTITUTIONAL_KNOWLEDGE.md`

### Step 5 — On "edit": Apply Developer's Edits

Apply the developer's requested edits to the draft. Show the updated draft in full. Then ask:

```
Updated draft. Write this entry? (yes / skip)
```

- **On yes**: Write using the same read-full-append-write-back mechanism from Step 4.
- **On skip**: Complete without writing. Continue to Completion Summary.

### Step 6 — On "skip": Complete Without Writing

Output: `KB entry not created.`

This is not an error state. Continue to Completion Summary.

### Step 7 — On Write Failure: Non-Fatal Handling (ADR-006)

If the write operation fails for any reason:
- Report the error clearly
- Do NOT block completion
- Store the draft in the current session by displaying it in full:

```
KB write failed: [error]. Draft preserved below for manual copy:
```

Then show the full draft again so the developer can copy it manually.

After Phase 5 completes (any outcome — written, edited and written, skipped, or write failure), continue to the Completion Summary below.

## Completion Summary

Always output this block at the very end of skill execution, after all phases are complete (including Phase 5):

```
/aod.bugfix Complete

Root cause: [one-line plain language statement]
Fix applied: [comma-separated list of edited files]
Verification: [PASS / FAIL / SKIPPED]
KB entry: [path: docs/INSTITUTIONAL_KNOWLEDGE.md or "skipped"]
```

- **Root cause**: The single-sentence root cause statement from Phase 1 Step 6, in plain language. No jargon.
- **Fix applied**: Exact file paths as listed in the Phase 3 implementation trace. If no files were edited (e.g., aborted at Phase 2), write "none".
- **Verification**: The outcome from Phase 4 — one of PASS, FAIL, or SKIPPED.
- **KB entry**: The file path where the KB entry was written (`docs/INSTITUTIONAL_KNOWLEDGE.md`), or "skipped" if the KB write step was skipped or failed. If the write failed, also include the error in parentheses: `skipped (write error: <reason>)`.

This block must always appear, regardless of how the skill exits (normal completion, developer abort, or partial failure).

## Edge Cases

| # | Scenario | Behavior |
|---|----------|----------|
| 1 | **No test suite available** | Phase 4 reports SKIPPED. The loop still completes normally — SKIPPED is a valid outcome, not a failure. The KB entry notes that verification was skipped due to no available test command. The completion summary shows `Verification: SKIPPED`. |
| 2 | **Root cause unclear after 5 Whys** | Surface exactly what was established (list all 5 Why answers) and state precisely what remains unknown. Ask targeted questions grounded in the specific gap — not generic "give me more context." Do not guess or proceed to Phase 2. Wait for developer clarification before continuing. |
| 3 | **Multiple plausible root causes** | Present a ranked list (most likely first) with a one-sentence rationale per ranking. Ask the developer to confirm which root cause to pursue. Do not proceed with more than one cause simultaneously. Scope Phase 2 and Phase 3 entirely to the confirmed cause. |
| 4 | **Fix introduces a new test failure** | Do not mark implementation complete. Explicitly report the regression: which test(s) failed, in which file, with what failure message. Present the developer with the two-option choice: (a) retry with updated approach or (b) reset to pre-fix state. Do not proceed to Phase 5 until the developer decides. |
| 5 | **Developer declines fix plan at Phase 2** | Surface 1–3 alternative approaches (different fix strategy, different root cause angle, or structural alternative). Ask which alternative to pursue. If the developer declines all alternatives, offer two options: "Restart with new context" or "Abort." On abort, output a summary of what was analyzed and stop. No files are modified. |
| 6 | **KB write fails** | Non-fatal. Report the error clearly. Store the KB draft in the current session (display it in full so the developer can copy it manually). The fix is still considered complete. The completion summary shows `KB entry: skipped (write error: <reason>)`. |
| 7 | **Developer pastes context with no error message** | Stop at Phase 0 and ask specifically: "I don't see an error message or failure symptom in what you pasted. Can you share the actual error, exception, or unexpected behavior you're seeing?" Do not proceed to Phase 0b until a failure signal is present. Do not attempt to infer a bug from code or config alone. |
| 8 | **Partial implementation failure** | Stop immediately at the point of failure. Report the exact list of files edited before the failure (from the running tracked list maintained during Phase 3). Report which file or action failed and why. Do not attempt to continue or rollback automatically. State: "Implementation incomplete. Files edited before failure: [list]. Failed on: [file/action]." Let the developer decide how to proceed. |
