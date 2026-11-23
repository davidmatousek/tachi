# S-39: A compromised peer presents a forged service identity to...

**Component**: policy-engine | **Risk Level**: Critical | **Finding**: S-39

A compromised peer presents a forged service identity to policy-engine, and policy-engine accepts the claim without verifying the signature chain back to the issuing authority.

```mermaid
flowchart TD
    S39_root["A compromised peer presents a forged service identity to..."]
    S39_or1{{"OR"}}
    S39_sub1["Reach policy-engine in the Operations Zone"]
    S39_sub2["Rely on the weakness described in S-39"]
    S39_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    S39_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    S39_leaf3["The weakness is present: A compromised peer presents a forged service identity to..."]
    S39_leaf4["No effective control observed: Require mutual TLS between audit-ledger and policy-engine and..."]

    S39_root --> S39_or1
    S39_or1 --> S39_sub1
    S39_or1 --> S39_sub2
    S39_sub1 --> S39_leaf1
    S39_sub1 --> S39_leaf2
    S39_sub2 --> S39_leaf3
    S39_sub2 --> S39_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S39_root goal
    class S39_or1 orGate
    class S39_sub1,S39_sub2 subGoal
    class S39_leaf1,S39_leaf2,S39_leaf3,S39_leaf4 leaf
```
