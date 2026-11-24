# AG-9: Tool calls made by planner-agent are not tied to the end user, so...

**Component**: planner-agent | **Risk Level**: Critical | **Finding**: AG-9

Tool calls made by planner-agent are not tied to the end user, so the tool server cannot tell whose authority a request carries.

```mermaid
flowchart TD
    AG9_root["Tool calls made by planner-agent are not tied to the end user, so the..."]
    AG9_or1{{"OR"}}
    AG9_sub1["Reach planner-agent in the Agent Runtime Zone"]
    AG9_sub2["Rely on the weakness described in AG-9"]
    AG9_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG9_leaf2["Task plans and tool selections are accepted without an independent check"]
    AG9_leaf3["The weakness is present: Tool calls made by planner-agent are not tied to the end user, so..."]
    AG9_leaf4["No effective control observed: Propagate a signed end-user context with each tool call from..."]

    AG9_root --> AG9_or1
    AG9_or1 --> AG9_sub1
    AG9_or1 --> AG9_sub2
    AG9_sub1 --> AG9_leaf1
    AG9_sub1 --> AG9_leaf2
    AG9_sub2 --> AG9_leaf3
    AG9_sub2 --> AG9_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG9_root goal
    class AG9_or1 orGate
    class AG9_sub1,AG9_sub2 subGoal
    class AG9_leaf1,AG9_leaf2,AG9_leaf3,AG9_leaf4 leaf
```
