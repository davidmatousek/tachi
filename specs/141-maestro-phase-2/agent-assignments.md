# Agent Assignments: Feature 141 — MAESTRO Phase 2

**Date**: 2026-04-12
**Author**: team-lead
**Feasibility**: APPROVED_WITH_CONCERNS (3 LOW)
**Estimated Duration**: 10-12 days (realistic)

---

## Agent Assignment Matrix

| Task | Description | Agent (subagent_type) | Effort | Notes |
|------|-------------|----------------------|--------|-------|
| T001 | Create attack-chain.yaml schema | senior-backend-engineer | 0.5h | New file, follows finding.yaml pattern |
| T002 | Create correlation pattern lookup table | senior-backend-engineer | 2h | Core reference — CSA pattern research needed |
| T003 | Update output-schemas.md | senior-backend-engineer | 0.5h | Additive update |
| T004 | Update dispatch-rules.md | senior-backend-engineer | 0.5h | Phase 3.5 documentation |
| T005 | Add parse_attack_chains() to tachi_parsers.py | senior-backend-engineer | 2h | Follows existing parser pattern |
| T006 | Insert Phase 3.5 skeleton into orchestrator.md | senior-backend-engineer | 2h | Precise line-level insertion after Phase 3 |
| T007 | Implement cross-layer correlation logic | senior-backend-engineer | 4h | Core algorithm — highest complexity task |
| T008 | Implement chain assembly and ranking | senior-backend-engineer | 2h | Deterministic sorting + cap at 5 |
| T009 | Implement chain-breaking control heuristic | senior-backend-engineer | 2h | Betweenness centrality for 3+ links |
| T010 | Implement attack-chains.md artifact generation | senior-backend-engineer | 2h | YAML frontmatter + sections |
| T011 | Write unit tests for correlation engine | tester | 4h | 8+ test cases per task description |
| T012 | Validate against examples/agentic-app/ | tester | 2h | Live pipeline validation |
| T013 | Add Section 6 to threat-report.md | senior-backend-engineer | 3h | Narrative generation with causal vocabulary |
| T014 | Update threat-report agent input contract | senior-backend-engineer | 0.5h | Frontmatter + skill references update |
| T015 | Validate narrative against agentic-app | tester | 1h | Word count + vocabulary check |
| T016 | Add chain extraction to extract-report-data.py | senior-backend-engineer | 3h | parse + Mermaid generation + Typst data |
| T017 | Create attack-chain.typ Typst template | senior-backend-engineer | 2h | ~100 lines, follows attack-path.typ pattern |
| T018 | Update main.typ (import + conditional gate) | senior-backend-engineer | 1h | Follows has-attack-trees pattern exactly |
| T019 | Extend mmdc preflight gate in security-report command | senior-backend-engineer | 1h | Additive artifact detection |
| T020 | Write integration tests for chain extraction | tester | 3h | Fixture + Mermaid syntax + Typst structure |
| T021 | Validate PDF rendering against agentic-app | tester | 2h | Visual verification of rendered pages |
| T022 | Extend agentic-app architecture (if needed) | senior-backend-engineer | 1h | Optional component additions |
| T023 | Regenerate agentic-app full pipeline output | senior-backend-engineer | 1h | Chain demonstration example |
| T024 | Regenerate web-app pipeline output | devops | 0.5h | No chains expected |
| T025 | Regenerate microservices pipeline output | devops | 0.5h | No chains expected |
| T026 | Regenerate ascii-web-api pipeline output | devops | 0.5h | No chains expected |
| T027 | Regenerate free-text-microservice pipeline output | devops | 0.5h | No chains expected |
| T028 | Regenerate mermaid-agentic-app pipeline output | devops | 0.5h | May have chains (L1/L2/L3/L7) |
| T029 | Update ADR-020 | architect | 2h | Phase 2 cross-layer correlation section |
| T030 | Regenerate backward-compatibility PDF baselines | devops | 1h | 5 examples under SOURCE_DATE_EPOCH |
| T031 | Run full pytest suite | tester | 1h | All tests including new test files |
| T032 | Update README.md prerequisites | senior-backend-engineer | 0.5h | Pipeline output list update |
| T033 | Final validation (SC-001 through SC-007) | tester | 2h | Full success criteria verification |

