# T-22: Unsanitised embedded documents and metadata reach vector-store-a...

**Component**: vector-store-a | **Risk Level**: High | **Finding**: T-22

Unsanitised embedded documents and metadata reach vector-store-a and are processed as trusted structure, so crafted input changes how later steps interpret the record.

```mermaid
flowchart TD
    T22_root["Unsanitised embedded documents and metadata reach vector-store-a and..."]
    T22_or1{{"OR"}}
    T22_sub1["Reach vector-store-a in the Data Zone"]
    T22_sub2["Rely on the weakness described in T-22"]
    T22_leaf1["A path exists from worker-2 over PostgreSQL over TLS"]
    T22_leaf2["Embedded documents and metadata are accepted without an independent check"]
    T22_leaf3["The weakness is present: Unsanitised embedded documents and metadata reach vector-store-a..."]
    T22_leaf4["No effective control observed: Validate embedded documents and metadata against a strict schema..."]

    T22_root --> T22_or1
    T22_or1 --> T22_sub1
    T22_or1 --> T22_sub2
    T22_sub1 --> T22_leaf1
    T22_sub1 --> T22_leaf2
    T22_sub2 --> T22_leaf3
    T22_sub2 --> T22_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T22_root goal
    class T22_or1 orGate
    class T22_sub1,T22_sub2 subGoal
    class T22_leaf1,T22_leaf2,T22_leaf3,T22_leaf4 leaf
```
