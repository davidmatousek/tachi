# S-15: Low-entropy identifiers accepted by worker-3 double as...

**Component**: worker-3 | **Risk Level**: High | **Finding**: S-15

Low-entropy identifiers accepted by worker-3 double as credentials, so an attacker who enumerates them submits requests under a victim's identity.

```mermaid
flowchart TD
    S15_root["Low-entropy identifiers accepted by worker-3 double as credentials, so..."]
    S15_or1{{"OR"}}
    S15_sub1["Reach worker-3 in the Agent Runtime Zone"]
    S15_sub2["Rely on the weakness described in S-15"]
    S15_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    S15_leaf2["Work orders and draft documents are accepted without an independent check"]
    S15_leaf3["The weakness is present: Low-entropy identifiers accepted by worker-3 double as..."]
    S15_leaf4["No effective control observed: Separate identifiers from secrets, generate secrets from a..."]

    S15_root --> S15_or1
    S15_or1 --> S15_sub1
    S15_or1 --> S15_sub2
    S15_sub1 --> S15_leaf1
    S15_sub1 --> S15_leaf2
    S15_sub2 --> S15_leaf3
    S15_sub2 --> S15_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S15_root goal
    class S15_or1 orGate
    class S15_sub1,S15_sub2 subGoal
    class S15_leaf1,S15_leaf2,S15_leaf3,S15_leaf4 leaf
```
