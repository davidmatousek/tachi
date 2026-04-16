# Agent Assignments: Feature 142 — MAESTRO Phase 3 — Agentic Threat Pattern Expansion

**Date**: 2026-04-16
**Author**: team-lead
**Feasibility**: APPROVED_WITH_CONCERNS (4 LOW — see tasks.md tech-lead sign-off notes)
**Estimated Duration**: 6-8 days realistic (5d optimistic floor with full 4-track parallelism)

---

## Agent Assignment Matrix

| Task | Description | Agent (subagent_type) | Effort | Notes |
|------|-------------|----------------------|--------|-------|
| T001 | Author `maestro-agentic-patterns-shared.md` (definitions + coverage table + classification rules + multi-agent gate predicate) | senior-backend-engineer | 4-6h | Core shared reference; satisfies US4 coverage mapping |
| T002 | Bump `schemas/finding.yaml` 1.3 → 1.4 (agentic_pattern enum + AGP- id.pattern regex extension) | senior-backend-engineer | 1-2h | Per architect MED-3 resolution; additive minor bump per ADR-026 |
| T003 | Update `dispatch-rules.md` for Phase 3.6 placement | senior-backend-engineer | 0.5h | Cross-reference ADR-026 |
| T004 | Update `output-schemas.md` (agentic_pattern field + Section 4b + has-agentic-patterns boolean) | senior-backend-engineer | 0.5h | Additive update |
| T005 | Extend `tachi_parsers.py` (parse_finding_pattern + parse_threats_findings + detect_artifacts) | senior-backend-engineer | 2h | Default `none` for backward compat (FR-017) |
| T006 | Insert Phase 3.6 skeleton into `orchestrator.md` after Phase 3.5 | senior-backend-engineer | 2h | Input/output contracts + independence invariants |
| T007 | Implement multi-agent gate predicate in Phase 3.6 (conditions a/b/c) | senior-backend-engineer | 2h | Sequential — synthesis engine entry step |
| T008 | Implement classification rule table application in Phase 3.6 | senior-backend-engineer | 3h | Sequential after T007; rules R-01 through R-06 |
| T009 | Implement net-new finding generation step in Phase 3.6 (AGP-NN prefix) | senior-backend-engineer | 3h | Sequential after T008; suppression checks |
| T010 | Set has-agentic-patterns boolean in Phase 3.6 final step | senior-backend-engineer | 0.5h | Sequential after T009 |
| T011 | Write unit tests in `tests/scripts/test_pattern_synthesis.py` | tester | 4h | Includes synthetic single-agent fixture (LOW-5), idempotence (PM LOW-2), content-overlap (LOW-7) |
| T012 | Write rule table validation tests in `test_pattern_classification_rules.py` | tester | 2h | Total-ordered priority + token list verification |
| T013 | Validate synthesis engine against extended agentic-app | tester | 1h | Sequences with Phase 5 (depends on T020) |
| T014 | Update `templates/tachi/output-schemas/threats.md` (Pattern column + Section 4b) | senior-backend-engineer | 2h | Empty values display as `—` |
| T015 | Add Agentic Pattern Analysis section to `threat-report.md` agent | senior-backend-engineer | 4h | Grep-determined section number; Multi-Pattern subsection ordering |
| T016 | Update `narrative-templates.md` with Agentic Pattern Analysis template | senior-backend-engineer | 2h | Includes architect MED-T15-1 divergence rationale |
| T017 | Extend SARIF emission in `orchestrator.md` (maestro-pattern:<name> tags) | senior-backend-engineer | 2h | Sequential — depends on grep-check of existing maestro-layer code path |
| T018 | Write integration tests in `test_pattern_extraction.py` | tester | 2h | SARIF format-parity regex check |
| T019 | Write parser tests in `test_finding_pattern_parser.py` | tester | 2h | All 8 enum values + null/missing handling |
| T020 | Extend `examples/agentic-app/architecture.md` (+Specialist Agent +Learning Loop +Inter-agent Channel) | senior-backend-engineer | 1-2h | Architect consultation noted; verify multi-agent keyword present |
| T021 | Regenerate `examples/agentic-app/` full pipeline output | senior-backend-engineer | 2h | Sequential after T020; verifies ≥1 net-new AGP-NN per pattern |
| T022 | Regenerate `examples/web-app/` pipeline output | senior-backend-engineer | 0.5h | Verify zero non-`none` patterns |
| T023 | Regenerate `examples/microservices/` pipeline output | senior-backend-engineer | 0.5h | Verify zero non-`none` patterns |
| T024 | Regenerate `examples/ascii-web-api/` pipeline output | senior-backend-engineer | 0.5h | Verify zero non-`none` patterns |
| T025 | Regenerate `examples/free-text-microservice/` pipeline output | senior-backend-engineer | 0.5h | Verify zero non-`none` patterns |
| T026 | Regenerate `examples/mermaid-agentic-app/` pipeline output | senior-backend-engineer | 0.5h | Verify zero non-`none` patterns; tighten rules if false positive |
| T027 | Update `ADR-020-maestro-layer-classification.md` Revision History entry | senior-backend-engineer | 1h | Cross-reference ADR-026; closes MAESTRO compliance umbrella |
| T028 | Update `test_backward_compatibility.py` (pattern field default + multi-agent gate enforcement + 5 baseline byte-identical) | tester | 2h | FR-017 + SC-003 + SC-004 |
| T029 | Add CI verification: zero edits to 11 detection agent files (architect LOW-3) | tester | 1h | git diff assertion in test_backward_compatibility.py |
| T030 | Regenerate backward-compatibility PDF baselines for 5 examples (SOURCE_DATE_EPOCH=1700000000) | senior-backend-engineer | 1h | Per ADR-021; verify byte-identical |
| T031 | Run full pytest suite (all 4 new test files + updated existing) | tester | 1h | Full regression validation |
| T032 | Update `README.md` to reference agentic_pattern field + 6 patterns + ADR-026 | senior-backend-engineer | 0.5h | Documentation index |
| T033 | Final SC validation (SC-001 through SC-010) | tester | 2h | Includes empirical wall-clock timing (LOW-6) and SC-002 measurement methodology (LOW-T33-1) |

