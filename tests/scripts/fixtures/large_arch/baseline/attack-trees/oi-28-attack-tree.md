# OI-28: Model output from summarizer-llm is inserted into a rendered page...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: OI-28

Model output from summarizer-llm is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.

```mermaid
flowchart TD
    OI28_root["Model output from summarizer-llm is inserted into a rendered page..."]
    OI28_or1{{"OR"}}
    OI28_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    OI28_sub2["Rely on the weakness described in OI-28"]
    OI28_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    OI28_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    OI28_leaf3["The weakness is present: Model output from summarizer-llm is inserted into a rendered page..."]
    OI28_leaf4["No effective control observed: Encode model output from summarizer-llm for its destination..."]

    OI28_root --> OI28_or1
    OI28_or1 --> OI28_sub1
    OI28_or1 --> OI28_sub2
    OI28_sub1 --> OI28_leaf1
    OI28_sub1 --> OI28_leaf2
    OI28_sub2 --> OI28_leaf3
    OI28_sub2 --> OI28_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI28_root goal
    class OI28_or1 orGate
    class OI28_sub1,OI28_sub2 subGoal
    class OI28_leaf1,OI28_leaf2,OI28_leaf3,OI28_leaf4 leaf
```
