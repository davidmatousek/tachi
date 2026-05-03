# ADR-003: STRIDE-per-Element Dispatch with Additive AI Keyword Matching

**Status**: Accepted
**Date**: 2026-03-21
**Deciders**: Architect
**Feature**: 003 (Orchestrator Agent)

---

## Context

The orchestrator agent needs a deterministic mechanism to decide which threat agents analyze which components. Given an architecture input with N components, each classified into one of four DFD element types (External Entity, Process, Data Store, Data Flow), the orchestrator must dispatch the correct subset of 11 threat agents (6 STRIDE + 5 AI) per component.

Key constraints:
- Dispatch rules must be deterministic -- the same input must always produce the same agent dispatch.
- STRIDE threat categories are not equally applicable to all DFD element types (e.g., External Entities cannot be tampered with directly).
- AI-specific threats apply only when a component involves LLM, agentic, or autonomous capabilities.
- The dispatch mechanism must be embeddable in a prompt file with no runtime dependencies.

---

## Decision

We will use **STRIDE-per-Element normalization** as the primary dispatch mechanism, with **additive AI keyword matching** as a secondary dispatch layer.

**STRIDE-per-Element**: Each component's DFD element type deterministically maps to a fixed set of applicable STRIDE categories via a normalization table:

| DFD Element Type | Applicable STRIDE Categories |
|------------------|------------------------------|
| External Entity  | S, R (2 categories) |
| Process          | S, T, R, I, D, E (6 categories) |
| Data Store       | T, I, D (3 categories) |
| Data Flow        | T, I, D (3 categories) |

**AI Keyword Dispatch**: After STRIDE dispatch, component names and descriptions are matched against keyword lists (case-insensitive, substring match) to determine if AI-specific agents should be additionally dispatched. LLM keywords (LLM, model, GPT, Claude) trigger 3 agents; AG keywords (agent, autonomous, orchestrator, MCP server, tool server, plugin) trigger 2 agents. AI dispatch is always additive -- it never replaces STRIDE dispatch.

---

## Rationale

**Reasons**:
1. **Deterministic by design**: DFD type-to-STRIDE mapping is a fixed lookup table. No probabilistic reasoning, no LLM judgment for dispatch decisions. The same component type always receives the same STRIDE agents.
2. **Coverage guarantee**: Every component receives at least 2 STRIDE agents (External Entity minimum). Process elements receive all 6. No component is under-analyzed due to dispatch logic.
3. **O(n) scaling**: Dispatch cost scales linearly with the number of components. Each component requires one table lookup (STRIDE) plus one keyword scan (AI). No pairwise comparisons.
4. **Embeddable in prompt**: The normalization table and keyword lists are static data that can be expressed in markdown/YAML within the orchestrator prompt file. No external dispatch engine required.
5. **Separation of concerns**: STRIDE dispatch is structural (based on what the component IS). AI dispatch is semantic (based on what the component DOES). The two layers are independent and composable.

---

## Alternatives Considered

### Alternative 1: LLM-Judged Dispatch
Let the LLM decide which agents to invoke per component based on its understanding of the architecture.

**Pros**:
- More nuanced dispatch for edge cases
- Could handle novel component types not anticipated in the normalization table

**Cons**:
- Non-deterministic: same input may produce different dispatch decisions across runs
- No coverage guarantee: LLM may skip relevant agents
- Not auditable: dispatch decisions are opaque
- Higher token cost: requires reasoning about dispatch for each component

**Why Not Chosen**: Determinism and auditability are critical for threat modeling. Dispatch decisions must be reproducible and explainable. LLM judgment is used within agents for threat analysis, not for dispatch routing.

### Alternative 2: Full-Matrix Dispatch (All Agents for All Components)
Dispatch all 11 agents for every component regardless of DFD type.

**Pros**:
- Simplest dispatch logic (no normalization needed)
- Maximum theoretical coverage

**Cons**:
- Produces irrelevant findings (e.g., Tampering analysis on an External Entity)
- O(n * 11) agent invocations regardless of applicability
- Higher token cost and execution time
- Noise in output reduces signal quality

**Why Not Chosen**: STRIDE-per-Element is an established methodology that filters out structurally inapplicable threats. Dispatching all agents produces false positives that reduce the utility of the threat model.

### Alternative 3: Rule Engine with Complex Conditions
Build a multi-factor rule engine that considers DFD type, technology stack, trust boundary position, and semantic analysis to determine dispatch.

**Pros**:
- Most precise dispatch possible
- Could reduce false positives further

**Cons**:
- Complex rules are hard to embed in a prompt file
- Rule interactions create debugging challenges
- Maintenance burden increases with each new rule
- Over-optimization risks missing threats that simpler rules would catch

**Why Not Chosen**: The two-layer approach (structural STRIDE + semantic AI keywords) achieves good precision with minimal complexity. The normalization table is established methodology; the keyword layer adds AI-specific coverage without complicating the structural layer.

---

## Consequences

### Positive
- Deterministic, reproducible dispatch decisions for any architecture input
- Coverage matrix in output directly traces back to dispatch rules, enabling audit
- Intermediate dispatch table artifact provides pre-execution validation checkpoint
- New AI keyword categories can be added without modifying the STRIDE normalization layer

### Negative
- Keyword matching may produce false positives (e.g., "model" in "data model" triggers LLM dispatch)
- Static normalization table cannot handle novel DFD element types without modification
- Ambiguous component classification defaults to Process (broadest coverage), which may over-dispatch

### Mitigation
- Ambiguous keyword matches (e.g., "model") are annotated in the dispatch table for human review
- Ambiguous DFD classification defaults to Process and is flagged in the component description
- Self-check validation at both intermediate output points (Component Inventory and Dispatch Table) catches dispatch errors before agent execution

---

## Related Decisions

- ADR-001: Atomic State Persistence (orchestrator state management)
- ADR-002: Prompt Segmentation (orchestrator prompt architecture)

---

## References

- [STRIDE-per-Element methodology](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Threat Modeling Process](https://owasp.org/www-community/Threat_Modeling_Process)
- Feature 003 spec: `specs/003-orchestrator-agent/spec.md`
- Orchestrator implementation: `agents/orchestrator.md`
