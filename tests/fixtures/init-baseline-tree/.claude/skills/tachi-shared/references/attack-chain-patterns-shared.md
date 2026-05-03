---
type: shared-reference
name: attack-chain-patterns-shared
version: 1.0.0
source_schema: schemas/attack-chain.yaml
consumers:
  - orchestrator
  - threat-report
---

# Cross-Layer Attack Chain Patterns — Shared Reference

Deterministic correlation pattern lookup table for cross-layer attack chain detection. Maps (STRIDE category, MAESTRO layer) pairs to valid successor (STRIDE category, MAESTRO layer) pairs with causal vocabulary. This is the single source of truth for chain assembly rules used during Phase 3.5.

**Source**: Derived from CSA MAESTRO cross-layer analysis patterns (February 2025, updated February 2026), MITRE ATT&CK v15+ lateral movement techniques, and OWASP LLM Top 10 v2025 chained attack scenarios.

---

## Causal Vocabulary

Use these canonical transition verbs when constructing chain narratives. Each verb describes a specific causal relationship between findings at adjacent layers.

| Verb | Meaning | Typical Direction |
|------|---------|-------------------|
| enables | Exploit at source layer creates the precondition for exploit at target layer | Downward (higher to lower layer number) |
| triggers | Exploit at source layer directly causes exploit at target layer | Downward or lateral |
| shifts | Exploit changes the attack surface from source layer to target layer | Any direction |
| manifests as | Cumulative effect of prior exploits becomes visible as business impact at target layer | Toward L7 (ecosystem/user impact) |

**Usage rules**:
- "enables" for indirect causal links (precondition)
- "triggers" for direct causal links (immediate consequence)
- "shifts" for lateral movement or layer-crossing pivot
- "manifests as" for terminal business impact (use only for the last transition in a chain)

---

## Transition Lookup Table

Organized by source layer. Each entry defines a valid (source STRIDE category, source layer) -> (target STRIDE category, target layer) transition with the causal verb and rationale.

### Source: L1 — Foundation Model

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Tampering | L2 | Tampering | triggers | Model output manipulation corrupts downstream data pipelines and vector stores |
| Tampering | L3 | Spoofing | enables | Manipulated model responses impersonate trusted agent instructions |
| Tampering | L3 | Privilege-Escalation | enables | Model manipulation produces outputs that bypass agent authorization checks |
| Info-Disclosure | L2 | Info-Disclosure | triggers | Model leaking training data exposes sensitive data in retrieval pipelines |
| Info-Disclosure | L7 | Info-Disclosure | manifests as | Model information leakage surfaces through agent ecosystem interfaces to end users |

### Source: L2 — Data Operations

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Tampering | L1 | Tampering | triggers | Poisoned training data or RAG context corrupts model behavior |
| Tampering | L3 | Spoofing | enables | Corrupted retrieval data causes agent to act on false context, impersonating trusted workflow |
| Tampering | L3 | Tampering | triggers | Poisoned data flows into agent planning, corrupting execution decisions |
| Tampering | L3 | Privilege-Escalation | enables | Manipulated data grants agent elevated permissions through corrupted authorization context |
| Info-Disclosure | L3 | Info-Disclosure | triggers | Exposed data store credentials or contents flow into agent context window |
| Info-Disclosure | L7 | Info-Disclosure | manifests as | Data exfiltration from vector stores surfaces through agent-to-user interfaces |

### Source: L3 — Agent Framework

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Tampering | L2 | Tampering | triggers | Compromised agent modifies data stores or vector indices |
| Tampering | L4 | Tampering | triggers | Agent manipulation alters deployment configuration or infrastructure state |
| Spoofing | L7 | Spoofing | manifests as | Agent identity impersonation surfaces as unauthorized actions visible to end users |
| Privilege-Escalation | L2 | Tampering | enables | Escalated agent privileges allow unauthorized data store modifications |
| Privilege-Escalation | L4 | Privilege-Escalation | triggers | Agent privilege escalation cascades to infrastructure-level access |
| Privilege-Escalation | L7 | Privilege-Escalation | manifests as | Agent with excessive permissions performs unauthorized ecosystem actions |
| Info-Disclosure | L7 | Info-Disclosure | manifests as | Agent leaks sensitive context through ecosystem interaction surfaces |
| Denial-of-Service | L4 | Denial-of-Service | triggers | Agent resource exhaustion cascades to infrastructure saturation |

