# I-1: Secrets such as the bearer token for edge-gateway appear in...

Carried from the baseline run.

**Component**: edge-gateway | **Risk Level**: High | **Finding**: I-1

Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

```mermaid
flowchart TD
    I1_root["Secrets such as the bearer token for edge-gateway appear in process..."]
    I1_or1{{"OR"}}
    I1_sub1["Reach edge-gateway in the Edge DMZ"]
    I1_sub2["Rely on the weakness described in I-1"]
    I1_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    I1_leaf2["Inbound api requests are accepted without an independent check"]
    I1_leaf3["The weakness is present: Secrets such as the bearer token for edge-gateway appear in..."]
    I1_leaf4["No effective control observed: Pass the bearer token to edge-gateway through a secret manager..."]

    I1_root --> I1_or1
    I1_or1 --> I1_sub1
    I1_or1 --> I1_sub2
    I1_sub1 --> I1_leaf1
    I1_sub1 --> I1_leaf2
    I1_sub2 --> I1_leaf3
    I1_sub2 --> I1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I1_root goal
    class I1_or1 orGate
    class I1_sub1,I1_sub2 subGoal
    class I1_leaf1,I1_leaf2,I1_leaf3,I1_leaf4 leaf
```
