# D-19: A dependency of model-gateway becomes unavailable and the failure...

**Component**: model-gateway | **Risk Level**: High | **Finding**: D-19

A dependency of model-gateway becomes unavailable and the failure cascades because model-gateway waits on it synchronously for every request.

```mermaid
flowchart TD
    D19_root["A dependency of model-gateway becomes unavailable and the failure..."]
    D19_or1{{"OR"}}
    D19_sub1["Reach model-gateway in the Agent Runtime Zone"]
    D19_sub2["Rely on the weakness described in D-19"]
    D19_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    D19_leaf2["Prompts and completions are accepted without an independent check"]
    D19_leaf3["The weakness is present: A dependency of model-gateway becomes unavailable and the failure..."]
    D19_leaf4["No effective control observed: Isolate calls from model-gateway to the dependency with timeouts..."]

    D19_root --> D19_or1
    D19_or1 --> D19_sub1
    D19_or1 --> D19_sub2
    D19_sub1 --> D19_leaf1
    D19_sub1 --> D19_leaf2
    D19_sub2 --> D19_leaf3
    D19_sub2 --> D19_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D19_root goal
    class D19_or1 orGate
    class D19_sub1,D19_sub2 subGoal
    class D19_leaf1,D19_leaf2,D19_leaf3,D19_leaf4 leaf
```
