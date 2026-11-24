# OI-15: File paths or names produced by worker-2 are used to write files...

**Component**: worker-2 | **Risk Level**: Critical | **Finding**: OI-15

File paths or names produced by worker-2 are used to write files, letting crafted output reach locations outside the intended directory.

```mermaid
flowchart TD
    OI15_root["File paths or names produced by worker-2 are used to write files..."]
    OI15_or1{{"OR"}}
    OI15_sub1["Reach worker-2 in the Agent Runtime Zone"]
    OI15_sub2["Rely on the weakness described in OI-15"]
    OI15_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    OI15_leaf2["Work orders and route candidates are accepted without an independent check"]
    OI15_leaf3["The weakness is present: File paths or names produced by worker-2 are used to write files..."]
    OI15_leaf4["No effective control observed: Generate file names for worker-2 on the server, confine writes to..."]

    OI15_root --> OI15_or1
    OI15_or1 --> OI15_sub1
    OI15_or1 --> OI15_sub2
    OI15_sub1 --> OI15_leaf1
    OI15_sub1 --> OI15_leaf2
    OI15_sub2 --> OI15_leaf3
    OI15_sub2 --> OI15_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI15_root goal
    class OI15_or1 orGate
    class OI15_sub1,OI15_sub2 subGoal
    class OI15_leaf1,OI15_leaf2,OI15_leaf3,OI15_leaf4 leaf
```
