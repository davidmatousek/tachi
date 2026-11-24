# AG-5: Delegation from trace-collector to planner-agent carries the full...

**Component**: planner-agent | **Risk Level**: High | **Finding**: AG-5

Delegation from trace-collector to planner-agent carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.

```mermaid
flowchart TD
    AG5_root["Delegation from trace-collector to planner-agent carries the full..."]
    AG5_or1{{"OR"}}
    AG5_sub1["Reach planner-agent in the Agent Runtime Zone"]
    AG5_sub2["Rely on the weakness described in AG-5"]
    AG5_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG5_leaf2["Task plans and tool selections are accepted without an independent check"]
    AG5_leaf3["The weakness is present: Delegation from trace-collector to planner-agent carries the full..."]
    AG5_leaf4["No effective control observed: Issue narrowly scoped, short-lived delegation grants to..."]

    AG5_root --> AG5_or1
    AG5_or1 --> AG5_sub1
    AG5_or1 --> AG5_sub2
    AG5_sub1 --> AG5_leaf1
    AG5_sub1 --> AG5_leaf2
    AG5_sub2 --> AG5_leaf3
    AG5_sub2 --> AG5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG5_root goal
    class AG5_or1 orGate
    class AG5_sub1,AG5_sub2 subGoal
    class AG5_leaf1,AG5_leaf2,AG5_leaf3,AG5_leaf4 leaf
```
