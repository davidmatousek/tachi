# LLM-57: Instructions hidden in shipment records fed into summaries reach...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: LLM-57

Instructions hidden in shipment records fed into summaries reach the prompt of summarizer-llm and override its system guidance, because content and instructions share one context.

```mermaid
flowchart TD
    LLM57_root["Instructions hidden in shipment records fed into summaries reach the..."]
    LLM57_or1{{"OR"}}
    LLM57_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM57_sub2["Rely on the weakness described in LLM-57"]
    LLM57_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM57_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM57_leaf3["The weakness is present: Instructions hidden in shipment records fed into summaries reach..."]
    LLM57_leaf4["No effective control observed: Separate instructions from content in the prompts of..."]

    LLM57_root --> LLM57_or1
    LLM57_or1 --> LLM57_sub1
    LLM57_or1 --> LLM57_sub2
    LLM57_sub1 --> LLM57_leaf1
    LLM57_sub1 --> LLM57_leaf2
    LLM57_sub2 --> LLM57_leaf3
    LLM57_sub2 --> LLM57_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM57_root goal
    class LLM57_or1 orGate
    class LLM57_sub1,LLM57_sub2 subGoal
    class LLM57_leaf1,LLM57_leaf2,LLM57_leaf3,LLM57_leaf4 leaf
```
