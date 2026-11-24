# LLM-23: Systematic queries against embed-service-2 let an attacker...

**Component**: embed-service-2 | **Risk Level**: Critical | **Finding**: LLM-23

Systematic queries against embed-service-2 let an attacker approximate the behaviour of the model and train a copy.

```mermaid
flowchart TD
    LLM23_root["Systematic queries against embed-service-2 let an attacker approximate..."]
    LLM23_or1{{"OR"}}
    LLM23_sub1["Reach embed-service-2 in the Agent Runtime Zone"]
    LLM23_sub2["Rely on the weakness described in LLM-23"]
    LLM23_leaf1["A path exists from intake-agent over gRPC over mTLS"]
    LLM23_leaf2["Document chunks and query embeddings are accepted without an independent check"]
    LLM23_leaf3["The weakness is present: Systematic queries against embed-service-2 let an attacker..."]
    LLM23_leaf4["No effective control observed: Rate-limit and profile query patterns against embed-service-2, add..."]

    LLM23_root --> LLM23_or1
    LLM23_or1 --> LLM23_sub1
    LLM23_or1 --> LLM23_sub2
    LLM23_sub1 --> LLM23_leaf1
    LLM23_sub1 --> LLM23_leaf2
    LLM23_sub2 --> LLM23_leaf3
    LLM23_sub2 --> LLM23_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM23_root goal
    class LLM23_or1 orGate
    class LLM23_sub1,LLM23_sub2 subGoal
    class LLM23_leaf1,LLM23_leaf2,LLM23_leaf3,LLM23_leaf4 leaf
```
