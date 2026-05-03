---
type: shared-reference
name: maestro-agentic-patterns-shared
version: 1.0.0
source_schema: schemas/finding.yaml
consumers:
  - orchestrator
  - threat-report
---

# MAESTRO Agentic Patterns — Shared Reference

Deterministic classification source for Phase 3.6 pattern synthesis. Defines the six canonical CSA MAESTRO cross-cutting agentic threat patterns, their coverage by existing tachi agents, the classification rule table consumed by the orchestrator at finding-emission time, and the multi-agent gate predicate that conditions non-`none` pattern assignment on architectural topology.

**Source**: Cloud Security Alliance, "Agentic AI Threat Modeling Framework: MAESTRO", February 2025 ([blog post](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)). Pattern semantics derived verbatim from the CSA cross-cutting taxonomy. Detection criteria extended with tachi-specific architectural indicators (component types, topology signals) that the synthesis engine can evaluate deterministically from the Phase 1 component inventory and data flow graph.

**Determinism Invariants**:
- This file is the single source of truth for the component_type token list (Section 4) and the topology indicator list (Section 4). Adding new tokens or indicators requires a minor version bump on this file and triggers backward-compatibility revalidation against all 6 example architectures.
- Rule evaluation is a pure function of finding fields (`category`, `maestro_layer`, `target_component`, `description`) and architectural metadata (component inventory + data flow graph). No LLM judgment is involved at the synthesis step (per ADR-021).
- The multi-agent gate predicate is evaluated EXACTLY ONCE per architecture and cached for the duration of Phase 3.6.

---

## Section 1: Six Canonical Pattern Definitions

Canonical ordering: Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Communication Vulnerabilities, Resource Competition. This ordering is used as the tertiary tiebreaker for threat-report subsection rendering (per data-model.md Entity 6).

### 1.1 Agent Collusion

**Definition**: Multiple compromised agents coordinate to achieve malicious objectives that no single agent could accomplish alone — exfiltrating data across shared channels, jointly manipulating planning outputs, or circumventing policies by distributing actions below per-agent detection thresholds.

**Representative Examples**:
- Two compromised agents jointly issuing high-volume tool calls to stage a coordinated DDoS against a downstream API, where per-agent rate limits would block a single-agent equivalent
- A supervisor agent and a worker agent exchanging information through a shared memory store to exfiltrate sensitive context that neither agent could extract on its own
- Three peer agents splitting a prohibited action into three individually-permitted sub-actions that collectively violate a governance policy (policy circumvention by action decomposition)

**Detection Criteria**:
- **Architectural preconditions**: ≥2 components classified `agentic` or `llm` AND ≥1 inter-component data flow between two agentic components (multi-agent topology with cooperation pathway)
- **Keyword indicators**: `coordinate`, `joint`, `cooperate`, `collude`, `shared channel`, `cross-agent`, `inter-agent`
- **Finding signals**: STRIDE category in [`spoofing`, `tampering`, `info-disclosure`] on an agentic-category component whose data flow graph links to another agentic component

**CSA Citation**: <https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro>

### 1.2 Emergent Behavior

**Definition**: Attackers exploit unpredictable behaviors that arise only from the interaction of multiple agents (cascading failures, feedback amplification, behavioral drift) — behaviors that are invisible in per-agent analysis and manifest only when agents act in concert.

**Representative Examples**:
- A supervisor-worker loop where a single malformed worker output cascades into progressively more malformed supervisor instructions, amplifying the error across successive turns until the system collapses into an unrecoverable state
- Two peer agents negotiating over a shared goal develop a narrow, unintended optimization that bypasses safety constraints when evaluated jointly (collective reward-hacking not visible to either agent in isolation)
- Behavioral drift in a mesh of agents where each agent adjusts to its neighbors' responses, producing a collective behavior that no single agent's safety evaluation would flag

**Detection Criteria**:
- **Architectural preconditions**: ≥2 components classified `agentic` or `llm` (multi-agent topology required; single-agent cascade failures are covered by agent-autonomy)
- **Keyword indicators**: `cascade`, `unpredictable`, `interaction`, `emergent`, `drift`, `feedback amplification`, `collective behavior`
- **Finding signals**: finding description contains at least one of the emergent-behavior keywords AND target component is `agentic`/`llm` category

