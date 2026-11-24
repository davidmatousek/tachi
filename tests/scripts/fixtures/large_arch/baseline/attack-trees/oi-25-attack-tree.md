# OI-25: File paths or names produced by summarizer-llm are used to write...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: OI-25

File paths or names produced by summarizer-llm are used to write files, letting crafted output reach locations outside the intended directory.

```mermaid
flowchart TD
    OI25_root["File paths or names produced by summarizer-llm are used to write..."]
    OI25_or1{{"OR"}}
    OI25_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    OI25_sub2["Rely on the weakness described in OI-25"]
    OI25_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    OI25_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    OI25_leaf3["The weakness is present: File paths or names produced by summarizer-llm are used to write..."]
    OI25_leaf4["No effective control observed: Generate file names for summarizer-llm on the server, confine..."]

    OI25_root --> OI25_or1
    OI25_or1 --> OI25_sub1
    OI25_or1 --> OI25_sub2
    OI25_sub1 --> OI25_leaf1
    OI25_sub1 --> OI25_leaf2
    OI25_sub2 --> OI25_leaf3
    OI25_sub2 --> OI25_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI25_root goal
    class OI25_or1 orGate
    class OI25_sub1,OI25_sub2 subGoal
    class OI25_leaf1,OI25_leaf2,OI25_leaf3,OI25_leaf4 leaf
```
