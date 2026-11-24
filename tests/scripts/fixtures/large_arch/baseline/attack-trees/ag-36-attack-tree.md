# AG-36: An attacker chains two individually safe tools through queue-a2 to...

**Component**: queue-a2 | **Risk Level**: Critical | **Finding**: AG-36

An attacker chains two individually safe tools through queue-a2 to reach an outcome neither was approved for, such as an export followed by an upload.

```mermaid
flowchart TD
    AG36_root["An attacker chains two individually safe tools through queue-a2 to..."]
    AG36_or1{{"OR"}}
    AG36_sub1["Reach queue-a2 in the Agent Runtime Zone"]
    AG36_sub2["Rely on the weakness described in AG-36"]
    AG36_leaf1["A path exists from intake-agent over NATS over TLS"]
    AG36_leaf2["Task and result messages are accepted without an independent check"]
    AG36_leaf3["The weakness is present: An attacker chains two individually safe tools through queue-a2 to..."]
    AG36_leaf4["No effective control observed: Define forbidden tool sequences for queue-a2, evaluate each call..."]

    AG36_root --> AG36_or1
    AG36_or1 --> AG36_sub1
    AG36_or1 --> AG36_sub2
    AG36_sub1 --> AG36_leaf1
    AG36_sub1 --> AG36_leaf2
    AG36_sub2 --> AG36_leaf3
    AG36_sub2 --> AG36_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG36_root goal
    class AG36_or1 orGate
    class AG36_sub1,AG36_sub2 subGoal
    class AG36_leaf1,AG36_leaf2,AG36_leaf3,AG36_leaf4 leaf
```
