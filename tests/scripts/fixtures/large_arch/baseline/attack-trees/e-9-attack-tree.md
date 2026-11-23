# E-9: A confused-deputy path lets a low-privilege caller ask...

**Component**: planner-agent | **Risk Level**: High | **Finding**: E-9

A confused-deputy path lets a low-privilege caller ask planner-agent to act on task plans and tool selections using the privileges of model-gateway.

```mermaid
flowchart TD
    E9_root["A confused-deputy path lets a low-privilege caller ask planner-agent..."]
    E9_or1{{"OR"}}
    E9_sub1["Reach planner-agent in the Agent Runtime Zone"]
    E9_sub2["Rely on the weakness described in E-9"]
    E9_leaf1["A path exists from queue-a2 over NATS over TLS"]
    E9_leaf2["Task plans and tool selections are accepted without an independent check"]
    E9_leaf3["The weakness is present: A confused-deputy path lets a low-privilege caller ask..."]
    E9_leaf4["No effective control observed: Pass the caller's authority through to planner-agent and evaluate..."]

    E9_root --> E9_or1
    E9_or1 --> E9_sub1
    E9_or1 --> E9_sub2
    E9_sub1 --> E9_leaf1
    E9_sub1 --> E9_leaf2
    E9_sub2 --> E9_leaf3
    E9_sub2 --> E9_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E9_root goal
    class E9_or1 orGate
    class E9_sub1,E9_sub2 subGoal
    class E9_leaf1,E9_leaf2,E9_leaf3,E9_leaf4 leaf
```
