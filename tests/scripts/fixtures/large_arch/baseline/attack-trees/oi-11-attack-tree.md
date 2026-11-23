# OI-11: Markdown or HTML produced by planner-agent contains remote images...

**Component**: planner-agent | **Risk Level**: High | **Finding**: OI-11

Markdown or HTML produced by planner-agent contains remote images that leak data when a client renders it.

```mermaid
flowchart TD
    OI11_root["Markdown or HTML produced by planner-agent contains remote images that..."]
    OI11_or1{{"OR"}}
    OI11_sub1["Reach planner-agent in the Agent Runtime Zone"]
    OI11_sub2["Rely on the weakness described in OI-11"]
    OI11_leaf1["A path exists from queue-a2 over NATS over TLS"]
    OI11_leaf2["Task plans and tool selections are accepted without an independent check"]
    OI11_leaf3["The weakness is present: Markdown or HTML produced by planner-agent contains remote images..."]
    OI11_leaf4["No effective control observed: Strip remote resources from the output of planner-agent before..."]

    OI11_root --> OI11_or1
    OI11_or1 --> OI11_sub1
    OI11_or1 --> OI11_sub2
    OI11_sub1 --> OI11_leaf1
    OI11_sub1 --> OI11_leaf2
    OI11_sub2 --> OI11_leaf3
    OI11_sub2 --> OI11_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI11_root goal
    class OI11_or1 orGate
    class OI11_sub1,OI11_sub2 subGoal
    class OI11_leaf1,OI11_leaf2,OI11_leaf3,OI11_leaf4 leaf
```
