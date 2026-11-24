# AG-16: worker-2 can start further agents or processes on request, so a...

**Component**: worker-2 | **Risk Level**: High | **Finding**: AG-16

worker-2 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

```mermaid
flowchart TD
    AG16_root["worker-2 can start further agents or processes on request, so a..."]
    AG16_or1{{"OR"}}
    AG16_sub1["Reach worker-2 in the Agent Runtime Zone"]
    AG16_sub2["Rely on the weakness described in AG-16"]
    AG16_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    AG16_leaf2["Work orders and route candidates are accepted without an independent check"]
    AG16_leaf3["The weakness is present: worker-2 can start further agents or processes on request, so a..."]
    AG16_leaf4["No effective control observed: Remove the ability of worker-2 to start other agents unless an..."]

    AG16_root --> AG16_or1
    AG16_or1 --> AG16_sub1
    AG16_or1 --> AG16_sub2
    AG16_sub1 --> AG16_leaf1
    AG16_sub1 --> AG16_leaf2
    AG16_sub2 --> AG16_leaf3
    AG16_sub2 --> AG16_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG16_root goal
    class AG16_or1 orGate
    class AG16_sub1,AG16_sub2 subGoal
    class AG16_leaf1,AG16_leaf2,AG16_leaf3,AG16_leaf4 leaf
```
