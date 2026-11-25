# I-5: embedded documents and metadata held by vector-store-a are...

**Component**: vector-store-a | **Risk Level**: Critical | **Finding**: I-5

embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position.

```mermaid
flowchart TD
    I5_root["embedded documents and metadata held by vector-store-a are readable by..."]
    I5_or1{{"OR"}}
    I5_sub1["Reach vector-store-a in the Data Zone"]
    I5_sub2["Rely on the weakness described in I-5"]
    I5_leaf1["A path exists from worker-2 over PostgreSQL over TLS"]
    I5_leaf2["Embedded documents and metadata are accepted without an independent check"]
    I5_leaf3["The weakness is present: embedded documents and metadata held by vector-store-a are..."]
    I5_leaf4["No effective control observed: Grant access to embedded documents and metadata per workload..."]

    I5_root --> I5_or1
    I5_or1 --> I5_sub1
    I5_or1 --> I5_sub2
    I5_sub1 --> I5_leaf1
    I5_sub1 --> I5_leaf2
    I5_sub2 --> I5_leaf3
    I5_sub2 --> I5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I5_root goal
    class I5_or1 orGate
    class I5_sub1,I5_sub2 subGoal
    class I5_leaf1,I5_leaf2,I5_leaf3,I5_leaf4 leaf
```
