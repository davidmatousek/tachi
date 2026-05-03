---
prd_reference: docs/product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-16
    status: APPROVED
    notes: "8/8 PRD FRs traced into 20 spec FRs, 6/6 PRD user stories preserved 1:1 with priorities intact (P0/P0/P1/P1/P1/P0), 22 acceptance scenarios. Mechanism-deferral discipline exemplary: all 4 FR-2 options (A/B/C/D) preserved without pre-judgment, schema-bump magnitude and section-numbering deferred to project ADR / implementation. Multi-agent gate predicate (3 OR conditions), pattern data placement invariant (finding IR + threats.md only — does NOT extend attack-chains.md), backward-compat (5 baselines byte-identical under SOURCE_DATE_EPOCH=1700000000 with agentic-app exclusion) all encoded at FR + AC + SC + Key Entity layers. 2 LOW polish items: LOW-1 (Edge Case 9 Path 3 wording) addressed inline; LOW-2 (FR-001/FR-002 consolidation) left per PM's 'current shape is acceptable' guidance."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Phase 3 — Agentic Threat Pattern Expansion

**Feature Branch**: `142-maestro-agentic-pattern-expansion`
**Created**: 2026-04-16
**Status**: Draft
**PRD Reference**: docs/product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md
**Input**: PRD 142 — Surface the six canonical MAESTRO cross-cutting agentic threat patterns (Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition) as named, filterable finding categories so cross-cutting agentic risks that don't fit cleanly into STRIDE-per-element become first-class output.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent Collusion as an Explicit Filter (Priority: P0)

A security engineer reviewing tachi threat model output on a multi-agent system can filter findings by an "Agent Collusion" pattern category. Coordinated multi-agent attack findings (e.g., two compromised agents jointly exfiltrating data through a shared communication channel) are tagged distinctly from single-agent exploits. The pattern column appears in the threats.md findings table and the SARIF output exposes the pattern as a tag.

**Why this priority**: Agent Collusion is one of three previously-uncovered canonical patterns. Without an explicit category, coordinated attacks are buried inside generic tool-abuse findings and cannot be prioritized for remediation strategies (coordination throttles, inter-agent rate limits) that differ from per-component controls.

**Independent Test**: Run the pipeline on a multi-agent architecture with two cooperating agents and a shared communication channel. Verify findings table shows an "Agentic Pattern" column with `agent_collusion` populated for at least one finding, and SARIF output includes `maestro-pattern:agent_collusion` in the result tags.

**Acceptance Scenarios**:

1. **Given** an architecture with two or more cooperating agents and at least one shared communication channel between them, **When** the pipeline runs, **Then** at least one finding is tagged `agentic_pattern: agent_collusion` reflecting coordinated multi-agent attack potential.
2. **Given** the threats.md output, **When** viewing the findings table, **Then** an Agentic Pattern column appears between the Category and Component columns, displaying the pattern enum value or `—` for findings tagged `none`.
3. **Given** a single-agent architecture (no second cooperating agent, no inter-agent data flow), **When** the pipeline runs, **Then** zero findings receive `agent_collusion` (multi-agent gate predicate prevents false positives).
4. **Given** a finding tagged `agent_collusion`, **When** examining the SARIF output, **Then** `result.properties.tags` includes `maestro-pattern:agent_collusion` matching the existing `maestro-layer:` tagging convention.

---

### User Story 2 - Temporal Attack Detection (Priority: P0)

A threat modeler analyzing a long-running agentic system (one with persistent memory, a fine-tuning loop, or a learning pipeline) sees explicit Temporal Attack findings — sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation. These findings are invisible to point-in-time STRIDE analysis because they require persistent state to manifest. The threat description explicitly identifies the temporal vector.

**Why this priority**: Temporal Attacks are a canonical CSA MAESTRO pattern with no dedicated home in any existing tachi agent. Architectures with persistent state are the highest-risk Temporal Attack surface, and shipping MAESTRO support without this category leaves a structural detection gap that adopters will notice immediately.

