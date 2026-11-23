# LLM-47: Anyone who can write to the ingestion path of eval-runner can slip...

**Component**: eval-runner | **Risk Level**: Critical | **Finding**: LLM-47

Anyone who can write to the ingestion path of eval-runner can slip in documents that contradict authoritative sources.

```mermaid
flowchart TD
    LLM47_root["Anyone who can write to the ingestion path of eval-runner can slip in..."]
    LLM47_or1{{"OR"}}
    LLM47_sub1["Reach eval-runner in the Operations Zone"]
    LLM47_sub2["Rely on the weakness described in LLM-47"]
    LLM47_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    LLM47_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    LLM47_leaf3["The weakness is present: Anyone who can write to the ingestion path of eval-runner can slip..."]
    LLM47_leaf4["No effective control observed: Restrict write access to the ingestion path of eval-runner, sign..."]

    LLM47_root --> LLM47_or1
    LLM47_or1 --> LLM47_sub1
    LLM47_or1 --> LLM47_sub2
    LLM47_sub1 --> LLM47_leaf1
    LLM47_sub1 --> LLM47_leaf2
    LLM47_sub2 --> LLM47_leaf3
    LLM47_sub2 --> LLM47_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM47_root goal
    class LLM47_or1 orGate
    class LLM47_sub1,LLM47_sub2 subGoal
    class LLM47_leaf1,LLM47_leaf2,LLM47_leaf3,LLM47_leaf4 leaf
```
