# E-22: embed-service-2 runs with broader permissions than its function...

**Component**: embed-service-2 | **Risk Level**: High | **Finding**: E-22

embed-service-2 runs with broader permissions than its function needs, so a flaw in handling document chunks and query embeddings yields access to unrelated resources.

```mermaid
flowchart TD
    E22_root["embed-service-2 runs with broader permissions than its function needs..."]
    E22_or1{{"OR"}}
    E22_sub1["Reach embed-service-2 in the Agent Runtime Zone"]
    E22_sub2["Rely on the weakness described in E-22"]
    E22_leaf1["A path exists from intake-agent over gRPC over mTLS"]
    E22_leaf2["Document chunks and query embeddings are accepted without an independent check"]
    E22_leaf3["The weakness is present: embed-service-2 runs with broader permissions than its function..."]
    E22_leaf4["No effective control observed: Reduce the permissions of embed-service-2 to the minimum for..."]

    E22_root --> E22_or1
    E22_or1 --> E22_sub1
    E22_or1 --> E22_sub2
    E22_sub1 --> E22_leaf1
    E22_sub1 --> E22_leaf2
    E22_sub2 --> E22_leaf3
    E22_sub2 --> E22_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E22_root goal
    class E22_or1 orGate
    class E22_sub1,E22_sub2 subGoal
    class E22_leaf1,E22_leaf2,E22_leaf3,E22_leaf4 leaf
```