**Independent Test**: Run the pipeline on an architecture with a fine-tuning pipeline OR persistent agent memory OR a long-running learning loop. Verify at least one finding is tagged `agentic_pattern: temporal_attack` and the threat description identifies the specific temporal vector (sleeper agent, gradual corruption, seasonal exploitation, or time-delayed activation).

**Acceptance Scenarios**:

1. **Given** an architecture containing at least one of: a fine-tuning pipeline component, a persistent agent memory store, or a long-running learning loop, **When** the pipeline runs, **Then** at least one finding is generated tagged `agentic_pattern: temporal_attack`.
2. **Given** a Temporal Attack finding, **When** reading the threat description, **Then** it explicitly names the temporal vector class (sleeper agent activation, gradual corruption, seasonal exploitation, or time-delayed activation).
3. **Given** a stateless single-shot inference architecture (no persistent memory, no fine-tuning, no learning loop), **When** the pipeline runs, **Then** zero Temporal Attack findings are generated.

---

### User Story 3 - Emergent Behavior Risks Called Out in Threat Report (Priority: P1)

A CISO reviewing the PDF security assessment for board communication sees a dedicated "Agentic Pattern Analysis" section that explicitly enumerates Emergent Behavior risks. The section breaks down findings by canonical pattern category, with a brief narrative on the emergent behavior class and recommended monitoring controls (fail-safe shutdowns, bounded action scopes, behavioral baselining). Without this section, the risk class is invisible to budget allocation decisions.

**Why this priority**: The PDF is the primary deliverable for executive stakeholders. Emergent Behavior calls for a different control class (monitoring + bounded scopes) than per-component controls, and budget allocation requires the named risk category to appear in the report.

**Independent Test**: Run the pipeline on a multi-agent architecture and generate the PDF security report. Verify the report includes an "Agentic Pattern Analysis" section that enumerates findings by pattern with a populated Emergent Behavior subsection containing 100-200 word narrative and recommended monitoring controls.

**Acceptance Scenarios**:

1. **Given** a multi-agent architecture, **When** the threat report is generated, **Then** an "Agentic Pattern Analysis" section appears, placed after the Cross-Layer Attack Chains section (Feature 141) and before the Findings Detail section.
2. **Given** Critical or High findings tagged `emergent_behavior`, **When** reading the corresponding subsection, **Then** it includes (a) the canonical pattern definition (1 sentence), (b) Critical/High/Medium/Low finding count, (c) 100-200 word narrative describing manifestation in this architecture, and (d) impacted finding IDs with cross-references.
3. **Given** an architecture with no emergent behavior risk (no Emergent Behavior findings detected), **When** viewing the section, **Then** the Emergent Behavior subsection is suppressed (zero-finding subsections are hidden, not shown empty).
4. **Given** an architecture with no pattern findings of any kind, **When** the threat report is generated, **Then** the Agentic Pattern Analysis section is omitted entirely.

---

### User Story 4 - Coverage Mapping Documentation (Priority: P1)

A tachi adopter evaluating the toolkit's MAESTRO completeness reads a coverage mapping table showing which existing AI threat agents (and STRIDE agents, where relevant) cover which canonical MAESTRO patterns today, and which patterns require new detection. The table answers "which of the six canonical MAESTRO patterns does tachi detect, and through which agent?" without ambiguity. Coverage assessments are honest — overclaiming undermines the gap analysis purpose.

**Why this priority**: Adopters comparing tachi against manual MAESTRO threat modeling deliverables need a one-page answer to "what does tachi cover." The mapping table is also load-bearing for future feature decisions — it surfaces gaps that warrant follow-up features and prevents redundant detection work.

**Independent Test**: Open the shared reference file `maestro-agentic-patterns-shared.md` and locate the coverage mapping table. Verify it lists all six canonical patterns, maps each to one or more existing agents (or marks "None — Coverage Required"), and uses the constrained Coverage Strength values (Full / Partial / None — Coverage Required).

