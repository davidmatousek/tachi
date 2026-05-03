---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "6/6 user stories covered, 20/20 FRs mapped, zero scope creep, MVP correctly scoped to Phase 1+2 (US1+US2+US4). Priority ordering correct — P0 before P1."
  architect_signoff:
    agent: architect
    date: 2026-04-06
    status: APPROVED_WITH_CONCERNS
    notes: "4 low-severity notes: (1) common.sh should NOT be sourced in install.sh (runs from target), (2) manifest path granularity to resolve during implementation, (3) T009 should use git -C for source version, (4) copy loop must prepend SOURCE_DIR to paths."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-06
    status: APPROVED
    notes: "20 tasks well-sized (20-45 min each). Realistic estimate 6.25 hrs with parallelism, within PRD 7-10 hr estimate. Single-agent feature (senior-backend-engineer). Critical path correctly identified."
---

# Tasks: Install Script and Version Tagging

**Input**: Design documents from `/specs/066-install-script-and/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not requested in spec — test tasks omitted. Testing strategy documented in plan.md for manual validation.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US3, US5, US6)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Create the machine-parseable manifest section and install script scaffold that all user stories depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T001 Add machine-parseable section to INSTALL_MANIFEST.md between `<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->` markers with one distributable path per line (directories with trailing `/`, files without)
- [X] T002 Update INSTALL_MANIFEST.md maintenance checklist to include "update the machine-parseable section" as a checklist item
- [X] T003 Create scripts/install.sh scaffold with `#!/usr/bin/env bash`, `set -euo pipefail`, color constants (RED, GREEN, NC), `die()` helper, and `usage()` function displaying --source, --version, --help flags

**Checkpoint**: Manifest has parseable section, install.sh scaffold exists and is syntactically valid.

---

## Phase 2: US1 - First-Time Install (Priority: P0) MVP

**Goal**: A user runs one command from their project root and all manifest files are copied from the tachi source directory.

**Also satisfies**: US2 (Update Existing Install) — `cp -r` overwrites by default, making the script idempotent. US4 (Custom Source Location) — source auto-detection and `--source` override are built as part of core argument handling.

**Independent Test**: Clone tachi, create an empty target directory, run `install.sh` from target root, verify all manifest files present with version summary displayed.

- [X] T004 [US1] Implement source auto-detection in scripts/install.sh using `${BASH_SOURCE[0]}` + `dirname` + `pwd` pattern to resolve SCRIPT_DIR, then derive SOURCE_DIR as parent directory
- [X] T005 [US1] Implement argument parsing in scripts/install.sh using `while/case` pattern: `--source <path>` overrides auto-detected source, `--version <tag>` stores requested version, `--help` calls usage() and exits
- [X] T006 [US1] Implement environment validation in scripts/install.sh: verify SOURCE_DIR exists, verify INSTALL_MANIFEST.md exists in SOURCE_DIR, verify git is available (warn if not — needed for version reporting)
- [X] T007 [US1] Implement manifest parsing function in scripts/install.sh: extract lines between `<!-- BEGIN MANIFEST -->` and `<!-- END MANIFEST -->` markers, skip blank lines and comment lines (starting with `#`)
- [X] T008 [US1] Implement file copy loop in scripts/install.sh: for each manifest path, determine if directory (trailing `/`) or file, run `mkdir -p` for target parent directory, run `cp -r` for directories or `cp` for files, count successes and warn on failures (continue copying remaining paths)
- [X] T009 [US1] Implement summary output in scripts/install.sh: display installed version via `git describe --tags --always` (or "untagged" if git unavailable), file/directory count, and source path
- [X] T010 [US1] Make scripts/install.sh executable with `chmod +x scripts/install.sh`

**Checkpoint**: US1 + US2 + US4 independently verifiable. Fresh install copies all files; re-run produces identical result; `--source` override works; auto-detection works when script is at its canonical location.

---

## Phase 3: US3 - Pinned Version Install (Priority: P1)

**Goal**: A user specifies `--version v4.0.0` and the script installs files from that exact tagged version, safely restoring the source repo afterward.

**Independent Test**: Create a test tag, run `install.sh --version <tag>`, verify correct files installed and source repo restored to original branch.

- [X] T011 [US3] Implement dirty working tree check in scripts/install.sh: when `--version` is specified, run `git -C "$SOURCE_DIR" status --porcelain` and `die` with clear message if output is non-empty
- [X] T012 [US3] Implement branch recording in scripts/install.sh: capture original ref via `git -C "$SOURCE_DIR" rev-parse --abbrev-ref HEAD`, with fallback to full SHA via `git -C "$SOURCE_DIR" rev-parse HEAD` when result is literal `HEAD` (detached HEAD state)
- [X] T013 [US3] Implement trap cleanup EXIT handler in scripts/install.sh: use guard variable (`ORIGINAL_REF=""`) populated only after confirming checkout will proceed; cleanup checks for non-empty guard before running `git -C "$SOURCE_DIR" checkout "$ORIGINAL_REF" --quiet`
- [X] T014 [US3] Implement tag validation in scripts/install.sh: verify requested tag exists with `git -C "$SOURCE_DIR" rev-parse --verify "refs/tags/$VERSION_TAG"`, on failure list available tags via `git -C "$SOURCE_DIR" tag -l 'v*' --sort=-v:refname` and die
- [X] T015 [US3] Implement git checkout of requested tag in scripts/install.sh: run `git -C "$SOURCE_DIR" checkout "$VERSION_TAG" --quiet` after dirty check, branch recording, and trap registration

