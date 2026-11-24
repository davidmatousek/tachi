# I-5: Logs and traces emitted by auth-broker include raw credential...

**Component**: auth-broker | **Risk Level**: High | **Finding**: I-5

Logs and traces emitted by auth-broker include raw credential assertions and session grants, so anyone with access to the logging pipeline can read content meant for one tenant.

```mermaid
flowchart TD
    I5_root["Logs and traces emitted by auth-broker include raw credential..."]
    I5_or1{{"OR"}}
    I5_sub1["Reach auth-broker in the Edge DMZ"]
    I5_sub2["Rely on the weakness described in I-5"]
    I5_leaf1["A path exists from edge-gateway over gRPC over mTLS"]
    I5_leaf2["Credential assertions and session grants are accepted without an independent check"]
    I5_leaf3["The weakness is present: Logs and traces emitted by auth-broker include raw credential..."]
    I5_leaf4["No effective control observed: Redact or tokenise sensitive fields before auth-broker emits logs..."]

    I5_root --> I5_or1
    I5_or1 --> I5_sub1
    I5_or1 --> I5_sub2
    I5_sub1 --> I5_leaf1
    I5_sub1 --> I5_leaf2
    I5_sub2 --> I5_leaf3
    I5_sub2 --> I5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I5_root goal
    class I5_or1 orGate
    class I5_sub1,I5_sub2 subGoal
    class I5_leaf1,I5_leaf2,I5_leaf3,I5_leaf4 leaf
```
