# S-3: A shared or long-lived webhook signature on partner-feed lets...

**Component**: partner-feed | **Risk Level**: High | **Finding**: S-3

A shared or long-lived webhook signature on partner-feed lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

```mermaid
flowchart TD
    S3_root["A shared or long-lived webhook signature on partner-feed lets anyone..."]
    S3_or1{{"OR"}}
    S3_sub1["Reach partner-feed in the Public Internet"]
    S3_sub2["Rely on the weakness described in S-3"]
    S3_leaf1["A path exists from edge-gateway over HTTPS (TLS 1.3)"]
    S3_leaf2["Signed carrier manifests are accepted without an independent check"]
    S3_leaf3["The weakness is present: A shared or long-lived webhook signature on partner-feed lets..."]
    S3_leaf4["No effective control observed: Replace the shared webhook signature with per-workload identities..."]

    S3_root --> S3_or1
    S3_or1 --> S3_sub1
    S3_or1 --> S3_sub2
    S3_sub1 --> S3_leaf1
    S3_sub1 --> S3_leaf2
    S3_sub2 --> S3_leaf3
    S3_sub2 --> S3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S3_root goal
    class S3_or1 orGate
    class S3_sub1,S3_sub2 subGoal
    class S3_leaf1,S3_leaf2,S3_leaf3,S3_leaf4 leaf
```
