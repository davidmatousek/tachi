# Attack Tree: I-1 -- Filter Rule Disclosure via Rejection Messages

| Field | Value |
|-------|-------|
| Finding ID | I-1 |
| Component | Guardrails Service |
| Risk Level | High |
| Threat | Filter Rule Disclosure via Rejection Messages |
| Correlation | None |

```mermaid
flowchart TD
    I1_root["Extract Guardrails filtering logic from rejection messages"]
    I1_and1{{"AND"}}
    I1_leaf1["Submit diverse prompts to trigger different rejection rules"]
    I1_leaf2["Analyze detailed rejection reasons for pattern extraction"]
    I1_leaf3["Reconstruct filtering rules to craft evasion prompts"]

    I1_root --> I1_and1
    I1_and1 --> I1_leaf1
    I1_and1 --> I1_leaf2
    I1_and1 --> I1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I1_root goal
    class I1_and1 andGate
    class I1_leaf1,I1_leaf2,I1_leaf3 leaf
```
