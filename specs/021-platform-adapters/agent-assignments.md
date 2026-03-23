---
feature: "021-platform-adapters"
created: 2026-03-23
author: team-lead
status: APPROVED
total_tasks: 40
total_waves: 10
estimated_effort: "7h (3h Sprint 1, 3h Sprint 2, 1h Polish)"
parallel_capacity: "14/40 tasks parallelizable (35%)"
---

# Agent Assignments: Feature 021 - Platform Adapters

**Source**: `specs/021-platform-adapters/tasks.md` (triple sign-off APPROVED)
**Agent Registry**: `.claude/agents/_README.md` (13 registered agents)

---

## Agent Assignment Matrix

All `subagent_type` values below are exact names from `.claude/agents/_README.md`.

| Task ID | Description | Agent | Rationale |
|---------|-------------|-------|-----------|
| T001 | Create adapter directory skeleton | senior-backend-engineer | File/directory creation |
| T002 | Create VERSION file generation script | senior-backend-engineer | Shell scripting |
| T003 | Document shared Metadata YAML format | architect | Design convention definition |
| T004 | Document path rewriting rules per platform | architect | Cross-platform design rules |
| T005 | Transform orchestrator for Claude Code | senior-backend-engineer | File transformation, markdown authoring |
| T006 | Transform 6 STRIDE agents for Claude Code | senior-backend-engineer | Batch file transformation |
| T007 | Transform 5 AI agents for Claude Code | senior-backend-engineer | Batch file transformation |
| T008 | Transform 2 report agents for Claude Code | senior-backend-engineer | File transformation |
| T009 | Generate VERSION for Claude Code adapter | senior-backend-engineer | Script execution |
| T010 | Create Claude Code installation README | senior-backend-engineer | Documentation authoring |
| T011 | Verify content preservation (Claude Code) | code-reviewer | Content diff verification |
| T012 | Create generic orchestrator prompt | senior-backend-engineer | File transformation with structural changes |
| T013 | Create 6 generic STRIDE prompts | senior-backend-engineer | Batch file transformation |
| T014 | Create 5 generic AI prompts | senior-backend-engineer | Batch file transformation |
| T015 | Create 2 generic report prompts | senior-backend-engineer | File transformation |
| T016 | Generate VERSION for generic adapter | senior-backend-engineer | Script execution |
| T017 | Create generic adapter README | senior-backend-engineer | Documentation authoring |
| T018 | Transform orchestrator for Cursor | senior-backend-engineer | File transformation with .mdc format |
| T019 | Transform 6 STRIDE agents for Cursor | senior-backend-engineer | Batch file transformation |
| T020 | Transform 5 AI agents for Cursor | senior-backend-engineer | Batch file transformation |
| T021 | Transform 2 report agents for Cursor | senior-backend-engineer | File transformation |
| T022 | Generate VERSION for Cursor adapter | senior-backend-engineer | Script execution |
| T023 | Create Cursor adapter README | senior-backend-engineer | Documentation authoring |
| T024 | Transform orchestrator for Copilot (size-split) | architect | Size-split design decision + implementation |
| T025 | Transform 6 STRIDE agents for Copilot | senior-backend-engineer | Batch file transformation |
| T026 | Transform 5 AI agents for Copilot | senior-backend-engineer | Batch file transformation |
| T027 | Transform threat-report for Copilot (size-split) | architect | Size-split strategy for 43K agent |
| T028 | Transform threat-infographic for Copilot | senior-backend-engineer | File transformation |
| T029 | Verify Copilot 30K character limit compliance | tester | Validation and constraint verification |
| T030 | Generate VERSION for Copilot adapter | senior-backend-engineer | Script execution |
| T031 | Create Copilot adapter README | senior-backend-engineer | Documentation authoring |
| T032 | Create GitHub Actions workflow YAML | devops | CI/CD workflow authoring |
| T033 | Add error handling to workflow | devops | CI/CD error handling |
| T034 | Add SARIF fingerprint computation | devops | CI/CD output formatting |
| T035 | Generate VERSION for GitHub Actions adapter | senior-backend-engineer | Script execution |
| T036 | Create GitHub Actions README | senior-backend-engineer | Documentation authoring |
| T037 | Update adapters/README.md | senior-backend-engineer | Documentation update |
| T038 | Run output parity validation | tester | Cross-adapter semantic comparison |
| T039 | Update PRD INDEX | senior-backend-engineer | Documentation update |
| T040 | Final review across all 5 adapters | code-reviewer | Cross-cutting quality verification |

