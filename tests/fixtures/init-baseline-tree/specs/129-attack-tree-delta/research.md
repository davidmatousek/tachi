# Research Summary: Attack Tree Delta Sub-Agent (Issue #129)

## Knowledge Base Findings

- No prior KB entries for sub-agent extraction patterns or attack tree reconciliation
- Feature 074 (Baseline-Aware Pipeline) established the delta_status enum (NEW, UNCHANGED, UPDATED, RESOLVED) and delta_counts frontmatter — the inputs this sub-agent consumes
- Feature 082 (Threat Agent Skill References) established the lean-agent detection variant pattern — single `**MANDATORY**: Read` directive at workflow start
- Feature 112 (Attack Path Pages) established the `attack-trees/` directory structure and standalone file naming convention (`{finding-id}-attack-tree.md`, lowercase)
- Feature 130 (mmdc Hard Prerequisite) established that mmdc validation is a downstream concern (report-assembler), not an agent concern

## Codebase Analysis

### Current Threat-Report Agent State
- **File**: `.claude/agents/tachi/threat-report.md` (337 lines)
- **Exceeds Report tier hard cap** (300 lines per `_TACHI_AGENT_BEST_PRACTICES.md`); extraction is also a compliance fix
- **Section 5 Delta Rules**: Lines 218-229 (Rules 1-3)
- **Dual Output Location**: Lines 302-330 (inline Section 5 + standalone files)
- **Rule 3 reconciliation**: "structurally similar" has no concrete algorithm — subjective judgment

### Sub-Agent Patterns
- **No existing pipeline-to-pipeline sub-agent spawning** in tachi — this would be the first
- **ADR-010**: File-based offloading, max 10 lines / ~200 tokens per return
- **Orchestrator dispatch**: Dispatches to 11 threat agents via Agent tool, merges inline returns

### Attack Tree Reference Files
- `attack-tree-construction.md` (200 lines): Covers syntax, structure, validation. **Zero reconciliation guidance**.
- `attack-tree-examples.md` (115 lines): Two fresh-generation examples (AG-1 3-level, LLM-2 2-level). **No reconciliation examples**.
- `narrative-templates.md`: Not referenced for Section 5 delta handling.

### Example Attack Trees (mermaid-agentic-app)
- 12 files in `attack-trees/`: ag-1/2/3, d-1, e-1, i-1/2, llm-1/2/3, s-1, t-2
- **Node ID format**: `{FindingID}_{type}{N}` (e.g., `AG1_root`, `AG1_leaf1`)
- **Leaf identification**: Nodes with `_leaf` prefix in ID
- **Gate types**: `_or` and `_and` prefixes for OR/AND gates
- **Styling**: `classDef` with 5 classes (goal, andGate, orGate, subGoal, leaf)

### Schema Conflicts
| Location | `attack_tree_count` Definition |
|----------|-------------------------------|
| `schemas/report.yaml` (line 52) | "one per Critical/High finding" (implies all) |
| `templates/output-schemas/threat-report.md` (line 50) | "NEW or UPDATED only, UNCHANGED excluded" |
| Observed output | Baseline 21, new run 16, files written 22 (all three differ) |

## Architecture Constraints

### Relevant ADRs
- **ADR-010** (Minimal-Return Architecture): File-based offloading, max 10-line return. Principle reusable for manifest pattern.
- **ADR-018** (Baseline-Aware Pipeline): SHA-256 fingerprinting for correlation. No anchoring bias — fresh discovery independent of baseline.
- **ADR-021** (Determinism): SOURCE_DATE_EPOCH for reproducible output. Same inputs must produce same outputs.
- **ADR-023** (Lean Agent Patterns): Detection variant (single-pass, single-point load). Not directly applicable to utility agent but informs shape.

### Agent Tier Caps
- **Leaf tier**: 100-150 lines (hard cap 200) — target for attack-tree-delta
- **Report tier**: 200-250 lines (hard cap 300) — threat-report currently at 337 (over cap)
- **Skill extraction pattern**: Domain content in `.claude/skills/tachi-{name}/references/`, lazy load via `**MANDATORY**: Read`

### Constitution Constraints
- **Principle III** (Backward Compatibility): 100% backward compatible with existing outputs
- **Principle VI** (Testing Excellence): 80% unit test minimum, test-first development
- **Principle VII** (Definition of Done): Three-step validation mandatory

## Industry Research

- Sub-agent delegation is a standard pattern in multi-agent orchestration (Microsoft AutoGen, LangGraph)
- Attack tree comparison in formal methods uses graph isomorphism — overkill for Mermaid flowcharts
- Leaf-label overlap with node-count guard is a pragmatic approximation suitable for LLM-generated trees
- Jaccard similarity on token-level word overlap is standard for fuzzy string matching (architect recommendation)

## Recommendations for Spec

- Define the sub-agent as **Leaf tier** (cap 200 lines) with detection variant shape
- Structural similarity algorithm must be deterministic and LLM-executable (no Python code)
- Use **token-level Jaccard similarity** per leaf label pair (architect C-1 recommendation)
- Add **gate-type comparison step** to detect AND/OR gate changes (architect C-2 recommendation)
- Frame `attack_tree_count` change as **deliberate reversal** of Feature 104 decision (architect C-4)
- Sub-agent writes standalone files only; threat-report handles inline Section 5 assembly
- mmdc validation is NOT the sub-agent's concern (Mermaid source only, not rendered PNGs)
- Include worked example of the similarity algorithm applied to a concrete tree pair
