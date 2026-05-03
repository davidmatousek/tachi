# Agent Assignments: Feature 007 — AI Threat Agents

**Created**: 2026-03-22
**Author**: team-lead
**Feasibility**: APPROVED (90% confidence, 1 sprint)
**Source**: `specs/007-ai-threat-agents/tasks.md` (48 tasks, 8 phases)

---

## Wave Strategy

```
Wave 1: Setup + Structural Audit (T001-T010)
    |
Wave 2: Agent Validation + Dispatch Validation (T011-T038) -- PARALLEL
    |    Track A: Agentic Agents (T011-T018)
    |    Track B: LLM Agents (T019-T028)
    |    Track C: Dispatch Validation (T035-T038)
    |
Wave 3: Cross-Agent Consistency (T029-T034)
    |
Wave 4: E2E Integration (T039-T045)
    |
Wave 5: Polish (T046-T048)
```

---

## Wave 1: Setup + Structural Audit

**Phases**: Phase 1 (Setup) + Phase 2 (Foundational)
**Tasks**: T001-T010 (10 tasks)
**Estimated Duration**: 45 minutes wall-clock

### Agent Assignment

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Verify schemas/finding.yaml supports AI categories | security-analyst | Schema validation requires understanding of AI threat taxonomy |
| T002 [P] | Verify INTERFACE-CONTRACT.md Section 3 dispatch keywords | security-analyst | Interface contract verification, security domain knowledge |
| T003 [P] | Verify example input contains AI/LLM/agentic components | security-analyst | Content verification against validation requirements |
| T004 [P] | Verify all 5 AI agent files exist | security-analyst | File inventory check |
| T005 [P] | Audit frontmatter: agent-autonomy.md | senior-backend-engineer | Structured YAML frontmatter validation |
| T006 [P] | Audit frontmatter: tool-abuse.md | senior-backend-engineer | Structured YAML frontmatter validation |
| T007 [P] | Audit frontmatter: prompt-injection.md | senior-backend-engineer | Structured YAML frontmatter validation |
| T008 [P] | Audit frontmatter: data-poisoning.md | senior-backend-engineer | Structured YAML frontmatter validation |
| T009 [P] | Audit frontmatter: model-theft.md | senior-backend-engineer | Structured YAML frontmatter validation |
| T010 [P] | Audit section structure: all 5 agents | senior-backend-engineer | Canonical section order verification |

### Execution Notes

- T001-T004 can run in parallel (different files, read-only verification)
- T005-T010 can all run in parallel (different agent files, no cross-dependencies)
- T001-T004 and T005-T010 are sequential: Setup must complete before Structural Audit

### Quality Gate

**Checkpoint**: All 5 agents pass structural audit -- frontmatter correct, sections in order.
**Gate Owner**: team-lead
**Criteria**: Zero structural defects remaining. Content validation may begin.

---

## Wave 2: Agent Validation + Dispatch Validation (PARALLEL)

**Phases**: Phase 3 (US1) + Phase 4 (US2) + Phase 6 (US4)
**Tasks**: T011-T028 (18 tasks) + T035-T038 (4 tasks) = 22 tasks
**Estimated Duration**: 75 minutes wall-clock (tracks run in parallel)

### Track A: Agentic Agent Validation (US1)

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T011 [P] | Validate detection patterns: agent-autonomy.md | security-analyst | AI threat pattern expertise, OWASP Agentic knowledge |
| T012 [P] | Validate detection patterns: tool-abuse.md | security-analyst | MCP/tool threat pattern expertise |
| T013 | Verify finding template: agent-autonomy.md | security-analyst | Component-specificity and trust assumption review |
| T014 | Verify finding template: tool-abuse.md | security-analyst | Component-specificity and trust assumption review |
| T015 | Verify OWASP references: agent-autonomy.md | security-analyst | ASI reference verification |
| T016 | Verify OWASP references: tool-abuse.md | security-analyst | ASI/MCP reference verification |
| T017 | Verify empty results guidance: agent-autonomy.md | security-analyst | False positive prevention |
| T018 | Verify empty results guidance: tool-abuse.md | security-analyst | False positive prevention |

