# I-22: Verbose error responses from model-gateway reveal internal paths...

**Component**: model-gateway | **Risk Level**: High | **Finding**: I-22

Verbose error responses from model-gateway reveal internal paths, query text and identifiers of prompts and completions to any caller who can trigger a failure.

```mermaid
flowchart TD
    I22_root["Verbose error responses from model-gateway reveal internal paths..."]
    I22_or1{{"OR"}}
    I22_sub1["Reach model-gateway in the Agent Runtime Zone"]
    I22_sub2["Rely on the weakness described in I-22"]
    I22_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    I22_leaf2["Prompts and completions are accepted without an independent check"]
    I22_leaf3["The weakness is present: Verbose error responses from model-gateway reveal internal paths..."]
    I22_leaf4["No effective control observed: Return generic error codes from model-gateway, log the detail on..."]

    I22_root --> I22_or1
    I22_or1 --> I22_sub1
    I22_or1 --> I22_sub2
    I22_sub1 --> I22_leaf1
    I22_sub1 --> I22_leaf2
    I22_sub2 --> I22_leaf3
    I22_sub2 --> I22_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I22_root goal
    class I22_or1 orGate
    class I22_sub1,I22_sub2 subGoal
    class I22_leaf1,I22_leaf2,I22_leaf3,I22_leaf4 leaf
```