### Source: L4 — Deployment Infrastructure

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Tampering | L3 | Tampering | enables | Infrastructure compromise provides access to modify agent configuration |
| Tampering | L6 | Tampering | triggers | Infrastructure manipulation disables or alters security controls |
| Info-Disclosure | L3 | Info-Disclosure | enables | Infrastructure data exposure reveals agent secrets or configuration |
| Info-Disclosure | L6 | Info-Disclosure | triggers | Infrastructure metadata leaks reveal security policy details |
| Privilege-Escalation | L3 | Privilege-Escalation | enables | Infrastructure-level access escalates to agent framework control |
| Denial-of-Service | L3 | Denial-of-Service | triggers | Infrastructure outage cascades to agent framework unavailability |
| Denial-of-Service | L7 | Denial-of-Service | manifests as | Infrastructure disruption renders agent ecosystem services unavailable |

### Source: L5 — Evaluation and Observability

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Tampering | L6 | Tampering | enables | Corrupted audit logs prevent detection of security control tampering |
| Repudiation | L6 | Repudiation | enables | Observability failure removes evidence trail for security violations |
| Repudiation | L3 | Repudiation | enables | Missing audit coverage allows agent actions to proceed without accountability |
| Denial-of-Service | L6 | Denial-of-Service | triggers | Monitoring blackout disables security alerting and automated response |

### Source: L6 — Security and Compliance

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Tampering | L3 | Privilege-Escalation | triggers | Disabled security controls allow agent to bypass authorization |
| Spoofing | L3 | Spoofing | enables | Authentication bypass at security layer enables agent identity impersonation |
| Spoofing | L7 | Spoofing | manifests as | Auth failure allows impersonated users to interact with agent ecosystem |
| Info-Disclosure | L3 | Info-Disclosure | enables | Leaked credentials or policies expose agent framework internals |
| Privilege-Escalation | L3 | Privilege-Escalation | triggers | RBAC bypass directly grants agents unauthorized capabilities |
| Privilege-Escalation | L7 | Privilege-Escalation | manifests as | Security policy bypass enables unauthorized ecosystem-level actions |

### Source: L7 — Agent Ecosystem

| Source Category | Target Layer | Target Category | Causal Verb | Rationale |
|----------------|-------------|-----------------|-------------|-----------|
| Spoofing | L3 | Spoofing | shifts | External entity impersonation at ecosystem boundary shifts to agent framework exploitation |
| Spoofing | L6 | Spoofing | shifts | Impersonated user at ecosystem boundary bypasses security controls |
| Tampering | L3 | Tampering | triggers | Malicious input through ecosystem interface corrupts agent behavior |
| Tampering | L2 | Tampering | triggers | Malicious user input propagates through agent to corrupt data stores |

---

## Chain Assembly Rules

### Minimum Requirements

1. **Layer span**: A chain must span at least 2 distinct MAESTRO layers.
2. **Severity threshold**: At least one member finding must have Critical or High severity.
3. **Structural evidence**: Adjacent findings in the chain must be connected by at least one correlation signal of type `component_lineage` or `data_flow_dependency`. Layer adjacency alone (`layer_adjacency_structural`) is insufficient — it must be combined with a structural relationship.

### Assembly Algorithm

1. **Group findings by component**: Collect findings targeting components connected by data flows in the architecture.
2. **Identify layer pairs**: For each pair of findings at different MAESTRO layers, check the transition lookup table for a valid (source category, source layer) -> (target category, target layer) entry.
3. **Verify structural evidence**: Confirm component lineage (data flow between components) or data flow dependency (shared data flow path) exists between the findings' target components.
4. **Build chains**: Link validated pairs into ordered sequences. A chain grows by appending findings where the last finding's (category, layer) has a valid transition to the new finding's (category, layer).
5. **Assign roles**: First finding = `initial_exploit`, last finding = `terminal_impact`, all others = `intermediate_cascade`.
6. **Filter**: Retain only chains with 2+ layers and at least one Critical/High finding.
7. **Rank**: Sort by max_severity descending (Critical > High > Medium > Low), then chain length descending, then chain_id alphabetical ascending.
8. **Cap**: Surface the top 5 chains. Include all chains in the artifact but mark only the top 5 as `surfaced: true`.

