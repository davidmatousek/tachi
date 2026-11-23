# AG-6: Memory written by planner-agent is trusted on later runs, so one...

**Component**: planner-agent | **Risk Level**: High | **Finding**: AG-6

Memory written by planner-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

```mermaid
flowchart TD
    AG6_root["Memory written by planner-agent is trusted on later runs, so one..."]
    AG6_or1{{"OR"}}
    AG6_sub1["Reach planner-agent in the Agent Runtime Zone"]
    AG6_sub2["Rely on the weakness described in AG-6"]
    AG6_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG6_leaf2["Task plans and tool selections are accepted without an independent check"]
    AG6_leaf3["The weakness is present: Memory written by planner-agent is trusted on later runs, so one..."]
    AG6_leaf4["No effective control observed: Tag memory entries with provenance and trust level, sanitise them..."]

    AG6_root --> AG6_or1
    AG6_or1 --> AG6_sub1
    AG6_or1 --> AG6_sub2
    AG6_sub1 --> AG6_leaf1
    AG6_sub1 --> AG6_leaf2
    AG6_sub2 --> AG6_leaf3
    AG6_sub2 --> AG6_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG6_root goal
    class AG6_or1 orGate
    class AG6_sub1,AG6_sub2 subGoal
    class AG6_leaf1,AG6_leaf2,AG6_leaf3,AG6_leaf4 leaf
```
