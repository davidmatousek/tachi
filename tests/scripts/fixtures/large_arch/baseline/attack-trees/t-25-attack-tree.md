# T-25: Backups and exports of task history and operator preferences on...

**Component**: memory-store | **Risk Level**: Critical | **Finding**: T-25

Backups and exports of task history and operator preferences on memory-store are writable by operators without a second approver, so a malicious change survives restores.

```mermaid
flowchart TD
    T25_root["Backups and exports of task history and operator preferences on..."]
    T25_or1{{"OR"}}
    T25_sub1["Reach memory-store in the Data Zone"]
    T25_sub2["Rely on the weakness described in T-25"]
    T25_leaf1["A path exists from planner-agent over PostgreSQL over TLS"]
    T25_leaf2["Task history and operator preferences are accepted without an independent check"]
    T25_leaf3["The weakness is present: Backups and exports of task history and operator preferences on..."]
    T25_leaf4["No effective control observed: Protect exports and backups of task history and operator..."]

    T25_root --> T25_or1
    T25_or1 --> T25_sub1
    T25_or1 --> T25_sub2
    T25_sub1 --> T25_leaf1
    T25_sub1 --> T25_leaf2
    T25_sub2 --> T25_leaf3
    T25_sub2 --> T25_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T25_root goal
    class T25_or1 orGate
    class T25_sub1,T25_sub2 subGoal
    class T25_leaf1,T25_leaf2,T25_leaf3,T25_leaf4 leaf
```
