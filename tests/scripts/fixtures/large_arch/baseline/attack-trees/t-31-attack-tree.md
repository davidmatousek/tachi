# T-31: Configuration of feature-store-2 can be rewritten by any service...

**Component**: feature-store-2 | **Risk Level**: High | **Finding**: T-31

Configuration of feature-store-2 can be rewritten by any service that holds the shared deployment credential, silently changing how ranking and fine-tuning features are handled.

```mermaid
flowchart TD
    T31_root["Configuration of feature-store-2 can be rewritten by any service that..."]
    T31_or1{{"OR"}}
    T31_sub1["Reach feature-store-2 in the Data Zone"]
    T31_sub2["Rely on the weakness described in T-31"]
    T31_leaf1["A path exists from eval-runner over PostgreSQL over TLS"]
    T31_leaf2["Ranking and fine-tuning features are accepted without an independent check"]
    T31_leaf3["The weakness is present: Configuration of feature-store-2 can be rewritten by any service..."]
    T31_leaf4["No effective control observed: Keep the configuration of feature-store-2 in a versioned..."]

    T31_root --> T31_or1
    T31_or1 --> T31_sub1
    T31_or1 --> T31_sub2
    T31_sub1 --> T31_leaf1
    T31_sub1 --> T31_leaf2
    T31_sub2 --> T31_leaf3
    T31_sub2 --> T31_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T31_root goal
    class T31_or1 orGate
    class T31_sub1,T31_sub2 subGoal
    class T31_leaf1,T31_leaf2,T31_leaf3,T31_leaf4 leaf
```
