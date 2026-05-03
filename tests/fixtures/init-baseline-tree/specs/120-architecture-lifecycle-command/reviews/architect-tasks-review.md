# Architect Review: tasks.md

**Feature**: 120 — Architecture Lifecycle Command
**Reviewer**: architect
**Date**: 2026-04-09
**Artifact**: `specs/120-architecture-lifecycle-command/tasks.md`
**Reviewed Against**: `plan.md`, `spec.md`, `data-model.md`, existing command files

---

## Review Summary

| Dimension | Verdict | Notes |
|-----------|---------|-------|
| Dependency Ordering | PASS | Intra-phase and inter-phase ordering is correct |
| Parallel Markers | PASS with 1 CONCERN | See finding F-02 |
| Technical Accuracy | PASS with 1 CONCERN | See finding F-01 |
| Integration Safety | PASS | No breakage risk to existing behavior |
| Validation Completeness | PASS | All 7 SCs, all edge cases covered |

**Overall**: APPROVED_WITH_CONCERNS (0 blocking, 2 concerns, 1 advisory)

---

## Findings

### F-01 [CONCERN] — Step numbering mismatch in T008

**Location**: T008 description
**Issue**: T008 says "insert between current Step 1 item 3 (output directory creation) and Step 2 (orchestrator invocation)." However, the actual `tachi.threat-model.md` structure is:

- Step 0: Parse Flags (items 1-8, where item 7 generates the run folder, item 8 auto-detects baseline)
- Step 1: Validate Prerequisites (items 1-3, where item 3 is "Check output directory" which creates `output_dir`)
- Step 2: Run Threat Analysis
- Step 3: Report Results

The insertion point is correct (between directory creation in Step 1 and orchestrator invocation in Step 2), and the plan.md description is accurate ("after the timestamped output folder is created (current Step 1 item 3)"). However, the task calls it "Step 1 item 3 (output directory creation)" which is technically the "Check output directory" prerequisite validation step, not the timestamped folder creation (which happens in Step 0 item 7). The run folder is computed and directory created across Steps 0 and 1.

**Impact**: Low. The insertion point between Step 1 and Step 2 is unambiguous regardless of which sub-item creates the directory. An implementing engineer will place the snapshot correctly.

**Recommendation**: The implementing agent should read the full command file (T002 already mandates this) and place the snapshot step after Step 1 completes and before Step 2 begins. No task text change needed, but the engineer should note that `mkdir -p` for the timestamped output dir may need to be verified as complete before the snapshot copy.

### F-02 [CONCERN] — T015 missing [P] marker but could be parallelizable with caveats

**Location**: T015 (Validate multi-run continuity)
**Issue**: T015 lacks a [P] marker while T012-T014 and T016-T020 all have [P]. T015 requires 3 consecutive runs on the same file, which means it has internal sequential ordering. However, it does not depend on any other validation task -- it can run in parallel with the other validation tasks as long as it operates on its own isolated test project directory.

**Impact**: Low. The missing [P] marker is conservative rather than incorrect. The task IS sequential internally (3 runs in order), which may have been the reason for omitting [P]. If the team-lead wants to maximize parallelism, T015 can be assigned to an agent with its own test directory alongside other validation tasks.

**Recommendation**: Acceptable as-is. The omission is defensible (internal sequentiality). If the team-lead wants to parallelize, they can override.

### F-03 [ADVISORY] — T006 two-pass write pattern is well-specified

**Location**: T006
**Observation**: T006 correctly specifies the two-pass write pattern from the plan: "write markdown body to output file first, compute SHA-256 checksum via `shasum -a 256` on the file, then prepend assembled YAML frontmatter." This matches plan.md Section "Step 3a: Inject Frontmatter" and addresses the architect concern from plan review about checksum computation ordering.

**Impact**: None -- this is positive validation, not a concern.

---

## Dimension Analysis

### 1. Dependency Ordering

**Verdict: PASS**

Inter-phase ordering is correct:
- Phase 1 (read-only) -> Phase 2 (modify tachi.architecture.md) -> Phase 4 (extend same file): Correct, US4 depends on US1+US2 changes being in place.
- Phase 1 (read-only) -> Phase 3 (modify tachi.threat-model.md): Correct, independent of Phase 2.
- Phases 2+3+4 -> Phase 5 (validation): Correct, all implementations must complete before validation.
- Phase 5 -> Phase 6 (polish): Correct, documentation only after everything validated.

Intra-phase ordering is correct:
- Phase 2: T004 (detect) -> T005 (archive) -> T006 (frontmatter) -> T007 (report): Matches the command flow sequence from plan.md (Step 0 -> Step 0a -> Step 3a -> Step 4).
- Phase 3: T008 (snapshot) -> T009 (report update): Correct, must add snapshot before updating report to mention it.
- Phase 4: T010 (guided mode) -> T011 (description field): Correct, mode must exist before description can be populated from it.

### 2. Parallel Opportunities

**Verdict: PASS with 1 concern (F-02)**

