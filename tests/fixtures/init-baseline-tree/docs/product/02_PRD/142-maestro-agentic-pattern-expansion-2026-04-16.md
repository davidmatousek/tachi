---
prd:
  number: "142"
  topic: maestro-agentic-pattern-expansion
  created: 2026-04-16
  status: Delivered
  delivered: 2026-04-16
  pr: 172
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-16, status: APPROVED, notes: "Closes the final structural gap in tachi's MAESTRO compliance umbrella (Phases 1, 2, 4, 5 already shipped). Surfaces six canonical CSA patterns as named filterable categories; correctly scoped P0 detection for the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack). FR-2 four-option mechanism analysis defers final architecture call to ADR-026 in /aod.plan." }
  architect_signoff: { agent: architect, date: 2026-04-16, status: APPROVED_WITH_CONCERNS, notes: "11 findings (1 BLOCKING addressed inline, 5 MEDIUM, 5 LOW). BLOCKING B1 resolved: schema versioning rationale reworded to acknowledge Feature 136 covered enum-VALUE renames not new enum-typed FIELDS, and ADR-026 required to extend the precedent. M1 resolved: FR-2 trade-off analysis symmetrized (ownership / write-back / regression footprint axes added). M2 resolved: Option D (orchestrator-side classification per Feature 084/136) added. M3 resolved: FR-7 Path 1/2/3 explicit response paths with planned scope budget. M4 resolved: multi-agent gate predicate added to FR-2 Business Rules. M5 resolved: pattern data placement locked to threats.md only (not attack-chains.md). LOW items folded into spec deliverables." }
  techlead_signoff: { agent: team-lead, date: 2026-04-16, status: APPROVED_WITH_CONCERNS, notes: "Timeline 6-10d realistic at wave-budget level (consistent with Feature 141 estimation precedent). Three medium concerns surfaced: (M1) Option C strongly preferred for schedule (5-8d vs 8-12d for Option A); (M2) milestone (b) language now conditional on FR-2 outcome; (M3) agentic-app architecture extension is HIGH probability (~70%) per Feature 141 precedent — explicit budget added. Parallelism: 4-5 waves with 3-track parallel in Wave 0 (ADR-026 + shared reference + schema) and Wave 2 (threats.md + threat-report + SARIF). Dependencies clean — all upstream features delivered. Triple sign-off path on tasks.md will revisit conditional milestones once architect locks FR-2." }
source:
  idea_id: 142
  story_id: null
---

# MAESTRO Phase 3: Agentic Threat Pattern Expansion