**Acceptance Scenarios**:

1. **Given** the shared reference `maestro-agentic-patterns-shared.md`, **When** viewing the coverage mapping table, **Then** all six canonical patterns appear in rows with three columns: Currently Covered By, Coverage Strength, and Gap.
2. **Given** the Coverage Strength column, **When** reading any row, **Then** it contains one of three values: Full, Partial, or None — Coverage Required (no other values).
3. **Given** any row marked Partial, **When** reading the Gap column, **Then** it includes a 1-sentence justification naming what the existing agent misses (preventing overclaiming).
4. **Given** a future tachi release that adds a new AI agent, **When** the new feature ships, **Then** the coverage mapping table is updated as part of that feature's deliverables (governance precedent established).

---

### User Story 5 - Pattern-Tagged Output for Downstream Tooling (Priority: P1)

A MAESTRO practitioner integrating tachi output with downstream tooling (custom dashboards, SOAR playbooks, ticket routing) can rely on the `agentic_pattern` field being present and well-defined on every finding. The IR field is required (default `none` for findings without pattern relevance) so consumers never need null-safety logic. SARIF output exposes the pattern as a tag for tools that consume SARIF natively.

**Why this priority**: Downstream tooling integration is the bridge between tachi as a one-shot tool and tachi as a pipeline component. A required field with a `none` default makes integration deterministic — consumers can always read the field without conditional logic.

**Independent Test**: Run the pipeline on any architecture (multi-agent or single-agent). Verify every finding in threats.md has a non-empty Pattern column value (either a canonical pattern name, `none`, or `multiple`), and verify the SARIF output preserves the value as a tag for non-`none` patterns.

**Acceptance Scenarios**:

1. **Given** any tachi finding produced by the pipeline, **When** examining the finding IR, **Then** the `agentic_pattern` field is populated with one of: a canonical pattern name (six values), `none`, or `multiple` (no missing/null values).
2. **Given** a finding that exemplifies two or more patterns equally (rare), **When** examining the IR, **Then** `agentic_pattern: multiple` is set and the threat description identifies which patterns apply.
3. **Given** the SARIF output, **When** examining a result with a non-`none` pattern, **Then** `result.properties.tags` includes `maestro-pattern:<pattern_name>` formatted in lowercase with colon separator (matching the existing `maestro-layer:` convention exactly).
4. **Given** a finding with `agentic_pattern: none`, **When** examining the SARIF output, **Then** no `maestro-pattern:` tag is present (avoiding tag noise on non-pattern findings).

---

### User Story 6 - End-to-End Multi-Agent Example (Priority: P0)

A prospective tachi adopter inspecting the example library can run the pipeline on at least one multi-agent example and see findings tagged with all three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack) in the artifact, threat report, and SARIF outputs. The example demonstrates the capability end-to-end and serves as the reference architecture for new users learning the feature.

**Why this priority**: Examples are the primary evaluation mechanism for adopters and the authoritative correctness reference for the feature. Without a working end-to-end example, adopters cannot validate the capability before committing to adoption, and the team cannot regression-test the feature against a known-good baseline.

**Independent Test**: Run the pipeline on the designated multi-agent example. Verify the output includes findings tagged with `agent_collusion`, `emergent_behavior`, and `temporal_attack` (at minimum), the threat report includes a populated Agentic Pattern Analysis section with at least three pattern subsections, and the SARIF includes corresponding pattern tags.

**Acceptance Scenarios**:

1. **Given** the examples directory after Feature 142 ships, **When** inspecting the designated multi-agent example, **Then** its threats.md output includes findings tagged with all three previously-uncovered patterns: Agent Collusion, Emergent Behavior, and Temporal Attack.
2. **Given** the example PDF is regenerated, **When** viewing the threat report, **Then** the Agentic Pattern Analysis section includes at least three populated pattern subsections (one per previously-uncovered pattern).
3. **Given** a new user runs the pipeline on the example, **When** comparing pattern assignments across runs, **Then** identical pattern assignments are produced (deterministic classification per ADR-021).
4. **Given** the 5 non-multi-agent baseline examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice), **When** the pipeline is regenerated after Feature 142 ships, **Then** zero new pattern findings appear in any of them under the multi-agent gate predicate.

