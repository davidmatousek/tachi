# T-2: Backups and exports of credential assertions and session grants on...

**Component**: auth-broker | **Risk Level**: High | **Finding**: T-2

Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

```mermaid
flowchart TD
    T2_root["Backups and exports of credential assertions and session grants on..."]
    T2_or1{{"OR"}}
    T2_sub1["Reach auth-broker in the Edge DMZ"]
    T2_sub2["Rely on the weakness described in T-2"]
    T2_leaf1["A path exists from edge-gateway over gRPC over mTLS"]
    T2_leaf2["Credential assertions and session grants are accepted without an independent check"]
    T2_leaf3["The weakness is present: Backups and exports of credential assertions and session grants on..."]
    T2_leaf4["No effective control observed: Protect exports and backups of credential assertions and session..."]

    T2_root --> T2_or1
    T2_or1 --> T2_sub1
    T2_or1 --> T2_sub2
    T2_sub1 --> T2_leaf1
    T2_sub1 --> T2_leaf2
    T2_sub2 --> T2_leaf3
    T2_sub2 --> T2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T2_root goal
    class T2_or1 orGate
    class T2_sub1,T2_sub2 subGoal
    class T2_leaf1,T2_leaf2,T2_leaf3,T2_leaf4 leaf
```
