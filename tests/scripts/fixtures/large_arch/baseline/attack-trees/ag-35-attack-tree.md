# AG-35: queue-a2 can start further agents or processes on request, so a...

**Component**: queue-a2 | **Risk Level**: High | **Finding**: AG-35

queue-a2 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

```mermaid
flowchart TD
    AG35_root["queue-a2 can start further agents or processes on request, so a..."]
    AG35_or1{{"OR"}}
    AG35_sub1["Reach queue-a2 in the Agent Runtime Zone"]
    AG35_sub2["Rely on the weakness described in AG-35"]
    AG35_leaf1["A path exists from intake-agent over NATS over TLS"]
    AG35_leaf2["Task and result messages are accepted without an independent check"]
    AG35_leaf3["The weakness is present: queue-a2 can start further agents or processes on request, so a..."]
    AG35_leaf4["No effective control observed: Remove the ability of queue-a2 to start other agents unless an..."]

    AG35_root --> AG35_or1
    AG35_or1 --> AG35_sub1
    AG35_or1 --> AG35_sub2
    AG35_sub1 --> AG35_leaf1
    AG35_sub1 --> AG35_leaf2
    AG35_sub2 --> AG35_leaf3
    AG35_sub2 --> AG35_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG35_root goal
    class AG35_or1 orGate
    class AG35_sub1,AG35_sub2 subGoal
    class AG35_leaf1,AG35_leaf2,AG35_leaf3,AG35_leaf4 leaf
```
