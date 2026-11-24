# LLM-14: An attacker splits a payload across several messages so that no...

**Component**: worker-3 | **Risk Level**: High | **Finding**: LLM-14

An attacker splits a payload across several messages so that no single message trips the filter in front of worker-3.

```mermaid
flowchart TD
    LLM14_root["An attacker splits a payload across several messages so that no single..."]
    LLM14_or1{{"OR"}}
    LLM14_sub1["Reach worker-3 in the Agent Runtime Zone"]
    LLM14_sub2["Rely on the weakness described in LLM-14"]
    LLM14_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    LLM14_leaf2["Work orders and draft documents are accepted without an independent check"]
    LLM14_leaf3["The weakness is present: An attacker splits a payload across several messages so that no..."]
    LLM14_leaf4["No effective control observed: Evaluate the accumulated conversation in worker-3 as a whole..."]

    LLM14_root --> LLM14_or1
    LLM14_or1 --> LLM14_sub1
    LLM14_or1 --> LLM14_sub2
    LLM14_sub1 --> LLM14_leaf1
    LLM14_sub1 --> LLM14_leaf2
    LLM14_sub2 --> LLM14_leaf3
    LLM14_sub2 --> LLM14_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM14_root goal
    class LLM14_or1 orGate
    class LLM14_sub1,LLM14_sub2 subGoal
    class LLM14_leaf1,LLM14_leaf2,LLM14_leaf3,LLM14_leaf4 leaf
```
