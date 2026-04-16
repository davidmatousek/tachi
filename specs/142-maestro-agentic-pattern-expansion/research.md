# Research Summary: MAESTRO Phase 3 — Agentic Threat Pattern Expansion (Feature 142)

**Created**: 2026-04-16
**PRD**: [docs/product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md](../../docs/product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md)
**Purpose**: Ground spec.md in codebase reality and architectural precedent before generation.

---

## Codebase Analysis

### Finding Schema (`schemas/finding.yaml`)
- **Current `schema_version`**: 1.3 (last bumped in Feature 136 for L5/L6/L7 enum-VALUE rename)
- **Existing enum-typed fields**: `category` (8 values), `likelihood` (3), `impact` (3), `risk_level` (5), `dfd_element_type` (4), `delta_status` (4), `maestro_layer` (8 values: `L1 — Foundation Model`, ..., `Unclassified`)
- **MAESTRO layer pattern** (lines 123-145): Uses long-form enum values (e.g., `"L1 — Foundation Model"`); defaults to `"Unclassified"`; assigned at Phase 1 component classification, inherited at finding emission in Phase 3
- **Implication for FR-3**: The new `agentic_pattern` field must follow the same shape — enum, default, optional/required posture, and inheritance pattern. Adding a NEW enum-typed field is structurally distinct from Feature 136's enum-VALUE rename — ADR-026 must extend the minor-bump rule explicitly.

### Five AI Threat Agents (lean shape, Feature 082 / ADR-023)
All five at `.claude/agents/tachi/` confirm the lean+skill-references pattern:
| Agent | Lines | Tools | Companion Skill |
|-------|-------|-------|-----------------|
| `prompt-injection.md` | 96 | Read, Glob, Grep | `.claude/skills/tachi-prompt-injection/references/detection-patterns.md` |
| `tool-abuse.md` | 98 | same | `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` |
| `agent-autonomy.md` | 114 | same | `.claude/skills/tachi-agent-autonomy/references/detection-patterns.md` |
| `data-poisoning.md` | 78 | same | `.claude/skills/tachi-data-poisoning/references/detection-patterns.md` |
| `model-theft.md` | 95 | same | `.claude/skills/tachi-model-theft/references/detection-patterns.md` |

Each has exactly one `**MANDATORY**: Read` directive at detection-workflow start. **Implication for FR-2 Option A**: editing all five reopens the stabilization Feature 082 just closed (high regression footprint per ADR-023 sibling-pattern governance).

### Orchestrator Classification (Feature 084 / 136 precedent — Option D anchor)
- `.claude/agents/tachi/orchestrator.md` Phase 1 (lines 173-184): keyword-based MAESTRO layer classification. Reads `.claude/skills/tachi-shared/references/maestro-layers-shared.md`; case-insensitive substring match against component name + description + DFD type; first-match-wins L1→L7 evaluation (specificity gradient)
- Phase 3 inheritance (lines 358, 371): both STRIDE and AI findings copy `maestro_layer` from their target component
- **Implication for FR-2 Option D**: this pattern is reusable byte-for-byte — same shared-reference shape, same inheritance model. Only risk is "Agent Collusion typically requires reasoning across multiple findings, not just keywords on a single component" (Open Q from PRD Technical Questions).

### Cross-Layer Chains Synthesis (Feature 141 Phase 3.5 precedent — Option C anchor)
- Phase 3.5 (orchestrator lines 386-394): runs AFTER Phase 3 deduplication and Section 4a intra-component correlation, BEFORE Phase 4 assessment
- Reads `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md` — deterministic transition lookup table format (source layer, source category) → (target layer, target category) with causal verb
- **Independence Invariant** (ADR-020 Phase 2 section): Phase 3.5 chains and Section 4a correlation are independent grouping mechanisms; a finding may participate in both. **Pattern field must inherit this invariant** — pattern membership is independent of chain membership.
- Output: `attack-chains.md` artifact + `has-attack-chains` boolean (conditional gating)
- **Implication for FR-2 Option C**: Phase 3.5 is the architectural slot. Two design choices for Option C: (i) extend Phase 3.5 to also assign patterns inline, or (ii) add a separate Phase 3.6 dedicated to pattern synthesis. **Critical distinction from Feature 141**: Phase 3.5 produces an aggregate artifact (`attack-chains.md`) WITHOUT modifying the finding IR. Option C MUST modify the finding IR (write-back pattern) — this is the architectural divergence from Feature 141 precedent.

### threats.md Template
- Section 7 findings table columns: Component, Threat, Likelihood, Impact, Risk Level, Mitigation, References (MAESTRO Layer column added in Feature 084)
- Section 4a (Correlated Findings): always rendered, conditional data
- Section 4b/4c not yet present
- **Implication for FR-4**: Pattern column placement after Category, before Component (visually grouped with classification metadata per PRD); new conditional Section 4b ("Findings by Agentic Pattern") follows Section 4a pattern

