# I-36: Cross-tenant filters on scheduler-1 are applied in application...

**Component**: scheduler-1 | **Risk Level**: High | **Finding**: I-36

Cross-tenant filters on scheduler-1 are applied in application code only, so one missing predicate exposes another tenant's recurring planning triggers.

```mermaid
flowchart TD
    I36_root["Cross-tenant filters on scheduler-1 are applied in application code..."]
    I36_or1{{"OR"}}
    I36_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    I36_sub2["Rely on the weakness described in I-36"]
    I36_leaf1["A path exists from queue-a2 over NATS over TLS"]
    I36_leaf2["Recurring planning triggers are accepted without an independent check"]
    I36_leaf3["The weakness is present: Cross-tenant filters on scheduler-1 are applied in application..."]
    I36_leaf4["No effective control observed: Enforce tenant isolation in the data layer with row-level policies..."]

    I36_root --> I36_or1
    I36_or1 --> I36_sub1
    I36_or1 --> I36_sub2
    I36_sub1 --> I36_leaf1
    I36_sub1 --> I36_leaf2
    I36_sub2 --> I36_leaf3
    I36_sub2 --> I36_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I36_root goal
    class I36_or1 orGate
    class I36_sub1,I36_sub2 subGoal
    class I36_leaf1,I36_leaf2,I36_leaf3,I36_leaf4 leaf
```
