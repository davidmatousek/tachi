# Attack Tree: I-2 — System prompt extraction via crafted meta-instruction queries

| Field | Value |
|-------|-------|
| Finding ID | I-2 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | System prompt extraction via crafted meta-instruction queries |
| Correlation | None |

```mermaid
flowchart TD
    I2_root["Extract system prompt contents from orchestrator"]
    I2_or1{{"OR"}}
    I2_leaf1["Submit meta-instruction query asking LLM to repeat its instructions"]
    I2_leaf2["Craft prompt requesting system prompt in encoded format"]
    I2_leaf3["Use role-play technique to elicit system prompt disclosure"]

    I2_root --> I2_or1
    I2_or1 --> I2_leaf1
    I2_or1 --> I2_leaf2
    I2_or1 --> I2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I2_root goal
    class I2_or1 orGate
    class I2_leaf1,I2_leaf2,I2_leaf3 leaf
```