### threat-report.md Template
- Existing sections: 1. Executive Summary, 2. Architecture Overview, 3. Threat Analysis (3.1-3.8 STRIDE+AI subsections), 4. Cross-Cutting Themes, 5. Attack Trees
- Feature 141 added Section 6 (Cross-Layer Attack Chains) post-Section 4
- **Implication for FR-5**: Section count must NOT be hardcoded in spec — implementation grep-counts existing sections at code-time. New "Agentic Pattern Analysis" section sits after Cross-Layer Attack Chains and before Findings Detail.

### SARIF Tag Convention
- `orchestrator.md` line 591: `Add "maestro-layer:{layer-id}" to result.properties.tags[]` (e.g., `maestro-layer:L3`); lowercase namespace, colon-separator
- **Implication for FR-6**: `maestro-pattern:<pattern_name>` MUST match exactly — same lowercase, same colon. Verification step: grep the existing maestro-layer tagging logic in the SARIF generator before implementing pattern tagging.

### agentic-app Example (FR-7 Path 1 viability)
- `examples/agentic-app/architecture.md`: 7 components — User, Guardrails Service, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger, External API
- **Current architecture has only ONE LLM Agent and ONE MCP Tool Server**, no fine-tuning pipeline, no persistent learning loop, no inter-agent communication channel
- **Implication for FR-7**: Path 1 (extend agentic-app) requires ≥3 architecture additions: a second cooperating agent, a long-running learning loop (for Temporal Attack), an inter-agent communication channel (for Agent Collusion + Communication Vulnerability). The PRD already budgets this as **planned scope** (1-2h in Wave 0).

### Backward Compatibility Test Mechanism
- `tests/scripts/test_backward_compatibility.py` lines 36-44: uses `SOURCE_DATE_EPOCH=1700000000` per ADR-021; baseline list excludes `agentic-app` (intentional regeneration target consistent with Features 141, 136); 5 baselines must remain byte-identical to validate "no false positive pattern findings on single-agent architectures"

### Recent ADRs (template + numbering)
- ADR-019 (shared definitions), ADR-020 (MAESTRO classification — extended for Phase 2 in Feature 141 Revision History), ADR-021 (SOURCE_DATE_EPOCH), ADR-022 (mmdc prerequisite), ADR-023 (threat agent skill references), ADR-024 (AIVSS posture), ADR-025 (NIST AI RMF posture)
- **ADR-026 does NOT yet exist** — to be created during `/aod.plan` per FR-8
- ADR template (`ADR-000-template.md`): Status, Date, Deciders, Context, Decision, Rationale, Alternatives Considered, Consequences (Positive/Negative), Related Decisions, References, Revision History

---

## Architecture Constraints

### Must Preserve
- **Determinism (ADR-021)**: Pattern classification must produce identical assignments for identical input — no LLM-judgment-based classification, regardless of mechanism choice
- **Backward compatibility (Constitution III, NON-NEGOTIABLE)**: 5 non-multi-agent baselines must remain byte-identical under SOURCE_DATE_EPOCH=1700000000
- **Independence invariant (ADR-020 Phase 2)**: Pattern grouping is independent of cross-layer chain grouping — a finding may belong to both
- **Lean agent shape (ADR-023)**: If Option B is chosen (new cross-cutting agent), it must follow the lean + companion skill pattern (≤180 lines hard cap; tools = Read, Glob, Grep)
- **Shared reference governance (ADR-019)**: Pattern definitions live in a single shared reference file; consumers reference via lazy load; producers list themselves as consumers in frontmatter
- **Zero-dependency runtime constraint**: No new runtime dependencies — Python stdlib only (matches Feature 128 / 136 precedent)

### Architectural Slots Available
- **Option A**: 5 existing agent files (high regression footprint per ADR-023)
- **Option B**: New `tachi-agentic-patterns` agent under `.claude/agents/tachi/` + companion skill at `.claude/skills/tachi-agentic-patterns/references/detection-patterns.md` (deduplication ripple per PRD FR-2)
- **Option C**: Phase 3.5 extension OR new Phase 3.6 in orchestrator (write-back to finding IR — architecturally divergent from Feature 141)
- **Option D**: Orchestrator Phase 1 keyword classification + Phase 3 inheritance (component-centric — may underclassify finding-content-driven patterns like Agent Collusion)

---

## Industry Research