### Agent Load Summary

| Agent | Task Count | Load % | Notes |
|-------|-----------|--------|-------|
| senior-backend-engineer | 28 | 70% | Primary execution agent; bulk file transformations |
| architect | 4 | 10% | Convention design + Copilot size-split decisions |
| devops | 3 | 7.5% | GitHub Actions workflow only (Phase 7) |
| code-reviewer | 2 | 5% | Content preservation + final review |
| tester | 2 | 5% | Character limit validation + parity testing |
| orchestrator | 1 | 2.5% | Wave coordination (implicit, not a task) |

**Note**: `senior-backend-engineer` load is high (70%) but spread across 10 waves with no single wave exceeding 4 tasks for this agent. The "backend engineer" role here is file creation, markdown authoring, and script writing -- appropriate per the knowledge-system stack context.

---

## Parallel Execution Waves

### Sprint 1: P0 Adapters (Claude Code + Generic)

Estimated Sprint 1 total: **3 hours**

---

#### Wave 1 -- Setup (Phase 1)

**Prerequisite**: None
**Estimated time**: 15 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T001 | senior-backend-engineer | Yes | Directory skeleton for all 5 adapters |
| T002 | senior-backend-engineer | Yes | VERSION generation script |

**Quality Gate**: Verify directory structure matches spec before proceeding.

---

#### Wave 2 -- Conventions + Generic Kickoff (Phase 2 + US2 start)

**Prerequisite**: Wave 1 complete
**Estimated time**: 30 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T003 | architect | No (sequential with T004) | Metadata YAML format convention |
| T004 | architect | No (after T003, same file) | Path rewriting rules, appends to conventions.md |
| T012 | senior-backend-engineer | Yes (independent of T003/T004) | Generic orchestrator has no Phase 2 dependency |

**CRITICAL NOTE**: T003 and T004 must be sequential -- they write to the same `conventions.md` file. T012 can start immediately since the generic adapter strips all metadata (no dependency on conventions).

**Quality Gate**: Conventions finalized. All subsequent adapter work depends on these rules.

---

#### Wave 3 -- US1 Orchestrator + US2 Batch Agents

**Prerequisite**: Wave 2 complete (conventions finalized for US1; T012 complete for US2 batch)
**Estimated time**: 30 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T005 | senior-backend-engineer | Yes | Claude Code orchestrator (needs conventions) |
| T013 | senior-backend-engineer | Yes | 6 generic STRIDE prompts |
| T014 | senior-backend-engineer | Yes | 5 generic AI prompts |
| T015 | senior-backend-engineer | Yes | 2 generic report prompts |

**Parallelism**: 4 tasks across 2 user stories, all targeting different output files.

---

#### Wave 4 -- US1 Batch Agents

**Prerequisite**: T005 complete (orchestrator establishes transformation pattern for US1)
**Estimated time**: 25 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T006 | senior-backend-engineer | Yes | 6 STRIDE agents for Claude Code |
| T007 | senior-backend-engineer | Yes | 5 AI agents for Claude Code |
| T008 | senior-backend-engineer | Yes | 2 report agents for Claude Code |

**Parallelism**: All 3 tasks write to different files with no cross-dependencies.

---

#### Wave 5 -- US1 + US2 Finalization

**Prerequisite**: Wave 4 complete (all Claude Code agents done); Wave 3 US2 tasks complete
**Estimated time**: 30 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T009 | senior-backend-engineer | Yes | VERSION for Claude Code |
| T010 | senior-backend-engineer | Yes | README for Claude Code |
| T016 | senior-backend-engineer | Yes | VERSION for generic |
| T017 | senior-backend-engineer | Yes | README for generic |

