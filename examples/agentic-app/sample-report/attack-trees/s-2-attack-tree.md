# Attack Tree: S-2 -- Guardrails Bypass via Service Impersonation

| Field | Value |
|-------|-------|
| Finding ID | S-2 |
| Component | Guardrails Service |
| Risk Level | High |
| Threat | Guardrails Bypass via Service Impersonation |
| Correlation | None |

```mermaid
flowchart TD
    S2_root["Bypass Guardrails by impersonating its identity to Orchestrator"]
    S2_or1{{"OR"}}
    S2_sub1["Direct network access to Orchestrator"]
    S2_sub2["Forge Guardrails service identity"]
    S2_leaf1["Discover Orchestrator internal endpoint via service enumeration"]
    S2_leaf2["Submit prompt directly to Orchestrator bypassing Guardrails"]
    S2_and1{{"AND"}}
    S2_leaf3["Obtain Guardrails service credentials or certificate"]
    S2_leaf4["Craft request mimicking Guardrails forwarding format"]

    S2_root --> S2_or1
    S2_or1 --> S2_sub1
    S2_or1 --> S2_sub2
    S2_sub1 --> S2_leaf1
    S2_sub1 --> S2_leaf2
    S2_sub2 --> S2_and1
    S2_and1 --> S2_leaf3
    S2_and1 --> S2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S2_root goal
    class S2_or1 orGate
    class S2_and1 andGate
    class S2_sub1,S2_sub2 subGoal
    class S2_leaf1,S2_leaf2,S2_leaf3,S2_leaf4 leaf
```
