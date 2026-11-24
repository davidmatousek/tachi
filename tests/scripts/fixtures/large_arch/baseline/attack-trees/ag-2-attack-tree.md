# AG-2: intake-agent retries failed actions on its own, repeating side...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: AG-2

intake-agent retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

```mermaid
flowchart TD
    AG2_root["intake-agent retries failed actions on its own, repeating side effects..."]
    AG2_or1{{"OR"}}
    AG2_sub1["Reach intake-agent in the Agent Runtime Zone"]
    AG2_sub2["Rely on the weakness described in AG-2"]
    AG2_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    AG2_leaf2["Free-text shipment requests are accepted without an independent check"]
    AG2_leaf3["The weakness is present: intake-agent retries failed actions on its own, repeating side..."]
    AG2_leaf4["No effective control observed: Make the actions of intake-agent idempotent with request keys, cap..."]

    AG2_root --> AG2_or1
    AG2_or1 --> AG2_sub1
    AG2_or1 --> AG2_sub2
    AG2_sub1 --> AG2_leaf1
    AG2_sub1 --> AG2_leaf2
    AG2_sub2 --> AG2_leaf3
    AG2_sub2 --> AG2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG2_root goal
    class AG2_or1 orGate
    class AG2_sub1,AG2_sub2 subGoal
    class AG2_leaf1,AG2_leaf2,AG2_leaf3,AG2_leaf4 leaf
```
