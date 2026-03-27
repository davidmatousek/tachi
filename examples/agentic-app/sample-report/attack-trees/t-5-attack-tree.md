# Attack Tree: T-5 -- Audit Log Tampering

| Field | Value |
|-------|-------|
| Finding ID | T-5 |
| Component | Audit Logger |
| Risk Level | High |
| Threat | Audit Log Tampering |
| Correlation | None |

```mermaid
flowchart TD
    T5_root["Modify or delete audit logs to cover attack evidence"]
    T5_or1{{"OR"}}
    T5_leaf1["Exploit application write access to log store"]
    T5_leaf2["Access log database with shared credentials"]
    T5_leaf3["Exploit log rotation to delete entries before retention"]

    T5_root --> T5_or1
    T5_or1 --> T5_leaf1
    T5_or1 --> T5_leaf2
    T5_or1 --> T5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T5_root goal
    class T5_or1 orGate
    class T5_leaf1,T5_leaf2,T5_leaf3 leaf
```
