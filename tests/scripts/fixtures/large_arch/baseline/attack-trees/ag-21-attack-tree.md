# AG-21: The goal or instruction set of worker-3 can be changed through...

**Component**: worker-3 | **Risk Level**: Critical | **Finding**: AG-21

The goal or instruction set of worker-3 can be changed through content it reads, steering it toward actions its operators never intended.

```mermaid
flowchart TD
    AG21_root["The goal or instruction set of worker-3 can be changed through content..."]
    AG21_or1{{"OR"}}
    AG21_sub1["Reach worker-3 in the Agent Runtime Zone"]
    AG21_sub2["Rely on the weakness described in AG-21"]
    AG21_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    AG21_leaf2["Work orders and draft documents are accepted without an independent check"]
    AG21_leaf3["The weakness is present: The goal or instruction set of worker-3 can be changed through..."]
    AG21_leaf4["No effective control observed: Keep the goals of worker-3 in signed configuration that content..."]

    AG21_root --> AG21_or1
    AG21_or1 --> AG21_sub1
    AG21_or1 --> AG21_sub2
    AG21_sub1 --> AG21_leaf1
    AG21_sub1 --> AG21_leaf2
    AG21_sub2 --> AG21_leaf3
    AG21_sub2 --> AG21_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG21_root goal
    class AG21_or1 orGate
    class AG21_sub1,AG21_sub2 subGoal
    class AG21_leaf1,AG21_leaf2,AG21_leaf3,AG21_leaf4 leaf
```
