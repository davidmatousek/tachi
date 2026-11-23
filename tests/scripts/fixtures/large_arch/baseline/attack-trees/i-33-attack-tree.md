# I-33: Logs and traces emitted by queue-a2 include raw task and result...

**Component**: queue-a2 | **Risk Level**: High | **Finding**: I-33

Logs and traces emitted by queue-a2 include raw task and result messages, so anyone with access to the logging pipeline can read content meant for one tenant.

```mermaid
flowchart TD
    I33_root["Logs and traces emitted by queue-a2 include raw task and result..."]
    I33_or1{{"OR"}}
    I33_sub1["Reach queue-a2 in the Agent Runtime Zone"]
    I33_sub2["Rely on the weakness described in I-33"]
    I33_leaf1["A path exists from intake-agent over NATS over TLS"]
    I33_leaf2["Task and result messages are accepted without an independent check"]
    I33_leaf3["The weakness is present: Logs and traces emitted by queue-a2 include raw task and result..."]
    I33_leaf4["No effective control observed: Redact or tokenise sensitive fields before queue-a2 emits logs and..."]

    I33_root --> I33_or1
    I33_or1 --> I33_sub1
    I33_or1 --> I33_sub2
    I33_sub1 --> I33_leaf1
    I33_sub1 --> I33_leaf2
    I33_sub2 --> I33_leaf3
    I33_sub2 --> I33_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I33_root goal
    class I33_or1 orGate
    class I33_sub1,I33_sub2 subGoal
    class I33_leaf1,I33_leaf2,I33_leaf3,I33_leaf4 leaf
```
