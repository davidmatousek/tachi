# AG-31: The goal or instruction set of tool-server-1 can be changed...

**Component**: tool-server-1 | **Risk Level**: Critical | **Finding**: AG-31

The goal or instruction set of tool-server-1 can be changed through content it reads, steering it toward actions its operators never intended.

```mermaid
flowchart TD
    AG31_root["The goal or instruction set of tool-server-1 can be changed through..."]
    AG31_or1{{"OR"}}
    AG31_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    AG31_sub2["Rely on the weakness described in AG-31"]
    AG31_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    AG31_leaf2["Tool call arguments and results are accepted without an independent check"]
    AG31_leaf3["The weakness is present: The goal or instruction set of tool-server-1 can be changed..."]
    AG31_leaf4["No effective control observed: Keep the goals of tool-server-1 in signed configuration that..."]

    AG31_root --> AG31_or1
    AG31_or1 --> AG31_sub1
    AG31_or1 --> AG31_sub2
    AG31_sub1 --> AG31_leaf1
    AG31_sub1 --> AG31_leaf2
    AG31_sub2 --> AG31_leaf3
    AG31_sub2 --> AG31_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG31_root goal
    class AG31_or1 orGate
    class AG31_sub1,AG31_sub2 subGoal
    class AG31_leaf1,AG31_leaf2,AG31_leaf3,AG31_leaf4 leaf
```