**CSA Citation**: <https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro>

### 1.3 Temporal Attacks

**Definition**: Attacks that exploit persistent state to achieve delayed or time-gated effects — sleeper agents activating under specific triggers, gradual corruption of learned parameters, seasonal exploitation patterns, or poisoned training data that surfaces only during re-training cycles.

**Representative Examples**:
- A sleeper agent embedded during fine-tuning that remains dormant until a specific keyword triggers malicious behavior months after deployment (time-delayed activation via model poisoning)
- Gradual corruption of a persistent agent memory store across many interactions, each individually below detection thresholds, that cumulatively rewrites the agent's operational context
- A learning loop that incorporates adversarial feedback over a training window, causing the agent to drift toward attacker-preferred outputs on a seasonal schedule

**Detection Criteria**:
- **Architectural preconditions**: architecture contains at least one of: a fine-tuning pipeline component, a persistent agent memory store, or a long-running learning loop (persistent_state topology indicator)
- **Keyword indicators**: `sleeper`, `time-delayed`, `gradual`, `seasonal`, `drift`, `persistent state`, `dormant`, `re-training`
- **Finding signals**: ANY architectural context match (finding-level signals are weak for temporal attacks; architectural context dominates). Net-new finding emission MAY be triggered by R-02 when no existing finding carries the pattern.

**CSA Citation**: <https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro>

### 1.4 Trust Exploitation

**Definition**: Attacks that subvert the trust relationships between agents — identity spoofing between cooperating agents, reputation manipulation in agent registries, trust chain attacks that pivot from a weakly-trusted agent to a highly-trusted peer, and impersonation of supervisor agents.

**Representative Examples**:
- An attacker spoofs the identity of a trusted supervisor agent to issue commands to worker agents that would be rejected if issued by an untrusted party (inter-agent identity forgery)
- Reputation manipulation in a peer-agent registry where an attacker accumulates trust signals through low-stakes interactions, then leverages the accumulated trust to execute high-stakes malicious actions
- Trust chain pivot where a compromise of a single low-privilege agent enables lateral escalation through trust relationships to a supervisor that grants privileged actions to "trusted peers"

**Detection Criteria**:
- **Architectural preconditions**: ≥2 components classified `agentic` or `llm` (multi-agent topology; single-agent identity attacks are covered by spoofing)
- **Keyword indicators**: `impersonate`, `trust`, `identity`, `peer`, `supervisor`, `reputation`, `credential forgery`, `inter-agent identity`
- **Finding signals**: STRIDE category in [`spoofing`] OR AI category `agentic` on a component with multi-agent topology

**CSA Citation**: <https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro>

### 1.5 Communication Vulnerabilities

**Definition**: Attacks against the inter-agent messaging substrate — interception of messages on shared channels, protocol manipulation that degrades authentication or integrity guarantees, routing attacks that divert messages to adversary-controlled agents, and replay attacks on agent-to-agent communication.

**Representative Examples**:
- Eavesdropping on an inter-agent message bus to harvest sensitive context that agents exchange in plaintext (inter-agent information disclosure)
- Protocol downgrade on an agent-to-agent channel that forces unauthenticated or unencrypted messaging, enabling tampering or spoofing of subsequent messages
- Message routing manipulation where an attacker-controlled agent inserts itself as a relay between two peer agents, reading and selectively modifying messages in transit (agent-in-the-middle)

**Detection Criteria**:
- **Architectural preconditions**: architecture has an `inter_agent_channel` component AND the architecture is `multi_agent` (composite; both conditions must hold)
- **Keyword indicators**: `intercept`, `eavesdrop`, `message`, `bus`, `channel`, `routing`, `protocol`, `downgrade`, `replay`, `relay`
- **Finding signals**: STRIDE category in [`info-disclosure`, `tampering`] OR AI category `tool-abuse` on a component matching the `inter_agent_channel` token

**CSA Citation**: <https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro>

### 1.6 Resource Competition