---

### Edge Cases

- What happens when a finding fits no canonical pattern? `agentic_pattern: none` is set explicitly — the field is required for all findings post-Feature-142, so `none` is the sentinel value (not missing/null).
- What happens when a finding fits two or more patterns equally? `agentic_pattern: multiple` is set and the threat description identifies which patterns apply. Analysts SHOULD prefer the dominant pattern when one exists; `multiple` is reserved for genuinely co-equal cases.
- What happens when the architecture lacks any multi-agent indicators? The multi-agent gate predicate (≥2 agentic/llm components OR ≥1 inter-component data flow between agentic components OR explicit multi-agent coordination keywords) prevents any pattern other than `none` from being assigned. All findings receive `agentic_pattern: none`.
- What happens when a single-agent architecture contains a fine-tuning pipeline? Temporal Attack patterns require persistent state, but the multi-agent gate predicate would fail (no second agent). Outcome: no temporal_attack finding is generated. This is a deliberate scope boundary — Temporal Attacks against single-agent systems are out of scope for Feature 142 and may warrant a follow-up feature.
- What happens when a finding's target component is `Unclassified` (no MAESTRO layer assigned)? The pattern field is independent of `maestro_layer` — Unclassified components can still receive a pattern if the multi-agent gate predicate is satisfied at the architecture level. This preserves the independence invariant from ADR-020 Phase 2.
- What happens when both pattern grouping AND cross-layer chain grouping apply to the same finding? The finding appears in both — pattern membership and chain membership are independent grouping mechanisms (consistent with the Section 4a / Phase 3.5 independence invariant). Cross-references are surfaced narratively in the threat report; the artifacts (threats.md and attack-chains.md) remain independent.
- What happens when the threat report has no pattern findings? The Agentic Pattern Analysis section is omitted entirely (not rendered empty).
- What happens when one pattern subsection has zero findings but another has many? Zero-finding subsections are suppressed; populated subsections are rendered. Subsection ordering is by maximum severity descending, then finding count descending.
- What happens when the chosen mechanism (per the project ADR) is post-hoc synthesis and synthesis would generate a net-new pattern finding for an uncovered pattern? Net-new finding generation MUST be deterministic (rule-based, not LLM-interpretive). If determinism cannot be guaranteed for a specific pattern's detection, that pattern is deferred to a follow-up feature with explicit deferral narrative recorded in the project plan (analogous to FR-015 Path 3 deferral, applied at the detection-mechanism layer rather than the example-architecture layer).
- What happens when a future feature adds a dedicated detection mechanism (e.g., a new agent) for a threat that overlaps with a canonical MAESTRO pattern name? The `agentic_pattern` field is a classification overlay — it does not preempt dedicated detection mechanisms for specific OWASP threats (e.g., ASI07 insecure inter-agent communication, ASI09 human-agent trust exploitation, LLM05 improper output handling). Pattern tagging and dedicated detection are independent mechanisms and may coexist: a finding may carry both a specific detection attribution and a MAESTRO pattern tag.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Pipeline MUST produce a shared reference file documenting each of the six canonical CSA MAESTRO agentic patterns (Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition) with definition, 2-3 representative examples, detection criteria, and existing-agent coverage assessment.
- **FR-002**: Shared reference MUST include a coverage mapping table with one row per canonical pattern and three columns: Currently Covered By, Coverage Strength, and Gap. Coverage Strength values MUST be restricted to Full, Partial, or None — Coverage Required (no other values, preventing overclaiming). Partial assessments MUST include a 1-sentence Gap justification naming what the existing agent misses.
- **FR-003**: Finding schema MUST be extended with an `agentic_pattern` enum field accepting eight values: the six canonical pattern names (`agent_collusion`, `emergent_behavior`, `temporal_attack`, `trust_exploitation`, `communication_vulnerability`, `resource_competition`), plus `none` and `multiple`. Default value: `none`. The field MUST be present on every finding produced after Feature 142 ships.
- **FR-004**: Finding schema version MUST bump from 1.3 to 1.4. The schema versioning rule MUST be documented to extend the Feature 136 enum-VALUE-rename minor-bump precedent to cover NEW enum-typed field additions, OR justify a major bump if the architect determines that adding a required field warrants major-version semantics. The decision MUST be recorded in the project ADR documenting the pattern classification mechanism.
- **FR-005**: Pattern classification MUST be deterministic — identical inputs MUST produce identical pattern assignments on every pipeline run (consistent with ADR-021). No LLM-judgment-based pattern classification is acceptable, regardless of which mechanism the project ADR selects.
- **FR-006**: Multi-agent gate predicate MUST be enforced at the pattern classification step: no `agentic_pattern` value other than `none` may be assigned unless the architecture exhibits at least one of (a) two or more components classified as `agentic` or `llm` category in the dispatch keywords, (b) at least one inter-component data flow between two agentic components, OR (c) explicit multi-agent coordination keywords (multi-agent, swarm, supervisor, delegation, agent mesh) in the architecture description. The gate MUST apply regardless of which mechanism the project ADR selects.
- **FR-007**: A project ADR (next available public ADR number, assigned at merge) MUST be authored documenting the pattern classification mechanism decision. The ADR MUST evaluate at least four candidate mechanisms — extend existing AI agents, add a new cross-cutting agent, post-hoc synthesis after deduplication, and orchestrator-side classification at finding emission — across three axes: pattern semantics ownership, schema write-back location, and existing-agent regression footprint. The ADR MUST select one option with full justification.
- **FR-008**: Pattern data placement MUST be confined to the finding IR and the threats.md output. The `agentic_pattern` field MUST NOT modify or extend the `attack-chains.md` artifact (Feature 141). The threat report agent MAY cross-reference chain membership in pattern narratives, but the two artifacts MUST remain independent.
- **FR-009**: threats.md output MUST be extended with an Agentic Pattern column placed between the Category and Component columns. Empty pattern values (where `agentic_pattern: none`) MUST display as `—`. The column MUST always render across all architectures (consistent table shape).
- **FR-010**: threats.md output MUST be extended with a conditional Section "Findings by Agentic Pattern" that groups findings by pattern when at least one finding has a non-`none` pattern. The section MUST be suppressed entirely when all findings have `agentic_pattern: none`.
- **FR-011**: Threat report MUST include a conditional "Agentic Pattern Analysis" section placed after the Cross-Layer Attack Chains section (Feature 141) and before the Findings Detail section. The section number MUST NOT be hardcoded — implementation determines the section number from the current count at code time.
- **FR-012**: Each pattern subsection in the Agentic Pattern Analysis MUST contain (a) the pattern name and 1-sentence canonical definition (sourced from the shared reference), (b) Critical/High/Medium/Low finding counts, (c) a 100-200 word narrative describing the pattern's manifestation in this architecture, and (d) impacted finding IDs with cross-references.
- **FR-013**: Pattern subsections MUST be ordered by maximum severity descending, then by finding count descending. Zero-finding subsections MUST be suppressed (not rendered empty). The full Agentic Pattern Analysis section MUST be omitted when no findings carry a non-`none` pattern.
- **FR-014**: SARIF output MUST propagate the `agentic_pattern` value as a tag on each result with a non-`none` pattern. The tag format MUST be `maestro-pattern:<pattern_name>` (lowercase, colon-separator, exact match to the existing `maestro-layer:<L#>` convention from Feature 084). Findings with `agentic_pattern: none` MUST NOT receive a pattern tag (avoiding tag noise).
- **FR-015**: At least one multi-agent example architecture MUST demonstrate findings tagged with each of the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack) end-to-end across the artifact, threat report, and SARIF outputs. The choice between extending the existing `agentic-app` example, building a new purpose-built example, or deferring un-demonstrable patterns MUST be recorded in the project plan.
- **FR-016**: All 6 example pipeline outputs MUST be regenerated. The 5 non-multi-agent baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) MUST produce zero new pattern findings (validated under the multi-agent gate predicate). The PDF outputs of those 5 baselines MUST be byte-identical under SOURCE_DATE_EPOCH=1700000000 (per ADR-021).
- **FR-017**: Pre-Feature-142 baseline findings (which lack the `agentic_pattern` field) MUST parse correctly when consumed by Feature 142 parsers and MUST default to `agentic_pattern: none`. A baseline parser regression test MUST validate this behavior.
- **FR-018**: ADR-020 MUST receive a Revision History entry referencing Phase 3 completion. The reference MUST link to the project ADR documenting the pattern classification mechanism and to the Feature 142 PRD.
- **FR-019**: Pattern classification MUST add less than 10 seconds to pipeline runtime for architectures with fewer than 100 findings (matching the Feature 141 Phase 3.5 budget).
- **FR-020**: Pattern classification MUST NOT introduce any new runtime dependencies (Python stdlib only — preserving the zero-runtime-dependency constraint per Feature 128 / 136 precedent).

