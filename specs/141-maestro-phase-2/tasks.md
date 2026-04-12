---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-12
    status: APPROVED_WITH_CONCERNS
    notes: "All 6 user stories covered (US4 into US1, US6 into US2). 17/17 FRs addressed. No scope creep. 3 LOW: SC-001/002 statistical targets limited by 6-example validation surface, SC-006 no timing test, mermaid-agentic-app chain status uncertain."
  architect_signoff:
    agent: architect
    date: 2026-04-12
    status: APPROVED_WITH_CONCERNS
    notes: "2 MEDIUM addressed: (1) T005 expanded to include detect_artifacts() update for has_attack_chains, (2) T016 split into T016 (parsing/rendering) + T016a (Typst data injection). 3 LOW: T006 line reference brittle but semantic, T011 TDD revalidation, backward-compat test update implicit in T030. 4 INFO acknowledged."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-12
    status: APPROVED_WITH_CONCERNS
    notes: "FEASIBLE. 34 tasks, 7 phases, 10-12.5 day realistic estimate (upper bound of PRD 8-12d). Correlation engine (Wave 3) is schedule bottleneck at 3-4 days. 3 LOW: single-example validation surface, potential Phase 4-5 parallelization, SC-006 timing test."
---

# Tasks: MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis

**Input**: Design documents from `specs/141-maestro-phase-2/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. US4 (chain-breaking controls) is integrated into US1 (part of the artifact). US6 (canonical format) is integrated into US2 (narrative vocabulary).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Schema & Shared References)

**Purpose**: Create foundational schema, shared reference files, and orchestration documentation that all subsequent phases depend on.

- [X] T001 Create attack chain schema at `schemas/attack-chain.yaml` (v1.0) with chain_id, title, layers, max_severity, findings, narrative, chain_breaking_controls, and surfaced fields per data-model.md
- [X] T002 [P] Create correlation pattern lookup table at `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md` with (STRIDE category, MAESTRO layer) -> (STRIDE category, MAESTRO layer) transition mappings, causal vocabulary per transition type, chain assembly rules, and chain-breaking heuristic algorithm
- [X] T003 [P] Update orchestration output schemas at `.claude/skills/tachi-orchestration/references/output-schemas.md` to add attack-chains.md artifact with section completeness checklist and conditional emission rules
- [X] T004 [P] Update orchestration dispatch rules at `.claude/skills/tachi-orchestration/references/dispatch-rules.md` to document Phase 3.5 cross-layer correlation placement after Phase 3 dedup and before Phase 4 Assess

---

## Phase 2: Foundational (Parser & Orchestrator Skeleton)

**Purpose**: Core infrastructure that MUST be complete before user story implementation — the parser function and orchestrator phase skeleton that all downstream work depends on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Add `parse_attack_chains()` function to `scripts/tachi_parsers.py` that parses an `attack-chains.md` artifact into a list of chain dictionaries with chain_id, title, layers, max_severity, findings (list of member dicts), narrative, chain_breaking_controls, and surfaced fields. Also update `detect_artifacts()` in `scripts/tachi_parsers.py` to detect `attack-chains.md` in the target directory and set `has_attack_chains` boolean in the artifacts dict (same pattern as `has_attack_trees`)
- [X] T006 Insert Phase 3.5 skeleton into `.claude/agents/tachi/orchestrator.md` after existing Phase 3 correlation detection (after line ~383) and before Phase 4 Assess — include input contract (Phase 1 component inventory, data flow graph, deduplicated findings IR), output contract (attack-chains.md, has-attack-chains boolean), independence invariant with Section 4a, and reference to attack-chain-patterns-shared.md

**Checkpoint**: Parser and orchestrator skeleton ready — user story implementation can begin.

---

## Phase 3: User Story 1+4 — Cross-Layer Chain Detection & Chain-Breaking Controls (Priority: P0)

**Goal**: The orchestrator detects cross-layer attack chains from deduplicated findings using rule-based correlation patterns, assembles them into an attack-chains.md artifact with chain-breaking control recommendations, and sets the `has-attack-chains` boolean for downstream consumption.

**Independent Test**: Run the orchestrator on an architecture with findings across 3+ MAESTRO layers. Verify attack-chains.md is produced with at least one chain containing ordered finding references, layer progression, causal narrative, and chain-breaking controls. Run again on a single-layer architecture and verify no artifact is produced.

- [X] T007 [US1] Implement cross-layer correlation logic in orchestrator Phase 3.5 at `.claude/agents/tachi/orchestrator.md`: group findings by component and MAESTRO layer, apply correlation signals (component lineage from data flow graph, data flow dependency from shared paths, layer adjacency with structural relationship), load transition lookup from `attack-chain-patterns-shared.md`
- [X] T008 [US1] Implement chain assembly and ranking in orchestrator Phase 3.5: assemble ordered finding sequences, filter to 2+ layers with Critical/High finding, rank by severity desc then length desc then chain ID alpha asc, cap surfaced chains at top 5
- [X] T009 [US1] Implement chain-breaking control heuristic in orchestrator Phase 3.5: for 2-link chains identify middle finding, for 3+ link chains identify highest betweenness centrality node, mark as heuristic with disclaimer
- [X] T010 [US1] Implement attack-chains.md artifact generation in orchestrator Phase 3.5: YAML frontmatter with schema_version, Section 1 Chain Summary table, Section 2 Chain Details per chain (title, layers, findings with roles, attack progression narrative with causal vocabulary, chain-breaking controls). Conditional on chain detection — set `has-attack-chains` boolean
- [X] T011 [P] [US1] Write unit tests in `tests/scripts/test_attack_chains.py`: chain detection from mock finding sets, single-layer no-chain case, Unclassified findings excluded, max 7-layer chain, ranking order verification, chain-breaking heuristic, determinism (same input = same output), many-to-many finding membership
- [X] T012 [US1] Validate correlation engine against `examples/agentic-app/` — verify at least one chain spanning 3+ layers is detected with genuine causal relationship (not false grouping)

**Checkpoint**: Correlation engine produces attack-chains.md with chain-breaking controls. Deterministic. No false chains on example architectures.

---

## Phase 4: User Story 2+6 — Threat Report Attack Chains Narrative (Priority: P0)

**Goal**: The threat report includes a new "Attack Chains" section with narrative walkthroughs for Critical and High chains, using canonical CSA MAESTRO vocabulary ("enables," "triggers," "shifts," "manifests as").

**Independent Test**: Generate a threat report from an architecture with detected chains. Verify the Attack Chains section appears after Attack Trees with 150-300 word narratives per chain. Verify no section appears when no chains exist.

- [X] T013 [US2] Add Section 6 "Cross-Layer Attack Chains" to `.claude/agents/tachi/threat-report.md` after existing Section 5 (Attack Trees): load attack-chains.md on-demand, generate narrative walkthrough per Critical/High chain covering initial exploit, intermediate cascades with causal transitions using canonical CSA vocabulary, and business impact. Section conditional on `has-attack-chains`
- [X] T014 [US2] Update threat-report agent input contract in `.claude/agents/tachi/threat-report.md` frontmatter and skill references to document expanded input from "threats.md only" to "threats.md + attack-chains.md (conditional)"
- [X] T015 [US2] Validate narrative generation against `examples/agentic-app/` — verify chain narratives are 150-300 words, use causal vocabulary, and follow the canonical CSA MAESTRO worked example structure

**Checkpoint**: Threat report Section 6 generates conditional narratives with canonical MAESTRO format.

---

## Phase 5: User Story 3 — PDF Attack Chain Diagram Pages (Priority: P0)

**Goal**: The PDF security report renders cross-layer attack chains as dedicated pages with vertical MAESTRO layer stack diagrams, condensed narrative, and finding references.

**Independent Test**: Generate a PDF from an architecture with detected chains. Verify chain pages appear after Attack Path pages with rendered diagrams, narrative, and finding IDs. Verify no pages appear when no chains exist.

- [X] T016 [US3] Add chain parsing and Mermaid rendering to `scripts/extract-report-data.py`: call `parse_attack_chains()` via tachi_parsers to load chain data, generate Mermaid flowchart TD diagrams per chain (vertical layer stack, L1 top to L7 bottom, downward arrows with causal labels), invoke existing `render_mermaid_to_png()` for chain diagram PNG rendering
- [X] T016a [US3] Add chain Typst data injection to `scripts/extract-report-data.py` `_generate_typst_data()` function: inject chain entries with id, title, layers, max-severity, has-image, image-path, narrative, finding-ids into the Typst data file (separate from parsing/rendering in T016)
- [X] T017 [P] [US3] Create Typst template at `templates/tachi/security-report/attack-chain.typ`: portrait layout, header with chain ID badge + title + layer progression, diagram section with rendered PNG, narrative section, impacted finding IDs footer, MAESTRO layer color scheme (distinct from attack tree colors)
- [X] T018 [US3] Update `templates/tachi/security-report/main.typ`: import attack-chain.typ, add `has-attack-chains` default value in Section 2b defaults block (matching `has-attack-trees` pattern), add conditional page sequencing immediately after Attack Path Analysis section (~line 235) with section divider
- [X] T019 [US3] Extend mmdc preflight gate in `.claude/commands/tachi.security-report.md` Step 1 to check for attack-chains artifact alongside attack-trees, update artifact detection table to include `attack-chains.md` with tier mapping
- [X] T020 [P] [US3] Write integration tests in `tests/scripts/test_attack_chain_extraction.py`: parse_attack_chains from fixture artifact, Mermaid flowchart syntax validation, Typst data structure verification, conditional gate (no chains = no pages)
- [X] T021 [US3] Validate PDF rendering against `examples/agentic-app/` — verify chain diagram pages render with correct vertical layout, MAESTRO colors, and finding references

**Checkpoint**: PDF chain diagram pages render correctly with vertical MAESTRO layer stack. Conditional gate works (no pages when no chains).

---

## Phase 6: User Story 5 — End-to-End Example Demonstration (Priority: P1)

**Goal**: At least one example architecture demonstrates a multi-layer chain end-to-end with all output formats (artifact, narrative, PDF diagrams). All 6 example outputs regenerated.

**Independent Test**: Run full pipeline on agentic-app example. Verify output includes attack-chains.md with 3+ layer chain, threat-report.md with Attack Chains section, and PDF with chain diagram pages. Verify 5 other examples produce byte-identical output when no chains detected.

- [X] T022 [US5] Extend `examples/agentic-app/` architecture description with 1-2 components to strengthen cross-layer data flows if needed for 3+ layer chain demonstration
- [X] T023 [US5] Regenerate `examples/agentic-app/` full pipeline output: threats.md, attack-chains.md, threat-report.md, security-report PDF with chain diagram pages
- [X] T024 [P] [US5] Regenerate `examples/web-app/` pipeline output (no chains expected)
- [X] T025 [P] [US5] Regenerate `examples/microservices/` pipeline output (no chains expected)
- [X] T026 [P] [US5] Regenerate `examples/ascii-web-api/` pipeline output (no chains expected)
- [X] T027 [P] [US5] Regenerate `examples/free-text-microservice/` pipeline output (no chains expected)
- [X] T028 [P] [US5] Regenerate `examples/mermaid-agentic-app/` pipeline output (may have chains given L1/L2/L3/L7 MAESTRO coverage)

**Checkpoint**: agentic-app demonstrates end-to-end chain. All 6 examples regenerated.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: ADR documentation, backward compatibility verification, and full regression testing.

- [X] T029 [P] Update ADR-020 at `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md`: add "Phase 2: Cross-Layer Correlation" section documenting correlation architecture, Phase 3.5 placement, rule-based pattern matching, chain assembly algorithm. Update Decision section. Cross-reference attack-chain.yaml schema
- [X] T030 Regenerate backward-compatibility PDF baselines under `SOURCE_DATE_EPOCH=1700000000` for 5 examples without chains (web-app, microservices, ascii-web-api, free-text-microservice, mermaid-agentic-app) and verify byte-identical against pre-feature baselines per ADR-021
- [X] T031 Run full pytest suite (`tests/scripts/`) and verify all tests pass including new test_attack_chains.py and test_attack_chain_extraction.py
- [X] T032 [P] Update `README.md` prerequisites section to document attack-chains artifact in pipeline output list
- [X] T033 Final validation: run pipeline on agentic-app and verify SC-001 (chain detection), SC-002 (chain quality), SC-003 (output completeness), SC-004 (determinism), SC-007 (3+ layer example chain)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1+US4 (Phase 3)**: Depends on Phase 2 — chain detection is the prerequisite for all downstream stories
- **US2+US6 (Phase 4)**: Depends on Phase 3 — needs attack-chains.md artifact to generate narratives
- **US3 (Phase 5)**: Depends on Phase 3 and Phase 4 — needs chain data for diagrams and narrative for condensed text
- **US5 (Phase 6)**: Depends on Phases 3, 4, 5 — end-to-end demonstration requires all pipeline components
- **Polish (Phase 7)**: Depends on Phase 6 — ADR and regression after all examples regenerated

### Within Each Phase

- Tasks marked [P] can run in parallel within their phase
- Unmarked tasks within a phase are sequential
- Tests (T011, T020) can run in parallel with other [P] tasks in their phase

### Parallel Opportunities

**Phase 1**: T002, T003, T004 can all run in parallel (different files, no dependencies)
**Phase 3**: T011 can run in parallel with T007-T010 (test file is independent)
**Phase 5**: T017 and T020 can run in parallel with each other (different files)
**Phase 6**: T024-T028 can all run in parallel (independent example directories)
**Phase 7**: T029 and T032 can run in parallel (different files)

---

## Parallel Example: Phase 1

```bash
# Launch all setup tasks together (different files):
Task: "Create attack-chain.yaml schema at schemas/attack-chain.yaml"
Task: "Create correlation pattern table at .claude/skills/tachi-shared/references/attack-chain-patterns-shared.md"
Task: "Update output-schemas.md at .claude/skills/tachi-orchestration/references/output-schemas.md"
Task: "Update dispatch-rules.md at .claude/skills/tachi-orchestration/references/dispatch-rules.md"
```

## Parallel Example: Phase 6

```bash
# Launch all non-agentic-app example regenerations in parallel:
Task: "Regenerate examples/web-app/ pipeline output"
Task: "Regenerate examples/microservices/ pipeline output"
Task: "Regenerate examples/ascii-web-api/ pipeline output"
Task: "Regenerate examples/free-text-microservice/ pipeline output"
Task: "Regenerate examples/mermaid-agentic-app/ pipeline output"
```

---

## Implementation Strategy

### MVP First (US1 Only — Phase 1-3)

1. Complete Phase 1: Setup (schemas, shared references)
2. Complete Phase 2: Foundational (parser, orchestrator skeleton)
3. Complete Phase 3: US1+US4 (correlation engine + artifact)
4. **STOP and VALIDATE**: Run orchestrator on agentic-app, verify chain detection
5. MVP deliverable: attack-chains.md artifact with chains and chain-breaking controls

### Incremental Delivery

1. Phase 1+2 -> Foundation ready
2. Phase 3 (US1+US4) -> Chain detection validated (MVP!)
3. Phase 4 (US2+US6) -> Threat report narrative with canonical format
4. Phase 5 (US3) -> PDF chain diagram pages
5. Phase 6 (US5) -> All examples regenerated, end-to-end demo
6. Phase 7 -> ADR, backward compat baselines, final regression

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 34 |
| Phase 1 (Setup) | 4 tasks |
| Phase 2 (Foundational) | 2 tasks |
| Phase 3 (US1+US4) | 6 tasks |
| Phase 4 (US2+US6) | 3 tasks |
| Phase 5 (US3) | 7 tasks |
| Phase 6 (US5) | 7 tasks |
| Phase 7 (Polish) | 5 tasks |
| Parallel opportunities | 5 waves with [P] tasks |
| MVP scope | Phase 1-3 (12 tasks) |
| Architect MEDIUM items addressed | T005 expanded (detect_artifacts), T016 split (T016+T016a) |
| Estimated effort | 8-12 days per PRD timeline |

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks within the same phase
- [Story] label maps task to specific user story for traceability
- US4 (chain-breaking controls) integrated into US1 — both produce the attack-chains.md artifact
- US6 (canonical MAESTRO format) integrated into US2 — narrative uses canonical CSA vocabulary
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