---

## Parallel Execution Waves

### Wave 0: Foundations (1-1.5 days)

**Quality Gate**: Schema, shared reference, ADR-026 (already authored), and orchestration documentation are syntactically valid and cross-referenced. Four-track parallel per plan.md Wave 0.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Shared Reference | T001 | senior-backend-engineer | Parallel with T002, T003, T004 |
| Schema | T002 | senior-backend-engineer | Parallel with T001, T003, T004 |
| Dispatch Rules | T003 | senior-backend-engineer | Parallel with T001, T002, T004 |
| Output Schemas | T004 | senior-backend-engineer | Parallel with T001, T002, T003 |

**Time**: ~1-1.5 day
**Gate Review**: code-reviewer spot-checks schema enum + AGP- regex; architect verifies ADR-026 cross-reference in T003

---

### Wave 1: Foundational + Synthesis Engine (2-3 days)

**Quality Gate**: Parser handles agentic_pattern field with backward-compat defaults; orchestrator Phase 3.6 produces deterministic pattern assignments; multi-agent gate predicate enforced; net-new findings emitted with AGP-NN prefix; tests pass on 6 baseline + extended agentic-app architectures.

**CRITICAL CHECKPOINT**: Phase 2 (T005-T006) MUST complete before any Phase 3 user story work begins. Synthesis chain T007 → T008 → T009 → T010 is sequential (no parallelism possible — same orchestrator file).

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Parser | T005 | senior-backend-engineer | Sequential (depends on T002 schema) |
| Orchestrator Skeleton | T006 | senior-backend-engineer | Sequential (depends on T001 shared reference) |
| Multi-Agent Gate | T007 | senior-backend-engineer | Sequential after T006 |
| Classification Rules | T008 | senior-backend-engineer | Sequential after T007 |
| Net-New Generation | T009 | senior-backend-engineer | Sequential after T008 |
| has-agentic-patterns Flag | T010 | senior-backend-engineer | Sequential after T009 |
| Synthesis Unit Tests | T011 | tester | Parallel with T007-T010 (independent test file) |
| Rule Validation Tests | T012 | tester | Parallel with T007-T010 (independent test file) |

**Time**: ~2-3 days
**Gate Review**: architect validates Phase 3.6 placement vs Feature 141 Phase 3.5 contract; code-reviewer reviews multi-agent gate predicate evaluation logic + classification rule precedence
**MVP CHECKPOINT**: End of T010 — synthesis engine produces deterministic pattern assignments. Stop and validate before proceeding to output surfacing.

