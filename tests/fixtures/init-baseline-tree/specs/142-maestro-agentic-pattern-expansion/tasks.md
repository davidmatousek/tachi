---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-16
    status: APPROVED
    notes: "6/6 user stories covered (US4 → T001 coverage table; US3+US5 → Phase 4 output surfacing). 20/20 spec FRs traced including FR-002 3-value Strength constraint, FR-006 multi-agent gate predicate, FR-014 SARIF parity, FR-015 Path 1 (extend agentic-app), FR-017 baseline default-`none`, FR-018 ADR-020 Revision History entry. 13/13 PRD DoD items mapped. Zero scope creep — MAESTRO infographics + compensating-controls pattern recs correctly deferred. All 3 architect MEDIUM (MED-1/2/3 from plan), 4 architect LOW (LOW-3/5/6 + LOW-7), and 1 PM LOW (LOW-2 idempotence) folded into specific tasks. Backward compatibility adequate (T028 + T029 + T030 enforce Constitution Principle III). Tasks.md follows Feature 141 precedent structure exactly. Path 1 selection (3 components in T020) is the architectural minimum for the 3 previously-uncovered patterns. 0 BLOCKING / 0 MEDIUM / 0 LOW."
  architect_signoff:
    agent: architect
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks.md cleanly translates architect-approved plan.md into 33 sequenced + parallelized tasks across 6 phases. All 3 plan.md MEDIUM resolutions (MED-1 ADR-026 governance rule, MED-2 component_type/topology token lists, MED-3 AGP-NN id prefix) properly reflected in task descriptions. Phase 3.6 placement (T006) preserves Feature 141 Phase 3.5 contract. Zero-edit invariant on 11 detection agents asserted in T029. Backward compat covered by T028+T029+T030. 4 architect LOW items folded (LOW-3 → T029, LOW-5 → T011, LOW-6 → T033, plus PM LOW-2 → T011 idempotence). 1 MEDIUM concern (MED-T15-1 subsection ordering tertiary tiebreaker rule consistency vs Feature 141 Section 6 chain ordering convention) RESOLVED INLINE in T016 description (deliberate divergence rationale documented). 2 LOW concerns (LOW-T11-1 content-overlap test for net-new findings, LOW-T33-1 SC-002 measurement methodology) RESOLVED INLINE in T011 and T033 descriptions respectively."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "33-task breakdown feasible within 5-8d Option C budget (calibrate 6-8d realistic, 5d optimistic floor with full 4-track parallelism). Wave structure (4-5 waves) maps cleanly to plan.md preview; critical path ~5-6d wall-clock; T007-T010 synthesis engine bottleneck inherent (no parallelism possible — sequential dependency chain on the orchestrator agent file). No file conflicts across [P] batches; recommended subagent_type mapping documented for agent-assignments.md generation. Phase 3.6 placement after Feature 141 Phase 3.5 preserves backward compat. 4 LOW concerns are advisory polish (effort calibration note, 4-track opportunistic phrasing, T015/T016 runtime-read clarification, T027/T032 promotion to Wave 3 for ~0.5d wall-clock compression) — none block triple sign-off. Phase 5 example regeneration parallelism (T022-T026 5-track) is the largest single-wave parallel opportunity. agentic-app extension (T020) at 1-2h is consistent with Feature 141 architecture extension precedent."
---

# Tasks: MAESTRO Phase 3 — Agentic Threat Pattern Expansion

