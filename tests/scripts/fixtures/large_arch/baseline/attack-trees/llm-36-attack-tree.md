# LLM-36: Fine-tuning data assembled from memory-store is not checked for...

**Component**: memory-store | **Risk Level**: High | **Finding**: LLM-36

Fine-tuning data assembled from memory-store is not checked for outliers or duplicates, so a small batch of crafted examples changes model behaviour.

```mermaid
flowchart TD
    LLM36_root["Fine-tuning data assembled from memory-store is not checked for..."]
    LLM36_or1{{"OR"}}
    LLM36_sub1["Reach memory-store in the Data Zone"]
    LLM36_sub2["Rely on the weakness described in LLM-36"]
    LLM36_leaf1["A path exists from planner-agent over PostgreSQL over TLS"]
    LLM36_leaf2["Task history and operator preferences are accepted without an independent check"]
    LLM36_leaf3["The weakness is present: Fine-tuning data assembled from memory-store is not checked for..."]
    LLM36_leaf4["No effective control observed: Screen training data from memory-store for duplicates, outliers..."]

    LLM36_root --> LLM36_or1
    LLM36_or1 --> LLM36_sub1
    LLM36_or1 --> LLM36_sub2
    LLM36_sub1 --> LLM36_leaf1
    LLM36_sub1 --> LLM36_leaf2
    LLM36_sub2 --> LLM36_leaf3
    LLM36_sub2 --> LLM36_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM36_root goal
    class LLM36_or1 orGate
    class LLM36_sub1,LLM36_sub2 subGoal
    class LLM36_leaf1,LLM36_leaf2,LLM36_leaf3,LLM36_leaf4 leaf
```
