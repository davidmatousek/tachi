# Attack Tree: D-2 -- Orchestrator Compute Exhaustion

| Field | Value |
|-------|-------|
| Finding ID | D-2 |
| Component | LLM Agent Orchestrator |
| Risk Level | Critical |
| Threat | Orchestrator Compute Exhaustion |
| Correlation | None |

```mermaid
flowchart TD
    D2_root["Exhaust LLM inference compute to block legitimate requests"]
    D2_or1{{"OR"}}
    D2_sub1["Maximum-length prompt flooding"]
    D2_sub2["Complex prompt exploitation"]
    D2_and1{{"AND"}}
    D2_leaf1["Generate concurrent requests with max-length prompts"]
    D2_leaf2["Consume all available inference compute slots"]
    D2_leaf3["Legitimate requests queued indefinitely or rejected"]
    D2_leaf4["Craft prompts triggering expensive reasoning chains"]
    D2_leaf5["Each request consumes disproportionate compute time"]

    D2_root --> D2_or1
    D2_or1 --> D2_sub1
    D2_or1 --> D2_sub2
    D2_sub1 --> D2_and1
    D2_and1 --> D2_leaf1
    D2_and1 --> D2_leaf2
    D2_and1 --> D2_leaf3
    D2_sub2 --> D2_leaf4
    D2_sub2 --> D2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D2_root goal
    class D2_or1 orGate
    class D2_and1 andGate
    class D2_sub1,D2_sub2 subGoal
    class D2_leaf1,D2_leaf2,D2_leaf3,D2_leaf4,D2_leaf5 leaf
```