**Input**: Design documents from `specs/142-maestro-agentic-pattern-expansion/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, ADR-026

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. US-1 (Agent Collusion filter) and US-2 (Temporal Attack detection) are integrated into Phase 3 (synthesis engine) since both depend on the same classification engine. US-5 (pattern-tagged downstream output) and US-3 (Emergent Behavior in PDF) are integrated into Phase 4 (output surfacing). US-4 (coverage mapping documentation) is integrated into Phase 1 (shared reference authoring). US-6 (end-to-end demo) is Phase 5.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Schema, Shared Reference, ADR-026)

**Purpose**: Foundational schema, shared reference file, and ADR documentation that all subsequent phases depend on. Three-track parallel per plan.md Wave 0.

- [X] T001 [P] [US4] Author shared reference at `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` with YAML frontmatter (type, version 1.0.0, consumers: orchestrator + threat-report), Section 1 (six canonical pattern definitions with CSA citations + 2-3 representative examples + detection criteria per pattern), Section 2 (coverage mapping table with 6 rows × 3 columns: Currently Covered By / Coverage Strength constrained to Full|Partial|None — Coverage Required / Gap with required 1-sentence justification on Partial), Section 3 (classification rule table R-01 through R-06 with match_conditions schema, priority, generates_finding_when_no_match flag, generation_template), Section 4 (multi-agent gate predicate spec with three OR conditions a/b/c + worked examples on the 6 baseline architectures + explicit component_type token list of 4 tokens + topology indicator list of 4 indicators per data-model.md MED-2 resolution)
- [X] T002 [P] [US5] Bump `schemas/finding.yaml` schema_version 1.3 → 1.4: add `agentic_pattern` enum field with 8 values (`agent_collusion`, `emergent_behavior`, `temporal_attack`, `trust_exploitation`, `communication_vulnerability`, `resource_competition`, `none`, `multiple`), default `none`, description per data-model.md Entity 1; AND extend `id.pattern` regex to accept `AGP-\d+` prefix for net-new generated findings (per data-model.md MED-3 resolution). Add CHANGELOG migration note for 1.3 → 1.4
- [X] T003 [P] Update `.claude/skills/tachi-orchestration/references/dispatch-rules.md` to document Phase 3.6 cross-pattern synthesis placement after Phase 3.5 cross-layer correlation and before Phase 4 Assess; cross-reference ADR-026
- [X] T004 [P] Update `.claude/skills/tachi-orchestration/references/output-schemas.md` to add `agentic_pattern` field to finding IR schema, add Section 4b "Findings by Agentic Pattern" to threats.md output schema (conditional on has-agentic-patterns), document new `has-agentic-patterns` boolean

**Note**: T001 satisfies US4 (coverage mapping documentation user story) because the coverage mapping table is the primary US4 deliverable. ADR-026 already authored during /aod.project-plan; no separate task needed.

**Checkpoint**: Schema, shared reference, and orchestration documentation ready. Wave 0 complete.

---

## Phase 2: Foundational (Parser & Orchestrator Skeleton)

**Purpose**: Core infrastructure that MUST be complete before user story implementation — the parser updates and orchestrator phase skeleton that all downstream work depends on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Update `scripts/tachi_parsers.py`: extend `parse_threats_findings()` to extract the new `agentic_pattern` column from threats.md tables (default to `none` for missing column to preserve backward compat per FR-017); add new `parse_finding_pattern()` helper that handles all 8 enum values + null/missing input; update `detect_artifacts()` to set `has_agentic_patterns` boolean when at least one finding has non-`none` pattern (mirrors `has_attack_chains` pattern from Feature 141)
- [X] T006 Insert Phase 3.6 skeleton into `.claude/agents/tachi/orchestrator.md` AFTER Phase 3.5 cross-layer correlation (Feature 141) and BEFORE Phase 4 Assess — include input contract (Phase 1 component inventory with agentic/llm classification, data flow graph, deduplicated findings IR with attack-chains.md from Phase 3.5), output contract (modifies findings IR in-place adding agentic_pattern, may emit net-new AGP-NN findings, sets has-agentic-patterns boolean), independence invariant statement vs Phase 3.5 (does NOT extend attack-chains.md per FR-008) and vs 11 detection agents (zero-edit invariant per ADR-026), reference to maestro-agentic-patterns-shared.md and ADR-026

**Checkpoint**: Parser and orchestrator skeleton ready — synthesis engine implementation can begin.

---

## Phase 3: User Story 1 + User Story 2 — Pattern Synthesis Engine (Priority: P0)

**Goal**: The orchestrator Phase 3.6 evaluates the multi-agent gate predicate, applies the classification rule table to assign `agentic_pattern` on every deduplicated finding, and optionally generates net-new findings (with AGP-NN prefix) for the three previously-uncovered patterns when no existing finding represents them. Deterministic by construction (ADR-021).

**Independent Test**: Run the orchestrator on the extended agentic-app architecture. Verify findings receive `agentic_pattern` values reflecting their content + architectural context. Verify ≥1 net-new AGP-NN finding is generated per previously-uncovered pattern (Agent Collusion, Temporal Attack, Emergent Behavior). Run again on a single-agent architecture (e.g., web-app) and verify all findings receive `agentic_pattern: none` (multi-agent gate predicate FALSE).

- [X] T007 [US1] Implement multi-agent gate predicate evaluation step in orchestrator Phase 3.6 at `.claude/agents/tachi/orchestrator.md`: count agentic/llm-classified components from Phase 1 (condition a), detect inter-component data flows where both endpoints are agentic/llm (condition b), case-insensitive substring search architecture description for keywords [multi-agent, swarm, supervisor, delegation, agent mesh] (condition c). If ALL three conditions FALSE → assign `agentic_pattern: none` to all findings → set has-agentic-patterns=false → exit phase. If ANY condition TRUE → continue to step T008
- [X] T008 [US1] Implement classification rule table application in orchestrator Phase 3.6: load rule entries R-01 through R-06 from `maestro-agentic-patterns-shared.md` Section 3, evaluate rules in priority order (lowest priority value = most specific = first), assign first matching pattern per finding, assign `multiple` on equal-priority match (per data-model.md Entity 3 tie-breaking spec), default `none` for findings matching no rule
- [X] T009 [US2] Implement net-new finding generation step in orchestrator Phase 3.6: for each rule with `generates_finding_when_no_match: true` (R-01 Agent Collusion, R-02 Temporal Attack, R-03 Emergent Behavior), check if any existing finding now carries the pattern label; if not AND architectural context matches the rule's match_conditions, emit a single net-new finding with id format `AGP-NN` (sequential), category: agentic, agentic_pattern: <pattern>, target_component = first matching component, description rendered from rule's generation_template, likelihood/impact defaulted to MEDIUM, risk_level computed via existing 3×3 OWASP matrix
- [X] T010 [US1] Set `has-agentic-patterns` boolean in orchestrator Phase 3.6 final step (true iff any non-`none` pattern present after T008+T009); this boolean is consumed by Phase 5 threat-report agent for conditional Agentic Pattern Analysis section gating
- [X] T011 [P] [US1] Write unit tests in `tests/scripts/test_pattern_synthesis.py`: multi-agent gate predicate evaluation across 6 baseline architectures + extended agentic-app + a synthetic single-agent-with-persistent-state fixture (per architect LOW-5); classification rule precedence + tied-priority `multiple` assignment cases; net-new finding generation triggers + suppression-when-existing checks (suppress when existing finding has matching pattern label OR — per architect LOW-7 / LOW-T11-1 — when existing finding description has ≥80% token overlap with the rule's generation_template, providing defense-in-depth against content duplication); determinism (same input twice produces byte-identical output per ADR-021); backward-compat (pre-Feature-142 finding IR without `agentic_pattern` field parses with default `none` per FR-017); idempotence (run synthesis twice on same architecture, second run produces zero net-new findings AND modifies zero existing findings — per PM LOW-2)
- [X] T012 [P] [US1] Write rule table validation tests in `tests/scripts/test_pattern_classification_rules.py`: all 6 patterns covered by ≥1 rule, each rule's match_conditions reference only documented finding fields and topology/component_type tokens from data-model.md, all `generates_finding_when_no_match: true` rules have non-empty generation_template, rule priority is total-ordered (no ambiguous priority on equal specificity)
- [X] T013 [US1] Validate synthesis engine against `examples/agentic-app/` (extended in T020) — verify ≥3 previously-uncovered patterns are surfaced (Agent Collusion, Temporal Attack, Emergent Behavior); verify findings receive deterministic pattern assignments across two consecutive runs

**Checkpoint**: Synthesis engine produces deterministic pattern assignments. Multi-agent gate predicate enforced. Net-new findings emitted with AGP-NN prefix. No false positives on single-agent architectures.

---

## Phase 4: User Story 5 + User Story 3 — Output Surfacing (Priority: P1 + P0)

**Goal**: The new `agentic_pattern` field is surfaced through all output formats: threats.md (Pattern column + conditional Section 4b), threat-report.md (conditional Agentic Pattern Analysis section), and SARIF (`maestro-pattern:<name>` tags matching `maestro-layer:` convention). Three-track parallel per plan.md Wave 2.

**Independent Test**: Generate threats.md, threat-report.md, and SARIF from a multi-agent architecture with detected patterns. Verify Pattern column appears in threats.md table; Section 4b groups findings by pattern; threat-report has Agentic Pattern Analysis section with ordered subsections; SARIF has `maestro-pattern:<name>` tags on non-`none` findings only.

- [X] T014 [P] [US5] Update `templates/tachi/output-schemas/threats.md`: add new Pattern column to Section 7 findings table inserted between Category and Component columns (column always renders; empty values display as `—`); add new conditional Section 4b "Findings by Agentic Pattern" placed AFTER Section 4a (intra-component correlation) and BEFORE Section 5, with grouping by canonical pattern (count + finding IDs per pattern), suppressed entirely when has-agentic-patterns=false
- [X] T015 [P] [US3] Add new "Agentic Pattern Analysis" conditional section to `.claude/agents/tachi/threat-report.md` placed AFTER Cross-Layer Attack Chains (Feature 141 Section 6) and BEFORE Findings Detail; section number determined at code time by grep-counting existing sections (NOT hardcoded per FR-011); load `maestro-agentic-patterns-shared.md` on-demand for canonical definitions; per pattern subsection: definition (1 sentence) + Critical/High/Medium/Low finding counts + 100-200 word narrative describing manifestation in this architecture + impacted finding IDs with cross-references; subsections ordered by max severity desc → finding count desc → pattern enum order tertiary tiebreak; zero-finding subsections suppressed; section omitted entirely when has-agentic-patterns=false; multi-pattern findings (`agentic_pattern: multiple`) rendered under each matching pattern AND under a dedicated "Multi-Pattern Findings" subsection rendered first per plan.md Open Questions Resolution
- [X] T016 [P] [US3] Update `.claude/skills/tachi-threat-reporting/references/narrative-templates.md`: add new Agentic Pattern Analysis section template with subsection structure, ordering rules (max severity desc → finding count desc → pattern enum order tertiary tiebreak — note: Feature 141 Section 6 uses chain_id alphabetic for its tertiary tiebreaker per architect MED-T15-1; the divergence is deliberate because pattern enum order is a meaningful semantic ordering CSA → tachi while chain_id alphabetic is an arbitrary uniqueness tiebreaker — document this divergence rationale in narrative-templates.md), suppression rules (zero-finding subsections hidden; full section omitted when has-agentic-patterns=false), Multi-Pattern Findings subsection format, optional chain-membership cross-reference format ("Finding F-12 (Agent Collusion) participates in Chain CHAIN-002") preserving FR-008 independence invariant
- [X] T017 [US5] Extend SARIF emission step in `.claude/agents/tachi/orchestrator.md` to add `maestro-pattern:<pattern_name>` tag to `result.properties.tags` for findings with non-`none` `agentic_pattern`; tag format MUST match the existing `maestro-layer:<L#>` convention exactly (lowercase, colon-separator, no quoting, no spaces); findings with `agentic_pattern: none` MUST NOT receive a `maestro-pattern:` tag (avoid noise); implementation MUST grep-check the existing `maestro-layer:` tagging code path before adding pattern tag (per plan.md Component 6 verification step)
- [X] T018 [P] [US5] Write integration tests in `tests/scripts/test_pattern_extraction.py`: extract-report-data.py correctly extracts pattern field from threats.md; threat-report Pattern Analysis subsection construction (severity counts, finding ID enumeration, ordering); SARIF tag emission format parity test that compares `maestro-pattern:<name>` token format against `maestro-layer:<L#>` token format from a sample SARIF output (regex parity check)
- [X] T019 [P] [US5] Write parser tests in `tests/scripts/test_finding_pattern_parser.py`: `parse_threats_findings()` returns pattern field on each finding object (8 valid enum values); default behavior on pre-Feature-142 baselines without the field (defaults to `none`); `parse_finding_pattern()` helper handles all 8 enum values + null/missing/empty-string input gracefully