**Parallelism**: 4 tasks, all independent files across 2 adapters.

---

#### Wave 6 -- Sprint 1 Verification

**Prerequisite**: Wave 5 complete (both P0 adapters finalized)
**Estimated time**: 30 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T011 | code-reviewer | Yes | Content preservation check (Claude Code) |
| T038 | tester | Yes | Output parity validation (Claude Code vs. generic) |

**Quality Gate -- Sprint 1 Exit Criteria**:
- All 14 Claude Code agent files present and content-preserved
- All 14 generic prompt files present and self-contained
- Output parity confirmed between Claude Code and generic adapters
- Both adapters have VERSION and README files

**STOP AND VALIDATE before proceeding to Sprint 2.**

---

### Sprint 2: P1 Adapters (Cursor + Copilot + GitHub Actions)

Estimated Sprint 2 total: **3 hours**

---

#### Wave 7 -- US3 + US4 + US5 Parallel Start

**Prerequisite**: Sprint 1 complete; conventions from Wave 2 available
**Estimated time**: 45 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T018 | senior-backend-engineer | Yes | Cursor orchestrator (.mdc format) |
| T024 | architect | Yes | Copilot orchestrator (size-split strategy) |
| T032 | devops | Yes | GitHub Actions workflow YAML |

**Parallelism**: 3 tasks across 3 different user stories, 3 different agents, zero overlap.

---

#### Wave 8 -- Batch Agents + Workflow Enhancement

**Prerequisite**: Wave 7 complete (orchestrators/workflow established per adapter)
**Estimated time**: 45 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T019 | senior-backend-engineer | Yes | 6 Cursor STRIDE rules |
| T020 | senior-backend-engineer | Yes | 5 Cursor AI rules |
| T021 | senior-backend-engineer | Yes | 2 Cursor report rules |
| T025 | senior-backend-engineer | Yes | 6 Copilot STRIDE agents |
| T026 | senior-backend-engineer | Yes | 5 Copilot AI agents |
| T027 | architect | Yes | Copilot threat-report (size-split) |
| T028 | senior-backend-engineer | Yes | Copilot threat-infographic (fits limit) |
| T033 | devops | Yes | Workflow error handling |
| T034 | devops | Yes | SARIF fingerprint computation |

**Parallelism**: 9 tasks across 3 user stories. Cursor and Copilot batch transforms are fully independent. GitHub Actions enhancements are independent of file-transformation adapters.

**Note**: T027 assigned to `architect` because the size-split decision for the 43K threat-report agent requires the same design judgment applied in T024. T033 and T034 are sequential within the GitHub Actions workflow but can run in parallel with all other Wave 8 tasks.

---

#### Wave 9 -- Finalization + Verification

**Prerequisite**: Wave 8 complete (all adapter agents/rules created)
**Estimated time**: 45 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T022 | senior-backend-engineer | Yes | VERSION for Cursor |
| T023 | senior-backend-engineer | Yes | README for Cursor |
| T029 | tester | Yes | Copilot 30K character limit verification |
| T030 | senior-backend-engineer | Yes | VERSION for Copilot |
| T031 | senior-backend-engineer | Yes | README for Copilot |
| T035 | senior-backend-engineer | Yes | VERSION for GitHub Actions |
| T036 | senior-backend-engineer | Yes | README for GitHub Actions |

**Parallelism**: 7 tasks, all independent. T029 (character limit check) can run while READMEs and VERSION files are generated.

**Quality Gate -- Sprint 2 Exit Criteria**:
- All 14 Cursor rule files present with .mdc extension
- All Copilot agents under 30K chars or properly split into agent + instructions
- GitHub Actions workflow has error handling and SARIF fingerprinting
- All 3 adapters have VERSION and README files

---

### Polish Phase

Estimated Polish total: **1 hour**

---

