# Data Model: MAESTRO Phase 3 — Agentic Threat Pattern Expansion (Feature 142)

**Created**: 2026-04-16
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)
**ADR**: [docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md](../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md)

---

## Entity Catalog

### Entity 1: Finding (Extended)

Existing entity (`schemas/finding.yaml`) gains one new field. All other fields unchanged.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | yes | — | Unique finding identifier (existing) |
| `category` | enum | yes | — | STRIDE+AI category (existing) |
| `maestro_layer` | enum | yes | `Unclassified` | MAESTRO layer (existing, Feature 084/136) |
| `agentic_pattern` | **enum (NEW)** | **yes** | **`none`** | **Canonical CSA MAESTRO agentic pattern (Feature 142)** |
| `component` | string | yes | — | Target component name (existing) |
| `dfd_element_type` | enum | yes | — | DFD element type (existing) |
| `description` | string | yes | — | Threat description (existing) |
| `likelihood` | enum | yes | — | Likelihood rating (existing) |
| `impact` | enum | yes | — | Impact rating (existing) |
| `risk_level` | enum | yes | — | Severity (existing) |
| `mitigation` | string | no | — | Mitigation recommendation (existing) |
| `references` | array | no | — | Reference links (existing) |
| `delta_status` | enum | no | — | Baseline delta tracking (existing, Feature 074) |

#### `agentic_pattern` Enum Values

| Value | Meaning |
|-------|---------|
| `agent_collusion` | Multiple compromised agents coordinating to achieve malicious objectives (DDoS, info gathering, policy circumvention) |
| `emergent_behavior` | Exploiting unpredictable behaviors arising from agent interactions (cascade failures, behavioral manipulation) |
| `temporal_attack` | Sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation |
| `trust_exploitation` | Identity spoofing between agents, reputation manipulation, trust chain attacks |
| `communication_vulnerability` | Inter-agent message interception, protocol manipulation, routing attacks |
| `resource_competition` | Resource monopolization, priority manipulation, coordination disruption between agents |
| `none` | Finding does not map to any canonical pattern (sentinel; required since field is mandatory post-Feature-142) |
| `multiple` | Finding exemplifies two or more patterns equally; analysts SHOULD prefer the dominant pattern when one exists |

#### Validation Rules

- `agentic_pattern` MUST be one of the 8 enum values above (no other strings accepted)
- `agentic_pattern` MUST be present on every finding produced post-Feature-142 (default `none` for findings without pattern relevance)
- Pre-Feature-142 baseline findings (without the field) MUST parse with default `agentic_pattern: none` (FR-017)
- Non-`none` `agentic_pattern` MUST NOT be assigned unless the multi-agent gate predicate (see Entity 4) evaluates to `true` for the architecture
- `agentic_pattern: multiple` MAY only be assigned when two or more rules in the classification table match a finding with equal priority

#### State Transitions

The `agentic_pattern` field is set exactly once during Phase 3.6 synthesis. After synthesis, the field is read-only — no downstream phase modifies it. The field flows through Phase 4 (assessment), Phase 5 (threat-report + SARIF emission), and PDF generation as static metadata.

---

### Entity 2: Agentic Pattern (Canonical Reference)

A first-class entity defined in `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern_name` | enum | yes | One of six canonical pattern names (matches the `agentic_pattern` enum minus `none` and `multiple`) |
| `definition` | string | yes | 1-2 sentence canonical description sourced from CSA MAESTRO blog 2025-02-06 |
| `representative_examples` | array (2-3 entries) | yes | Concrete attack vector examples |
| `detection_criteria` | string | yes | Architectural preconditions, keyword indicators, finding signals |
| `csa_citation` | string | yes | Source URL for CSA canonical definition |
| `current_coverage` | enum | yes | `Full`, `Partial`, or `None — Coverage Required` (Coverage Strength) |
| `covering_agents` | array | yes (may be empty) | List of existing agents that produce findings exemplifying this pattern |
| `coverage_gap_justification` | string | conditional | Required when `current_coverage == Partial`; 1-sentence explanation of what existing agents miss |

#### Coverage Mapping Table Constraint (FR-002)