Verified [P] markers:
- Phase 1: T001, T002, T003 all read-only on different files. [P] correct.
- Phase 2 + Phase 3: Different files (`tachi.architecture.md` vs `tachi.threat-model.md`). Parallel execution correct.
- Phase 5: T012-T014, T016-T020 are independent validation scenarios on separate test contexts. [P] correct. T015 and T021 lack [P] -- T015 is internally sequential (3 runs), T021 depends on guided update mode (Phase 4). Both omissions are defensible.
- Phase 6: T022 and T023 modify different files. [P] correct.

### 3. Technical Accuracy

**Verdict: PASS with 1 concern (F-01)**

Key technical design elements verified against plan.md:

| Design Element | Plan Reference | Task Reference | Match |
|----------------|---------------|----------------|-------|
| Two-pass checksum | Step 3a: "write body, compute SHA-256, prepend frontmatter" | T006: "write markdown body to output file first, compute SHA-256 checksum via `shasum -a 256` on the file, then prepend assembled YAML frontmatter" | Exact match |
| Archive path derivation | Step 0a: "`{parent_dir}/.archive/v{N}/{filename}`" | T005: "derive archive path as `{parent_dir}/.archive/v{N}/{filename}` relative to architecture file's parent directory" | Exact match |
| Snapshot integration point | Step 1.4: "after timestamped output folder created, before orchestrator invoked" | T008: "insert between current Step 1 item 3 and Step 2" | Functionally correct (see F-01) |
| Version logic (new file) | "v1, previous_version: null" | T006: "v1 for new files (previous_version: null)" | Exact match |
| Version logic (legacy) | "v1, legacy archived as v0" | T006: "v1 for legacy upgrades (previous_version: .archive/v0/{filename})" | Exact match |
| Version logic (managed) | "v{N+1}" | T006: "v{N+1} for managed updates" | Exact match |
| Frontmatter fields | 5 fields: version, date, description, checksum, previous_version | T004/T006: all 5 fields specified | Exact match |
| Idempotent archive | FR-009: "overwrite permitted for same version number" | T005: "Include idempotent retry behavior (overwrite same version number)" | Exact match |
| Guided update abort | Plan Step 0b: "abort update, leave file untouched" | T010: "abort update, leave file untouched, no archive operation, no version increment" | Exact match with added specificity |

### 4. Integration Safety

**Verdict: PASS**

Backward compatibility analysis:

- **tachi.architecture.md**: New steps are inserted AROUND existing Steps 1-3 (Step 0/0a/0b before, Step 3a after Step 3). The existing 4-step flow (Determine Scope -> Analyze -> Generate -> Report) is preserved. New files get frontmatter appended; existing pipeline behavior unchanged.
- **tachi.threat-model.md**: Single new step (1.4) inserted between Step 1 and Step 2. The orchestrator still receives architecture content via `<architecture-input>` tags (unchanged). Snapshot is informational only -- no downstream consumer reads it.
- **Example files**: T003 reads examples to confirm no frontmatter exists. T019 validates all 3 examples work as threat model input. No example files are modified (FR-021 compliance).
- **Downstream pipeline**: T020 explicitly validates risk-scores, controls, infographic, and report stages produce identical output (FR-022, SC-006 compliance).

### 5. Validation Completeness

**Verdict: PASS**

All 7 success criteria mapped to validation tasks:

| Success Criterion | Validation Task(s) | Coverage |
|-------------------|-------------------|----------|
| SC-001: Valid frontmatter on all generated files | T012 | Complete |
| SC-002: N runs produce N-1 archive entries | T015 | Complete |
| SC-003: Snapshot in threat model output | T017 | Complete |
| SC-004: Legacy files work as input | T019 | Complete |
| SC-005: Checksum matches recomputation | T016 | Complete |
| SC-006: Downstream unaffected | T020 | Complete |
| SC-007: Guided update description accuracy | T021 | Complete |

Edge cases from spec mapped to tasks:

| Edge Case | Task Coverage |
|-----------|--------------|
| Corrupted frontmatter (treat as legacy) | T013 covers legacy path; corrupted frontmatter is a subset |
| First-time generation (no existing file) | T012 |
| Legacy file without frontmatter | T013 |
| Archive directory already has version (idempotent) | T005 specifies idempotent behavior |
| Non-default architecture file path | T005 derives path from parent_dir (generic) |
| Guided update with no changes (abort) | T010 specifies abort behavior |
| Snapshot skip when no architecture file | T018 |
| Concurrent updates | Explicitly out of scope (single-user, noted in spec assumptions) |
| Empty architecture file | Covered by legacy path (T013 -- no frontmatter) |
| Missing parent directory | Existing behavior, not modified |

---

## Sign-off

**STATUS**: APPROVED_WITH_CONCERNS
**FINDINGS**: 3 (2 CONCERN, 1 ADVISORY)
**BLOCKING**: 0

The tasks document is technically sound and ready for implementation. The two concerns are low-impact and do not require changes before proceeding. The dependency ordering is correct, parallel markers are accurate (with one conservative omission), technical design elements match the plan exactly, integration safety is maintained, and all success criteria plus edge cases have validation coverage.