**Checkpoint**: Pattern field surfaced through threats.md (column + Section 4b), threat-report (Agentic Pattern Analysis section), SARIF (maestro-pattern tags). All consumers can read the new field. Output is deterministic and conditional gating is correct.

---

## Phase 5: User Story 6 — End-to-End Multi-Agent Example (Priority: P0)

**Goal**: The agentic-app example architecture is extended (per FR-15 Path 1 selected in plan.md Component 7) to demonstrate findings tagged with all three previously-uncovered patterns end-to-end. All 6 example pipelines regenerated with pattern column populated. 5 non-multi-agent baselines produce zero non-`none` patterns (validates multi-agent gate predicate).

**Independent Test**: Run full pipeline on extended agentic-app. Verify threats.md has Pattern column populated for ≥3 patterns (Agent Collusion, Temporal Attack, Emergent Behavior); threat-report has Agentic Pattern Analysis section with ≥3 populated subsections; SARIF has `maestro-pattern:` tags. Verify 5 baselines produce identical structure with empty Pattern column (`—` for all rows).

- [X] T020 [US6] Extend `examples/agentic-app/architecture.md` with three new components per plan.md Component 7 Path 1 (1-2h budget): (a) Specialist Agent (second LLM Agent peer to existing LLM Agent Orchestrator); (b) Long-running Learning Loop (fine-tuning subsystem consuming Audit Logger output to retrain agents periodically); (c) Inter-agent Communication Channel (message bus or shared memory between Orchestrator and Specialist). Add explicit data flows: User → Specialist Agent, Specialist Agent ↔ Orchestrator (via channel), Orchestrator → Learning Loop, Audit Logger → Learning Loop, Learning Loop → both agents (model update flow). Verify the extended architecture description contains at least one of the multi-agent gate predicate keywords ("multi-agent", "swarm", "supervisor", "delegation", "agent mesh") to satisfy condition (c)
- [X] T021 [US6] Regenerate `examples/agentic-app/` full pipeline output: run threat-model command end-to-end, produce updated threats.md (with Pattern column populated for ≥3 previously-uncovered patterns), updated threat-report.md (with Agentic Pattern Analysis section), updated SARIF (with maestro-pattern tags), regenerated PDF security-report.pdf. Verify ≥1 net-new AGP-NN finding emitted per previously-uncovered pattern
- [X] T022 [P] [US6] Regenerate `examples/web-app/` pipeline output: verify zero non-`none` patterns (multi-agent gate predicate FALSE — single-agent architecture); verify Pattern column renders as `—` for all findings; verify Section 4b suppressed; verify Agentic Pattern Analysis section omitted from threat-report
- [X] T023 [P] [US6] Regenerate `examples/microservices/` pipeline output: verify zero non-`none` patterns (predicate FALSE — non-agentic architecture); same column/section verification as T022
- [X] T024 [P] [US6] Regenerate `examples/ascii-web-api/` pipeline output: verify zero non-`none` patterns (predicate FALSE); same column/section verification
- [X] T025 [P] [US6] Regenerate `examples/free-text-microservice/` pipeline output: verify zero non-`none` patterns (predicate FALSE); same column/section verification
- [X] T026 [P] [US6] Regenerate `examples/mermaid-agentic-app/` pipeline output: predicate may evaluate TRUE via condition (a) (≥2 agents in DFD) but rule table should NOT match any non-`none` pattern (no inter-agent communication, no persistent state, no multi-agent keywords). Verify zero non-`none` patterns; if any rule incorrectly matches, tighten the rule's match_conditions to exclude the false positive (per data-model.md Entity 4 worked examples; preserves backward compat for 5 baseline byte-identical PDFs)

