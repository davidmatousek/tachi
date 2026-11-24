# S-25: A shared or long-lived service credential on embed-service-2 lets...

**Component**: embed-service-2 | **Risk Level**: Critical | **Finding**: S-25

A shared or long-lived service credential on embed-service-2 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

```mermaid
flowchart TD
    S25_root["A shared or long-lived service credential on embed-service-2 lets..."]
    S25_or1{{"OR"}}
    S25_sub1["Reach embed-service-2 in the Agent Runtime Zone"]
    S25_sub2["Rely on the weakness described in S-25"]
    S25_leaf1["A path exists from intake-agent over gRPC over mTLS"]
    S25_leaf2["Document chunks and query embeddings are accepted without an independent check"]
    S25_leaf3["The weakness is present: A shared or long-lived service credential on embed-service-2 lets..."]
    S25_leaf4["No effective control observed: Replace the shared service credential with per-workload identities..."]

    S25_root --> S25_or1
    S25_or1 --> S25_sub1
    S25_or1 --> S25_sub2
    S25_sub1 --> S25_leaf1
    S25_sub1 --> S25_leaf2
    S25_sub2 --> S25_leaf3
    S25_sub2 --> S25_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S25_root goal
    class S25_or1 orGate
    class S25_sub1,S25_sub2 subGoal
    class S25_leaf1,S25_leaf2,S25_leaf3,S25_leaf4 leaf
```
