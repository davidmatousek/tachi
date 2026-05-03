# Agent Assignments: Feature 104 — Downstream Baseline Propagation

**Date**: 2026-04-08
**Feasibility**: APPROVED
**Total Tasks**: 18 across 7 phases
**Estimated Waves**: 5 execution waves

---

## Agent Assignment Matrix

| Agent | Tasks Assigned | Load | Rationale |
|-------|---------------|------|-----------|
| senior-backend-engineer | T004, T005, T006, T010, T013 | 5 tasks (28%) | Python scripts: shared parser, both extraction scripts |
| architect | T001, T002, T003 | 3 tasks (17%) | Schema template design — defines the delta contract |
| security-analyst | T008, T009 | 2 tasks (11%) | Threat-report agent instructions (security domain expertise) |
| frontend-developer | T011, T014 | 2 tasks (11%) | Agent instruction markdown (infographic + report-assembler) |
| orchestrator | T012, T015 | 2 tasks (11%) | Command file updates (infographic + security-report commands) |
| tester | T007, T016, T017 | 3 tasks (17%) | Validation: parser verification, primary test, regression test |
| senior-backend-engineer | T018 | 1 task (6%) | Example output regeneration (requires running Python pipeline) |

**Total agent load**: No agent exceeds 5 tasks (28%). Workload is balanced.

---

## Parallel Execution Waves

### Wave 1: Schema Foundation (Blocking)

**Gate**: Must complete before Wave 2

| Task | Agent | File | Description |
|------|-------|------|-------------|
| T001 [P] | architect | `templates/tachi/output-schemas/threats.md` | Add Status column to Section 7 |
| T002 [P] | architect | `templates/tachi/output-schemas/threats.md` | Add Section 8 Delta Summary |
| T003 [P] | architect | `templates/tachi/output-schemas/threat-report.md` | Update schema v1.0 to v1.1 |

**Notes**: T001 and T002 target the same file but different sections (Section 7 vs Section 8). Assign to same agent to avoid conflict. T003 is a different file, truly parallel.

**Estimated effort**: Small — markdown template edits

---

### Wave 2: Shared Parser + Threat Report Agent (Parallel Streams)

**Gate**: Wave 1 complete. Must complete before Wave 3.

**Stream A: Shared Parser** (sequential within stream — same file)

| Task | Agent | File | Description |
|------|-------|------|-------------|
| T004 | senior-backend-engineer | `scripts/tachi_parsers.py` | Add `parse_baseline_frontmatter()` |
| T005 | senior-backend-engineer | `scripts/tachi_parsers.py` | Add `parse_resolved_findings()` |
| T006 | senior-backend-engineer | `scripts/tachi_parsers.py` | Extend `parse_threats_findings()` with delta_status |

**Stream B: Threat Report Agent** (independent — reads threats.md directly, no parser dependency)

| Task | Agent | File | Description |
|------|-------|------|-------------|
| T008 [P] | security-analyst | `agents/threat-report.md` | Update input contract |
| T009 | security-analyst | `agents/threat-report.md` | Update output instructions with Section 8 |

**Notes**: Stream A and Stream B run in parallel. Stream A tasks are sequential (same file). Stream B tasks are sequential (same file, input contract before output instructions).

**Estimated effort**: Medium — Python function additions + agent instruction rewrites

---

### Quality Gate 1: Foundation Validation

**Prerequisite**: Wave 2 complete (both streams)

| Task | Agent | Description |
|------|-------|-------------|
| T007 | tester | Validate parser functions against example outputs |

**Pass criteria**: `parse_threats_findings()` returns delta_status when present, returns identical output when absent. `parse_resolved_findings()` parses Section 4b. `parse_baseline_frontmatter()` extracts nested baseline fields.

**Estimated effort**: Small — manual verification

---

### Wave 3: Downstream Consumers (Maximum Parallelism)

**Gate**: Quality Gate 1 passed. Must complete before Wave 4.

**Stream A: Infographic Pipeline (US2)**

