# LLM-19: Indirect injection through documents retrieved for model-gateway...

**Component**: model-gateway | **Risk Level**: Critical | **Finding**: LLM-19

Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system.

```mermaid
flowchart TD
    LLM19_root["Indirect injection through documents retrieved for model-gateway lets..."]
    LLM19_or1{{"OR"}}
    LLM19_sub1["Reach model-gateway in the Agent Runtime Zone"]
    LLM19_sub2["Rely on the weakness described in LLM-19"]
    LLM19_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    LLM19_leaf2["Prompts and completions are accepted without an independent check"]
    LLM19_leaf3["The weakness is present: Indirect injection through documents retrieved for model-gateway..."]
    LLM19_leaf4["No effective control observed: Score retrieved passages for instruction-like content before..."]

    LLM19_root --> LLM19_or1
    LLM19_or1 --> LLM19_sub1
    LLM19_or1 --> LLM19_sub2
    LLM19_sub1 --> LLM19_leaf1
    LLM19_sub1 --> LLM19_leaf2
    LLM19_sub2 --> LLM19_leaf3
    LLM19_sub2 --> LLM19_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM19_root goal
    class LLM19_or1 orGate
    class LLM19_sub1,LLM19_sub2 subGoal
    class LLM19_leaf1,LLM19_leaf2,LLM19_leaf3,LLM19_leaf4 leaf
```
