# Attack Tree: E-3 -- Administrative Tool Access via Parameter Manipulation

| Field | Value |
|-------|-------|
| Finding ID | E-3 |
| Component | MCP Tool Server |
| Risk Level | Critical |
| Threat | Administrative Tool Access via Parameter Manipulation |
| Correlation | None |

```mermaid
flowchart TD
    E3_root["Invoke admin tool endpoints by manipulating tool_name"]
    E3_or1{{"OR"}}
    E3_sub1["Direct parameter manipulation"]
    E3_sub2["Prompt injection to control tool selection"]
    E3_and1{{"AND"}}
    E3_leaf1["Enumerate available tools via Tool Server discovery"]
    E3_leaf2["Craft tool call with admin tool_name parameter"]
    E3_leaf3["Tool Server executes without RBAC validation"]
    E3_leaf4["Achieve prompt injection against Orchestrator"]
    E3_leaf5["Cause Orchestrator to request admin-level tool call"]

    E3_root --> E3_or1
    E3_or1 --> E3_sub1
    E3_or1 --> E3_sub2
    E3_sub1 --> E3_and1
    E3_and1 --> E3_leaf1
    E3_and1 --> E3_leaf2
    E3_and1 --> E3_leaf3
    E3_sub2 --> E3_leaf4
    E3_sub2 --> E3_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E3_root goal
    class E3_or1 orGate
    class E3_and1 andGate
    class E3_sub1,E3_sub2 subGoal
    class E3_leaf1,E3_leaf2,E3_leaf3,E3_leaf4,E3_leaf5 leaf
```
