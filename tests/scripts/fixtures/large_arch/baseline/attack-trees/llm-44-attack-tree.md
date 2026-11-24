# LLM-44: A user message crafted to look like a system directive persuades...

**Component**: eval-runner | **Risk Level**: Critical | **Finding**: LLM-44

A user message crafted to look like a system directive persuades eval-runner to disclose its configuration or ignore its rules.

```mermaid
flowchart TD
    LLM44_root["A user message crafted to look like a system directive persuades..."]
    LLM44_or1{{"OR"}}
    LLM44_sub1["Reach eval-runner in the Operations Zone"]
    LLM44_sub2["Rely on the weakness described in LLM-44"]
    LLM44_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    LLM44_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    LLM44_leaf3["The weakness is present: A user message crafted to look like a system directive persuades..."]
    LLM44_leaf4["No effective control observed: Keep the system guidance for eval-runner out of reach of user..."]

    LLM44_root --> LLM44_or1
    LLM44_or1 --> LLM44_sub1
    LLM44_or1 --> LLM44_sub2
    LLM44_sub1 --> LLM44_leaf1
    LLM44_sub1 --> LLM44_leaf2
    LLM44_sub2 --> LLM44_leaf3
    LLM44_sub2 --> LLM44_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM44_root goal
    class LLM44_or1 orGate
    class LLM44_sub1,LLM44_sub2 subGoal
    class LLM44_leaf1,LLM44_leaf2,LLM44_leaf3,LLM44_leaf4 leaf
```
