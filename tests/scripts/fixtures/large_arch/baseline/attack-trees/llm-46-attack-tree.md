# LLM-46: Embeddings stored by eval-runner can be crowded with...

**Component**: eval-runner | **Risk Level**: Critical | **Finding**: LLM-46

Embeddings stored by eval-runner can be crowded with near-duplicate vectors that win similarity searches for chosen queries.

```mermaid
flowchart TD
    LLM46_root["Embeddings stored by eval-runner can be crowded with near-duplicate..."]
    LLM46_or1{{"OR"}}
    LLM46_sub1["Reach eval-runner in the Operations Zone"]
    LLM46_sub2["Rely on the weakness described in LLM-46"]
    LLM46_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    LLM46_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    LLM46_leaf3["The weakness is present: Embeddings stored by eval-runner can be crowded with..."]
    LLM46_leaf4["No effective control observed: Limit how many near-duplicate vectors one source can add to..."]

    LLM46_root --> LLM46_or1
    LLM46_or1 --> LLM46_sub1
    LLM46_or1 --> LLM46_sub2
    LLM46_sub1 --> LLM46_leaf1
    LLM46_sub1 --> LLM46_leaf2
    LLM46_sub2 --> LLM46_leaf3
    LLM46_sub2 --> LLM46_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM46_root goal
    class LLM46_or1 orGate
    class LLM46_sub1,LLM46_sub2 subGoal
    class LLM46_leaf1,LLM46_leaf2,LLM46_leaf3,LLM46_leaf4 leaf
```
