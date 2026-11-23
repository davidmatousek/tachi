# E-29: A privileged maintenance task of trace-collector can be triggered...

**Component**: trace-collector | **Risk Level**: High | **Finding**: E-29

A privileged maintenance task of trace-collector can be triggered through a queue message that any producer on the bus may publish.

```mermaid
flowchart TD
    E29_root["A privileged maintenance task of trace-collector can be triggered..."]
    E29_or1{{"OR"}}
    E29_sub1["Reach trace-collector in the Operations Zone"]
    E29_sub2["Rely on the weakness described in E-29"]
    E29_leaf1["A path exists from intake-agent over OTLP over TLS"]
    E29_leaf2["Prompts, completions and tool traces are accepted without an independent check"]
    E29_leaf3["The weakness is present: A privileged maintenance task of trace-collector can be triggered..."]
    E29_leaf4["No effective control observed: Restrict who can publish maintenance messages that trace-collector..."]

    E29_root --> E29_or1
    E29_or1 --> E29_sub1
    E29_or1 --> E29_sub2
    E29_sub1 --> E29_leaf1
    E29_sub1 --> E29_leaf2
    E29_sub2 --> E29_leaf3
    E29_sub2 --> E29_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E29_root goal
    class E29_or1 orGate
    class E29_sub1,E29_sub2 subGoal
    class E29_leaf1,E29_leaf2,E29_leaf3,E29_leaf4 leaf
```