### CSA MAESTRO — Six Canonical Patterns (cross-referenced sources)
Three authoritative sources confirmed by web search:
1. **CSA Blog** (Feb 2025): https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro — original framework publication
2. **Snyk Labs**: https://labs.snyk.io/resources/maestro-threat-modeling/ — enumerates all six canonical patterns
3. **Practical DevSecOps**: https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/ — independent restatement of the same six patterns

The six patterns are stable across all three sources:
1. **Agent Collusion** — multiple compromised agents coordinating (DDoS, info gathering, policy circumvention)
2. **Emergent Behavior** — exploiting unpredictable behaviors arising from agent interactions
3. **Temporal Attacks** — sleeper agents, gradual corruption, seasonal exploitation
4. **Trust Exploitation** — identity spoofing between agents, reputation manipulation
5. **Communication Vulnerabilities** — inter-agent message interception, protocol manipulation
6. **Resource Competition** — resource monopolization, priority manipulation between agents

### Newer CSA Publications
- CSA "MAESTRO for Real-World Agentic AI Threats" (Feb 2026) — applies framework to CI/CD pipelines; reinforces the six-pattern list as canonical
- CSO Online "Introducing MAESTRO" — confirms framework adoption beyond CSA

### Industry Implementation Precedents
- **IriusRisk** "MAESTRO: Streamlining Agentic AI Security" — confirms IriusRisk surfaces MAESTRO patterns as named filterable categories in their threat modeling tool. Direct competitive reference: tachi must surface canonical patterns explicitly to be considered a peer MAESTRO implementation.
- **Christian Schneider blog** — independent threat modeler treats canonical patterns as the lingua franca of MAESTRO discourse

### Stability Assessment
- Six pattern names are well-defined and stable across primary, secondary, and tertiary sources
- Pattern aliases or compatibility shims unnecessary at v1.4 schema bump
- CSA framework not yet at v2 — patterns expected to remain canonical for 2+ year stability runway (matches AI RMF 1.0 stability assessment in ADR-025)

---

## Recommendations for Spec

### Spec MUST Include
1. **All six canonical patterns** as enum values in `agentic_pattern` (FR-3) — non-negotiable, established by canonical CSA source
2. **`none` and `multiple` values** for findings without pattern relevance and findings exemplifying multiple patterns equally (FR-3)
3. **Multi-agent gate predicate** as an explicit invariant (FR-2 Business Rules) — three OR conditions: ≥2 agentic/llm components, ≥1 inter-component data flow between agentic components, OR multi-agent coordination keywords. The gate is enforced regardless of which mechanism (A/B/C/D) ADR-026 selects.
4. **Pattern data placement invariant** — `agentic_pattern` lives in finding IR + threats.md only; does NOT extend `attack-chains.md`. The threat-report agent may cross-reference chain membership in pattern narratives, but the artifacts remain independent.
5. **FR-2 explicit option list with all four mechanisms** — the spec preserves PRD's four-option presentation rather than pre-judging the architect's call
6. **Backward compatibility validation requirement** — 5 baselines byte-identical under SOURCE_DATE_EPOCH=1700000000; agentic-app intentional regeneration target

### Spec MUST Defer (to ADR-026 / `/aod.plan`)
- **Mechanism choice (Option A/B/C/D)** — architect's call during `/aod.plan`
- **Schema bump rationale** — minor (1.3→1.4 additive enum-typed field) vs major (2.0 new required field) — documented in ADR-026
- **agentic-app extension specifics** — Path 1 vs Path 2 vs Path 3 locked in `/aod.plan` Wave 0
- **Pattern subsection number in threat-report.md** — section count grep-determined at implementation time, not hardcoded
- **If Option C: Phase 3.5 extension vs Phase 3.6 dedicated phase** — orchestrator-pipeline detail
- **If Option B: `category: agentic` reuse vs new `category: agentic-pattern`** — schema impact + deduplication interaction

### Spec MUST Avoid
- **Implementation language / framework references** — spec is technology-agnostic; "the orchestrator", "the synthesis phase", "the new agent" referenced functionally
- **Code snippets** — schema YAML excerpt acceptable (FR-3 is data contract, not implementation)
- **Hardcoded section numbers in threat-report.md** — implementation determines from current count
- **False precision on coverage table values** — Coverage Strength values restricted to Full / Partial / None — Coverage Required (avoid 5-point Likert scales that invite overclaiming)

### Spec Structural Notes
- User stories US-1 through US-6 in PRD are well-formed — port as-is with priority preservation (P0 for US-1, US-2, US-6; P1 for US-3, US-4, US-5)
- FR-1 through FR-8 are well-scoped — port to spec preserving the 8-FR structure
- Risks 142.1 through 142.5 are accurate per Feature 082 / 141 precedent — port verbatim with minor wording polish
- DoD checklist (PRD lines 545-559) is implementation-ready — port verbatim
