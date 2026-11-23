# R-31: Operators approve changes to credential assertions and session...

**Component**: auth-broker | **Risk Level**: High | **Finding**: R-31

Operators approve changes to credential assertions and session grants through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

```mermaid
flowchart TD
    R31_root["Operators approve changes to credential assertions and session grants..."]
    R31_or1{{"OR"}}
    R31_sub1["Reach auth-broker in the Edge DMZ"]
    R31_sub2["Rely on the weakness described in R-31"]
    R31_leaf1["A path exists from edge-gateway over gRPC over mTLS"]
    R31_leaf2["Credential assertions and session grants are accepted without an independent check"]
    R31_leaf3["The weakness is present: Operators approve changes to credential assertions and session..."]
    R31_leaf4["No effective control observed: Bind each approval to the exact change hash it covers, record..."]

    R31_root --> R31_or1
    R31_or1 --> R31_sub1
    R31_or1 --> R31_sub2
    R31_sub1 --> R31_leaf1
    R31_sub1 --> R31_leaf2
    R31_sub2 --> R31_leaf3
    R31_sub2 --> R31_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R31_root goal
    class R31_or1 orGate
    class R31_sub1,R31_sub2 subGoal
    class R31_leaf1,R31_leaf2,R31_leaf3,R31_leaf4 leaf
```
