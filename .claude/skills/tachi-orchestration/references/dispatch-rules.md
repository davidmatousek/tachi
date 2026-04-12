---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# STRIDE + AI Dispatch Rules and Correlation Matrices

## STRIDE-per-Element Normalization

Each component from the Phase 1 inventory is mapped to its applicable STRIDE threat categories based on its DFD element type. Agents are dispatched only for applicable categories, ensuring focused analysis.

### Normalization Mapping

```yaml
stride_per_element:
  External Entity:
    applicable_categories: [S, R]
    description: >
      External entities can be spoofed (S) and may deny actions (R).
      They do not process, store, or transport data directly.

  Process:
    applicable_categories: [S, T, R, I, D, E]
    description: >
      Processes are subject to all six STRIDE categories.
      They are the most broadly threatened element type.

  Data Store:
    applicable_categories: [T, I, D]
    description: >
      Data stores can be tampered with (T), leak information (I),
      or be rendered unavailable (D).

  Data Flow:
    applicable_categories: [T, I, D]
    description: >
      Data flows can be tampered with in transit (T), leak
      information (I), or be disrupted (D).
```

### Quick Reference

| DFD Element Type | S | T | R | I | D | E |
|------------------|---|---|---|---|---|---|
| External Entity  | x |   | x |   |   |   |
| Process          | x | x | x | x | x | x |
| Data Store       |   | x |   | x | x |   |
| Data Flow        |   | x |   | x | x |   |

**Category legend**: S = Spoofing, T = Tampering, R = Repudiation, I = Information Disclosure, D = Denial of Service, E = Elevation of Privilege

For each component in the Phase 1 inventory, look up its DFD element type in the table above. The marked categories (x) are the STRIDE agents to dispatch for that component. Every DFD element type maps to at least 2 STRIDE categories, so the normalization step never produces zero applicable categories for a valid component.

---

## AI Keyword Dispatch Rules

In addition to STRIDE dispatch, components are evaluated for AI-specific threat analysis. AI dispatch is **additive** to STRIDE dispatch — it never replaces STRIDE categories. A component always receives its STRIDE agents first, and AI agents are added on top when keywords match.

### Keyword-to-Category Mapping

**LLM keywords** — when any of the following keywords are found in a component's name or description, dispatch the LLM threat agents:

- `"LLM"`
- `"model"`
- `"GPT"`
- `"Claude"`

LLM dispatch triggers these agents:
- `prompt-injection` (OWASP LLM01:2025)
- `data-poisoning` (OWASP LLM03:2025)
- `model-theft` (OWASP LLM10:2025)

**AG keywords** — when any of the following keywords are found in a component's name or description, dispatch the AG (Agentic) threat agents:

- `"agent"`
- `"autonomous"`
- `"orchestrator"`
- `"MCP server"`
- `"tool server"`
- `"plugin"`

AG dispatch triggers these agents:
- `agent-autonomy` (ASI-01)
- `tool-abuse` (MCP-03)

### Matching Rules

1. **Case-insensitive**: All keyword matching is case-insensitive. "llm", "LLM", "Llm" all match.
2. **Scope**: Keywords are matched against both the component **name** and the component **description** from the Phase 1 inventory.
3. **Multi-word keywords**: Keywords containing spaces (e.g., "MCP server", "tool server") match as a complete phrase. The words must appear adjacent and in order.
4. **Substring matching**: A keyword match anywhere within the name or description triggers dispatch. For example, "ModelValidator" contains "model" and triggers LLM dispatch.

### Dual-Dispatch

When a component matches keywords from **both** the LLM and AG categories, both agent categories are dispatched. This is called dual-dispatch.

**Example**: A component named "LLM Agent Orchestrator" matches:
- `"LLM"` --> LLM agents dispatched (prompt-injection, data-poisoning, model-theft)
- `"agent"` --> AG agents dispatched (agent-autonomy, tool-abuse)
- `"orchestrator"` --> AG agents dispatched (already included from "agent" match — no duplicate dispatch)

