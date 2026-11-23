# LLM-58: A user message crafted to look like a system directive persuades...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: LLM-58

A user message crafted to look like a system directive persuades summarizer-llm to disclose its configuration or ignore its rules.

```mermaid
flowchart TD
    LLM58_root["A user message crafted to look like a system directive persuades..."]
    LLM58_or1{{"OR"}}
    LLM58_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM58_sub2["Rely on the weakness described in LLM-58"]
    LLM58_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM58_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM58_leaf3["The weakness is present: A user message crafted to look like a system directive persuades..."]
    LLM58_leaf4["No effective control observed: Keep the system guidance for summarizer-llm out of reach of user..."]

    LLM58_root --> LLM58_or1
    LLM58_or1 --> LLM58_sub1
    LLM58_or1 --> LLM58_sub2
    LLM58_sub1 --> LLM58_leaf1
    LLM58_sub1 --> LLM58_leaf2
    LLM58_sub2 --> LLM58_leaf3
    LLM58_sub2 --> LLM58_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM58_root goal
    class LLM58_or1 orGate
    class LLM58_sub1,LLM58_sub2 subGoal
    class LLM58_leaf1,LLM58_leaf2,LLM58_leaf3,LLM58_leaf4 leaf
```
