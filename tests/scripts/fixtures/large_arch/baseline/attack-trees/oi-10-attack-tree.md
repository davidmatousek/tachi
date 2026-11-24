# OI-10: Structured output from planner-agent is trusted by router-agent as...

**Component**: planner-agent | **Risk Level**: Critical | **Finding**: OI-10

Structured output from planner-agent is trusted by router-agent as already validated, so a malformed field flows straight into business logic.

```mermaid
flowchart TD
    OI10_root["Structured output from planner-agent is trusted by router-agent as..."]
    OI10_or1{{"OR"}}
    OI10_sub1["Reach planner-agent in the Agent Runtime Zone"]
    OI10_sub2["Rely on the weakness described in OI-10"]
    OI10_leaf1["A path exists from queue-a2 over NATS over TLS"]
    OI10_leaf2["Task plans and tool selections are accepted without an independent check"]
    OI10_leaf3["The weakness is present: Structured output from planner-agent is trusted by router-agent as..."]
    OI10_leaf4["No effective control observed: Validate the output of planner-agent against a strict schema in..."]

    OI10_root --> OI10_or1
    OI10_or1 --> OI10_sub1
    OI10_or1 --> OI10_sub2
    OI10_sub1 --> OI10_leaf1
    OI10_sub1 --> OI10_leaf2
    OI10_sub2 --> OI10_leaf3
    OI10_sub2 --> OI10_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI10_root goal
    class OI10_or1 orGate
    class OI10_sub1,OI10_sub2 subGoal
    class OI10_leaf1,OI10_leaf2,OI10_leaf3,OI10_leaf4 leaf
```
