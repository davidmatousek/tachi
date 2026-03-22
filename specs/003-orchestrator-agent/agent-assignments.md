# Agent Assignments: Feature 003 - Orchestrator Agent

**Feature**: 003-orchestrator-agent
**Date**: 2026-03-21
**Assigned by**: team-lead
**Execution model**: Sequential single-agent (all tasks target one file)

---

## Feasibility Status

| Dimension | Assessment |
|-----------|------------|
| Effort | 35 tasks, single markdown file deliverable, 4-6 hours realistic |
| Capacity | 1 primary agent + 2 review agents -- no overload risk |
| Timeline | Within 1 sprint (4-6 hours authoring + 1-2 hours review) |
| Dependencies | F-001 artifacts complete and verified on disk |
| **Verdict** | **FEASIBLE** |

---

## Agent Assignment Matrix

| Agent | Role | Tasks Assigned | Load |
|-------|------|----------------|------|
| senior-backend-engineer | Primary author | T001-T029 (29 tasks) | HIGH (primary) |
| code-reviewer | Compliance review | T033, T034, T035 | LOW (review phase only) |
| tester | Validation scenarios | T030, T031, T032 | LOW (validation phase only) |
| security-analyst | Input sanitization review | T003 review, T016 review | MINIMAL (spot check) |
| architect | Concern resolution | T014 advisory (context payload format) | MINIMAL (advisory) |

### Agent Selection Rationale

- **senior-backend-engineer**: Primary authoring agent. Handles all file creation/editing. Possesses the technical depth required for OWASP methodology, DFD classifications, dispatch logic, and schema-compliant output assembly. The "backend engineer" designation is apt because the orchestrator prompt encodes algorithmic logic (format detection heuristics, normalization tables, risk matrix computation) even though the deliverable is markdown.

- **tester**: Validates the authored prompt against the 3 example inputs. The tester reviews whether the prompt instructions would produce correct outputs for each example scenario. This is validation-by-review, not test execution.

- **code-reviewer**: Reviews the complete prompt for platform neutrality (SC-010), interface contract compliance (verbatim table matching), and overall prompt quality (readability, conciseness, logical flow).

- **security-analyst**: Spot-checks the input sanitization boundary (T003) and the dispatch protocol (T014) for prompt injection resistance. This is a focused review, not a full security audit.

- **architect**: Available for advisory consultation on the MEDIUM concern from plan.md review (agent context payload format). The architect does not execute tasks but may be consulted during T014 authoring.

---

## Execution Waves

### Wave 1: Setup and Foundation (T001-T004)
**Duration**: 40-60 minutes
**Agent**: senior-backend-engineer

| Task | Description | Dependencies |
|------|-------------|--------------|
| T001 | Read all F-001 reference artifacts | None |
| T002 | Author frontmatter and Role & Purpose section | T001 |
| T003 | Author Input Sanitization Boundary section | T002 |
| T004 | Author Output Format Specification subsection | T002 |

**Note**: T003 and T004 are logically parallel but executed sequentially (single file). Order: T003 then T004 (boundary before format spec, matching prompt flow).

**Quality Gate W1**: Prompt skeleton review
- Verify frontmatter fields present (agent_name, category, status, version, references)
- Verify Role & Purpose section establishes orchestrator identity
- Verify input sanitization boundary uses XML-style markers
- Verify output format spec references templates/threats.md structure
- **Security spot-check**: security-analyst reviews T003 output for boundary robustness

---

### Wave 2: MVP -- Parse Architecture (T005-T010)
**Duration**: 60-90 minutes
**Agent**: senior-backend-engineer

| Task | Description | Dependencies |
|------|-------------|--------------|
| T005 | Author Phase 1 Scope preamble | T003, T004 |
| T006 | Author format detection instructions | T005 |
| T007 | Author component extraction with DFD classification | T006 |
| T008 | Author trust boundary identification | T007 |
| T009 | Author System Overview assembly | T008 |
| T010 | Author intermediate output requirement | T009 |

**Quality Gate W2**: MVP validation (critical checkpoint)
- Verify format detection covers all 5 formats with correct heuristic priority
- Verify DFD classification heuristics include concrete examples
- Verify trust boundary notation covers all format-specific markers
- Verify System Overview assembly produces Components, Data Flows, and Technologies tables
- **Validation**: tester reviews T005-T010 output against mermaid-agentic-app example characteristics

---

### Wave 3: Dispatch Logic (T011-T016)
**Duration**: 45-60 minutes
**Agent**: senior-backend-engineer

| Task | Description | Dependencies |
|------|-------------|--------------|
| T011 | Author Phase 2 preamble | T010 |
| T012 | Embed STRIDE-per-Element normalization table | T011 |
| T013 | Author AI keyword dispatch rules | T012 |
| T014 | Author agent invocation protocol | T013 |
| T015 | Author dispatch protocol (parallel + sequential) | T014 |
| T016 | Author dispatch table intermediate output | T015 |

**Quality Gate W3**: Dispatch correctness
- Verify STRIDE-per-Element table matches docs/INTERFACE-CONTRACT.md Section 2 verbatim
- Verify AI keyword lists match docs/INTERFACE-CONTRACT.md Section 3
- Verify dual-dispatch logic handles components matching both LLM and AG keywords
- Verify agent invocation includes full architecture context
- **Architect advisory**: architect available for T014 if context payload format needs clarification

---