The Coverage Strength column is restricted to exactly three values. No "Strong", "Mostly", "Almost", "Significant" — these vague qualifiers are rejected to prevent overclaiming. The three permitted values create a forced choice that surfaces gaps honestly.

| Pattern (PRD initial assessment) | Currently Covered By | Coverage Strength | Gap |
|----------------------------------|---------------------|-------------------|-----|
| Agent Collusion | None directly | None — Coverage Required | New detection required (Phase 3.6 + R-01) |
| Emergent Behavior | agent-autonomy (cascading failures) | Partial | Detects per-agent cascade but misses cross-agent emergent patterns |
| Temporal Attacks | None directly | None — Coverage Required | New detection required (Phase 3.6 + R-02 with net-new generation) |
| Trust Exploitation | spoofing (identity), tool-abuse (tool trust) | Partial | Misses inter-agent identity context (single-agent identity ≠ inter-agent trust chain) |
| Communication Vulnerabilities | tool-abuse (MCP/protocol), info-disclosure (eavesdropping) | Partial | Misses inter-agent messaging context (component-level eavesdropping ≠ inter-agent message interception) |
| Resource Competition | denial-of-service (component-level), agent-autonomy (resource consumption) | Partial | Misses inter-agent context (per-component DoS ≠ multi-agent resource monopolization) |

---

### Entity 3: Classification Rule

Rule entries lookup table in `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` Section 3, consumed by Phase 3.6 synthesis engine.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | string | yes | Unique identifier (R-01, R-02, ...) |
| `pattern` | enum | yes | One of six canonical pattern names that this rule assigns |
| `priority` | integer | yes | Evaluation priority (lower = more specific = evaluated first) |
| `match_conditions` | object | yes | Conjunction of zero-or-more match predicates (see schema below) |
| `generates_finding_when_no_match` | boolean | yes | If `true`, rule may emit a net-new finding when no existing finding carries the pattern |
| `generation_template` | string | conditional | Required when `generates_finding_when_no_match: true`; markdown template for net-new finding description |

#### `match_conditions` Schema

```yaml
match_conditions:
  category_in:                          # optional
    - <category enum value>             # finding.category must be in this list
    ...
  maestro_layer_in:                     # optional
    - <layer enum value>                # finding.maestro_layer must be in this list
    ...
  target_component_matches:             # optional
    type_or_name_regex: <regex>         # regex match on component type or name
  architecture_has:                     # optional
    component_type:                     # at least one component of given type must exist
      - <type token>
      ...
    topology:                           # topology indicator
      - multi_agent                     # ≥2 agentic/llm components (matches gate cond. a)
      - inter_agent_data_flow           # ≥1 inter-component data flow between agentic components (gate cond. b)
      - persistent_state                # fine-tuning / persistent memory / learning loop component
      - inter_agent_channel             # explicit inter-agent message bus or shared memory
  description_contains:                 # optional
    - <token>                           # finding.description must contain at least one token (case-insensitive)
    ...
```

A rule's `match_conditions` is satisfied when ALL specified conditions are satisfied (conjunction). A condition with multiple values uses disjunction within the condition (any value matches).

#### Component Type Token List (canonical, finite enumeration)

The `architecture_has.component_type` predicate uses an explicit finite token list to ensure determinism (per ADR-021). Tokens are matched case-insensitively against the architecture description's component types and component names. Wave 0 implementation MUST use this exact token list — no fuzzy matching, no LLM-based interpretation:

| Token | Matches | Used By Rule(s) |
|-------|---------|-----------------|
| `fine_tuning_pipeline` | Component name OR description containing: "fine-tuning pipeline", "fine tuning pipeline", "training pipeline", "fine-tune pipeline" | R-02 (Temporal Attack) |
| `persistent_agent_memory` | Component name OR description containing: "agent memory", "persistent memory", "memory store", "long-term memory", "agent state store" | R-02 (Temporal Attack) |
| `long_running_learning_loop` | Component name OR description containing: "learning loop", "feedback loop", "continual learning", "RLHF loop", "reward model loop", "self-improvement loop" | R-02 (Temporal Attack) |
| `inter_agent_channel` | Component name OR description containing: "inter-agent channel", "message bus" (when context is multi-agent), "agent communication channel", "shared queue" (when context is multi-agent), "shared memory" (when context is multi-agent) | R-05 (Communication Vulnerability) |

