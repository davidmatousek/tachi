# OI-9: planner-agent emits URLs that downstream services fetch, so an...

**Component**: planner-agent | **Risk Level**: Critical | **Finding**: OI-9

planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

```mermaid
flowchart TD
    OI9_root["planner-agent emits URLs that downstream services fetch, so an..."]
    OI9_or1{{"OR"}}
    OI9_sub1["Reach planner-agent in the Agent Runtime Zone"]
    OI9_sub2["Rely on the weakness described in OI-9"]
    OI9_leaf1["A path exists from queue-a2 over NATS over TLS"]
    OI9_leaf2["Task plans and tool selections are accepted without an independent check"]
    OI9_leaf3["The weakness is present: planner-agent emits URLs that downstream services fetch, so an..."]
    OI9_leaf4["No effective control observed: Validate URLs from planner-agent against an allowlist, resolve and..."]

    OI9_root --> OI9_or1
    OI9_or1 --> OI9_sub1
    OI9_or1 --> OI9_sub2
    OI9_sub1 --> OI9_leaf1
    OI9_sub1 --> OI9_leaf2
    OI9_sub2 --> OI9_leaf3
    OI9_sub2 --> OI9_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI9_root goal
    class OI9_or1 orGate
    class OI9_sub1,OI9_sub2 subGoal
    class OI9_leaf1,OI9_leaf2,OI9_leaf3,OI9_leaf4 leaf
```
