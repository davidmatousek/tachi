# ADR-026: Agentic Pattern Classification Mechanism

**Status**: Accepted
**Date**: 2026-04-16
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 142 (MAESTRO Phase 3 — Agentic Threat Pattern Expansion)
**Related ADRs**: [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (shared cross-agent definitions), [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO layer classification — extended for Phase 3 here), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (lean agent + skill-references pattern)

---

## Context

Tachi's six-phase agentic-AI threat-modeling pipeline detects threats organized around STRIDE-per-element (6 STRIDE agents) and AI-domain analogues (5 AI agents covering Prompt Injection, Tool Abuse, Agent Autonomy, Data Poisoning, Model Theft). This 11-agent detection tier was stabilized in Feature 082 under the lean + skill-references pattern (ADR-023).

The **CSA MAESTRO framework** (Multi-Agent Environment, Security, Threat, Risk, and Outcome — published February 2025 at [`https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro`](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)) defines six canonical cross-cutting agentic threat patterns that emerge from multi-agent coordination, persistent state, and inter-agent communication. These patterns are distinct from STRIDE-per-element threats:

1. **Agent Collusion** — multiple compromised agents coordinating (DDoS, info gathering, policy circumvention)
2. **Emergent Behavior** — exploiting unpredictable behaviors arising from agent interactions (cascade failures, behavioral manipulation)
3. **Temporal Attacks** — sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation
4. **Trust Exploitation** — identity spoofing between agents, reputation manipulation, trust chain attacks
5. **Communication Vulnerabilities** — inter-agent message interception, protocol manipulation, routing attacks
6. **Resource Competition** — resource monopolization, priority manipulation, coordination disruption between agents

Of the six, three are **previously uncovered** by tachi's existing 11 detection agents: Agent Collusion, Emergent Behavior (only partial coverage via agent-autonomy cascade detection), and Temporal Attacks (no detection). The other three are partially covered by existing STRIDE+AI agents but lack the multi-agent context (Trust Exploitation requires inter-agent identity context, Communication Vulnerabilities require inter-agent messaging context, Resource Competition requires inter-agent context).

The MAESTRO compliance umbrella (Issue [`#136`](https://github.com/davidmatousek/tachi/issues/136)) has progressed through Phase 1 (Features 084 / 136 — passive layer overlay), Phase 2 (Feature 141 — cross-layer chains), Phase 4 (Feature 143 — AIVSS posture ADR-024), and Phase 5 (Feature 144 — NIST AI RMF posture ADR-025). Phase 3 — surfacing the canonical agentic patterns as named, filterable categories — is the final structural feature in the umbrella. PRD 142 ([`docs/product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md`](../../product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md)) was approved 2026-04-16 with PM APPROVED and Architect+Team-Lead APPROVED_WITH_CONCERNS.

PRD FR-2 enumerated **four candidate mechanisms** for assigning the new `agentic_pattern` enum field on findings:

- **Option A: Extend existing AI agents** — each of the 5 AI agents adds explicit pattern responsibility inline during detection
- **Option B: Add a new cross-cutting agent** (`tachi-agentic-patterns`) — a single new agent owns all six patterns
- **Option C: Hybrid post-hoc synthesis** — existing agents unchanged; a new synthesis phase runs after deduplication and assigns patterns based on finding content + architectural context
- **Option D: Orchestrator-side classification at finding emission** — the orchestrator assigns `agentic_pattern` at the same point it currently assigns `maestro_layer` (Feature 084/136 keyword-classification pattern)

Each option was evaluated on three axes:

1. **Pattern semantics ownership** — where does the canonical interpretation of each pattern live in the codebase?
2. **Schema write-back location** — where in the pipeline is the finding's `agentic_pattern` field written?
3. **Existing-agent regression footprint** — how many of the 11 stabilized detection agents are touched, with what risk?

This ADR records the chosen mechanism and its rationale.

### Constraints

- **Determinism (ADR-021)**: pattern classification must produce identical assignments for identical input — no LLM-judgment-based classification
- **Backward compatibility (Constitution Principle III, NON-NEGOTIABLE)**: 5 non-multi-agent baseline architectures must produce zero non-`none` patterns, with PDF outputs byte-identical under SOURCE_DATE_EPOCH=1700000000
- **Zero-regression on detection tier**: Feature 082 just stabilized the 11-agent skill-references pattern. Reopening any existing agent carries documented regression risk per ADR-023 sibling-pattern governance
- **Independence invariants from ADR-020 Phase 2**: pattern grouping and Cross-Layer Chain grouping (Feature 141) are independent mechanisms; pattern data must not extend `attack-chains.md`
- **Multi-agent gate predicate (FR-006)**: no non-`none` pattern may be assigned unless the architecture exhibits multi-agent indicators — the gate must apply regardless of which mechanism is selected
- **Schema versioning**: the Feature 136 minor-bump rule covered enum-VALUE renames on existing fields (`schemas/finding.yaml` 1.2 → 1.3). Adding a NEW enum-typed field is structurally distinct and requires this ADR to extend or explicitly diverge from that precedent

---

## Decision

We adopt **Option C — Hybrid Post-Hoc Synthesis** as the pattern classification mechanism for Feature 142 and all future agentic pattern extensions.

The implementation adds:

1. A new orchestrator pipeline phase **Phase 3.6** ("Pattern Synthesis Engine") that runs **after** Feature 141's Phase 3.5 cross-layer chain correlation and **before** Phase 4 assessment.
2. A new shared reference `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` containing the six canonical pattern definitions, the coverage mapping table (FR-002), the **classification rule table** consumed by Phase 3.6, and the multi-agent gate predicate specification (FR-006).
3. A new `agentic_pattern` enum field on `schemas/finding.yaml` (eight values: six canonical patterns plus `none` and `multiple`), with **schema_version bumped 1.3 → 1.4** under the extended minor-bump rule (see Schema Versioning Rule Extension below).
4. Phase 3.6 evaluates the multi-agent gate predicate against the architecture; if false, every finding receives `agentic_pattern: none` and the synthesis exits. If true, Phase 3.6 evaluates the classification rule table against each deduplicated finding (assigning the first matching pattern, or `multiple` on equal-priority match, or `none` if no rule matches), then optionally generates net-new findings for the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack) when no existing finding carries the pattern.
5. Downstream propagation: the new field is surfaced as a column in `threats.md` (after Category, before Component) with conditional Section 4b "Findings by Agentic Pattern"; the `threat-report.md` agent adds a conditional "Agentic Pattern Analysis" section after Cross-Layer Attack Chains (Feature 141); SARIF emits `maestro-pattern:<name>` tags matching the existing `maestro-layer:<L#>` convention.

**Critical invariants preserved**:
- **Zero-edit on the 11 existing detection agents** (6 STRIDE + 5 AI). Phase 3.6 reads the deduplicated finding IR but does NOT invoke or modify any threat-detection agent. Feature 082's stabilization holds.
- **Independence from Feature 141 Phase 3.5**. Pattern data does not extend `attack-chains.md`. Pattern membership and chain membership are independent grouping mechanisms.
- **Determinism per ADR-021**. The classification rule table is a pure function of finding fields and architectural metadata; no LLM judgment is involved at the synthesis step.

### Schema Versioning Rule Extension

ADR-026 extends the Feature 136 enum-VALUE-rename minor-bump rule (recorded in ADR-020 Revision History 2026-04-10) to cover **NEW enum-typed field additions** where:

- (a) the new field is additive (no existing field is removed or renamed)
- (b) the new field has a default value enabling backward compatibility (parsers reading the field for missing/null values get the default)
- (c) the schema shape and existing required fields are unchanged (no structural breakage)

When all three conditions hold, the addition warrants a **minor schema bump** (x.y → x.(y+1)). For Feature 142, all three conditions hold for `agentic_pattern`: the field is purely additive, defaults to `none` (graceful for findings without pattern relevance and for pre-Feature-142 baselines per FR-017), and the existing schema shape is unchanged. The bump is **1.3 → 1.4** (minor), not 2.0 (major).

This rule extension applies prospectively to future enum-typed field additions. Future ADRs may further extend the rule for non-enum field additions, or maintain the major-bump convention for any addition that violates conditions (a), (b), or (c).

**Cross-field validation rule clarification**: Cross-field validation rules that constrain WHEN the new field can take non-default values (e.g., "non-`none` `agentic_pattern` MUST NOT be assigned unless the multi-agent gate predicate evaluates to `true`") are part of the additive contract and do NOT trigger a major bump. Such rules constrain the new field's value space conditionally without modifying the schema's serialization shape, existing required fields, or pre-existing field semantics. They are a natural part of introducing a new field that depends on architectural context. The minor-bump rule covers the schema shape; cross-field validation rules covering the new field's conditional value space are governed by the field's own definition (in this case, FR-006 and the multi-agent gate predicate spec in `maestro-agentic-patterns-shared.md` Section 4).

### Governance Rule for Future Post-Hoc Synthesis Phases

Phase 3.6 establishes a precedent that future post-hoc synthesis phases (Phase 3.7, Phase 3.8, etc.) may follow. To prevent ambiguity in future feature evaluations, this ADR formalizes the governance rule:

**Rule**: Future post-hoc synthesis phases that run after Phase 3 deduplication MAY write back to the finding IR ONLY when the synthesized field is **finding-level metadata** (a property of an individual finding, not a relationship between findings). Aggregate-only synthesis (Feature 141 Phase 3.5 model — produces a separate artifact without modifying findings) remains the **default** for cross-finding aggregates such as chains, correlation groups, attack trees, or other multi-finding structures.

**Decision criteria for future post-hoc synthesis phases**:
| Synthesized Output Type | Synthesis Model | Example |
|-------------------------|------------------|---------|
| Finding-level metadata field | Write-back to finding IR (Phase 3.6 model) | `agentic_pattern` (this feature) |
| Cross-finding aggregate (chain, group, tree) | Aggregate-only, separate artifact (Phase 3.5 model) | `attack-chains.md` (Feature 141) |
| Mixed (finding-level field + aggregate) | Two phases, one of each model — NOT a single hybrid phase | hypothetical future feature |

**Rationale for the rule**: Mixing write-back and aggregate-emission in a single phase complicates the input/output contract and makes phase composition harder to reason about. Separating concerns (one phase per output type) keeps each phase's contract clear and enables independent testing.

**Rule application**: Future ADRs proposing post-hoc synthesis phases MUST cite this ADR and explicitly classify the synthesized output as either finding-level metadata or cross-finding aggregate. The classification determines which synthesis model the phase uses. Mixed cases require two phases, one of each model.

---

## Rationale

### Reason 1 — Zero regression on the 11 existing detection agents

Feature 082 stabilized the 11-agent skill-references pattern (`.claude/agents/tachi/<name>.md` + companion `.claude/skills/tachi-<name>/references/detection-patterns.md`). ADR-023 documents the lean+skill-references convention with explicit "do not reopen existing agents" governance. Reopening any of the 5 AI agents (Option A) or introducing the dedup-ripple of a new cross-cutting agent (Option B) would carry documented regression risk against the 11-agent stabilization.

Option C — by reading the deduplicated finding IR post-detection — protects every existing agent from regression. The 11 agents remain byte-identical; the new pattern field is a finding-level annotation applied after their work completes.

### Reason 2 — Reuses Feature 141's Phase 3.5 architectural slot

Feature 141 introduced Phase 3.5 (cross-layer chain correlation) as a post-detection synthesis phase. The architectural shape — read deduplicated findings + read architectural metadata + apply deterministic rule table → produce structured output — is proven by Feature 141 and adopters/implementers will recognize the pattern.

Phase 3.6 sits immediately after Phase 3.5 in the orchestrator pipeline. The two phases share the same architectural slot (post-dedup synthesis) but produce different outputs: Phase 3.5 produces an aggregate artifact (`attack-chains.md`) without modifying findings; Phase 3.6 modifies the finding IR in-place (write-back). This deliberate divergence is documented and contained (see Reason 5).

### Reason 3 — Supports finding-content-based pattern detection

**Agent Collusion** is the hardest pattern to classify because it requires reasoning across **multiple findings** AND **architectural context** (multi-agent topology + inter-agent data flows). A single finding's content does not establish collusion; it requires the analyst to see that two findings on related agents represent coordinated action.

Of the four options:
- **Option D (orchestrator-side keyword classification)** — pure component-keyword matching cannot detect this; the keyword classifier sees one component at a time and lacks finding-content awareness
- **Options A and B (agent-tier classification)** — each agent runs in isolation and lacks cross-finding awareness; both options would need to either reinvent cross-finding correlation or accept incomplete Agent Collusion coverage
- **Option C (post-hoc synthesis)** — the synthesis engine sees the **complete deduplicated finding IR** plus the **complete architectural context** (component inventory, data flows, MAESTRO layers, dispatch keywords). It is the only mechanism that can evaluate "does the architecture have ≥2 agents AND does this finding's component participate in inter-agent data flows?" in a single rule evaluation.

The same advantage applies (with smaller magnitude) to Emergent Behavior (requires multi-agent + behavioral keywords) and Temporal Attack (requires architectural persistent-state indicators).

### Reason 4 — Determinism preserved (ADR-021)

The classification rule table is a pure function of finding fields and architectural metadata. Each rule's `match_conditions` is structurally evaluated (no LLM interpretation):

- `category in [list]` — exact enum match
- `maestro_layer in [list]` — exact enum match
- `target_component_matches: regex` — deterministic regex evaluation
- `architecture has: [topology indicator]` — boolean evaluation against architecture description (deterministic per ADR-021)
- `description contains: [tokens]` — case-insensitive substring match

The same architecture + same rule table produces identical pattern assignments on every run. This matches Feature 141's transition lookup table determinism (per ADR-020 Phase 2 Section "Correlation Algorithm — table-based, no probabilistic scoring").

### Reason 5 — Architectural divergence from Feature 141 is contained and justified

Feature 141 Phase 3.5 produces an **aggregate artifact** (`attack-chains.md`) WITHOUT modifying the finding IR. Phase 3.6 modifies the finding IR in-place (write-back). This is a deliberate divergence because:

1. **Pattern is a finding-level field**, not an aggregate. Downstream consumers (SARIF tags per FR-014, threats.md column per FR-009, threat-report subsections per FR-011) all need to access the field through the existing finding parsing path.
2. **The write-back is contained to a single new phase**. Phase 3.6 is the only writer; Phase 4-5 are pure readers. No other phase modifies the field.
3. **Alternative aggregate-artifact designs were considered and rejected**. Producing a separate `agentic-patterns.md` aggregate (mirroring Feature 141) would require downstream consumers to join two artifacts to display patterns alongside findings. SARIF tag emission would require a custom join during emission. The cost of joining everywhere exceeds the cost of writing-back once.
4. **The divergence is documented and bounded**. This ADR records the precedent: post-hoc synthesis MAY write back to the finding IR when the synthesized field is finding-level metadata. Aggregate-only synthesis (Feature 141 model) remains the default for cross-finding aggregates (chains, correlation groups).

### Reason 6 — Schedule-compatible

Team-Lead PRD review (architect_signoff notes lines 10-11 of PRD frontmatter) explicitly recommends Option C for schedule efficiency:
- Option A: 8-12 days (HIGH regression footprint, 5 agents touched, must include explicit regression validation gate)
- Option C: 5-8 days (zero existing-agent edits, zero deduplication ripple, single new phase)
- Option B: 6-10 days (deduplication ripple + coverage matrix + Risk Summary aggregation logic)
- Option D: 5-7 days (orchestrator-only, but cannot detect Agent Collusion, requires accepting incomplete coverage on the hardest pattern)

Option C produces the best (zero regression risk, schedule-favorable, complete pattern coverage) outcome.

---

## Alternatives Considered

### Alternative 1: Option A — Extend Existing AI Agents

Each of the 5 AI agents (prompt-injection, tool-abuse, agent-autonomy, data-poisoning, model-theft) gains explicit pattern assignment in its detection workflow. New keyword triggers added per agent for the patterns it owns.

**Pros**:
- No new agents added (preserves 11-agent inventory)
- No orchestrator phase additions
- Pattern responsibility lives with the agents that produce findings

**Cons**:
- **HIGH regression footprint** — touches all 5 AI agents that were just stabilized in Feature 082
- ADR-023 explicitly cautions against reopening the 11-agent stabilization
- Distributes pattern semantics across 5 files — risks inconsistent interpretation
- Coverage gaps (Agent Collusion, Temporal Attacks) lack a clear owner — which agent gets responsibility for "no agent currently detects this"?
- 6 STRIDE agents would also need to gain pattern responsibility for Trust Exploitation (currently STRIDE spoofing) and Communication Vulnerabilities (currently STRIDE info-disclosure) — extending the touch radius from 5 to 11 agents
- Schedule penalty: 8-12 days vs Option C's 5-8 days

**Why Not Chosen**: HIGH regression footprint on the 11-agent skill-references pattern (Feature 082) outweighs the architectural benefit of agent-tier ownership. ADR-023 governance explicitly disfavors reopening stabilized agents. The architecture is stable; the right place for net-new functionality is a new phase, not editing stable phases.

### Alternative 2: Option B — Add a New Cross-Cutting Agent (`tachi-agentic-patterns`)

A new agent under `.claude/agents/tachi/` runs as a regular detection agent in Phase 2 alongside the 5 existing AI agents. It produces findings tagged with `agentic_pattern` and a new `category` value (e.g., `agentic-pattern`) or reuses `category: agentic`.

**Pros**:
- Clean ownership — single source of truth for pattern semantics
- Easy to extend with new patterns (add to the new agent, not 11 agents)
- Follows the lean+skill-references shape from ADR-023 (would have a companion `.claude/skills/tachi-agentic-patterns/references/detection-patterns.md`)

**Cons**:
- **MEDIUM regression footprint via deduplication ripple**. A new agent producing findings on multi-agent components (e.g., a Communication Vulnerability finding on an MCP server) must dedupe correctly with tool-abuse findings on the same MCP server. Dedup_key generation, Section 4a intra-component correlation, the orchestrator coverage matrix, and the Risk Summary aggregation logic must all learn the new category
- Adds a 12th detection agent for what is structurally a finding-annotation problem (over-engineered)
- Coverage matrix and Risk Summary aggregation must learn the new category — additional surface area for bugs
- Higher cognitive cost for adopters reading the agent inventory ("why are there 5 AI agents and 1 cross-cutting agent?")
- Schedule penalty vs Option C due to the dedup ripple validation work

**Why Not Chosen**: The deduplication ripple is a documented MEDIUM regression risk (PRD FR-2 Cons section). Adding a full agent for a single new field is over-engineered when the field can be assigned post-hoc with zero existing-agent impact. Option C achieves the same centralization benefit (single source of truth in the synthesis phase + shared reference) without the dedup ripple.

### Alternative 3: Option D — Orchestrator-side Classification at Finding Emission

The orchestrator assigns `agentic_pattern` at the same point it currently assigns `maestro_layer` — during Phase 1 component classification, with finding-level inheritance during Phase 3. Pattern classification is keyword-driven against component name, description, and DFD type, matching the Feature 084/136 MAESTRO layer keyword-classification pattern.

**Pros**:
- **LOW regression footprint** — touches only the orchestrator's classification step + a new shared reference; no agent edits
- Reuses the proven Feature 084/136 keyword-classification pattern (same shape, same shared-reference convention, same inheritance model)
- **Deterministic by construction** — keyword match is rule-based per ADR-020
- Simplest implementation if pure keyword classification were sufficient

**Cons**:
- **Cannot detect Agent Collusion** with pure keyword-on-component classification. Agent Collusion requires reasoning across multiple findings AND architectural context (≥2 agents + inter-agent data flows). A keyword classifier sees one component at a time and lacks both finding-content awareness and architectural-context awareness
- Component-centric classification underclassifies finding-content-driven patterns (e.g., Emergent Behavior with description tokens like "cascade", "unpredictable", "interaction", "emergent")
- Generating net-new findings for previously-uncovered patterns is awkward in a component-centric phase that runs before detection — there are no findings yet to check existence against
- Forces the architect to either (a) accept incomplete coverage on the hardest pattern (Agent Collusion), or (b) add a separate post-detection Agent Collusion synthesis phase (which is essentially Option C, defeating the simplicity argument)

**Why Not Chosen**: The keyword-on-component classifier cannot detect Agent Collusion (which is the most important previously-uncovered pattern). Accepting incomplete coverage on Agent Collusion contradicts SC-001 (6 of 6 pattern coverage). Adding a separate Agent Collusion synthesis phase to compensate ends up implementing Option C anyway, with the additional complexity of having two pattern-classification phases (one keyword-tier, one synthesis-tier). Option C in its full form is the simpler choice.

---

## Consequences

### Positive

- **Zero regression on the 11 existing detection agents** (6 STRIDE + 5 AI). Feature 082's stabilization holds. ADR-023 governance respected.
- **Reuses Feature 141 architectural slot** (Phase 3.5 sister-phase) — adopters and implementers recognize the pattern.
- **Complete coverage of all six canonical patterns** including the three previously-uncovered (SC-001 = 6/6 pattern coverage).
- **Deterministic by construction** (ADR-021 invariant preserved).
- **Multi-agent gate predicate enforced at the synthesis step** — single enforcement point for FR-006 invariant.
- **Backward compatible**: schema bump 1.3 → 1.4 is additive; pre-Feature-142 baselines parse with default `none`; 5 non-multi-agent baseline PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000.
- **Schedule-favorable**: 5-8 day estimate vs Option A's 8-12 days.
- **Schema versioning rule extended** to cover NEW enum-typed field additions — durable precedent for future schema evolution.
- **Pattern data placement contained** to finding IR + threats.md — no extension of `attack-chains.md` (Feature 141 independence preserved per FR-008).

### Negative

- **New orchestrator pipeline phase (Phase 3.6)** adds context-window pressure (estimated +5-7K tokens per architecture: rule table + architectural metadata + finding IR re-read). Comparable to Feature 141 Phase 3.5 budget.
- **Architectural divergence from Feature 141 documented** — Phase 3.5 aggregate-artifact model does NOT extend to write-back; Phase 3.6 introduces the write-back precedent. Future readers must distinguish the two synthesis-phase models. Mitigated by clear documentation in this ADR + plan.md.
- **Net-new finding generation** (for Agent Collusion, Temporal Attack, Emergent Behavior) introduces a new finding-emission path outside the 11 detection agents. This requires careful test coverage to prevent duplicate findings (existing finding + net-new finding for the same pattern) — addressed by the explicit "skip net-new generation if any existing finding now carries the pattern" check in Phase 3.6 Step 3.
- **Rule table maintenance burden**. Adding a new pattern (or refining an existing pattern's rule conditions) requires editing the shared reference and re-running examples. This is the same maintenance burden as Feature 141's transition lookup table.
- **Pattern subsection rendering complexity**. The threat-report agent must conditionally render the new section, suppress zero-finding subsections, and order remaining subsections by max severity then finding count. Tested by `tests/scripts/test_pattern_extraction.py`.

### Mitigation

- Phase 3.6 context overhead is bounded by reading deduplicated findings (not raw agent output) — same mitigation as Feature 141 Phase 3.5
- Architectural divergence is explicitly recorded in this ADR and in plan.md Component 1; future readers have a single source of truth for the precedent
- Net-new finding generation has explicit "skip if existing" check + dedicated test coverage in `tests/scripts/test_pattern_synthesis.py`
- Rule table maintenance follows the existing Feature 141 transition table maintenance pattern; rule precedence and tie-breaking documented in the shared reference
- Pattern subsection rendering complexity is bounded by the existing Feature 015 narrative generation pattern — no new rendering primitives introduced

---

## Related Decisions

- [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md): Shared cross-agent definitions pattern that governs `maestro-agentic-patterns-shared.md` placement, frontmatter, and consumer-listing convention
- [ADR-020](ADR-020-maestro-layer-classification.md): MAESTRO layer classification — extended in this ADR with Phase 3 (agentic pattern expansion); ADR-020 Revision History receives a back-reference to this ADR (FR-018)
- [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md): SOURCE_DATE_EPOCH determinism — pattern classification rule table is rule-based, preserving the determinism invariant
- [ADR-023](ADR-023-threat-agent-skill-references-pattern.md): Lean agent + skill-references pattern — Option B (new cross-cutting agent) rejection rationale draws on ADR-023 governance against reopening the stabilized 11-agent inventory; if Option B HAD been selected, the new agent would have followed ADR-023 conventions
- [Feature 141 PRD](../../product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md): Phase 3.5 cross-layer correlation — direct architectural precedent for post-hoc synthesis phase placement
- [Feature 084 PRD](../../product/02_PRD/084-maestro-layer-mapping-2026-04-07.md) / [Feature 136 PRD](../../product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md): MAESTRO layer keyword classification — Option D comparison reference (orchestrator-side classification pattern)
- [Feature 082 PRD](../../product/02_PRD/082-threat-agent-skill-references-2026-04-11.md): 11-agent skill-references stabilization — the foundation that Option C protects from regression

---

## References

- `.claude/agents/tachi/orchestrator.md` — Phase 3.6 insertion point (Wave 1 implementation)
- `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` — Six pattern definitions, coverage mapping table, classification rule table, multi-agent gate predicate spec (Wave 0 implementation)
- `schemas/finding.yaml` v1.4 — `agentic_pattern` enum field (Wave 0 implementation)
- `templates/tachi/output-schemas/threats.md` — Pattern column + Section 4b (Wave 2 implementation)
- `.claude/agents/tachi/threat-report.md` — Agentic Pattern Analysis section (Wave 2 implementation)
- Cloud Security Alliance, "Agentic AI Threat Modeling Framework: MAESTRO", February 2025 — [`https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro`](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- Snyk Labs, "MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems" — [`https://labs.snyk.io/resources/maestro-threat-modeling/`](https://labs.snyk.io/resources/maestro-threat-modeling/)
- Practical DevSecOps, "MAESTRO: An Agentic AI Threat Modeling Framework" — [`https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/`](https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/)

---

## Revision History

**2026-04-16 (Initial — Feature 142)**: Records the Hybrid Post-Hoc Synthesis (Option C) decision for MAESTRO Phase 3 agentic pattern classification mechanism. Documents four-option trade-off across pattern semantics ownership / schema write-back location / existing-agent regression footprint axes. Extends the Feature 136 enum-VALUE-rename minor-bump rule to cover NEW enum-typed field additions under three additive-compatibility conditions. Establishes the precedent that post-hoc synthesis phases MAY write back to the finding IR when the synthesized field is finding-level metadata (architectural divergence from Feature 141's aggregate-only model).