| Task | Agent | File | Description |
|------|-------|------|-------------|
| T010 [P] | senior-backend-engineer | `scripts/extract-infographic-data.py` | Delta-aware extraction |
| T011 [P] | frontend-developer | `agents/threat-infographic.md` | Update agent instructions |
| T012 | orchestrator | `.claude/commands/infographic.md` | Update command with delta context |

**Notes**: T010 and T011 are parallel (different files). T012 depends on both (command references agent behavior and extracted data).

**Stream B: PDF Report Pipeline (US3)**

| Task | Agent | File | Description |
|------|-------|------|-------------|
| T013 [P] | senior-backend-engineer | `scripts/extract-report-data.py` | Delta-aware extraction |
| T014 [P] | frontend-developer | `.claude/agents/tachi/report-assembler.md` | Update agent instructions |
| T015 | orchestrator | `.claude/commands/security-report.md` | Update command with delta context |

**Notes**: T013 and T014 are parallel (different files). T015 depends on both. Streams A and B are fully independent.

**Estimated effort**: Medium — extraction script changes + agent/command instruction updates

---

### Wave 4: End-to-End Validation

**Gate**: Wave 3 complete (all user stories implemented)

| Task | Agent | Description |
|------|-------|-------------|
| T016 | tester | Primary validation: baseline-compared threat model on second-brain-mcp |
| T017 | tester | Regression validation: no-baseline run produces pre-104 behavior |

**Notes**: T016 and T017 can run in parallel (different test scenarios, read-only validation). T016 must pass before T018 (example regeneration uses the validated pipeline).

**Pass criteria**: RESOLVED excluded from active counts in all three formats. NEW highlighted. Section 8 present. No-baseline output identical to pre-104.

**Estimated effort**: Medium — full pipeline execution and manual verification

---

### Wave 5: Example Regeneration

**Gate**: Wave 4 passed (both validation tests)

| Task | Agent | Description |
|------|-------|-------------|
| T018 | senior-backend-engineer | Regenerate all 6 example outputs with delta-aware pipeline |

**Notes**: Requires running the complete pipeline against all example architectures. Sequential by nature (each example is a full pipeline run).

**Estimated effort**: Medium — 6 full pipeline executions

---

## Wave Summary

| Wave | Tasks | Parallelism | Agents Active | Blocking? |
|------|-------|-------------|---------------|-----------|
| Wave 1 | T001, T002, T003 | 3 parallel | 1 (architect) | Yes — schema contract |
| Wave 2 | T004-T006, T008-T009 | 2 streams parallel | 2 (senior-backend-engineer, security-analyst) | Yes — parser + agent foundation |
| QG1 | T007 | 1 sequential | 1 (tester) | Yes — foundation validation |
| Wave 3 | T010-T015 | 2 streams x 3 tasks | 4 (senior-backend-engineer, frontend-developer, orchestrator x2) | Yes — all consumers |
| Wave 4 | T016, T017 | 2 parallel | 1 (tester) | Yes — validation |
| Wave 5 | T018 | 1 sequential | 1 (senior-backend-engineer) | No — polish |

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Same-file contention in tachi_parsers.py | All parser tasks assigned to single agent (sequential) | senior-backend-engineer |
| Same-file contention in schema templates | T001+T002 assigned to same agent | architect |
| Validation delays in Wave 4 | Tester runs both scenarios in parallel | tester |
| Example regeneration scope creep | Scope limited to 6 existing examples, no new examples | senior-backend-engineer |

---

## Feasibility Assessment

| Dimension | Assessment |
|-----------|-----------|
| **Effort** | 18 tasks across 10 files. No new files. All changes are additive. Well within single-session capacity. |
| **Capacity** | 6 agents engaged, no agent exceeds 28% load. Balanced distribution. |
| **Timeline** | 5 waves with clear gates. Optimistic: 4 waves (skip QG1 if confident). Realistic: 5 waves. Pessimistic: 6 waves (if validation reveals issues requiring rework). |
| **Dependencies** | All dependencies are internal. No external blockers. Feature 074 confirmed stable. |

**Verdict**: FEASIBLE

**Confidence**: High — the feature modifies existing files with additive changes following an established pattern (Feature 074 delta branching). No new architectural decisions required.
