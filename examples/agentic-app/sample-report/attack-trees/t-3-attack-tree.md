# Attack Tree: T-3 -- JSON-RPC Parameter Injection

| Field | Value |
|-------|-------|
| Finding ID | T-3 |
| Component | MCP Tool Server |
| Risk Level | Critical |
| Threat | JSON-RPC Parameter Injection |
| Correlation | None |

```mermaid
flowchart TD
    T3_root["Inject malicious payloads into tool call parameters"]
    T3_or1{{"OR"}}
    T3_sub1["Tamper with parameters in transit"]
    T3_sub2["Manipulate Orchestrator to generate malicious parameters"]
    T3_and1{{"AND"}}
    T3_leaf1["Intercept JSON-RPC message on network"]
    T3_leaf2["Inject SQL or shell command fragments into parameters"]
    T3_leaf3["Tool Server executes without schema validation"]
    T3_and2{{"AND"}}
    T3_leaf4["Achieve prompt injection against Orchestrator"]
    T3_leaf5["Cause Orchestrator to produce tool calls with injected parameters"]
    T3_leaf6["Tool Server trusts Orchestrator-sourced parameters"]

    T3_root --> T3_or1
    T3_or1 --> T3_sub1
    T3_or1 --> T3_sub2
    T3_sub1 --> T3_and1
    T3_and1 --> T3_leaf1
    T3_and1 --> T3_leaf2
    T3_and1 --> T3_leaf3
    T3_sub2 --> T3_and2
    T3_and2 --> T3_leaf4
    T3_and2 --> T3_leaf5
    T3_and2 --> T3_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T3_root goal
    class T3_or1 orGate
    class T3_and1,T3_and2 andGate
    class T3_sub1,T3_sub2 subGoal
    class T3_leaf1,T3_leaf2,T3_leaf3,T3_leaf4,T3_leaf5,T3_leaf6 leaf
```
