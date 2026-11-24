# R-24: Clock drift between scheduler-1 and queue-a2 leaves events in...

**Component**: scheduler-1 | **Risk Level**: High | **Finding**: R-24

Clock drift between scheduler-1 and queue-a2 leaves events in inconsistent order, so the sequence of actions on recurring planning triggers cannot be reconstructed reliably.

```mermaid
flowchart TD
    R24_root["Clock drift between scheduler-1 and queue-a2 leaves events in..."]
    R24_or1{{"OR"}}
    R24_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    R24_sub2["Rely on the weakness described in R-24"]
    R24_leaf1["A path exists from queue-a2 over NATS over TLS"]
    R24_leaf2["Recurring planning triggers are accepted without an independent check"]
    R24_leaf3["The weakness is present: Clock drift between scheduler-1 and queue-a2 leaves events in..."]
    R24_leaf4["No effective control observed: Synchronise scheduler-1 and queue-a2 to a trusted time source..."]

    R24_root --> R24_or1
    R24_or1 --> R24_sub1
    R24_or1 --> R24_sub2
    R24_sub1 --> R24_leaf1
    R24_sub1 --> R24_leaf2
    R24_sub2 --> R24_leaf3
    R24_sub2 --> R24_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R24_root goal
    class R24_or1 orGate
    class R24_sub1,R24_sub2 subGoal
    class R24_leaf1,R24_leaf2,R24_leaf3,R24_leaf4 leaf
```
