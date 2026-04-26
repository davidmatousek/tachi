# Attack Tree: OI-2 — Server-Side Code Execution via LLM-Synthesized Tool Call Request Parameters

**Finding ID**: OI-2
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    OI2_root["Achieve server-side code or query execution via LLM-synthesized parameters in Tool Call Request to MCP Tool Server"]
    OI2_or1{{"OR"}}
    OI2_sub1["Inject SQL payload via LLM output embedded in Tool Call Request database parameter"]
    OI2_sub2["Inject OS command via LLM output embedded in Tool Call Request command parameter"]
    OI2_and1{{"AND"}}
    OI2_leaf1["Prime Orchestrator via adversarial prompt to emit SQL injection fragment in tool parameter"]
    OI2_leaf2["Confirm MCP Tool Server constructs SQL by string interpolation of LLM-supplied value"]
    OI2_leaf3["SQL injection executes on database with Tool Server service account credentials"]
    OI2_and2{{"AND"}}
    OI2_leaf4["Prime Orchestrator to emit shell metacharacter sequence in command tool argument"]
    OI2_leaf5["Confirm MCP Tool Server executes command via shell invocation not argument vector"]
    OI2_leaf6["OS command executes on Tool Server host with service account privileges and external API access"]

    OI2_root --> OI2_or1
    OI2_or1 --> OI2_sub1
    OI2_or1 --> OI2_sub2
    OI2_sub1 --> OI2_and1
    OI2_and1 --> OI2_leaf1
    OI2_and1 --> OI2_leaf2
    OI2_and1 --> OI2_leaf3
    OI2_sub2 --> OI2_and2
    OI2_and2 --> OI2_leaf4
    OI2_and2 --> OI2_leaf5
    OI2_and2 --> OI2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI2_root goal
    class OI2_or1 orGate
    class OI2_and1,OI2_and2 andGate
    class OI2_sub1,OI2_sub2 subGoal
    class OI2_leaf1,OI2_leaf2,OI2_leaf3,OI2_leaf4,OI2_leaf5,OI2_leaf6 leaf
```
