# Attack Tree: T-2 -- Prompt Tampering in Transit

| Field | Value |
|-------|-------|
| Finding ID | T-2 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | Prompt Tampering in Transit |
| Correlation | None |

```mermaid
flowchart TD
    T2_root["Inject malicious content into validated prompt in transit"]
    T2_and1{{"AND"}}
    T2_leaf1["Gain network position between Guardrails and Orchestrator"]
    T2_leaf2["Intercept unencrypted or unsigned prompt data"]
    T2_leaf3["Modify prompt content to include adversarial instructions"]

    T2_root --> T2_and1
    T2_and1 --> T2_leaf1
    T2_and1 --> T2_leaf2
    T2_and1 --> T2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T2_root goal
    class T2_and1 andGate
    class T2_leaf1,T2_leaf2,T2_leaf3 leaf
```
