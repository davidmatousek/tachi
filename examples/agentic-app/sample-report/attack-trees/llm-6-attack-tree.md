# Attack Tree: LLM-6 — Server-Side Code Execution via LLM-Synthesized Tool Call Parameters

**Finding ID**: LLM-6
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM6_root["Achieve server-side code execution via LLM-synthesized injection payload in tool call parameters"]
    LLM6_or1{{"OR"}}
    LLM6_sub1["Inject SQL payload via LLM-synthesized database tool parameter"]
    LLM6_sub2["Inject shell metacharacters via LLM-synthesized command tool parameter"]
    LLM6_and1{{"AND"}}
    LLM6_leaf1["Craft user prompt causing Orchestrator to emit SQL injection in tool parameter"]
    LLM6_leaf2["Confirm Tool Server constructs SQL query by string interpolation of LLM-supplied value"]
    LLM6_leaf3["Execute arbitrary SQL against database via injection point in tool call"]
    LLM6_and2{{"AND"}}
    LLM6_leaf4["Craft user prompt causing Orchestrator to emit shell metacharacters in command tool argument"]
    LLM6_leaf5["Confirm Tool Server passes argument to shell via string concatenation not argument vector"]
    LLM6_leaf6["Execute arbitrary OS command on Tool Server host with service account privileges"]

    LLM6_root --> LLM6_or1
    LLM6_or1 --> LLM6_sub1
    LLM6_or1 --> LLM6_sub2
    LLM6_sub1 --> LLM6_and1
    LLM6_and1 --> LLM6_leaf1
    LLM6_and1 --> LLM6_leaf2
    LLM6_and1 --> LLM6_leaf3
    LLM6_sub2 --> LLM6_and2
    LLM6_and2 --> LLM6_leaf4
    LLM6_and2 --> LLM6_leaf5
    LLM6_and2 --> LLM6_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM6_root goal
    class LLM6_or1 orGate
    class LLM6_and1,LLM6_and2 andGate
    class LLM6_sub1,LLM6_sub2 subGoal
    class LLM6_leaf1,LLM6_leaf2,LLM6_leaf3,LLM6_leaf4,LLM6_leaf5,LLM6_leaf6 leaf
```
