# E-3: planner-agent runs with broader permissions than its function...

**Component**: planner-agent | **Risk Level**: High | **Finding**: E-3

planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources.

```mermaid
flowchart TD
    E3_root["planner-agent runs with broader permissions than its function needs..."]
    E3_or1{{"OR"}}
    E3_sub1["Reach planner-agent in the Agent Runtime Zone"]
    E3_sub2["Rely on the weakness described in E-3"]
    E3_leaf1["A path exists from model-gateway over HTTPS (TLS 1.3)"]
    E3_leaf2["Task plans and tool selections are accepted without an independent check"]
    E3_leaf3["The weakness is present: planner-agent runs with broader permissions than its function..."]
    E3_leaf4["No effective control observed: Reduce the permissions of planner-agent to the minimum for task..."]

    E3_root --> E3_or1
    E3_or1 --> E3_sub1
    E3_or1 --> E3_sub2
    E3_sub1 --> E3_leaf1
    E3_sub1 --> E3_leaf2
    E3_sub2 --> E3_leaf3
    E3_sub2 --> E3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E3_root goal
    class E3_or1 orGate
    class E3_sub1,E3_sub2 subGoal
    class E3_leaf1,E3_leaf2,E3_leaf3,E3_leaf4 leaf
```
