# OI-23: Structured output from summarizer-llm is trusted by...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: OI-23

Structured output from summarizer-llm is trusted by feature-store-2 as already validated, so a malformed field flows straight into business logic.

```mermaid
flowchart TD
    OI23_root["Structured output from summarizer-llm is trusted by feature-store-2 as..."]
    OI23_or1{{"OR"}}
    OI23_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    OI23_sub2["Rely on the weakness described in OI-23"]
    OI23_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    OI23_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    OI23_leaf3["The weakness is present: Structured output from summarizer-llm is trusted by..."]
    OI23_leaf4["No effective control observed: Validate the output of summarizer-llm against a strict schema in..."]

    OI23_root --> OI23_or1
    OI23_or1 --> OI23_sub1
    OI23_or1 --> OI23_sub2
    OI23_sub1 --> OI23_leaf1
    OI23_sub1 --> OI23_leaf2
    OI23_sub2 --> OI23_leaf3
    OI23_sub2 --> OI23_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI23_root goal
    class OI23_or1 orGate
    class OI23_sub1,OI23_sub2 subGoal
    class OI23_leaf1,OI23_leaf2,OI23_leaf3,OI23_leaf4 leaf
```
