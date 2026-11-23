# AG-42: Memory written by tool-server-1 is trusted on later runs, so one...

**Component**: tool-server-1 | **Risk Level**: High | **Finding**: AG-42

Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

```mermaid
flowchart TD
    AG42_root["Memory written by tool-server-1 is trusted on later runs, so one..."]
    AG42_or1{{"OR"}}
    AG42_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    AG42_sub2["Rely on the weakness described in AG-42"]
    AG42_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    AG42_leaf2["Tool call arguments and results are accepted without an independent check"]
    AG42_leaf3["The weakness is present: Memory written by tool-server-1 is trusted on later runs, so one..."]
    AG42_leaf4["No effective control observed: Tag memory entries with provenance and trust level, sanitise them..."]

    AG42_root --> AG42_or1
    AG42_or1 --> AG42_sub1
    AG42_or1 --> AG42_sub2
    AG42_sub1 --> AG42_leaf1
    AG42_sub1 --> AG42_leaf2
    AG42_sub2 --> AG42_leaf3
    AG42_sub2 --> AG42_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG42_root goal
    class AG42_or1 orGate
    class AG42_sub1,AG42_sub2 subGoal
    class AG42_leaf1,AG42_leaf2,AG42_leaf3,AG42_leaf4 leaf
```
