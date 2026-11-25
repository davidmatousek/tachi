# LLM-5: Indirect injection through documents retrieved for model-gateway...

Carried from the baseline run.

**Component**: model-gateway | **Risk Level**: High | **Finding**: LLM-5

Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system.

```mermaid
flowchart TD
    LLM5_root["Indirect injection through documents retrieved for model-gateway lets..."]
    LLM5_or1{{"OR"}}
    LLM5_sub1["Reach model-gateway in the Agent Runtime Zone"]
    LLM5_sub2["Rely on the weakness described in LLM-5"]
    LLM5_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    LLM5_leaf2["Prompts and completions are accepted without an independent check"]
    LLM5_leaf3["The weakness is present: Indirect injection through documents retrieved for model-gateway..."]
    LLM5_leaf4["No effective control observed: Score retrieved passages for instruction-like content before..."]

    LLM5_root --> LLM5_or1
    LLM5_or1 --> LLM5_sub1
    LLM5_or1 --> LLM5_sub2
    LLM5_sub1 --> LLM5_leaf1
    LLM5_sub1 --> LLM5_leaf2
    LLM5_sub2 --> LLM5_leaf3
    LLM5_sub2 --> LLM5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM5_root goal
    class LLM5_or1 orGate
    class LLM5_sub1,LLM5_sub2 subGoal
    class LLM5_leaf1,LLM5_leaf2,LLM5_leaf3,LLM5_leaf4 leaf
```
