# Attack Tree: S-1 -- User Identity Spoofing via Token Replay

| Field | Value |
|-------|-------|
| Finding ID | S-1 |
| Component | User |
| Risk Level | High |
| Threat | User Identity Spoofing via Token Replay |
| Correlation | None |

```mermaid
flowchart TD
    S1_root["Impersonate legitimate user to submit unauthorized prompts"]
    S1_or1{{"OR"}}
    S1_sub1["Replay stolen bearer token"]
    S1_sub2["Forge new bearer token"]
    S1_and1{{"AND"}}
    S1_leaf1["Intercept token from network traffic or logs"]
    S1_leaf2["Submit requests with stolen token before expiry"]
    S1_and2{{"AND"}}
    S1_leaf3["Extract signing key or exploit weak algorithm"]
    S1_leaf4["Craft token with target user claims"]

    S1_root --> S1_or1
    S1_or1 --> S1_sub1
    S1_or1 --> S1_sub2
    S1_sub1 --> S1_and1
    S1_and1 --> S1_leaf1
    S1_and1 --> S1_leaf2
    S1_sub2 --> S1_and2
    S1_and2 --> S1_leaf3
    S1_and2 --> S1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S1_root goal
    class S1_or1 orGate
    class S1_and1,S1_and2 andGate
    class S1_sub1,S1_sub2 subGoal
    class S1_leaf1,S1_leaf2,S1_leaf3,S1_leaf4 leaf
```
