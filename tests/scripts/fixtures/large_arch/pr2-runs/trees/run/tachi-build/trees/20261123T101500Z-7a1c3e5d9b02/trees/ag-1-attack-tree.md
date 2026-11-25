# AG-1: Memory written by intake-agent is trusted on later runs, so one...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: AG-1

Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

```mermaid
flowchart TD
    AG1_root["Memory written by intake-agent is trusted on later runs, so one..."]
    AG1_or1{{"OR"}}
    AG1_sub1["Reach intake-agent in the Agent Runtime Zone"]
    AG1_sub2["Rely on the weakness described in AG-1"]
    AG1_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    AG1_leaf2["Free-text shipment requests are accepted without an independent check"]
    AG1_leaf3["The weakness is present: Memory written by intake-agent is trusted on later runs, so one..."]
    AG1_leaf4["No effective control observed: Tag memory entries with provenance and trust level, sanitise them..."]

    AG1_root --> AG1_or1
    AG1_or1 --> AG1_sub1
    AG1_or1 --> AG1_sub2
    AG1_sub1 --> AG1_leaf1
    AG1_sub1 --> AG1_leaf2
    AG1_sub2 --> AG1_leaf3
    AG1_sub2 --> AG1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG1_root goal
    class AG1_or1 orGate
    class AG1_sub1,AG1_sub2 subGoal
    class AG1_leaf1,AG1_leaf2,AG1_leaf3,AG1_leaf4 leaf
```
