# LLM-25: Embeddings stored by summarizer-llm can be crowded with...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: LLM-25

Embeddings stored by summarizer-llm can be crowded with near-duplicate vectors that win similarity searches for chosen queries.

```mermaid
flowchart TD
    LLM25_root["Embeddings stored by summarizer-llm can be crowded with near-duplicate..."]
    LLM25_or1{{"OR"}}
    LLM25_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM25_sub2["Rely on the weakness described in LLM-25"]
    LLM25_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM25_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM25_leaf3["The weakness is present: Embeddings stored by summarizer-llm can be crowded with..."]
    LLM25_leaf4["No effective control observed: Limit how many near-duplicate vectors one source can add to..."]

    LLM25_root --> LLM25_or1
    LLM25_or1 --> LLM25_sub1
    LLM25_or1 --> LLM25_sub2
    LLM25_sub1 --> LLM25_leaf1
    LLM25_sub1 --> LLM25_leaf2
    LLM25_sub2 --> LLM25_leaf3
    LLM25_sub2 --> LLM25_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM25_root goal
    class LLM25_or1 orGate
    class LLM25_sub1,LLM25_sub2 subGoal
    class LLM25_leaf1,LLM25_leaf2,LLM25_leaf3,LLM25_leaf4 leaf
```