#### Wave 10 -- Cross-Cutting Polish

**Prerequisite**: Sprint 2 complete (all 5 adapters finalized)
**Estimated time**: 45 minutes

| Task | Agent | Parallel | Notes |
|------|-------|----------|-------|
| T037 | senior-backend-engineer | Yes | Update adapters/README.md |
| T039 | senior-backend-engineer | Yes | Update PRD INDEX |
| T040 | code-reviewer | No (after T037, T039) | Final review across all 5 adapters |

**Quality Gate -- Feature Exit Criteria**:
- All 5 adapters independently installable
- All 5 adapters have README.md and VERSION file
- File-transformation adapters (US1, US3, US4) have exactly 14 agent files each
- Output parity confirmed (T038, completed in Sprint 1)
- PRD INDEX updated
- No orphaned references or broken paths

---

## Wave Dependency Graph

```
Wave 1 (Setup)
  |
  v
Wave 2 (Conventions + Generic kickoff)
  |            \
  v             v
Wave 3          |  (US1 orchestrator + US2 batch -- parallel)
  |             |
  v             |
Wave 4          |  (US1 batch agents)
  |             |
  v             v
Wave 5 (US1 + US2 finalization)
  |
  v
Wave 6 (Sprint 1 verification)
  |
  ====== SPRINT BOUNDARY ======
  |
  v
Wave 7 (US3 + US4 + US5 parallel start)
  |
  v
Wave 8 (Batch agents + workflow enhancements)
  |
  v
Wave 9 (Finalization + verification)
  |
  v
Wave 10 (Cross-cutting polish + final review)
```

---

## Sprint Boundaries

### Sprint 1 (P0 -- MVP)

| Metric | Value |
|--------|-------|
| Phases | 1, 2, 3, 4 |
| Waves | 1 through 6 |
| Tasks | T001-T017, T038 (18 tasks) |
| User Stories | US1 (Claude Code), US2 (Generic) |
| Estimated Duration | 3 hours |
| Adapters Delivered | 2 of 5 |
| Deliverables | Claude Code adapter (14 agents), Generic adapter (14 prompts), output parity confirmed |

### Sprint 2 (P1 -- Incremental Delivery)

| Metric | Value |
|--------|-------|
| Phases | 5, 6, 7 |
| Waves | 7 through 9 |
| Tasks | T018-T036 (19 tasks) |
| User Stories | US3 (Cursor), US4 (Copilot), US5 (GitHub Actions) |
| Estimated Duration | 3 hours |
| Adapters Delivered | 3 of 5 (cumulative: 5) |
| Deliverables | Cursor adapter (14 rules), Copilot adapter (14 agents + 2 instructions), GitHub Actions workflow |

### Polish (Cross-Cutting)

| Metric | Value |
|--------|-------|
| Phases | 8 |
| Waves | 10 |
| Tasks | T037, T039, T040 (3 tasks) |
| Estimated Duration | 1 hour |
| Deliverables | Updated adapters/README.md, updated PRD INDEX, final cross-adapter review |

---

## Risk Notes

1. **T003/T004 Sequential Constraint**: Both write to the same `conventions.md`. Cannot be parallelized. Scheduled back-to-back in Wave 2.

2. **T024 Copilot Size-Split Complexity**: The orchestrator is 120K characters -- the largest size-split. Assigned to `architect` for design judgment on what goes into the compact agent vs. the instructions file.

3. **T032 Highest Complexity**: The GitHub Actions workflow YAML is the most architecturally distinct task (CI/CD, not file transformation). Assigned to `devops` with sequential enhancements (T033, T034) in Wave 8.

4. **T027 Threat-Report Size-Split**: At 43K characters, this requires the same split strategy as T024. Also assigned to `architect` for consistency.

5. **senior-backend-engineer Load**: 28 of 40 tasks. Mitigated by wave distribution (max 7 tasks in any wave) and the fact that most tasks are formulaic file transformations following established patterns from the orchestrator tasks.

---

**End of Agent Assignments**
