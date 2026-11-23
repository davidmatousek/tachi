# AG-26: reviewer-agent retries failed actions on its own, repeating side...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: AG-26

reviewer-agent retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

```mermaid
flowchart TD
    AG26_root["reviewer-agent retries failed actions on its own, repeating side..."]
    AG26_or1{{"OR"}}
    AG26_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    AG26_sub2["Rely on the weakness described in AG-26"]
    AG26_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    AG26_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    AG26_leaf3["The weakness is present: reviewer-agent retries failed actions on its own, repeating side..."]
    AG26_leaf4["No effective control observed: Make the actions of reviewer-agent idempotent with request keys..."]

    AG26_root --> AG26_or1
    AG26_or1 --> AG26_sub1
    AG26_or1 --> AG26_sub2
    AG26_sub1 --> AG26_leaf1
    AG26_sub1 --> AG26_leaf2
    AG26_sub2 --> AG26_leaf3
    AG26_sub2 --> AG26_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG26_root goal
    class AG26_or1 orGate
    class AG26_sub1,AG26_sub2 subGoal
    class AG26_leaf1,AG26_leaf2,AG26_leaf3,AG26_leaf4 leaf
```
