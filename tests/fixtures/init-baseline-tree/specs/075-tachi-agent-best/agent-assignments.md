# Agent Assignments: Feature 075 — Tachi Agent Best Practices

**Feature**: 075-tachi-agent-best
**Generated**: 2026-03-31
**Total Tasks**: 29 across 5 waves
**Feature Type**: Docs-only (markdown/YAML editing, zero application code)

---

## Agent Assignment Matrix

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Record baseline line counts | senior-backend-engineer | Shell + markdown output |
| T002 | Capture pre-extraction pipeline output checksums | tester | Baseline capture for regression |
| T003 | Create tachi-orchestration SKILL.md | senior-backend-engineer | Markdown authoring |
| T004 | Extract SARIF specification from orchestrator | senior-backend-engineer | Content extraction to markdown |
| T005 | Extract dispatch rules from orchestrator | senior-backend-engineer | Content extraction to markdown |
| T006 | Extract output schemas from orchestrator | senior-backend-engineer | Content extraction to markdown |
| T007 | Refactor orchestrator.md post-extraction | senior-backend-engineer | Agent file refactoring |
| T008 | Create tachi-risk-scoring SKILL.md | senior-backend-engineer | Markdown authoring |
| T009 | Extract scoring dimensions from risk-scorer | senior-backend-engineer | Content extraction to markdown |
| T010 | Extract CVSS vectors from risk-scorer | senior-backend-engineer | Content extraction to markdown |
| T011 | Extract severity bands from risk-scorer | senior-backend-engineer | Content extraction to markdown |
| T012 | Refactor risk-scorer.md post-extraction | senior-backend-engineer | Agent file refactoring |
| T013 | Create tachi-control-analysis SKILL.md | senior-backend-engineer | Markdown authoring |
| T014 | Extract control categories from control-analyzer | senior-backend-engineer | Content extraction to markdown |
| T015 | Extract evidence criteria from control-analyzer | senior-backend-engineer | Content extraction to markdown |
| T016 | Extract residual risk formulas from control-analyzer | senior-backend-engineer | Content extraction to markdown |
| T017 | Refactor control-analyzer.md post-extraction | senior-backend-engineer | Agent file refactoring |
| T018 | Verify all methodology agents <=1,000 lines | tester | Line count verification |
| T019 | Tone audit 6 STRIDE leaf agents | senior-backend-engineer | Markdown editing across 6 files |
| T020 | Tone audit 5 AI threat leaf agents | senior-backend-engineer | Markdown editing across 5 files |
| T021 | Tone audit 2 report agents | senior-backend-engineer | Markdown editing across 2 files |
| T022 | Tone audit 3 methodology agents (post-extraction) | senior-backend-engineer | Markdown editing, data-top verification |
| T023 | Tone audit threat-report agent | senior-backend-engineer | Markdown editing |
| T024 | Trim threat-report.md to <=800 lines | senior-backend-engineer | Whitespace/comment consolidation |
| T025 | Verify threat-report.md <=800 lines | tester | Line count verification |
| T026 | Run full pipeline and compare against baseline | tester | Output equivalence validation |
| T027 | Verify all 18 agents within tier caps | tester | Batch line count verification |
| T028 | Verify all 18 agents pass 8-criterion quality checklist | code-reviewer | Quality checklist assessment |
| T029 | Update compliance table in best practices doc | senior-backend-engineer | Markdown table update |

### Agent Workload Summary

| Agent | Tasks | Task IDs |
|-------|-------|----------|
| senior-backend-engineer | 21 | T001, T003-T017, T019-T024, T029 |
| tester | 5 | T002, T018, T025-T027 |
| code-reviewer | 1 | T028 |
| orchestrator | -- | Wave coordination (implicit) |

---

## Parallel Execution Waves

### Wave 1: Setup (Baseline Capture)

**Tasks**: 2 | **Parallel**: Yes | **Est. Duration**: 10 min

| Task | Agent | Parallel |
|------|-------|----------|
| T001 | senior-backend-engineer | Yes |
| T002 | tester | Yes |

**Quality Gate**: Baseline line counts recorded. Pipeline output checksums saved to `specs/075-tachi-agent-best/baseline-output/`. All subsequent changes are regression-testable.

---

### Wave 2: Skill Extraction + Leaf/Report Tone Audit

**Tasks**: 15 | **Parallel**: Yes (all 15) | **Est. Duration**: 30 min

