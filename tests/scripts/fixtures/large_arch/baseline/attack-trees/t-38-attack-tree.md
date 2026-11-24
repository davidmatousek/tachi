# T-38: Backups and exports of replayed traces and judge verdicts on...

**Component**: eval-runner | **Risk Level**: High | **Finding**: T-38

Backups and exports of replayed traces and judge verdicts on eval-runner are writable by operators without a second approver, so a malicious change survives restores.

```mermaid
flowchart TD
    T38_root["Backups and exports of replayed traces and judge verdicts on..."]
    T38_or1{{"OR"}}
    T38_sub1["Reach eval-runner in the Operations Zone"]
    T38_sub2["Rely on the weakness described in T-38"]
    T38_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    T38_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    T38_leaf3["The weakness is present: Backups and exports of replayed traces and judge verdicts on..."]
    T38_leaf4["No effective control observed: Protect exports and backups of replayed traces and judge verdicts..."]

    T38_root --> T38_or1
    T38_or1 --> T38_sub1
    T38_or1 --> T38_sub2
    T38_sub1 --> T38_leaf1
    T38_sub1 --> T38_leaf2
    T38_sub2 --> T38_leaf3
    T38_sub2 --> T38_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T38_root goal
    class T38_or1 orGate
    class T38_sub1,T38_sub2 subGoal
    class T38_leaf1,T38_leaf2,T38_leaf3,T38_leaf4 leaf
```
