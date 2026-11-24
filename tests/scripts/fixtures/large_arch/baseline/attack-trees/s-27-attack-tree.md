# S-27: An attacker replays a captured inference credential against...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: S-27

An attacker replays a captured inference credential against summarizer-llm, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

```mermaid
flowchart TD
    S27_root["An attacker replays a captured inference credential against..."]
    S27_or1{{"OR"}}
    S27_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    S27_sub2["Rely on the weakness described in S-27"]
    S27_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    S27_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    S27_leaf3["The weakness is present: An attacker replays a captured inference credential against..."]
    S27_leaf4["No effective control observed: Bind each inference credential to the client certificate or device..."]

    S27_root --> S27_or1
    S27_or1 --> S27_sub1
    S27_or1 --> S27_sub2
    S27_sub1 --> S27_leaf1
    S27_sub1 --> S27_leaf2
    S27_sub2 --> S27_leaf3
    S27_sub2 --> S27_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S27_root goal
    class S27_or1 orGate
    class S27_sub1,S27_sub2 subGoal
    class S27_leaf1,S27_leaf2,S27_leaf3,S27_leaf4 leaf
```
