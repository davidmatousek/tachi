# AG-13: An attacker chains two individually safe tools through...

**Component**: router-agent | **Risk Level**: Critical | **Finding**: AG-13

An attacker chains two individually safe tools through router-agent to reach an outcome neither was approved for, such as an export followed by an upload.

```mermaid
flowchart TD
    AG13_root["An attacker chains two individually safe tools through router-agent to..."]
    AG13_or1{{"OR"}}
    AG13_sub1["Reach router-agent in the Agent Runtime Zone"]
    AG13_sub2["Rely on the weakness described in AG-13"]
    AG13_leaf1["A path exists from planner-agent over HTTP/2 over mTLS"]
    AG13_leaf2["Subtask assignments are accepted without an independent check"]
    AG13_leaf3["The weakness is present: An attacker chains two individually safe tools through..."]
    AG13_leaf4["No effective control observed: Define forbidden tool sequences for router-agent, evaluate each..."]

    AG13_root --> AG13_or1
    AG13_or1 --> AG13_sub1
    AG13_or1 --> AG13_sub2
    AG13_sub1 --> AG13_leaf1
    AG13_sub1 --> AG13_leaf2
    AG13_sub2 --> AG13_leaf3
    AG13_sub2 --> AG13_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG13_root goal
    class AG13_or1 orGate
    class AG13_sub1,AG13_sub2 subGoal
    class AG13_leaf1,AG13_leaf2,AG13_leaf3,AG13_leaf4 leaf
```