**Determinism invariant**: This token list IS the source of truth. Adding new tokens requires a minor version bump on `maestro-agentic-patterns-shared.md` and triggers backward-compatibility revalidation against all 6 example architectures.

#### Topology Indicator Token List (canonical, finite enumeration)

The `architecture_has.topology` predicate uses an explicit finite list of topology indicators. Each indicator is a deterministic structural check on the Phase 1 component inventory + data flow graph:

| Topology Indicator | Definition | Used By Rule(s) |
|--------------------|------------|-----------------|
| `multi_agent` | ≥2 components classified as `agentic` or `llm` category in Phase 1 dispatch keywords (matches Multi-Agent Gate Predicate condition (a)) | R-01 (Agent Collusion), R-03 (Emergent Behavior), R-04 (Trust Exploitation), R-06 (Resource Competition) |
| `inter_agent_data_flow` | ≥1 inter-component data flow where BOTH source and target components are `agentic` or `llm` (matches Multi-Agent Gate Predicate condition (b)) | R-01 (Agent Collusion) |
| `persistent_state` | At least one component matches any of the four `persistent_state`-related component_type tokens (`fine_tuning_pipeline`, `persistent_agent_memory`, `long_running_learning_loop`) — convenience grouping for R-02 | R-02 (Temporal Attack) |
| `inter_agent_channel` | At least one component matches the `inter_agent_channel` component_type token AND the architecture is `multi_agent` | R-05 (Communication Vulnerability) — composite; both conditions must hold |

**Determinism invariant**: All four topology indicators are pure functions of the Phase 1 component inventory and data flow graph. No LLM judgment, no fuzzy matching. Adding new topology indicators requires a minor version bump on `maestro-agentic-patterns-shared.md`.

#### Rule Priority and Tie-Breaking

- Rules evaluated in ascending `priority` order (lowest priority value first = most specific)
- First matching rule wins
- If two rules have the same priority AND both match: assign `agentic_pattern: multiple` (the rare equal-pattern case)
- Tie-breaking for `multiple`: the threat report renders the finding under all matching pattern subsections AND under a dedicated "Multi-Pattern Findings" subsection (per plan.md Open Questions Resolution)

#### Initial Rule Set (R-01 through R-06)

The initial rule set covers all six canonical patterns. Each rule documented in `maestro-agentic-patterns-shared.md` Section 3 with full `match_conditions`, priority, and (where applicable) `generation_template`.

| Rule | Pattern | Priority | Generates Net-New? | Architectural Trigger |
|------|---------|----------|---------------------|------------------------|
| R-01 | agent_collusion | 10 | yes | category in [agentic, llm] + multi_agent topology + inter_agent_data_flow |
| R-02 | temporal_attack | 20 | yes | architecture has persistent_state component (fine-tuning / memory / learning loop) |
| R-03 | emergent_behavior | 30 | yes | category in [agentic, llm] + multi_agent + description contains [cascade, unpredictable, interaction, emergent] |
| R-04 | trust_exploitation | 40 | no | category in [spoofing, agentic] + multi_agent topology |
| R-05 | communication_vulnerability | 50 | no | category in [agentic, info-disclosure] + target component is inter_agent_channel |
| R-06 | resource_competition | 60 | no | category in [denial-of-service, agentic] + multi_agent + description contains [resource, monopol, competition, priority] |

(Priority numbers are illustrative; final values set during Wave 0 implementation.)

---

### Entity 4: Multi-Agent Gate Predicate

A pre-classification gate evaluated once per architecture in Phase 3.6 Step 1.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `result` | boolean | yes | `true` iff at least one of conditions a/b/c holds |
| `condition_a` | boolean | yes | ≥2 components classified as `agentic` or `llm` category in Phase 1 dispatch keywords |
| `condition_b` | boolean | yes | ≥1 inter-component data flow where BOTH source and target components are `agentic`/`llm` |
| `condition_c` | boolean | yes | ≥1 case-insensitive substring match on the architecture description for any of: `multi-agent`, `swarm`, `supervisor`, `delegation`, `agent mesh` |
| `evaluation_metadata` | object | yes | Diagnostic data for debugging: which condition triggered, which components matched, which keywords found |

