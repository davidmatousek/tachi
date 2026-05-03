---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-27
    status: APPROVED
    notes: "All 5 user stories covered, 17 FRs traceable, no scope creep. MVP (Phases 1-3) delivers core value. Recommend reproducibility spot-check during T029."
  architect_signoff:
    agent: architect
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "All plan deliverables covered. Medium: T023 should document security-severity semantic shift between threats.sarif and risk-scores.sarif. Low: minor task description clarity improvements."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible 5.5-9.5h across 6 waves. Low: Wave 4 overloaded (consider 4a/4b split during orchestration). Low: T014+T015 can run earlier in Wave 4."
---

# Tasks: Quantitative Risk Scoring

**Input**: Design documents from `/specs/035-quantitative-risk-scoring/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not explicitly requested in spec. Validation tasks in final phase cover acceptance criteria.

**Organization**: Tasks grouped by user story for independent implementation. All deliverables are markdown/YAML files (agent orchestration toolkit — no compiled code).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US5 from spec.md)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Schema Foundation)

**Purpose**: Create the scoring schema that all subsequent work depends on

- [X] T001 Create scored finding schema at schemas/risk-scoring.yaml with fields: cvss_base, cvss_vector, exploitability, scalability, reachability, composite_score, severity_band, risk_owner, remediation_sla, risk_disposition, review_date. Include category_defaults (8 CVSS vectors for STRIDE+AI categories), weights (0.35/0.30/0.15/0.20), and severity_bands aligned with schemas/output.yaml
- [X] T002 [P] Create risk-scorer agent skeleton at .claude/agents/tachi/risk-scorer.md with frontmatter, overview, and section stubs for: Threat Parsing, Trust Zone Extraction, CVSS Scoring, Exploitability Assessment, Scalability Assessment, Reachability Analysis, Composite Calculation, Governance Fields, Output Generation (markdown), Output Generation (SARIF)
- [X] T003 [P] Create risk-scores.md output template at templates/risk-scores.md with section stubs: frontmatter, Executive Summary, Scored Threat Table, Dimensional Breakdown, Governance Fields, Scoring Methodology

---

## Phase 2: Foundational (Threat Parsing + Template Structure)

**Purpose**: Core parsing capability that ALL user stories depend on — MUST complete before story work begins

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Write Threat Parsing section in .claude/agents/tachi/risk-scorer.md — define parsing rules for threats.md (extract findings from STRIDE Tables Sections 3-4, AI Threat Tables, and Correlated Findings Section 4a). Specify field extraction: id, component, category, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type. Include input precedence rule: threats.md canonical, threats.sarif fallback
- [X] T005 [P] Write SARIF Parsing section in .claude/agents/tachi/risk-scorer.md — define parsing rules for threats.sarif (extract results array, preserve partialFingerprints, extract rule metadata). Map SARIF fields to finding IR fields
- [X] T006 [P] Create risk-scores.sarif output template at templates/risk-scores.sarif with SARIF 2.1.0 skeleton: $schema, version, runs array with tool.driver (name, version, rules with extended properties), results array with property bag placeholders for scoring dimensions and governance fields. Preserve taxonomy declarations pattern from templates/threats.sarif

**Checkpoint**: Parsing foundation ready — agent can read threat model input in both formats

---

## Phase 3: User Story 1 — Quantitative Threat Scoring (Priority: P0) MVP

**Goal**: Each threat finding receives four dimensional scores (CVSS 3.1, exploitability, scalability, reachability) and a weighted composite score on a 0.0-10.0 scale

**Independent Test**: Run scoring agent against examples/agentic-app/sample-report/threats.md and verify each finding has 4 dimension scores + composite + CVSS vector string

### Implementation for User Story 1

- [X] T007 [US1] Write CVSS 3.1 Base Scoring section in .claude/agents/tachi/risk-scorer.md — define scoring methodology: load category defaults from schemas/risk-scoring.yaml, refine per-threat based on description analysis (attack vector, attack complexity, privileges required, user interaction, scope, confidentiality, integrity, availability). Include AI-specific guidance for agentic and llm categories. Output: cvss_base (0.0-10.0) and cvss_vector string per finding
- [X] T008 [P] [US1] Write Exploitability Assessment section in .claude/agents/tachi/risk-scorer.md — define four sub-dimensions: known exploit/technique existence (0-10), attack complexity (0-10), tooling availability (0-10), skill level required (0-10). Include AI-specific guidance: prompt injection = trivially exploitable, model poisoning = high skill. Output: exploitability score (0.0-10.0) per finding
- [X] T009 [P] [US1] Write Scalability Assessment section in .claude/agents/tachi/risk-scorer.md — define four sub-dimensions: scriptability (0-10), target scope (0-10), resource requirements (0-10), detection difficulty (0-10). Output: scalability score (0.0-10.0) per finding
- [X] T010 [US1] Write Composite Calculation section in .claude/agents/tachi/risk-scorer.md — define weighted formula: Composite = (0.35 x CVSS) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability). Map composite to severity band per schemas/risk-scoring.yaml. Note: reachability defaults to 5.0 until US4 implementation; this enables US1 to be independently testable. Include correlation group handling: score primaries, peers inherit

**Checkpoint**: Agent can score all four dimensions for any threat finding and produce a composite score

---

## Phase 4: User Story 2 — Risk Governance Fields (Priority: P0)

**Goal**: Each scored threat has governance metadata (owner, SLA, disposition, review date) for remediation tracking

**Independent Test**: Verify all scored findings have governance fields populated with correct severity-driven defaults

### Implementation for User Story 2

- [X] T011 [US2] Write Governance Fields section in .claude/agents/tachi/risk-scorer.md — define field generation rules: risk_owner defaults to "Unassigned", remediation_sla mapped from severity band (Critical=24h, High=7d, Medium=30d, Low=90d), risk_disposition mapped from severity (Critical/High=Mitigate, Medium/Low=Review), review_date calculated as scoring date + SLA duration. Reference severity_bands from schemas/risk-scoring.yaml

**Checkpoint**: Every scored finding has all four governance fields populated

---

## Phase 5: User Story 3 — Dual Output Formats (Priority: P0)

**Goal**: Scored findings rendered in both human-readable risk-scores.md and machine-readable risk-scores.sarif with consistent data

**Independent Test**: Generate both outputs; verify risk-scores.md contains sorted scored table and risk-scores.sarif validates against SARIF 2.1.0 schema

### Implementation for User Story 3

- [X] T012 [US3] Write Markdown Output Generation section in .claude/agents/tachi/risk-scorer.md — define output structure: executive summary (total by severity band, highest-risk component), scored threat table sorted by composite descending (columns: ID, Component, Threat, CVSS, Exploitability, Scalability, Reachability, Composite, Severity, SLA, Disposition), dimensional breakdown per finding. Reference templates/risk-scores.md for structure
- [X] T013 [US3] Write SARIF Output Generation section in .claude/agents/tachi/risk-scorer.md — define SARIF generation rules: set security-severity to composite score as numeric string per finding, add property bag (cvss-base-score, cvss-vector, exploitability, scalability, reachability, composite-weights, risk-owner, remediation-sla, risk-disposition, review-date). Preserve findingId/v1 and primaryLocationLineHash from source threats.sarif. Preserve taxonomies (run.taxonomies[], supportedTaxonomies[], rule relationships[]). Set rule-level security-severity to max composite among that rule's findings. Reference templates/risk-scores.sarif for structure
- [X] T014 [P] [US3] Populate risk-scores.md template at templates/risk-scores.md with complete section content: frontmatter format, executive summary layout, scored threat table column definitions, dimensional breakdown format, governance fields display, methodology section placeholder
- [X] T015 [P] [US3] Populate risk-scores.sarif template at templates/risk-scores.sarif with complete SARIF structure: tool.driver with risk-scorer name and rule definitions for 8 categories, results array schema with full property bag, taxonomy preservation pattern, fingerprint fields

**Checkpoint**: Agent can produce both output formats with consistent scores and governance fields

---

## Phase 6: User Story 4 — Reachability-Aware Scoring (Priority: P1)

**Goal**: Reachability scores adjusted based on component trust zone exposure, differentiating internet-facing from well-protected components

**Independent Test**: Run scoring against a threat model with trust boundaries; verify Untrusted zone components score reachability 8.0-10.0 and Trusted zone components score 1.0-4.0

### Implementation for User Story 4

- [X] T016 [US4] Write Trust Zone Extraction section in .claude/agents/tachi/risk-scorer.md — define parsing rules for threats.md Section 2 trust zone table: extract zone names, trust levels (Untrusted/Semi-Trusted/Trusted), component-to-zone assignments. Build component-to-zone mapping dictionary
- [X] T017 [US4] Write Reachability Scoring section in .claude/agents/tachi/risk-scorer.md — define zone-to-reachability baseline mapping: Untrusted/External=8.0-10.0, Semi-Trusted/Application=4.0-7.0, Trusted/Internal=1.0-4.0. Include zone name fuzzy matching for non-standard naming. Apply default 5.0 with warning when no trust data available. Include supplementary architecture.md parsing: adjust baseline with authentication barriers (-1.5 per layer), network segmentation (-1.0 per boundary)
- [X] T018 [US4] Update Composite Calculation section in .claude/agents/tachi/risk-scorer.md — replace default reachability (5.0) with trust-zone-derived reachability scores from T017. Ensure composite formula uses actual reachability when available, falls back to 5.0 when not

**Checkpoint**: Reachability scores reflect actual architecture trust boundaries

---

## Phase 7: User Story 5 — Scoring Methodology Documentation (Priority: P1)

**Goal**: risk-scores.md includes a clear methodology section explaining scoring dimensions, weights, and formula

**Independent Test**: Verify methodology section explains all four dimensions, documents weights, and includes the composite formula and severity band mapping

### Implementation for User Story 5

- [X] T019 [US5] Write Methodology section content in templates/risk-scores.md — add section explaining: four scoring dimensions with descriptions of what each measures, default weights with rationale (CVSS 35%, Exploitability 30%, Scalability 15%, Reachability 20%), composite formula, severity band mapping table, data sources (threats.md trust zones, architecture.md), reproducibility note (+/- 0.5 tolerance)

**Checkpoint**: Output includes transparent scoring methodology for stakeholder review

---

## Phase 8: Command + Integration

**Purpose**: Wire the agent into the command layer and distribution adapters

- [X] T020 Create /risk-score command definition at .claude/commands/risk-score.md — define: frontmatter with description, flag parsing (input file path, --output-dir), validation (check threats.md or threats.sarif exists, check tachi agents installed), input precedence (threats.md canonical, threats.sarif fallback), agent invocation of risk-scorer, output summary (severity band distribution, file paths, next steps). Follow .claude/commands/threat-model.md pattern
- [X] T021 [P] Copy .claude/agents/tachi/risk-scorer.md to adapters/claude-code/agents/risk-scorer.md for distribution
- [X] T022 [P] Copy .claude/commands/risk-score.md to adapters/claude-code/commands/risk-score.md for distribution
- [X] T023 [P] Update adapters/claude-code/agents/references/sarif-generation.md — add "Risk Scoring SARIF Extension" section documenting: extended property bag schema for risk-scores.sarif, security-severity as composite score (numeric string), fingerprint preservation rules, taxonomy preservation, rule-level vs result-level security-severity
- [X] T024 Update schemas/finding.yaml — add optional scored_finding extension reference block at end of file pointing to schemas/risk-scoring.yaml for scoring field definitions. Preserve backward compatibility (extension is optional)

---

## Phase 9: Validation + Example Output

**Purpose**: Validate against success criteria and produce reference output

- [X] T025 Generate example risk-scores.md by running /risk-score against examples/agentic-app/sample-report/threats.md — save output to examples/agentic-app/sample-report/risk-scores.md. Verify: executive summary present, scored table sorted by composite descending, all governance fields populated, methodology section included
- [X] T026 [P] Generate example risk-scores.sarif by running /risk-score against examples/agentic-app/sample-report/threats.md — save output to examples/agentic-app/sample-report/risk-scores.sarif. Verify: validates against SARIF 2.1.0 schema, security-severity is numeric string per finding, fingerprints preserved from threats.sarif, taxonomies preserved
- [X] T027 Verify score differentiation (SC-001): compare composite scores for findings that had identical qualitative ratings in threats.md — confirm >= 80% receive different composite scores (exclude correlated peer groups from measurement)
- [X] T028 Verify dual-format parity (SC-005): compare all scores and governance fields between risk-scores.md and risk-scores.sarif — confirm 100% consistency
- [X] T029 Run end-to-end /risk-score command validation: execute full command flow (flag parsing → validation → scoring → output → summary) against example input and verify completion summary displays correct severity band distribution

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (schema + agent skeleton must exist) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 (parsing foundation). No dependencies on other stories
- **US2 (Phase 4)**: Depends on Phase 3 (needs composite scores to map governance fields)
- **US3 (Phase 5)**: Depends on Phase 3 + Phase 4 (needs scored findings with governance fields to render)
- **US4 (Phase 6)**: Can start after Phase 2 (independent reachability scoring). Integrates into composite in T018
- **US5 (Phase 7)**: Can start after Phase 1 (template exists). No code dependencies
- **Command + Integration (Phase 8)**: Depends on Phases 3-7 (agent must be complete before command wraps it)
- **Validation (Phase 9)**: Depends on Phase 8 (command must be functional for end-to-end testing)

### User Story Dependencies

- **US1 (P0)**: Start after Foundational — independent, core scoring
- **US2 (P0)**: Start after US1 — needs severity bands from composite scores
- **US3 (P0)**: Start after US2 — needs governance fields for complete output
- **US4 (P1)**: Start after Foundational — independent reachability work, integrates into composite after US1
- **US5 (P1)**: Start after Setup — template content only, no code dependency

### Parallel Opportunities

- T002 + T003 in Phase 1 (different files)
- T005 + T006 in Phase 2 (different files/sections)
- T008 + T009 in Phase 3 (independent scoring dimensions)
- T014 + T015 in Phase 5 (different template files)
- T021 + T022 + T023 in Phase 8 (independent adapter copies)
- T025 + T026 in Phase 9 (different output formats)
- US4 (Phase 6) and US5 (Phase 7) can run in parallel with US2-US3

---

## Parallel Example: Wave Execution

```
Wave 1 (Phase 1 — Setup):
  T001: schemas/risk-scoring.yaml
  T002: .claude/agents/tachi/risk-scorer.md (skeleton)     [P]
  T003: templates/risk-scores.md (stubs)                    [P]

