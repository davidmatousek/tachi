# Attack Tree: D-1 -- Guardrails Service Resource Exhaustion

| Field | Value |
|-------|-------|
| Finding ID | D-1 |
| Component | Guardrails Service |
| Risk Level | Critical |
| Threat | Guardrails Service Resource Exhaustion |
| Correlation | None |

```mermaid
flowchart TD
    D1_root["Exhaust Guardrails Service CPU to block all prompt processing"]
    D1_or1{{"OR"}}
    D1_sub1["Exploit ReDoS-vulnerable regex patterns"]
    D1_sub2["Flood with high-volume requests"]
    D1_and1{{"AND"}}
    D1_leaf1["Identify regex patterns used in content filtering"]
    D1_leaf2["Craft input triggering catastrophic backtracking"]
    D1_leaf3["Submit sufficient volume to saturate all workers"]
    D1_and2{{"AND"}}
    D1_leaf4["Generate automated high-volume request stream"]
    D1_leaf5["Bypass any client-side rate controls"]
    D1_leaf6["Sustain flood until service degradation occurs"]

    D1_root --> D1_or1
    D1_or1 --> D1_sub1
    D1_or1 --> D1_sub2
    D1_sub1 --> D1_and1
    D1_and1 --> D1_leaf1
    D1_and1 --> D1_leaf2
    D1_and1 --> D1_leaf3
    D1_sub2 --> D1_and2
    D1_and2 --> D1_leaf4
    D1_and2 --> D1_leaf5
    D1_and2 --> D1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D1_root goal
    class D1_or1 orGate
    class D1_and1,D1_and2 andGate
    class D1_sub1,D1_sub2 subGoal
    class D1_leaf1,D1_leaf2,D1_leaf3,D1_leaf4,D1_leaf5,D1_leaf6 leaf
```
