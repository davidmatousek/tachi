---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 user stories and 17 FRs covered. Zero scope creep. Minor: T051 covers FR-007+FR-008 in one task; T072 spot-checks 3/6 examples (grep covers rest)."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correct, tiered strategy reflected, parallelism sound. Medium: T067 /infographic grep needs regex refinement; docs/architecture non-ADR files high count; verify all 6 examples."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "72 tasks well-calibrated. Critical path correct. Timeline 2-2.5 hours feasible. Medium: ~15 mutable files not explicitly covered by named tasks. Single orchestrator agent correct for atomicity."
---

# Tasks: Rename Tachi Commands to tachi.* Namespace

**Input**: Design documents from `specs/121-rename-tachi-commands/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Organization**: Tasks follow the plan's 4-wave execution strategy, mapped to user stories for traceability.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Prototype Gate)

**Purpose**: Validate the rename pattern with a single command before scaling. Follows PAT-018 (prototype-first gate).

- [X] T001 Rename prototype command: `git mv .claude/commands/threat-model.md .claude/commands/tachi.threat-model.md`
- [X] T002 Update internal cross-references within `.claude/commands/tachi.threat-model.md` (Tier 1 slash patterns only)
- [X] T003 Verify prototype: grep for `/threat-model` in `.claude/commands/tachi.threat-model.md` returns zero matches
- [X] T004 Verify prototype: invoke `/tachi.threat-model` confirms command resolves correctly

**Checkpoint**: Prototype validated — rename pattern works. Scale to remaining commands.

---

## Phase 2: Wave 1 — Command File Renames (US1: Namespace-Prefixed Invocation)

**Goal**: All 6 tachi pipeline commands exist as `tachi.*` prefixed files in `.claude/commands/` and adapter directories.

**Independent Test**: List all files in `.claude/commands/` matching `tachi.*` — should find exactly 6 files.

### Primary Command Renames

- [X] T005 [P] [US1] Rename `git mv .claude/commands/risk-score.md .claude/commands/tachi.risk-score.md`
- [X] T006 [P] [US1] Rename `git mv .claude/commands/compensating-controls.md .claude/commands/tachi.compensating-controls.md`
- [X] T007 [P] [US1] Rename `git mv .claude/commands/infographic.md .claude/commands/tachi.infographic.md`
- [X] T008 [P] [US1] Rename `git mv .claude/commands/security-report.md .claude/commands/tachi.security-report.md`

### New Command

- [X] T009 [US1] Create `.claude/commands/tachi.architecture.md` with bounded stub content per Issue #120

### Adapter Renames

- [X] T010 [P] [US1] Rename `git mv adapters/claude-code/commands/threat-model.md adapters/claude-code/commands/tachi.threat-model.md`
- [X] T011 [P] [US1] Rename `git mv adapters/claude-code/commands/infographic.md adapters/claude-code/commands/tachi.infographic.md`
- [X] T012 [P] [US1] Rename `git mv adapters/claude-code/commands/risk-score.md adapters/claude-code/commands/tachi.risk-score.md`
- [X] T013 [P] [US1] Rename `git mv adapters/github-actions/tachi-threat-model.yml adapters/github-actions/tachi.threat-model.yml`

### Internal Cross-References Within Renamed Files

- [X] T014 [P] [US1] Update internal cross-references in `.claude/commands/tachi.risk-score.md`
- [X] T015 [P] [US1] Update internal cross-references in `.claude/commands/tachi.compensating-controls.md`
- [X] T016 [P] [US1] Update internal cross-references in `.claude/commands/tachi.infographic.md`
- [X] T017 [P] [US1] Update internal cross-references in `.claude/commands/tachi.security-report.md`
- [X] T018 [P] [US1] Update internal cross-references in `adapters/claude-code/commands/tachi.threat-model.md`
- [X] T019 [P] [US1] Update internal cross-references in `adapters/claude-code/commands/tachi.infographic.md`
- [X] T020 [P] [US1] Update internal cross-references in `adapters/claude-code/commands/tachi.risk-score.md`
- [X] T021 [P] [US1] Update internal cross-references in `adapters/github-actions/tachi.threat-model.yml` and `adapters/github-actions/README.md`

**Checkpoint**: All 6 `tachi.*` commands exist. Old unprefixed command files are gone. Internal cross-references updated.

---

## Phase 3: Wave 2 — Cross-Reference Updates (US2: Cross-Reference Integrity)

**Goal**: All references to old command names across agents, skills, templates, schemas, and scripts are updated to new `tachi.*` names.

**Independent Test**: Grep entire codebase for old slash command patterns (`/threat-model`, `/risk-score`, `/compensating-controls`, `/infographic`, `/security-report`) — zero matches outside immutable historical artifacts.

### Tier 1: Slash Command Invocations (safe — automated)

Update all `/old-name` → `/tachi.old-name` patterns across each surface area:

- [X] T022 [P] [US2] Update Tier 1 slash references in `.claude/agents/tachi/orchestrator.md`
- [X] T023 [P] [US2] Update Tier 1 slash references in `.claude/agents/tachi/risk-scorer.md`
- [X] T024 [P] [US2] Update Tier 1 slash references in `.claude/agents/tachi/control-analyzer.md`
- [X] T025 [P] [US2] Update Tier 1 slash references in `.claude/agents/tachi/report-assembler.md`
- [X] T026 [P] [US2] Update Tier 1 slash references in `.claude/agents/tachi/threat-infographic.md`
- [X] T027 [P] [US2] Update Tier 1 slash references in `.claude/agents/tachi/threat-report.md`
- [X] T028 [P] [US2] Update Tier 1 slash references in remaining `.claude/agents/tachi/*.md` files (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse)
- [X] T029 [P] [US2] Update Tier 1 slash references in `.claude/skills/tachi-orchestration/` files
- [X] T030 [P] [US2] Update Tier 1 slash references in `.claude/skills/tachi-risk-scoring/` files
- [X] T031 [P] [US2] Update Tier 1 slash references in `.claude/skills/tachi-control-analysis/` files
- [X] T032 [P] [US2] Update Tier 1 slash references in `.claude/skills/tachi-infographics/` files
- [X] T033 [P] [US2] Update Tier 1 slash references in `.claude/skills/tachi-report-assembly/` files
- [X] T034 [P] [US2] Update Tier 1 slash references in `.claude/skills/tachi-threat-reporting/` files
- [X] T035 [P] [US2] Update Tier 1 slash references in `templates/tachi/output-schemas/*.md` files
- [X] T036 [P] [US2] Update Tier 1 slash references in `templates/tachi/infographics/*.md` files
- [X] T037 [P] [US2] Update Tier 1 slash references in `templates/tachi/security-report/*.typ` files
- [X] T038 [P] [US2] Update Tier 1 slash references in `schemas/*.yaml` files
- [X] T039 [P] [US2] Update Tier 1 slash references in `scripts/*.py` files (error messages, CTA text)
- [X] T040 [P] [US2] Update Tier 1 slash references in `adapters/copilot/` and `adapters/cursor/` files
- [X] T041 [P] [US2] Update Tier 1 slash references in `adapters/claude-code/agents/` files

### Tier 2: Path-Qualified File References (safe — automated)

Update all `commands/old-name.md` → `commands/tachi.old-name.md` patterns:

- [X] T042 [P] [US2] Update Tier 2 path-qualified file references in `.claude/agents/tachi/*.md` files
- [X] T043 [P] [US2] Update Tier 2 path-qualified file references in `.claude/skills/tachi-*/**/*.md` files
- [X] T044 [P] [US2] Update Tier 2 path-qualified file references in `adapters/**/*.md` files
- [X] T045 [P] [US2] Update Tier 2 path-qualified file references in `docs/**/*.md` files (excluding immutable PRDs and ADRs)

### Tier 3: Manual Review (bare filename edge cases)

Review ~20-30 instances of bare command filenames in skill metadata, agent tool lists, and schema `command_ref` fields. Distinguish command file references from pipeline output artifact names:

- [X] T046 [US2] Manual review and update of bare filename references in `.claude/skills/tachi-*/` metadata headers
- [X] T047 [US2] Manual review and update of bare filename references in `schemas/*.yaml` command_ref fields
- [X] T048 [US2] Manual review and update of bare filename references in `.claude/agents/tachi/*.md` tool/command lists

**Checkpoint**: Tier 1 + Tier 2 + Tier 3 complete. Grep verification for old slash patterns returns zero matches outside immutable artifacts.

---

## Phase 4: Wave 3 — Infrastructure & Documentation (US3 + US4 + US5)

**Goal**: Install script handles upgrades cleanly, manifest is updated, all documentation references new names, migration guidance is published.

### US3: Install Script Cleanup

**Independent Test**: Run `scripts/install.sh` against a mock project with old command files — verify old files removed, only `tachi.*` files installed.

- [X] T049 [US3] Add deprecated-file cleanup section to `scripts/install.sh` between version checkout (line 126) and manifest parsing (line 130)
- [X] T050 [US3] Define deprecated files list in `scripts/install.sh`: 5 old command paths
- [X] T051 [US3] Implement cleanup loop: iterate deprecated list, `rm -f` each in target dir, log removals

### US3: Manifest Update

- [X] T052 [US3] Update human-readable "Command Files" table in `INSTALL_MANIFEST.md` (lines 19-29) with new `tachi.*` filenames and add `tachi.architecture.md`
- [X] T053 [US3] Update machine-parseable manifest section in `INSTALL_MANIFEST.md` (lines 72-84) with new `tachi.*` filenames and add `tachi.architecture.md`
- [X] T054 [US3] Update file count references in `INSTALL_MANIFEST.md` from "5 files" to "6 files"

### US4 + US5: Documentation Updates

**Independent Test (US4)**: Verify all 6 `tachi.*` commands appear when listing command files. **Independent Test (US5)**: CHANGELOG contains old-to-new mapping table.

- [X] T055 [P] [US5] Add CHANGELOG migration entry with old-to-new command name mapping table at top of `CHANGELOG.md`
- [X] T056 [P] [US4] Update command references in `CLAUDE.md`
- [X] T057 [P] [US4] Update command references in `README.md`
- [X] T058 [P] [US4] Update command references in `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- [X] T059 [P] [US4] Update command references in `docs/guides/CONSUMER_GUIDE_TACHI.md`
- [X] T060 [P] [US4] Update command references in `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md`
- [X] T061 [P] [US4] Update command references in `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`
- [X] T062 [P] [US4] Update command references in `docs/guides/prompts/developer-guide-prompt.md`
- [X] T063 [P] [US4] Update command references in remaining `docs/**/*.md` files (architecture, devops, planning, research docs — excluding immutable PRDs and ADRs)

**Checkpoint**: Install script handles upgrades, manifest updated, all docs reference new names, CHANGELOG has migration entry.

---

## Phase 5: Verification & Polish

**Purpose**: Final validation that all renames are complete and no old references remain.

- [X] T064 Grep verification: search for `/threat-model` across entire codebase (excluding `specs/*/` except current feature, and `docs/product/02_PRD/`) — must return zero matches
- [X] T065 Grep verification: search for `/risk-score` with same exclusions — must return zero matches
- [X] T066 Grep verification: search for `/compensating-controls` with same exclusions — must return zero matches
- [X] T067 Grep verification: search for `/infographic` with same exclusions — must return zero matches (note: must exclude false positives where `/infographic` appears as a different word context)
- [X] T068 Grep verification: search for `/security-report` with same exclusions — must return zero matches
- [X] T069 Verify all 6 `tachi.*` command files exist in `.claude/commands/`: `tachi.threat-model.md`, `tachi.risk-score.md`, `tachi.compensating-controls.md`, `tachi.infographic.md`, `tachi.security-report.md`, `tachi.architecture.md`
- [X] T070 Verify `INSTALL_MANIFEST.md` machine-parseable section contains only `tachi.*` command filenames
- [X] T071 Verify `adapters/github-actions/VERSION` file is consistent after rename
- [X] T072 Spot-check 3 example directories in `examples/` for updated command name references

**Checkpoint**: All verification passes. Feature ready for PR.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup/Prototype)**: No dependencies — start immediately
- **Phase 2 (Wave 1 File Renames)**: Depends on Phase 1 prototype validation
- **Phase 3 (Wave 2 Cross-References)**: Depends on Phase 2 (files must be renamed before updating references to them)
- **Phase 4 (Wave 3 Infrastructure + Docs)**: Depends on Phase 2 (manifest needs new filenames); can partially overlap with Phase 3
- **Phase 5 (Verification)**: Depends on Phases 2, 3, and 4 all complete

### User Story Dependencies

- **US1 (Command Invocation)**: Phase 2 — can start after prototype (Phase 1)
- **US2 (Cross-Reference Integrity)**: Phase 3 — depends on US1 file renames completing
- **US3 (Upgrade Cleanup)**: Phase 4 (install script + manifest) — depends on Phase 2
- **US4 (Command Discovery)**: Achieved by US1 rename — documentation in Phase 4
- **US5 (Migration Guidance)**: Phase 4 (CHANGELOG) — depends on knowing final command names

### Parallel Opportunities

**Phase 2**: All primary renames (T005-T008) can run in parallel. All adapter renames (T010-T013) can run in parallel. All internal cross-ref updates (T014-T021) can run in parallel.

**Phase 3**: All Tier 1 tasks (T022-T041) can run in parallel (different file surfaces). All Tier 2 tasks (T042-T045) can run in parallel. Tier 3 tasks (T046-T048) can run in parallel.

**Phase 4**: Documentation tasks (T055-T063) can all run in parallel. Install script tasks (T049-T051) are sequential.

---

## Parallel Example: Phase 2 (Wave 1)

```
# Launch all primary renames in parallel:
Agent: "git mv .claude/commands/risk-score.md .claude/commands/tachi.risk-score.md"
Agent: "git mv .claude/commands/compensating-controls.md .claude/commands/tachi.compensating-controls.md"
Agent: "git mv .claude/commands/infographic.md .claude/commands/tachi.infographic.md"
Agent: "git mv .claude/commands/security-report.md .claude/commands/tachi.security-report.md"

# Then launch all internal cross-ref updates in parallel:
Agent: "Update refs in tachi.risk-score.md"
Agent: "Update refs in tachi.compensating-controls.md"
Agent: "Update refs in tachi.infographic.md"
Agent: "Update refs in tachi.security-report.md"
```

## Parallel Example: Phase 3 (Wave 2)

```
# Launch all Tier 1 surface areas in parallel:
Agent: "Update agents in .claude/agents/tachi/"
Agent: "Update skills in .claude/skills/tachi-*/"
Agent: "Update templates in templates/tachi/"
Agent: "Update schemas in schemas/"
Agent: "Update scripts in scripts/*.py"
Agent: "Update adapters in adapters/"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Prototype gate
2. Complete Phase 2: All file renames
3. **STOP and VALIDATE**: All 6 `tachi.*` commands resolve correctly
4. Remaining phases add cross-reference integrity and documentation

### Incremental Delivery

1. Phase 1 + 2 → File renames complete (US1 done)
2. Phase 3 → Cross-references updated (US2 done)
3. Phase 4 → Install cleanup + docs (US3, US4, US5 done)
4. Phase 5 → Verified and ready for PR

### Single-Agent Strategy (recommended for atomicity)

Given the atomic delivery requirement (FR-016), a single orchestrator agent should execute all phases sequentially to ensure consistency. Parallel execution within phases is fine, but inter-phase sequencing must be preserved.

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 72 |
| Phase 1 (Setup/Prototype) | 4 |
| Phase 2 (File Renames — US1) | 17 |
| Phase 3 (Cross-References — US2) | 27 |
| Phase 4 (Infrastructure + Docs — US3/US4/US5) | 15 |
| Phase 5 (Verification) | 9 |
| Parallelizable tasks | 52 |
| User stories covered | 5/5 |

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Prototype-first (Phase 1) catches pattern issues before bulk execution
- Tier 1/2/3 pattern strategy prevents output artifact name corruption (Architect concern M-1)
- Historical artifacts (PRDs, archived specs, old CHANGELOG entries) are excluded from all updates
- All 72 tasks must complete before the single atomic PR to main
