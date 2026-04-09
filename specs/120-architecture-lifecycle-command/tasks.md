---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "4/4 user stories mapped. 22/22 FRs addressed. 7/7 success criteria covered by validation tasks. No scope creep. P0/P1 ordering matches spec. 3 informational findings (0 blocking)."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "3 findings (2 CONCERN, 1 ADVISORY, 0 blocking). C-01: T008 sub-item reference imprecise but functionally correct (T002 reads full file). C-02: T015 lacks [P] but conservative choice is defensible. F-03: two-pass checksum correctly implements plan spec."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "5 waves, 2-agent parallelism, ~45-55 min wall-clock. 2 non-blocking concerns: (L) Wave 3 validation realistically 25-30 min not 15-20 due to full command execution cycles; (L) tester agent acceptable for validation with senior-backend-engineer as fallback."
---

# Tasks: Architecture Lifecycle Command

**Input**: Design documents from `specs/120-architecture-lifecycle-command/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, research.md

**Tests**: Not explicitly requested in spec. Validation tasks are included as Phase 5.

**Organization**: Tasks grouped by user story priority. US1+US2 are tightly coupled (same command flow) and combined into one phase.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

**Purpose**: Load context and prepare workspace

- [X] T001 Read current command file at `.claude/commands/tachi.architecture.md` to understand existing 4-step structure
- [X] T002 [P] Read current command file at `.claude/commands/tachi.threat-model.md` to understand Step 0/1/2 structure and insertion point
- [X] T003 [P] Read example architecture files at `examples/agentic-app/architecture.md`, `examples/microservices/architecture.md`, `examples/web-app/architecture.md` to confirm no frontmatter exists

---

## Phase 2: US1+US2 — Architecture Version Tracking + Archive (Priority: P0) MVP

**Goal**: Architecture files have YAML frontmatter with version metadata; previous versions are archived before updates.

**Independent Test**: Run `/tachi.architecture` on a project. Verify the output has frontmatter (version, date, description, checksum, previous_version). Run again — verify previous version is archived and new version is incremented.

### Implementation

- [X] T004 [US1] Add Step 0 (Detect Existing File) to `.claude/commands/tachi.architecture.md` — check if output path has an existing architecture file, read it, check for YAML frontmatter `---` delimiters, parse `version`/`date`/`description`/`checksum`/`previous_version` fields, treat files without frontmatter as v0
- [X] T005 [US2] Add Step 0a (Archive Current Version) to `.claude/commands/tachi.architecture.md` — derive archive path as `{parent_dir}/.archive/v{N}/{filename}` relative to architecture file's parent directory, create directory with `mkdir -p`, copy complete file including frontmatter to archive, display archive confirmation message. Include idempotent retry behavior (overwrite same version number). Skip archive for first-time generation (no existing file)
- [X] T006 [US1] Add Step 3a (Inject Frontmatter) to `.claude/commands/tachi.architecture.md` — after architecture content generation (Step 3), implement two-pass write pattern: write markdown body to output file first, compute SHA-256 checksum via `shasum -a 256` on the file, then prepend assembled YAML frontmatter with `version`, `date`, `description`, `checksum` (prefixed `sha256:`), and `previous_version`. Version logic: v1 for new files (previous_version: null), v1 for legacy upgrades (previous_version: .archive/v0/{filename}), v{N+1} for managed updates (previous_version: .archive/v{N}/{filename})
- [X] T007 [US1] Update Step 4 (Report) in `.claude/commands/tachi.architecture.md` — add version number, archive location (if applicable), and checksum to the report output display

**Checkpoint**: `/tachi.architecture` produces versioned architecture files with frontmatter and archives previous versions.

---

## Phase 3: US3 — Automatic Architecture Snapshot in Threat Model Runs (Priority: P0)

**Goal**: Every `/tachi.threat-model` output folder contains a verbatim copy of the architecture file that was analyzed.

**Independent Test**: Run `/tachi.threat-model` with an architecture file present. Verify the timestamped output folder contains `architecture.md` alongside `threats.md`.

### Implementation

- [X] T008 [US3] Add Step 1.4 (Architecture Snapshot) to `.claude/commands/tachi.threat-model.md` — insert between current Step 1 item 3 (output directory creation) and Step 2 (orchestrator invocation). Check if architecture file exists at `{architecture_path}`, if yes copy verbatim to `{output_dir}/{architecture_filename}` preserving all content including frontmatter, if not skip silently. Display snapshot confirmation when copied.
- [X] T009 [US3] Update Step 3 (Report) in `.claude/commands/tachi.threat-model.md` — add `architecture.md` to the "Files generated" list in the report output display, conditional on snapshot having been performed

**Checkpoint**: `/tachi.threat-model` output folders are self-contained with architecture snapshot.

---

## Phase 4: US4 — Guided Architecture Update (Priority: P1)

**Goal**: When updating an existing architecture, the command guides users through change categories to ensure completeness.

**Independent Test**: Run `/tachi.architecture` with an existing architecture file. Verify the command presents a guided update flow and the `description` field reflects the changes made.

### Implementation

- [X] T010 [US4] Add Step 0b (Guided Update Mode) to `.claude/commands/tachi.architecture.md` — insert between Step 0a (archive) and Step 1 (determine scope). When existing file detected: display current architecture summary (components, flows, boundaries extracted from file), present guided update categories in sequence (new services, removed components, changed data flows, modified trust boundaries, added/removed external entities, changed AI capabilities), allow user to skip categories with no changes, collect all changes as context for generation step. If user indicates no changes across all categories: abort update, leave file untouched, no archive operation, no version increment.
- [X] T011 [US4] Update Step 3a frontmatter injection in `.claude/commands/tachi.architecture.md` — populate `description` field from guided update changes (e.g., "Added payment gateway service, updated API data flows") when guided mode was used; use generation summary for first-time generation

**Checkpoint**: Guided update mode ensures completeness and produces accurate change descriptions.

---

## Phase 5: Validation (P0)

**Purpose**: Verify all success criteria and acceptance scenarios across all user stories.

- [X] T012 [P] Validate first-time generation: run `/tachi.architecture` on a project with no existing architecture file, verify output has `version: 1`, `date` set to today, valid `sha256:` checksum, `previous_version: null`, and no archive directory created (SC-001, US1-scenario-4, US2-scenario-4)
- [X] T013 [P] Validate legacy file upgrade: create an architecture file without frontmatter, run `/tachi.architecture`, verify legacy file archived as `v0`, new file has `version: 1` with `previous_version: .archive/v0/architecture.md` (FR-005, US1-scenario-1, US2-scenario-3)
- [X] T014 [P] Validate managed update: on a file with `version: 3` frontmatter, run `/tachi.architecture`, verify `version: 4`, previous version archived at `.archive/v3/architecture.md` (US1-scenario-2, US2-scenario-1)
- [X] T015 Validate multi-run continuity: run `/tachi.architecture` 3 consecutive times, verify archive contains v1 and v2 entries with correct content from each version (SC-002)
- [X] T016 [P] Validate checksum integrity: for a generated architecture file, recompute SHA-256 of body content and verify it matches the `checksum` frontmatter field (SC-005)
- [X] T017 [P] Validate threat model snapshot: run `/tachi.threat-model` with an architecture file present, verify timestamped output folder contains `architecture.md` with original frontmatter preserved verbatim (SC-003, US3-scenario-1, US3-scenario-2)
- [X] T018 [P] Validate snapshot skip: run `/tachi.threat-model` with no architecture file at the expected path, verify snapshot step is skipped silently and threat model proceeds (US3-scenario-3)
- [X] T019 [P] Validate backward compatibility: run `/tachi.threat-model` using each of the 3 example architecture files (no frontmatter) as input, verify all produce valid threat model output (SC-004, FR-021)
- [X] T020 [P] Validate downstream unaffected: after full pipeline run, verify risk-scores, controls, infographic, and report stages produce identical output format — no schema changes needed (SC-006, FR-022)
- [X] T021 Validate guided update description: run `/tachi.architecture` in guided update mode, make specific changes, verify `description` field accurately summarizes the changes (SC-007)

**Checkpoint**: All 7 success criteria verified. All acceptance scenarios from 4 user stories covered.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and cleanup

- [X] T022 [P] Update CLAUDE.md Recent Changes section with Feature 120 summary at `.claude/../CLAUDE.md`
- [X] T023 [P] Verify `.archive/` convention is documented in command file comments for discoverability

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — read-only context loading
- **US1+US2 (Phase 2)**: Depends on Phase 1 — modifies `tachi.architecture.md`
- **US3 (Phase 3)**: Depends on Phase 1 — modifies `tachi.threat-model.md`. Independent of Phase 2.
- **US4 (Phase 4)**: Depends on Phase 2 — extends `tachi.architecture.md` changes from US1+US2
- **Validation (Phase 5)**: Depends on Phases 2, 3, and 4
- **Polish (Phase 6)**: Depends on Phase 5

### User Story Dependencies

- **US1+US2 (P0)**: Can start after Setup. Independent of US3.
- **US3 (P0)**: Can start after Setup. Independent of US1+US2. **Can run in parallel with Phase 2.**
- **US4 (P1)**: Depends on US1+US2 (extends the same command file changes)

### Within Each User Story

- Step 0 (detect) before Step 0a (archive) before Step 3a (frontmatter) — sequential within `tachi.architecture.md`
- Step 1.4 (snapshot) before Step 3 report update — sequential within `tachi.threat-model.md`

### Parallel Opportunities

- **Phase 1**: T001, T002, T003 all read-only — all [P]
- **Phase 2 + Phase 3**: US1+US2 and US3 modify DIFFERENT files — can run in parallel as Wave 1
- **Phase 5**: T012-T020 (except T015) are independent validation scenarios — all [P]
- **Phase 6**: T022, T023 modify different files — both [P]

---

## Parallel Example: Wave 1 (Phase 2 + Phase 3)

```bash
# These modify different files and can run simultaneously:
# Agent A: tachi.architecture.md (T004 → T005 → T006 → T007)
# Agent B: tachi.threat-model.md (T008 → T009)
```

---

## Implementation Strategy

### MVP First (US1+US2+US3 — all P0)

1. Complete Phase 1: Setup (read context)
2. Complete Phase 2: US1+US2 (version tracking + archive) — `tachi.architecture.md`
3. Complete Phase 3: US3 (snapshot) — `tachi.threat-model.md`
4. **STOP and VALIDATE**: Run Phases 5 validation (T012-T020)
5. MVP delivered: versioned architecture files + self-contained threat model output

### Incremental Delivery

1. Setup + US1+US2 + US3 → MVP with versioning, archive, and snapshot
2. Add US4 (guided update) → Enhanced update experience
3. Polish → Documentation updates

### Parallel Team Strategy

With two agents:
1. Both read Setup context (Phase 1)
2. Agent A: US1+US2 on `tachi.architecture.md` (T004-T007)
3. Agent B: US3 on `tachi.threat-model.md` (T008-T009)
4. Both complete → Agent A continues to US4 (T010-T011)
5. Both run validation (T012-T021 split across agents)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 23 |
| Phase 2 (US1+US2) | 4 tasks |
| Phase 3 (US3) | 2 tasks |
| Phase 4 (US4) | 2 tasks |
| Validation tasks | 10 tasks |
| Parallel opportunities | T001-T003, Phase 2+3 concurrent, T012-T020 |
| Files modified | 2 (`tachi.architecture.md`, `tachi.threat-model.md`) |
| Suggested MVP | Phases 1-3 + Phase 5 (P0 features + validation) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1+US2 combined because they modify the same command flow in the same file
- US3 is independent and can run in parallel with US1+US2
- US4 depends on US1+US2 (extends the same file)
- No test tasks (not requested in spec); validation tasks serve as acceptance verification
- Commit after each task or logical group
