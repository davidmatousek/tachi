# OI-3: Markdown or HTML produced by intake-agent contains remote images...

**Component**: intake-agent | **Risk Level**: High | **Finding**: OI-3

Markdown or HTML produced by intake-agent contains remote images that leak data when a client renders it.

```mermaid
flowchart TD
    OI3_root["Markdown or HTML produced by intake-agent contains remote images that..."]
    OI3_or1{{"OR"}}
    OI3_sub1["Reach intake-agent in the Agent Runtime Zone"]
    OI3_sub2["Rely on the weakness described in OI-3"]
    OI3_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    OI3_leaf2["Free-text shipment requests are accepted without an independent check"]
    OI3_leaf3["The weakness is present: Markdown or HTML produced by intake-agent contains remote images..."]
    OI3_leaf4["No effective control observed: Strip remote resources from the output of intake-agent before..."]

    OI3_root --> OI3_or1
    OI3_or1 --> OI3_sub1
    OI3_or1 --> OI3_sub2
    OI3_sub1 --> OI3_leaf1
    OI3_sub1 --> OI3_leaf2
    OI3_sub2 --> OI3_leaf3
    OI3_sub2 --> OI3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI3_root goal
    class OI3_or1 orGate
    class OI3_sub1,OI3_sub2 subGoal
    class OI3_leaf1,OI3_leaf2,OI3_leaf3,OI3_leaf4 leaf
```
