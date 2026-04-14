# Attack Tree Construction

Rules for building Mermaid attack trees in the tachi threat report. Covers tree structure, minimum depth requirements, decomposition stopping rules, Mermaid syntax conventions, color styling, and validation checklist.

---

## Tree Structure

Each attack tree has three node types arranged in a root-to-leaf hierarchy:

1. **Root Node (Goal)**: The attacker's ultimate objective, derived from the finding's `threat` field. There is exactly one root node per tree. Frame as an attacker goal statement (e.g., "Exfiltrate sensitive data via prompt injection").

2. **Intermediate Nodes (Sub-Goals)**: Decomposed steps the attacker must achieve to reach the root goal. Each intermediate node connects to its children through an explicit **AND gate** or **OR gate** node:
   - **AND gate**: All child sub-goals must be achieved (conjunctive decomposition)
   - **OR gate**: Any one child sub-goal is sufficient (disjunctive decomposition)

3. **Leaf Nodes (Atomic Actions)**: Concrete, indivisible attack actions at the bottom of the tree. Each leaf represents a specific action requiring identifiable resources -- skill, access level, tools, or time.

---

## Minimum Depth Requirements

| Finding Severity | Minimum Tree Depth | Rationale |
|-----------------|-------------------|-----------|
| Critical | 3 levels (root -> intermediate -> leaf) | Critical findings demand deeper decomposition to expose multi-step attack paths |
| High | 2 levels (root -> leaf, or root -> intermediate -> leaf) | High findings require at least one level of decomposition beyond the goal |

**Depth counting**: Root = level 1. Each edge traversal adds one level. Gate nodes (AND/OR) do NOT count as a separate level -- they are structural connectors between parent and children at the same decomposition tier.

---

## Decomposition Stopping Rule

Stop decomposing when leaf nodes represent **concrete actions requiring specific resources**:
- **Skill**: Specific technical expertise (e.g., "craft adversarial prompt bypassing input classifier")
- **Access**: Specific access level (e.g., "obtain document upload credentials")
- **Tools**: Specific tooling (e.g., "use DNS spoofing tool to redirect API calls")
- **Time**: Specific time investment (e.g., "systematically query API over extended period")

Do NOT decompose to implementation-level detail such as specific CVE exploit code, packet formats, or byte-level manipulation. The goal is to communicate attack paths to stakeholders, not to provide an exploit cookbook.

### Asymmetry and Realism

- Trees are naturally asymmetric -- different attack paths have different depths
- OR branches may have varying numbers of children
- Not every branch needs the same depth; decompose proportionally to complexity
- Prefer realistic attack paths over exhaustive enumeration

---

## Mermaid Syntax Conventions

All attack trees use Mermaid `flowchart TD` syntax. Follow these conventions exactly to ensure consistent rendering across GitHub Markdown preview, Mermaid Live Editor, and documentation tools.

### Orientation

Always use `flowchart TD` (top-down). The root goal appears at the top; leaf actions appear at the bottom. This matches the natural reading direction for attack tree decomposition.

### Node ID Format

All node IDs follow the pattern: `{FindingID}_{type}{N}`

| Component | Format | Examples |
|-----------|--------|----------|
| FindingID | Category + number, no hyphen | `AG1`, `S1`, `LLM1` |
| type | Node type abbreviation | `root`, `and`, `or`, `sub`, `leaf` |
| N | Sequential counter per type | `1`, `2`, `3` |

**Examples**: `AG1_root`, `AG1_or1`, `AG1_sub1`, `AG1_leaf1`, `AG1_and1`, `LLM1_root`, `S1_leaf2`

**Rules**:
- Node IDs must start with a letter (alphanumeric prefix)
- No hyphens in node IDs -- use the finding ID without its hyphen (AG-1 -> `AG1`)
- Never use bare reserved words as node IDs: `end`, `default`, `graph`, `subgraph`, `click`, `style`, `linkStyle`
- Never start a node ID with `o` or `x` immediately after an edge operator (`-->`, `---`)

### Node Shapes and Labels