#### Predicate Evaluation Algorithm

```
function evaluate_multi_agent_gate(architecture, components):
    condition_a = count_components_with_category(components, ["agentic", "llm"]) >= 2
    condition_b = exists_inter_component_data_flow(components, source_in_categories=["agentic", "llm"], target_in_categories=["agentic", "llm"])
    condition_c = any_keyword_match(architecture.description, ["multi-agent", "swarm", "supervisor", "delegation", "agent mesh"])
    result = condition_a or condition_b or condition_c
    return {result, condition_a, condition_b, condition_c, evaluation_metadata}
```

#### Validation Rules

- The predicate is evaluated EXACTLY ONCE per architecture (cached for Phase 3.6 duration)
- The predicate evaluation is deterministic (pure function of architecture + components)
- Condition (a) uses the existing Phase 1 dispatch keyword categories — no new keyword classification needed
- Condition (b) requires both endpoints of a data flow to be `agentic`/`llm`; `agentic` ↔ `data_store` does not count
- Condition (c) keywords list is documented in `maestro-agentic-patterns-shared.md` Section 4 and is the source of truth (any future expansion bumps a minor version)

#### Worked Examples on the 6 Tachi Examples

| Example | Cond (a): ≥2 agentic/llm | Cond (b): inter-agent flow | Cond (c): keyword match | Predicate Result | Pattern Findings Expected |
|---------|---------------------------|------------------------------|--------------------------|-------------------|----------------------------|
| web-app | false | false | false | **false** | none on any finding |
| microservices | false | false | false | **false** | none on any finding |
| ascii-web-api | false | false | false | **false** | none on any finding |
| mermaid-agentic-app | true (2 agents in DFD) | unclear | unclear | **true** | needs validation; expected `none` if no inter-agent comm |
| free-text-microservice | false | false | false | **false** | none on any finding |
| agentic-app (extended for Feature 142) | true (3 agents) | true (Specialist Agent ↔ Orchestrator) | true ("multi-agent" in arch description) | **true** | non-`none` patterns expected for ≥3 |

**Note on mermaid-agentic-app**: This example has multiple agents in the Mermaid DFD but lacks inter-agent communication channels and multi-agent coordination keywords. Predicate evaluation is `true` via condition (a) alone. To preserve backward compatibility (5 baseline byte-identical PDFs), the rule table must NOT match any non-`none` pattern on findings from this architecture. Validated during Wave 4 backward-compat tests; if a rule incorrectly matches, the rule's `match_conditions` are tightened (typically by adding `description_contains` constraints) to exclude the false positive.

---

### Entity 5: Net-New Generated Finding

A finding emitted by Phase 3.6 when no existing detection-tier finding carries the pattern that the architecture indicates should exist.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `id` | string | generated | Format: `AGP-NN` (sequential, e.g., `AGP-01`, `AGP-02`); aligned with existing 1-4 letter prefix convention (S, T, R, I, D, E, AG, LLM); finding.yaml `id.pattern` regex extended in Wave 0 to accept `AGP-` prefix |
| `category` | enum | rule | Always `agentic` for net-new pattern findings |
| `maestro_layer` | enum | inherited | Inherited from target component (existing inheritance pattern from Feature 084) |
| `agentic_pattern` | enum | rule | The pattern this generation rule covers |
| `component` | string | rule | First component matching the rule's `target_component_matches` predicate |
| `dfd_element_type` | enum | inherited | Inherited from target component |
| `description` | string | rule template | Rendered from rule's `generation_template` with component name + architectural context substituted |
| `likelihood` | enum | default | `MEDIUM` (analyst can re-rate) |
| `impact` | enum | default | `MEDIUM` (analyst can re-rate) |
| `risk_level` | enum | computed | Computed from likelihood × impact via existing OWASP 3×3 matrix |
| `mitigation` | string | rule template | Rendered from rule's mitigation template (recommended controls per pattern) |
| `references` | array | rule | CSA citation + relevant detection criteria reference |
| `delta_status` | enum | new | Always `NEW` for net-new generated findings (consumed by baseline delta tracking) |