**Definition**: Attacks that exploit contention between agents for shared resources — resource monopolization by one agent starving peers, priority manipulation in shared schedulers, coordination disruption that induces resource-use conflicts, and quota-exhaustion attacks that degrade peer agents' availability.

**Representative Examples**:
- A compromised agent monopolizes a shared rate-limited external API, starving peer agents of the quota they need to complete their objectives (resource monopolization)
- Priority-manipulation of a shared task queue where an attacker inflates their agent's priority signals to preempt peer work (scheduler exploitation)
- Coordination disruption in a swarm of delegated workers, where an attacker induces two peers to contend for the same lock or mutex, causing both to fail and cascading into supervisor-level retry storms

**Detection Criteria**:
- **Architectural preconditions**: ≥2 components classified `agentic` or `llm` (multi-agent topology; single-agent DoS is covered by denial-of-service)
- **Keyword indicators**: `resource`, `monopol`, `competition`, `priority`, `quota`, `starve`, `preempt`, `contention`, `lock`, `mutex`
- **Finding signals**: STRIDE category `denial-of-service` OR AI category `agentic` on a multi-agent component whose description contains at least one resource-competition keyword

**CSA Citation**: <https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro>

---

## Section 2: Coverage Mapping Table

This table records tachi's current coverage of the six canonical MAESTRO patterns by existing detection agents. Coverage Strength values are restricted to exactly three values: `Full`, `Partial`, `None — Coverage Required`. The restricted vocabulary prevents vague qualifiers ("Strong", "Mostly", "Almost") that would enable overclaiming and undermine the gap analysis purpose.

Every `Partial` row includes a 1-sentence Gap justification naming what the existing agent misses.

| Pattern | Currently Covered By | Coverage Strength | Gap |
|---------|----------------------|-------------------|-----|
| Agent Collusion | None directly | None — Coverage Required | New detection required — Phase 3.6 rule R-01 (existing 11 agents lack cross-finding + multi-agent architectural reasoning) |
| Emergent Behavior | agent-autonomy (cascading failures detected per-agent) | Partial | agent-autonomy detects per-agent cascade but misses cross-agent emergent patterns that manifest only from multi-agent interaction |
| Temporal Attacks | None directly | None — Coverage Required | New detection required — Phase 3.6 rule R-02 with net-new finding generation (no existing agent inspects persistent-state components for temporal vectors) |
| Trust Exploitation | spoofing (identity attacks), tool-abuse (tool trust boundaries) | Partial | spoofing covers single-agent identity forgery but misses inter-agent identity context; tool-abuse covers tool-level trust but misses the agent-to-agent trust chain semantics |
| Communication Vulnerabilities | tool-abuse (MCP/protocol attacks), info-disclosure (generic eavesdropping) | Partial | Existing agents cover component-level eavesdropping and protocol attacks but miss the inter-agent messaging context (per-component analysis cannot express "message between two agents on a shared bus") |
| Resource Competition | denial-of-service (component-level exhaustion), agent-autonomy (runaway agent resource consumption) | Partial | denial-of-service covers per-component availability; agent-autonomy covers single-agent runaway; neither captures the multi-agent contention semantic (one agent starving peers) |

**Governance Note (FR-002 precedent)**: Future tachi releases that add a new AI agent MUST update this coverage mapping table as part of that feature's deliverables. Coverage claims on this table are load-bearing for feature planning — overclaiming invalidates the gap analysis and must be avoided.

---

## Section 3: Classification Rule Table

Rule entries consumed by the orchestrator Phase 3.6 synthesis engine. Each rule is evaluated in ascending `priority` order (lowest priority value = most specific = evaluated first). The first matching rule wins; findings matching two or more rules with equal priority receive `agentic_pattern: multiple` per the tie-breaking rule in data-model.md Entity 3.

Rules with `generates_finding_when_no_match: true` may emit net-new findings (id prefix `AGP-`) when the architectural context matches and no existing finding already carries the pattern label. Net-new finding generation is a Phase 3.6 Step 3 operation that runs after Step 2 (existing-finding pattern assignment).

