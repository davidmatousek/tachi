# R-16: Operators approve changes to work orders and route candidates...

**Component**: worker-2 | **Risk Level**: Critical | **Finding**: R-16

Operators approve changes to work orders and route candidates through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

```mermaid
flowchart TD
    R16_root["Operators approve changes to work orders and route candidates through..."]
    R16_or1{{"OR"}}
    R16_sub1["Reach worker-2 in the Agent Runtime Zone"]
    R16_sub2["Rely on the weakness described in R-16"]
    R16_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    R16_leaf2["Work orders and route candidates are accepted without an independent check"]
    R16_leaf3["The weakness is present: Operators approve changes to work orders and route candidates..."]
    R16_leaf4["No effective control observed: Bind each approval to the exact change hash it covers, record..."]

    R16_root --> R16_or1
    R16_or1 --> R16_sub1
    R16_or1 --> R16_sub2
    R16_sub1 --> R16_leaf1
    R16_sub1 --> R16_leaf2
    R16_sub2 --> R16_leaf3
    R16_sub2 --> R16_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R16_root goal
    class R16_or1 orGate
    class R16_sub1,R16_sub2 subGoal
    class R16_leaf1,R16_leaf2,R16_leaf3,R16_leaf4 leaf
```