| Task | Agent | Track | Parallel |
|------|-------|-------|----------|
| T003 | senior-backend-engineer | A: Orchestrator | Yes |
| T004 | senior-backend-engineer | A: Orchestrator | Yes |
| T005 | senior-backend-engineer | A: Orchestrator | Yes |
| T006 | senior-backend-engineer | A: Orchestrator | Yes |
| T008 | senior-backend-engineer | B: Risk-Scorer | Yes |
| T009 | senior-backend-engineer | B: Risk-Scorer | Yes |
| T010 | senior-backend-engineer | B: Risk-Scorer | Yes |
| T011 | senior-backend-engineer | B: Risk-Scorer | Yes |
| T013 | senior-backend-engineer | C: Control-Analyzer | Yes |
| T014 | senior-backend-engineer | C: Control-Analyzer | Yes |
| T015 | senior-backend-engineer | C: Control-Analyzer | Yes |
| T016 | senior-backend-engineer | C: Control-Analyzer | Yes |
| T019 | senior-backend-engineer | Tone: STRIDE Leaf | Yes |
| T020 | senior-backend-engineer | Tone: AI Leaf | Yes |
| T021 | senior-backend-engineer | Tone: Report | Yes |

**Quality Gate**: All 12 reference files created with correct frontmatter. All 3 SKILL.md files created. Leaf and report agent tone audits complete. No content duplication between source agents and extracted files.

---

### Wave 3: Agent Refactoring + Threat-Report Trim

**Tasks**: 4 | **Parallel**: Yes | **Est. Duration**: 20 min

| Task | Agent | Dependency | Parallel |
|------|-------|------------|----------|
| T007 | senior-backend-engineer | T003-T006 (Track A done) | Yes |
| T012 | senior-backend-engineer | T008-T011 (Track B done) | Yes |
| T017 | senior-backend-engineer | T013-T016 (Track C done) | Yes |
| T024 | senior-backend-engineer | None | Yes |

**Quality Gate**: Orchestrator, risk-scorer, and control-analyzer refactored with Skill References sections and Read-tool loading instructions. Threat-report.md trimmed. Extracted content removed from source agents.

---

### Wave 4: Post-Extraction Verification + Methodology Tone Audit

**Tasks**: 4 | **Parallel**: Yes | **Est. Duration**: 15 min

| Task | Agent | Dependency | Parallel |
|------|-------|------------|----------|
| T018 | tester | T007, T012, T017 | Yes |
| T022 | senior-backend-engineer | T007, T012, T017 | Yes |
| T023 | senior-backend-engineer | None (threat-report) | Yes |
| T025 | tester | T024 | Yes |

**Quality Gate**: All 3 methodology agents verified at <=1,000 lines. No content duplication detected. Methodology and threat-report agents tone-audited. Threat-report.md verified at <=800 lines.

---

### Wave 5: Validation + Compliance

**Tasks**: 4 | **Parallel**: Partial | **Est. Duration**: 20 min

| Task | Agent | Dependency | Parallel |
|------|-------|------------|----------|
| T026 | tester | Waves 2-4 complete | Yes |
| T027 | tester | Waves 2-4 complete | Yes |
| T028 | code-reviewer | Waves 2-4 complete | Yes |
| T029 | senior-backend-engineer | T027, T028 (needs verified counts) | After T027 |

**Quality Gate**: Pipeline output equivalent to baseline. All 18 agents within tier caps. All 18 agents pass 8-criterion quality checklist. Compliance table in `_TACHI_AGENT_BEST_PRACTICES.md` updated with accurate post-refactor data.

---

## Execution Summary

| Wave | Tasks | Max Parallel | Est. Duration | Cumulative |
|------|-------|-------------|---------------|------------|
| 1 | 2 | 2 | 10 min | 10 min |
| 2 | 15 | 15 | 30 min | 40 min |
| 3 | 4 | 4 | 20 min | 60 min |
| 4 | 4 | 4 | 15 min | 75 min |
| 5 | 4 | 3+1 | 20 min | 95 min |
| **Total** | **29** | -- | **~95 min** | -- |

---

## Critical Path

```
T001/T002 (baseline)
    |
    v
T003-T016 + T019-T021 (extraction + leaf/report tone) [Wave 2]
    |
    v
T007, T012, T017, T024 (refactor + trim) [Wave 3]
    |
    v
T018, T022, T023, T025 (verify + methodology tone) [Wave 4]
    |
    v
T026-T029 (validation + compliance) [Wave 5]
```

**Longest path**: T001 -> T003 -> T007 -> T018 -> T026 -> T029 (6 sequential dependencies across 5 waves)

---

**End of Agent Assignments**