### Determinism

Chain assembly must produce identical output for identical input. This is achieved by:
- Deterministic transition lookup (table-based, no probabilistic scoring)
- Deterministic ranking (three-key sort with no ties possible due to alpha tiebreaker)
- Sequential chain ID assignment (CHAIN-001, CHAIN-002, ...) in ranked order

---

## Chain-Breaking Heuristic Algorithm

For each assembled chain, identify the structurally central finding whose remediation would maximally disrupt the chain.

### Algorithm

1. **2-link chains** (3 findings): The middle finding (index 1) is the chain-breaking point. Removing it disconnects the initial exploit from the terminal impact.

2. **3+ link chains** (4+ findings): Compute betweenness centrality for each intermediate finding:
   - For each intermediate finding at position `i` (0-indexed, excluding first and last):
   - Count the number of shortest paths between all other finding pairs that pass through position `i`
   - The finding with the highest count is the chain-breaking point
   - Tie-breaking: highest severity first, then earliest position in chain

3. **1-link chains** (2 findings): Identify the finding with the higher severity as the chain-breaking point. If equal severity, use the initial exploit.

### Output

For the identified chain-breaking finding, generate:
- `target_finding_id`: The finding ID
- `target_layer`: Its MAESTRO layer
- `structural_rationale`: Why removal breaks the chain (centrality explanation)
- `control_recommendation`: Specific control action derived from the finding's mitigation
- `is_heuristic`: Always `true`

### Disclaimer

Chain-breaking controls are structurally derived from graph centrality analysis. They identify the most disruptive remediation target based on chain topology, not verified control effectiveness. Security teams should validate recommended controls against their specific deployment context.

---

## AI Category Coverage (Scope Boundary)

The transition lookup table covers the 6 STRIDE categories only (Spoofing, Tampering, Repudiation, Info-Disclosure, Denial-of-Service, Privilege-Escalation). Findings with `agentic` or `llm` categories are intentionally excluded from the transition table because:

1. **Precision over recall**: AG and LLM findings often duplicate STRIDE findings at the same component (e.g., an AG-1 "tool abuse" finding at L3 overlaps with E-5 "privilege escalation" at L3). Including both in chain formation would produce redundant chains.
2. **STRIDE coverage is sufficient**: The STRIDE categories already cover the fundamental threat types. AI-specific findings add depth at a single layer but do not define new cross-layer transition patterns.
3. **Correlation groups handle overlap**: Phase 3 Section 4a already groups co-located STRIDE+AI findings. Phase 3.5 chains address a different dimension (cross-layer propagation).

AG and LLM findings CAN appear in chains indirectly when their target component also has a STRIDE finding that participates in a chain. The chain references the STRIDE finding; the AI finding remains linked via Section 4a correlation groups.

## MAESTRO Layer Normalization

The transition lookup table and chain schema use short-form layer codes (`L1` through `L7`). The finding IR from Phase 3 uses long-form values from `finding.yaml` (e.g., `"L3 — Agent Framework"`). During Phase 3.5, the orchestrator MUST normalize long-form to short-form by extracting the `L{N}` prefix before lookup table queries.

## Excluded Transitions

The following transitions are explicitly excluded from the lookup table because they lack reliable causal evidence in the CSA MAESTRO framework:

- **L1 -> L4**: Foundation model exploits rarely directly compromise deployment infrastructure without passing through L3 (agent framework)
- **L1 -> L6**: Model-level attacks affect security through L3 intermediaries, not directly
- **L4 -> L1**: Infrastructure compromise affects models through L2 (data operations), not directly
- **L5 -> L1**: Observability failures affect models through L6 (security) or L3 (agent) intermediaries
- **L7 -> L1**: External entity attacks reach foundation models through L3 or L2 intermediaries

These exclusions prevent false chain links. When CSA publishes additional cross-layer attack evidence, transitions can be added to the lookup table.
