# Attack Tree: I-2 -- Internal State Leakage via Error Messages

| Field | Value |
|-------|-------|
| Finding ID | I-2 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | Internal State Leakage via Error Messages |
| Correlation | None |

```mermaid
flowchart TD
    I2_root["Extract internal topology from Orchestrator error messages"]
    I2_or1{{"OR"}}
    I2_leaf1["Trigger tool call failures to expose internal service details"]
    I2_leaf2["Cause context retrieval errors to reveal KB schema"]
    I2_leaf3["Induce model configuration errors exposing parameters"]

    I2_root --> I2_or1
    I2_or1 --> I2_leaf1
    I2_or1 --> I2_leaf2
    I2_or1 --> I2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I2_root goal
    class I2_or1 orGate
    class I2_leaf1,I2_leaf2,I2_leaf3 leaf
```
