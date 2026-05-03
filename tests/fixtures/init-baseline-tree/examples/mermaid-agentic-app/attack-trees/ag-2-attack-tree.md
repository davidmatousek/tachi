# Attack Tree: AG-2 — Unrestricted tool access without per-session capability scoping

| Field | Value |
|-------|-------|
| Finding ID | AG-2 |
| Component | MCP Tool Server |
| Risk Level | Critical |
| Threat | Unrestricted tool access without per-session capability scoping |
| Correlation | None |

```mermaid
flowchart TD
    AG2_root["Invoke unauthorized tools via unrestricted MCP access"]
    AG2_or1{{"OR"}}
    AG2_sub1["Exploit lack of session-scoped tool allowlists"]
    AG2_sub2["Leverage prompt injection to access tools"]
    AG2_and1{{"AND"}}
    AG2_leaf1["Authenticate as a low-privilege user"]
    AG2_leaf2["Enumerate available tools via orchestrator probing"]
    AG2_leaf3["Invoke high-privilege tool directly through crafted request"]
    AG2_and2{{"AND"}}
    AG2_leaf4["Inject prompt that overrides orchestrator instructions"]
    AG2_leaf5["Direct orchestrator to invoke restricted tool"]
    AG2_leaf6["Extract results from tool invocation via response"]

    AG2_root --> AG2_or1
    AG2_or1 --> AG2_sub1
    AG2_or1 --> AG2_sub2
    AG2_sub1 --> AG2_and1
    AG2_and1 --> AG2_leaf1
    AG2_and1 --> AG2_leaf2
    AG2_and1 --> AG2_leaf3
    AG2_sub2 --> AG2_and2
    AG2_and2 --> AG2_leaf4
    AG2_and2 --> AG2_leaf5
    AG2_and2 --> AG2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333

    class AG2_root goal
    class AG2_or1 orGate
    class AG2_and1,AG2_and2 andGate
    class AG2_sub1,AG2_sub2 subGoal
    class AG2_leaf1,AG2_leaf2,AG2_leaf3,AG2_leaf4,AG2_leaf5,AG2_leaf6 leaf
```