Wave 2 (Phase 2 — Foundation):
  T004: Agent parsing section (threats.md)
  T005: Agent parsing section (threats.sarif)               [P]
  T006: templates/risk-scores.sarif                         [P]

Wave 3 (Phase 3 — US1 Core Scoring):
  T007: CVSS scoring section
  T008: Exploitability section                              [P]
  T009: Scalability section                                 [P]
  T010: Composite calculation

Wave 4 (Phases 4+5+6+7 — US2/US3/US4/US5):
  T011: Governance fields (US2)
  T016: Trust zone extraction (US4)                         [P]
  T019: Methodology content (US5)                           [P]
  → then T012+T013 (US3 output gen, depends on T011)
  → then T014+T015 (US3 templates)                          [P]
  → then T017+T018 (US4 reachability scoring)

Wave 5 (Phase 8 — Command + Integration):
  T020: Command definition
  T021+T022+T023: Adapter copies + SARIF ref update         [P]
  T024: finding.yaml update

Wave 6 (Phase 9 — Validation):
  T025+T026: Example output generation                      [P]
  T027: Score differentiation check
  T028: Dual-format parity check
  T029: End-to-end command validation
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (schema + skeleton)
2. Complete Phase 2: Foundation (parsing)
3. Complete Phase 3: US1 (four-dimension scoring + composite)
4. **STOP and VALIDATE**: Score example threat model, verify 4 dimensions per finding
5. Core value delivered — quantitative scores differentiate previously-identical threats