```yaml
rules:
  - rule_id: R-01
    pattern: agent_collusion
    priority: 10
    match_conditions:
      category_in:
        - agentic
        - llm
      architecture_has:
        topology:
          - inter_agent_data_flow
      description_contains:
        - coordinate
        - joint
        - collude
        - cross-agent
        - inter-agent
        - shared channel
        - shared memory
    generates_finding_when_no_match: true
    generation_template: |
      Two or more agentic components in {component} coordinate over an inter-agent
      data flow, creating a potential for coordinated malicious action. Compromised
      agents could jointly exfiltrate data, split prohibited actions across peers,
      or issue coordinated tool calls that individually fall below per-agent
      detection thresholds. Recommended controls: inter-agent rate limits,
      coordination throttles, and per-flow audit logging.

  - rule_id: R-02
    pattern: temporal_attack
    priority: 20
    match_conditions:
      architecture_has:
        topology:
          - persistent_state
    generates_finding_when_no_match: true
    generation_template: |
      The architecture includes {component} — a persistent-state component
      (fine-tuning pipeline, persistent agent memory, or long-running learning
      loop) that enables temporal attacks: sleeper agents activated by delayed
      triggers, gradual corruption below detection thresholds, and seasonal
      exploitation patterns. Recommended controls: training-data provenance
      attestation, memory-write audit trails, and periodic behavioral
      baselining against pre-training snapshots.

  - rule_id: R-03
    pattern: emergent_behavior
    priority: 30
    match_conditions:
      category_in:
        - agentic
        - llm
      architecture_has:
        topology:
          - multi_agent
      description_contains:
        - cascade
        - unpredictable
        - interaction
        - emergent
    generates_finding_when_no_match: true
    generation_template: |
      Multi-agent interactions in {component} exhibit the potential for emergent
      behavior — cascading failures, feedback amplification, or collective
      optimization that bypasses per-agent safety evaluation. Recommended
      controls: fail-safe shutdown circuits, bounded action scopes per agent,
      and behavioral baselining of the collective agent system.

  - rule_id: R-04
    pattern: trust_exploitation
    priority: 40
    match_conditions:
      category_in:
        - spoofing
        - agentic
      architecture_has:
        topology:
          - multi_agent
    generates_finding_when_no_match: false

  - rule_id: R-05
    pattern: communication_vulnerability
    priority: 50
    match_conditions:
      # NOTE: `agentic` is the schema enum value for findings produced by the tool-abuse agent
      # (per schemas/finding.yaml category enum). R-05 targets tool-abuse-category findings via the
      # `agentic` enum value plus `info-disclosure` for eavesdropping-style findings.
      category_in:
        - agentic
        - info-disclosure
      target_component_matches:
        type_or_name_regex: '(?i)(inter.?agent.?channel|message.?bus|agent.?communication.?channel|shared.?(queue|memory))'
      architecture_has:
        topology:
          - inter_agent_channel
    generates_finding_when_no_match: false

  - rule_id: R-06
    pattern: resource_competition
    priority: 60
    match_conditions:
      category_in:
        - denial-of-service
        - agentic
      architecture_has:
        topology:
          - multi_agent
      description_contains:
        - resource
        - monopol
        - competition
        - priority
    generates_finding_when_no_match: false
```

**R-01 refinement (Feature 142 P1 architect checkpoint, 2026-04-16)**: R-01 was initially authored with `architecture_has.topology: [multi_agent, inter_agent_data_flow]` as a disjunction and no `description_contains` filter. The P1 architect review surfaced that this caused R-01 to classify every agentic/llm finding in a multi-agent architecture as Agent Collusion, including findings that describe single-agent autonomy (e.g., `Autonomous execution of consequential tool calls`) rather than cross-agent coordination. The revised R-01 (Wave 3 Issue 2 remediation) requires BOTH the architectural precondition (inter_agent_data_flow topology) AND finding-level evidence of coordination semantics (`description_contains` with collusion-indicative tokens). This preserves the rule's semantic fidelity to the CSA Agent Collusion definition ("multiple compromised agents coordinating to achieve malicious objectives") and primarily surfaces the pattern via net-new AGP-NN generation (Step 3) rather than existing-finding classification (Step 2).

