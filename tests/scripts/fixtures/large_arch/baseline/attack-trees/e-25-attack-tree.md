# E-25: An administrative interface of summarizer-llm is reachable from...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: E-25

An administrative interface of summarizer-llm is reachable from the same network as ordinary callers and relies on a single shared password.

```mermaid
flowchart TD
    E25_root["An administrative interface of summarizer-llm is reachable from the..."]
    E25_or1{{"OR"}}
    E25_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    E25_sub2["Rely on the weakness described in E-25"]
    E25_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    E25_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    E25_leaf3["The weakness is present: An administrative interface of summarizer-llm is reachable from..."]
    E25_leaf4["No effective control observed: Move the administrative interface of summarizer-llm behind a..."]

    E25_root --> E25_or1
    E25_or1 --> E25_sub1
    E25_or1 --> E25_sub2
    E25_sub1 --> E25_leaf1
    E25_sub1 --> E25_leaf2
    E25_sub2 --> E25_leaf3
    E25_sub2 --> E25_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E25_root goal
    class E25_or1 orGate
    class E25_sub1,E25_sub2 subGoal
    class E25_leaf1,E25_leaf2,E25_leaf3,E25_leaf4 leaf
```
