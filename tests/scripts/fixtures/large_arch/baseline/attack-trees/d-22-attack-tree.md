# D-22: A single oversized or deeply nested payload makes summarizer-llm...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: D-22

A single oversized or deeply nested payload makes summarizer-llm spend disproportionate memory and CPU parsing shipment records fed into summaries.

```mermaid
flowchart TD
    D22_root["A single oversized or deeply nested payload makes summarizer-llm spend..."]
    D22_or1{{"OR"}}
    D22_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    D22_sub2["Rely on the weakness described in D-22"]
    D22_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    D22_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    D22_leaf3["The weakness is present: A single oversized or deeply nested payload makes summarizer-llm..."]
    D22_leaf4["No effective control observed: Cap payload size, nesting depth and parse time in summarizer-llm..."]

    D22_root --> D22_or1
    D22_or1 --> D22_sub1
    D22_or1 --> D22_sub2
    D22_sub1 --> D22_leaf1
    D22_sub1 --> D22_leaf2
    D22_sub2 --> D22_leaf3
    D22_sub2 --> D22_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D22_root goal
    class D22_or1 orGate
    class D22_sub1,D22_sub2 subGoal
    class D22_leaf1,D22_leaf2,D22_leaf3,D22_leaf4 leaf
```