**Checkpoint**: US3 independently verifiable. Version-pinned install works, invalid tags show available versions, dirty tree is refused, branch restoration works on normal exit, error exit, and Ctrl+C interrupt.

---

## Phase 4: US5 - Manual Install Preserved (Priority: P1)

**Goal**: README and Developer Guide present scripted install as primary path while preserving manual commands as alternative.

**Independent Test**: Open README and Developer Guide, verify scripted install is visible by default and manual commands are in collapsible section.

- [X] T016 [P] [US5] Update README.md Step 2: replace 6 `cp -r` commands with single `install.sh` invocation from target project root, show version-pinned example as secondary, wrap existing manual commands in `<details><summary>Manual install (alternative)</summary>` block, preserve INSTALL_MANIFEST.md reference
- [X] T017 [P] [US5] Update docs/guides/DEVELOPER_GUIDE_TACHI.md Step 2 install section: replace manual copy commands with `install.sh` invocation matching README, preserve manual commands as alternative reference

**Checkpoint**: US5 independently verifiable. Both docs show scripted install primary, manual commands accessible in collapsible section.

---

## Phase 5: US6 - Version Tagging Adoption (Priority: P1)

**Goal**: The tachi repository has its first semantic version tag, enabling version-pinned installs and `git describe` version reporting.

**Independent Test**: Run `git describe --tags` and verify it returns `v4.0.0` or a distance-from-tag string.

- [ ] T018 [US6] After PR merge to main, create annotated tag `v4.0.0` with message "Release v4.0.0 — first tagged release with install script" via `git tag -a v4.0.0 -m "..."` and push with `git push origin v4.0.0`

**Checkpoint**: US6 verifiable. `git describe --tags` returns meaningful version string.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality validation and final checks.

- [X] T019 [P] Run shellcheck on scripts/install.sh and fix any warnings
- [X] T020 [P] Verify all paths in machine-parseable manifest section match actual distributable files in the repository

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on Phase 1 completion — BLOCKS US3 and docs
- **US3 (Phase 3)**: Depends on Phase 2 (core script must exist to add version support)
- **US5 (Phase 4)**: Depends on Phase 2 (script must exist to document it). Can run in parallel with Phase 3.
- **US6 (Phase 5)**: Depends on PR merge to main — independent of other phases
- **Polish (Phase 6)**: Depends on Phase 2 + Phase 3 completion

### User Story Dependencies

- **US1 + US2 + US4 (P0)**: Can start after Foundational — no dependencies on other stories
- **US3 (P1)**: Depends on US1 (adds --version to existing script)
- **US5 (P1)**: Depends on US1 (documents the script). Can parallel with US3.
- **US6 (P1)**: Independent — can parallel with any phase, but tag created after merge

### Parallel Opportunities

- T001 and T002 can run in parallel (different sections of same file, but sequential is safer)
- T016 and T017 can run in parallel (different files)
- T019 and T020 can run in parallel (different validation scopes)
- Phase 3 (US3) and Phase 4 (US5) can run in parallel after Phase 2 completes

---

## Parallel Example: Phase 4 (US5)

```
# Documentation tasks can run simultaneously (different files):
Task: "Update README.md Step 2" (T016)
Task: "Update Developer Guide install section" (T017)
```

## Parallel Example: After Phase 2

```
# US3 and US5 can run in parallel (different concerns):
Wave A: Phase 3 tasks (T011-T015) — version checkout support
Wave B: Phase 4 tasks (T016-T017) — documentation updates
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Foundational (manifest + scaffold)
2. Complete Phase 2: US1 (core install script)
3. **STOP and VALIDATE**: Run install.sh from empty target, verify all files copied
4. This MVP already satisfies US1, US2, and US4

### Incremental Delivery

1. Foundation → US1 core script → **MVP ready**
2. Add US3 (version checkout) → Test with tags
3. Add US5 (docs update) → README + Guide reflect new install path
4. Merge PR → Add US6 (tag v4.0.0) → Full feature complete
5. Polish → shellcheck + manifest verification

### Summary

| Metric | Value |
|--------|-------|
| Total tasks | 20 |
| Phases | 6 |
| Parallel opportunities | 4 (T016/T017, T019/T020, Phase 3 ∥ Phase 4) |
| MVP scope | Phase 1 + Phase 2 (10 tasks) |
| Post-merge task | 1 (T018 — git tag) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 (Update) and US4 (Custom Source) are satisfied by US1 implementation — no separate tasks needed
- US6 (Version Tagging) T018 executes after PR merge to main, not during feature branch work
- Architect concerns addressed: trap guard (T013), detached HEAD fallback (T012), manifest checklist (T002)
- Commit after each task or logical group
