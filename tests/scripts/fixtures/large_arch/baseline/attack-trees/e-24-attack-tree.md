# E-24: Role claims carried in the inference credential presented to...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: E-24

Role claims carried in the inference credential presented to summarizer-llm are honoured without confirmation against the authoritative directory.

```mermaid
flowchart TD
    E24_root["Role claims carried in the inference credential presented to..."]
    E24_or1{{"OR"}}
    E24_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    E24_sub2["Rely on the weakness described in E-24"]
    E24_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    E24_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    E24_leaf3["The weakness is present: Role claims carried in the inference credential presented to..."]
    E24_leaf4["No effective control observed: Resolve roles for summarizer-llm from the authoritative directory..."]

    E24_root --> E24_or1
    E24_or1 --> E24_sub1
    E24_or1 --> E24_sub2
    E24_sub1 --> E24_leaf1
    E24_sub1 --> E24_leaf2
    E24_sub2 --> E24_leaf3
    E24_sub2 --> E24_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E24_root goal
    class E24_or1 orGate
    class E24_sub1,E24_sub2 subGoal
    class E24_leaf1,E24_leaf2,E24_leaf3,E24_leaf4 leaf
```
