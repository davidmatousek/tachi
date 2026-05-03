# PM Tasks Review: Feature 120 — Architecture Lifecycle Command

**Reviewer**: product-manager
**Date**: 2026-04-09
**Artifact**: `specs/120-architecture-lifecycle-command/tasks.md`
**Against**: `specs/120-architecture-lifecycle-command/spec.md` (PM-APPROVED 2026-04-09)
**PRD Reference**: `docs/product/02_PRD/120-architecture-lifecycle-command-2026-04-09.md`

---

## Verdict: APPROVED

**Findings**: 3 (0 blocking, 0 medium, 3 informational/low)

---

## 1. User Story Coverage

All 4 user stories from spec.md are mapped to implementation tasks with explicit `[US{N}]` labels.

| User Story | Priority | Tasks | Coverage |
|-----------|----------|-------|----------|
| US1 — Architecture Version Tracking | P0 | T004, T006, T007 | COMPLETE — frontmatter detection (T004), injection with version/checksum (T006), report display (T007) |
| US2 — Architecture Archive | P0 | T005 | COMPLETE — archive copy with `mkdir -p`, idempotent retry, first-time skip |
| US3 — Automatic Architecture Snapshot | P0 | T008, T009 | COMPLETE — verbatim copy into timestamped folder (T008), report listing (T009) |
| US4 — Guided Architecture Update | P1 | T010, T011 | COMPLETE — guided categories (T010), description population (T011) |

**Assessment**: Full coverage. Every acceptance scenario from each user story is addressed by at least one implementation task, and every user story has at least one validation task in Phase 5.

---

## 2. Functional Requirements Coverage

All 22 FRs from spec.md traced to implementation or validation tasks.

| FR | Description | Task(s) | Status |
|----|-------------|---------|--------|
| FR-001 | YAML frontmatter with 5 fields | T004, T006 | COVERED |
| FR-002 | Version starts at 1, increments by 1 | T006 | COVERED |
| FR-003 | SHA-256 of body only, prefixed `sha256:` | T006 | COVERED |
| FR-004 | Explicit `shasum -a 256` tool invocation | T006 | COVERED (two-pass write pattern specified) |
| FR-005 | Legacy files treated as v0 | T004, T006 | COVERED + validated (T013) |
| FR-006 | Archive to `{parent_dir}/.archive/v{N}/architecture.md` | T005 | COVERED |
| FR-007 | Archive preserves complete file including frontmatter | T005 | COVERED |
| FR-008 | Archive directory created automatically | T005 | COVERED (`mkdir -p`) |
| FR-009 | Archive append-only, idempotent per version | T005 | COVERED (idempotent retry noted) |
| FR-010 | No archive for first-time generation | T005 | COVERED (skip clause) |
| FR-011 | `previous_version` field with archive path or null | T006 | COVERED (version logic specified) |
| FR-012 | Copy architecture into timestamped output folder | T008 | COVERED |
| FR-013 | Verbatim copy, no modifications | T008 | COVERED |
| FR-014 | Snapshot filename matches source | T008 | COVERED |
| FR-015 | Skip silently if architecture file missing | T008 | COVERED + validated (T018) |
| FR-016 | Snapshot after Step 1.3, before Step 2 | T008 | COVERED (insertion point specified) |
| FR-017 | Guided update mode with 6 categories | T010 | COVERED |
| FR-018 | No changes = file untouched, no archive, no increment | T010 | COVERED (abort clause) |
| FR-019 | Description field summarizes session changes | T011 | COVERED |
| FR-020 | Archive path relative to parent directory | T005 | COVERED (`{parent_dir}` in path) |
| FR-021 | Example files unmodified | T019 | VALIDATED (backward compatibility test) |
| FR-022 | Downstream stages unaffected | T020 | VALIDATED (downstream format check) |

**Assessment**: 22/22 FRs covered. No gaps. FR-004 (explicit tool invocation) is addressed in T006's two-pass write pattern specification, which is a direct response to the Team-Lead's PRD concern.

---

## 3. Scope Analysis

### Scope Adherence

Tasks stay within the boundaries defined in spec.md's "In Scope" and "Out of Scope" sections.

| Scope Check | Result |
|-------------|--------|
| Only 2 command files modified | PASS — `tachi.architecture.md` and `tachi.threat-model.md` |
| No downstream pipeline changes | PASS — T020 validates this explicitly |
| No example file modifications | PASS — T019 validates examples work as-is |
| No new dependencies | PASS — all operations are local filesystem |
| No schema changes to existing outputs | PASS — T020 covers this |
| MVP/P1 separation preserved | PASS — Phase 2+3 are P0, Phase 4 is P1 |

### Scope Creep Check

No tasks exceed spec boundaries:
- T022 (CLAUDE.md update) and T023 (archive convention docs) are standard polish tasks consistent with project conventions, not scope creep.
- No tasks introduce diff visualization, version pinning, git integration, or any other out-of-scope item.

**Assessment**: Clean scope. No creep detected.

---

## 4. Priority Alignment

| Priority | Spec Scope | Tasks Phase | Alignment |
|----------|-----------|-------------|-----------|
| P0 (MVP) | Frontmatter, archive, snapshot, legacy handling | Phase 2 (US1+US2) + Phase 3 (US3) | ALIGNED |
| P1 | Guided update, description auto-population | Phase 4 (US4) | ALIGNED |