The component receives its STRIDE categories (based on DFD type) plus all 5 AI agents.

### Ambiguity Note

The keyword `"model"` is ambiguous — it could refer to a data model, a domain model, or an LLM. When `"model"` is matched, dispatch the LLM agents and include a note in the dispatch table: `"Keyword 'model' matched — may refer to data model rather than LLM. AI agents dispatched for coverage; review findings for relevance."` This ensures no AI-relevant component is missed while flagging potential false positives.

### Agent-to-Table Mapping

AI findings produced by the dispatched agents are grouped into 2 output tables:

| Output Table | Agents | Reference Standards |
|--------------|--------|---------------------|
| AG (Agentic Threats) | agent-autonomy, tool-abuse | OWASP Agentic Top 10, MCP Top 10 |
| LLM (LLM Threats) | prompt-injection, data-poisoning, model-theft | OWASP LLM Top 10 v2025 |

---

## Dispatch Table Format (Intermediate Output)

Before invoking any agents, produce a visible dispatch table as an intermediate artifact. This table shows every component, its STRIDE categories, its AI categories (if any), and the total number of agents that will be dispatched. The dispatch table enables validation that the normalization and keyword matching rules were applied correctly before agent execution begins.

Label this section clearly:

```
### Dispatch Table (Intermediate)
```

### Table Format

| Component | DFD Type | MAESTRO Layer | STRIDE Categories | AI Categories | Total Agents |
|-----------|----------|---------------|-------------------|---------------|--------------|

- **Component**: The component name from the Phase 1 inventory.
- **DFD Type**: The DFD element type (External Entity, Process, Data Store, or Data Flow).
- **MAESTRO Layer**: The CSA MAESTRO architectural layer classification assigned during Phase 1 (e.g., "L3 — Agent Framework"). Set to "Unclassified" if no layer keywords matched. See `.claude/skills/tachi-shared/references/maestro-layers-shared.md` for the layer taxonomy and classification algorithm.
- **STRIDE Categories**: Comma-separated list of applicable STRIDE categories based on DFD type (e.g., "S, R" for External Entity).
- **AI Categories**: Comma-separated list of applicable AI categories based on keyword matching (e.g., "LLM, AG" for dual-dispatch). Use "—" if no AI keywords matched.
- **Total Agents**: The total count of individual agents to be dispatched for this component. Count each STRIDE category as 1 agent and each AI agent individually (AG = 2 agents: agent-autonomy + tool-abuse; LLM = 3 agents: prompt-injection + data-poisoning + model-theft).

### Example Rows

| Component | DFD Type | MAESTRO Layer | STRIDE Categories | AI Categories | Total Agents |
|-----------|----------|---------------|-------------------|---------------|--------------|
| LLM Agent Orchestrator | Process | L3 — Agent Framework | S, T, R, I, D, E | LLM, AG | 11 |
| MCP Tool Server | Process | L3 — Agent Framework | S, T, R, I, D, E | AG | 8 |
| User | External Entity | L7 — Agent Ecosystem | S, R | — | 2 |
| Knowledge Base | Data Store | L2 — Data Operations | T, I, D | — | 3 |
| External API | External Entity | Unclassified | S, R | — | 2 |

In this example:
- "LLM Agent Orchestrator" is a Process (6 STRIDE agents) with dual-dispatch (3 LLM + 2 AG agents) = 11 total. Classified as L3 (Agent Framework) due to "orchestrator" keyword.
- "MCP Tool Server" is a Process (6 STRIDE agents) with AG dispatch (2 AG agents) = 8 total. Classified as L3 due to "MCP server" keyword.
- "User" is an External Entity (2 STRIDE agents) with no AI match = 2 total. Classified as L7 (Agent Ecosystem) due to the `user` keyword matching human-agent interaction scope.
- "Knowledge Base" is a Data Store (3 STRIDE agents) with no AI match = 3 total. Classified as L2 due to "knowledge base" keyword.
- "External API" is an External Entity with no matching MAESTRO keywords = Unclassified.

### Summary

