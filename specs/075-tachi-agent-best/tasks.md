---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-31
    status: APPROVED
    notes: "All 4 user stories, 14 FRs, and 9 success criteria have complete task coverage with no scope creep. MVP independently deliverable."
  architect_signoff:
    agent: architect
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correct, 3 extraction tracks truly independent, ADR-002 loading mechanism reflected. 2 non-blocking concerns: consider explicit extraction boundary markers in agent content, and note that T022 methodology tone audit should verify data-top ordering was maintained during extraction."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-31
    status: APPROVED
    notes: "29 tasks across 5 waves realistic for single-session docs-only delivery. Parallelization maximized at 15 concurrent tasks in Wave 2. Critical path correctly identified."
---

# Tasks: Tachi Agent Best Practices

**Input**: Design documents from `specs/075-tachi-agent-best/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All deliverables are markdown/YAML files — zero application code.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Baseline Capture)

**Purpose**: Establish regression baseline before any changes

- [X] T001 Record baseline line counts for all 18 tachi agents in .claude/agents/tachi/ (wc -l *.md)
- [X] T002 Capture pre-extraction pipeline output by running /threat-model, /risk-score, and /compensating-controls on examples/architecture-*.md — save output checksums to specs/075-tachi-agent-best/baseline-output/

**Checkpoint**: Baseline captured. All subsequent changes can be regression-tested against this.

---

## Phase 2: User Story 1 — Skill Extraction for Methodology Agents (Priority: P1) MVP

**Goal**: Extract domain knowledge from orchestrator, risk-scorer, and control-analyzer into on-demand skills, bringing all three agents to <=1,000 lines.

**Independent Test**: Run /threat-model + /risk-score + /compensating-controls on example architecture; compare output against Phase 1 baseline for equivalence.

### Track A: Orchestrator Extraction

- [X] T003 [P] [US1] Create tachi-orchestration skill — directory .claude/skills/tachi-orchestration/ and SKILL.md with frontmatter (name, description), domain overview, and loading table mapping references to workflow phases
- [X] T004 [P] [US1] Extract SARIF 2.1.0 generation specification (~490 lines) from .claude/agents/tachi/orchestrator.md to .claude/skills/tachi-orchestration/references/sarif-specification.md with source_agent/extracted_from/version frontmatter
- [X] T005 [P] [US1] Extract STRIDE + AI dispatch rules and correlation matrices from .claude/agents/tachi/orchestrator.md to .claude/skills/tachi-orchestration/references/dispatch-rules.md
- [X] T006 [P] [US1] Extract output schema tables, validation checklist, and error templates from .claude/agents/tachi/orchestrator.md to .claude/skills/tachi-orchestration/references/output-schemas.md
- [X] T007 [US1] Refactor .claude/agents/tachi/orchestrator.md — remove extracted content, add Skill References section with Read-tool loading instructions per ADR-002, add tool restrictions to frontmatter, verify <=1,000 lines

### Track B: Risk-Scorer Extraction

- [X] T008 [P] [US1] Create tachi-risk-scoring skill — directory .claude/skills/tachi-risk-scoring/ and SKILL.md with frontmatter, domain overview, and loading table
- [X] T009 [P] [US1] Extract four-dimensional scoring model definitions from .claude/agents/tachi/risk-scorer.md to .claude/skills/tachi-risk-scoring/references/scoring-dimensions.md
- [X] T010 [P] [US1] Extract CVSS base vector mappings and weight tables from .claude/agents/tachi/risk-scorer.md to .claude/skills/tachi-risk-scoring/references/cvss-vectors.md
- [X] T011 [P] [US1] Extract severity band definitions and composite formulas from .claude/agents/tachi/risk-scorer.md to .claude/skills/tachi-risk-scoring/references/severity-bands.md
- [X] T012 [US1] Refactor .claude/agents/tachi/risk-scorer.md — remove extracted content, add Skill References section with Read-tool loading instructions, add tool restrictions to frontmatter, verify <=1,000 lines

### Track C: Control-Analyzer Extraction

- [X] T013 [P] [US1] Create tachi-control-analysis skill — directory .claude/skills/tachi-control-analysis/ and SKILL.md with frontmatter, domain overview, and loading table
- [X] T014 [P] [US1] Extract 8 control category definitions and detection patterns from .claude/agents/tachi/control-analyzer.md to .claude/skills/tachi-control-analysis/references/control-categories.md
- [X] T015 [P] [US1] Extract evidence criteria and effectiveness classification rules from .claude/agents/tachi/control-analyzer.md to .claude/skills/tachi-control-analysis/references/evidence-criteria.md
- [X] T016 [P] [US1] Extract residual risk calculation formulas and recommendations from .claude/agents/tachi/control-analyzer.md to .claude/skills/tachi-control-analysis/references/residual-risk.md
- [X] T017 [US1] Refactor .claude/agents/tachi/control-analyzer.md — remove extracted content, add Skill References section with Read-tool loading instructions, add tool restrictions to frontmatter, verify <=1,000 lines

### Extraction Verification

- [X] T018 [US1] Verify all three methodology agents <=1,000 lines (wc -l) and no content duplication between agents and their skill reference files

**Checkpoint**: All methodology agents at or below 1,000-line cap. Skills created with on-demand reference files. Pipeline quality not yet validated (Wave 4).

---

## Phase 3: User Story 2 — Claude 4.6 Tone Audit (Priority: P2)

**Goal**: Audit all 18 tachi agents for aggressive emphasis patterns, tool restrictions, description field quality, and data-top ordering.

**Independent Test**: Scan all agent files for CRITICAL/MUST/ALWAYS/NEVER counts before and after. Verify remaining instances are genuinely critical. Check frontmatter for tool restrictions and description fields.

- [X] T019 [P] [US2] Tone audit 6 STRIDE leaf agents — soften non-critical emphasis, add tool restrictions to frontmatter, review description fields for delegation routing in .claude/agents/tachi/spoofing.md, tampering.md, repudiation.md, info-disclosure.md, denial-of-service.md, privilege-escalation.md
- [X] T020 [P] [US2] Tone audit 5 AI threat leaf agents — soften non-critical emphasis, add tool restrictions to frontmatter, review description fields in .claude/agents/tachi/prompt-injection.md, data-poisoning.md, model-theft.md, agent-autonomy.md, tool-abuse.md
- [X] T021 [P] [US2] Tone audit 2 compliant report agents — soften non-critical emphasis, add tool restrictions, review description fields in .claude/agents/tachi/report-assembler.md, threat-infographic.md
- [X] T022 [US2] Tone audit 3 methodology agents (post-extraction) — review emphasis patterns in .claude/agents/tachi/orchestrator.md, risk-scorer.md, control-analyzer.md; verify data-top ordering (schemas before workflow steps)
- [X] T023 [US2] Tone audit threat-report agent — soften non-critical emphasis, add tool restrictions, review description field, verify data-top ordering in .claude/agents/tachi/threat-report.md

**Checkpoint**: All 18 agents audited for Claude 4.6 alignment. Tool restrictions and description fields verified.

---

## Phase 4: User Story 3 — Threat-Report Trim (Priority: P2)

**Goal**: Trim threat-report.md from 801 to <=800 lines without removing functional content.

**Independent Test**: Count lines in threat-report.md. Verify <=800 and no functional content removed.

- [X] T024 [US3] Trim .claude/agents/tachi/threat-report.md to <=800 lines — remove whitespace, consolidate comments, or shorten non-functional content (1 line reduction needed)
- [X] T025 [US3] Verify .claude/agents/tachi/threat-report.md <=800 lines (wc -l)

**Checkpoint**: Threat-report compliant with 800-line Report tier cap.

---

## Phase 5: User Story 4 — Validation and Compliance Table (Priority: P3)

**Goal**: Validate pipeline output equivalence, verify all agents pass quality checklist, and update compliance table.

**Independent Test**: Compare post-extraction pipeline output with Phase 1 baseline. Verify compliance table accuracy against actual file line counts.

- [X] T026 [US4] Run full pipeline on example architecture post-extraction (/threat-model + /risk-score + /compensating-controls) — compare output against specs/075-tachi-agent-best/baseline-output/ checksums for equivalence
- [X] T027 [US4] Verify all 18 tachi agent line counts within tier caps (Leaf <=300, Report <=800, Methodology <=1,000) using batch wc -l
- [X] T028 [US4] Verify all 18 tachi agents pass 8-criterion quality checklist from .claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md Section 6
- [X] T029 [US4] Update compliance table in .claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md Section 5 with accurate post-refactor line counts, status, and extraction notes for methodology agents

**Checkpoint**: Pipeline output equivalent. All agents compliant. Compliance table accurate.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (US-1 Skill Extraction)**: Depends on Phase 1 baseline capture
- **Phase 3 (US-2 Tone Audit)**: T019-T021 (leaf/report agents) can run in parallel with Phase 2; T022-T023 (methodology + threat-report agents) depend on Phase 2 completion
- **Phase 4 (US-3 Threat-Report Trim)**: Can run in parallel with Phase 2 or Phase 3
- **Phase 5 (US-4 Validation)**: Depends on Phases 2, 3, and 4 all complete

### Within Phase 2 (Skill Extraction)

Three tracks (A, B, C) are fully independent — orchestrator, risk-scorer, and control-analyzer have no cross-dependencies:
- Track A: T003-T006 parallel → T007 sequential
- Track B: T008-T011 parallel → T012 sequential
- Track C: T013-T016 parallel → T017 sequential
- T018 depends on T007, T012, T017 all complete

### Parallel Opportunities

- **Wave 1**: T001, T002 (baseline)
- **Wave 2**: T003-T006 + T008-T011 + T013-T016 (all [P] extraction tasks) + T019-T021 (leaf/report tone audit, independent of extraction)
- **Wave 3**: T007, T012, T017 (agent refactoring, after extraction) + T024 (threat-report trim)
- **Wave 4**: T018, T022, T023, T025 (post-extraction verification + methodology tone audit)
- **Wave 5**: T026-T029 (validation + compliance table)

---

## Parallel Example: Phase 2 Extraction

```
# Wave 2 — Launch all extraction tasks and leaf/report tone audits together:
T003: Create tachi-orchestration SKILL.md
T004: Extract sarif-specification.md
T005: Extract dispatch-rules.md
T006: Extract output-schemas.md
T008: Create tachi-risk-scoring SKILL.md
T009: Extract scoring-dimensions.md
T010: Extract cvss-vectors.md
T011: Extract severity-bands.md
T013: Create tachi-control-analysis SKILL.md
T014: Extract control-categories.md
T015: Extract evidence-criteria.md
T016: Extract residual-risk.md
T019: Tone audit STRIDE leaf agents (6 files)
T020: Tone audit AI threat leaf agents (5 files)
T021: Tone audit report agents (2 files)
# 15 parallel tasks across 6 agents
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Baseline capture
2. Complete Phase 2: Skill extraction (3 parallel tracks)
3. **STOP and VALIDATE**: Run pipeline comparison to confirm output equivalence
4. This alone delivers SC-001 through SC-006 and SC-009

### Incremental Delivery

1. Phase 1 → Baseline captured
2. Phase 2 → Skill extraction complete → Pipeline still functional (MVP)
3. Phase 3 → Tone audit complete → All agents Claude 4.6 aligned
4. Phase 4 → Threat-report trimmed → All agents within tier caps
5. Phase 5 → Validation passed → Compliance table updated → Feature complete

### Summary

| Metric | Value |
|--------|-------|
| Total tasks | 29 |
| US-1 tasks | 16 (T003-T018) |
| US-2 tasks | 5 (T019-T023) |
| US-3 tasks | 2 (T024-T025) |
| US-4 tasks | 4 (T026-T029) |
| Setup tasks | 2 (T001-T002) |
| Max parallel tasks in one wave | 15 (Wave 2) |
| Execution waves | 5 |
| Estimated duration | Single session (docs-only per PAT-012) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All deliverables are markdown/YAML — no compilation, no tests, no deployment
- Content extraction is verbatim relocation — no rewording or summarization
- Reference files include source_agent/extracted_from/version frontmatter per Feature 029 precedent
- Loading mechanism is Read tool per ADR-002 — not frontmatter skills: declarations
