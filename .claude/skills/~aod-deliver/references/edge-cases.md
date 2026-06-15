# Edge Cases, Common Rationalizations, and Red Flags

This reference is loaded on demand — only when handling an edge case or checking a rationalization/red-flag. Do NOT load this file on a clean happy-path close.

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "AC-coverage gate is too strict, I'll mark them MANUAL-ONLY" | `[MANUAL-ONLY]` is for non-automatable ACs (e.g. visual review). Don't use it as an escape hatch. |
| "I'll add `--no-tests` to bypass the failing E2E once" | Step 0d requires `--no-tests=<reason>` with 10-500 chars; reason is appended to the audit log. |
| "MANUAL-ONLY needs no reason for trivial ACs" | Step 9a.5 exit 4 halts with reason length below 10 chars; the AC ID and minimum are emitted to stderr. |
| "Pack contract block is missing — I'll silently skip the gate" | Step 9a exit 5 routes through the unified error branch; status becomes `e2e_validation.status = "error"`. |
| "I can pass both `--no-tests` and `--require-tests` to be safe" | Step 0c rejects this contradiction with exit 2; `--require-tests` is the deprecated former opt-in. |
| "Uncovered ACs can be deferred — I'll fix them post-merge" | Step 9a.5 step 5 HALTS via Step 9e with `reason = "ac_coverage_fail"`, exit 10; no merge happens. |

## Red Flags

- Agent invokes `/aod.deliver` with `--no-tests=skip` (5 chars) and is surprised by Step 0d rejection.
- Agent passes `--no-tests --require-tests` together, ignoring Step 0c flag-conflict exit 2.
- Agent's `[MANUAL-ONLY]` reason is a placeholder like "TODO" instead of meeting Step 9a.5 10-char minimum.
- Agent skips the AC-coverage gate (Step 9a.5) when `e2e_validation.status` is unset and pack has a real contract.
- Agent treats Step 9a exit 5 as a hard-block when it should resolve to `e2e_validation.status = "error"` and proceed to Step 10.
- Agent's audit log lacks the `<reason>` per Step 0d integration note despite an active `--no-tests` opt-out.
