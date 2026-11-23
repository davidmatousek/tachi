# TE-13: summarizer-llm speaks with an authoritative tone about customs and...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: TE-13

summarizer-llm speaks with an authoritative tone about customs and legal matters, and operators may defer to it without checking.

```mermaid
flowchart TD
    TE13_root["summarizer-llm speaks with an authoritative tone about customs and..."]
    TE13_or1{{"OR"}}
    TE13_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    TE13_sub2["Rely on the weakness described in TE-13"]
    TE13_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    TE13_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    TE13_leaf3["The weakness is present: summarizer-llm speaks with an authoritative tone about customs and..."]
    TE13_leaf4["No effective control observed: Label the output of summarizer-llm as machine generated, state its..."]

    TE13_root --> TE13_or1
    TE13_or1 --> TE13_sub1
    TE13_or1 --> TE13_sub2
    TE13_sub1 --> TE13_leaf1
    TE13_sub1 --> TE13_leaf2
    TE13_sub2 --> TE13_leaf3
    TE13_sub2 --> TE13_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class TE13_root goal
    class TE13_or1 orGate
    class TE13_sub1,TE13_sub2 subGoal
    class TE13_leaf1,TE13_leaf2,TE13_leaf3,TE13_leaf4 leaf
```
