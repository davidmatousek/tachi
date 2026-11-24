# LLM-53: Instructions hidden in guardrail rules and approval decisions...

**Component**: policy-engine | **Risk Level**: High | **Finding**: LLM-53

Instructions hidden in guardrail rules and approval decisions reach the prompt of policy-engine and override its system guidance, because content and instructions share one context.

```mermaid
flowchart TD
    LLM53_root["Instructions hidden in guardrail rules and approval decisions reach..."]
    LLM53_or1{{"OR"}}
    LLM53_sub1["Reach policy-engine in the Operations Zone"]
    LLM53_sub2["Rely on the weakness described in LLM-53"]
    LLM53_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    LLM53_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    LLM53_leaf3["The weakness is present: Instructions hidden in guardrail rules and approval decisions..."]
    LLM53_leaf4["No effective control observed: Separate instructions from content in the prompts of..."]

    LLM53_root --> LLM53_or1
    LLM53_or1 --> LLM53_sub1
    LLM53_or1 --> LLM53_sub2
    LLM53_sub1 --> LLM53_leaf1
    LLM53_sub1 --> LLM53_leaf2
    LLM53_sub2 --> LLM53_leaf3
    LLM53_sub2 --> LLM53_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM53_root goal
    class LLM53_or1 orGate
    class LLM53_sub1,LLM53_sub2 subGoal
    class LLM53_leaf1,LLM53_leaf2,LLM53_leaf3,LLM53_leaf4 leaf
```