**Rule Priority and Tie-Breaking**:
- Rules evaluated in ascending `priority` order (10 → 20 → 30 → 40 → 50 → 60). Lowest value = most specific = first match wins.
- If two rules share identical priority AND both match the same finding: the finding receives `agentic_pattern: multiple`.
- Findings matching no rule receive `agentic_pattern: none`.
- Total-ordered priority (no two rules currently share a priority value) — no `multiple` assignments are emitted by the initial rule set R-01 through R-06. Future rule additions that share priority with an existing rule warrant a minor version bump on this file and an explicit tie-breaking design note.

**Match Condition Semantics**:
- `category_in` — `finding.category` MUST be in the list (disjunction within the condition).
- `maestro_layer_in` — `finding.maestro_layer` MUST be in the list (disjunction within the condition). Not used by R-01 through R-06; reserved for future rules.
- `target_component_matches.type_or_name_regex` — case-insensitive regex match against the target component's type OR name.
- `architecture_has.topology` — at least one listed topology indicator MUST evaluate true against the Phase 1 component inventory + data flow graph (disjunction within the condition).
- `architecture_has.component_type` — at least one listed component_type token MUST evaluate true against the architecture description (disjunction within the condition). Not used by R-01 through R-06 at the rule level; component_type tokens are consumed transitively via the `persistent_state` and `inter_agent_channel` topology indicators.
- `description_contains` — `finding.description` MUST contain at least one listed token (case-insensitive substring match; disjunction within the condition).

All conditions within a single `match_conditions` block are conjoined (AND): a rule fires only when EVERY specified condition is satisfied.

**Net-New Finding Generation Constraints**:
- Only R-01, R-02, R-03 have `generates_finding_when_no_match: true` (the three previously-uncovered patterns).
- R-04, R-05, R-06 have `generates_finding_when_no_match: false` — existing agents (spoofing, tool-abuse, info-disclosure, denial-of-service) produce findings that the rule retroactively classifies; no net-new generation needed.
- Generation is suppressed when any existing finding already carries the pattern label (prevents duplicate coverage).
- Maximum 1 net-new finding per pattern per architecture (no flooding).
- Net-new finding id format: `AGP-NN` (sequential, aligned with the existing 1-4 letter prefix convention S/T/R/I/D/E/AG/LLM). The `schemas/finding.yaml` `id.pattern` regex is extended in Wave 0 to accept the new prefix.

---

## Section 4: Multi-Agent Gate Predicate

The multi-agent gate predicate is evaluated once per architecture at the start of Phase 3.6 (before rule table application). The predicate gates the assignment of any non-`none` `agentic_pattern` value: if the predicate returns `false`, every finding receives `agentic_pattern: none` and Phase 3.6 exits without modifying the finding IR further and without emitting net-new findings. If the predicate returns `true`, the classification rule table is applied to every finding.

The predicate is the single enforcement point for FR-006 across all six patterns. It is enforced regardless of which individual rule is under evaluation.

### Predicate Specification

The predicate returns `true` when at least one of three OR conditions (a, b, c) holds against the architecture description and component inventory. All three conditions are independently sufficient; any one triggers the `true` branch.

**Condition (a) — Agentic Component Count**: at least 2 components are classified as `agentic` or `llm` category in the Phase 1 dispatch keywords. This condition alone — without inter-agent communication or explicit multi-agent keywords — is sufficient because two or more agents in the same architecture introduce the semantic surface for coordination, trust, and emergent interaction even if the current data flow graph does not yet encode the interaction explicitly.

**Condition (b) — Inter-Agent Data Flow**: at least 1 inter-component data flow exists where BOTH source and target components are classified as `agentic` or `llm` category. A single `agentic` ↔ `data_store` or `agentic` ↔ `external_service` flow does NOT count — both endpoints must be agentic.

**Condition (c) — Explicit Multi-Agent Keywords**: case-insensitive substring search on the architecture description matches at least one of: `multi-agent`, `swarm`, `supervisor`, `delegation`, `agent mesh`. This list is authoritative; expansion requires a minor version bump on this file.

