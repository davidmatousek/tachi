# S-40: An unauthenticated callback or health route on edge-gateway...

**Component**: edge-gateway | **Risk Level**: High | **Finding**: S-40

An unauthenticated callback or health route on edge-gateway accepts requests that downstream code treats as if they had come from auth-broker.

```mermaid
flowchart TD
    S40_root["An unauthenticated callback or health route on edge-gateway accepts..."]
    S40_or1{{"OR"}}
    S40_sub1["Reach edge-gateway in the Edge DMZ"]
    S40_sub2["Rely on the weakness described in S-40"]
    S40_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    S40_leaf2["Inbound api requests are accepted without an independent check"]
    S40_leaf3["The weakness is present: An unauthenticated callback or health route on edge-gateway..."]
    S40_leaf4["No effective control observed: Remove implicit trust in route names: authenticate every route of..."]

    S40_root --> S40_or1
    S40_or1 --> S40_sub1
    S40_or1 --> S40_sub2
    S40_sub1 --> S40_leaf1
    S40_sub1 --> S40_leaf2
    S40_sub2 --> S40_leaf3
    S40_sub2 --> S40_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S40_root goal
    class S40_or1 orGate
    class S40_sub1,S40_sub2 subGoal
    class S40_leaf1,S40_leaf2,S40_leaf3,S40_leaf4 leaf
```
