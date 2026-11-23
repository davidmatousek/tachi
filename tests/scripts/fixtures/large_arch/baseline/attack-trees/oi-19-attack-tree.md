# OI-19: File paths or names produced by model-gateway are used to write...

**Component**: model-gateway | **Risk Level**: High | **Finding**: OI-19

File paths or names produced by model-gateway are used to write files, letting crafted output reach locations outside the intended directory.

```mermaid
flowchart TD
    OI19_root["File paths or names produced by model-gateway are used to write files..."]
    OI19_or1{{"OR"}}
    OI19_sub1["Reach model-gateway in the Agent Runtime Zone"]
    OI19_sub2["Rely on the weakness described in OI-19"]
    OI19_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    OI19_leaf2["Prompts and completions are accepted without an independent check"]
    OI19_leaf3["The weakness is present: File paths or names produced by model-gateway are used to write..."]
    OI19_leaf4["No effective control observed: Generate file names for model-gateway on the server, confine..."]

    OI19_root --> OI19_or1
    OI19_or1 --> OI19_sub1
    OI19_or1 --> OI19_sub2
    OI19_sub1 --> OI19_leaf1
    OI19_sub1 --> OI19_leaf2
    OI19_sub2 --> OI19_leaf3
    OI19_sub2 --> OI19_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI19_root goal
    class OI19_or1 orGate
    class OI19_sub1,OI19_sub2 subGoal
    class OI19_leaf1,OI19_leaf2,OI19_leaf3,OI19_leaf4 leaf
```
