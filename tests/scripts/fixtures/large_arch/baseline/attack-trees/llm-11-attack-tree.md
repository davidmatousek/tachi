# LLM-11: Prompt content logged by planner-agent is later replayed to...

**Component**: router-agent | **Risk Level**: Critical | **Finding**: LLM-11

Prompt content logged by planner-agent is later replayed to router-agent for evaluation, carrying planted instructions into a trusted context.

```mermaid
flowchart TD
    LLM11_root["Prompt content logged by planner-agent is later replayed to..."]
    LLM11_or1{{"OR"}}
    LLM11_sub1["Reach router-agent in the Agent Runtime Zone"]
    LLM11_sub2["Rely on the weakness described in LLM-11"]
    LLM11_leaf1["A path exists from planner-agent over HTTP/2 over mTLS"]
    LLM11_leaf2["Subtask assignments are accepted without an independent check"]
    LLM11_leaf3["The weakness is present: Prompt content logged by planner-agent is later replayed to..."]
    LLM11_leaf4["No effective control observed: Mark replayed prompts as untrusted when router-agent processes..."]

    LLM11_root --> LLM11_or1
    LLM11_or1 --> LLM11_sub1
    LLM11_or1 --> LLM11_sub2
    LLM11_sub1 --> LLM11_leaf1
    LLM11_sub1 --> LLM11_leaf2
    LLM11_sub2 --> LLM11_leaf3
    LLM11_sub2 --> LLM11_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM11_root goal
    class LLM11_or1 orGate
    class LLM11_sub1,LLM11_sub2 subGoal
    class LLM11_leaf1,LLM11_leaf2,LLM11_leaf3,LLM11_leaf4 leaf
```