### Track B: LLM Agent Validation (US2)

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T019 [P] | Validate detection patterns: prompt-injection.md | security-analyst | LLM threat pattern expertise |
| T020 [P] | Validate detection patterns: data-poisoning.md | security-analyst | Data/model poisoning expertise |
| T021 [P] | Validate detection patterns: model-theft.md | security-analyst | Model extraction expertise |
| T022 | Verify finding template: prompt-injection.md | security-analyst | Component-specificity review |
| T023 | Verify finding template: data-poisoning.md | security-analyst | Component-specificity review |
| T024 | Verify finding template: model-theft.md | security-analyst | Component-specificity review |
| T025 [P] | Verify OWASP references: prompt-injection.md | security-analyst | LLM0x reference verification |
| T026 [P] | Verify OWASP references: data-poisoning.md | security-analyst | LLM0x reference verification |
| T027 [P] | Verify OWASP references: model-theft.md | security-analyst | LLM0x reference verification |
| T028 | Verify empty results guidance: all 3 LLM agents | security-analyst | False positive prevention |

### Track C: Dispatch Validation (US4)

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T035 | Verify Layer 1 dispatch keywords match orchestrator | senior-backend-engineer | Interface contract cross-reference |
| T036 | Verify Layer 2 keywords extend (not conflict) Layer 1 | senior-backend-engineer | Keyword conflict detection |
| T037 | Verify dual-dispatch behavior | senior-backend-engineer | Orchestrator logic verification |
| T038 | Verify dispatch matrix against example input | senior-backend-engineer | End-to-end keyword trace |

### Execution Notes

