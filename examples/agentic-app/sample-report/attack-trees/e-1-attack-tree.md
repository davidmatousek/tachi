# Attack Tree: E-1 -- Guardrails Bypass via Alternate Route

| Field | Value |
|-------|-------|
| Finding ID | E-1 |
| Component | Guardrails Service |
| Risk Level | High |
| Threat | Guardrails Bypass via Alternate Route |
| Correlation | None |

```mermaid
flowchart TD
    E1_root["Access Orchestrator bypassing Guardrails authorization"]
    E1_or1{{"OR"}}
    E1_leaf1["Exploit API gateway misconfiguration exposing internal routes"]
    E1_leaf2["Access Orchestrator via internal network from compromised service"]
    E1_leaf3["Use alternative protocol or port not covered by Guardrails"]

    E1_root --> E1_or1
    E1_or1 --> E1_leaf1
    E1_or1 --> E1_leaf2
    E1_or1 --> E1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E1_root goal
    class E1_or1 orGate
    class E1_leaf1,E1_leaf2,E1_leaf3 leaf
```