### Key Entities

- **Agentic Pattern**: A canonical CSA MAESTRO cross-cutting threat category (one of six) describing a class of agentic risk that emerges from multi-agent coordination, persistent state, or inter-agent communication, distinct from per-component STRIDE threats. Key attributes: pattern name (enum), 1-sentence canonical definition, 2-3 representative examples, detection criteria, current coverage by existing agents.
- **Finding Pattern Tag**: A pattern category assignment on a finding, set via the `agentic_pattern` field. Values: one of six canonical patterns, `none` (no pattern relevance), or `multiple` (two or more patterns equally — rare). Required on every finding post-Feature-142.
- **Coverage Mapping Row**: An entry in the shared reference coverage mapping table. Key attributes: pattern name (one of six), Currently Covered By (list of existing agents or "None"), Coverage Strength (Full / Partial / None — Coverage Required), Gap (1-sentence justification when Partial).
- **Multi-Agent Gate Predicate**: An architecture-level invariant that gates non-`none` pattern assignment. Composed of three OR conditions: (a) ≥2 components classified as `agentic` or `llm`, (b) ≥1 inter-component data flow between two agentic components, (c) explicit multi-agent coordination keywords in the architecture description (multi-agent, swarm, supervisor, delegation, agent mesh).
- **Pattern Analysis Section**: A conditional section in the threat report that enumerates findings by canonical pattern when at least one non-`none` pattern is present. Composed of one subsection per pattern with non-zero finding count, ordered by maximum severity descending then finding count descending.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Pattern coverage — 6 of 6 canonical CSA MAESTRO agentic patterns have at least one detection path in tachi after Feature 142 ships (the three previously-uncovered patterns gain new detection).
- **SC-002**: Multi-agent detection rate — at least 80% of qualifying multi-agent architectures (those satisfying the multi-agent gate predicate) produce at least one non-`none` pattern finding.
- **SC-003**: Zero false positives — 0% of single-agent or non-agentic architectures produce non-`none` pattern findings (validated against the 5 baseline examples that fail the multi-agent gate predicate).
- **SC-004**: Backward compatibility — 5 baseline PDF outputs (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) remain byte-identical under SOURCE_DATE_EPOCH=1700000000 after Feature 142 ships. The 6th example (multi-agent demonstration target) is intentionally regenerated.
- **SC-005**: Determinism — pipeline runs on identical inputs produce identical pattern assignments (no variance across runs).
- **SC-006**: Coverage table completeness — the shared reference coverage mapping table covers all six canonical patterns with assessments restricted to the three permitted Coverage Strength values; every Partial assessment includes a 1-sentence Gap justification.
- **SC-007**: SARIF tag fidelity — for every finding with non-`none` pattern, the SARIF output includes exactly one `maestro-pattern:<name>` tag matching the lowercase / colon-separator format of the existing `maestro-layer:` convention.
- **SC-008**: Performance budget — pattern classification adds less than 10 seconds to pipeline runtime for architectures with fewer than 100 findings.
- **SC-009**: Demonstration completeness — at least one multi-agent example architecture surfaces findings tagged with all three previously-uncovered patterns in all output formats (threats.md, threat report, SARIF).
- **SC-010**: Field universality — every finding produced post-Feature-142 has a populated `agentic_pattern` field (no missing/null values; `none` is the sentinel for non-pattern findings).

