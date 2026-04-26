# Attack Tree: D-5 — MCP Tool Server Connection Pool Exhausted via High-Volume Tool Requests

**Finding ID**: D-5
**Risk Level**: Critical
**Component**: MCP Tool Server
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    D5_root["Exhaust MCP Tool Server connection pool to deny all tool call availability"]
    D5_or1{{"OR"}}
    D5_sub1["Flood Tool Server with high-rate tool call requests from compromised agent"]
    D5_sub2["Trigger runaway tool invocation from injected LLM context"]
    D5_and1{{"AND"}}
    D5_leaf1["Compromise Orchestrator or Specialist Agent to issue tool calls at maximum rate"]
    D5_leaf2["Confirm Tool Server lacks per-caller rate limiting or connection pool overflow rejection"]
    D5_leaf3["Saturate connection pool causing all legitimate tool calls to fail"]
    D5_and2{{"AND"}}
    D5_leaf4["Inject adversarial content into Orchestrator context causing autonomous tool call loop"]
    D5_leaf5["Confirm no circuit breaker halts runaway tool invocation sequences"]
    D5_leaf6["Tool call flood exhausts API provider rate limits and connection pool simultaneously"]

    D5_root --> D5_or1
    D5_or1 --> D5_sub1
    D5_or1 --> D5_sub2
    D5_sub1 --> D5_and1
    D5_and1 --> D5_leaf1
    D5_and1 --> D5_leaf2
    D5_and1 --> D5_leaf3
    D5_sub2 --> D5_and2
    D5_and2 --> D5_leaf4
    D5_and2 --> D5_leaf5
    D5_and2 --> D5_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D5_root goal
    class D5_or1 orGate
    class D5_and1,D5_and2 andGate
    class D5_sub1,D5_sub2 subGoal
    class D5_leaf1,D5_leaf2,D5_leaf3,D5_leaf4,D5_leaf5,D5_leaf6 leaf
```
