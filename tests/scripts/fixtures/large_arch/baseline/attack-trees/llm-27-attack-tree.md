# LLM-27: Evaluation labels consumed from summarizer-llm are produced by a...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: LLM-27

Evaluation labels consumed from summarizer-llm are produced by a judge model that can itself be influenced by planted traces.

```mermaid
flowchart TD
    LLM27_root["Evaluation labels consumed from summarizer-llm are produced by a judge..."]
    LLM27_or1{{"OR"}}
    LLM27_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM27_sub2["Rely on the weakness described in LLM-27"]
    LLM27_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM27_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM27_leaf3["The weakness is present: Evaluation labels consumed from summarizer-llm are produced by a..."]
    LLM27_leaf4["No effective control observed: Calibrate the judge on a human-labelled subset from..."]

    LLM27_root --> LLM27_or1
    LLM27_or1 --> LLM27_sub1
    LLM27_or1 --> LLM27_sub2
    LLM27_sub1 --> LLM27_leaf1
    LLM27_sub1 --> LLM27_leaf2
    LLM27_sub2 --> LLM27_leaf3
    LLM27_sub2 --> LLM27_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM27_root goal
    class LLM27_or1 orGate
    class LLM27_sub1,LLM27_sub2 subGoal
    class LLM27_leaf1,LLM27_leaf2,LLM27_leaf3,LLM27_leaf4 leaf
```
