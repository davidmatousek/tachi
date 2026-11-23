# T-32: A race between concurrent writers lets an attacker overwrite...

**Component**: feature-store-2 | **Risk Level**: High | **Finding**: T-32

A race between concurrent writers lets an attacker overwrite ranking and fine-tuning features on feature-store-2 after validation but before use, defeating the earlier check.

```mermaid
flowchart TD
    T32_root["A race between concurrent writers lets an attacker overwrite ranking..."]
    T32_or1{{"OR"}}
    T32_sub1["Reach feature-store-2 in the Data Zone"]
    T32_sub2["Rely on the weakness described in T-32"]
    T32_leaf1["A path exists from eval-runner over PostgreSQL over TLS"]
    T32_leaf2["Ranking and fine-tuning features are accepted without an independent check"]
    T32_leaf3["The weakness is present: A race between concurrent writers lets an attacker overwrite..."]
    T32_leaf4["No effective control observed: Make validation and use atomic: take a version-checked write or..."]

    T32_root --> T32_or1
    T32_or1 --> T32_sub1
    T32_or1 --> T32_sub2
    T32_sub1 --> T32_leaf1
    T32_sub1 --> T32_leaf2
    T32_sub2 --> T32_leaf3
    T32_sub2 --> T32_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T32_root goal
    class T32_or1 orGate
    class T32_sub1,T32_sub2 subGoal
    class T32_leaf1,T32_leaf2,T32_leaf3,T32_leaf4 leaf
```
