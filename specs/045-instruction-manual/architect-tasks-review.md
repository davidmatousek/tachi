# Architect Review: tasks.md (045 — End-to-End tachi Instruction Manual)

**Reviewer**: architect
**Date**: 2026-03-28
**Artifact**: `specs/045-instruction-manual/tasks.md`
**Context**: `specs/045-instruction-manual/plan.md`, `specs/045-instruction-manual/spec.md`

---

## Review Summary

| Area | Verdict |
|------|---------|
| Dependency ordering | PASS (with 1 concern) |
| Parallel markings | PASS (with 1 concern) |
| File path accuracy | PASS (with 1 finding) |
| Prompt-spec-first sequencing | PASS |
| Validation coverage | PASS (with 1 concern) |
| git mv approach | PASS |

**Overall**: APPROVED_WITH_CONCERNS (3 medium findings, 0 blockers)

---

## Detailed Findings

### Finding 1 (Medium): Compensating-controls command path — only `.claude/commands/` exists

**Location**: T004
**Task text**: "Read `/compensating-controls` command spec (search `.claude/commands/` and `adapters/claude-code/commands/`) and extract invocation syntax..."

**Issue**: The `/compensating-controls` command spec exists only at `.claude/commands/compensating-controls.md`. There is no corresponding file under `adapters/claude-code/commands/`. The `adapters/` directory contains `risk-score.md`, `infographic.md`, and `threat-model.md` but NOT `compensating-controls.md`.

The task text correctly says "search both locations" which is safe — the implementer will simply find nothing at the second path. However, the phrasing could mislead an implementer into thinking a file is missing or that content needs to be extracted from two sources.

**Recommendation**: Clarify that the authoritative command spec is at `.claude/commands/compensating-controls.md`. The `adapters/` path can be listed as a fallback check but is not expected to contain a file. This is non-blocking — the "search both" instruction will still produce the correct outcome.

---

### Finding 2 (Medium): Phase 2 parallel claim for T012 editing same file

**Location**: Dependencies & Execution Order section, Phase 2 parallel opportunities
**Text**: "T007-T009 edit the same file sequentially, but T012 (factual corrections) can run in parallel with T010-T011"

**Issue**: T012 edits `docs/guides/prompts/GUIDE_PROMPT.md` — the same file as T010 and T011. The claim that T012 "can run in parallel with T010-T011" is technically unsafe. Even though T012 targets different content (agent count, template names) than T010 (workflow section) and T011 (output artifacts section), concurrent edits to the same file risk merge conflicts, lost writes, or inconsistent intermediate states.

In practice, since this is an AI agent executing sequentially within a single context, true parallel file writes are unlikely. But the [P] marking convention exists to signal independence, and editing the same file is not independent by the project's definition.

**Recommendation**: Remove the parallel claim for T012 relative to T010-T011. Run T007 through T013 sequentially since they all modify the same file. T014-T015 (rename + reference update) remain correctly sequenced after T013. This is non-blocking — the task list body does NOT mark T012 with [P], so the actual task items are correct. The issue is only in the prose summary under "Parallel Opportunities."

---

### Finding 3 (Medium): Validation task T028 should cross-check both command locations

**Location**: T028
**Task text**: "Verify all command invocations in the guide match actual command specs in `adapters/claude-code/commands/` and `.claude/commands/`"

**Issue**: This task correctly lists both command locations, which is good. However, the task does not specify what to verify beyond "match." For a documentation-only feature where accuracy is the primary quality gate, this task should explicitly require checking:
1. Invocation syntax (flags, argument order)
2. Input file requirements (which files are required vs. optional)
3. Output artifact names and formats
4. Default behaviors (e.g., auto-detection, fallback paths)

The plan.md Phase 4 validation section (item 5) adds "Verify Appendix B structures match actual output formats" which partially addresses this, mapped to an implicit expectation. But T028 as written could be satisfied by a superficial path check.

**Recommendation**: Expand T028 or add a sub-checklist specifying the four verification dimensions above. This ensures the implementer performs a substantive accuracy check rather than just confirming file paths exist. Non-blocking — the validation intent is present, just underspecified.

---

