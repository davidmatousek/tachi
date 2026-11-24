# S-24: A compromised peer presents a forged service identity to...

**Component**: embed-service-2 | **Risk Level**: High | **Finding**: S-24

A compromised peer presents a forged service identity to embed-service-2, and embed-service-2 accepts the claim without verifying the signature chain back to the issuing authority.

```mermaid
flowchart TD
    S24_root["A compromised peer presents a forged service identity to..."]
    S24_or1{{"OR"}}
    S24_sub1["Reach embed-service-2 in the Agent Runtime Zone"]
    S24_sub2["Rely on the weakness described in S-24"]
    S24_leaf1["A path exists from intake-agent over gRPC over mTLS"]
    S24_leaf2["Document chunks and query embeddings are accepted without an independent check"]
    S24_leaf3["The weakness is present: A compromised peer presents a forged service identity to..."]
    S24_leaf4["No effective control observed: Require mutual TLS between intake-agent and embed-service-2 and..."]

    S24_root --> S24_or1
    S24_or1 --> S24_sub1
    S24_or1 --> S24_sub2
    S24_sub1 --> S24_leaf1
    S24_sub1 --> S24_leaf2
    S24_sub2 --> S24_leaf3
    S24_sub2 --> S24_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S24_root goal
    class S24_or1 orGate
    class S24_sub1,S24_sub2 subGoal
    class S24_leaf1,S24_leaf2,S24_leaf3,S24_leaf4 leaf
```