#### Generation Constraints

- Net-new findings are appended to the deduplicated finding IR AFTER Phase 3.6 Step 2 (existing-finding pattern assignment)
- Maximum 1 net-new finding per pattern per architecture (no flooding)
- Generation skipped when ANY existing finding already carries the pattern label
- Net-new findings flow through Phase 4-5 identically to detection-tier findings (no special handling)
- Generation is deterministic: same architecture + same rule table produces identical generated findings (per ADR-021)

---

### Entity 6: Pattern Analysis Section (Threat Report)

A conditional section in `threat-report.md` enumerating findings by canonical pattern.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `section_number` | integer | yes | Determined at code time by counting existing sections (NOT hardcoded per FR-011) |
| `section_title` | string | yes | "Agentic Pattern Analysis" |
| `subsections` | array | yes (may be empty) | One subsection per pattern with non-zero finding count |
| `condition_gate` | boolean | yes | Section rendered iff `has-agentic-patterns: true` |

#### Subsection Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern_name` | enum | yes | Canonical pattern name (one of six) |
| `definition` | string | yes | 1-sentence canonical definition (loaded from `maestro-agentic-patterns-shared.md`) |
| `severity_counts` | object | yes | `{Critical: N, High: N, Medium: N, Low: N}` for findings tagged with this pattern |
| `narrative` | string | yes | 100-200 word narrative describing manifestation in this architecture (generated by threat-report agent) |
| `impacted_finding_ids` | array | yes | Cross-references to findings tagged with this pattern (anchors into Section 7 Findings Detail) |
| `chain_membership_cross_refs` | array | optional | If a finding also participates in a Cross-Layer Attack Chain (Feature 141), narrative MAY cross-reference (e.g., "Finding F-12 participates in Chain CHAIN-002") — independence invariant preserved (FR-008) |

#### Subsection Ordering

1. Primary sort: max severity descending (Critical > High > Medium > Low > Note)
2. Secondary sort: finding count descending
3. Tertiary sort: pattern enum order (agent_collusion < emergent_behavior < temporal_attack < trust_exploitation < communication_vulnerability < resource_competition)

#### Multi-Pattern Subsection (when any finding has `agentic_pattern: multiple`)

A dedicated "Multi-Pattern Findings" subsection is rendered first (most architectural significance) when at least one finding carries `agentic_pattern: multiple`. The subsection lists each multi-pattern finding with all matching pattern names. Findings with `multiple` ALSO appear under each matching pattern's subsection (no exclusion).

---

## Schema Changes Summary

| File | Change Type | Schema Version |
|------|-------------|-----------------|
| `schemas/finding.yaml` | UPDATE — add `agentic_pattern` enum field | 1.3 → **1.4** (minor bump per ADR-026) |
| `schemas/attack-chain.yaml` | NO CHANGE — pattern data does not extend chain schema (FR-008) | unchanged |
| `templates/tachi/output-schemas/threats.md` | UPDATE — Pattern column + Section 4b | (no schema_version field on this template) |
| `templates/tachi/output-schemas/threat-report.md` | UPDATE — schema_version 1.1 → **1.2**; conditional Agentic Pattern Analysis section | 1.1 → 1.2 |

## Backward Compatibility Contract

- Pre-Feature-142 finding parsers (without `agentic_pattern` field knowledge) ignore the new field gracefully — schema 1.3 → 1.4 is additive
- Pre-Feature-142 baseline findings (without the field) parse with default `agentic_pattern: none` when consumed by Feature 142 parsers (FR-017)
- 5 non-multi-agent baseline architectures produce zero non-`none` patterns (FR-016 / SC-003) — multi-agent gate predicate enforced
- 5 baseline PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000 (FR-016 / SC-004)
- agentic-app intentionally regenerated as multi-agent demonstration target (consistent with Feature 141 / 136 convention)
- All 11 existing threat-detection agents (6 STRIDE + 5 AI) remain byte-identical (Option C zero-edit invariant per ADR-026)