### Assumptions

- The CSA MAESTRO framework (publicly documented in CSA Blog 2025-02-06, Snyk Labs, and Practical DevSecOps) is the canonical source for the six pattern names. The names are stable for a 2+ year horizon (no immediate v2 framework revision expected).
- Feature 084 (MAESTRO Layer Mapping) and Feature 136 (Canonical Layer Names) are merged and stable. Pattern findings inherit `maestro_layer` from their target component using the existing inheritance mechanism.
- Feature 141 (Cross-Layer Attack Chains) is merged and stable. Pattern grouping and chain grouping are independent mechanisms — a finding may belong to both.
- Feature 082 (Threat Agent Skill References) is merged and stable. If the project ADR selects a mechanism that requires editing existing AI agents or adding a new agent, the existing lean+skill-references shape is the governing convention.
- The multi-agent gate predicate (FR-006) is sufficient to prevent false positives on single-agent architectures. The 5 non-multi-agent baseline examples are the validation surface.
- At least one example architecture (likely an extended `agentic-app` or a purpose-built multi-agent example) can demonstrate all three previously-uncovered patterns end-to-end. The choice between extension paths is recorded in the project plan.

### Scope Boundaries

**In Scope (P0)**:
- Six canonical pattern definitions in shared reference (FR-001, FR-002)
- Finding schema extension with `agentic_pattern` enum field, version bump 1.3 → 1.4 (FR-003, FR-004, FR-017)
- Multi-agent gate predicate enforcement (FR-006)
- Project ADR documenting pattern classification mechanism (FR-007)
- Pattern data placement invariant — `agentic_pattern` in finding IR + threats.md only (FR-008)
- threats.md output extension with Agentic Pattern column and conditional Section "Findings by Agentic Pattern" (FR-009, FR-010)
- Threat report Agentic Pattern Analysis section (FR-011, FR-012, FR-013)
- SARIF pattern tag propagation (FR-014)
- At least one multi-agent example demonstrating all three previously-uncovered patterns (FR-015)
- All 6 example pipeline outputs regenerated (FR-016)
- ADR-020 Revision History entry (FR-018)

**Should Have (P1)**:
- Coverage mapping table extended to all 11 threat agents (6 STRIDE + 5 AI), not only the 5 AI agents
- Pattern category surfaced in MAESTRO infographic templates (Feature 091 stack and heatmap variants)
- Pattern-to-control recommendations in compensating-controls.md output

**Out of Scope**:
- LLM-judgment-based pattern classification (rejected per ADR-021 determinism requirement)
- Net-new threat agents beyond the optional new cross-cutting agent if selected by the project ADR
- Pattern-aware risk scoring (pattern membership does not affect CVSS scores in this phase)
- Custom pattern definitions (users cannot define organization-specific patterns in this phase)
- Cross-pattern correlation (pattern A enables pattern B chains) — deferred
- Pattern-aware SARIF rule grouping (pattern is a tag, not a SARIF `rule` field)
- New MAESTRO-pattern-specific PDF page templates (patterns surface in narrative; no new full-bleed pages)
- Multi-architecture pattern aggregation (patterns are per-architecture analysis)
- Temporal Attack detection on single-agent architectures (deliberate scope boundary — multi-agent gate predicate excludes single-agent contexts; may warrant a follow-up feature)