- Track A and Track B run simultaneously (different agent files, zero overlap)
- Track C runs simultaneously with A+B (reads orchestrator.md and INTERFACE-CONTRACT.md, not agents/ai/*)
- Within Track A: T011, T012 can run in parallel; T013-T018 are sequential per-agent
- Within Track B: T019-T021 can run in parallel; T025-T027 can run in parallel
- Track C is sequential (each task builds on prior understanding)

### Quality Gate

**Checkpoint**: Both agentic agents validated (US1), all 3 LLM agents validated (US2), dispatch verified (US4).
**Gate Owner**: team-lead
**Criteria**: AG-prefixed findings are component-specific, schema-compliant, OWASP-grounded. LLM-prefixed findings same. Dispatch matrix matches expected behavior.

---

## Wave 3: Cross-Agent Consistency

**Phase**: Phase 5 (US3)
**Tasks**: T029-T034 (6 tasks)
**Estimated Duration**: 25 minutes wall-clock

### Agent Assignment

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T029 | Cross-check section organization: all 5 agents | code-reviewer | Cross-file structural consistency |
| T030 | Cross-check finding templates: all 5 agents | code-reviewer | Field name/count consistency |
| T031 | Verify ID prefix conventions | code-reviewer | AG-N vs LLM-N convention check |
| T032 | Verify category field values | code-reviewer | Enum value consistency |
| T033 | Verify risk computation sections | code-reviewer | OWASP 3x3 matrix consistency |
| T034 | Verify output_schema references | code-reviewer | Frontmatter cross-reference |

### Execution Notes

- All tasks are sequential (each is a cross-agent comparison operation)
- Single agent handles all consistency checks for uniform evaluation criteria

### Quality Gate

**Checkpoint**: All 5 agents produce format-consistent findings.
**Gate Owner**: team-lead
**Criteria**: Identical section organization, identical field names, correct ID prefixes, correct category values, identical risk matrix, consistent schema references.

---

## Wave 4: End-to-End Integration

**Phase**: Phase 7 (US5)
**Tasks**: T039-T045 (7 tasks)
**Estimated Duration**: 40 minutes wall-clock

### Agent Assignment

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T039 | Run orchestrator, verify AG threat table | orchestrator | Executes the dispatch protocol being validated |
| T040 | Verify LLM threat table in output | orchestrator | Validates LLM agent assembly |
| T041 | Verify 100% component specificity | orchestrator | Quality guardrail validation |
| T042 | Verify risk_level matches 3x3 matrix | orchestrator | Computation correctness |
| T043 | Verify coverage matrix (dual-dispatch, agentic-only) | orchestrator | Dispatch accuracy validation |
| T044 | Verify finding ID namespace separation | orchestrator | AG/LLM vs S/T/R/I/D/E conflict check |
| T045 | Verify empty results for non-AI components | orchestrator | False positive prevention |

### Execution Notes

- T039 must run first (produces the output file all other tasks validate)
- T040-T045 could theoretically run in parallel once T039 completes, but sequential is acceptable given the same output file
- This wave requires the orchestrator agent because it must execute the actual dispatch protocol

### Quality Gate

**Checkpoint**: End-to-end integration validated -- complete threat model with 8 tables (6 STRIDE + 2 AI).
**Gate Owner**: team-lead
**Criteria**: AG and LLM tables present with findings, 100% component specificity, correct risk levels, no namespace conflicts, empty results for non-AI components.

---

## Wave 5: Polish

**Phase**: Phase 8
**Tasks**: T046-T048 (3 tasks)
**Estimated Duration**: 15 minutes wall-clock

### Agent Assignment

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T046 [P] | Add MITRE ATLAS cross-references | senior-backend-engineer | Reference addition, P1 |
| T047 [P] | Add CWE identifiers | senior-backend-engineer | Reference addition, P1 |
| T048 | Verify agents/ai/README.md accuracy | code-reviewer | Documentation consistency check |

### Execution Notes

- T046 and T047 can run in parallel (different reference types, same files but different sections)
- T048 is sequential (depends on all prior waves completing)

### Quality Gate

**Checkpoint**: Feature complete.
**Gate Owner**: team-lead
**Criteria**: P1 cross-references added where applicable, README documentation accurate.

---

## Summary: Agent Workload Distribution

| Agent | Waves | Task Count | Load % | Role |
|-------|-------|------------|--------|------|
| security-analyst | 1, 2 | 22 | 46% | Setup verification, all agent content validation (Tracks A+B) |
| senior-backend-engineer | 1, 2, 5 | 12 | 25% | Frontmatter audit, dispatch validation, P1 references |
| code-reviewer | 3, 5 | 7 | 15% | Cross-agent consistency, documentation verification |
| orchestrator | 4 | 7 | 15% | E2E integration validation |
| **Total** | | **48** | **100%** | |

### Workload Balance Assessment

- **security-analyst at 46%**: This is the correct assignment. The core value of this feature is validating AI threat agent content quality (detection patterns, finding templates, OWASP references). The security-analyst has the domain expertise to evaluate whether OWASP AI framework references are correctly applied, detection patterns cover the right attack subcategories, and findings demonstrate proper threat + trust assumption formulation. No other agent in the registry has this expertise.
- **No agent exceeds 80% load**: Within target.
- **No agent is idle across waves**: Each agent is utilized in non-overlapping waves, preventing bottlenecks.
- **Sequential wave execution**: Agents are not double-booked. security-analyst finishes Waves 1-2 before code-reviewer starts Wave 3.

### Agent Selection Rationale

| Agent | Why Selected | Why Not Alternatives |
|-------|-------------|---------------------|
| security-analyst | Domain expertise in OWASP AI frameworks, threat patterns, and finding quality | No other agent understands AI threat taxonomy, OWASP ASI/LLM/MCP references, or component-specificity requirements for security findings |
| senior-backend-engineer | Structured content validation (YAML frontmatter, keyword matching, reference insertion) | Tasks are structural, not security-analytical; code-reviewer would over-focus on style |
| code-reviewer | Cross-file consistency checks requiring uniform evaluation criteria | Purpose-built for comparing structure across files and flagging inconsistencies |
| orchestrator | Executes the actual dispatch protocol being validated | No other agent can run the orchestrator against sample input; tester could verify outputs independently but cannot execute dispatch |

### Agents NOT Assigned (with justification)

| Agent | Why Not Used |
|-------|-------------|
| product-manager | No scope decisions needed; requirements already defined |
| architect | No technical design decisions; architecture already established |
| team-lead | Governance only; does not execute tasks |
| frontend-developer | No frontend work |
| ux-ui-designer | No UI/UX work |
| tester | Validation is inline (prompt files, not code); could supplement Wave 4 but orchestrator is primary |
| debugger | No bugs to investigate |
| devops | No deployment |
| web-researcher | No external research needed; OWASP references already documented in research.md |

---

## Timeline Summary

| Wave | Duration (Wall-Clock) | Cumulative | Blocking |
|------|----------------------|------------|----------|
| Wave 1: Setup + Structural | 45 min | 0:45 | Blocks Wave 2 |
| Wave 2: Validation (parallel) | 75 min | 2:00 | Blocks Wave 3 |
| Wave 3: Consistency | 25 min | 2:25 | Blocks Wave 4 |
| Wave 4: E2E Integration | 40 min | 3:05 | Blocks Wave 5 |
| Wave 5: Polish | 15 min | 3:20 | None |
| **Total** | **3 hours 20 min** | | |

**Sprint fit**: 3.3 hours wall-clock comfortably fits within 1 sprint. Even with the pessimistic multiplier (1.5x), the estimate is ~5 hours -- still within a single sprint.

---

**End of Agent Assignments**
