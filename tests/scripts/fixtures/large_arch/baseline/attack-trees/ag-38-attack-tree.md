# AG-38: scheduler-1 can start further agents or processes on request, so a...

**Component**: scheduler-1 | **Risk Level**: High | **Finding**: AG-38

scheduler-1 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

```mermaid
flowchart TD
    AG38_root["scheduler-1 can start further agents or processes on request, so a..."]
    AG38_or1{{"OR"}}
    AG38_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    AG38_sub2["Rely on the weakness described in AG-38"]
    AG38_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG38_leaf2["Recurring planning triggers are accepted without an independent check"]
    AG38_leaf3["The weakness is present: scheduler-1 can start further agents or processes on request, so a..."]
    AG38_leaf4["No effective control observed: Remove the ability of scheduler-1 to start other agents unless an..."]

    AG38_root --> AG38_or1
    AG38_or1 --> AG38_sub1
    AG38_or1 --> AG38_sub2
    AG38_sub1 --> AG38_leaf1
    AG38_sub1 --> AG38_leaf2
    AG38_sub2 --> AG38_leaf3
    AG38_sub2 --> AG38_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG38_root goal
    class AG38_or1 orGate
    class AG38_sub1,AG38_sub2 subGoal
    class AG38_leaf1,AG38_leaf2,AG38_leaf3,AG38_leaf4 leaf
```
