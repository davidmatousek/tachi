# R-26: Operators approve changes to prompts, completions and tool traces...

**Component**: trace-collector | **Risk Level**: High | **Finding**: R-26

Operators approve changes to prompts, completions and tool traces through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

```mermaid
flowchart TD
    R26_root["Operators approve changes to prompts, completions and tool traces..."]
    R26_or1{{"OR"}}
    R26_sub1["Reach trace-collector in the Operations Zone"]
    R26_sub2["Rely on the weakness described in R-26"]
    R26_leaf1["A path exists from intake-agent over OTLP over TLS"]
    R26_leaf2["Prompts, completions and tool traces are accepted without an independent check"]
    R26_leaf3["The weakness is present: Operators approve changes to prompts, completions and tool traces..."]
    R26_leaf4["No effective control observed: Bind each approval to the exact change hash it covers, record..."]

    R26_root --> R26_or1
    R26_or1 --> R26_sub1
    R26_or1 --> R26_sub2
    R26_sub1 --> R26_leaf1
    R26_sub1 --> R26_leaf2
    R26_sub2 --> R26_leaf3
    R26_sub2 --> R26_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R26_root goal
    class R26_or1 orGate
    class R26_sub1,R26_sub2 subGoal
    class R26_leaf1,R26_leaf2,R26_leaf3,R26_leaf4 leaf
```