**Checkpoint**: Extended agentic-app demonstrates ≥3 patterns end-to-end. All 6 examples regenerated. 5 baselines produce zero non-`none` patterns (multi-agent gate predicate validated).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: ADR-020 update, backward compatibility verification, full regression testing, and documentation.

- [X] T027 [P] Update `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md`: append a new Revision History entry referencing Phase 3 completion. Entry text: "**2026-04-16 (Feature 142)**: Phase 3 — Agentic Pattern Expansion. Adds the `agentic_pattern` enum field to the finding IR, surfacing the six canonical CSA MAESTRO agentic patterns. Pattern classification mechanism documented in ADR-026 (Hybrid Post-Hoc Synthesis — Phase 3.6 in the orchestrator pipeline). MAESTRO compliance umbrella (Issue #136) is now structurally complete: Phase 1 (Features 084 / 136), Phase 2 (Feature 141), Phase 3 (this feature), Phase 4 (Feature 143 — AIVSS posture ADR-024), Phase 5 (Feature 144 — NIST AI RMF posture ADR-025)." Cross-reference ADR-026
- [X] T028 Update `tests/scripts/test_backward_compatibility.py` to add: (a) pattern field default validation (pre-Feature-142 baseline findings parse with default `none` per FR-017); (b) multi-agent gate predicate enforcement assertion (zero non-`none` patterns in 5 baseline architectures); (c) preserve existing 5 baseline PDF byte-identical assertions under SOURCE_DATE_EPOCH=1700000000 per ADR-021
- [X] T029 Add CI verification task per architect LOW-3: assert zero edits to the 11 detection agent files. Add a new test in `tests/scripts/test_backward_compatibility.py` that runs `git diff --name-only main..HEAD -- '.claude/agents/tachi/spoofing.md' '.claude/agents/tachi/tampering.md' '.claude/agents/tachi/repudiation.md' '.claude/agents/tachi/info-disclosure.md' '.claude/agents/tachi/denial-of-service.md' '.claude/agents/tachi/privilege-escalation.md' '.claude/agents/tachi/prompt-injection.md' '.claude/agents/tachi/data-poisoning.md' '.claude/agents/tachi/model-theft.md' '.claude/agents/tachi/agent-autonomy.md' '.claude/agents/tachi/tool-abuse.md' '.claude/skills/tachi-*/references/detection-patterns.md'` and asserts empty output (zero-edit invariant per ADR-026 Decision section)
- [X] T030 Regenerate backward-compatibility PDF baselines for 5 examples without expected pattern changes (web-app, microservices, ascii-web-api, free-text-microservice, mermaid-agentic-app) under SOURCE_DATE_EPOCH=1700000000 per ADR-021; verify byte-identical against pre-feature baselines (preserves Constitution Principle III invariant)
- [X] T031 Run full pytest suite (`pytest tests/scripts/`): verify all 4 new test files pass (test_pattern_synthesis.py, test_pattern_classification_rules.py, test_pattern_extraction.py, test_finding_pattern_parser.py) AND existing tests still pass including updated test_backward_compatibility.py
- [X] T032 [P] Update `README.md` (or appropriate documentation index) to reference the new `agentic_pattern` field, the six canonical MAESTRO patterns, and ADR-026 mechanism decision; add reference to `maestro-agentic-patterns-shared.md` in the shared reference list
- [X] T033 Final validation: run pipeline on extended agentic-app and verify all 10 SCs from spec.md (SC-001 6/6 pattern coverage; SC-002 ≥80% multi-agent detection rate — measurement methodology per architect LOW-T33-1 (narrowed per P1 architect checkpoint ruling): the SC-002 denominator is "findings where the architecture has a topology indicator matching a rule's architectural preconditions" (not all findings in the architecture); count (a) total findings whose target component has a matching topology indicator and (b) actual non-`none` pattern assignments produced by the synthesis engine on those findings; ratio must be ≥80% averaged across the multi-agent test corpus (currently agentic-app extended; document caveat per PM LOW-3 that broader corpus needed for high-confidence measurement); SC-003 0% false positives on 4 single-agent baselines (web-app, microservices, ascii-web-api, free-text-microservice) — mermaid-agentic-app is an edge case where the multi-agent gate predicate evaluates TRUE (≥2 agentic components, inter-agent data flow via Orchestrator ↔ MCP Tool Server) and existing R-04/R-06 rules may surface patterns that are technically true positives under the rule definitions but deviate from the hand-edited baseline; this is a documented known limitation with R-04/R-06 tightening tracked as a follow-up rule-tuning feature; SC-004 5 PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000 (preserved regardless of Pattern column content because `scripts/extract-report-data.py` does not consume `agentic_pattern` and Typst templates do not render Section 4b); SC-005 determinism across runs; SC-006 coverage table completeness with 3 permitted Coverage Strength values; SC-007 SARIF tag fidelity; SC-008 <10s pipeline overhead — empirically measured via wall-clock timing on agentic-app extended per architect LOW-6, adjust budget to ≤15s if 10s proves too tight; SC-009 demonstration completeness; SC-010 field universality)

