# S-8: An unauthenticated callback or health route on planner-agent...

**Component**: planner-agent | **Risk Level**: Critical | **Finding**: S-8

An unauthenticated callback or health route on planner-agent accepts requests that downstream code treats as if they had come from trace-collector.

```mermaid
flowchart TD
    S8_root["An unauthenticated callback or health route on planner-agent accepts..."]
    S8_or1{{"OR"}}
    S8_sub1["Reach planner-agent in the Agent Runtime Zone"]
    S8_sub2["Rely on the weakness described in S-8"]
    S8_leaf1["A path exists from queue-a2 over NATS over TLS"]
    S8_leaf2["Task plans and tool selections are accepted without an independent check"]
    S8_leaf3["The weakness is present: An unauthenticated callback or health route on planner-agent..."]
    S8_leaf4["No effective control observed: Remove implicit trust in route names: authenticate every route of..."]

    S8_root --> S8_or1
    S8_or1 --> S8_sub1
    S8_or1 --> S8_sub2
    S8_sub1 --> S8_leaf1
    S8_sub1 --> S8_leaf2
    S8_sub2 --> S8_leaf3
    S8_sub2 --> S8_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S8_root goal
    class S8_or1 orGate
    class S8_sub1,S8_sub2 subGoal
    class S8_leaf1,S8_leaf2,S8_leaf3,S8_leaf4 leaf
```