The implementation strategy section explicitly defines MVP as "Phases 1-3 + Phase 5 (P0 features + validation)" and positions Phase 4 (US4/P1) as incremental delivery after MVP validation. This matches the spec's P0/P1 separation exactly.

The dependency chain is also correct: US4 (P1) depends on US1+US2 (P0) because it extends the same command file, while US3 (P0) is correctly identified as independent and parallelizable with Phase 2.

**Assessment**: Priority ordering matches spec. MVP boundary is correctly drawn.

---

## 5. Success Criteria Validation Coverage

All 7 success criteria from spec.md are mapped to validation tasks.

| SC | Description | Validation Task(s) | Coverage |
|----|-------------|-------------------|----------|
| SC-001 | 100% architecture files have valid frontmatter (5 fields) | T012 | COVERED — first-time generation validates all 5 fields |
| SC-002 | N runs produce N-1 archive entries | T015 | COVERED — 3 consecutive runs verify v1, v2 entries |
| SC-003 | 100% threat model folders contain snapshot | T017 | COVERED — snapshot with frontmatter preserved |
| SC-004 | Legacy/example files work as input | T019 | COVERED — all 3 examples validated |
| SC-005 | Checksum matches recomputation | T016 | COVERED — SHA-256 recomputation test |
| SC-006 | No downstream changes needed | T020 | COVERED — full pipeline format verification |
| SC-007 | Guided update produces accurate description | T021 | COVERED — description accuracy check |

**Assessment**: 7/7 success criteria have dedicated validation tasks. Each validation task references the specific SC it verifies (e.g., "SC-001, US1-scenario-4, US2-scenario-4").

---

## 6. Findings

### Finding 1 (Informational): US3-scenario-4 coverage is implicit

**Observation**: Spec US3 acceptance scenario 4 states "Given a threat model run with a custom output directory, When the snapshot is taken, Then the architecture copy is placed in the same timestamped subfolder as the threat output." No dedicated validation task tests a custom output directory scenario.

**Assessment**: This is not a gap. T008 specifies snapshot placement in `{output_dir}/{architecture_filename}`, which is directory-agnostic. The command already handles custom output directories, and the snapshot step inherits that path. No dedicated task needed.

**Severity**: Informational. No action required.

### Finding 2 (Informational): Edge case coverage is distributed, not explicit

**Observation**: The spec defines 7 edge cases (concurrent updates, corrupted frontmatter, missing parent directory, empty architecture file, archive version collision, non-default path, very large files). These are addressed implicitly by implementation task specifications (e.g., T005 covers idempotent retry for archive collision, T004 covers corrupted frontmatter via "treat as v0" fallback) rather than having dedicated edge case validation tasks.

**Assessment**: Acceptable for this feature scope. Edge cases are inherently covered by the implementation logic (e.g., treating malformed frontmatter as legacy/v0 is the default path, not a special case). Adding 7 more validation tasks would over-index on test coverage for a 2-command-file change.

**Severity**: Informational. No action required.

### Finding 3 (Low): T015 depends on T012-T014 sequence

**Observation**: T015 (multi-run continuity) is listed without [P] marker, correctly indicating it depends on sequential execution. However, T015 validates SC-002 which requires 3 consecutive runs. This task implicitly subsumes the scenarios from T012 (first-time generation) and T014 (managed update). The dependency is correctly modeled but worth noting for the build agent: T015 should not be attempted until the implementation is stable.

**Assessment**: The dependency ordering in the document already handles this (Phase 5 depends on Phases 2-4). No change needed.

**Severity**: Low. No action required.

---

## 7. Quality Assessment

### Traceability

Every task has an explicit `[US{N}]` label connecting it to a user story. Validation tasks reference specific SCs and acceptance scenarios. The traceability chain from PRD -> spec -> plan -> tasks is unbroken.

### Parallel Execution Design

The parallel strategy is well-designed:
- Phase 2 (tachi.architecture.md) and Phase 3 (tachi.threat-model.md) modify different files and can run simultaneously as Wave 1
- Validation tasks T012-T020 (except T015) are marked [P] for independent execution
- This directly supports the Team-Lead's 3-wave estimate from PRD review

### Implementation Strategy

The MVP-first strategy (Phases 1-3 + Phase 5) followed by incremental P1 delivery (Phase 4) is sound product practice. It delivers user value (versioning + traceability) before adding the convenience feature (guided updates).

### Checkpoint Design

Each implementation phase has an independent test description and a checkpoint statement. This allows build agents to validate incrementally rather than only at the end.

---

## 8. Sign-off

**Status**: APPROVED
**Date**: 2026-04-09
**Agent**: product-manager

**Rationale**:
- 4/4 user stories fully covered with explicit task-to-story mapping
- 22/22 functional requirements addressed by implementation or validation tasks
- 7/7 success criteria have dedicated validation tasks
- Scope is clean with no creep beyond spec boundaries
- P0/P1 priority alignment matches spec exactly
- MVP boundary correctly drawn at Phases 1-3
- Parallel execution strategy supports efficient delivery
- 3 informational/low findings, 0 blocking

Tasks are ready for Team-Lead sign-off and agent assignment.
