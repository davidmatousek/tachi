# Attack Tree: S-4 -- DNS Spoofing to Redirect External API Calls

| Field | Value |
|-------|-------|
| Finding ID | S-4 |
| Component | MCP Tool Server |
| Risk Level | High |
| Threat | DNS Spoofing to Redirect External API Calls |
| Correlation | None |

```mermaid
flowchart TD
    S4_root["Redirect Tool Server API calls to attacker-controlled endpoint"]
    S4_or1{{"OR"}}
    S4_leaf1["Spoof DNS response to resolve External API to attacker IP"]
    S4_leaf2["Compromise TLS certificate via CA manipulation"]
    S4_leaf3["Perform man-in-the-middle on unvalidated TLS connection"]

    S4_root --> S4_or1
    S4_or1 --> S4_leaf1
    S4_or1 --> S4_leaf2
    S4_or1 --> S4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S4_root goal
    class S4_or1 orGate
    class S4_leaf1,S4_leaf2,S4_leaf3 leaf
```
