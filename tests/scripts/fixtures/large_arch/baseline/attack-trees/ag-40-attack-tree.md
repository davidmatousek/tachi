# AG-40: policy-engine can start further agents or processes on request, so...

**Component**: policy-engine | **Risk Level**: High | **Finding**: AG-40

policy-engine can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

```mermaid
flowchart TD
    AG40_root["policy-engine can start further agents or processes on request, so a..."]
    AG40_or1{{"OR"}}
    AG40_sub1["Reach policy-engine in the Operations Zone"]
    AG40_sub2["Rely on the weakness described in AG-40"]
    AG40_leaf1["A path exists from auth-broker over gRPC over mTLS"]
    AG40_leaf2["Guardrail rules and approval decisions are accepted without an independent check"]
    AG40_leaf3["The weakness is present: policy-engine can start further agents or processes on request, so..."]
    AG40_leaf4["No effective control observed: Remove the ability of policy-engine to start other agents unless..."]

    AG40_root --> AG40_or1
    AG40_or1 --> AG40_sub1
    AG40_or1 --> AG40_sub2
    AG40_sub1 --> AG40_leaf1
    AG40_sub1 --> AG40_leaf2
    AG40_sub2 --> AG40_leaf3
    AG40_sub2 --> AG40_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG40_root goal
    class AG40_or1 orGate
    class AG40_sub1,AG40_sub2 subGoal
    class AG40_leaf1,AG40_leaf2,AG40_leaf3,AG40_leaf4 leaf
```
