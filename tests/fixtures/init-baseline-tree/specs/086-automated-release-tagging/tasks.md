---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "All 4 user stories covered. All 15 FRs trace to tasks. Zero scope creep. Phase-based organization correct for shared config files."
  architect_signoff:
    agent: architect
    date: 2026-04-06
    status: APPROVED
    notes: "Dependencies correctly ordered. Parallel opportunities valid. All tasks map 1:1 to plan deliverables. install.sh compatibility confirmed at code level. Advisory: T005 missing [P] marker (cosmetic)."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-06
    status: APPROVED
    notes: "Granularity proportional to scope. Critical path: T001→T002→T005. Parallel depth optimal. Estimated 30-45 minutes total. 3-wave agent assignment created."
---

# Tasks: Automated Release Tagging via GitHub Actions

**Input**: Design documents from `specs/086-automated-release-tagging/`
**Prerequisites**: plan.md (required), spec.md (required)

**Note**: All 4 user stories (US1-US4) are delivered by the same 3 configuration files. The tasks are organized by implementation phase rather than per-story, since the files are indivisible deliverables that satisfy all stories simultaneously.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create directory structure for GitHub Actions workflow

- [X] T001 Create `.github/workflows/` directory for GitHub Actions workflow files

---

## Phase 2: Core Configuration (US1 + US2 + US3 — P0)

**Purpose**: Create the 3 configuration files that deliver automated release tagging, CHANGELOG generation, and release timing control

**Goal**: After this phase, pushing to main triggers release-please to create Release PRs with auto-determined version bumps and grouped CHANGELOG entries

- [X] T002 [P] [US1] Create GitHub Actions workflow at `.github/workflows/release-please.yml` with trigger on push to main, permissions for contents:write and pull-requests:write, using googleapis/release-please-action@v4 with release-type simple
- [X] T003 [P] [US2] Create release configuration at `release-please-config.json` with release-type simple, changelog-sections mapping conventional commit types to CHANGELOG groups (Features, Bug Fixes, Documentation, Miscellaneous), and include-component-in-tag false
- [X] T004 [P] [US1] Create version manifest at `.release-please-manifest.json` with initial content `{"." : "4.0.0"}` matching the existing v4.0.0 tag baseline

**Checkpoint**: All 3 core files created. US1 (auto tagging), US2 (CHANGELOG), and US3 (release timing control) are delivered by these files working together.

---

## Phase 3: Verification & Documentation (US4 — P1)

**Purpose**: Verify backward compatibility with install.sh and update documentation

- [X] T005 [US4] Verify tag format compatibility — confirm that release-please's `vMAJOR.MINOR.PATCH` tag format works with `scripts/install.sh --version` by reviewing install.sh tag validation logic (git rev-parse, git checkout, git describe)
- [X] T006 [P] Verify CHANGELOG.md compatibility — confirm existing manual CHANGELOG.md content is preserved when release-please prepends new entries (review CHANGELOG.md header format)
- [X] T007 [P] Add release process documentation section to README.md explaining that releases are automated via release-please, conventional commits drive version bumps, and the maintainer merges the Release PR to publish

**Checkpoint**: All verification complete. US4 (install.sh compatibility) confirmed. Documentation updated.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Core Configuration (Phase 2)**: Depends on Phase 1 (T001 creates the directory for T002)
- **Verification & Documentation (Phase 3)**: Depends on Phase 2 (files must exist to verify)

### Parallel Opportunities

- **Phase 2**: T002, T003, T004 are all [P] — different files, can be created simultaneously
- **Phase 3**: T005, T006, T007 are independent verification tasks that can run in parallel

### User Story Coverage

| User Story | Delivered By | Verified By |
|-----------|-------------|-------------|
| US1: Auto Version Tag | T002, T004 | (end-to-end after merge to main) |
| US2: Auto CHANGELOG | T003 | T006 |
| US3: Release Timing Control | T002 (workflow design) | (inherent — Release PR is not auto-merged) |
| US4: install.sh Compatibility | T002, T004 (tag format) | T005 |

---

## Implementation Strategy

### Single-Wave MVP

1. Complete T001 (Setup)
2. Complete T002 + T003 + T004 in parallel (Core Configuration)
3. Complete T005 + T006 + T007 in parallel (Verification)
4. **DONE**: All 4 user stories delivered, all 7 success criteria met

### End-to-End Validation (post-merge)

After merging to main, the real validation occurs:
1. Push triggers release-please workflow
2. release-please creates a Release PR with version bump + CHANGELOG entries
3. Maintainer reviews and merges Release PR
4. Git tag + GitHub Release are created automatically
5. `install.sh --version vX.Y.Z` works with the new tag

---

## Notes

- Total tasks: 7
- Parallel opportunities: Phase 2 (3 tasks) and Phase 3 (3 tasks)
- No test tasks included — this is configuration-only with no application logic to unit test
- End-to-end validation happens post-merge when the workflow actually runs on GitHub
