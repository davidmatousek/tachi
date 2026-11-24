# LLM-39: Fine-tuning data assembled from feature-store-2 is not checked for...

**Component**: feature-store-2 | **Risk Level**: High | **Finding**: LLM-39

Fine-tuning data assembled from feature-store-2 is not checked for outliers or duplicates, so a small batch of crafted examples changes model behaviour.

```mermaid
flowchart TD
    LLM39_root["Fine-tuning data assembled from feature-store-2 is not checked for..."]
    LLM39_or1{{"OR"}}
    LLM39_sub1["Reach feature-store-2 in the Data Zone"]
    LLM39_sub2["Rely on the weakness described in LLM-39"]
    LLM39_leaf1["A path exists from eval-runner over PostgreSQL over TLS"]
    LLM39_leaf2["Ranking and fine-tuning features are accepted without an independent check"]
    LLM39_leaf3["The weakness is present: Fine-tuning data assembled from feature-store-2 is not checked for..."]
    LLM39_leaf4["No effective control observed: Screen training data from feature-store-2 for duplicates, outliers..."]

    LLM39_root --> LLM39_or1
    LLM39_or1 --> LLM39_sub1
    LLM39_or1 --> LLM39_sub2
    LLM39_sub1 --> LLM39_leaf1
    LLM39_sub1 --> LLM39_leaf2
    LLM39_sub2 --> LLM39_leaf3
    LLM39_sub2 --> LLM39_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM39_root goal
    class LLM39_or1 orGate
    class LLM39_sub1,LLM39_sub2 subGoal
    class LLM39_leaf1,LLM39_leaf2,LLM39_leaf3,LLM39_leaf4 leaf
```