---

## Parallel Execution Waves

### Wave 1: Foundation Setup (0.5 day)

**Quality Gate**: All schema and reference files exist and are syntactically valid.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Schema | T001 | senior-backend-engineer | Sequential (must be first — schema defines the contract) |
| Correlation Patterns | T002 | senior-backend-engineer | Parallel with T003, T004 |
| Output Schemas | T003 | senior-backend-engineer | Parallel with T002, T004 |
| Dispatch Rules | T004 | senior-backend-engineer | Parallel with T002, T003 |

**Time**: ~0.5 day
**Gate Review**: code-reviewer spot-checks schema + pattern table completeness

---

### Wave 2: Parser & Skeleton (1 day)

**Quality Gate**: parse_attack_chains() passes smoke test; orchestrator Phase 3.5 skeleton is syntactically correct and placed after Phase 3 / before Phase 4.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Parser | T005 | senior-backend-engineer | Sequential (must precede skeleton) |
| Orchestrator Skeleton | T006 | senior-backend-engineer | Sequential (depends on schema from Wave 1) |

**Time**: ~1 day
**Gate Review**: code-reviewer validates parser function signature + orchestrator insertion point
**CRITICAL CHECKPOINT**: No user story work begins until this wave completes.

---

### Wave 3: Correlation Engine (3-4 days)

**Quality Gate**: Correlation engine produces attack-chains.md on agentic-app with genuine causal chains. Deterministic output. No false chains on other examples.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Correlation Logic | T007 | senior-backend-engineer | Sequential |
| Chain Assembly | T008 | senior-backend-engineer | Sequential (depends on T007) |
| Chain-Breaking Heuristic | T009 | senior-backend-engineer | Sequential (depends on T008) |
| Artifact Generation | T010 | senior-backend-engineer | Sequential (depends on T009) |
| Unit Tests | T011 | tester | Parallel (independent test file) |
| Example Validation | T012 | tester | Sequential after T010 (needs engine output) |

**Time**: 3-4 days
**Gate Review**: architect validates correlation algorithm design against spec FR-001 through FR-007; code-reviewer reviews Python + orchestrator changes
**MVP CHECKPOINT**: Stop and validate. If engine quality is insufficient, iterate before proceeding.

---

### Wave 4: Threat Report Narrative (1-1.5 days)

**Quality Gate**: Threat report Section 6 generates conditional narratives for Critical/High chains. 150-300 word narratives with causal vocabulary.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Section 6 Implementation | T013 | senior-backend-engineer | Sequential |
| Input Contract Update | T014 | senior-backend-engineer | Sequential (depends on T013) |
| Narrative Validation | T015 | tester | Sequential (depends on T014) |

**Time**: 1-1.5 days
**Gate Review**: code-reviewer validates narrative generation pattern matches existing Section 5

---

### Wave 5: PDF Chain Diagrams (2-2.5 days)

**Quality Gate**: PDF chain diagram pages render with vertical MAESTRO layer stack, correct colors, and finding references. Conditional gate works.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Python Extraction | T016 | senior-backend-engineer | Sequential |
| Typst Template | T017 | senior-backend-engineer | Parallel with T016 (independent file) |
| main.typ Integration | T018 | senior-backend-engineer | Sequential (depends on T017) |
| Command Preflight Gate | T019 | senior-backend-engineer | Sequential (depends on T018) |
| Integration Tests | T020 | tester | Parallel with T017 (independent file) |
| PDF Validation | T021 | tester | Sequential after T019 (needs full pipeline) |

**Time**: 2-2.5 days
**Gate Review**: architect validates page placement in main.typ; code-reviewer reviews Typst template

---

### Wave 6: Example Regeneration (1-1.5 days)

