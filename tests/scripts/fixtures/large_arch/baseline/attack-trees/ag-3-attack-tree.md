# AG-3: intake-agent can start further agents or processes on request, so...

**Component**: intake-agent | **Risk Level**: High | **Finding**: AG-3

intake-agent can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

```mermaid
flowchart TD
    AG3_root["intake-agent can start further agents or processes on request, so a..."]
    AG3_or1{{"OR"}}
    AG3_sub1["Reach intake-agent in the Agent Runtime Zone"]
    AG3_sub2["Rely on the weakness described in AG-3"]
    AG3_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    AG3_leaf2["Free-text shipment requests are accepted without an independent check"]
    AG3_leaf3["The weakness is present: intake-agent can start further agents or processes on request, so..."]
    AG3_leaf4["No effective control observed: Remove the ability of intake-agent to start other agents unless an..."]

    AG3_root --> AG3_or1
    AG3_or1 --> AG3_sub1
    AG3_or1 --> AG3_sub2
    AG3_sub1 --> AG3_leaf1
    AG3_sub1 --> AG3_leaf2
    AG3_sub2 --> AG3_leaf3
    AG3_sub2 --> AG3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG3_root goal
    class AG3_or1 orGate
    class AG3_sub1,AG3_sub2 subGoal
    class AG3_leaf1,AG3_leaf2,AG3_leaf3,AG3_leaf4 leaf
```