**Checkpoint**: All 33 tasks complete. ADR-020 updated. 5 baselines byte-identical. Full test suite green. SCs validated.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately. Three-track parallel (T001 + T002 + T003 + T004) per plan.md Wave 0
- **Foundational (Phase 2)**: Depends on Phase 1 — needs schema (T002) and shared reference (T001) to exist. T005 depends on T002 (schema field shape). T006 depends on T001 (shared reference path)
- **US1+US2 (Phase 3)**: Depends on Phase 2 — synthesis engine reads parser (T005) and orchestrator skeleton (T006). T007 → T008 → T009 → T010 sequential. T011 + T012 [P] alongside. T013 depends on T020 (extended agentic-app) so it sequences with Phase 5
- **US5+US3 (Phase 4)**: Depends on Phase 3 — output surfacing reads pattern field on findings. T014 [P], T015 [P], T016 [P], T017 (depends on existing maestro-layer tagging code path), T018 [P], T019 [P]
- **US6 (Phase 5)**: Depends on Phases 3 + 4 — end-to-end demonstration requires synthesis engine + output surfacing. T020 first (architecture extension prerequisite for T021); T022-T026 [P] (independent example directories)
- **Polish (Phase 6)**: Depends on Phase 5 — ADR update + regression after all examples regenerated. T027 [P], T028 → T029 → T030 → T031 → T033 (final validation last). T032 [P]

