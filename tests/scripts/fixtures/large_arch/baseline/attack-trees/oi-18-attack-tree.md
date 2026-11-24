# OI-18: Markdown or HTML produced by model-gateway contains remote images...

**Component**: model-gateway | **Risk Level**: High | **Finding**: OI-18

Markdown or HTML produced by model-gateway contains remote images that leak data when a client renders it.

```mermaid
flowchart TD
    OI18_root["Markdown or HTML produced by model-gateway contains remote images that..."]
    OI18_or1{{"OR"}}
    OI18_sub1["Reach model-gateway in the Agent Runtime Zone"]
    OI18_sub2["Rely on the weakness described in OI-18"]
    OI18_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    OI18_leaf2["Prompts and completions are accepted without an independent check"]
    OI18_leaf3["The weakness is present: Markdown or HTML produced by model-gateway contains remote images..."]
    OI18_leaf4["No effective control observed: Strip remote resources from the output of model-gateway before..."]

    OI18_root --> OI18_or1
    OI18_or1 --> OI18_sub1
    OI18_or1 --> OI18_sub2
    OI18_sub1 --> OI18_leaf1
    OI18_sub1 --> OI18_leaf2
    OI18_sub2 --> OI18_leaf3
    OI18_sub2 --> OI18_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI18_root goal
    class OI18_or1 orGate
    class OI18_sub1,OI18_sub2 subGoal
    class OI18_leaf1,OI18_leaf2,OI18_leaf3,OI18_leaf4 leaf
```
