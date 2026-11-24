# LLM-56: Model weights or adapters served by embed-service-2 are readable...

**Component**: embed-service-2 | **Risk Level**: Critical | **Finding**: LLM-56

Model weights or adapters served by embed-service-2 are readable by operators and by any process sharing the host.

```mermaid
flowchart TD
    LLM56_root["Model weights or adapters served by embed-service-2 are readable by..."]
    LLM56_or1{{"OR"}}
    LLM56_sub1["Reach embed-service-2 in the Agent Runtime Zone"]
    LLM56_sub2["Rely on the weakness described in LLM-56"]
    LLM56_leaf1["A path exists from intake-agent over gRPC over mTLS"]
    LLM56_leaf2["Document chunks and query embeddings are accepted without an independent check"]
    LLM56_leaf3["The weakness is present: Model weights or adapters served by embed-service-2 are readable..."]
    LLM56_leaf4["No effective control observed: Store the weights for embed-service-2 encrypted with keys in a..."]

    LLM56_root --> LLM56_or1
    LLM56_or1 --> LLM56_sub1
    LLM56_or1 --> LLM56_sub2
    LLM56_sub1 --> LLM56_leaf1
    LLM56_sub1 --> LLM56_leaf2
    LLM56_sub2 --> LLM56_leaf3
    LLM56_sub2 --> LLM56_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM56_root goal
    class LLM56_or1 orGate
    class LLM56_sub1,LLM56_sub2 subGoal
    class LLM56_leaf1,LLM56_leaf2,LLM56_leaf3,LLM56_leaf4 leaf
```
