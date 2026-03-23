# Attack Tree: D-1 — Resource exhaustion via computationally expensive prompts

| Field | Value |
|-------|-------|
| Finding ID | D-1 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | Resource exhaustion via computationally expensive prompts |
| Correlation | None |

```mermaid
flowchart TD
    D1_root["Exhaust LLM inference resources to degrade service"]
    D1_or1{{"OR"}}
    D1_leaf1["Submit prompts requiring maximum token generation"]
    D1_leaf2["Submit concurrent requests exceeding rate limits"]
    D1_leaf3["Craft prompts triggering expensive reasoning chains"]

    D1_root --> D1_or1
    D1_or1 --> D1_leaf1
    D1_or1 --> D1_leaf2
    D1_or1 --> D1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D1_root goal
    class D1_or1 orGate
    class D1_leaf1,D1_leaf2,D1_leaf3 leaf
```