### Within Each Phase

- Tasks marked [P] can run in parallel within their phase
- Unmarked tasks within a phase are sequential
- Test file tasks (T011, T012, T018, T019) can run in parallel with implementation tasks in their phase if test files are independent

### Parallel Opportunities

- **Phase 1 (Wave 0)**: T001 + T002 + T003 + T004 fully parallel (4 different files; T001 = shared ref, T002 = schema, T003/T004 = orchestration ref). Three-track parallelism per plan.md Wave 0
- **Phase 3 (Wave 1)**: T011 + T012 [P] alongside T007-T010 (test files independent of orchestrator agent file)
- **Phase 4 (Wave 2)**: T014 + T015 + T016 + T018 + T019 fully parallel (5 different files; T017 sequences after grep-check of existing SARIF code path). Three-track parallelism per plan.md Wave 2 (templates / agent / SARIF)
- **Phase 5 (Wave 3)**: T022 + T023 + T024 + T025 + T026 fully parallel (5 independent example directories)
- **Phase 6 (Wave 4)**: T027 + T032 [P] alongside the sequential test pipeline T028 → T029 → T030 → T031

---

## Parallel Example: Phase 1 (Wave 0)

```bash
# Launch all setup tasks together (4 different files):
Task: "Author shared reference at .claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md"
Task: "Bump schemas/finding.yaml schema_version 1.3 → 1.4 with agentic_pattern enum"
Task: "Update .claude/skills/tachi-orchestration/references/dispatch-rules.md for Phase 3.6"
Task: "Update .claude/skills/tachi-orchestration/references/output-schemas.md with pattern field"
```

