---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 4 user stories covered (US1-US4). All 14 FRs addressed across 29 tasks. SC-001 through SC-009 achievable via validation phase. P1 stories before P2. No scope creep. 2 non-blocking observations."
  architect_signoff:
    agent: architect
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered. Parallel opportunities properly identified. All 5 deliverables covered. 1 medium concern: orchestrator YAML frontmatter version/description update should be included in T017. 3 low concerns resolvable during implementation."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "29-task / 5-wave breakdown is well-sized for content-as-code scope. Critical path correctly identified. Parallelization opportunities maximized. 3 low findings: consider merging T024-T027 into single validation pass, Wave 3 parallelism depends on careful file section management, T015 example trees are highest-effort single task."
---

# Tasks: Threat Report Agent & Attack Trees

**Input**: Design documents from `/specs/015-threat-report-agent/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create foundational schema and template files that the report agent references

- [X] T001 [P] Create report output schema defining 7 required sections, completeness rules, and attack tree file naming in `schemas/report.yaml`
- [X] T002 [P] Create report template with YAML frontmatter placeholder, 7 section headings (Executive Summary through Appendix), field placeholders, and structural guidance in `templates/threat-report.md`

**Checkpoint**: Schema and template files ready — report agent can reference them in its contracts

---

## Phase 2: Foundational (Report Agent Core Structure)

**Purpose**: Create the report agent prompt file with YAML frontmatter, core mission, input contract, and quality standards. MUST complete before user story sections can be written.

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create `agents/threat-report.md` with YAML frontmatter (agent_name: threat-report, category: report, input_schema: schemas/output.yaml, output_schema: schemas/report.yaml, output_files list) and Core Mission section describing the agent's purpose: transform structured threat findings into narrative report with attack trees and remediation roadmap
- [X] T004 Write Input Contract section in `agents/threat-report.md` specifying: consumes complete `threats.md` (7 sections + 4a), references `schemas/output.yaml` for structure validation, lists all finding IR fields consumed (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type)
- [X] T005 Write Quality Standards / Validation Checklist section in `agents/threat-report.md` covering: all 7 report sections present and non-empty, every finding ID appears in Appendix, every Critical/High finding has attack tree, Mermaid syntax self-check, executive summary ≤500 words with no jargon, component names match exactly, risk levels preserved without reinterpretation

**Checkpoint**: Report agent core established — user story sections can now be added

---

## Phase 3: User Story 1 — Narrative Threat Report (Priority: P1) MVP

**Goal**: Report agent generates a narrative `threat-report.md` with executive summary, architecture overview, agent-by-agent threat analysis, cross-cutting themes, and finding reference appendix

**Independent Test**: Run report agent against `examples/mermaid-agentic-app/threats.md`, verify `threat-report.md` produced with all 7 sections, executive summary understandable without STRIDE knowledge

- [X] T006 [US1] Write Executive Summary Template section in `agents/threat-report.md` specifying: 5 required elements (risk posture, top 3-5 threats by business impact, key recommendations, compliance relevance with SOC2/ISO 27001/CWE/OWASP mapping, remediation timeline by priority tier), ~500 word maximum, no unexplained acronyms, define every acronym on first use, note what is working well alongside problems
- [X] T007 [US1] Write Architecture Overview methodology section in `agents/threat-report.md` specifying: derive system context from `threats.md` Section 1 (components, data flows, technologies), derive trust boundary summary from Section 2 (trust zones, boundary crossings with controls), present in narrative form for non-technical audience
- [X] T008 [US1] Write Threat Analysis methodology section in `agents/threat-report.md` specifying: agent-by-agent narrative with subsections for each STRIDE category (3.1-3.6) and AI category (4.1-4.2), full reasoning for each finding, component annotations, finding ID references, progressive technical depth from general to specific
- [X] T009 [US1] Write Cross-Cutting Theme Detection section in `agents/threat-report.md` specifying 4 detection criteria: (a) multiple findings from different agents targeting same component, (b) similar mitigation recommendations across threat categories, (c) findings forming attack chains where one finding's impact enables another's precondition, (d) component clusters with disproportionately high finding counts. Each theme must cite contributing finding IDs
- [X] T010 [US1] Write Correlation Group Handling section in `agents/threat-report.md` specifying: respect Section 4a groups from `threats.md`, discuss correlated findings as logical units in narrative, reference primary finding with cross-references to correlated peers, do not individually repeat correlated findings
- [X] T011 [US1] Write Finding Reference Appendix methodology section in `agents/threat-report.md` specifying: complete mapping table from report sections back to original finding IDs, every finding ID from `threats.md` Sections 3, 4, and 4a must appear, zero finding loss rule, table format with columns for finding ID, report section, and page/heading reference

**Checkpoint**: Report agent can generate complete narrative report. US1 independently testable.

---

## Phase 4: User Story 2 — Mermaid Attack Trees (Priority: P1)

**Goal**: Report agent generates Mermaid `flowchart TD` attack trees for every Critical and High finding following Schneier's methodology

**Independent Test**: Run report agent, verify every Critical/High finding has attack tree rendering correctly in Mermaid Live Editor, trees appear inline and as standalone files

- [X] T012 [US2] Write Attack Tree Construction Rules section in `agents/threat-report.md` specifying: root node = attacker's ultimate goal (from finding `threat` field), intermediate nodes = decomposed sub-goals with explicit AND/OR gates, leaf nodes = concrete atomic attack actions, minimum 3 levels for Critical findings, minimum 2 levels for High, decomposition stopping rule (stop when leaf nodes represent concrete actions requiring specific resources — skill, access, tools, time; do not decompose to implementation-level detail like specific CVEs or packet formats)
- [X] T013 [US2] Write Mermaid Conventions section in `agents/threat-report.md` specifying: `flowchart TD` orientation, node ID format `{FindingID}_{type}{N}` (e.g., AG1_root, AG1_and1, AG1_leaf1), explicit AND/OR gate nodes using diamond `{{"AND"}}` or hexagon `{{"OR"}}` shapes, all labels quoted `["Label text"]`, `classDef` styling (goal fill:#ff6b6b for red, andGate fill:#ffa500 for orange, orGate fill:#4ecdc4 for teal, leaf fill:#95e1d3 for green), `class` assignments for each node
- [X] T014 [US2] Write Mermaid Validation Checklist section in `agents/threat-report.md` covering: reserved word avoidance (never use `end`, `default` as bare node IDs), avoid `o`/`x` as first character after edge operators, quoted labels for all special characters (parentheses, colons, quotes), alphanumeric-prefixed node IDs only, maximum ~20 nodes per tree for readability, no loops in tree structure, `classDef`/`class` styling (not inline)
- [X] T015 [US2] Add two example attack trees to `agents/threat-report.md`: one for a STRIDE Critical finding (e.g., spoofing/privilege-escalation pattern with 3+ levels) and one for an AI High finding (e.g., agentic threat pattern with 2+ levels), demonstrating proper Mermaid syntax, AND/OR gates, node naming convention, color styling, and decomposition depth
- [X] T016 [US2] Write Dual Output Location instructions in `agents/threat-report.md` specifying: attack trees embedded inline in Section 5 (Attack Trees) of `threat-report.md` within Mermaid code blocks, AND saved as standalone files in `attack-trees/{finding-id}-attack-tree.md` (e.g., `attack-trees/AG-1-attack-tree.md`), standalone files include finding metadata header (ID, component, risk level, threat summary) above the Mermaid block

**Checkpoint**: Report agent can generate Mermaid attack trees for all Critical/High findings. US2 independently testable.

---

## Phase 5: User Story 4 — Orchestrator Integration (Priority: P1)

**Goal**: Phase 5 (Report) integrated into orchestrator pipeline, running after Phase 4 completes with fresh-context isolation

**Independent Test**: Run full orchestrator pipeline against sample input, verify Phase 5 produces `threat-report.md` and `attack-trees/` alongside `threats.md` and `threats.sarif`

- [X] T017 [US4] Add Phase 5 (Report) definition section to `agents/orchestrator.md` following existing phase pattern: describe purpose (generate narrative threat report with attack trees and remediation roadmap), input (completed `threats.md` from Phase 4), output (`threat-report.md` + `attack-trees/` directory), reference to `agents/threat-report.md`
- [X] T018 [US4] Add Phase 5 dispatch logic to `agents/orchestrator.md` specifying: invoke `agents/threat-report.md` after Phase 4 completes and `threats.md` is written, pass only `threats.md` file path as input (fresh context — do NOT pass accumulated pipeline state from Phases 1-4), write output to same directory as `threats.md`
- [X] T019 [US4] Add opt-out configuration to `agents/orchestrator.md` specifying: Phase 5 is default-on, can be skipped via `--skip-report` flag or equivalent orchestrator configuration, when skipped the pipeline completes normally after Phase 4 with no change to existing behavior
- [X] T020 [US4] Update orchestrator validation checklist in `agents/orchestrator.md` to include Phase 5 outputs: verify `threat-report.md` exists in output directory (when Phase 5 enabled), verify `attack-trees/` directory exists with files for each Critical/High finding, verify report frontmatter contains correct finding count and risk distribution

**Checkpoint**: Full pipeline (Phases 1-5) functional. US4 independently testable by running orchestrator.

---

## Phase 6: User Story 3 — Remediation Roadmap (Priority: P2)

**Goal**: Report agent generates a prioritized remediation roadmap with effort estimates that project managers can convert directly to backlog items

**Independent Test**: Run report agent, verify Remediation Roadmap section lists all findings ordered by risk level with effort estimates, each item directly convertible to a development task

- [X] T021 [US3] Write Remediation Roadmap methodology section in `agents/threat-report.md` specifying: list all findings ordered by risk level (Critical→Immediate first, then High→Short-term, Medium→Medium-term, Low→Backlog), group by component within same risk level, each item includes finding ID, component, mitigation text (preserved verbatim from `threats.md`), effort estimate (Low/Medium/High), dependency notes
- [X] T022 [US3] Write Effort Estimation heuristics in `agents/threat-report.md` specifying: Low effort = configuration changes, parameter tuning, existing feature enablement; Medium effort = new validation logic, access control additions, monitoring implementation; High effort = architectural changes, new components, protocol redesign. Estimates are qualitative complexity assessments, not time estimates
- [X] T023 [US3] Write Correlation Consolidation rules for roadmap in `agents/threat-report.md` specifying: correlated findings from Section 4a consolidated into single roadmap item, use primary finding ID, include correlation scope notes listing all contributing finding IDs, effort estimate reflects combined scope of correlated remediation

**Checkpoint**: Complete report agent — all 7 sections covered. US3 independently testable.

---

## Phase 7: Validation & Polish

**Purpose**: End-to-end validation against sample data and cross-cutting quality checks

- [X] T024 Run report agent against `examples/mermaid-agentic-app/threats.md` (19 findings: 3 Critical, 9 High, 7 Medium) and generate `threat-report.md` with all 7 sections
- [X] T025 Validate all 12 attack trees (3 Critical + 9 High findings) render correctly in Mermaid syntax — check node IDs, quoted labels, no reserved words, proper `classDef` styling
- [X] T026 Verify finding completeness: every finding ID from sample `threats.md` (S-1, S-2, T-1, T-2, R-1, R-2, I-1, I-2, D-1, D-2, E-1, AG-1 through AG-4, LLM-1 through LLM-4) appears in the Appendix: Finding Reference mapping
- [X] T027 Verify cross-cutting themes identified in sample output (at least 1 theme expected — LLM Agent Orchestrator has 10 findings across multiple agents)
- [X] T028 Save validated sample outputs to `examples/mermaid-agentic-app/threat-report.md` and `examples/mermaid-agentic-app/attack-trees/` directory
- [X] T029 Run full orchestrator pipeline (Phases 1-5) against `examples/mermaid-agentic-app/input.md` and verify Phase 5 produces report alongside existing `threats.md` and `threats.sarif`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately. T001 and T002 are parallel (different files).
- **Foundational (Phase 2)**: Depends on Phase 1 (agent references schema/template). T003 first, then T004 and T005 can be sequential within same file.
- **US1 Narrative (Phase 3)**: Depends on Phase 2. Tasks are sequential (same file `agents/threat-report.md`).
- **US2 Attack Trees (Phase 4)**: Depends on Phase 2. Can run in parallel with Phase 3 if sections are merged carefully, but safer sequentially after Phase 3.
- **US4 Orchestrator (Phase 5)**: Depends on Phase 2 (agent must exist). Can run in parallel with Phases 3-4 (different file `agents/orchestrator.md`).
- **US3 Roadmap (Phase 6)**: Depends on Phase 2. Can run in parallel with Phase 5.
- **Validation (Phase 7)**: Depends on ALL previous phases.

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational — no dependencies on other stories
- **US2 (P1)**: Depends on Foundational — independent of US1 (different sections of same file)
- **US4 (P1)**: Depends on Foundational — independent of US1/US2 (different file entirely)
- **US3 (P2)**: Depends on Foundational — independent of US1/US2/US4

### Parallel Opportunities

- **Phase 1**: T001 ∥ T002 (different files: `schemas/report.yaml` vs `templates/threat-report.md`)
- **Phase 5 ∥ Phase 3-4**: T017-T020 can run in parallel with T006-T016 (different files: `agents/orchestrator.md` vs `agents/threat-report.md`)
- **Phase 6 ∥ Phase 5**: T021-T023 can overlap with T017-T020 if agent sections are being written to different parts of the file

### Critical Path

```
T001+T002 → T003 → T004 → T005 → T006-T011 → T012-T016 → T021-T023 → T024-T029
                                  ↑                                        ↑
                                  └── T017-T020 (parallel, different file) ─┘
