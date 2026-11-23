# D-8: Expensive queries over task plans and tool selections can be...

**Component**: planner-agent | **Risk Level**: Critical | **Finding**: D-8

Expensive queries over task plans and tool selections can be triggered by any authorised caller of planner-agent, so one user can degrade the service for all.

```mermaid
flowchart TD
    D8_root["Expensive queries over task plans and tool selections can be triggered..."]
    D8_or1{{"OR"}}
    D8_sub1["Reach planner-agent in the Agent Runtime Zone"]
    D8_sub2["Rely on the weakness described in D-8"]
    D8_leaf1["A path exists from queue-a2 over NATS over TLS"]
    D8_leaf2["Task plans and tool selections are accepted without an independent check"]
    D8_leaf3["The weakness is present: Expensive queries over task plans and tool selections can be..."]
    D8_leaf4["No effective control observed: Enforce cost limits and pagination on queries to planner-agent..."]

    D8_root --> D8_or1
    D8_or1 --> D8_sub1
    D8_or1 --> D8_sub2
    D8_sub1 --> D8_leaf1
    D8_sub1 --> D8_leaf2
    D8_sub2 --> D8_leaf3
    D8_sub2 --> D8_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D8_root goal
    class D8_or1 orGate
    class D8_sub1,D8_sub2 subGoal
    class D8_leaf1,D8_leaf2,D8_leaf3,D8_leaf4 leaf
```