### Wave 4: Assembly and Output (T017-T024)
**Duration**: 60-90 minutes
**Agent**: senior-backend-engineer

| Task | Description | Dependencies |
|------|-------------|--------------|
| T017 | Author Phase 3 preamble and finding collection | T016 |
| T018 | Author risk_level validation (OWASP 3x3) | T017 |
| T019 | Author STRIDE table assembly (6 tables) | T018 |
| T020 | Author AI threat table assembly (2 tables) | T018 |
| T021 | Author Phase 4 preamble | T019, T020 |
| T022 | Author coverage matrix generation | T021 |
| T023 | Author risk summary and recommended actions | T022 |
| T024 | Author output structural validation checklist | T023 |

**Note**: T019 and T020 are logically parallel but executed sequentially. Order: T019 then T020 (STRIDE tables before AI tables, matching output template order).

**Quality Gate W4**: Output completeness
- Verify all 7 output sections are covered
- Verify OWASP 3x3 matrix is correctly embedded
- Verify 5-to-2 AI agent table mapping is correct
- Verify coverage matrix format matches templates/threats.md
- Verify finding ID pattern validation is specified

---

### Wave 5: Error Handling (T025-T029)
**Duration**: 30-45 minutes
**Agent**: senior-backend-engineer

| Task | Description | Dependencies |
|------|-------------|--------------|
| T025 | Author UNSUPPORTED_FORMAT error response | T010 (references parsing) |
| T026 | Author NO_COMPONENTS error response | T010 |
| T027 | Author INVALID_FORMAT_VALUE error response | T010 |
| T028 | Author ambiguous classification handling | T010 |
| T029 | Author non-conforming finding handling | T010 |

**Note**: T025-T027 are logically parallel but executed sequentially. T028-T029 have soft dependencies on US2/US3 concepts but do not require those sections to be complete (the agent has accumulated context from sequential execution).

**Quality Gate W5**: Error coverage
- Verify all 3 error codes from INTERFACE-CONTRACT.md Section 7 are handled
- Verify error responses include actionable guidance
- Verify ambiguous classification defaults to Process with human review flag
- Verify non-conforming findings are flagged, not dropped

---

### Wave 6: Polish and Validation (T030-T035)
**Duration**: 45-60 minutes
**Agents**: tester (T030-T032), code-reviewer (T033-T035)

| Task | Agent | Description | Dependencies |
|------|-------|-------------|--------------|
| T030 | tester | Validate against mermaid-agentic-app | T029 (all authoring complete) |
| T031 | tester | Validate against ascii-web-api | T029 |
| T032 | tester | Validate against free-text-microservice | T029 |
| T033 | code-reviewer | Review for platform-specific syntax | T029 |
| T034 | code-reviewer | Review for interface contract compliance | T029 |
| T035 | code-reviewer | Final review of prompt quality | T029 |

**Note**: This is the only wave where multiple agents can genuinely operate in parallel, since T030-T032 are read-only validation tasks and T033-T035 are read-only review tasks. The tester and code-reviewer can work simultaneously.

**Quality Gate W6**: Final sign-off
- All 3 example validations pass
- No platform-specific syntax found (SC-010)
- Interface contract compliance verified (verbatim tables, correct keywords, correct error codes)
- Prompt is readable, concise, and logically structured
- **Delivery gate**: Ready for PR creation and merge

---

## Timeline Summary

| Wave | Tasks | Agent(s) | Duration | Cumulative |
|------|-------|----------|----------|------------|
| W1: Setup + Foundation | T001-T004 | senior-backend-engineer | 40-60 min | 0:40-1:00 |
| W2: MVP Parse | T005-T010 | senior-backend-engineer | 60-90 min | 1:40-2:30 |
| W3: Dispatch | T011-T016 | senior-backend-engineer | 45-60 min | 2:25-3:30 |
| W4: Assembly | T017-T024 | senior-backend-engineer | 60-90 min | 3:25-5:00 |
| W5: Error Handling | T025-T029 | senior-backend-engineer | 30-45 min | 3:55-5:45 |
| W6: Polish | T030-T035 | tester, code-reviewer | 45-60 min | 4:40-6:45 |

**Optimistic total**: 4.5 hours
**Realistic total**: 5.5 hours
**Pessimistic total**: 7 hours (includes rework from architect concern resolution)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Architect MEDIUM concern (context payload format) delays T014 | LOW | MEDIUM | Architect available for advisory; proceed with documented protocol, refine if needed |
| Single-agent bottleneck extends timeline | LOW | LOW | Sequential execution is intentional; no mitigation needed |
| Prompt exceeds practical token length | LOW | MEDIUM | Monitor at W4 checkpoint; plan.md notes no token limit issues observed |
| Validation reveals structural issues requiring rework | MEDIUM | MEDIUM | MVP checkpoint at W2 enables early detection; incremental delivery reduces rework scope |

---

## Handoff to Orchestrator

**Feasibility**: APPROVED
**Tasks location**: `specs/003-orchestrator-agent/tasks.md`
**Wave strategy**: 6 waves, sequential primary authoring (W1-W5) + parallel review (W6)
**Primary agent**: senior-backend-engineer (T001-T029)
**Review agents**: tester (T030-T032), code-reviewer (T033-T035)
**Advisory agents**: security-analyst (T003 spot-check), architect (T014 advisory)
**Estimated duration**: 5-6 hours realistic

---

**End of Agent Assignments**
