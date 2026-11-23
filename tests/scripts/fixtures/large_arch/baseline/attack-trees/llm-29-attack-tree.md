# LLM-29: Evaluation labels consumed from kb-index are produced by a judge...

**Component**: kb-index | **Risk Level**: Critical | **Finding**: LLM-29

Evaluation labels consumed from kb-index are produced by a judge model that can itself be influenced by planted traces.

```mermaid
flowchart TD
    LLM29_root["Evaluation labels consumed from kb-index are produced by a judge model..."]
    LLM29_or1{{"OR"}}
    LLM29_sub1["Reach kb-index in the Data Zone"]
    LLM29_sub2["Rely on the weakness described in LLM-29"]
    LLM29_leaf1["A path exists from s3-archive over HTTPS (TLS 1.3)"]
    LLM29_leaf2["Carrier tariffs and customs rules are accepted without an independent check"]
    LLM29_leaf3["The weakness is present: Evaluation labels consumed from kb-index are produced by a judge..."]
    LLM29_leaf4["No effective control observed: Calibrate the judge on a human-labelled subset from kb-index..."]

    LLM29_root --> LLM29_or1
    LLM29_or1 --> LLM29_sub1
    LLM29_or1 --> LLM29_sub2
    LLM29_sub1 --> LLM29_leaf1
    LLM29_sub1 --> LLM29_leaf2
    LLM29_sub2 --> LLM29_leaf3
    LLM29_sub2 --> LLM29_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM29_root goal
    class LLM29_or1 orGate
    class LLM29_sub1,LLM29_sub2 subGoal
    class LLM29_leaf1,LLM29_leaf2,LLM29_leaf3,LLM29_leaf4 leaf
```
