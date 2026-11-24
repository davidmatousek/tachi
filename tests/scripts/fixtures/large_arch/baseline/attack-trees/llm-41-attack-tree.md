# LLM-41: A user message crafted to look like a system directive persuades...

**Component**: trace-collector | **Risk Level**: High | **Finding**: LLM-41

A user message crafted to look like a system directive persuades trace-collector to disclose its configuration or ignore its rules.

```mermaid
flowchart TD
    LLM41_root["A user message crafted to look like a system directive persuades..."]
    LLM41_or1{{"OR"}}
    LLM41_sub1["Reach trace-collector in the Operations Zone"]
    LLM41_sub2["Rely on the weakness described in LLM-41"]
    LLM41_leaf1["A path exists from intake-agent over OTLP over TLS"]
    LLM41_leaf2["Prompts, completions and tool traces are accepted without an independent check"]
    LLM41_leaf3["The weakness is present: A user message crafted to look like a system directive persuades..."]
    LLM41_leaf4["No effective control observed: Keep the system guidance for trace-collector out of reach of user..."]

    LLM41_root --> LLM41_or1
    LLM41_or1 --> LLM41_sub1
    LLM41_or1 --> LLM41_sub2
    LLM41_sub1 --> LLM41_leaf1
    LLM41_sub1 --> LLM41_leaf2
    LLM41_sub2 --> LLM41_leaf3
    LLM41_sub2 --> LLM41_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM41_root goal
    class LLM41_or1 orGate
    class LLM41_sub1,LLM41_sub2 subGoal
    class LLM41_leaf1,LLM41_leaf2,LLM41_leaf3,LLM41_leaf4 leaf
```