### Incremental Delivery

1. Setup + Foundation → parsing ready
2. Add US1 → scoring works with default reachability (5.0) → **MVP**
3. Add US2 → governance fields attach to every scored finding
4. Add US3 → dual output generation (risk-scores.md + risk-scores.sarif)
5. Add US4 → reachability uses actual trust boundaries
6. Add US5 → methodology section documents scoring approach
7. Command + Integration → /risk-score command wraps everything
8. Validation → verify all success criteria

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 29 |
| Phase 1 (Setup) | 3 tasks |
| Phase 2 (Foundation) | 3 tasks |
| Phase 3 (US1 - Scoring) | 4 tasks |
| Phase 4 (US2 - Governance) | 1 task |
| Phase 5 (US3 - Output) | 4 tasks |
| Phase 6 (US4 - Reachability) | 3 tasks |
| Phase 7 (US5 - Methodology) | 1 task |
| Phase 8 (Command) | 5 tasks |
| Phase 9 (Validation) | 5 tasks |
| Parallel opportunities | 6 wave groups with [P] parallelism |
| Estimated waves | 6 execution waves |
| MVP scope | Phases 1-3 (10 tasks) |

## Notes

- All deliverables are markdown/YAML files — no compilation, no build system
- Agent file (.claude/agents/tachi/risk-scorer.md) is the primary deliverable containing scoring logic
- Template files define output structure; agent file defines how to populate them
- Adapter copies are identical to source files (straight copy for distribution)
- Validation tasks require running the actual /risk-score command against example data
