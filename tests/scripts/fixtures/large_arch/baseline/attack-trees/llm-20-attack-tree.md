# LLM-20: Model weights or adapters served by model-gateway are readable by...

**Component**: model-gateway | **Risk Level**: Critical | **Finding**: LLM-20

Model weights or adapters served by model-gateway are readable by operators and by any process sharing the host.

```mermaid
flowchart TD
    LLM20_root["Model weights or adapters served by model-gateway are readable by..."]
    LLM20_or1{{"OR"}}
    LLM20_sub1["Reach model-gateway in the Agent Runtime Zone"]
    LLM20_sub2["Rely on the weakness described in LLM-20"]
    LLM20_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    LLM20_leaf2["Prompts and completions are accepted without an independent check"]
    LLM20_leaf3["The weakness is present: Model weights or adapters served by model-gateway are readable by..."]
    LLM20_leaf4["No effective control observed: Store the weights for model-gateway encrypted with keys in a..."]

    LLM20_root --> LLM20_or1
    LLM20_or1 --> LLM20_sub1
    LLM20_or1 --> LLM20_sub2
    LLM20_sub1 --> LLM20_leaf1
    LLM20_sub1 --> LLM20_leaf2
    LLM20_sub2 --> LLM20_leaf3
    LLM20_sub2 --> LLM20_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM20_root goal
    class LLM20_or1 orGate
    class LLM20_sub1,LLM20_sub2 subGoal
    class LLM20_leaf1,LLM20_leaf2,LLM20_leaf3,LLM20_leaf4 leaf
```
