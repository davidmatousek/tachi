# AG-12: router-agent can act on subtask assignments without a human...

**Component**: router-agent | **Risk Level**: High | **Finding**: AG-12

router-agent can act on subtask assignments without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

```mermaid
flowchart TD
    AG12_root["router-agent can act on subtask assignments without a human approval..."]
    AG12_or1{{"OR"}}
    AG12_sub1["Reach router-agent in the Agent Runtime Zone"]
    AG12_sub2["Rely on the weakness described in AG-12"]
    AG12_leaf1["A path exists from planner-agent over HTTP/2 over mTLS"]
    AG12_leaf2["Subtask assignments are accepted without an independent check"]
    AG12_leaf3["The weakness is present: router-agent can act on subtask assignments without a human..."]
    AG12_leaf4["No effective control observed: Require explicit human approval in router-agent for actions above..."]

    AG12_root --> AG12_or1
    AG12_or1 --> AG12_sub1
    AG12_or1 --> AG12_sub2
    AG12_sub1 --> AG12_leaf1
    AG12_sub1 --> AG12_leaf2
    AG12_sub2 --> AG12_leaf3
    AG12_sub2 --> AG12_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG12_root goal
    class AG12_or1 orGate
    class AG12_sub1,AG12_sub2 subGoal
    class AG12_leaf1,AG12_leaf2,AG12_leaf3,AG12_leaf4 leaf
```
