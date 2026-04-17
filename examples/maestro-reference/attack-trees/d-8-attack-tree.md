# Attack Tree: D-8 — Clinical LLM Inference Capacity Exhaustion

**Component**: Clinical LLM | **Risk Level**: High | **Finding**: D-8

An attacker exhausts Clinical LLM inference capacity through large prompt floods via the API Gateway, preventing legitimate clinical reasoning requests from being served.

```mermaid
flowchart TD
    D8_root["Exhaust Clinical LLM inference capacity via large prompt flood through API Gateway"]
    D8_or1{{"OR"}}
    D8_leaf1["Generate high-volume large prompt requests via API Gateway without per-session rate limiting"]
    D8_leaf2["Craft maximally-large prompts consuming disproportionate inference compute per request"]
    D8_leaf3["Sustain flood until inference queue saturates and legitimate clinical queries time out"]

    D8_root --> D8_or1
    D8_or1 --> D8_leaf1
    D8_or1 --> D8_leaf2
    D8_or1 --> D8_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D8_root goal
    class D8_or1 orGate
    class D8_leaf1,D8_leaf2,D8_leaf3 leaf
```
