# S-17: A compromised peer presents a forged service identity to worker-3...

**Component**: worker-3 | **Risk Level**: High | **Finding**: S-17

A compromised peer presents a forged service identity to worker-3, and worker-3 accepts the claim without verifying the signature chain back to the issuing authority.

```mermaid
flowchart TD
    S17_root["A compromised peer presents a forged service identity to worker-3, and..."]
    S17_or1{{"OR"}}
    S17_sub1["Reach worker-3 in the Agent Runtime Zone"]
    S17_sub2["Rely on the weakness described in S-17"]
    S17_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    S17_leaf2["Work orders and draft documents are accepted without an independent check"]
    S17_leaf3["The weakness is present: A compromised peer presents a forged service identity to worker-3..."]
    S17_leaf4["No effective control observed: Require mutual TLS between router-agent and worker-3 and validate..."]

    S17_root --> S17_or1
    S17_or1 --> S17_sub1
    S17_or1 --> S17_sub2
    S17_sub1 --> S17_leaf1
    S17_sub1 --> S17_leaf2
    S17_sub2 --> S17_leaf3
    S17_sub2 --> S17_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S17_root goal
    class S17_or1 orGate
    class S17_sub1,S17_sub2 subGoal
    class S17_leaf1,S17_leaf2,S17_leaf3,S17_leaf4 leaf
```
