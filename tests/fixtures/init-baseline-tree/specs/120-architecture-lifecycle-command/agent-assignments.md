# Agent Assignments: Feature 120 — Architecture Lifecycle Command

**Generated**: 2026-04-09
**Total Tasks**: 23
**Estimated Wall-Clock**: 45-55 minutes (with 2-agent parallelism)

## Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001 | orchestrator | Context loading — reads file, distributes to agents |
| T002 | orchestrator | Context loading — reads file, distributes to agents |
| T003 | orchestrator | Context loading — reads files, distributes to agents |
| T004 | senior-backend-engineer | Markdown command file editing — `tachi.architecture.md` |
| T005 | senior-backend-engineer | Markdown command file editing — `tachi.architecture.md` |
| T006 | senior-backend-engineer | Markdown command file editing — `tachi.architecture.md` |
| T007 | senior-backend-engineer | Markdown command file editing — `tachi.architecture.md` |
| T008 | senior-backend-engineer | Markdown command file editing — `tachi.threat-model.md` |
| T009 | senior-backend-engineer | Markdown command file editing — `tachi.threat-model.md` |
| T010 | senior-backend-engineer | Markdown command file editing — `tachi.architecture.md` |
| T011 | senior-backend-engineer | Markdown command file editing — `tachi.architecture.md` |
| T012 | tester | Validation scenario execution |
| T013 | tester | Validation scenario execution |
| T014 | tester | Validation scenario execution |
| T015 | tester | Validation scenario execution (sequential multi-run) |
| T016 | tester | Validation scenario execution |
| T017 | tester | Validation scenario execution |
| T018 | tester | Validation scenario execution |
| T019 | tester | Validation scenario execution |
| T020 | tester | Validation scenario execution |
| T021 | tester | Validation scenario execution |
| T022 | senior-backend-engineer | Documentation update — CLAUDE.md |
| T023 | senior-backend-engineer | Documentation review — command file comments |

## Parallel Execution Waves

### Wave 0: Setup (5 min)
**Agent**: orchestrator

| Task | Description |
|------|-------------|
| T001 | Read `tachi.architecture.md` |
| T002 [P] | Read `tachi.threat-model.md` |
| T003 [P] | Read example architecture files |

**Quality Gate**: All context loaded, no missing files.

---

### Wave 1: Core Implementation (15-20 min)
**Agents**: 2x senior-backend-engineer (parallel)

| Stream A: `tachi.architecture.md` | Stream B: `tachi.threat-model.md` |
|-----------------------------------|------------------------------------|
| T004 [US1] Detect existing file | T008 [US3] Architecture snapshot |
| T005 [US2] Archive mechanism | T009 [US3] Report update |
| T006 [US1] Inject frontmatter | |
| T007 [US1] Report update | |

**Quality Gate**: Both command files updated. Run quick smoke test: `/tachi.architecture` on a test project produces frontmatter; `/tachi.threat-model` output folder contains snapshot.

---

### Wave 2: Guided Update Mode (10 min)
**Agent**: senior-backend-engineer

| Task | Description |
|------|-------------|
| T010 [US4] | Guided update categories in `tachi.architecture.md` |
| T011 [US4] | Description field population |

**Quality Gate**: Guided mode presents categories and produces accurate description.

---

### Wave 3: Validation (25-30 min)
**Agents**: 2x tester (parallel)

| Tester A | Tester B |
|----------|----------|
| T012 First-time generation | T016 Checksum integrity |
| T013 Legacy file upgrade | T017 Threat model snapshot |
| T014 Managed update | T018 Snapshot skip |
| T015 Multi-run continuity | T019 Backward compatibility (3 examples) |
| T021 Guided update description | T020 Downstream unaffected |

**Quality Gate**: All 7 success criteria verified. All acceptance scenarios pass.

---

### Wave 4: Polish (5 min)
**Agent**: senior-backend-engineer

| Task | Description |
|------|-------------|
| T022 [P] | Update CLAUDE.md |
| T023 [P] | Verify archive convention documented |

**Quality Gate**: Documentation current. Feature ready for PR.

---

## Time Estimates

| Wave | Duration | Agents | Bottleneck |
|------|----------|--------|------------|
| Wave 0 | 5 min | 1 orchestrator | File reads |
| Wave 1 | 15-20 min | 2 senior-backend-engineer | Stream A (4 tasks vs 2) |
| Wave 2 | 10 min | 1 senior-backend-engineer | Sequential edits |
| Wave 3 | 25-30 min | 2 tester | Command execution cycles |
| Wave 4 | 5 min | 1 senior-backend-engineer | Parallel edits |
| **Total** | **45-55 min** | **Peak: 2 agents** | |

## Critical Path

```
T001 → T004 → T005 → T006 → T007 → T010 → T011 → T012 → T015 → T022
```

Length: 10 tasks (longest chain through US1+US2 → US4 → validation → polish)
