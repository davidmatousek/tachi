# OI-2: Structured output from intake-agent is trusted by queue-a2 as...

**Component**: intake-agent | **Risk Level**: High | **Finding**: OI-2

Structured output from intake-agent is trusted by queue-a2 as already validated, so a malformed field flows straight into business logic.

```mermaid
flowchart TD
    OI2_root["Structured output from intake-agent is trusted by queue-a2 as already..."]
    OI2_or1{{"OR"}}
    OI2_sub1["Reach intake-agent in the Agent Runtime Zone"]
    OI2_sub2["Rely on the weakness described in OI-2"]
    OI2_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    OI2_leaf2["Free-text shipment requests are accepted without an independent check"]
    OI2_leaf3["The weakness is present: Structured output from intake-agent is trusted by queue-a2 as..."]
    OI2_leaf4["No effective control observed: Validate the output of intake-agent against a strict schema in..."]

    OI2_root --> OI2_or1
    OI2_or1 --> OI2_sub1
    OI2_or1 --> OI2_sub2
    OI2_sub1 --> OI2_leaf1
    OI2_sub1 --> OI2_leaf2
    OI2_sub2 --> OI2_leaf3
    OI2_sub2 --> OI2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI2_root goal
    class OI2_or1 orGate
    class OI2_sub1,OI2_sub2 subGoal
    class OI2_leaf1,OI2_leaf2,OI2_leaf3,OI2_leaf4 leaf
```
