# OI-24: Markdown or HTML produced by summarizer-llm contains remote images...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: OI-24

Markdown or HTML produced by summarizer-llm contains remote images that leak data when a client renders it.

```mermaid
flowchart TD
    OI24_root["Markdown or HTML produced by summarizer-llm contains remote images..."]
    OI24_or1{{"OR"}}
    OI24_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    OI24_sub2["Rely on the weakness described in OI-24"]
    OI24_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    OI24_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    OI24_leaf3["The weakness is present: Markdown or HTML produced by summarizer-llm contains remote images..."]
    OI24_leaf4["No effective control observed: Strip remote resources from the output of summarizer-llm before..."]

    OI24_root --> OI24_or1
    OI24_or1 --> OI24_sub1
    OI24_or1 --> OI24_sub2
    OI24_sub1 --> OI24_leaf1
    OI24_sub1 --> OI24_leaf2
    OI24_sub2 --> OI24_leaf3
    OI24_sub2 --> OI24_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI24_root goal
    class OI24_or1 orGate
    class OI24_sub1,OI24_sub2 subGoal
    class OI24_leaf1,OI24_leaf2,OI24_leaf3,OI24_leaf4 leaf
```
