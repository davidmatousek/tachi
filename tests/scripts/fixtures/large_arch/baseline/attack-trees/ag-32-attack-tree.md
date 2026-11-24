# AG-32: tool-server-1 runs without a budget on steps or spend, so a loop...

**Component**: tool-server-1 | **Risk Level**: High | **Finding**: AG-32

tool-server-1 runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

```mermaid
flowchart TD
    AG32_root["tool-server-1 runs without a budget on steps or spend, so a loop or an..."]
    AG32_or1{{"OR"}}
    AG32_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    AG32_sub2["Rely on the weakness described in AG-32"]
    AG32_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    AG32_leaf2["Tool call arguments and results are accepted without an independent check"]
    AG32_leaf3["The weakness is present: tool-server-1 runs without a budget on steps or spend, so a loop..."]
    AG32_leaf4["No effective control observed: Set hard limits on steps, tool calls, runtime and spend for..."]

    AG32_root --> AG32_or1
    AG32_or1 --> AG32_sub1
    AG32_or1 --> AG32_sub2
    AG32_sub1 --> AG32_leaf1
    AG32_sub1 --> AG32_leaf2
    AG32_sub2 --> AG32_leaf3
    AG32_sub2 --> AG32_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG32_root goal
    class AG32_or1 orGate
    class AG32_sub1,AG32_sub2 subGoal
    class AG32_leaf1,AG32_leaf2,AG32_leaf3,AG32_leaf4 leaf
```