## Parallel Example: Phase 5 (Wave 3 — example regeneration)

```bash
# Launch all non-agentic-app example regenerations in parallel:
Task: "Regenerate examples/web-app/ pipeline output (verify zero non-none patterns)"
Task: "Regenerate examples/microservices/ pipeline output (verify zero non-none patterns)"
Task: "Regenerate examples/ascii-web-api/ pipeline output (verify zero non-none patterns)"
Task: "Regenerate examples/free-text-microservice/ pipeline output (verify zero non-none patterns)"
Task: "Regenerate examples/mermaid-agentic-app/ pipeline output (verify zero non-none patterns; tighten rules if any false positive)"
```

---

## Implementation Strategy

### MVP First (US1+US2 Only — Phases 1-3)

1. Complete Phase 1: Setup (Wave 0 — schema, shared reference, ADR-026 already exists)
2. Complete Phase 2: Foundational (parser + orchestrator skeleton)
3. Complete Phase 3: Synthesis Engine (Wave 1 — multi-agent gate + classification rules + net-new generation)
4. **STOP and VALIDATE**: Run synthesis on extended agentic-app, verify pattern assignment + AGP-NN findings
5. MVP deliverable: Phase 3.6 produces deterministic pattern assignments

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready (schema, shared ref, parser, orchestrator skeleton)
2. Phase 3 (US1+US2) → Synthesis engine validated (MVP!)
3. Phase 4 (US5+US3) → Output surfacing complete (threats.md + threat-report + SARIF)
4. Phase 5 (US6) → End-to-end demonstration on extended agentic-app
5. Phase 6 → ADR-020 update + tests + final regression