**Status**: Delivered
**Created**: 2026-04-16
**Delivered**: 2026-04-16 (PR #172, commit c0b7378)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Evidence**: Canonical CSA MAESTRO sources (CSA blog, Snyk Labs, Practical DevSecOps) name six specific cross-cutting agentic threat patterns (Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition) that STRIDE-per-element does not cover. Tachi's five AI threat agents cover some patterns implicitly but surface none as named categories. ICE: Impact 7, Confidence 6, Effort 5 = 18.

---

## Executive Summary

### The One-Liner
Surface the six canonical MAESTRO cross-cutting agentic threat patterns — Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition — as named, filterable finding categories so cross-cutting agentic risks that don't fit cleanly into STRIDE-per-element become first-class output.

### Problem Statement
Tachi's five AI threat agents (prompt-injection, tool-abuse, agent-autonomy, data-poisoning, model-theft) detect agentic threats organized around STRIDE analogues and target component types. They do not classify findings against the six canonical MAESTRO agentic patterns. A security engineer analyzing a multi-agent supervisor cannot today filter findings by "Agent Collusion" because the concept does not exist in tachi's output schema. Three of the six canonical patterns (Agent Collusion, Emergent Behavior, Temporal Attacks) have no dedicated home in any existing agent and are effectively invisible in tachi output.

This matters because MAESTRO practitioners expect these categories — they are the substantive content behind the "Multi-Agent" in MAESTRO. Shipping MAESTRO support without explicit multi-agent threat categories is shipping the framework's branding without its substance. Adopters comparing tachi output to manual MAESTRO threat modeling deliverables see a structural gap: the canonical categories that anchor MAESTRO discourse are missing from the tool that claims to implement it.

The MAESTRO compliance umbrella ([#136](https://github.com/davidmatousek/tachi/issues/136)) has progressed through Phase 1 (passive layer overlay, Features 084 / 136), Phase 2 (cross-layer attack chains, Feature 141), and Phase 4/5 (compliance posture ADRs for AIVSS and NIST AI RMF, Features 143 / 144). Phase 3 — the canonical agentic pattern categories — remains the single open structural gap in tachi's MAESTRO posture.

### Proposed Solution
Extend the finding intermediate representation (IR) with an `agentic_pattern` enum field whose values are the six canonical MAESTRO agentic pattern names plus `none` and `multiple`. Add explicit detection for the three patterns currently uncovered (Agent Collusion, Emergent Behavior, Temporal Attacks) and surface pattern category in:

1. The **finding schema** (`schemas/finding.yaml`), bumped to v1.4 with the new `agentic_pattern` enum field
2. The **shared reference** (`maestro-agentic-patterns-shared.md`) defining each of the six patterns with detection criteria and a coverage mapping table showing which existing agents detect which patterns today
3. The **threats.md output** with a new pattern category column and a per-pattern grouping section
4. The **threat report narrative** with a new "Agentic Pattern Analysis" section that groups findings by pattern when applicable
5. **At least one multi-agent example** demonstrating pattern coverage end-to-end (likely `agentic-app`)

The mechanism by which findings receive their pattern classification is the central architecture decision and is documented as the **Phase 3 ADR** (proposed ADR-026). Three candidate mechanisms (extend existing agents, new cross-cutting agent, hybrid synthesis) are presented in FR-2 with the architect making the final call during `/aod.plan`.

### Success Criteria
- Finding schema includes `agentic_pattern` enum field with all six canonical patterns plus `none` and `multiple`
- Shared reference documents each of the six patterns with definition, examples, and detection criteria
- Coverage mapping table shows which existing AI threat agents detect which patterns today (gap analysis)
- At least one multi-agent example surfaces findings tagged with all three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attacks)
- Threat report narrative groups findings by pattern when applicable
- Backward compatible: findings without pattern classification render as before; existing 5 examples without multi-agent characteristics produce no false pattern findings
- ADR-026 committed documenting the chosen pattern classification mechanism
- All 6 example pipeline outputs regenerated

### Timeline
Estimated 6-10 days — focused additive feature touching detection, schema, and output. Three milestone boundaries: (a) ADR-026 mechanism decision + shared reference drafted (day 3), (b) detection wired and validated against the demonstration example (day 6 if Option B/C/D selected; day 8 if Option A selected — see FR-2), (c) all 6 examples regenerated + regression complete (day 10). The mechanism decision (ADR-026) is the principal schedule risk — the four options in FR-2 have meaningfully different effort profiles, with Options C/D producing the lowest effort and Option A the highest.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's vision is to be the default threat modeling toolkit for teams building agentic AI applications. The six canonical MAESTRO agentic patterns are the framework's signature differentiator — they name the cross-cutting risks that emerge from multi-agent coordination and that no STRIDE-per-element analysis can surface. Implementing them moves tachi from "STRIDE tool with MAESTRO labels and cross-layer chains" to "full MAESTRO implementation including the six canonical agentic categories." This directly strengthens tachi's positioning as the default toolkit for multi-agent threat modeling.

### Roadmap Fit
This is Phase 3 of the MAESTRO compliance initiative ([#136](https://github.com/davidmatousek/tachi/issues/136)). It is the final structural feature in the MAESTRO umbrella — Phases 1, 2, 4, 5 have shipped (Features 084, 136, 141, 143, 144). With Phase 3 delivered, tachi will have completed the MAESTRO compliance roadmap with three implementation features (taxonomy overlay, cross-layer chains, agentic patterns) and two documentation-only ADR spikes (AIVSS and NIST AI RMF posture).

### Predecessor Relationship
| Feature | Relationship |
|---------|-------------|
| 084 (MAESTRO Layer Mapping) | Provides MAESTRO layer assignment; pattern findings inherit layer from target component — prerequisite |
| 136 (MAESTRO Canonical Layer Correctness) | Corrected L5/L6/L7 names that pattern definitions reference — prerequisite |
| 141 (MAESTRO Cross-Layer Attack Chains) | Cross-layer chains and pattern categorization are independent grouping mechanisms — a finding may belong to both — complementary |
| 082 (Threat Agent Skill References) | Lean agent + companion skill pattern is the architectural shape any new agent or pattern-detection skill should follow — convention |
| 074 (Baseline-Aware Pipeline) | Pattern field flows through baseline correlation; no special handling required — passive compatibility |
| 005 (STRIDE Threat Agents) | STRIDE findings remain category=`spoofing|tampering|...`; pattern field is orthogonal and applies primarily to AI findings — unchanged |
| 007 (AI Threat Agents) | The five existing AI agents are the principal extension surface — see FR-2 for the three candidate mechanisms |
| 015 (Threat Report) | Narrative section structure extended with pattern grouping — extension point |

---

## Target Users & Personas

### Primary Persona: Security Engineer Analyzing Multi-Agent Systems
- **Role**: Security engineer running tachi on multi-agent agentic AI systems
- **Experience**: Intermediate-to-senior, familiar with STRIDE and MAESTRO frameworks
- **Goals**: Filter and prioritize findings that represent coordinated multi-agent attacks distinctly from single-agent exploits
- **Pain Points**: Agent Collusion findings are buried inside generic tool-abuse output; Temporal Attacks (sleeper agents) are invisible because no agent looks for them; Emergent Behavior risks have no dedicated category

**Why This Matters**: The patterns map directly to remediation strategies. Agent Collusion calls for coordination throttles and inter-agent rate limits. Temporal Attacks call for behavioral baselining and drift detection. Emergent Behavior calls for fail-safe shutdowns and bounded action scopes. Without the pattern category, a security engineer cannot prioritize the right control class.

### Secondary Persona: MAESTRO Practitioner / Threat Modeler
- **Role**: Threat modeler adopting MAESTRO methodology, evaluating tools
- **Experience**: Familiar with CSA MAESTRO framework and canonical patterns
- **Goals**: Produce threat models that are directly comparable to manual MAESTRO deliverables
- **Pain Points**: Tachi output uses category=`agentic` and category=`llm` for AI findings — these are tachi-internal STRIDE analogues, not MAESTRO categories

**Why This Matters**: Tachi adoption in MAESTRO-aware organizations depends on producing output that reads as MAESTRO output. The six canonical pattern names are the lingua franca of MAESTRO discourse. Without them, tachi outputs are easily dismissed as "STRIDE with MAESTRO sticker" rather than recognized as a full MAESTRO implementation.

### Tertiary Persona: CISO / Security Leadership
- **Role**: Chief Information Security Officer reviewing PDF security assessment for board communication
- **Experience**: Strategic security leader, limited time for finding-level detail
- **Goals**: Brief executives on cross-cutting agentic risks that go beyond per-component vulnerabilities
- **Pain Points**: Emergent Behavior and Temporal Attack risks require dedicated monitoring budget; without these named categories in the report, they are invisible to budget allocation

**Why This Matters**: A board-level briefing needs named risk categories that map to investment decisions. "Three Critical findings related to Agent Collusion" is actionable; "three Critical agentic findings" is not.

---

## User Stories

### US-1: Security Engineer Wants Agent Collusion as an Explicit Filter
**When** reviewing tachi threat model output on a multi-agent system,
**I want** Agent Collusion surfaced as an explicit pattern category on findings,
**So I can** filter and prioritize coordinated multi-agent attack findings distinctly from single-agent exploits.

**Acceptance Criteria**:
- **Given** a multi-agent architecture with two or more cooperating agents and shared communication channels, **when** the pipeline runs, **then** findings reflecting coordinated agent behavior are tagged `agentic_pattern: agent_collusion`
- **Given** the threats.md output, **when** viewing the findings table, **then** an Agentic Pattern column displays the assigned pattern (or `—` for unclassified findings)
- **Given** a single-agent architecture, **when** the pipeline runs, **then** no findings receive `agent_collusion` (no false positives — collusion requires multi-agent context)

**Priority**: P0 | **Effort**: M

### US-2: Threat Modeler Wants Temporal Attack Detection
**When** modeling threats against a long-running agentic system,
**I want** Temporal Attack patterns (sleeper agents, gradual corruption, seasonal exploitation) detected and surfaced,
**So I can** reason about finding categories that are invisible to point-in-time STRIDE analysis.

**Acceptance Criteria**:
- **Given** an architecture with a fine-tuning pipeline, persistent agent memory, or long-running learning loop, **when** the pipeline runs, **then** at least one Temporal Attack finding is generated tagged `agentic_pattern: temporal_attack`
- **Given** a Temporal Attack finding, **when** viewing the threat description, **then** it explicitly identifies the temporal vector (sleeper agent activation, gradual corruption, seasonal exploitation)
- **Given** a stateless single-shot inference architecture, **when** the pipeline runs, **then** no Temporal Attack findings are generated (no false positives — temporal attacks require persistent state)

**Priority**: P0 | **Effort**: M

### US-3: CISO Wants Emergent Behavior Risks Called Out
**When** reviewing the PDF security assessment for board communication,
**I want** the threat report to explicitly call out Emergent Behavior risks,
**So I can** allocate monitoring budget to detect unpredictable multi-agent interactions rather than assuming STRIDE coverage is sufficient.

**Acceptance Criteria**:
- **Given** a multi-agent architecture, **when** the threat report is generated, **then** an "Agentic Pattern Analysis" section enumerates findings by pattern category (Agent Collusion, Emergent Behavior, Temporal Attack, Trust Exploitation, Communication Vulnerability, Resource Competition)
- **Given** Critical or High findings tagged with `emergent_behavior`, **when** viewing the section, **then** the report includes a brief narrative on the emergent behavior class and recommended monitoring controls
- **Given** an architecture with no emergent behavior risk, **when** viewing the section, **then** the Emergent Behavior subsection is suppressed (zero-finding subsections are hidden, not shown empty)

**Priority**: P1 | **Effort**: M

### US-4: Tachi Adopter Wants Coverage Mapping Documentation
**When** evaluating tachi's MAESTRO completeness before adoption,
**I want** the shared reference to map each of the five existing AI threat agents to which canonical MAESTRO patterns they cover (and which they don't),
**So I can** understand tachi's MAESTRO completeness at a glance and recognize which risks require external supplementary controls.

**Acceptance Criteria**:
- **Given** the shared reference `maestro-agentic-patterns-shared.md`, **when** viewing the coverage table, **then** each of the six canonical patterns is mapped to one or more existing AI agents (or marked "Not covered — new detection added in Feature 142")
- **Given** the coverage table, **when** read end-to-end, **then** it answers the question "which of the six canonical MAESTRO patterns does tachi detect, and through which agent?" without ambiguity
- **Given** a future tachi release, **when** a new AI agent is added, **then** the coverage table is updated as part of that feature's deliverables (governance precedent)

**Priority**: P1 | **Effort**: S

### US-5: MAESTRO Practitioner Wants Pattern-Tagged Output
**When** comparing tachi output to manual MAESTRO threat modeling deliverables,
**I want** findings tagged with the canonical pattern category in the IR and SARIF outputs,
**So that** tachi outputs are directly comparable to manual deliverables and downstream tooling can filter by pattern.

**Acceptance Criteria**:
- **Given** a tachi finding for a multi-agent risk, **when** examining the finding IR, **then** the `agentic_pattern` field is populated with one of the six canonical pattern names, `none`, or `multiple`
- **Given** the SARIF output, **when** examining a result with a pattern, **then** the `properties` block includes the `agentic_pattern` value as a tag for downstream filtering
- **Given** a finding that fits no canonical pattern, **when** examining the IR, **then** `agentic_pattern: none` is set explicitly (no missing field — the field is required for all findings post-Feature-142)

**Priority**: P1 | **Effort**: S

### US-6: Adopter Wants End-to-End Multi-Agent Example
**When** evaluating tachi before adoption,
**I want** at least one example architecture to demonstrate all six canonical patterns end-to-end (or document which are not applicable),
**So I can** see what the capability looks like before committing to adoption.

**Acceptance Criteria**:
- **Given** the examples directory, **when** inspecting `agentic-app` (or a similarly multi-agent example), **then** its output includes findings tagged with at least three of the six canonical patterns (the three previously-uncovered: Agent Collusion, Emergent Behavior, Temporal Attack)
- **Given** the example, **when** the PDF is regenerated, **then** the threat report includes the "Agentic Pattern Analysis" section with at least three populated subsections
- **Given** the example, **when** a new user runs the pipeline, **then** pattern assignment is reproducible (deterministic classification per ADR-021)

**Priority**: P0 | **Effort**: M

---

## Functional Requirements

### FR-1: Six Canonical Pattern Definitions in Shared Reference
**Description**: A new shared reference file (`maestro-agentic-patterns-shared.md`) defining each of the six canonical MAESTRO agentic patterns with detection criteria.

**Content per pattern**:
- **Definition**: 1-2 sentence canonical description sourced from CSA MAESTRO
- **Examples**: 2-3 concrete attack vectors representative of the pattern
- **Detection criteria**: Architectural preconditions, keyword indicators, and finding signals that point to the pattern
- **Existing agent coverage**: Which of the 5 AI threat agents (or 6 STRIDE agents) currently produces findings that exemplify this pattern, if any

**Six patterns**:
1. **Agent Collusion**: Multiple compromised agents coordinating to achieve malicious objectives (DDoS, information gathering, policy circumvention)
2. **Emergent Behavior**: Exploiting unpredictable behaviors that arise from agent interactions (cascade failures, behavioral manipulation)
3. **Temporal Attacks**: Sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation
4. **Trust Exploitation**: Identity spoofing between agents, reputation manipulation, trust chain attacks
5. **Communication Vulnerabilities**: Inter-agent message interception, protocol manipulation, routing attacks
6. **Resource Competition**: Resource monopolization, priority manipulation, coordination disruption between agents

**Coverage Mapping Table** (initial assessment, subject to refinement):

| Pattern | Currently Covered By | Coverage Strength | Gap |
|---------|---------------------|------------------|-----|
| Agent Collusion | None directly | None | New detection required |
| Emergent Behavior | agent-autonomy (cascading failures) | Partial | Explicit detection required |
| Temporal Attacks | None directly | None | New detection required |
| Trust Exploitation | spoofing (identity), tool-abuse (tool trust) | Partial | Multi-agent identity context required |
| Communication Vulnerabilities | tool-abuse (MCP/protocol), info-disclosure (eavesdropping) | Partial | Inter-agent messaging context required |
| Resource Competition | denial-of-service (component-level), agent-autonomy (resource consumption) | Partial | Inter-agent context required |

**Business Rules**:
- Each pattern definition includes its CSA MAESTRO source citation
- Coverage assessments are honest — overclaiming coverage undermines the gap analysis purpose. Coverage Strength uses three values only: **Full** (the agent's existing detection produces findings that materially exemplify the pattern with no gap), **Partial** (the agent detects related risks but misses key signals — the column must include a 1-sentence justification noting what's missing), **None — Coverage Required** (no existing agent produces findings exemplifying the pattern; new detection is required)
- The reference file follows the existing `tachi-shared/references/` shape (frontmatter, type, version, consumers) per ADR-019 shared cross-agent definitions governance

### FR-2: Pattern Classification Mechanism (Central ADR Decision)
**Description**: The mechanism by which findings receive their `agentic_pattern` value. This is the central architecture decision deferred to `/aod.plan` and documented as ADR-026. Four candidate options, each evaluated on three axes: pattern semantics ownership, schema write-back location, and existing-agent regression footprint.

**Option A — Extend existing AI agents** (each agent gains explicit pattern responsibility):
- Each of the 5 existing AI agents adds explicit pattern assignment in its finding construction step
- New keyword triggers added per agent for the patterns it owns
- Pattern assignment happens inline during detection
- **Ownership**: Distributed across 5 agent files
- **Schema write-back**: Inline in agent finding construction
- **Regression footprint**: HIGH — touches all 5 agents recently stabilized in Feature 082
- *Pros*: No new agents, no orchestrator changes, simplest dispatch surface
- *Cons*: Distributes pattern responsibility across 5 files; coverage gaps (Agent Collusion, Temporal Attacks) need a new owner; risks inconsistent pattern semantics across agents; reopens the 11-agent stabilization that Feature 082 just closed

**Option B — Add a new cross-cutting agent** (single new agent owns all six patterns):
- A new `tachi-agentic-patterns` agent is added under `.claude/agents/tachi/`
- This agent runs as a regular detection agent in Phase 2 alongside the 5 existing AI agents
- It produces findings tagged with `agentic_pattern` and a new `category` value (e.g., `agentic-pattern`) or reuses `category: agentic`
- **Ownership**: Centralized in the new agent
- **Schema write-back**: Inline in new agent's finding construction
- **Regression footprint**: MEDIUM — no existing-agent edits, but introduces ripple across deduplication (Phase 3 dedup_key generation), Section 4a intra-component correlation, the orchestrator coverage matrix, and the Risk Summary aggregation logic
- *Pros*: Clean ownership, single source of truth for pattern semantics, easy to extend with new patterns
- *Cons*: Multi-touchpoint deduplication ripple (Communication Vulnerability finding + tool-abuse finding on the same MCP server must dedupe correctly); orchestrator coverage matrix and Risk Summary aggregation must learn the new category

**Option C — Hybrid (post-hoc synthesis)** (existing agents unchanged; new synthesis phase):
- Agents 1-5 keep their current STRIDE-analog responsibilities and their current finding output
- A new synthesis phase (similar to Phase 3.5 cross-layer chains in Feature 141) runs after deduplication
- This phase reads existing findings and assigns `agentic_pattern` based on finding content + architectural context (multi-agent indicators, persistent state, etc.)
- May also generate net-new findings for patterns not covered by any existing agent (Agent Collusion, Temporal Attacks)
- **Ownership**: Centralized in the synthesis phase (orchestrator-side or new sub-agent)
- **Schema write-back**: Modifies the deduplicated finding IR after detection (write-back pattern, distinct from Feature 141 which produces a separate `attack-chains.md` aggregate without modifying findings)
- **Regression footprint**: LOWEST — zero edits to the 11 existing agents
- *Pros*: Existing agent code unchanged (zero agent regression risk); pattern semantics centralized; reuses the Feature 141 Phase 3.5 post-dedup architectural slot
- *Cons*: Two-phase logic (detect then classify); modifies the finding IR after detection (unlike Feature 141 which only aggregates); risk that the synthesis phase becomes a "second detection agent" by accident if pattern-generation logic grows

**Option D — Orchestrator-side classification at finding emission** (the maestro_layer pattern from Feature 084/136):
- The orchestrator assigns `agentic_pattern` at the same point it currently assigns `maestro_layer` — during Phase 1 component classification, with finding-level inheritance during Phase 3
- Pattern classification is keyword-driven against component name, description, and DFD type — same algorithm shape as MAESTRO layer keyword matching
- **Ownership**: Centralized in the orchestrator's classification step
- **Schema write-back**: Inline at finding emission (same hook as `maestro_layer`)
- **Regression footprint**: LOW — touches the orchestrator's classification step and the maestro-layers shared reference structure, no agent edits
- *Pros*: Reuses the proven Feature 084 / 136 keyword-classification pattern; simplest implementation; deterministic by construction (keyword match is rule-based)
- *Cons*: Pure keyword matching may underclassify patterns that require finding-content analysis (e.g., Agent Collusion typically requires looking at the *threat description* across multiple findings, not just the target component); generating net-new findings for uncovered patterns is harder when the classification phase is component-centric rather than finding-centric

**ADR-026 must select one option and justify it across all four**. Recommendation noted from PRD author: **Option C (Hybrid)** is most architecturally consistent with Feature 141 (post-hoc cross-layer correlation), protects existing agents from regression, and naturally supports finding-content-based pattern detection. Option D is the lightest-effort alternative if the architect determines that keyword-driven classification is sufficient. Options A and B carry higher regression footprints. Final call belongs to the architect during `/aod.plan`.

**Business Rules** (independent of mechanism choice):
- Pattern classification must be deterministic (ADR-021)
- Pattern classification must not produce false positives on architectures lacking multi-agent characteristics
- **Multi-agent gate predicate**: No `agentic_pattern` value other than `none` may be assigned unless the architecture exhibits at least one of: (a) ≥2 components classified as `agentic` or `llm` category in the dispatch keywords, (b) ≥1 inter-component data flow between two agentic components, or (c) explicit multi-agent coordination keywords in the architecture description (multi-agent, swarm, supervisor, delegation, agent mesh). The gate is enforced at the classification step, regardless of which mechanism (A/B/C/D) ADR-026 selects.
- The mechanism choice does not affect the schema, threats.md format, or threat report format — only the agent dispatch and detection pipeline
- **Pattern data placement**: `agentic_pattern` lives in the finding IR (and threats.md) only — it does NOT modify or extend `attack-chains.md` (Feature 141 artifact). The threat-report agent may cross-reference chain membership in pattern narratives, but the two artifacts remain independent (consistent with Feature 141 independence invariant)

### FR-3: Finding Schema Extension
**Description**: Extend `schemas/finding.yaml` with the new `agentic_pattern` enum field.

**Schema change**:
```yaml
# schemas/finding.yaml addition
agentic_pattern:
  type: string
  enum:
    - agent_collusion
    - emergent_behavior
    - temporal_attack
    - trust_exploitation
    - communication_vulnerability
    - resource_competition
    - none
    - multiple
  default: none
  description: >
    Canonical CSA MAESTRO agentic threat pattern category.
    Use 'none' for findings that do not map to any pattern.
    Use 'multiple' for findings that exemplify two or more patterns
    equally (rare; prefer the dominant pattern when one exists).
```

**Business Rules**:
- `schema_version` bumps from 1.3 to 1.4. **Versioning rationale**: Feature 136 established a minor-bump rule for enum-value-only renames on an existing field. Feature 142 adds an entirely new enum-typed field — a related but structurally distinct change. The PRD proposes a minor bump (additive, optional, default-`none`, backward compatible for parsers that ignore the field), but ADR-026 must extend the Feature 136 rule to explicitly cover *new enum-typed field additions* alongside *enum-value renames* — or justify a major bump if the architect determines that adding a required field warrants major-version semantics. This decision is locked in ADR-026 before implementation begins.
- The field is required after Feature 142 ships (default `none` makes this seamless for findings without pattern relevance)
- Backward compatible: existing parsers that do not know about `agentic_pattern` ignore the field; existing findings written by agents that do not yet assign pattern receive `none` by default
- Baseline parser regression test: confirm that pre-Feature-142 baseline findings (which do not include the field) parse correctly and default to `agentic_pattern: none` when consumed by Feature 142 parsers

### FR-4: threats.md Output Extension
**Description**: Extend the threats.md output format to surface pattern category.

**Changes**:
- New "Pattern" column in the findings table (Section 7) — displays the pattern enum value or `—` for `none`
- New optional Section 4b "Findings by Agentic Pattern" — groups findings by pattern, suppressed when no patterns are populated
- Pattern column placement: after Category, before Component (visually grouped with other classification metadata)

**Business Rules**:
- Section 4b is conditional — only rendered when at least one finding has a non-`none` pattern
- Section 4b complements Section 4a (intra-component correlation) and Section 4c (Feature 141 cross-layer chain references) — all three are independent grouping mechanisms
- The Pattern column always renders (consistent table shape across architectures); empty value displays as `—`

### FR-5: Threat Report "Agentic Pattern Analysis" Section
**Description**: A new section in `threat-report.md` that narratively analyzes findings by canonical pattern.

**Placement**: New section "Agentic Pattern Analysis" placed after Cross-Layer Attack Chains (Feature 141) and before Findings Detail. The section number is determined at implementation time by `grep`-counting existing sections in the threat-report.md output schema — do NOT hardcode a section number in this PRD because the existing count may shift between PRD draft and implementation.

**Content per pattern subsection** (only rendered when at least one finding tagged with the pattern):
- Pattern name and 1-sentence definition (from shared reference)
- Count of Critical, High, Medium, Low findings tagged with the pattern
- 100-200 word narrative describing the pattern's manifestation in this architecture
- List of impacted finding IDs with cross-references

**Business Rules**:
- Section is conditional: only included when at least one finding has a non-`none` pattern
- Subsections are conditional: zero-finding patterns are suppressed (not shown empty)
- Narrative is generated by the threat-report agent (extends existing narrative generation per Feature 015 patterns)
- Pattern subsections ordered by maximum severity, then by finding count (matches Section 6 chain ordering convention)

### FR-6: SARIF Pattern Tag Propagation
**Description**: Propagate the `agentic_pattern` value into SARIF output as a tag for downstream tooling.

**Implementation**: For each finding with a non-`none` pattern, add a `properties.tags` entry of the form `maestro-pattern:<pattern_name>` (e.g., `maestro-pattern:agent_collusion`). The format must match the Feature 084 `maestro-layer:<L#>` tag convention exactly (same casing, same colon-separator, same lowercase tag namespace) — verify against the SARIF generator's existing maestro-layer tagging logic before implementation.

**Business Rules**:
- Tags follow existing SARIF tag conventions (lowercase, colon-separated namespace)
- `none`-pattern findings receive no pattern tag (avoids tag noise)
- Backward compatible: SARIF consumers that ignore the new tag see no behavioral change

### FR-7: Example Architecture Demonstration
**Description**: At least one multi-agent example architecture must demonstrate the new pattern coverage end-to-end.

**Candidate examples** — three response paths, ranked by team-lead and architect schedule preference:
- **Path 1 (preferred): Extend `agentic-app`** — it was the demo architecture for Feature 141 cross-layer chains and has the richest MAESTRO layer coverage. However, the current architecture has only one LLM Agent and one MCP Tool Server, no fine-tuning pipeline, and no persistent learning loop. Demonstrating Agent Collusion, Emergent Behavior, and Temporal Attack will require **planned architecture extension** (3+ new components: a second cooperating agent, a long-running learning loop, and an inter-agent communication channel). Extension is treated as **planned scope**, not contingency, with a 1-2h budget allocated in Wave 0 of `/aod.plan`.
- **Path 2: Build a purpose-built 7th example** — a new `multi-agent-supervisor` or `agentic-collusion-demo` example designed from the start to exercise all six canonical patterns. Higher up-front effort (~1 day) but produces a cleaner demonstration artifact and avoids modifying the agentic-app baseline that Feature 141 just stabilized.
- **Path 3: Document deferred patterns** — if `agentic-app` extension cannot demonstrate one or more patterns within the day-6 milestone, defer the un-demonstrable pattern(s) to a follow-up feature with explicit narrative explaining the deferred status.

**Demonstration requirements**:
- At least one finding tagged with each of the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack)
- Pattern findings appear in threats.md, the threat report narrative, and SARIF
- Example regeneration is reproducible (deterministic per ADR-021)

**Business Rules**:
- The choice between Path 1, 2, or 3 is locked in `/aod.plan` Wave 0 alongside ADR-026; the architect leads the call with team-lead schedule input
- Other 5 examples regenerated with no new pattern findings expected (single-agent architectures should not trigger multi-agent patterns — this is a backward-compatibility validation, not a coverage requirement)
- Multi-agent gate predicate (FR-2 Business Rules) enforces the "no false patterns on single-agent architectures" invariant for the 5 baseline examples

### FR-8: ADR-026 Documentation
**Description**: New ADR documenting the Phase 3 pattern classification mechanism decision.

**Content**:
- Status: Proposed during `/aod.define`, Accepted at `/aod.plan` sign-off
- Context: The three options from FR-2 with trade-off analysis
- Decision: The chosen option with full justification
- Consequences: Pipeline shape changes, schema impact, regression risk profile
- Cross-references: ADR-020 (MAESTRO classification), ADR-021 (determinism), ADR-019 (shared cross-agent definitions), Feature 141 PRD (Phase 2 precedent)

**Business Rules**:
- ADR follows the existing tachi ADR template
- ADR is committed in the same PR as the implementation
- ADR-020 receives a back-reference in its Revision History noting Phase 3 completion

---

## Non-Functional Requirements

### Backward Compatibility (NON-NEGOTIABLE)
- Existing pipeline output must remain unchanged for findings that do not map to any pattern (default `none` is invisible in displayed output via `—`)
- All new sections (4b in threats.md, Agentic Pattern Analysis in threat-report.md) are conditionally gated on the presence of non-`none` pattern findings
- The 5 existing examples without multi-agent characteristics (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) must produce zero new pattern findings — validated against backward-compatibility baselines
- agentic-app is the intentional regeneration target (consistent with the Feature 141 / Feature 136 precedent)
- Backward-compatibility test: 5 baseline PDFs byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021) for non-multi-agent examples

### Determinism
- Pattern classification must produce identical pattern assignments for identical input (per ADR-021)
- Whichever mechanism is chosen in ADR-026, the structural classification step must be deterministic — no LLM-judgment-based pattern assignment
- If Option C (hybrid synthesis) generates net-new findings for uncovered patterns, those finding generations must also be deterministic (rule-based, not interpretive)

### Performance
- Pattern classification adds <10s to pipeline runtime for architectures with <100 findings (matches Feature 141 Phase 3.5 budget; tighter budgets are not justified given that Option C/D both add a pipeline phase comparable in shape to Feature 141's correlation engine)
- No additional external API calls
- Reuses existing finding IR — no parallel data structures

### Maintainability
- Pattern definitions, examples, and detection criteria live in a single shared reference file (single source of truth)
- Coverage mapping table is updated as part of any future AI agent addition (governance precedent — captured in ADR-026 consequences)
- Pattern enum values are versioned via `schema_version` bumps (1.4 for this feature; future pattern refinements bump again per Feature 136 precedent)

---

## Success Metrics

### Primary Metrics

**Pattern Coverage**:
- **Definition**: Percentage of the six canonical MAESTRO patterns with at least one detection path in tachi
- **Target**: 100% (6/6 patterns have a detection path; the three previously-uncovered patterns gain new detection)

**Multi-Agent Architecture Detection Rate**:
- **Definition**: Percentage of multi-agent architectures (≥2 cooperating agents) that produce at least one pattern finding
- **Target**: >80% of qualifying architectures produce at least one pattern finding

**False Positive Rate on Non-Multi-Agent Architectures**:
- **Definition**: Percentage of single-agent or non-agentic architectures producing pattern findings
- **Target**: 0% (single-agent architectures must produce zero pattern findings — validated against 5 example baselines)

### Adoption Indicators
- MAESTRO practitioners cite pattern findings in security reviews
- Tachi output is referenced in MAESTRO compliance discussions as "implementing the canonical pattern categories"
- Coverage mapping table is referenced as the authoritative answer to "which MAESTRO patterns does tachi cover?"

---

## Scope & Boundaries

### In Scope (P0 — This PRD)
- Six canonical pattern definitions in shared reference (FR-1)
- Pattern classification mechanism per ADR-026 (FR-2 — three candidate options)
- Finding schema extension with `agentic_pattern` enum field (FR-3)
- threats.md output extension (Pattern column + optional Section 4b) (FR-4)
- Threat report Agentic Pattern Analysis section (FR-5)
- SARIF pattern tag propagation (FR-6)
- agentic-app example demonstrating all three previously-uncovered patterns (FR-7)
- ADR-026 documenting the mechanism decision (FR-8)
- All 6 example pipeline outputs regenerated

### Should Have (P1)
- Coverage mapping table extended to all 11 threat agents (6 STRIDE + 5 AI), not only the 5 AI agents
- Pattern category surfaced in MAESTRO infographic templates (Feature 091 stack and heatmap variants) — additive infographic enhancement
- Pattern-to-control recommendations in compensating-controls.md output

### Out of Scope
- LLM-judgment-based pattern classification (rejected per ADR-021)
- Net-new threat agents beyond the optional Option B (single cross-cutting agent if chosen by ADR-026)
- Pattern-aware risk scoring (pattern membership does not affect CVSS scores in this phase)
- Custom pattern definitions (users cannot define organization-specific patterns in this phase)
- Cross-pattern correlation (pattern A enables pattern B chains — deferred)
- Pattern-aware SARIF rule grouping (pattern is a tag, not a SARIF `rule` field)
- New MAESTRO-pattern-specific PDF page templates (patterns surface in narrative; no new full-bleed pages)
- Multi-architecture pattern aggregation (patterns are per-architecture analysis)

### Assumptions
- Feature 141 (cross-layer chains) is merged and stable — pattern categorization and chain correlation are independent and additive
- The agentic-app example architecture supports all three previously-uncovered patterns naturally (or with minimal extension)
- Single-agent architectures should produce zero pattern findings — this is the backward-compatibility invariant
- The 5 existing AI threat agents do not require behavioral changes (Option C protects this; Options A and B may require minor changes per the chosen mechanism)

### Constraints

**Technical Constraints**:
- Deterministic pattern classification is required (ADR-021) — full LLM-based classification is not acceptable
- Schema bumps follow the enum-value-only minor-bump precedent from Feature 136 (1.3 → 1.4)
- Pattern field must be additive — existing parsers that do not know about `agentic_pattern` must continue to work

**External Dependencies**:
- CSA MAESTRO framework specification for canonical pattern definitions and detection criteria
- No new runtime dependencies (zero-dependency runtime constraint preserved)

---

## Risks & Dependencies

### Technical Risks

**Risk 142.1**: Pattern classification false positives on single-agent architectures
- **Likelihood**: Medium
- **Impact**: High (false patterns undermine the credibility of the entire feature, especially for adopters whose architectures are not multi-agent)
- **Mitigation**: Conservative classification rules requiring explicit multi-agent indicators (≥2 agents in component inventory, inter-agent communication flows, persistent shared state); validate against all 5 non-multi-agent examples before release with zero-finding requirement
- **Contingency**: If false positives appear during validation, tighten the classification predicate to require additional architectural signals

**Risk 142.2**: Mechanism decision (ADR-026) selects an option that requires touching all 5 existing AI agents
- **Likelihood**: Medium (Option A explicitly requires this; Option B partially requires it via deduplication)
- **Impact**: Medium (regression risk on the 5 existing AI agents that were just refactored to lean shape in Feature 082)
- **Mitigation**: PRD recommendation flags Option C (hybrid synthesis) as architecturally consistent with Feature 141 and zero-regression on existing agents; architect makes final call with full trade-off awareness
- **Contingency**: If Options A or B are chosen, the implementation plan adds an explicit regression validation gate against the 11-agent skill-references baseline from Feature 082

**Risk 142.3**: Coverage mapping table overclaims coverage of patterns the existing agents only partially detect
- **Likelihood**: Medium (overclaiming is the easy mistake — every agent "kind of" covers most patterns)
- **Impact**: Medium (overclaiming undermines the gap analysis utility — adopters cannot trust the table)
- **Mitigation**: Coverage table includes a "Coverage Strength" column with three honest values (Full / Partial / None — Coverage Required); each Partial assessment includes a 1-sentence justification noting what is missing
- **Contingency**: If during ADR-026 analysis any "Partial" assessment is challenged as overclaim, downgrade to "None" rather than over-defend

**Risk 142.4**: agentic-app example does not naturally exercise all three previously-uncovered patterns
- **Likelihood**: Low (agentic-app is purpose-built as the multi-agent demo)
- **Impact**: Low (architecture extensions are cheap and isolated)
- **Mitigation**: If agentic-app gaps exist for one or more patterns, extend the architecture by 1-2 components (e.g., add a long-running learning loop for Temporal Attack demonstration); extensions must remain plausible
- **Contingency**: If extensions become non-plausible, defer the un-demonstrable pattern to a follow-up feature with explicit narrative explaining the deferred status

**Risk 142.5**: Pattern enum values become a maintenance burden as MAESTRO evolves
- **Likelihood**: Low (CSA MAESTRO patterns are stable per the canonical sources cited)
- **Impact**: Medium (enum changes require schema bumps)
- **Mitigation**: Schema versioning convention (Feature 136 precedent) handles enum changes cleanly with minor bumps; the six canonical patterns are well-defined and unlikely to change names
- **Contingency**: Pattern aliases or compatibility shims can be added if MAESTRO renames a pattern in a future revision

### Dependencies

**Internal Dependencies**:
- **Feature 084** (MAESTRO Layer Mapping): MAESTRO layer assignment used in pattern detection criteria — DELIVERED
- **Feature 136** (MAESTRO Canonical Layer Correctness): Canonical layer names referenced in pattern definitions — DELIVERED
- **Feature 141** (Cross-Layer Attack Chains): Cross-layer chain correlation is the architectural precedent for post-hoc finding analysis (Option C) — DELIVERED
- **Feature 082** (Threat Agent Skill References): Lean agent + companion skill pattern is the convention for any new agent (if Option B chosen) — DELIVERED
- **Feature 074** (Baseline-Aware Pipeline): Pattern field flows through baseline correlation — DELIVERED
- **Feature 005 / 007** (STRIDE / AI Threat Agents): Existing agent set that the coverage mapping table assesses — DELIVERED
- **Feature 015** (Threat Report): Narrative generation patterns reused for the new Agentic Pattern Analysis section — DELIVERED
- **Feature 003** (Orchestrator): New synthesis phase (if Option C chosen) extends orchestrator pipeline — DELIVERED

**External Dependencies**:
- CSA MAESTRO framework specification for canonical pattern definitions and citations

**Dependency Graph**:
```
[MAESTRO Phase 3: Agentic Pattern Expansion (142)]
  +-- Depends on: Feature 084 (MAESTRO Layer Mapping) — DELIVERED
  +-- Depends on: Feature 136 (Canonical Layer Names) — DELIVERED
  +-- Depends on: Feature 141 (Cross-Layer Chains) — DELIVERED
  +-- Depends on: Feature 082 (Lean Agent Convention) — DELIVERED
  +-- External: CSA MAESTRO spec for canonical pattern definitions
```

---

## Definition of Done

- [ ] Six canonical pattern definitions documented in `maestro-agentic-patterns-shared.md`
- [ ] Coverage mapping table (6 patterns x 11 agents) committed in shared reference
- [ ] ADR-026 committed documenting the chosen pattern classification mechanism
- [ ] `schemas/finding.yaml` extended with `agentic_pattern` enum field, version bumped 1.3 → 1.4
- [ ] `threats.md` template extended with Pattern column and conditional Section 4b
- [ ] `threat-report.md` template extended with conditional "Agentic Pattern Analysis" section
- [ ] SARIF output includes `maestro-pattern:<name>` tag for findings with non-`none` pattern
- [ ] At least one multi-agent example (agentic-app) demonstrates findings for the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack)
- [ ] Pattern classification is deterministic — same input produces same pattern assignments every run
- [ ] Backward compatible: 5 non-multi-agent example baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) byte-identical under `SOURCE_DATE_EPOCH=1700000000`
- [ ] No false-positive pattern findings in single-agent architectures (validated against 5 baselines)
- [ ] All 6 example pipeline outputs regenerated
- [ ] ADR-020 Revision History references Phase 3 completion
- [ ] `/aod.analyze` passes with no inconsistencies

---

## Open Questions

### Product Questions
- [ ] Should the coverage mapping table be extended to all 11 threat agents (6 STRIDE + 5 AI) or scoped to AI agents only? — product-manager — 2026-04-23 — Open (P1 leans toward all 11 for completeness)
- [ ] Should pattern category surface in MAESTRO infographic templates (Feature 091 stack and heatmap)? — product-manager — 2026-04-23 — Open (P1; additive enhancement)
- [ ] How should `agentic_pattern: multiple` be presented in the threat report narrative — listed under all matching patterns, or under a dedicated "Multi-Pattern Findings" subsection? — product-manager — 2026-04-23 — Open

### Technical Questions (deferred to `/aod.plan`)
- [ ] Which of the four FR-2 mechanism options (A/B/C/D) should ADR-026 select? — architect — `/aod.plan` — Open (PRD recommendation: Option C hybrid synthesis; Option D is the lightest alternative if keyword-driven classification is sufficient)
- [ ] Should the schema bump be minor (1.3 → 1.4, additive enum-typed field) or major (2.0, new required field)? ADR-026 must extend the Feature 136 enum-rename minor-bump rule to cover new enum-typed field additions — or justify the major bump. — architect — `/aod.plan` — Open
- [ ] If Option B (new cross-cutting agent) is chosen, should it use `category: agentic` (reusing the existing AG enum) or a new `category: agentic-pattern` value? How does deduplication interact with Section 4a intra-component correlation? — architect — `/aod.plan` — Open
- [ ] If Option C (post-hoc synthesis) is chosen, where in the pipeline does it run — Phase 3.5 alongside cross-layer chains, a separate Phase 3.6, or merged into Phase 3.5? — architect — `/aod.plan` — Open
- [ ] If Option D (orchestrator-side classification) is chosen, can keyword-only classification adequately detect Agent Collusion (which typically requires reasoning across multiple findings)? — architect — `/aod.plan` — Open
- [ ] Should the pattern classification predicate be encoded as a lookup table (per Feature 141 transition table precedent) or as per-pattern detection rules in the shared reference? — architect — `/aod.plan` — Open
- [ ] Path 1 (extend agentic-app), Path 2 (new 7th example), or Path 3 (defer un-demonstrable patterns) for FR-7? — architect with team-lead schedule input — `/aod.plan` Wave 0 — Open

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- GitHub Issue: [#142](https://github.com/davidmatousek/tachi/issues/142)
- Parent Issue: [#136](https://github.com/davidmatousek/tachi/issues/136) (MAESTRO framework compliance)

### Related PRDs
- [PRD 084: MAESTRO Layer Mapping](084-maestro-layer-mapping-2026-04-07.md) — taxonomy overlay this feature extends
- [PRD 091: MAESTRO Infographic Templates](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md) — MAESTRO visualization precedent
- [PRD 136: MAESTRO Canonical Layer Correctness](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — corrected layer names
- [PRD 141: MAESTRO Cross-Layer Attack Chains](141-maestro-cross-layer-attack-chains-2026-04-12.md) — Phase 2 architectural precedent (post-hoc correlation)
- [PRD 143: MAESTRO AIVSS Evaluation ADR](143-maestro-aivss-evaluation-adr-2026-04-14.md) — Phase 4 compliance posture
- [PRD 144: NIST AI RMF Evaluation ADR](144-nist-ai-rmf-evaluation-adr-2026-04-15.md) — Phase 5 compliance posture
- [PRD 015: Threat Report & Attack Trees](015-threat-report-agent-attack-trees-2026-03-23.md) — narrative generation patterns
- [PRD 082: Threat Agent Skill References](082-threat-agent-skill-references-2026-04-11.md) — lean agent + skill reference pattern

### Technical Documentation
- [ADR-019: Shared Cross-Agent Definitions](../../architecture/02_ADRs/ADR-019-shared-definitions-and-model-field-governance.md) — shared reference convention
- [ADR-020: MAESTRO Layer Classification](../../architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — current MAESTRO architecture (to be extended for Phase 3)
- [ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF](../../architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) — determinism constraint
- [ADR-023: Threat Agent Skill References Pattern](../../architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) — lean agent shape (relevant if Option B chosen)
- ADR-026 (proposed): Pattern Classification Mechanism — to be created during `/aod.plan` per FR-8

### External Resources
- [CSA Blog: Agentic AI Threat Modeling Framework — MAESTRO (2025-02-06)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- [Snyk Labs: MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems](https://labs.snyk.io/resources/maestro-threat-modeling/) — enumerates all six canonical patterns
- [Practical DevSecOps: MAESTRO — An Agentic AI Threat Modeling Framework](https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/)

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-04-16 | Closes final structural gap in MAESTRO compliance umbrella; correctly scoped P0 detection for three previously-uncovered patterns |
| Architect | architect | Approved with Concerns | 2026-04-16 | 1 BLOCKING addressed inline, 5M/5L; FR-2 expanded to 4 options including new Option D; M1-M5 mediums resolved in PRD body |
| Team Lead | team-lead | Approved with Concerns | 2026-04-16 | 6-10d realistic (Option C preferred for schedule); 4-5 waves, 3-track parallel in Wave 0 and Wave 2; agentic-app extension budgeted as planned scope |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-16 | product-manager | Initial PRD draft |
