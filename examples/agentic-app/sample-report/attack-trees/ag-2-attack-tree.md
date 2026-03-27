# Attack Tree: AG-2 -- Unbounded Agent Reasoning Loop

| Field | Value |
|-------|-------|
| Finding ID | AG-2 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | Unbounded Agent Reasoning Loop |
| Correlation | CG-3 (See also: R-3) |

```mermaid
flowchart TD
    AG2_root["Trigger unbounded Orchestrator reasoning loop"]
    AG2_and1{{"AND"}}
    AG2_leaf1["Submit ambiguous prompt with unclear completion criteria"]
    AG2_leaf2["Orchestrator enters iterative loop without termination constraint"]
    AG2_leaf3["Resources consumed indefinitely until external intervention"]

    AG2_root --> AG2_and1
    AG2_and1 --> AG2_leaf1
    AG2_and1 --> AG2_leaf2
    AG2_and1 --> AG2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG2_root goal
    class AG2_and1 andGate
    class AG2_leaf1,AG2_leaf2,AG2_leaf3 leaf
```
