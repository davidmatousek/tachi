# S-36: Low-entropy identifiers accepted by eval-runner double as...

**Component**: eval-runner | **Risk Level**: Critical | **Finding**: S-36

Low-entropy identifiers accepted by eval-runner double as credentials, so an attacker who enumerates them submits requests under a victim's identity.

```mermaid
flowchart TD
    S36_root["Low-entropy identifiers accepted by eval-runner double as credentials..."]
    S36_or1{{"OR"}}
    S36_sub1["Reach eval-runner in the Operations Zone"]
    S36_sub2["Rely on the weakness described in S-36"]
    S36_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    S36_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    S36_leaf3["The weakness is present: Low-entropy identifiers accepted by eval-runner double as..."]
    S36_leaf4["No effective control observed: Separate identifiers from secrets, generate secrets from a..."]

    S36_root --> S36_or1
    S36_or1 --> S36_sub1
    S36_or1 --> S36_sub2
    S36_sub1 --> S36_leaf1
    S36_sub1 --> S36_leaf2
    S36_sub2 --> S36_leaf3
    S36_sub2 --> S36_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S36_root goal
    class S36_or1 orGate
    class S36_sub1,S36_sub2 subGoal
    class S36_leaf1,S36_leaf2,S36_leaf3,S36_leaf4 leaf
```
