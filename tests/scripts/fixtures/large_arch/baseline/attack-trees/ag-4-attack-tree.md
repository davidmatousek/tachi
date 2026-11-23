# AG-4: planner-agent runs without a budget on steps or spend, so a loop...

**Component**: planner-agent | **Risk Level**: High | **Finding**: AG-4

planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

```mermaid
flowchart TD
    AG4_root["planner-agent runs without a budget on steps or spend, so a loop or an..."]
    AG4_or1{{"OR"}}
    AG4_sub1["Reach planner-agent in the Agent Runtime Zone"]
    AG4_sub2["Rely on the weakness described in AG-4"]
    AG4_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG4_leaf2["Task plans and tool selections are accepted without an independent check"]
    AG4_leaf3["The weakness is present: planner-agent runs without a budget on steps or spend, so a loop..."]
    AG4_leaf4["No effective control observed: Set hard limits on steps, tool calls, runtime and spend for..."]

    AG4_root --> AG4_or1
    AG4_or1 --> AG4_sub1
    AG4_or1 --> AG4_sub2
    AG4_sub1 --> AG4_leaf1
    AG4_sub1 --> AG4_leaf2
    AG4_sub2 --> AG4_leaf3
    AG4_sub2 --> AG4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG4_root goal
    class AG4_or1 orGate
    class AG4_sub1,AG4_sub2 subGoal
    class AG4_leaf1,AG4_leaf2,AG4_leaf3,AG4_leaf4 leaf
```
