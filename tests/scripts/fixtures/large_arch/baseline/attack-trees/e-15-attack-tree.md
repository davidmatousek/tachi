# E-15: Object identifiers in requests to worker-3 are trusted without an...

**Component**: worker-3 | **Risk Level**: High | **Finding**: E-15

Object identifiers in requests to worker-3 are trusted without an ownership check, so a caller can read or change work orders and draft documents that belong to others.

```mermaid
flowchart TD
    E15_root["Object identifiers in requests to worker-3 are trusted without an..."]
    E15_or1{{"OR"}}
    E15_sub1["Reach worker-3 in the Agent Runtime Zone"]
    E15_sub2["Rely on the weakness described in E-15"]
    E15_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    E15_leaf2["Work orders and draft documents are accepted without an independent check"]
    E15_leaf3["The weakness is present: Object identifiers in requests to worker-3 are trusted without an..."]
    E15_leaf4["No effective control observed: Check ownership or entitlement for every object reference at..."]

    E15_root --> E15_or1
    E15_or1 --> E15_sub1
    E15_or1 --> E15_sub2
    E15_sub1 --> E15_leaf1
    E15_sub1 --> E15_leaf2
    E15_sub2 --> E15_leaf3
    E15_sub2 --> E15_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E15_root goal
    class E15_or1 orGate
    class E15_sub1,E15_sub2 subGoal
    class E15_leaf1,E15_leaf2,E15_leaf3,E15_leaf4 leaf
```
