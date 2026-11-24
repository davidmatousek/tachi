# AG-18: The goal or instruction set of worker-2 can be changed through...

**Component**: worker-2 | **Risk Level**: High | **Finding**: AG-18

The goal or instruction set of worker-2 can be changed through content it reads, steering it toward actions its operators never intended.

```mermaid
flowchart TD
    AG18_root["The goal or instruction set of worker-2 can be changed through content..."]
    AG18_or1{{"OR"}}
    AG18_sub1["Reach worker-2 in the Agent Runtime Zone"]
    AG18_sub2["Rely on the weakness described in AG-18"]
    AG18_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    AG18_leaf2["Work orders and route candidates are accepted without an independent check"]
    AG18_leaf3["The weakness is present: The goal or instruction set of worker-2 can be changed through..."]
    AG18_leaf4["No effective control observed: Keep the goals of worker-2 in signed configuration that content..."]

    AG18_root --> AG18_or1
    AG18_or1 --> AG18_sub1
    AG18_or1 --> AG18_sub2
    AG18_sub1 --> AG18_leaf1
    AG18_sub1 --> AG18_leaf2
    AG18_sub2 --> AG18_leaf3
    AG18_sub2 --> AG18_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG18_root goal
    class AG18_or1 orGate
    class AG18_sub1,AG18_sub2 subGoal
    class AG18_leaf1,AG18_leaf2,AG18_leaf3,AG18_leaf4 leaf
```
