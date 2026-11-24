# D-27: A single oversized or deeply nested payload makes feature-store-2...

**Component**: feature-store-2 | **Risk Level**: High | **Finding**: D-27

A single oversized or deeply nested payload makes feature-store-2 spend disproportionate memory and CPU parsing ranking and fine-tuning features.

```mermaid
flowchart TD
    D27_root["A single oversized or deeply nested payload makes feature-store-2..."]
    D27_or1{{"OR"}}
    D27_sub1["Reach feature-store-2 in the Data Zone"]
    D27_sub2["Rely on the weakness described in D-27"]
    D27_leaf1["A path exists from eval-runner over PostgreSQL over TLS"]
    D27_leaf2["Ranking and fine-tuning features are accepted without an independent check"]
    D27_leaf3["The weakness is present: A single oversized or deeply nested payload makes feature-store-2..."]
    D27_leaf4["No effective control observed: Cap payload size, nesting depth and parse time in feature-store-2..."]

    D27_root --> D27_or1
    D27_or1 --> D27_sub1
    D27_or1 --> D27_sub2
    D27_sub1 --> D27_leaf1
    D27_sub1 --> D27_leaf2
    D27_sub2 --> D27_leaf3
    D27_sub2 --> D27_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D27_root goal
    class D27_or1 orGate
    class D27_sub1,D27_sub2 subGoal
    class D27_leaf1,D27_leaf2,D27_leaf3,D27_leaf4 leaf
```