### Parallel Team Strategy

With multiple developers (per Feature 141 wave precedent):

1. Wave 0 (Phase 1): 4-track parallel — one developer per track (shared ref / schema / dispatch-rules / output-schemas)
2. Wave 1 (Phase 3): 1 developer on synthesis engine; 1 developer on test files (T011 + T012)
3. Wave 2 (Phase 4): 3-track parallel — templates (T014 threats.md) / agent (T015 threat-report) / SARIF (T017 orchestrator) + tests (T018 + T019) on a 4th developer
4. Wave 3 (Phase 5): 5-track parallel for example regeneration (T022-T026); architect leads T020 architecture extension; 1 developer on T021 agentic-app full regeneration
5. Wave 4 (Phase 6): 1-2 developers on ADR + tests + docs

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 33 |
| Phase 1 (Setup / Wave 0) | 4 tasks (T001-T004) |
| Phase 2 (Foundational) | 2 tasks (T005-T006) |
| Phase 3 (US1+US2 Synthesis Engine / Wave 1) | 7 tasks (T007-T013) |
| Phase 4 (US5+US3 Output Surfacing / Wave 2) | 6 tasks (T014-T019) |
| Phase 5 (US6 Example Demo / Wave 3) | 7 tasks (T020-T026) |
| Phase 6 (Polish / Wave 4) | 7 tasks (T027-T033) |
| User stories covered | 6 of 6 (US1+US2 in Phase 3; US3+US5 in Phase 4; US4 in Phase 1 [coverage table]; US6 in Phase 5) |
| Functional requirements covered | 20 of 20 (all FR-001 through FR-020) |
| Estimated effort | 5-8 days (matches Team-Lead PRD review estimate for Option C) |
| Parallel opportunities | 4-track parallel in Wave 0; 3-track parallel in Wave 2; 5-track parallel in Wave 3 |
| New test files | 4 (test_pattern_synthesis.py, test_pattern_classification_rules.py, test_pattern_extraction.py, test_finding_pattern_parser.py) |
| Updated test files | 1 (test_backward_compatibility.py) |
| New shared references | 1 (maestro-agentic-patterns-shared.md) |
| New ADRs | 1 (ADR-026 — already authored during /aod.project-plan) |
| Schema changes | 1 (finding.yaml 1.3 → 1.4 with agentic_pattern enum + AGP- id.pattern extension) |
| Architecture extensions | 1 (agentic-app: +Specialist Agent, +Learning Loop, +Inter-agent Channel) |
| Existing detection agents touched | 0 (Option C zero-edit invariant per ADR-026) |
| Cross-feature artifacts modified | 0 (attack-chains.md unchanged per FR-008) |
| New runtime dependencies | 0 (Python stdlib only per FR-020) |

## Notes

- [P] tasks = different files, no dependencies — safe to run in parallel
- [Story] label maps task to specific user story for traceability (US1 + US2 share Phase 3 due to common synthesis engine; US3 + US5 share Phase 4 due to common output surfacing)
- US4 (coverage mapping) is satisfied by T001 (shared reference Section 2 includes the coverage mapping table)
- ADR-026 already authored during /aod.project-plan; no separate task in tasks.md
- Pre-Feature-142 baseline test (T028) validates FR-017 backward compatibility
- Zero-edit invariant test (T029) validates ADR-026 Option C foundation
- 5 baseline byte-identical PDFs (T030) validates Constitution Principle III
- Three architect MEDIUM concerns (MED-1, MED-2, MED-3) addressed inline during /aod.project-plan; tasks reference the resolutions
- Eight architect LOW concerns and three PM LOW concerns folded into specific tasks: LOW-3 → T029, LOW-5 → T011 (synthetic single-agent fixture), LOW-6 → T033 (empirical wall-clock measurement), PM LOW-2 → T011 (idempotence test); remaining LOWs are advisory and tracked in plan.md notes
- Stop at any checkpoint to validate independently — particularly after Phase 3 (synthesis engine) and Phase 5 (end-to-end demo)
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence
