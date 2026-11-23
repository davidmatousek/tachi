# S-32: A compromised peer presents a forged service identity to...

**Component**: trace-collector | **Risk Level**: High | **Finding**: S-32

A compromised peer presents a forged service identity to trace-collector, and trace-collector accepts the claim without verifying the signature chain back to the issuing authority.

```mermaid
flowchart TD
    S32_root["A compromised peer presents a forged service identity to..."]
    S32_or1{{"OR"}}
    S32_sub1["Reach trace-collector in the Operations Zone"]
    S32_sub2["Rely on the weakness described in S-32"]
    S32_leaf1["A path exists from intake-agent over OTLP over TLS"]
    S32_leaf2["Prompts, completions and tool traces are accepted without an independent check"]
    S32_leaf3["The weakness is present: A compromised peer presents a forged service identity to..."]
    S32_leaf4["No effective control observed: Require mutual TLS between planner-agent and trace-collector and..."]

    S32_root --> S32_or1
    S32_or1 --> S32_sub1
    S32_or1 --> S32_sub2
    S32_sub1 --> S32_leaf1
    S32_sub1 --> S32_leaf2
    S32_sub2 --> S32_leaf3
    S32_sub2 --> S32_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S32_root goal
    class S32_or1 orGate
    class S32_sub1,S32_sub2 subGoal
    class S32_leaf1,S32_leaf2,S32_leaf3,S32_leaf4 leaf
```
