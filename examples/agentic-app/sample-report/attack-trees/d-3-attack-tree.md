# Attack Tree: D-3 -- Tool Server Concurrent Execution Exhaustion

| Field | Value |
|-------|-------|
| Finding ID | D-3 |
| Component | MCP Tool Server |
| Risk Level | High |
| Threat | Tool Server Concurrent Execution Exhaustion |
| Correlation | CG-4 (See also: AG-4) |

```mermaid
flowchart TD
    D3_root["Exhaust Tool Server resources via concurrent tool calls"]
    D3_and1{{"AND"}}
    D3_leaf1["Submit requests triggering multiple parallel tool calls"]
    D3_leaf2["Each tool call creates connections to External API"]
    D3_leaf3["Connection pool and memory exhausted without concurrency cap"]

    D3_root --> D3_and1
    D3_and1 --> D3_leaf1
    D3_and1 --> D3_leaf2
    D3_and1 --> D3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D3_root goal
    class D3_and1 andGate
    class D3_leaf1,D3_leaf2,D3_leaf3 leaf
```
