# E-5: Role claims carried in the refresh token presented to auth-broker...

**Component**: auth-broker | **Risk Level**: High | **Finding**: E-5

Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against the authoritative directory.

```mermaid
flowchart TD
    E5_root["Role claims carried in the refresh token presented to auth-broker are..."]
    E5_or1{{"OR"}}
    E5_sub1["Reach auth-broker in the Edge DMZ"]
    E5_sub2["Rely on the weakness described in E-5"]
    E5_leaf1["A path exists from edge-gateway over gRPC over mTLS"]
    E5_leaf2["Credential assertions and session grants are accepted without an independent check"]
    E5_leaf3["The weakness is present: Role claims carried in the refresh token presented to auth-broker..."]
    E5_leaf4["No effective control observed: Resolve roles for auth-broker from the authoritative directory on..."]

    E5_root --> E5_or1
    E5_or1 --> E5_sub1
    E5_or1 --> E5_sub2
    E5_sub1 --> E5_leaf1
    E5_sub1 --> E5_leaf2
    E5_sub2 --> E5_leaf3
    E5_sub2 --> E5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E5_root goal
    class E5_or1 orGate
    class E5_sub1,E5_sub2 subGoal
    class E5_leaf1,E5_leaf2,E5_leaf3,E5_leaf4 leaf
```
