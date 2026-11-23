# T-4: Unsanitised task plans and tool selections reach planner-agent and...

**Component**: planner-agent | **Risk Level**: High | **Finding**: T-4

Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so crafted input changes how later steps interpret the record.

```mermaid
flowchart TD
    T4_root["Unsanitised task plans and tool selections reach planner-agent and are..."]
    T4_or1{{"OR"}}
    T4_sub1["Reach planner-agent in the Agent Runtime Zone"]
    T4_sub2["Rely on the weakness described in T-4"]
    T4_leaf1["A path exists from queue-a2 over NATS over TLS"]
    T4_leaf2["Task plans and tool selections are accepted without an independent check"]
    T4_leaf3["The weakness is present: Unsanitised task plans and tool selections reach planner-agent and..."]
    T4_leaf4["No effective control observed: Validate task plans and tool selections against a strict schema at..."]

    T4_root --> T4_or1
    T4_or1 --> T4_sub1
    T4_or1 --> T4_sub2
    T4_sub1 --> T4_leaf1
    T4_sub1 --> T4_leaf2
    T4_sub2 --> T4_leaf3
    T4_sub2 --> T4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T4_root goal
    class T4_or1 orGate
    class T4_sub1,T4_sub2 subGoal
    class T4_leaf1,T4_leaf2,T4_leaf3,T4_leaf4 leaf
```
