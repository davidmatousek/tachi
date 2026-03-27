# Attack Tree: I-5 -- Sensitive Data in Audit Logs

| Field | Value |
|-------|-------|
| Finding ID | I-5 |
| Component | Audit Logger |
| Risk Level | High |
| Threat | Sensitive Data in Audit Logs |
| Correlation | None |

```mermaid
flowchart TD
    I5_root["Access sensitive data in overly permissive audit logs"]
    I5_or1{{"OR"}}
    I5_leaf1["Exploit operations staff access to read sensitive log tier"]
    I5_leaf2["Query log store for prompt content containing PII"]
    I5_leaf3["Extract API credentials logged for debugging"]

    I5_root --> I5_or1
    I5_or1 --> I5_leaf1
    I5_or1 --> I5_leaf2
    I5_or1 --> I5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I5_root goal
    class I5_or1 orGate
    class I5_leaf1,I5_leaf2,I5_leaf3 leaf
```
