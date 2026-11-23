# AG-19: Tool calls made by worker-2 are not tied to the end user, so the...

**Component**: worker-2 | **Risk Level**: High | **Finding**: AG-19

Tool calls made by worker-2 are not tied to the end user, so the tool server cannot tell whose authority a request carries.

```mermaid
flowchart TD
    AG19_root["Tool calls made by worker-2 are not tied to the end user, so the tool..."]
    AG19_or1{{"OR"}}
    AG19_sub1["Reach worker-2 in the Agent Runtime Zone"]
    AG19_sub2["Rely on the weakness described in AG-19"]
    AG19_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    AG19_leaf2["Work orders and route candidates are accepted without an independent check"]
    AG19_leaf3["The weakness is present: Tool calls made by worker-2 are not tied to the end user, so the..."]
    AG19_leaf4["No effective control observed: Propagate a signed end-user context with each tool call from..."]

    AG19_root --> AG19_or1
    AG19_or1 --> AG19_sub1
    AG19_or1 --> AG19_sub2
    AG19_sub1 --> AG19_leaf1
    AG19_sub1 --> AG19_leaf2
    AG19_sub2 --> AG19_leaf3
    AG19_sub2 --> AG19_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG19_root goal
    class AG19_or1 orGate
    class AG19_sub1,AG19_sub2 subGoal
    class AG19_leaf1,AG19_leaf2,AG19_leaf3,AG19_leaf4 leaf
```
