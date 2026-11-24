# LLM-54: Encoded or multilingual payloads bypass the keyword filter in...

**Component**: model-gateway | **Risk Level**: High | **Finding**: LLM-54

Encoded or multilingual payloads bypass the keyword filter in front of model-gateway, which only checks plain English text.

```mermaid
flowchart TD
    LLM54_root["Encoded or multilingual payloads bypass the keyword filter in front of..."]
    LLM54_or1{{"OR"}}
    LLM54_sub1["Reach model-gateway in the Agent Runtime Zone"]
    LLM54_sub2["Rely on the weakness described in LLM-54"]
    LLM54_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    LLM54_leaf2["Prompts and completions are accepted without an independent check"]
    LLM54_leaf3["The weakness is present: Encoded or multilingual payloads bypass the keyword filter in..."]
    LLM54_leaf4["No effective control observed: Normalise and decode inputs before filtering in model-gateway..."]

    LLM54_root --> LLM54_or1
    LLM54_or1 --> LLM54_sub1
    LLM54_or1 --> LLM54_sub2
    LLM54_sub1 --> LLM54_leaf1
    LLM54_sub1 --> LLM54_leaf2
    LLM54_sub2 --> LLM54_leaf3
    LLM54_sub2 --> LLM54_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM54_root goal
    class LLM54_or1 orGate
    class LLM54_sub1,LLM54_sub2 subGoal
    class LLM54_leaf1,LLM54_leaf2,LLM54_leaf3,LLM54_leaf4 leaf
```