### Predicate Evaluation Algorithm

```
function evaluate_multi_agent_gate(architecture, components):
    # Condition (a) — count components by dispatch keyword category
    agentic_llm_count = count_components_with_category(
        components,
        categories=["agentic", "llm"]
    )
    condition_a = agentic_llm_count >= 2

    # Condition (b) — inter-agent data flow endpoints
    condition_b = exists_inter_component_data_flow(
        components,
        source_in_categories=["agentic", "llm"],
        target_in_categories=["agentic", "llm"]
    )

    # Condition (c) — keyword match on architecture description
    condition_c = any_keyword_match(
        architecture.description,
        keywords=["multi-agent", "swarm", "supervisor", "delegation", "agent mesh"],
        case_insensitive=True
    )

    result = condition_a or condition_b or condition_c

    return {
        "result": result,
        "condition_a": condition_a,
        "condition_b": condition_b,
        "condition_c": condition_c,
        "evaluation_metadata": {
            "agentic_llm_count": agentic_llm_count,
            "matched_components": matched_component_list,
            "matched_keywords": matched_keyword_list
        }
    }
```

The evaluation is a pure function of the architecture description and component inventory (both produced by Phase 1). Predicate output is byte-identical across repeated runs with identical inputs (per ADR-021 determinism). The result is cached for the duration of Phase 3.6 and MUST NOT be re-evaluated per finding.

### Component Type Token List (canonical, finite)

The `architecture_has.component_type` condition uses this explicit finite token list. Tokens match case-insensitively against the architecture description's component types and component names. This list IS the source of truth — fuzzy matching, embedding-based similarity, and LLM-based interpretation are explicitly prohibited. Adding new tokens requires a minor version bump on this file.

| Token | Keyword Match Strings (case-insensitive; any match triggers the token) | Used By |
|-------|-----------------------------------------------------------------------|---------|
| `fine_tuning_pipeline` | "fine-tuning pipeline", "fine tuning pipeline", "training pipeline", "fine-tune pipeline" | R-02 (via `persistent_state` topology) |
| `persistent_agent_memory` | "agent memory", "persistent memory", "memory store", "long-term memory", "agent state store" | R-02 (via `persistent_state` topology) |
| `long_running_learning_loop` | "learning loop", "feedback loop", "continual learning", "RLHF loop", "reward model loop", "self-improvement loop" | R-02 (via `persistent_state` topology) |
| `inter_agent_channel` | "inter-agent channel", "message bus" (when context is multi-agent), "agent communication channel", "shared queue" (when context is multi-agent), "shared memory" (when context is multi-agent) | R-05 (via `inter_agent_channel` topology) |

### Topology Indicator List (canonical, finite)

The `architecture_has.topology` condition uses this explicit finite list of topology indicators. Each indicator is a deterministic structural check on the Phase 1 component inventory and data flow graph. This list IS the source of truth — adding new indicators requires a minor version bump on this file.

| Topology Indicator | Definition | Used By |
|--------------------|------------|---------|
| `multi_agent` | ≥2 components classified as `agentic` or `llm` category in Phase 1 dispatch keywords (matches multi-agent gate predicate condition (a)) | R-01, R-03, R-04, R-06 |
| `inter_agent_data_flow` | ≥1 inter-component data flow where BOTH source and target components are `agentic` or `llm` (matches multi-agent gate predicate condition (b)) | R-01 |
| `persistent_state` | At least one component matches any of the three `persistent_state`-related component_type tokens (`fine_tuning_pipeline`, `persistent_agent_memory`, `long_running_learning_loop`) — convenience grouping for R-02 | R-02 |
| `inter_agent_channel` | At least one component matches the `inter_agent_channel` component_type token AND the architecture is `multi_agent` (composite; both conditions must hold) | R-05 |

### Worked Examples on the 6 Tachi Examples

The table below evaluates the multi-agent gate predicate against the six existing tachi example architectures. It establishes the expected behavior against which Phase 5 regeneration validates the predicate is neither over-eager (false positives on single-agent baselines) nor under-eager (false negatives on the extended multi-agent example).

