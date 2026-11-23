# R-15: Log entries from router-agent can be edited or deleted by the same...

**Component**: router-agent | **Risk Level**: High | **Finding**: R-15

Log entries from router-agent can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

```mermaid
flowchart TD
    R15_root["Log entries from router-agent can be edited or deleted by the same..."]
    R15_or1{{"OR"}}
    R15_sub1["Reach router-agent in the Agent Runtime Zone"]
    R15_sub2["Rely on the weakness described in R-15"]
    R15_leaf1["A path exists from planner-agent over HTTP/2 over mTLS"]
    R15_leaf2["Subtask assignments are accepted without an independent check"]
    R15_leaf3["The weakness is present: Log entries from router-agent can be edited or deleted by the same..."]
    R15_leaf4["No effective control observed: Write the records of router-agent to an append-only store that..."]

    R15_root --> R15_or1
    R15_or1 --> R15_sub1
    R15_or1 --> R15_sub2
    R15_sub1 --> R15_leaf1
    R15_sub1 --> R15_leaf2
    R15_sub2 --> R15_leaf3
    R15_sub2 --> R15_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R15_root goal
    class R15_or1 orGate
    class R15_sub1,R15_sub2 subGoal
    class R15_leaf1,R15_leaf2,R15_leaf3,R15_leaf4 leaf
```
