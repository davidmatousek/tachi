# Attack Tree: D-1 — Resource Exhaustion via High-Volume Computationally Expensive Prompts

**Finding ID**: D-1
**Risk Level**: Critical
**Component**: Guardrails Service
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    D1_root["Exhaust Guardrails Service capacity to disrupt filtering pipeline availability"]
    D1_or1{{"OR"}}
    D1_sub1["Flood Guardrails with high-volume prompt submissions"]
    D1_sub2["Submit adversarially expensive prompts to maximize rule evaluation cost"]
    D1_and1{{"AND"}}
    D1_leaf1["Identify User-Guardrails endpoint without per-IP rate limiting"]
    D1_leaf2["Submit high-rate prompt flood using distributed sources or botnet"]
    D1_leaf3["Saturate Guardrails processing queue to deny service to legitimate users"]
    D1_and2{{"AND"}}
    D1_leaf4["Craft prompts triggering complex regex or multi-rule evaluation chains"]
    D1_leaf5["Confirm Guardrails has no computational budget cap per prompt evaluation"]
    D1_leaf6["Submit crafted prompts at moderate rate to degrade service without triggering volume alerts"]

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