**Quality Gate**: agentic-app demonstrates end-to-end chain. 5 non-chain examples produce expected output (no unexpected chains).

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| agentic-app Architecture | T022 | senior-backend-engineer | Sequential (must precede regeneration) |
| agentic-app Full Pipeline | T023 | senior-backend-engineer | Sequential (depends on T022) |
| web-app Regeneration | T024 | devops | Parallel (independent) |
| microservices Regeneration | T025 | devops | Parallel (independent) |
| ascii-web-api Regeneration | T026 | devops | Parallel (independent) |
| free-text-microservice Regeneration | T027 | devops | Parallel (independent) |
| mermaid-agentic-app Regeneration | T028 | devops | Parallel (independent) |

**Time**: 1-1.5 days
**Gate Review**: code-reviewer verifies agentic-app chain output; tester spot-checks non-chain examples for unexpected artifacts

---

### Wave 7: Polish & Final Regression (1-1.5 days)

**Quality Gate**: All tests pass. ADR updated. Baselines byte-identical. All 7 success criteria verified.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| ADR-020 Update | T029 | architect | Parallel with T032 |
| Baseline Regeneration | T030 | devops | Sequential (depends on Wave 6) |
| Full Pytest Suite | T031 | tester | Sequential (depends on T030) |
| README Update | T032 | senior-backend-engineer | Parallel with T029 |
| Final Validation (SC-001-007) | T033 | tester | Sequential (depends on T031) |

**Time**: 1-1.5 days
**Gate Review**: architect final sign-off on ADR; security-analyst final check (no new secrets, subprocess safety); product-manager final SC verification

---

## Wave Summary

| Wave | Name | Tasks | Time | Parallelism | Gate |
|------|------|-------|------|-------------|------|
| 1 | Foundation Setup | T001-T004 | 0.5d | 3 of 4 parallel | Schema + pattern completeness |
| 2 | Parser & Skeleton | T005-T006 | 1d | Sequential | CRITICAL: blocks all user stories |
| 3 | Correlation Engine | T007-T012 | 3-4d | T011 parallel | MVP: chain detection validated |
| 4 | Threat Report Narrative | T013-T015 | 1-1.5d | Sequential | Narrative quality validated |
| 5 | PDF Chain Diagrams | T016-T021 | 2-2.5d | T017, T020 parallel | PDF rendering validated |
| 6 | Example Regeneration | T022-T028 | 1-1.5d | T024-T028 parallel | End-to-end demonstration |
| 7 | Polish & Regression | T029-T033 | 1-1.5d | T029, T032 parallel | Full regression + sign-off |

**Total**: 10-12.5 days (realistic)
**Critical Path**: Waves 1-7 are sequential at the wave level
**MVP Boundary**: End of Wave 3 (12 tasks, ~4.5-5.5 days)

---

## Agent Workload Summary

| Agent (subagent_type) | Waves Active | Total Tasks | Total Effort | Peak Load |
|-----------------------|-------------|-------------|-------------|-----------|
| senior-backend-engineer | 1-6 | 18 | ~30h | Wave 3 (6 tasks, 12h) |
| tester | 3-7 | 8 | ~15h | Wave 3 (2 tasks, 6h) |
| devops | 6-7 | 6 | ~3.5h | Wave 6 (5 tasks, 2.5h) |
| architect | 3, 5, 7 | 3 | ~4h | Wave 7 (1 task, 2h) |
| code-reviewer | 1-6 (gates) | 5 reviews | ~3h | Distributed |
| security-analyst | 7 | 1 review | ~1h | Wave 7 only |
| product-manager | 7 | 1 review | ~1h | Wave 7 only |

No agent exceeds 80% load in any wave. senior-backend-engineer is the primary implementer across Waves 1-6, which is appropriate for a feature that is predominantly agent file authoring + Python script development.

---

## Handoff to Orchestrator

**Feasibility**: APPROVED_WITH_CONCERNS (3 LOW — see team-lead.md)
**Tasks Location**: `specs/141-maestro-phase-2/tasks.md`
**Wave Strategy**: 7 sequential waves with intra-wave parallelism
**Agent Assignments**: Per matrix above — all agents are valid subagent_type names from `.claude/agents/_README.md`
**MVP Gate**: Wave 3 completion (correlation engine validated on agentic-app)
**Time Budget**: 10-12 days realistic
