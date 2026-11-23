# AG-10: planner-agent invokes tools with arguments assembled from model...

**Component**: planner-agent | **Risk Level**: High | **Finding**: AG-10

planner-agent invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed.

```mermaid
flowchart TD
    AG10_root["planner-agent invokes tools with arguments assembled from model..."]
    AG10_or1{{"OR"}}
    AG10_sub1["Reach planner-agent in the Agent Runtime Zone"]
    AG10_sub2["Rely on the weakness described in AG-10"]
    AG10_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG10_leaf2["Task plans and tool selections are accepted without an independent check"]
    AG10_leaf3["The weakness is present: planner-agent invokes tools with arguments assembled from model..."]
    AG10_leaf4["No effective control observed: Validate every argument against the tool schema in planner-agent..."]

    AG10_root --> AG10_or1
    AG10_or1 --> AG10_sub1
    AG10_or1 --> AG10_sub2
    AG10_sub1 --> AG10_leaf1
    AG10_sub1 --> AG10_leaf2
    AG10_sub2 --> AG10_leaf3
    AG10_sub2 --> AG10_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG10_root goal
    class AG10_or1 orGate
    class AG10_sub1,AG10_sub2 subGoal
    class AG10_leaf1,AG10_leaf2,AG10_leaf3,AG10_leaf4 leaf
```
