# LLM-38: Records written into s3-archive by low-trust sources are later...

**Component**: s3-archive | **Risk Level**: Critical | **Finding**: LLM-38

Records written into s3-archive by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.

```mermaid
flowchart TD
    LLM38_root["Records written into s3-archive by low-trust sources are later used as..."]
    LLM38_or1{{"OR"}}
    LLM38_sub1["Reach s3-archive in the Data Zone"]
    LLM38_sub2["Rely on the weakness described in LLM-38"]
    LLM38_leaf1["A path exists from trace-collector over HTTPS (TLS 1.3)"]
    LLM38_leaf2["Archived transcripts and training corpora are accepted without an independent check"]
    LLM38_leaf3["The weakness is present: Records written into s3-archive by low-trust sources are later..."]
    LLM38_leaf4["No effective control observed: Record provenance for every entry in s3-archive, require review..."]

    LLM38_root --> LLM38_or1
    LLM38_or1 --> LLM38_sub1
    LLM38_or1 --> LLM38_sub2
    LLM38_sub1 --> LLM38_leaf1
    LLM38_sub1 --> LLM38_leaf2
    LLM38_sub2 --> LLM38_leaf3
    LLM38_sub2 --> LLM38_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM38_root goal
    class LLM38_or1 orGate
    class LLM38_sub1,LLM38_sub2 subGoal
    class LLM38_leaf1,LLM38_leaf2,LLM38_leaf3,LLM38_leaf4 leaf
```
