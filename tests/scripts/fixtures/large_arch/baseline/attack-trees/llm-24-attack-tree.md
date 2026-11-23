# LLM-24: summarizer-llm follows links and files named in shipment records...

**Component**: summarizer-llm | **Risk Level**: Critical | **Finding**: LLM-24

summarizer-llm follows links and files named in shipment records fed into summaries, which turns a harmless-looking request into a fetch of attacker-controlled content.

```mermaid
flowchart TD
    LLM24_root["summarizer-llm follows links and files named in shipment records fed..."]
    LLM24_or1{{"OR"}}
    LLM24_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    LLM24_sub2["Rely on the weakness described in LLM-24"]
    LLM24_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    LLM24_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    LLM24_leaf3["The weakness is present: summarizer-llm follows links and files named in shipment records..."]
    LLM24_leaf4["No effective control observed: Restrict what summarizer-llm may fetch to an allowlist of domains..."]

    LLM24_root --> LLM24_or1
    LLM24_or1 --> LLM24_sub1
    LLM24_or1 --> LLM24_sub2
    LLM24_sub1 --> LLM24_leaf1
    LLM24_sub1 --> LLM24_leaf2
    LLM24_sub2 --> LLM24_leaf3
    LLM24_sub2 --> LLM24_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM24_root goal
    class LLM24_or1 orGate
    class LLM24_sub1,LLM24_sub2 subGoal
    class LLM24_leaf1,LLM24_leaf2,LLM24_leaf3,LLM24_leaf4 leaf
```