| Node Type | Shape Syntax | Label Format |
|-----------|-------------|--------------|
| Root (Goal) | `["Label"]` -- rectangle | `AG1_root["Attacker's ultimate goal"]` |
| AND Gate | `{{"AND"}}` -- diamond/rhombus | `AG1_and1{{"AND"}}` |
| OR Gate | `{{"OR"}}` -- diamond/rhombus | `AG1_or1{{"OR"}}` |
| Sub-Goal | `["Label"]` -- rectangle | `AG1_sub1["Intermediate sub-goal"]` |
| Leaf (Action) | `["Label"]` -- rectangle | `AG1_leaf1["Concrete atomic action"]` |

**Label quoting rules**:
- Always quote ALL labels using `["..."]` syntax
- This prevents parsing errors from special characters (parentheses, colons, semicolons, quotes)
- Gate nodes are the exception -- they use `{{"AND"}}` or `{{"OR"}}` without square brackets

### Edge Syntax

Use `-->` for all edges (solid arrow). No edge labels unless needed for disambiguation.

```
AG1_root --> AG1_or1
AG1_or1 --> AG1_sub1
AG1_or1 --> AG1_sub2
AG1_sub1 --> AG1_and1
AG1_and1 --> AG1_leaf1
AG1_and1 --> AG1_leaf2
```

### Color Styling

Define styles using `classDef` at the end of the diagram. Apply to nodes using `class` declarations.

```
classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

class AG1_root goal
class AG1_and1 andGate
class AG1_or1 orGate
class AG1_sub1 subGoal
class AG1_leaf1,AG1_leaf2,AG1_leaf3 leaf
```

| Style Name | Color | Hex | Applied To |
|-----------|-------|-----|-----------|
| goal | Red | `#ff6b6b` | Root goal nodes |
| andGate | Orange | `#ffa500` | AND gate nodes |
| orGate | Teal | `#4ecdc4` | OR gate nodes |
| subGoal | Light gray | `#d5dbdb` | Intermediate sub-goal nodes |
| leaf | Green | `#95e1d3` | Leaf action nodes |

### Tree Size Limit

Target a maximum of approximately **20 nodes** per tree for readability. If a tree naturally exceeds 20 nodes, consider:
- Consolidating similar leaf actions under a shared sub-goal
- Reducing decomposition depth on lower-risk branches
- Splitting into sub-trees with cross-references (for exceptionally complex Critical findings)

---

## Standalone File Naming

Each attack tree is saved as a standalone file in the `attack-trees/` directory. The filename MUST follow this convention exactly:

- **Pattern**: `{finding-id}-attack-tree.md`
- **Case**: The finding ID MUST be **lowercased** in the filename
- **Suffix**: Always `-attack-tree.md` — never use a description slug or other suffix
- **Examples**: Finding `AG-1` → filename `ag-1-attack-tree.md`, Finding `LLM-2` → filename `llm-2-attack-tree.md`, Finding `S-1` → filename `s-1-attack-tree.md`
- **Wrong examples**: `AG-1-attack-tree.md` (uppercase), `ag-1-no-hitl-stdio.md` (description slug), `AG-1-no-hitl-stdio.md` (both wrong)

To produce the filename: take the finding ID (e.g., `AG-1`), convert to lowercase (e.g., `ag-1`), append `-attack-tree.md`.

---

## Validation Checklist

Before including any Mermaid attack tree in the report or standalone file, run every check below. A tree that fails any check must be corrected before output.

### Syntax Safety

- [ ] Diagram starts with `flowchart TD` on its own line
- [ ] No bare reserved words used as node IDs: `end`, `default`, `graph`, `subgraph`, `click`, `style`, `linkStyle`, `classDef`, `class`
- [ ] No node ID starts with `o` or `x` immediately after an edge operator (`-->`)
- [ ] All node IDs are alphanumeric with underscores only -- no hyphens, spaces, or special characters
- [ ] All node IDs start with a letter (not a number)
- [ ] All text labels are quoted using `["..."]` syntax (except AND/OR gate labels)
- [ ] Special characters in labels (parentheses, colons, semicolons, single quotes, double quotes) are enclosed within `["..."]` quoting
- [ ] No unescaped `"` inside quoted labels -- rephrase to avoid nested quotes

