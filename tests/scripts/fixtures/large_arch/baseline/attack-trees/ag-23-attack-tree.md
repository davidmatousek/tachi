# AG-23: An attacker chains two individually safe tools through worker-3 to...

**Component**: worker-3 | **Risk Level**: High | **Finding**: AG-23

An attacker chains two individually safe tools through worker-3 to reach an outcome neither was approved for, such as an export followed by an upload.

```mermaid
flowchart TD
    AG23_root["An attacker chains two individually safe tools through worker-3 to..."]
    AG23_or1{{"OR"}}
    AG23_sub1["Reach worker-3 in the Agent Runtime Zone"]
    AG23_sub2["Rely on the weakness described in AG-23"]
    AG23_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    AG23_leaf2["Work orders and draft documents are accepted without an independent check"]
    AG23_leaf3["The weakness is present: An attacker chains two individually safe tools through worker-3 to..."]
    AG23_leaf4["No effective control observed: Define forbidden tool sequences for worker-3, evaluate each call..."]

    AG23_root --> AG23_or1
    AG23_or1 --> AG23_sub1
    AG23_or1 --> AG23_sub2
    AG23_sub1 --> AG23_leaf1
    AG23_sub1 --> AG23_leaf2
    AG23_sub2 --> AG23_leaf3
    AG23_sub2 --> AG23_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG23_root goal
    class AG23_or1 orGate
    class AG23_sub1,AG23_sub2 subGoal
    class AG23_leaf1,AG23_leaf2,AG23_leaf3,AG23_leaf4 leaf
```