**Note**: T013 (validate synthesis on extended agentic-app) sequences with Wave 3 because it depends on T020 (architecture extension).

---

### Wave 2: Output Surfacing (1-1.5 days)

**Quality Gate**: Pattern field surfaced through threats.md (column + Section 4b), threat-report (Agentic Pattern Analysis section), SARIF (maestro-pattern tags). All consumers can read the new field. Conditional gating works correctly. Three-track parallel per plan.md Wave 2.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| threats.md Template | T014 | senior-backend-engineer | Parallel with T015, T016, T018, T019 |
| Threat Report Section | T015 | senior-backend-engineer | Parallel with T014, T016, T018, T019 |
| Narrative Templates | T016 | senior-backend-engineer | Parallel with T014, T015, T018, T019 |
| SARIF Tag Emission | T017 | senior-backend-engineer | Sequential (depends on grep-check of existing maestro-layer code path per Component 6) |
| Integration Tests | T018 | tester | Parallel with T014-T016, T019 |
| Parser Tests | T019 | tester | Parallel with T014-T016, T018 |

**Time**: ~1-1.5 days
**Gate Review**: code-reviewer validates SARIF format parity (regex check); architect validates threat-report section ordering vs Feature 141 Section 6 convention (architect MED-T15-1 divergence rationale)

---

### Wave 3: agentic-app Extension + Example Regeneration (1-1.5 days)

**Quality Gate**: Extended agentic-app demonstrates ≥3 patterns end-to-end (Agent Collusion, Temporal Attack, Emergent Behavior). All 6 examples regenerated. 5 baselines produce zero non-`none` patterns (multi-agent gate predicate validated). Five-track parallel for non-agentic-app regeneration per plan.md Wave 3.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| Architecture Extension | T020 | senior-backend-engineer | Sequential (must precede T021 + T013) |
| agentic-app Full Pipeline | T021 | senior-backend-engineer | Sequential (depends on T020) |
| Synthesis Validation | T013 | tester | Sequential after T021 (validates extended demo) |
| web-app Regeneration | T022 | senior-backend-engineer | Parallel with T023-T026 |
| microservices Regeneration | T023 | senior-backend-engineer | Parallel with T022, T024-T026 |
| ascii-web-api Regeneration | T024 | senior-backend-engineer | Parallel with T022, T023, T025, T026 |
| free-text-microservice Regeneration | T025 | senior-backend-engineer | Parallel with T022-T024, T026 |
| mermaid-agentic-app Regeneration | T026 | senior-backend-engineer | Parallel with T022-T025 |

**Time**: ~1-1.5 days
**Gate Review**: code-reviewer verifies agentic-app surfaces ≥3 patterns; tester spot-checks 5 baselines for zero non-`none` patterns; architect consulted on T020 component additions per plan.md Component 7 Path 1

---

### Wave 4: Polish, Regression, & Final Validation (1-1.5 days)

**Quality Gate**: ADR-020 updated (closes MAESTRO compliance umbrella). Zero-edit invariant on 11 detection agents enforced via CI. 5 baseline PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000. Full pytest suite green. All 10 SCs verified.

| Track | Tasks | Agent | Parallel? |
|-------|-------|-------|-----------|
| ADR-020 Update | T027 | senior-backend-engineer | Parallel with T032 (per team-lead LOW recommendation: promote to Wave 3 if compression desired) |
| Backward-Compat Test Updates | T028 | tester | Sequential (depends on Wave 3) |
| Zero-Edit CI Test | T029 | tester | Sequential after T028 |
| Baseline PDF Regeneration | T030 | senior-backend-engineer | Sequential after T029 |
| Full Pytest Run | T031 | tester | Sequential after T030 |
| README Update | T032 | senior-backend-engineer | Parallel with T027 (per team-lead LOW recommendation: promote to Wave 3 if compression desired) |
| Final SC Validation | T033 | tester | Sequential after T031 (last task) |

**Time**: ~1-1.5 days
**Gate Review**: architect final sign-off on ADR-020 Revision History entry + ADR-026 cross-reference; security-analyst final check (no new secrets, deterministic rule table, no SARIF tag injection surface); product-manager final SC verification (SC-001 through SC-010)

---

## Wave Summary

