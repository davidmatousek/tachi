# AG-43: Tool calls made by queue-a2 are not tied to the end user, so the...

**Component**: queue-a2 | **Risk Level**: High | **Finding**: AG-43

Tool calls made by queue-a2 are not tied to the end user, so the tool server cannot tell whose authority a request carries.

```mermaid
flowchart TD
    AG43_root["Tool calls made by queue-a2 are not tied to the end user, so the tool..."]
    AG43_or1{{"OR"}}
    AG43_sub1["Reach queue-a2 in the Agent Runtime Zone"]
    AG43_sub2["Rely on the weakness described in AG-43"]
    AG43_leaf1["A path exists from intake-agent over NATS over TLS"]
    AG43_leaf2["Task and result messages are accepted without an independent check"]
    AG43_leaf3["The weakness is present: Tool calls made by queue-a2 are not tied to the end user, so the..."]
    AG43_leaf4["No effective control observed: Propagate a signed end-user context with each tool call from..."]

    AG43_root --> AG43_or1
    AG43_or1 --> AG43_sub1
    AG43_or1 --> AG43_sub2
    AG43_sub1 --> AG43_leaf1
    AG43_sub1 --> AG43_leaf2
    AG43_sub2 --> AG43_leaf3
    AG43_sub2 --> AG43_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG43_root goal
    class AG43_or1 orGate
    class AG43_sub1,AG43_sub2 subGoal
    class AG43_leaf1,AG43_leaf2,AG43_leaf3,AG43_leaf4 leaf
```