After the dispatch table, include a summary with:

1. **Total unique agent invocations**: The sum of all Total Agents values across all components. Note that the same agent type may be invoked for multiple components — each component-agent pair counts as one invocation.
2. **Components with AI dispatch**: The count of components that have at least one AI category (LLM and/or AG).
3. **Components with dual-dispatch**: The count of components dispatched to both LLM and AG categories.

### Self-Check

After producing the dispatch table, verify:

- Every component from the Phase 1 inventory appears in the dispatch table.
- Every component has a MAESTRO Layer value (one of L1-L7 or "Unclassified"). No empty cells in the MAESTRO Layer column.
- Every component has at least 2 STRIDE categories (the minimum for any DFD element type — External Entity and Data Flow/Data Store each have at least 2-3 applicable categories).
- AI categories are present only for components whose names or descriptions matched the keyword rules.
- Total Agents count is arithmetically correct for each row.

If any self-check fails, correct the dispatch table before invoking agents. Do not proceed to agent invocation with an invalid dispatch table.

After the dispatch table is validated, invoke agents according to the selected dispatch mode (parallel or sequential) and proceed to Phase 3: Determine Countermeasures.

---

## Correlation Detection

Correlation detection runs after all findings have been collected and assembled into the STRIDE tables (Section 3) and AI tables (Section 4), but before Phase 4. Its purpose is to identify cross-category finding pairs that indicate a related underlying threat when they target the same component.

The 5 correlation rules below define which STRIDE-to-AI category pairings constitute a correlated threat. Matching is deterministic and rule-based — no semantic similarity or probabilistic scoring is involved. Each rule identifies a shared threat basis between one STRIDE category and one AI category.

---

### Correlation Rule Table

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

---

### Correlation Detection Algorithm

Execute the following steps to identify correlated findings:

1. Group all findings from the STRIDE tables (Section 3) and AI tables (Section 4) by their target component name. Each group contains every finding — regardless of category — that targets a single component.
2. Within each component group, identify all cross-category finding pairs. A cross-category pair consists of one finding from a STRIDE category and one finding from an AI category. Do not pair findings within the same domain (STRIDE-to-STRIDE or AI-to-AI).
3. For each cross-category pair, check whether the STRIDE category and AI category match any of the 5 rules in the Correlation Rule Table. Matching is by category only — the threat descriptions do not need to be semantically similar.
4. When a match is found, create a correlation group (CG-N). If the same component already has a correlation group from a different rule match, merge all matched findings into that existing group. The result is one correlation group per component, regardless of how many rules triggered.
5. Each finding may belong to at most one correlation group. If a finding matches multiple rules through the same component, it joins the single merged group for that component.
6. Findings that do not match any rule remain uncorrelated and are unaffected. They stay in their original STRIDE or AI tables with no modification.

---

### Correlation Group Assembly

After running the detection algorithm, assemble the resulting correlation groups:

1. Assign sequential IDs: CG-1, CG-2, CG-3, etc., numbered in the order the correlated components appear in the Phase 1 inventory. If the first component in the inventory with a correlation is "LLM Agent Orchestrator" and the second is "MCP Tool Server", their groups are CG-1 and CG-2 respectively.
2. For each group, set the risk level to the highest risk level among its member findings. Use the severity order: Critical > High > Medium > Low > Note. If a group contains one "High" finding and one "Medium" finding, the group risk level is "High".
3. For each group, build the threat summary by listing each member finding's perspective, prefixed by its category name. Format: "{Category}: {threat description}; {Category}: {threat description}". List STRIDE findings before AI findings. Within each domain, list findings in the order of their IDs.
4. Store the assembled correlation groups. They will be consumed by:
   - Section 4a (Correlated Findings table) — written immediately after this phase.
   - Phase 4 Coverage Matrix generation — for deduplicated cell counts.
   - Phase 4 Risk Summary computation — for deduplicated totals.

---

### Correlation Self-Check

Before proceeding, verify the assembled correlation groups:

1. Verify that no finding ID appears in more than one correlation group.
2. Verify that every finding ID referenced in a correlation group exists in either the STRIDE tables (Section 3) or the AI tables (Section 4).
3. Verify that each correlation group contains findings from at least 2 different agent categories (at minimum one STRIDE and one AI category).
4. Verify that the group risk level matches the highest risk level among its member findings using the severity order: Critical > High > Medium > Low > Note.
5. If any check fails, correct the correlation groups before proceeding.

After the self-check passes, assemble Section 4a of the output using the correlation groups. Section 4a uses the following table format:

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|

When zero correlation groups exist, output: "No cross-agent correlations detected." followed by the empty table header with no data rows. Do not omit Section 4a — it is always present in the output.

After Section 4a is assembled, proceed to Phase 3.5: Cross-Layer Correlation.

---

## Phase 3.5: Cross-Layer Attack Chain Correlation

Phase 3.5 runs after Phase 3 correlation detection (Section 4a) and before Phase 4 Assess. It analyzes findings across MAESTRO layers to identify cross-layer attack chains — sequences of related findings that cascade vertically through the MAESTRO layer stack.

### Placement

```
Phase 3: Determine Countermeasures
  ├── Collect findings from agents
  ├── Merge/deduplicate
  ├── Table assembly (Sections 3, 4)
  └── Correlation detection (Section 4a)
Phase 3.5: Cross-Layer Attack Chain Correlation    <-- NEW
  ├── Group findings by component + MAESTRO layer
  ├── Apply correlation signals
  ├── Assemble chains using transition lookup table
  ├── Generate attack-chains.md (conditional)
  └── Set has-attack-chains boolean
Phase 4: Assess
  ├── Coverage matrix
  ├── Risk summary
  └── SARIF output
```

### Input Contract

Phase 3.5 consumes:
1. **Phase 1 component inventory**: Component names, types, MAESTRO layer assignments
2. **Phase 1 data flow graph**: Source -> target component relationships
3. **Deduplicated findings IR**: From Phase 3, each finding has `component`, `maestro_layer`, `stride_category`, `severity`
4. **Correlation pattern lookup table**: Loaded from `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md`

Phase 3.5 does NOT consume:
- Section 4a output (independence invariant — cross-layer chains and intra-component correlation groups are independent grouping mechanisms)
- Raw agent output (operates on deduplicated findings IR only, bounding input size)

### Output Contract

Phase 3.5 produces:
1. **`attack-chains.md`**: Structured artifact with YAML frontmatter, chain summary table, and chain details sections (conditional — only produced when chains are detected)
2. **`has-attack-chains` boolean**: Consumed by Phase 5 (threat-report agent Section 6) and PDF pipeline (`extract-report-data.py`, `main.typ`)

### Independence Invariant

Phase 3.5 cross-layer chains and Phase 3 Section 4a intra-component correlation groups are independent grouping mechanisms:
- A finding may appear in both a Section 4a correlation group AND a Phase 3.5 attack chain without conflict
- Phase 3.5 does not read, modify, or depend on Section 4a output
- Section 4a does not read, modify, or depend on Phase 3.5 output
- Both contribute independently to the threat model's analytical value

### Correlation Signals

Phase 3.5 uses three correlation signals in priority order:

| Priority | Signal | Description | Sufficient Alone? |
|----------|--------|-------------|-------------------|
| 1 | Component lineage | Findings targeting components connected by data flows | Yes |
| 2 | Data flow dependency | Findings on components sharing data flow paths | Yes |
| 3 | Layer adjacency + structural | Adjacent MAESTRO layers with transition lookup table match | No — requires signal 1 or 2 |

Signal 3 (layer adjacency) refines the transition type using the lookup table in `attack-chain-patterns-shared.md` but is not sufficient alone. At least one structural signal (1 or 2) is required.

### Reference

- Schema: `schemas/attack-chain.yaml` (v1.0)
- Patterns: `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md`
- Layers: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`

After Phase 3.5 completes (or is skipped when no cross-layer chains exist), proceed to Phase 4: Assess.