| Wave | Name | Tasks | Time | Parallelism | Gate |
|------|------|-------|------|-------------|------|
| 0 | Foundations | T001-T004 | 1-1.5d | 4-track parallel | Schema + shared ref + orchestration docs |
| 1 | Foundational + Synthesis Engine | T005-T012 | 2-3d | T011/T012 parallel with T007-T010 | MVP: synthesis engine validated |
| 2 | Output Surfacing | T014-T019 | 1-1.5d | 5-track parallel (T017 sequential) | Pattern field surfaced through all formats |
| 3 | agentic-app Extension + Regeneration | T013, T020-T026 | 1-1.5d | 5-track parallel for T022-T026 | End-to-end demonstration |
| 4 | Polish, Regression, Final Validation | T027-T033 | 1-1.5d | T027/T032 parallel | Full regression + 10 SC verification |

**Total**: 6-8 days realistic (5d optimistic floor with full 4-track parallelism in Wave 0 and 5-track in Wave 3)
**Critical Path**: Wave 0 → Wave 1 → Wave 2 → Wave 3 → Wave 4 (sequential at wave level)
**Critical Path Bottleneck**: T007 → T008 → T009 → T010 synthesis chain (sequential dependency on orchestrator agent file — no parallelism possible)
**MVP Boundary**: End of Wave 1 (synthesis engine validated; ~3-4.5 days)

---

## Quality Gates Between Waves

Per Constitution and plan.md checkpoints:

| Gate | Wave Boundary | Reviewer | Pass Criteria |
|------|---------------|----------|----------------|
| G0 | Pre-Wave-0 | team-lead | tasks.md triple sign-off APPROVED (verified) |
| G1 | Wave 0 → Wave 1 | code-reviewer + architect | Schema valid; shared ref complete; ADR-026 cross-referenced |
| G2 | Wave 1 → Wave 2 | architect + code-reviewer | Synthesis engine deterministic; multi-agent gate enforced; AGP-NN findings generated; tests green |
| G3 | Wave 2 → Wave 3 | code-reviewer | All 3 output formats render pattern field; SARIF format parity verified |
| G4 | Wave 3 → Wave 4 | tester | Extended agentic-app surfaces ≥3 patterns; 5 baselines produce zero non-`none` patterns |
| G5 | Wave 4 → DONE | product-manager + architect + security-analyst | All 10 SCs validated; ADR-020 updated; baselines byte-identical; pytest green |

---

## Agent Workload Summary

| Agent (subagent_type) | Waves Active | Total Tasks | Total Effort | Peak Load |
|-----------------------|-------------|-------------|--------------|-----------|
| senior-backend-engineer | 0-4 | 22 | ~37-43h | Wave 1 (8 tasks, ~17h synthesis chain) |
| tester | 1-4 | 9 | ~17h | Wave 4 (4 tasks, ~6h) |
| architect | G1, G2, G5 (gate reviews) | 3 reviews | ~3h | Distributed across gates |
| code-reviewer | G1-G4 (gate reviews) | 4 reviews | ~2h | Distributed across gates |
| security-analyst | G5 only | 1 review | ~1h | Wave 4 only |
| product-manager | G5 only | 1 review | ~1h | Wave 4 only |

**No agent exceeds 80% load in any wave.** senior-backend-engineer is the primary implementer across Waves 0-3 (consistent with Feature 141 precedent — predominantly markdown agent file authoring + Python script + schema work). tester load concentrated in Waves 1-4 for unit tests, integration tests, validation, and final SC verification.

---

## Handoff to Orchestrator

**Feasibility**: APPROVED_WITH_CONCERNS (4 LOW from tasks.md tech-lead notes — advisory polish; none block execution)
**Tasks Location**: `specs/142-maestro-agentic-pattern-expansion/tasks.md`
**Wave Strategy**: 5 sequential waves (Wave 0-4) with intra-wave parallelism (4-track in Wave 0; 5-track in Waves 2 and 3)
**Agent Assignments**: Per matrix above — all agents use exact subagent_type names from `.claude/agents/_README.md`
**MVP Gate**: Wave 1 completion (synthesis engine validated on baseline architectures)
**Time Budget**: 6-8 days realistic (5d optimistic with full parallelism)
**Critical Path Risk**: T007-T010 synthesis chain in Wave 1 is sequential bottleneck — single developer required, no parallelism opportunity
**Optional Compression**: Per team-lead LOW item, T027 (ADR-020) and T032 (README) can be promoted to Wave 3 to compress Wave 4 by ~0.5d wall-clock if needed