```

---

## Parallel Example: Wave Execution

```
Wave 1 (Setup — parallel):
  Agent A: T001 — schemas/report.yaml
  Agent B: T002 — templates/threat-report.md

Wave 2 (Foundational — sequential, same file):
  Agent A: T003 → T004 → T005 — agents/threat-report.md core

Wave 3 (User Stories — parallel across files):
  Agent A: T006-T011 — agents/threat-report.md (US1 narrative sections)
  Agent B: T017-T020 — agents/orchestrator.md (US4 orchestrator integration)

Wave 4 (Attack Trees + Roadmap — sequential, same file):
  Agent A: T012-T016 — agents/threat-report.md (US2 attack trees)
  Agent A: T021-T023 — agents/threat-report.md (US3 roadmap)

Wave 5 (Validation — sequential):
  Agent A: T024-T029 — End-to-end validation against sample data
```

---

## Implementation Strategy

### MVP First (US1 + US4 Only)

1. Complete Phase 1: Setup (schemas + template)
2. Complete Phase 2: Foundational (agent core)
3. Complete Phase 3: US1 — Narrative report sections
4. Complete Phase 5: US4 — Orchestrator integration
5. **STOP and VALIDATE**: Run pipeline, verify narrative report generates
6. Deploy/demo if ready — report without attack trees is still valuable

### Incremental Delivery

1. Setup + Foundational → Agent core ready
2. Add US1 (Narrative) → Test independently → Narrative report works
3. Add US2 (Attack Trees) → Test independently → Trees render in Mermaid
4. Add US4 (Orchestrator) → Test pipeline → Phase 5 dispatches correctly
5. Add US3 (Roadmap) → Test independently → Roadmap items are actionable
6. Validation → Full end-to-end against sample data

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 29 |
| Phase 1 (Setup) | 2 |
| Phase 2 (Foundational) | 3 |
| Phase 3 (US1 Narrative) | 6 |
| Phase 4 (US2 Attack Trees) | 5 |
| Phase 5 (US4 Orchestrator) | 4 |
| Phase 6 (US3 Roadmap) | 3 |
| Phase 7 (Validation) | 6 |
| Parallel opportunities | 3 wave groups |
| New files | 4 |
| Modified files | 1 |

---

## Notes

- All deliverables are markdown/YAML files — no application code, no test framework
- Single agent prompt file (`agents/threat-report.md`) is the main deliverable — most tasks are sections within it
- Orchestrator update (`agents/orchestrator.md`) is the only modified file — minimal diff approach
- Validation phase uses existing sample data at `examples/mermaid-agentic-app/threats.md`
- No automated test tasks — validation is manual (run agent against sample, verify outputs)
