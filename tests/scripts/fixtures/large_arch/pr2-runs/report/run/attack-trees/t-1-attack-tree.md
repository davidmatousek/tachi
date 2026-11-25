# T-1: Backups and exports of credential assertions and session grants on...

Carried from the baseline run.

**Component**: auth-broker | **Risk Level**: High | **Finding**: T-1

Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

```mermaid
flowchart TD
    T1_root["Backups and exports of credential assertions and session grants on..."]
    T1_or1{{"OR"}}
    T1_sub1["Reach auth-broker in the Edge DMZ"]
    T1_sub2["Rely on the weakness described in T-1"]
    T1_leaf1["A path exists from edge-gateway over gRPC over mTLS"]
    T1_leaf2["Credential assertions and session grants are accepted without an independent check"]
    T1_leaf3["The weakness is present: Backups and exports of credential assertions and session grants on..."]
    T1_leaf4["No effective control observed: Protect exports and backups of credential assertions and session..."]

    T1_root --> T1_or1
    T1_or1 --> T1_sub1
    T1_or1 --> T1_sub2
    T1_sub1 --> T1_leaf1
    T1_sub1 --> T1_leaf2
    T1_sub2 --> T1_leaf3
    T1_sub2 --> T1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T1_root goal
    class T1_or1 orGate
    class T1_sub1,T1_sub2 subGoal
    class T1_leaf1,T1_leaf2,T1_leaf3,T1_leaf4 leaf
```
