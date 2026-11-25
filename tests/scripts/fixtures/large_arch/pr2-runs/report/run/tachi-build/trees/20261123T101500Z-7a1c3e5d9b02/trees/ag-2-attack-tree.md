# AG-2: planner-agent runs without a budget on steps or spend, so a loop...

**Component**: planner-agent | **Risk Level**: Critical | **Finding**: AG-2

planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

```mermaid
flowchart TD
    AG2_root["planner-agent runs without a budget on steps or spend, so a loop or an..."]
    AG2_or1{{"OR"}}
    AG2_sub1["Reach planner-agent in the Agent Runtime Zone"]
    AG2_sub2["Rely on the weakness described in AG-2"]
    AG2_leaf1["A path exists from model-gateway over HTTPS (TLS 1.3)"]
    AG2_leaf2["Task plans and tool selections are accepted without an independent check"]
    AG2_leaf3["The weakness is present: planner-agent runs without a budget on steps or spend, so a loop..."]
    AG2_leaf4["No effective control observed: Set hard limits on steps, tool calls, runtime and spend for..."]

    AG2_root --> AG2_or1
    AG2_or1 --> AG2_sub1
    AG2_or1 --> AG2_sub2
    AG2_sub1 --> AG2_leaf1
    AG2_sub1 --> AG2_leaf2
    AG2_sub2 --> AG2_leaf3
    AG2_sub2 --> AG2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG2_root goal
    class AG2_or1 orGate
    class AG2_sub1,AG2_sub2 subGoal
    class AG2_leaf1,AG2_leaf2,AG2_leaf3,AG2_leaf4 leaf
```