### Structural Integrity

- [ ] Exactly one root node per tree
- [ ] No orphan nodes (every node is connected by at least one edge)
- [ ] No loops or cycles -- the tree is a directed acyclic graph (DAG)
- [ ] Every AND/OR gate node has at least 2 child edges
- [ ] Every path from root to leaf passes through at least one gate node (for trees with depth >= 3)
- [ ] Tree depth meets minimum requirement: 3 levels for Critical, 2 levels for High

### Naming Convention

- [ ] All node IDs follow `{FindingID}_{type}{N}` format
- [ ] FindingID portion matches the source finding ID without hyphen (e.g., AG-1 -> `AG1`)
- [ ] Node type abbreviations are one of: `root`, `and`, `or`, `sub`, `leaf`
- [ ] Sequential counters are consistent (no gaps in numbering within a type)

### Styling

- [ ] `classDef` declarations present for: `goal`, `andGate`, `orGate`, `subGoal`, `leaf`
- [ ] `class` assignments applied to every node in the tree
- [ ] Root node assigned `goal` class
- [ ] AND gate nodes assigned `andGate` class
- [ ] OR gate nodes assigned `orGate` class
- [ ] Leaf nodes assigned `leaf` class
- [ ] Color values match the standard palette: goal=`#ff6b6b`, andGate=`#ffa500`, orGate=`#4ecdc4`, leaf=`#95e1d3`

### Standalone File Naming

- [ ] Filename is the finding ID lowercased plus `-attack-tree.md` (e.g., AG-1 → `ag-1-attack-tree.md`)
- [ ] No uppercase letters in filename
- [ ] No description slugs — suffix is always `-attack-tree.md`

### Readability

- [ ] Total node count does not exceed ~20 nodes
- [ ] Labels are concise but descriptive (aim for 3-10 words per label)
- [ ] Gate purpose is clear from surrounding context
- [ ] Tree layout does not create excessive width (prefer depth over breadth where possible)

---

## Baseline Reconciliation

When a baseline exists and the architecture has changed (Rule 2 applies), fresh attack trees are generated for ALL Critical/High findings, then this structural similarity algorithm is applied to each UNCHANGED finding to decide whether to carry forward the baseline version or keep the fresh version.

**Purpose**: Rule 3 reconciliation preserves consistency. If an UNCHANGED finding's attack tree is substantively the same as the baseline despite minor LLM wording variation, the baseline version is preserved. This prevents cosmetic churn while still detecting meaningful structural changes.

### Named Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `LEAF_MATCH_THRESHOLD` | 0.70 | Minimum token-level Jaccard similarity for a leaf label pair to count as a match |
| `TREE_SIMILARITY_THRESHOLD` | 0.80 | Minimum proportion of matched leaf pairs for overall tree similarity |
| `NODE_COUNT_VARIANCE` | 0.20 | Maximum allowed proportional difference in total node count |

### Algorithm Steps

For each UNCHANGED finding that has both a fresh tree and a baseline tree:

**Step 1 — Parse Mermaid Trees**: Parse both `flowchart TD` diagrams. Extract total node count (all nodes matching the `{FindingID}_{type}{N}` pattern), total edge count (`-->` connections), and an ordered gate-type list (scan node IDs for `_or` and `_and` prefixes, record in the order they appear).

**Step 2 — Extract Leaf Labels**: Identify leaf nodes by the `_leaf` prefix in their node ID (e.g., `AG1_leaf1`, `AG1_leaf2`). Extract the text label from each leaf's `["..."]` quoted content.

**Step 3 — Tokenize Labels**: For each leaf label:
1. Convert to lowercase
2. Strip all punctuation (periods, commas, colons, semicolons, parentheses, single and double quotes)
3. Split on whitespace into tokens
4. Treat hyphenated words as single tokens (e.g., `"high-stakes"` → one token `high-stakes`)
5. No stop-word removal — retain every token

**Step 4 — Per-Label Jaccard Similarity**: For each pair of leaf labels (one baseline, one fresh), compute:

```
jaccard(A, B) = |tokens(A) ∩ tokens(B)| / |tokens(A) ∪ tokens(B)|
```

