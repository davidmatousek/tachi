# S-13: An unauthenticated callback or health route on worker-2 accepts...

**Component**: worker-2 | **Risk Level**: High | **Finding**: S-13

An unauthenticated callback or health route on worker-2 accepts requests that downstream code treats as if they had come from trace-collector.

```mermaid
flowchart TD
    S13_root["An unauthenticated callback or health route on worker-2 accepts..."]
    S13_or1{{"OR"}}
    S13_sub1["Reach worker-2 in the Agent Runtime Zone"]
    S13_sub2["Rely on the weakness described in S-13"]
    S13_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    S13_leaf2["Work orders and route candidates are accepted without an independent check"]
    S13_leaf3["The weakness is present: An unauthenticated callback or health route on worker-2 accepts..."]
    S13_leaf4["No effective control observed: Remove implicit trust in route names: authenticate every route of..."]

    S13_root --> S13_or1
    S13_or1 --> S13_sub1
    S13_or1 --> S13_sub2
    S13_sub1 --> S13_leaf1
    S13_sub1 --> S13_leaf2
    S13_sub2 --> S13_leaf3
    S13_sub2 --> S13_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S13_root goal
    class S13_or1 orGate
    class S13_sub1,S13_sub2 subGoal
    class S13_leaf1,S13_leaf2,S13_leaf3,S13_leaf4 leaf
```
