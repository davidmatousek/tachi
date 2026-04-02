# Attack Tree Examples

Reference attack tree implementations demonstrating correct Mermaid syntax, node naming, gate logic, color styling, and decomposition depth. Use these as patterns when generating trees for actual findings.

---

## Example 1: Critical Finding -- Autonomous Execution Without Approval (AG-1 Pattern)

This example demonstrates a 3-level Critical finding tree with both AND and OR gates, based on an agentic threat pattern where an orchestrator executes consequential actions without human approval.

```mermaid
flowchart TD
    AG1_root["Execute unauthorized consequential actions via orchestrator"]
    AG1_or1{{"OR"}}
    AG1_sub1["Exploit missing risk-tier classification"]
    AG1_sub2["Bypass human-in-the-loop checkpoint"]
    AG1_and1{{"AND"}}
    AG1_leaf1["Identify high-stakes tool operation exposed by orchestrator"]
    AG1_leaf2["Craft prompt triggering multi-step tool chain"]
    AG1_leaf3["Confirm no approval gate distinguishes read vs write operations"]
    AG1_and2{{"AND"}}
    AG1_leaf4["Discover checkpoint trigger conditions via probing"]
    AG1_leaf5["Construct prompt that routes below checkpoint threshold"]
    AG1_leaf6["Execute irreversible external action without approval"]

    AG1_root --> AG1_or1
    AG1_or1 --> AG1_sub1
    AG1_or1 --> AG1_sub2
    AG1_sub1 --> AG1_and1
    AG1_and1 --> AG1_leaf1
    AG1_and1 --> AG1_leaf2
    AG1_and1 --> AG1_leaf3
    AG1_sub2 --> AG1_and2
    AG1_and2 --> AG1_leaf4
    AG1_and2 --> AG1_leaf5
    AG1_and2 --> AG1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG1_root goal
    class AG1_or1 orGate
    class AG1_and1,AG1_and2 andGate
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333

    class AG1_sub1,AG1_sub2 subGoal
    class AG1_leaf1,AG1_leaf2,AG1_leaf3,AG1_leaf4,AG1_leaf5,AG1_leaf6 leaf
```

### What This Example Demonstrates

- **3 levels of decomposition** (root -> sub-goals -> leaf actions) meeting Critical minimum depth
- **OR gate** at level 2: attacker can exploit missing classification OR bypass checkpoints
- **AND gates** at level 3: each sub-goal requires multiple coordinated actions
- **Node ID convention**: `AG1_root`, `AG1_or1`, `AG1_sub1`, `AG1_and1`, `AG1_leaf1`, etc.
- **Quoted labels**: All labels use `["..."]` syntax
- **classDef/class styling**: Four color classes applied to all nodes
- **12 total nodes**: Well within the ~20 node readability limit
- **Realistic leaf actions**: Each leaf requires specific skill or access (probing, prompt crafting, identifying exposed operations)

---

## Example 2: High Finding -- Indirect Prompt Injection via RAG (LLM-2 Pattern)

This example demonstrates a 2-level High finding tree with an OR gate, based on an LLM threat pattern where adversarial content in retrieved documents hijacks the orchestrator.

```mermaid
flowchart TD
    LLM2_root["Hijack orchestrator behavior via poisoned RAG documents"]
    LLM2_or1{{"OR"}}
    LLM2_sub1["Inject adversarial instructions into knowledge base"]
    LLM2_sub2["Exploit existing document with embedded instructions"]
    LLM2_and1{{"AND"}}
    LLM2_leaf1["Obtain document upload access to knowledge base"]
    LLM2_leaf2["Craft document with adversarial instructions that override system prompt"]
    LLM2_leaf3["Ensure document ranks highly for target query embeddings"]
    LLM2_leaf4["Identify existing document containing instruction-like content"]
    LLM2_leaf5["Craft user query that triggers retrieval of the exploitable document"]

    LLM2_root --> LLM2_or1
    LLM2_or1 --> LLM2_sub1
    LLM2_or1 --> LLM2_sub2
    LLM2_sub1 --> LLM2_and1
    LLM2_and1 --> LLM2_leaf1
    LLM2_and1 --> LLM2_leaf2
    LLM2_and1 --> LLM2_leaf3
    LLM2_sub2 --> LLM2_leaf4
    LLM2_sub2 --> LLM2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM2_root goal
    class LLM2_or1 orGate
    class LLM2_and1 andGate
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333

    class LLM2_sub1,LLM2_sub2 subGoal
    class LLM2_leaf1,LLM2_leaf2,LLM2_leaf3,LLM2_leaf4,LLM2_leaf5 leaf
```

### What This Example Demonstrates

- **2+ levels of decomposition** meeting High minimum depth (root -> sub-goals -> leaf actions)
- **Asymmetric tree**: Left branch (inject) uses AND gate with 3 leaves; right branch (exploit existing) has 2 direct leaves
- **OR gate**: Attacker can inject new malicious documents OR exploit existing ones
- **AND gate**: Injection path requires upload access AND adversarial crafting AND embedding ranking
- **Node ID convention**: `LLM2_root`, `LLM2_or1`, `LLM2_sub1`, `LLM2_leaf1`, etc.
- **10 total nodes**: Compact tree appropriate for High severity
- **Realistic leaf actions**: Each leaf represents a distinct attacker capability (credential access, adversarial prompt engineering, embedding manipulation, query crafting)
