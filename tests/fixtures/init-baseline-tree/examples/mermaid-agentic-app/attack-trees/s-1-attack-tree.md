# Attack Tree: S-1 — Authentication credential replay or forgery for user impersonation

| Field | Value |
|-------|-------|
| Finding ID | S-1 |
| Component | User |
| Risk Level | High |
| Threat | Authentication credential replay or forgery for user impersonation |
| Correlation | None |

```mermaid
flowchart TD
    S1_root["Impersonate legitimate user via credential compromise"]
    S1_or1{{"OR"}}
    S1_leaf1["Replay captured session token from network interception"]
    S1_leaf2["Forge authentication credential using leaked signing key"]
    S1_leaf3["Reuse expired token exploiting insufficient expiry validation"]

    S1_root --> S1_or1
    S1_or1 --> S1_leaf1
    S1_or1 --> S1_leaf2
    S1_or1 --> S1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S1_root goal
    class S1_or1 orGate
    class S1_leaf1,S1_leaf2,S1_leaf3 leaf
```