## Verified Correct

The following areas were verified and found to be sound:

### Dependency Ordering

- Phase 1 (Setup) has no dependencies — correct.
- Phase 2 (Prompt Spec) depends on Phase 1 and blocks Phases 3-6 — correct. This enforces the spec-first principle.
- Phase 3 (Pipeline Guide) depends on Phase 2 — correct. The guide draws from the updated spec.
- Phase 4 (Quick Start) depends on Phase 3 — correct. Cross-references require section anchors.
- Phase 5 (OpenClaw) depends on Phase 3 — correct. References command sections.
- Phase 6 (Appendix) depends on Phase 3 — correct. Output format details must be finalized.
- Phase 7 (Validation) depends on all prior phases — correct.
- No circular dependencies detected.
- No missing prerequisites detected.

### Prompt-Spec-First Sequencing

Phase 2 (US4 — Prompt Specification Update) is explicitly marked as "MUST complete before the developer guide is updated (Phases 3-6)." The dependency chain enforces this: Phase 3 depends on Phase 2, and Phases 4-6 depend on Phase 3. This is correctly ordered per the plan.md requirement that "spec is source of truth."

### Parallel Opportunities (Correct Ones)

- **T002-T006 [P]**: Reading different, independent files. No conflicts. Correct.
- **T024, T025 [P]**: Editing different subsections of Appendix B. Since these target distinct, non-overlapping content blocks within the same file, the parallel claim is acceptable (different appendix subsections).
- **T028, T029 [P]**: Performing different validation checks (command invocation match vs. spec-guide parity). No file conflicts. Correct.

### File Path Accuracy

- `docs/guides/prompts/GUIDE_PROMPT.md` — EXISTS. Verified.
- `docs/guides/DEVELOPER_GUIDE_TACHI.md` — EXISTS. Verified.
- `adapters/claude-code/commands/risk-score.md` — EXISTS. Verified.
- `adapters/claude-code/commands/infographic.md` — EXISTS. Verified.
- `.claude/commands/compensating-controls.md` — EXISTS. Verified.
- `docs/INTERFACE-CONTRACT.md` — EXISTS. Verified.
- README.md link to `docs/guides/DEVELOPER_GUIDE_TACHI.md` — EXISTS. Verified.

### git mv Approach

T014 uses `git mv docs/guides/prompts/GUIDE_PROMPT.md docs/guides/prompts/developer-guide-prompt.md` which is correct. `git mv` preserves file history, which the plan.md architect review (Finding L2) recommended noting. T015 correctly follows with a codebase search for stale references to the old filename.

Note: The Grep search for `GUIDE_PROMPT` reveals 9 files currently referencing the old name. T015 must update all of them. The task is correctly scoped but could benefit from noting the expected hit count (9 files) as a completeness check.

### Section Insertion Points

- T016 references "after Section 7 (Reading and Acting)" — Section 7 is confirmed at line 1018 of the developer guide. Correct insertion point.
- T020 references "after Step 6 in Quick Start" — Step 6 is confirmed at line 124 of the developer guide. Correct insertion point.
- The guide currently has Sections 1-9 plus Appendices A-C. New sections will need to be numbered Section 8+ with existing Sections 8-9 renumbered. T031 (consistency review) covers this with "section numbering sequential."

### Summary Table Accuracy

- Total tasks: 31. Counted: T001-T031. Correct.
- Phase counts: 6 + 9 + 4 + 1 + 3 + 3 + 5 = 31. Correct.
- Files modified: 2 + 1 rename. Correct.
- MVP scope: Phases 1-3 = 6 + 9 + 4 = 19 tasks. Correct.

---

## Disposition

**STATUS**: APPROVED_WITH_CONCERNS

Three medium findings, all non-blocking:
1. Compensating-controls path clarification (T004) — safe as written, could be clearer
2. Phase 2 parallel prose claim for T012 is technically unsafe (task items themselves are correct)
3. Validation task T028 underspecified for accuracy dimensions

None of these require structural changes to the task breakdown. The dependency ordering is sound, the spec-first sequencing is correctly enforced, parallel opportunities are conservatively applied, and file paths are accurate against the actual repository state.