A pair **matches** if `jaccard >= LEAF_MATCH_THRESHOLD` (0.70). Use greedy best-match pairing: for each baseline leaf, select the fresh leaf with the highest Jaccard score that has not yet been paired. Each leaf may be matched at most once.

**Step 5 — Tree-Level Similarity**:

```
tree_similarity = matched_pairs / max(baseline_leaf_count, fresh_leaf_count)
```

**Step 6 — Gate-Type Comparison**: Compare the ordered gate-type lists from both trees. If the lists differ in length or at any position, treat the trees as **materially different** regardless of leaf similarity. This guard catches semantic changes like OR→AND conversions where leaf labels may still overlap.

**Step 7 — Node Count Guard**:

```
node_variance = |baseline_nodes - fresh_nodes| / max(baseline_nodes, fresh_nodes)
```

If `node_variance > NODE_COUNT_VARIANCE` (0.20), treat the trees as **materially different**.

**Step 8 — Decision**: Carry forward the baseline version if ALL three conditions hold:
- `tree_similarity >= 0.80` (Step 5)
- Gate types identical (Step 6)
- `node_variance <= 0.20` (Step 7)

Otherwise, keep the fresh version and record the action as `regenerated` in the manifest.

### Worked Example

#### Example A: Structurally Similar → Carry Forward Baseline

Baseline S-1 tree has 16 nodes (1 root, 1 AND gate, 2 OR gates, 12 leaves). Fresh S-1 tree has 17 nodes (1 root, 1 AND gate, 2 OR gates, 13 leaves). Three representative leaf comparisons:

| Baseline Leaf | Fresh Leaf | Intersection / Union | Jaccard |
|---|---|---|---|
| `"Exploit weak session token generation"` | `"Exploit weak session token generation mechanism"` | 5 / 6 | 0.83 ✓ |
| `"Forge credentials using leaked API keys"` | `"Forge credentials using leaked API key material"` | 5 / 7 | 0.71 ✓ |
| `"Hijack active session via cookie theft"` | `"Hijack active session via cookie theft"` | 6 / 6 | 1.00 ✓ |

Aggregate across all leaves: 12 of 13 fresh leaves find a baseline match at Jaccard ≥ 0.70.

- **Tree similarity**: `12 / max(12, 13) = 12/13 = 0.92` ≥ 0.80 ✓
- **Gate types**: `[AND, OR, OR]` == `[AND, OR, OR]` ✓
- **Node variance**: `|16 - 17| / 17 = 0.06` ≤ 0.20 ✓

**Decision**: All three conditions met → **carry forward baseline version**. Manifest action: `carried_forward`.

#### Example B: Materially Different → Use Fresh

Baseline AG-2 tree has 10 nodes (1 root, 2 OR gates, 1 sub-goal, 6 leaves). Fresh AG-2 tree has 12 nodes (1 root, 1 OR gate, 1 AND gate, 2 sub-goals, 7 leaves). Three representative leaf comparisons:

| Baseline Leaf | Fresh Leaf | Intersection / Union | Jaccard |
|---|---|---|---|
| `"Intercept tool call parameters"` | `"Intercept and modify tool call parameters"` | 4 / 6 | 0.67 ✗ |
| `"Exploit unvalidated plugin inputs"` | `"Leverage unvalidated agent plugin configuration"` | 2 / 6 | 0.33 ✗ |
| `"Abuse elevated runtime permissions"` | `"Abuse elevated runtime permissions"` | 4 / 4 | 1.00 ✓ |

Aggregate: 4 of 7 fresh leaves match a baseline leaf at Jaccard ≥ 0.70.

- **Tree similarity**: `4 / max(6, 7) = 4/7 ≈ 0.57` < 0.80 ✗
- **Gate types**: `[OR, OR]` ≠ `[OR, AND]` ✗ (OR→AND gate change)
- **Node variance**: `|10 - 12| / 12 ≈ 0.17` ≤ 0.20 ✓

**Decision**: Both leaf similarity and gate-type checks fail → **use fresh version**. Manifest action: `regenerated`. Any one failed check is sufficient to reject the baseline; here two fail independently.
