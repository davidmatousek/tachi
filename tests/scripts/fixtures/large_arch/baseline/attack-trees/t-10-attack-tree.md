# T-10: Configuration of tool-server-1 can be rewritten by any service...

**Component**: tool-server-1 | **Risk Level**: Critical | **Finding**: T-10

Configuration of tool-server-1 can be rewritten by any service that holds the shared deployment credential, silently changing how tool call arguments and results are handled.

```mermaid
flowchart TD
    T10_root["Configuration of tool-server-1 can be rewritten by any service that..."]
    T10_or1{{"OR"}}
    T10_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    T10_sub2["Rely on the weakness described in T-10"]
    T10_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    T10_leaf2["Tool call arguments and results are accepted without an independent check"]
    T10_leaf3["The weakness is present: Configuration of tool-server-1 can be rewritten by any service..."]
    T10_leaf4["No effective control observed: Keep the configuration of tool-server-1 in a versioned..."]

    T10_root --> T10_or1
    T10_or1 --> T10_sub1
    T10_or1 --> T10_sub2
    T10_sub1 --> T10_leaf1
    T10_sub1 --> T10_leaf2
    T10_sub2 --> T10_leaf3
    T10_sub2 --> T10_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T10_root goal
    class T10_or1 orGate
    class T10_sub1,T10_sub2 subGoal
    class T10_leaf1,T10_leaf2,T10_leaf3,T10_leaf4 leaf
```
