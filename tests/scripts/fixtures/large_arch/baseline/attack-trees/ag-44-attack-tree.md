# AG-44: scheduler-1 can act on recurring planning triggers without a human...

**Component**: scheduler-1 | **Risk Level**: Critical | **Finding**: AG-44

scheduler-1 can act on recurring planning triggers without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

```mermaid
flowchart TD
    AG44_root["scheduler-1 can act on recurring planning triggers without a human..."]
    AG44_or1{{"OR"}}
    AG44_sub1["Reach scheduler-1 in the Agent Runtime Zone"]
    AG44_sub2["Rely on the weakness described in AG-44"]
    AG44_leaf1["A path exists from queue-a2 over NATS over TLS"]
    AG44_leaf2["Recurring planning triggers are accepted without an independent check"]
    AG44_leaf3["The weakness is present: scheduler-1 can act on recurring planning triggers without a human..."]
    AG44_leaf4["No effective control observed: Require explicit human approval in scheduler-1 for actions above a..."]

    AG44_root --> AG44_or1
    AG44_or1 --> AG44_sub1
    AG44_or1 --> AG44_sub2
    AG44_sub1 --> AG44_leaf1
    AG44_sub1 --> AG44_leaf2
    AG44_sub2 --> AG44_leaf3
    AG44_sub2 --> AG44_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG44_root goal
    class AG44_or1 orGate
    class AG44_sub1,AG44_sub2 subGoal
    class AG44_leaf1,AG44_leaf2,AG44_leaf3,AG44_leaf4 leaf
```
