# LLM-26: Anyone who can write to the ingestion path of summarizer-llm can...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: LLM-26

Anyone who can write to the ingestion path of summarizer-llm can slip in documents that contradict authoritative sources.

```mermaid
flowchart TD
    LLM26_root["Anyone who can write to the ingestion path of summarizer-llm can slip..."]
    LLM26_or1{{"OR"}}
    LLM26_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM26_sub2["Rely on the weakness described in LLM-26"]
    LLM26_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM26_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM26_leaf3["The weakness is present: Anyone who can write to the ingestion path of summarizer-llm can..."]
    LLM26_leaf4["No effective control observed: Restrict write access to the ingestion path of summarizer-llm..."]

    LLM26_root --> LLM26_or1
    LLM26_or1 --> LLM26_sub1
    LLM26_or1 --> LLM26_sub2
    LLM26_sub1 --> LLM26_leaf1
    LLM26_sub1 --> LLM26_leaf2
    LLM26_sub2 --> LLM26_leaf3
    LLM26_sub2 --> LLM26_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM26_root goal
    class LLM26_or1 orGate
    class LLM26_sub1,LLM26_sub2 subGoal
    class LLM26_leaf1,LLM26_leaf2,LLM26_leaf3,LLM26_leaf4 leaf
```
