# LLM-40: Instructions hidden in prompts, completions and tool traces reach...

**Component**: trace-collector | **Risk Level**: Critical | **Finding**: LLM-40

Instructions hidden in prompts, completions and tool traces reach the prompt of trace-collector and override its system guidance, because content and instructions share one context.

```mermaid
flowchart TD
    LLM40_root["Instructions hidden in prompts, completions and tool traces reach the..."]
    LLM40_or1{{"OR"}}
    LLM40_sub1["Reach trace-collector in the Operations Zone"]
    LLM40_sub2["Rely on the weakness described in LLM-40"]
    LLM40_leaf1["A path exists from intake-agent over OTLP over TLS"]
    LLM40_leaf2["Prompts, completions and tool traces are accepted without an independent check"]
    LLM40_leaf3["The weakness is present: Instructions hidden in prompts, completions and tool traces reach..."]
    LLM40_leaf4["No effective control observed: Separate instructions from content in the prompts of..."]

    LLM40_root --> LLM40_or1
    LLM40_or1 --> LLM40_sub1
    LLM40_or1 --> LLM40_sub2
    LLM40_sub1 --> LLM40_leaf1
    LLM40_sub1 --> LLM40_leaf2
    LLM40_sub2 --> LLM40_leaf3
    LLM40_sub2 --> LLM40_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM40_root goal
    class LLM40_or1 orGate
    class LLM40_sub1,LLM40_sub2 subGoal
    class LLM40_leaf1,LLM40_leaf2,LLM40_leaf3,LLM40_leaf4 leaf
```
