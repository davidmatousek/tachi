---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-16
    status: APPROVED
    notes: "20/20 spec FRs covered without silent omissions; 6/6 user stories preserved 1:1; Option C selection aligns with PRD recommendation + team-lead schedule recommendation; four-option ADR-026 trade-off symmetric across the three required axes (ownership / write-back / regression footprint); Path 1 selected for FR-15 with 1-2h budget per PRD planned scope. P1 deferrals (MAESTRO infographics + compensating-controls recommendations) are constitutionally sound — both are spec-explicit Should-Have not Must-Have. Backward compatibility commitments match FR-016/FR-017/SC-004 exactly. Schema versioning rule extension (3-condition test) captures right invariants. 11/11 PRD open questions resolved with product-acceptable resolutions. 0 BLOCKING / 0 MEDIUM / 3 LOW polish items (P1 follow-up Issue filing, Wave 4 idempotence test, Multi-Agent Detection Rate measurement plan)."
  architect_signoff:
    agent: architect
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "Option C in ADR-026 is sound across all three axes; A/B/D rejections hold up including Option D Agent Collusion counter-argument. Phase 3.6 placement after Phase 3.5 preserves Feature 141 backward compat. ADR-021 determinism, ADR-023 11-agent stabilization, ADR-019 shared-reference governance, Constitution Principle III backward-compat all honored. 3 MEDIUM concerns RESOLVED INLINE: (MED-1) ADR-026 Decision section now formalizes Governance Rule for Future Post-Hoc Synthesis Phases (write-back vs aggregate model); (MED-2) data-model.md now enumerates explicit component_type token list (4 tokens) and topology indicator list (4 indicators) — Wave 0 implementation has finite token list source of truth; (MED-3) net-new finding ID prefix changed from AGENTIC-PATTERN-NN to AGP-NN (3-letter prefix aligned with existing 1-4 letter convention); finding.yaml id.pattern regex extension scheduled for Wave 0. 8 LOW polish items remain for tasks.md / Wave-level implementation."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MAESTRO Phase 3 — Agentic Threat Pattern Expansion

**Branch**: `142-maestro-agentic-pattern-expansion` | **Date**: 2026-04-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/142-maestro-agentic-pattern-expansion/spec.md`

## Summary

Add a post-detection pattern synthesis phase (Phase 3.6) to the orchestrator pipeline that assigns the new `agentic_pattern` enum field on the deduplicated finding IR using a deterministic classification engine. The engine reads two inputs — finding content (descriptions, target component, STRIDE category, MAESTRO layer) and architectural context (multi-agent topology, persistent-state indicators, inter-agent communication channels) — and applies a rule-based lookup table to assign one of six canonical CSA MAESTRO pattern values (or `none` / `multiple`). For the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack), the synthesis phase MAY also generate net-new findings using the same deterministic rules.

**Mechanism Decision**: **Option C (Hybrid Post-Hoc Synthesis)** — selected during this planning step and locked in **ADR-026**. Rationale below; full ADR at `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`.

Outputs propagate through the entire pipeline: the new `agentic_pattern` column appears in threats.md (after Category, before Component) with conditional Section 4b "Findings by Agentic Pattern"; the threat report adds a conditional "Agentic Pattern Analysis" section after Cross-Layer Attack Chains (Feature 141); SARIF receives `maestro-pattern:<name>` tags matching the existing `maestro-layer:` convention. All output is conditional on the multi-agent gate predicate (FR-006) being satisfied — the 5 non-multi-agent baselines produce zero new pattern findings and remain byte-identical under SOURCE_DATE_EPOCH=1700000000.

## Technical Context

**Language/Version**: Python 3.11 (extraction scripts), Typst (PDF templates), Markdown (agent files, schemas, ADRs)
**Primary Dependencies**: stdlib-only Python scripts (zero runtime dependencies per project constraint), Typst CLI, mmdc (Mermaid CLI, hard prerequisite per ADR-022 — already installed for Feature 141 chain diagrams)
**Storage**: File-based (markdown artifacts, YAML schemas)
**Testing**: pytest >= 8.0 (established in Feature 128), backward-compatibility PDF baselines under SOURCE_DATE_EPOCH=1700000000 (ADR-021)
**Target Platform**: Local CLI (any OS with Python 3.11+, Typst, optional mmdc)
**Project Type**: Knowledge system / methodology template (no application code)
**Performance Goals**: Pattern synthesis phase < 10s for architectures with < 100 findings (matches Feature 141 Phase 3.5 budget)
**Constraints**: Deterministic output (ADR-021), backward compatible (Constitution Principle III), zero new runtime dependencies, multi-agent gate predicate enforced at synthesis step (FR-006)
**Scale/Scope**: 6 example architectures, 50-70 findings typical per architecture, 6 canonical pattern values + `none` + `multiple`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Multi-agent gate predicate (FR-006) ensures 5 non-multi-agent baselines produce zero pattern findings. PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000. Schema bump 1.3 → 1.4 is additive (default `none`). Pre-Feature-142 baseline findings parse correctly with default `agentic_pattern: none` (FR-017). |
| VI. Testing Excellence | PASS | pytest unit tests for synthesis engine + classification rules; integration tests for parser + SARIF emission; backward-compat PDF baselines per ADR-021; new tests for multi-agent gate predicate enforcement. |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | 13-item DoD checklist in PRD lines 545-559; all items map to testable tasks. |
| IX. Git Workflow (NON-NEGOTIABLE) | PASS | Feature branch `142-maestro-agentic-pattern-expansion`; conventional commits; PR before merge. |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | PASS | PRD 142 approved (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS). Spec approved (PM APPROVED unconditional). ADR-026 authored as part of this plan documenting Option C selection. |

No violations. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```
specs/142-maestro-agentic-pattern-expansion/
├── plan.md                  # This file
├── research.md              # Codebase + architecture research (completed during /aod.spec)
├── data-model.md            # Pattern entity model and schema design
├── checklists/
│   └── requirements.md      # Spec quality checklist
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
# Files modified or created by this feature:

.claude/agents/tachi/
└── orchestrator.md                              # Phase 3.6 insertion (pattern synthesis)
                                                  # Phase 1 multi-agent gate predicate evaluation
                                                  # Phase 3.6 invocation point after Phase 3.5

.claude/agents/tachi/
└── threat-report.md                             # New conditional section: Agentic Pattern Analysis
                                                  # (placed after Cross-Layer Attack Chains, before Findings Detail)

.claude/skills/tachi-shared/references/
├── maestro-agentic-patterns-shared.md           # NEW: 6 pattern definitions + coverage mapping table
└── maestro-layers-shared.md                     # No-op (no edit needed; pattern field independent of layer)

.claude/skills/tachi-orchestration/references/
├── dispatch-rules.md                            # Update: Phase 3.6 documentation
└── output-schemas.md                            # Update: agentic_pattern field on finding IR

.claude/skills/tachi-threat-reporting/references/
└── narrative-templates.md                       # Update: Agentic Pattern Analysis section template

schemas/
└── finding.yaml                                 # Update: add agentic_pattern enum field, version 1.3 → 1.4

scripts/
├── tachi_parsers.py                             # Update: parse_finding_pattern(), parse_threats_findings()
└── extract-report-data.py                       # Update: pattern data extraction for PDF report

templates/tachi/output-schemas/
├── threats.md                                   # Update: Pattern column + conditional Section 4b
└── threat-report.md                             # Update: schema_version 1.1 → 1.2; conditional pattern section

templates/tachi/security-report/
└── (no new Typst templates — patterns surface in narrative, not new full-bleed pages per Out-of-Scope)

.claude/commands/
├── tachi.threat-model.md                        # Update: Phase 3.6 invocation in pipeline description
└── tachi.security-report.md                     # No-op (pattern data flows through existing extraction)

docs/architecture/02_ADRs/
├── ADR-026-pattern-classification-mechanism.md  # NEW: Option C decision + 4-option trade-off
└── ADR-020-maestro-layer-classification.md      # Update: Revision History entry for Phase 3 completion

