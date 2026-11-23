# T-13: Replay of an earlier valid update to prompts and completions...

**Component**: model-gateway | **Risk Level**: High | **Finding**: T-13

Replay of an earlier valid update to prompts and completions reaches model-gateway because updates carry no nonce or expiry, restoring a state the owner already corrected.

```mermaid
flowchart TD
    T13_root["Replay of an earlier valid update to prompts and completions reaches..."]
    T13_or1{{"OR"}}
    T13_sub1["Reach model-gateway in the Agent Runtime Zone"]
    T13_sub2["Rely on the weakness described in T-13"]
    T13_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    T13_leaf2["Prompts and completions are accepted without an independent check"]
    T13_leaf3["The weakness is present: Replay of an earlier valid update to prompts and completions..."]
    T13_leaf4["No effective control observed: Add a nonce and a short expiry to every update accepted by..."]

    T13_root --> T13_or1
    T13_or1 --> T13_sub1
    T13_or1 --> T13_sub2
    T13_sub1 --> T13_leaf1
    T13_sub1 --> T13_leaf2
    T13_sub2 --> T13_leaf3
    T13_sub2 --> T13_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T13_root goal
    class T13_or1 orGate
    class T13_sub1,T13_sub2 subGoal
    class T13_leaf1,T13_leaf2,T13_leaf3,T13_leaf4 leaf
```
