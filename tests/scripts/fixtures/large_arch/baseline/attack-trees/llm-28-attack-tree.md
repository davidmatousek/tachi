# LLM-28: Model weights or adapters served by summarizer-llm are readable by...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: LLM-28

Model weights or adapters served by summarizer-llm are readable by operators and by any process sharing the host.

```mermaid
flowchart TD
    LLM28_root["Model weights or adapters served by summarizer-llm are readable by..."]
    LLM28_or1{{"OR"}}
    LLM28_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM28_sub2["Rely on the weakness described in LLM-28"]
    LLM28_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM28_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM28_leaf3["The weakness is present: Model weights or adapters served by summarizer-llm are readable by..."]
    LLM28_leaf4["No effective control observed: Store the weights for summarizer-llm encrypted with keys in a..."]

    LLM28_root --> LLM28_or1
    LLM28_or1 --> LLM28_sub1
    LLM28_or1 --> LLM28_sub2
    LLM28_sub1 --> LLM28_leaf1
    LLM28_sub1 --> LLM28_leaf2
    LLM28_sub2 --> LLM28_leaf3
    LLM28_sub2 --> LLM28_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM28_root goal
    class LLM28_or1 orGate
    class LLM28_sub1,LLM28_sub2 subGoal
    class LLM28_leaf1,LLM28_leaf2,LLM28_leaf3,LLM28_leaf4 leaf
```