| Example | Condition (a): ≥2 agentic/llm | Condition (b): inter-agent flow | Condition (c): keyword match | Predicate Result | Pattern Findings Expected |
|---------|-------------------------------|-------------------------------|------------------------------|------------------|---------------------------|
| web-app | false | false | false | **false** | `agentic_pattern: none` on every finding |
| microservices | false | false | false | **false** | `agentic_pattern: none` on every finding |
| ascii-web-api | false | false | false | **false** | `agentic_pattern: none` on every finding |
| mermaid-agentic-app | **true** (≥2 agents in Mermaid DFD) | false | false | **true** | predicate TRUE via (a) alone; rule table MUST NOT match any non-`none` pattern because no inter-agent communication, no persistent state, and no multi-agent keywords — any rule match on this architecture indicates a false positive and requires rule tightening |
| free-text-microservice | false | false | false | **false** | `agentic_pattern: none` on every finding |
| agentic-app (extended for Feature 142) | **true** (3 agents: Orchestrator + Specialist + Audit Logger's downstream Learning Loop subsystem) | **true** (Specialist ↔ Orchestrator via Inter-agent Channel) | **true** ("multi-agent" keyword in architecture description) | **true** | non-`none` patterns expected for ≥3 (Agent Collusion, Temporal Attack, Emergent Behavior); net-new AGP-NN findings expected for the three previously-uncovered patterns |

**Note on mermaid-agentic-app**: This architecture satisfies condition (a) alone — the Mermaid DFD contains multiple agent components — but lacks inter-agent communication channels, persistent-state components, and explicit multi-agent coordination keywords. The predicate evaluates `true`, so the rule table is applied, but no rule should match: R-01 requires `inter_agent_data_flow` (absent), R-02 requires `persistent_state` (absent), R-03 requires both `multi_agent` AND emergent-behavior description tokens (absent), R-04 requires a `spoofing`/`agentic` finding on multi-agent topology (no such finding in the current baseline), R-05 requires an `inter_agent_channel` component (absent), R-06 requires a `denial-of-service` finding with resource-competition tokens (absent from current baseline). Phase 5 regeneration validates that zero non-`none` patterns appear in mermaid-agentic-app output; if any rule incorrectly matches, the rule's `match_conditions` are tightened (typically by adding `description_contains` constraints) to exclude the false positive.

**Note on backward compatibility**: The 5 single-predicate-false architectures (web-app, microservices, ascii-web-api, free-text-microservice, and mermaid-agentic-app) MUST produce zero non-`none` pattern findings after Feature 142 ships. This is the structural foundation for SC-004 (5 baseline PDFs byte-identical under SOURCE_DATE_EPOCH=1700000000). The mermaid-agentic-app case is a true-predicate-no-rule-match edge case that must be validated empirically during Phase 5.

---

## Cross-References

- [ADR-026: Agentic Pattern Classification Mechanism](../../../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md) — canonical decision record for the Hybrid Post-Hoc Synthesis (Option C) mechanism that consumes this shared reference
- [ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF Comparison](../../../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) — determinism invariant that this file preserves (rule evaluation is pure-function; no LLM judgment)
- [ADR-020: MAESTRO Layer Classification](../../../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — Phase 3 agentic pattern expansion is an extension of ADR-020; Revision History entry added in Feature 142 Wave 4
- [ADR-019: Shared Cross-Agent Definitions](../../../../docs/architecture/02_ADRs/ADR-019-shared-definitions-and-model-field-governance.md) — governance pattern for shared references under `.claude/skills/tachi-shared/references/`; this file follows the ADR-019 frontmatter and consumer-listing convention
- [attack-chain-patterns-shared.md](attack-chain-patterns-shared.md) — sister shared reference for Feature 141 Phase 3.5 cross-layer chain correlation; pattern synthesis (this file) and chain correlation are independent grouping mechanisms per FR-008 (a finding may appear in both a pattern subsection and a chain)
- [maestro-layers-shared.md](maestro-layers-shared.md) — MAESTRO layer definitions; `agentic_pattern` field is independent of `maestro_layer` (a pattern finding can target a component with any layer value, including `Unclassified`)