examples/
├── agentic-app/                                 # Pattern demonstration (architecture extended; regenerated)
│   ├── architecture.md                          # EXTENDED: +second cooperating agent, +learning loop, +inter-agent channel
│   └── threats.md                               # Regenerated with pattern column populated for ≥3 patterns
└── {web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/
    └── (regenerated with pattern column showing — for all findings; PDFs byte-identical)

tests/scripts/
├── test_pattern_synthesis.py                    # NEW: synthesis engine unit tests + multi-agent gate
├── test_pattern_classification_rules.py         # NEW: classification rules table validation
├── test_pattern_extraction.py                   # NEW: extract-report-data pattern extraction
├── test_finding_pattern_parser.py               # NEW: tachi_parsers.py pattern field parsing
└── test_backward_compatibility.py               # Update: pattern field default validation (FR-017)
```

**Structure Decision**: Extends existing project structure. No new directories created at the top level. All changes follow established Feature 082 / 141 / 084 patterns: orchestrator phase insertion in `.claude/agents/tachi/orchestrator.md`, shared reference in `.claude/skills/tachi-shared/references/`, schema update in `schemas/`, scripts in `scripts/`, output schema templates in `templates/tachi/output-schemas/`, tests in `tests/scripts/`. **Zero new top-level directories**. **Zero new agents** (Option C protects all 11 existing agents from regression).

## Components

### Component 1: Pattern Synthesis Engine (Orchestrator Phase 3.6)

**Location**: `.claude/agents/tachi/orchestrator.md` (Phase 3.6 insertion **after** Feature 141's Phase 3.5 cross-layer correlation, **before** Phase 4 assessment)

**Responsibility**: After Phase 3.5 cross-layer chain correlation completes, synthesize the `agentic_pattern` value for each deduplicated finding using a deterministic rule-based classification engine. The engine MAY also generate net-new findings for the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack) when the architecture meets the multi-agent gate predicate AND the rule table indicates a pattern that no existing finding represents.

**Input Contract**:
- Reads the **Phase 1 component inventory** with MAESTRO layer assignments + DFD types + agentic/llm category classification (from existing dispatch keywords)
- Reads the **data flow graph** (source → target component relationships)
- Reads the **deduplicated finding IR** from Phase 3 (post-dedup, post-Section-4a-correlation, post-Phase-3.5-chains)
- Loads `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` for the canonical pattern definitions, coverage mapping, and **classification rule table**
- Loads `.claude/skills/tachi-shared/references/maestro-layers-shared.md` for layer keyword reference (re-used; no edits)

**Output Contract**:
- **Modifies the deduplicated finding IR in-place**: every finding receives a populated `agentic_pattern` field (one of six canonical values, `none`, or `multiple`)
- **MAY append net-new findings** for previously-uncovered patterns when (a) the architecture satisfies the multi-agent gate predicate AND (b) the architectural context matches the rule for a pattern with no existing finding representative
- Sets `has-agentic-patterns` boolean (derived: true iff at least one finding has non-`none` pattern) consumed by Phase 5 (threat-report agent) for conditional section inclusion

**Independence Invariants**:
- **vs. Feature 141 Phase 3.5**: Pattern synthesis runs AFTER cross-layer chain correlation; chains and patterns are independent grouping mechanisms (a finding may participate in both). Phase 3.6 does NOT read or modify `attack-chains.md` (FR-008).
- **vs. Section 4a intra-component correlation**: Pattern field is finding-level metadata; Section 4a is a presentation-time grouping mechanism. They are orthogonal.
- **vs. existing 11 agents**: Phase 3.6 reads the deduplicated finding IR but does NOT invoke or modify any threat-detection agent. The 5 AI agents (prompt-injection, tool-abuse, agent-autonomy, data-poisoning, model-theft) and 6 STRIDE agents remain byte-identical (zero-edit invariant).

**Architectural Divergence from Feature 141 (Documented in ADR-026)**: Phase 3.5 produces an aggregate artifact (`attack-chains.md`) WITHOUT modifying the finding IR. Phase 3.6 modifies the finding IR in-place (write-back). This is a deliberate divergence because pattern is a finding-level field that MUST live on the finding for downstream consumers (SARIF tags, threats.md column, threat-report subsections) to access it via the existing parsing path. The write-back is contained to a single new phase and is the lowest-cost way to surface a finding-level field without reopening the 11-agent stabilization.

**Multi-Agent Gate Predicate (FR-006 enforcement)**: Before any non-`none` pattern is assigned (whether to an existing finding or as a net-new finding), the engine evaluates the predicate against the architecture description:
1. **Condition (a)**: count components classified as `agentic` or `llm` category in the Phase 1 dispatch keywords → require ≥2
2. **Condition (b)**: count inter-component data flows where BOTH source and target components are `agentic`/`llm` → require ≥1
3. **Condition (c)**: case-insensitive substring search on the architecture description for keywords: `multi-agent`, `swarm`, `supervisor`, `delegation`, `agent mesh` → require ≥1 match

If **none** of (a), (b), (c) hold: every finding receives `agentic_pattern: none` and Phase 3.6 emits zero net-new findings. The `has-agentic-patterns` boolean is set to `false`.

If **at least one** of (a), (b), (c) holds: the classification rule table is evaluated for each finding (existing or candidate net-new).

**Classification Rule Table Design** (lives in `maestro-agentic-patterns-shared.md`):

The rule table is structured as a list of rule entries. Each rule entry has the form:

```
Rule R-NN:
  pattern: <one of six canonical pattern names>
  match_conditions:
    - finding.category in [<categories>]                      # optional
    - finding.maestro_layer in [<layers>]                     # optional
    - finding.target_component matches <regex on type or name>  # optional
    - architecture has <topology indicator>                  # optional
    - finding.description contains <token list (any)>        # optional
  generates_finding_when_no_match: true | false              # for previously-uncovered patterns
  generation_template: <markdown template>                    # required if generates_finding_when_no_match: true
```

The engine evaluates rules in priority order (most specific first per ADR-020 specificity gradient) and assigns the first matching pattern. Findings matching no rule receive `agentic_pattern: none`. Findings matching rules for two or more patterns equally (rare) receive `agentic_pattern: multiple` — the rule precedence table includes a tie-breaker per FR-007 ADR.

**Rule Examples** (illustrative; full table in shared reference):

- **R-01 (Agent Collusion)**: `category in [agentic, llm] AND architecture has ≥2 agentic components AND ≥1 inter-agent data flow → pattern: agent_collusion`
- **R-02 (Temporal Attack)**: `architecture has fine-tuning pipeline OR persistent agent memory OR long-running learning loop component → pattern: temporal_attack` (and `generates_finding_when_no_match: true` because no existing agent detects this)
- **R-03 (Emergent Behavior)**: `category in [agentic, llm] AND architecture has ≥2 agentic components AND finding.description contains [cascade, unpredictable, interaction, emergent] → pattern: emergent_behavior`
- **R-04 (Trust Exploitation)**: `category in [spoofing, agentic] AND architecture has ≥2 agentic components → pattern: trust_exploitation`
- **R-05 (Communication Vulnerability)**: `category in [agentic, info-disclosure] AND finding.target_component is inter-agent channel → pattern: communication_vulnerability` (where `agentic` is the finding category enum value produced by the tool-abuse detection agent per schemas/finding.yaml)
- **R-06 (Resource Competition)**: `category in [denial-of-service, agentic] AND architecture has ≥2 agentic components AND finding.description contains [resource, monopol, competition, priority] → pattern: resource_competition`

The rule table is **deterministic by construction** (per ADR-021): each rule is a pure function of finding fields and architectural metadata; no LLM judgment is involved.

**Net-New Finding Generation**:
- Only patterns with `generates_finding_when_no_match: true` may emit net-new findings
- Initially scoped to: Agent Collusion, Temporal Attack, Emergent Behavior (the three previously-uncovered patterns per PRD)
- Generation triggers when: architecture satisfies the multi-agent gate predicate AND the architectural context matches the rule's `match_conditions` AND no existing finding already carries that pattern label
- Generated finding format: standard finding IR with `id` prefix `AGP-` + sequence (e.g., `AGP-01`, `AGP-02`) — aligned with existing 1-4 letter prefix convention (S, T, R, I, D, E, AG, LLM); `finding.yaml` `id.pattern` regex extended in Wave 0 to accept the new prefix. `category: agentic`, `agentic_pattern` set to the pattern name, `risk_level` defaulted to `Medium` (analyst can re-rate), description from the rule's `generation_template`, target component = first matching component in the architecture
- Net-new findings flow through downstream phases identically to detection-tier findings (no special handling required by parser, threat-report, SARIF emitter)

### Component 2: Shared Reference — Agentic Patterns

**Location**: `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md`

**Content** (per FR-001, FR-002):
- YAML frontmatter: type, version (1.0.0), consumers (orchestrator Phase 3.6, threat-report agent)
- **Section 1: Six canonical pattern definitions** — one subsection per pattern (Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition). Each subsection contains: definition (1-2 sentences sourced from CSA blog 2025-02-06), 2-3 representative attack vectors, detection criteria (architectural preconditions + keyword indicators), CSA citation
- **Section 2: Coverage mapping table** (FR-002) — six rows, three columns: Currently Covered By, Coverage Strength (Full / Partial / None — Coverage Required), Gap (1-sentence justification when Partial). Initial assessment matches PRD lines 215-222.
- **Section 3: Classification rule table** — the rule entries (R-01 through R-06+) consumed by Phase 3.6 synthesis engine
- **Section 4: Multi-agent gate predicate definition** — formal specification of the three OR conditions (a/b/c) per FR-006, with worked examples on the 6 example architectures showing which evaluate to true/false

**Consumed by**: Orchestrator (Phase 3.6 synthesis), threat-report agent (Agentic Pattern Analysis section narrative), tachi-shared reference governance per ADR-019

### Component 3: Finding Schema Extension

**Location**: `schemas/finding.yaml` (update; version 1.3 → 1.4)

**Schema change**:
```yaml
# schemas/finding.yaml addition (illustrative — see data-model.md for full spec)
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
    Field is required after Feature 142 ships; default 'none' makes
    backward compatible for findings without pattern relevance.
```

**Versioning rationale (ADR-026 Decision)**: **Minor bump 1.3 → 1.4** (additive new enum-typed field). The Feature 136 enum-VALUE-rename minor-bump rule is extended in ADR-026 to cover NEW enum-typed field additions where (a) the field is additive, (b) the field has a default value enabling backward compatibility, and (c) the schema shape and existing required fields are unchanged. All three conditions hold. A major bump would be unjustified — pre-Feature-142 parsers ignore unknown fields gracefully (FR-017), and consumers reading the new field gracefully default to `none` for missing values.

### Component 4: threats.md Output Extension

**Location**: `templates/tachi/output-schemas/threats.md`

**Changes** (per FR-009, FR-010):
- **Section 7 findings table**: New Pattern column inserted between Category and Component. Empty values (`agentic_pattern: none`) display as `—`. Column always renders for consistent table shape across architectures.
- **Section 4b (NEW conditional)**: "Findings by Agentic Pattern" — groups findings by canonical pattern. Each group shows pattern name, finding count, finding IDs. Section is rendered only when `has-agentic-patterns: true` (at least one finding has non-`none` pattern). Section position: after Section 4a (intra-component correlation), before Section 5 (existing).
- Section 4b complements (does not replace) Section 4a. Independence invariant from spec edge case 6 preserved.

### Component 5: Threat Report Agentic Pattern Analysis Section

**Location**: `.claude/agents/tachi/threat-report.md` (new conditional section), `.claude/skills/tachi-threat-reporting/references/narrative-templates.md` (new section template)

**Design** (per FR-011, FR-012, FR-013):
- New section "Agentic Pattern Analysis" placed after Cross-Layer Attack Chains (Feature 141 Section 6) and before Findings Detail
- **Section number is grep-determined at code time** (not hardcoded per FR-011) — implementation reads the current threat-report.md output schema, counts existing sections, and assigns the next sequential number
- One subsection per pattern with non-zero finding count
- Subsection ordering: max severity descending, then finding count descending (matches Feature 141 Section 6 chain ordering convention)
- Each subsection contains: (a) pattern name + 1-sentence canonical definition (from shared reference), (b) Critical/High/Medium/Low finding counts, (c) 100-200 word narrative describing manifestation in this architecture, (d) impacted finding IDs with cross-references
- Zero-finding subsections suppressed entirely (not rendered empty)
- Full section omitted when `has-agentic-patterns: false`

**Narrative generation**: Follows existing Feature 015 (threat report) narrative pattern — load the `maestro-agentic-patterns-shared.md` shared reference on-demand, read the canonical definition, synthesize an architecture-specific manifestation narrative using the finding descriptions and target components. The threat-report agent MAY cross-reference Cross-Layer Attack Chain membership in the narrative (e.g., "Finding F-12 (Agent Collusion) participates in Chain CHAIN-002") but does NOT modify the chain artifact (FR-008 invariant preserved).

### Component 6: SARIF Pattern Tag Propagation

**Location**: `.claude/agents/tachi/orchestrator.md` (SARIF emission step) + extension to existing maestro-layer tagging logic

**Design** (per FR-014):
- For each finding with `agentic_pattern` not equal to `none`, append a tag to `result.properties.tags` of the form `maestro-pattern:<pattern_name>` (e.g., `maestro-pattern:agent_collusion`)
- Format MUST match the existing `maestro-layer:<L#>` convention exactly: lowercase namespace, colon-separator, no quoting, no spaces
- Findings with `agentic_pattern: none` MUST NOT receive a `maestro-pattern:` tag (avoiding noise)
- Implementation reuses the existing maestro-layer tagging code path — same insertion point in the orchestrator's SARIF emission step

**Verification step**: Implementation grep-checks the existing `maestro-layer:` tagging logic in the orchestrator before adding the pattern tag, and adds an explicit unit test that verifies format parity.

### Component 7: Example Architecture Extension (agentic-app)

**Location**: `examples/agentic-app/architecture.md`

**Path Decision**: **Path 1 (extend agentic-app)** — selected during this planning step per FR-015 and PRD FR-7 Path 1/2/3 trade-off. Rationale:
- Path 1 reuses the demonstrated Feature 141 cross-layer chain test surface; agentic-app is the canonical multi-agent demonstration architecture
- Path 2 (build a new 7th example) would duplicate Feature 141's setup investment and add maintenance burden for a single feature
- Path 3 (defer un-demonstrable patterns) would leave the feature incomplete and undermine SC-009

**Architecture extensions** (added to the existing 7-component architecture):
- **+ Second LLM Agent**: a peer agent (named "Specialist Agent") cooperating with the existing LLM Agent Orchestrator via a new inter-agent communication channel — exercises **Agent Collusion** + **Communication Vulnerability** + **Trust Exploitation** patterns
- **+ Long-running Learning Loop**: a fine-tuning subsystem that consumes Audit Logger output to retrain the LLM agents periodically — exercises **Temporal Attack** pattern (sleeper agent insertion via training data poisoning)
- **+ Inter-agent Communication Channel**: a message bus or shared memory between the two agents — exercises **Communication Vulnerability** + **Resource Competition** patterns

**Result**: Extended agentic-app surfaces findings tagged with at least 3 of the 6 canonical patterns (Agent Collusion, Emergent Behavior, Temporal Attack — the three previously-uncovered) and likely 5-6 patterns total once the rule table evaluates the extended architecture.

**Architecture extension budget**: 1-2h (per PRD lines 356, 506-509 — already budgeted in PRD as planned scope, not contingency).

## Data Flow

```
Architecture Description + Components + Data Flows (Phase 1 output)
    │
    ▼
[Phase 1: MAESTRO Layer Classification] (existing, unchanged)
    │
    ▼
[Phase 2: Threat Agent Dispatch] (existing — 6 STRIDE + 5 AI agents, all UNCHANGED)
    │
    ▼
[Phase 3: Deduplication + Section 4a Correlation] (existing, unchanged)
    │
    ▼
[Phase 3.5: Cross-Layer Chain Correlation] (Feature 141, unchanged)
    │ Output: attack-chains.md (conditional)
    │
    ▼
[Phase 3.6: Pattern Synthesis Engine] (NEW — Feature 142)
    │ Reads: maestro-agentic-patterns-shared.md (rule table + multi-agent gate predicate)
    │ Reads: deduplicated finding IR (post-Phase 3.5)
    │ Reads: Phase 1 component inventory + data flow graph + agentic/llm category counts
    │
    │ Step 1: Evaluate multi-agent gate predicate (FR-006 conditions a/b/c)
    │   ├─ FALSE → assign agentic_pattern: none to all findings → exit
    │   └─ TRUE  → continue
    │
    │ Step 2: For each finding in IR:
    │   ├─ Evaluate classification rule table in priority order
    │   ├─ Assign first matching pattern (or 'multiple' on equal-priority match)
    │   └─ Default to 'none' if no rule matches
    │
    │ Step 3: For each rule with generates_finding_when_no_match: true:
    │   ├─ Check if any existing finding now carries this pattern
    │   ├─ If not AND architectural context matches → emit net-new finding
    │   └─ Append net-new findings to IR (with id prefix AGP-)
    │
    │ Step 4: Set has-agentic-patterns boolean (true iff any non-'none' pattern)
    │
    ▼
[Phase 4: Coverage Matrix + Risk Summary] (existing, unchanged — passively reads new pattern field)
    │
    ▼
[Phase 5: threat-report Agent + SARIF Emission] (UPDATED)
    │
    ├──► threats.md (NEW Pattern column, conditional Section 4b)
    │
    ├──► threat-report.md (NEW conditional Agentic Pattern Analysis section)
    │      │ Loads: maestro-agentic-patterns-shared.md (canonical definitions)
    │      │ Reads: deduplicated finding IR with agentic_pattern populated
    │      │ Conditional on: has-agentic-patterns boolean
    │
    └──► SARIF (NEW maestro-pattern:<name> tags on result.properties.tags)
           Conditional per finding: only when agentic_pattern != 'none'
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Pattern Synthesis Engine | Orchestrator agent (markdown instructions) | Matches existing pipeline phase pattern (Phase 3.5 precedent in Feature 141); no new runtime dependency |
| Pattern Storage | Shared reference file (markdown) | Matches existing tachi-shared pattern (maestro-layers-shared.md, attack-chain-patterns-shared.md, severity-bands-shared.md); ADR-019 governance |
| Schema | YAML (finding.yaml v1.4) | Matches existing finding schema convention; minor bump per ADR-026 extending Feature 136 precedent |
| Pattern Parsing | Python 3.11 stdlib | Matches existing tachi_parsers.py pattern; zero-dependency constraint per Feature 128/136 |
| Output Templates | Markdown (threats.md, threat-report.md) | Matches existing output-schemas convention |
| SARIF Emission | Existing orchestrator SARIF step | Reuses existing maestro-layer:<L#> tagging code path; format parity verified by unit test |
| Testing | pytest >= 8.0 | Established in Feature 128; backward-compat baselines per ADR-021 |
| Example Architecture | Markdown (agentic-app extension) | Matches existing examples/ convention; 1-2h architectural extension budget |

## Testing Strategy

### Unit Tests (`tests/scripts/test_pattern_synthesis.py`)
- Multi-agent gate predicate evaluation: 8 architectures (6 baseline + 2 multi-agent variants) tested for predicate true/false outcome
- Classification rule precedence: synthetic findings tested against each rule in isolation + tied-priority cases (verify `multiple` assignment)
- Net-new finding generation: rule-by-rule trigger tests + suppression when existing finding already carries the pattern
- Determinism: same input twice produces byte-identical IR output (per ADR-021)
- Backward compatibility: pre-Feature-142 finding IR (no `agentic_pattern` field) parses with default `none` (FR-017)

### Rule Table Validation Tests (`tests/scripts/test_pattern_classification_rules.py`)
- All 6 patterns covered by at least one rule (no orphan patterns)
- Each rule's `match_conditions` uses only documented finding fields
- All rules with `generates_finding_when_no_match: true` have a non-empty `generation_template`
- Rule priority is total-ordered (no ambiguous priority on equal specificity)

### Integration Tests (`tests/scripts/test_pattern_extraction.py`)
- `extract-report-data.py` correctly extracts pattern field from threats.md
- Pattern subsection construction in threat-report
- SARIF tag emission format parity with `maestro-layer:` convention

### Parser Tests (`tests/scripts/test_finding_pattern_parser.py`)
- `parse_threats_findings()` returns pattern field on each finding object
- Default behavior on pre-Feature-142 baselines: pattern field defaults to `none`
- New `parse_finding_pattern()` helper handles all 8 enum values + null/missing

### Backward Compatibility Tests (`tests/scripts/test_backward_compatibility.py` — UPDATE)
- 5 baseline PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000 (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice)
- agentic-app intentionally regenerated as the multi-agent demo target
- Pre-Feature-142 baseline findings (without pattern field) parse correctly with default `none`
- Multi-agent gate predicate enforced: zero non-`none` patterns appear in any of the 5 baseline outputs

### Example Validation
- agentic-app extended architecture surfaces findings for at least 3 previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack)
- All 6 example pipelines run successfully end-to-end (no errors, no missing fields)
- Pattern column renders consistently across all 6 examples

## Security Considerations

- **No new external API calls** (rule-based classification is local; no LLM-judgment integration)
- **No new secrets or credentials**
- **Pattern data sensitivity**: Pattern field is metadata about finding categorization; same sensitivity level as existing finding fields (no elevation)
- **Net-new finding generation safety**: Generated findings use deterministic templates; no user-input echoing; no command-injection or template-injection surface (templates are static markdown in the shared reference)
- **SARIF tag injection**: Pattern names are constrained to enum values; no user-controlled tag construction (eliminates SARIF tag-spoofing surface)

## Migration & Backward Compatibility

- **Schema extension**: `finding.yaml` 1.3 → 1.4 — additive enum-typed field with default `none`. Pre-Feature-142 parsers ignore the new field gracefully.
- **Pre-Feature-142 baseline findings**: parse correctly with default `agentic_pattern: none` (FR-017). Validated by new test in `test_backward_compatibility.py`.
- **5 non-multi-agent baseline PDFs**: byte-identical under SOURCE_DATE_EPOCH=1700000000 (per ADR-021). Multi-agent gate predicate (FR-006) ensures zero new pattern findings in these architectures, so the threats.md table renders the new Pattern column as `—` for all rows and Section 4b is suppressed entirely.
- **agentic-app**: intentionally regenerated as the multi-agent demonstration target (consistent with Feature 141 / 136 convention — 5-of-6 byte-identical, 1-of-6 regenerated)
- **Pipeline shape**: Phase 3.6 is additive — existing phases 1-3.5 unchanged; Phase 4-5 passively read the new pattern field
- **Existing 11 threat-detection agents (6 STRIDE + 5 AI)**: ZERO edits — Option C protects all 11 agents from regression (validates SC against Feature 082 stabilization)
- **Cross-layer chain artifact (`attack-chains.md`)**: ZERO edits — pattern data placement invariant (FR-008) preserves Feature 141 artifact independence
- **Existing `maestro-layer:` SARIF tags**: unchanged — new `maestro-pattern:` tags coexist using identical format

## ADR Updates

### ADR-026: Pattern Classification Mechanism (NEW)

**Location**: `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`

**Status**: Proposed (during /aod.define) → **Accepted** (this planning step, 2026-04-16)

**Decision**: **Option C (Hybrid Post-Hoc Synthesis)** — selected from the four PRD FR-2 candidate mechanisms. Rationale and full alternatives analysis in the ADR.

**Three-axis evaluation** (matching PRD FR-2 axes):

| Option | Pattern Semantics Ownership | Schema Write-Back Location | Existing-Agent Regression Footprint |
|--------|------------------------------|------------------------------|--------------------------------------|
| A: Extend agents | Distributed across 5 AI agent files | Inline in agent finding construction | **HIGH** — reopens Feature 082 stabilization on all 5 AI agents |
| B: New cross-cutting agent | Centralized in new `tachi-agentic-patterns` agent | Inline in new agent's finding construction | MEDIUM — no agent edits, but deduplication ripple + Section 4a correlation + orchestrator coverage matrix + Risk Summary aggregation |
| **C: Hybrid post-hoc synthesis** | **Centralized in Phase 3.6 synthesis** | **Modifies finding IR after detection (write-back)** | **LOWEST — zero agent edits, zero deduplication impact** |
| D: Orchestrator-side classification | Centralized in orchestrator's classification step | Inline at finding emission (Phase 3 inheritance) | LOW — orchestrator-only edits; same shape as Feature 084/136 maestro_layer pattern |

**Why Option C selected**:
1. **Zero regression on the 11 existing detection agents** — explicit invariant from Option C analysis. Feature 082 just stabilized 11 agents under the lean+skill-references pattern (ADR-023). Reopening any of them carries unacceptable regression risk.
2. **Reuses Feature 141's Phase 3.5 architectural slot** — Phase 3.6 sits immediately after Phase 3.5 in the orchestrator pipeline. The architectural shape (post-detection synthesis) is proven by Feature 141. Adopters and implementers will recognize the pattern.
3. **Supports finding-content-based pattern detection** — Agent Collusion (PRD's hardest pattern) requires reasoning across multiple findings AND architectural context. Option C is the only mechanism that operates on the full deduplicated finding IR with full architectural context. Option D (keyword on component) cannot detect this; Options A/B distribute the responsibility and would each reinvent the architectural-context lookup.
4. **Determinism preserved** — the rule table is a pure function of finding fields and architectural metadata. No LLM judgment. ADR-021 invariant holds.
5. **Schedule-compatible** — Team-Lead PRD review explicitly recommends Option C for schedule (5-8d vs 8-12d for Option A).

**Why other options rejected**:
- **Option A**: HIGH regression footprint reopens Feature 082 stabilization (11-agent skill-references pattern just stabilized; ADR-023 explicitly warns against reopening). Distributed pattern semantics across 5 files invites inconsistency. Team-lead schedule penalty (8-12d).
- **Option B**: MEDIUM regression via deduplication ripple. Adding a new agent for a single new field is over-engineered when the field can be assigned post-hoc. Coverage matrix and Risk Summary aggregation logic must learn the new category. Higher cognitive cost for adopters reading the agent inventory.
- **Option D**: LOW regression but pure keyword-on-component classification cannot detect Agent Collusion (which requires reasoning across multiple findings, not just keywords on a single component target). Component-centric classification underclassifies finding-content-driven patterns. Net-new finding generation for previously-uncovered patterns is awkward in a component-centric phase.

**Architectural divergence from Feature 141 (acknowledged + accepted)**: Phase 3.5 produces an aggregate artifact WITHOUT modifying the finding IR. Phase 3.6 modifies the finding IR in-place (write-back). The divergence is deliberate: pattern is a finding-level field that MUST live on the finding for downstream consumers (SARIF tags, threats.md column, threat-report subsections) to access via the existing parsing path. The write-back is contained to a single new phase. This precedent is documented in ADR-026 to guide future similar decisions.

**Schema versioning rule extension**: ADR-026 extends the Feature 136 enum-VALUE-rename minor-bump rule (ADR-020 Revision History) to cover NEW enum-typed field additions where (a) the field is additive, (b) the field has a default value enabling backward compatibility, and (c) the schema shape and existing required fields are unchanged. Bump 1.3 → 1.4 is a minor bump (not major). All three conditions hold for `agentic_pattern`.

**Cross-references**: ADR-019 (shared cross-agent definitions — governs `maestro-agentic-patterns-shared.md`), ADR-020 (MAESTRO layer classification — Phase 3 completion), ADR-021 (determinism — pattern classification rule-based), ADR-023 (lean agent skill-references — Option B rejection rationale), Feature 141 PRD (Phase 3.5 cross-layer correlation — architectural precedent), Feature 084/136 PRDs (MAESTRO layer keyword classification — Option D comparison)

### ADR-020: MAESTRO Layer Classification (UPDATE — Revision History entry)

**Location**: `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` (existing — append Revision History entry)

**New Revision History entry**:
> **2026-04-16 (Feature 142)**: Phase 3 — Agentic Pattern Expansion. Adds the `agentic_pattern` enum field to the finding IR, surfacing the six canonical CSA MAESTRO agentic patterns (Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition). Pattern classification mechanism documented in ADR-026 (Hybrid Post-Hoc Synthesis — Phase 3.6 in the orchestrator pipeline). MAESTRO compliance umbrella (Issue #136) is now structurally complete: Phase 1 (Features 084 / 136 — passive layer overlay), Phase 2 (Feature 141 — cross-layer chains), Phase 3 (this feature — agentic patterns), Phase 4 (Feature 143 — AIVSS posture ADR-024), Phase 5 (Feature 144 — NIST AI RMF posture ADR-025).

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Multi-agent gate predicate false negatives (legitimate multi-agent architecture incorrectly excluded) | Low | Medium | Three OR conditions (a/b/c) provide three independent escape hatches. Worked examples in `maestro-agentic-patterns-shared.md` Section 4 cover the 6 example architectures. |
| Multi-agent gate predicate false positives (single-agent architecture incorrectly admitted) | Low | High | All three OR conditions explicitly require multi-agent indicators. Validated against 5 non-multi-agent baseline architectures (zero pattern findings expected per FR-016 / SC-003). |
| Rule table coverage gaps (a real pattern manifestation matches no rule) | Medium | Medium | Rules R-01 through R-06 cover the six canonical patterns; additional rules can be added in follow-up features. Pattern field defaults to `none` for unmatched findings (graceful degradation). |
| Net-new finding generation duplicates existing detection-tier findings | Low | Medium | Generation step explicitly checks `if any existing finding now carries this pattern → skip net-new generation`. Test coverage in `test_pattern_synthesis.py`. |
| Phase 3.6 increases orchestrator context window pressure | Medium | Medium | Phase 3.6 reads only the deduplicated finding IR (not raw agent output) plus the rule table (~3-5K tokens) and architectural metadata (~1-2K tokens). Total context overhead ~5-7K tokens per architecture. Comparable to Feature 141 Phase 3.5. |
| agentic-app architecture extension introduces drift in non-pattern findings | Medium | Low | Architecture extension affects only the new components (second agent, learning loop, inter-agent channel); existing 7 components produce the same baseline findings. agentic-app is intentionally regenerated (excluded from byte-identical baseline test per Feature 141 convention). |
| Pattern field surfacing breaks existing parsers | Low | High | FR-017 explicit baseline parser regression test; pre-Feature-142 baselines parse with default `none`. Schema bump rationale (ADR-026) documents the additive-only contract. |
| Subsection ordering ambiguity in threat-report (two patterns equal max severity AND equal finding count) | Low | Low | Tertiary sort key: pattern enum order (agent_collusion < emergent_behavior < ... < resource_competition). Documented in narrative-templates.md. |

## Open Questions Resolution (from Spec / PRD)

The PRD (lines 565-577) lists open questions deferred to /aod.plan. Resolutions captured here:

| PRD Open Question | Resolution |
|-------------------|------------|
| Which mechanism (A/B/C/D)? | **Option C (Hybrid Post-Hoc Synthesis)** — locked in ADR-026, this planning step |
| Schema bump minor or major? | **Minor (1.3 → 1.4)** — additive enum-typed field with default; ADR-026 extends Feature 136 minor-bump rule |
| If Option C: Phase 3.5 extension or Phase 3.6? | **New Phase 3.6** — independent phase preserves Feature 141 Phase 3.5 contract and Section 4a/3.5 independence invariant |
| Path 1, 2, or 3 for FR-7 example? | **Path 1 (extend agentic-app)** — selected this planning step; 1-2h budget per PRD planned scope |
| Coverage table scope (5 AI agents only or all 11)? | **All 11 agents** (P1 from spec scope boundaries — included in this plan as Should-Have, deliverable in `maestro-agentic-patterns-shared.md` Section 2) |
| Pattern in MAESTRO infographics (Feature 091)? | **Deferred** — P1 from spec; rolls forward to follow-up feature to keep this feature scope focused |
| Pattern-to-control recommendations in compensating-controls.md? | **Deferred** — P1 from spec; rolls forward to follow-up feature |
| `multiple` presentation in threat-report? | **Listed under all matching patterns AND under a "Multi-Pattern Findings" subsection** if any exist; subsection ordered first (most architectural significance) |
| If Option B: category reuse vs new value? | N/A (Option C selected) |
| If Option D: keyword sufficiency for Agent Collusion? | N/A (Option D rejected — keyword insufficiency is a key reason for Option C selection) |
| Rule encoding: lookup table vs per-pattern detection rules in shared reference? | **Lookup table** (consistent with Feature 141 transition table precedent) — single classification rule table in `maestro-agentic-patterns-shared.md` Section 3 |

## Implementation Wave Structure (Preview for /aod.tasks)

The implementation can be parallelized across 4-5 waves. Detailed task breakdown is /aod.tasks output; this preview ensures the plan is feasibility-validated before triple sign-off.

| Wave | Tasks (high-level) | Parallelism | Estimated Effort |
|------|---------------------|-------------|-------------------|
| **Wave 0**: Foundations (3-track parallel) | (a) ADR-026 authored + accepted, (b) `maestro-agentic-patterns-shared.md` drafted with definitions + coverage table + rule table + multi-agent gate predicate spec + explicit component_type and topology token lists (per architect MED-2), (c) `schemas/finding.yaml` bumped 1.3 → 1.4 with `agentic_pattern` enum AND `id.pattern` regex extended to accept `AGP-` prefix (per architect MED-3) | 3-track parallel | 1-1.5d |
| **Wave 1**: Synthesis Engine | Orchestrator Phase 3.6 implementation (multi-agent gate evaluation + classification rule application + net-new finding generation) | Sequential after Wave 0 | 1-2d |
| **Wave 2**: Output Surfacing (3-track parallel) | (a) threats.md template extension (Pattern column + Section 4b), (b) threat-report agent + narrative templates extension, (c) SARIF tagging with format-parity verification | 3-track parallel after Wave 1 | 1-1.5d |
| **Wave 3**: agentic-app Extension + Example Regeneration | (a) agentic-app architecture.md extended (+second agent +learning loop +inter-agent channel), (b) all 6 examples regenerated, (c) backward-compatibility baselines confirmed for 5-of-6 | Sequential after Wave 2 | 1-1.5d |
| **Wave 4**: Tests + ADR-020 Update + Documentation | (a) 5 new test files written + existing test_backward_compatibility.py updated, (b) ADR-020 Revision History entry, (c) README/docs updates | Parallel after Wave 3 | 1-1.5d |

**Total wave-budget effort**: 5-8 days (consistent with Team-Lead PRD review estimate for Option C). Wave 0 + Wave 4 can overlap with the agentic-app extension prep work (Wave 3 prep).

**Dependencies cleanly resolved**:
- Wave 0 depends only on existing repository state
- Wave 1 depends on Wave 0 (synthesis engine reads the rule table from `maestro-agentic-patterns-shared.md`)
- Wave 2 depends on Wave 1 (output surfacing reads pattern field on findings)
- Wave 3 depends on Wave 2 (regeneration produces output that the new templates render)
- Wave 4 depends on Wave 3 (backward-compat tests need regenerated baselines for comparison)
