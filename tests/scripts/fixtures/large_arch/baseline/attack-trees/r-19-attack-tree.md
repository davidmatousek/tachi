# R-19: Failed and rejected attempts against model-gateway are not logged...

**Component**: model-gateway | **Risk Level**: High | **Finding**: R-19

Failed and rejected attempts against model-gateway are not logged, so probing of prompts and completions leaves no trace that an investigator could use.

```mermaid
flowchart TD
    R19_root["Failed and rejected attempts against model-gateway are not logged, so..."]
    R19_or1{{"OR"}}
    R19_sub1["Reach model-gateway in the Agent Runtime Zone"]
    R19_sub2["Rely on the weakness described in R-19"]
    R19_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    R19_leaf2["Prompts and completions are accepted without an independent check"]
    R19_leaf3["The weakness is present: Failed and rejected attempts against model-gateway are not logged..."]
    R19_leaf4["No effective control observed: Log denied and malformed requests to model-gateway at a retained..."]

    R19_root --> R19_or1
    R19_or1 --> R19_sub1
    R19_or1 --> R19_sub2
    R19_sub1 --> R19_leaf1
    R19_sub1 --> R19_leaf2
    R19_sub2 --> R19_leaf3
    R19_sub2 --> R19_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R19_root goal
    class R19_or1 orGate
    class R19_sub1,R19_sub2 subGoal
    class R19_leaf1,R19_leaf2,R19_leaf3,R19_leaf4 leaf
```
