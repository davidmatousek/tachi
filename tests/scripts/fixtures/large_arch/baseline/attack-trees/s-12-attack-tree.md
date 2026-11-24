# S-12: A shared or long-lived worker credential on worker-2 lets anyone...

**Component**: worker-2 | **Risk Level**: High | **Finding**: S-12

A shared or long-lived worker credential on worker-2 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

```mermaid
flowchart TD
    S12_root["A shared or long-lived worker credential on worker-2 lets anyone who..."]
    S12_or1{{"OR"}}
    S12_sub1["Reach worker-2 in the Agent Runtime Zone"]
    S12_sub2["Rely on the weakness described in S-12"]
    S12_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    S12_leaf2["Work orders and route candidates are accepted without an independent check"]
    S12_leaf3["The weakness is present: A shared or long-lived worker credential on worker-2 lets anyone..."]
    S12_leaf4["No effective control observed: Replace the shared worker credential with per-workload identities..."]

    S12_root --> S12_or1
    S12_or1 --> S12_sub1
    S12_or1 --> S12_sub2
    S12_sub1 --> S12_leaf1
    S12_sub1 --> S12_leaf2
    S12_sub2 --> S12_leaf3
    S12_sub2 --> S12_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S12_root goal
    class S12_or1 orGate
    class S12_sub1,S12_sub2 subGoal
    class S12_leaf1,S12_leaf2,S12_leaf3,S12_leaf4 leaf
```
