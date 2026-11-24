# E-23: Object identifiers in requests to summarizer-llm are trusted...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: E-23

Object identifiers in requests to summarizer-llm are trusted without an ownership check, so a caller can read or change shipment records fed into summaries that belong to others.

```mermaid
flowchart TD
    E23_root["Object identifiers in requests to summarizer-llm are trusted without..."]
    E23_or1{{"OR"}}
    E23_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    E23_sub2["Rely on the weakness described in E-23"]
    E23_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    E23_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    E23_leaf3["The weakness is present: Object identifiers in requests to summarizer-llm are trusted..."]
    E23_leaf4["No effective control observed: Check ownership or entitlement for every object reference at..."]

    E23_root --> E23_or1
    E23_or1 --> E23_sub1
    E23_or1 --> E23_sub2
    E23_sub1 --> E23_leaf1
    E23_sub1 --> E23_leaf2
    E23_sub2 --> E23_leaf3
    E23_sub2 --> E23_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E23_root goal
    class E23_or1 orGate
    class E23_sub1,E23_sub2 subGoal
    class E23_leaf1,E23_leaf2,E23_leaf3,E23_leaf4 leaf
```
